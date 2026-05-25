"""
找教练 Agent —— 智能匹配专业运动教练。

外部 API 依赖:
  - 自建教练数据库 (推荐) — 建表 coaches，管理教练信息
  - 第三方平台接入:
      - Keep 教练平台: https://www.gotokeep.com  (无公开 API，需合作)
      - 乐刻运动: https://www.lefit.com  (无公开 API)
      - 超级猩猩: https://www.supermonkey.com.cn
  - MVP 方案: 本地数据库预填充 20-50 条教练数据

环境变量:
  COACH_DB_URL    - 教练数据库连接 (可复用主库)
  COACH_API_URL   - 第三方教练平台 API (可选)
"""

from agents.base import BaseAgent
from llm.factory import get_llm


class FindCoachAgent(BaseAgent):
    agent_type = "find-coach"
    display_name = "找教练"
    description = "智能匹配专业运动教练"
    group = "core"
    icon = "🎯"

    SYSTEM_PROMPT = """你是一个教练推荐助手。根据用户的运动项目、水平、目标和位置，推荐最合适的教练。
返回教练信息时请包含：
- 教练名称和评分
- 专长领域
- 匹配理由
- 参考价格

如果下面提供了真实的教练数据，请基于这些数据推荐。如果没有真实数据，请明确告知用户"当前暂无教练数据"。
请用专业、客观的语气回复。"""

    # ============================================================
    #  TODO: 接入教练数据库后，取消此方法的注释并实现
    # ============================================================
    #
    # async def _fetch_coaches(
    #     self, sport: str = "", city: str = "", level: str = ""
    # ) -> list[dict]:
    #     """
    #     从教练数据库按条件查询教练。
    #
    #     推荐方案: 自建 coaches 表
    #       SQLite 建表语句:
    #         CREATE TABLE coaches (
    #           id INTEGER PRIMARY KEY,
    #           name TEXT NOT NULL,          -- 教练姓名
    #           sport TEXT NOT NULL,         -- 运动项目 (篮球/健身/瑜伽...)
    #           city TEXT NOT NULL,          -- 所在城市
    #           level TEXT DEFAULT '全部',   -- 适合水平 (初级/中级/高级)
    #           rating REAL DEFAULT 5.0,     -- 评分 (1-5)
    #           specialties TEXT,            -- 专长, 逗号分隔
    #           price_per_session INTEGER,   -- 单次课时费(元)
    #           phone TEXT,                  -- 联系电话
    #           avatar_url TEXT              -- 头像
    #         );
    #
    #       预填充数据来源:
    #         - 手动录入合作教练
    #         - 爬取公开教练信息 (合规前提下)
    #
    #     备选方案: 第三方平台
    #         截止 2025 年，Keep/乐刻/超级猩猩 均无公开教练 API。
    #         接入需走商务合作渠道，联系各平台 BD。
    #     """
    #     import os
    #     from sqlalchemy import select
    #     from db.session import async_session
    #     from models.coach import Coach  # 需要先创建此 model
    #
    #     async with async_session() as db:
    #         query = select(Coach)
    #         if sport:
    #             query = query.where(Coach.sport == sport)
    #         if city:
    #             query = query.where(Coach.city == city)
    #         result = await db.execute(query)
    #         coaches = result.scalars().all()
    #         return [
    #             {
    #                 "name": c.name, "rating": c.rating,
    #                 "specialties": c.specialties, "price": c.price_per_session,
    #             }
    #             for c in coaches
    #         ]
    # ============================================================

    async def handle(self, message: str, attachments: list[str] = None) -> dict:
        # ---- 预留: 调用教练数据库 ----
        # coaches = await self._fetch_coaches(sport="篮球", city="北京", level="初级")
        # if coaches:
        #     data_context = f"\n\n以下是从教练数据库查询到的真实教练:\n{coaches}"
        #     messages = [{"role": "user", "content": message + data_context}]
        # else:
        #     messages = [{"role": "user", "content": message}]
        # ---- 当前: 仅 LLM 对话 (无真实数据) ----
        llm = get_llm()
        messages = [{"role": "user", "content": message}]
        reply = await llm.chat(messages, self.SYSTEM_PROMPT)

        return {
            "reply": reply,
            "structured": {"type": "coach_recommendations"},
        }
