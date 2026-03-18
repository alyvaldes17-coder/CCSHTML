"""
stock_monitor.py — Monitor centralizado de stock VTEX

UN solo worker hace polling del catálogo público de Nike.cl.
Cuando detecta stock, dispara callback (para lanzar los 11 Chromes simultáneo).

Ventajas vs. modo_monitor en engine.py:
  - 1 request global vs 11 requests por cuenta → menos tráfico, menos bans
  - Detección ~50ms vs ~150ms por cuenta
  - No necesita sesión/cookies → API pública
  - Puede monitorear múltiples SKUs a la vez
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Callable, Dict, List, Optional

import httpx

CATALOG_URL = "https://www.nike.cl/api/catalog_system/pub/products/search"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "es-CL,es;q=0.9",
}

# Intervalos en segundos
DEFAULT_INTERVAL = 0.5       # 500ms — agresivo pero no baneado
BACKOFF_INTERVAL = 5.0       # Si Nike devuelve 429/5xx
MAX_CONSECUTIVE_ERRORS = 10  # Parar si Nike nos bloquea


class StockEvent:
    """Evento emitido cuando se detecta stock."""

    __slots__ = ("sku", "name", "quantity", "price", "timestamp")

    def __init__(self, sku: str, name: str, quantity: int, price: float):
        self.sku = sku
        self.name = name
        self.quantity = quantity
        self.price = price
        self.timestamp = datetime.now().strftime("%H:%M:%S")

    def to_dict(self) -> dict:
        return {
            "sku": self.sku,
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price,
            "timestamp": self.timestamp,
        }


class StockMonitor:
    """
    Monitor asíncrono de stock VTEX.

    Uso:
        monitor = StockMonitor(on_stock=my_callback, on_log=my_log)
        monitor.add_sku("134427")
        await monitor.start()   # corre hasta .stop()
    """

    def __init__(
        self,
        on_stock: Optional[Callable[[StockEvent], None]] = None,
        on_log: Optional[Callable[[str], None]] = None,
        interval: float = DEFAULT_INTERVAL,
    ):
        self.on_stock = on_stock
        self.on_log = on_log
        self.interval = interval
        self.skus: List[str] = []
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._consecutive_errors = 0
        self._checks = 0
        self._stock_found: Dict[str, float] = {}  # sku → timestamp última detección

    # ── SKU management ──

    def add_sku(self, sku: str):
        sku = str(sku).strip()
        if sku and sku not in self.skus:
            self.skus.append(sku)
            self._log(f"[Monitor] ➕ SKU {sku} agregado — total: {len(self.skus)}")

    def remove_sku(self, sku: str):
        sku = str(sku).strip()
        if sku in self.skus:
            self.skus.remove(sku)
            self._log(f"[Monitor] ➖ SKU {sku} removido — total: {len(self.skus)}")

    def set_skus(self, skus: List[str]):
        self.skus = [str(s).strip() for s in skus if str(s).strip()]
        self._log(f"[Monitor] 📋 SKUs configurados: {self.skus}")

    # ── Control ──

    async def start(self):
        """Inicia el polling loop."""
        if self._running:
            self._log("[Monitor] Ya está corriendo")
            return
        if not self.skus:
            self._log("[Monitor] ⚠️ Sin SKUs configurados")
            return

        self._running = True
        self._consecutive_errors = 0
        self._checks = 0
        self._log(f"[Monitor] 🟢 Iniciado — SKUs: {self.skus} — intervalo: {self.interval}s")
        self._task = asyncio.create_task(self._poll_loop())

    def stop(self):
        """Detiene el polling."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
        self._log("[Monitor] 🔴 Detenido")

    @property
    def running(self) -> bool:
        return self._running

    @property
    def stats(self) -> dict:
        return {
            "running": self._running,
            "skus": self.skus,
            "checks": self._checks,
            "errors": self._consecutive_errors,
            "interval": self.interval,
        }

    # ── Polling loop ──

    async def _poll_loop(self):
        async with httpx.AsyncClient(headers=HEADERS, timeout=8.0, http2=False) as client:
            while self._running:
                for sku in list(self.skus):
                    if not self._running:
                        break
                    await self._check_sku(client, sku)

                await asyncio.sleep(self.interval)

    async def _check_sku(self, client: httpx.AsyncClient, sku: str):
        self._checks += 1
        url = f"{CATALOG_URL}?fq=skuId:{sku}"

        try:
            resp = await client.get(url)

            if resp.status_code == 429:
                self._consecutive_errors += 1
                wait = min(BACKOFF_INTERVAL * self._consecutive_errors, 30)
                self._log(f"[Monitor] ⚠️ Rate limited (429) — backoff {wait:.0f}s")
                await asyncio.sleep(wait)
                return

            if resp.status_code >= 500:
                self._consecutive_errors += 1
                self._log(f"[Monitor] ⚠️ Nike error {resp.status_code}")
                await asyncio.sleep(BACKOFF_INTERVAL)
                return

            if resp.status_code != 200:
                self._consecutive_errors += 1
                return

            # Reset errores
            self._consecutive_errors = 0

            data = resp.json()
            if not data:
                if self._checks % 20 == 0:
                    self._log(f"[Monitor] SKU {sku} — sin data (#{self._checks})")
                return

            product = data[0]
            items = product.get("items", [])

            for item in items:
                if str(item.get("itemId")) != str(sku):
                    continue

                sellers = item.get("sellers", [])
                if not sellers:
                    continue

                offer = sellers[0].get("commertialOffer", {})
                qty = offer.get("AvailableQuantity", 0)
                available = offer.get("IsAvailable", False)
                price = offer.get("Price", 0)

                if available and qty > 0:
                    # Cooldown: no disparar si ya detectamos stock hace <30s
                    last = self._stock_found.get(sku, 0)
                    if time.time() - last < 30:
                        return

                    self._stock_found[sku] = time.time()
                    name = item.get("name", product.get("productName", sku))

                    evt = StockEvent(sku=sku, name=name, quantity=qty, price=price)
                    self._log(
                        f"[Monitor] 🔥 ¡STOCK DETECTADO! {name} — "
                        f"{qty} uds — ${price:,.0f} — check #{self._checks}"
                    )

                    if self.on_stock:
                        try:
                            self.on_stock(evt)
                        except Exception as e:
                            self._log(f"[Monitor] ❌ Error en callback: {e}")
                else:
                    if self._checks % 20 == 0:
                        self._log(f"[Monitor] 💤 SKU {sku} sin stock (#{self._checks})")

        except httpx.TimeoutException:
            self._consecutive_errors += 1
            if self._consecutive_errors % 3 == 0:
                self._log(f"[Monitor] ⏱️ Timeout #{self._consecutive_errors}")
        except Exception as e:
            self._consecutive_errors += 1
            if self._consecutive_errors % 5 == 0:
                self._log(f"[Monitor] ❌ Error: {e}")

        if self._consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
            self._log(f"[Monitor] 🛑 Demasiados errores ({self._consecutive_errors}) — detenido")
            self._running = False

    # ── Logging ──

    def _log(self, msg: str):
        if self.on_log:
            self.on_log(msg)
        else:
            print(msg)
