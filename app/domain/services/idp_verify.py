# app/services/idp_verify.py
from typing import TypedDict, Literal

class IdpProfile(TypedDict):
    provider_user_id: str
    email: str
    email_verified: bool
    name: str | None
    avatar_url: str | None

async def verify_google_id_token(id_token: str) -> IdpProfile:
    # TODO: validar firma/iss/aud/exp con JWKS oficial de Google
    # De momento, levanta error si el token parece inválido
    if not id_token or len(id_token) < 20:
        raise ValueError("Invalid Google ID token")
    # MOCK: reemplazar por verificación real
    return {
        "provider_user_id": "google|mocksub",
        "email": "mock@example.com",
        "email_verified": True,
        "name": "Mock User",
        "avatar_url": None,
    }

async def verify_apple_id_token(id_token: str) -> IdpProfile:
    # TODO: validar firma/iss/aud/exp con JWKS de Apple
    if not id_token or len(id_token) < 20:
        raise ValueError("Invalid Apple ID token")
    return {
        "provider_user_id": "apple|mocksub",
        "email": "mock@example.com",
        "email_verified": True,
        "name": "Mock User",
        "avatar_url": None,
    }
