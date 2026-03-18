#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engines/engine.py — NikeBotEngine v11.2

FIXES v11.2:
  - evento_handshake acepta payment_mode — fix TypeError
  - headless=new REMOVIDO — Nike lo detecta y bloquea checkout
  - Sedante VTEX METHOD_SELECTED: 2s → 0ms (continúa inmediato)
  - Loop EV4: 300ms → 50ms
  - Doble click con 100ms intervalo
  - stealth JS mejorado
"""

import json
import os
import subprocess
import threading
import time
import urllib.request
from pathlib import Path

import websocket


CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
]

CHROME_FLAGS = [
    # REMOVIDO: --headless=new — Nike lo detecta (Shape Security chequea WebGL/GPU/fonts)
    "--remote-allow-origins=*",
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
    "--disable-translate",
    "--disable-breakpad",
    "--disable-component-update",
    "--disable-renderer-backgrounding",
    "--no-crash-upload",
    "--safebrowsing-disable-auto-update",
    "--password-store=basic",
    "--use-mock-keychain",
    "--renderer-process-limit=1",
    "--js-flags=--max-old-space-size=128",
    "--disable-gpu",
    "--disable-gpu-compositing",
    "--disable-software-rasterizer",
    "--disable-canvas-aa",
    "--disable-2d-canvas-clip-aa",
    "--num-raster-threads=1",
    "--enable-low-end-device-mode",
    "--disable-backgrounding-occluded-windows",
    "--mute-audio",
]

URLS_BLOQUEADAS = [
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg",
    "*.webp", "*.ico", "*.bmp",
    "*.woff", "*.woff2", "*.ttf", "*.otf", "*.eot",
    "*.mp4", "*.webm",
    "*google-analytics*", "*googletagmanager*",
    "*doubleclick*", "*facebook.net*",
    "*hotjar*", "*newrelic*", "*nr-data*",
    "*segment.io*", "*mixpanel*", "*amplitude*",
    "*demdex*", "*omtrdc*", "*2o7.net*",
    "*nike.com/tracking*", "*s.pinimg*",
]

PAYMENT_LABELS = {
    "transfer":    "Transferencia con tu banco",
    "mercadopago": "Mercado Pago",
    "etpay":       "Transferencia automática",
    "debit":       "Tarjeta de débito",
    "credit_card": "Tarjeta de crédito",
}

HANDSHAKE_OK         = "FINALIZAR_CLICK_OK"
HANDSHAKE_CARD       = "CARD_CLICK_OK"
HANDSHAKE_CARD_ERROR = "CARD_CLICK_ERROR"


class NikeBotEngine:

    def __init__(self, port: int = 9223, account_name: str = "default"):
        self.port         = port
        self.account_name = account_name
        self.chrome_exe   = self._find_chrome()
        self.profile_path = self._get_profile_path(account_name)

    def _find_chrome(self) -> str:
        for p in CHROME_PATHS:
            if os.path.exists(p):
                return p
        raise FileNotFoundError("Chrome no encontrado.")

    def _get_profile_path(self, name: str) -> str:
        if os.path.isabs(name) and os.path.exists(name):
            return name
        auth = os.path.join("auth", name, "profile_login")
        if os.path.exists(auth):
            return auth
        base = Path.home() / "AppData" / "Local" / "Chromium" / "User Data" / name
        base.mkdir(parents=True, exist_ok=True)
        return str(base)

    def _get_tabs(self) -> list:
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{self.port}/json", timeout=2
            ) as r:
                return json.loads(r.read())
        except Exception:
            return []

    def _get_tab_url(self) -> str | None:
        for _ in range(5):
            tabs = self._get_tabs()
            tab = next((t for t in tabs
                        if t.get("type") == "page"
                        and "nike.cl/checkout" in t.get("url", "")
                        and "webSocketDebuggerUrl" in t), None)
            if not tab:
                tab = next((t for t in tabs
                            if t.get("type") == "page"
                            and "nike.cl" in t.get("url", "")
                            and "webSocketDebuggerUrl" in t), None)
            if not tab:
                tab = next((t for t in tabs
                            if t.get("type") == "page"
                            and "webSocketDebuggerUrl" in t
                            and t.get("url", "").startswith("http")), None)
            if not tab:
                tab = next((t for t in tabs
                            if t.get("type") == "page"
                            and "webSocketDebuggerUrl" in t), None)
            if tab:
                return tab["webSocketDebuggerUrl"]
            time.sleep(0.4)
        return None

    def _conectar(self) -> websocket.WebSocket | None:
        url = self._get_tab_url()
        if not url:
            return None
        try:
            ws = websocket.create_connection(url, timeout=5)
            for m in ("Network.enable", "Page.enable", "Runtime.enable"):
                ws.send(json.dumps({"id": 0, "method": m, "params": {}}))
            ws.send(json.dumps({
                "id": 0,
                "method": "Page.addScriptToEvaluateOnNewDocument",
                "params": {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {get: () => false});
                        window.chrome = {runtime: {}};
                        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                        Object.defineProperty(navigator, 'languages', {get: () => ['es-CL', 'es', 'en-US', 'en']});
                        const _origQuery = window.navigator.permissions.query;
                        window.navigator.permissions.query = (p) => (
                            p.name === 'notifications' ?
                            Promise.resolve({state: Notification.permission}) :
                            _origQuery(p)
                        );
                        delete window.__HEADLESS_TESTING__;
                    """
                },
            }))
            ws.send(json.dumps({
                "id": 0,
                "method": "Network.setBlockedURLs",
                "params": {"urls": URLS_BLOQUEADAS},
            }))
            return ws
        except Exception as e:
            print(f"[CDP] Error: {e}")
            return None

    def _send_cdp(self, ws, payload: dict, stage: str = "CDP",
                  reconnect_once: bool = True):
        """Envio robusto por CDP: si el socket se cierra, reconecta una vez."""
        try:
            ws.send(json.dumps(payload))
            return ws, True
        except Exception as e:
            msg = str(e).lower()
            is_closed = "socket is already closed" in msg
            print(f"[{stage}] ⚠️ send falló: {e}")

            if not reconnect_once or not is_closed:
                return ws, False

            print(f"[{stage}] Reintentando con nueva conexión CDP...")
            ws2 = self._conectar()
            if not ws2:
                print(f"[{stage}] ❌ No se pudo reconectar CDP")
                return None, False

            try:
                ws2.send(json.dumps(payload))
                print(f"[{stage}] ✅ Reconectado")
                return ws2, True
            except Exception as e2:
                print(f"[{stage}] ❌ Reconexión falló: {e2}")
                return ws2, False

    def _escuchar(self, ws, metodo: str, substring: str = "",
                  timeout: float = 5.0) -> tuple[bool, float]:
        t0 = time.time()
        while True:
            elapsed = time.time() - t0
            if elapsed >= timeout:
                return False, elapsed * 1000
            try:
                ws.settimeout(min(1.0, timeout - elapsed))
                raw = ws.recv()
                if not raw:
                    continue
                msg    = json.loads(raw)
                actual = msg.get("method", "")
                if actual != metodo:
                    continue
                if metodo == "Network.responseReceived":
                    url = msg.get("params", {}).get("response", {}).get("url", "")
                    if substring.lower() in url.lower():
                        return True, (time.time() - t0) * 1000
                elif metodo in ("Page.frameStoppedLoading", "Page.loadEventFired"):
                    return True, (time.time() - t0) * 1000
                elif metodo == "Runtime.consoleAPICalled":
                    args  = msg.get("params", {}).get("args", [])
                    texto = args[0].get("value", "") if args else ""
                    if substring in texto:
                        return True, (time.time() - t0) * 1000
                elif metodo == "Page.navigatedWithinDocument":
                    nav_url = msg.get("params", {}).get("url", "")
                    if substring.lower() in nav_url.lower():
                        return True, (time.time() - t0) * 1000
            except websocket.WebSocketTimeoutException:
                continue
            except Exception:
                return False, (time.time() - t0) * 1000

    def _js_evaluar(self, ws, js: str, msg_id: int = 50,
                    timeout: float = 5.0) -> str:
        try:
            ws.send(json.dumps({
                "id": msg_id,
                "method": "Runtime.evaluate",
                "params": {"expression": js, "awaitPromise": True, "timeout": int(timeout*1000)},
            }))
            deadline = time.time() + timeout + 1
            while time.time() < deadline:
                try:
                    ws.settimeout(0.3)
                    msg = json.loads(ws.recv())
                    if msg.get("id") == msg_id:
                        return msg.get("result", {}).get("result", {}).get("value", "") or ""
                except websocket.WebSocketTimeoutException:
                    continue
                except Exception:
                    break
        except Exception:
            pass
        return ""

    def _get_current_url(self, ws) -> str:
        return self._js_evaluar(ws, "window.location.href", msg_id=55, timeout=2.0)

    def _poll_url(self, substring: str, timeout: float = 120.0) -> bool:
        t0 = time.time()
        print(f"[EV5] Polling URL '{substring}' (max {timeout}s)...")
        while time.time() - t0 < timeout:
            try:
                tab_url = self._get_tab_url()
                if not tab_url:
                    time.sleep(2.0)
                    continue
                ws = websocket.create_connection(tab_url, timeout=3)
                url = self._js_evaluar(ws, "window.location.href", msg_id=91, timeout=2.0)
                ws.close()
                if substring in url:
                    elapsed = int((time.time() - t0) * 1000)
                    print(f"[EV5] ✅ Detectado '{substring}' en {elapsed}ms")
                    return True
            except Exception:
                pass
            time.sleep(2.0)
        print(f"[EV5] Timeout {timeout}s — no se detectó '{substring}'")
        return False

    # =========================================================================
    # MODO MONITOR
    # =========================================================================

    def modo_monitor(self, ws, skus: list[str],
                     intervalo_ms: int = 150,
                     stop_event: threading.Event = None) -> bool:
        sku       = skus[0]
        intentos  = 0
        t0        = time.time()
        intervalo = intervalo_ms / 1000.0

        js_atc_validar = f"""
        (() => {{
            return new Promise((resolve) => {{
                fetch('https://www.nike.cl/checkout/cart/add?sku={sku}&qty=1&seller=1&sc=1', {{
                    credentials: 'include', redirect: 'follow',
                }})
                .then(() => fetch('https://www.nike.cl/api/checkout/pub/orderForm', {{
                    credentials: 'include',
                    headers: {{'Accept': 'application/json'}}
                }}))
                .then(r => r.json())
                .then(data => {{
                    const items = data?.items || [];
                    const item  = items.find(i =>
                        String(i.id) === '{sku}' || String(i.productId) === '{sku}'
                    ) || (items.length ? items[0] : null);
                    if (!item) {{ resolve('ATC_FAIL'); return; }}
                    const a = item.availability || '';
                    if (a === 'available') resolve('AVAILABLE');
                    else if (a === 'withoutStock' || a === 'cannotBeDelivered') resolve('WITHOUT_STOCK');
                    else resolve(item.quantity > 0 ? 'AVAILABLE' : 'ATC_FAIL');
                }})
                .catch(e => resolve('ERROR:' + e.message));
            }});
        }})();
        """

        print(f"[Monitor] 🔫 SKU {sku} — polling cada {intervalo_ms}ms")

        while not (stop_event and stop_event.is_set()):
            intentos += 1
            resultado = self._js_evaluar(ws, js_atc_validar, msg_id=77, timeout=2.5)

            if resultado == "AVAILABLE":
                elapsed = time.time() - t0
                print(f"[Monitor] ✅ STOCK en intento {intentos} ({elapsed:.1f}s)")
                return True
            elif resultado == "WITHOUT_STOCK":
                if intentos % 10 == 0:
                    print(f"[Monitor] sin stock físico (#{intentos})")
            elif resultado == "ATC_FAIL":
                if intentos % 30 == 0:
                    print(f"[Monitor] sin stock ({int(time.time()-t0)}s | #{intentos})")
            else:
                time.sleep(0.5)
                continue

            time.sleep(intervalo)

        return False

    # =========================================================================
    # EVENTOS
    # =========================================================================

    def pre_vuelo(self) -> websocket.WebSocket | None:
        t0 = time.time()
        print(f"[EV0] Pre-vuelo {self.account_name}...")
        ws = self._conectar()
        if not ws:
            print(f"[EV0] FALLO — Chrome no responde")
            return None
        print(f"[EV0] Listo en {int((time.time()-t0)*1000)}ms")
        return ws

    def evento_atc(self, ws, skus: list[str]) -> bool:
        t0  = time.time()
        sku = skus[0]
        print(f"[EV1] ATC fetch: SKU {sku}...")

        js_atc = f"""
        (() => {{
            return new Promise(async (resolve) => {{
                try {{
                    await fetch('https://www.nike.cl/checkout/cart/add?sku={sku}&qty=1&seller=1&sc=1', {{
                        credentials: 'include', redirect: 'follow'
                    }});
                    const r    = await fetch('https://www.nike.cl/api/checkout/pub/orderForm', {{
                        credentials: 'include',
                        headers: {{'Accept': 'application/json'}}
                    }});
                    const data  = await r.json();
                    const items = data?.items || [];
                    if (!items.length) {{ resolve('EMPTY'); return; }}
                    const item  = items.find(i =>
                        String(i.id) === '{sku}' || String(i.productId) === '{sku}'
                    ) || items[0];
                    const a = item.availability || 'unknown';
                    resolve(a + '|' + (item.quantity||0) + '|' + (data.value||0));
                }} catch(e) {{
                    resolve('ERROR:' + e.message);
                }}
            }});
        }})();
        """

        avail_raw = self._js_evaluar(ws, js_atc, msg_id=78, timeout=5.0)
        ms = int((time.time() - t0) * 1000)
        print(f"[EV1] Carrito: '{avail_raw}' en {ms}ms")

        if not avail_raw or avail_raw.startswith("ERROR") or avail_raw == "EMPTY":
            print(f"[EV1] FALLO — carrito vacío o error")
            return False

        availability = avail_raw.split("|")[0]
        if availability == "available":
            print(f"[EV1] ✅ Item disponible")
            return True
        elif availability in ("withoutStock", "cannotBeDelivered"):
            print(f"[EV1] ⚠️ Sin stock ({availability})")
            return False
        else:
            print(f"[EV1] Availability: '{availability}' — continuando")
            return True

    def evento_navegacion(self, ws):
        print("[EV2] Navegando a /#/payment...")
        ws, sent = self._send_cdp(
            ws,
            {"id": 20, "method": "Page.navigate",
             "params": {"url": "https://www.nike.cl/checkout/#/payment"}},
            stage="EV2"
        )
        if not sent or not ws:
            print("[EV2] ❌ No se pudo navegar: CDP no disponible")
            return None

        ok, ms = self._escuchar(ws, "Network.responseReceived", "orderForm", timeout=8.0)
        time.sleep(0.8)

        url_actual = self._get_current_url(ws)
        print(f"[EV2] URL: {url_actual}")

        if "orderPlaced" in url_actual:
            print("[EV2] ⚡ Ya en orderPlaced")
            return ws

        if "#/payment" not in url_actual:
            print("[EV2] ⚠️ Forzando via JS hash...")
            self._js_evaluar(ws, "window.location.hash = '#/payment'", msg_id=22, timeout=2.0)
            time.sleep(1.0)

        print(f"[EV2] ✅ DOM_READY:{ms:.0f}ms")
        return ws

    def evento_inyeccion(self, ws, payment_mode: str, card_data: dict) -> str:
        print(f"[EV3] Inyectando '{payment_mode}'...")

        if payment_mode in ("credit_card", "debit"):
            try:
                from engines.card_payment_js import build_card_js
                js    = build_card_js(card_data, card_type="debit" if payment_mode == "debit" else "credit")
                senal = HANDSHAKE_CARD
            except ImportError:
                js    = self._js_pago(payment_mode)
                senal = HANDSHAKE_OK
            js_wrapped = f"(() => {{ console.log('[BOT] Card payment script cargado'); {js.strip()} }})();"
        else:
            senal      = HANDSHAKE_OK
            js_wrapped = "console.log('[BOT] 🔥 MEGA-PRO: transfer (EV4 controla)');"

        ws, sent = self._send_cdp(
            ws,
            {
                "id": 30,
                "method": "Runtime.evaluate",
                "params": {"expression": js_wrapped, "awaitPromise": False}
            },
            stage="EV3"
        )
        if not sent:
            print("[EV3] ⚠️ No se pudo inyectar script")
        print(f"[EV3] Señal: {senal}")
        return senal

    def evento_handshake(self, ws, senal: str, timeout: float = 25.0,
                         payment_mode: str = "transfer") -> tuple[bool, str]:
        """
        EV4 v4: Polling activo desde Python con memoria anti-loop.
        Retorna: (exito: bool, payment_url: str)
        """
        print(f"[EV4] Iniciando polling activo (max {timeout}s)...")
        t0    = time.time()
        label = PAYMENT_LABELS.get(payment_mode, "Transferencia con tu banco")

        try:
            ws, _ = self._send_cdp(
                ws, {"id": 99, "method": "Runtime.enable", "params": {}},
                stage="EV4", reconnect_once=True
            )
            ws, _ = self._send_cdp(
                ws, {"id": 98, "method": "Log.enable", "params": {}},
                stage="EV4", reconnect_once=False
            )
        except Exception:
            pass

        tick         = 0
        state_counts = {}

        while True:
            elapsed = time.time() - t0
            if elapsed >= timeout:
                break

            tick += 1

            js_tick = f"""
            (() => {{
                const url  = window.location.href;
                const hash = window.location.hash;

                if (url.includes('orderPlaced')) return 'ORDER_PLACED';

                // Detección Fintoc multicapa
                const fintocFrame = document.querySelector('iframe[src*="fintoc"]');
                if (fintocFrame && fintocFrame.offsetHeight > 0)
                    return 'FINTOC_OPEN|' + fintocFrame.src;
                const fintocWidget = document.querySelector(
                    '[class*="fintoc"], [id*="fintoc"], .fintoc-widget__container'
                );
                if (fintocWidget && fintocWidget.offsetHeight > 50)
                    return 'FINTOC_OPEN|modal';
                const bankSelector = document.querySelector('[class*="institution"], [class*="bank-list"]');
                if (bankSelector && bankSelector.offsetHeight > 0)
                    return 'FINTOC_OPEN|banklist';
                const bankContent = [...document.querySelectorAll('div, section')]
                    .find(el => el.offsetHeight > 200 && 
                                (el.textContent || '').includes('Banco BCI') &&
                                (el.textContent || '').includes('Banco Scotiabank'));
                if (bankContent) return 'FINTOC_OPEN|banklist';
                const fintocOverlay = [...document.querySelectorAll('div')].find(d => {{
                    const s = getComputedStyle(d);
                    return s.position === 'fixed' && 
                           parseFloat(s.zIndex) > 100 &&
                           d.offsetHeight > 200;
                }});
                if (fintocOverlay) return 'FINTOC_OPEN|overlay';

                if (hash.startsWith('#/cart')) {{
                    window.location.hash = '#/payment';
                    return 'ROUTING_TO_PAYMENT';
                }}
                if (hash.includes('#/profile') || hash.includes('#/shipping'))
                    return 'STUCK_IN_PREVIOUS_STEP:' + hash;

                const modalBtn = [...document.querySelectorAll('button')].find(b => {{
                    const t = (b.textContent || '').trim().toLowerCase();
                    return t === 'entendido' || t === 'aceptar' || t.includes('verifica los datos');
                }});
                if (modalBtn && modalBtn.offsetParent !== null) {{
                    modalBtn.click();
                    return 'MODAL_KILLED:' + modalBtn.textContent.trim();
                }}

                const labelTxt = '{label}'.toLowerCase();
                const lbl = [...document.querySelectorAll('label')].find(l =>
                    (l.textContent || '').toLowerCase().includes(labelTxt)
                );
                if (!lbl) return 'WAITING_FOR_DOM';

                const radioId = lbl.getAttribute('for');
                const radio   = radioId ? document.getElementById(radioId) : null;
                if (!radio?.checked) {{
                    lbl.click();
                    if (radio) {{
                        radio.checked = true;
                        radio.dispatchEvent(new Event('change', {{bubbles: true}}));
                    }}
                    window.__method_selected_at = Date.now();
                    return 'METHOD_SELECTED';
                }}

                if (window.__method_selected_at &&
                    Date.now() - window.__method_selected_at < 600) {{
                    return 'WAITING_VTEX_RESPONSE';
                }}

                const totalNodo  = document.querySelector('.summary-totalizers__total-value, .monetary');
                const precioTxt  = totalNodo ? totalNodo.textContent.replace(/[^0-9]/g, '') : '99999';
                const precioActual = parseInt(precioTxt || '99999');
                if (precioActual > 0 && precioActual < 1000) {{
                    fetch('/api/checkout/pub/orderForm').then(r=>r.json()).then(d=>{{
                        const id = d.orderFormId;
                        fetch('/api/checkout/pub/orderForm/'+id+'/attachments/marketingData',{{
                            method:'POST', credentials:'include',
                            headers:{{'Content-Type':'application/json'}},
                            body:JSON.stringify({{attachmentId:'marketingData',marketingTags:[],utmCampaign:null}})
                        }});
                        fetch('/api/checkout/pub/orderForm/'+id+'/coupons',{{
                            method:'POST', credentials:'include',
                            headers:{{'Content-Type':'application/json'}},
                            body:JSON.stringify({{text:''}})
                        }});
                        if (window.vtexjs?.checkout?.removeDiscount) window.vtexjs.checkout.removeDiscount();
                    }});
                    return 'PRICE_ZERO_PURGED';
                }}

                if (window.__bot_clicked && (Date.now() - window.__bot_clicked < 8000))
                    return 'WAITING_VTEX_RESPONSE';

                let btn = null;
                const allBtns = [...document.querySelectorAll('button')].filter(b => {{
                    if (b.disabled || b.offsetParent === null) return false;
                    const txt = (b.innerText || b.textContent || '').trim().toLowerCase();
                    if (txt.includes('guardar') || txt.includes('editar')) return false;
                    return b.id === 'payment-data-submit' ||
                           (b.hasAttribute('data-testid') && b.getAttribute('data-testid') === 'place-order-button') ||
                           txt === 'finalizar compra' ||
                           txt === 'finalizar la compra' ||
                           txt.startsWith('finalizar');
                }});
                btn = allBtns.sort((a,b) =>
                    b.getBoundingClientRect().width - a.getBoundingClientRect().width
                )[0] || null;
                if (!btn) return 'NO_BTN_FINALIZAR';

                btn.scrollIntoView({{behavior: 'instant', block: 'center'}});
                btn.click();
                setTimeout(() => btn.click(), 100);
                window.__bot_clicked = Date.now();
                return 'CLICKED:' + (btn.innerText || btn.textContent).trim();
            }})()
            """

            try:
                ws.send(json.dumps({
                    "id": 300 + tick,
                    "method": "Runtime.evaluate",
                    "params": {"expression": js_tick, "awaitPromise": False}
                }))
            except Exception:
                break

            deadline = time.time() + 0.15
            while time.time() < deadline:
                try:
                    ws.settimeout(0.05)
                    raw = ws.recv()
                    msg = json.loads(raw)
                    method  = msg.get("method", "")
                    msg_id  = msg.get("id", 0)

                    if msg_id == 300 + tick:
                        val = msg.get("result", {}).get("result", {}).get("value", "") or ""
                        if val:
                            # Solo loguear estados útiles (no spam de WAITING)
                            if not val.startswith("WAITING"):
                                print(f"[EV4] tick={tick} -> {val}")
                            else:
                                print(".", end="", flush=True)

                            state_counts[val] = state_counts.get(val, 0) + 1
                            max_loops = 60 if val == "WAITING_VTEX_RESPONSE" else (20 if val in ("NO_BTN_FINALIZAR", "WAITING_FOR_DOM") else 12)
                            if state_counts.get(val, 0) > max_loops:
                                print(f"\n[EV4] ❌ Loop infinito en '{val}' — abortando")
                                return False, ""

                            if val == "ORDER_PLACED":
                                ms = (time.time() - t0) * 1000
                                print(f"\n[EV4] ✅ ORDER_PLACED en {ms:.0f}ms")
                                return True, ""

                            if val.startswith("FINTOC_OPEN"):
                                ms     = (time.time() - t0) * 1000
                                partes = val.split("|")
                                link   = partes[1] if len(partes) > 1 else ""
                                print(f"\n[EV4] ✅ FINTOC_OPEN en {ms:.0f}ms | {link[:40]}...")
                                return True, link

                            # Pausas tácticas mínimas
                            if val == "METHOD_SELECTED":
                                # Sin sleep — continúa inmediato
                                break
                            elif val.startswith("MODAL_KILLED"):
                                time.sleep(0.5)
                                break
                            elif val.startswith("CLICKED"):
                                print(f"\n[EV4] 🔥 Click ejecutado — esperando Fintoc...")
                                state_counts["WAITING_VTEX_RESPONSE"] = 0
                                time.sleep(0.3)
                                break

                    elif method == "Runtime.consoleAPICalled":
                        args  = msg.get("params", {}).get("args", [])
                        texto = "".join(str(a.get("value","") or a.get("description","")) for a in args)
                        if texto and "[BOT]" in texto:
                            print(f"[JS] {texto}")
                        if senal in texto or "orderPlaced" in texto:
                            ms = (time.time() - t0) * 1000
                            print(f"[EV4] ✅ Console signal en {ms:.0f}ms")
                            return True, ""

                    elif method == "Page.navigatedWithinDocument":
                        nav_url = msg.get("params", {}).get("url", "")
                        if "orderPlaced" in nav_url:
                            ms = (time.time() - t0) * 1000
                            print(f"[EV4] ✅ orderPlaced nav en {ms:.0f}ms")
                            return True, ""

                except websocket.WebSocketTimeoutException:
                    continue
                except Exception:
                    break

            time.sleep(0.05)

        print(f"\n[EV4] FALLO — no confirmado en {timeout}s")
        return False, ""

    # =========================================================================
    # NOTIFICADOR DISCORD
    # =========================================================================

    def _enviar_discord(self, sku: str, estado: str, tiempo_ms: int, payment_url: str = ""):
        WEBHOOK_URL = "https://discord.com/api/webhooks/1447517266106253372/weQNi4CyyNaUwT-L4KT1QzkhSFGTruxpnw7ioRqdBRQNBjCWp7SXhfRVzxT_XW6cJ_DH"
        color   = 5763719 if "FINTOC" in estado else 3066993
        payload = {
            "username": "Nike Bot Pro",
            "embeds": [{
                "title": f"🎉 {estado}",
                "color": color,
                "fields": [
                    {"name": "👤 Cuenta",  "value": self.account_name, "inline": True},
                    {"name": "👟 SKU",     "value": sku,               "inline": True},
                    {"name": "⏱️ Tiempo", "value": f"{tiempo_ms}ms",  "inline": True},
                ],
                "footer": {"text": "Bot v11.2 🦈"}
            }]
        }
        try:
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=3)
            print(f"[Discord] 📩 ¡Notificación enviada al celular del jefe!")
        except Exception as e:
            print(f"[Discord] ❌ Error: {e}")

    # =========================================================================
    # ORQUESTADOR
    # =========================================================================

    def ejecutar_ataque_completo(
        self,
        skus:                 list[str],
        payment_mode:         str             = "transfer",
        card_data:            dict            = None,
        modo_monitor:         bool            = False,
        stop_event:           threading.Event = None,
        esperar_confirmacion: bool            = True,
    ) -> dict:
        if card_data is None:
            card_data = {}

        resultado = {"exito": False, "telemetria": {}, "fallo_en": None}
        t_global  = time.time()

        t0 = time.time()
        ws = self.pre_vuelo()
        resultado["telemetria"]["ev0_ms"] = int((time.time()-t0)*1000)
        if not ws:
            resultado["fallo_en"] = "EV0"
            return resultado

        payment_url = ""

        try:
            print(f"[PRE-EV1] Limpiando descuentos previos...")
            desc_pre = self._limpiar_descuentos_nuclear(ws)
            print(f"[PRE-EV1] {desc_pre}")

            t0 = time.time()
            if modo_monitor:
                print(f"[EV1] Modo monitor — loop hasta stock...")
                stock = self.modo_monitor(ws, skus, stop_event=stop_event)
                if not stock:
                    resultado["fallo_en"] = "EV1_MONITOR_DETENIDO"
                    return resultado
                ev1_ok = self.evento_atc(ws, skus)
                if not ev1_ok:
                    print(f"[EV1] ATC post-monitor falló, continuando...")
            else:
                ev1_ok = self.evento_atc(ws, skus)
                if not ev1_ok:
                    resultado["fallo_en"] = "EV1_SIN_STOCK"
                    resultado["mensaje"]  = f"SKU {skus[0]} sin stock."
                    return resultado
            resultado["telemetria"]["ev1_ms"] = int((time.time()-t0)*1000)

            for intento in range(3):
                desc = self._limpiar_descuentos(ws)
                if desc.startswith("OK:"):
                    try:
                        parts          = desc.split(":")
                        total          = int(parts[1])
                        desc_restantes = parts[2] if len(parts) > 2 else "?"
                        if total >= 1000:
                            print(f"[Engine] ✅ Total OK: ${total} | Descuentos: {desc_restantes}")
                            break
                        else:
                            print(f"[Engine] ⚠️ Total ${total} — reintento {intento+1}/3...")
                            time.sleep(2.0)
                    except Exception:
                        break
                else:
                    print(f"[Engine] ⚠️ _limpiar_descuentos: {desc}")
                    break
                if intento == 2:
                    resultado["fallo_en"] = "DESCUENTO_INVALIDO"
                    return resultado

            print(f"[PRE-EV2] Confirmando shipping...")
            shipping_ok = self._confirmar_shipping(ws)
            print(f"[PRE-EV2] {shipping_ok}")

            t0 = time.time()
            ws = self.evento_navegacion(ws)
            if not ws:
                resultado["fallo_en"] = "EV2_CDP"
                return resultado
            resultado["telemetria"]["ev2_ms"] = int((time.time()-t0)*1000)

            # EV3 solo para tarjetas — transfer usa EV4 directo
            if payment_mode not in ("transfer", "etpay", "mercadopago"):
                senal = self.evento_inyeccion(ws, payment_mode, card_data)
            else:
                senal = HANDSHAKE_OK
                ws, sent = self._send_cdp(
                    ws,
                    {
                        "id": 30, "method": "Runtime.evaluate",
                        "params": {
                            "expression": "console.log('[BOT] 🔥 MEGA-PRO: transfer (EV4 controla)');",
                            "awaitPromise": False
                        }
                    },
                    stage="EV3"
                )
                if not sent or not ws:
                    resultado["fallo_en"] = "EV3_CDP"
                    return resultado

            t0 = time.time()
            ev4ok, payment_url = self.evento_handshake(
                ws, senal, timeout=25.0, payment_mode=payment_mode
            )
            resultado["telemetria"]["ev4_ms"] = int((time.time()-t0)*1000)

            if not ev4ok:
                resultado["fallo_en"] = "EV4"
                return resultado

            resultado["exito"] = True

        finally:
            try:
                ws.close()
            except Exception:
                pass

        if esperar_confirmacion and resultado.get("exito"):
            t0    = time.time()
            ev5ok = self._poll_url("orderPlaced", timeout=120.0)
            resultado["telemetria"]["ev5_ms"] = int((time.time()-t0)*1000)
            resultado["compra_ok"] = ev5ok

        resultado["telemetria"]["total_ms"] = int((time.time()-t_global)*1000)

        estado_txt = "COMPRA FINALIZADA" if resultado.get("compra_ok") else "PAGO FINTOC LISTO PARA CONFIRMAR"

        print(f"\n{'='*60}")
        print(f"✅ {estado_txt} — {self.account_name}")
        print(f"Tel: {resultado['telemetria']}")
        print(f"{'='*60}\n")

        self._enviar_discord(
            sku         = skus[0] if skus else "N/A",
            estado      = estado_txt,
            tiempo_ms   = resultado["telemetria"]["total_ms"],
            payment_url = payment_url
        )

        return resultado

    # =========================================================================
    # COMPATIBILIDAD
    # =========================================================================

    def ataque_backend_cdp(self, skus: list[str] = None) -> bool:
        if not skus:
            return False
        ws = self.pre_vuelo()
        if not ws:
            return False
        ok = self.evento_atc(ws, skus)
        ws.close()
        return ok

    def ataque_backend_os(self, skus: list[str] = None) -> bool:
        if not skus:
            return False
        flags = CHROME_FLAGS + [
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={self.profile_path}",
        ]
        for idx, sku in enumerate(skus):
            url = f"https://www.nike.cl/checkout/cart/add?sku={sku}&qty=1&seller=1&sc=1"
            try:
                subprocess.Popen([self.chrome_exe] + flags + [url],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"[Backend-OS] Error: {e}")
                return False
            if idx < len(skus) - 1:
                time.sleep(0.4)
        return True

    def ataque_frontend(self, payment_mode: str = "transfer",
                        card_data: dict = None, skip_cart_verify: bool = False) -> bool:
        return self.ejecutar_ataque_completo(
            skus=[], payment_mode=payment_mode, card_data=card_data or {}
        ).get("exito", False)

    def cleanup(self):
        pass

    # =========================================================================
    # JS DE PAGO (tarjetas)
    # =========================================================================

    def _js_pago(self, payment_mode: str) -> str:
        label     = PAYMENT_LABELS.get(payment_mode, "Transferencia con tu banco")
        handshake = HANDSHAKE_OK

        return f"""
        (() => {{
            const MAX=30000, t0=Date.now();
            let done=false, sel=false, vtexOk=false, clicked=false, clickTime=0;

            function esBtnError(b) {{
                const txt = b.textContent?.trim().toLowerCase() || '';
                return txt.includes('sin el item') || txt.includes('verifica los datos');
            }}
            function buscarBtn() {{
                const todos = [...document.querySelectorAll('button')]
                    .filter(b => !esBtnError(b) && !b.disabled);
                return (
                    todos.find(b => b.textContent?.trim()==='Finalizar compra') ||
                    todos.find(b => b.textContent?.trim()==='Finalizar la compra') ||
                    document.getElementById('payment-data-submit') ||
                    document.querySelector('[data-testid="place-order-button"]') ||
                    todos.find(b => b.textContent?.trim().toLowerCase().startsWith('finalizar'))
                );
            }}
            function esVisible(el) {{
                if (!el) return false;
                const r = el.getBoundingClientRect();
                if (r.width < 50 || r.height < 50) return false;
                const s = getComputedStyle(el);
                return s.display !== 'none' && s.visibility !== 'hidden' && s.opacity !== '0';
            }}
            function fintocAbierto() {{
                const iframes = [...document.querySelectorAll('iframe')]
                    .filter(f => f.src && f.src.includes('fintoc'));
                if (iframes.some(f => esVisible(f))) return true;
                const w = document.querySelector('[class*="fintoc-widget"],[id*="fintoc-widget"]');
                if (w) {{
                    const r = w.getBoundingClientRect();
                    if (r.height > 200 && esVisible(w)) return true;
                }}
                return false;
            }}
            function seleccionarMetodo() {{
                if (sel) return true;
                if (window.location.hash.startsWith('#/cart')) {{
                    window.location.hash = '#/payment'; return false;
                }}
                const lbl = [...document.querySelectorAll('label')]
                    .find(l => (l.textContent||'').includes('{label}'));
                if (!lbl) return false;
                const radioId = lbl.getAttribute('for');
                const inp = radioId ? document.getElementById(radioId) : null;
                if (inp?.checked) {{ vtexOk=true; sel=true; return true; }}
                lbl.click();
                if (inp) {{
                    inp.checked=true;
                    inp.dispatchEvent(new Event('change',{{bubbles:true}}));
                }}
                sel=true;
                setTimeout(()=>{{vtexOk=true;}},800);
                return true;
            }}
            const iv = setInterval(() => {{
                if (done) {{ clearInterval(iv); return; }}
                if (Date.now()-t0 > MAX) {{ clearInterval(iv); return; }}
                if (window.location.href.includes('orderPlaced')) {{
                    done=true; console.log('{handshake}'); clearInterval(iv); return;
                }}
                if (!clicked) {{
                    if (!seleccionarMetodo()) return;
                    const btn = buscarBtn();
                    if (!btn) return;
                    if (!vtexOk && Date.now()-t0 < 1200) return;
                    vtexOk=true;
                    btn.scrollIntoView({{behavior:'auto',block:'center'}});
                    btn.click();
                    setTimeout(()=>btn.click(), 100);
                    clicked=true; clickTime=Date.now();
                }} else {{
                    const postClick = Date.now()-clickTime;
                    if (postClick < 500) return;
                    if (fintocAbierto()) {{
                        done=true; console.log('{handshake}'); clearInterval(iv); return;
                    }}
                    if (postClick > 5000) {{
                        clicked=false; clickTime=0; vtexOk=true;
                    }}
                }}
            }}, 200);
        }})();
        """

    # =========================================================================
    # LIMPIAR DESCUENTOS
    # =========================================================================

    def _limpiar_descuentos(self, ws) -> str:
        from engines.limpiar_rastro import js_limpiar_descuentos
        resultado = self._js_evaluar(ws, js_limpiar_descuentos(), msg_id=95, timeout=15.0)
        if not resultado:
            return "ERROR:empty_response"
        return resultado

    def _confirmar_shipping(self, ws) -> str:
        js = """
        (() => {
            return new Promise(async (resolve) => {
                try {
                    const r = await fetch('https://www.nike.cl/api/checkout/pub/orderForm', {
                        credentials: 'include',
                        headers: {'Accept': 'application/json', 'Cache-Control': 'no-cache'}
                    });
                    const d = await r.json();
                    const id = d.orderFormId;
                    const addr = d.shippingData?.address;
                    const logistic = d.shippingData?.logisticsInfo;
                    const shippingOk = addr && addr.street &&
                                       logistic && logistic.length > 0 &&
                                       logistic[0].selectedSla;
                    if (shippingOk) { resolve('SHIPPING_OK:' + addr.street); return; }
                    if (logistic && logistic.length > 0 && !logistic[0].selectedSla) {
                        const slas = logistic[0].slas || [];
                        if (slas.length > 0) {
                            const slaId = slas[0].id;
                            await fetch('https://www.nike.cl/api/checkout/pub/orderForm/' + id + '/attachments/shippingData', {
                                method: 'POST', credentials: 'include',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({
                                    attachmentId: 'shippingData',
                                    logisticsInfo: logistic.map((l, i) => ({
                                        itemIndex: i,
                                        selectedSla: slaId,
                                        selectedDeliveryChannel: 'delivery'
                                    }))
                                })
                            });
                            resolve('SHIPPING_CONFIRMED:' + slaId); return;
                        }
                    }
                    resolve('SHIPPING_MISSING');
                } catch(e) { resolve('ERROR:' + e.message); }
            });
        })();
        """
        return self._js_evaluar(ws, js, msg_id=85, timeout=8.0)

    def _limpiar_descuentos_nuclear(self, ws) -> str:
        js = """
        (() => {
            return new Promise(async (resolve) => {
                const B = 'https://www.nike.cl';
                try {
                    const r0 = await fetch(B + '/api/checkout/pub/orderForm', {
                        credentials: 'include',
                        headers: {'Accept': 'application/json', 'Cache-Control': 'no-cache'}
                    });
                    const d0 = await r0.json();
                    const id = d0.orderFormId;
                    if (!id) { resolve('ERROR:NO_ORDERFORM'); return; }
                    await fetch(B + '/api/checkout/pub/orderForm/' + id + '/coupons', {
                        method: 'POST', credentials: 'include',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({text: ''})
                    }).catch(() => {});
                    await fetch(B + '/api/checkout/pub/orderForm/' + id + '/attachments/marketingData', {
                        method: 'POST', credentials: 'include',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            attachmentId: 'marketingData',
                            utmSource: null, utmMedium: null, utmCampaign: null,
                            utmiPage: null, utmiPart: null, utmiCampaign: null,
                            coupon: null, marketingTags: []
                        })
                    }).catch(() => {});
                    if (window.vtexjs?.checkout?.removeDiscount) {
                        await new Promise(res => {
                            window.vtexjs.checkout.removeDiscount().done(res).fail(res);
                        });
                    }
                    await fetch(B + '/api/checkout/pub/orderForm/' + id + '/attachments/clientProfileData', {
                        method: 'POST', credentials: 'include',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({attachmentId: 'clientProfileData', marketingOptIn: false})
                    }).catch(() => {});
                    const r1 = await fetch(B + '/api/checkout/pub/orderForm', {
                        credentials: 'include',
                        headers: {'Accept': 'application/json', 'Cache-Control': 'no-cache'}
                    });
                    const d1 = await r1.json();
                    const totalFinal = d1.value || 0;
                    const nDescFinal = (d1.ratesAndBenefitsData?.rateAndBenefitsIdentifiers || []).length;
                    resolve('OK:' + totalFinal + ':' + nDescFinal);
                } catch(e) { resolve('ERROR:' + e.message); }
            });
        })();
        """
        resultado = self._js_evaluar(ws, js, msg_id=94, timeout=10.0)
        if resultado.startswith("OK:"):
            try:
                total = int(resultado.split(":")[1])
                if total < 1000:
                    print(f"[Engine] ⚠️ Cuenta con descuento forzado — continuando")
                else:
                    print(f"[Engine] ✅ Descuentos limpiados PRE-ATC — total ${total}")
            except Exception:
                pass
        return resultado

    # =========================================================================
    # LIMPIAR CARRITO
    # =========================================================================

    def _limpiar_carrito(self, _retry: bool = False) -> str:
        print(f"[Engine] Limpiando carrito ({self.account_name})...")
        tab_url = self._get_tab_url()
        if not tab_url:
            return "NO_TAB"
        try:
            ws = websocket.create_connection(tab_url, timeout=5)
            ws.send(json.dumps({"id": 0, "method": "Runtime.enable", "params": {}}))
            js = """
            (() => {
                return new Promise((resolve) => {
                    fetch('https://www.nike.cl/api/checkout/pub/orderForm', {
                        credentials: 'include',
                        headers: {'Accept': 'application/json'}
                    })
                    .then(r => r.json())
                    .then(data => {
                        const id    = data.orderFormId;
                        const items = data.items || [];
                        if (!items.length) { resolve('EMPTY'); return; }
                        const oi = items.map((_,i) => ({index:i, quantity:0}));
                        return fetch(
                            'https://www.nike.cl/api/checkout/pub/orderForm/' + id + '/items/removeAll',
                            {
                                method: 'POST', credentials: 'include',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({orderItems: oi})
                            }
                        ).then(() => resolve('CLEARED'));
                    })
                    .catch(e => resolve('ERROR:' + e.message));
                });
            })();
            """
            resultado = self._js_evaluar(ws, js, msg_id=98, timeout=6.0)
            ws.close()
            print(f"[Engine] Carrito: {resultado}")
            return resultado
        except Exception as e:
            return f"ERROR:{e}"


# Aliases
HybridAssassinUltra   = NikeBotEngine
HybridAssassinV6      = NikeBotEngine
HybridAssassin        = NikeBotEngine
HybridAssassinFusion  = NikeBotEngine
HybridAssassinStealth = NikeBotEngine
