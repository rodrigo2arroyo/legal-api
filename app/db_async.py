# app/db_async.py
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.domain.models.models import Base
from app.core.config import settings

print(settings.DATABASE_URL)
DATABASE_URL = settings.DATABASE_URL

# Engine global (una sola instancia por proceso)
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    future=True,
)

# Session factory async
SessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Dependencia para FastAPI
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# (Opcional) ping de salud
async def db_healthcheck() -> bool:
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
