# weave-talk

> English (default) · [中文版](README.md)

A **full-duplex voice conversation service**:
end-to-end ASR → LLM → TTS pipeline over a real-time WebSocket, with barge-in, interjection and an emotion system, no tool calling (pure voice conversation).

## Highlights

- **True full-duplex**: WebSocket event protocol `session/ready/state/user_turn/assistant_text/speaking_start/interrupted/ended` — speak while listening, interrupt anytime
- **Barge-in**: TTS stops the moment the user starts speaking; `_norm_barge_compare` does fragment-level normalization comparison, with dedicated short-fragment judgment
- **EoT (End-of-Turn) judgment**: intent-classifier sub-agent + semantic check dual channel, with a `_eot_watchdog` timeout backstop
- **Emotion system**: emotion state decays across the conversation (`_decay_emotion`) and can drive interjection text and TTS style (`_speak_interjection`)
- **3 ASR modes, configurable**: DashScope realtime streaming (fun-asr-realtime / qwen3-asr-flash-realtime), MiMo streaming, generic HTTP transcription
- **Configurable TTS**: MiMo mimo-v2.5-tts (OpenAI-compatible streaming), voice & style instruction support
- **Multi-provider LLM routing**: any OpenAI-compatible base_url; `[providers.*]` routes by priority, falling back to the first available provider (default first) when the named one is missing
- **Graceful degradation**: no ASR config → WS sends an error event and closes; TTS off → text-only events; no LLM → fallback copy
- **Frontend**: Vue3 voice UI (VoiceChat component + useVoiceDuplex duplex client)

## Directory Structure

```
weave-talk/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entry, health check, test user
│   │   ├── core/config.py     # config loading (trimmed Config, supports config_model.toml merge)
│   │   ├── core/deps.py       # JWT auth dependency
│   │   ├── db/database.py     # 6 models
│   │   ├── api/auth.py        # register/login/me
│   │   ├── api/voice.py       # session API + /api/voice/ws full-duplex WebSocket
│   │   ├── services/voice_service.py  # session orchestration (trimmed: no tool calling)
│   │   ├── services/asr_service.py    # ASR (verbatim copy)
│   │   ├── services/tts_service.py    # TTS (verbatim copy)
│   │   ├── services/llm_service.py    # LLM (verbatim copy)
│   │   └── ...
│   ├── config.toml           # infra section (server/security/database, committable)
│   ├── config_model.toml     # model section ([api]/[asr]/[voice]/[providers], real keys, not committed)
│   ├── static/               # frontend build artifacts
│   └── requirements.txt
├── frontend/                 # Vue3 + Vite (voice conversation frontend)
└── scripts/                  # install_venv/init_db/start/stop/restart/build
```

## Prerequisites

| Dependency | Version | Notes |
|------|---------|------|
| OS | - | macOS / Ubuntu 22.04+ / Windows (WSL2 recommended; Git Bash on native Windows) |
| Python | 3.11+ (3.13 recommended) | Ubuntu 24.04 ships 3.12; 22.04: `add-apt-repository ppa:deadsnakes/ppa && sudo apt install python3.12`; macOS: `brew install python@3.13`; Windows: python.org installer (check Add to PATH) |
| Node.js | 18+ (frontend build only) | macOS: `brew install node`; Ubuntu: `sudo apt install nodejs npm` (24.04 ships 18) or NodeSource; Windows: `winget install OpenJS.NodeJS.LTS` |

> Database defaults to **SQLite** (zero external deps, auto-created on first launch).
> For PostgreSQL 14+, change `[database] type = "postgres"` in `backend/config.toml`.

## Standalone Deployment (3 steps)

This project does not depend on any outer directory layout:

```bash
bash scripts/install_venv.sh   # project .venv + deps (idempotent; PYTHON_BIN to override interpreter)
bash scripts/init_db.sh        # initializes by [database] type: sqlite no-PG; postgres idempotent create+prebuild
bash scripts/start.sh          # start (auto-picks .venv)
curl http://127.0.0.1:8203/healthz
```

## Deployment Steps

### 1. Database

**Recommended (self-contained)**: run the project script — it handles SQLite pre-create / PostgreSQL idempotent create + prebuild (repeatable):

```bash
bash scripts/init_db.sh
```

**SQLite (default)**: nothing to do; `backend/weave_talk.db` is created on first launch.

**PostgreSQL (optional)**: requires local PostgreSQL 14+:
macOS: `brew install postgresql@16 && brew services start postgresql@16`;
Ubuntu: `sudo apt install postgresql && sudo systemctl start postgresql`;
Windows: use WSL2 and follow the Ubuntu steps.
The script idempotently runs `createdb weave_talk`; or manually:

```bash
createdb -U postgres -h 127.0.0.1 weave_talk
```

Authentication notes: macOS/Homebrew uses trust auth locally (no password needed). Ubuntu's
default local TCP auth is scram: first run `sudo -u postgres psql -c "ALTER USER postgres PASSWORD '<strong password>'"`,
then `export PGPASSWORD='<strong password>'` when running scripts (init_db.sh passes it through),
and write the same password into `[database] password` in `backend/config.toml`
(the service reads config only, not environment variables).

> In the family monorepo you may run `bash <family-root>/scripts/init_databases.sh`
> (equivalent to each project's `scripts/init_db.sh` in order).

### 2. Virtual Environment

**Recommended (self-contained)**:

```bash
bash scripts/install_venv.sh
```

Equivalent manual steps:

```bash
python3.11 -m venv .venv     # or python3.13
./.venv/bin/pip install -r backend/requirements.txt
```

### 3. Configuration

Infrastructure section in `backend/config.toml` (committable template):

```toml
[server]
host = "127.0.0.1"
port = 8203

[security]
jwt_secret_key = "change-me-to-a-long-random-string"

[database]
# type = "sqlite" (default) | "postgres"
type = "sqlite"
path = "weave_talk.db"
# postgres mode uses these fields:
# host = "127.0.0.1"
# port = 5432
# username = "postgres"
# password = ""
# name = "weave_talk"
```

Model section in `backend/config_model.toml` (not committed, contains real keys;
`[api]/[asr]/[voice]/[providers]` blocks merge and override wholesale):

```toml
# ── LLM (final fallback when voice_* is not covered) ──
[api]
base_url = "https://api.deepseek.com/v1"
api_key = "sk-..."
model_name = "deepseek-v4-flash"

# ── ASR (pick one of three) ──
[asr]
is_dashscope = true           # DashScope realtime streaming (fun-asr-realtime)
dashscope_api_key = "sk-..."
dashscope_model = "fun-asr-realtime"
# is_mimo = true              # or MiMo streaming (qwen3-asr)
# base_url = "..."            # or generic HTTP transcription (when both streaming flags are false)

# ── Voice conversation ──
[voice]
enabled = true
identity = ""                     # assistant name (optional, default used when empty)
provider = "default"          # [providers.*] route key; falls back to [api] when missing
model_name = "deepseek-v4-flash"
temperature = 0.7
max_tokens = 1024
context_turns = 8
disable_thinking = true
# 50+ keys for barge-in/EoT/fragment-merge/noise-gating/interjection/emotion (defaults provided)

# system prompt: tone / style-word constraints / no-emoji, etc. (no tool instructions; freely configurable)
system_prompt = "你是一个全双工语音对话助手，正在与用户进行实时语音交流。请严格遵守以下要求：..."

# ── TTS (MiMo mimo-v2.5-tts) ──
tts_enabled = true
tts_base_url = ""             # empty = fall back to [providers.mimo]
tts_api_key = ""
tts_model = "mimo-v2.5-tts"
tts_voice = "冰糖"
tts_style_instruction = "用自然、亲切、口语化的语气，语速适中，像朋友聊天一样温暖。"

# ── Multi-provider routing ──
[providers.mimo]
type = "mimo"
base_url = "https://api.xiaomimimo.com/v1"
api_key = "sk-..."
model_name = "mimo-v2.5-pro-ultraspeed"
priority = 1
```

Degradation behavior:
- No ASR config (`is_dashscope=false`, `is_mimo=false`, `base_url=""`) →
  `/api/voice/ws` sends `{"event":"error","error":"语音识别服务未配置"}` after connect and closes
- `tts_enabled=false` → text events only, no playback
- LLM call failure (no key / network error) → sends `{"event":"error","error":"生成失败: ..."}`

### 4. Build Frontend + Start

```bash
# run from the project root
bash scripts/build.sh     # npm install + vite build → backend/static/ (skip if prebuilt exists)
bash scripts/start.sh
```

Default log: `weave-talk/weave-talk.log`; PID: `weave-talk/weave-talk.pid`.

### 5. Verify

#### 5.1 Health check

```bash
curl http://127.0.0.1:8203/healthz
# expect: {"status":"ok","service":"weave-talk","database":"ok","voice_enabled":true}
```

#### 5.2 HTTP sessions & messages

```bash
TOKEN=$(curl -sS -X POST http://127.0.0.1:8203/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"test","password":"123456"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

curl -sS -X POST http://127.0.0.1:8203/api/voice/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title":"local check"}'
```

#### 5.3 WebSocket full-duplex verification

```bash
cat > /tmp/weave-talk-ws-test.py <<'PY'
import asyncio, json, os, websockets

async def recv_until(ws, wanted, timeout=60):
    while True:
        raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
        if isinstance(raw, bytes):
            continue  # TTS audio frames
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

TOKEN=$TOKEN SID=<session-id> python3 /tmp/weave-talk-ws-test.py
```

Note: overly short / non-semantic client text (e.g., bare "smoke") is judged as noise by the
intent-classifier sub-agent, which emits `user_turn_cancelled` + `ignored` (native semantics, not an error).

## API Overview

| Method | Path | Description |
|------|------|------|
| POST | /api/auth/register | register |
| POST | /api/auth/login | login (returns access_token) |
| POST | /api/auth/logout | logout |
| GET | /api/auth/me | current user |
| GET | /api/voice/sessions | voice session list (under "voice assistant") |
| POST | /api/voice/sessions | create voice session |
| GET | /api/voice/sessions/{id}/messages | session message history |
| WS | /api/voice/ws?token=&conversation_id= | full-duplex voice session |

## FAQ

- **Why is the first WS event `session` and not `ready`?** By protocol design,
  `session` (session ID + assistant ID) comes first, then `ready` (TTS capability).
- **Voice input does nothing?** Check the [asr] config — at least one of the three modes must be available;
  with no ASR, the service sends an error event and closes the connection.
- **Reply but no sound?** `[voice].tts_enabled=false` produces text events only; or check
  `tts_base_url`/`[providers.mimo]`.
- **config_model.toml changes not applied?** Restart the service (config loads at startup only).
- **Test account?** `test / 123456` (auto-created on first launch).

## Security Notes

- **Default test account**: `test / 123456` is auto-created on first start with
  no protection — **development use only**. Before exposing to the public
  internet, delete the database so only your registered account exists, or
  customize `_ensure_test_user` in `backend/app/main.py`.
- **JWT secret**: never hardcoded. Read from `JWT_SECRET_KEY` env var first;
  otherwise auto-generated and persisted to `backend/.jwt_secret` (gitignored)
  on first start. Set the env var explicitly for public deployments.
- **CORS**: default `cors_allow_origins = ["*"]` with credentials force-disabled
  (browser spec). Use an explicit origin allow-list when credentials are needed.
- **Login rate limit**: 10 failures / 60s window per (username, IP) → 429.
  Behind a reverse proxy all clients share the proxy IP — adjust or disable
  (`login_rate_limit_max = 0`) as needed.
- **Logout revokes instantly**: JWTs are recorded in `user_sessions` on login
  and removed on logout — a logged-out token returns 401 immediately.
