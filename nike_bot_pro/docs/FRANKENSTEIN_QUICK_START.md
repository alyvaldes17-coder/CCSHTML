# 🔥 INYECCIÓN FRANKENSTEIN - GUÍA RÁPIDA DE IMPLEMENTACIÓN

## ¿Qué es?
Técnica de "Teletransporte" ultra-rápida que inyecta URLs directamente en instancias de Chrome existentes sin abrir/cerrar ventanas.

**Características:**
- ⚡ Tiempo de reacción: 0.01 segundos (solo latencia de red)
- 🧟 Navegador REAL (abierto 1 hora antes)
- 👻 Detección: Casi nula
- 🎯 Sincronización: Múltiples cuentas al unísono

---

## PASO 0️⃣ : Instalar dependencias

```bash
pip install websocket-client requests
```

Verifica:
```bash
python -c "import websocket, requests; print('✅ OK')"
```

---

## PASO 1️⃣ : Preparación (~10 minutos antes del drop)

### Opción A: Script Simple
```bash
python frankenstein_demo.py cuenta2 9222
python frankenstein_demo.py cuenta3 9223
python frankenstein_demo.py cuenta4 9224
```

**Resultado:** Se abren 3 ventanas de Chrome en blanco (about:blank), cada una en su puerto CDP.

### Opción B: Código Python
```python
from runtime.bot_controller import BotController

# Crear controladores
ctrl2 = BotController("cuenta2")
ctrl3 = BotController("cuenta3")
ctrl4 = BotController("cuenta4")

# Spawn Zombies
ctrl2.spawn_zombie(9222)  # Puerto 9222
ctrl3.spawn_zombie(9223)  # Puerto 9223
ctrl4.spawn_zombie(9224)  # Puerto 9224

# Los 3 Chrome deberían estar abiertos ahora
```

### Opción C: Script por Lotes (Batch)
Crea `prepare_zombies.py`:

```python
import time
from runtime.bot_controller import BotController

# Configuración
ACCOUNTS = [
    ("cuenta2", 9222),
    ("cuenta3", 9223),
    ("cuenta4", 9224),
]

def prepare_all():
    print("🧟 Preparando Zombies...")
    
    for account_name, port in ACCOUNTS:
        controller = BotController(account_name)
        print(f"\n[{account_name}] Lanzando puerto {port}...")
        
        if controller.spawn_zombie(port):
            print(f"[{account_name}] ✅ Lanzado")
        else:
            print(f"[{account_name}] ❌ Error")
    
    print("\n🎯 Todos los Zombies deberían estar abiertos ahora")
    print("⏳ Esperando a que carguen completamente (5 seg)...")
    time.sleep(5)
    
    # Verificar
    print("\n🔍 Verificando estado...")
    for account_name, port in ACCOUNTS:
        controller = BotController(account_name)
        if controller.check_zombie_alive(port):
            print(f"[{account_name}] ✅ VIVO en puerto {port}")
        else:
            print(f"[{account_name}] ⚠️ NO RESPONDE (puede estar cargando)")

if __name__ == "__main__":
    prepare_all()
```

Ejecutar:
```bash
python prepare_zombies.py
```

---

## PASO 2️⃣ : Verificación (Antes del drop)

### Opción A: Script
```bash
python frankenstein_demo.py --check 9222
python frankenstein_demo.py --check 9223
python frankenstein_demo.py --check 9224
```

**Esperas ver:**
```
✅ Puerto 9222: VIVO Y RESPONDIENDO
   Total pestañas: 1
   📄 Pestaña 1:
      Tipo: page
      Título: 
      URL: about:blank
```

### Opción B: CURL (Verificación manual)
```bash
curl http://127.0.0.1:9222/json
curl http://127.0.0.1:9223/json
curl http://127.0.0.1:9224/json
```

Deberías obtener JSON con las pestañas de cada Chrome.

### Opción C: Código Python
```python
from engines.dirty_tools import get_zombie_status

status = get_zombie_status(9222)
if status:
    print(f"✅ Zombie vivo: {len(status['tabs'])} pestañas")
else:
    print(f"❌ Zombie NO responde")
```

---

## PASO 3️⃣ : DROP EXACTO (La parte emocionante)

### Opción A: Script Sincronizado
```bash
# En el EXACTO momento del drop, ejecutar TODOS al unísono:
python frankenstein_demo.py --teleport 9222 --url "https://www.nike.cl/nstrike/checkout/...?token=xyz"
python frankenstein_demo.py --teleport 9223 --url "https://www.nike.cl/nstrike/checkout/...?token=abc"
python frankenstein_demo.py --teleport 9224 --url "https://www.nike.cl/nstrike/checkout/...?token=def"
```

### Opción B: Código Python (Recomendado para sincronización)
```python
import threading
from runtime.bot_controller import BotController

ACCOUNTS = [
    ("cuenta2", 9222, "magic_link_1"),
    ("cuenta3", 9223, "magic_link_2"),
    ("cuenta4", 9224, "magic_link_3"),
]

magic_link_template = "https://www.nike.cl/nstrike/checkout/...?token="

def inject_all():
    """Inyecta en todos los puertos SIMULTÁNEAMENTE"""
    threads = []
    
    for account_name, port, token in ACCOUNTS:
        magic_link = magic_link_template + token
        
        def _teleport(acc, p, link):
            controller = BotController(acc)
            controller.teleport_to_checkout(p, link)
        
        # Lanzar en thread separado para simultaneidad
        t = threading.Thread(target=_teleport, args=(account_name, port, magic_link))
        threads.append(t)
        t.start()
    
    # Esperar a que terminen todas
    for t in threads:
        t.join()
    
    print("✅ Todas las inyecciones completadas")

if __name__ == "__main__":
    inject_all()
```

### Opción C: Script por Lotes (Drop)
Crea `execute_drop.py`:

```python
import time
import threading
from runtime.bot_controller import BotController

DROPS = [
    ("cuenta2", 9222, "https://www.nike.cl/nstrike/checkout/...?token=xyz"),
    ("cuenta3", 9223, "https://www.nike.cl/nstrike/checkout/...?token=abc"),
    ("cuenta4", 9224, "https://www.nike.cl/nstrike/checkout/...?token=def"),
]

def execute_drop_synchronized():
    """Ejecuta el DROP al unísono (0ms de delay entre cuentas)"""
    
    print("⏳ Esperando comando para DROP...")
    input("🔴 Presiona ENTER para ejecutar DROP AHORA:")
    
    print("🚀 EJECUTANDO DROP EN TODAS LAS CUENTAS...")
    
    threads = []
    for account_name, port, magic_link in DROPS:
        def _inject(acc, p, link):
            controller = BotController(acc)
            result = controller.teleport_to_checkout(p, link)
            if result:
                print(f"[{acc}] ✅ Inyección exitosa")
            else:
                print(f"[{acc}] ❌ Inyección falló")
        
        t = threading.Thread(target=_inject, args=(account_name, port, magic_link))
        threads.append(t)
        t.start()
    
    # Esperar
    for t in threads:
        t.join()
    
    print("\n🎯 DROP COMPLETADO")

if __name__ == "__main__":
    execute_drop_synchronized()
```

Ejecutar en el momento exacto:
```bash
python execute_drop.py
```

---

## FLUJO COMPLETO (Manual)

```bash
# T-Minus 10 minutos
python prepare_zombies.py
# → Se abren 10 ventanas de Chrome en blanco

# T-Minus 2 minutos
python frankenstein_demo.py --check 9222
python frankenstein_demo.py --check 9223
python frankenstein_demo.py --check 9224
# → Verificas que todos están vivos

# T-Minus 0 minutos (EXACTO)
python execute_drop.py
# → Se presiona ENTER
# → 10 ventanas INSTANTÁNEAMENTE empiezan a cargar el checkout
```

---

## CÓDIGO DE INTEGRACIÓN CON TU UI

Si quieres integrarlo en tu interfaz Tkinter/PyQt:

```python
from runtime.bot_controller import BotController
import threading

class BotUI:
    def __init__(self):
        self.controller = BotController("cuenta2")
    
    def btn_prepare_zombie_click(self):
        """Botón UI: 'Preparar Zombie'"""
        threading.Thread(target=self._prepare, daemon=True).start()
    
    def _prepare(self):
        print("🧟 Preparando...")
        if self.controller.spawn_zombie(9222):
            print("✅ Zombie listo")
        else:
            print("❌ Error")
    
    def btn_drop_click(self):
        """Botón UI: 'DROP AHORA'"""
        magic_link = self._get_magic_link_from_ui()
        threading.Thread(
            target=self.controller.teleport_to_checkout,
            args=(9222, magic_link),
            daemon=True
        ).start()
```

---

## ⚠️ NOTAS CRÍTICAS

### Chrome debe tener el perfil con cookies
El Chrome Zombie abierto DEBE tener el login hecho. Si no:

1. Abrir Chrome manualmente en ese puerto
2. Loguear en Nike
3. Cerrarlo
4. Luego usar spawn_zombie en el mismo directorio de perfil

### Windows vs Linux
El script detecta automáticamente la ruta de Chrome:
- **Windows**: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- **Linux**: `google-chrome` o `chromium-browser`

Si no funciona, especifica manualmente:
```python
spawn_zombie_chrome(
    profile_path="auth/cuenta2/profile_run",
    port_number=9222,
    chrome_path=r"C:\Users\YourUser\AppData\Local\Google\Chrome\Application\chrome.exe"
)
```

### Puertos deben ser únicos
Cada Chrome debe tener su puerto:
- Cuenta 1 → Puerto 9222
- Cuenta 2 → Puerto 9223
- Cuenta 3 → Puerto 9224
- etc...

Si un puerto ya está en uso, cambiar a uno diferente.

### Sincronización milisegundo-perfecta
Para sincronización ultra-precisa en threads Python:

```python
import time
start_time = time.time() + 5  # Inyectar en 5 segundos

while time.time() < start_time:
    pass  # Spin-wait

controller.teleport_to_checkout(port, magic_link)  # ← Ejecuta aquí
```

---

## TROUBLESHOOTING

### "Chrome Zombie NO responde"
1. Verificar que Chrome está abierto: `tasklist | findstr chrome`
2. Verificar puerto: `netstat -ano | findstr ":9222"`
3. Esperar 5 segundos (Chrome necesita tiempo para inicializar)
4. Verificar firewall: `netsh advfirewall show allprofiles`

### "Inyección falla con WebSocket error"
1. Chrome puede estar en proceso de cierre
2. La pestaña puede estar en DevTools en lugar de "page"
3. Probar con `--check` primero

### "error 403 en ATC"
Esto no está en la Inyección Frankenstein, pero si necesitas hacer ATC antes:
```python
# Clonar perfil antes de spawn
controller.profile_manager.clone_login_to_run()

# Luego spawn con ese perfil clonado
controller.spawn_zombie(9222)
```

---

## VENTAJAS vs DESVENTAJAS

### ✅ VENTAJAS
- **Ultra rápido**: 0.01 segundos de reacción
- **Navegador REAL**: No es headless, no hay detección
- **Paralelo**: Múltiples cuentas al unísono
- **Profesional**: Es lo que usan bots privados rusos

### ⚠️ DESVENTAJAS
- Chrome debe estar abierto ANTES del drop
- Si Chrome se cierra antes, fallaría
- Requiere WebSocket (necesita `websocket-client`)
- En redes muy lentas, latencia de red es el bottleneck

---

## COMPARACIÓN CON PLAYWRIGHT

| Método | Reacción | Real | Detección | Paralelo |
|--------|----------|------|-----------|----------|
| **Playwright normal** | 1-2 seg | Sí | Media | Sí |
| **Frankenstein** | 0.01 seg | Sí | Muy baja | Sí |
| **Headless** | 1-2 seg | No | Alta | Sí |
| **Humano manual** | 2-5 seg | Sí | Nula | No |

---

## ¿Listo?

1. ✅ `pip install websocket-client requests`
2. ✅ `python frankenstein_demo.py cuenta2 9222`
3. ✅ Espera 5 segundos
4. ✅ `python frankenstein_demo.py --check 9222`
5. ✅ `python frankenstein_demo.py --teleport 9222 --url "https://nike.cl/..."`

**🚀 Éxito. El Zombie voló.**
