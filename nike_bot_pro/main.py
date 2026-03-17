import sys
import os

from manager.account_manager import AccountManager
from ui.app import AppUI

# ── MODO DESARROLLO ──────────────────────────────────────────────────────────
# True  = tu PC, python main.py → sin validacion, acceso total
# False = .exe del cliente → necesita key, limitado por plan
# build.py cambia esto a False automaticamente al compilar
DEV_MODE = True


def mostrar_splash_licencia(info: dict):
    """Muestra info de licencia en terminal antes de abrir la UI."""
    plan          = info.get("plan", "?").upper()
    cliente       = info.get("cliente", "?")
    dias          = info.get("dias_restantes", 0)
    cuentas_max   = info.get("cuentas_max", 3)
    expira        = info.get("expira", "?")

    print(f"\n{'='*55}")
    print(f"  NIKE BOT PRO — Licencia activa")
    print(f"{'='*55}")
    print(f"  Cliente:  {cliente}")
    print(f"  Plan:     {plan} ({cuentas_max} cuentas)")
    print(f"  Expira:   {expira} ({dias} dias restantes)")
    if dias <= 5:
        print(f"  !! LICENCIA PROXIMA A EXPIRAR — contacta al proveedor")
    print(f"{'='*55}\n")


def mostrar_error_licencia(error: str):
    """Muestra error de licencia en ventana grafica."""
    try:
        import customtkinter as ctk

        ctk.set_appearance_mode("dark")
        root = ctk.CTk()
        root.title("Nike Bot Pro — Error de licencia")
        root.geometry("420x220")
        root.resizable(False, False)

        ctk.CTkLabel(
            root,
            text="Licencia invalida",
            font=("Segoe UI Semibold", 16),
            text_color="#ff1744"
        ).pack(pady=(30, 8))

        ctk.CTkLabel(
            root,
            text=error,
            font=("Segoe UI", 12),
            text_color="#888888"
        ).pack(pady=4)

        ctk.CTkLabel(
            root,
            text="Contacta a @nikebotpro_cl para renovar",
            font=("Segoe UI", 11),
            text_color="#555555"
        ).pack(pady=8)

        ctk.CTkButton(
            root, text="Cerrar", command=root.destroy,
            fg_color="#2e0010", hover_color="#3d0015",
            text_color="#ff1744", width=120
        ).pack(pady=12)

        root.mainloop()
    except Exception:
        print(f"\nError de licencia: {error}")
        print("Contacta a @nikebotpro_cl para renovar\n")


def main():
    # ── 1. VALIDAR LICENCIA ──────────────────────────────────────────────────
    if DEV_MODE:
        # Tu PC — acceso total, sin validacion
        print("[DEV] Modo desarrollo — sin validacion de licencia")
        ok   = True
        info = {"plan": "full", "cuentas_max": 99, "cliente": "DEV", "dias_restantes": 999, "expira": "N/A"}
    else:
        # .exe del cliente — validar contra GitHub Gist
        try:
            from licensing.license_manager import LicenseValidator, PLANES
            ok, info = LicenseValidator.validar()
        except ImportError:
            ok   = False
            info = {"error": "Modulo de licencias no disponible"}

        if not ok:
            error = info.get("error", "Licencia invalida")
            mostrar_error_licencia(error)
            sys.exit(1)

        mostrar_splash_licencia(info)

    # ── 2. CARGAR MANAGER ───────────────────────────────────────────────────
    manager = AccountManager()
    manager.load_accounts()

    # Limitar cuentas segun el plan (solo para clientes)
    if not DEV_MODE:
        cuentas_max = info.get("cuentas_max", PLANES.get(info.get("plan", "basic"), {}).get("cuentas", 3))
        if cuentas_max < 99:
            cuentas_disponibles = list(manager.accounts.keys())[:cuentas_max]
            manager.accounts = {
                k: v for k, v in manager.accounts.items()
                if k in cuentas_disponibles
            }
            print(f"[Licencia] Plan {info['plan'].upper()} — {len(manager.accounts)} cuentas activas")

    # ── 3. LANZAR UI ────────────────────────────────────────────────────────
    app = AppUI(manager, None)

    # Mostrar dias restantes en el titulo si quedan pocos (solo clientes)
    if not DEV_MODE and info.get("dias_restantes", 99) <= 5:
        app.root.title(
            f"Nike Bot Pro — Licencia expira en {info['dias_restantes']} dias"
        )

    app.run()


# ════════════════════════════════════════════════════════════════════════════
# ⭐ NUEVO: MODO SATURACIÓN PARA DROPS
# ════════════════════════════════════════════════════════════════════════════

def modo_drop_saturacion_manual(app):
    """
    Modo manual de saturación (sin Franco Tirador)
    Usuario decide cuándo lanzar el ataque
    """
    
    from core.orquestador_saturacion import OrquestadorSaturacion
    
    print(f"\n{'='*70}")
    print(f"🔥 MODO DROP - SATURACIÓN MANUAL")
    print(f"{'='*70}\n")
    
    # 1. Obtener SKU del usuario
    sku = input("Ingresa el SKU del drop: ").strip()
    
    if not sku:
        print("❌ SKU vacío - Abortando")
        return
    
    # 2. Filtrar cuentas READY
    cuentas_ready = [
        controller for controller in app.controllers.values()
        if hasattr(controller, 'state') and controller.state == 'READY'
    ]
    
    print(f"\n✅ Cuentas listas: {len(cuentas_ready)}/{len(app.controllers)}")
    
    if len(cuentas_ready) == 0:
        print("❌ No hay cuentas listas - Primero loguea tus cuentas")
        return
    
    for i, ctrl in enumerate(cuentas_ready, 1):
        account_name = getattr(ctrl, 'account_name', f'Cuenta {i}')
        print(f"   [{i}] {account_name}")
    
    # 3. Confirmar lanzamiento
    print(f"\n⚠️  Se lanzarán {len(cuentas_ready)} cuentas simultáneamente")
    confirmar = input("¿Continuar? (s/n): ").strip().lower()
    
    if confirmar != 's':
        print("❌ Cancelado por usuario")
        return
    
    # 4. Ejecutar saturación
    orquestador = OrquestadorSaturacion(cuentas_ready)
    exito = orquestador.ataque_saturacion(sku)
    
    if exito:
        print("\n✅ Ataque de saturación completado exitosamente")
    else:
        print("\n❌ Ataque falló - Ver logs arriba")


def modo_franco_tirador_auto(app):
    """
    Modo automático con Franco Tirador
    Monitorea stock y lanza saturación cuando detecta disponibilidad
    """
    
    from core.orquestador_saturacion import OrquestadorSaturacion, FrancoTiradorV2
    
    print(f"\n{'='*70}")
    print(f"🎯 MODO FRANCO TIRADOR - AUTOMÁTICO")
    print(f"{'='*70}\n")
    
    # 1. Obtener SKU
    sku = input("Ingresa el SKU a monitorear: ").strip()
    
    if not sku:
        print("❌ SKU vacío - Abortando")
        return
    
    # 2. Intervalo de monitoreo
    print("\nIntervalo de monitoreo:")
    print("  [1] 2 segundos (recomendado - seguro)")
    print("  [2] 1 segundo (agresivo - puede ser detectado)")
    print("  [3] 5 segundos (conservador)")
    
    opcion = input("Selecciona [1-3]: ").strip()
    
    intervalos = {'1': 2, '2': 1, '3': 5}
    interval = intervalos.get(opcion, 2)
    
    # 3. Filtrar cuentas ready
    cuentas_ready = [
        controller for controller in app.controllers.values()
        if hasattr(controller, 'state') and controller.state == 'READY'
    ]
    
    print(f"\n✅ Cuentas listas: {len(cuentas_ready)}/{len(app.controllers)}")
    
    if len(cuentas_ready) == 0:
        print("❌ No hay cuentas listas")
        return
    
    # 4. Callback cuando detecta stock
    def on_stock_detected(sku_detectado):
        print(f"\n🚨 Stock detectado - Lanzando saturación...")
        orquestador = OrquestadorSaturacion(cuentas_ready)
        orquestador.ataque_saturacion(sku_detectado)
    
    # 5. Iniciar Franco Tirador
    franco = FrancoTiradorV2(sku, interval=interval)
    
    try:
        franco.start_monitoring(on_stock_detected)
    except KeyboardInterrupt:
        print("\n⚠️ Detenido por usuario")
        franco.stop()


# ════════════════════════════════════════════════════════════════════════════
# AGREGAR AL MENÚ PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════

def mostrar_menu_drop(app):
    """Menú de opciones para drops"""
    
    print(f"\n{'='*70}")
    print(f"🚀 MENÚ DROP - MODO SATURACIÓN")
    print(f"{'='*70}")
    print("  [1] Saturación Manual (lanzar ahora)")
    print("  [2] Franco Tirador Automático (monitorear y lanzar)")
    print("  [0] Volver")
    print(f"{'='*70}\n")
    
    opcion = input("Selecciona opción: ").strip()
    
    if opcion == '1':
        modo_drop_saturacion_manual(app)
    elif opcion == '2':
        modo_franco_tirador_auto(app)
    elif opcion == '0':
        return
    else:
        print("❌ Opción inválida")


if __name__ == "__main__":
    main()
