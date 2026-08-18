from collections import defaultdict, deque
from datetime import UTC, datetime
from time import monotonic

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_config
from app.core.deps import get_current_user
from app.db.database import User, UserSession, get_db
from app.schemas.chat import LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

# 登录失败限流：按 (用户名, IP) 维度滑动窗口计数，窗口内失败超阈值返回 429。
# 进程内状态（单 worker 部署）；防暴力破解而非精确节流。
_fail_log: dict = defaultdict(deque)


def _too_many_login_failures(username: str, client_ip: str) -> bool:
    cfg = get_config()
    limit = cfg.security_login_rate_limit_max
    if limit <= 0:
        return False
    window = cfg.security_login_rate_limit_window_seconds
    key = (username, client_ip)
    q = _fail_log[key]
    now = monotonic()
    while q and now - q[0] > window:
        q.popleft()
    if not q:
        # 窗口过期后清空 key，防止 (username, IP) 组合无限累积
        _fail_log.pop(key, None)
        return False
    return len(q) >= limit


def _record_login_failure(username: str, client_ip: str) -> None:
    cfg = get_config()
    if cfg.security_login_rate_limit_max <= 0:
        return
    _fail_log[(username, client_ip)].append(monotonic())


def _user_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        created_at=user.created_at.isoformat(),
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    if not request.username or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名和密码不能为空"
        )
    if len(request.username) < 2 or len(request.username) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名长度必须在2-50个字符之间"
        )
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度不能少于6个字符"
        )

    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已存在"
        )

    user = User(
        username=request.username,
        password_hash=await hash_password(request.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)


    return _user_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, login_req: LoginRequest, db: AsyncSession = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    if _too_many_login_failures(login_req.username, client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="登录失败次数过多，请稍后再试",
        )

    result = await db.execute(select(User).where(User.username == login_req.username))
    user = result.scalar_one_or_none()

    if not user or not await verify_password(login_req.password, user.password_hash):
        _record_login_failure(login_req.username, client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    user.last_login_at = datetime.now(UTC).replace(tzinfo=None)
    user.last_login_ip = client_ip
    await db.commit()


    access_token = create_access_token(user.id, user.username)

    user_agent = request.headers.get("user-agent", "")

    user_session = UserSession(
        user_id=user.id,
        session_token=access_token,
        ip_address=client_ip,
        user_agent=user_agent,
        last_active_at=datetime.now(UTC).replace(tzinfo=None)
    )
    db.add(user_session)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=_user_response(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return _user_response(current_user)


@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        result = await db.execute(
            select(UserSession).where(
                UserSession.user_id == current_user.id,
                UserSession.session_token == token
            )
        )
        session = result.scalar_one_or_none()
        if session:
            await db.delete(session)
            await db.commit()

    return {"message": "Logged out successfully"}
