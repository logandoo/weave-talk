"""Weave Talk — 双工语音对话后端入口。

路由：/api/auth/*（注册/登录/me/logout）+ /api/voice/*（语音会话 REST + 双工 WebSocket）。
启动时：校验 JWT 密钥、init_db()、创建 audio_files 目录、确保测试用户存在。
前端构建产物位于 backend/static（由 scripts/build.sh 生成后复制）。
"""
import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import select

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
)

from app.api import auth, voice  # noqa: E402
from app.core.config import get_config  # noqa: E402
from app.db.database import AsyncSessionLocal, init_db, User  # noqa: E402
from app.services.http_client import close_shared_async_client  # noqa: E402

logger = logging.getLogger(__name__)

config = get_config()

app = FastAPI(title="Weave Talk API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.security_cors_allow_origins,
    allow_credentials=config.security_cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(voice.router)


async def _ensure_test_user() -> None:
    """确保 test 用户存在（前端/测试可直接登录：test / 123456）。"""
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.username == "test"))
            if result.scalar_one_or_none() is None:
                from app.services.auth_service import hash_password

                user = User(
                    username="test",
                    password_hash=await hash_password("123456"),
                )
                db.add(user)
                await db.commit()
                logger.info("test user created (test / 123456)")
    except Exception as exc:
        logger.warning("test user ensure failed: %s", exc)


@app.on_event("startup")
async def startup_event():
    if not config.security_jwt_secret_key:
        raise RuntimeError("JWT secret key is not configured")

    audio_files_dir = os.path.join(os.path.dirname(__file__), "..", "audio_files")
    os.makedirs(audio_files_dir, exist_ok=True)
    await init_db()
    await _ensure_test_user()


@app.on_event("shutdown")
async def shutdown_event():
    await close_shared_async_client()


@app.get("/healthz")
async def healthz():
    return {
        "status": "ok",
        "voice_enabled": config.voice_enabled,
    }


static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
index_path = os.path.join(static_dir, "index.html")


@app.get("/")
def root():
    if os.path.isfile(index_path):
        return FileResponse(index_path, media_type="text/html", headers={"Cache-Control": "no-store"})
    return {"message": "Weave Talk API is running", "docs": "/docs"}


# SPA catch-all: serve static assets, fall back to index.html for client-side
# routes (/login、/voice 等由前端路由接管).
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    if full_path.startswith("api/") or full_path == "healthz":
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not Found")
    if full_path:
        file_path = os.path.realpath(os.path.join(static_dir, full_path))
        if file_path.startswith(os.path.realpath(static_dir) + os.sep) and os.path.isfile(file_path):
            return FileResponse(file_path)
    if os.path.isfile(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"detail": "Not Found"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=config.server_host,
        port=config.server_port,
        reload=False,
    )
