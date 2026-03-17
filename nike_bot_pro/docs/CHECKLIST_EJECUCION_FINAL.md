# 🚀 CHECKLIST FINAL DE EJECUCIÓN

**Lee esto ANTES de cada drop.**

---

## PRE-DROP (48 horas antes)

### Setup de cuenta

- [ ] Account existe en `accounts.json`
- [ ] Account tiene `"enabled": true`
- [ ] Ejecutar: `python login_runner.py <account>`
- [ ] Esperar a Chrome, loguear en Nike.cl
- [ ] Cerrar Chrome (script crea .login_ok)
- [ ] Verificar: `.login_ok` existe en `auth/<account>/`

### Validación rápida

```bash
# Step 1: Syntax check
python -m py_compile runtime/*.py
python -m py_compile ui/*.py

# Step 2: Import check
python -c "from runtime.backend_vtex import backend_run"
python -c "from runtime.multiprocessing_runner import run_account"
python -c "from ui.app_v0_9_simple import app"

# Step 3: Profile check
ls -la auth/<account>/
# Debe mostrar:
# - profile_run/
# - profile_login/
# - .login_ok
```

**Status**: ✅ O ❌ STOP

---

## 1 HORA ANTES DEL DROP

### Sistema listo

- [ ] UI funciona: `python ui/app_v0_9_simple.py`
- [ ] Puedo seleccionar account
- [ ] Puedo ingresar SKU (campo activo)
- [ ] Botones funcionan (LOGIN | PLAY)
- [ ] Logs en tiempo real (observable)
- [ ] Cerrar UI (Ctrl+C)

### Network check

```bash
# Verificar conectividad Nike
curl -I https://www.nike.cl/
curl -I https://www.nike.cl/checkout/cart/add

# Ambas deben retornar 200 OK
```

**Status**: ✅ O ❌ STOP

---

## 5 MINUTOS ANTES DEL DROP

### Último check

- [ ] Chrome real cerrado (solo el de sistema)
- [ ] Ningún browser abierto con profile
- [ ] SKU confirmado (doble check)
- [ ] Account confirmado (doble check)
- [ ] CPU/RAM disponible (monitor)

### Pre-flight test

```bash
# Test rápido sin ejecutar el bot
python -c "
from profile_manager_v2 import clone_auth_to_run
from runtime.multiprocessing_runner import preflight
import sys

user = 'test_account'
result = clone_auth_to_run(user)
print(f'Clone: {result}')

# Si clone OK, test preflight
if result:
    result = preflight(user, f'auth/{user}/profile_run')
    print(f'Preflight: {result}')
"

# Debe mostrar:
# Clone: True
# Preflight: True
```

**Status**: ✅ O ❌ STOP

---

## 🎯 MOMENTO DEL DROP

### Ejecución exacta

**Paso 1: Abrir UI**

```bash
python ui/app_v0_9_simple.py
```

Esperar a que aparezca la ventana.

**Paso 2: Seleccionar account**

- Dropdown: Seleccionar `<account>`
- Verificar que aparece en el log

**Paso 3: Ingresar SKU**

- Campo: Pegar SKU del drop (ej: `DZ2945-001`)
- Verificar en el input field

**Paso 4: Click PLAY**

- Click botón "PLAY"
- Observar log en tiempo real

---

## DURANTE LA EJECUCIÓN (15 segundos)

### Logs esperados (EN ORDEN)

```
[account] State: STARTING
[account] State: CLONING
[account] State: PREFLIGHT
  → Debe mostrar "Nike verifica..."
  → Debe mostrar "✅ Sesión válida" O "❌ Sesión inválida"

[account] State: BACKEND_SETUP
[account] State: BACKEND_ATC
  → Debe mostrar "[ATC] [SKU] Status 200 → OK" O "Status 302 → OK"
  → Si falla: "Status 400 → FAIL" O "Timeout → FAIL"

[account] State: BACKEND_PRICE_OK
[account] State: FREEZE_BACKEND
  → Backend debe cerrarse completamente aquí

[account] State: HANDOVER
  → Chrome debe abrirse automáticamente

[account] State: WAITING_HUMAN
  → Terminal muestra: "[account] ENTER para cerrar"
```

### Indicadores de ÉXITO

✅ Chrome se abre automáticamente
✅ Chrome abre magic link exacta: `https://www.nike.cl/checkout/cart/add?sku=...`
✅ Item ya está en el carrito (visible en Chrome)
✅ User puede completar checkout

### Indicadores de PROBLEMA

❌ Chrome no se abre → Debug HANDOVER
❌ Magic link incorrecta → Verificar multiprocessing_runner.py
❌ Item NO está en carrito → Verificar ATC status en logs
❌ "Estado: ERROR" → Leer mensaje de error

---

## POST-EJECUCIÓN

### Si ganaste la compra

- [ ] Cerrar Chrome cuando termines
- [ ] Presionar ENTER en terminal
- [ ] Verificar estado: DONE
- [ ] ✅ ÉXITO

### Si perdiste

- [ ] Leer el error en logs
- [ ] Revisar si fue PREFLIGHT, ATC, o FREEZE
- [ ] Ejecutar debug según corresponda

---

## DEBUG RÁPIDO (si hay problemas)

### Problema: "Sesión inválida" (PREFLIGHT falla)

```bash
# Solución 1: Limpiar cache
python profile_cleanup.py <account>

# Solución 2: Re-login
python login_runner.py <account>
```

### Problema: "ATC Status 400" (ATC falla)

```bash
# Verificar:
# 1. SKU es correcto
# 2. Nike.cl está online
# 3. Producto existe en Nike.cl

curl https://www.nike.cl/ -I
# Debe retornar 200 OK
```

### Problema: "Chrome no se abre" (HANDOVER falla)

```bash
# Verificar:
# 1. Chrome está instalado
# 2. Ningún Chrome abierto con ese profile

# Buscar Chrome
where chrome
where chromium

# Si no encuentra, instalar:
# Windows: Descargar de google.com/chrome
```

### Problema: "FREEZE no ocurre" (backend sigue ejecutando)

```bash
# Verificar backend_vtex.py
# Debe tener session.close() después de price_check

grep -A 5 "session.close" runtime/backend_vtex.py
```

---

## SEGURIDAD (ANTES DE EJECUTAR)

- [ ] Nike.cl está UP (no en mantenimiento)
- [ ] Tu account no está BANNED (login funciona)
- [ ] SKU es VÁLIDO (existe en Nike.cl)
- [ ] Network es ESTABLE (no VPN, no proxy)
- [ ] CPU/RAM DISPONIBLE (sistema limpio)

---

## CHECKLIST FINAL

**Antes de ejecutar, verifica TODO esto:**

```
PRE-DROP (48h antes):
[ ] login_runner.py ejecutado
[ ] .login_ok existe
[ ] Profile válido

1 HORA ANTES:
[ ] UI abre sin errores
[ ] Network check OK
[ ] Syntax check OK

5 MINUTOS ANTES:
[ ] Pre-flight test OK
[ ] Chrome cerrado
[ ] SKU confirmado

EJECUCIÓN:
[ ] python ui/app_v0_9_simple.py
[ ] Seleccionar account
[ ] Ingresar SKU
[ ] Click PLAY
[ ] Observar logs
[ ] Chrome se abre
[ ] Magic link correca
[ ] User completa checkout

RESULTADO:
[ ] Estado: DONE
[ ] Compra realizada
[ ] ✅ ÉXITO
```

---

## LAST WORDS

**No hay magia.**

Si sigues estos pasos, el bot hará:

1. ✅ Loguear en Nike
2. ✅ Verificar sesión
3. ✅ Agregar al carrito (backend)
4. ✅ Cerrar el backend
5. ✅ Abrir Chrome
6. ✅ Esperar al usuario

**Eso es TODO lo que hace.**

No hay más. No hay features ocultas. No hay tricks.

**Es simple. Es consistente. Es congelado.**

Si no ganas, no es culpa del bot.

Pregúntate:

- ¿Nike liberó el producto?
- ¿Tu sesión es válida?
- ¿Tu SKU es correcto?
- ¿Tu network es rápido?
- ¿Completaste el checkout?

**Todas esas cosas son TU responsabilidad.**

El bot hizo su trabajo.

---

**Buena suerte. 🚀**
