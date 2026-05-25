import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File

from config import settings
from core.exceptions import success_response, UploadError
from api.v1.agents import get_current_user_id
from db.session import get_db
from models.models import UploadedFile

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm"}


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    db=Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise UploadError(f"不支持的图片格式: {file.content_type}")

    # Check file size
    content = await file.read()
    if len(content) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise UploadError(f"图片大小超过限制 ({settings.MAX_IMAGE_SIZE_MB}MB)")

    # Save file
    ext = os.path.splitext(file.filename or "image.jpg")[1]
    file_id = str(uuid.uuid4())
    date_dir = datetime.now().strftime("%Y/%m/%d")
    save_dir = os.path.join(settings.UPLOAD_DIR, date_dir)
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, f"{file_id}{ext}")
    with open(file_path, "wb") as f:
        f.write(content)

    # Save to DB
    uploaded = UploadedFile(
        id=file_id,
        user_id=user_id,
        file_type="image",
        original_name=file.filename or "image.jpg",
        storage_path=file_path,
        mime_type=file.content_type or "image/jpeg",
        size_bytes=len(content),
    )
    db.add(uploaded)

    url = f"/static/uploads/{date_dir}/{file_id}{ext}"
    return success_response({
        "file_id": file_id,
        "url": url,
        "thumbnail_url": url,
    })


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    db=Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise UploadError(f"不支持的视频格式: {file.content_type}")

    content = await file.read()
    if len(content) > settings.MAX_VIDEO_SIZE_MB * 1024 * 1024:
        raise UploadError(f"视频大小超过限制 ({settings.MAX_VIDEO_SIZE_MB}MB)")

    ext = os.path.splitext(file.filename or "video.mp4")[1]
    file_id = str(uuid.uuid4())
    date_dir = datetime.now().strftime("%Y/%m/%d")
    save_dir = os.path.join(settings.UPLOAD_DIR, date_dir)
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(save_dir, f"{file_id}{ext}")
    with open(file_path, "wb") as f:
        f.write(content)

    uploaded = UploadedFile(
        id=file_id,
        user_id=user_id,
        file_type="video",
        original_name=file.filename or "video.mp4",
        storage_path=file_path,
        mime_type=file.content_type or "video/mp4",
        size_bytes=len(content),
    )
    db.add(uploaded)

    url = f"/static/uploads/{date_dir}/{file_id}{ext}"
    return success_response({
        "file_id": file_id,
        "url": url,
    })
