# AI Job Hunt Assistant 🚀

> 一个基于 AI 的智能求职助手，集成简历编写、岗位匹配、面试准备等功能，帮助你更高效地完成求职全流程。

**地址：** [https://purseek-ai-resume-production.up.railway.app](https://purseek-ai-resume-production.up.railway.app)

---

## 功能总览

| 功能 | 说明 |
|---|---|
| **📋 个人资料** | 通过 AI 对话引导逐步完善个人信息、工作经历、技能等 |
| **💬 AI 对话** | 多轮智能对话，AI 引导式采集信息，支持会话断点续传 |
| **📄 简历编辑** | 在线编辑简历，AI 润色，支持 Markdown / PDF / Docx 导出 |
| **🎯 岗位匹配** | JD 解析 + 人岗匹配度分析 + 自动生成定制简历 |
| **📚 知识库** | 上传简历、文档等资料，建立个人知识库，支持语义检索 |
| **🎤 面试题** | 根据岗位信息智能生成面试题目，按类别筛选练习 |

---

## 技术栈

| 层 | 技术 |
|---|---|
| **后端** | Python 3.12, FastAPI, Uvicorn |
| **前端** | React 18, Next.js 15, TypeScript, TailwindCSS, Vite |
| **AI 引擎** | LangChain, DeepSeek / Groq / OpenRouter |
| **数据库** | JSON 文件存储（轻量），FAISS 向量检索 |
| **容器化** | Docker, Railway |

---

## 功能详情

### 📋 个人资料

通过 AI 对话逐步引导填写个人信息，支持手动修改和编辑，数据自动保存。

### 💬 AI 对话

智能对话机器人，支持多轮交互和会话管理。对话过程中自动提取关键信息，支持断点续传。

### 📄 简历编辑

在线简历编辑器，支持：
- 分模块编辑（个人信息、工作经历、项目经验等）
- AI 一键润色
- 导出 Markdown / PDF / Docx 格式
- 中英文双语简历

### 🎯 岗位匹配

- **JD 解析**：输入职位描述，自动提取关键信息
- **匹配分析**：分析简历与岗位的匹配度，给出优化建议
- **定制简历**：根据目标岗位自动生成定制版简历
- **猎聘搜索**（可选）：搜索外部职位信息

### 📚 知识库

上传简历、项目文档等资料构建个人知识库，支持自然语言提问和语义检索。

### 🎤 面试题

根据岗位信息自动生成面试题目，可按类别筛选、自测练习。

---

## 本地开发

### 前置条件

- Python 3.12+
- Node.js 20+
- 一个或多个 LLM API Key（DeepSeek / Groq / OpenRouter）

### 1. 克隆项目

```bash
git clone https://github.com/<你的用户名>/<仓库名>.git
cd AI Job Hunt Assistant
```

### 2. 后端配置

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

创建 `.env` 文件（**不要提交到 Git**）：

```env
DEEPSEEK_API_KEY=sk-your-key
DEEPSEEK_MODEL=deepseek-chat
OPENROUTER_API_KEY=sk-or-your-key
GROQ_API_KEY=gsk-your-key
```

启动后端服务：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

### 3. 前端配置

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://localhost:5173`，会自动代理 API 请求到后端。

---

## 环境变量

在 Railway Dashboard → **Variables** 中配置：

| 变量 | 说明 | 必填 |
|---|---|---|
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 推荐 |
| `DEEPSEEK_MODEL` | DeepSeek 模型名，默认 `deepseek-chat` | 可选 |
| `OPENROUTER_API_KEY` | OpenRouter API Key | 可选 |
| `GROQ_API_KEY` | Groq API Key | 可选 |
| `LIEPIN_MCP_ENABLED` | 是否启用猎聘 MCP（需额外部署），留空使用模拟数据 | 可选 |

---

## 部署

项目使用 Docker 部署在 Railway 上。每次 `git push` 到 GitHub 后，Railway 自动构建并部署。

```bash
git add .
git commit -m "your message"
git push
```

---

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── core/          # 配置和工具
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务逻辑
│   │   └── main.py        # 入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/           # 页面路由
│   │   ├── pages/         # 页面组件
│   │   ├── lib/           # API 客户端
│   │   ├── stores/        # 状态管理
│   │   └── types/         # 类型定义
│   └── package.json
├── data/                  # 本地数据存储（gitignored）
├── railway.json           # Railway 部署配置
└── README.md
```

---

## 许可

MIT License
