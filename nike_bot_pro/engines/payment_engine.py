# engines/payment_engine.py
"""
Payment Engine - Versión concreta.
Pragma: sin Over-Engineering.
Solo inyecta payment bancario en orderForm.
"""
import logging


class PaymentEngine:
    """Inyecta payment method bancario en orderForm."""

    def __init__(self, session, log=None):
        """
        Args:
            session: requests.Session con cookies VTEX
            log: logger (opcional)
        """
        self.session = session
        self.log = log or logging.getLogger("PaymentEngine")

    def set_bank_payment(self, order_form_id: str) -> dict:
        """
        Inyecta payment method bancario.
        
        PAYMENT_BANK_SELECTED:
        - Backend call (sin UI)
        - Inyecta paymentSystem = "bankInvoice" (AJUSTA según Nike CL)
        - VTEX retorna orderForm actualizado
        
        Args:
            order_form_id: orderFormId desde OrderForm
        
        Retorna: OrderForm actualizado
        Lanza: Exception si falla
        """
        self.log.info(f"🏦 Inyectando payment: bankInvoice")

        payload = {
            "payments": [
                {
                    "paymentSystem": "bankInvoice",  # 📌 AJUSTA según Nike CL
                    "value": None,
                    "installments": 1
                }
            ]
        }

        url = f"/api/checkout/pub/orderForm/{order_form_id}/attachments/paymentData"
        
        try:
            r = self.session.post(url, json=payload)
            r.raise_for_status()
            of = r.json()
            self.log.info(f"✅ Payment inyectado")
            return of
        except Exception as e:
            self.log.error(f"❌ Error inyectando: {e}")
            raise

