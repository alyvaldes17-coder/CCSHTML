"""
INTEGRACIÓN DE BotController CON UI (Ejemplo de cómo actualizar ui/app.py)

Este archivo muestra cómo integrar el nuevo BotController (con 6 mejoras)
en tu UI de CustomTkinter.

PASOS:
1. Importar BotController en lugar de Account directo
2. Cambiar _login() para usar controller.handle_btn_login_click()
3. Cambiar _play() para usar controller.handle_btn_play_click(sku)
4. Actualizar estado de botones con is_login_enabled() e is_play_enabled()
"""

# ═══════════════════════════════════════════════════════════════════════
# EJEMPLO 1: Importaciones (reemplazar en ui/app.py línea 1-15)
# ═══════════════════════════════════════════════════════════════════════

"""
ANTES:
    from manager.account_manager import AccountManager
    from controller.controller import Controller
    from core.states import AccountState

DESPUÉS:
"""
from manager.account_manager import AccountManager
from runtime.bot_controller import BotController
from core.account_state import AccountState, STATES_LOGIN_BLOCKED, STATES_PLAY_BLOCKED


# ═══════════════════════════════════════════════════════════════════════
# EJEMPLO 2: Estructura de data (reemplazar en __init__)
# ═══════════════════════════════════════════════════════════════════════

"""
Ahora cada account tiene un BotController asociado:

self.controllers = {}  # {account_name: BotController}

En _build_accounts():
    for name, acc in self.manager.accounts.items():
        # Crear controller para cada cuenta
        profile_path = os.path.join(acc.account_path, "profile_pw")
        controller = BotController(name, profile_path)
        self.controllers[name] = controller
"""


# ═══════════════════════════════════════════════════════════════════════
# EJEMPLO 3: Actualizar _add_account_row() para botones bloqueados
# ═══════════════════════════════════════════════════════════════════════

def _add_account_row_UPDATED(self, name, acc):
    """
    Versión MEJORADA con botones bloqueados según estado.
    
    MEJORA #6: Los botones se deshabilitan según el estado.
    """
    import customtkinter as ctk
    
    controller = self.controllers[name]
    
    row = ctk.CTkFrame(self.container)
    row.pack(fill="x", padx=6, pady=4)

    # Indicador sesión
    session_text = controller.get_status_text()
    session_color = {
        "❌ No logueado": "#FF6B6B",
        "🔄 Logueando...": "#FFA500",
        "✅ Listo para PLAY": "#00FF00",
        "📊 Monitoreando...": "#00AAFF",
        "🎯 ¡Precio encontrado!": "#00FF99",
        "🚀 Chrome abierto": "#FF00FF",
    }.get(session_text, "#FFFFFF")
    
    lbl_session = ctk.CTkLabel(
        row, text=session_text, width=200, anchor="w",
        text_color=session_color, font=("Arial", 10, "bold")
    )
    lbl_session.pack(side="left", padx=6)

    ctk.CTkLabel(row, text=name, width=100, anchor="w").pack(side="left")
    ctk.CTkLabel(row, text=acc.sku or "❌ SIN SKU", width=100).pack(side="left", padx=6)

    # ═════════════════════════════════════════════════
    # BOTONES CON ESTADO (MEJORA #6)
    # ═════════════════════════════════════════════════
    
    # BOTÓN LOGIN
    btn_login = ctk.CTkButton(
        row, text="🔐 LOGIN", width=90, fg_color="orange",
        state="normal" if controller.is_login_enabled() else "disabled",
        command=lambda c=controller, a=name: self._login_v2(c, a)
    )
    btn_login.pack(side="right", padx=3)

    # BOTÓN PLAY (solo habilitado si READY)
    btn_play = ctk.CTkButton(
        row, text="▶ PLAY", width=90,
        fg_color="green" if controller.is_play_enabled() else "#444444",
        state="normal" if controller.is_play_enabled() else "disabled",
        command=lambda c=controller, a=name, s=acc.sku: self._play_v2(c, a, s)
    )
    btn_play.pack(side="right", padx=3)

    # BOTÓN STOP
    btn_stop = ctk.CTkButton(
        row, text="⏹ STOP", width=90, fg_color="red",
        command=lambda c=controller: c.stop_worker()
    )
    btn_stop.pack(side="right", padx=3)

    self.rows[name] = {
        "controller": controller,
        "status": lbl_session,
        "btn_login": btn_login,
        "btn_play": btn_play,
        "btn_stop": btn_stop
    }


# ═══════════════════════════════════════════════════════════════════════
# EJEMPLO 4: Nuevos handlers _login_v2 y _play_v2
# ═══════════════════════════════════════════════════════════════════════

def _login_v2(self, controller: BotController, account_name: str):
    """
    Versión mejorada de _login que usa BotController.
    
    Separa responsabilidades:
    - UI: Llamar handle_btn_login_click()
    - Controller: Manejar estados, validar, etc.
    """
    print(f"\n[UI] 🔐 LOGIN iniciado: {account_name}")
    
    def do_login():
        try:
            success = controller.handle_btn_login_click()
            
            if success:
                print(f"[UI] ✅ {account_name}: Login completado")
                # Refrescar UI
                self._refresh_single_row(account_name)
            else:
                print(f"[UI] ❌ {account_name}: Login falló")
                self._refresh_single_row(account_name)
        
        except Exception as e:
            print(f"[UI] ❌ ERROR LOGIN: {e}")
            import traceback
            traceback.print_exc()
    
    # Fire-and-forget en thread
    import threading
    thread = threading.Thread(target=do_login, daemon=True, name=f"login-{account_name}")
    thread.start()


def _play_v2(self, controller: BotController, account_name: str, sku: str):
    """
    Versión mejorada de _play que usa BotController.
    
    El controller se encarga de:
    - Validar que está en READY
    - Monitorear backend
    - Lanzar Chrome cuando precio está locked
    """
    print(f"\n[UI] ▶ PLAY iniciado: {account_name} (SKU: {sku})")
    
    if not sku:
        print(f"[UI] ❌ {account_name}: No hay SKU configurado")
        return
    
    def do_play():
        try:
            controller.handle_btn_play_click(sku)
            print(f"[UI] ✅ {account_name}: Play finalizado")
            self._refresh_single_row(account_name)
        
        except Exception as e:
            print(f"[UI] ❌ ERROR PLAY: {e}")
            import traceback
            traceback.print_exc()
    
    # Fire-and-forget en thread
    import threading
    thread = threading.Thread(target=do_play, daemon=True, name=f"play-{account_name}")
    thread.start()


def _refresh_single_row(self, account_name: str):
    """Refrescar UI de una sola fila (actualizar botones + estado)"""
    if account_name not in self.rows:
        return
    
    row_data = self.rows[account_name]
    controller = row_data["controller"]
    
    # Actualizar texto de estado
    row_data["status"].configure(text=controller.get_status_text())
    
    # Actualizar botones
    row_data["btn_login"].configure(
        state="normal" if controller.is_login_enabled() else "disabled"
    )
    row_data["btn_play"].configure(
        state="normal" if controller.is_play_enabled() else "disabled",
        fg_color="green" if controller.is_play_enabled() else "#444444"
    )


# ═══════════════════════════════════════════════════════════════════════
# EJEMPLO 5: Refresh automático (en _refresh_loop)
# ═══════════════════════════════════════════════════════════════════════

"""
En tu _refresh_loop() actual:

    def _refresh_loop(self):
        while True:
            try:
                # Actualizar todas las filas
                for name in self.rows:
                    self._refresh_single_row(name)
                
                # Actualizar logs
                self._update_logs()
                
                self.root.after(1000, self._refresh_loop)  # cada 1s
            except Exception as e:
                print(f"Error en refresh loop: {e}")
"""


# ═══════════════════════════════════════════════════════════════════════
# RESUMEN DE CAMBIOS
# ═══════════════════════════════════════════════════════════════════════

"""
✅ CAMBIOS OBLIGATORIOS:

1. Importar BotController y AccountState (NEW)
2. En __init__: crear self.controllers = {}
3. En _build_accounts(): crear BotController para cada cuenta
4. Reemplazar _add_account_row() con versión mejorada
5. Agregar _login_v2(), _play_v2(), _refresh_single_row()
6. Actualizar _refresh_loop() para llamar _refresh_single_row()

✅ RESULTADO FINAL:

- Botón LOGIN bloqueado si ya está logueando
- Botón PLAY bloqueado si no está READY
- Estados visuales claros y actualizados en tiempo real
- No hay race conditions
- No hay mixed responsabilidades

✅ ARQUITECTURA FINAL:

UI (customtkinter)
  ↓
BotController (maneja estados y lógica)
  ↓
PlaywrightEngine (solo abre Chrome)
  ↓
Playwright (browser control)
"""
