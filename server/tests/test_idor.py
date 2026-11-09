"""会话越权（IDOR）回归测试。

历史问题：agent_chat / delete_conversation 只按 id 查会话，
不校验归属，知道别人的 conversation_id 就能读写/删除别人的会话。
"""

import uuid

import pytest
from sqlalchemy import select

from db.session import async_session
from models.models import Conversation, Message


async def _create_conversation(client, auth_headers, user_id: str) -> str:
    """让某个用户发一条消息，返回新建的 conversation_id。"""
    resp = await client.post(
        "/api/v1/agents/food-calories/chat",
        json={"message": "你好"},
        headers=auth_headers(user_id),
    )
    assert resp.status_code == 200, resp.text
    cid = resp.json()["data"]["conversation_id"]
    assert cid
    return cid


async def _conversation_exists(conversation_id: str) -> bool:
    async with async_session() as db:
        result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        return result.scalar_one_or_none() is not None


async def _message_count(conversation_id: str) -> int:
    async with async_session() as db:
        result = await db.execute(select(Message).where(Message.conversation_id == conversation_id))
        return len(result.scalars().all())


async def test_cannot_append_to_others_conversation(client, strict_auth, auth_headers):
    """B 拿 A 的 conversation_id 发消息，不能写进 A 的会话。"""
    alice_cid = await _create_conversation(client, auth_headers, "alice")
    before = await _message_count(alice_cid)

    resp = await client.post(
        "/api/v1/agents/food-calories/chat",
        json={"conversation_id": alice_cid, "message": "我是 bob，我来插一脚"},
        headers=auth_headers("bob"),
    )
    assert resp.status_code == 200, resp.text

    # B 应该被分到一个新会话，而不是写进 alice 的
    bob_cid = resp.json()["data"]["conversation_id"]
    assert bob_cid != alice_cid, "B 的请求被写进了 A 的会话（IDOR）"

    # A 的会话消息数不能变化
    assert await _message_count(alice_cid) == before, "A 的会话被外部写入"


async def test_cannot_read_others_conversation_list(client, strict_auth, auth_headers):
    """history 列表只返回自己的会话。"""
    alice_cid = await _create_conversation(client, auth_headers, "alice2")

    resp = await client.get(
        "/api/v1/agents/food-calories/history", headers=auth_headers("bob2")
    )
    assert resp.status_code == 200
    ids = [c["id"] for c in resp.json()["data"]]
    assert alice_cid not in ids


async def test_cannot_delete_others_conversation(client, strict_auth, auth_headers):
    """B 删除 A 的会话必须无效。"""
    alice_cid = await _create_conversation(client, auth_headers, "alice3")

    resp = await client.delete(
        f"/api/v1/agents/food-calories/history/{alice_cid}",
        headers=auth_headers("bob3"),
    )
    # 接口保持幂等（返回成功），但 A 的会话必须还在
    assert resp.status_code == 200, resp.text
    assert await _conversation_exists(alice_cid), "B 删掉了 A 的会话（IDOR）"


async def test_owner_can_delete_own_conversation(client, strict_auth, auth_headers):
    """正例：本人可以删自己的会话。"""
    alice_cid = await _create_conversation(client, auth_headers, "alice4")
    assert await _conversation_exists(alice_cid)

    resp = await client.delete(
        f"/api/v1/agents/food-calories/history/{alice_cid}",
        headers=auth_headers("alice4"),
    )
    assert resp.status_code == 200, resp.text
    assert not await _conversation_exists(alice_cid), "本人删除自己的会话失败"


async def test_delete_requires_auth(client, strict_auth):
    """删除接口现在必须有鉴权依赖。"""
    resp = await client.delete(f"/api/v1/agents/food-calories/history/{uuid.uuid4()}")
    assert resp.status_code == 401
