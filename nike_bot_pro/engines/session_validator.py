# engines/session_validator.py
"""
Validador de sesión VTEX.
Asegura que las cookies estén válidas antes de ejecutar backend.
"""
import logging
from typing import Optional
import requests


class SessionValidator:
    """
    Valida sesión VTEX haciendo una llamada real a OrderForm.
    
    ⚠️ PRINCIPIO CLAVE:
    Una sesión es válida si VTEX permite crear/leer un OrderForm.
    No validamos por nombre de cookies (VTEX las cambia todo el tiempo).
    """

    VTEX_API_BASE = "https://www.nike.cl"
    ORDERFORM_ENDPOINT = "/api/checkout/pub/orderForm"

    def __init__(self, log: Optional[object] = None):
        self.log = log or logging.getLogger("SessionValidator")

    def has_valid_cookies(self, session: requests.Session) -> bool:
        """
        Verifica que una sesión sea válida haciendo una llamada real a VTEX OrderForm.
        
        ✅ VÁLIDA SI:
        - Status 200 + OrderForm response OK
        - OrderForm tiene orderFormId
        
        ❌ INVÁLIDA SI:
        - Status 401/403 (Unauthorized)
        - No hay respuesta JSON
        - No hay orderFormId
        - Timeout / error de conexión
        
        Args:
            session: requests.Session (debe tener cookies del perfil)
        
        Retorna: True si VTEX acepta la sesión, False en caso contrario
        """
        try:
            url = f"{self.VTEX_API_BASE}{self.ORDERFORM_ENDPOINT}"
            
            resp = session.get(url, timeout=5)
            
            # Status 200 es OBLIGATORIO
            if resp.status_code != 200:
                self.log.warning(
                    f"❌ VTEX rechazó sesión (status {resp.status_code}). "
                    f"Cookies inválidas o expiradas."
                )
                return False
            
            # Parsear JSON
            try:
                data = resp.json()
            except Exception as e:
                self.log.warning(f"❌ OrderForm no es JSON válido: {e}")
                return False
            
            # VALIDACIÓN CRÍTICA: orderFormId debe existir
            if not isinstance(data, dict) or "orderFormId" not in data:
                self.log.warning(
                    f"❌ OrderForm válido pero sin orderFormId. "
                    f"Estructura rota o sesión corrupta."
                )
                return False
            
            # ✅ ÉXITO: sesión VTEX válida
            self.log.debug(f"✅ Sesión VTEX válida (orderFormId: {data.get('orderFormId')})")
            return True
            
        except requests.exceptions.Timeout:
            self.log.warning(f"⚠️ Timeout validando cookies (5s). VTEX lento.")
            return False
            
        except requests.exceptions.ConnectionError:
            self.log.warning(f"❌ No hay conexión a VTEX. Revisa internet.")
            return False
            
        except Exception as e:
            self.log.error(f"❌ Error inesperado validando cookies: {e}")
            return False

    def get_cookie_names(self, session: requests.Session) -> set:
        """Retorna nombres de cookies en la sesión (solo para debug)"""
        try:
            return {c.name for c in session.cookies}
        except:
            return set()

    def assert_valid_cookies(self, session: requests.Session):
        """Lanza excepción si las cookies no son válidas"""
        if not self.has_valid_cookies(session):
            raise RuntimeError(
                "❌ VTEX rechazó la sesión. "
                "Cookies inválidas o expiradas. "
                "Ejecuta LOGIN y luego SESSION_SEED."
            )
