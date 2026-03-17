#!/usr/bin/env python3
"""
🔥 FRANKENSTEIN DEMO - Demostración de Inyección Hot-Swap

Este script muestra cómo usar la técnica "Inyección Frankenstein" en 3 pasos:

PASO 1 (T-Minus 10 min): spawn_zombie_chrome() - Abre Chrome Zombie
PASO 2 (Preparación): check_zombie_status() - Verifica que está vivo
PASO 3 (Drop exacto): teleport_chrome() - Inyecta URL mágica

El navegador es REAL. Lleva abierto 1 hora. La detección es casi nula.
Tiempo de reacción: 0.01 segundos (solo latencia de red).

USO:
    python frankenstein_demo.py <account_name> <port> [magic_link]

EJEMPLOS:
    # Paso 1: Preparar 3 Zombies
    python frankenstein_demo.py cuenta2 9222
    python frankenstein_demo.py cuenta3 9223
    python frankenstein_demo.py cuenta4 9224

    # Paso 2: Verificar que están vivos
    curl http://127.0.0.1:9222/json
    curl http://127.0.0.1:9223/json
    curl http://127.0.0.1:9224/json

    # Paso 3: Drop con Inyección (ejecutar al UNÍSONO)
    python frankenstein_demo.py cuenta2 9222 "https://nike.cl/nstrike/..."
    python frankenstein_demo.py cuenta3 9223 "https://nike.cl/nstrike/..."
    python frankenstein_demo.py cuenta4 9224 "https://nike.cl/nstrike/..."
"""

import sys
import time
import argparse
from pathlib import Path

# Agregar path raíz
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from runtime.bot_controller import BotController
from engines.dirty_tools import spawn_zombie_chrome, teleport_chrome, get_zombie_status


def demo_spawn(account_name: str, port: int) -> None:
    """
    DEMO PASO 1: Preparar Zombie Chrome
    
    Esto abre un Chrome en about:blank listo para recibir órdenes.
    Ejecutar ~10 minutos antes del drop.
    """
    print(f"\n{'='*70}")
    print(f"🧟 DEMO PASO 1: SPAWN ZOMBIE")
    print(f"{'='*70}")
    print(f"Account: {account_name}")
    print(f"Port: {port}")
    print(f"URL after spawn: http://127.0.0.1:{port}/json")
    print()
    
    controller = BotController(account_name)
    
    # Opción A: Usar método de BotController
    # success = controller.spawn_zombie(port)
    
    # Opción B: Usar directo dirty_tools (más control)
    success = spawn_zombie_chrome(
        profile_path=controller.profile_run,
        port_number=port,
        headless=False  # Visible
    )
    
    if success:
        print(f"\n✅ Chrome Zombie abierto en puerto {port}")
        print(f"⏳ Esperando 5 segundos para que termine de cargar...")
        time.sleep(5)
        
        # Verificar que responde
        status = get_zombie_status(port)
        if status:
            print(f"✅ Zombie RESPONDE al puerto {port}")
            print(f"   Total pestañas: {len(status.get('tabs', []))}")
            for i, tab in enumerate(status.get('tabs', []), 1):
                print(f"   - Tab {i}: {tab.get('title', 'Sin título')[:50]}")
        else:
            print(f"❌ Zombie NO responde (puede estar listo pero necesita esperar)")
    else:
        print(f"❌ Error al lanzar Chrome Zombie")


def demo_check(port: int) -> None:
    """
    DEMO VERIFICACIÓN: Comprobar estado del Zombie
    
    Útil para verificar que el Chrome está listo antes del drop.
    """
    print(f"\n{'='*70}")
    print(f"🔍 DEMO VERIFICACIÓN: CHECK ZOMBIE")
    print(f"{'='*70}")
    print(f"Puerto: {port}")
    print()
    
    status = get_zombie_status(port)
    
    if status is None:
        print(f"❌ Puerto {port}: NO RESPONDE")
        print(f"   Chrome puede no estar abierto, o todavía está cargando")
    else:
        print(f"✅ Puerto {port}: VIVO Y RESPONDIENDO")
        print(f"   Total pestañas: {len(status.get('tabs', []))}")
        
        tabs = status.get('tabs', [])
        for i, tab in enumerate(tabs, 1):
            print(f"\n   📄 Pestaña {i}:")
            print(f"      Tipo: {tab.get('type')}")
            print(f"      Título: {tab.get('title', 'Sin título')}")
            print(f"      URL: {tab.get('url', 'Sin URL')}")
            print(f"      WebSocket: {tab.get('webSocketDebuggerUrl', 'N/A')[:60]}...")


def demo_teleport(port: int, magic_link: str) -> None:
    """
    DEMO PASO 3: Teleportar (Inyectar URL mágica)
    
    Esta es la operación del DROP EXACTO.
    Ejecutar al unísono en todos los puertos.
    """
    print(f"\n{'='*70}")
    print(f"⚡ DEMO PASO 3: TELEPORT (INYECCIÓN MÁGICA)")
    print(f"{'='*70}")
    print(f"Puerto: {port}")
    print(f"Magic Link: {magic_link[:60]}...")
    print()
    
    # Verificar que el Zombie existe
    print(f"🔍 Verificando que Zombie está vivo...")
    status = get_zombie_status(port)
    if status is None:
        print(f"❌ Puerto {port}: NO RESPONDE")
        print(f"   Corre PASO 1 (spawn) primero")
        return
    
    print(f"✅ Zombie está VIVO")
    print()
    
    # INYECCIÓN
    print(f"💉 Inyectando URL mágica...")
    success = teleport_chrome(port, magic_link)
    
    if success:
        print(f"\n✅ INYECCIÓN EXITOSA")
        print(f"🚀 Chrome debería estar cargando el checkout ahora")
    else:
        print(f"\n❌ INYECCIÓN FALLÓ")
        print(f"   Verifica que el Zombie está respondiendo")
        print(f"   Intenta de nuevo con: python frankenstein_demo.py --check {port}")


def main():
    parser = argparse.ArgumentParser(
        description="🔥 Frankenstein Demo - Hot-Swap Chrome Injection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EJEMPLOS:

  # Paso 1: Preparar Zombie
  python frankenstein_demo.py cuenta2 9222

  # Verificar que está vivo
  python frankenstein_demo.py --check 9222

  # Paso 3: Inyectar URL mágica (en el momento del drop)
  python frankenstein_demo.py --teleport 9222 "https://nike.cl/nstrike/..."

  # Flujo completo manual
  1. python frankenstein_demo.py cuenta2 9222
  2. sleep 5
  3. python frankenstein_demo.py --check 9222
  4. python frankenstein_demo.py --teleport 9222 "https://nike.cl/..."
        """
    )
    
    parser.add_argument("account", nargs="?", help="Nombre de cuenta (ej: cuenta2)")
    parser.add_argument("port", nargs="?", type=int, help="Puerto CDP (ej: 9222)")
    parser.add_argument("magic_link", nargs="?", help="URL mágica a inyectar (opcional)")
    
    parser.add_argument("--check", type=int, metavar="PORT", help="Solo verificar Zombie en puerto")
    parser.add_argument("--teleport", type=int, metavar="PORT", help="Inyectar a puerto")
    parser.add_argument("--url", type=str, help="URL para --teleport")
    
    args = parser.parse_args()
    
    # Modo 1: --check (verificación)
    if args.check:
        demo_check(args.check)
        return
    
    # Modo 2: --teleport (inyección)
    if args.teleport:
        if not args.url:
            print("❌ Error: --teleport requiere --url")
            parser.print_help()
            sys.exit(1)
        demo_teleport(args.teleport, args.url)
        return
    
    # Modo 3: Normal (spawn)
    if not args.account or not args.port:
        print("❌ Error: Se requiere <account> y <port>")
        parser.print_help()
        sys.exit(1)
    
    # Si tiene magic_link, es inyección directa
    if args.magic_link:
        demo_spawn(args.account, args.port)
        time.sleep(2)
        demo_teleport(args.port, args.magic_link)
    else:
        # Solo spawn
        demo_spawn(args.account, args.port)


if __name__ == "__main__":
    main()
