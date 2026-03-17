#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_pre_ev2.py

Script de diagnóstico para capturar exactamente qué retorna [PRE-EV2]
en la confirmación de shipping.
"""

import sys
import os
import json
import threading
import time

# Agregar el project root al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from runtime.bot_controller import BotController

def test_pre_ev2():
    """Ejecuta el ataque en cuenta1 y captura la salida de [PRE-EV2]."""
    
    account_name = "cuenta1"
    sku = None
    
    # Intenta leer el SKU de config.json
    cfg_path = os.path.join("auth", account_name, "config.json")
    try:
        with open(cfg_path, encoding="utf-8") as f:
            cfg = json.load(f)
        skus = [s for s in cfg.get("skus", []) if s]
        sku = skus[0] if skus else cfg.get("sku")
    except Exception as e:
        print(f"[TEST] Error leyendo config: {e}")
    
    if not sku:
        print(f"[TEST] ERROR: No hay SKU configurado en {account_name}")
        print(f"[TEST] Agrega un SKU en auth/{account_name}/config.json")
        return
    
    print(f"\n{'='*70}")
    print(f"  TEST [PRE-EV2] — Diagnóstico de Shipping")
    print(f"{'='*70}")
    print(f"  Cuenta:  {account_name}")
    print(f"  SKU:     {sku}")
    print(f"  Modo:    Ejecutar ataque sin comprar")
    print(f"{'='*70}\n")
    
    controller = BotController(account_name)
    
    # Redirigir stdout para capturar [PRE-EV2]
    pre_ev2_result = [None]  # List para que el callback pueda modificar
    
    original_print = print
    pre_ev2_found = [False]
    
    def custom_print(*args, **kwargs):
        """Intercepta los prints para capturar [PRE-EV2]."""
        msg = " ".join(str(a) for a in args)
        if "[PRE-EV2]" in msg:
            pre_ev2_found[0] = True
            pre_ev2_result[0] = msg
            original_print(f"\n{'!'*70}")
            original_print(f"!!! CAPTURADO: {msg}")
            original_print(f"{'!'*70}\n")
        original_print(*args, **kwargs)
    
    import builtins
    builtins.print = custom_print
    
    try:
        # Lanzar el ataque
        print(f"[TEST] Iniciando ataque en thread...")
        attack_done = threading.Event()
        
        def run_attack():
            try:
                controller.handle_btn_play_hybrid(sku)
            except Exception as e:
                custom_print(f"[TEST] Exception: {e}")
            finally:
                attack_done.set()
        
        thread = threading.Thread(target=run_attack, daemon=False)
        thread.start()
        
        # Esperar hasta 60 segundos
        print(f"[TEST] Esperando resultado de ataque (max 60s)...")
        if attack_done.wait(timeout=60):
            print(f"[TEST] Ataque completado")
        else:
            print(f"[TEST] TIMEOUT — ataque tardó más de 60s")
        
        # Restaurar print
        builtins.print = original_print
        
        print(f"\n{'='*70}")
        print(f"  RESULTADO DIAGNÓSTICO")
        print(f"{'='*70}")
        
        if pre_ev2_found[0]:
            print(f"\n✓ [PRE-EV2] encontrado en logs:")
            print(f"  {pre_ev2_result[0]}\n")
            
            # Parsear el resultado
            if "SHIPPING_OK:" in pre_ev2_result[0]:
                print(f"  ✓ SHIPPING YA CONFIRMADO")
                print(f"    → La dirección ya está en el sistema")
            elif "SHIPPING_CONFIRMED:" in pre_ev2_result[0]:
                print(f"  ✓ SHIPPING CONFIRMADO por el bot")
                print(f"    → Se seleccionó el primer SLA disponible")
            elif "SHIPPING_MISSING:" in pre_ev2_result[0]:
                print(f"  ✗ FALTAN DATOS DE SHIPPING")
                try:
                    # Extraer el JSON del mensaje
                    json_start = pre_ev2_result[0].find("{")
                    if json_start != -1:
                        json_str = pre_ev2_result[0][json_start:]
                        info = json.loads(json_str)
                        print(f"    → hasAddr: {info.get('hasAddr')} (dirección)")
                        print(f"    → hasLogistic: {info.get('hasLogistic')} (opciones de envío)")
                        print(f"    → hasSla: {info.get('hasSla')} (SLA seleccionado)")
                except:
                    pass
            elif "ERROR:" in pre_ev2_result[0]:
                print(f"  ✗ ERROR EN SHIPPING")
                err = pre_ev2_result[0].split("ERROR:")[-1]
                print(f"    → {err}")
        else:
            print(f"\n✗ [PRE-EV2] NO encontrado en logs")
            print(f"  → El ataque no llegó a esa etapa o falló antes\n")
        
        print(f"{'='*70}\n")
        
    except Exception as e:
        builtins.print = original_print
        print(f"[TEST] ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            controller.stop_worker()
        except:
            pass


if __name__ == "__main__":
    test_pre_ev2()
