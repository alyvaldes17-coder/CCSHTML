#!/usr/bin/env python3
"""
EJEMPLO COMPLETO: Uso del Motor Definitivo
Demuestra cómo usar el flujo automático de 5 pasos.
"""

import sys
import os
import time

# Agregar ruta al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from runtime.bot_controller import BotController
from engines.dirty_tools import spawn_zombie_chrome, kill_zombie_chrome

print("\n" + "="*70)
print("EJEMPLO: Motor Definitivo (Hybrid Assassin + Rematador)")
print("="*70)

# ================================================================
# CONFIGURACION
# ================================================================
ACCOUNT_NAME = "cuenta2"
PORT = 9223
SKU_PRUEBA = "DQ8426100"  # Puedes cambiar esto por otro SKU

print(f"""
Configuración:
  - Cuenta: {ACCOUNT_NAME}
  - Puerto CDP: {PORT}
  - SKU a probar: {SKU_PRUEBA}
""")

# ================================================================
# PASO 1: CREAR CONTROLADOR
# ================================================================
print("\n[PASO 1] Inicializando BotController...")
try:
    controller = BotController(ACCOUNT_NAME)
    print(f"[OK] BotController listo para {ACCOUNT_NAME}")
except Exception as e:
    print(f"[ERROR] No se pudo crear BotController: {e}")
    sys.exit(1)

# ================================================================
# PASO 2: ABRIR CHROME (OPCIONAL - si no está abierto)
# ================================================================
print(f"\n[PASO 2] Chrome debe estar abierto en puerto {PORT}...")
print(f"  Instrucciones:")
print(f"    1. Abre una terminal")
print(f"    2. Ejecuta: chrome --user-data-dir=C:\\...\\profile_login --remote-debugging-port={PORT}")
print(f"    3. Loguéate en Nike manualmente")
print(f"    4. Regresa aquí y presiona ENTER")

try:
    input("\nPresiona ENTER cuando Chrome esté listo...")
except KeyboardInterrupt:
    print("\n[CANCELADO por usuario]")
    sys.exit(0)

# ================================================================
# PASO 3: EJECUTAR EL MOTOR DEFINITIVO
# ================================================================
print(f"\n[PASO 3] Ejecutando Motor Definitivo...")
print(f"  SKU: {SKU_PRUEBA}")
print(f"  Puerto: {PORT}")
print("\n  El flujo es:")
print("    1. Conectar Chrome (CDP)")
print("    2. Robar Cookies")
print("    3. Backend ATC")
print("    4. Frontend Navigation")
print("    5. Clicks Finales (Rematador)")
print("\n" + "-"*70)

try:
    resultado = controller.ataque_hibrido(PORT, SKU_PRUEBA)
    print("-"*70)
    
    if resultado:
        print(f"\n[EXITO] Motor completado exitosamente!")
        print(f"  Tu navegador debería mostrar la pantalla de pago.")
        print(f"  Status: Listo para ingresar clave del banco")
    else:
        print(f"\n[FALLO] El motor no completó exitosamente.")
        print(f"  Verifica que:")
        print(f"    - Chrome está abierto en puerto {PORT}")
        print(f"    - El usuario está loguado en Nike")
        print(f"    - El SKU {SKU_PRUEBA} existe y es válido")

except KeyboardInterrupt:
    print("\n\n[CANCELADO por usuario]")
    
except Exception as e:
    print(f"\n[ERROR] Excepción durante el ataque: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("FIN DEL EJEMPLO")
print("="*70 + "\n")
