# app/services/me_service.py
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from app.domain.repositories.plans_repo import PlansRepo
from app.domain.repositories.usage_repo import UsageRepo
from app.schemas.me import MeLimitsOut, MeUsageWeekOut
from app.utils.time_windows import week_window_lima

DEFAULT_FREE_LIMITS = {"weekly_free_analyses": 1, "history_cap": 3}

class MeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.plans = PlansRepo(db)
        self.usage = UsageRepo(db)

    async def _resolve_effective_limits(self, user_id) -> tuple[str, Optional[int], Optional[int]]:
        """
        Retorna (plan_code, weekly_limit, history_cap)
        - Si hay plan vigente: lee de plan.limits (JSON)
        - Si no hay: usa FREE por defecto (o plan.code == 'free' si existe)
        - None significa ILIMITADO
        """
        sub_with_plan = await self.plans.get_active_subscription_with_plan(user_id)
        if sub_with_plan:
            _, plan = sub_with_plan
            limits = (plan.limits or {}) if plan.limits is not None else {}
            weekly = limits.get("weekly_free_analyses")
            hist = limits.get("history_cap")
            # Convención: si premium no tiene tope, guarda None
            return plan.code, weekly, hist

        # Fallback: FREE
        free = await self.plans.get_plan_by_code("free")
        if free and free.limits:
            weekly = free.limits.get("weekly_free_analyses", DEFAULT_FREE_LIMITS["weekly_free_analyses"])
            hist = free.limits.get("history_cap", DEFAULT_FREE_LIMITS["history_cap"])
            return free.code, weekly, hist

        # Si ni siquiera hay plan free sembrado, aplica valores por defecto
        return "free", DEFAULT_FREE_LIMITS["weekly_free_analyses"], DEFAULT_FREE_LIMITS["history_cap"]

    async def get_limits(self, user_id) -> MeLimitsOut:
        week_start, next_week_start = week_window_lima()
        plan_code, weekly_limit, history_cap = await self._resolve_effective_limits(user_id)
        used = await self.usage.get_week_count(user_id, week_start.date())

        # Si el plan es premium y definiste sin topes, weekly_limit/history_cap pueden ser None
        return MeLimitsOut(
            plan=plan_code,
            weekly_free_analyses=weekly_limit,
            history_cap=history_cap,
            used_this_week=used,
            resets_at=next_week_start,
        )

    async def get_usage_week(self, user_id) -> MeUsageWeekOut:
        week_start, next_week_start = week_window_lima()
        plan_code, weekly_limit, _ = await self._resolve_effective_limits(user_id)
        count = await self.usage.get_week_count(user_id, week_start.date())
        return MeUsageWeekOut(
            count=count,
            limit=weekly_limit,
            window_start=week_start,
            window_end=next_week_start,
        )
