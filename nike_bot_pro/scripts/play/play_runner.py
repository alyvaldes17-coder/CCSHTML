#!/usr/bin/env python3
"""
play_runner.py - PRE-FLIGHT CHECK antes del drop

REGLA: Bloquear si Nike no reconoce sesion

FLUJO:
1. Clone (MASTER -> RUN)
2. Preflight (sesion valida?)
   - GET /mi-cuenta headless
   - Verificar "Hola" visible
   - Si NO -> bloquear PLAY
3. Backend + ATC (aqui va tu logica de drop)
4. Handover humano
"""
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# Import del modulo anterior
sys.path.insert(0, str(Path(__file__).parent))
from profile_manager_v2 import clone_auth_to_run


def preflight(profile_run: str) -> bool:
    """
    Verificacion pre-flight (headless)
    
    Returns:
        True si Nike reconoce sesion
        False si error o sesion invalida
    """
    try:
        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=profile_run,
                channel="chrome",
                headless=True,
                viewport={"width": 1280, "height": 720}
            )
            
            page = ctx.new_page()
            page.goto("https://www.nike.cl/mi-cuenta", timeout=30000)
            
            # Verificar sesion (buscar "Hola")
            try:
                hello = page.locator("text=Hola").first
                ok = hello.is_visible(timeout=5000)
            except:
                ok = False
            
            ctx.close()
            return ok
            
    except Exception as e:
        print(f"[PREFLIGHT] [ERROR] {type(e).__name__}: {e}")
        return False


def run_drop(user: str):
    """
    Ejecutar drop completo
    
    FLUJO:
    1. Clone
    2. Preflight
    3. Backend (aca va tu logica)
    4. Handover humano
    """
    base = os.path.abspath(f"auth/{user}")
    profile_run = os.path.join(base, "profile_run")
    
    print("\n" + "="*70)
    print(f"[PLAY] [{user}] Iniciando drop")
    print("="*70)
    
    # STEP 1: Clone
    print(f"[PLAY] [{user}] Step 1: Clonando perfil...")
    if not clone_auth_to_run(user):
        print(f"[PLAY] [{user}] [BLOCKED] Clone fallido")
        return
    
    # STEP 2: Preflight
    print(f"[PLAY] [{user}] Step 2: Verificando sesion (headless)...")
    if not preflight(profile_run):
        print(f"[PLAY] [{user}] [BLOCKED] Sesion invalida")
        print(f"[PLAY] [{user}] Ejecuta: python login_runner.py {user}")
        return
    
    print(f"[PLAY] [{user}] [OK] Sesion valida -> DROP AUTORIZADO")
    
    # STEP 3: Backend (tu logica aqui)
    # TODO: backend rapido + ATC + pricing lock
    
    # STEP 4: Handover humano
    print(f"[PLAY] [{user}] Step 3: Handover humano (visible)")
    
    try:
        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=profile_run,
                channel="chrome",
                headless=False,
                viewport=None,
                args=["--start-maximized"]
            )
            
            page = ctx.new_page()
            # Magic link ATC
            # page.goto(f"https://www.nike.cl/checkout/cart/add?sku=<SKU>&qty=1")
            page.goto("https://www.nike.cl", timeout=30000)
            
            print(f"[PLAY] [{user}] Esperando handover humano...")
            print(f"[PLAY] [{user}] Presiona ENTER cuando termines")
            input()
            
            ctx.close()
            
    except Exception as e:
        print(f"[PLAY] [{user}] [ERROR] {type(e).__name__}: {e}")
    
    print(f"[PLAY] [{user}] [DONE] Drop completado\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python play_runner.py <user>")
        sys.exit(1)
    
    user = sys.argv[1]
    run_drop(user)
