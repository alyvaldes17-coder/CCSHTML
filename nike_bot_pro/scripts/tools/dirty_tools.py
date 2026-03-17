"""
🔥 DIRTY TOOLS - Inyección Frankenstein (Hot-Swap de Chrome)

Técnica de "Teletransporte" ultra-rápida:
- spawn_zombie_chrome(): Abre Chrome en estado "Zombie" (about:blank, esperando órdenes)
- teleport_chrome(): Se conecta vía CDP y fuerza navegación sin simular escribir URL

Tiempo de reacción: 0.01 segundos (solo latencia de red)
Detección: Casi nula (el navegador es real y lleva abierto 1 hora)

⚠️ CRÍTICO: Requiere: pip install websocket-client requests
"""

import json
import requests
import websocket
import subprocess
import sys
import os
from typing import Optional, Dict, Any


def spawn_zombie_chrome(
    profile_path: str,
    port_number: int,
    chrome_path: Optional[str] = None,
    headless: bool = False
) -> bool:
    """
    🧟‍♂️ Abre un Chrome 'Zombie' listo para recibir órdenes.
    
    Lo ejecutas 10 minutos antes del drop.
    El navegador espera en about:blank, gastando mínimo RAM.
    
    Args:
        profile_path: Ruta al perfil Chrome (ej: auth/cuenta2/profile_run)
        port_number: Puerto CDP único (9222, 9223, 9224, etc)
        chrome_path: Ruta a chrome.exe (detecta automáticamente si no se especifica)
        headless: Si True, ventana oculta. False (default) = visible
    
    Returns:
        True si el proceso se inició correctamente
    
    Ejemplo:
        spawn_zombie_chrome("auth/cuenta2/profile_run", 9222)
        spawn_zombie_chrome("auth/cuenta3/profile_run", 9223)
    """
    
    try:
        # 🔍 Detectar chrome.exe automáticamente
        if chrome_path is None:
            if sys.platform == "win32":
                # Rutas comunes en Windows
                possible_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                ]
                chrome_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        chrome_path = path
                        break
                
                if chrome_path is None:
                    print(f"❌ [ZOMBIE] No encontré Chrome en rutas estándar Windows")
                    return False
            else:
                chrome_path = "google-chrome"  # Linux/Mac
        
        # Crear directorio del perfil si no existe
        os.makedirs(profile_path, exist_ok=True)
        
        # 🧟 Argumentos del Chrome Zombie
        args = [
            chrome_path,
            f"--user-data-dir={profile_path}",
            "--profile-directory=Default",
            f"--remote-debugging-port={port_number}",  # 🗝️ LA LLAVE MAESTRA
            "--start-maximized",
            "--no-sandbox",
            "--disable-infobars",
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
        ]
        
        if headless:
            args.append("--headless=new")
        
        # about:blank = página vacía, gasta 0 RAM
        args.append("about:blank")
        
        print(f"🧟 [ZOMBIE] Lanzando Chrome en puerto {port_number}")
        print(f"🧟 [ZOMBIE] Perfil: {profile_path}")
        print(f"🧟 [ZOMBIE] Chrome.exe: {chrome_path}")
        
        # Lanzar proceso sin esperar (non-blocking)
        subprocess.Popen(args)
        
        print(f"✅ [ZOMBIE] Proceso iniciado. Chrome debería estar cargando...")
        
        return True
        
    except Exception as e:
        print(f"❌ [ZOMBIE] Error al lanzar Chrome: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def teleport_chrome(port_number: int, magic_link: str, max_retries: int = 3) -> bool:
    """
    ⚡ Hackea el Chrome existente y lo fuerza a ir al checkout.
    
    Se conecta al puerto CDP del Chrome Zombie y ejecuta comandos del protocolo
    de depuración remota de Chrome (CDP - Chrome DevTools Protocol).
    
    Tiempo estimado: 10ms + latencia de red.
    
    Args:
        port_number: Puerto CDP del Chrome Zombie (9222, 9223, etc)
        magic_link: URL a la que forzar navegación (ej: link mágico de Nike)
        max_retries: Intentos de conexión (en caso de que Chrome no esté listo)
    
    Returns:
        True si la inyección fue exitosa
    
    Ejemplo:
        teleport_chrome(9222, "https://www.nike.cl/nstrike/checkout/...?token=xyz")
        teleport_chrome(9223, "https://www.nike.cl/nstrike/checkout/...?token=abc")
    """
    
    for attempt in range(max_retries):
        try:
            print(f"💉 [INYECCIÓN] Intento {attempt + 1}/{max_retries} al puerto {port_number}...")
            
            # 🔍 PASO 1: Buscar la pestaña activa en el Chrome Zombie
            # Le preguntamos al puerto CDP: "¿Qué pestañas tienes?"
            response = requests.get(
                f"http://127.0.0.1:{port_number}/json",
                timeout=5
            )
            
            if response.status_code != 200:
                print(f"⚠️ [INYECCIÓN] Respuesta inesperada: {response.status_code}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)
                    continue
                return False
            
            tabs = response.json()
            
            if not tabs:
                print(f"❌ [INYECCIÓN] No hay pestañas en puerto {port_number}")
                return False
            
            # Buscamos la pestaña que sea 'page' (la visible, no DevTools)
            target_tab = None
            for tab in tabs:
                if tab.get('type') == 'page':
                    target_tab = tab
                    break
            
            if not target_tab:
                # Si no hay 'page', agarramos la primera
                target_tab = tabs[0]
            
            print(f"✅ [INYECCIÓN] Pestaña encontrada: {target_tab.get('title', 'Sin título')}")
            
            # 🔗 PASO 2: Conexión WebSocket Directa (Sin intermediarios Playwright)
            ws_url = target_tab.get('webSocketDebuggerUrl')
            
            if not ws_url:
                print(f"❌ [INYECCIÓN] No hay webSocketDebuggerUrl en pestaña")
                return False
            
            print(f"🔗 [INYECCIÓN] Conectando a WebSocket: {ws_url[:80]}...")
            
            ws = websocket.create_connection(ws_url, timeout=5)
            
            print(f"💉 [INYECCIÓN] Teletransportando a: {magic_link[:80]}...")
            
            # 🎯 PASO 3: COMANDO CDP PURO (Nivel Kernel de Chrome)
            # Esto NO simula escribir la URL, le ordena al motor cambiarla.
            navigate_command = {
                "id": 1,
                "method": "Page.navigate",
                "params": {"url": magic_link}
            }
            
            ws.send(json.dumps(navigate_command))
            
            # Esperar respuesta
            response_data = ws.recv()
            response_obj = json.loads(response_data)
            
            if "error" in response_obj:
                print(f"❌ [INYECCIÓN] Error CDP: {response_obj['error']}")
                ws.close()
                return False
            
            print(f"✅ [INYECCIÓN] Page.navigate enviado correctamente")
            
            # 🪟 PASO 4: Enfoque agresivo (Traer ventana al frente)
            focus_command = {
                "id": 2,
                "method": "Page.bringToFront"
            }
            
            ws.send(json.dumps(focus_command))
            
            # No esperamos respuesta del bring-to-front, solo cerramos
            ws.close()
            
            print(f"✅ [ÉXITO] Inyección completada en puerto {port_number}")
            print(f"🚀 Chrome ya está cargando la URL mágica")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ [INYECCIÓN] Error de conexión HTTP: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
                continue
            return False
            
        except websocket.WebSocketException as e:
            print(f"⚠️ [INYECCIÓN] Error WebSocket: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
                continue
            return False
            
        except Exception as e:
            print(f"💀 [INYECCIÓN] Error inesperado: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
                continue
            return False
    
    print(f"💀 [FAIL] El Zombie en puerto {port_number} no respondió después de {max_retries} intentos")
    return False


def kill_zombie_chrome(port_number: int) -> bool:
    """
    🪦 Mata el Chrome Zombie gracefully.
    
    Args:
        port_number: Puerto CDP del Chrome a matar
    
    Returns:
        True si se logró cerrar
    """
    try:
        # Intentar cerrar vía CDP primero
        response = requests.get(
            f"http://127.0.0.1:{port_number}/json",
            timeout=2
        )
        
        if response.status_code == 200:
            tabs = response.json()
            if tabs:
                target_tab = tabs[0]
                ws_url = target_tab.get('webSocketDebuggerUrl')
                
                if ws_url:
                    ws = websocket.create_connection(ws_url, timeout=2)
                    
                    close_command = {
                        "id": 999,
                        "method": "Browser.close"
                    }
                    
                    ws.send(json.dumps(close_command))
                    ws.close()
                    
                    print(f"🪦 [ZOMBIE] Cerrado gracefully en puerto {port_number}")
                    return True
        
        print(f"⚠️ [ZOMBIE] No se pudo cerrar gracefully, intentando fuerza bruta...")
        
        # Fallback: matar por puerto (Windows)
        if sys.platform == "win32":
            subprocess.run(
                f"taskkill /FI \"PID eq (netstat -ano | find /I \":{port_number}\" | find /I \"LISTENING\")\" /F",
                shell=True,
                capture_output=True
            )
        
        return True
        
    except Exception as e:
        print(f"⚠️ [ZOMBIE] Error al cerrar: {type(e).__name__}: {e}")
        return False


def get_zombie_status(port_number: int) -> Optional[Dict[str, Any]]:
    """
    🔍 Obtiene estado del Chrome Zombie.
    
    Args:
        port_number: Puerto CDP
    
    Returns:
        Dict con info de pestañas, o None si no responde
    """
    try:
        response = requests.get(
            f"http://127.0.0.1:{port_number}/json",
            timeout=2
        )
        
        if response.status_code == 200:
            return {
                "status": "alive",
                "tabs": response.json(),
                "port": port_number
            }
        
        return None
        
    except Exception as e:
        print(f"⚠️ [STATUS] Error consultando puerto {port_number}: {e}")
        return None
