from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_async import get_db
from app.api.core.authn import get_current_user
from app.domain.services.me_services import MeService
from app.schemas.me import MeLimitsOut, MeUsageWeekOut
from app.schemas.user import UserOut, UserUpdateIn
from app.domain.models.models import User

router = APIRouter()

@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return user

@router.patch("/me", response_model=UserOut)
async def update_me(
    payload: UserUpdateIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.name is not None:
        user.name = payload.name.strip() or user.name
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/me/limits", response_model=MeLimitsOut)
async def me_limits(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = MeService(db)
    return await svc.get_limits(user.id)

@router.get("/me/usage/week", response_model=MeUsageWeekOut)
async def me_usage_week(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = MeService(db)
    return await svc.get_usage_week(user.id)