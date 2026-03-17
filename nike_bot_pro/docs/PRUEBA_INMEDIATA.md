# 🚀 PRUEBA INMEDIATA - Alineación Completa

## Exactamente Qué Hacer (Paso a Paso)

### PASO 1: Verifica que .login_ok existe

```bash
cd c:\Users\beriann\Documents\Repos\nike_bot_pro
ls -la auth/cuenta2/.login_ok
```

**Debería ver**:
```
-rw-r--r--  auth/cuenta2/.login_ok
```

Si NO existe:
```bash
python login_runner.py cuenta2
# Loguea manualmente en Nike
# Chrome se cierra automáticamente
```

---

### PASO 2: Ejecuta el validador

```bash
python validate_alignment.py
```

**Debería ver**:
```
1️⃣  FUENTE DE VERDAD (EN DISCO)
  [cuenta2] ✅ LOGUEADO

2️⃣  BOTCONTROLLER (EN MEMORIA)
  [cuenta2] ✅ READY (state=READY)

3️⃣  ACCOUNTMANAGER (EN MEMORIA)
  [cuenta2] ✅ CARGADA

4️⃣  VALIDACIÓN DE ALINEACIÓN
  [cuenta2] ✅ ALINEADO (LOGUEADO)
```

Si ves ✅ ALINEADO en cuenta2 = **TODO CORRECTO**

---

### PASO 3: Abre la UI

```bash
python ui/app_v0_9_simple.py
```

**Debería ver**:
- Lista de cuentas a la izquierda
- Junto a "cuenta2": **✅** (verde)
- Junto a "cuenta1", "cuenta3": ❌ (rojo)

---

### PASO 4: Haz PLAY

1. En la lista, haz clic en "cuenta2" (debería resaltarse en azul)
2. A la derecha, en SKU, escribe: **176816**
3. Haz clic en **[2] PLAY (backend + handover)**
4. **DEBE EJECUTARSE SIN BLOQUEOS** ✅

---

## Si Algo Falla

### Caso A: "ALINEADO" pero PLAY aún se bloquea

**Diagnóstico**:
```bash
# Verifica que el archivo realmente existe
cat auth/cuenta2/.login_ok
```

**Debe mostrar**:
```
OK
```

Si está vacío, borra y vuelve a LOGIN:
```bash
rm auth/cuenta2/.login_ok
python login_runner.py cuenta2
```

---

### Caso B: BotController muestra "NO_AUTH" pero disco muestra "LOGUEADO"

**Significa**: BotController no está leyendo la versión correcta.

**Solución**:
```bash
# Cierra todos los Python processes
# Y vuelve a ejecutar validate_alignment.py
```

---

### Caso C: validate_alignment muestra "DESALINEADO"

**Esto NO debe pasar si seguiste los pasos correctamente.**

Si pasa, revisa:
```bash
# 1. ¿Existe el archivo?
ls -la auth/cuenta2/.login_ok

# 2. ¿Tiene contenido?
cat auth/cuenta2/.login_ok

# 3. ¿Es cuenta2 o cuenta diferente?
ls -la auth/*/. login_ok
```

---

## Qué Cambió Exactamente

**Hice 3 cambios mínimos y exactos**:

1. **BotController** - Lee `.login_ok` al iniciar
2. **AccountManager** - Valida cuentas por `.login_ok`
3. **play_launcher.py** - Verifica `.login_ok` antes de PLAY

**Eso es TODO.**

No hay cambios en Chrome, en Nike, ni en nada más.

---

## Resumen Final

| Item | Antes | Después |
|------|-------|---------|
| LOGIN funciona | ✅ | ✅ |
| `.login_ok` se crea | ✅ | ✅ |
| BotController lee `.login_ok` | ❌ | ✅ |
| PLAY se bloquea | ❌ | ✅ NO se bloquea |
| UI muestra estado correcto | ❌ | ✅ |

---

## Validación en 30 Segundos

```bash
# 1. Validador
python validate_alignment.py
# Busca: [cuenta2] ✅ ALINEADO (LOGUEADO)

# 2. UI
python ui/app_v0_9_simple.py
# Busca: cuenta2 con ✅ verde

# 3. PLAY
# Haz clic en botón PLAY
# Debe ejecutarse SIN decir "No logueado"
```

**Si los 3 checkpoints son ✅, el sistema está correcto.**
