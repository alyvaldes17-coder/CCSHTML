# ACCIÓN INMEDIATA — V0.9 DEBUG LOGIN

**Situación**: LOGIN fallando (email rechazado, loops, o sesión inválida)

**Tiempo**: 15-20 minutos para diagnóstico

---

## FLUJO RECOMENDADO (EN ORDEN)

### 1️⃣ Cleanup (5min)

```bash
python profile_cleanup.py cuenta1
```

**Resultado esperado**: 
```
[CLEANUP] Limpiando auth/cuenta1/profile_login
[CLEANUP] Completado: 4 directorios borrados
[CLEANUP] ✅ Perfil limpio y listo para login manual
```

---

### 2️⃣ Login manual (10min)

```bash
python login_runner.py cuenta1
```

**Cuando se abra Chrome**:
1. Navega a Nike.cl/login (ya estará abierto)
2. Loguéate manualmente:
   - Email ✅
   - Password ✅
   - 2FA si pide ✅
3. **IMPORTANTE**: No cierres Chrome hasta terminar
4. Cuando termines, cierra la ventana
5. Script verifica automáticamente

**Señales de éxito**:
- Console: `[SUCCESS] LOGIN VERIFICADO`
- Archivo creado: `auth/cuenta1/.login_ok`

**Señal de error**:
- Console: `[ERROR] Nike NO reconoce sesion`
- Ir a Paso 3

---

### 3️⃣ Si Paso 2 falló, diagnóstico (5min)

```bash
python diagnose_login_issue.py cuenta1
```

**Qué te dirá**:
- ✅ `PERFIL LIMPIO` → Funciona, úsalo
- ❌ `EL PERFIL ESTÁ CONTAMINADO` → Crear nuevo (Paso 4)
- ❌ `Ambos fallaron` → Problema en Nike/cuenta

---

### 4️⃣ Si perfil está contaminado

```bash
# 1. Eliminar perfil viejo
rm -rf auth/cuenta1/profile_login

# 2. Crear nuevo y loguear
python login_runner.py cuenta1

# 3. Loguéate en el nuevo perfil (cuando se abra)

# 4. Script verifica y crea .login_ok
```

**Resultado**: Perfil limpio, listo para PLAY

---

## QUICK DECISION TREE

```
¿Se abre Chrome?
├─ NO → Error en Playwright
│       → Verifica Chrome instalado: 
│       → python -m playwright install
│
└─ SÍ → ¿Logín manual funciona?
        ├─ SÍ, pasa email/password/2FA → Paso 2 OK
        │   └─ Espera: console dice SUCCESS?
        │       ├─ SÍ → .login_ok creado, FIN ✅
        │       └─ NO → Paso 3 diagnóstico
        │
        └─ NO, email rechazado o loops
            └─ Paso 3 diagnóstico
                ├─ Incógnito funciona?
                │   ├─ SÍ → Perfil contaminado, Paso 4
                │   └─ NO → Cuenta bloqueada/email inválido
                │           Prueba otro email o desbloquea
```

---

## EVIDENCIA DE ÉXITO

Cuando LOGIN esté bien, verás:

```bash
$ python login_runner.py cuenta1

[LOGIN] FASE 1: Usuario loguea en profile_login
[LOGIN] Abriendo Chrome con profile: auth/cuenta1/profile_login
[LOGIN] Por favor loguéate en Nike.cl
[LOGIN] Cuando termines, CIERRA Chrome
[LOGIN] Script verificara sesion automaticamente

# (aquí se abre Chrome, tú logúeas)

[LOGIN] Chrome cerrado. Verificando sesion...

[LOGIN] FASE 2: Verificacion post-cierre (headless)
[LOGIN] [OK] Nike reconoce sesion
[LOGIN] Creando marca de integridad: .login_ok

======================================================================
[SUCCESS] LOGIN VERIFICADO
======================================================================
Marca: auth/cuenta1/.login_ok
Profile: auth/cuenta1/profile_login

[NEXT] Ahora puedes ejecutar:
  python main.py
  -> Click PLAY -> se clonara automaticamente
```

**Archivo creado**: `auth/cuenta1/.login_ok` (vacío, solo marca)

---

## VERIFICACION POST-LOGIN

```bash
# Verificar que .login_ok existe
ls -la auth/cuenta1/.login_ok

# Debería devolver:
# -rw-r--r--  1 user  group  0 Jan  3 12:34 auth/cuenta1/.login_ok
```

---

## PASO SIGUIENTE (PLAY)

Una vez LOGIN OK:

```bash
# Ejecutar PLAY con SKU de ejemplo
python runtime/multiprocessing_runner.py 123456789 cuenta1

# O desde UI:
python ui/app_v0_9_simple.py
# -> Selecciona cuenta1
# -> Ingresa SKU
# -> Click PLAY
```

---

## SOPORTE RAPIDO

| Problema | Solución |
|----------|----------|
| Chrome no abre | `python -m playwright install chrome` |
| Email rechazado | Verifica email/password en Nike.cl directo |
| Loops infinitos | Cleanup + intenta con incógnito |
| Sesión inválida | Cleanup + nuevo LOGIN |
| Perfil corrupto | `rm -rf auth/cuenta1/profile_login` + nuevo LOGIN |

---

**Status**: ✅ Sistema listo

Cuando veas `.login_ok` creado → **PLAY puede ejecutarse**

