<p align="center">
  <img src="https://img.shields.io/badge/🐾%20OurClaw-v2.0-1a73e8" alt="OurClaw">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue">
  <img src="https://img.shields.io/badge/LLM-DeepSeek%20%7C%20OpenAI%20%7C%20更多-brightgreen">
  <img src="https://img.shields.io/badge/license-MIT-green">
</p>

<h1 align="center">🐾 OurClaw — 你的 AI 学术龙虾 - 技能扩展十分方便</h1>

<p align="center">
  <b>可扩展 · 可编程 · 可对话 · 会技能</b><br>
  一个基于大语言模型的智能助手框架，支持 <b>Web 网页</b>、<b>桌面应用</b> 和 <b>终端</b> 三种使用方式。
</p>

<p align="center">
  <b>🔥 最强特色：你可以把 Claude/GPT 等任何 AI 的 Skill 融入自己的技能树</b><br>
  <i>只需说一句 ——「把 GitHub 上的 [仓库地址] 技能加入你的技能」即可自动导入！</i>
</p>

---

## 📢 v2.0 更新内容

> OurClaw v2.0 正式发布！新增了以下核心能力：

### 🧠 大脑模型自由切换
现在你可以在 `env` 文件中自由选择 Claw 使用的**大脑模型**：
- `MAIN_MODEL=deepseek` — 使用 DeepSeek（默认，稳定可靠）
- `MAIN_MODEL=openai` — 使用 OpenAI GPT（需配置 `OPENAI_API_KEY`）

无需修改任何代码，修改 `env` 中的 `MAIN_MODEL` 即可一键切换。

### 🖼️ 新增三大图像工具

| 工具 | 能力 | 说明 |
|------|------|------|
| 🎨 **图像生成** (`image_gen_tool`) | 文生图 | 基于 Qwen-Image-2.0 模型，根据文字描述生成图像 |
| 🔍 **图像分析** (`image_analyzer_tool`) | 图片理解 | 基于 Qwen3.6-Plus 多模态模型，分析图片内容、OCR 识别 |
| 🧠 **图像理解** (`image_understanding_tool`) | 图文匹配 | 深度理解图片中的文字、物体、场景和布局 |

> 💡 以上图像工具均通过 `DASHSCOPE_API_KEY` 环境变量调用 DashScope（阿里通义千问）API，无需额外配置密钥。

---

## 📦 快速体验

### 方式一：🌐 Web 网页版（推荐新手）

一键启动，浏览器打开即可使用，**支持语音输入和对话提需求**。

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 Web 服务
python app.py
```

浏览器访问 👉 **http://127.0.0.1:8000**

**Web 版特点：**
- 🎤 **语音输入** — 点击录音按钮，直接说话即可输入
- 💬 **对话式交互** — 像聊天一样提出需求，Claw 自动理解并执行
- 📁 **可视化文件管理** — 左侧文件树浏览、预览项目文件
- 📋 **实时执行日志** — 右侧面板展示每一步的思考与工具调用
- 🖥️ **零安装** — 只需浏览器，手机/电脑均可使用

### 方式二：🖥️ 桌面应用版（Tkinter）

原生桌面应用，功能与 Web 版一致，适合习惯桌面操作的用户。

```bash
python sysapp.py
```

### 方式三：⚡ 终端高级版（面向开发者 / 高级用户）

直接调用核心引擎，适合集成到脚本或需要极简交互的场景。

```bash
python Claw.py
```

或以代码方式集成：

```python
from Claw import CoreClawAgent
import asyncio

agent = CoreClawAgent()
response = await agent.chat("帮我查一下北京的天气")
print(response)
```

---

## 🧠 核心能力矩阵

| 能力 | 说明 | 使用场景 |
|------|------|----------|
| 🌐 **联网搜索** | Tavily 搜索引擎，实时获取最新信息 | 查新闻、查资料、实时数据 |
| 📄 **网页抓取** | 抓取任意网页内容并转为 Markdown | 阅读文章、爬取数据 |
| 🐍 **代码执行** | 沙盒中运行 Python 代码 | 数据处理、计算、脚本执行 |
| 💻 **终端操作** | 执行 Shell 命令、文件操作 | 项目构建、文件管理 |
| 🎤 **语音理解** | 支持 WAV/MP3/M4A 等格式语音转文字 | 会议记录、语音输入 |
| 📁 **文件管理** | 读取/创建/修改项目文件 | 代码编辑、文档处理 |
| 📚 **知识检索** | 本地知识库检索 | 查阅历史记录、记忆回溯 |
| 🧠 **长期记忆** | 记住用户偏好和习惯 | 个性化服务 |
| ⏰ **定时任务** | 后台定时执行用户任务 | 天气提醒、定时检查 |
| 🎨 **图像生成** | Qwen-Image-2.0 文生图 | 插图创作、概念设计、AI 绘画 |
| 🔍 **图像分析** | Qwen3.6-Plus 多模态分析 | 图片内容描述、OCR 识别、场景理解 |
| 🧠 **图像理解** | 深度图文匹配与布局分析 | 图表解读、物体检测、图像问答 |

---

## 🎯 内置技能一览

OurClaw 拥有可插拔的 **技能系统（Agent Skills）**，每个技能对应一个专业能力，通过触发词即可唤起。

| 技能 | 触发词举例 | 功能说明 |
|------|-----------|----------|
| 🌤️ **天气查询** | `"北京的天气怎么样"`、`"查一下上海的天气"` | 实时天气 + Open-Meteo 逐小时气象数据 |
| 📝 **文章总结** | `"总结一下这篇文章"`、`"帮我概括这段文字"` | 将长文/网页精炼为 5 条核心内容 |
| 🔬 **科研搜索** | `"查询最新的强化学习研究方向"`、`"找一下 AI 论文"` | 搜索某领域最新研究并生成 2000+ 字报告 |
| 🎙️ **语音识别** | `"帮我识别这段语音"`、`"听一下这个录音"` | 将音频文件转文字（支持多格式） |
| 📊 **数据分析** | `"对这个 CSV 做线性回归"`、`"跑个 K-means 聚类"` | 数据科学：机器学习/统计学习/深度学习全流程 |
| ⏱️ **定时任务** | `"每天早上8点提醒我"`、`"定时检查服务器"` | 创建和管理定时后台任务 |
| 🛠️ **创建技能** | `"帮我创建一个发送邮件的技能"` | 自定义新技能或从 GitHub 导入外部技能 |

### 🔌 导入外部技能（独家特色）

**你可以把任何 GitHub 上的 AI Skill 项目整合到 Claw 的技能树中！**

只需对 Claw 说：

> **"把 https://github.com/xxx/xxx 这个技能加入你的技能"**

Claw 会自动：
1. ✅ 克隆仓库并分析技能结构
2. ✅ 提取 SKILL.md 或 README 中的技能定义
3. ✅ 整合本地工具调用（终端/代码执行/网页抓取等）
4. ✅ 生成标准技能文件，立即可用

这意味着你可以把 **Claude Artifacts、GPT Actions、各类 AI 工作流** 等任何可复用的技能方案轻松整合进来，不断扩充 Claw 的能力边界！

---

## 🏗️ 架构概览

```
OurClaw/
├── Claw.py                 # 🤖 核心 Agent 引擎（高级用户入口）
├── app.py                  # 🌐 Web 服务器入口（FastAPI）
├── sysapp.py               # 🖥️ 桌面应用入口（Tkinter）
├── background_loop.py      # ⏰ 后台定时任务调度器
├── memory_manager.py       # 🧠 记忆管理系统
├── skills_scanner.py       # 🔍 技能扫描器
├── requirements.txt        # 📦 依赖清单
├── skills/                 # 🎯 技能库（可插拔）
│   ├── get_weather/        #   🌤️ 天气查询
│   ├── summary/            #   📝 文章总结
│   ├── searchfile/         #   🔬 科研搜索
│   ├── speech_recognition/ #   🎙️ 语音识别
│   ├── Data_Anlysis/       #   📊 数据分析
│   ├── task_manager/       #   ⏱️ 定时任务
│   └── crate_skill/        #   🛠️ 创建/导入技能
├── tools/                  # 🔧 基础工具集
│   ├── terminal_tool.py    #   💻 终端执行
│   ├── python_repl_tool.py #   🐍 代码执行
│   ├── fetch_url_tool.py   #   🌐 网页抓取
│   ├── fetch_tavily_tool.py#   🔍 联网搜索
│   ├── read_file_tool.py   #   📁 文件读取
│   ├── speech_recognition_tool.py  # 🎤 语音识别
│   ├── pdf_parser_tool.py  #   📄 PDF 解析
│   ├── word_parser_tool.py #   📝 Word 解析
│   ├── image_analyzer_tool.py#   🔍 图像分析
│   ├── image_gen_tool.py#        🎨 图像生成
│   ├── image_understanding_tool.py#  🧠 图像理解
│   └── write_memory_tool.py#   🧠 记忆写入
├── memory/                 # 💾 记忆存储
│   ├── IDENTITY.md         #   🆔 身份设定
│   ├── SOUL.md             #   💫 性格特征
│   ├── USER.md             #   👤 用户档案
│   └── MEMORY.md           #   📓 对话记忆
├── static/                 # 🎨 前端静态文件
│   └── index.html          #   Web 界面
├── tasks/                  # ⏰ 定时任务存放
└── Audio/                  # 🎵 音频文件
```

---

## 🚀 使用流程

```
用户提问 ──▶  Claw 识别意图 ──▶  匹配技能/调用工具 ──▶  执行并返回结果
                │                       │
                ▼                       ▼
           联网搜索 / 代码执行 / 终端操作 / 语音识别 / 网页抓取 ...
```

### 用户分级推荐

| 用户类型 | 推荐方式 | 理由 |
|----------|----------|------|
| 👶 **新手用户** | `python app.py` → Web 界面 | 可视化操作，语音输入，无需编程 |
| 👨‍💻 **日常用户** | `python sysapp.py` → 桌面版 | 原生体验，文件管理更方便 |
| 🧙 **高级用户/开发者** | 直接调用 `Claw.py` | 可编程集成，灵活度最高 |

---

## ⚙️ 配置说明

在项目根目录创建 `.env` 文件，配置以下 API Key。以下是各 Key 的申请教程 👇

---

### 🧠 大脑模型选择

OurClaw v2.0 支持在 DeepSeek 和 OpenAI GPT 之间自由切换：

| 项目 | 说明 |
|------|------|
| **配置项** | `MAIN_MODEL=deepseek`（默认）或 `MAIN_MODEL=openai` |
| **DeepSeek** | 默认模型，稳定可靠，详见下方 DeepSeek 配置 |
| **OpenAI GPT** | 切换为 `MAIN_MODEL=openai` 后生效，需配置下方 OpenAI 的 Key |

```env
# 大脑模型选择
MAIN_MODEL=deepseek        # deepseek 或 openai
```

> 💡 修改 `MAIN_MODEL` 即可一键切换大脑模型，无需改动任何代码。

---

### 🔑 DeepSeek API Key

| 项目 | 说明 |
|------|------|
| **用途** | 驱动 OurClaw 的大模型对话与推理能力 |
| **申请地址** | [https://platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys) |
| **注册步骤** | ① 打开链接 → ② 注册/登录账号 → ③ 进入控制台 → ④ 左侧「API Keys」→ ⑤ 点击「创建 API Key」→ ⑥ 复制生成的 `sk-...` 密钥 |
| **费用** | 新用户有免费额度，后续按量计费，价格极低 |

```env
# DeepSeek 配置（核心 LLM）
DEEPSEEK_API_KEY=sk-你的key-粘贴到这里
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

> 💡 `DEEPSEEK_MODEL` 可选值：`deepseek-chat`（默认）、`deepseek-reasoner`（推理增强版，适合复杂逻辑任务）

---

### 🔑 OpenAI GPT API Key（可选，切换大脑模型时使用）

| 项目 | 说明 |
|------|------|
| **用途** | 当 `MAIN_MODEL=openai` 时，驱动 OurClaw 的大模型对话与推理能力 |
| **申请地址** | [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| **注册步骤** | ① 打开链接 → ② 注册/登录 OpenAI 账号 → ③ 进入 API Keys 页面 → ④ 点击「Create new secret key」→ ⑤ 复制生成的 `sk-...` 密钥 |
| **费用** | 按量计费，需绑定支付方式 |

```env
# OpenAI 配置（当 MAIN_MODEL=openai 时使用）
OPENAI_API_KEY=sk-你的key-粘贴到这里
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
```

> 💡 `OPENAI_MODEL` 可选值：`gpt-4o`（默认）、`gpt-4o-mini`、`gpt-4-turbo` 等。如需使用兼容 OpenAI 接口的第三方 API，修改 `OPENAI_BASE_URL` 即可。

---

### 🔑 Tavily API Key（联网搜索，建议配置）

| 项目 | 说明 |
|------|------|
| **用途** | 让 OurClaw 具备联网搜索能力（查新闻、查资料、实时数据） |
| **申请地址** | [https://app.tavily.com/sign-in](https://app.tavily.com/sign-in) |
| **注册步骤** | ① 打开链接 → ② 点击 **Sign up** 注册（支持 Google / GitHub 账号）→ ③ 登录后进入 Dashboard → ④ 在 **API Keys** 页面点击 **Create API Key** → ⑤ 复制生成的 `tvly-...` 密钥 |
| **免费额度** | 每月 1000 次搜索请求，个人使用完全够用 |

```env
# 可选：Tavily 搜索 API Key（联网搜索用）
TAVILY_API_KEY=tvly-你的key-粘贴到这里
```

> ⚠️ 不配置此 key 则联网搜索功能不可用。

---

### 🔑 DashScope API Key（语音识别 & 图像工具，按需配置）

| 项目 | 说明 |
|------|------|
| **用途** | 使用阿里通义千问 Qwen 多模态模型进行语音转文字和图像生成/分析/理解（支持 WAV/MP3/M4A/JPG/PNG 等格式） |
| **申请地址** | [https://bailian.console.aliyun.com/](https://bailian.console.aliyun.com/) |
| **注册步骤** | ① 打开链接 → ② 使用阿里云账号登录（未注册则先注册）→ ③ 进入 **百炼** 控制台 → ④ 左侧菜单 **API-KEY 管理** → ⑤ 点击 **创建 API-KEY** → ⑥ 复制生成的 `sk-...` 密钥 |
| **费用** | 新用户有免费额度；语音识别模型按字符计费，图像模型按次计费，价格低廉 |

```env
# 可选：DashScope API Key（语音识别 & 图像工具用）
DASHSCOPE_API_KEY=sk-你的key-粘贴到这里
```

> ⚠️ 不配置此 key 则语音识别和图像工具均不可用。

---

### ✅ 配置完成后验证

配置好 `.env` 后启动 Claw，若看到类似以下日志说明配置成功：

```
✅ DeepSeek API 已连接
✅ Tavily 搜索 API 已连接
✅ DashScope 语音识别 API 已连接
```

---



## 📦 依赖安装

```bash
pip install -r requirements.txt
```

核心依赖一览：
- `langchain` / `langgraph` — LLM 应用框架
- `fastapi` / `uvicorn` — Web 服务
- `deepseek` — 大模型驱动（默认）
- `openai` / `langchain-openai` — GPT 模型驱动（可选切换）
- `tavily` — 联网搜索
- `dashscope` — 语音识别 & 图像生成/分析/理解
- `PyPDF2` / `python-docx` — 文档解析

---

## 🔮 未来规划

- [ ] 技能市场 — 社区共享技能包
- [ ] 知识库 RAG — 上传文档自动构建知识库
- [ ] 本地模型支持（Ollama / llama.cpp）
- [ ] 插件系统 — 更灵活的能力扩展

---

<p align="center">
  <b>🐾 OurClaw — 你的智能小龙虾，自动完成你的任务</b><br>
  <i>从今天开始，让 AI 替你干活</i>
</p>
