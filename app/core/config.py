import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

current_env = os.getenv("ENV", "dev")

env_file_map = {
    "dev": BASE_DIR / ".env.dev",
    "prd": BASE_DIR / ".env.prd",
}

env_path = env_file_map.get(current_env, BASE_DIR / ".env.dev")
load_dotenv(env_path, override=True)  # load correct file

print(f"Loaded env: {env_path} (ENV={current_env})")


# 2) Define settings model
class Settings(BaseSettings):
    ENV: str = "dev"
    DATABASE_URL: str

    JWT_PRIVATE: str
    JWT_ALG: str = "HS256"

    ACCESS_TTL_MIN: int = 15
    REFRESH_TTL_DAYS: int = 60

    class Config:
        # We already loaded from .env.dev with load_dotenv,
        # so we just read from the environment
        env_prefix = ""  # read variables as-is (DATABASE_URL, JWT_PRIVATE, etc.)


settings = Settings()
