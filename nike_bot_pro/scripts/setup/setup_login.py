#!/usr/bin/env python3
"""
setup_login.py - Configuración de LOGIN (ejecutar UNA SOLA VEZ por cuenta)

ARQUITECTURA MASTER/SLAVE:
┌─ MASTER (profile_login) - Usuario loguea manualmente UNA SOLA VEZ
│  └─ Cookies persistentes aquí
│
└─ SLAVE (profile_run) - Clonado automáticamente para cada ejecución bot
   └─ Se descarta después de usar (sin locks)

FLUJO:
1. Este script abre Nike.cl en profile_login
2. TÚ logueas manualmente (email + contraseña)
3. Se guardan cookies en profile_login
4. Cierras Chrome
5. Bot clona cookies automáticamente para ejecutar

SEGURIDAD:
✅ profile_login nunca se corrompe (solo tú logueas)
✅ Bot siempre arranca limpio (clona fresco)
✅ Sin SingletonLock (se limpian automáticamente en slave)

USO:
    python setup_login.py cuenta2
    python setup_login.py cuenta3
    python setup_login.py cuenta_vip
"""
import sys
import subprocess
from pathlib import Path
from profile_manager import ProfileManager


def setup_login_account(account_name: str) -> bool:
    """
    Ejecuta login_runner.py en SUBPROCESS para cuentaX.
    
    IMPORTANTE: Subprocess = proceso independiente
    - No congela la UI
    - Playwright puede abrir Chrome sin problemas
    - Usuario se loguea manualmente
    - Cookies se guardan en auth/cuentaX/profile_login
    
    Args:
        account_name: "cuenta2", "cuenta3", etc
        
    Returns:
        True si completó exitosamente
    """
    print("\n" + "="*70)
    print(f"🔐 SETUP LOGIN: {account_name.upper()}")
    print("="*70)
    print()
    
    # Validar que ProfileManager puede usar esta cuenta
    manager = ProfileManager(account_name)
    login_profile = manager.get_login_profile_path()
    
    print(f"📂 Profile master: {login_profile}")
    print()
    print("INSTRUCCIONES:")
    print("  1. Se abrirá una ventana de Chrome")
    print("  2. Loguéate en Nike.cl con tu email/contraseña")
    print("  3. Cierra la ventana cuando termines")
    print("  4. Las cookies se guardarán automáticamente")
    print()
    print("⏳ Presiona ENTER para continuar...")
    input()
    
    try:
        # Ejecutar login_runner.py en subprocess
        # login_runner.py espera profile_login como argumento
        result = subprocess.run(
            [sys.executable, "login_runner.py", login_profile],
            check=False,  # No lanzar excepción si falla
            text=True,
            cwd=str(Path(__file__).parent)
        )
        
        if result.returncode == 0:
            print()
            print("✅ Login completado exitosamente")
            print(f"✅ Cookies guardadas en: {login_profile}")
            
            # Validar que hay cookies
            if manager.verify_master_profile():
                print("✅ Verificación: Master profile tiene cookies válidas")
                print()
                print(f"🎉 {account_name} está listo para usar con el bot")
                return True
            else:
                print("⚠️ Advertencia: No se detectaron cookies")
                print("❌ Intenta de nuevo")
                return False
        else:
            print()
            print(f"❌ login_runner.py falló con código {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Menú principal para setup de cuentas"""
    if len(sys.argv) < 2:
        print("\n" + "="*70)
        print("SETUP LOGIN - Loguear cuentas Nike")
        print("="*70)
        print()
        print("USO:")
        print("  python setup_login.py <cuenta_name>")
        print()
        print("EJEMPLOS:")
        print("  python setup_login.py cuenta2")
        print("  python setup_login.py cuenta3")
        print("  python setup_login.py cuenta_premium")
        print()
        print("NOTA: Ejecuta UNA SOLA VEZ por cuenta")
        print("      El bot clonará estas cookies automáticamente")
        print()
        return 1
    
    account_name = sys.argv[1]
    
    # Validar formato
    if not account_name or account_name.startswith("-"):
        print(f"❌ Nombre de cuenta inválido: {account_name}")
        return 1
    
    # Ejecutar setup
    success = setup_login_account(account_name)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

