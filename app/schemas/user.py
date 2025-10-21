from pydantic import BaseModel, HttpUrl
from typing import Optional

class UserOut(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str

    class Config:
        from_attributes = True  # pydantic v2

class UserUpdateIn(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
