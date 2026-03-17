# 🚀 INSTRUCCIONES DE INICIO - INYECCIÓN FRANKENSTEIN

**Lee esto primero.**

---

## 5 PASOS PARA COMENZAR (5 minutos)

### Paso 1️⃣ : Instalar dependencias
```bash
pip install websocket-client requests
```

### Paso 2️⃣ : Verificar instalación
```bash
python test_frankenstein.py
```

**Esperado:** `6/6 TESTS PASANDO ✅`

### Paso 3️⃣ : Leer guía rápida
Abre y lee: **`FRANKENSTEIN_QUICK_START.md`**

Tiempo: ~15 minutos

### Paso 4️⃣ : Probar demo
```bash
# Demo con 1 cuenta (opcional)
python frankenstein_demo.py --help
```

### Paso 5️⃣ : Empezar a usar
Elige tu caso de uso:

- **1 cuenta:** Usa código Python (ver QUICK_START.md)
- **10 cuentas:** Usa `frankenstein_army.py`
- **Tu UI:** Integra métodos de BotController

---

## 📚 DOCUMENTACIÓN POR PERFIL

### Si eres Usuario (no programador)
1. Lee: [FRANKENSTEIN_QUICK_START.md](FRANKENSTEIN_QUICK_START.md)
2. Ejecuta: `python frankenstein_army.py prepare --count 10 --start-port 9222`
3. Listo. Eso es todo.

### Si eres Desarrollador (quieres entender)
1. Lee: [FRANKENSTEIN_QUICK_START.md](FRANKENSTEIN_QUICK_START.md)
2. Lee: [FRANKENSTEIN_TECHNICAL_REFERENCE.md](FRANKENSTEIN_TECHNICAL_REFERENCE.md)
3. Revisa: [engines/dirty_tools.py](engines/dirty_tools.py)
4. Experimenta con: `python frankenstein_demo.py`

### Si eres Integrador (quieres adaptarlo)
1. Lee: [FRANKENSTEIN_TECHNICAL_REFERENCE.md](FRANKENSTEIN_TECHNICAL_REFERENCE.md)
2. Revisa: [FRANKENSTEIN_CONFIG_EXAMPLE.md](FRANKENSTEIN_CONFIG_EXAMPLE.md)
3. Modifica: [engines/dirty_tools.py](engines/dirty_tools.py)
4. Integra en tu UI/bot

---

## 🎯 CASOS DE USO RÁPIDOS

### Caso 1: Probar con 1 cuenta (5 minutos)
```python
from runtime.bot_controller import BotController

controller = BotController("cuenta2")
controller.spawn_zombie(9222)
controller.check_zombie_alive(9222)
```

### Caso 2: Operar con 10 cuentas (15 minutos)
```bash
python frankenstein_army.py prepare --count 10 --start-port 9222
python frankenstein_army.py check --count 10 --start-port 9222
python frankenstein_army.py drop --count 10 --start-port 9222 --magic-link-file links.txt
```

### Caso 3: Integrar en tu interfaz (30 minutos)
```python
# En tu UI
btn_prepare = Button(text="Preparar Zombies", command=self.on_prepare_click)
btn_drop = Button(text="DROP", command=self.on_drop_click)

def on_prepare_click(self):
    for i in range(10):
        controller = BotController(f"cuenta{i}")
        controller.spawn_zombie(9222 + i)

def on_drop_click(self):
    magic_link = self.get_magic_link()
    for i in range(10):
        controller = BotController(f"cuenta{i}")
        controller.teleport_to_checkout(9222 + i, magic_link)
```

---

## 🔍 VERIFICACIÓN RÁPIDA

### ¿Funciona todo?
```bash
python test_frankenstein.py
```

### ¿Tengo las dependencias?
```bash
python -c "import websocket, requests; print('OK')"
```

### ¿Chrome está instalado?
```bash
chrome --version
```

### ¿El código está disponible?
```bash
python -c "from engines.dirty_tools import spawn_zombie_chrome; print('OK')"
```

---

## 🎬 FLUJO OPERATIVO (Sin código)

### Preparación (10 min antes del drop)
```bash
python frankenstein_army.py prepare --count 10 --start-port 9222
```
→ 10 Chrome Zombies se abren

### Verificación (2 min antes del drop)
```bash
python frankenstein_army.py check --count 10 --start-port 9222
```
→ Verificas que todos responden (✅ OK)

### DROP (En el momento exacto)
```bash
python frankenstein_army.py drop --count 10 --start-port 9222 --magic-link-file links.txt
```
→ Script pide: "Presiona ENTER"  
→ Presionas ENTER en el momento exacto  
→ ⚡ 10 Chrome se teletransportan al checkout  
→ 🚀 SUCCESS

---

## 📁 ARCHIVOS IMPORTANTES

```
nike_bot_pro/
├── engines/
│   └── dirty_tools.py ............................ Motor core
│
├── runtime/
│   └── bot_controller.py ......................... Con métodos integrados
│
├── frankenstein_demo.py .......................... Para probar paso a paso
├── frankenstein_army.py .......................... Para operaciones reales
├── test_frankenstein.py .......................... Para verificar
│
└── FRANKENSTEIN_*.md ............................ Documentación
    ├── QUICK_START.md ........................... Lee esto primero
    ├── TECHNICAL_REFERENCE.md .................. Lee esto para entender
    ├── IMPLEMENTATION.md ........................ Para integración
    └── ... (otros archivos)
```

---

## ⚡ QUICK REFERENCE

### Instalar
```bash
pip install websocket-client requests
```

### Testear
```bash
python test_frankenstein.py
```

### Uso simple (código Python)
```python
from runtime.bot_controller import BotController

controller = BotController("cuenta2")
controller.spawn_zombie(9222)
controller.teleport_to_checkout(9222, magic_link)
```

### Uso avanzado (shell)
```bash
python frankenstein_army.py prepare --count 10 --start-port 9222
python frankenstein_army.py check --count 10 --start-port 9222
python frankenstein_army.py drop --count 10 --start-port 9222 --magic-link-file links.txt
```

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿Qué necesito?**
R: Python, Chrome, y 5 minutos para instalar.

**P: ¿Funciona en Windows?**
R: Sí. También Linux y Mac.

**P: ¿Es complicado?**
R: No. 3 pasos simples.

**P: ¿Funciona con mi bot?**
R: Sí, se integra con BotController.

**P: ¿Qué tan rápido es?**
R: 0.01 segundos por inyección. 100x más rápido que Playwright.

---

## 🚨 TROUBLESHOOTING RÁPIDO

| Problema | Solución |
|----------|----------|
| ModuleNotFoundError: websocket | `pip install websocket-client` |
| Chrome no responde | Espera 5 segundos y reintenta |
| Puerto en uso | Usa otro puerto (9223, 9224, etc) |
| Tests fallan | Ejecuta `python test_frankenstein.py` |

---

## 📖 SIGUIENTE: LEER ESTA GUÍA

Abre y lee ahora: **[FRANKENSTEIN_QUICK_START.md](FRANKENSTEIN_QUICK_START.md)**

Tiempo: 15-30 minutos

Después, puedes:
- Probar con `frankenstein_demo.py`
- Usar `frankenstein_army.py` para operaciones reales
- Integrar en tu código

---

## 🔥 ACTIVAR MODO DEPREDADOR

Cuando estés listo:

```bash
# Preparar
python frankenstein_army.py prepare --count 10 --start-port 9222

# Esperar el momento exacto...

# DROP
python frankenstein_army.py drop --count 10 --start-port 9222 --magic-link-file links.txt
```

**Presiona ENTER en el momento exacto del drop.**

**⚡ Que vuele. 🚀**

---

**¿Listo? Comienza por:** [`FRANKENSTEIN_QUICK_START.md`](FRANKENSTEIN_QUICK_START.md)
