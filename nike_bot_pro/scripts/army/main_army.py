#!/usr/bin/env python3
"""
main_army.py - ESTRATEGIA DEL EJÉRCITO (Multi-Cuenta)

Carga TODAS las cuentas READY y dispara al unísono cuando llega el drop.

Flujo:
1. Escanear auth/ y reclutar cuentas
2. Esperar notificación de drop (Discord o manual)
3. Lanzar TODAS las cuentas en paralelo (threads)
4. Cada una intenta comprar simultáneamente

Ventaja: Si tienes 5 cuentas, tienes 5x más probabilidad.
"""
import os
import sys
import threading
import subprocess
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).parent))

from runtime.bot_controller import BotController
from core.account_state import AccountState


class Ejercito:
    """
    Gestor del ejército de cuentas.
    Coordina el ataque simultáneo de múltiples bots.
    """
    
    def __init__(self, auth_path: str = "auth"):
        """
        Args:
            auth_path: Ruta a la carpeta de autenticación
        """
        self.auth_path = os.path.abspath(auth_path)
        self.soldados = []  # Lista de BotControllers
        self.lock = threading.Lock()
        
    def reclutar(self):
        """
        Escanea auth/ y carga todas las cuentas configuradas.
        Solo carga cuentas que tengan un perfil_pw válido.
        """
        print("\n" + "="*60)
        print("🪖 RECLUTANDO EJÉRCITO...")
        print("="*60)
        
        if not os.path.exists(self.auth_path):
            print(f"❌ Ruta no encontrada: {self.auth_path}")
            return
        
        for nombre_cuenta in os.listdir(self.auth_path):
            # Filtrar directorios especiales
            if nombre_cuenta.startswith('.') or nombre_cuenta == "__pycache__":
                continue
            if "discord" in nombre_cuenta.lower():
                continue
            
            ruta_perfil = os.path.join(self.auth_path, nombre_cuenta, "profile_pw")
            
            # Si existe la carpeta de perfil, reclutar
            if os.path.isdir(ruta_perfil):
                try:
                    print(f"  🪖 Reclutando: {nombre_cuenta}")
                    bot = BotController(nombre_cuenta, ruta_perfil)
                    self.soldados.append(bot)
                except Exception as e:
                    print(f"  ❌ Error reclutando {nombre_cuenta}: {e}")
        
        print(f"\n✅ Ejército listo: {len(self.soldados)} cuentas")
        return len(self.soldados) > 0
    
    def listar_soldados(self):
        """Muestra estado de todas las cuentas"""
        print("\n" + "="*60)
        print("📋 ESTADO DEL EJÉRCITO")
        print("="*60)
        
        for i, bot in enumerate(self.soldados, 1):
            status = bot.get_status_text()
            print(f"{i:2d}. {bot.account_name:20s} → {status}")
    
    def loguear_todo(self):
        """
        LOGIN simultáneo para TODAS las cuentas.
        Lanza cada login en un thread separado.
        """
        print("\n" + "="*60)
        print("🔐 LOGUEO MASIVO")
        print("="*60)
        print(f"Loguendo {len(self.soldados)} cuentas simultáneamente...\n")
        
        threads = []
        
        for bot in self.soldados:
            def do_login(controller=bot):
                try:
                    print(f"[{controller.account_name}] 🔐 LOGIN iniciado...")
                    
                    # Lanzar login en subprocess
                    profile_path = os.path.abspath(controller.profile_path)
                    
                    import subprocess
                    process = subprocess.Popen([
                        sys.executable,
                        "login_runner.py",
                        profile_path
                    ])
                    
                    process.wait()  # Esperar a que termine
                    
                    # Validar sesión después de que Chrome se cierre
                    if controller.validate_session_real():
                        controller.state = AccountState.READY
                        print(f"[{controller.account_name}] ✅ READY")
                    else:
                        controller.state = AccountState.NO_AUTH
                        print(f"[{controller.account_name}] ❌ Validación falló")
                        
                except Exception as e:
                    print(f"[{controller.account_name}] ❌ Error: {e}")
                    controller.state = AccountState.NO_AUTH
            
            thread = threading.Thread(target=do_login, daemon=False)
            threads.append(thread)
            thread.start()
        
        # Esperar a que todos terminen
        for thread in threads:
            thread.join()
        
        print("\n✅ Logueo masivo completado")
        self.listar_soldados()
    
    def ataque_coordinado(self, sku: str, timeout_segundos: int = 30):
        """
        ATAQUE COORDINADO: Lanzar TODAS las cuentas simultáneamente.
        
        Cada cuenta:
        1. Inicia MONITORING (backend)
        2. Espera a que precio esté disponible
        3. Abre Chrome para checkout
        4. TODO en paralelo (no secuencial)
        
        Args:
            sku: SKU objetivo (ej: "12345")
            timeout_segundos: Timeout total del ataque
        """
        print("\n" + "="*60)
        print("🔥 ¡ORDEN DE ATAQUE RECIBIDA!")
        print("="*60)
        print(f"Objetivo: SKU {sku}")
        print(f"Fuego: {len(self.soldados)} cuentas")
        print("="*60 + "\n")
        
        # Filtrar solo cuentas READY
        ready_bots = [b for b in self.soldados if b.state == AccountState.READY]
        
        if not ready_bots:
            print("❌ No hay cuentas READY. Haz LOGIN primero.")
            return False
        
        print(f"🚀 Lanzando ataque con {len(ready_bots)} cuentas...\n")
        
        threads = []
        
        for bot in ready_bots:
            def do_attack(controller=bot, target_sku=sku):
                try:
                    print(f"[{controller.account_name}] 🎯 Atacando SKU {target_sku}...")
                    # Worker loop bloqueante (monitorea + compra)
                    controller.handle_btn_play_click(target_sku)
                    
                except Exception as e:
                    print(f"[{controller.account_name}] ❌ Error: {e}")
            
            # Lanzar en thread (ejecución paralela)
            thread = threading.Thread(target=do_attack, daemon=True)
            threads.append(thread)
            thread.start()
            
            # Pequeño delay entre lanzamientos (1ms cada uno)
            # Para evitar race conditions
            import time
            time.sleep(0.001)
        
        print(f"✅ Todos los soldados desplegados\n")
        
        # Esperar (no más de timeout_segundos)
        import time
        start = time.time()
        while len([t for t in threads if t.is_alive()]) > 0:
            if time.time() - start > timeout_segundos:
                print(f"\n⏱️ Timeout alcanzado ({timeout_segundos}s). Operación terminada.")
                break
            time.sleep(1)
        
        print("\n✅ Ataque coordinado completado")
        return True
    
    def drop_simulado(self, sku: str):
        """
        Simula un drop manual para testing.
        Ataca con todas las cuentas.
        """
        print(f"\n🧪 SIMULANDO DROP - SKU: {sku}")
        self.ataque_coordinado(sku)
    
    def estado_general(self):
        """Reporte general del ejército"""
        print("\n" + "="*60)
        print("📊 REPORTE GENERAL")
        print("="*60)
        
        ready = sum(1 for b in self.soldados if b.state == AccountState.READY)
        login_in_progress = sum(1 for b in self.soldados if b.state == AccountState.LOGIN_IN_PROGRESS)
        no_auth = sum(1 for b in self.soldados if b.state == AccountState.NO_AUTH)
        
        print(f"Total cuentas:        {len(self.soldados)}")
        print(f"  ✅ READY:           {ready}")
        print(f"  🔄 Loguando:        {login_in_progress}")
        print(f"  ❌ Sin autenticar:  {no_auth}")
        
        if ready == len(self.soldados):
            print(f"\n🟢 Ejército LISTO PARA COMBATE")
        else:
            print(f"\n🟡 Ejército parcialmente listo")


def main():
    """
    Menu interactivo para gestionar el ejército.
    """
    ejercito = Ejercito()
    
    # Reclutar todas las cuentas
    if not ejercito.reclutar():
        print("❌ No se pudieron cargar cuentas. Revisa auth/")
        return
    
    # Menu
    while True:
        print("\n" + "="*60)
        print("⚔️  COMANDO DEL EJÉRCITO")
        print("="*60)
        print("1. Listar soldados")
        print("2. Estado general")
        print("3. LOGIN masivo (todas las cuentas)")
        print("4. Ataque coordinado (SKU específico)")
        print("5. Drop simulado (para testing)")
        print("6. Salir")
        print("="*60)
        
        opcion = input("Elige opción (1-6): ").strip()
        
        if opcion == "1":
            ejercito.listar_soldados()
        
        elif opcion == "2":
            ejercito.estado_general()
        
        elif opcion == "3":
            ejercito.loguear_todo()
        
        elif opcion == "4":
            sku = input("Ingresa SKU: ").strip()
            if sku:
                ejercito.ataque_coordinado(sku)
        
        elif opcion == "5":
            sku = input("Ingresa SKU para drop simulado: ").strip()
            if sku:
                ejercito.drop_simulado(sku)
        
        elif opcion == "6":
            print("\n👋 ¡Hasta luego, General!")
            break
        
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    main()
