from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ========== Auth Requests ==========

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str  # min 8 chars, reqs uppercase, lowercase, digit

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ValidateTokenRequest(BaseModel):
    token: str
    hwid: str  # Enviado en header X-HWID

class RevokeTokenRequest(BaseModel):
    token: str

# ========== Auth Responses ==========

class TokenResponse(BaseModel):
    token: str
    plan: str
    expires_in: int  # seconds
    max_accounts: int

class LoginResponse(BaseModel):
    token: str
    expires: str  # ISO format
    plan: str
    max_accounts: int

class ValidateResponse(BaseModel):
    valid: bool
    email: Optional[str] = None
    plan: Optional[str] = None
    max_accounts: Optional[int] = None
    expires: Optional[str] = None

class RevokeResponse(BaseModel):
    ok: bool
    message: str

# ========== Admin ==========

class UserResponse(BaseModel):
    id: int
    email: str
    plan: str
    max_accounts: int
    is_active: bool
    created_at: datetime

class UpdatePlanRequest(BaseModel):
    plan: str  # 'starter', 'pro', 'elite'

# ========== Error Responses ==========

class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
