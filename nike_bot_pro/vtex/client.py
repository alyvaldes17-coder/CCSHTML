"""
================================================================================
vtex/client.py — Cliente VTEX Unificado
================================================================================
Fusión de: curl_client.py + tls_client_vtex.py + vtex_client.py

Uso:
    client = VtexClient(base_url, cookies, user_agent, transport="curl")
    client = VtexClient(base_url, cookies, user_agent, transport="tls")
    client = VtexClient(base_url, cookies, user_agent, transport="httpx")

transport="curl" → Máxima evasión WAF (producción)
transport="tls"  → TLS fingerprinting anti-Cloudflare
transport="httpx"→ HTTP/2, más rápido (tests/debug)
================================================================================
"""

import json
import logging
import subprocess
from typing import Optional

# Imports opcionales según transport
try:
    import httpx
    _HTTPX_OK = True
except ImportError:
    _HTTPX_OK = False

try:
    import tls_client as _tls_client
    _TLS_OK = True
except ImportError:
    _TLS_OK = False


class VtexClient:
    """
    Cliente VTEX unificado con transport configurable.
    Un solo objeto, tres modos de transporte.
    """

    def __init__(
        self,
        base_url: str,
        cookies: dict,
        user_agent: str = None,
        order_form_id: str = None,
        transport: str = "curl",   # "curl" | "tls" | "httpx"
        log_level: str = "INFO",
    ):
        self.base_url = base_url.rstrip("/")
        self.cookies = cookies or {}
        self.order_form_id = order_form_id
        self.transport = transport
        self.log = logging.getLogger("VtexClient")
        self.log.setLevel(log_level.upper())

        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

        # Inicializar sesión según transport
        self._session = None
        if transport == "tls":
            if not _TLS_OK:
                raise RuntimeError("tls-client no instalado. Ejecuta: pip install tls-client")
            self._session = _tls_client.Session(
                client_identifier="chrome_124",
                random_tls_extension_order=True
            )
            if self.cookies:
                self._session.cookies.update(self.cookies)
            self._session.headers.update(self._base_headers())

        elif transport == "httpx":
            if not _HTTPX_OK:
                raise RuntimeError("httpx no instalado. Ejecuta: pip install httpx[http2]")
            self._session = httpx.Client(http2=True, timeout=30.0)
            self._session.headers.update(self._base_headers())
            for name, value in self.cookies.items():
                if value:
                    self._session.cookies.set(name, value)

        # transport="curl" no necesita sesión persistente

    # =========================================================================
    # HEADERS BASE
    # =========================================================================

    def _base_headers(self, referer: str = None) -> dict:
        return {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://www.nike.cl",
            "Referer": referer or "https://www.nike.cl/checkout/",
            "Accept-Language": "es-CL,es;q=0.9",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest",
        }

    def _cookie_header(self) -> str:
        return "; ".join(f"{k}={v}" for k, v in self.cookies.items() if v)

    # =========================================================================
    # DISPATCHER — elige el transport correcto
    # =========================================================================

    def _request(self, method: str, url: str, data: dict = None, referer: str = None) -> dict:
        if self.transport == "curl":
            return self._curl(method, url, data, referer)
        elif self.transport == "tls":
            return self._tls_request(method, url, data, referer)
        elif self.transport == "httpx":
            return self._httpx_request(method, url, data, referer)
        else:
            raise ValueError(f"Transport desconocido: {self.transport}")

    # =========================================================================
    # TRANSPORT: CURL (máxima evasión WAF)
    # =========================================================================

    def _curl(self, method: str, url: str, data: dict = None, referer: str = None) -> dict:
        cmd = [
            "curl", "-s", "-L", "-X", method, url,
            "-H", "Accept: application/json",
            "-H", "Content-Type: application/json",
            "-H", f"User-Agent: {self.user_agent}",
            "-H", "Accept-Language: es-CL,es;q=0.9",
            "-H", f"Referer: {referer or 'https://www.nike.cl/checkout/'}",
            "-H", "Origin: https://www.nike.cl",
            "-H", f"Cookie: {self._cookie_header()}",
            "--compressed",
        ]
        if data:
            cmd.extend(["-d", json.dumps(data)])

        try:
            result = subprocess.run(
                cmd, capture_output=True,
                encoding="utf-8", errors="replace", timeout=30
            )
            if result.returncode != 0:
                raise RuntimeError(f"curl error: {result.stderr}")
            text = result.stdout.strip()
            if not text:
                raise RuntimeError("Respuesta vacía (posible WAF block)")
            return json.loads(text)
        except subprocess.TimeoutExpired:
            raise RuntimeError("curl timeout")
        except json.JSONDecodeError:
            preview = result.stdout[:120] if "result" in dir() else "empty"
            raise RuntimeError(f"JSON inválido: {preview}")

    # =========================================================================
    # TRANSPORT: TLS-CLIENT (TLS fingerprinting anti-Cloudflare)
    # =========================================================================

    def _tls_request(self, method: str, url: str, data: dict = None, referer: str = None) -> dict:
        headers = {"Referer": referer or "https://www.nike.cl/checkout/"}
        try:
            if method.upper() == "GET":
                res = self._session.get(url, headers=headers, timeout_seconds=15)
            else:
                res = self._session.post(url, json=data or {}, headers=headers, timeout_seconds=15)

            if not res.text:
                return {"error": "WAF Block (Empty)"}
            return res.json()
        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # TRANSPORT: HTTPX (HTTP/2, más rápido para tests)
    # =========================================================================

    def _httpx_request(self, method: str, url: str, data: dict = None, referer: str = None) -> dict:
        headers = {"Referer": referer or "https://www.nike.cl/checkout/"}
        try:
            if method.upper() == "GET":
                res = self._session.get(url, headers=headers)
            else:
                res = self._session.post(url, json=data or {}, headers=headers)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # API PÚBLICA — mismos métodos para los 3 transports
    # =========================================================================

    def get_order_form(self) -> dict:
        url = f"{self.base_url}/api/checkout/pub/orderForm"
        if self.order_form_id:
            url += f"?orderFormId={self.order_form_id}"
        return self._request("GET", url)

    def create_order_form(self) -> dict:
        url = f"{self.base_url}/api/checkout/pub/orderForm"
        result = self._request("POST", url, data={})
        if isinstance(result, dict) and "id" in result:
            self.order_form_id = result["id"]
        return result

    def warmup_orderform(self) -> dict:
        result = self.get_order_form()
        if isinstance(result, dict) and "id" in result:
            self.order_form_id = result["id"]
        return result

    def add_to_cart(
        self, sku_id: str, seller: str,
        quantity: int = 1, order_form_id: str = None,
        referer_url: str = None
    ) -> dict:
        effective_id = order_form_id or self.order_form_id
        if not effective_id:
            raise RuntimeError("orderFormId no inicializado — llama warmup_orderform() primero")

        url = f"{self.base_url}/api/checkout/pub/orderForm/items?orderFormId={effective_id}"
        payload = {
            "orderItems": [
                {"id": str(sku_id), "quantity": int(quantity), "seller": str(seller)}
            ]
        }
        return self._request("POST", url, data=payload, referer=referer_url)

    def frontend_add_to_cart(
        self, sku_id: str, quantity: int = 1,
        seller: str = "1", sales_channel: str = "1"
    ) -> bool:
        """Simula click humano en 'Comprar ahora' — crea orderForm automáticamente."""
        url = (
            f"{self.base_url}/checkout/cart/add"
            f"?sku={sku_id}&qty={quantity}&seller={seller}&sc={sales_channel}"
        )
        try:
            if self.transport == "tls":
                res = self._session.get(url, allow_redirects=True, timeout_seconds=20)
                return "/checkout/" in res.url or res.status_code == 200
            elif self.transport == "httpx":
                res = self._session.get(url, follow_redirects=True)
                return "/checkout/" in str(res.url) or res.status_code == 200
            else:
                # curl con follow redirects
                cmd = [
                    "curl", "-s", "-L", "-o", "/dev/null", "-w", "%{url_effective}",
                    "-H", f"Cookie: {self._cookie_header()}",
                    "-H", f"User-Agent: {self.user_agent}",
                    url
                ]
                result = subprocess.run(cmd, capture_output=True, encoding="utf-8", timeout=20)
                return "/checkout/" in result.stdout
        except Exception as e:
            self.log.error(f"frontend_add_to_cart error: {e}")
            return False

    def simulation(
        self, sku_id: str, seller: str,
        quantity: int = 1, order_form_id: str = None,
        postal_code: str = "8320000", referer_url: str = None
    ) -> bool:
        effective_id = order_form_id or self.order_form_id
        url = f"{self.base_url}/api/checkout/pub/orderForm/{effective_id}/simulation"
        payload = {
            "items": [{"id": str(sku_id), "quantity": int(quantity), "seller": str(seller)}],
            "postalCode": postal_code,
            "country": "CHL",
        }
        try:
            result = self._request("POST", url, data=payload, referer=referer_url)
            if isinstance(result, dict):
                if "logisticsInfo" in result or "ratesAndBenefitsData" in result:
                    return True
                if "error" in result:
                    return False
            return False
        except RuntimeError as e:
            # WAF block → fail open para no abortar el flujo
            if "vacía" in str(e) or "Empty" in str(e):
                return True
            return False

    def clear_cart(self) -> dict:
        url = f"{self.base_url}/api/checkout/pub/orderForm/items/removeAll"
        return self._request("POST", url, data={})

    def warm_up_shipping(self, order_form_id: str = None) -> bool:
        effective_id = order_form_id or self.order_form_id
        url = f"{self.base_url}/api/checkout/pub/orderForm/{effective_id}/attachments/shippingData"
        try:
            self._request("POST", url, data={"address": None, "logisticsInfo": []})
            return True
        except Exception:
            return False

    def warm_up_commercial_context(self, order_form_id: str = None) -> bool:
        effective_id = order_form_id or self.order_form_id
        url = f"{self.base_url}/api/checkout/pub/orderForm/{effective_id}"
        try:
            result = self._request("POST", url, data={"salesChannel": 1})
            return isinstance(result, dict)
        except Exception:
            return False

    def pdp_context_warmup(self, sku: str) -> bool:
        url = f"{self.base_url}/api/catalog_system/pub/products/variations/{sku}"
        try:
            result = self._request("GET", url)
            return isinstance(result, dict) and any(k in result for k in ("id", "skuId", "productId"))
        except Exception:
            return False

    def get_pdp_url_from_sku(self, sku_id: str) -> Optional[str]:
        url = f"{self.base_url}/api/catalog_system/pub/products/search?fq=skuId:{sku_id}"
        try:
            result = self._request("GET", url)
            if result and isinstance(result, list) and len(result) > 0:
                link = result[0].get("link")
                if link:
                    return link
        except Exception as e:
            self.log.warning(f"get_pdp_url_from_sku error: {e}")
        return None

    # Alias de compatibilidad
    def get_pdp_url(self, sku_id: str) -> Optional[str]:
        return self.get_pdp_url_from_sku(sku_id)

    def extract_price(self, order_form: dict) -> float:
        try:
            for t in order_form.get("totalizers", []):
                if t.get("id") == "Items":
                    return t.get("value", 0) / 100
        except Exception as e:
            self.log.error(f"extract_price error: {e}")
        return 0

    def place_order_api(self, total_value_cents: int) -> dict:
        endpoint = f"/api/checkout/pub/orderForm/{self.order_form_id}/transaction"
        payload = {
            "referenceId": self.order_form_id,
            "value": int(total_value_cents),
            "interestValue": 0,
            "savePersonalData": False,
            "optinNewsLetter": False,
        }
        try:
            return self._request("POST", f"{self.base_url}{endpoint}", data=payload)
        except Exception as e:
            self.log.error(f"place_order_api error: {e}")
            return {}
