import logging
import uuid
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from config import settings
from db.session import get_db
from models.models import User, Conversation, Message
from core.security import decode_access_token
from core.exceptions import AuthenticationError, success_response
from agents.registry import get_agent, list_agents

router = APIRouter()
logger = logging.getLogger(__name__)

DEV_USER_ID = "dev-user"


def get_current_user_id(authorization: str = Header(default="")) -> str:
    """从 Bearer token 解析用户 id，解析失败一律拒绝。

    以前的实现在 token 无效时直接返回 "dev-user"，结果是全站无鉴权
    （本模块以及 health/nutrition/ratings/reports/uploads/user/motion
    共 19 处依赖关系都受影响）。现在只有显式打开
    ALLOW_ANONYMOUS_USER 才会回落到 dev-user（仅限本地开发）。
    """
    token = authorization.removeprefix("Bearer ").strip() if authorization else ""
    user_id = decode_access_token(token) if token else None
    if user_id:
        return user_id

    if settings.ALLOW_ANONYMOUS_USER:
        logger.warning(
            "未认证请求被放行到 %s（ALLOW_ANONYMOUS_USER=true，仅限本地开发，勿用于生产）",
            DEV_USER_ID,
        )
        return DEV_USER_ID

    raise AuthenticationError("未登录或登录已过期")


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    attachments: list[str] = []
    metadata: dict = {}


@router.get("")
async def get_agents():
    """List all available agents."""
    agents = list_agents()
    return success_response(agents)


@router.post("/{agent_type}/chat")
async def agent_chat(
    agent_type: str,
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Send a message to an agent and get a response."""
    agent = get_agent(agent_type)
    if not agent:
        return success_response({
            "conversation_id": req.conversation_id or str(uuid.uuid4()),
            "reply": f"抱歉，未找到名为 {agent_type} 的智能体。",
            "structured": None,
            "message_id": str(uuid.uuid4()),
        })

    # Get or create conversation
    # 必须同时按 user_id 过滤：否则只要知道别人的 conversation_id
    # 就能把消息写进别人的会话里读走上下文（IDOR）。
    conversation = None
    if req.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == req.conversation_id,
                Conversation.user_id == user_id,
                Conversation.agent_type == agent_type,
            )
        )
        conversation = result.scalar_one_or_none()

    if not conversation:
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            agent_type=agent_type,
            title=req.message[:20] if req.message else "",
        )
        db.add(conversation)
        await db.flush()

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=req.message,
        metadata_json=req.metadata if req.metadata else None,
    )
    db.add(user_msg)
    await db.flush()

    # Get agent response
    response = await agent.handle(req.message, req.attachments)

    # Save assistant message
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response["reply"],
        metadata_json=response.get("structured"),
    )
    db.add(assistant_msg)
    # 必须 flush 才能拿到 id：Message.id 是 ORM 层 default，只 add 不 flush 时
    # assistant_msg.id 还是 None，前端收到的 message_id 恒为 null
    await db.flush()

    return success_response({
        "conversation_id": conversation.id,
        "reply": response["reply"],
        "structured": response.get("structured"),
        "message_id": assistant_msg.id,
    })


@router.get("/{agent_type}/history")
async def get_history(
    agent_type: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get conversation history for an agent."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id, Conversation.agent_type == agent_type)
        .order_by(Conversation.created_at.desc())
    )
    conversations = result.scalars().all()
    return success_response([
        {
            "id": c.id,
            "agent_type": c.agent_type,
            "title": c.title,
            "created_at": c.created_at.isoformat(),
        }
        for c in conversations
    ])


@router.delete("/{agent_type}/history/{conversation_id}")
async def delete_conversation(
    agent_type: str,
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Delete a conversation."""
    # 带 user_id 过滤：原来只按 id 查，任何人知道 id 就能删别人的会话
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    conversation = result.scalar_one_or_none()
    if conversation:
        await db.delete(conversation)
    return success_response(None)
