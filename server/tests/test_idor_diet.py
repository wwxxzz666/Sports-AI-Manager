"""餐饮记录的越权（IDOR）回归测试。

历史问题：
- DELETE /nutrition/meal/{record_id}   只按 id 查，无鉴权依赖
- PUT    /health/diet/{record_id}/confirm  同上
知道 record_id 就能删/改别人的餐饮记录。
"""

import uuid
from datetime import date

import pytest
from sqlalchemy import select

from db.session import async_session
from models.models import DietRecord, FoodItem


async def _seed_meal(user_id: str, calories: float = 500) -> str:
    """直接落库造一条餐饮记录，避免依赖 LLM 链路。"""
    record_id = str(uuid.uuid4())
    async with async_session() as db:
        db.add(
            DietRecord(
                id=record_id,
                user_id=user_id,
                meal_type="lunch",
                total_calories=calories,
                confirmed=False,
                record_date=date.today(),
            )
        )
        db.add(
            FoodItem(
                id=str(uuid.uuid4()),
                diet_record_id=record_id,
                food_name="测试食物",
                calories=calories,
            )
        )
        await db.commit()
    return record_id


async def _get_record(record_id: str):
    async with async_session() as db:
        result = await db.execute(select(DietRecord).where(DietRecord.id == record_id))
        return result.scalar_one_or_none()


async def test_cannot_delete_others_meal(client, strict_auth, auth_headers):
    alice_record = await _seed_meal("alice-meal")

    resp = await client.delete(
        f"/api/v1/nutrition/meal/{alice_record}", headers=auth_headers("bob-meal")
    )
    assert resp.status_code == 200, resp.text

    assert await _get_record(alice_record) is not None, "B 删掉了 A 的餐饮记录（IDOR）"


async def test_owner_can_delete_own_meal(client, strict_auth, auth_headers):
    owner_record = await _seed_meal("carol-meal")

    resp = await client.delete(
        f"/api/v1/nutrition/meal/{owner_record}", headers=auth_headers("carol-meal")
    )
    assert resp.status_code == 200, resp.text

    assert await _get_record(owner_record) is None, "本人删除自己的记录失败"


async def test_cannot_confirm_others_diet_record(client, strict_auth, auth_headers):
    alice_record = await _seed_meal("alice-confirm")

    resp = await client.put(
        f"/api/v1/health/diet/{alice_record}/confirm", headers=auth_headers("bob-confirm")
    )
    assert resp.status_code == 200, resp.text

    record = await _get_record(alice_record)
    assert record is not None
    assert record.confirmed is False, "B 改掉了 A 的记录状态（IDOR）"


async def test_owner_can_confirm_own_diet_record(client, strict_auth, auth_headers):
    owner_record = await _seed_meal("carol-confirm")

    resp = await client.put(
        f"/api/v1/health/diet/{owner_record}/confirm", headers=auth_headers("carol-confirm")
    )
    assert resp.status_code == 200, resp.text

    record = await _get_record(owner_record)
    assert record is not None and record.confirmed is True


async def test_delete_meal_requires_auth(client, strict_auth):
    resp = await client.delete(f"/api/v1/nutrition/meal/{uuid.uuid4()}")
    assert resp.status_code == 401


async def test_confirm_diet_requires_auth(client, strict_auth):
    resp = await client.put(f"/api/v1/health/diet/{uuid.uuid4()}/confirm")
    assert resp.status_code == 401
