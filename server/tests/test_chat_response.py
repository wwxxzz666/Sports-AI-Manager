"""agent_chat 响应字段回归测试。

历史问题：assistant_msg 只 db.add() 没有 flush，而 Message.id 是 ORM 层
default（uuid4），未 flush 时是 None，所以接口返回的 message_id 恒为 null。
"""

import uuid

from sqlalchemy import select

from db.session import async_session
from models.models import Message


async def test_chat_returns_non_null_message_id(client, strict_auth, auth_headers):
    resp = await client.post(
        "/api/v1/agents/food-calories/chat",
        json={"message": "你好"},
        headers=auth_headers("msg-user"),
    )
    assert resp.status_code == 200, resp.text

    data = resp.json()["data"]
    message_id = data["message_id"]
    assert message_id is not None, "message_id 仍然为 null"
    assert isinstance(message_id, str) and message_id

    # 拿到的 id 必须能在库里查到
    async with async_session() as db:
        result = await db.execute(select(Message).where(Message.id == message_id))
        msg = result.scalar_one_or_none()

    assert msg is not None, f"message_id={message_id} 在库里不存在"
    assert msg.role == "assistant"
    assert msg.conversation_id == data["conversation_id"]


async def test_chat_persists_both_messages(client, strict_auth, auth_headers):
    """一轮对话应落两条消息（user + assistant）。"""
    resp = await client.post(
        "/api/v1/agents/food-calories/chat",
        json={"message": "今天吃什么"},
        headers=auth_headers("msg-user2"),
    )
    assert resp.status_code == 200, resp.text
    conversation_id = resp.json()["data"]["conversation_id"]

    async with async_session() as db:
        result = await db.execute(
            select(Message).where(Message.conversation_id == conversation_id)
        )
        roles = sorted(m.role for m in result.scalars().all())

    assert roles == ["assistant", "user"], f"落库消息角色异常: {roles}"
