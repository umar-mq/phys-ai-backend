from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session, select
from datetime import datetime, timedelta

from app.database import get_session
from app.models import (
    User, SessionModel, 
    SignUpRequest, SignInRequest, 
    AuthResponse, UserResponse, SessionResponse
)
from app.auth_utils import get_password_hash, verify_password, generate_session_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/sign-up/email", response_model=AuthResponse, status_code=201)
async def sign_up(request: SignUpRequest, db: Session = Depends(get_session)):
    # 1. Check if user exists
    statement = select(User).where(User.email == request.email)
    existing_user = db.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # 2. Create User
    new_user = User(
        email=request.email,
        name=request.name,
        password_hash=get_password_hash(request.password),
        image=request.image
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 3. Create Session
    token = generate_session_token()
    # Default session expiry: 7 days
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    new_session = SessionModel(
        token=token,
        user_id=new_user.id,
        expires_at=expires_at
    )
    db.add(new_session)
    db.commit()

    return AuthResponse(
        user=UserResponse(id=new_user.id, email=new_user.email, name=new_user.name, image=new_user.image),
        session=SessionResponse(token=token)
    )

@router.post("/sign-in/email", response_model=AuthResponse)
async def sign_in(request: SignInRequest, db: Session = Depends(get_session)):
    # 1. Find User
    statement = select(User).where(User.email == request.email)
    user = db.exec(statement).first()
    
    # 2. Verify Password
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 3. Create Session
    token = generate_session_token()
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    new_session = SessionModel(
        token=token,
        user_id=user.id,
        expires_at=expires_at
    )
    db.add(new_session)
    db.commit()

    return AuthResponse(
        user=UserResponse(id=user.id, email=user.email, name=user.name, image=user.image),
        session=SessionResponse(token=token)
    )

@router.get("/session", response_model=AuthResponse | None)
async def get_current_session(
    authorization: str = Header(None), 
    db: Session = Depends(get_session)
):
    """
    Validates the Bearer token and returns the user session.
    Returns null if invalid or missing, rather than 401 (per spec behavior for 'Get Session').
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.split(" ")[1]
    
    # 1. Find Session
    session_record = db.get(SessionModel, token)
    if not session_record:
        return None
    
    # 2. Check Expiry
    if session_record.expires_at < datetime.utcnow():
        # Clean up expired session
        db.delete(session_record)
        db.commit()
        return None

    # 3. Get User
    user = db.get(User, session_record.user_id)
    if not user:
        return None

    return AuthResponse(
        user=UserResponse(id=user.id, email=user.email, name=user.name, image=user.image),
        session=SessionResponse(token=token)
    )