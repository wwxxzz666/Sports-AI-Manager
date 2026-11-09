from datetime import date
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from db.session import get_db
from models.models import DietRecord, FoodItem, HealthMetric
from core.exceptions import success_response
from api.v1.agents import get_current_user_id

router = APIRouter()


class SaveMetricsRequest(BaseModel):
    steps: Optional[int] = None
    sleep_minutes: Optional[int] = None
    exercise_minutes: Optional[int] = None
    weight_kg: Optional[float] = None
    heart_rate_avg: Optional[int] = None
    calories_burned: Optional[int] = None


@router.post("/metrics")
async def save_health_metrics(
    req: SaveMetricsRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Save or update today's health metrics."""
    today = date.today()
    result = await db.execute(
        select(HealthMetric).where(
            HealthMetric.user_id == user_id,
            HealthMetric.metric_date == today,
        )
    )
    metric = result.scalar_one_or_none()

    if not metric:
        metric = HealthMetric(
            id=str(uuid.uuid4()),
            user_id=user_id,
            metric_date=today,
        )
        db.add(metric)

    if req.steps is not None:
        metric.daily_step_count = req.steps
    if req.sleep_minutes is not None:
        metric.sleep_minutes = req.sleep_minutes
    if req.exercise_minutes is not None:
        metric.exercise_minutes = req.exercise_minutes
    if req.weight_kg is not None:
        metric.weight_kg = req.weight_kg
    if req.heart_rate_avg is not None:
        metric.heart_rate_avg = req.heart_rate_avg
    if req.calories_burned is not None:
        metric.calories_burned = req.calories_burned

    await db.flush()
    return success_response({"metric_date": today.isoformat()})


@router.get("/metrics")
async def get_health_metrics(
    metric_date: str = "",
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    target_date = date.fromisoformat(metric_date) if metric_date else date.today()
    result = await db.execute(
        select(HealthMetric).where(
            HealthMetric.user_id == user_id,
            HealthMetric.metric_date == target_date,
        )
    )
    metric = result.scalar_one_or_none()

    if metric:
        data = {
            "steps": metric.daily_step_count,
            "heartRate": metric.heart_rate_avg,
            "sleepMinutes": metric.sleep_minutes,
            "caloriesBurned": metric.calories_burned,
            "exerciseMinutes": metric.exercise_minutes,
            "weight": metric.weight_kg or 0,
        }
    else:
        # Return mock data for demo
        data = {
            "steps": 6842,
            "heartRate": 72,
            "sleepMinutes": 450,
            "caloriesBurned": 328,
            "exerciseMinutes": 35,
            "weight": 68.5,
        }
    return success_response(data)


@router.get("/diet/today")
async def get_today_diet(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    today = date.today()
    result = await db.execute(
        select(DietRecord).where(
            DietRecord.user_id == user_id,
            DietRecord.record_date == today,
        )
    )
    records = result.scalars().all()

    total_calories = sum(r.total_calories for r in records)
    total_protein = sum(r.total_protein for r in records)
    total_carbs = sum(r.total_carbs for r in records)
    total_fat = sum(r.total_fat for r in records)

    meals = []
    for r in records:
        items_result = await db.execute(
            select(FoodItem).where(FoodItem.diet_record_id == r.id)
        )
        items = items_result.scalars().all()
        meals.append({
            "id": r.id,
            "mealType": r.meal_type,
            "imageUrl": r.image_url,
            "totalCalories": r.total_calories,
            "items": [
                {
                    "id": item.id,
                    "foodName": item.food_name,
                    "portion": item.portion_description,
                    "portionGrams": item.portion_grams,
                    "calories": item.calories,
                    "proteinG": item.protein_g,
                    "carbsG": item.carbs_g,
                    "fatG": item.fat_g,
                    "confidence": item.confidence,
                    "userConfirmed": item.user_confirmed,
                }
                for item in items
            ],
            "recordDate": r.record_date.isoformat(),
            "confirmed": r.confirmed,
        })

    return success_response({
        "totalCalories": total_calories,
        "goalCalories": 2200,
        "protein": total_protein,
        "carbs": total_carbs,
        "fat": total_fat,
        "meals": meals,
    })


@router.put("/diet/{record_id}/confirm")
async def confirm_diet_record(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    # 必须带 user_id 过滤：原来只按 id 查，任何人知道 record_id
    # 就能修改别人的餐饮记录
    result = await db.execute(
        select(DietRecord).where(
            DietRecord.id == record_id,
            DietRecord.user_id == user_id,
        )
    )
    record = result.scalar_one_or_none()
    if record:
        record.confirmed = True
    return success_response(None)
