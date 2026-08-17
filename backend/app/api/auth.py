from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db, User, UserSession
from app.schemas.chat import UserCreate, UserResponse, LoginRequest, TokenResponse
from app.services.auth_service import hash_password, verify_password, create_access_token
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["auth"])


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
    result = await db.execute(select(User).where(User.username == login_req.username))
    user = result.scalar_one_or_none()

    if not user or not await verify_password(login_req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    user.last_login_at = datetime.utcnow()
    user.last_login_ip = request.client.host if request.client else None
    await db.commit()


    access_token = create_access_token(user.id, user.username)

    user_agent = request.headers.get("user-agent", "")

    user_session = UserSession(
        user_id=user.id,
        session_token=access_token,
        ip_address=request.client.host if request.client else None,
        user_agent=user_agent,
        last_active_at=datetime.utcnow()
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
    current_user: User = Depends(__import__("app.core.deps", fromlist=["get_current_user"]).get_current_user)
):
    return _user_response(current_user)


@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(__import__("app.core.deps", fromlist=["get_current_user"]).get_current_user)
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