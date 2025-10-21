# app/domain/repositories/users_repo.py
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.models import User, UserIdentity

class UsersRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        q = await self.db.execute(select(User).where(User.email == email))
        return q.scalar_one_or_none()

    async def get_by_provider(self, provider: str, provider_user_id: str) -> User | None:
        q = await self.db.execute(
            select(User).join(UserIdentity).where(
                UserIdentity.provider == provider,
                UserIdentity.provider_user_id == provider_user_id
            )
        )
        return q.scalar_one_or_none()

    async def create_with_identity(self, *, email: str, name: str | None,
                                   provider: str, provider_user_id: str,
                                   email_verified: bool, avatar_url: str | None) -> User:
        user = User(email=email, name=name, avatar_url=avatar_url)
        self.db.add(user)
        await self.db.flush()
        ident = UserIdentity(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            email_verified=email_verified,
            raw_profile=None
        )
        self.db.add(ident)
        await self.db.flush()
        return user
