# 🚀 Git & GitHub — Guía Rápida (Sin Preguntar)

## PARTE 1: GIT BÁSICO (Local)

### 1️⃣ Inicializar repositorio en tu proyecto
```bash
cd c:\Users\beriann\Documents\Repos\nikebotprofuncionalv1
git init
```
✅ Crea carpeta `.git` (control de versiones local)

### 2️⃣ Ver estado actual
```bash
git status
```
Muestra qué archivos cambiaron, cuáles están "staged" (listos para commit).

### 3️⃣ Agregar archivos (staging)
```bash
# Agregar TODO
git add .

# Agregar solo un archivo
git add nike_bot_pro/engines/engine.py

# Agregar carpeta específica
git add nike_bot_pro/
```

### 4️⃣ Hacer commit (guardar snapshot)
```bash
# Con mensaje
git commit -m "Initial commit: Nike Bot v11.2 - Production Ready"

# Mensaje multiline si cambios son complejos
git commit -m "Fix: evento_handshake payment_mode parameter

- Removed --headless=new flag (Shape Security detection)
- Optimized timings: loop 300ms → 50ms
- Added payment_url extraction from Fintoc"
```

### 5️⃣ Ver historial
```bash
# Últimos commits
git log

# Más compacto
git log --oneline -10

# Detalles de cambios
git log -p -5
```

---

## PARTE 2: GITHUB (Nube)

### 1️⃣ Crear repositorio en GitHub
**En navegador:**
1. Ve a https://github.com/new
2. Nombre: `nikebotprofuncionalv1`
3. Descripción: `Nike Bot v11.2 - Alto rendimiento ATCs con optimizaciones de timing y Discord`
4. **Visibility: PRIVATE** (si tienes equipo, solo ellos ven)
5. NO marques "Initialize with README" (ya tienes código local)
6. Click **Create repository**

**Resultado:** URL como `https://github.com/TU_USUARIO/nikebotprofuncionalv1.git`

### 2️⃣ Conectar tu local a GitHub
```bash
git remote add origin https://github.com/TU_USUARIO/nikebotprofuncionalv1.git
git branch -M main
git push -u origin main
```

**Qué hace:**
- `remote add origin` = Link con la nube
- `branch -M main` = Renombra rama a "main" (estándar GitHub)
- `push -u origin main` = Sube código + vincula rama

### 3️⃣ Verificar conexión
```bash
git remote -v
```
Debe mostrar:
```
origin  https://github.com/TU_USUARIO/nikebotprofuncionalv1.git (fetch)
origin  https://github.com/TU_USUARIO/nikebotprofuncionalv1.git (push)
```

### 4️⃣ Push (subir cambios)
```bash
# Después de hacer commit
git push origin main

# Próximas veces, solo:
git push
```

### 5️⃣ Pull (bajar cambios)
```bash
# Si un colega hizo cambios
git pull origin main

# O solo:
git pull
```

---

## PARTE 3: COLABORACIÓN

### Escenario: Un colega quiere contribuir

#### Paso 1️⃣: Invitar al repositorio
**En GitHub:**
1. Settings → Collaborators → Add people
2. Escribe email/username del colega
3. Click Add

#### Paso 2️⃣: El colega clona el repo
```bash
git clone https://github.com/TU_USUARIO/nikebotprofuncionalv1.git
cd nikebotprofuncionalv1
```

#### Paso 3️⃣: Colega crea rama para su feature
```bash
# Crear rama nueva
git checkout -b feature/agregar-proxy-rotacion

# Edita código...
git add .
git commit -m "Add: Rotación de proxies en modo_monitor"

# Sube la rama
git push origin feature/agregar-proxy-rotacion
```

#### Paso 4️⃣: Pull Request (pedir aprobación)
**En GitHub:**
1. Verás botón "Compare & pull request" después del push
2. Describe qué cambios hizo
3. Click "Create pull request"
4. Tú revisas el código y haces click "Merge pull request"

#### Paso 5️⃣: Tu local se actualiza
```bash
git checkout main
git pull origin main
# Código del colega ahora está en tu máquina
```

---

## PARTE 4: CREAR .gitignore (MUY IMPORTANTE)

Crear archivo `.gitignore` en raíz del proyecto:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/

# Entornos
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Archivos sensibles (NO subir credenciales)
auth/*/cookies_extracted.json
auth/*/session_token.json
*.bak
.DS_Store

# Logs
logs/
*.log

# Chrome/Chromium
.chromium/
profile_pw/
```

**Luego:**
```bash
git add .gitignore
git commit -m "Add: gitignore para archivos sensibles"
git push
```

---

## PARTE 5: CUANDO HAY CONFLICTOS

### Conflicto = Tú y colega editaron MISMO archivo

**Síntoma:**
```bash
git pull
CONFLICT (content): Merge conflict in nike_bot_pro/engines/engine.py
```

**Solución:**
1. Abre el archivo en VS Code
2. Verás secciones con `<<<<<<`, `======`, `>>>>>`
3. Elige qué código mantener (VS Code te muestra botones)
4. Guarda el archivo
5. Haz commit:
```bash
git add .
git commit -m "Resolve merge conflict in engine.py"
git push
```

---

## PARTE 6: COMANDOS DE RESCATE

| Comando | Qué hace |
|---------|----------|
| `git status` | Ver qué cambió |
| `git diff` | Ver exactamente qué líneas cambiaron |
| `git log --oneline` | Ver historial compacto |
| `git checkout -- archivo.py` | Deshacer cambios en un archivo |
| `git reset HEAD~1` | Deshacer último commit (pero mantiene cambios) |
| `git revert <hash>` | Hacer commit inverso (SEGURO) |
| `git branch -a` | Ver todas las ramas |
| `git checkout -b nueva-rama` | Crear nueva rama |
| `git branch -d rama-vieja` | Borrar rama local |

---

## PARTE 7: FLUJO TÍPICO PARA TI

### Desarrollo normal:
```bash
# Día 1: Cambios en engine.py
cd c:\Users\beriann\Documents\Repos\nikebotprofuncionalv1
git status
git add nike_bot_pro/engines/engine.py
git commit -m "Optimize: reducir timeout EV4 a 20s"
git push

# Día 2: Cambios en config
git add nike_bot_pro/config/
git commit -m "Update: nuevos parámetros de stealth"
git push
```

### Con colega:
```bash
# Tu rama de feature
git checkout -b feature/discord-embeds
git add .
git commit -m "Add: Discord embeds mejorados con Nike branding"
git push origin feature/discord-embeds

# Colega revisa en GitHub → Merge
# Tú actualizas tu local:
git checkout main
git pull
```

---

## PARTE 8: CHEAT SHEET VISUAL

```
┌─────────────────────────────────────┐
│ ARCHIVO LOCAL (no tracked)          │
└──────────────┬──────────────────────┘
               │ git add .
               ▼
┌─────────────────────────────────────┐
│ STAGING AREA (staged, listo)        │
└──────────────┬──────────────────────┘
               │ git commit -m "..."
               ▼
┌─────────────────────────────────────┐
│ LOCAL REPO (.git)                   │
└──────────────┬──────────────────────┘
               │ git push origin main
               ▼
┌─────────────────────────────────────┐
│ GITHUB (remote/cloud)               │
└─────────────────────────────────────┘
```

---

## PARTE 9: TRUCOS PRO

### 1. Amending (reparar último commit sin crear uno nuevo)
```bash
# Olvide incluir un archivo o el mensaje sucks
git add archivo_olvidado.py
git commit --amend -m "Fix: mejor descripción"
git push -f origin main  # (cuidado, solo si no lo vió colega)
```

### 2. Stash (guardar cambios sin commitear)
```bash
# Inespecido: necesitas cambiar de rama pero no quieres commitear
git stash
git checkout otra-rama
# Luego:
git checkout mi-rama
git stash pop
```

### 3. Tags (marcar versiones importantes)
```bash
git tag v11.2-production
git push origin v11.2-production

# Listar
git tag -l
```

### 4. GitHub Actions (automático)
Crea `.github/workflows/test.yml` para tests automáticos en cada push.
(No lo necesitas aún, pero existe)

---

## PARTE 10: PROBLEMAS COMUNES

| Problema | Solución |
|----------|----------|
| "fatal: not a git repository" | Corre `git init` en carpeta raíz |
| "fatal: destination path ... already exists" | El repo ya existe, no clones |
| "error: src refspec main does not match any" | Haz commit ANTES de push |
| "everything up-to-date" pero no se subió | Probablemente cambios están en stash |
| "conflict merge" | Edita archivo conflictivo, resuelve, commit |
| Quieres deshacer push a GitHub | `git revert <hash>` (SEGURO) |

---

## PARTE 11: REFERENCIAS RÁPIDAS

**Git Oficial:** https://git-scm.com/doc
**GitHub Docs:** https://docs.github.com
**Interactive Learning:** https://learngitbranching.js.org/

---

## TL;DR — MÁS RÁPIDO

```bash
# Primera vez
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USER/nikebotprofuncionalv1.git
git branch -M main
git push -u origin main

# Diariamente
git add .
git commit -m "Descripción del cambio"
git push

# Con colega
git checkout -b feature/algo
# ... edita ...
git add .
git commit -m "..."
git push origin feature/algo
# → Va a GitHub, colega aprueba, tú haces merge
```

---

## TABLA DE AYUDA RÁPIDA

Pega esto en terminal cuando no recuerdes:

| Quiero... | Comando |
|-----------|---------|
| Ver cambios | `git status` |
| Ver líneas exactas cambiadas | `git diff` |
| Guardar cambios | `git add . && git commit -m "msg"` |
| Subir a GitHub | `git push` |
| Bajar cambios de GitHub | `git pull` |
| Crear rama nueva | `git checkout -b nombre` |
| Cambiar rama | `git checkout nombre` |
| Ver todas las ramas | `git branch -a` |
| Ver historial | `git log --oneline -10` |
| Deshacer último commit | `git reset HEAD~1` |
| Conectar a GitHub | `git remote add origin URL` |

---

## ✅ Estás listo. No preguntes más jaja

Keep this open in a tab. Bookmark it. You got this. 🦈
