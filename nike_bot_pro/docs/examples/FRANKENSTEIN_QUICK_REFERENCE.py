#!/usr/bin/env python3
"""
🔥 FRANKENSTEIN - QUICK REFERENCE

Referencia rápida de comandos y código para la Inyección Frankenstein.
"""

# ═══════════════════════════════════════════════════════════════════════════
# 1️⃣  INSTALACIÓN (30 segundos)
# ═══════════════════════════════════════════════════════════════════════════

# En terminal:
"""
pip install websocket-client requests
"""

# ═══════════════════════════════════════════════════════════════════════════
# 2️⃣  TESTS (1 minuto)
# ═══════════════════════════════════════════════════════════════════════════

# En terminal:
"""
python test_frankenstein.py
# Resultado esperado: 6/6 PASS
"""

# ═══════════════════════════════════════════════════════════════════════════
# 3️⃣  USO SIMPLE (1 cuenta)
# ═══════════════════════════════════════════════════════════════════════════

"""
# Paso 1: Importar
from runtime.bot_controller import BotController

# Paso 2: Crear controlador
controller = BotController("cuenta2")

# Paso 3: Preparar Zombie (10 min antes del drop)
controller.spawn_zombie(9222)

# Paso 4: Verificar que está vivo
if controller.check_zombie_alive(9222):
    print("✅ Listo para inyectar")

# Paso 5: Inyectar (en el momento del drop)
magic_link = "https://www.nike.cl/nstrike/checkout/...?token=xyz"
controller.teleport_to_checkout(9222, magic_link)
"""

# ═══════════════════════════════════════════════════════════════════════════
# 4️⃣  USO AVANZADO (10+ cuentas)
# ═══════════════════════════════════════════════════════════════════════════

"""
# Terminal - Preparación (T-Minus 10 minutos)
python frankenstein_army.py prepare --count 10 --start-port 9222

# Terminal - Verificación (T-Minus 2 minutos)
python frankenstein_army.py check --count 10 --start-port 9222

# Terminal - DROP (T-Minus 0 segundos)
python frankenstein_army.py drop --count 10 --start-port 9222 --magic-link-file links.txt
# → Script pide que presiones ENTER
# → Presiona ENTER
# → ⚡ TODOS los Chrome cargan al checkout INSTANTÁNEAMENTE
"""

# ═══════════════════════════════════════════════════════════════════════════
# 5️⃣  CÓDIGO DE INTEGRACIÓN CON UI
# ═══════════════════════════════════════════════════════════════════════════

"""
import threading
from runtime.bot_controller import BotController

class MiBot:
    def __init__(self):
        self.accounts = ["cuenta2", "cuenta3", "cuenta4"]
        self.controllers = {}
        self.magic_link = None
    
    # BOTÓN 1: "Preparar Zombies"
    def on_btn_prepare_click(self):
        # Lanzar en thread para no bloquear UI
        threading.Thread(target=self._prepare, daemon=True).start()
    
    def _prepare(self):
        print("🧟 Preparando Zombies...")
        for i, account in enumerate(self.accounts):
            port = 9222 + i
            controller = BotController(account)
            self.controllers[account] = (controller, port)
            
            if controller.spawn_zombie(port):
                print(f"  [{account}] ✅ Puerto {port}")
            else:
                print(f"  [{account}] ❌ Error")
        
        print("✅ Todos los Zombies están listos")
    
    # BOTÓN 2: "Obtener Magic Link" (del sitio de Nike)
    def on_btn_get_link_click(self):
        # Aquí va lógica para obtener el link mágico
        # Por ahora, placeholder
        self.magic_link = "https://nike.cl/nstrike/..."
        print(f"🔗 Magic link: {self.magic_link}")
    
    # BOTÓN 3: "DROP AHORA"
    def on_btn_drop_click(self):
        if not self.magic_link:
            print("❌ Primero obtén el magic link")
            return
        
        print("🚀 EJECUTANDO DROP...")
        for account, (controller, port) in self.controllers.items():
            # Lanzar en thread para simultaneidad
            threading.Thread(
                target=controller.teleport_to_checkout,
                args=(port, self.magic_link),
                daemon=True
            ).start()
        
        print("⚡ Todas las inyecciones lanzadas")
"""

# ═══════════════════════════════════════════════════════════════════════════
# 6️⃣  DEBUGGING RÁPIDO
# ═══════════════════════════════════════════════════════════════════════════

"""
# Ver si Chrome está abierto
tasklist | findstr chrome

# Ver si el puerto está escuchando
netstat -ano | findstr :9222

# Ver qué está en el puerto 9222
curl http://127.0.0.1:9222/json

# Verificar que la librería está instalada
python -c "import websocket; print('OK')"

# Ejecutar demo interactiva
python frankenstein_demo.py --help
"""

# ═══════════════════════════════════════════════════════════════════════════
# 7️⃣  FUNCIONES CORE (Quick API)
# ═══════════════════════════════════════════════════════════════════════════

"""
# Desde dirty_tools:
from engines.dirty_tools import (
    spawn_zombie_chrome,
    teleport_chrome,
    kill_zombie_chrome,
    get_zombie_status
)

# Spawn
spawn_zombie_chrome("auth/cuenta2/profile_run", 9222)

# Check status
status = get_zombie_status(9222)
if status:
    print(f"✅ Vivo ({len(status['tabs'])} pestañas)")
else:
    print("❌ No responde")

# Teleport
teleport_chrome(9222, "https://nike.cl/nstrike/...")

# Kill
kill_zombie_chrome(9222)
"""

# ═══════════════════════════════════════════════════════════════════════════
# 8️⃣  CONFIGURACIÓN PUERTOS
# ═══════════════════════════════════════════════════════════════════════════

"""
# Puerto por cuenta:
Cuenta 2  → Puerto 9222
Cuenta 3  → Puerto 9223
Cuenta 4  → Puerto 9224
...
Cuenta N  → Puerto 9222 + (N - 2)

# Máximo de cuentas:
Puertos disponibles: 9222 - 9399
Total: 178 puertos / 178 máximo cuentas
"""

# ═══════════════════════════════════════════════════════════════════════════
# 9️⃣  TIMELINE TÍPICO DE DROP
# ═══════════════════════════════════════════════════════════════════════════

"""
T-600 seg (10 minutos antes):
└─ python frankenstein_army.py prepare --count 10 --start-port 9222
   └─ 10 Chrome Zombies se abren en about:blank

T-300 seg:
└─ Espera, navega manualmente en los Chrome si lo deseas

T-10 seg (2 minutos antes):
└─ python frankenstein_army.py check --count 10 --start-port 9222
   └─ Verificas que todos responden (✅ TODOS VIVOS)

T-0 seg (EXACTO):
└─ python frankenstein_army.py drop --count 10 --start-port 9222 --magic-link-file links.txt
   └─ Script pide que presiones ENTER
   └─ Presionas ENTER
   └─ ⚡ 10 Chrome se teletransportan al checkout INSTANTÁNEAMENTE
   └─ 🚀 SUCCESS
"""

# ═════════════════════════════════════════════════════════════════════════════
# 🔟 COMANDOS ÚTILES (Copy-Paste)
# ═════════════════════════════════════════════════════════════════════════════

# Preparar 3 cuentas
CMD_PREPARE_3 = """python frankenstein_army.py prepare --count 3 --start-port 9222"""

# Preparar 10 cuentas
CMD_PREPARE_10 = """python frankenstein_army.py prepare --count 10 --start-port 9222"""

# Verificar 3 cuentas
CMD_CHECK_3 = """python frankenstein_army.py check --count 3 --start-port 9222"""

# DROP con archivo de links
CMD_DROP = """python frankenstein_army.py drop --count 10 --start-port 9222 --magic-link-file links.txt"""

# Demo interactiva
CMD_DEMO = """python frankenstein_demo.py cuenta2 9222"""

# Tests
CMD_TEST = """python test_frankenstein.py"""

# ═════════════════════════════════════════════════════════════════════════════
# ERRORES COMUNES Y SOLUCIONES
# ═════════════════════════════════════════════════════════════════════════════

"""
ERROR: ModuleNotFoundError: No module named 'websocket'
SOLUCIÓN: pip install websocket-client

ERROR: Port 9222 already in use
SOLUCIÓN: taskkill /PID <pid> /F  (o usa otro puerto)

ERROR: Chrome no responde en puerto 9222
SOLUCIÓN: 
  1. Verifica: tasklist | findstr chrome
  2. Espera 5 segundos
  3. Intenta de nuevo

ERROR: Inyección falla después de teleport
SOLUCIÓN:
  1. Verifica: python frankenstein_demo.py --check 9222
  2. Si NO RESPONDE: Chrome no está listo
  3. Si SÍ RESPONDE: URL mágica puede ser inválida

ERROR: Solo funciona 1 cuenta, las otras fallan
SOLUCIÓN:
  1. Asegurar que cada puerto es ÚNICO
  2. Asegurar que cada perfil EXISTE
  3. Ejecutar: python test_frankenstein.py (diagnóstico)
"""

# ═════════════════════════════════════════════════════════════════════════════
# DOCUMENTACIÓN COMPLETA
# ═════════════════════════════════════════════════════════════════════════════

"""
📖 GUÍAS DISPONIBLES:

1. FRANKENSTEIN_QUICK_START.md
   - Guía de 30 minutos para empezar
   - Ejemplos paso a paso
   - Casos de uso simples

2. FRANKENSTEIN_TECHNICAL_REFERENCE.md
   - Referencia técnica profunda
   - Cómo funciona CDP
   - Debugging avanzado

3. FRANKENSTEIN_IMPLEMENTATION.md
   - Detalles de implementación
   - Archivos creados
   - Arquitectura

4. FRANKENSTEIN_RESUMEN_EJECUTIVO.md
   - Resumen ejecutivo
   - Métricas
   - Tests
"""

# ═════════════════════════════════════════════════════════════════════════════
# ⚡ TL;DR (Too Long; Didn't Read)
# ═════════════════════════════════════════════════════════════════════════════

"""
1. Instala:      pip install websocket-client requests
2. Verifica:     python test_frankenstein.py
3. Prepara:      python frankenstein_army.py prepare --count 10
4. Verifica:     python frankenstein_army.py check --count 10
5. DROP:         python frankenstein_army.py drop --count 10 --magic-link-file links.txt
6. Presiona:     ENTER en el script

✅ HECHO. Chrome voló. 🚀
"""

print(__doc__)
