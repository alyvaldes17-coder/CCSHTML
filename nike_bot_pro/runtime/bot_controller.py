"""
runtime/bot_controller.py — v11.0 PRODUCCIÓN

Cambios vs v10:
  - _pause_event: pause/resume real sin crash
  - is_attacking protegido con _lock en finally y stop_worker
  - handle_btn_launch_browser: limpia carrito AUTOMÁTICAMENTE al abrir Nav
  - _worker: lee card_data desde config.json["card"] — ya no llega vacío
  - _worker: lee payment_mode desde config.json correctamente
  - CHROME_FLAGS: agrega anti-detección automation
"""

import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request

import psutil
import websocket

from config.settings import AUTH_ROOT
from core.account_state import AccountState, STATES_LOGIN_BLOCKED
from core.account_manager import AccountInfo, CoreAccountManager, get_manager
from engines.engine import NikeBotEngine
from profiles.manager import ProfileManager


CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

CHROME_FLAGS = [
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-extensions",
    "--disable-background-networking",
    "--disable-sync",
    "--disable-translate",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-gpu-compositing",
    "--disable-software-rasterizer",
    "--mute-audio",
    "--remote-allow-origins=*",
    "--exclude-switches=enable-automation",
    # ── Optimización RAM para 13 instancias (16GB) ──
    "--renderer-process-limit=1",
    "--js-flags=--max-old-space-size=128",
    "--disable-canvas-aa",
    "--disable-2d-canvas-clip-aa",
    "--num-raster-threads=1",
    "--enable-low-end-device-mode",
    "--disable-backgrounding-occluded-windows",
]


class BotController:

    def __init__(self, account_name: str, base_path: str = "auth"):
        self.account_name    = account_name
        self.profile_manager = ProfileManager(account_name, base_path)
        self.profile_login   = self.profile_manager.get_login_profile_path()
        self.profile_run     = self.profile_manager.get_run_profile_path()

        self._am   = get_manager()
        self._info = self._am.get(account_name) or AccountInfo(account_id=account_name)

        account_path       = os.path.join(AUTH_ROOT, account_name)
        self.login_ok_path = os.path.join(account_path, ".login_ok")

        if os.path.exists(self.login_ok_path):
            self.state = AccountState.READY
            self._am.set_state(account_name, "READY")
        else:
            self.state = AccountState.NO_AUTH

        self.cdp_port = self._info.port

        self.stop_signal  = False
        self.is_attacking = False
        self._lock        = threading.Lock()
        self._stop_event  = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # set = corriendo, clear = pausado

        # Callbacks opcionales que la UI puede conectar
        self.on_log          = None   # callable(msg: str)
        self.on_state_change = None   # callable(state: str)

        print(f"[{account_name}] BotController v11 puerto={self.cdp_port}")

    # =========================================================================
    # HELPERS INTERNOS
    # =========================================================================

    def _log(self, msg: str):
        print(msg)
        if callable(self.on_log):
            try:
                self.on_log(msg)
            except Exception:
                pass

    def _set_state(self, state: str):
        if callable(self.on_state_change):
            try:
                self.on_state_change(state)
            except Exception:
                pass

    def _read_config(self) -> dict:
        path = os.path.join(AUTH_ROOT, self.account_name, "config.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    # =========================================================================
    # PROPIEDADES
    # =========================================================================

    @property
    def info(self) -> AccountInfo:
        return self._am.get(self.account_name) or self._info

    @property
    def email(self) -> str:
        return self.info.email or "—"

    @property
    def display_name(self) -> str:
        return self.info.display_name or self.account_name

    @property
    def skus_config(self) -> list[str]:
        return self.info.skus or []

    @property
    def payment_mode_config(self) -> str:
        return self.info.payment_mode or "transfer"

    # =========================================================================
    # ESTADOS
    # =========================================================================

    def is_login_enabled(self) -> bool:
        return self.state not in STATES_LOGIN_BLOCKED

    def is_play_enabled(self) -> bool:
        return self.state == AccountState.READY

    def get_status_text(self) -> str:
        return {
            AccountState.NO_AUTH:           "No logueado",
            AccountState.LOGIN_IN_PROGRESS: "Logueando...",
            AccountState.READY:             "Listo para PLAY",
            AccountState.MONITORING:        "Monitoreando...",
            AccountState.PRICE_LOCKED:      "Precio encontrado",
            AccountState.EXECUTING:         "Ejecutando...",
        }.get(self.state, "Desconocido")

    # =========================================================================
    # CHROME
    # =========================================================================

    def _find_chrome(self) -> str | None:
        for path in CHROME_CANDIDATES:
            if os.path.exists(path):
                return path
        return None

    def _puerto_esta_ocupado(self) -> bool:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        r = s.connect_ex(("127.0.0.1", self.cdp_port)) == 0
        s.close()
        return r

    # Alias para app.py que llama _puerto_ocupado()
    def _puerto_ocupado(self) -> bool:
        return self._puerto_esta_ocupado()

    def _chrome_en_nike(self) -> bool:
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{self.cdp_port}/json", timeout=2
            ) as r:
                tabs = json.loads(r.read())
            return any("nike.cl" in t.get("url", "") for t in tabs)
        except Exception:
            return False

    def _get_ws_url(self) -> str | None:
        """
        FIX v10.1: Acepta CUALQUIER tab incluyendo nueva pestaña / Google.
        Orden: checkout nike > nike.cl > http > cualquier page.
        """
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{self.cdp_port}/json", timeout=2
            ) as r:
                tabs = json.loads(r.read())

            # 1. Tab de checkout nike.cl
            tab = next((t for t in tabs
                        if t.get("type") == "page"
                        and "nike.cl/checkout" in t.get("url", "")
                        and "webSocketDebuggerUrl" in t), None)
            # 2. Cualquier tab nike.cl
            if not tab:
                tab = next((t for t in tabs
                            if t.get("type") == "page"
                            and "nike.cl" in t.get("url", "")
                            and "webSocketDebuggerUrl" in t), None)
            # 3. Cualquier page con URL http
            if not tab:
                tab = next((t for t in tabs
                            if t.get("type") == "page"
                            and "webSocketDebuggerUrl" in t
                            and t.get("url", "").startswith("http")), None)
            # 4. FIX v10.1: Cualquier page (nueva pestaña, chrome://, Google, etc.)
            if not tab:
                tab = next((t for t in tabs
                            if t.get("type") == "page"
                            and "webSocketDebuggerUrl" in t), None)

            return tab["webSocketDebuggerUrl"] if tab else None
        except Exception:
            return None

    def _navegar_via_cdp(self, url: str) -> bool:
        """Navega a una URL via CDP. Retorna True si tuvo tab disponible."""
        try:
            ws_url = self._get_ws_url()
            if not ws_url:
                return False
            ws = websocket.create_connection(ws_url, timeout=3)
            ws.send(json.dumps({"id": 1, "method": "Page.navigate",
                                "params": {"url": url}}))
            deadline = time.time() + 3
            while time.time() < deadline:
                try:
                    ws.settimeout(0.3)
                    msg = json.loads(ws.recv())
                    if msg.get("id") == 1:
                        break
                except Exception:
                    break
            ws.close()
            return True
        except Exception:
            return False

    def _sanitizar_entorno(self) -> None:
        port = self.cdp_port
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                for conn in proc.connections(kind="inet"):
                    if conn.laddr.port == port:
                        proc.kill()
                        try:
                            proc.wait(timeout=2)
                        except psutil.TimeoutExpired:
                            proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        lock_file = os.path.join(self.profile_login, "SingletonLock")
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
            except OSError:
                pass

    def _esperar_puerto(self, timeout: float = 10.0) -> bool:
        inicio = time.time()
        while time.time() - inicio < timeout:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if s.connect_ex(("127.0.0.1", self.cdp_port)) == 0:
                s.close()
                return True
            s.close()
            time.sleep(0.2)
        return False

    def handle_btn_launch_browser(self) -> bool:
        """
        Nav: abre Chrome con la sesión existente y limpia el carrito.
        """
        self._log(f"[{self.account_name}] Abriendo navegador...")

        engine = NikeBotEngine(self.cdp_port, self.account_name)
        engine.profile_path = self.profile_login

        if self._puerto_esta_ocupado():
            self._log(f"[{self.account_name}] Chrome abierto — limpiando carrito...")
            self._navegar_via_cdp("https://www.nike.cl/checkout/#/cart")
            time.sleep(2.5)
            resultado = engine._limpiar_carrito()
            self._log(f"[{self.account_name}] ✅ Carrito {resultado} — precalentado")
            return True

        # Chrome cerrado — lanzar con sesión existente
        self._sanitizar_entorno()
        chrome = self._find_chrome()
        if not chrome:
            self._log(f"[{self.account_name}] Chrome no encontrado.")
            return False

        args = [
            chrome,
            f"--user-data-dir={self.profile_login}",
            f"--remote-debugging-port={self.cdp_port}",
            "--window-size=1280,900",
            "https://www.nike.cl",
        ] + CHROME_FLAGS

        try:
            proc = subprocess.Popen(
                args,
                creationflags=0x00000008 if sys.platform == "win32" else 0,
                **({} if sys.platform == "win32" else {"preexec_fn": os.setsid}),
            )
            self._log(f"[{self.account_name}] Chrome lanzado PID={proc.pid}")

            if not self._esperar_puerto():
                self._log(f"[{self.account_name}] Timeout esperando Chrome")
                return False

            time.sleep(3.5)
            self._log(f"[{self.account_name}] Limpiando carrito automáticamente...")
            self._navegar_via_cdp("https://www.nike.cl/checkout/#/cart")
            time.sleep(2.0)
            resultado = engine._limpiar_carrito()
            self._log(f"[{self.account_name}] ✅ Carrito {resultado} — listo para drop")
            return True

        except Exception as e:
            self._log(f"[{self.account_name}] Error: {e}")
            return False
    # =========================================================================

    def handle_btn_play_hybrid(self, sku_input: str) -> None:
        with self._lock:
            if self.is_attacking:
                # Toggle pause/resume
                if self._pause_event.is_set():
                    self._pause_event.clear()  # pausar
                    self._log(f"[{self.account_name}] ⏸ Pausado")
                    self._set_state("paused")
                else:
                    self._pause_event.set()    # resumir
                    self._log(f"[{self.account_name}] ▶ Resumido")
                    self._set_state("playing")
                return

            self.is_attacking = True
            self.stop_signal  = False
            self._stop_event.clear()
            self._pause_event.set()  # asegurar que arranca corriendo

            t = threading.Thread(
                target=self._worker,
                args=(sku_input,),
                daemon=True,
                name=f"sniper-{self.account_name}",
            )
            t.start()

    # =========================================================================
    # WORKER
    # =========================================================================

    def _worker(self, sku_input: str) -> None:
        t0 = time.time()

        try:
            # Leer config.json — fuente de verdad
            cfg          = self._read_config()
            payment_mode = cfg.get("payment_mode") or cfg.get("payment_method") or "transfer"
            skus         = [s for s in cfg.get("skus", []) if s]
            if not skus and cfg.get("sku"):
                skus = [cfg["sku"]]

            # card_data desde config.json["card"]
            card_data = {}
            if payment_mode in ("credit_card", "debit"):
                card_data = cfg.get("card", {})
                if not card_data.get("card_number"):
                    self._log(f"[{self.account_name}] ⚠️ Sin datos tarjeta — configura en Edit")

            if sku_input and sku_input not in skus:
                skus = [sku_input] + skus

            if not skus:
                self._log(f"[{self.account_name}] Sin SKU configurado")
                return

            masked = ("****" + card_data["card_number"][-4:]) if card_data.get("card_number") else ""
            self._log(f"\n{'='*60}")
            self._log(f"🔥 [{self.account_name}] ATAQUE v11")
            self._log(f"   SKUs:  {skus}")
            self._log(f"   Pago:  {payment_mode}" + (f"  Tarjeta: {masked}" if masked else ""))
            self._log(f"{'='*60}")

            self._set_state("playing")

            if not self._chrome_en_nike():
                self._log(f"[{self.account_name}] Navegando a Nike.cl...")
                if not self._navegar_via_cdp("https://www.nike.cl/checkout/#/cart"):
                    self._log(f"[{self.account_name}] ⚠️ Abre Nav primero")
                    self._set_state("failed")
                    return
                time.sleep(3.0)

            engine = NikeBotEngine(self.cdp_port, self.account_name)
            engine.profile_path = self.profile_login

            resultado = engine.ejecutar_ataque_completo(
                skus                 = skus,
                payment_mode         = payment_mode,
                card_data            = card_data,
                modo_monitor         = True,
                stop_event           = self._stop_event,
                esperar_confirmacion = True,
            )

            total_ms = int((time.time() - t0) * 1000)

            if resultado.get("compra_ok"):
                self._log(f"[{self.account_name}] ✅ COMPRA OK en {total_ms}ms")
                self._set_state("done")
                self._am.registrar_compra(self.account_name, skus[0], telemetria=resultado["telemetria"])
                self.state = AccountState.READY
            elif resultado.get("exito"):
                self._log(f"[{self.account_name}] ✅ Pago iniciado — esperando confirmación")
                self._set_state("done")
            else:
                fallo = resultado.get("fallo_en", "?")
                if "DETENIDO" in str(fallo):
                    self._set_state("stopped")
                else:
                    self._log(f"[{self.account_name}] ❌ Fallo en {fallo} ({total_ms}ms)")
                    self._set_state("failed")

        except Exception as e:
            import traceback
            self._log(f"[{self.account_name}] Error fatal: {e}")
            traceback.print_exc()
            self._set_state("failed")

        finally:
            with self._lock:
                self.is_attacking = False
            self._log(f"[{self.account_name}] Worker detenido")

    # =========================================================================
    # LIMPIAR CARRITO
    # =========================================================================

    def limpiar_carrito(self) -> str:
        """Limpia el carrito. Llamado desde botón 🗑 en la UI."""
        engine = NikeBotEngine(self.cdp_port, self.account_name)
        engine.profile_path = self.profile_login
        return engine._limpiar_carrito()

    # =========================================================================
    # CHECK SESSION
    # =========================================================================

    def check_session(self) -> bool:
        """Verifica sesión activa via orderForm API."""
        try:
            ws_url = self._get_ws_url()
            if not ws_url:
                return False

            ws = websocket.create_connection(ws_url, timeout=5)
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
                        const email = data?.clientProfileData?.email || '';
                        resolve(email ? 'OK:' + email : 'NO_AUTH');
                    })
                    .catch(() => resolve('NO_AUTH'));
                });
            })();
            """

            ws.send(json.dumps({
                "id": 55, "method": "Runtime.evaluate",
                "params": {"expression": js, "awaitPromise": True, "timeout": 6000},
            }))

            deadline = time.time() + 8
            while time.time() < deadline:
                try:
                    ws.settimeout(0.5)
                    msg = json.loads(ws.recv())
                    if msg.get("id") == 55:
                        val = (msg.get("result", {})
                                  .get("result", {})
                                  .get("value", ""))
                        ws.close()
                        if val.startswith("OK:"):
                            email = val[3:]
                            self._log(f"[{self.account_name}] Sesión OK: {email}")
                            self.state = AccountState.READY
                            # Guardar email en el manager para que _get_full_email lo lea
                            self._am.update_config(self.account_name, email=email)
                            # También guardar en config.json (leído por la UI)
                            try:
                                cfg_path = os.path.join(AUTH_ROOT, self.account_name, "config.json")
                                cfg = {}
                                if os.path.exists(cfg_path):
                                    with open(cfg_path, "r", encoding="utf-8") as f:
                                        cfg = json.load(f)
                                cfg["email"] = email
                                cfg["nike_email"] = email
                                os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
                                with open(cfg_path, "w", encoding="utf-8") as f:
                                    json.dump(cfg, f, indent=2, ensure_ascii=False)
                            except Exception:
                                pass
                            if not os.path.exists(self.login_ok_path):
                                open(self.login_ok_path, "w").close()
                            return True
                        else:
                            self._log(f"[{self.account_name}] Sin sesión activa")
                            return False
                except websocket.WebSocketTimeoutException:
                    continue
                except Exception:
                    break

            try:
                ws.close()
            except Exception:
                pass
            return False

        except Exception as e:
            self._log(f"[{self.account_name}] check_session error: {e}")
            return False

    # =========================================================================
    # MULTI-CUENTA
    # =========================================================================

    @staticmethod
    def disparar_todos(controllers: list["BotController"], sku: str = "") -> None:
        ready = [c for c in controllers if c.state == AccountState.READY and not c.is_attacking]
        if not ready:
            print("[Multi] Sin cuentas READY.")
            return
        print(f"[Multi] Disparando {len(ready)} cuentas — SKU {sku}")
        for ctrl in ready:
            ctrl.handle_btn_play_hybrid(sku)

    @staticmethod
    def detener_todos(controllers: list["BotController"]) -> None:
        for ctrl in controllers:
            if ctrl.is_attacking:
                ctrl.stop_worker()

    # =========================================================================
    # UPDATE / STOP
    # =========================================================================

    def update_account(self, display_name=None, email=None,
                       payment_mode=None, skus=None, notas=None):
        self._am.update_config(
            self.account_name,
            display_name=display_name,
            email=email,
            payment_mode=payment_mode,
            skus=skus,
            notas=notas,
        )
        self._info = self._am.get(self.account_name)

    def stop_worker(self) -> None:
        self._stop_event.set()
        self._pause_event.set()  # desbloquear si estaba pausado
        self.stop_signal = True
        with self._lock:
            self.is_attacking = False
        self._log(f"[{self.account_name}] Worker detenido")
