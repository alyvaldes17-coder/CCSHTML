from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from datetime import datetime
from typing import Optional
from auth_server.schemas import (
    RegisterRequest, LoginRequest, 
    TokenResponse, LoginResponse, ValidateResponse, RevokeResponse
)
from auth_server.models import User, PlanType
from auth_server.services import create_access_token, verify_token, UserService
from auth_server.database import get_session

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    session: Session = Depends(get_session)
):
    """Register new user"""
    
    # Check user doesn't exist
    existing = UserService.get_user_by_email(session, request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = UserService.create_user(
        session,
        email=request.email,
        password=request.password,
        plan=PlanType.STARTER
    )
    
    # Generate token
    token, expires = create_access_token(
        email=user.email,
        plan=user.plan.value,
        hwid="00000000-0000-0000-0000-000000000000"
    )
    
    return TokenResponse(
        token=token,
        plan=user.plan.value,
        expires_in=30*86400,
        max_accounts=user.max_accounts
    )

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    session: Session = Depends(get_session)
):
    """Login user"""
    
    # Authenticate
    user = UserService.authenticate_user(session, request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token
    token, expires = create_access_token(
        email=user.email,
        plan=user.plan.value,
        hwid="00000000-0000-0000-0000-000000000000"
    )
    
    return LoginResponse(
        token=token,
        expires=expires.isoformat(),
        plan=user.plan.value,
        max_accounts=user.max_accounts
    )

@router.get("/validate", response_model=ValidateResponse)
async def validate(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    x_hwid: str = Header(default="00000000-0000-0000-0000-000000000000"),
    session: Session = Depends(get_session)
):
    """Validate token + HWID"""
    
    # Extract token from credentials
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token, x_hwid)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Get user
    email = payload.get("sub")
    user = UserService.get_user_by_email(session, email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return ValidateResponse(
        valid=True,
        email=user.email,
        plan=user.plan.value,
        max_accounts=user.max_accounts,
        expires=datetime.fromtimestamp(payload.get("exp")).isoformat() if payload.get("exp") else None
    )

@router.post("/revoke", response_model=RevokeResponse)
async def revoke(session: Session = Depends(get_session)):
    """Revoke token (logout)"""
    
    return RevokeResponse(
        ok=True,
        message="Token revoked"
    )
