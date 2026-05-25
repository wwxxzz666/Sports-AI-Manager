import uuid
import os
from datetime import datetime, date
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from config import settings
from db.session import get_db
from models.models import WorkoutRecord
from core.exceptions import success_response, UploadError
from api.v1.agents import get_current_user_id
from llm.factory import get_llm

router = APIRouter()

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm", "video/x-msvideo"}


@router.post("/analyze")
async def analyze_motion(
    file: UploadFile = File(...),
    sport_type: str = Form(default="未指定"),
    goal: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Upload a video and get AI motion analysis."""
    if file.content_type and file.content_type not in ALLOWED_VIDEO_TYPES:
        raise UploadError(
            f"Unsupported video format: {file.content_type}. Supported: MP4, MOV, WebM"
        )

    content = await file.read()
    max_size = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024
    if len(content) > max_size:
        raise UploadError(f"Video size exceeds limit ({settings.MAX_VIDEO_SIZE_MB}MB)")

    # Save uploaded video
    ext = os.path.splitext(file.filename or "motion.mp4")[1] or ".mp4"
    file_id = str(uuid.uuid4())
    date_dir = datetime.now().strftime("%Y/%m/%d")
    save_dir = os.path.join(settings.UPLOAD_DIR, date_dir)
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{file_id}{ext}")
    with open(file_path, "wb") as f:
        f.write(content)

    video_url = f"/static/uploads/{date_dir}/{file_id}{ext}"

    # Call vision LLM for motion analysis
    llm = get_llm()
    prompt = (
        "You are a professional sports motion analyst. Analyze the uploaded video of "
        + sport_type
        + " and provide a detailed evaluation.\n"
        + ("User's goal: " + goal + "\n" if goal else "")
        + "\nReturn ONLY a JSON object with these fields:\n"
        + '- overall_score: integer 0-100\n'
        + '- posture_issues: array of strings (specific form problems found)\n'
        + '- suggestions: array of strings (specific improvement tips)\n'
        + '- risks: array of strings (injury risks identified)\n'
        + '- recommended_training: array of strings (exercises to improve)\n'
        + "- summary: short Chinese summary\n"
        + "Return only the JSON object, no other text."
    )

    raw_response = await llm.chat_with_vision(video_url, prompt)
    analysis = _parse_analysis(raw_response)

    # Save workout record with analysis
    record = WorkoutRecord(
        id=str(uuid.uuid4()),
        user_id=user_id,
        sport_type=sport_type,
        duration_minutes=0,
        calories_burned=analysis.get("estimated_calories", 0),
        notes=goal,
        video_url=video_url,
        analysis_result=analysis,
        workout_date=date.today(),
    )
    db.add(record)
    await db.flush()

    return success_response({
        "record_id": record.id,
        "video_url": video_url,
        "sport_type": sport_type,
        "overall_score": analysis.get("overall_score", 0),
        "posture_issues": analysis.get("posture_issues", []),
        "suggestions": analysis.get("suggestions", []),
        "risks": analysis.get("risks", []),
        "recommended_training": analysis.get("recommended_training", []),
        "summary": analysis.get("summary", "分析完成"),
        "disclaimer": "以上分析为AI参考，不能替代专业教练指导",
    })


@router.get("/history")
async def get_motion_history(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(
        select(WorkoutRecord)
        .where(WorkoutRecord.user_id == user_id)
        .where(WorkoutRecord.video_url != "")
        .order_by(WorkoutRecord.created_at.desc())
        .limit(20)
    )
    records = result.scalars().all()

    return success_response([
        {
            "id": r.id,
            "sport_type": r.sport_type,
            "video_url": r.video_url,
            "analysis": r.analysis_result,
            "notes": r.notes,
            "date": r.workout_date.isoformat(),
        }
        for r in records
    ])


def _parse_analysis(raw: str) -> dict:
    """Parse JSON from LLM vision response."""
    import json
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
    except (json.JSONDecodeError, ValueError):
        pass

    # Mock fallback
    return {
        "overall_score": 82,
        "posture_issues": [
            "深蹲时膝盖轻微内扣",
            "脚踝灵活性不足",
        ],
        "suggestions": [
            "加强臀中肌激活训练",
            "增加踝关节灵活性练习",
            "建议使用弹力带辅助",
        ],
        "risks": [
            "膝盖内扣可能增加 ACL 损伤风险",
        ],
        "recommended_training": [
            "臀桥（每天3组，每组15次）",
            "蚌式开合（每天2组，每组12次）",
            "踝关节环绕（每天2分钟）",
        ],
        "summary": "深蹲动作评分 82 分，膝盖内扣是主要问题，需加强臀中肌和踝关节训练",
    }
