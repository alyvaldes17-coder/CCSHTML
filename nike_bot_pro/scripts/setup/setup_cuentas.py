#!/usr/bin/env python3
"""
setup_cuentas.py - Inicializar múltiples cuentas

Recorre todas las cuentas definidas y genera su profile_pw
abriendo login_runner.py para cada una.

Uso:
    python setup_cuentas.py
    
    # Verás esto:
    🪖 Inicializando cuentas...
    
    cuenta1: Abriendo Chrome para LOGIN...
    [Espera a que loguees en cuenta1]
    cuenta1: Sesión guardada ✅
    
    cuenta2: Abriendo Chrome para LOGIN...
    [Espera a que loguees en cuenta2]
    cuenta2: Sesión guardada ✅
    
    ... etc para todas las cuentas ...
"""
import os
import sys
import subprocess
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).parent))

from runtime.bot_controller import BotController


# EDITA ESTO CON TUS CUENTAS
CUENTAS_A_INICIALIZAR = [
    "cuenta1",
    "cuenta2",
    "cuenta_hermano",
    "cuenta_mama",
]


def setup_cuentas():
    """
    Inicializa todas las cuentas.
    Para cada una:
    1. Crea carpeta auth/cuenta_X/profile_pw
    2. Abre login_runner.py
    3. Usuario loguea manualmente
    4. Valida que cookies se guardaron
    """
    print("\n" + "="*60)
    print("🪖 INICIALIZADOR DE CUENTAS")
    print("="*60)
    print(f"Inicializando {len(CUENTAS_A_INICIALIZAR)} cuentas...\n")
    
    exitosas = 0
    fallidas = 0
    
    for nombre_cuenta in CUENTAS_A_INICIALIZAR:
        profile_path = os.path.abspath(os.path.join("auth", nombre_cuenta, "profile_pw"))
        
        # Crear carpeta si no existe
        Path(profile_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 Carpeta creada: {profile_path}")
        
        # Crear controller
        try:
            bot = BotController(nombre_cuenta, profile_path)
            print(f"[{nombre_cuenta}] 🎛️ Controller inicializado")
        except Exception as e:
            print(f"[{nombre_cuenta}] ❌ Error creando controller: {e}")
            fallidas += 1
            continue
        
        # Lanzar login en subprocess
        print(f"[{nombre_cuenta}] 🔐 Abriendo Chrome para LOGIN...")
        print(f"[{nombre_cuenta}] 👤 Loguéate en Nike y CIERRA el navegador")
        print(f"[{nombre_cuenta}] ⏳ Esperando...\n")
        
        try:
            # Lanzar login_runner.py como subprocess
            process = subprocess.Popen([
                sys.executable,
                "login_runner.py",
                profile_path
            ])
            
            # Esperar a que se cierre Chrome
            returncode = process.wait()
            
            if returncode == 0:
                print(f"[{nombre_cuenta}] ✅ Chrome cerrado correctamente\n")
            else:
                print(f"[{nombre_cuenta}] ⚠️ Chrome cerró con código {returncode}\n")
        
        except Exception as e:
            print(f"[{nombre_cuenta}] ❌ Error lanzando login: {e}\n")
            fallidas += 1
            continue
        
        # Validar que las cookies se guardaron
        try:
            if bot.validate_session_real():
                print(f"[{nombre_cuenta}] ✅ VALIDACIÓN: Sesión guardada correctamente")
                print(f"[{nombre_cuenta}] 🎖️ Estado: READY\n")
                exitosas += 1
            else:
                print(f"[{nombre_cuenta}] ⚠️ VALIDACIÓN: No se confirmó sesión")
                print(f"[{nombre_cuenta}] 📝 Intenta LOGIN de nuevo en main_army.py\n")
                # No contar como fallida, quizás Nike necesita esperar
        
        except Exception as e:
            print(f"[{nombre_cuenta}] ❌ Error validando: {e}\n")
            fallidas += 1
    
    # Resumen final
    print("="*60)
    print("📊 RESUMEN DE INICIALIZACIÓN")
    print("="*60)
    print(f"Total cuentas:     {len(CUENTAS_A_INICIALIZAR)}")
    print(f"Exitosas:          {exitosas}")
    print(f"Pendientes:        {len(CUENTAS_A_INICIALIZAR) - exitosas - fallidas}")
    print(f"Fallidas:          {fallidas}")
    
    if exitosas == len(CUENTAS_A_INICIALIZAR):
        print(f"\n🟢 ¡EJÉRCITO LISTO! Todas las cuentas inicializadas.")
        print(f"   Ejecuta: python main_army.py")
    else:
        print(f"\n🟡 Algunas cuentas necesitan LOGIN manual.")
        print(f"   Ejecuta: python main_army.py")
        print(f"   Opción 3: LOGIN masivo")
    
    print("="*60)


def listar_cuentas_actuales():
    """Muestra qué cuentas existen actualmente en auth/"""
    auth_path = "auth"
    
    if not os.path.exists(auth_path):
        print("❌ Carpeta auth/ no encontrada")
        return
    
    print("\n📋 CUENTAS EXISTENTES EN auth/:")
    for item in os.listdir(auth_path):
        ruta = os.path.join(auth_path, item)
        if os.path.isdir(ruta) and item != "discord_session" and not item.startswith('.'):
            profile_pw = os.path.join(ruta, "profile_pw")
            if os.path.exists(profile_pw):
                print(f"  ✅ {item} (profile_pw presente)")
            else:
                print(f"  ❌ {item} (profile_pw FALTANTE)")


def main():
    """Menu principal"""
    print("\n" + "="*60)
    print("🪖 SETUP DE EJÉRCITO - CONFIGURAR CUENTAS")
    print("="*60)
    print("1. Listar cuentas actuales en auth/")
    print("2. Inicializar cuentas nuevas")
    print("3. Salir")
    print("="*60)
    
    opcion = input("Elige opción (1-3): ").strip()
    
    if opcion == "1":
        listar_cuentas_actuales()
    
    elif opcion == "2":
        # Mostrar cuentas a inicializar
        print("\n📋 Cuentas a inicializar:")
        for i, cuenta in enumerate(CUENTAS_A_INICIALIZAR, 1):
            print(f"  {i}. {cuenta}")
        
        confirm = input("\n¿Continuar? (s/n): ").strip().lower()
        if confirm == "s":
            setup_cuentas()
    
    elif opcion == "3":
        print("👋 Hasta luego")
    
    else:
        print("❌ Opción inválida")


if __name__ == "__main__":
    # Si se ejecuta con argumentos, hacer setup directo (sin menu)
    if len(sys.argv) > 1:
        if sys.argv[1] == "auto":
            setup_cuentas()
        else:
            print("Uso: python setup_cuentas.py [auto]")
    else:
        main()
