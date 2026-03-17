#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🔥 MULTI-DROPS FLEXIBLE - Especifica cuántas cuentas usar

Puedes ejecutar con:
    python drops_flexible.py 2    # Solo cuenta2 y cuenta3
    python drops_flexible.py 3    # cuenta2, cuenta3 y cuenta4
    python drops_flexible.py 5    # 5 cuentas
    python drops_flexible.py 10   # 10 cuentas

Escalable: Empieza con 2, luego 3, luego las que necesites.
Sin esperar a tener todas loguadas.
"""

from runtime.bot_controller import BotController
import threading
import time
import sys

# Por defecto: 2 cuentas
NUM_CUENTAS = int(sys.argv[1]) if len(sys.argv) > 1 else 2
SKU = "168447"

print(f"\n{'='*70}")
print(f"🔥 NIKE DROPS - {NUM_CUENTAS} CUENTAS EN PARALELO")
print(f"{'='*70}\n")

CUENTAS = [f"cuenta{i}" for i in range(2, 2 + NUM_CUENTAS)]
print(f"Cuentas: {', '.join(CUENTAS)}\n")

# ==========================================
# STEP 1: ABRIR CHROME
# ==========================================
print(f"Abriendo {NUM_CUENTAS} Chrome en paralelo...\n")

controllers = {}
threads = []
lock = threading.Lock()

for i, cuenta in enumerate(CUENTAS, 1):
    controller = BotController(cuenta)
    controllers[cuenta] = controller
    puerto = 9222 + int(cuenta.replace("cuenta", ""))
    
    def abrir_nav(c_name, c_controller, puerto_num, posicion):
        try:
            with lock:
                print(f"[{posicion}] [{c_name}] Abriendo puerto {puerto_num}...")
            c_controller.handle_btn_launch_browser()
            with lock:
                print(f"[{posicion}] [{c_name}] ✅ Listo")
        except Exception as e:
            with lock:
                print(f"[{posicion}] [{c_name}] ❌ {e}")
    
    t = threading.Thread(
        target=abrir_nav,
        args=(cuenta, controller, puerto, i),
        daemon=True
    )
    t.start()
    threads.append(t)

for t in threads:
    t.join(timeout=15)

print(f"\n✅ Todos abiertos\n")
input("⏳ Presiona ENTER cuando loguees todos: ")

# ==========================================
# STEP 2: ATACAR
# ==========================================
print(f"\n🔥 ATACANDO {NUM_CUENTAS} CUENTAS EN PARALELO...\n")

threads = []
resultados = {}

for cuenta in CUENTAS:
    def atacar(c_name, c_controller, c_sku):
        try:
            c_controller.handle_btn_play_hybrid(c_sku)
            resultados[c_name] = "OK"
        except Exception as e:
            resultados[c_name] = f"ERROR: {e}"
    
    t = threading.Thread(
        target=atacar,
        args=(cuenta, controllers[cuenta], SKU),
        daemon=True
    )
    t.start()
    threads.append(t)

print(f"⏳ Esperando {NUM_CUENTAS} ataques (máx 20s)...\n")
time.sleep(20)

print(f"\n{'='*70}")
print(f"📊 RESULTADOS")
print(f"{'='*70}\n")

ok_count = sum(1 for v in resultados.values() if v == "OK")
for cuenta in CUENTAS:
    status = resultados.get(cuenta, "EN PROGRESO")
    emoji = "✅" if status == "OK" else "⏳" if status == "EN PROGRESO" else "❌"
    print(f"{emoji} [{cuenta}] {status}")

print(f"\n{'='*70}")
print(f"✅ {ok_count}/{NUM_CUENTAS} completadas\n")

if ok_count == NUM_CUENTAS:
    print(f"🎯 Revisa los Chrome - ¿Ves {NUM_CUENTAS} pantallas de pago?\n")
    print(f"💡 Próximas ejecuciones:")
    print(f"   python drops_flexible.py 3   (para 3 cuentas)")
    print(f"   python drops_flexible.py 5   (para 5 cuentas)")
    print(f"   python drops_flexible.py 10  (para 10 cuentas)\n")
