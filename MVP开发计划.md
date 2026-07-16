# AI Job Hunt Assistant MVP 开发计划

## 1. MVP 目标

MVP 的目标不是一次性完成完整求职助手，而是在秋招前优先交付一条可实战使用的核心闭环：

1. 通过 AI 深度引导对话完成个人经历建档。
2. 将经历库结构化保存为本地 JSON。
3. 基于经历库生成母简历，并支持基础编辑。
4. 支持手动录入岗位 JD，生成岗位匹配度分析。
5. 基于 JD 和母简历生成定制简历初版，并支持导出 PDF。

MVP 成功的标志是：用户可以从零开始完成一次 30-45 分钟的 AI 建档，得到一份可编辑、可导出的母简历，并能针对一个手动输入的 JD 得到匹配分析与定制简历建议。

## 2. MVP 范围

### 2.1 必做 P0

| 模块 | MVP 能力 | 说明 |
| --- | --- | --- |
| AI 建档 | 多轮引导对话、追问、阶段总结 | 重点挖掘项目、技能、教育背景、偏好 |
| 经历库 | 保存 profile.json | 结构化保存 STAR、技术栈、量化成果、亮点 |
| 母简历 | 根据 profile.json 生成 resume_master.json | 先生成一版完整简历内容，不追求复杂模板 |
| 简历编辑 | 基础表单编辑 + A4 预览 | 简历预览区使用纯白实色，不使用玻璃拟态 |
| PDF 导出 | 导出规范 PDF | A4、黑白打印友好、内容不溢出 |
| JD 录入 | 手动粘贴 JD | MVP 不接招聘 API |
| 匹配分析 | 生成总分、维度分、优势、短板、建议 | 使用 AI JSON 输出，后续可加规则算法 |
| 定制简历 | 根据 JD 调整项目、技能顺序、描述侧重点 | 不改变事实，只重排和改写表达 |

### 2.2 暂不做 P1/P2

| 功能 | 暂缓原因 | 后续阶段 |
| --- | --- | --- |
| 招聘 API 接入 | API 可用性与数据质量不确定 | 第二阶段 |
| 自动岗位搜索与筛选 | 依赖岗位数据源 | 第二阶段 |
| 面试题生成 | 可基于定制简历扩展，非 MVP 闭环必须 | 第二阶段 |
| 薪资分析 | 数据源不稳定，短期价值低于简历闭环 | 第三阶段 |
| 多用户注册登录 | 产品定位为单用户工具 | 暂不做 |
| 自动投递 | 技术与合规风险高 | 不做 |

## 3. 技术方案

### 3.1 技术栈

| 层级 | 技术 | 说明 |
| --- | --- | --- |
| 前端 | Next.js 14 App Router + TypeScript | Web 桌面端优先 |
| UI | Tailwind CSS + shadcn/ui + Lucide React | 保持 UI 文档中的淡紫玻璃拟态风格 |
| 动效 | Framer Motion | 用于消息出现、卡片 hover、AI 生成态 |
| 状态管理 | Zustand | 管理对话、简历草稿、岗位分析状态 |
| 后端 | FastAPI + Python 3.10+ | 提供 AI、数据和 PDF 服务 |
| AI 模型 | Claude API 或兼容 LLM Provider | 复杂生成用强模型，简单追问可用低成本模型 |
| 存储 | 本地 JSON 文件 | 单用户 MVP，降低数据库和部署复杂度 |
| PDF | WeasyPrint 或 Playwright/Puppeteer | 优先选稳定渲染方案，保证简历格式 |

### 3.2 项目结构

```text
ai-job-assistant/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── stores/
│   └── types/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── prompts/
│   ├── templates/
│   └── main.py
├── data/
│   ├── profile.json
│   ├── resume_master.json
│   ├── settings.json
│   ├── jobs/
│   └── tailored/
└── docs/
```

### 3.3 本地 JSON 存储约定

MVP 先不引入数据库。所有写入操作通过后端服务完成，避免前端直接操作文件。

```text
data/
├── profile.json
├── resume_master.json
├── settings.json
├── jobs/
│   └── job_001.json
└── tailored/
    └── job_001_resume_v1.json
```

## 4. 核心用户流程

### 4.1 首次使用流程

1. 用户进入首页，点击开始建档。
2. AI 用轻松语气说明流程，降低求职焦虑。
3. 用户通过聊天描述项目、课程、论文、技能和偏好。
4. AI 每次只问一个问题，持续追问量化数据、困难、技术选型和结果。
5. 每完成一个项目，AI 给出阶段总结。
6. 用户确认总结后，后端写入 profile.json。
7. 用户点击生成母简历。
8. 系统生成 resume_master.json，并进入简历编辑页。
9. 用户编辑后保存并导出 PDF。

### 4.2 岗位分析流程

1. 用户进入岗位页，手动粘贴 JD。
2. 系统提取岗位标题、公司、城市、技能要求和偏好信息。
3. AI 根据母简历和 JD 输出匹配分析。
4. 页面展示总分、维度分、匹配技能、缺失技能、优势、短板和优化建议。
5. 用户点击生成定制简历。
6. 系统生成定制简历 JSON，并展示与母简历的差异。
7. 用户确认后导出定制 PDF。

## 5. 功能模块拆解

### 5.1 AI 建档模块

#### 前端页面

路由：`/onboarding`

核心组件：

| 组件 | 职责 |
| --- | --- |
| ChatPage | 建档页面容器 |
| ChatBubble | AI/用户消息气泡 |
| ChatInput | 文本输入、发送、快捷回复 |
| OnboardingProgress | 阶段进度条 |
| ProfilePreviewPanel | 右侧实时信息预览，MVP 可选 |
| SummaryCard | 项目阶段总结与确认 |

#### 对话阶段

| 阶段 | 目标 | 关键产出 |
| --- | --- | --- |
| 0. 暖场 | 说明流程、降低压力 | 用户开始对话 |
| 1. 核心项目 | 挖掘 1-3 个项目 | STAR、技术栈、量化成果 |
| 2. 教育背景 | 学历、方向、课程、论文 | education、research_focus |
| 3. 技能盘点 | 技能等级和证据 | skills with evidence |
| 4. 求职偏好 | 城市、岗位、公司类型、薪资 | preferences |
| 5. 总结确认 | 汇总经历库 | profile.json |

#### AI 行为要求

1. 每次只问一个问题。
2. 优先追问量化数据，如规模、准确率、耗时、提升比例。
3. 对模糊回答进行温和追问。
4. 每个项目至少提炼 3 个亮点。
5. 每个项目必须尽量补齐 STAR 四要素。
6. 不编造事实；缺失信息标记为 unknown 或待补充。

### 5.2 经历库模块

路由：`/profile`

MVP 能力：

1. 展示基础信息、教育背景、项目经历、技能、求职偏好。
2. 支持编辑项目标题、时间、技术栈、STAR 内容、简历描述。
3. 支持保存到 `profile.json`。
4. 支持从经历库触发重新生成母简历。

MVP 可先使用表单和卡片列表，不做复杂拖拽排序。

### 5.3 简历管理模块

路由：`/resume`

MVP 能力：

1. 生成母简历。
2. 左侧编辑表单，右侧 A4 实时预览。
3. 保存简历 JSON。
4. 导出 PDF。

简历内容模块：

| 模块 | 是否必需 | 说明 |
| --- | --- | --- |
| 基本信息 | 必需 | 姓名、电话、邮箱、城市、GitHub/作品链接 |
| 求职意向 | 必需 | AI Agent / 数据分析 / 遥感数据处理等 |
| 教育背景 | 必需 | 学校、专业、学历、时间、课程 |
| 技能清单 | 必需 | 按岗位方向分组 |
| 项目经历 | 必需 | 2-4 个核心项目 |
| 论文/成果 | 可选 | 有则展示 |
| 奖项/证书 | 可选 | 有则展示 |

UI 注意：简历编辑器和 PDF 预览区域必须是纯白底、实色文字，不使用玻璃拟态，保证打印和阅读专业性。

### 5.4 岗位与匹配分析模块

路由：`/jobs`

MVP 能力：

1. 新建岗位，手动粘贴 JD。
2. 保存岗位到 `data/jobs/job_xxx.json`。
3. 触发匹配分析。
4. 展示匹配分析详情。

匹配分析维度：

| 维度 | 权重 | 输出 |
| --- | --- | --- |
| 技能匹配 | 40 | matched_skills、missing_skills |
| 经历相关度 | 30 | relevant_projects、experience_gap |
| 硬性条件 | 20 | education、location、years |
| 偏好契合 | 10 | company_type、city、work_life_balance |

匹配结果展示：

1. 总分圆形徽章。
2. 四个维度进度条。
3. 匹配技能和缺失技能标签。
4. 优势、短板、优化建议三列。
5. 生成定制简历按钮。

### 5.5 定制简历模块

MVP 可以集成在岗位详情页中，不单独开复杂页面。

能力：

1. 根据 JD 从母简历中选择最相关项目。
2. 调整技能顺序。
3. 对项目描述进行岗位导向改写。
4. 输出修改原因。
5. 支持用户接受全部修改。
6. 保存到 `data/tailored/job_xxx_resume_v1.json`。
7. 导出 PDF。

限制：

1. 不改变事实。
2. 不新增用户未提供的成果、经历和技能。
3. AI 修改必须附 reason，方便用户检查。

## 6. API 设计

### 6.1 AI 对话

`POST /api/chat/start`

返回开场消息和当前阶段。

`POST /api/chat/message`

请求：

```json
{
  "session_id": "session_001",
  "message": "我做过一个遥感图像分类项目",
  "stage": "project_deep_dive"
}
```

返回：

```json
{
  "reply": "这个项目是怎么开始的？是导师安排，还是你自己的想法？",
  "stage": "project_deep_dive",
  "missing_info": ["project_background", "user_role"],
  "should_summarize": false
}
```

`POST /api/profile/extract`

将阶段对话提炼为结构化项目或技能条目。

### 6.2 经历库

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/profile` | 获取 profile.json |
| PUT | `/api/profile` | 保存完整 profile.json |
| POST | `/api/profile/projects` | 新增项目 |
| PUT | `/api/profile/projects/{project_id}` | 更新项目 |

### 6.3 简历

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/resume/generate` | 基于 profile 生成母简历 |
| GET | `/api/resume/master` | 获取母简历 |
| PUT | `/api/resume/master` | 保存母简历 |
| POST | `/api/resume/export-pdf` | 导出 PDF |

### 6.4 岗位与匹配

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/jobs` | 新建手动 JD |
| GET | `/api/jobs` | 获取岗位列表 |
| GET | `/api/jobs/{job_id}` | 获取岗位详情 |
| POST | `/api/match/analyze` | 生成匹配分析 |
| POST | `/api/tailor/generate` | 生成定制简历 |

## 7. 数据结构草案

### 7.1 profile.json

```json
{
  "basic_info": {
    "name": "",
    "phone": "",
    "email": "",
    "city": "",
    "links": []
  },
  "education": [
    {
      "school": "",
      "degree": "硕士",
      "major": "电子信息",
      "start_date": "",
      "end_date": "",
      "courses": [],
      "research_focus": []
    }
  ],
  "projects": [
    {
      "id": "proj_001",
      "name": "遥感图像分类优化系统",
      "time_range": "",
      "role": "独立负责",
      "star": {
        "situation": "",
        "task": "",
        "action": [],
        "result": ""
      },
      "technologies": ["Python", "PyTorch"],
      "metrics": [
        {
          "name": "准确率提升",
          "value": "75% -> 92%"
        }
      ],
      "highlights": [],
      "resume_text": "",
      "interview_questions": []
    }
  ],
  "skills": [
    {
      "name": "Python",
      "level": 4,
      "level_name": "熟练",
      "evidence": "独立完成多个数据处理和模型训练项目"
    }
  ],
  "preferences": {
    "target_roles": [],
    "target_cities": [],
    "company_types": [],
    "salary_range": "20-30k",
    "work_life_balance": true
  }
}
```

### 7.2 resume_master.json

```json
{
  "id": "resume_master",
  "title": "母简历",
  "target_role": "AI Agent / 数据分析 / 遥感数据处理",
  "sections": {
    "basic_info": {},
    "summary": "",
    "education": [],
    "skills": [],
    "projects": [],
    "publications": [],
    "awards": []
  },
  "updated_at": ""
}
```

### 7.3 job_xxx.json

```json
{
  "id": "job_001",
  "title": "数据分析师",
  "company": "",
  "city": "",
  "jd_raw": "",
  "jd_extracted": {
    "required_skills": [],
    "nice_to_have": [],
    "responsibilities": [],
    "keywords": []
  },
  "match_report": {
    "total_score": 0,
    "breakdown": {},
    "matched_skills": [],
    "missing_skills": {},
    "strengths": [],
    "weaknesses": [],
    "optimization_tips": [],
    "recommendation": ""
  },
  "created_at": ""
}
```

## 8. UI 实现要求

### 8.1 全局风格

1. 主色：`#B8A9E8`。
2. 背景：淡紫渐变 `linear-gradient(135deg, #EEE9FF 0%, #E0D8F5 100%)`。
3. 主卡片：玻璃拟态 `rgba(255,255,255,0.6)` + `backdrop-filter: blur(20px)`。
4. 圆角：卡片 16px，按钮 12px，输入框 10px。
5. 图标：统一使用 Lucide React。
6. 交互动效：hover 150-250ms，卡片上移 2px。

### 8.2 页面布局

1. 左侧导航栏 80px。
2. 顶部栏 72px。
3. 主内容区自适应。
4. 桌面端优先，MVP 支持 768px 以上基本适配。

### 8.3 MVP 页面

| 页面 | 路由 | 重点 |
| --- | --- | --- |
| 首页 | `/` | 显示当前进度和主要入口，不做营销落地页 |
| AI 建档 | `/onboarding` | 对话气泡、进度条、输入栏 |
| 经历库 | `/profile` | 项目卡片、技能标签、编辑表单 |
| 简历管理 | `/resume` | 左编辑、右 A4 预览、保存导出 |
| 岗位分析 | `/jobs` | JD 输入、岗位列表、匹配报告 |

## 9. AI Prompt 规划

MVP 需要 5 类 Prompt：

| Prompt | 用途 |
| --- | --- |
| Onboarding Start | 开场、降低压力、说明流程 |
| Project Deep Dive | 深挖项目，追问背景、任务、行动、结果 |
| Value Extraction | 将对话提炼成 STAR、亮点、简历文本 |
| Resume Generate | 从 profile 生成母简历 JSON |
| Match Analyze | 对 JD 和简历做匹配分析 |
| Tailor Resume | 生成定制简历和修改原因 |

Prompt 输出必须尽量要求 JSON 格式，并在后端进行解析和校验。解析失败时保留原始文本，并提示用户重试。

## 10. 开发排期

### Week 1：打通核心数据和 AI 建档

| 天数 | 任务 | 产出 |
| --- | --- | --- |
| Day 1 | 初始化前后端项目、CORS、环境变量 | Next.js + FastAPI Hello World |
| Day 2 | 全局 UI 框架、Sidebar、TopBar、基础组件 | 可导航的应用骨架 |
| Day 3 | AI 对话接口和 Chat UI | 用户可发送消息并收到 AI 回复 |
| Day 4 | 建档阶段状态机、追问 Prompt | 可按阶段推进对话 |
| Day 5 | Value Extraction、profile.json 写入 | 对话结果可结构化保存 |
| Day 6 | 经历库页面 | 可查看和编辑 profile |
| Day 7 | Week 1 联调与修复 | 完整跑通建档到经历库 |

### Week 2：简历、匹配分析和定制闭环

| 天数 | 任务 | 产出 |
| --- | --- | --- |
| Day 8 | 母简历生成接口 | profile -> resume_master.json |
| Day 9 | 简历编辑器与 A4 预览 | 可编辑、可保存 |
| Day 10 | PDF 导出 | 可导出母简历 PDF |
| Day 11 | JD 录入和岗位保存 | job_xxx.json |
| Day 12 | 匹配分析接口和报告页面 | 总分、维度分、建议 |
| Day 13 | 定制简历生成与差异展示 | tailored_resume_v1.json |
| Day 14 | 全流程 QA、Prompt 调优、样式修复 | MVP 可实战使用 |

## 11. 验收标准

### 11.1 功能验收

1. AI 建档能连续完成至少 5 个阶段。
2. 对话中能对模糊回答进行追问。
3. 每个项目能生成 STAR、技术栈、亮点和简历描述。
4. `profile.json` 可保存和再次读取。
5. 母简历可生成、编辑、保存。
6. PDF 可导出，A4 排版无明显溢出。
7. 手动 JD 可保存。
8. 匹配分析包含总分、维度分、优势、短板和建议。
9. 定制简历能基于 JD 改写项目描述，并说明修改原因。

### 11.2 体验验收

1. AI 语气友好，不像考试。
2. 每次 AI 只问一个核心问题。
3. 页面加载和 AI 生成有明确 loading 状态。
4. 对话、简历、岗位分析之间的流程清晰。
5. 简历预览保持专业、干净、黑白打印友好。

### 11.3 数据验收

1. 所有 JSON 文件格式稳定。
2. AI 输出不得覆盖用户已有数据，除非用户确认。
3. 定制简历不得编造事实。
4. 缺失信息使用空字符串、空数组或 `unknown` 标记。

## 12. 测试计划

### 12.1 后端测试

1. API 健康检查。
2. JSON 读写测试。
3. AI 输出解析失败兜底测试。
4. PDF 导出接口测试。
5. 文件不存在时的初始化测试。

### 12.2 前端测试

1. 路由跳转正常。
2. 对话发送和 loading 状态正常。
3. 表单编辑和保存正常。
4. A4 预览内容不溢出。
5. 匹配报告空状态、加载态、成功态、失败态完整。

### 12.3 手工验收脚本

1. 新用户进入首页。
2. 点击开始建档。
3. 输入一个项目经历。
4. AI 至少追问 3 次。
5. 确认阶段总结。
6. 进入经历库查看项目。
7. 生成母简历。
8. 编辑一个项目描述。
9. 导出 PDF。
10. 新增一个 JD。
11. 查看匹配分析。
12. 生成定制简历。
13. 导出定制 PDF。

## 13. 风险与应对

| 风险 | 影响 | 应对 |
| --- | --- | --- |
| AI 追问质量不稳定 | 建档效果变差 | 固定阶段状态机 + Prompt 中明确追问信号 |
| AI JSON 解析失败 | 数据无法保存 | 后端加 JSON schema 校验和重试 |
| PDF 样式不稳定 | 简历不可用 | 简历预览用简单 HTML/CSS，减少复杂玻璃样式 |
| 本地 JSON 并发写入 | 数据覆盖 | MVP 单用户，后端写入时使用临时文件原子替换 |
| 开发时间紧 | 核心闭环延期 | 招聘 API、面试、薪资全部后置 |
| 模型成本 | 开发测试成本上升 | 简单任务用低成本模型，调试时启用 mock provider |

## 14. 开发优先级建议

第一优先级：AI 建档质量。它是整个产品的核心差异化能力。

第二优先级：简历生成和 PDF 导出。用户必须能拿到可投递的结果。

第三优先级：手动 JD 匹配和定制简历。它完成“同一份经历面向不同岗位重组表达”的关键价值。

UI 需要保持专业和柔和，但 MVP 不应过度投入复杂动效。先保证流程顺、数据稳、简历能用，再做视觉润色。

## 15. MVP 完成定义

当以下条件全部满足时，MVP 可以认为完成：

1. 从空白数据开始，可以完成一次完整 AI 建档。
2. 系统生成的 profile.json 字段完整、可编辑、可保存。
3. 母简历可以生成并导出 PDF。
4. 用户可以手动粘贴 JD 并得到匹配报告。
5. 用户可以生成一版定制简历并导出 PDF。
6. 全流程不依赖招聘 API、不依赖数据库、不需要多用户登录。
7. 页面风格符合 UI 文档的淡紫玻璃拟态方向，简历区域保持纯白专业排版。
