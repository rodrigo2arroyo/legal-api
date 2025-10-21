from pydantic import BaseModel, Field
from typing import Literal, Optional

Provider = Literal["google", "apple"]

class SocialLoginIn(BaseModel):
    provider: Provider
    id_token: str  # ID token del IdP (JWT)
    # opcionalmente: authorization_code para Apple con JWT poco persistente

class TokenPairOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    needs_profile_completion: bool = False

class RefreshIn(BaseModel):
    refresh_token: str
