"""Auth Routes - Authentication & Token Management"""
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from datetime import datetime
from typing import Optional

# Use absolute imports - proper for FastAPI/Uvicorn context
from auth_server.database import get_session
from auth_server.models import User, PlanType
from auth_server.schemas import (
    RegisterRequest, LoginRequest, 
    TokenResponse, LoginResponse, ValidateResponse, RevokeResponse
)
from auth_server.services import UserService
from auth_server.core.security import TokenManager, HWIDManager, get_token_manager

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Get token manager (TODO: inyectar desde config)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "nike-bot-pro-dev-secret-key-min-32-chars-change-prod-2026")
token_manager = get_token_manager(SECRET_KEY)


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    x_hwid: str = Header(..., description="Hardware ID"),
    session: Session = Depends(get_session)
):
    """
    Register new user con HWID validation.
    
    Headers:
    - X-HWID: Hardware ID del dispositivo (obligatorio)
    """
    
    # Validar que HWID no esté vacío
    if not x_hwid or x_hwid == "00000000-0000-0000-0000-000000000000":
        raise HTTPException(status_code=400, detail="HWID inválido - por favor proporciona X-HWID válido")
    
    # Verificar que usuario no exista
    existing = UserService.get_user_by_email(session, request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Crear usuario
    user = UserService.create_user(
        session,
        email=request.email,
        password=request.password,
        plan=PlanType.STARTER
    )
    
    # Generar token con HWID + IP binding
    token, expires = token_manager.create_token(
        email=user.email,
        plan=user.plan.value,
        hwid=x_hwid,
        ip_address=None  # TODO: extraer de request.client.host
    )
    
    return TokenResponse(
        token=token,
        plan=user.plan.value,
        expires_in=int((expires - datetime.utcnow()).total_seconds()),
        max_accounts=user.max_accounts
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    x_hwid: str = Header(..., description="Hardware ID"),
    session: Session = Depends(get_session)
):
    """
    Login con HWID validation.
    
    Headers:
    - X-HWID: Hardware ID del dispositivo (obligatorio)
    """
    
    # Validar que HWID no esté vacío
    if not x_hwid or x_hwid == "00000000-0000-0000-0000-000000000000":
        raise HTTPException(status_code=400, detail="HWID inválido - por favor proporciona X-HWID válido")
    
    # Autenticar usuario
    user = UserService.authenticate_user(session, request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generar token con HWID
    token, expires = token_manager.create_token(
        email=user.email,
        plan=user.plan.value,
        hwid=x_hwid,
        ip_address=None  # TODO: extraer de request.client.host
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
    x_hwid: str = Header(..., description="Hardware ID"),
    x_forwarded_for: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    """
    Validate token + HWID + IP (opcional).
    
    CRÍTICO: Sin validación exitosa cada X minutos = BLOQUEADO.
    
    Headers:
    - Authorization: Bearer {token} (obligatorio)
    - X-HWID: Hardware ID (obligatorio)
    - X-Forwarded-For: IP del cliente (opcional, para IP binding)
    """
    
    token = credentials.credentials
    
    try:
        # Validar token con HWID + IP
        payload = token_manager.validate_token(
            token=token,
            provided_hwid=x_hwid,
            client_ip=x_forwarded_for,
            require_re_auth=True  # Exige re-auth cada X minutos
        )
    except HTTPException as e:
        raise e
    
    # Obtener usuario de la DB
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
async def revoke(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
):
    """
    Revoke token (logout).
    Instantáneamente inválido en el servidor.
    """
    token = credentials.credentials
    token_manager.revoke_token(token)
    
    return RevokeResponse(
        ok=True,
        message="Token revoked - logout exitoso"
    )
