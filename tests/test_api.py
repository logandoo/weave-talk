"""weave-talk REST API 回归测试（wave-2026-08-18 重建）。

运行前提：weave-talk 服务已在 127.0.0.1:8203 运行（scripts/start.sh）。
覆盖：auth / 会话 REST（sessions 列表/创建/消息）/ healthz / 登出失效。
WS 双工协议由 test_security.py 覆盖（stub LLM 驱动）。
"""
import sys
import uuid

import httpx

BASE = "http://127.0.0.1:8203"
PASSED = 0
FAILED = 0


def check(name: str, fn) -> None:
    global PASSED, FAILED
    try:
        fn()
        PASSED += 1
        print(f"PASS {name}")
    except AssertionError as exc:
        FAILED += 1
        print(f"FAIL {name}: {exc}")
    except Exception as exc:
        FAILED += 1
        print(f"ERROR {name}: {type(exc).__name__}: {exc}")


def main():
    client = httpx.Client(timeout=30, base_url=BASE)
    tok = client.post("/api/auth/login", json={"username": "test", "password": "123456"})
    assert tok.status_code == 200, f"login: {tok.status_code} {tok.text}"
    token = tok.json()["access_token"]
    H = {"Authorization": f"Bearer {token}"}
    TAG = uuid.uuid4().hex[:8]

    def t_healthz():
        r = client.get("/healthz")
        assert r.status_code == 200 and r.json()["status"] == "ok"

    def t_session_create_list():
        r = client.post("/api/voice/sessions", headers=H)
        assert r.status_code == 200, f"create session: {r.status_code} {r.text}"
        sid = r.json()["id"]
        r2 = client.get("/api/voice/sessions", headers=H)
        assert r2.status_code == 200 and any(s["id"] == sid for s in r2.json())

    def t_session_messages_empty():
        sid = client.post("/api/voice/sessions", headers=H).json()["id"]
        r = client.get(f"/api/voice/sessions/{sid}/messages", headers=H)
        assert r.status_code == 200 and r.json() == []

    def t_session_missing_404():
        r = client.get(f"/api/voice/sessions/nonexistent_{TAG}/messages", headers=H)
        assert r.status_code == 404

    def t_unauthorized():
        r = client.get("/api/voice/sessions")
        assert r.status_code == 401, f"no token should 401, got {r.status_code}"

    def t_logout_revokes():
        t2 = client.post("/api/auth/login", json={"username": "test", "password": "123456"}).json()["access_token"]
        H2 = {"Authorization": f"Bearer {t2}"}
        assert client.get("/api/auth/me", headers=H2).status_code == 200
        client.post("/api/auth/logout", headers=H2)
        assert client.get("/api/auth/me", headers=H2).status_code == 401

    check("healthz", t_healthz)
    check("session_create_list", t_session_create_list)
    check("session_messages_empty", t_session_messages_empty)
    check("session_missing_404", t_session_missing_404)
    check("unauthorized", t_unauthorized)
    check("logout_revokes", t_logout_revokes)

    print(f"\n{PASSED}/{PASSED + FAILED} passed")
    sys.exit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
