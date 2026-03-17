#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🔥 MULTI-CUENTA DROPS ESCALABLE - Hasta 10+ Chrome en paralelo

Para Nike drops: 10 cuentas atacando simultáneamente, sin interferencia.
Cada una en su propio puerto (9224, 9225, ..., 9233), con sus propias cookies.

ARQUITECTURA:
- Cada cuenta: BotController("cuentaX")
- Cada puerto: 9222 + numero_de_cuenta (dinámico, no interfiere)
- Cada Chrome: Inmortal y persistente (Opción B)
- Ataque: tls_client blindado contra 403 + warm start cookies

FLUJO:
1. Abre 10 Chrome en paralelo (~3 segundos)
2. Espera a que te loguees en los 10
3. Presiona PLAY → Ataca los 10 en paralelo (~2-3 segundos)

ESCALABLE: Cambia solo la variable CUENTAS para agregar más.
"""

from runtime.bot_controller import BotController
import threading
import time

# ==========================================
# ⚙️ CONFIGURACIÓN
# ==========================================
# Para 10 cuentas, necesitas: cuenta2, cuenta3, ..., cuenta11
CUENTAS = [f"cuenta{i}" for i in range(2, 12)]  # cuenta2 a cuenta11 (10 total)
SKU = "168447"  # ← Cambiar al SKU del drop real

print(f"\n{'='*70}")
print(f"🔥 NIKE DROPS - MULTI-CUENTA ESCALABLE")
print(f"{'='*70}")
print(f"Cuentas configuradas: {len(CUENTAS)}")
print(f"Cuentas: {', '.join(CUENTAS)}")
print(f"SKU: {SKU}")
print(f"{'='*70}\n")

# ==========================================
# STEP 1: ABRIR N CHROME (PARALELO)
# ==========================================
print(f"⏱️  STEP 1: Abriendo {len(CUENTAS)} Chrome en paralelo...\n")

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
                print(f"[{c_name:12}] 🚀 Lanzando en puerto {puerto_num}...")
            c_controller.handle_btn_launch_browser()
            with lock:
                print(f"[{c_name:12}] ✅ Chrome lanzado")
        except Exception as e:
            with lock:
                print(f"[{c_name:12}] ❌ Error: {e}")
    
    t = threading.Thread(
        target=abrir_nav,
        args=(cuenta, controller, puerto, i),
        daemon=True,
        name=f"abrir-{cuenta}"
    )
    t.start()
    threads.append(t)

# Esperar a que todos terminen de abrir
for t in threads:
    t.join(timeout=15)

print(f"\n✅ STEP 1 COMPLETADO: Todos los Chrome están abiertos\n")
print(f"{'='*70}")
print(f"📝 AHORA - Loguéate en CADA ventana de Chrome:")
for i, cuenta in enumerate(CUENTAS, 1):
    puerto = 9222 + int(cuenta.replace("cuenta", ""))
    print(f"   {i:2}. {cuenta:12} → Chrome en puerto {puerto}")
print(f"{'='*70}\n")

input("⏳ Presiona ENTER cuando hayas loguado en TODOS los Chrome: ")

# ==========================================
# STEP 2: ATACAR N CUENTAS (PARALELO)
# ==========================================
print(f"\n{'='*70}")
print(f"🔥 STEP 2: INICIANDO ATAQUES SIMULTÁNEOS...")
print(f"{'='*70}\n")

threads = []
resultados = {}

for cuenta in CUENTAS:
    puerto = 9222 + int(cuenta.replace("cuenta", ""))
    
    def atacar(c_name, c_controller, c_sku, puerto_num):
        try:
            with lock:
                print(f"[{c_name:12}] ⚔️  PLAY en puerto {puerto_num} - SKU {c_sku}")
            c_controller.handle_btn_play_hybrid(c_sku)
            resultados[c_name] = "OK"
            with lock:
                print(f"[{c_name:12}] ✅ PLAY completado")
        except Exception as e:
            resultados[c_name] = f"ERROR: {e}"
            with lock:
                print(f"[{c_name:12}] ❌ Error en PLAY: {e}")
    
    t = threading.Thread(
        target=atacar,
        args=(cuenta, controllers[cuenta], SKU, puerto),
        daemon=True,
        name=f"play-{cuenta}"
    )
    t.start()
    threads.append(t)

# Monitorear progreso
print(f"⏳ Esperando resultados de {len(CUENTAS)} cuentas (máx 20 segundos)...\n")
time.sleep(20)

# ==========================================
# STEP 3: RESULTADOS
# ==========================================
print(f"\n{'='*70}")
print(f"🎉 RESULTADOS FINALES")
print(f"{'='*70}\n")

ok_count = 0
for cuenta in CUENTAS:
    status = resultados.get(cuenta, "EN PROGRESO")
    puerto = 9222 + int(cuenta.replace("cuenta", ""))
    
    if status == "OK":
        ok_count += 1
        emoji = "✅"
    elif "ERROR" in status:
        emoji = "❌"
    else:
        emoji = "⏳"
    
    print(f"{emoji} [{cuenta:12}] Puerto {puerto} → {status}")

print(f"\n{'='*70}")
print(f"📊 RESUMEN: {ok_count}/{len(CUENTAS)} cuentas completadas")
print(f"{'='*70}\n")

if ok_count == len(CUENTAS):
    print(f"🎯 ¡ÉXITO TOTAL! Deberías ver {ok_count} pantallas de pago abiertas")
    print(f"💰 Completa los pagos manualmente en cada Chrome\n")
else:
    print(f"⚠️  Revisa los Chrome que tienen errores (posiblemente sin login)\n")

print(f"💡 PRÓXIMOS PASOS:")
print(f"   1. Revisa cada Chrome → ¿Ves pantalla de pago?")
print(f"   2. Ingresa clave del banco en cada uno")
print(f"   3. ¡Gana en 10 cuentas simultáneamente!\n")

