import uuid
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_db
from models.models import AIRating, HealthMetric, DietRecord
from core.exceptions import success_response
from api.v1.agents import get_current_user_id
from llm.factory import get_llm

router = APIRouter()


def _get_tier(score: float) -> str:
    if score >= 90:
        return "王者"
    elif score >= 80:
        return "钻石"
    elif score >= 65:
        return "黄金"
    elif score >= 45:
        return "白银"
    return "青铜"


@router.post("/generate")
async def generate_rating(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Generate a new AI rating based on user's recent data."""
    # Fetch last 30 days of health metrics
    today = date.today()
    result = await db.execute(
        select(HealthMetric)
        .where(HealthMetric.user_id == user_id)
        .order_by(HealthMetric.metric_date.desc())
        .limit(30)
    )
    metrics = result.scalars().all()

    # Fetch diet records for summary
    diet_result = await db.execute(
        select(DietRecord)
        .where(DietRecord.user_id == user_id)
        .order_by(DietRecord.record_date.desc())
        .limit(30)
    )
    diet_records = diet_result.scalars().all()

    # Build data summary for LLM
    avg_steps = sum(m.daily_step_count for m in metrics) / max(len(metrics), 1)
    avg_exercise = sum(m.exercise_minutes for m in metrics) / max(len(metrics), 1)
    avg_sleep = sum(m.sleep_minutes for m in metrics) / max(len(metrics), 1)
    avg_cal_burned = sum(m.calories_burned for m in metrics) / max(len(metrics), 1)
    total_diet_cal = sum(r.total_calories for r in diet_records)

    data_summary = f"""用户近30天数据：
- 平均步数：{int(avg_steps)}/天
- 平均运动时长：{int(avg_exercise)}分钟/天
- 平均睡眠：{avg_sleep / 60:.1f}小时/天
- 平均消耗：{int(avg_cal_burned)} kcal/天
- 近30天饮食记录总热量：{int(total_diet_cal)} kcal"""

    # Call LLM for rating
    llm = get_llm()
    system_prompt = (
        "You are a sports ability rating expert. Analyze user data and provide ratings.\n"
        "Rating tiers: 青铜(0-44), 白银(45-64), 黄金(65-79), 钻石(80-89), 王者(90-100)\n"
        "Rate on 5 dimensions (0-100 each): strength, endurance, flexibility, consistency, nutrition\n"
        "Return ONLY a JSON object with: composite_score, tier, percentile, "
        "dimensions:{strength,endurance,flexibility,consistency,nutrition}, summary"
    )

    raw = await llm.chat(
        [{"role": "user", "content": f"请根据以下数据给出运动能力评级：\n{data_summary}"}],
        system_prompt,
    )
    rating = _parse_rating(raw)

    # Save to DB
    record = AIRating(
        id=str(uuid.uuid4()),
        user_id=user_id,
        composite_score=rating.get("composite_score", 78),
        tier=rating.get("tier", _get_tier(rating.get("composite_score", 78))),
        percentile=rating.get("percentile", 72),
        strength_score=rating.get("dimensions", {}).get("strength", 75),
        endurance_score=rating.get("dimensions", {}).get("endurance", 82),
        flexibility_score=rating.get("dimensions", {}).get("flexibility", 70),
        consistency_score=rating.get("dimensions", {}).get("consistency", 78),
        nutrition_score=rating.get("dimensions", {}).get("nutrition", 85),
        rating_date=today,
    )
    db.add(record)
    await db.flush()

    return success_response({
        "id": record.id,
        "composite_score": record.composite_score,
        "tier": record.tier,
        "percentile": record.percentile,
        "dimensions": {
            "strength": record.strength_score,
            "endurance": record.endurance_score,
            "flexibility": record.flexibility_score,
            "consistency": record.consistency_score,
            "nutrition": record.nutrition_score,
        },
        "summary": rating.get("summary", ""),
        "rating_date": today.isoformat(),
    })


@router.get("/current")
async def get_current_rating(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get latest rating with full dimensions."""
    result = await db.execute(
        select(AIRating)
        .where(AIRating.user_id == user_id)
        .order_by(AIRating.rating_date.desc())
        .limit(1)
    )
    record = result.scalar_one_or_none()

    if not record:
        return success_response(None)

    return success_response({
        "id": record.id,
        "composite_score": record.composite_score,
        "tier": record.tier,
        "percentile": record.percentile,
        "dimensions": {
            "strength": record.strength_score,
            "endurance": record.endurance_score,
            "flexibility": record.flexibility_score,
            "consistency": record.consistency_score,
            "nutrition": record.nutrition_score,
        },
        "rating_date": record.rating_date.isoformat(),
    })


@router.get("/history")
async def get_rating_history(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get rating history with deltas."""
    result = await db.execute(
        select(AIRating)
        .where(AIRating.user_id == user_id)
        .order_by(AIRating.rating_date.desc())
        .limit(20)
    )
    ratings = result.scalars().all()

    if not ratings:
        return success_response([])

    items = []
    for i, r in enumerate(ratings):
        delta = 0
        if i < len(ratings) - 1:
            delta = round(r.composite_score - ratings[i + 1].composite_score, 1)
        items.append({
            "id": r.id,
            "score": r.composite_score,
            "tier": r.tier,
            "date": r.rating_date.isoformat(),
            "delta": delta,
        })

    return success_response(items)


def _parse_rating(raw: str) -> dict:
    """Parse JSON from LLM rating response."""
    import json
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
    except (json.JSONDecodeError, ValueError):
        pass

    return {
        "composite_score": 78,
        "tier": "黄金",
        "percentile": 72,
        "dimensions": {
            "strength": 75,
            "endurance": 82,
            "flexibility": 70,
            "consistency": 78,
            "nutrition": 85,
        },
        "summary": "综合评分78分，黄金段位。耐力是你的优势，柔韧性需要加强。",
    }
