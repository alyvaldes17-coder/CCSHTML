import time
import logging
import os
import json
import threading
from datetime import datetime
from pathlib import Path
from core.states import AccountState
from vtex.tls_client_vtex import TlsVTEXClient
from auth.profile_cookies import get_cookies_for_account
from utils.zombie_killer import matar_zombies_del_perfil, matar_chrome_especifico
from config.settings import BASE_URL

# ⚠️ CONSOLIDACIÓN EN PROGRESO: 30 dic 2025
# RUTA DE EJECUCIÓN REAL:
# main.py → manager/account_manager.py → play() → Thread(account_worker)
#
# ESTADO ACTUAL: account_worker() es MONOLITO (736 líneas)
# TODO: Refactorizar para llamar a runner/state_machine.py::StateMachine.run()
#
# RUTAS MUERTAS (marcadas para eliminar):
# ❌ runner/account_manager.py (eliminado: era duplicado)
# ❌ deterministic_checkout.py (importada pero no llamada)
# ❌ bank_payment_flow.py (existía pero en standby)
# ❌ tools/payment_launcher.py (subprocess, será reemplazado)

HEARTBEAT_INTERVAL = 2
STABILITY_CHECK_INTERVAL = 1.2

log = logging.getLogger("worker")


def open_login_browser(account_path, account_name):
    """
    ⚠️ DEPRECATED: Esta función no se usa más.
    
    El LOGIN ahora se maneja completamente con subprocess en engines/manual_login.py
    que usa subprocess.Popen + process.wait() para Chrome persistente.
    
    Mantendré esta función como stub para evitar imports rotos, pero NO la llames.
    """
    raise RuntimeError(
        "open_login_browser() está DEPRECATED. "
        "Usa engines/manual_login.py::do_login() en su lugar"
    )



def matar_zombies_del_perfil(profile_path, dprint):
    """Mata procesos Chrome que bloquean el perfil"""
    try:
        import psutil
    except ImportError:
        dprint("   psutil no instalado (skipping)")
        return
    
    import os
    ruta_perfil = os.path.abspath(profile_path).replace("/", "\\").lower()
    dprint("   Buscando zombies...")
    killed_count = 0
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'].lower() == 'chrome.exe':
                    cmdline = ' '.join(proc.info['cmdline']).lower()
                    if ruta_perfil in cmdline:
                        proc.terminate()
                        try:
                            proc.wait(timeout=2)
                        except psutil.TimeoutExpired:
                            proc.kill()
                        killed_count += 1
            except (Exception,):
                pass
        
        if killed_count == 0:
            dprint("   No habia zombies (ok)")
        else:
            dprint("   {} zombie(s) eliminado(s)".format(killed_count))
    except Exception as e:
        dprint("   Error: {} (ignorado)".format(e))

# Stub temporal para evitar error de StateMachine indefinido
class StateMachine:
    def __init__(self, session, page, log):
        self.session = session
        self.page = page
        self.log = log
        self.error_reason = "STUB: No implementado"

    def run(self, bank_name=None):
        # Devuelve un estado de prueba y un orderform vacío
        return AccountState.ERROR, {}

def account_worker(account, live: bool = True, max_price_attempts: int | None = None):
    """
    ✅ REFACTORIZADO: Ahora SOLO prepara contexto y llama StateMachine.run()
    
    Responsabilidad (simplificada):
    1. Validar sesión y cookies
    2. Crear requests.Session + Playwright Page
    3. Llamar StateMachine.run() ← ORQUESTADOR ÚNICO
    4. Actualizar estado de account
    5. Fin
    
    NOTA: Toda la lógica de flujo está en runner/state_machine.py::StateMachine
    Este worker es ahora un WRAPPER delgado que:
    - Prepara sesión
    - Abre browser
    - Llama StateMachine
    - Maneja errors
    """
    # from runner.state_machine import StateMachine  # Eliminado: no existe
    from playwright.sync_api import sync_playwright
    from requests import Session
    
    debug_file = "logs/{}_debug.log".format(account.name)
    Path("logs").mkdir(exist_ok=True)
    
    def dprint(*args):
        msg = " ".join(str(a) for a in args)
        print("[{}] {}".format(account.name, msg))
        try:
            with open(debug_file, "a", encoding="utf-8") as df:
                df.write("[{}] {}\n".format(datetime.now().strftime('%H:%M:%S'), msg))
        except:
            pass
    
    dprint("🚀 WORKER REFACTORIZADO: Llamando StateMachine.run()")
    log_account = logging.getLogger("worker.{}".format(account.name))
    
    try:
        # ════════════════════════════════════════════════════════════════════
        # PASO 1: PREPARAR SESIÓN
        # ════════════════════════════════════════════════════════════════════
        dprint("1️⃣ Preparando sesión...")
        
        # 🔥 VALIDACIÓN: Si el perfil existe = está listo para usar
        # La VERDADERA validación ocurre navegando, no leyendo SQLite
        cookies = get_cookies_for_account(account.account_path)
        
        if cookies:
            dprint(f"   ✅ Cookies encontradas en profile_pw (perfil válido)")
        else:
            dprint("   ℹ️  No hay cookies locales (continuando - validación real al navegar)")
        
        cookies = cookies or {}  # Dict vacío si no hay cookies
        
        dprint("   ✅ Sesión lista")
        
        # Crear requests.Session con cookies VTEX
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        session = Session()
        session.headers.update({"User-Agent": user_agent})
        for key, value in cookies.items():
            session.cookies.set(key, value)
        
        # ════════════════════════════════════════════════════════════════════
        # PASO 2: ABRIR NAVEGADOR PLAYWRIGHT (ASYNC)
        # ════════════════════════════════════════════════════════════════════
        dprint("2️⃣ Abriendo navegador...")
        
        profile_dir = os.path.join(account.account_path, "profile_pw")
        os.makedirs(profile_dir, exist_ok=True)
        
        # Matar zombies antes de abrir
        matar_zombies_del_perfil(profile_dir, dprint)
        
        # 🔥 LLAMADA SYNC: sin deadlocks en Windows (sync_playwright)
        dprint("   [DEBUG] 2.0 SYNC: Lanzando navegador...")
        try:
            from playwright.sync_api import sync_playwright
            
            dprint("   [DEBUG] 2.0a: Iniciando sync_playwright...")
            p = sync_playwright().start()
            dprint("   [DEBUG] 2.0b: sync_playwright iniciado")
            
            browser = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            dprint("   [DEBUG] 2.0c: Context abierto")
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            dprint("   [DEBUG] 2.0d SYNC: Navegador abierto ✅")
        except Exception as e:
            dprint(f"   ❌ Error abriendo navegador: {e}")
            account.state = AccountState.ERROR
            account.last_error = str(e)[:200]
            raise
        
        # ✅ Las cookies ya están en el profile_pw (se cargaron al inicio)
        # No necesitamos sincronizar porque sync_playwright usa el mismo directorio
        dprint(f"   ✅ Sesión lista (perfil: {os.path.basename(profile_dir)})")
        
        # ════════════════════════════════════════════════════════════════════
        # PASO 3: LLAMAR STATEMACHINE
        # ════════════════════════════════════════════════════════════════════
        # 📋 CONFIRMACIÓN RUNTIME - VERDAD ABSOLUTA DEL RUN
        print("")
        print("=" * 70)
        print(f"[{account.name}] ⚙️ RUNTIME CONFIG:")
        print(f"[{account.name}]   - SKU: {account.sku or 'SIN SKU'}")
        print(f"[{account.name}]   - Payment: TRANSFERENCIA (BANK)")
        print(f"[{account.name}]   - Auto-Checkout: {account.auto_checkout}")
        print("=" * 70)
        print("")
        
        dprint("3️⃣ Llamando StateMachine.run()...")
        
        sm = StateMachine(
            session=session,
            page=page,
            log=log_account
        )
        
        final_state, final_orderform = sm.run(
            bank_name=getattr(account, 'bank_name', 'Banco Santander')
        )
        
        # ════════════════════════════════════════════════════════════════════
        # PASO 4: PROCESAR RESULTADO
        # ════════════════════════════════════════════════════════════════════
        dprint("4️⃣ Procesando resultado...")
        
        # from core.bot_state import BotState  # Eliminado: no existe
        
        if final_state == AccountState.AWAITING_BANK_CONFIRMATION:
            dprint("")
            dprint("=" * 70)
            dprint("✅ FLUJO COMPLETADO - ESPERANDO CONFIRMACIÓN")
            dprint("=" * 70)
            
            if final_orderform and final_orderform.get('items'):
                total = final_orderform['items'][0].get('price', 0)
                dprint("💰 Total: ${:,.0f} CLP".format(total / 100))
            
            dprint("👤 El usuario debe confirmar en su banco")
            dprint("🤖 El bot NO toca nada más")
            dprint("")
            
            account.state = AccountState.AWAITING_BANK_CONFIRMATION
            account.last_status = "Esperando confirmación bancaria"
            if final_orderform and final_orderform.get('items'):
                account.last_price = final_orderform['items'][0].get('price', 0)
        
        elif final_state == AccountState.ERROR:
            dprint("")
            dprint("❌ FLUJO FALLÓ")
            dprint(f"   Motivo: {sm.error_reason}")
            dprint("")
            
            account.state = AccountState.ERROR
            account.last_status = "Error en flujo"
            account.last_error = sm.error_reason[:200]
        
        else:
            dprint(f"⚠️ Estado terminal inesperado: {final_state.name}")
            account.state = AccountState.ERROR
            account.last_status = f"Estado inesperado: {final_state.name}"
        
        dprint("WORKER FINALIZADO")
    
    except Exception as e:
        dprint("❌ ERROR GENERAL: {}".format(e))
        log_account.exception("Worker crashed: {}".format(e))
        import traceback
        dprint(traceback.format_exc())
        account.state = AccountState.ERROR
        account.last_error = str(e)[:200]


# ============================================================================
# ❌ DEPRECATED: run_drop_task (REEMPLAZADO POR account_worker REFACTORIZADO)
# ============================================================================
# Esta función es OBSOLETA. NO USAR.
# 
# Motivo: Tenía la lógica vieja con "FASE A: BACKEND".
# Reemplazo: account_worker() - version refactorizada que llama StateMachine.run()
#
# TODO: Eliminar completamente después de validar transición a account_worker.
# 
# Para que Python no lance SyntaxError, la función está comentada completamente abajo:
#
# def run_drop_task(account):
#     """DEPRECATED"""
#     pass
#


# ============================================================================
# 🔒 FLUJO DETERMINISTA COMPLETO (Nuevo)
# ============================================================================# ============================================================================
# 🔒 FLUJO DETERMINISTA COMPLETO (Nuevo)
# ============================================================================


def account_worker_deterministic(account, live: bool = True):
    """
    ✅ FLUJO DETERMINISTA PROFESIONAL (nivel Atmos)
    
    GARANTIZADO:
    - Precio congelado (sin $0)
    - Banco seleccionado
    - Modal Fintoc abierto
    - STOP determinista
    - Usuario confirma en su banco
    
    No automatiza:
    - Login bancario
    - 2FA
    - Confirmación final
    """
    
    debug_file = f"logs/{account.name}_deterministic.log"
    Path("logs").mkdir(exist_ok=True)
    
    def dprint(*args):
        msg = " ".join(str(a) for a in args)
        print(f"[{account.name}] {msg}")
        try:
            with open(debug_file, "a", encoding="utf-8") as df:
                df.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        except:
            pass
    
    dprint("=" * 70)
    dprint("🔒 FLUJO DETERMINISTA INICIADO")
    dprint("=" * 70)
    
    log_account = logging.getLogger(f"worker.{account.name}.deterministic")
    
    try:
        # ═════════════════════════════════════════════
        # Fase 0: Validar sesión
        # ═════════════════════════════════════════════
        dprint("0️⃣ Verificando sesión Nike...")
        
        cookies = get_cookies_for_account(account.account_path)
        if cookies:
            dprint(f"✅ Cookies encontradas ({len(cookies)} items)")
        else:
            dprint("ℹ️  Sin cookies - navegación iniciará login si es necesario")
        
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        dprint("1️⃣ Creando cliente VTEX...")
        client = TlsVTEXClient(
            base_url=BASE_URL,
            cookies=cookies,
            user_agent=user_agent,
            order_form_id=None
        )
        
        # Verificar loggedIn
        dprint("2️⃣ Validando loggedIn...")
        of = client.get_order_form()
        
        if not of.get("loggedIn"):
            dprint("❌ Usuario NO logueado en Nike")
            account.state = AccountState.ERROR
            return
        
        dprint("✅ Usuario logueado")
        
        # ═════════════════════════════════════════════
        # Fase 1: ATC (Add To Cart)
        # ═════════════════════════════════════════════
        dprint("3️⃣ Agregando al carrito...")
        
        if account.sku and live:
            try:
                success = client.frontend_add_to_cart(
                    sku_id=account.sku,
                    quantity=1,
                    seller=account.seller,
                    sales_channel="1"
                )
                
                if not success:
                    dprint("❌ add_to_cart falló")
                    account.state = AccountState.ERROR
                    return
                
                of = client.get_order_form()
                if not of or not of.get('items'):
                    dprint("❌ Carrito vacío")
                    account.state = AccountState.ERROR
                    return
                
                item_name = of['items'][0].get('name', 'UNKNOWN')
                item_price = of['items'][0].get('price', 0)
                
                dprint(f"✅ ATC OK: {item_name}")
                dprint(f"   Precio: ${item_price/100:,.0f} CLP")
                
                account.state = AccountState.CART_LOCKED
                account.last_status = "Carrito asegurado"
                
            except Exception as e:
                dprint(f"❌ ERROR ATC: {e}")
                account.state = AccountState.ERROR
                return
        
        # ═════════════════════════════════════════════
        # Fase 2: Abrir Playwright y ejecutar flujo determinista
        # DEPRECATED: account_worker_deterministic fue reemplazado
        # Usa: runtime/bot_controller.py::BotController en su lugar
        dprint("❌ ERROR: account_worker_deterministic() está DEPRECATED")
        account.state = AccountState.ERROR
        account.last_error = "Usa BotController en su lugar"
        return
    
    except Exception as e:
        dprint(f"❌ ERROR GENERAL: {e}")
        log_account.exception(f"Worker crashed: {e}")
        account.state = AccountState.ERROR
        account.last_error = str(e)[:200]
