#!/usr/bin/env bash
# Weave Talk 启动脚本。
# venv 回落序：PYTHON 环境变量 > 项目 .venv > family 根 .venv > /tmp/weave-family-venv。
# 可用环境变量覆盖运行参数：HOST / PORT / LOG_FILE / PID_FILE。
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAMILY_DIR="$(dirname "$DIR")"

if [[ -n "${PYTHON:-}" ]]; then
  VENV_PYTHON="$PYTHON"
else
  VENV_PYTHON=""
  for _v in "$DIR/.venv" "$FAMILY_DIR/.venv" /tmp/weave-family-venv; do
    if [[ -x "$_v/bin/python" ]]; then VENV_PYTHON="$_v/bin/python"; break; fi
    if [[ -f "$_v/Scripts/python.exe" ]]; then VENV_PYTHON="$_v/Scripts/python.exe"; break; fi
  done
  if [[ -z "$VENV_PYTHON" ]]; then
    echo "未找到 Python 虚拟环境。请先执行：bash scripts/install_venv.sh" >&2
    exit 1
  fi
fi

PID_FILE="${PID_FILE:-$DIR/weave-talk.pid}"
LOG_FILE="${LOG_FILE:-$DIR/weave-talk.log}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8203}"

if [[ -f "$PID_FILE" ]]; then
  PID="$(cat "$PID_FILE")"
  if kill -0 "$PID" >/dev/null 2>&1; then
    echo "weave-talk 已在运行 (PID: $PID)"
    exit 0
  fi
  rm -f "$PID_FILE"
fi

cd "$DIR/backend"
export PYTHONDONTWRITEBYTECODE=1
echo "启动 weave-talk: http://$HOST:$PORT (日志: $LOG_FILE)"
nohup "$VENV_PYTHON" -m uvicorn app.main:app --host "$HOST" --port "$PORT" >"$LOG_FILE" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" >"$PID_FILE"
sleep 1
if kill -0 "$NEW_PID" >/dev/null 2>&1; then
  echo "启动成功 (PID: $NEW_PID)"
else
  echo "启动失败，最近日志：" >&2
  tail -n 40 "$LOG_FILE" >&2 || true
  rm -f "$PID_FILE"
  exit 1
fi
