# app/domain/repositories/plans_repo.py
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from datetime import datetime, timezone
from app.domain.models.models import Plan, Subscription

class PlansRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_subscription_with_plan(self, user_id) -> Optional[tuple[Subscription, Plan]]:
        """
        Devuelve (subscription, plan) si hay una suscripción vigente (status active/in_trial y dentro del periodo).
        Si hay varias, toma la de mayor prioridad (por ahora, la más reciente).
        """
        now_utc = datetime.now(tz=timezone.utc)
        q = (
            select(Subscription, Plan)
            .join(Plan, Subscription.plan_id == Plan.id)
            .where(
                Subscription.user_id == user_id,
                Subscription.status.in_(("active", "in_trial")),
                # si hay fechas de periodo, valida vigencia
                (Subscription.current_period_start.is_(None) | (Subscription.current_period_start <= now_utc)),
                (Subscription.current_period_end.is_(None) | (Subscription.current_period_end > now_utc)),
            )
            .order_by(Subscription.created_at.desc())
            .limit(1)
        )
        res = await self.db.execute(q)
        row = res.first()
        if not row:
            return None
        return row[0], row[1]

    async def get_plan_by_code(self, code: str) -> Optional[Plan]:
        q = select(Plan).where(Plan.code == code, Plan.active.is_(True)).limit(1)
        res = await self.db.execute(q)
        return res.scalar_one_or_none()
