# LOGIN TROUBLESHOOTING — V0.9 CONGELADO

**Problema**: El email avanza pero se queda, falla auth, o loops

**Solución en 3 pasos**

---

## PASO 1: Reset suave (5min)

```bash
python profile_cleanup.py cuenta1
```

**Qué hace**:
- Borra Cache/
- Borra Code Cache/
- Borra Service Worker/
- Mantiene cookies, localStorage, auth tokens
- Borra .login_ok (requiere re-login)

**Resultado esperado**: Perfil limpio, sin caché contaminado

---

## PASO 2: LOGIN manual normal

```bash
python login_runner.py cuenta1
```

**Flujo**:
1. Se abre Chrome (no headless)
2. Tú navegas a Nike.cl/login
3. Loguéate manualmente:
   - Email ✅
   - Contraseña ✅
   - 2FA si pide ✅
4. Cierra Chrome
5. Script verifica automáticamente
6. Si OK → crea .login_ok

**Señales de éxito**:
- ✅ Email pasa al siguiente paso
- ✅ Contraseña se pide sin error
- ✅ 2FA se resuelve
- ✅ Redirige a dashboard/selección de cuenta
- ✅ Script imprime: `[SUCCESS] LOGIN VERIFICADO`

**Señales de error**:
- ❌ Email rechazado
- ❌ "Demasiados intentos"
- ❌ Loop infinito
- ❌ Página blanca
- ❌ Script dice: `[ERROR] Nike NO reconoce sesion`

---

## PASO 3: Si falla, diagnóstico completo

```bash
python diagnose_login_issue.py cuenta1
```

**Qué hace**:
1. Limpia el perfil (como Paso 1)
2. Intenta login con Chrome normal
3. Si falla, prueba con incógnito (perfil limpio)
4. Compara resultados

**Interpretación**:

| Normal | Incógnito | Diagnóstico |
|--------|-----------|-------------|
| ✅ | - | Perfil limpio. Úsalo. |
| ❌ | ✅ | **Perfil contaminado.** Crear nuevo. |
| ❌ | ❌ | Problema en Nike o cuenta. Prueba email distinto. |
| ✅ | ✅ | Ambiguo. Reintentar Paso 2. |

---

## PASO 4: Si perfil está contaminado

Si diagnóstico dice: **"EL PERFIL ESTÁ CONTAMINADO"**

```bash
# 1. Eliminar perfil viejo
rm -rf auth/cuenta1/profile_login

# 2. Crear nuevo (script lo hace)
python login_runner.py cuenta1

# 3. Loguéate en el nuevo
# (se abre Chrome automáticamente)

# 4. Script verifica y crea .login_ok
```

**Importante**: 
- Nuevo perfil es perfil_login limpio
- PLAY clonará de este al ejecutarse
- Solo profile_run se destruye después de cada uso

---

## ARQUITECURA (RECORDATORIO)

```
auth/cuenta1/
├── profile_login/       (MASTER - dónde logueas TÚ)
│   └── Cookies, localStorage (persistente)
├── profile_run/         (SLAVE - dónde ejecuta BOT)
│   └── Se clona de profile_login
│   └── Se destruye después de cada PLAY
└── .login_ok            (marca: login OK)
```

**Regla crítica**:
- ❌ profile_login nunca se toca durante PLAY
- ✅ profile_login solo se usa en LOGIN
- ✅ profile_run se clona limpio cada vez

---

## SÍNTOMAS COMUNES

### "Email rechazado" o "Demasiados intentos"

**Causa**: Cuenta bloqueada o contraseña incorrecta

**Fix**:
1. Verifica email/contraseña en Nike.cl directo (sin bot)
2. Desbloquea cuenta si está locked
3. Reintenta Paso 2

---

### "Se queda en email" o "Loop infinito"

**Causa**: Nike rechaza algo (bot detection, 2FA, etc)

**Fix**:
1. Paso 1: Reset suave
2. Paso 2: Intenta login manual
3. **Durante login**: NO cierres Chrome hasta terminar
4. Si Paso 2 falla → Paso 3 (diagnóstico)

---

### "Sesión inválida después del PLAY"

**Nota**: Esto NO debe ocurrir si Paso 2 fue OK

**Causa posible**: profile_run se corrompió

**Fix**:
- No toques profile_login
- Simplemente ejecuta PLAY de nuevo
- profile_run se clona fresco

---

## CHECKLIST FINAL

- [ ] `python profile_cleanup.py cuenta1` ✅
- [ ] `python login_runner.py cuenta1` ✅ (ve LOGIN OK)
- [ ] Verify .login_ok creado: `ls auth/cuenta1/.login_ok`
- [ ] Intenta PLAY: `python runtime/multiprocessing_runner.py <SKU> cuenta1`
- [ ] Si PLAY falla solo → Paso 3 diagnóstico
- [ ] Si LOGIN falla → Paso 4 crear perfil nuevo

---

## ARQUITECTURA FINAL

**LOGIN (manual, off-drop)**
- profile_login limpio
- Usuario loguea
- .login_ok creado
- ✅ Listo

**PLAY (automatizado, drop)**
- Clona profile_login → profile_run
- Ejecuta flujo (backend < 1s)
- Destruye profile_run
- Repite

**Garantía**: 
- Si Paso 2 es OK, PLAY funcionará
- Si Paso 2 falla, Paso 3 te dice por qué

---

## PRÓXIMA ACCIÓN

1. Ejecuta: `python profile_cleanup.py cuenta1`
2. Ejecuta: `python login_runner.py cuenta1`
3. Loguéate en Chrome cuando se abra
4. Espera "SUCCESS" en terminal
5. Listo para PLAY

