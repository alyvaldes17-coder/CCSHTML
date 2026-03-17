# vtex/orderform_validator.py
"""
Validador determinista para OrderForm.
Define cuándo el backend está realmente listo para payment.
"""
import logging
import asyncio
from typing import Dict, Any, Optional


class OrderFormValidator:
    """
    Valida que OrderForm esté en estado listo para payment.
    Implementa FREEZE WINDOW para evitar $0 y pagos incompletos.
    """

    def __init__(self, log_level: str = "INFO"):
        self.log = logging.getLogger("OrderFormValidator")
        self.log.setLevel(log_level.upper())
        self.last_stable_snapshot = None
        self.freeze_timestamp = None

    def is_basic_ready(self, order_form: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validación básica: campos mínimos presentes.
        Retorna (bool, razón_si_falla)
        """
        # Campos obligatorios
        if not order_form.get("orderFormId"):
            return False, "orderFormId vacío"

        items = order_form.get("items", [])
        if not items:
            return False, "carrito vacío"

        # Todos los items deben tener precio > 0
        for i, item in enumerate(items):
            if not isinstance(item.get("price"), (int, float)) or item["price"] <= 0:
                return False, f"item[{i}] sin precio válido (${item.get('price', 0)})"

        # Total debe ser > 0
        totalizers = order_form.get("totalizers", [])
        if not totalizers:
            return False, "sin totalizers"

        total_value = sum(t.get("value", 0) for t in totalizers)
        if total_value <= 0:
            return False, f"total = ${total_value} (inválido)"

        # Shipping debe estar confirmado
        shipping_data = order_form.get("shippingData", {})
        if not shipping_data.get("address"):
            return False, "dirección de envío no confirmada"

        logistics_info = shipping_data.get("logisticsInfo", [])
        if not logistics_info or not logistics_info[0].get("selectedSla"):
            return False, "SLA de envío no seleccionado"

        # Payment debe estar definido
        payment_data = order_form.get("paymentData", {})
        if not payment_data.get("paymentSystems"):
            return False, "sin payment systems disponibles"

        return True, "OK"

    def is_pricing_stable(
        self,
        current_snapshot: Dict[str, Any],
        previous_snapshot: Optional[Dict[str, Any]] = None,
        stability_window_ms: int = 400
    ) -> tuple[bool, str]:
        """
        Verifica que pricing no haya cambiado en el último intervalo.
        Esto evita el $0 y payment incompletos.
        
        Args:
            current_snapshot: OrderForm actual
            previous_snapshot: OrderForm anterior (si None, solo se guarda el actual)
            stability_window_ms: milisegundos esperados entre checks
        
        Retorna: (is_stable, razón)
        """
        if previous_snapshot is None:
            # Primera captura, guardar y esperar siguiente
            self.last_stable_snapshot = current_snapshot
            return False, "primera captura, esperando siguiente"

        # Comparar totalizers
        current_total = sum(
            t.get("value", 0) for t in current_snapshot.get("totalizers", [])
        )
        prev_total = sum(
            t.get("value", 0) for t in previous_snapshot.get("totalizers", [])
        )

        if current_total != prev_total:
            return False, f"total cambió: ${prev_total} → ${current_total}"

        # Comparar items[].price
        current_items = current_snapshot.get("items", [])
        prev_items = previous_snapshot.get("items", [])

        if len(current_items) != len(prev_items):
            return False, f"items cantidad cambió: {len(prev_items)} → {len(current_items)}"

        for i, (curr, prev) in enumerate(zip(current_items, prev_items)):
            if curr.get("price") != prev.get("price"):
                return False, f"item[{i}].price cambió: ${prev.get('price')} → ${curr.get('price')}"

        # Comparar SLA (si cambió el shipping)
        curr_sla = current_snapshot.get("shippingData", {}).get("logisticsInfo", [{}])[0].get("selectedSla")
        prev_sla = previous_snapshot.get("shippingData", {}).get("logisticsInfo", [{}])[0].get("selectedSla")

        if curr_sla != prev_sla:
            return False, f"SLA cambió: {prev_sla} → {curr_sla}"

        return True, f"estable durante {stability_window_ms}ms"

    async def wait_for_frozen_price(
        self,
        get_orderform_fn,
        timeout_sec: int = 30,
        stability_window_ms: int = 400,
        check_interval_ms: int = 200
    ) -> tuple[bool, Dict[str, Any], str]:
        """
        Espera a que el precio se estabilice (FREEZE WINDOW).
        
        Args:
            get_orderform_fn: función async que retorna OrderForm
            timeout_sec: máximo tiempo a esperar
            stability_window_ms: intervalo sin cambios que indica estabilidad
            check_interval_ms: cada cuánto millisegundos chequear
        
        Retorna: (success, frozen_orderform, razón)
        """
        import time

        start = time.time()
        last_snapshot = None
        stable_count = 0
        stable_threshold = stability_window_ms // check_interval_ms

        self.log.info(
            f"⏳ Esperando precio congelado (timeout={timeout_sec}s, "
            f"stability_window={stability_window_ms}ms)"
        )

        while time.time() - start < timeout_sec:
            try:
                current = await get_orderform_fn()

                # 1. Validar básico
                is_ok, reason = self.is_basic_ready(current)
                if not is_ok:
                    self.log.debug(f"   ❌ {reason}, reintentando...")
                    last_snapshot = None
                    stable_count = 0
                    await asyncio.sleep(check_interval_ms / 1000.0)
                    continue

                # 2. Validar estabilidad
                is_stable, reason = self.is_pricing_stable(current, last_snapshot)
                if is_stable:
                    stable_count += 1
                    self.log.debug(
                        f"   ✅ {reason} [{stable_count}/{stable_threshold}]"
                    )

                    if stable_count >= stable_threshold:
                        elapsed = time.time() - start
                        self.log.info(
                            f"🔒 Precio CONGELADO en {elapsed:.1f}s"
                        )
                        self.freeze_timestamp = time.time()
                        return True, current, "OK"
                else:
                    self.log.debug(f"   🔄 {reason}, reset contador")
                    stable_count = 0

                last_snapshot = current
                await asyncio.sleep(check_interval_ms / 1000.0)

            except Exception as e:
                self.log.warning(f"   ⚠️ Error al obtener orderForm: {e}")
                stable_count = 0
                last_snapshot = None
                await asyncio.sleep(check_interval_ms / 1000.0)

        elapsed = time.time() - start
        return False, None, f"timeout ({elapsed:.1f}s, sin estabilidad)"

    def get_total_price(self, order_form: Dict[str, Any]) -> int:
        """Retorna el total en centavos (ej: 12299000 = $122.990)"""
        return sum(t.get("value", 0) for t in order_form.get("totalizers", []))

    def get_currency_display(self, total_cents: int, currency: str = "CLP") -> str:
        """Formato para display: $122.990"""
        if currency == "CLP":
            return f"${total_cents // 100:,}".replace(",", ".")
        return f"{total_cents / 100:,.2f}"
