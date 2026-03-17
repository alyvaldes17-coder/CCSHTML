# 🚀 HYBRID HANDOVER - Quick Start (5 minutos)

## TL;DR

**Hybrid es Frankenstein pero 4x más rápido + fallback automático.**

---

## ⚡ Ataque en 3 líneas

```python
from runtime.bot_controller import BotController

controller = BotController("cuenta2")
controller.ataque_hibrido(9223, "DQ8426100")  # ¡Listo!
```

---

## 📋 Flujo Completo

```python
from runtime.bot_controller import BotController
import time

# Setup
controller = BotController("cuenta2")

# T-10min: Preparar
print("[T-10min] Abriendo Chrome...")
controller.spawn_zombie(9223)

# T-00min: Esperar
time.sleep(600)  # 10 minutos

# T+0s: ATACAR
print("[T+0] ¡¡¡ ATAQUEEEE !!!")
resultado = controller.ataque_hibrido(9223, "DQ8426100")

if resultado:
    print("✅ Exitoso en 0.7s")
else:
    print("❌ Falló")

# Cleanup
controller.kill_zombie(9223)
```

---

## 🧪 Test Local (Ahora Mismo)

```python
from engines.hybrid_engine import HybridAssassin
import time

# 1. Abre Chrome manualmente
# chrome --user-data-dir=C:\...\auth\cuenta2\profile_login --remote-debugging-port=9223
# Loguéate en Nike

# 2. Ejecuta esto
bot = HybridAssassin(port=9223, sku="DQ8426100")  # Calcetines baratos

# 3. Conectar
if not bot.conectar_chrome():
    print("❌ Chrome no responde")
    exit()

# 4. Sincronizar
bot.sincronizar_sangre()

# 5. Atacar
input("Presiona ENTER para atacar...")
bot.ejecutar_ataque(fallback_enabled=True)

# 6. Resultado
print(bot.obtener_status())
print(bot.obtener_metricas())
```

---

## 🎯 ¿Cuál Usar?

| Situación | Método | Razón |
|-----------|--------|-------|
| Rápido + Seguro | **Hybrid** | 0.7s + fallback |
| Seguro + Lento | **Frankenstein** | 3s pero probado |
| No sé | **Hybrid** | Tiene fallback |

---

## ⚠️ Si Falla

```
[cuenta2] ❌ [Backend] Error: Connection timeout
[cuenta2] 🛡️ [FALLBACK] Activando método Frankenstein...
[cuenta2] ✅ Exitoso (2.850s)
```

**Automático.** No queda colgado.

---

## 📊 Métricas Esperadas

**Si funciona Hybrid:**
```
Backend: 150-300ms
Total:   700-800ms
```

**Si cae a Frankenstein:**
```
Total:   2500-3500ms
```

**Si falla completamente:**
```
❌ Status: Fallido
```

---

## 🔧 Métodos Disponibles

### Ataque Completo
```python
controller.ataque_hibrido(port, sku)
# Retorna: True/False
```

### Solo Sincronizar
```python
controller.sincronizar_hibrido(port)
# Retorna: True/False
# Útil para preparar antes de un drop
```

### Clásico Frankenstein (Sigue disponible)
```python
controller.spawn_zombie(port)
controller.teleport_to_checkout(port, magic_link)
controller.kill_zombie(port)
```

---

## 🚨 Checklist Pre-Drop

- [ ] SKU correcto
- [ ] Puerto correcto (9223, 9224, etc)
- [ ] Chrome logueado
- [ ] Conexión a Nike OK
- [ ] Prueba con calcetines primero
- [ ] Timeout = 10-15 segundos

---

## 📱 Ejemplo Multi-Cuenta

```python
from runtime.bot_controller import BotController

accounts = {
    "cuenta2": 9223,
    "cuenta3": 9224,
    "cuenta4": 9225,
}

# Preparar todas
for name, port in accounts.items():
    bot = BotController(name)
    bot.spawn_zombie(port)

# Esperar...

# Atacar todas
for name, port in accounts.items():
    bot = BotController(name)
    bot.ataque_hibrido(port, "DQ8426100")
```

---

## 🔗 Más Info

- **Técnica Completa**: [HYBRID_HANDOVER_GUIDE.md](HYBRID_HANDOVER_GUIDE.md)
- **Frankenstein**: [FRANKENSTEIN_START_HERE.md](FRANKENSTEIN_START_HERE.md)
- **Código Fuente**: [hybrid_engine.py](../../engines/hybrid_engine.py)

---

**Status**: Ready ✅
