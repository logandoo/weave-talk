#!/usr/bin/env bash
# 创建本项目本地虚拟环境并安装依赖（幂等：已有 .venv 则复用并同步依赖）。
# 自动探测 3.11+ 的 Python 解释器（代码使用了 3.11+ 语法）；
# 优先级：环境变量 PYTHON_BIN > python3.13 > python3.12 > python3.11 > python3 > python > py（若 ≥3.11）。
# 跨平台：macOS/Linux 用 .venv/bin/python，Windows 用 .venv/Scripts/python.exe 均可识别。
#
# 用法：bash scripts/install_venv.sh
# 环境变量：
#   PYTHON_BIN  解释器（显式指定时跳过自动探测）
#   VENV_DIR    venv 位置（默认 <项目根>/.venv）
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$DIR/.venv}"

# venv 内解释器路径（跨平台）：优先 bin/python（mac/Linux），其次 Scripts/python.exe（Windows）
venv_python() {
  local base="$1"
  if [[ -x "$base/bin/python" || -x "$base/bin/python3" ]]; then
    if [[ -x "$base/bin/python" ]]; then printf '%s' "$base/bin/python"; else printf '%s' "$base/bin/python3"; fi
    return 0
  fi
  if [[ -f "$base/Scripts/python.exe" ]]; then
    printf '%s' "$base/Scripts/python.exe"
    return 0
  fi
  return 1
}

is_modern() {
  "$1" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null
}

if [[ -n "${PYTHON_BIN:-}" ]]; then
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "未找到解释器 ${PYTHON_BIN}" >&2
    exit 1
  fi
  if ! is_modern "$PYTHON_BIN"; then
    echo "${PYTHON_BIN} 版本过低（$("$PYTHON_BIN" -V 2>&1)）。本项目需要 Python 3.11+，可用 PYTHON_BIN 指定解释器。" >&2
    exit 1
  fi
else
  PYTHON_BIN=""
  for cand in python3.13 python3.12 python3.11 python3 python py; do
    if command -v "$cand" >/dev/null 2>&1 && is_modern "$cand"; then
      PYTHON_BIN="$cand"
      break
    fi
  done
  if [[ -z "$PYTHON_BIN" ]]; then
    echo "未找到 Python 3.11+ 解释器（已尝试 python3.13/3.12/3.11/python3/python/py）。" >&2
    echo "  Ubuntu 24.04 自带 3.12；Ubuntu 22.04 需 add-apt-repository ppa:deadsnakes/ppa && sudo apt install python3.12 后重试。" >&2
    echo "  macOS: brew install python@3.13；Windows: 从 python.org 安装并勾选 Add to PATH。" >&2
    echo "  或用 PYTHON_BIN=... 显式指定解释器。" >&2
    exit 1
  fi
fi

if ! VP="$(venv_python "$VENV_DIR")" 2>/dev/null || ! is_modern "$VP"; then
  if [[ -e "$VENV_DIR" ]]; then
    echo "现有 $VENV_DIR 的解释器低于 3.11，删除重建"
    rm -rf "$VENV_DIR"
  fi
  echo "创建虚拟环境: ${VENV_DIR}（${PYTHON_BIN} $("$PYTHON_BIN" -V 2>&1)）"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
else
  echo "虚拟环境已存在，复用: ${VENV_DIR}"
fi

VENV_PY="$(venv_python "$VENV_DIR")" || { echo "无法定位 venv 解释器: $VENV_DIR" >&2; exit 1; }
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install -r "$DIR/backend/requirements.txt"
echo "依赖安装完成: $VENV_DIR"
