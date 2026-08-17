#!/usr/bin/env bash
# Weave Talk 前端构建：npm install → npm run build → dist 复制到 backend/static。
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FE="$DIR/frontend"
STATIC="$DIR/backend/static"

cd "$FE"
if [[ ! -d node_modules ]]; then
  echo "npm install ..."
  npm install
fi
echo "npm run build ..."
npm run build

rm -rf "$STATIC"
mkdir -p "$STATIC"
cp -R "$FE/dist/." "$STATIC/"
echo "前端构建完成，产物已复制到 $STATIC"
