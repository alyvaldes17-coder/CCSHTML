# 🎯 GITHUB WORKFLOW PARA NIKE BOT PRO

Patrón específico para tu proyecto y equipo.

---

## SETUP INICIAL (Solo una vez)

### 1. En GitHub (tu navegador)
```
https://github.com/new
Nombre: nikebotprofuncionalv1
Visibility: PRIVATE
NO marques "Initialize with README"
Click "Create repository"
```

### 2. En tu computadora
```bash
cd c:\Users\beriann\Documents\Repos\nikebotprofuncionalv1

git init

# Crear .gitignore PRIMERO
# (copia desde GITHUB_GUIA_RAPIDA.md - PARTE 4)

git add .
git commit -m "Initial commit: Nike Bot v11.2 Production Ready

- evento_handshake with payment_mode parameter
- Removed --headless=new (Shape Security safe)
- Optimized timings: 50ms loop, 150ms CDP deadline
- Discord integration with payment URL
- Full stealth JS payload"

git remote add origin https://github.com/TU_USUARIO/nikebotprofuncionalv1.git
git branch -M main
git push -u origin main
```

**Verificar en GitHub:** https://github.com/TU_USUARIO/nikebotprofuncionalv1
Debes ver todos tus archivos.

---

## WORKFLOW DIARIO (para ti)

### Cambios pequeños (timings, flags, JavaScript)
```bash
# 1. Ver qué cambió
git status

# 2. Agregar cambios
git add .

# 3. Commit descriptivo
git commit -m "Optimize: reducir EV4 timeout de 25s a 20s"

# 4. Subir
git push
```

### Cambios grandes (nuevas features)
```bash
# 1. Crear rama para feature
git checkout -b feature/agregar-modo-monitor-avanzado

# 2. Editar en esa rama (todo toma commits aquí)
# ... edita código ...

# 3. Haz varios commits si cambios son diferentes
git add nike_bot_pro/core/account_manager.py
git commit -m "Add: monitor avanzado con thresholds"

git add tests/test_monitor.py
git commit -m "Test: validar monitor con 3 SKUs"

# 4. Subir rama
git push origin feature/agregar-modo-monitor-avanzado

# 5. En GitHub: click "Compare & pull request"
# - Describe los cambios
# - Asigna revisor si hay
# - Click "Create pull request"

# 6. Una vez aprobado, MERGE en GitHub

# 7. De vuelta en tu local
git checkout main
git pull origin main
# ahora tenés los cambios
```

---

## WORKFLOW CON EQUIPO (Colega contribuye)

### Colega quiere añadir feature

**Para TI (dueño del repo):**
1. Settings → Collaborators → "Add people"
2. Email o username del colega

**Para COLEGA:**
```bash
git clone https://github.com/TU_USUARIO/nikebotprofuncionalv1.git
cd nikebotprofuncionalv1

# Crear rama PROPIA para su feature
git checkout -b feature/colega-proxy-rotacion

# Editar código...
git add .
git commit -m "Add: Sistema de rotación de proxies"

# Subir rama
git push origin feature/colega-proxy-rotacion
```

**De vuelta PARA TI:**
1. En GitHub verás PR de colega
2. Revisa código (tab "Files changed")
3. Si está bien: click "Merge pull request"
4. En tu local:
```bash
git checkout main
git pull
# Código del colega está integrado
```

---

## PATRONES GIT PARA NIKE BOT

### Commit messages (sé específico)
```
✅ BUENO:
git commit -m "Fix: evento_handshake timeout 25s → 20s"
git commit -m "Add: Discord embed con payment_url"
git commit -m "Optimize: CDP deadline 500ms → 150ms"

❌ MALO:
git commit -m "cambios"
git commit -m "arreglos varios"
git commit -m "update"
```

### Ramas (nomenclatura clara)
```
feature/     → Nueva funcionalidad (feature/proxy-rotation)
fix/         → Bug fix (fix/fintoc-detection)
optimize/    → Performance (optimize/ev4-timing)
docs/        → Documentación (docs/api-reference)
refactor/    → Cambios de código sin cambiar comportamiento
test/        → Tests nuevos (test/stress-test-11-accounts)

EJEMPLO:
git checkout -b feature/agregar-webhook-discord
git checkout -b fix/headless-detection
git checkout -b optimize/reduce-loop-sleep
```

### Cuando trabajar en rama vs main
```
Main (siempre producto) → Solo merges de PRs ya revisadas

Tu rama local → Desarrollo, muchos commits, sin miedo

Regla: Si es cambio chico y solo trabajas tú → puedes hacer commit directo a main
       Si es feature grande o hay equipo → rama + PR
```

---

## CONFLICTOS (Cuando colega edita lo mismo que tú)

### Escenario
```
Tú: editas evento_handshake en main
Colega: también edita evento_handshake en su rama
Colega hace PR antes que tú
```

### Solución
```bash
# Colega ve conflicto en GitHub
# Click "Resolve conflicts" en GitHub mismo
# Elige qué código mantener
# Click "Mark as resolved"

# O si lo hace desde terminal:
git pull origin main  # Baja tu código con marca de conflicto
# Abre VS Code, vs Code te muestra <<<< ==== >>>>
# Elige cuál código mantener
git add .
git commit -m "Resolve: merge conflict in evento_handshake"
git push origin su-rama
```

---

## REVISIÓN DE CÓDIGO (Code Review)

### Tú revisa un PR de colega

**En GitHub:**
1. Abre la rama del PR
2. Tab "Files changed"
3. Lee los cambios línea por línea
4. Si algo no te gusta:
   - Hover sobre la línea
   - Click comentario
   - Escribe: "Esta variable debería ser string, no int"
5. Si todo bien:
   - Click "Review changes"
   - Select "Approve"
   - Click "Submit review"

**Colega ajusta código basado en feedback:**
```bash
# En su rama
git add .
git commit -m "Review feedback: cambiar variable type a string"
git push

# El PR se actualiza automáticamente, tú ves cambios nuevos
```

---

## DEPLOYMENT (Cuando código está listo para producción)

### Opción 1: Simple (tag)
```bash
# En main, después de que todo esté probado
git tag v11.3-production
git push origin v11.3-production
```

**En GitHub:** Releases taré automáticamente tu versión

### Opción 2: Release Notes
```bash
En GitHub: Releases → Draft new release
Tag: v11.3
Title: Nike Bot v11.3 Production
Description:
  ## Changes
  - Removed --headless=new (Shape Security safe)
  - Optimized EV4: 300ms → 50ms loop
  - Added Discord payment_url capture
  ...
Click "Publish release"
```

---

## COMANDOS ESPECÍFICOS PARA TI

```bash
# Después de cambios en engine.py
git add nike_bot_pro/engines/engine.py
git commit -m "Optimize: EV4 timing adjustments"
git push

# Después de cambios en Discord webhook
git add nike_bot_pro/engines/
git commit -m "Add: Discord embeds with payment link"
git push

# Crear rama para testing
git checkout -b test/stress-test-13-accounts
# ... haz cambios ...
git push origin test/stress-test-13-accounts
# Después, delete rama cuando termine

# Ver qué hizo colega
git log --author="colega" --oneline -5

# Ver todos los cambios en engine.py
git log -p nike_bot_pro/engines/engine.py -5
```

---

## SEGURIDAD (¡IMPORTANTE!)

### Nunca commitees
- account names/emails (auth/)
- API keys (Discord webhook está PÚBLICA, cambiarla)
- Credit card info
- Passwords, session tokens

### Archivo `.gitignore` debe tener
```
auth/*/cookies_extracted.json
auth/*/session_token.json
*.bak
.env (si usas variables de entorno)
```

### Si accidentalmente pusheaste credencial
```bash
# EMERGENCIA: cambiar webhook Discord inmediatamente
# (está expuesto en code)

# Si fue antes del push:
git reset HEAD~1
# Edita el archivo, quita credencial
git add .
git commit -m "Remove: Discord webhook (changed)"
git push

# Si fue después del push:
# Es tarde, cambiar credencial en Discord + en código
git add .
git commit -m "Security: updated Discord webhook"
git push
```

---

## EMERGENCIAS

### Necesitas deshacer un cambio ya pusheado
```bash
# Ver commits recientes
git log --oneline -10

# Deshacer commit específico (SEGURO)
git revert <hash>
git push

# El revert CREA un nuevo commit que deshace el anterior
# No borra historial, solo lo invierte
```

### Rompiste algo en main
```bash
# Ver a qué estaba bien antes
git log --oneline -5

# Volver a commit anterior (pero mantiene cambios locales)
git reset --soft <hash>

# Ahora tienes los cambios en staging, puedes editarlos
# O si querés deshacer TODO:
git reset --hard <hash>  # ⚠️ Cuidado, borra cambios
```

---

## CHECKLISTA ANTES DE HACER PUSH

```
☑️ ¿git status muestra los archivos correctos?
☑️ ¿El mensaje de commit describe qué cambió?
☑️ ¿No incluyo archivos sensibles (auth/, cookies, tokens)?
☑️ ¿Hice git add . antes de commit?
☑️ ¿He probado el código localmente?
☑️ ☑️ Si es feature grande: ¿Uso rama, no main?

Si todo OK: git push ✅
```

---

## RESUMEN RÁPIDO

**Tu flujo normal:**
```bash
git status
git add .
git commit -m "descripcion clara"
git push
```

**Cuando es feature grande:**
```bash
git checkout -b feature/nombre
# ... edita ...
git add .
git commit -m "..."
git push origin feature/nombre
# PR en GitHub → Review → Merge
git checkout main
git pull
```

**Quando hay conflicto:**
```bash
Abre archivo con <<<< ==== >>>>
Elige código correcto
git add .
git commit -m "Resolve conflict"
git push
```

---

## 📌 BOOKMARK ESTO

Cuando olvides: abre este archivo.
No hay preguntas brutas, solo falta de documentación buena.

Tú tienes esto. 🦈
