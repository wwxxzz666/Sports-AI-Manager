# 后端服务

FastAPI 后端，提供 AI Agent 对话、健康数据管理、饮食记录、动作分析、评级系统等 API。

## 安装

```bash
cd server
pip install -r requirements.txt
```

## 配置

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 填写必要配置：

```env
# LLM — 必填
LLM_PROVIDER=deepseek        # deepseek | qwen
LLM_API_KEY=sk-your-key      # DeepSeek 或 通义千问 API Key

# 可选: 第三方 API
WEATHER_API_KEY=             # 和风天气 API Key (go-out-prep Agent)
FIND_GAME_API_KEY=           # 活动平台 API Key (find-game Agent)
```

## 启动

```bash
python main.py
```

服务运行在 `http://localhost:8000`，自动建表（SQLite）。

API 文档：`http://localhost:8000/docs`

## API 端点

### 智能体对话

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/agents` | 获取所有 Agent 列表 |
| POST | `/api/v1/agents/{type}/chat` | 发送消息给指定 Agent |

### 饮食记录

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/nutrition/recognize` | 拍照识别食物 |
| POST | `/api/v1/nutrition/meals` | 保存餐食记录 |
| GET  | `/api/v1/nutrition/meals/today` | 查询今日饮食 |

### 健康数据

| 方法 | 路径 | 说明 |
|------|------|------|
| GET  | `/api/v1/health/metrics` | 获取健康指标 |
| POST | `/api/v1/health/metrics` | 手动录入健康数据 |
| GET  | `/api/v1/health/diet/summary` | 今日饮食摘要 |

### 动作分析

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/motion/analyze` | 上传视频 + AI 动作分析 |
| GET  | `/api/v1/motion/history` | 分析历史记录 |

### AI 评级

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/ratings/generate` | 生成最新评级 |
| GET  | `/api/v1/ratings/current` | 当前评级 |
| GET  | `/api/v1/ratings/history` | 历史评级记录 |

## Agent 开发

新增 Agent 需继承 `BaseAgent`，参考 `agents/find_game.py`：

```python
from agents.base import BaseAgent
from llm.factory import get_llm

class MyAgent(BaseAgent):
    agent_type = "my-agent"
    display_name = "我的智能体"
    description = "描述"
    group = "core"
    icon = "🤖"

    SYSTEM_PROMPT = "你是一个..."  # 系统提示词

    async def handle(self, message: str, attachments=None) -> dict:
        llm = get_llm()
        reply = await llm.chat([{"role": "user", "content": message}], self.SYSTEM_PROMPT)
        return {"reply": reply, "structured": {"type": "my_agent"}}
```

然后在 `agents/registry.py` 中注册即可。

## LLM Provider 扩展

要添加新的大模型（如 Claude、Gemini），在 `llm/` 下创建客户端继承 `BaseLLMProvider`，在 `llm/factory.py` 中注册。

当前支持：
- **DeepSeek** (`deepseek-chat`) — 纯文本，默认
- **通义千问** (`qwen-max` / `qwen-vl-max`) — 文本 + 多模态
