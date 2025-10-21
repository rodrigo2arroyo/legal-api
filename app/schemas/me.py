# app/domain/schemas/me.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MeLimitsOut(BaseModel):
    plan: str
    weekly_free_analyses: Optional[int]  # None = ilimitado
    history_cap: Optional[int]           # None = ilimitado
    used_this_week: int
    resets_at: datetime                  # inicio de la próxima semana (America/Lima)

class MeUsageWeekOut(BaseModel):
    count: int
    limit: Optional[int]                 # None = ilimitado
    window_start: datetime               # lunes 00:00 America/Lima (inicio ventana)
    window_end: datetime                 # lunes siguiente 00:00 America/Lima (fin ventana)
