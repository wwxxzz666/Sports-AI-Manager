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
    # 单独控制 SQL 回显：原来写的是 echo=settings.DEBUG，
    # 生产开 DEBUG 会把每条 SQL（含用户数据）都打进日志
    SQL_ECHO: bool = False

    # Auth
    JWT_SECRET: str = "dev-secret-change-in-production"  # 非 DEBUG 模式下使用该默认值会在启动时报错
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for dev
    # 仅限本地开发：开启后未认证请求会被当成 dev-user 放行。
    # 生产环境必须保持 False，否则全站无鉴权。
    ALLOW_ANONYMOUS_USER: bool = False

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
