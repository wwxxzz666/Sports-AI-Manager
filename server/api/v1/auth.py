from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from db.session import get_db
from models.models import User
from core.security import hash_password, verify_password, create_access_token
from core.exceptions import AuthenticationError, success_response

router = APIRouter()


class RegisterRequest(BaseModel):
    phone: str
    password: str
    nickname: str = "用户"


class LoginRequest(BaseModel):
    phone: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    user_id: str
    nickname: str


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if phone exists
    result = await db.execute(select(User).where(User.phone == req.phone))
    if result.scalar_one_or_none():
        raise AuthenticationError("该手机号已注册")

    user = User(
        phone=req.phone,
        nickname=req.nickname,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    await db.flush()

    token = create_access_token(user.id)
    return success_response({
        "access_token": token,
        "user_id": user.id,
        "nickname": user.nickname,
    })


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.phone == req.phone))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise AuthenticationError("手机号或密码错误")

    token = create_access_token(user.id)
    return success_response({
        "access_token": token,
        "user_id": user.id,
        "nickname": user.nickname,
    })
