# ACCIONES RECOMENDADAS AHORA

**Usuario**: Hay problemas de LOGIN  
**Recomendación**: 3 acciones en orden (15-20 min)

---

## ACCIÓN 1: RESET SUAVE (5 min)

```bash
python profile_cleanup.py cuenta1
```

**Qué hace**:
- Borra Cache/
- Borra Code Cache/
- Borra Service Worker/
- Mantiene cookies (auth, sesión)
- Borra .login_ok (requiere re-login)

**Resultado esperado**:
```
[CLEANUP] ✅ Perfil limpio y listo para login manual
```

---

## ACCIÓN 2: LOGIN MANUAL LIMPIO (10 min)

```bash
python login_runner.py cuenta1
```

**Proceso**:
1. Se abre Chrome
2. Tú logúeas manualmente:
   - Email ✅
   - Contraseña ✅
   - 2FA si pide ✅
3. **No cierres Chrome hasta terminar**
4. Cierra la ventana
5. Script verifica automáticamente

**Señal de éxito**:
```
[SUCCESS] LOGIN VERIFICADO
Marca: auth/cuenta1/.login_ok
```

**Si falla**, ir a ACCIÓN 3

---

## ACCIÓN 3: DIAGNÓSTICO (5 min)

```bash
python diagnose_login_issue.py cuenta1
```

**Flujo**:
1. Limpia el perfil (como ACCIÓN 1)
2. Intenta login con Chrome normal
3. Si falla, prueba incógnito (perfil limpio)
4. Compara resultados

**Interpretación**:

```
✅ PERFIL LIMPIO
└─ Funciona. Úsalo.

❌ PERFIL CONTAMINADO
├─ Incógnito funciona ✅
├─ Normal falla ❌
└─ → Crear perfil nuevo:
    rm -rf auth/cuenta1/profile_login
    python login_runner.py cuenta1

❌ AMBOS FALLAN
└─ Problema en Nike o cuenta
   Prueba: otro email, desbloquea cuenta, verifica password
```

---

## SI PERFIL CONTAMINADO

```bash
# 1. Eliminar viejo
rm -rf auth/cuenta1/profile_login

# 2. Crear nuevo y loguear
python login_runner.py cuenta1
# (loguéate en Chrome cuando se abra)

# 3. Script verifica y crea .login_ok
```

---

## DESPUÉS (CUANDO LOGIN OK)

```bash
# Verificar .login_ok creado
ls -la auth/cuenta1/.login_ok

# Ejecutar PLAY
python runtime/multiprocessing_runner.py 123456789 cuenta1
```

---

## RESUMEN

| Acción | Comando | Tiempo |
|--------|---------|--------|
| 1. Reset suave | `python profile_cleanup.py cuenta1` | 1 min |
| 2. LOGIN manual | `python login_runner.py cuenta1` | 10 min |
| 3. Diagnóstico | `python diagnose_login_issue.py cuenta1` | 5 min |

**Total**: ~15-20 minutos

**Resultado**: .login_ok creado, PLAY funcionará

---

## ARQUITECTURA (REFUERZO)

```
auth/cuenta1/
├── profile_login/       (dónde LOGUEAS tú)
│   └── Cookies, localStorage (persistente)
├── profile_run/         (dónde ejecuta BOT)
│   └── Se clona y destruye automáticamente
└── .login_ok            (marca: LOGIN OK)
```

**Reglas**:
- ✅ profile_login se toca SOLO en LOGIN
- ✅ profile_run se clona fresco cada PLAY
- ✅ .login_ok creada por login_runner, consumida por preflight

---

## PRÓXIMA ACCIÓN

Ejecuta **AHORA**:

```bash
python profile_cleanup.py cuenta1
python login_runner.py cuenta1
```

Espera `[SUCCESS]` en consola.

**Hecho**. PLAY está listo.

