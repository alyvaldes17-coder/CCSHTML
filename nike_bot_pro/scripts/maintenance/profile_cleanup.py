#!/usr/bin/env python3
"""
profile_cleanup.py - Reset suave del perfil (Cache, Code Cache, Service Worker)

USO:
  python profile_cleanup.py cuenta1    # Limpia auth/cuenta1/profile_login
  
ACCIÓN:
  1. Borra Cache
  2. Borra Code Cache
  3. Borra Service Worker
  4. Mantiene: cookies, localStorage, sessionStorage, auth tokens
"""
import os
import sys
import shutil
from pathlib import Path


def cleanup_profile(account_name: str, profile_type: str = "profile_login") -> bool:
    """
    Reset suave de perfil: borra cache pero mantiene datos de sesión
    
    Args:
        account_name: "cuenta1", "cuenta2", etc
        profile_type: "profile_login" (default) o "profile_run"
    
    Returns:
        True si limpieza exitosa, False en error
    """
    profile_path = Path("auth") / account_name / profile_type
    
    if not profile_path.exists():
        print(f"[CLEANUP] ERROR: {profile_path} no existe")
        return False
    
    print(f"\n[CLEANUP] Limpiando {profile_path}")
    print("=" * 70)
    
    # Directorios a borrar (cache, no datos de sesión)
    dirs_to_remove = [
        "Cache",                    # Cache general
        "Code Cache",               # Código cacheado (JavaScript, CSS compilado)
        "Service Worker",           # Service workers
        "Blob_Storage",             # Almacenamiento de blobs (a veces problemático)
    ]
    
    removed_count = 0
    
    for dir_name in dirs_to_remove:
        dir_path = profile_path / "Default" / dir_name
        
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"  [OK] Borrado: {dir_name}/")
                removed_count += 1
            except Exception as e:
                print(f"  [WARN] Error borrando {dir_name}: {e}")
        else:
            print(f"  [SKIP] No existe: {dir_name}/")
    
    # Mantener (NO borrar):
    # - Default/Cookies (auth, sesión)
    # - Default/Local Storage (datos persistentes)
    # - Default/Session Storage (sesión temporal)
    # - Default/Network (config de red)
    
    print("=" * 70)
    print(f"[CLEANUP] Completado: {removed_count} directorios borrados")
    print("[CLEANUP] Mantenidos: Cookies, localStorage, sessionStorage, auth tokens")
    print("\n[NEXT] Abre Chrome y loguéate de nuevo\n")
    
    return True


def cleanup_and_verify(account_name: str) -> bool:
    """
    Limpia y verifica que el perfil esté limpio
    """
    profile_path = Path("auth") / account_name / "profile_login"
    
    # Paso 1: Limpieza
    if not cleanup_profile(account_name, "profile_login"):
        return False
    
    # Paso 2: Verificar que .login_ok se borra también
    # (porque el login falló, hay que rehacer)
    login_ok = profile_path.parent / ".login_ok"
    if login_ok.exists():
        try:
            login_ok.unlink()
            print(f"[CLEANUP] Borrado: .login_ok (requiere re-login)")
        except Exception as e:
            print(f"[CLEANUP] WARN: No se pudo borrar .login_ok: {e}")
    
    print(f"[CLEANUP] ✅ Perfil limpio y listo para login manual")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python profile_cleanup.py <cuenta>")
        print("Ejemplo: python profile_cleanup.py cuenta1")
        sys.exit(1)
    
    account = sys.argv[1]
    cleanup_and_verify(account)
