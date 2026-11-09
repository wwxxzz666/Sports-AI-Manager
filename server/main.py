import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from db.session import init_db
from api.router import api_router
from llm.factory import close_llm

logger = logging.getLogger(__name__)

# 这些都是"复制 .env.example 就上线"会踩到的默认值
UNSAFE_JWT_SECRETS = {
    "",
    "dev-secret-change-in-production",
    "change-me-to-a-random-string",
}


def validate_settings() -> None:
    """生产模式下拒绝明显不安全的默认配置。

    只在 DEBUG=false 时生效，避免打断本地开发。
    """
    if settings.DEBUG:
        return

    if settings.JWT_SECRET in UNSAFE_JWT_SECRETS:
        raise RuntimeError(
            "JWT_SECRET 仍是默认值，生产环境必须设置为随机字符串。"
            "请修改 server/.env 中的 JWT_SECRET。"
        )

    if settings.ALLOW_ANONYMOUS_USER:
        logger.error(
            "ALLOW_ANONYMOUS_USER=true 但 DEBUG=false：所有未认证请求会被"
            "当成同一个 dev-user 处理，请立即关闭该开关。"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    validate_settings()
    os.makedirs("data", exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    await init_db()
    yield
    # Shutdown
    await close_llm()


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# API Routes
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
