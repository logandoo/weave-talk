#!/usr/bin/env bash
# 转发到 canonical 脚本 scripts/build.sh（用户约定的前端构建入口）。
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "$DIR/scripts/build.sh"
