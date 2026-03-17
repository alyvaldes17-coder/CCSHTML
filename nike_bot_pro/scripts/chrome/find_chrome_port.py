#!/usr/bin/env python3
"""
Detecta EXACTAMENTE qué puerto Chrome está usando.
Sin asumir nada, simplemente ver netstat después de abrir Chrome.
"""

import subprocess
import time
import os
import re
import sys
import platform
import requests

def get_chrome_ports():
    """Obtiene todos los puertos que Chrome está escuchando."""
    try:
        # netstat -ano con findstr para Chrome
        result = subprocess.check_output(
            "netstat -ano | findstr chrome.exe",
            shell=True,
            text=True
        )
        
        ports = set()
        for line in result.strip().split('\n'):
            if 'LISTENING' in line:
                # Formato: TCP    127.0.0.1:9223  0.0.0.0:0  LISTENING  PID
                match = re.search(r':(\d+)\s+', line)
                if match:
                    port = match.group(1)
                    ports.add(int(port))
        
        return ports
    except Exception as e:
        print(f"❌ Error leyendo netstat: {e}")
        return set()

def test_port(port, timeout=1):
    """Intenta conectar a un puerto."""
    try:
        session = requests.Session()
        session.trust_env = False
        resp = session.get(f"http://127.0.0.1:{port}/json", timeout=timeout)
        return resp.status_code == 200
    except:
        return False

def main():
    print(f"\n{'='*60}")
    print(f"🔍 DETECTOR DE PUERTOS DE CHROME")
    print(f"{'='*60}\n")
    
    # Paso 1: Cerrar Chrome viejo
    print(f"[1/4] Cerrando Chrome viejo...")
    os.system("taskkill /F /IM chrome.exe 2>nul")
    time.sleep(2)
    
    # Paso 2: Abrir Chrome con TODOS los flags posibles
    print(f"[2/4] Abriendo Chrome...")
    
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    
    if not os.path.exists(chrome_path):
        print(f"❌ Chrome no encontrado")
        return False
    
    # MÁS flags agresivos para forzar el puerto
    args = [
        chrome_path,
        "--remote-debugging-port=9223",
        "--remote-debugging-address=127.0.0.1",  # Adicional
        "--no-sandbox",
        "--disable-background-networking",  # Para que no interfiera nada
        "--disable-background-timer-throttling",
        "--disable-breakpad",
        "--disable-client-side-phishing-detection",
        "--disable-default-apps",
        "--disable-extensions",
        "--disable-features=TranslateUI",
        "--disable-hang-monitor",
        "--disable-popup-blocking",
        "--disable-prompt-on-repost",
        "--disable-sync",
        "--start-maximized",
        "about:blank"
    ]
    
    print(f"    Flags: {len(args)-1} argumentos")
    
    try:
        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"    ✅ Chrome iniciado (PID {proc.pid})")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False
    
    # Paso 3: Esperar y muestrear puertos
    print(f"\n[3/4] Muestreando puertos (esperando Chrome)...\n")
    
    encontrado = False
    for attempt in range(1, 8):
        time.sleep(2)
        ports = get_chrome_ports()
        
        if not ports:
            print(f"    Intento #{attempt}: Chrome aún no en netstat")
            continue
        
        print(f"    Intento #{attempt}: Chrome está en puerto(s): {sorted(ports)}")
        
        # Verificar cada puerto
        for port in sorted(ports):
            if port < 1000:  # Ignorar puertos del sistema
                continue
            
            if test_port(port):
                print(f"         ✅ Puerto {port} responde a /json")
                encontrado = True
            else:
                print(f"         ⏳ Puerto {port} no responde")
    
    # Paso 4: Resumen
    print(f"\n[4/4] Resumen")
    print(f"{'='*60}\n")
    
    if encontrado:
        print(f"✅ ÉXITO: Chrome responde en algún puerto")
        print(f"   Solución: Actualizar bot_controller.py con el puerto correcto")
    else:
        ports = get_chrome_ports()
        if ports:
            print(f"⚠️ Chrome abrió en puerto(s) {sorted(ports)}")
            print(f"   pero NO responde a /json")
            print(f"   Posible causa: Flag --remote-debugging-port no funciona")
            print(f"   o hay conflicto con otro flag")
        else:
            print(f"❌ Chrome NO aparece en netstat")
            print(f"   Causa: Proceso no se inició o está crasheando")
    
    # Limpiar
    os.system("taskkill /F /IM chrome.exe 2>nul")
    time.sleep(1)
    
    return encontrado

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
