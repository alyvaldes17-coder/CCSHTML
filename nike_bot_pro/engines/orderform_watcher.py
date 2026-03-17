# engines/orderform_watcher.py
"""
OrderForm Watcher - Versión concreta.
Pragma: sin Over-Engineering.
Solo watch de pricing (PRICING_WAIT + PRICING_FROZEN).
"""
import time
import logging


class OrderFormWatcher:
    """Observa OrderForm para congelación de precio."""

    def __init__(self, session, log=None):
        """
        Args:
            session: requests.Session con cookies VTEX
            log: logger (opcional)
        """
        self.session = session
        self.log = log or logging.getLogger("OrderFormWatcher")

    def fetch(self) -> dict:
        """Obtiene OrderForm actual."""
        r = self.session.get("/api/checkout/pub/orderForm")
        r.raise_for_status()
        return r.json()

    def is_ready(self, of: dict) -> bool:
        """¿OrderForm está listo para congelar?"""
        try:
            # OrderFormId
            if not of.get("orderFormId"):
                self.log.debug("❌ sin orderFormId")
                return False

            # Items
            items = of.get("items", [])
            if not items:
                self.log.debug("❌ items vacío")
                return False

            # Price check
            for i, item in enumerate(items):
                price = item.get("price", 0)
                if price <= 0:
                    self.log.debug(f"❌ item[{i}] price <= 0")
                    return False

            # Total check
            totalizers = of.get("totalizers", [])
            total = sum(t.get("value", 0) for t in totalizers)
            if total <= 0:
                self.log.debug(f"❌ total <= 0")
                return False

            # Shipping check
            logistics = of.get("shippingData", {}).get("logisticsInfo", [])
            if not logistics or not logistics[0].get("selectedSla"):
                self.log.debug("❌ sin SLA seleccionado")
                return False

            # Payment systems
            if not of.get("paymentData", {}).get("paymentSystems"):
                self.log.debug("❌ sin payment systems")
                return False

            return True

        except Exception as e:
            self.log.debug(f"❌ error validando: {e}")
            return False

    def wait_until_ready(self, timeout=8) -> dict:
        """
        PRICING_WAIT → ready signal
        Espera a que OrderForm esté listo.
        
        ✅ MEJORA E4: Circuit breaker si VTEX no responde (500, 503)
        
        Bloquea si:
        - price == 0
        - total == 0
        - sin SLA
        
        Lanza:
        - TimeoutError si timeout
        - RuntimeError si VTEX está caído (circuit break)
        
        Retorna: OrderForm cuando is_ready() == True
        """
        start = time.time()
        attempt = 0
        consecutive_errors = 0

        while time.time() - start < timeout:
            attempt += 1
            try:
                # Fetch con validación de error
                r = self.session.get("/api/checkout/pub/orderForm")
                
                # CIRCUIT BREAKER: Si VTEX devuelve 5xx → fail fast
                if r.status_code >= 500:
                    self.log.error(f"❌ VTEX unavailable ({r.status_code})")
                    raise RuntimeError(f"VTEX circuit open: {r.status_code}")
                
                r.raise_for_status()
                of = r.json()
                consecutive_errors = 0  # Reset counter
                
                if self.is_ready(of):
                    elapsed = time.time() - start
                    self.log.info(f"✅ OrderForm ready en {elapsed:.1f}s (intento {attempt})")
                    return of

            except RuntimeError as e:
                # Circuit break: propagar error inmediatamente
                if "circuit open" in str(e).lower():
                    self.log.error(f"🔴 VTEX circuit break: {e}")
                    raise
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    self.log.error(f"❌ 3 errores consecutivos, abortando")
                    raise
            except Exception as e:
                consecutive_errors += 1
                self.log.debug(f"⚠️ Error fetch (intento {attempt}): {e}")
                if consecutive_errors >= 3:
                    raise RuntimeError(f"Demasiados errores: {e}")

            time.sleep(0.25)

        elapsed = time.time() - start
        raise TimeoutError(f"OrderForm no ready después {elapsed:.1f}s ({attempt} intentos)")

    def freeze(self, window_ms=400) -> dict:
        """
        PRICING_FROZEN → congelación confirmada
        Implementa freeze window.
        
        Captura 2 snapshots con intervalo.
        Si son iguales (pricing, SLA) → congelado.
        Si cambió → lanza RuntimeError.
        
        Args:
            window_ms: intervalo entre capturas (default 400ms)
        
        Retorna: OrderForm congelado
        Lanza: RuntimeError si no está estable
        """
        window = window_ms / 1000.0

        self.log.info(f"🔒 Capturando snapshot A...")
        snap1 = self.fetch()

        time.sleep(window)

        self.log.info(f"🔒 Capturando snapshot B (después {window_ms}ms)...")
        snap2 = self.fetch()

        # Comparar totalizers
        total1 = snap1.get("totalizers", [])
        total2 = snap2.get("totalizers", [])

        if total1 != total2:
            raise RuntimeError(f"Totalizers cambió: {total1} vs {total2}")

        # Comparar items prices
        items1 = snap1.get("items", [])
        items2 = snap2.get("items", [])

        for i, (item1, item2) in enumerate(zip(items1, items2)):
            if item1.get("price") != item2.get("price"):
                raise RuntimeError(
                    f"item[{i}].price cambió: {item1.get('price')} vs {item2.get('price')}"
                )

        # Comparar SLA
        sla1 = snap1.get("shippingData", {}).get("logisticsInfo", [{}])[0].get("selectedSla")
        sla2 = snap2.get("shippingData", {}).get("logisticsInfo", [{}])[0].get("selectedSla")

        if sla1 != sla2:
            raise RuntimeError(f"SLA cambió: {sla1} vs {sla2}")

        self.log.info(f"✅ Pricing congelado")
        return snap2

    def get_total(self, of: dict) -> int:
        """Retorna total en centavos (ej: 12299000 = $122.990)"""
        return sum(t.get("value", 0) for t in of.get("totalizers", []))

    def display_price(self, total_cents: int) -> str:
        """Formato para display: $122.990"""
        return f"${total_cents // 100:,}".replace(",", ".")
