#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_shipping_direct.py

Prueba directa del método _confirmar_shipping sin necesidad de
lanzar el ataque completo.
"""

import sys
import os
import json
import websocket
import urllib.request
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engines.engine import NikeBotEngine


def test_shipping_direct():
    """Abre una conexión CDP directamente y prueba _confirmar_shipping."""
    
    account_name = "cuenta1"
    
    # Verificar que Chrome está corriendo para esta cuenta
    print(f"\n{'='*70}")
    print(f"  TEST DIRECTO — _confirmar_shipping")
    print(f"{'='*70}")
    print(f"  Cuenta: {account_name}\n")
    
    engine = NikeBotEngine(port=9223, account_name=account_name)
    
    try:
        # Obtener lista de tabs
        print(f"[TEST] Buscando Chrome en puerto 9223...")
        try:
            with urllib.request.urlopen("http://127.0.0.1:9223/json", timeout=3) as r:
                tabs = json.loads(r.read())
        except Exception as e:
            print(f"[TEST] ✗ Chrome NO está corriendo en puerto 9223")
            print(f"[TEST] Excepción: {e}")
            print(f"\n[TEST] ¿Chrome está abierto?")
            print(f"[TEST] Verifica en la UI o lanza Chrome con:")
            print(f"       python -c \"from runtime.bot_controller import BotController; c = BotController('cuenta1'); c.handle_btn_launch_browser()\"")
            return
        
        tab = next((t for t in tabs if t.get("type") == "page"), None)
        if not tab:
            print(f"[TEST] ✗ No hay tab de página abierta en Chrome")
            print(f"[TEST] Abre https://www.nike.cl en Chrome")
            return
        
        ws_url = tab["webSocketDebuggerUrl"]
        print(f"[TEST] ✓ Chrome encontrado")
        print(f"[TEST] URL WebSocket: {ws_url[:50]}...")
        print(f"[TEST] Conectando...\n")
        
        ws = websocket.create_connection(ws_url, timeout=5)
        print(f"[TEST] ✓ Conectado\n")
        
        # Llamar _confirmar_shipping
        print(f"[TEST] Llamando _confirmar_shipping()...")
        print(f"[TEST] (esto consulta el orderForm de Nike via API)\n")
        
        result = engine._confirmar_shipping(ws)
        
        ws.close()
        
        print(f"\n{'='*70}")
        print(f"  RESULTADO")
        print(f"{'='*70}\n")
        
        print(f"Retorno: {result}\n")
        
        # Analizar el resultado
        if result.startswith("SHIPPING_OK:"):
            addr = result.replace("SHIPPING_OK:", "").strip()
            print(f"✓ SHIPPING YA CONFIRMADO")
            print(f"  → Dirección: {addr}")
            print(f"  → El shipping está listo para pagar")
        
        elif result.startswith("SHIPPING_CONFIRMED:"):
            sla = result.replace("SHIPPING_CONFIRMED:", "").strip()
            print(f"✓ SHIPPING CONFIRMADO por API")
            print(f"  → SLA seleccionado: {sla}")
            print(f"  → El bot acaba de activar este método de envío")
        
        elif result.startswith("SHIPPING_MISSING:"):
            info_str = result.replace("SHIPPING_MISSING:", "").strip()
            print(f"✗ FALTAN DATOS DE SHIPPING")
            try:
                info = json.loads(info_str)
                print(f"  → hasAddr: {info.get('hasAddr')} (¿hay dirección?)")
                print(f"  → hasLogistic: {info.get('hasLogistic')} (¿hay opciones de envío?)")
                print(f"  → hasSla: {info.get('hasSla')} (¿hay SLA seleccionado?)")
                print(f"\n  DIAGNÓSTICO:")
                if not info.get('hasAddr'):
                    print(f"  ✗ NO hay dirección guardada → agrégala en checkout/shipping")
                if not info.get('hasLogistic'):
                    print(f"  ✗ NO hay opciones de envío → ingresa dirección válida")
                if not info.get('hasSla') and info.get('hasLogistic'):
                    print(f"  ✗ NO hay SLA seleccionado → selecciona método de envío en Nike")
            except:
                print(f"  → {info_str}")
        
        elif result.startswith("ERROR:"):
            err = result.replace("ERROR:", "").strip()
            print(f"✗ ERROR EN API")
            print(f"  → {err}")
        
        else:
            print(f"? RESPUESTA DESCONOCIDA")
            print(f"  → {result}")
        
        print(f"\n{'='*70}\n")
        
    except Exception as e:
        print(f"[TEST] Exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_shipping_direct()
