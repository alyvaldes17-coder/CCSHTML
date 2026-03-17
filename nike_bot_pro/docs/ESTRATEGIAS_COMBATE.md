# ⚔️ ESTRATEGIAS DE COMBATE: Ejército vs Glotón

## 📌 CONTEXTO

Hay dos formas de maximizar tus probabilidades en un drop:

1. **Estrategia 1: El Ejército (Multi-Cuenta)** 
   - Múltiples cuentas Nike
   - Cada una compra simultáneamente
   - 5 cuentas = 5x más probabilidad

2. **Estrategia 2: El Glotón (Una Cuenta, Múltiples Links)**
   - UNA sola cuenta
   - Reutiliza el navegador
   - Ataca varios SKUs consecutivos
   - Útil si tienes 3 drops de tallas diferentes

---

## 🪖 ESTRATEGIA 1: EL EJÉRCITO (RECOMENDADO)

### ¿Cuándo usarlo?
- ✅ Tienes 3+ cuentas Nike configuradas
- ✅ Quieres maximizar probabilidad
- ✅ Cada cuenta tiene sesión READY
- ✅ El drop es competido

### Flujo

```
main_army.py
  │
  ├─ Escanear auth/ → Cargar BotControllers
  │
  ├─ Loguear TODO (simultáneo)
  │  ├─ login_runner.py (subprocess) para cuenta 1
  │  ├─ login_runner.py (subprocess) para cuenta 2
  │  └─ login_runner.py (subprocess) para cuenta 3
  │
  └─ Esperar DROP (manual o Discord)
     │
     └─ Ataque Coordinado (FUEGO!)
        ├─ Cuenta 1: handle_btn_play_click(sku) en thread
        ├─ Cuenta 2: handle_btn_play_click(sku) en thread
        └─ Cuenta 3: handle_btn_play_click(sku) en thread
           (Todas ejecutan EN PARALELO)
```

### Implementación

#### 1. Cargar el Ejército

```bash
python main_army.py
```

Menu:
```
1. Listar soldados        # Ver todas las cuentas
2. Estado general         # Estado de cada una
3. LOGIN masivo           # Loguear todas
4. Ataque coordinado      # Lanzar ataque (ingresa SKU)
5. Drop simulado          # Testing
6. Salir
```

#### 2. Flujo Real de Batalla

```bash
# Terminal 1: Cargar ejército
$ python main_army.py
🪖 RECLUTANDO EJÉRCITO...
  🪖 Reclutando: cuenta2
  🪖 Reclutando: cuenta3
  🪖 Reclutando: cuenta4
✅ Ejército listo: 3 cuentas

# Opción 3: LOGIN masivo
Loguendo 3 cuentas simultáneamente...
[cuenta2] 🔐 LOGIN iniciado...
[cuenta3] 🔐 LOGIN iniciado...
[cuenta4] 🔐 LOGIN iniciado...
  # Se abren 3 Chromes a la vez
  # El usuario loguea manualmente en cada una
✅ Logueo masivo completado

# Opción 2: Ver estado
📋 ESTADO DEL EJÉRCITO
1. cuenta2  → ✅ Listo para PLAY
2. cuenta3  → ✅ Listo para PLAY
3. cuenta4  → ✅ Listo para PLAY

# Opción 4: ESPERAR DROP y Ataque
Ingresa SKU: 12345
🔥 ¡ORDEN DE ATAQUE RECIBIDA!
🚀 Lanzando ataque con 3 cuentas...
[cuenta2] 🎯 Atacando SKU 12345...
[cuenta3] 🎯 Atacando SKU 12345...
[cuenta4] 🎯 Atacando SKU 12345...
  # Las 3 monitorean SIMULTÁNEAMENTE
  # Cuando alguna detecta precio → abre Chrome
  # Todas pueden llegar a /checkout al mismo tiempo
✅ Ataque coordinado completado
```

### Ventajas del Ejército

| Aspecto | Ejército | Glotón |
|---------|----------|--------|
| Probabilidad | 5x si 5 cuentas | 1x |
| Velocidad | Simultánea | Secuencial |
| Para drops competidos | ✅ IDEAL | ❌ Lento |
| Cookies/sesiones | Aisladas | Compartidas |
| Límite de cantidad | Bypasseado (5 cuentas ≠ 1) | Bloqueado |

**Resultado esperado:** Si Nike tiene 100 pares, con 5 cuentas atacando a la vez, tu probabilidad de ganar sube exponencialmente.

---

## 🍽️ ESTRATEGIA 2: EL GLOTÓN (Una Cuenta, Múltiples Links)

### ¿Cuándo usarlo?
- ✅ Solo tienes 1 cuenta Nike (o quieres usar 1)
- ✅ Caen 3 drops seguidos (talla 9, 10, 11)
- ✅ Cada drop es SKU diferente pero misma sesión
- ✅ Reclamos/limitaciones de cuenta

### Problema Clásico (SIN Glotón)

```
Drop 1: SKU 12345
  → Chrome abre, compra → Cierra
  
Drop 2: SKU 54321 (10 segundos después)
  → Intenta abrir Chrome
  → ❌ SingletonLock bloqueado (la anterior acaba de cerrar)
  → Chrome NO abre
  → FALLA la compra
```

### Solución: PlaywrightEngineV3 (Glotón)

```python
# USO:
from engines.playwright_engine_v3 import PlaywrightEngineV3

engine = PlaywrightEngineV3("auth/cuenta2/profile_pw")

# Drop 1
engine.launch_checkout_mission("https://nike.cl/...sku=12345")
# Chrome abre, usuario compra

# Drop 2 (10 segundos después)
engine.launch_checkout_mission("https://nike.cl/...sku=54321")
# ♻️ Reutiliza el MISMO navegador
# Nueva pestaña se abre
# Usuario compra de nuevo

# Drop 3
engine.launch_checkout_mission("https://nike.cl/...sku=789")
# ♻️ Otra pestaña
# Usuario compra tercera vez
```

### Implementación

Reemplazar PlaywrightEngine:

```python
# ANTES
from engines.playwright_engine_v2 import PlaywrightEngine

# DESPUÉS (Glotón)
from engines.playwright_engine_v3 import PlaywrightEngineV3 as PlaywrightEngine
```

En `BotController.__init__()`:

```python
self.engine = PlaywrightEngine(profile_path)  # Automáticamente reutiliza ahora
```

### Flujo Glotón

```
Drop 1: SKU 12345
  └─ engine.launch_checkout_mission(url)
     ├─ ensure_browser_open() → Abre Chrome
     ├─ new_tab(url) → Pestaña 1
     └─ Usuario compra

Drop 2: SKU 54321 (10 seg después)
  └─ engine.launch_checkout_mission(url)
     ├─ ensure_browser_open() → Detecta que ya está abierto ✅
     ├─ new_tab(url) → Pestaña 2
     └─ Usuario compra

Drop 3: SKU 789
  └─ engine.launch_checkout_mission(url)
     ├─ ensure_browser_open() → Reutiliza existente ✅
     ├─ new_tab(url) → Pestaña 3
     └─ Usuario compra
```

### Ventajas del Glotón

- ✅ Sin delay (no reinicia Chrome)
- ✅ Sesión compartida (mismas cookies)
- ✅ Evita SingletonLock
- ✅ Múltiples pestañas activas simultáneamente

---

## 🎯 RECOMENDACIÓN FINAL

### Si tienes 3+ cuentas: **USA EL EJÉRCITO** 🪖
```bash
python main_army.py
# Opción 3: LOGIN masivo
# Opción 4: Ataque coordinado
```

**Por qué:**
- Máxima probabilidad (5 ≠ 1)
- Bypassea límites de cantidad
- Nike ve 5 personas diferentes
- Mejor para drops competidos

### Si tienes 1 cuenta: **USA EL GLOTÓN** 🍽️
```python
# En tu bot actual:
from engines.playwright_engine_v3 import PlaywrightEngineV3

engine = PlaywrightEngineV3(profile_path)
# Múltiples links sin problemas
```

**Por qué:**
- Evita reiniciar Chrome
- Sesión compartida
- Rápido para drops consecutivos
- Sin SingletonLock

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Estrategia 1 (Ejército)
- [ ] Tienes 3+ cuentas configuradas en auth/
- [ ] `main_army.py` presente
- [ ] `login_runner.py` presente
- [ ] BotController funciona correctamente
- [ ] Ejecutas: `python main_army.py`

### Estrategia 2 (Glotón)
- [ ] `playwright_engine_v3.py` presente
- [ ] Cambiar import en BotController o handler
- [ ] Mismo BotController, solo cambia engine
- [ ] Testing: Múltiples `launch_checkout_mission()` seguidas

---

## 🚀 EJEMPLO COMPLETO: Ejército 5 Cuentas

```bash
$ python main_army.py

⚔️  COMANDO DEL EJÉRCITO
🪖 RECLUTANDO EJÉRCITO...
  🪖 Reclutando: cuenta2
  🪖 Reclutando: cuenta3
  🪖 Reclutando: cuenta4
  🪖 Reclutando: cuenta5
  🪖 Reclutando: conta6
✅ Ejército listo: 5 cuentas

1. Listar soldados
2. Estado general
3. LOGIN masivo
4. Ataque coordinado
5. Drop simulado
6. Salir

> 3

🔐 LOGUEO MASIVO
Loguendo 5 cuentas simultáneamente...

[cuenta2] 🔐 LOGIN iniciado...
[cuenta3] 🔐 LOGIN iniciado...
[cuenta4] 🔐 LOGIN iniciado...
[cuenta5] 🔐 LOGIN iniciado...
[conta6] 🔐 LOGIN iniciado...

# Se abren 5 Chromes a la vez
# Usuario loguea manualmente en cada una

[cuenta2] ✅ READY
[cuenta3] ✅ READY
[cuenta4] ✅ READY
[cuenta5] ✅ READY
[conta6] ✅ READY

✅ Logueo masivo completado

> 4

Ingresa SKU: 123456

🔥 ¡ORDEN DE ATAQUE RECIBIDA!
Objetivo: SKU 123456
Fuego: 5 cuentas

🚀 Lanzando ataque con 5 cuentas...

[cuenta2] 🎯 Atacando SKU 123456...
[cuenta3] 🎯 Atacando SKU 123456...
[cuenta4] 🎯 Atacando SKU 123456...
[cuenta5] 🎯 Atacando SKU 123456...
[conta6] 🎯 Atacando SKU 123456...

# Las 5 monitorean SIMULTÁNEAmente
# Si precio detectado en segunda 5:
[cuenta2] 🎯 PRECIO DETECTADO
[cuenta2] 📌 PRICE_LOCKED
[cuenta2] 🚀 EJECUTANDO
# Chrome se abre para cuenta2

# En segundo 6:
[cuenta3] 🎯 PRECIO DETECTADO
[cuenta3] 📌 PRICE_LOCKED
[cuenta3] 🚀 EJECUTANDO
# Chrome se abre para cuenta3

# etc...

# RESULTADO: Si Nike tiene 50 pares, tu ejército de 5
# puede capturar varios antes que la competencia
```

---

## 📝 RESUMEN

| Factor | Ejército | Glotón |
|--------|----------|--------|
| **Archivo** | `main_army.py` | `playwright_engine_v3.py` |
| **Cuentas** | Múltiples | 1 |
| **Ejecución** | Paralela | Secuencial |
| **Sesiones** | Aisladas | Compartida |
| **Drops competidos** | ✅ Ideal | ❌ Riesgoso |
| **Drops consecutivos** | Posible pero complejo | ✅ Ideal |
| **Probabilidad** | N x probabilidad | 1 x |

**Conclusión:** Para máxima potencia → **USA EL EJÉRCITO** 🪖
