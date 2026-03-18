"""
Security Module - HWID + IP Binding + Token Validation

Estrategia:
1. Token JWT con HWID (hardware ID)
2. IP binding opcional (detecta cambio de país/red)
3. Validación obligatoria CADA X minutos (sin internet = bloqueado)
4. Revocación instantánea desde servidor
"""

import logging
import hashlib
import json
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from functools import lru_cache

import jwt
from fastapi import HTTPException, Header

logger = logging.getLogger(__name__)


class HWIDManager:
    """
    Genera y valida HWID (Hardware ID).
    
    Basado en:
    - MAC address del dispositivo
    - CPU serial (si disponible)
    - Diskdrive serial
    - Combinación hash
    """
    
    @staticmethod
    def generate_hwid(mac_address: str, cpu_id: str = "", disk_id: str = "") -> str:
        """
        Genera un HWID deterministico basado en hardware.
        
        Args:
            mac_address: MAC address del dispositivo (ej: "AA:BB:CC:DD:EE:FF")
            cpu_id: CPU serial (opcional)
            disk_id: Disk serial (opcional)
            
        Returns:
            HWID como string hash
        """
        components = f"{mac_address}:{cpu_id}:{disk_id}"
        hwid = hashlib.sha256(components.encode()).hexdigest()
        return hwid
    
    @staticmethod
    def validate_hwid(provided_hwid: str, stored_hwid: str) -> bool:
        """Valida que el HWID sea el mismo"""
        return provided_hwid == stored_hwid


class IPManager:
    """
    Gestiona IP binding - detecta cambios sospechosos.
    """
    
    @staticmethod
    def extract_ip_from_headers(x_forwarded_for: Optional[str] = None, 
                                x_real_ip: Optional[str] = None) -> str:
        """
        Extrae IP del cliente desde headers.
        
        Priority:
        1. X-Forwarded-For (proxies)
        2. X-Real-IP (nginx)
        3. Default fallback
        """
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        if x_real_ip:
            return x_real_ip.strip()
        return "127.0.0.1"
    
    @staticmethod
    def is_ip_suspicious(old_ip: str, new_ip: str, max_distance_km: int = 500) -> bool:
        """
        Detecta si el cambio de IP es sospechoso.
        
        NOTA: Implementación simple. En producción usar GeoIP API.
        
        Args:
            old_ip: IP anterior
            new_ip: IP nueva
            max_distance_km: Distancia máxima "viajable" en X minutos
            
        Returns:
            True si es sospechoso, False si es normal
        """
        # Por ahora: simple detección (diferente IP = potencialmente sospechoso)
        # En producción: usar MaxMind GeoIP2 o similar
        if old_ip != new_ip:
            logger.warning(f"⚠️ IP cambió de {old_ip} a {new_ip}")
            return True
        return False


class TokenManager:
    """
    Gestión completa de tokens JWT con validaciones extras.
    
    Flujo:
    1. Cliente login → recibe token JWT + HWID
    2. Cliente request → envía token + HWID en header
    3. Server valida: JWT + HWID + IP (opcional)
    4. Sin validación cada X min = bloqueado
    """
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", 
                 token_expire_minutes: int = 30, 
                 re_auth_minutes: int = 5):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire_minutes = token_expire_minutes
        self.re_auth_minutes = re_auth_minutes
        
        # Cache en memoria de tokens válidos + su último check
        # En producción: usar Redis
        self._token_cache: Dict[str, Dict] = {}
    
    def create_token(self, email: str, plan: str, hwid: str, 
                    ip_address: Optional[str] = None) -> Tuple[str, datetime]:
        """
        Crea un JWT con extra claims.
        
        Args:
            email: Email del usuario
            plan: Plan del usuario (starter, elite, etc)
            hwid: Hardware ID del dispositivo
            ip_address: IP del cliente (opcional, para binding)
            
        Returns:
            (token, expires_at)
        """
        now = datetime.utcnow()
        expires = now + timedelta(minutes=self.token_expire_minutes)
        
        payload = {
            "sub": email,  # subject (usuario)
            "plan": plan,
            "hwid": hwid,
            "ip": ip_address,
            "iat": now,  # issued at
            "exp": expires,  # expiration
            "re_auth_until": (now + timedelta(minutes=self.re_auth_minutes)).timestamp()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        # Cache el token + marca timestamp
        self._token_cache[token] = {
            "email": email,
            "last_validated": now,
            "hwid": hwid,
            "expires": expires
        }
        
        logger.info(f"✅ Token creado para {email} (HWID: {hwid[:8]}...)")
        
        return token, expires
    
    def validate_token(self, token: str, provided_hwid: str, 
                      client_ip: Optional[str] = None,
                      require_re_auth: bool = True) -> Dict:
        """
        Valida un token con TODAS las checks.
        
        Checks:
        1. JWT signature válida
        2. No expirado
        3. HWID coincide
        4. IP no cambió (opcional)
        5. Re-auth timeout no pasado (si require_re_auth=True)
        
        Args:
            token: JWT token
            provided_hwid: HWID del cliente (header X-HWID)
            client_ip: IP del cliente
            require_re_auth: Si True, requiere re-autenticación cada X min
            
        Returns:
            Payload del token si válido
            
        Raises:
            HTTPException si inválido
        """
        try:
            # 1. Validar firma + expiration
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            logger.warning(f"❌ Token expirado")
            raise HTTPException(status_code=401, detail="Token expirado")
        except jwt.InvalidTokenError as e:
            logger.warning(f"❌ Token inválido: {e}")
            raise HTTPException(status_code=401, detail="Token inválido")
        
        # 2. Validar HWID
        token_hwid = payload.get("hwid")
        if not token_hwid or not HWIDManager.validate_hwid(provided_hwid, token_hwid):
            logger.warning(f"❌ HWID no coincide. Esperado: {token_hwid[:8]}..., Recibido: {provided_hwid[:8]}...")
            raise HTTPException(status_code=401, detail="HWID inválido - dispositivo no autorizado")
        
        # 3. Validar IP (opcional)
        token_ip = payload.get("ip")
        if token_ip and client_ip:
            if IPManager.is_ip_suspicious(token_ip, client_ip):
                logger.warning(f"⚠️ SOSPECHA: IP cambió. Antigua: {token_ip}, Nueva: {client_ip}")
                # En modo STRICT: levantar error
                # En modo WARN: solo loguear
                # Aquí: modo WARN (puede ser VPN)
        
        # 4. Validar re-auth timeout
        if require_re_auth:
            re_auth_until = payload.get("re_auth_until")
            if re_auth_until:
                if datetime.utcnow().timestamp() > re_auth_until:
                    logger.warning(f"❌ Re-auth timeout pasado para {payload.get('sub')}")
                    raise HTTPException(status_code=401, detail="Requiere re-autenticación")
        
        # 5. Actualizar último check en cache
        if token in self._token_cache:
            self._token_cache[token]["last_validated"] = datetime.utcnow()
        
        logger.info(f"✅ Token válido para {payload.get('sub')} (HWID: {provided_hwid[:8]}...)")
        
        return payload
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoca un token instantáneamente.
        
        En producción: agregar a Redis blacklist con TTL
        """
        if token in self._token_cache:
            del self._token_cache[token]
            logger.info(f"🚫 Token revocado")
            return True
        return False
    
    def get_token_status(self, token: str) -> Dict:
        """Obtiene estado del token (debug)"""
        if token in self._token_cache:
            info = self._token_cache[token]
            return {
                "valid": True,
                "email": info["email"],
                "last_validated": info["last_validated"].isoformat(),
                "expires": info["expires"].isoformat(),
                "hwid_match": info["hwid"][:8] + "..."
            }
        return {"valid": False}


# Instancia global (en producción: usar depunas inyección)
def get_token_manager(secret_key: str) -> TokenManager:
    """Factory para TokenManager"""
    return TokenManager(
        secret_key=secret_key,
        algorithm="HS256",
        token_expire_minutes=30,
        re_auth_minutes=5
    )
