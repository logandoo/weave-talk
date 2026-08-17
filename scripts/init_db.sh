#!/usr/bin/env bash
# 初始化 weave-talk 数据库（幂等，可重复执行）。
# 按 backend/config.toml 的 [database] type 分发：
#   type = "sqlite"   → 无需 PostgreSQL；有 venv 时经 init_db 预建库文件+表
#                       （无 venv 也无需任何操作：服务首次启动自动建）
#   type = "postgres" → 幂等创建 weave_talk PG 数据库 + 经 init_db 预建表
#
# 用法：bash scripts/init_db.sh
# PG 参数可用环境变量覆盖：PGUSER / PGHOST / PGPORT / PGPASSWORD
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAMILY_DIR="$(dirname "$DIR")"
PGUSER="${PGUSER:-postgres}"
PGHOST="${PGHOST:-127.0.0.1}"
PGPORT="${PGPORT:-5432}"
export PGPASSWORD="${PGPASSWORD:-}"

if [[ -n "${PYTHON:-}" ]]; then
  VENV_PYTHON="$PYTHON"
else
  VENV_PYTHON=""
  for _v in "$DIR/.venv" "$FAMILY_DIR/.venv" /tmp/weave-family-venv; do
    if [[ -x "$_v/bin/python" ]]; then VENV_PYTHON="$_v/bin/python"; break; fi
    if [[ -f "$_v/Scripts/python.exe" ]]; then VENV_PYTHON="$_v/Scripts/python.exe"; break; fi
  done
fi

# 读取 backend/config.toml [database] 段的 type 值（缺 key 时默认 sqlite，与后端解析一致）
cfg_db_type() {
  local cfg="$DIR/backend/config.toml"
  if [[ ! -f "$cfg" ]]; then
    echo "缺少 ${cfg}，无法确定 [database] type" >&2
    exit 1
  fi
  awk '/^\[database\]/{f=1;next} /^\[/{f=0} f && /^[[:space:]]*type[[:space:]]*=/' "$cfg" \
    | sed -E "s/^[[:space:]]*type[[:space:]]*=[[:space:]]*[\"\']?([A-Za-z]+).*/\1/" \
    | tr '[:upper:]' '[:lower:]'
}

precreate_tables() {
  if [[ -z "$VENV_PYTHON" ]]; then
    echo "  未找到 Python venv，跳过预建表（服务首次启动时自动创建；可先运行 scripts/install_venv.sh）"
    return 0
  fi
  if (cd "$DIR/backend" && "$VENV_PYTHON" -c \
      "import asyncio; from app.db.database import init_db; asyncio.run(init_db())"); then
    echo "  表结构已预建（init_db）"
  else
    echo "  init_db 预建失败，请检查日志" >&2
    exit 1
  fi
}

db_type="$(cfg_db_type)"
[[ -n "$db_type" ]] || db_type="sqlite"
case "$db_type" in
  sqlite)
    echo "weave-talk 数据库类型: sqlite"
    echo "  库文件 backend/*.db 首次启动自动创建，无需 PostgreSQL"
    precreate_tables
    ;;
  postgres)
    echo "weave-talk 数据库类型: postgres"
    if ! command -v psql >/dev/null 2>&1; then
      echo "未找到 psql。postgres 分支需先安装 PostgreSQL 14+（macOS: brew install postgresql@16；" >&2
      echo "Ubuntu: sudo apt install postgresql；Windows 建议 WSL2 后按 Ubuntu 步骤）。" >&2
      exit 1
    fi
    if psql -U "$PGUSER" -h "$PGHOST" -p "$PGPORT" -d postgres -tAc \
        "SELECT 1 FROM pg_database WHERE datname='weave_talk'" | grep -q 1; then
      echo "  PG 数据库 weave_talk 已存在，跳过创建"
    else
      createdb -U "$PGUSER" -h "$PGHOST" -p "$PGPORT" weave_talk
      echo "  PG 数据库 weave_talk 创建完成"
    fi
    precreate_tables
    ;;
  *)
    echo "未知的 [database] type: ${db_type}（应为 sqlite 或 postgres）" >&2
    exit 1
    ;;
esac
echo "weave-talk 数据库初始化完成"
