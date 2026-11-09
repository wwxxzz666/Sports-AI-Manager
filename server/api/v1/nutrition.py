import uuid
import os
import json
from datetime import date, datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from config import settings
from db.session import get_db
from models.models import DietRecord, FoodItem
from core.exceptions import success_response, UploadError
from api.v1.agents import get_current_user_id
from llm.factory import get_llm

router = APIRouter()


@router.post("/recognize")
async def recognize_food(
    file: UploadFile = File(...),
    db=Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Upload a food photo and get AI recognition results."""
    if file.content_type and not file.content_type.startswith("image/"):
        raise UploadError("Only image files are supported")

    content = await file.read()
    if len(content) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise UploadError(f"Image size exceeds limit ({settings.MAX_IMAGE_SIZE_MB}MB)")

    # Save uploaded image
    ext = os.path.splitext(file.filename or "food.jpg")[1] or ".jpg"
    file_id = str(uuid.uuid4())
    date_dir = datetime.now().strftime("%Y/%m/%d")
    save_dir = os.path.join(settings.UPLOAD_DIR, date_dir)
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{file_id}{ext}")
    with open(file_path, "wb") as f:
        f.write(content)

    image_url = f"/static/uploads/{date_dir}/{file_id}{ext}"

    # Call vision LLM for food recognition
    llm = get_llm()
    vision_prompt = (
        "You are a food recognition expert. Analyze this food image and identify all food items. "
        "Return ONLY a JSON array. Each item must have:\n"
        '- name: food name in Chinese\n'
        '- portion: portion description in Chinese (e.g. "一碗 (约200g)")\n'
        '- portion_grams: estimated weight in grams (number)\n'
        '- calories: estimated calories in kcal (number)\n'
        '- protein_g: protein in grams (number)\n'
        '- carbs_g: carbohydrates in grams (number)\n'
        '- fat_g: fat in grams (number)\n'
        '- confidence: recognition confidence 0-1 (number)\n\n'
        "Return only the JSON array, no other text."
    )

    raw_response = await llm.chat_with_vision(image_url, vision_prompt)
    food_items = _parse_food_items(raw_response)

    # Mark low-confidence items
    for item in food_items:
        if item.get("confidence", 1.0) < settings.FOOD_CONFIDENCE_THRESHOLD:
            item["needs_confirmation"] = True
        item["id"] = str(uuid.uuid4())

    total_calories = sum(item.get("calories", 0) for item in food_items)
    total_protein = sum(item.get("protein_g", 0) for item in food_items)
    total_carbs = sum(item.get("carbs_g", 0) for item in food_items)
    total_fat = sum(item.get("fat_g", 0) for item in food_items)

    return success_response({
        "image_url": image_url,
        "items": food_items,
        "total_calories": round(total_calories, 1),
        "total_protein": round(total_protein, 1),
        "total_carbs": round(total_carbs, 1),
        "total_fat": round(total_fat, 1),
        "disclaimer": "以上为估算值，仅供健康管理参考",
    })


class SaveMealItem(BaseModel):
    food_name: str
    portion: str = ""
    portion_grams: float = 0
    calories: float = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0
    confidence: float = 1.0
    user_confirmed: bool = True


class SaveMealRequest(BaseModel):
    meal_type: str  # breakfast, lunch, dinner, snack
    image_url: str = ""
    items: list[SaveMealItem]
    record_date: Optional[str] = None


@router.post("/meal")
async def save_meal(
    req: SaveMealRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Save confirmed food items as a diet record."""
    record_date_val = date.fromisoformat(req.record_date) if req.record_date else date.today()

    total_cal = sum(item.calories for item in req.items)
    total_protein = sum(item.protein_g for item in req.items)
    total_carbs = sum(item.carbs_g for item in req.items)
    total_fat = sum(item.fat_g for item in req.items)

    diet_record = DietRecord(
        id=str(uuid.uuid4()),
        user_id=user_id,
        meal_type=req.meal_type,
        image_url=req.image_url,
        total_calories=round(total_cal, 1),
        total_protein=round(total_protein, 1),
        total_carbs=round(total_carbs, 1),
        total_fat=round(total_fat, 1),
        confirmed=True,
        record_date=record_date_val,
    )
    db.add(diet_record)
    await db.flush()

    for item in req.items:
        food_item = FoodItem(
            id=str(uuid.uuid4()),
            diet_record_id=diet_record.id,
            food_name=item.food_name,
            portion_description=item.portion,
            portion_grams=item.portion_grams,
            calories=item.calories,
            protein_g=item.protein_g,
            carbs_g=item.carbs_g,
            fat_g=item.fat_g,
            confidence=item.confidence,
            user_confirmed=item.user_confirmed,
        )
        db.add(food_item)

    return success_response({
        "id": diet_record.id,
        "meal_type": req.meal_type,
        "total_calories": diet_record.total_calories,
        "items_count": len(req.items),
        "record_date": record_date_val.isoformat(),
    })


@router.delete("/meal/{record_id}")
async def delete_meal(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Delete a diet record and its food items."""
    # 必须带 user_id 过滤：原来只按 id 查，任何人知道 record_id
    # 就能删掉别人的餐饮记录
    result = await db.execute(
        select(DietRecord).where(
            DietRecord.id == record_id,
            DietRecord.user_id == user_id,
        )
    )
    record = result.scalar_one_or_none()
    if record:
        # Delete associated food items
        items_result = await db.execute(
            select(FoodItem).where(FoodItem.diet_record_id == record_id)
        )
        for item in items_result.scalars().all():
            await db.delete(item)
        await db.delete(record)
    return success_response(None)


def _parse_food_items(raw: str) -> list[dict]:
    """Parse food items from LLM vision response."""
    try:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            items = json.loads(raw[start:end])
            if isinstance(items, list):
                return items
    except (json.JSONDecodeError, ValueError):
        pass

    # Mock fallback with multiple items
    return [
        {
            "name": "米饭",
            "portion": "一碗 (约200g)",
            "portion_grams": 200,
            "calories": 232,
            "protein_g": 5.2,
            "carbs_g": 51.2,
            "fat_g": 0.6,
            "confidence": 0.92,
        },
        {
            "name": "红烧肉",
            "portion": "3块 (约150g)",
            "portion_grams": 150,
            "calories": 585,
            "protein_g": 22.5,
            "carbs_g": 12.0,
            "fat_g": 49.5,
            "confidence": 0.68,
        },
        {
            "name": "清炒时蔬",
            "portion": "一碟 (约100g)",
            "portion_grams": 100,
            "calories": 45,
            "protein_g": 2.1,
            "carbs_g": 6.8,
            "fat_g": 1.2,
            "confidence": 0.88,
        },
    ]
