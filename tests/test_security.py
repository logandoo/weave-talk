"""weave-talk 安全与工程修复验收测试（wave-2026-08-18）。

运行前提：weave-talk 服务已在 127.0.0.1:8203 运行（scripts/start.sh）。
测试用例从 README + acceptance.md wave2 标准导出。
注意：WS 文本路径测试会真实调用 LLM（config 配置的 provider），耗时可达 60s。
"""
import asyncio
import json
import sys

import httpx

BASE = "http://127.0.0.1:8203"
USER = "test"
PASSWORD = "123456"


def login(client: httpx.Client) -> dict:
    r = client.post(f"{BASE}/api/auth/login", json={"username": USER, "password": PASSWORD})
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return r.json()


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_logout_invalidates_token(client: httpx.Client) -> None:
    token = login(client)["access_token"]
    r = client.get(f"{BASE}/api/auth/me", headers=auth_headers(token))
    assert r.status_code == 200, "pre-logout /me should be 200"
    r = client.post(f"{BASE}/api/auth/logout", headers=auth_headers(token))
    assert r.status_code == 200, f"logout failed: {r.status_code}"
    r = client.get(f"{BASE}/api/auth/me", headers=auth_headers(token))
    assert r.status_code == 401, f"post-logout /me should be 401, got {r.status_code}"


def test_other_token_still_valid_after_logout(client: httpx.Client) -> None:
    t1 = login(client)["access_token"]
    t2 = login(client)["access_token"]
    client.post(f"{BASE}/api/auth/logout", headers=auth_headers(t1))
    r1 = client.get(f"{BASE}/api/auth/me", headers=auth_headers(t1))
    assert r1.status_code == 401, f"logged-out token must be 401, got {r1.status_code}"
    r2 = client.get(f"{BASE}/api/auth/me", headers=auth_headers(t2))
    assert r2.status_code == 200, f"live token must stay 200, got {r2.status_code}"


def test_cors_star_forces_no_credentials(client: httpx.Client) -> None:
    r = client.options(
        f"{BASE}/api/auth/login",
        headers={"Origin": "http://evil.example.com", "Access-Control-Request-Method": "POST"},
    )
    assert r.status_code in (200, 400, 405), f"preflight failed: {r.status_code}"
    acc = r.headers.get("access-control-allow-credentials", "false")
    if r.headers.get("access-control-allow-origin", ""):
        assert acc.lower() == "false", (
            f"allow_origins=['*'] must not pair with credentials=true; got ACC={acc}"
        )


def test_login_rate_limit(client: httpx.Client) -> None:
    """连续失败（不存在的用户名）超阈值后返回 429，不泄露用户是否存在。"""
    code = 401
    for i in range(1, 12):
        r = client.post(
            f"{BASE}/api/auth/login",
            json={"username": "probe_ratelimit_不存在", "password": "wrong"},
        )
        code = r.status_code
    assert code == 429, f"rate limit should kick in with 429, got {code}"


def test_no_test_backdoor(client: httpx.Client) -> None:
    """生产 WS 协议不得再接受 _test_inject_asr 注入事件。"""
    token = login(client)["access_token"]
    sid = client.post(
        f"{BASE}/api/voice/sessions", headers=auth_headers(token)
    ).json()["id"]
    result = _ws_roundtrip(token, sid, inject_test_event=True)
    assert result is not None, "WS must respond (even with an error) but not hang"
    assert result != "injected", "_test_inject_asr must be removed; got injected ASR text"


def test_ws_text_path_without_asr(client: httpx.Client) -> None:
    """ASR 未配置时文本输入路径必须可用（memory 承诺），不得 error 退出。"""
    token = login(client)["access_token"]
    sid = client.post(
        f"{BASE}/api/voice/sessions", headers=auth_headers(token)
    ).json()["id"]
    result = _ws_roundtrip(token, sid, inject_test_event=False)
    assert result == "assistant_done", (
        f"text path must work without ASR; got {result!r}"
    )


def _ws_roundtrip(token: str, sid: str, inject_test_event: bool) -> str:
    """打开 WS → 等 ready → 发 text（或 _test_inject_asr）→ 等 assistant_text done。"""

    async def main() -> str:
        import websockets

        url = f"ws://127.0.0.1:8203/api/voice/ws?token={token}&conversation_id={sid}"
        async with websockets.connect(url) as ws:
            events = []
            sent_text = False
            deadline = asyncio.get_event_loop().time() + 45
            while asyncio.get_event_loop().time() < deadline:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=12)
                except asyncio.TimeoutError:
                    continue
                except websockets.ConnectionClosed as exc:
                    return f"closed:{exc.code}"
                if isinstance(raw, bytes):
                    continue
                m = json.loads(raw)
                events.append(m.get("event"))
                if m.get("event") == "ready" and not sent_text:
                    if inject_test_event:
                        await ws.send(json.dumps({
                            "event": "_test_inject_asr", "text": "测试注入文本",
                        }, ensure_ascii=False))
                    else:
                        await ws.send(json.dumps({
                            "event": "text", "text": "你好，请用一句话介绍你自己",
                        }, ensure_ascii=False))
                    sent_text = True
                if inject_test_event:
                    if m.get("event") == "asr_segment" and m.get("text") == "测试注入文本":
                        return "injected"
                else:
                    if m.get("event") == "assistant_text" and m.get("done"):
                        return "assistant_done"
                if m.get("event") == "error":
                    return f"error:{m.get('error', '')[:60]}"
            return "timeout"

    return asyncio.run(main())


def _require_voice_enabled() -> None:
    """预检：WS 用例需要 voice_enabled=true，否则快速失败而非长超时。"""
    r = httpx.get(f"{BASE}/healthz", timeout=10)
    assert r.status_code == 200, f"healthz failed: {r.status_code}"
    if not r.json().get("voice_enabled"):
        raise AssertionError(
            "voice_enabled=false — WS 用例无法运行。请用 tests/run_security_suite.sh "
            "启动（它会以含 [voice] enabled=true 的测试配置重启服务）。"
        )


def main() -> None:
    client = httpx.Client(timeout=30)
    tests = [
        test_logout_invalidates_token,
        test_other_token_still_valid_after_logout,
        test_cors_star_forces_no_credentials,
        test_login_rate_limit,
        test_no_test_backdoor,
        test_ws_text_path_without_asr,
    ]
    # WS 用例预检（其余用例不依赖 voice_enabled）
    if "test_ws_text_path_without_asr" in sys.argv[1:] or len(sys.argv) == 1:
        try:
            _require_voice_enabled()
        except AssertionError as exc:
            print(f"SKIP test_ws_text_path_without_asr: {exc}")
            tests = [t for t in tests if t is not test_ws_text_path_without_asr]
    failures = 0
    for t in tests:
        name = t.__name__
        try:
            t(client)
            print(f"PASS {name}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {name}: {exc}")
        except Exception as exc:
            failures += 1
            print(f"ERROR {name}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
