# 🎮 GUÍA DE CONFIGURACIÓN: Modo Un Jugador vs Modo Ejército

## 📊 Estructura de Carpetas (El Cuartel)

```
nike_bot_pro/
│
├── auth/                          🪖 CUARTEL (Aquí viven las cuentas)
│   ├── cuenta1/                   ├─ Soldado 1
│   │   └── profile_pw/            │  └─ Cookies/sesión de Nike
│   ├── cuenta2/                   ├─ Soldado 2
│   │   └── profile_pw/            │  └─ Cookies/sesión de Nike
│   ├── cuenta_hermano/            ├─ Soldado 3
│   │   └── profile_pw/            │  └─ Cookies/sesión de Nike
│   ├── cuenta_mama/               ├─ Soldado 4
│   │   └── profile_pw/            │  └─ Cookies/sesión de Nike
│   └── discord_session/           └─ El Espía (sesión Discord aparte)
│
├── core/                          ⚙️ PIEZAS CORE
│   ├── account_state.py
│   ├── bot_state.py
│   └── ...
│
├── engines/                       🔧 MOTORES
│   ├── playwright_engine_v2.py    ├─ Abre Chrome (original)
│   └── playwright_engine_v3.py    └─ Reutiliza Chrome (Glotón)
│
├── runtime/                       🧠 CEREBROS
│   └── bot_controller.py          └─ Controla 1 cuenta
│
├── ui/                            🎨 INTERFAZ
│   └── app.py                     └─ Modo Manual (Un Jugador)
│
├── main.py                        ▶️ MODO UN JUGADOR (Testing)
├── main_army.py                   🪖 MODO EJÉRCITO (Producción)
├── login_runner.py                🔐 Script de LOGIN (subprocess)
│
└── ESTRUCTURA_CONFIGURACION.md    📖 Este archivo
```

---

## 🎮 MODO 1: Un Jugador (Testing Manual)

### ¿Cuándo usarlo?
- ✅ Quieres probar una sola cuenta
- ✅ Desarrollo y debugging
- ✅ Aprender cómo funciona
- ✅ Interfaz gráfica (CustomTkinter)

### Cómo ejecutar

```bash
python main.py
```

### Qué pasa
1. Interfaz gráfica se abre (CustomTkinter)
2. Cargas tus cuentas desde `accounts.json`
3. Puedes hacer LOGIN/PLAY manualmente con botones
4. UNA sola cuenta a la vez
5. Logs en tiempo real

### Estructura de código

```python
# main.py
from ui.app import AppUI
from manager.account_manager import AccountManager

# Carga JSON con tus cuentas
manager = AccountManager()

# Interfaz gráfica
app = AppUI(manager)
app.run()
```

### Requisitos
- CustomTkinter instalado
- `accounts.json` configurado correctamente
- Cuenta con `auth/cuenta2/profile_pw/` lista

---

## 🪖 MODO 2: Ejército (Producción Multi-Cuenta)

### ¿Cuándo usarlo?
- ✅ Drop competido
- ✅ Máxima probabilidad (5 cuentas = 5x más)
- ✅ Velocidad
- ✅ SIN interfaz gráfica (consola pura)

### Cómo ejecutar

```bash
python main_army.py
```

### Qué pasa
1. Script escanea `auth/` automáticamente
2. Carga TODAS las subcarpetas (cada = 1 cuenta)
3. Menu interactivo:
   ```
   1. Listar soldados        # Ver todas las cuentas
   2. Estado general         # Estado de cada una
   3. LOGIN masivo           # Loguear todas simultáneamente
   4. Ataque coordinado      # Lanzar ataque (ingresa SKU)
   5. Drop simulado          # Para testing
   6. Salir
   ```

### Estructura de código

```python
# main_army.py
from runtime.bot_controller import BotController

class Ejercito:
    def reclutar(self):
        # Escanea auth/ y crea BotController para cada
        for nombre in os.listdir(self.auth_path):
            bot = BotController(nombre, ruta_perfil)
            self.soldados.append(bot)
    
    def loguear_todo(self):
        # Loguea TODAS simultáneamente en threads
        
    def ataque_coordinado(self, sku):
        # Lanzar TODOS con mismo SKU en paralelo

app = Ejercito()
app.reclutar()
app.loguear_todo()  # Si necesitas
app.ataque_coordinado("12345")  # Cuando cae el drop
```

### Requisitos
- Múltiples cuentas en `auth/`
- Cada una con su `profile_pw/` con sesión válida
- NO necesita CustomTkinter
- NO necesita `accounts.json`

---

## ⚙️ CONFIGURACIÓN PASO A PASO

### Paso 1: Crear estructura auth/ (Reclutar Soldados)

```bash
# La estructura básica ya debe existir
auth/
├── cuenta1/
│   └── profile_pw/      ← Aquí van las cookies de Nike
├── cuenta2/             ← Ya la tienes funcionando
│   └── profile_pw/
└── discord_session/     ← Sesión Discord (aparte)
```

### Paso 2: Generar profile_pw para cada cuenta

**Opción A: Usar main.py (Manual)**

```bash
1. python main.py
2. En la interfaz, cambiar cuenta manualmente
   (Editar el código o accounts.json para apuntar a cuenta_hermano)
3. Presionar LOGIN
4. Loguear manualmente en Nike
5. Chrome se cierra → Cookies guardadas en auth/cuenta_hermano/profile_pw/
6. Repetir para cada cuenta
```

**Opción B: Script de prueba rápida (Recomendado)**

Crear `setup_cuentas.py`:

```python
#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from runtime.bot_controller import BotController

# Cuentas a crear
CUENTAS = [
    "cuenta1",
    "cuenta2", 
    "cuenta_hermano",
    "cuenta_mama",
]

print("Inicializando cuentas...")

for nombre_cuenta in CUENTAS:
    profile_path = f"auth/{nombre_cuenta}/profile_pw"
    
    # Crear carpeta si no existe
    Path(profile_path).mkdir(parents=True, exist_ok=True)
    
    # Crear controller
    bot = BotController(nombre_cuenta, profile_path)
    
    print(f"\n{nombre_cuenta}: Lanzando LOGIN...")
    
    # Lanzar login en subprocess
    process = subprocess.Popen([
        sys.executable,
        "login_runner.py",
        profile_path
    ])
    
    # Esperar a que termine
    process.wait()
    
    # Validar
    if bot.validate_session_real():
        print(f"✅ {nombre_cuenta}: Sesión guardada correctamente")
    else:
        print(f"⚠️ {nombre_cuenta}: Validación pendiente")

print("\n✅ Todas las cuentas inicializadas")
```

Ejecutar:
```bash
python setup_cuentas.py
# Se abre Chrome para cada cuenta, loguea manualmente en cada una
```

### Paso 3: Verificar configuración

```bash
python main_army.py

# Opción 1: Listar soldados
1

# Debería mostrar:
📋 ESTADO DEL EJÉRCITO
1. cuenta1          → ❌ No logueado
2. cuenta2          → ✅ Listo para PLAY
3. cuenta_hermano   → ❌ No logueado
4. cuenta_mama      → ❌ No logueado
```

---

## 🚀 FLUJO REAL DE BATALLA

### Escenario: Drop está próximo (Tu estrategia)

```bash
# DÍA 1 (Preparación - 1 hora antes del drop)
$ python main_army.py

⚔️  COMANDO DEL EJÉRCITO
🪖 RECLUTANDO EJÉRCITO...
  🪖 Reclutando: cuenta1
  🪖 Reclutando: cuenta2
  🪖 Reclutando: cuenta_hermano
  🪖 Reclutando: cuenta_mama
✅ Ejército listo: 4 cuentas

⚔️  COMANDO DEL EJÉRCITO
1. Listar soldados
2. Estado general
3. LOGIN masivo
4. Ataque coordinado
5. Drop simulado
6. Salir

# Opción 3: Loguear todas simultáneamente
> 3

🔐 LOGUEO MASIVO
Loguendo 4 cuentas simultáneamente...

[cuenta1] 🔐 LOGIN iniciado...
[cuenta2] 🔐 LOGIN iniciado...
[cuenta_hermano] 🔐 LOGIN iniciado...
[cuenta_mama] 🔐 LOGIN iniciado...

# Se abren 4 Chromes a la vez
# Tú logueas manualmente en cada una (rápido, ~5 segundos por cuenta)

[cuenta1] ✅ READY
[cuenta2] ✅ READY
[cuenta_hermano] ✅ READY
[cuenta_mama] ✅ READY

✅ Logueo masivo completado
```

```bash
# DÍA 2 (El Drop - Es ahora!)
$ python main_army.py
✅ Ejército listo: 4 cuentas

# Opción 2: Ver estado rápido
> 2

📊 REPORTE GENERAL
Total cuentas:        4
  ✅ READY:           4
  🔄 Loguando:        0
  ❌ Sin autenticar:  0

🟢 Ejército LISTO PARA COMBATE

# Opción 4: ATAQUE COORDINADO
> 4

Ingresa SKU: 123456

🔥 ¡ORDEN DE ATAQUE RECIBIDA!
Objetivo: SKU 123456
Fuego: 4 cuentas

🚀 Lanzando ataque con 4 cuentas...

[cuenta1] 🎯 Atacando SKU 123456...
[cuenta2] 🎯 Atacando SKU 123456...
[cuenta_hermano] 🎯 Atacando SKU 123456...
[cuenta_mama] 🎯 Atacando SKU 123456...

# Las 4 monitorean SIMULTÁNEAMENTE
# Cuando alguna detecta precio:

[cuenta2] 🎯 PRECIO DETECTADO
[cuenta2] 📌 PRICE_LOCKED
[cuenta2] 🚀 EJECUTANDO
# Chrome se abre para cuenta2 → checkout → pago

# En segundo 2:
[cuenta_hermano] 🎯 PRECIO DETECTADO
[cuenta_hermano] 🚀 EJECUTANDO
# Chrome se abre para cuenta_hermano

# RESULTADO: Múltiples órdenes creadas simultáneamente
# Probabilidad: 4x más que con 1 sola cuenta
```

---

## 📋 CHECKLIST DE CONFIGURACIÓN

### Pre-Drop (Preparación)
- [ ] Tienes 2+ cuentas Nike diferentes
- [ ] Cada cuenta tiene su carpeta en `auth/`
- [ ] Cada carpeta tiene `profile_pw/` con sesión guardada
- [ ] `main_army.py` presente en raíz
- [ ] `login_runner.py` presente en raíz
- [ ] `python main_army.py` muestra todas las cuentas

### Post-Logueo (Antes del drop)
- [ ] Ejecutas `python main_army.py`
- [ ] Opción 3: LOGIN masivo (4 Chromes se abren)
- [ ] Logueas en cada una
- [ ] Opción 2: Estado general muestra READY en todas

### El Drop (En el momento)
- [ ] Tienes `main_army.py` abierto
- [ ] Obtienes SKU del drop
- [ ] Opción 4: Ingresa SKU
- [ ] Todas las cuentas atacan en paralelo
- [ ] (Esperanza) Una de ellas gana la orden

---

## 🔧 TROUBLESHOOTING

### "Reclutando 0 cuentas"
```bash
# Verificar estructura:
$ ls auth/
cuenta1/  cuenta2/  discord_session/

$ ls auth/cuenta1/
profile_pw/  # Debe existir
```

### "Estado: ❌ No logueado en todas"
```bash
# Hacer LOGIN masivo (opción 3)
# Si Chrome no abre → revisar login_runner.py
# Si Chrome abre pero no loguea → problema de Nike, not this bot
```

### "Chrome se abre pero 'Se pega' (congelado)"
```bash
# Significa que está corriendo en MAIN THREAD
# Solución: Asegúrate de usar subprocess en login_runner.py
# main_army.py debe lanzar subprocess.Popen(), no thread directo
```

### "¿Cómo cancelo un ataque?"
```bash
# CTRL+C en la terminal
# Esto detiene main_army.py
# Los Chromes que ya abrieron siguen vivos (es intencional)
# El usuario puede seguir comprando manualmente
```

---

## 📝 RESUMEN FINAL

| Aspecto | main.py (Un Jugador) | main_army.py (Ejército) |
|---------|----------------------|------------------------|
| **Uso** | Testing/desarrollo | Producción/drop |
| **Cuentas** | 1 | Múltiples |
| **Interfaz** | GUI (CustomTkinter) | CLI (Consola) |
| **Ejecución** | Manual (botones) | Automática (una orden) |
| **Velocidad** | Lenta (secuencial) | Rápida (paralela) |
| **Probabilidad** | 1x | Nx (N = cuentas) |

**Uso típico:**
```bash
# Desarrollo (durante la semana)
python main.py

# Drop (momento crítico)
python main_army.py
```

---

## 🎯 PRÓXIMOS PASOS

1. ✅ Verificar que `main_army.py` está en raíz
2. ✅ Crear 2+ cuentas en `auth/`
3. ✅ Generar `profile_pw/` para cada una (Login)
4. ✅ Ejecutar `python main_army.py` y verificar que lista todas
5. ✅ En el drop → Opción 4 y lanzar ataque

**Cuando todo esté listo, el Ejército estará COMBATIVO.** 🪖⚔️
