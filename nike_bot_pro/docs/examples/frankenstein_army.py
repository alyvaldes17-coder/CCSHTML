#!/usr/bin/env python3
"""
🔥 FRANKENSTEIN ARMY - Orquestación de múltiples Zombies

Gestor de múltiples cuentas con Inyección Frankenstein:
- Preparación sincronizada de Zombies
- Inyección simultánea en el drop
- Monitoreo de estado en tiempo real

USO:
    python frankenstein_army.py prepare --accounts cuenta2,cuenta3,cuenta4 --start-port 9222
    python frankenstein_army.py check --start-port 9222 --count 3
    python frankenstein_army.py drop --start-port 9222 --count 3 --magic-link-file links.txt
"""

import sys
import time
import json
import argparse
import threading
from pathlib import Path
from typing import List, Tuple, Dict

# Path setup
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from runtime.bot_controller import BotController
from engines.dirty_tools import (
    spawn_zombie_chrome, 
    teleport_chrome, 
    get_zombie_status, 
    kill_zombie_chrome
)


class FrankensteinArmy:
    """Gestor de múltiples Chrome Zombies"""
    
    def __init__(self):
        self.zombies: Dict[int, str] = {}  # port -> account_name
    
    def add_zombie(self, account_name: str, port: int) -> None:
        """Registra un nuevo Zombie"""
        self.zombies[port] = account_name
    
    def prepare_zombies(self, accounts: List[Tuple[str, int]], headless: bool = False) -> Dict[int, bool]:
        """
        Prepara múltiples Zombies (Paso 1)
        
        Args:
            accounts: Lista de (account_name, port) tuples
            headless: Si True, ventanas ocultas
        
        Returns:
            Dict de {port: success}
        """
        print(f"\n{'='*70}")
        print(f"🧟 PREPARANDO {len(accounts)} ZOMBIES")
        print(f"{'='*70}\n")
        
        results = {}
        threads = []
        
        for account_name, port in accounts:
            self.add_zombie(account_name, port)
            
            def _spawn(acc, p):
                controller = BotController(acc)
                success = controller.spawn_zombie(p, headless=headless)
                results[p] = success
            
            t = threading.Thread(target=_spawn, args=(account_name, port))
            threads.append(t)
            t.start()
        
        # Esperar a que terminen todos
        for t in threads:
            t.join()
        
        # Resumen
        print(f"\n{'='*70}")
        print(f"RESUMEN PREPARACIÓN:")
        print(f"{'='*70}")
        
        for port in sorted(results.keys()):
            account_name = self.zombies.get(port, "?")
            status = "✅ OK" if results[port] else "❌ ERROR"
            print(f"[{account_name:15}] Puerto {port}: {status}")
        
        return results
    
    def check_zombies(self, start_port: int, count: int) -> Dict[int, bool]:
        """
        Verifica estado de múltiples Zombies (Paso 2)
        
        Args:
            start_port: Puerto inicial (ej: 9222)
            count: Cantidad de Zombies a verificar
        
        Returns:
            Dict de {port: alive}
        """
        print(f"\n{'='*70}")
        print(f"🔍 VERIFICANDO {count} ZOMBIES (puertos {start_port}-{start_port+count-1})")
        print(f"{'='*70}\n")
        
        results = {}
        
        for i in range(count):
            port = start_port + i
            account_name = self.zombies.get(port, f"cuenta{i+2}")
            
            print(f"[{account_name:15}] Puerto {port}...", end=" ", flush=True)
            
            status = get_zombie_status(port)
            
            if status is None:
                print("❌ NO RESPONDE")
                results[port] = False
            else:
                tabs_count = len(status.get('tabs', []))
                print(f"✅ VIVO ({tabs_count} pestañas)")
                results[port] = True
        
        # Resumen
        alive = sum(1 for v in results.values() if v)
        print(f"\n📊 {alive}/{count} Zombies respondieron correctamente")
        
        return results
    
    def drop_all(self, start_port: int, count: int, magic_links: List[str]) -> Dict[int, bool]:
        """
        Ejecuta DROP sincronizado (Paso 3)
        
        Args:
            start_port: Puerto inicial
            count: Cantidad de inyecciones
            magic_links: Lista de URLs mágicas (debe coincidir con count)
        
        Returns:
            Dict de {port: success}
        """
        if len(magic_links) < count:
            print(f"❌ Error: tienes {len(magic_links)} links pero {count} Zombies")
            return {}
        
        print(f"\n{'='*70}")
        print(f"⚡ DROP SINCRONIZADO - {count} INYECCIONES")
        print(f"{'='*70}\n")
        
        # Verificar que todos están vivos antes
        print("🔍 Verificando Zombies antes del drop...")
        pre_check = self.check_zombies(start_port, count)
        
        alive_count = sum(1 for v in pre_check.values() if v)
        if alive_count < count:
            print(f"\n⚠️ Advertencia: Solo {alive_count}/{count} Zombies respondieron")
            response = input("¿Continuar de todos modos? (s/n): ")
            if response.lower() != "s":
                print("Abortado.")
                return {}
        
        # Esperar confirmación
        print(f"\n{'='*70}")
        print(f"🔴 PREPARADO PARA DROP")
        print(f"{'='*70}")
        print(f"Puerto inicial: {start_port}")
        print(f"Cantidad: {count}")
        print(f"Magic links: {len(magic_links)}")
        print()
        input("🎯 Presiona ENTER cuando hayas confirmado que es el DROP EXACTO:")
        
        print(f"\n🚀 ¡¡¡ DROP EN PROGRESO !!!\n")
        
        results = {}
        threads = []
        
        # Inyectar simultáneamente
        for i in range(count):
            port = start_port + i
            magic_link = magic_links[i]
            account_name = self.zombies.get(port, f"cuenta{i+2}")
            
            def _teleport(acc, p, link):
                success = teleport_chrome(p, link, max_retries=1)
                results[p] = success
                status_emoji = "✅" if success else "❌"
                print(f"[{acc:15}] Puerto {p}: {status_emoji} Inyección")
            
            t = threading.Thread(target=_teleport, args=(account_name, port, magic_link))
            threads.append(t)
            t.start()
        
        # Esperar (con timeout)
        for t in threads:
            t.join(timeout=10)
        
        # Resumen
        success_count = sum(1 for v in results.values() if v)
        print(f"\n{'='*70}")
        print(f"📊 RESULTADO: {success_count}/{count} inyecciones exitosas")
        print(f"{'='*70}\n")
        
        return results
    
    def cleanup_zombies(self, start_port: int, count: int) -> None:
        """
        Mata todos los Zombies
        
        Args:
            start_port: Puerto inicial
            count: Cantidad a matar
        """
        print(f"\n{'='*70}")
        print(f"🪦 LIMPIANDO {count} ZOMBIES")
        print(f"{'='*70}\n")
        
        for i in range(count):
            port = start_port + i
            account_name = self.zombies.get(port, f"cuenta{i+2}")
            
            print(f"[{account_name:15}] Puerto {port}...", end=" ", flush=True)
            
            if kill_zombie_chrome(port):
                print("✅ Cerrado")
            else:
                print("⚠️ No se pudo cerrar")
        
        print()


def cmd_prepare(args):
    """Comando: prepare"""
    accounts = []
    
    if args.accounts:
        account_names = args.accounts.split(",")
        for i, acc in enumerate(account_names):
            port = args.start_port + i
            accounts.append((acc.strip(), port))
    elif args.count:
        for i in range(args.count):
            account_name = f"cuenta{2+i}"
            port = args.start_port + i
            accounts.append((account_name, port))
    else:
        print("❌ Error: especifica --accounts o --count")
        return
    
    army = FrankensteinArmy()
    army.prepare_zombies(accounts, headless=args.headless)


def cmd_check(args):
    """Comando: check"""
    army = FrankensteinArmy()
    army.check_zombies(args.start_port, args.count or 3)


def cmd_drop(args):
    """Comando: drop"""
    if not args.magic_link_file and not args.magic_link:
        print("❌ Error: especifica --magic-link-file o --magic-link")
        return
    
    # Cargar magic links
    if args.magic_link_file:
        try:
            with open(args.magic_link_file) as f:
                magic_links = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {args.magic_link_file}")
            return
    else:
        magic_links = [args.magic_link]
    
    army = FrankensteinArmy()
    army.drop_all(args.start_port, args.count or len(magic_links), magic_links)


def cmd_cleanup(args):
    """Comando: cleanup"""
    army = FrankensteinArmy()
    army.cleanup_zombies(args.start_port, args.count or 3)


def main():
    parser = argparse.ArgumentParser(
        description="🔥 Frankenstein Army - Orquestador de Chrome Zombies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EJEMPLOS:

  # Preparar 3 Zombies
  python frankenstein_army.py prepare --count 3 --start-port 9222

  # Preparar cuentas específicas
  python frankenstein_army.py prepare --accounts cuenta2,cuenta3,cuenta4 --start-port 9222

  # Verificar que están vivos
  python frankenstein_army.py check --count 3 --start-port 9222

  # DROP con archivo de links
  python frankenstein_army.py drop --count 3 --start-port 9222 --magic-link-file links.txt

  # DROP con un único link
  python frankenstein_army.py drop --count 3 --start-port 9222 --magic-link "https://nike.cl/..."

  # Limpiar Zombies después
  python frankenstein_army.py cleanup --count 3 --start-port 9222
        """
    )
    
    parser.add_argument("--start-port", type=int, default=9222, help="Puerto CDP inicial (default: 9222)")
    
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")
    
    # prepare
    prepare_parser = subparsers.add_parser("prepare", help="Preparar Zombies")
    prepare_parser.add_argument("--accounts", help="Cuentas separadas por coma (ej: cuenta2,cuenta3,cuenta4)")
    prepare_parser.add_argument("--count", type=int, help="Cantidad de Zombies a preparar (default: 3)")
    prepare_parser.add_argument("--headless", action="store_true", help="Ventanas ocultas")
    prepare_parser.set_defaults(func=cmd_prepare)
    
    # check
    check_parser = subparsers.add_parser("check", help="Verificar Zombies")
    check_parser.add_argument("--count", type=int, default=3, help="Cantidad a verificar (default: 3)")
    check_parser.set_defaults(func=cmd_check)
    
    # drop
    drop_parser = subparsers.add_parser("drop", help="Ejecutar DROP")
    drop_parser.add_argument("--count", type=int, help="Cantidad de inyecciones")
    drop_parser.add_argument("--magic-link-file", help="Archivo con URLs (una por línea)")
    drop_parser.add_argument("--magic-link", help="URL única")
    drop_parser.set_defaults(func=cmd_drop)
    
    # cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Matar Zombies")
    cleanup_parser.add_argument("--count", type=int, default=3, help="Cantidad a matar (default: 3)")
    cleanup_parser.set_defaults(func=cmd_cleanup)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
