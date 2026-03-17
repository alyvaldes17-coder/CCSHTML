# 🔫 Solución Quirúrgica - Referencia Rápida

## Cambios Realizados

### 1️⃣ Creado: `utils.py` (NUEVO)

```python
def matar_chrome_especifico(profile_path: str) -> None
```

**Qué hace:**
- Busca procesos de `chrome.exe` que usen una carpeta **específica**
- Usa comando WMIC para ser quirúrgico
- Mata SOLO esos procesos (no toca Chrome en general)
- Espera 1 segundo a que Windows libere archivos bloqueados

**Importancia:**
- Resuelve el problema de "Chrome fantasma" bloqueando la carpeta del perfil
- Seguro para tu Chrome personal (no lo toca)

**Comando interno:**
```bash
wmic process where "name='chrome.exe' and CommandLine like '%AUTH%CUENTA2%PROFILE_PW%'" call terminate
```

---

### 2️⃣ Actualizado: `engines/manual_login.py`

**Cambio 1: Import**
```python
from utils import matar_chrome_especifico
```

**Cambio 2: En `open_chrome_for_login_native()`**
```python
def open_chrome_for_login_native(account_name: str, profile_dir: str) -> bool:
    abs_profile_path = os.path.abspath(profile_dir)
    
    # 🔫 LIMPIEZA QUIRÚRGICA - AHORA AQUÍ
    matar_chrome_especifico(abs_profile_path)
    
    # ... resto del código
```

**Cambio 3: En `open_chrome_for_login_playwright()`**
```python
def open_chrome_for_login_playwright(account_name: str, profile_dir: str) -> bool:
    abs_profile_path = os.path.abspath(profile_dir)
    
    # 🔫 LIMPIEZA QUIRÚRGICA - AHORA AQUÍ
    matar_chrome_especifico(abs_profile_path)
    
    # ... resto del código
```

---

## Flujo de Ejecución

```
Usuario haz click en [LOGIN]
         ↓
    ui/app.py
         ↓
    state_machine.play()
         ↓
    engines/manual_login.py::open_chrome_for_login()
         ↓
    ┌─ PASO 1: matar_chrome_especifico(auth/cuenta2/profile_pw)
    │         ├─ ¿Hay Chrome colgado usando esa carpeta? → MUERE
    │         └─ Tu Chrome (YouTube, Gmail) → INTACTO (no usa esa carpeta)
    │
    ├─ PASO 2: Convertir a ruta ABSOLUTA
    │
    ├─ PASO 3: Validar carpeta
    │
    ├─ PASO 4: Buscar Chrome
    │
    ├─ PASO 5: Lanzar Chrome
    │         └─ Carpeta AHORA está libre (no bloqueada)
    │
    └─ PASO 6: Mostrar instrucciones
```

---

## Por Qué Funciona (Técnico)

| Problema | Causa | Solución |
|----------|-------|----------|
| Chrome no abre | Carpeta bloqueada por proceso fantasma | `matar_chrome_especifico()` mata procesos de esa carpeta |
| Mata tu Chrome | Solución anterior usaba `taskkill /F /IM chrome.exe` | WMIC busca procesos específicos por ruta |
| Windows bloquea | Si un proceso tiene abierta una carpeta, no se puede reusar | Esperar 1 segundo después de terminar proceso |

---

## Verificaciones

- ✅ `utils.py`: Sintaxis verificada
- ✅ `engines/manual_login.py`: Sintaxis verificada
- ✅ Imports correctos
- ✅ Función `matar_chrome_especifico()` disponible en ambos métodos

---

## Próximo Paso

En la UI, haz click en **LOGIN**:

1. Sistema automáticamente:
   - Busca procesos fantasma
   - Los mata si existen
   - Abre Chrome limpio
   
2. Tú:
   - Logueas en Nike
   - Cierras con X (crítico)
   
3. Sistema:
   - Guarda cookies automáticamente

---

## Si Algo Falla

**Chrome no abre:**
1. Abre Task Manager (Ctrl+Shift+Esc)
2. Busca `chrome.exe`
3. Verifica que no hay procesos huérfanos
4. Si hay, mátalos manualmente

**WMIC no funciona:**
1. Abre CMD como Administrador
2. Prueba: `wmic process list brief`
3. Si falla, WMIC no está disponible (muy raro en Windows 10+)

**Carpeta sigue bloqueada:**
1. Reinicia Windows (libera todos los procesos)
2. Intenta nuevamente

---

## Documentación Completa

Más detalles en: [docs/SOLUCION_QUIRURGICA.txt](../docs/SOLUCION_QUIRURGICA.txt)
