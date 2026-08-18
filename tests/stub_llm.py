"""确定性 OpenAI 兼容 LLM 桩服务（weave-talk 测试用）。

走真实 HTTP 链路（http.server + SSE），避免外部 LLM 依赖：
- 流式：SSE data: {"choices":[{"delta":{"content":"..."}}]}
- 非流式：普通 JSON

用法: python3 tests/stub_llm.py [port]  默认 18099
"""
import json
import sys
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer

REPLY = "你好呀，我是你的语音助手，这是一条用于验证的确定性回复。"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("[stub-llm] %s\n" % (fmt % args))

    def _reply_json(self, body):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            payload = {}
        is_stream = bool(payload.get("stream"))

        if is_stream:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            for piece in REPLY:
                chunk = {
                    "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": payload.get("model", "stub"),
                    "choices": [{"index": 0, "delta": {"content": piece}, "finish_reason": None}],
                }
                self.wfile.write(b"data: " + json.dumps(chunk, ensure_ascii=False).encode("utf-8") + b"\n\n")
                self.wfile.flush()
            final = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": payload.get("model", "stub"),
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            self.wfile.write(b"data: " + json.dumps(final).encode("utf-8") + b"\n\n")
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
        else:
            body = json.dumps({
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": payload.get("model", "stub"),
                "choices": [{"index": 0, "message": {"role": "assistant", "content": REPLY}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 1, "completion_tokens": len(REPLY), "total_tokens": 1 + len(REPLY)},
            }).encode("utf-8")
            self._reply_json(body)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 18099
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"stub LLM listening on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
