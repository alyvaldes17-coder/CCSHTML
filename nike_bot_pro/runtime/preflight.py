"""
runtime/preflight.py - PRE-FLIGHT FINAL v1.0

Valida SOLO y SOLO esto:
✅ .login_ok existe
✅ profile_login/ existe  
✅ Clone profile_login → profile_run funciona
✅ Chrome ejecutable existe
✅ SKU válido

Si cualquiera falla → ABORT. Sin intentos, sin correcciones.

REGLAS:
- PRE-FLIGHT no toca red
- PRE-FLIGHT no abre Chrome
- PRE-FLIGHT no valida cookies
- PRE-FLIGHT no arregla nada
- Si falla → abortas
- Si pasa → ejecutas sin pensar
"""
import os
import shutil


def preflight(account_path: str, sku: str, chrome_path: str) -> tuple[bool, str]:
    r"""
    Valida precondiciones para PLAY.
    
    Args:
        account_path: Path absoluto a auth/cuenta (ej: C:\Users\...\auth\cuenta2)
        sku: SKU a comprar (debe ser válido/no-vacío)
        chrome_path: Path a chrome.exe
    
    Returns:
        (success, reason)
        - (True, "OK") si todas las validaciones pasan
        - (False, reason) si alguna falla
    
    Raises:
        Nunca. Siempre retorna tupla.
    """
    
    # 1) .login_ok existe
    login_ok = os.path.join(account_path, ".login_ok")
    if not os.path.exists(login_ok):
        return False, "NO_LOGIN_OK"
    
    # 2) profile_login/ existe
    profile_login = os.path.join(account_path, "profile_login")
    if not os.path.isdir(profile_login):
        return False, "PROFILE_LOGIN_MISSING"
    
    # 3) Clone profile_login → profile_run
    profile_run = os.path.join(account_path, "profile_run")
    try:
        if os.path.exists(profile_run):
            shutil.rmtree(profile_run)
        
        shutil.copytree(
            profile_login,
            profile_run,
            ignore=shutil.ignore_patterns(
                "Cache", "Code Cache", "Crashpad",
                "ShaderCache", "GrShaderCache",
                "Dictionaries", "hyphen-data"
            )
        )
    except Exception as e:
        return False, f"CLONE_FAIL: {str(e)}"
    
    # 4) Chrome ejecutable existe
    if not os.path.isfile(chrome_path):
        return False, "CHROME_NOT_FOUND"
    
    # 5) SKU válido
    if not sku or not str(sku).strip():
        return False, "SKU_INVALID"
    
    # ✅ PREFLIGHT OK
    return True, "OK"
