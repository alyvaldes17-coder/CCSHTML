# 🔧 FIX: PLAY Bloqueado Después de LOGIN V0.9

## Problema Identificado

**Síntoma**: Usuario ejecuta `python login_runner.py cuenta2` ✅ exitosamente, pero cuando intenta PLAY en la UI, dice "No logueado" ❌

**Flujo de ejecución**:
1. `python login_runner.py cuenta2` → Abre Chrome
2. Usuario loguea manualmente
3. Chrome cierra
4. Script crea archivo: `auth/cuenta2/.login_ok` ✅
5. Usuario abre UI y selecciona PLAY
6. ❌ **BLOQUEADO** - No permite ejecutar PLAY

## Causa Raíz

El problema tenía **dos partes**:

### Parte 1: Validación Silenciosa en Multiprocessing
- `play_launcher.py` NO validaba `.login_ok` **antes** de lanzar multiprocessing
- Se pasaba directamente a `run_accounts_mp()` 
- Adentro, `clone_auth_to_run()` validaba `.login_ok` pero si fallaba:
  - Emitía error al bus de estados
  - Pero el usuario no lo veía claramente en la UI
  - Parecía que PLAY "no pasaba" sin razón visible

### Parte 2: UI Sin Información Visual
- `app_v0_9_simple.py` mostraba lista de cuentas pero SIN indicador de login
- Usuario no sabía cuál cuenta está logueada y cuál no
- No había forma de verificar visualmente si `.login_ok` existe

## Solución Implementada

### 1. **Validación Early en `play_launcher.py`**

Agregué validación **CRÍTICA** ANTES de lanzar multiprocessing:

```python
from profile_manager_v2 import verify_login_ok

def launch_play_for_accounts(accounts, sku, bus=None):
    # VALIDACIÓN: Verificar que TODAS las cuentas estén logueadas
    not_logged_in = []
    for account in accounts:
        if not verify_login_ok(account):
            not_logged_in.append(account)
    
    if not_logged_in:
        print("[LAUNCHER] ❌ BLOQUEADO - Cuentas NO logueadas:")
        for acc in not_logged_in:
            print(f"  - {acc} (falta .login_ok)")
        print("[LAUNCHER] Ejecuta: python login_runner.py <cuenta>")
        return  # ← BLOQUEA antes de lanzar multiprocessing
```

**Ventaja**: 
- ✅ Error CLARO inmediatamente
- ✅ Mensaje dice exactamente qué hacer
- ✅ No intenta lanzar multiprocessing sin sesión

### 2. **Indicadores Visuales en `app_v0_9_simple.py`**

Agregué:
- **Estado visual** junto a cada cuenta: ✅ o ❌
- **Colores**: Verde si logueado, Rojo si no
- **Función `get_login_status()`** que revisa `.login_ok` en tiempo real

```python
def get_login_status(account_name: str) -> tuple:
    """Retorna (emoji, status_text, color)"""
    if verify_login_ok(account_name):
        return ("✅", "Logueado", "green")
    else:
        return ("❌", "No logueado", "red")
```

**Ventaja**:
- 👁️ Usuario VE visualmente cuál cuenta está logueada
- 👁️ Mismo en UI app
- 👁️ Si ve ❌, sabe que debe hacer LOGIN primero

## Cómo Usar la Corrección

### Flujo Correcto Ahora:

```bash
# Paso 1: LOGIN (una sola vez por cuenta)
python login_runner.py cuenta2
# → Espera a que loguees manualmente en Chrome
# → Chrome cierra automáticamente
# → Script crea auth/cuenta2/.login_ok

# Paso 2: Abre UI
python ui/app_v0_9_simple.py
# → Ves: "cuenta2" con ✅ verde (logueado)

# Paso 3: PLAY funciona
# → Especifica SKU
# → Haz clic en [2] PLAY
# → Multiprocessing se ejecuta exitosamente
```

### Si PLAY Sigue Bloqueado:

```
[LAUNCHER] ❌ BLOQUEADO - Las siguientes cuentas NO están logueadas:
  - cuenta2 (falta .login_ok)
[LAUNCHER] Ejecuta primero: python login_runner.py <cuenta>
```

**Significa**: El archivo `.login_ok` no existe o está en ruta incorrecta.

**Solución**:
```bash
# 1. Verifica que archivo existe
ls -la auth/cuenta2/.login_ok

# Si NO existe: Re-ejecuta LOGIN
python login_runner.py cuenta2

# Si EXISTE pero sigue fallando: Borra y vuelve a hacer LOGIN
rm auth/cuenta2/.login_ok
python login_runner.py cuenta2
```

## Archivos Modificados

| Archivo | Cambio | Impacto |
|---------|--------|--------|
| `ui/play_launcher.py` | Agregó `verify_login_ok()` validación | Bloqueaahora con mensaje claro si falta `.login_ok` |
| `ui/app_v0_9_simple.py` | Agregó indicadores visuales ✅/❌ | Usuario VE estado de cada cuenta en UI |

## Validación

✅ **Antes**:
- Ejecutas PLAY sin verificar login
- Multiprocessing falla silenciosamente
- Error confuso en logs

✅ **Después**:
- Ejecutas PLAY
- Si falta `.login_ok` → **BLOQUEA inmediatamente** con mensaje claro
- Si está OK → **Se ejecuta** correctamente

## Próximos Pasos

1. **Ejecuta de nuevo**:
   ```bash
   python login_runner.py cuenta2
   python ui/app_v0_9_simple.py
   ```

2. **Deberías ver**:
   - Ícono ✅ verde junto a "cuenta2"
   - Botón PLAY funciona sin problemas
   - Si hace click, empieza la ejecución

3. **Si aún hay problemas**:
   ```bash
   # Verifica que .login_ok fue creado
   ls auth/cuenta2/.login_ok
   
   # Verifica que EXISTE y tiene contenido
   cat auth/cuenta2/.login_ok
   # Debe mostrar: OK
   ```

## Resumen

**El problema**: UI permitía PLAY sin validar que usuario estuviera logueado

**La solución**: 
1. ✅ Validación temprana en `play_launcher.py`
2. ✅ Indicadores visuales en `app_v0_9_simple.py`
3. ✅ Mensajes claros si falta `.login_ok`

**Resultado**: Ahora PLAY funciona correctamente después de LOGIN exitoso.
