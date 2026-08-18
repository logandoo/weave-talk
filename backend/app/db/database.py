import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, relationship

from app.core.config import get_config

logger = logging.getLogger(__name__)

config = get_config()

def utcnow() -> datetime:
    """naive UTC 当前时间（数据库 DateTime 列为 naive，与既有数据一致）。"""
    return datetime.now(UTC).replace(tzinfo=None)


Base = declarative_base()

IS_SQLITE = config.database_type == "sqlite"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    agent_permissions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    assistants = relationship("Assistant", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    asr_hotwords = relationship("UserAsrHotword", back_populates="user", cascade="all, delete-orphan")


class Assistant(Base):
    __tablename__ = "assistants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    system_prompt = Column(Text, default="")
    temperature = Column(Float, nullable=True)
    top_p = Column(Float, nullable=True)
    top_k = Column(Integer, nullable=True)
    presence_penalty = Column(Float, nullable=True)
    frequency_penalty = Column(Float, nullable=True)
    max_tokens = Column(Integer, nullable=True)
    use_custom_model = Column(Boolean, default=False)
    custom_api_url = Column(String(500), nullable=True)
    custom_api_key = Column(String(500), nullable=True)
    custom_model_name = Column(String(200), nullable=True)
    provider_type = Column(String(20), default="deepseek")
    extra_body = Column(Text, nullable=True)
    # PHASE 3: optional sub-task LLM override. Keeping these NULL means
    # iterations reuse the main client with thinking forced off (the
    # default for all existing assistants).
    subtask_custom_api_url = Column(String(500), nullable=True)
    subtask_custom_api_key = Column(String(500), nullable=True)
    subtask_custom_model_name = Column(String(200), nullable=True)
    subtask_provider_type = Column(String(20), nullable=True)
    subtask_extra_body = Column(Text, nullable=True)
    use_subtask_model = Column(Boolean, default=False)
    thinking_budget = Column(Integer, nullable=True)
    # Qwen3.8(VLLM) provider: non-thinking sampling set (min_p / repetition_penalty
    # join the existing temperature/top_p/top_k/presence_penalty) plus the
    # thinking-mode sampling set and preserve_thinking (chat_template_kwargs).
    min_p = Column(Float, nullable=True)
    repetition_penalty = Column(Float, nullable=True)
    thinking_temperature = Column(Float, nullable=True)
    thinking_top_p = Column(Float, nullable=True)
    thinking_top_k = Column(Integer, nullable=True)
    thinking_min_p = Column(Float, nullable=True)
    thinking_presence_penalty = Column(Float, nullable=True)
    thinking_repetition_penalty = Column(Float, nullable=True)
    preserve_thinking = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    conversations = relationship("Conversation", back_populates="assistant", cascade="all, delete-orphan")
    user = relationship("User", back_populates="assistants")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assistant_id = Column(String(36), ForeignKey("assistants.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), default="新对话")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    # Deathmatch (死磕) mode
    deathmatch_mode = Column(Boolean, default=False)
    deathmatch_goal = Column(Text, nullable=True)
    deathmatch_status = Column(String(20), default="inactive")
    deathmatch_turns = Column(Integer, default=0)
    deathmatch_max_turns = Column(Integer, default=30)
    deathmatch_consecutive_failures = Column(Integer, default=0)
    deathmatch_verdict = Column(Text, nullable=True)
    deathmatch_reason = Column(Text, nullable=True)
    deathmatch_grilling_complete = Column(Boolean, default=False)
    deathmatch_grilling_total = Column(Integer, default=0)
    deathmatch_grilling_completed = Column(Integer, default=0)
    deathmatch_grilling_round = Column(Integer, default=0)
    deathmatch_grilling_round_total = Column(Integer, default=3)
    deathmatch_grilling_qa_history = Column(JSON, default=list)
    deathmatch_context_summary = Column(Text, nullable=True)
    deathmatch_expected_marker = Column(Text, nullable=True)
    deathmatch_marker_miss_count = Column(Integer, default=0)
    deathmatch_compressed_context = Column(Text, nullable=True)
    # PEVR (Plan-Execute-Verify-Replan) extension — see loop_improve.md Phase 3
    deathmatch_plan = Column(JSON, nullable=True)            # structured plan {steps:[...]}
    deathmatch_plan_version = Column(Integer, default=0)     # bumped on each replan
    deathmatch_reflections = Column(JSON, default=list)       # recent reflection entries
    deathmatch_wall_time_started_at = Column(DateTime, nullable=True)
    deathmatch_max_wall_time_seconds = Column(Integer, default=3600)
    deathmatch_wall_time_used_seconds = Column(Integer, default=0)  # cumulative across resume cycles (C1)
    deathmatch_bible_draft = Column(JSON, nullable=True)  # story-bible draft written right after grilling (creative goals)
    deathmatch_subgoals = Column(JSON, default=list)  # user-appended acceptance criteria mid-loop (D3)
    deathmatch_last_verification_result = Column(JSON, nullable=True)
    deathmatch_verify_failures = Column(Integer, default=0)   # consecutive verifier non-complete
    deathmatch_human_gate = Column(Text, nullable=True)       # structured human-gate report

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    user = relationship("User", back_populates="conversations")
    assistant = relationship("Assistant", back_populates="conversations")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"))
    role = Column(String(20))
    content = Column(Text)
    reasoning_content = Column(Text, nullable=True)
    tool_results = Column(Text, nullable=True)
    # PHASE 2B: OpenAI-style tool_calls array (JSON-encoded list of
    # {id, type:"function", function:{name, arguments}}). Persisted so
    # multi-turn conversations replay structured tool history through the
    # LLM context instead of just opaque content text.
    tool_calls = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(512), unique=True, index=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    last_active_at = Column(DateTime, default=utcnow)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="sessions")


class UserAsrHotword(Base):
    __tablename__ = "user_asr_hotwords"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(120), nullable=False)
    weight = Column(Integer, nullable=False, default=4)
    lang = Column(String(10), nullable=True)
    dashscope_vocabulary_id = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="asr_hotwords")


_engine_kwargs: dict = {"echo": False, "pool_pre_ping": True}
if IS_SQLITE:
    # SQLite（aiosqlite）：队列池默认即可；busy_timeout 防止写锁竞争直接抛
    # "database is locked"。WAL + foreign_keys 由 _register_sqlite_pragmas 施加。
    _engine_kwargs["connect_args"] = {"timeout": 30}
else:
    _engine_kwargs.update(
        pool_size=config.database_pool_size,
        max_overflow=config.database_max_overflow,
        pool_timeout=config.database_pool_timeout,
        pool_recycle=config.database_pool_recycle,
    )

engine = create_async_engine(config.database_url, **_engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def _register_sqlite_pragmas(target_engine) -> None:
    """SQLite 连接级 PRAGMA：WAL（并发读/写不互斥）+ 外键强制（SQLite 默认关闭）+ 忙等待。

    PRAGMA 是 per-connection 的（journal_mode 除外），必须挂 connect 事件；
    foreign_keys 关闭时 ON DELETE CASCADE 等约束不会生效。
    """
    from sqlalchemy import event

    @event.listens_for(target_engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()


if IS_SQLITE:
    _register_sqlite_pragmas(engine)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
