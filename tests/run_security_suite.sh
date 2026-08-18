#!/usr/bin/env bash
# weave-talk 安全/WS 测试套件 runner（自包含）：
#   1. 生成临时测试 config_model（[voice] enabled=true + stub provider）
#   2. 启动 stub LLM（tests/stub_llm.py）
#   3. 以 CONFIG_MODEL_PATH 指向测试配置重启服务
#   4. 跑 test_api.py + test_security.py（完整含 WS 用例）
#   5. 恢复默认配置并重启服务
# 用法：bash tests/run_security_suite.sh
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$DIR/.venv/bin/python}"
STUB_PORT="${STUB_PORT:-18199}"

echo "== 1/5 生成测试 config_model =="
TEST_CFG="$(mktemp /tmp/weave_talk_test_cfg.XXXXXX.toml)"
cat > "$TEST_CFG" << TOML
[api]
base_url = "http://127.0.0.1:${STUB_PORT}/v1"
api_key = "stub"
model_name = "stub"

[voice]
enabled = true
provider = "stubtest"
model_name = "stub"

[providers.stubtest]
base_url = "http://127.0.0.1:${STUB_PORT}/v1"
api_key = "stub"
model_name = "stub"
priority = 99

[asr]
is_dashscope = true
dashscope_api_key = ""
TOML
echo "test config: $TEST_CFG"

echo "== 2/5 启动 stub LLM (:${STUB_PORT}) =="
"$PYTHON_BIN" "$DIR/tests/stub_llm.py" "$STUB_PORT" > /tmp/weave_talk_stub_llm.log 2>&1 &
STUB_PID=$!
trap 'kill $STUB_PID 2>/dev/null || true; rm -f "$TEST_CFG"' EXIT
sleep 1
curl -fsS -X POST "http://127.0.0.1:${STUB_PORT}/v1/chat/completions" \
  -H 'Content-Type: application/json' \
  -d '{"model":"stub","messages":[{"role":"user","content":"hi"}]}' > /dev/null || { echo "stub LLM failed to start"; cat /tmp/weave_talk_stub_llm.log; exit 1; }

echo "== 3/5 以测试配置重启 weave-talk =="
CONFIG_MODEL_PATH="$TEST_CFG" bash "$DIR/scripts/restart.sh"
sleep 3
curl -fsS http://127.0.0.1:8203/healthz > /dev/null || { echo "service failed to start"; exit 1; }

echo "== 4/5 运行测试套件 =="
"$PYTHON_BIN" "$DIR/tests/test_api.py"
"$PYTHON_BIN" "$DIR/tests/test_security.py"

echo "== 5/5 恢复默认配置并重启 =="
bash "$DIR/scripts/restart.sh"
sleep 3
curl -fsS http://127.0.0.1:8203/healthz > /dev/null
echo "SUITE PASSED"
