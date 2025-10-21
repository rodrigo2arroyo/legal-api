# app/domain/repositories/usage_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from app.domain.models.models import UserUsageWindow

class UsageRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_week_count(self, user_id, week_start_date: date) -> int:
        q = (
            select(UserUsageWindow.analyses_count)
            .where(
                UserUsageWindow.user_id == user_id,
                UserUsageWindow.window_start == week_start_date
            )
            .limit(1)
        )
        res = await self.db.execute(q)
        val = res.scalar_one_or_none()
        return int(val or 0)
