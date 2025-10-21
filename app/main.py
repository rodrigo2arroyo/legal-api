# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.db_async import engine
from app.api.routes.auth import router as auth_router
from app.api.routes.me import router as me_router
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await engine.dispose()

app = FastAPI(title="Legal Risk AI", lifespan=lifespan)

# CORS (ajusta orígenes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod especifica
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(me_router, tags=["me"])

@app.get("/")
async def root():
    return {"ok": True}
