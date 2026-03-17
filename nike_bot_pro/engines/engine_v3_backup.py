#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engines/engine.py — NikeBotEngine v3.0 (Handshake + Event-Driven)

CAMBIO PRINCIPAL vs v2.x:
- Python NO declara exito hasta que el JS confirma via console.log que
  clickeo Finalizar compra. Fin de los falsos positivos.
- Cada evento tiene su propio timeout y telemetria.
- _limpiar_carrito: navega a nike.cl antes del fetch (fix Failed to fetch)
"""

import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

import websocket


class NikeBotEngine:

    def __init__(self, port: int = 9223, account_name: str = "default"):
        self.port = port
        self.account_name = account_name
        self.chrome_exe = self._find_chrome()
        self.profile_path = self._get_profile_path(account_name)

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _find_chrome(self) -> str:
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        raise FileNotFoundError("Chrome no encontrado.")

    def _get_profile_path(self, account_name: str) -> str:
        if os.path.isabs(account_name) and os.path.exists(account_name):
            return account_name
        auth_path = os.path.join("auth", account_name, "profile_login")
        if os.path.exists(auth_path):
            return auth_path
        base = Path.home() / "AppData" / "Local" / "Chromium" / "User Data" / account_name
        base.mkdir(parents=True, exist_ok=True)
        return str(base)

    def _get_chrome_flags(self) -> list:
        return [
            f"--remote-debugging-port={self.port}",
            "--remote-allow-origins=*",
            "--disable-blink-features=AutomationControlled",
            "--exclude-switches=enable-automation",
            "--disable-dev-shm-usage",
            "--metrics-recording-only",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-popup-blocking",
            "--disable-hang-monitor",
            "--disable-background-networking",
            "--disable-default-apps",
            "--disable-extensions",
            "--disable-sync",
        ]

    def _get_tab_url(self) -> str | None:
        for _ in range(5):
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{self.port}/json", timeout=2
                ) as r:
                    tabs = json.loads(r.read())
                for tab in tabs:
                    if tab.get("type") == "page" and "webSocketDebuggerUrl" in tab:
                        return tab["webSocketDebuggerUrl"]
            except Exception:
                pass
            time.sleep(0.6)
        return None

    def _conectar_cdp(self) -> websocket.WebSocket | None:
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{self.port}/json", timeout=3
            ) as r:
                tabs = json.loads(r.read())
            tab = next((t for t in tabs if t.get("webSocketDebuggerUrl")), None)
            if not tab:
                return None
            return websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=5)
        except Exception as e:
            print(f"[Engine] Error CDP: {e}")
            return None

    def _esperar_evento_cdp(
        self,
        ws: websocket.WebSocket,
        metodo: str,
        substring: str = "",
        timeout: float = 5.0,
    ) -> bool:
        """
        Radar CDP: escucha mensajes del WebSocket hasta encontrar
        el evento/metodo buscado. No bloquea con sleep — poll rapido.

        Metodos soportados:
          "Network.responseReceived" + substring de URL
          "Page.loadEventFired"
          "Page.frameStoppedLoading"
          "Runtime.consoleAPICalled" + substring del mensaje
        """
        inicio = time.time()
        while time.time() - inicio < timeout:
            try:
                ws.settimeout(0.15)
                raw = ws.recv()
                if not raw:
                    continue
                msg = json.loads(raw)
                actual = msg.get("method", "")

                if actual != metodo:
                    continue

                if metodo == "Network.responseReceived":
                    url = msg.get("params", {}).get("response", {}).get("url", "")
                    if substring in url:
                        return True

                elif metodo in ("Page.loadEventFired", "Page.frameStoppedLoading"):
                    return True

                elif metodo == "Runtime.consoleAPICalled":
                    args = msg.get("params", {}).get("args", [])
                    texto = args[0].get("value", "") if args else ""
                    if substring in texto:
                        return True

            except websocket.WebSocketTimeoutException:
                continue
            except Exception:
                break

        return False

    # =========================================================================
    # BACKEND
    # =========================================================================

    def ataque_backend_os(self, skus: list = None) -> bool:
        if not skus:
            return False
        flags = self._get_chrome_flags()
        flags.append(f"--user-data-dir={self.profile_path}")
        for idx, sku in enumerate(skus):
            url = f"https://www.nike.cl/checkout/cart/add?sku={sku}&qty=1&seller=1&sc=1"
            try:
                subprocess.Popen(
                    [self.chrome_exe] + flags + [url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                print(f"[Backend-OS] SKU {sku} ({idx+1}/{len(skus)})")
            except Exception as e:
                print(f"[Backend-OS] Error: {e}")
                return False
            if idx < len(skus) - 1:
                time.sleep(0.4)
        return True

    def ataque_backend_cdp(self, skus: list = None) -> bool:
        """
        EVENTO 1: Agregar SKUs al carrito via CDP.
        Espera confirmacion real de VTEX via Network.responseReceived.
        Retorna False si VTEX no confirma en 6s — no sigue a ciegas.
        """
        if not skus:
            return False

        print(f"[EV1] Agregando {len(skus)} SKU(s) al carrito...")
        t0 = time.time()

        ws_url = self._get_tab_url()
        if not ws_url:
            print("[EV1] Sin CDP, fallback a OS...")
            return self.ataque_backend_os(skus=skus)

        try:
            ws = websocket.create_connection(ws_url, timeout=5)

            # Activar radares
            ws.send(json.dumps({"id": 0, "method": "Network.enable", "params": {}}))
            ws.send(json.dumps({"id": 0, "method": "Page.enable",    "params": {}}))
            ws.send(json.dumps({"id": 0, "method": "Runtime.enable", "params": {}}))

            # Resource blocker
            ws.send(json.dumps({
                "id": 0,
                "method": "Network.setBlockedURLs",
                "params": {
                    "urls": [
                        "*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.webp",
                        "*.woff", "*.woff2", "*.ttf", "*.otf",
                        "*google-analytics*", "*doubleclick*",
                        "*hotjar*", "*newrelic*", "*facebook*",
                        "*demdex*", "*omtrdc*",
                    ]
                }
            }))

            for idx, sku in enumerate(skus):
                url = f"https://www.nike.cl/checkout/cart/add?sku={sku}&qty=1&seller=1&sc=1"
                ws.send(json.dumps({
                    "id": idx + 1,
                    "method": "Page.navigate",
                    "params": {"url": url}
                }))
                print(f"  [{idx+1}/{len(skus)}] SKU {sku}")
                if idx < len(skus) - 1:
                    # Esperar que la navegacion del SKU anterior termine
                    self._esperar_evento_cdp(ws, "Page.frameStoppedLoading", timeout=3.0)
                    time.sleep(0.1)

            # Esperar confirmacion VTEX via Network (orderForm actualizado)
            confirmado = self._esperar_evento_cdp(
                ws, "Network.responseReceived", "orderForm", timeout=6.0
            )

            ms = int((time.time() - t0) * 1000)

            if confirmado:
                print(f"[EV1] Carrito confirmado por VTEX en {ms}ms")
                ws.close()
                return True
            else:
                print(f"[EV1] VTEX no confirmo en 6s ({ms}ms). Abortando.")
                ws.close()
                return False

        except Exception as e:
            print(f"[EV1] Error: {e}")
            return self.ataque_backend_os(skus=skus)

    # =========================================================================
    # FRONTEND — con handshake real
    # =========================================================================

    def ataque_frontend(
        self,
        payment_mode: str = "transfer",
        card_data: dict = None,
        skip_cart_verify: bool = False,
    ) -> bool:
        """
        EVENTOS 2, 3 y 4:
          EV2: Navegar a /#/profile y esperar DOM (Page.frameStoppedLoading)
          EV3: Inyectar JS de pago
          EV4: Esperar senal handshake del JS antes de declarar exito

        Python NO cierra el WebSocket hasta que el JS confirme el click.
        """
        print("[Frontend] Iniciando checkout event-driven...")
        if card_data is None:
            card_data = {}

        ws_url = self._get_tab_url()
        if not ws_url:
            print("[Frontend] Sin conexion CDP.")
            return False

        telemetria = {}

        try:
            ws = websocket.create_connection(ws_url, timeout=5)

            # Activar radares (pueden ya estar activos, no hay problema)
            ws.send(json.dumps({"id": 0, "method": "Network.enable", "params": {}}))
            ws.send(json.dumps({"id": 0, "method": "Page.enable",    "params": {}}))
            ws.send(json.dumps({"id": 0, "method": "Runtime.enable", "params": {}}))

            # ── EVENTO 2: Navegar a /#/profile ──
            t0 = time.time()
            print("[EV2] Navegando a /#/profile...")
            ws.send(json.dumps({
                "id": 2,
                "method": "Page.navigate",
                "params": {"url": "https://www.nike.cl/checkout/#/profile"}
            }))

            dom_ok = self._esperar_evento_cdp(
                ws, "Page.frameStoppedLoading", timeout=6.0
            )
            telemetria["nav_ms"] = int((time.time() - t0) * 1000)

            if dom_ok:
                print(f"[EV2] DOM listo en {telemetria['nav_ms']}ms")
                time.sleep(0.8)  # React hidration
            else:
                print(f"[EV2] DOM no confirmo ({telemetria['nav_ms']}ms), esperando 2s extra...")
                time.sleep(2.0)

            # ── EVENTO 3: Inyectar JS ──
            t0 = time.time()
            print(f"[EV3] Inyectando JS '{payment_mode}'...")

            if payment_mode in ("credit_card", "debit"):
                from engines.card_payment_js import build_card_js
                js = build_card_js(
                    card_data,
                    card_type="debit" if payment_mode == "debit" else "credit"
                )
                senal = "CARD_CLICK_OK"
            else:
                js = self._build_payment_js(payment_mode)
                senal = "FINALIZAR_CLICK_OK"

            ws.send(json.dumps({
                "id": 3,
                "method": "Runtime.evaluate",
                "params": {"expression": js}
            }))

            # ── EVENTO 4: Handshake — esperar senal del JS ──
            print(f"[EV4] Esperando confirmacion del JS (senal: '{senal}')...")
            click_ok = self._esperar_evento_cdp(
                ws, "Runtime.consoleAPICalled", senal, timeout=25.0
            )

            telemetria["js_ms"] = int((time.time() - t0) * 1000)

            if click_ok:
                print(f"[EV4] HANDSHAKE OK — Click confirmado en {telemetria['js_ms']}ms")
                print(f"[Frontend] Telemetria: {telemetria}")
                ws.close()
                return True
            else:
                print(f"[EV4] JS no confirmo click en 25s ({telemetria['js_ms']}ms)")
                print("[EV4] Revisa F12 -> Console para ver que labels/botones encontro el JS.")
                ws.close()
                return False

        except Exception as e:
            print(f"[Frontend] Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    # =========================================================================
    # JS DE PAGO — emite senal handshake al clickear
    # =========================================================================

    def _build_payment_js(self, payment_mode: str) -> str:
        """
        Loop 200ms hasta 30s.
        Al clickear Finalizar emite console.log('FINALIZAR_CLICK_OK')
        que Python intercepta via Runtime.consoleAPICalled.
        """
        payment_labels = {
            "transfer":    "Transferencia con tu banco",
            "mercadopago": "Mercado Pago",
            "etpay":       "Transferencia automática",
        }
        label_text = payment_labels.get(payment_mode, "Transferencia con tu banco")

        return f"""
        (() => {{
            console.log('[BOT] Iniciado: {payment_mode}');

            const MAX_MS   = 30000;
            const inicio   = Date.now();
            let metodo_sel = false;
            let click_hecho = false;

            const iv = setInterval(() => {{
                if (click_hecho) {{ clearInterval(iv); return; }}
                if (Date.now() - inicio > MAX_MS) {{
                    console.log('[BOT] Timeout 30s.');
                    clearInterval(iv);
                    return;
                }}

                // Matar modales
                const btnModal = [...document.querySelectorAll('a, button, span')]
                    .find(e => e.innerText?.includes('Continuar compra'));
                if (btnModal) {{ btnModal.click(); return; }}

                // PASO 1: Seleccionar metodo
                if (!metodo_sel) {{
                    const labels = [...document.querySelectorAll('label')];
                    const lbl = labels.find(l => l.innerText?.includes('{label_text}'));

                    if (lbl) {{
                        const radio = document.getElementById(lbl.getAttribute('for'));
                        if (radio) {{
                            if (!radio.checked) {{
                                radio.checked = true;
                                radio.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                radio.dispatchEvent(new Event('click',  {{ bubbles: true }}));
                                console.log('[BOT] Metodo seleccionado: {label_text}');
                            }}
                            metodo_sel = true;
                        }}
                    }} else {{
                        // Debug: mostrar labels disponibles
                        const textos = [...document.querySelectorAll('label')]
                            .map(l => l.innerText?.trim()).filter(t => t && t.length > 2);
                        if (textos.length)
                            console.log('[BOT] Labels: ' + textos.join(' | '));
                    }}
                    return;
                }}

                // PASO 2: Click Finalizar
                const btn =
                    document.getElementById('payment-data-submit') ||
                    document.querySelector('[data-testid="place-order-button"]') ||
                    document.querySelector('.payment-submit-wrap button') ||
                    [...document.querySelectorAll('button')].find(b =>
                        b.textContent?.trim().toLowerCase().includes('finalizar')
                    );

                if (btn) {{
                    if (btn.disabled) {{
                        console.log('[BOT] Boton disabled, esperando...');
                        return;
                    }}
                    console.log('[BOT] Clickeando: ' + btn.textContent.trim());
                    btn.scrollIntoView({{ behavior: 'auto' }});
                    btn.click();
                    click_hecho = true;

                    // SENAL HANDSHAKE — Python la intercepta via Runtime.consoleAPICalled
                    console.log('FINALIZAR_CLICK_OK');

                    clearInterval(iv);
                }} else {{
                    const btns = [...document.querySelectorAll('button')]
                        .map(b => b.textContent?.trim()).filter(Boolean);
                    if (btns.length)
                        console.log('[BOT] Botones: ' + btns.join(' | '));
                }}

            }}, 200);
        }})();
        """

    # =========================================================================
    # LIMPIAR CARRITO
    # =========================================================================

    def _limpiar_carrito(self) -> bool:
        """
        Limpia carrito via API VTEX real.
        Navega a nike.cl primero para que el fetch no falle con
        'Failed to fetch' cuando Chrome esta en about:blank.
        """
        print(f"[Engine] Limpiando carrito (puerto {self.port})...")

        ws = self._conectar_cdp()
        if not ws:
            print("[Engine] Sin conexion CDP.")
            return False

        try:
            # Primero navegar a nike.cl para contexto correcto del fetch
            ws.send(json.dumps({"id": 0, "method": "Page.enable", "params": {}}))
            ws.send(json.dumps({
                "id": 97,
                "method": "Page.navigate",
                "params": {"url": "https://www.nike.cl"}
            }))
            self._esperar_evento_cdp(ws, "Page.frameStoppedLoading", timeout=5.0)
            time.sleep(0.5)

            js = """
            (() => {
                return new Promise((resolve) => {
                    fetch('/api/checkout/pub/orderForm', {
                        credentials: 'include',
                        headers: { 'Accept': 'application/json' }
                    })
                    .then(r => r.json())
                    .then(data => {
                        const id    = data.orderFormId;
                        const items = data.items || [];
                        if (items.length === 0) { resolve('EMPTY'); return; }
                        const orderItems = items.map((_, i) => ({ index: i, quantity: 0 }));
                        return fetch(
                            '/api/checkout/pub/orderForm/' + id + '/items/removeAll',
                            {
                                method: 'POST',
                                credentials: 'include',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ orderItems })
                            }
                        ).then(() => resolve('CLEARED'));
                    })
                    .catch(e => resolve('ERROR:' + e.message));
                });
            })();
            """

            ws.send(json.dumps({
                "id": 98,
                "method": "Runtime.evaluate",
                "params": {"expression": js, "awaitPromise": True, "timeout": 8000}
            }))

            resultado = "NO_RESPONSE"
            deadline = time.time() + 10
            while time.time() < deadline:
                try:
                    ws.settimeout(0.5)
                    msg = json.loads(ws.recv())
                    if msg.get("id") == 98:
                        resultado = (
                            msg.get("result", {})
                               .get("result", {})
                               .get("value", "NO_RESPONSE")
                        )
                        break
                except websocket.WebSocketTimeoutException:
                    continue
                except Exception:
                    break

            ws.close()
            print(f"[Engine] Carrito: {resultado}")
            return resultado in ("CLEARED", "EMPTY")

        except Exception as e:
            print(f"[Engine] Error: {e}")
            try:
                ws.close()
            except Exception:
                pass
            return False

    def cleanup(self):
        pass


# Aliases de compatibilidad
HybridAssassinUltra   = NikeBotEngine
HybridAssassinV6      = NikeBotEngine
HybridAssassin        = NikeBotEngine
HybridAssassinFusion  = NikeBotEngine
HybridAssassinStealth = NikeBotEngine
