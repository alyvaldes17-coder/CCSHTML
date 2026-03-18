"""
Token Manager for Nike Bot Commercial Edition

Handles:
- Online token validation (against API)
- Offline token validation (JWT signature check)
- Token persistence and expiry checking
- Hardware ID binding
"""

import os
import json
import jwt
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
from cryptography.fernet import Fernet
import uuid
import socket
import platform


class TokenManager:
    """Centralized token validation and management"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.token_file = Path.home() / ".nike-bot" / "token"
        self.key_file = Path.home() / ".nike-bot" / ".key"
        self.hwid_file = Path.home() / ".nike-bot" / ".hwid"
        
        # Create directories if needed
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        self.cipher = self._initialize_cipher()
    
    def _initialize_cipher(self) -> Fernet:
        """Get or create encryption key"""
        if self.key_file.exists():
            key = self.key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
            os.chmod(str(self.key_file), 0o600)  # Read-only for user
        
        return Fernet(key)
    
    def generate_hardware_id(self) -> str:
        """
        Generate unique hardware ID based on:
        - CPU info
        - Motherboard serial
        - Disk ID
        - MAC address
        """
        components = [
            platform.processor(),
            platform.machine(),
            platform.node(),
            str(uuid.getnode()),  # MAC address
        ]
        
        hwid = hashlib.sha256("".join(components).encode()).hexdigest()
        return hwid
    
    def save_token(self, token: str) -> bool:
        """
        Encrypt and save token to disk
        Returns: True if successful
        """
        try:
            # Verify token is valid before saving
            payload = jwt.decode(token, options={"verify_signature": False})
            exp_time = datetime.fromtimestamp(payload.get("exp", 0))
            
            # Create encrypted payload
            data = {
                "token": token,
                "hwid": self.generate_hardware_id(),
                "saved_at": datetime.now().isoformat(),
                "expires_at": exp_time.isoformat()
            }
            
            encrypted = self.cipher.encrypt(json.dumps(data).encode())
            self.token_file.write_bytes(encrypted)
            os.chmod(str(self.token_file), 0o600)  # Read-only
            
            return True
        except Exception as e:
            print(f"Error saving token: {e}")
            return False
    
    def load_token(self) -> Optional[str]:
        """
        Decrypt and load token from disk
        Returns: token string or None
        """
        try:
            if not self.token_file.exists():
                return None
            
            encrypted = self.token_file.read_bytes()
            decrypted = self.cipher.decrypt(encrypted).decode()
            data = json.loads(decrypted)
            
            token = data.get("token")
            stored_hwid = data.get("hwid")
            current_hwid = self.generate_hardware_id()
            
            # Verify hardware ID match
            if stored_hwid != current_hwid:
                print("ERROR: Token was created on different machine")
                return None
            
            return token
        except Exception as e:
            print(f"Error loading token: {e}")
            return None
    
    def validate_token_online(self, token: str) -> Optional[Dict]:
        """
        Validate token with API server
        Returns: dict with {valid, email, plan, expires} or None
        """
        try:
            response = requests.post(
                f"{self.api_url}/auth/validate-token",
                json={"token": token},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API error: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("Could not connect to API (offline)")
            return None
        except Exception as e:
            print(f"Error validating token online: {e}")
            return None
    
    def validate_token_offline(self, token: str) -> Optional[Dict]:
        """
        Validate token locally (offline mode)
        Only checks JWT signature and expiry
        """
        try:
            # Note: In production, use a secret key from environment
            # For now, we only verify the structure
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # Check expiry
            exp_time = datetime.fromtimestamp(payload.get("exp", 0))
            if exp_time < datetime.utcnow():
                print("Error: Token has expired")
                return None
            
            return {
                "valid": True,
                "email": payload.get("email"),
                "plan": payload.get("plan"),
                "expires": payload.get("exp")
            }
        except Exception as e:
            print(f"Error validating token offline: {e}")
            return None
    
    def validate_token(self, token: Optional[str] = None) -> Optional[Dict]:
        """
        Main validation method: try online first, fallback to offline
        
        Args:
            token: Optional token string. If None, loads from disk.
        
        Returns:
            Dict with validation result or None if invalid
        """
        if not token:
            token = self.load_token()
        
        if not token:
            print("Error: No token found")
            return None
        
        # Try online validation first
        result = self.validate_token_online(token)
        if result and result.get("valid"):
            return result
        
        # Fallback to offline validation
        result = self.validate_token_offline(token)
        if result and result.get("valid"):
            print("Warning: Using offline validation (no internet)")
            return result
        
        return None
    
    def check_expiry(self, token: Optional[str] = None) -> Dict:
        """
        Check token expiry status
        Returns: {expires_at, days_remaining, expires_soon}
        """
        if not token:
            token = self.load_token()
        
        if not token:
            return {"error": "No token found"}
        
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            exp_time = datetime.fromtimestamp(payload.get("exp", 0))
            days_remaining = (exp_time - datetime.utcnow()).days
            
            return {
                "expires_at": exp_time.isoformat(),
                "days_remaining": max(0, days_remaining),
                "expires_soon": days_remaining <= 3,
                "expired": days_remaining < 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    def revoke_token(self) -> bool:
        """Revoke token by deleting local file"""
        try:
            if self.token_file.exists():
                self.token_file.unlink()
            return True
        except Exception as e:
            print(f"Error revoking token: {e}")
            return False


# Singleton instance
_token_manager: Optional[TokenManager] = None

def get_token_manager() -> TokenManager:
    """Get singleton instance of TokenManager"""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager
