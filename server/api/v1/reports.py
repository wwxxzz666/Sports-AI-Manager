from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_db
from models.models import AIRating
from core.exceptions import success_response
from api.v1.agents import get_current_user_id

router = APIRouter()


@router.get("/weekly")
async def get_weekly_report(
    week: str = "",
    user_id: str = Depends(get_current_user_id),
):
    # Return mock weekly report for demo
    return success_response({
        "week": week or "2026-W21",
        "workoutCount": 4,
        "totalDuration": 200,
        "totalCalories": 1680,
        "dietScore": 76,
        "sleepScore": 82,
        "highlight": "跑步配速提升了 8 秒/km",
        "suggestion": "增加柔韧性训练，注意补充蛋白质",
    })


@router.get("/rating-history")
async def get_rating_history(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(
        select(AIRating)
        .where(AIRating.user_id == user_id)
        .order_by(AIRating.rating_date.desc())
        .limit(20)
    )
    ratings = result.scalars().all()

    if not ratings:
        # Return mock data for demo
        return success_response([
            {"id": "1", "score": 78, "tier": "黄金", "date": "2026-05-18", "delta": 3},
            {"id": "2", "score": 75, "tier": "黄金", "date": "2026-05-11", "delta": 2},
            {"id": "3", "score": 73, "tier": "白银", "date": "2026-05-04", "delta": -1},
            {"id": "4", "score": 74, "tier": "白银", "date": "2026-04-27", "delta": 5},
            {"id": "5", "score": 69, "tier": "白银", "date": "2026-04-20", "delta": 0},
        ])

    return success_response([
        {
            "id": r.id,
            "score": r.composite_score,
            "tier": r.tier,
            "date": r.rating_date.isoformat(),
        }
        for r in ratings
    ])
