# app/services/auth_service.py
import os
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.users_repo import UsersRepo
from app.domain.repositories.sessions_repo import SessionsRepo
from app.api.core.security import (
    make_access_token, new_refresh_pair, hash_refresh, verify_refresh, REFRESH_TTL_DAYS
)
from app.domain.services.idp_verify import verify_google_id_token, verify_apple_id_token
from app.schemas.auth import SocialLoginIn, TokenPairOut

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UsersRepo(db)
        self.sessions = SessionsRepo(db)

    async def social_login(self, payload: SocialLoginIn) -> TokenPairOut:
        if payload.provider == "google":
            profile = await verify_google_id_token(payload.id_token)
        elif payload.provider == "apple":
            profile = await verify_apple_id_token(payload.id_token)
        else:
            raise ValueError("Unsupported provider")

        # 2) Buscar o crear usuario
        user = await self.users.get_by_provider(payload.provider, profile["provider_user_id"])
        if not user:
            user = await self.users.get_by_email(profile["email"])
        if not user:
            user = await self.users.create_with_identity(
                email=profile["email"],
                name=profile.get("name"),
                provider=payload.provider,
                provider_user_id=profile["provider_user_id"],
                email_verified=profile.get("email_verified", False),
                avatar_url=profile.get("avatar_url"),
            )

        # 3) Emitir tokens + crear sesión refresh
        access, ttl = make_access_token(str(user.id))
        raw_refresh, jti = new_refresh_pair()
        refresh_hash = hash_refresh(raw_refresh)

        from datetime import datetime, timezone, timedelta as td
        expires_at = datetime.now(tz=timezone.utc) + td(days=REFRESH_TTL_DAYS)

        await self.sessions.create(
            user_id=user.id,
            refresh_hash=refresh_hash,
            jti=jti,
            parent_jti=None,
            expires_at=expires_at,
            user_agent="login-social",
            ip=None
        )

        await self.db.commit()

        needs_profile = not bool(user.name)  # o si faltan otros campos obligatorios
        return TokenPairOut(
            access_token=access, refresh_token=raw_refresh, expires_in=ttl,
            needs_profile_completion=needs_profile
        )

    async def rotate_refresh(self, raw_refresh: str, user_agent: str | None, ip: str | None) -> TokenPairOut:
        # Estrategia: el jti viaja como parte del refresh (raw=... contiene jti? opcional).
        # Aquí, por simplicidad, buscamos por coincidencia de hash en sesiones activas.
        # En producción, incluye jti en el refresh (ej. raw="<jti>.<random>") y búscalo directo.
        # ---- Simplificado: escanea por jti si lo incluyes, o valida sobre la sesión actual.
        # Aquí asumimos que el cliente manda el jti en el propio token raw (prefijo).
        try:
            jti, _ = raw_refresh.split(".", 1)
        except Exception:
            raise ValueError("Malformed refresh token")

        session = await self.sessions.get_active_by_jti(jti)
        if not session:
            raise ValueError("Invalid or revoked refresh token")

        if not verify_refresh(raw_refresh, session.refresh_token_hash):
            # posible replay: revoca la cadena
            await self.sessions.revoke_chain(session.jti)
            await self.db.commit()
            raise ValueError("Refresh token mismatch")

        # Revoca el actual y crea uno nuevo (rotación)
        await self.sessions.revoke_chain(session.jti)

        access, ttl = make_access_token(str(session.user_id))
        new_raw, new_jti = new_refresh_pair()
        refresh_hash = hash_refresh(new_raw)

        from datetime import datetime, timezone, timedelta as td
        expires_at = datetime.now(tz=timezone.utc) + td(days=REFRESH_TTL_DAYS)

        await self.sessions.create(
            user_id=session.user_id,
            refresh_hash=refresh_hash,
            jti=new_jti,
            parent_jti=session.jti,
            expires_at=expires_at,
            user_agent=user_agent,
            ip=ip
        )

        await self.db.commit()
        return TokenPairOut(access_token=access, refresh_token=new_raw, expires_in=ttl)

    async def logout(self, raw_refresh: str, user_agent: str | None, ip: str | None):
        # 1) Validar formato
        try:
            jti, _ = raw_refresh.split(".", 1)
        except ValueError:
            # token mal formado → error controlado, no 500
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malformed refresh token",
            )

        # 2) Buscar sesión
        session = await self.sessions.get_active_by_jti(jti)
        if not session:
            # refresh ya revocado / no existe → no es error de servidor
            return

        # 3) Revocar cadena
        await self.sessions.revoke_chain(session.jti)
        await self.db.commit()

