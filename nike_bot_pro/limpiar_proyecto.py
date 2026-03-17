"""
limpiar_proyecto.py v2 — Limpieza COMPLETA Nike Bot Pro
Corre desde nike_bot_pro/: python limpiar_proyecto.py
"""

import os
import shutil
import glob

ARCHIVOS_MUERTOS = [
    # Engines backups/muertos
    "engines/engine_v2_backup.py",
    "engines/engine_v3_backup.py",
    "engines/engine_v4_backup.py",
    "engines/engine_v6_backup.py",
    "engines/engine_v7_backup.py",
    "engines/engine_optimized.py",
    "engines/hybrid_assassin_fusion.py",
    "engines/hybrid_engine_v6.py",
    "engines/franco_tirador.py",
    "engines/deterministic_checkout.py",
    "engines/checkout_orchestrator.py",
    "engines/state_machine_orchestrator.py",
    "engines/request_engine.py",
    "engines/session_bridge.py",
    "engines/manual_login.py",
    "engines/manual_review.py",
    "engines/bank_payment_flow.py",
    "engines/injector.js",
    # Runtime backups/muertos
    "runtime/bot_controller_optimized_v1_backup.py",
    "runtime/bot_controller_optimized.py.bak",
    "runtime/bot_controller_v5_backup.py",
    "runtime/bot_controller_v6_backup.py",
    "runtime/bot_controller_v7_backup.py",
    "runtime/backend_vtex.py",
    "runtime/cascade_manager.py",
    "runtime/chrome_preloader.py",
    "runtime/multiprocessing_runner.py",
    "runtime/process_states.py",
    "runtime/state_bus.py",
    # UI muertos
    "ui/app_v1_backup.py",
    "ui/app_integration_example.py",
    "ui/play_launcher.py",
    "ui/state_listener.py",
    # Utils muertos
    "utils/config.py",
    "utils/config_loader.py",
    "utils/contingency_handler.py",
    "utils/fingerprint_manager.py",
    "utils/master_optimization_suite.py",
    "utils/request_optimizer.py",
    "utils/sku_validator.py",
    "utils/timing_strategies.py",
    "utils/chrome_manager.py",
    "utils/resource_blocker.py",
    "config/system_optimizer.py",
    # Auth muertos
    "auth/auth.py",
    "auth/extract_cookies.py",
    "auth/extraertoken.py",
    "auth/get.py",
    "auth/session_store.py",
    "auth/account_manager.py",
    # VTEX muertos
    "vtex/curl_client.py",
    "vtex/order_form.py",
    # Core muertos
    "core/events.py",
    "core/payment_mode.py",
    "core/bot_state.py",
    # Scripts raíz muertos
    "audit_project.py",
    "fix_engine.py",
    "diagnose_login_issue.py",
    "socket_test_simple.py",
    "validacion_threading_fix_final.py",
    "test_engine_init.py",
    "test_imports_post_fix.py",
    "test_stock_endpoint.py",
    "build.py",
    # Tests (todos muertos)
    "tests/test_account_manager_config.py",
    "tests/test_account_manager.py",
    "tests/test_chrome_port.py",
    "tests/test_circuit_breaker.py",
    "tests/test_conexion_fix.py",
    "tests/test_conexion.py",
    "tests/test_controller_new.py",
    "tests/test_controller.py",
    "tests/test_core.py",
    "tests/test_cuenta2_orderform.py",
    "tests/test_deterministic_flow.py",
    "tests/test_dispatch_and_retry.py",
    "tests/test_manager.py",
    "tests/test_session_validator.py",
    "tests/test_state_machine_flow.py",
    "tests/test_state_machine.py",
    "tests/test_worker_checkout.py",
    "tests/test_worker_price.py",
    "tests/test_worker.py",
]

CARPETAS_MUERTAS = [
    "BACKUP_MOTORES_VIEJOS",
    "runner",
    "tests",
    "experimental",
]

MD_CONSERVAR = {"README.md"}


def main():
    raiz = os.path.dirname(os.path.abspath(__file__))
    print(f"\n{'='*60}")
    print(f"LIMPIEZA COMPLETA — NIKE BOT PRO v2")
    print(f"Raiz: {raiz}")
    print(f"{'='*60}\n")

    existentes = [os.path.join(raiz, f) for f in ARCHIVOS_MUERTOS
                  if os.path.exists(os.path.join(raiz, f))]
    no_encontrados = [f for f in ARCHIVOS_MUERTOS
                      if not os.path.exists(os.path.join(raiz, f))]
    carpetas = [os.path.join(raiz, c) for c in CARPETAS_MUERTAS
                if os.path.exists(os.path.join(raiz, c))]
    mds = [r for r in glob.glob(os.path.join(raiz, "*.md"))
           if os.path.basename(r) not in MD_CONSERVAR]

    print(f"Carpetas ({len(carpetas)}):")
    for c in carpetas:
        print(f"   {os.path.relpath(c, raiz)}/")

    print(f"\n.md raiz ({len(mds)}):")
    for m in sorted(mds):
        print(f"   {os.path.basename(m)}")

    print(f"\nArchivos ({len(existentes)}):")
    for f in existentes:
        print(f"   {os.path.relpath(f, raiz)}")

    if no_encontrados:
        print(f"\nYa borrados ({len(no_encontrados)})")

    total = len(existentes) + len(carpetas) + len(mds)
    if total == 0:
        print("\nProyecto ya limpio.")
        return

    print(f"\n{'='*60}")
    print(f"Total: {total} elementos")
    if input("Borrar todo? [s/N]: ").strip().lower() != "s":
        print("Cancelado.")
        return

    borrados = errores = 0

    for ruta in carpetas:
        try:
            shutil.rmtree(ruta)
            print(f"OK {os.path.relpath(ruta, raiz)}/")
            borrados += 1
        except Exception as e:
            print(f"ERROR {e}"); errores += 1

    for ruta in mds + existentes:
        try:
            os.remove(ruta)
            print(f"OK {os.path.relpath(ruta, raiz)}")
            borrados += 1
        except Exception as e:
            print(f"ERROR {e}"); errores += 1

    print("\nLimpiando __pycache__ y .pyc...")
    for dirpath, dirnames, _ in os.walk(raiz):
        if "env" in dirpath.split(os.sep):
            continue
        for d in dirnames:
            if d == "__pycache__":
                try:
                    shutil.rmtree(os.path.join(dirpath, d))
                except Exception:
                    pass
    for pyc in glob.glob(os.path.join(raiz, "**/*.pyc"), recursive=True):
        try:
            os.remove(pyc)
        except Exception:
            pass

    print(f"\n{'='*60}")
    print(f"Borrados: {borrados} | Errores: {errores}")
    print("Proyecto limpio. Reinicia el bot.\n")


if __name__ == "__main__":
    main()
