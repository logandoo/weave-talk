#!/usr/bin/env bash
# 转发到 canonical 脚本 scripts/start.sh（用户约定的生命周期入口）。
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "$DIR/scripts/start.sh"
