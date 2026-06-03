# AI 运动管家 (Sports AI Manager)

<p align="center">
  <img src="https://img.shields.io/badge/Vue-3.5-4fc08d?logo=vue.js" alt="Vue">
  <img src="https://img.shields.io/badge/Vite-6.x-646cff?logo=vite" alt="Vite">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.11+-3776ab?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/LLM-DeepSeek|Qwen-ff6b6b" alt="LLM">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT">
  <img src="https://img.shields.io/github/stars/wwxxzz666/Sports-AI-Manager?style=social" alt="Stars">
</p>

<p align="center">
  <b>An intelligent sports management H5 app with 11 AI Agents — covering diet tracking, workout analysis, AI rating, rehab guidance, and more.</b>
</p>

---

一个基于 Vue 3 + FastAPI 的智能运动管家 H5 应用，集成 **11 个 AI Agent**，覆盖饮食识别、运动打卡、动作分析、AI 评级、康复指导、找局约球、天气装备推荐等全方位运动管理场景。

## 功能概览

| 页面 | 功能 |
|------|------|
| 🏠 **首页** | 健康概览、快捷智能体、AI 对话（自动路由到对应 Agent） |
| 💬 **对话** | 11 个 Agent 独立对话，支持流式响应 |
| 🍎 **饮食记录** | 拍照识别食物热量、三餐记录、营养素分析 |
| ❤️ **健康中心** | 步数/心率/睡眠/体重手动录入、饮食摄入追踪、设备连接 |
| 📹 **动作分析** | 上传运动视频，AI 分析姿态、评分、风险提示 |
| 🏆 **AI 评级** | 五维能力雷达图、段位系统（青铜→王者）、历史趋势 |
| 🤖 **智能体市场** | Agent 列表浏览、搜索、快捷入口 |

## 11 个 AI Agent

| Agent | 简介 | 多模态 |
|-------|------|--------|
| `food-calories` 🍎 | 拍照识别食物，计算热量与三大营养素 | ✅ |
| `workout-checkin` 💪 | 运动打卡记录，进度追踪 | |
| `find-game` 🏀 | 发现身边运动活动和赛事 | |
| `find-coach` 🎯 | 智能匹配专业教练 | |
| `motion-analysis` 🎬 | AI 视频分析运动动作姿态 | ✅ |
| `ai-rating` 🏆 | 综合评估运动能力等级 | |
| `go-out-prep` 🌤️ | 天气查询 + 运动出行装备建议 | |
| `rehab-coach` 🩺 | 运动损伤康复指导方案 | |
| `user-profile` 👤 | 个人健康数据画像分析 | |
| `weekly-report` 📊 | 每周运动健康数据总结 | |
| `leave-replacement` 📅 | 请假后运动计划调整 | |

## 技术栈

**前端**
- Vue 3 (Composition API + `<script setup>`)
- Vite 6 + TypeScript
- Vant 4 (移动端 UI)
- Pinia (状态管理 + 持久化)
- Vue Router 4
- Axios + ECharts

**后端**
- FastAPI (Python 异步 Web 框架)
- SQLAlchemy 2 (异步 ORM) + aiosqlite
- JWT 认证 (开发模式免登录)
- httpx (HTTP 客户端)

**AI**
- DeepSeek / 通义千问 双 LLM Provider 支持
- OpenAI 兼容 API 格式，可扩展
- `qwen-vl-max` 驱动多模态识别（食物/动作）

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/wwxxzz666/Sports-AI-Manager.git
cd Sports-AI-Manager
```

### 2. 启动后端

```bash
cd server
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek 或通义千问 API Key

python main.py
# 服务运行在 http://localhost:8000
```

### 3. 启动前端

```bash
# 回到项目根目录
npm install
npm run dev
# 开发服务器运行在 http://localhost:5173
```

### 4. 配置 LLM

编辑 `server/.env`：

```env
# 使用 DeepSeek（默认，仅文本对话）
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
LLM_API_KEY=sk-your-deepseek-api-key

# 或使用通义千问（支持多模态）
LLM_PROVIDER=qwen
LLM_MODEL=qwen-max
LLM_VISION_MODEL=qwen-vl-max
LLM_API_KEY=your-qwen-api-key
```

> DeepSeek 不支持多模态，`food-calories` 和 `motion-analysis` 需通义千问。
> 仅文本对话的 9 个 Agent 在 DeepSeek 下完全可用。

### 5. 接入第三方 API（可选）

```env
# 天气 API — go-out-prep Agent 实时天气
WEATHER_API_PROVIDER=qweather
WEATHER_API_KEY=your-key

# 活动 API — find-game Agent 真实活动数据
FIND_GAME_API_URL=
FIND_GAME_API_KEY=your-key
```

详细接入指南见各 Agent 源文件注释。

## 项目结构

```
Sports-AI-Manager/
├── src/                          # 前端源码
│   ├── api/                      # API 请求模块
│   ├── components/               # 通用组件
│   │   ├── chat/                 # 对话组件 (ChatStream, ChatBubble, ChatInputBar)
│   │   ├── common/               # 通用组件 (EmptyState, LoadingSkeleton, ErrorRetry)
│   │   └── layout/               # 布局组件 (PageHeader, TabBar)
│   ├── composables/              # Vue Composables
│   ├── router/                   # Vue Router 配置
│   ├── stores/                   # Pinia 状态管理
│   ├── utils/                    # 工具函数
│   └── views/                    # 页面视图 (7 个页面)
├── server/                       # 后端源码
│   ├── agents/                   # 11 个 AI Agent 实现
│   ├── api/v1/                   # FastAPI 路由
│   ├── core/                     # 核心模块 (安全、异常)
│   ├── db/                       # 数据库会话
│   ├── llm/                      # LLM Provider (DeepSeek + Qwen)
│   ├── models/                   # SQLAlchemy 模型
│   └── main.py                   # 应用入口
├── package.json
├── vite.config.ts
└── README.md
```

## License

MIT
