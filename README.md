# weave-talk

> 中文版（默认） · [English](README.en.md)

**全双工语音对话服务**：ASR → LLM → TTS 端到端管线，WebSocket 实时双工，
支持打断、插话、情绪系统，无工具调用（聚焦纯语音对话）。

## 项目特点

- **真·全双工**：WebSocket 事件协议 `session/ready/state/user_turn/assistant_text/speaking_start/interrupted/ended`，边说边听、随时插话
- **打断（barge-in）**：用户开口瞬间即停 TTS，`_norm_barge_compare` 做片段级归一化比对，短碎片有独立判定逻辑
- **EoT（End-of-Turn）判定**：意图分类子代理 + 语义检查双通道，判定"这句话说完了没"；`_eot_watchdog` 超时兜底
- **情绪系统**：情绪状态随对话衰减（`_decay_emotion`），可驱动插话文案与 TTS 风格（`_speak_interjection`）
- **ASR 三模可配**：DashScope 实时流式（fun-asr-realtime / qwen3-asr-flash-realtime）、MiMo 流式、通用 HTTP 转写
- **TTS 可配**：MiMo mimo-v2.5-tts（OpenAI 兼容流式接口），支持音色/风格指令
- **LLM 多路由**：任意 OpenAI 兼容 base_url，`[providers.*]` 按 priority 路由，缺省回落 `[api]`
- **优雅降级**：ASR 未配置→WS 下发 error 并关闭；TTS 关闭→只回文本事件；LLM 失败→error 事件
- **前端**：Vue3 语音界面（VoiceChat 组件 + useVoiceDuplex 双工客户端）

## 目录结构

```
weave-talk/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI 入口、健康检查、test 用户
│   │   ├── core/config.py     # 配置加载（Config 精简实现，支持 config_model.toml 合并）
│   │   ├── core/deps.py       # JWT 鉴权依赖
│   │   ├── db/database.py     # 6 模型
│   │   ├── api/auth.py        # 注册/登录/me
│   │   ├── api/voice.py       # 会话 API + /api/voice/ws 双工 WebSocket
│   │   ├── services/voice_service.py  # 会话编排（无工具调用）
│   │   ├── services/asr_service.py    # ASR（原样复制）
│   │   ├── services/tts_service.py    # TTS（原样复制）
│   │   ├── services/llm_service.py    # LLM（原样复制）
│   │   └── ...
│   ├── config.toml           # 基础设施段（server/security/database，可提交）
│   ├── config_model.toml     # 模型段（[api]/[asr]/[voice]/[providers]，含真实 key，不入 git）
│   ├── static/               # 前端构建产物
│   └── requirements.txt
├── frontend/                 # Vue3 + Vite（语音对话前端）
└── scripts/                  # install_venv/init_db/start/stop/restart/build
```

## 部署前提

| 依赖 | 版本要求 | 说明 |
|------|---------|------|
| 操作系统 | - | macOS / Ubuntu 22.04+ / Windows（推荐 WSL2；原生 Windows 用 Git Bash 跑 bash 脚本） |
| Python | 3.11+（建议 3.13） | Ubuntu 24.04 自带 3.12；22.04 需 `add-apt-repository ppa:deadsnakes/ppa && sudo apt install python3.12`；macOS: `brew install python@3.13`；Windows: python.org 安装器（勾选 Add to PATH） |
| Node.js | 18+（仅前端构建需要） | macOS: `brew install node`；Ubuntu: `sudo apt install nodejs npm`（24.04 自带 18）或 NodeSource；Windows: `winget install OpenJS.NodeJS.LTS` |

> 数据库默认使用 **SQLite**（零外部依赖，首次启动自动建库建表）。
> 如需 PostgreSQL 14+，改 `backend/config.toml` 的 `[database] type = "postgres"`。

## 独立部署（自包含三步）

本项目不依赖外层目录结构，独立部署只需：

```bash
bash scripts/install_venv.sh   # 本项目 .venv + 依赖（幂等；PYTHON_BIN 可指定解释器）
bash scripts/init_db.sh        # 按 [database] type 初始化：sqlite 免 PG；postgres 幂等建库+预建表
bash scripts/start.sh          # 启动（自动选用 .venv）
curl http://127.0.0.1:8203/healthz
```

## 部署步骤

### 1. 数据库

**推荐（自包含）**：直接运行项目级脚本，它按 `[database] type` 自动处理
SQLite 预建 / PostgreSQL 幂等建库 + 预建表（幂等可重复）：

```bash
bash scripts/init_db.sh
```

**SQLite（默认）**：实际无需任何操作，首次启动自动创建 `backend/weave_talk.db`。

**PostgreSQL（可选）**：前置需本机 PostgreSQL 14+：
macOS: `brew install postgresql@16 && brew services start postgresql@16`；
Ubuntu: `sudo apt install postgresql && sudo systemctl start postgresql`；
Windows: 推荐 WSL2 后按 Ubuntu 步骤。
脚本会幂等 `createdb weave_talk`；也可以手工：

```bash
createdb -U postgres -h 127.0.0.1 weave_talk
```

认证说明：macOS/Homebrew 默认本地免密（trust），直接可用；Ubuntu 默认本地 TCP 为 scram
认证，需先 `sudo -u postgres psql -c "ALTER USER postgres PASSWORD '<强密码>'"`，脚本运行时
`export PGPASSWORD='<强密码>'`（init_db.sh 透传该变量），并把同一密码写入
`backend/config.toml` 的 `[database] password`（服务连接只读 config，不走环境变量）。

> 在 family 多项目目录下，也可运行家族级入口 `bash <family根>/scripts/init_databases.sh`
>（等价于依次调用各项目 `scripts/init_db.sh`）。

### 2. 创建虚拟环境并安装依赖

**推荐（自包含）**：

```bash
bash scripts/install_venv.sh
```

等价的手工步骤：

```bash
python3.11 -m venv .venv     # 或 python3.13
./.venv/bin/pip install -r backend/requirements.txt
```

### 3. 修改配置

基础设施段在 `backend/config.toml`（可提交模板）：

```toml
[server]
host = "127.0.0.1"
port = 8203

[security]
jwt_secret_key = "请改成足够长的随机字符串"

[database]
# type = "sqlite"（默认）| "postgres"
type = "sqlite"
path = "weave_talk.db"
# postgres 模式使用以下字段：
# host = "127.0.0.1"
# port = 5432
# username = "postgres"
# password = ""
# name = "weave_talk"
```

模型段在 `backend/config_model.toml`（不入 git，含真实 key；`[api]/[asr]/[voice]/[providers]`
整段覆盖合并到 Config）：

```toml
# ── LLM（voice_* 未覆盖时的最终回落）──
[api]
base_url = "https://api.deepseek.com/v1"
api_key = "sk-..."
model_name = "deepseek-v4-flash"

# ── ASR 语音识别（三选一）──
[asr]
is_dashscope = true           # DashScope 实时流式（fun-asr-realtime）
dashscope_api_key = "sk-..."
dashscope_model = "fun-asr-realtime"
# is_mimo = true              # 或 MiMo 流式（qwen3-asr）
# base_url = "..."            # 或通用 HTTP 转写（两种流式均 false 时）

# ── 语音对话 ──
[voice]
enabled = true
identity = ""                     # 助手名（可选，留空用默认）
provider = "default"          # [providers.*] 路由键；缺失时回落 [api]
model_name = "deepseek-v4-flash"
temperature = 0.7
max_tokens = 1024
context_turns = 8
disable_thinking = true
# 打断/EoT/碎片合并/噪音门控/插话/情绪等 50+ 键（有默认值）

# system prompt：决定口吻/风格词约束/禁 emoji 等（无工具指引，可自由配置）
system_prompt = "你是一个全双工语音对话助手，正在与用户进行实时语音交流。请严格遵守以下要求：..."

# ── TTS 语音合成（MiMo mimo-v2.5-tts）──
tts_enabled = true
tts_base_url = ""             # 空 = 回落 [providers.mimo]
tts_api_key = ""
tts_model = "mimo-v2.5-tts"
tts_voice = "冰糖"
tts_style_instruction = "用自然、亲切、口语化的语气，语速适中，像朋友聊天一样温暖。"

# ── 多供应商路由 ──
[providers.mimo]
type = "mimo"
base_url = "https://api.xiaomimimo.com/v1"
api_key = "sk-..."
model_name = "mimo-v2.5-pro-ultraspeed"
priority = 1
```

降级行为：
- ASR 未配置（`is_dashscope=false`、`is_mimo=false`、`base_url=""`）→
  `/api/voice/ws` 建立后下发 `{"event":"error","error":"语音识别服务未配置"}` 并关闭
- `tts_enabled=false` → 只回文本事件不播报
- LLM 调用失败（无 key / 网络错误）→ 下发 `{"event":"error","error":"生成失败: ..."}`

### 4. 构建前端 + 启动

```bash
# 在项目根目录执行
bash scripts/build.sh     # npm install + vite build → backend/static/（已有构建产物可跳过）
bash scripts/start.sh
```

默认日志：`weave-talk/weave-talk.log`；PID：`weave-talk/weave-talk.pid`。

### 5. 验证

#### 5.1 健康检查

```bash
curl http://127.0.0.1:8203/healthz
# 期望：{"status":"ok","service":"weave-talk","database":"ok","voice_enabled":true}
```

#### 5.2 HTTP 会话与消息

```bash
TOKEN=$(curl -sS -X POST http://127.0.0.1:8203/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"test","password":"123456"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

curl -sS -X POST http://127.0.0.1:8203/api/voice/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title":"本地验证"}'
```

#### 5.3 WebSocket 双工链路验证

```bash
cat > /tmp/weave-talk-ws-test.py <<'PY'
import asyncio, json, os, websockets

async def recv_until(ws, wanted, timeout=60):
    while True:
        raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
        if isinstance(raw, bytes):
            continue  # TTS 播报音频帧
        m = json.loads(raw)
        if m.get("event") == wanted:
            return m

async def main():
    token = os.environ["TOKEN"]
    sid = os.environ["SID"]
    async with websockets.connect(
        f"ws://127.0.0.1:8203/api/voice/ws?token={token}&conversation_id={sid}"
    ) as ws:
        assert (await recv_until(ws, "session"))["event"] == "session"
        assert (await recv_until(ws, "ready"))["event"] == "ready"
        await ws.send(json.dumps({"event": "text", "text": "你好，请做个简单的自我介绍"}, ensure_ascii=False))
        assert (await recv_until(ws, "user_turn"))["event"] == "user_turn"
        done = await recv_until(ws, "assistant_text")
        while not done.get("done"):
            done = await recv_until(ws, "assistant_text")
        print("assistant:", done["text"])
        await ws.send(json.dumps({"event": "stop"}))

asyncio.run(main())
PY

TOKEN=$TOKEN SID=<会话ID> python3 /tmp/weave-talk-ws-test.py
```

注意：客户端文本若过短/无语义（如单独 "smoke"），语音助手的意图分类子代理会判定
为噪声并下发 `user_turn_cancelled` + `ignored`（服务原生语义，非错误）。

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 注册 |
| POST | /api/auth/login | 登录（返回 access_token） |
| POST | /api/auth/logout | 登出 |
| GET | /api/auth/me | 当前用户 |
| GET | /api/voice/sessions | 语音会话列表（挂在"语音助理"下） |
| POST | /api/voice/sessions | 新建语音会话 |
| GET | /api/voice/sessions/{id}/messages | 会话消息历史 |
| WS | /api/voice/ws?token=&conversation_id= | 全双工语音会话 |

## FAQ

- **为什么 WS 第一个事件是 session 而不是 ready？** 协议设计如此：先发
  session（会话 ID + assistant ID）再发 ready（tts 能力）。
- **语音输入没有反应？** 检查 [asr] 配置：三种模式必须至少一种可用；
  ASR 未配置时服务会在 WS 建立后下发 error 并关闭连接。
- **有回复但没有声音？** `[voice].tts_enabled=false` 时只回文本事件；或检查
  `tts_base_url`/`[providers.mimo]` 配置。
- **改了 config_model.toml 不生效？** 需重启服务（配置仅在启动时加载）。
- **测试账号？** `test / 123456`（首次启动自动创建）。
