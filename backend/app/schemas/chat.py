from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any

class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    created_at: str
    agent_permissions: Optional[Dict[str, Any]] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
