import hashlib
import os, time, uuid, bcrypt, jwt
from datetime import datetime, timedelta, timezone
from typing import Any

JWT_PRIVATE = os.getenv("JWT_PRIVATE", "dev-secret")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
ACCESS_TTL_MIN = int(os.getenv("ACCESS_TTL_MIN", "15"))
REFRESH_TTL_DAYS = int(os.getenv("REFRESH_TTL_DAYS", "60"))

def now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)

def make_access_token(sub: str, role: str = "user", plan: str = "free") -> tuple[str, int]:
    exp = now_utc() + timedelta(minutes=ACCESS_TTL_MIN)
    jti = str(uuid.uuid4())
    payload = {"sub": sub, "role": role, "plan": plan, "jti": jti, "exp": exp}
    token = jwt.encode(payload, JWT_PRIVATE, algorithm=JWT_ALG)
    return token, int(ACCESS_TTL_MIN * 60)

def hash_refresh(raw_refresh: str) -> str:
    digest = hashlib.sha256(raw_refresh.encode()).digest()
    return bcrypt.hashpw(digest, bcrypt.gensalt()).decode()

def verify_refresh(raw_refresh: str, hashed: str) -> bool:
    try:
        digest = hashlib.sha256(raw_refresh.encode()).digest()
        return bcrypt.checkpw(digest, hashed.encode())
    except Exception:
        return False

def new_refresh_pair() -> tuple[str, str]:
    raw = str(uuid.uuid4()) + "." + str(uuid.uuid4())
    jti = str(uuid.uuid4())
    return raw, jti
