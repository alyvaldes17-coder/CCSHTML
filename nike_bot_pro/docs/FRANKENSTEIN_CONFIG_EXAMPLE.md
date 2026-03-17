# 🔥 CONFIGURACIÓN DE EJEMPLO - 10 CUENTAS

# Este archivo contiene ejemplos de configuración para ejecutar
# la Inyección Frankenstein con múltiples cuentas

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN: 10 Cuentas Nike
# ═══════════════════════════════════════════════════════════════════════════

## Mapeo de Cuenta → Puerto CDP
accounts_config = {
    "cuenta2": 9222,
    "cuenta3": 9223,
    "cuenta4": 9224,
    "cuenta5": 9225,
    "cuenta6": 9226,
    "cuenta7": 9227,
    "cuenta8": 9228,
    "cuenta9": 9229,
    "cuenta10": 9230,
    "cuenta11": 9231,
}

# ═══════════════════════════════════════════════════════════════════════════
# MAGIC LINKS - Ejemplo de URLs
# ═══════════════════════════════════════════════════════════════════════════

# Estos son EJEMPLOS. Reemplaza con los URLs reales del drop de Nike
magic_links = [
    "https://www.nike.cl/nstrike/checkout/cuenta2?token=magic_token_1",
    "https://www.nike.cl/nstrike/checkout/cuenta3?token=magic_token_2",
    "https://www.nike.cl/nstrike/checkout/cuenta4?token=magic_token_3",
    "https://www.nike.cl/nstrike/checkout/cuenta5?token=magic_token_4",
    "https://www.nike.cl/nstrike/checkout/cuenta6?token=magic_token_5",
    "https://www.nike.cl/nstrike/checkout/cuenta7?token=magic_token_6",
    "https://www.nike.cl/nstrike/checkout/cuenta8?token=magic_token_7",
    "https://www.nike.cl/nstrike/checkout/cuenta9?token=magic_token_8",
    "https://www.nike.cl/nstrike/checkout/cuenta10?token=magic_token_9",
    "https://www.nike.cl/nstrike/checkout/cuenta11?token=magic_token_10",
]

# ═══════════════════════════════════════════════════════════════════════════
# SCRIPT: Operación Frankenstein Completa
# ═══════════════════════════════════════════════════════════════════════════

"""
#!/usr/bin/env python3

import time
import threading
from runtime.bot_controller import BotController

# ╔════════════════════════════════════════════════════════════════╗
# ║ PASO 1: PREPARAR ZOMBIES (10 minutos antes del drop)         ║
# ╚════════════════════════════════════════════════════════════════╝

def prepare_zombies():
    \"\"\"T-600 seg: Abre 10 Chrome Zombies\"\"\"
    
    print("\\n🧟 [PASO 1] Preparando 10 Zombies...")
    print("="*70)
    
    accounts_config = {
        "cuenta2": 9222,
        "cuenta3": 9223,
        "cuenta4": 9224,
        "cuenta5": 9225,
        "cuenta6": 9226,
        "cuenta7": 9227,
        "cuenta8": 9228,
        "cuenta9": 9229,
        "cuenta10": 9230,
        "cuenta11": 9231,
    }
    
    threads = []
    for account, port in accounts_config.items():
        def _spawn(acc, p):
            controller = BotController(acc)
            if controller.spawn_zombie(p):
                print(f"  [{acc:15}] ✅ Puerto {p}")
            else:
                print(f"  [{acc:15}] ❌ Error")
        
        t = threading.Thread(target=_spawn, args=(account, port))
        threads.append(t)
        t.start()
    
    # Esperar a que terminen todos
    for t in threads:
        t.join()
    
    print("\\n✅ [PASO 1] Todos los Zombies están preparados")
    print("\\n⏳ Esperando 10 minutos...\n")


# ╔════════════════════════════════════════════════════════════════╗
# ║ PASO 2: VERIFICAR ZOMBIES (2 minutos antes del drop)          ║
# ╚════════════════════════════════════════════════════════════════╝

def check_zombies():
    \"\"\"T-120 seg: Verifica que todos responden\"\"\"
    
    print("\\n🔍 [PASO 2] Verificando Zombies...")
    print("="*70)
    
    accounts_config = {
        "cuenta2": 9222,
        "cuenta3": 9223,
        "cuenta4": 9224,
        "cuenta5": 9225,
        "cuenta6": 9226,
        "cuenta7": 9227,
        "cuenta8": 9228,
        "cuenta9": 9229,
        "cuenta10": 9230,
        "cuenta11": 9231,
    }
    
    alive_count = 0
    for account, port in accounts_config.items():
        controller = BotController(account)
        if controller.check_zombie_alive(port):
            print(f"  [{account:15}] ✅ VIVO")
            alive_count += 1
        else:
            print(f"  [{account:15}] ⚠️ NO RESPONDE")
    
    total = len(accounts_config)
    print(f"\\n📊 {alive_count}/{total} Zombies listos\\n")
    
    if alive_count < total:
        response = input("⚠️ ¿Continuar de todos modos? (s/n): ")
        if response.lower() != "s":
            print("Abortado.")
            return False
    
    return True


# ╔════════════════════════════════════════════════════════════════╗
# ║ PASO 3: DROP SINCRONIZADO (En el momento exacto)              ║
# ╚════════════════════════════════════════════════════════════════╝

def execute_drop():
    \"\"\"T-0 seg: Inyecta URLs mágicas en todos los Zombies\"\"\"
    
    print("\\n⚡ [PASO 3] DROP SINCRONIZADO")
    print("="*70)
    
    accounts_config = {
        "cuenta2": 9222,
        "cuenta3": 9223,
        "cuenta4": 9224,
        "cuenta5": 9225,
        "cuenta6": 9226,
        "cuenta7": 9227,
        "cuenta8": 9228,
        "cuenta9": 9229,
        "cuenta10": 9230,
        "cuenta11": 9231,
    }
    
    magic_links = [
        "https://www.nike.cl/nstrike/checkout/1?token=abc123",
        "https://www.nike.cl/nstrike/checkout/2?token=def456",
        "https://www.nike.cl/nstrike/checkout/3?token=ghi789",
        "https://www.nike.cl/nstrike/checkout/4?token=jkl012",
        "https://www.nike.cl/nstrike/checkout/5?token=mno345",
        "https://www.nike.cl/nstrike/checkout/6?token=pqr678",
        "https://www.nike.cl/nstrike/checkout/7?token=stu901",
        "https://www.nike.cl/nstrike/checkout/8?token=vwx234",
        "https://www.nike.cl/nstrike/checkout/9?token=yz5678",
        "https://www.nike.cl/nstrike/checkout/10?token=abc901",
    ]
    
    print("\\n🎯 Esperando comando de drop...")
    print(f"    Cuentas: {len(accounts_config)}")
    print(f"    Magic links: {len(magic_links)}")
    
    input("\\n🔴 Presiona ENTER en el EXACTO momento del drop:\\n")
    
    print("\\n🚀 ¡¡¡ EJECUTANDO DROP !!!")
    print("="*70)
    
    threads = []
    accounts_list = list(accounts_config.items())
    
    for i, (account, port) in enumerate(accounts_list):
        magic_link = magic_links[i % len(magic_links)]
        
        def _teleport(acc, p, link):
            controller = BotController(acc)
            success = controller.teleport_to_checkout(p, link)
            status = "✅" if success else "❌"
            print(f"  [{acc:15}] {status} Inyección completada")
        
        t = threading.Thread(target=_teleport, args=(account, port, magic_link))
        threads.append(t)
        t.start()
    
    # Esperar a que terminen todas las inyecciones
    for t in threads:
        t.join()
    
    print("\\n✅ [PASO 3] Todas las inyecciones completadas")
    print("\\n🎉 CHROME VOLÓ. Los 10 están cargando el checkout al unísono.\\n")


# ╔════════════════════════════════════════════════════════════════╗
# ║ MAIN: Orquesta todo
# ╚════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    
    print("\\n" + "="*70)
    print("🔥 FRANKENSTEIN - OPERACIÓN 10 CUENTAS")
    print("="*70)
    
    # Paso 1: Preparar
    prepare_zombies()
    
    # Esperar 10 minutos (comentar para pruebas rápidas)
    # time.sleep(600)
    
    # Para pruebas: esperar solo 5 segundos
    print("(DEMO: esperando 5 segundos en lugar de 10 minutos)")
    time.sleep(5)
    
    # Paso 2: Verificar
    if not check_zombies():
        print("Abortado.")
        exit(1)
    
    # Paso 3: DROP
    execute_drop()
    
    print("\\n" + "="*70)
    print("🏁 OPERACIÓN COMPLETADA")
    print("="*70)
    print("\\nSiguientes pasos:")
    print("- Los Chrome deberían estar cargando el checkout")
    print("- Monitorea el proceso en tiempo real")
    print("- Cierra los Chrome cuando termines")
    print()
"""

# ═══════════════════════════════════════════════════════════════════════════
# ARCHIVO: links.txt
# ═══════════════════════════════════════════════════════════════════════════

# Crea un archivo "links.txt" en el mismo directorio con:

"""
https://www.nike.cl/nstrike/checkout/cuenta2?token=magic_token_1
https://www.nike.cl/nstrike/checkout/cuenta3?token=magic_token_2
https://www.nike.cl/nstrike/checkout/cuenta4?token=magic_token_3
https://www.nike.cl/nstrike/checkout/cuenta5?token=magic_token_4
https://www.nike.cl/nstrike/checkout/cuenta6?token=magic_token_5
https://www.nike.cl/nstrike/checkout/cuenta7?token=magic_token_6
https://www.nike.cl/nstrike/checkout/cuenta8?token=magic_token_7
https://www.nike.cl/nstrike/checkout/cuenta9?token=magic_token_8
https://www.nike.cl/nstrike/checkout/cuenta10?token=magic_token_9
https://www.nike.cl/nstrike/checkout/cuenta11?token=magic_token_10
"""

# ═══════════════════════════════════════════════════════════════════════════
# USO DIRECTO: frankenstein_army.py
# ═══════════════════════════════════════════════════════════════════════════

# Opción 1: Usar frankenstein_army.py (Recomendado)
"""
# Paso 1: Preparar 10 Zombies
python frankenstein_army.py prepare --count 10 --start-port 9222 --accounts cuenta2,cuenta3,cuenta4,cuenta5,cuenta6,cuenta7,cuenta8,cuenta9,cuenta10,cuenta11

# Paso 2: Verificar
python frankenstein_army.py check --count 10 --start-port 9222

# Paso 3: DROP
python frankenstein_army.py drop --count 10 --start-port 9222 --magic-link-file links.txt
"""

# ═══════════════════════════════════════════════════════════════════════════
# NOTAS IMPORTANTES
# ═══════════════════════════════════════════════════════════════════════════

"""
1. CUENTAS
   - Cada cuenta necesita perfil con cookies de Nike
   - Archivo .login_ok en auth/cuentaX/

2. PUERTOS
   - Cada puerto debe ser ÚNICO (9222-9231 en este ejemplo)
   - Máximo: 178 puertos disponibles (9222-9399)

3. MAGIC LINKS
   - Reemplaza con URLs reales del drop
   - Uno por cuenta
   - Deben tener formato de checkout válido

4. TIMING
   - T-600: python frankenstein_army.py prepare
   - T-120: python frankenstein_army.py check
   - T-0:   python frankenstein_army.py drop
          (presiona ENTER en el momento exacto)

5. MONITOREO
   - Los Chrome se abrirán automáticamente
   - Estarán cargando el checkout
   - Monitorea en tiempo real
"""

# ═══════════════════════════════════════════════════════════════════════════
# ⚠️  REQUISITOS
# ═══════════════════════════════════════════════════════════════════════════

"""
✅ Instalado:
   pip install websocket-client requests

✅ Tests pasando:
   python test_frankenstein.py

✅ Perfiles existentes:
   auth/cuenta2/, auth/cuenta3/, ..., auth/cuenta11/
   Cada uno con .login_ok

✅ Puertos libres:
   9222-9231 (para 10 cuentas)

✅ Chrome instalado
   tasklist | findstr chrome (debe listar chrome)
"""
