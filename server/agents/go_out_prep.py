"""
出门准备 Agent —— 天气查询 + 运动出行装备建议。

外部 API 依赖:
  - 和风天气 API: https://dev.qweather.com  (推荐，国内最稳定)
  - OpenWeatherMap: https://openweathermap.org/api  (国际通用)
  - 高德天气 API: https://lbs.amap.com/api/webservice/guide/api/weatherinfo

环境变量:
  WEATHER_API_PROVIDER - 天气服务商 (qweather | openweather | amap)
  WEATHER_API_KEY      - API Key

免费额度:
  和风天气: 1000次/天, 支持 3 天预报
  OpenWeatherMap: 1000次/天, 当前天气 + 5 天预报
  高德天气: 100000次/天, 4 天预报
"""

from agents.base import BaseAgent
from llm.factory import get_llm


class GoOutPrepAgent(BaseAgent):
    agent_type = "go-out-prep"
    display_name = "出门准备"
    description = "运动出行天气与装备建议"
    group = "health"
    icon = "🌤️"

    SYSTEM_PROMPT = """你是一个运动出行准备助手。根据用户的运动计划和当前天气情况，提供出行准备建议。
回复应包含：
1. 天气概况（温度、风力、紫外线等）
2. 推荐装备清单
3. 风险提示
4. 安全建议

如果下面提供了真实的天气数据，请基于这些数据回复。
如果没有真实天气数据，请明确告知用户"暂未获取到实时天气，以下为通用建议"。
请用实用、简洁的语言回复。"""

    # ============================================================
    #  TODO: 接入天气 API 后，取消此方法的注释并实现
    # ============================================================
    #
    # async def _fetch_weather(self, city: str = "北京") -> dict | None:
    #     """
    #     从天气服务商获取实时天气。
    #
    #     推荐: 和风天气 (qweather.com) — 国内免费额度充足
    #
    #     1. 注册 https://dev.qweather.com
    #     2. 创建应用 → 获取 API Key
    #     3. 调用接口:
    #        GET https://devapi.qweather.com/v7/weather/now?location={city}&key={KEY}
    #        GET https://devapi.qweather.com/v7/weather/3d?location={city}&key={KEY}
    #
    #     返回示例:
    #     {
    #       "now": {
    #         "temp": "22", "feelsLike": "20", "humidity": "65",
    #         "windDir": "北风", "windScale": "3", "text": "晴"
    #       }
    #     }
    #
    #     备选方案:
    #     - OpenWeatherMap: api.openweathermap.org/data/2.5/weather?q={city}&appid={KEY}&units=metric
    #     - 高德天气:   restapi.amap.com/v3/weather/weatherInfo?city={adcode}&key={KEY}
    #     """
    #     import os, httpx
    #     provider = os.getenv("WEATHER_API_PROVIDER", "")
    #     api_key = os.getenv("WEATHER_API_KEY", "")
    #
    #     if not api_key:
    #         return None
    #
    #     if provider == "qweather":
    #         url = f"https://devapi.qweather.com/v7/weather/now"
    #         async with httpx.AsyncClient() as client:
    #             resp = await client.get(url, params={"location": city, "key": api_key})
    #             if resp.status_code == 200:
    #                 return resp.json()
    #
    #     elif provider == "openweather":
    #         url = "https://api.openweathermap.org/data/2.5/weather"
    #         async with httpx.AsyncClient() as client:
    #             resp = await client.get(url, params={"q": city, "appid": api_key, "units": "metric", "lang": "zh_cn"})
    #             if resp.status_code == 200:
    #                 return resp.json()
    #
    #     elif provider == "amap":
    #         url = "https://restapi.amap.com/v3/weather/weatherInfo"
    #         async with httpx.AsyncClient() as client:
    #             resp = await client.get(url, params={"city": city, "key": api_key})
    #             if resp.status_code == 200:
    #                 return resp.json()
    #
    #     return None
    # ============================================================

    async def handle(self, message: str, attachments: list[str] = None) -> dict:
        # ---- 预留: 调用天气 API ----
        # weather = await self._fetch_weather(city="北京")
        # if weather:
        #     data_context = f"\n\n以下是从天气服务商获取的实时天气数据:\n{weather}"
        #     messages = [{"role": "user", "content": message + data_context}]
        # else:
        #     messages = [{"role": "user", "content": message}]
        # ---- 当前: 仅 LLM 对话 (无实时天气) ----
        llm = get_llm()
        messages = [{"role": "user", "content": message}]
        reply = await llm.chat(messages, self.SYSTEM_PROMPT)

        return {
            "reply": reply,
            "structured": {
                "type": "go_out_prep",
                "weather": {},
                "equipment": [],
                "risks": [],
                "safety_suggestions": [],
            },
        }
