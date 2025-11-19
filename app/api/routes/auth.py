from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_async import get_db
from app.schemas.auth import SocialLoginIn, TokenPairOut, RefreshIn
from app.domain.services.auth_service import AuthService

router = APIRouter()

@router.post("/social", response_model=TokenPairOut)
async def social_login(payload: SocialLoginIn, db: AsyncSession = Depends(get_db)):
    """
    Recibe id_token de Google/Apple => verifica => crea/encuentra user =>
    crea sesión (refresh) => emite access+refresh (rotables).
    """
    service = AuthService(db)
    try:
        return await service.social_login(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/refresh", response_model=TokenPairOut)
async def refresh_tokens(payload: RefreshIn, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Rotación segura: recibe refresh, invalida el anterior y emite par nuevo.
    """
    ua = request.headers.get("user-agent", "unknown")
    ip = request.client.host if request.client else None
    service = AuthService(db)
    try:
        return await service.rotate_refresh(payload.refresh_token, user_agent=ua, ip=ip)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/logout")
async def logout(
    refresh: RefreshIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    ua = request.headers.get("user-agent", "unknown")
    ip = request.client.host if request.client else None
    service = AuthService(db)

    try:
        await service.logout(refresh.refresh_token, user_agent=ua, ip=ip)
        return {"ok": True}
    except HTTPException:
        # Re-levanta los HTTPException tal cual (400/401/403, etc.)
        raise
    except Exception as e:
        # Mientras debuggeas: loguea el error
        import traceback
        print("LOGOUT ERROR:", repr(e))
        traceback.print_exc()
        # Y devuelve un JSON de error (no "Internal Server Error" plano)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        )