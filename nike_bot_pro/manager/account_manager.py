from threading import Thread, Event
from datetime import datetime
from typing import Dict, Optional
import os
import json
import time

from core.account import Account
from core.states import AccountState, GlobalState


MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 3.0  # segundos (3, 6, 12)


class AccountManager:
    def __init__(self, auth_path: str = "auth"):
        # 🔥 CRÍTICO: Convertir a RUTA ABSOLUTA (igual que en manual_login.py)
        # Así evitamos que get_cookies_for_account() falle con "unable to open database file"
        self.auth_path = os.path.abspath(auth_path)
        self.accounts: Dict[str, Account] = {}
        self.max_concurrent = 1

    def load_accounts(self) -> None:
        if not os.path.isdir(self.auth_path):
            print(f"[AccountManager] No existe carpeta {self.auth_path}")
            return
        
        print(f"[AccountManager] Cargando cuentas desde {self.auth_path}...")
        
        for name in os.listdir(self.auth_path):
            # ❌ Ignorar carpetas del sistema y backups
            if name.startswith("__") or name.startswith(".") or name.endswith(".bak"):
                continue
            
            d = os.path.join(self.auth_path, name)
            if not os.path.isdir(d):
                continue
            
            # FUENTE DE VERDAD: .login_ok (creado por login_runner.py)
            # Si existe → READY
            # Si no existe → NO_AUTH
            login_ok = os.path.join(d, ".login_ok")
            valid = os.path.exists(login_ok)
            
            # target check
            target = os.path.join(d, "target.json")
            sku = None
            seller = None
            if os.path.isfile(target):
                try:
                    with open(target, "r", encoding="utf-8") as f:
                        t = json.load(f)
                    sku = t.get("sku")
                    seller = t.get("seller")
                except Exception:
                    sku = None
            # optional per-account config (flags)
            cfg_path = os.path.join(d, "config.json")
            auto_checkout = False
            payment_mode = "manual"
            if os.path.isfile(cfg_path):
                try:
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                    auto_checkout = bool(cfg.get("auto_checkout", False))
                    # payment_mode se define por ejecución, no por config
                    payment_mode = cfg.get("payment_mode", "manual")
                    # allow sku to be defined in config.json as alternative to target.json
                    try:
                        if not sku and cfg.get("sku"):
                            sku = cfg.get("sku")
                            seller = cfg.get("seller", seller)
                    except Exception:
                        pass
                except Exception:
                    auto_checkout = False
                    payment_mode = "manual"
            # determine initial state based ONLY on .login_ok
            if not valid:
                init = AccountState.NO_AUTH
            else:
                init = AccountState.READY
            
            acc = Account(name=name, sku=sku, seller=seller, state=init, account_path=d)
            print(f"[AccountManager] {name}: state={init.name}, sku={sku}, .login_ok={valid}")
            
            # apply flags from config
            acc.auto_checkout = auto_checkout
            acc.payment_mode = payment_mode
            # diagnostics defaults
            acc.retries = 0
            acc.last_error = None
            acc.next_retry_at = None
            if acc.pause_event:
                acc.pause_event.set()
            self.accounts[name] = acc
        
        print(f"[AccountManager] ✅ Cargadas {len(self.accounts)} cuentas")

    def play(self, name: str, live: bool = True, max_price_attempts: int | None = None) -> tuple[bool, str]:
        acc = self.accounts.get(name)
        if not acc:
            return False, "Cuenta no encontrada"
        # Permitir PLAY aunque el estado no sea READY, si hay SKU configurada.
        if not acc.sku:
            return False, "Cuenta sin SKU/Seller"
        
        # 4️⃣ MEJORA: Prevenir doble PLAY (race condition)
        if acc.worker_running:
            return False, f"⚠️ Worker ya en ejecución → espera a que termine"
        
        # 🔒 CAMBIO C: GUARDIA DE SESIÓN (DEPRECATED - moved to StateMachine)
        # La validación de sesión ahora se maneja DENTRO de account_worker()
        # en StateMachine.run() con SESSION_SEED automático.
        # Este bloque está DESACTIVADO porque:
        # 1. acc.session no existe (Account no tiene sesión)
        # 2. La validación ocurre en StateMachine._transition_ready()
        # 3. Si faltan cookies → SESSION_SEED se ejecuta automáticamente
        # 
        # NOTA: Si quieres guardia ANTES del thread, necesitarías:
        # - Crear sesión en account_manager.py
        # - O pasar las cookies a account_worker
        # Por ahora, la guardia ocurre DENTRO de account_worker (correcto).
        
        # Prevenir duplicación: si ya hay un thread corriendo, no iniciar otro
        if acc.thread is not None and acc.thread.is_alive():
            return False, f"Cuenta ya en ejecución (thread activo)"
        running = sum(1 for v in self.accounts.values() if v.state == AccountState.RUNNING)
        if running >= self.max_concurrent:
            return False, "Límite de concurrencia alcanzado"
        
        # 4️⃣ + 5️⃣ MEJORA: Marcar worker como ejecutándose + logging semántico
        acc.worker_running = True
        acc.kill_event.clear()
        acc.pause_event.set()
        
        # start real worker thread
        from runtime.worker import account_worker
        acc.state = AccountState.RUNNING
        acc.start_time = datetime.now()
        acc.thread = Thread(target=account_worker, args=(acc, live, max_price_attempts), daemon=True)
        acc.thread.start()
        
        # start watcher
        w = Thread(target=self._watch_thread, args=(acc,), daemon=True)
        w.start()
        
        return True, "🟡 Preparando sesión segura…"

    def _start_account(self, acc, live: bool = True) -> tuple[bool, str]:
        """Validate session/orderForm before starting account; returns (ok, msg)
        Also clear transient error state before starting a new attempt.
        """
        # pre-validate tokens and orderForm
        from auth.session_builder import build_requests_session
        from vtex.vtex_client import VTEXClient
        from config.settings import BASE_URL
        try:
            session = build_requests_session(acc.account_path or acc.name)
            client = VTEXClient(BASE_URL, session=session)
            client.get_order_form()
        except Exception as e:
            acc.last_error = str(e)[:200]
            acc.last_error_ts = time.time()
            acc.state = AccountState.NO_AUTH
            return False, "Tokens inválidos o sesión muerta"
        # clear transient error and status and start
        acc.last_error = None
        acc.last_status = None
        return self.play(acc.name, live=live)

    def start_queue(self, stagger: float = 0.7, live: bool = True):
        """Start READY accounts up to max_concurrent with a stagger between starts."""
        while True:
            running = sum(1 for v in self.accounts.values() if v.state == AccountState.RUNNING)
            if running >= self.max_concurrent:
                break
            now = time.time()
            next_acc = next(
                (a for a in self.accounts.values()
                 if a.state == AccountState.READY and (a.next_retry_at is None or a.next_retry_at <= now)),
                None
            )
            if not next_acc:
                break
            ok, msg = self._start_account(next_acc, live=live)
            # stagger
            time.sleep(stagger)
        return True

    def set_max_concurrent(self, value: int):
        try:
            value = int(value)
            if value < 1:
                return False, "Valor inválido"
            self.max_concurrent = value
            self._dispatch_queue()
            return True, f"max_concurrent={value}"
        except Exception:
            return False, "Error al setear concurrencia"

    def run_all_ready(self):
        """Trigger dispatcher to attempt READY accounts up to current concurrency."""
        self._dispatch_queue()
        return True, "Ejecutando READY"

    def stop_all(self):
        for acc in self.accounts.values():
            acc.kill_event.set()
        return True, "STOP ALL enviado"

    # --- Retry / Requeue helpers ---
    
    def check_manual(self, name: str) -> tuple[bool, str]:
        """
        ✅ CHECK MANUAL: Abre navegador con sesión real para revisión.
        
        Qué HACE:
        - Valida que hay cookies válidas
        - Abre Chrome visible
        - Inyecta sesión VTEX real
        - Navega a checkout
        
        Qué NO HACE:
        - No toca backend
        - No avanza estados
        - No automátiza nada
        - Humano puede revisar datos/precio/dirección
        
        Returns:
            (True, "🔍 Browser abierto") si exitoso
            (False, "❌ motivo") si falla
        """
        acc = self.accounts.get(name)
        if not acc:
            return False, "Cuenta no encontrada"
        
        # Validar que hay cookies
        try:
            from engines.session_validator import SessionValidator
            validator = SessionValidator()
            if not validator.has_valid_cookies(acc.session):
                return False, "❌ No hay sesión válida para revisar"
        except Exception as e:
            return False, f"Error validando sesión: {e}"
        
        # Abrir navegador para revisión
        try:
            from engines.manual_review import open_manual_review_sync
            import logging
            
            logger = logging.getLogger("CheckManual")
            logger.info(f"🔍 Abriendo navegador para revisión manual de {acc.name}...")
            
            page = open_manual_review_sync(acc.session, log=logger)
            if page:
                logger.info(f"✅ Browser abierto - humano puede revisar")
                return True, "🔍 Browser abierto para revisión manual"
            else:
                return False, "❌ Error abriendo navegador"
        
        except Exception as e:
            return False, f"Error en CHECK: {e}"
    
    def _requeue_with_backoff(self, acc: Account, reason: str):
        """Schedule a requeue with exponential backoff. Does not block the caller."""
        acc.retries = (acc.retries or 0) + 1
        acc.last_error = reason
        acc.last_error_ts = time.time()

        if acc.retries > MAX_RETRIES:
            acc.state = AccountState.ERROR
            print(f"[{acc.name}] ERROR definitivo tras retries")
            return

        backoff = RETRY_BACKOFF_BASE * (2 ** (acc.retries - 1))
        # schedule next attempt at (now + backoff)
        acc.next_retry_at = time.time() + backoff
        acc.state = AccountState.READY
        print(f"[{acc.name}] Reintento #{acc.retries} en {backoff:.1f}s (scheduled)")
        # trigger dispatcher to consider next READY accounts
        self._dispatch_queue()

    def _watch_thread(self, acc: Account):
        """Watch a worker thread and decide requeue / error / ready when it exits."""
        if not acc.thread:
            return
        acc.thread.join()
        # If the account was stopped manually (kill_event set), do not auto-dispatch.
        if acc.kill_event.is_set():
            print(f"[{acc.name}] Stopped manually; watcher will not re-dispatch")
            acc.worker_running = False  # 4️⃣ MEJORA: Limpiar flag
            return
        # if worker set a transient error, handle requeue/backoff
        if acc.last_error:
            print(f"[{acc.name}] ❌ Worker terminó con error: {acc.last_error}")
            acc.worker_running = False  # 4️⃣ MEJORA: Limpiar flag
            # TEMPORAL (DEBUG): NO requeue automático, solo marcar ERROR
            acc.state = AccountState.ERROR
            return
        # if the account completed an action (e.g., successful checkout), leave it OFF
        if getattr(acc, "completed", False):
            acc.state = AccountState.OFF
            acc.worker_running = False  # 4️⃣ MEJORA: Limpiar flag
            print(f"[{acc.name}] Cuenta completada, estado OFF")
            return
        # otherwise, worker exited cleanly -> reset retries and mark READY and dispatch
        acc.retries = 0
        acc.state = AccountState.READY
        acc.worker_running = False  # 4️⃣ MEJORA: Limpiar flag
        self._dispatch_queue()

    def _dispatch_queue(self):
        """Trigger the dispatcher (non-blocking)."""
        t = Thread(target=self.start_queue, daemon=True)
        t.start()

    def stop(self, name: str, timeout: float = 2.0) -> tuple[bool, str]:
        acc = self.accounts.get(name)
        if not acc:
            return False, "Cuenta no encontrada"
        # allow stopping if there is an active thread even if state changed (e.g., NO_AUTH triggered after worker exit)
        if acc.state not in (AccountState.RUNNING, AccountState.PAUSED) and acc.thread is None:
            return False, "Cuenta no en ejecución"
        acc.kill_event.set()
        # wait for thread to exit
        if acc.thread is not None:
            acc.thread.join(timeout)
            if acc.thread.is_alive():
                return False, "No se pudo detener en tiempo"
            acc.thread = None
        acc.state = AccountState.READY
        return True, "Detenida"

    def update_config(self, name: str) -> tuple[bool, str]:
        """Reload `auth/<name>/config.json` and apply to account if not RUNNING.

        Returns (ok, message).
        """
        acc = self.accounts.get(name)
        if not acc:
            return False, "Cuenta no encontrada"
        if acc.state == AccountState.RUNNING:
            return False, "No se puede actualizar mientras la cuenta está RUNNING"
        cfg_path = os.path.join(self.auth_path, name, "config.json")
        if not os.path.isfile(cfg_path):
            return False, "No existe config.json"
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            acc.auto_checkout = bool(cfg.get("auto_checkout", False))
            acc.payment_mode = cfg.get("payment_mode", acc.payment_mode)
            # allow updating sku/seller too
            if cfg.get("sku"):
                acc.sku = cfg.get("sku")
            if cfg.get("seller"):
                acc.seller = cfg.get("seller")
            return True, "Config actualizada"
        except Exception as e:
            return False, f"Error leyendo config: {e}"

    def save_accounts(self) -> tuple[bool, str]:
        """
        💾 Persiste cambios de todas las cuentas en disco.
        
        Escribe config.json para cada cuenta con:
        - sku
        - seller
        - auto_checkout
        - payment_mode
        
        Returns (ok, message).
        """
        saved = 0
        failed = 0
        
        for name, acc in self.accounts.items():
            try:
                # Ruta al config.json (con ruta absoluta)
                cfg_path = os.path.abspath(os.path.join(self.auth_path, name, "config.json"))
                os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
                
                # Preparar config
                cfg = {
                    "sku": acc.sku,
                    "seller": acc.seller if hasattr(acc, 'seller') else getattr(acc, 'seller_id', ''),
                    "auto_checkout": acc.auto_checkout,
                    "payment_mode": getattr(acc, 'payment_mode', 'manual')
                }
                
                # Escribir a disco
                with open(cfg_path, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, indent=2)
                
                saved += 1
            except Exception as e:
                print(f"[AccountManager] ⚠️ Error guardando {name}: {e}")
                failed += 1
        
        if failed == 0:
            msg = f"✅ {saved} cuentas guardadas"
            return True, msg
        else:
            msg = f"⚠️ {saved} guardadas, {failed} errores"
            return True, msg  # Devolver True aunque haya algunos errores

    def list_accounts(self):
        out = []
        for name, a in self.accounts.items():
            runtime = "—"
            if a.state in (AccountState.RUNNING, AccountState.PAUSED) and a.thread:
                runtime = f"thread:{a.thread.ident} started:{a.start_time or '—'}"
            out.append({"name": name, "state": a.state.name, "sku": a.sku, "runtime": runtime})
        return out

    def get_global_state(self) -> GlobalState:
        states = set(a.state for a in self.accounts.values())
        if all(s in (AccountState.OFF, AccountState.READY, AccountState.NO_AUTH) for s in states):
            return GlobalState.IDLE
        if states and all(s == AccountState.RUNNING for s in states if s not in (AccountState.OFF, AccountState.NO_AUTH)):
            return GlobalState.RUNNING
        if AccountState.RUNNING in states:
            return GlobalState.PARTIAL
        return GlobalState.IDLE


__all__ = ["AccountManager"]
