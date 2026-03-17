#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🔥 SETUP RÁPIDO: Loguear N cuentas en paralelo

Abre TODOS los Chrome simultáneamente para que loguees en TODOS a la vez.
Mucho más eficiente que uno por uno.

Uso:
    python setup_cuentas_paralelo.py
    
Loguea en todos, presiona ENTER. Listo para drops.
"""

from runtime.bot_controller import BotController
import threading

NUM_CUENTAS = 10  # Cambiar si quieres menos

print(f"\n{'='*70}")
print(f"🔥 SETUP: Loguando {NUM_CUENTAS} cuentas en PARALELO")
print(f"{'='*70}\n")

CUENTAS = [f"cuenta{i}" for i in range(2, 2 + NUM_CUENTAS)]
controllers = {}
threads = []
lock = threading.Lock()

for i, cuenta in enumerate(CUENTAS, 1):
    controller = BotController(cuenta)
    controllers[cuenta] = controller
    puerto = 9222 + int(cuenta.replace("cuenta", ""))
    
    def abrir(c_name, c_ctrl, p, pos):
        try:
            with lock:
                print(f"[{pos:2}] [{c_name:12}] Abriendo puerto {p}...")
            c_ctrl.handle_btn_launch_browser()
            with lock:
                print(f"[{pos:2}] [{c_name:12}] ✅ Listo para loguear")
        except Exception as e:
            with lock:
                print(f"[{pos:2}] [{c_name:12}] ❌ {e}")
    
    t = threading.Thread(target=abrir, args=(cuenta, controller, puerto, i), daemon=True)
    t.start()
    threads.append(t)

for t in threads:
    t.join(timeout=15)

print(f"\n{'='*70}")
print(f"📝 Loguea en cada Chrome (puertos 9224-9233)")
print(f"💡 Puedes loguear todos simultáneamente")
print(f"{'='*70}\n")

input("⏳ ENTER cuando loguees todos: ")

print(f"\n✅ LISTO para drops!\nEjecuta: python multi_drops.py\n")
