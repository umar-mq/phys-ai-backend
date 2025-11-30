import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: f"u_{uuid.uuid4()}", primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str
    password_hash: str
    image: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SessionModel(SQLModel, table=True):
    __tablename__ = "session"  # "Session" is a reserved word in some contexts
    
    token: str = Field(primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic Schemas for Auth API (Request/Response)

class SignUpRequest(SQLModel):
    email: str
    password: str
    name: str
    image: Optional[str] = None

class SignInRequest(SQLModel):
    email: str
    password: str

class UserResponse(SQLModel):
    id: str
    email: str
    name: str
    image: Optional[str] = None

class SessionResponse(SQLModel):
    token: str

class AuthResponse(SQLModel):
    user: UserResponse
    session: SessionResponse