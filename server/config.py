from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Server
    APP_NAME: str = "AI运动管家"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/sports_manager.db"

    # Auth
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for dev

    # LLM Provider
    LLM_PROVIDER: str = "deepseek"
    LLM_MODEL: str = "deepseek-chat"
    LLM_VISION_MODEL: str = "qwen-vl-max"
    LLM_BASE_URL: str | None = None
    LLM_API_KEY: str = ""
    LLM_API_SECRET: str | None = None

    # Fallback LLM
    LLM_FALLBACK_PROVIDER: str | None = None
    LLM_FALLBACK_MODEL: str | None = None
    LLM_FALLBACK_API_KEY: str | None = None

    # Storage
    STORAGE_BACKEND: str = "local"
    UPLOAD_DIR: str = "./uploads"
    MAX_IMAGE_SIZE_MB: int = 10
    MAX_VIDEO_SIZE_MB: int = 100

    # Feature flags
    ENABLE_AI_RATING: bool = True
    ENABLE_MOTION_ANALYSIS: bool = True
    FOOD_CONFIDENCE_THRESHOLD: float = 0.7

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
