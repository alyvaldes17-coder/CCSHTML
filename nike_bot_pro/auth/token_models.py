# auth/token_models.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class TokenData:
    account_name: str
    email: Optional[str]
    auth_cookie: str
    vtex_session: str
    vtex_segment: str
    expires_at: Optional[str] = None
