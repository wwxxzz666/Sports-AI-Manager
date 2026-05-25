from fastapi import APIRouter

from api.v1 import auth, agents, health, uploads, reports, user, nutrition, motion, ratings

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(agents.router, prefix="/agents", tags=["智能体"])
api_router.include_router(health.router, prefix="/health", tags=["健康"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["上传"])
api_router.include_router(reports.router, prefix="/reports", tags=["报告"])
api_router.include_router(user.router, prefix="/user", tags=["用户"])
api_router.include_router(nutrition.router, prefix="/nutrition", tags=["营养"])
api_router.include_router(motion.router, prefix="/motion", tags=["动作分析"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["AI评级"])
