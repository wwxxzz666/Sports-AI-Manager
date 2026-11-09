"""食物解析回归测试。

历史问题：这段解析逻辑在 agents/food_calories.py 和 api/v1/nutrition.py
各有一份，解析失败时都回退到写死的「米饭 + 红烧肉 + 清炒时蔬」，
用户上传任意图片（甚至不是食物）都得到这份假营养数据。
"""

import json

from agents.food_calories import FoodCaloriesAgent
from core.food_parser import parse_food_items

GOOD_ITEMS = [
    {"name": "牛排", "calories": 450, "protein_g": 40, "confidence": 0.9},
    {"name": "沙拉", "calories": 120, "protein_g": 3, "confidence": 0.85},
]


def test_parse_plain_json_array():
    assert parse_food_items(json.dumps(GOOD_ITEMS, ensure_ascii=False)) == GOOD_ITEMS


def test_parse_json_in_code_fence():
    raw = "```json\n" + json.dumps(GOOD_ITEMS, ensure_ascii=False) + "\n```"
    assert parse_food_items(raw) == GOOD_ITEMS


def test_parse_json_with_surrounding_text():
    raw = "好的，识别结果如下：\n" + json.dumps(GOOD_ITEMS, ensure_ascii=False) + "\n希望有帮助！"
    assert parse_food_items(raw) == GOOD_ITEMS


def test_parse_wrapped_in_items_key():
    raw = json.dumps({"items": GOOD_ITEMS}, ensure_ascii=False)
    assert parse_food_items(raw) == GOOD_ITEMS


def test_parse_garbage_returns_empty_not_mock():
    """关键回归：解析失败不能返回假数据。"""
    for raw in ("", None, "这不是 JSON", "{}", "[]", '{"error": true, "message": "不支持多模态"}'):
        result = parse_food_items(raw)  # type: ignore[arg-type]
        assert result == [], f"输入 {raw!r} 应返回空列表，实际 {result}"


def test_parse_filters_entries_missing_required_fields():
    raw = json.dumps([{"portion": "一碗"}, {"name": "面条", "calories": 300}], ensure_ascii=False)
    assert parse_food_items(raw) == [{"name": "面条", "calories": 300}]


class _GarbageLLM:
    async def chat_with_vision(self, image_url, prompt):
        return "抱歉，我看不清这张图"

    async def chat(self, messages, system_prompt=""):
        return "随便聊聊"


async def test_food_agent_reports_failure_without_fake_data(monkeypatch):
    """识别失败时不能返回米饭/红烧肉。"""
    monkeypatch.setattr("agents.food_calories.get_llm", lambda: _GarbageLLM())

    result = await FoodCaloriesAgent().handle(
        "识别这张图", attachments=["http://example.com/a.jpg"]
    )

    assert result["structured"]["recognized"] is False
    assert result["structured"]["items"] == []
    assert result["structured"]["total_calories"] == 0
    assert "米饭" not in result["reply"]
    assert "红烧肉" not in result["reply"]
