# app/domain/repositories/sessions_repo.py
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.models import AuthSession

class SessionsRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, *, user_id, refresh_hash: str, jti: str, parent_jti: str | None,
                     expires_at: datetime, user_agent: str | None, ip: str | None) -> AuthSession:
        s = AuthSession(
            user_id=user_id,
            refresh_token_hash=refresh_hash,
            jti=jti,
            parent_jti=parent_jti,
            expires_at=expires_at,
            user_agent=user_agent,
            ip=ip
        )
        self.db.add(s)
        await self.db.flush()
        return s

    async def get_active_by_jti(self, jti: str) -> AuthSession | None:
        q = await self.db.execute(select(AuthSession).where(AuthSession.jti == jti, AuthSession.revoked_at.is_(None)))
        return q.scalar_one_or_none()

    async def revoke_chain(self, jti: str):
        # revoca el jti actual (puedes ampliar a la cadena si detectas replay)
        now = datetime.utcnow()
        await self.db.execute(
            update(AuthSession).where(AuthSession.jti == jti, AuthSession.revoked_at.is_(None)).values(revoked_at=now)
        )
