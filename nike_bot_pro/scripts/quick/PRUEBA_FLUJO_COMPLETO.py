#!/usr/bin/env python3
"""
Prueba del flujo COMPLETO sin UI
Simula ABRIR NAV + PLAY
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from runtime.bot_controller import BotController
import time
import threading

print("=" * 70)
print("PRUEBA COMPLETA: ABRIR NAV → 3 seg → PLAY")
print("=" * 70)

# Crear controlador
controller = BotController("cuenta2")

print("\n[PASO 1] Presionando ABRIR NAV...")
print("-" * 70)
result = controller.handle_btn_launch_browser()
if not result:
    print("❌ ABRIR NAV falló")
    sys.exit(1)

print("\n[PASO 2] Esperando 2 segundos...")
time.sleep(2)

print("\n[PASO 3] Presionando PLAY...")
print("-" * 70)
controller.handle_btn_play_hybrid("168447")

# ✅ ESPERAR A QUE TERMINEN LOS THREADS
print("\n[PASO 4] Esperando 15 segundos a que el ataque termine...")
time.sleep(15)

print("\n" + "=" * 70)
print("PRUEBA COMPLETADA")
print("=" * 70)
