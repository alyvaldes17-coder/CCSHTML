from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

# Config
ALGORITHM = "HS256"
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ACCESS_TOKEN_EXPIRE_DAYS = 30

# Password hashing - usando pbkdf2_sha256 (más compatible)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(email: str, plan: str, hwid: str) -> tuple[str, datetime]:
    """
    Create JWT token
    Returns: (token, expires_at)
    """
    expires = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    payload = {
        "sub": email,
        "plan": plan,
        "hwid": hwid,
        "exp": expires,
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expires

def verify_token(token: str, hwid: str) -> dict | None:
    """
    Verify JWT token
    Returns: payload dict or None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify HWID matches
        token_hwid = payload.get("hwid")
        if token_hwid != hwid:
            return None  # HWID mismatch
        
        return payload
    except JWTError:
        return None
