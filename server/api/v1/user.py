from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from db.session import get_db
from models.models import User
from core.exceptions import success_response
from api.v1.agents import get_current_user_id

router = APIRouter()


class ProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    fitness_goal: Optional[str] = None
    daily_calorie_goal: Optional[int] = None


@router.get("/profile")
async def get_profile(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    if user_id == "dev-user":
        return success_response({
            "id": "dev-user",
            "phone": "13800138000",
            "nickname": "用户",
            "avatar_url": "",
            "gender": "",
            "height_cm": 175,
            "weight_kg": 68.5,
            "fitness_goal": "增肌减脂",
            "daily_calorie_goal": 2200,
        })

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return success_response({"id": user_id, "nickname": "用户"})

    return success_response({
        "id": user.id,
        "phone": user.phone,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "gender": user.gender,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "fitness_goal": user.fitness_goal,
        "daily_calorie_goal": user.daily_calorie_goal,
    })


@router.put("/profile")
async def update_profile(
    req: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    if user_id == "dev-user":
        return success_response({"message": "开发模式，暂不保存"})

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        for key, value in req.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
    return success_response(None)
