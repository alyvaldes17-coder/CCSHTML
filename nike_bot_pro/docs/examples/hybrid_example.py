#!/usr/bin/env python3
"""
🔥 HYBRID HANDOVER - Ejemplo Práctico Completo

Este script muestra cómo usar el ataque híbrido en un escenario real.

Incluye:
- Preparación de múltiples Zombies
- Sincronización de identidades
- Ejecución de ataque híbrido
- Fallback automático
- Cleanup

USO:
    python hybrid_example.py
"""

import time
import sys
from pathlib import Path
from runtime.bot_controller import BotController

# =============================================================================
# 🎯 CONFIGURACIÓN
# =============================================================================

# Cuentas a usar
ACCOUNTS = {
    "cuenta2": 9223,
    "cuenta3": 9224,
    # "cuenta4": 9225,  # Descomenta para más cuentas
}

# SKU a atacar (calcetines para testing, reemplazar con SKU real)
SKU_TARGET = "DQ8426100"

# Tiempos
PREP_TIME = 5       # segundos para preparación (real: 600 = 10 min)
WAIT_TIME = 3       # segundos de espera (real: 300 = 5 min)

# =============================================================================
# 📋 FASE 1: PREPARACIÓN (T-10 minutos)
# =============================================================================

def fase_preparacion():
    """Abre Chrome Zombies para todas las cuentas."""
    print("\n" + "="*70)
    print("FASE 1: PREPARACIÓN (T-10 minutos)")
    print("="*70)
    
    controllers = {}
    
    for account_name, port in ACCOUNTS.items():
        print(f"\n[{account_name}] 🧟 Abriendo Zombie en puerto {port}...")
        
        controller = BotController(account_name)
        
        # Abre Chrome con CDP
        if controller.spawn_zombie(port, headless=False):
            print(f"[{account_name}] ✅ Zombie abierto")
            controllers[account_name] = (controller, port)
            time.sleep(1)  # Pequeña pausa entre aberturas
        else:
            print(f"[{account_name}] ❌ Falló al abrir Zombie")
    
    print(f"\n✅ {len(controllers)} Zombies preparados")
    return controllers

# =============================================================================
# 💉 FASE 2: SINCRONIZACIÓN (T-5 minutos)
# =============================================================================

def fase_sincronizacion(controllers):
    """Sincroniza identidades (extrae cookies de Chrome)."""
    print("\n" + "="*70)
    print("FASE 2: SINCRONIZACIÓN (T-5 minutos)")
    print("="*70)
    
    sincronizados = 0
    
    for account_name, (controller, port) in controllers.items():
        print(f"\n[{account_name}] 💉 Sincronizando identidad...")
        
        if controller.sincronizar_hibrido(port):
            print(f"[{account_name}] ✅ Identidad sincronizada")
            sincronizados += 1
        else:
            print(f"[{account_name}] ⚠️ Sincronización incompleta (continuamos)")
    
    print(f"\n✅ {sincronizados}/{len(controllers)} identidades sincronizadas")
    return sincronizados > 0

# =============================================================================
# 🎬 FASE 3: ESPERA (T - 00:00)
# =============================================================================

def fase_espera():
    """Espera a la hora exacta del drop."""
    print("\n" + "="*70)
    print("FASE 3: ESPERA")
    print("="*70)
    
    print(f"\n⏳ Esperando {WAIT_TIME} segundos...")
    print("En producción: esperar a las 10:00:00 AM (drop oficial)")
    
    for i in range(WAIT_TIME, 0, -1):
        print(f"  T-{i:02d}s", end='\r', flush=True)
        time.sleep(1)
    
    print("\n🔔 ¡¡¡ ES LA HORA !!!\n")

# =============================================================================
# ⚔️ FASE 4: ATAQUE (T+0)
# =============================================================================

def fase_ataque(controllers):
    """Ejecuta el ataque híbrido en todas las cuentas."""
    print("\n" + "="*70)
    print("FASE 4: ATAQUE HÍBRIDO")
    print("="*70)
    
    resultados = {}
    
    print(f"\n🔥 ATACANDO SKU: {SKU_TARGET}\n")
    
    for account_name, (controller, port) in controllers.items():
        print(f"[{account_name}] ⚔️ Iniciando ataque...")
        
        # Ataque híbrido (con fallback automático)
        try:
            resultado = controller.ataque_hibrido(port, SKU_TARGET)
            resultados[account_name] = resultado
            
            if resultado:
                print(f"[{account_name}] ✅ ÉXITO")
            else:
                print(f"[{account_name}] ❌ FALLÓ")
        
        except Exception as e:
            print(f"[{account_name}] 💀 Error: {e}")
            resultados[account_name] = False
    
    return resultados

# =============================================================================
# 🧹 FASE 5: CLEANUP
# =============================================================================

def fase_cleanup(controllers):
    """Cierra todos los Zombies."""
    print("\n" + "="*70)
    print("FASE 5: CLEANUP")
    print("="*70)
    
    for account_name, (controller, port) in controllers.items():
        print(f"\n[{account_name}] 🪦 Cerrando Zombie...")
        
        if controller.kill_zombie(port):
            print(f"[{account_name}] ✅ Zombie muerto")
        else:
            print(f"[{account_name}] ⚠️ No se cerró gracefully")

# =============================================================================
# 📊 RESUMEN
# =============================================================================

def mostrar_resumen(resultados):
    """Muestra resumen de resultados."""
    print("\n" + "="*70)
    print("📊 RESUMEN DEL ATAQUE")
    print("="*70 + "\n")
    
    exitosos = sum(1 for r in resultados.values() if r)
    total = len(resultados)
    
    for account_name, resultado in resultados.items():
        status = "✅ EXITOSO" if resultado else "❌ FALLÓ"
        print(f"  {account_name}: {status}")
    
    print(f"\nTotal: {exitosos}/{total} cuentas exitosas")
    
    if exitosos == total:
        print("\n🎉 ¡¡¡ ATAQUE COMPLETAMENTE EXITOSO !!!")
        print("🏆 Llegas al checkout en todas las cuentas")
    elif exitosos > 0:
        print(f"\n⚠️ {exitosos} cuentas completaron el ataque")
    else:
        print("\n💀 Todas las cuentas fallaron")
    
    print("\n" + "="*70)

# =============================================================================
# 🚀 MAIN
# =============================================================================

def main():
    """Ejecuta el flujo completo."""
    
    print("\n")
    print("🔥" * 35)
    print("HYBRID HANDOVER - ATAQUE COMPLETO")
    print("🔥" * 35)
    
    try:
        # Fase 1: Preparación
        controllers = fase_preparacion()
        
        if not controllers:
            print("❌ No se prepararon Zombies. Abortando.")
            return 1
        
        # Pequeña pausa
        time.sleep(PREP_TIME)
        
        # Fase 2: Sincronización
        if not fase_sincronizacion(controllers):
            print("⚠️ Advertencia: No se sincronizaron todas las identidades")
        
        # Fase 3: Espera
        fase_espera()
        
        # Fase 4: Ataque
        resultados = fase_ataque(controllers)
        
        # Fase 5: Cleanup
        fase_cleanup(controllers)
        
        # Resumen
        mostrar_resumen(resultados)
        
        # Retornar status
        exitosos = sum(1 for r in resultados.values() if r)
        return 0 if exitosos > 0 else 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Abortado por usuario (Ctrl+C)")
        return 2
    
    except Exception as e:
        print(f"\n\n💀 Error fatal: {e}")
        import traceback
        traceback.print_exc()
        return 3

# =============================================================================
# 🏃 EJECUTAR
# =============================================================================

if __name__ == "__main__":
    print("\n")
    print("⚠️ ADVERTENCIA")
    print("-" * 70)
    print("Este script ATACA con CUENTAS REALES.")
    print("Modifica ACCOUNTS y SKU_TARGET según sea necesario.")
    print("Para testing, usa calcetines baratos.")
    print("-" * 70)
    
    respuesta = input("\n¿Continuar? (s/n): ").lower().strip()
    
    if respuesta != 's':
        print("Abortado.")
        sys.exit(0)
    
    # Ejecutar
    exit_code = main()
    sys.exit(exit_code)
