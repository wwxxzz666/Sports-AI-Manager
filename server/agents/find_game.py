"""
帮我找局 Agent —— 运动活动/赛事推荐。

外部 API 依赖:
  - 大众点评运动健身类目 API: https://open.dianping.com  (需企业认证)
  - 微信小程序运动赛事接口: 微信公众平台 > 运动健康服务
  - 自建方案: 爬取 Keep/咕咚 公开活动页，存入本地数据库

环境变量:
  FIND_GAME_API_URL   - 活动数据源 URL
  FIND_GAME_API_KEY   - API 认证 Key
"""

from agents.base import BaseAgent
from llm.factory import get_llm


class FindGameAgent(BaseAgent):
    agent_type = "find-game"
    display_name = "帮我找局"
    description = "发现身边的运动活动和赛事"
    group = "core"
    icon = "🏀"

    SYSTEM_PROMPT = """你是一个运动活动推荐助手。根据用户的运动偏好、位置和时间，推荐合适的运动活动和赛事。
返回活动推荐时请包含以下信息：
- 活动名称
- 时间
- 地点
- 价格
- 名额
- 推荐理由

如果下面提供了真实的实时活动数据，请基于这些数据回复用户。
如果没有真实数据，请明确告知用户"当前暂无实时活动数据，建议直接查看大众点评或Keep等平台"。
请用友好、专业的语气回复。"""

    # ============================================================
    #  TODO: 接入真实活动 API 后，取消此方法的注释并实现
    # ============================================================
    #
    # async def _fetch_real_activities(self, sport: str, city: str, level: str = "") -> list[dict]:
    #     """
    #     从外部活动平台获取真实活动数据。
    #
    #     推荐接入方案（任选其一）:
    #
    #     方案A: 大众点评开放平台
    #       文档: https://open.dianping.com
    #       申请: 企业认证 → 运动健身类目 → 获取 app_key / app_secret
    #       接口: /v1/poi/sports/search  (按运动类型+城市筛选)
    #       费用: 免费额度 500次/天
    #
    #     方案B: 自建活动数据库 (推荐MVP方案)
    #       建表 events(id, title, sport_type, city, address, date, price, capacity, source)
    #       预填充本地场馆和常驻活动的数据
    #       定期通过爬虫/人工更新
    #
    #     方案C: 微信运动赛事 (小程序内)
    #       文档: https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/sport.html
    #       适合: 已有微信小程序的前端项目
    #     """
    #     import os, httpx
    #     api_url = os.getenv("FIND_GAME_API_URL", "")
    #     api_key = os.getenv("FIND_GAME_API_KEY", "")
    #
    #     if not api_url:
    #         return []
    #
    #     async with httpx.AsyncClient() as client:
    #         resp = await client.get(
    #             api_url,
    #             params={"sport": sport, "city": city, "level": level},
    #             headers={"Authorization": f"Bearer {api_key}"},
    #             timeout=10.0,
    #         )
    #         if resp.status_code == 200:
    #             return resp.json().get("activities", [])
    #     return []
    # ============================================================

    async def handle(self, message: str, attachments: list[str] = None) -> dict:
        # ---- 预留: 调用真实活动 API ----
        # activities = await self._fetch_real_activities(sport="篮球", city="北京")
        # if activities:
        #     # 将真实数据拼入 prompt 让 LLM 格式化输出
        #     data_context = f"\n\n以下是从活动平台获取的实时数据:\n{activities}"
        #     messages = [{"role": "user", "content": message + data_context}]
        # else:
        #     messages = [{"role": "user", "content": message}]
        # ---- 当前: 仅 LLM 对话 (无真实数据) ----
        llm = get_llm()
        messages = [{"role": "user", "content": message}]
        reply = await llm.chat(messages, self.SYSTEM_PROMPT)

        return {
            "reply": reply,
            "structured": {"type": "activity_recommendations"},
        }
