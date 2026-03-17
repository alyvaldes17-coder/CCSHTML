# HERRAMIENTAS DE DEBUG — V0.9 COMPLETO

**3 scripts nuevos para resolver problemas de LOGIN**

---

## RESUMEN EJECUTIVO

| Script | Acción | Tiempo |
|--------|--------|--------|
| `profile_cleanup.py` | Reset suave (borra cache) | 1min |
| `diagnose_login_issue.py` | Test normal + incógnito | 5min |
| `login_runner.py` | LOGIN manual con verificación | 10min |

**Flujo recomendado**:
1. Cleanup
2. LOGIN manual
3. Si falla → Diagnóstico
4. Si diagnóstico dice contaminado → Crear perfil nuevo

---

## SCRIPT 1: profile_cleanup.py

**Objetivo**: Reset suave (elimina cache sin perder sesión)

```bash
python profile_cleanup.py cuenta1
```

**Qué borra**:
- Cache/
- Code Cache/
- Service Worker/
- Blob_Storage/
- .login_ok (requiere re-login)

**Qué mantiene**:
- Cookies
- localStorage
- sessionStorage
- Auth tokens

**Resultado esperado**:
```
[CLEANUP] Completado: 4 directorios borrados
[CLEANUP] ✅ Perfil limpio y listo para login manual
```

---

## SCRIPT 2: diagnose_login_issue.py

**Objetivo**: Detectar si perfil está contaminado

```bash
python diagnose_login_issue.py cuenta1
```

**Pasos internos**:
1. Limpia el perfil (como Script 1)
2. Intenta login con Chrome normal
3. Si falla, prueba incógnito (perfil limpio)
4. Compara resultados

**Interpretación**:

```
NORMAL OK + INCÓGNITO ? → Perfil limpio, úsalo
NORMAL FAIL + INCÓGNITO OK → Perfil contaminado, crear nuevo
NORMAL FAIL + INCÓGNITO FAIL → Problema en Nike/cuenta
```

**Resultado esperado**:
```
[DIAGNOSE] ✅ PERFIL LIMPIO
[DIAGNOSE] El perfil funciona correctamente

O

[DIAGNOSE] 🔥 DIAGNÓSTICO:
[DIAGNOSE] • Incógnito funciona ✅
[DIAGNOSE] • Perfil normal falló ❌
[DIAGNOSE] → EL PERFIL ESTÁ CONTAMINADO
```

---

## SCRIPT 3: login_runner.py (YA EXISTE, MEJORADO)

**Objetivo**: LOGIN manual con post-verificación

```bash
python login_runner.py cuenta1
```

**Flujo**:
1. Abre Chrome (no headless)
2. Tú logúeas manualmente
3. Cierras Chrome
4. Script verifica con Nike
5. Crea .login_ok si OK

**Pasos para loguear**:
1. Email ✅
2. Password ✅
3. 2FA si pide ✅
4. **No cierres Chrome hasta terminar**

**Señales de éxito**:
```
[SUCCESS] LOGIN VERIFICADO
Marca: auth/cuenta1/.login_ok
Profile: auth/cuenta1/profile_login
```

**Señales de error**:
```
[ERROR] Nike NO reconoce sesion
Marca .login_ok NO creada
```

---

## FLUJO RECOMENDADO (COMPLETE)

### PASO 1: Cleanup (proactivo)

```bash
python profile_cleanup.py cuenta1
```

Siempre ejecuta esto primero, elimina cache viejo.

### PASO 2: LOGIN manual

```bash
python login_runner.py cuenta1
```

Espera "SUCCESS". Si falla, ir a PASO 3.

### PASO 3: Diagnosticar

```bash
python diagnose_login_issue.py cuenta1
```

Te dirá si perfil está contaminado.

### PASO 4: Si contaminado

```bash
rm -rf auth/cuenta1/profile_login
python login_runner.py cuenta1
```

Crea perfil nuevo, logúea de nuevo.

---

## ARQUITECTURA (REFUERZO)

```
auth/cuenta1/
├── profile_login/          (MASTER - dónde logueas TÚ)
│   ├── Default/
│   │   ├── Cookies         ✅ (mantener)
│   │   ├── Local Storage   ✅ (mantener)
│   │   ├── Cache           ❌ (limpiar si corrupto)
│   │   └── Code Cache      ❌ (limpiar si corrupto)
│   └── ...
├── profile_run/            (SLAVE - clona automáticamente)
│   └── Se destruye después de cada PLAY
└── .login_ok               (marca de integridad: LOGIN OK)
```

**Reglas**:
1. profile_login: NUNCA toques durante PLAY
2. profile_run: Se clona fresco cada vez
3. .login_ok: Creada por login_runner.py, consumida por preflight()

---

## SÍNTOMAS Y SOLUCIONES

### Síntoma: "Email rechazado"

**Causa**: Contraseña incorrecta o cuenta bloqueada

**Solución**:
1. Verifica email/password en Nike.cl directo
2. Desbloquea cuenta si está locked
3. Reintenta Paso 2

---

### Síntoma: "Se queda en email" o "Loop"

**Causa**: Perfil contaminado o bot detection

**Solución**:
1. Paso 1: Cleanup
2. Paso 2: LOGIN normal
3. Si falla → Paso 3 diagnóstico
4. Si diagnóstico dice contaminado → Paso 4

---

### Síntoma: "Sesión inválida en PLAY"

**Nota**: Si Paso 2 fue OK, no debería ocurrir

**Causa**: profile_run se corrompió

**Solución**:
- No toques profile_login
- Simplemente corre PLAY de nuevo
- profile_run se clona fresco

---

## PRÓXIMA ACCIÓN

**Ejecuta en orden**:

```bash
# 1. Cleanup
python profile_cleanup.py cuenta1

# 2. LOGIN manual
python login_runner.py cuenta1
# (loguéate en Chrome cuando se abra)

# 3. Verificar .login_ok creado
ls -la auth/cuenta1/.login_ok

# 4. Si OK, puedes hacer PLAY
python runtime/multiprocessing_runner.py <SKU> cuenta1
```

**Tiempo total**: ~15 minutos

**Resultado**: .login_ok creado, PLAY funcionará

---

## STATUS FINAL

✅ **3 scripts de debug implementados**
✅ **Flujo de diagnóstico completo**
✅ **Documentación y guías incluidas**

**Sistema V0.9 congelado y DEBUG-READY**

