"""
ui/app.py

Cambios vs version anterior:
- on_log callback: logs del engine aparecen en la UI en tiempo real
- on_state_change: estado se actualiza cuando EV4 confirma (no cuando termina el thread)
- "Completado" solo cuando handshake real
- Boton carrito separado del flujo
- PLAY hace toggle pause/resume cuando hay ataque en curso
- STOP detiene completamente
- Check Sessions verifica sesion real via CDP
"""

import customtkinter as ctk
import threading
import os
import json
import time
from collections import deque

from manager.account_manager import AccountManager
from core.account_state import AccountState as BotAccountState
from ui.account_editor import AccountEditor
from runtime.bot_controller import BotController

# ─── PALETA ───────────────────────────────────────────────────────────────────
C_BG         = "#0a0a0a"
C_PANEL      = "#111111"
C_ROW        = "#161616"
C_ROW_ALT    = "#121212"
C_BORDER     = "#2a2a2a"

C_GREEN      = "#00e676"
C_GREEN_DIM  = "#0d2e1a"
C_YELLOW     = "#ffd600"
C_YELLOW_DIM = "#2e2600"
C_RED        = "#ff1744"
C_RED_DIM    = "#2e0010"
C_BLUE       = "#2979ff"
C_BLUE_DIM   = "#0a1a3d"
C_ORANGE     = "#ff9100"
C_ORANGE_DIM = "#2e1a00"
C_GRAY       = "#2a2a2a"
C_PURPLE     = "#aa00ff"
C_PURPLE_DIM = "#1a0030"

C_TEXT     = "#e8e8e8"
C_TEXT_DIM = "#555555"
C_TEXT_MED = "#888888"

FONT_MONO  = ("Consolas", 10)
FONT_LABEL = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI Semibold", 10)
FONT_TITLE = ("Segoe UI Semibold", 12)


def _darken(hex_color: str, factor: float = 0.65) -> str:
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"
    except Exception:
        return hex_color


class AppUI:
    def __init__(self, manager: AccountManager, controller=None):
        self.manager     = manager
        self.controller  = controller
        self.rows        = {}
        self.controllers = {}
        self._log_buffer = deque(maxlen=500)
        self.max_cuentas = 99
        self._cuenta_count = 0

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()
        self.root.title("Nike Bot Pro")
        self.root.geometry("1420x740")
        self.root.configure(fg_color=C_BG)
        self.root.attributes("-alpha", 0.96)

        self._build_ui()
        self._refresh_loop()

    # =========================================================================
    # CONSTRUCCION UI
    # =========================================================================

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self.root, fg_color=C_PANEL, height=46, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="⬡  NIKE BOT PRO",
            font=("Segoe UI Semibold", 13), text_color=C_GREEN
        ).pack(side="left", padx=16)

        ctrl = ctk.CTkFrame(header, fg_color="transparent")
        ctrl.pack(side="left", padx=8)

        ctk.CTkLabel(ctrl, text="Concurrent:", font=FONT_LABEL,
                     text_color=C_TEXT_DIM).pack(side="left", padx=(0, 4))
        self.var_concurrent = ctk.StringVar(
            value=str(getattr(self.manager, "max_concurrent", 1))
        )
        ctk.CTkEntry(
            ctrl, width=44, textvariable=self.var_concurrent,
            fg_color=C_ROW, border_color=C_BORDER,
            text_color=C_TEXT, font=FONT_MONO
        ).pack(side="left")
        self._btn(ctrl, "Set", self._apply_concurrency, C_GRAY, w=44).pack(side="left", padx=4)
        self._btn(ctrl, "Check Sessions", self._check_all_sessions,
                  C_BLUE_DIM, w=120, text_color=C_BLUE).pack(side="left", padx=4)
        self._btn(ctrl, "▶ Run All READY", self._run_all,
                  C_GREEN_DIM, w=120, text_color=C_GREEN).pack(side="left", padx=4)
        self._btn(ctrl, "🧹 Limpiar Rastro", self._limpiar_rastro_todas,
                  "#1a1a00", w=120, text_color="#ffd600").pack(side="left", padx=4)

        self._btn(header, "■  STOP ALL", self._stop_all,
                  C_RED_DIM, w=100, text_color=C_RED).pack(side="right", padx=12)

        # Body
        body = ctk.CTkFrame(self.root, fg_color=C_BG)
        body.pack(fill="both", expand=True, padx=8, pady=6)

        # Panel cuentas
        left = ctk.CTkFrame(body, fg_color=C_PANEL, corner_radius=6)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Cabecera columnas
        col_header = ctk.CTkFrame(left, fg_color=C_BORDER, height=24, corner_radius=0)
        col_header.pack(fill="x", padx=1, pady=(1, 0))
        col_header.pack_propagate(False)
        for text, w in [
            ("", 26), ("Cuenta", 148), ("Puerto", 46), ("SKU", 84),
            ("Pago", 68), ("Estado", 140), ("", 5)
        ]:
            ctk.CTkLabel(col_header, text=text, width=w, font=("Segoe UI", 8),
                         text_color=C_TEXT_DIM, anchor="w").pack(side="left", padx=3)

        self.scroll = ctk.CTkScrollableFrame(
            left, fg_color="transparent",
            scrollbar_button_color=C_BORDER,
            scrollbar_button_hover_color=C_GRAY
        )
        self.scroll.pack(fill="both", expand=True, padx=1, pady=1)

        # Footer con botón + Agregar cuenta
        foot = ctk.CTkFrame(left, fg_color=C_BORDER, height=30, corner_radius=0)
        foot.pack(fill="x", padx=1, pady=(0, 1))
        foot.pack_propagate(False)
        self._cuenta_lbl = ctk.CTkLabel(foot, text="0 cuentas",
            font=("Segoe UI", 9), text_color=C_TEXT_DIM)
        self._cuenta_lbl.pack(side="left", padx=10)
        ctk.CTkButton(foot, text="＋ Agregar cuenta",
            fg_color="transparent", hover_color=C_GREEN_DIM,
            text_color=C_GREEN, font=("Segoe UI Semibold", 9),
            width=130, height=22, border_width=1, border_color=C_GREEN_DIM,
            command=self._agregar_cuenta,
        ).pack(side="right", padx=8, pady=4)

        self._build_accounts()

        # Panel logs
        right = ctk.CTkFrame(body, fg_color=C_PANEL, corner_radius=6, width=320)
        right.pack(side="right", fill="both", padx=(5, 0))
        right.pack_propagate(False)

        log_head = ctk.CTkFrame(right, fg_color=C_BORDER, height=24, corner_radius=0)
        log_head.pack(fill="x")
        log_head.pack_propagate(False)
        ctk.CTkLabel(log_head, text="LOGS EN VIVO", font=("Segoe UI", 8),
                     text_color=C_TEXT_DIM).pack(side="left", padx=8)
        self._btn(log_head, "✕", self._clear_logs, C_GRAY, w=28, h=20,
                  font=("Segoe UI", 9)).pack(side="right", padx=4, pady=2)

        self.log_box = ctk.CTkTextbox(
            right, state="disabled", wrap="none",
            font=("Consolas", 9), fg_color=C_BG,
            text_color="#33ff77", corner_radius=0
        )
        self.log_box.pack(fill="both", expand=True, padx=1, pady=1)

    def _btn(self, parent, text, cmd, color, w=80, text_color=C_TEXT,
             font=FONT_BOLD, h=26):
        return ctk.CTkButton(
            parent, text=text, command=cmd,
            width=w, height=h,
            fg_color=color, hover_color=_darken(color),
            text_color=text_color, font=font,
            corner_radius=3, border_width=0,
        )

    # =========================================================================
    # FILAS DE CUENTAS
    # =========================================================================

    def _get_display_name(self, name: str) -> str:
        """
        Retorna el nombre visible para la cuenta.
        Busca en config.json los campos en orden de prioridad:
          1. display_name  2. email  3. nike_email (legacy)  4. account_id
        """
        cfg_path = os.path.join("auth", name, "config.json")
        try:
            with open(cfg_path, encoding="utf-8") as f:
                cfg = json.load(f)

            dn = cfg.get("display_name", "").strip()
            if dn:
                return dn

            email = cfg.get("email", "").strip()
            if email:
                return email.split("@")[0]

            nike_email = cfg.get("nike_email", "").strip()
            if nike_email:
                return nike_email.split("@")[0]
        except Exception:
            pass
        return name

    def _get_full_email(self, name: str) -> str:
        """Email completo — busca en account.json y config.json."""
        for filename in ("account.json", "config.json"):
            path = os.path.join("auth", name, filename)
            try:
                with open(path, encoding="utf-8") as f:
                    cfg = json.load(f)
                email = cfg.get("email") or cfg.get("nike_email") or ""
                if email:
                    return email
            except Exception:
                pass
        return ""

    def _build_accounts(self):
        """Inicia vacío — usuario agrega con +"""
        for w in self.scroll.winfo_children():
            w.destroy()
        self.rows = {}
        self.controllers = {}
        self._cuenta_count = 0
        self._actualizar_footer()

    def _agregar_cuenta(self):
        if self._cuenta_count >= self.max_cuentas:
            self._log(f"[UI] Límite de {self.max_cuentas} cuentas")
            return

        mostradas = set(self.rows.keys())

        # Ordenar por puerto real
        cuentas_ordenadas = sorted(
            self.manager.accounts.items(),
            key=lambda x: self._get_port(x[0])
        )

        for name, acc in cuentas_ordenadas:
            if name not in mostradas:
                self._add_row(name, acc, self._cuenta_count)
                self._cuenta_count += 1
                self._actualizar_footer()
                # Auto-verificar sesión de esta cuenta recién agregada
                self._verificar_sesion_disco(name)
                self._log(f"[UI] + {self._get_display_name(name)}")
                return

        # No hay más cuentas disponibles — crear nueva
        self._crear_cuenta_nueva()

    def _crear_cuenta_nueva(self):
        """Diálogo simple para crear cuenta nueva."""
        # Calcular próximo nombre automático
        existentes = list(self.manager.accounts.keys())
        nums = []
        for n in existentes:
            try:
                nums.append(int(n.replace("cuenta", "")))
            except Exception:
                pass
        siguiente = max(nums) + 1 if nums else 1
        nuevo_nombre = f"cuenta{siguiente}"

        dialogo = ctk.CTkToplevel(self.root)
        dialogo.title("Nueva cuenta")
        dialogo.geometry("340x180")
        dialogo.resizable(False, False)
        dialogo.transient(self.root)
        dialogo.grab_set()
        dialogo.configure(fg_color=C_BG)

        ctk.CTkLabel(dialogo, text="Nombre de la cuenta:",
                     font=("Segoe UI", 11), text_color=C_TEXT
                     ).pack(padx=20, pady=(20, 4), anchor="w")

        entry = ctk.CTkEntry(dialogo, fg_color=C_ROW, border_color=C_BORDER,
                             text_color=C_TEXT, font=("Consolas", 12), height=34)
        entry.pack(fill="x", padx=20)
        entry.insert(0, nuevo_nombre)
        entry.select_range(0, "end")
        entry.focus()

        def confirmar():
            nombre = entry.get().strip()
            if not nombre:
                return
            # Crear carpeta y config vacío
            carpeta = os.path.join("auth", nombre)
            os.makedirs(os.path.join(carpeta, "profile_login"), exist_ok=True)
            cfg = os.path.join(carpeta, "config.json")
            if not os.path.exists(cfg):
                with open(cfg, "w") as f:
                    json.dump({"payment_mode": "transfer"}, f, indent=2)
            # Recargar manager y agregar fila
            self.manager.load_accounts()
            acc = self.manager.accounts.get(nombre)
            if acc:
                self._add_row(nombre, acc, self._cuenta_count)
                self._cuenta_count += 1
                self._actualizar_footer()
                self._log(f"[UI] Nueva cuenta: {nombre}")
            dialogo.destroy()

        ctk.CTkButton(dialogo, text="Crear", fg_color=C_GREEN_DIM,
                      text_color=C_GREEN, height=34,
                      command=confirmar).pack(fill="x", padx=20, pady=12)

        entry.bind("<Return>", lambda _: confirmar())

    def _verificar_sesion_disco(self, name: str):
        """Verifica .login_ok sin necesitar Chrome."""
        login_ok = os.path.join("auth", name, ".login_ok")
        ctrl = self.controllers.get(name)
        if not ctrl or name not in self.rows:
            return
        r = self.rows[name]
        if os.path.exists(login_ok):
            ctrl.state = BotAccountState.READY
            email = self._get_full_email(name)
            display = email.split("@")[0] if email else self._get_display_name(name)
            try:
                r["name"].configure(text=display, text_color=C_GREEN)
                r["dot"].configure(text_color=C_GREEN)
                r["status"].configure(text="Listo", text_color=C_GREEN)
            except Exception:
                pass
        else:
            try:
                r["dot"].configure(text_color=C_RED)
                r["status"].configure(text="No logueado", text_color=C_TEXT_DIM)
            except Exception:
                pass

    def _get_port(self, name: str) -> int:
        """Lee el puerto real desde el AccountManager."""
        from core.account_manager import get_manager
        info = get_manager().get(name)
        if info:
            return info.port
        return 9999

    def _quitar_cuenta(self, name):
        """Quita una cuenta de la tabla (no la borra del manager)."""
        if name not in self.rows:
            return
        r = self.rows.pop(name)
        # Detener worker si está corriendo
        ctrl = self.controllers.pop(name, None)
        if ctrl:
            try:
                ctrl.stop_worker()
            except Exception:
                pass
        # Destruir el widget de la fila
        try:
            r["row"].destroy()
        except Exception:
            pass
        self._cuenta_count = max(0, self._cuenta_count - 1)
        self._actualizar_footer()
        self._log(f"[UI] - {self._get_display_name(name)}")

    def _actualizar_footer(self):
        n = getattr(self, '_cuenta_count', 0)
        try:
            self._cuenta_lbl.configure(text=f"{n} cuenta{'s' if n != 1 else ''}")
        except Exception:
            pass

    def _add_row(self, name, acc, index):
        # Crear controller para esta cuenta
        ctrl = BotController(name)
        ctrl.on_log = lambda msg, n=name: self.root.after(
            0, lambda m=msg: self._log(m)
        )
        ctrl.on_state_change = lambda state, n=name: self.root.after(
            0, lambda s=state, nm=n: self._set_state(nm, s)
        )
        self.controllers[name] = ctrl

        bg       = C_ROW if index % 2 == 0 else C_ROW_ALT
        is_ready = ctrl.state == BotAccountState.READY

        row = ctk.CTkFrame(self.scroll, fg_color=bg, height=34, corner_radius=3)
        row.pack(fill="x", pady=1)
        row.pack_propagate(False)

        dot = ctk.CTkLabel(
            row, text="●", width=24,
            text_color=C_GREEN if is_ready else C_RED,
            font=("Segoe UI", 11)
        )
        dot.pack(side="left", padx=(6, 0))

        lbl_name = ctk.CTkLabel(
            row, text=self._get_display_name(name),
            width=146, anchor="w", font=FONT_BOLD, text_color=C_TEXT
        )
        lbl_name.pack(side="left", padx=4)

        lbl_port = ctk.CTkLabel(
            row, text=str(ctrl.cdp_port), width=44, anchor="w",
            font=FONT_MONO, text_color=C_TEXT_DIM
        )
        lbl_port.pack(side="left", padx=4)

        sku_val = acc.sku or "—"
        lbl_sku = ctk.CTkLabel(
            row, text=sku_val, width=82, anchor="w",
            font=FONT_MONO, text_color=C_GREEN if acc.sku else C_TEXT_DIM
        )
        lbl_sku.pack(side="left", padx=4)

        pay_map = {
            "transfer": "Fintoc", "mercadopago": "MP",
            "credit_card": "Card", "debit": "Débito", "manual": "Manual",
        }
        pm = getattr(acc, "payment_mode", getattr(acc, "payment_method", "manual"))
        ctk.CTkLabel(
            row, text=pay_map.get(pm, pm), width=66, anchor="w",
            font=FONT_LABEL, text_color=C_TEXT_MED
        ).pack(side="left", padx=4)

        lbl_status = ctk.CTkLabel(
            row, text=ctrl.get_status_text(), width=138, anchor="w",
            font=FONT_LABEL,
            text_color=C_GREEN if is_ready else C_TEXT_DIM
        )
        lbl_status.pack(side="left", padx=4)

        # Botones (derecha)
        btns = ctk.CTkFrame(row, fg_color="transparent")
        btns.pack(side="right", padx=6)

        # ✕ Quitar de la tabla
        self._btn(btns, "✕", lambda n=name: self._quitar_cuenta(n),
                  C_GRAY, w=24, text_color=C_TEXT_DIM, h=24,
                  font=("Segoe UI", 9)).pack(side="right", padx=2)

        # ■ STOP
        self._btn(btns, "■", lambda n=name, c=ctrl: self._stop(c, n),
                  C_RED_DIM, w=28, text_color=C_RED, h=24).pack(side="right", padx=2)

        # Login
        self._btn(btns, "Login", lambda n=name, c=ctrl: self._login(c, n),
                  "#2a1a00", w=50, text_color=C_YELLOW, h=24).pack(side="right", padx=2)

        # Nav
        self._btn(btns, "Nav", lambda n=name, c=ctrl: self._nav(c, n),
                  C_BLUE_DIM, w=40, text_color=C_BLUE, h=24).pack(side="right", padx=2)

        # 🗑 Carrito — boton separado, NO parte del ataque
        self._btn(btns, "🗑", lambda n=name, c=ctrl: self._limpiar_carrito(c, n),
                  C_ORANGE_DIM, w=30, text_color=C_ORANGE, h=24).pack(side="right", padx=2)

        # ▶ PLAY — toggle pause/resume
        btn_play = self._btn(
            btns, "▶ Play",
            lambda n=name, c=ctrl, s=acc.sku: self._play(c, n, s),
            C_GREEN_DIM, w=68, text_color=C_GREEN,
            font=("Segoe UI Semibold", 10), h=24
        )
        btn_play.pack(side="right", padx=2)

        # Edit
        self._btn(btns, "Edit", lambda a=acc, n=name: self._edit(a, n),
                  C_GRAY, w=40, h=24).pack(side="right", padx=2)

        self.rows[name] = {
            "row": row, "dot": dot, "name": lbl_name,
            "port": lbl_port, "sku": lbl_sku, "status": lbl_status,
            "btn_play": btn_play, "controller": ctrl, "bg": bg,
        }

    # =========================================================================
    # ACCIONES
    # =========================================================================

    def _play(self, ctrl, name, sku):
        """
        Si hay ataque en curso → toggle pause/resume (cambia icono).
        Si no hay ataque → iniciar nuevo.
        """
        cfg_path = os.path.join("auth", name, "config.json")
        try:
            with open(cfg_path, encoding="utf-8") as f:
                cfg = json.load(f)
            skus = [s for s in cfg.get("skus", []) if s]
            sku  = skus[0] if skus else cfg.get("sku") or sku
        except Exception:
            pass

        if not sku:
            self._log(f"[UI] ERROR: Sin SKU — {name}")
            return

        email = self._get_full_email(name)
        label = f"{name}" + (f" ({email})" if email else "")

        if ctrl.is_attacking:
            # Toggle pause/resume
            is_paused = not ctrl._pause_event.is_set()
            if is_paused:
                self._log(f"[UI] RESUME: {label}")
            else:
                self._log(f"[UI] PAUSE: {label}")
            ctrl.handle_btn_play_hybrid(sku)
            # Actualizar icono del boton
            btn = self.rows.get(name, {}).get("btn_play")
            if btn:
                if is_paused:
                    btn.configure(text="▶ Play")
                else:
                    btn.configure(text="⏸ Pause")
        else:
            self._log(f"[UI] PLAY: {label} SKU={sku}")
            # Cambiar boton a Pause
            btn = self.rows.get(name, {}).get("btn_play")
            if btn:
                btn.configure(text="⏸ Pause")
            threading.Thread(
                target=ctrl.handle_btn_play_hybrid,
                args=(sku,),
                daemon=True,
                name=f"play-{name}"
            ).start()

    def _nav(self, ctrl, name):
        email = self._get_full_email(name)
        self._log(f"[UI] NAV: {name}" + (f" ({email})" if email else ""))

        def do():
            ctrl.handle_btn_launch_browser()
            self.root.after(0, lambda: self._refresh_row(name))

        threading.Thread(target=do, daemon=True, name=f"nav-{name}").start()

    def _login(self, ctrl, name):
        email = self._get_full_email(name)
        self._log(f"[UI] LOGIN: {name}" + (f" ({email})" if email else ""))
        import subprocess, sys
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            runner = os.path.join(script_dir, "..", "scripts", "auth", "login_runner.py")
            proc = subprocess.Popen([sys.executable, runner, name])

            def monitor():
                proc.wait()
                if os.path.exists(os.path.join("auth", name, ".login_ok")):
                    ctrl.state = BotAccountState.READY
                    self._log(f"[UI] {name}: READY")
                self.root.after(0, lambda: self._refresh_row(name))

            threading.Thread(target=monitor, daemon=True).start()
        except Exception as e:
            self._log(f"[UI] ERROR login {name}: {e}")

    def _stop(self, ctrl, name):
        """Stop real — detiene el worker completamente."""
        self._log(f"[UI] STOP: {name}")
        ctrl.stop_worker()
        # Restaurar boton a Play
        btn = self.rows.get(name, {}).get("btn_play")
        if btn:
            btn.configure(text="▶ Play")

    def _limpiar_carrito(self, ctrl, name):
        """
        FIX v2.1:
        - Limpia el carrito via API
        - Navega a /#/cart para refrescar visualmente la pagina
        - Actualiza la fila en la UI
        """
        self._log(f"[UI] Limpiando carrito: {name}")

        def do():
            resultado = ctrl.limpiar_carrito()
            ok = resultado in ("CLEARED", "EMPTY", True)
            msg = f"[UI] {'OK' if ok else 'ERROR'} Carrito: {name} -> {resultado}"
            self.root.after(0, lambda: self._log(msg))

            if ok:
                # Navegar a /#/cart para que Chrome refleje el cambio
                try:
                    import urllib.request as _urlreq
                    import json as _json
                    with _urlreq.urlopen(
                        f"http://127.0.0.1:{ctrl.cdp_port}/json", timeout=2
                    ) as r:
                        tabs = _json.loads(r.read())
                    tab = next((t for t in tabs if t.get("type") == "page"
                                and "webSocketDebuggerUrl" in t), None)
                    if tab:
                        import websocket as _ws
                        ws = _ws.create_connection(tab["webSocketDebuggerUrl"], timeout=3)
                        ws.send(_json.dumps({
                            "id": 99,
                            "method": "Page.navigate",
                            "params": {"url": "https://www.nike.cl/checkout/#/cart"}
                        }))
                        import time as _time
                        _time.sleep(1.5)
                        ws.send(_json.dumps({
                            "id": 100,
                            "method": "Page.navigate",
                            "params": {"url": "https://www.nike.cl/checkout/#/payment"}
                        }))
                        ws.close()
                        self.root.after(0, lambda: self._log(f"[UI] Carrito refrescado: {name}"))
                except Exception as e:
                    err_msg = f"[UI] Nav post-clear: {e}"
                    self.root.after(0, lambda m=err_msg: self._log(m))

            self.root.after(0, lambda: self._refresh_row(name))

        threading.Thread(target=do, daemon=True, name=f"cart-{name}").start()

    def _check_session(self, ctrl, name):
        """Verifica sesion real via CDP para una cuenta."""
        self._log(f"[UI] Verificando sesion: {name}")

        def do():
            ok = ctrl.check_session()

            def update():
                if name in self.rows:
                    r = self.rows[name]
                    if ok:
                        # Mostrar email en la columna cuenta
                        email = self._get_full_email(name)
                        display = email.split("@")[0] if email else name
                        r["name"].configure(text=display, text_color=C_GREEN)
                        r["dot"].configure(text_color=C_GREEN)
                        r["status"].configure(text="Listo para PLAY", text_color=C_GREEN)
                        self._log(f"[UI] {name} ({email}): READY")
                    else:
                        r["name"].configure(text=self._get_display_name(name),
                                           text_color=C_TEXT)
                        r["dot"].configure(text_color=C_RED)
                        r["status"].configure(text="No logueado", text_color=C_TEXT_DIM)
                        self._log(f"[UI] {name}: NO_AUTH")

            self.root.after(0, update)

        threading.Thread(target=do, daemon=True, name=f"check-{name}").start()

    def _edit(self, acc, name):
        ctrl = self.controllers.get(name)
        port = ctrl.cdp_port if ctrl else 0
        AccountEditor(self.root, acc, manager=self.manager, cdp_port=port)
        self.root.after(800, lambda: self._refresh_row(name))

    def _run_all(self):
        self._log("[UI] Run All READY...")
        for name, ctrl in self.controllers.items():
            if ctrl.state == BotAccountState.READY:
                acc = self.manager.accounts.get(name)
                if acc and getattr(acc, "sku", None):
                    self._play(ctrl, name, acc.sku)

    def _stop_all(self):
        self._log("[UI] STOP ALL")
        for name, ctrl in self.controllers.items():
            ctrl.stop_worker()
            btn = self.rows.get(name, {}).get("btn_play")
            if btn:
                btn.configure(text="▶ Play")

    def _check_all_sessions(self):
        """Verifica sesión — si Chrome está abierto lee email real, si no lee disco."""
        if not self.controllers:
            return
        self._log("[UI] Verificando sesiones...")
        for name, ctrl in self.controllers.items():
            def do(n=name, c=ctrl):
                # Intentar leer email real via CDP si Chrome está abierto
                if c._puerto_ocupado():
                    try:
                        ok = c.check_session()
                    except Exception:
                        ok = False
                    if ok:
                        self.root.after(0, lambda nm=n: self._verificar_sesion_disco(nm))
                        return
                # Fallback: leer .login_ok del disco
                self.root.after(0, lambda nm=n: self._verificar_sesion_disco(nm))
            threading.Thread(target=do, daemon=True, name=f"chk-{name}").start()

    def _apply_concurrency(self):
        raw = self.var_concurrent.get().strip()
        if raw.isdigit():
            self._log(f"[UI] Concurrencia: {raw}")

    # =========================================================================
    # ESTADOS VISUALES
    # =========================================================================

    def _set_state(self, name: str, state: str):
        """
        Actualiza visual de la fila.

        Estados:
          playing  → amarillo  "Ejecutando..."
          done     → verde     "Completado ✓"   (solo cuando EV4 confirma)
          failed   → rojo      "Fallo ✗"
          stopped  → rojo dim  "Pausado"
          ready    → verde     "Listo para PLAY"
          checking → azul      "Verificando..."
        """
        if name not in self.rows:
            return
        r = self.rows[name]

        configs = {
            "playing":    (C_YELLOW, C_YELLOW_DIM, "Ejecutando..."),
            "done":       (C_GREEN,  C_GREEN_DIM,  "Completado"),
            "failed":     (C_RED,    C_RED_DIM,    "Fallo"),
            "stopped":    (C_RED,    r["bg"],      "Pausado"),
            "ready":      (C_GREEN,  r["bg"],      "Listo para PLAY"),
            "checking":   (C_BLUE,   C_BLUE_DIM,   "Verificando..."),
            "monitoring": (C_YELLOW, C_YELLOW_DIM, "Monitoreando..."),
        }
        dot_c, row_c, txt = configs.get(state, (C_TEXT_DIM, r["bg"], state))

        try:
            r["dot"].configure(text_color=dot_c)
            r["status"].configure(text=txt, text_color=dot_c)
            r["row"].configure(fg_color=row_c)
        except Exception:
            pass

        # Si termino (done/failed/stopped), restaurar boton a Play
        if state in ("done", "failed", "stopped", "ready"):
            btn = r.get("btn_play")
            if btn:
                btn.configure(text="▶ Play")

    def _refresh_row(self, name: str):
        if name not in self.rows:
            return
        r    = self.rows[name]
        ctrl = r["controller"]
        is_ready = ctrl.state == BotAccountState.READY

        try:
            r["dot"].configure(text_color=C_GREEN if is_ready else C_RED)
            r["name"].configure(text=self._get_display_name(name))
            r["status"].configure(
                text=ctrl.get_status_text(),
                text_color=C_GREEN if is_ready else C_TEXT_DIM
            )
            r["row"].configure(fg_color=r["bg"])

            cfg_path = os.path.join("auth", name, "config.json")
            try:
                with open(cfg_path, encoding="utf-8") as f:
                    cfg = json.load(f)
                sku = cfg.get("sku") or (cfg.get("skus", [None])[0])
                r["sku"].configure(
                    text=sku or "—",
                    text_color=C_GREEN if sku else C_TEXT_DIM
                )
            except Exception:
                pass
        except Exception:
            pass

    # =========================================================================
    # LIMPIAR RASTRO
    # =========================================================================

    def _limpiar_rastro_todas(self):
        """Limpia rastro bot y descuentos en todas las cuentas con Chrome abierto."""
        self._log("[UI] 🧹 Limpiando rastro en todas las cuentas...")
        for name, ctrl in self.controllers.items():
            def do(n=name, c=ctrl):
                self._limpiar_rastro_cuenta(n, c)
            threading.Thread(target=do, daemon=True, name=f"rastro-{name}").start()

    def _limpiar_rastro_cuenta(self, name: str, ctrl):
        """Limpia rastro y descuentos en una cuenta específica."""
        from engines.limpiar_rastro import js_limpiar_rastro, js_limpiar_descuentos

        # Verificar que Chrome está abierto
        if not ctrl._puerto_esta_ocupado():
            return  # Chrome cerrado — skip silencioso

        tab_url = ctrl._get_ws_url()
        if not tab_url:
            self._log(f"[{name}] Sin tab disponible — skip")
            return

        try:
            import websocket
            ws = websocket.create_connection(tab_url, timeout=5)
            ws.send(json.dumps({"id": 0, "method": "Runtime.enable", "params": {}}))

            # Paso 1: Limpiar rastro de tracking
            ws.send(json.dumps({
                "id": 90,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": js_limpiar_rastro(),
                    "awaitPromise": False,
                }
            }))
            time.sleep(0.5)

            # Paso 2: Eliminar descuentos VTEX
            ws.send(json.dumps({
                "id": 91,
                "method": "Runtime.evaluate",
                "params": {
                    "expression":   js_limpiar_descuentos(),
                    "awaitPromise": True,
                    "timeout":      12000,
                }
            }))

            deadline = time.time() + 14
            resultado = ""
            while time.time() < deadline:
                try:
                    ws.settimeout(0.5)
                    msg = json.loads(ws.recv())
                    if msg.get("id") == 91:
                        resultado = msg.get("result", {}).get("result", {}).get("value", "") or ""
                        break
                except Exception:
                    continue

            ws.close()

            if resultado.startswith("OK:"):
                parts = resultado.split(":")
                total = int(parts[1]) if len(parts) > 1 else 0
                desc  = parts[2] if len(parts) > 2 else "?"
                if total < 1000:
                    self._log(f"[{name}] ⚠️ Total ${total} — descuento persistente (cuenta marcada)")
                else:
                    total_fmt = f"${total:,}".replace(",", ".")
                    self._log(f"[{name}] ✅ Limpio — Total {total_fmt} | Descuentos restantes: {desc}")
            else:
                self._log(f"[{name}] ⚠️ {resultado or 'Sin respuesta'}")

        except Exception as e:
            self._log(f"[{name}] Error limpiar rastro: {e}")

    # =========================================================================
    # LOGS
    # =========================================================================

    def _log(self, msg: str):
        self._log_buffer.append(msg)
        # No printear aqui — el controller ya printea a terminal
        # Solo agregar al buffer de la UI

    def _refresh_loop(self):
        """Actualiza el log_box cada 300ms con el contenido del buffer."""
        try:
            lines = list(self._log_buffer)[-100:]
            text  = "\n".join(lines)
            self.log_box.configure(state="normal")
            current = self.log_box.get("1.0", "end-1c")
            if current != text:
                self.log_box.delete("1.0", "end")
                self.log_box.insert("end", text)
                self.log_box.see("end")
            self.log_box.configure(state="disabled")
        except Exception:
            pass
        self.root.after(300, self._refresh_loop)

    def _clear_logs(self):
        self._log_buffer.clear()
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def run(self):
        self.root.mainloop()

