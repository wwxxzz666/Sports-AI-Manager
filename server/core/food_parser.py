"""从视觉模型返回里解析食物列表。

历史问题：这段逻辑原本在 agents/food_calories.py 和 api/v1/nutrition.py
各有一份，解析失败时都会返回写死的「米饭 + 红烧肉 + 清炒时蔬」。
用户上传任意图片（甚至不是食物）都会得到这份假营养数据，
界面看起来像识别成功，实际是编造的。

现在的约定：解析失败返回 []，由调用方明确告知用户"识别失败"。
"""

import json
import re

# 模型经常把 JSON 包在 ```json ... ``` 里
_FENCE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)

# 必备字段，缺任一视为不合格条目
_REQUIRED = ("name", "calories")


def parse_food_items(raw: str) -> list[dict]:
    """把模型返回解析成食物列表；无法解析时返回空列表。"""
    if not raw or not isinstance(raw, str):
        return []

    candidates = [raw, _FENCE.sub("", raw).strip()]

    # 兜底：截取第一个 [ 到最后一个 ] 之间的内容
    start, end = raw.find("["), raw.rfind("]")
    if start >= 0 and end > start:
        candidates.append(raw[start : end + 1])

    for text in candidates:
        try:
            data = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            continue

        if isinstance(data, dict):
            # 有些模型会包一层 {"items": [...]}
            data = data.get("items") or data.get("foods") or data.get("data")
        if not isinstance(data, list):
            continue

        items = [item for item in data if isinstance(item, dict) and all(k in item for k in _REQUIRED)]
        if items:
            return items

    return []
