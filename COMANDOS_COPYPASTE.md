# 🎬 COMMANDS QUICK COPY-PASTE

Copia y pega directamente según lo que necesites.

---

## PRIMERA CONFIGURACIÓN (Una sola vez)

### Paso 1: Crear repo en GitHub
Ve a: https://github.com/new
- Nombre: `nikebotprofuncionalv1`
- Selecciona "Private"
- Luego click "Create repository"

### Paso 2: En terminal, corre ESTO
```bash
cd c:\Users\beriann\Documents\Repos\nikebotprofuncionalv1

git init

git add .

git commit -m "Initial commit: Nike Bot v11.2 Production Ready"

git remote add origin https://github.com/TU_USUARIO/nikebotprofuncionalv1.git

git branch -M main

git push -u origin main
```

**REEMPLAZA `TU_USUARIO` con tu username de GitHub**

Listo. Ya está en GitHub.

---

## DIARIAMENTE (Cambios pequeños)

### Cambio en engine.py
```bash
git add .
git commit -m "Fix: EV4 timeout adjustment"
git push
```

### Cambio en config
```bash
git add .
git commit -m "Update: nuevos parámetros stealth"
git push
```

### Cambio en múltiples archivos
```bash
git add .
git commit -m "Optimize: reducir sleep en EV4 loop"
git push
```

---

## FEATURE NUEVA (Cambio grande)

### Crear rama
```bash
git checkout -b feature/agregar-proxy-rotation
```

### Hacer cambios (haz varios commits si necesitas)
```bash
git add .
git commit -m "Add: proxy rotation logic"

# Más cambios si hay
git add .
git commit -m "Test: validar proxy rotation"

# Subir rama
git push origin feature/agregar-proxy-rotation
```

Luego en GitHub:
1. Verás botón "Compare & pull request" 
2. Click
3. Describe los cambios
4. Click "Create pull request"
5. Espera aprobación o apruébate a ti mismo
6. Click "Merge pull request"

De vuelta en terminal:
```bash
git checkout main
git pull
```

---

## COLEGA CONTRIBUYE

### Para TI: Invitar colega
En GitHub:
1. Repo → Settings → Collaborators
2. Click "Add people"
3. Escribe email/username
4. Envía invitación

### Para COLEGA: Clonar y contribuir
```bash
git clone https://github.com/TU_USUARIO/nikebotprofuncionalv1.git
cd nikebotprofuncionalv1

git checkout -b feature/colega-nueva-funcionalidad

# Edita código en su rama...

git add .
git commit -m "Add: funcionalidad nueva"
git push origin feature/colega-nueva-funcionalidad
```

### De vuelta PARA TI: Revisar y mergear
En GitHub:
1. Verás PR de colega
2. Tab "Files changed" para revisar
3. Si OK: "Review changes" → "Approve" → "Submit"
4. Click "Merge pull request"

En terminal:
```bash
git checkout main
git pull
```

---

## VER CAMBIOS

### Qué archivos cambiaron
```bash
git status
```

### Exactamente qué líneas cambiaron
```bash
git diff
```

### Historial (últimos 10 commits)
```bash
git log --oneline -10
```

### Quién hizo qué (si hay team)
```bash
git log --author="colega" --oneline -5
```

### Cambios en un archivo específico
```bash
git log -p nike_bot_pro/engines/engine.py -5
```

---

## DESHACER COSAS

### Deshacer cambios ANTES de commitear
```bash
# Reset un archivo específico
git checkout -- nike_bot_pro/engines/engine.py

# Reset TODO
git reset --hard HEAD
```

### Deshacer último commit (pero mantiene cambios)
```bash
git reset HEAD~1
# Ahora tienes los cambios en staging, puedes re-editarlos
```

### Deshacer commit YA PUSHEADO (SEGURO)
```bash
git revert <hash>
git push

# Reemplaza <hash> con el commit hash (ej: a1b2c3d)
# Ver hash con: git log --oneline
```

### Volver a un commit anterior (peligroso)
```bash
git reset --hard <hash>
git push -f

# ⚠️ Solo si ningún colega depende de los commits que estás borrando
```

---

## RAMAS

### Ver ramas locales
```bash
git branch
```

### Ver TODAS las ramas (incluyendo remote)
```bash
git branch -a
```

### Cambiar de rama
```bash
git checkout main
git checkout feature/mi-feature
```

### Crear y cambiar a rama nueva
```bash
git checkout -b feature/algo-nuevo
```

### Borrar rama local
```bash
git branch -d feature/ya-mergeada
```

### Borrar rama remote (GitHub)
```bash
git push origin --delete feature/ya-no-la-necesito
```

---

## CONFLICTOS (cuando dos personas editan lo mismo)

### Síntoma
```
git pull
CONFLICT (content): Merge conflict in archivo.py
```

### En VS Code
Abre el archivo conflictivo.
Verás algo como:
```
<<<<<<< HEAD
tu código
=======
código del colega
>>>>>>> rama-colega
```

**Elige uno:**
- Click "Accept Current Change" (tu código)
- Click "Accept Incoming Change" (código colega)
- Click "Accept Both Changes" (los dos)

Luego:
```bash
git add .
git commit -m "Resolve: merge conflict in archivo.py"
git push
```

---

## TAGS (Marcar versiones importantes)

### Crear tag
```bash
git tag v11.3-production
git push origin v11.3-production
```

### Ver tags
```bash
git tag -l
```

### Borrar tag
```bash
git tag -d v11.2-old
git push origin --delete v11.2-old
```

---

## EMERGENCIAS

### GitHub está caído, no puedo pushear
```bash
# Tus cambios están en local de todas formas
git status # Verifica
# Cuando GitHub vuelva, git push
```

### Hice commit en rama equivocada
```bash
# Estoy en main pero quería estar en feature/algo
git reset HEAD~1  # Deshacer commit, mantener cambios

git checkout -b feature/algo  # Crear rama nueva

git add .
git commit -m "mensaje"

git push origin feature/algo
```

### Necesito los cambios de colega urgente
```bash
git fetch origin  # Descargas las ramas
git checkout rama-colega
```

### Quiero empezar desde cero (nuclear reset)
```bash
# ⚠️ Pierdes TODOS los cambios locales
git fetch origin
git reset --hard origin/main
```

---

## AUTENTICACIÓN (Si pide usuario/password)

### Primera vez
```bash
git push
# Pide usuario y password
# En password: copia el token (no contraseña GitHub)
```

### Crear token en GitHub
1. GitHub → Settings → Developer settings → Personal access tokens
2. Click "Tokens (classic)"
3. Click "Generate new token"
4. Nombre: "git-push"
5. Selecciona: `repo` (full control)
6. Click "Generate"
7. **Copia el token** (no lo pierdes de vista)
8. Cuando git pida password, pega el token

### Guardar credenciales (para no escribir cada vez)
```bash
git config --global credential.helper wincred
# Próximo push te pide una sola vez, luego lo guarda
```

---

## ALIAS (Comandos más cortos)

Si escribes mucho:
```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.cm "commit -m"
git config --global alias.ps push
git config --global alias.pl pull

# Ahora:
git st    # en lugar de git status
git co -b feature/nombre  # git checkout -b
git cm "mensaje"  # git commit -m
git ps  # git push
git pl  # git pull
```

---

## WORKFLOW COMPLETO VIDEO (en tu cabeza)

### Escenario: Hoy trabajas 2 horas en 1 feature

```bash
# 9:00 AM - Empiezo
git checkout -b feature/agregar-monitor-v2

# 10:30 AM - Primer checkpoint
git add .
git commit -m "Add: monitor base structure"

# 11:15 AM - Más features
git add .
git commit -m "Add: monitor logic con thresholds"

# 11:45 AM - Testing
git add tests/
git commit -m "Test: validar monitor con 5 SKUs"

# 12:00 PM - Listo, subo
git push origin feature/agregar-monitor-v2

# En GitHub: Create PR, self-approve, merge

# 12:05 PM - Back to main
git checkout main
git pull
# Listo, feature está integrada
```

---

## CHECKLIST ANTES DE CADA PUSH

```
☑️ git status (¿archivos correctos?)
☑️ ¿El mensaje de commit es claro?
☑️ ¿Probé el código antes?
☑️ ¿No estoy subiendo credenciales?
☑️ git push

Done.
```

---

## SI NO SABES QUÉ HACER

1. Abre terminal
2. Escribe: `git status`
3. Git te dirá qué cambios tienes
4. Busca abajo en este archivo qué necesitas

No hay forma de romper nada permanentemente con Git.
Todo se puede deshacer.

---

**IMPRIMIR ESTO / BOOKMARK / REFERENCIA**

Eres libre. 🦈
