# app/utils/time_windows.py
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

TZ_LIMA = ZoneInfo("America/Lima")

def now_lima() -> datetime:
    return datetime.now(tz=TZ_LIMA)

def week_window_lima(ref: datetime | None = None) -> tuple[datetime, datetime]:
    """
    Devuelve (week_start, next_week_start) para la semana ISO en America/Lima.
    week_start = lunes 00:00:00, next_week_start = week_start + 7 días.
    """
    if ref is None:
        ref = now_lima()
    # Lunes=0 .. Domingo=6
    weekday = ref.weekday()
    # Fecha del lunes de esta semana en Lima
    monday_date = (ref - timedelta(days=weekday)).date()
    week_start = datetime.combine(monday_date, time(0, 0), tzinfo=TZ_LIMA)
    next_week_start = week_start + timedelta(days=7)
    return week_start, next_week_start
