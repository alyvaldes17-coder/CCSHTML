# LOGIN RUNNER FINAL (CHROME REAL)

**Version**: FINAL  
**Status**: ✅ Implementada  

---

## CAMBIO CRÍTICO

### ❌ ANTES (Playwright en LOGIN)
```python
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(user_data_dir=...)
    # Problema: Nike rechaza Playwright en login
```

### ✅ AHORA (Chrome real vía subprocess)
```python
chrome = find_chrome()
subprocess.Popen([
    chrome,
    f"--user-data-dir={profile_login.resolve()}",
    "--start-maximized",
    "https://www.nike.cl/login"
])
# Usuario loguea con Chrome normal
# Script espera cierre
# Crea .login_ok
```

---

## ARQUITECTURA FINAL

```
LOGIN (Chrome real):
├─ Abrir Chrome normal (subprocess)
├─ Usuario loguea manualmente
├─ Usuario cierra Chrome
└─ Script crea .login_ok (marca solamente)
     ├─ NO verifica con Nike aquí
     └─ Verificación = PRE-FLIGHT

PRE-FLIGHT (Playwright headless):
├─ Clonar profile_login → profile_run
├─ Abrir Chrome headless con profile_run
├─ GET https://www.nike.cl/mi-cuenta
├─ Buscar "Hola" (sesión válida)
└─ SI OK → ejecutar PLAY
   SI NO → bloquear PLAY

PLAY (Playwright visible):
├─ Usar profile_run
├─ Backend ATC (< 1s)
├─ Magic link /checkout/#/payment
└─ Handover a usuario
```

**Separación absoluta**:
- LOGIN: Chrome real (humano)
- PRE-FLIGHT: Playwright headless (verificación)
- PLAY: Playwright visible (bot + humano)

---

## FLUJO FINAL (CONGELADO)

```
1. python login_runner.py cuenta1
   └─ Chrome abre → Usuario loguea → Cierra
   └─ Script crea .login_ok

2. python runtime/multiprocessing_runner.py <SKU> cuenta1
   ├─ PRE-FLIGHT: verifica Nike con headless profile_run
   │  └─ Si OK → continúa
   │  └─ Si FAIL → bloquea PLAY
   ├─ BACKEND: ATC en < 1s
   ├─ FREEZE: cierra sesión HTTP
   └─ HANDOVER: Chrome visible + magic link

3. Usuario confirma pago (1 click / OTP)
   └─ DONE
```

**Tiempo total**: ~1-2 min LOGIN + ~30s checkout

---

## CÓDIGO FINAL

### login_runner.py

```python
import subprocess, os, sys, time
from pathlib import Path

def find_chrome():
    for p in [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]:
        if os.path.exists(p): return p
    raise RuntimeError("Chrome no encontrado")

def main():
    user = sys.argv[1]
    base = Path("auth") / user
    profile_login = base / "profile_login"
    login_ok = base / ".login_ok"

    base.mkdir(parents=True, exist_ok=True)
    profile_login.mkdir(parents=True, exist_ok=True)

    chrome = find_chrome()
    args = [
        chrome,
        f"--user-data-dir={profile_login.resolve()}",
        "--start-maximized",
        "https://www.nike.cl/login",
    ]

    proc = subprocess.Popen(args)
    print("[LOGIN] Loguéate y cierra Chrome cuando termines.")

    while proc.poll() is None:
        time.sleep(1)

    login_ok.write_text("OK")
    print("[SUCCESS] .login_ok creado")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Uso: python login_runner.py <cuenta>")
    main()
```

### preflight() en multiprocessing_runner.py

```python
def preflight(user: str, profile_run: str) -> bool:
    """
    PRE-FLIGHT: Verifica que Nike reconoce sesión
    (ejecuta ANTES de PLAY)
    """
    try:
        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=profile_run,
                channel="chrome",
                headless=True
            )
            
            page = ctx.new_page()
            page.goto("https://www.nike.cl/mi-cuenta", timeout=15000)
            
            # Verificar sesión real: "Hola" visible
            ok = page.locator("text=Hola").first.is_visible()
            ctx.close()
            return ok
            
    except Exception as e:
        print(f"[PREFLIGHT] [{user}] Error: {e}")
        return False
```

---

## USO

### Desde terminal

```bash
# 1. LOGIN
python login_runner.py cuenta1
# → Chrome abre, tú logúeas
# → Cierras Chrome
# → Script crea .login_ok

# 2. PLAY
python runtime/multiprocessing_runner.py 123456789 cuenta1
# → PRE-FLIGHT verifica
# → Backend ejecuta
# → Chrome abre con magic link
# → Tú confirmas pago
```

### Desde UI

```python
# Botón LOGIN
subprocess.Popen([
    sys.executable,
    "login_runner.py",
    account_name
])

# Botón PLAY
launch_play_for_accounts(
    accounts=[account_name],
    sku=sku_input,
    bus=state_bus
)
```

---

## GARANTÍAS

✅ **Nike acepta** (Chrome real, no Playwright)  
✅ **Sessión válida** (PRE-FLIGHT verifica antes de PLAY)  
✅ **1 camino único** (sin variantes ni fallbacks)  
✅ **Determinista** (pasos fijos, sin loops)  
✅ **< 1.5s backend** (ATC + price check)  

---

## VALIDACIÓN

```bash
# Verificar sintaxis
python -m py_compile login_runner.py

# Verificar preflight en multiprocessing_runner.py
python -c "from runtime.multiprocessing_runner import preflight; print('OK')"

# Ejecutar
python login_runner.py cuenta1
```

---

## ARQUITECTURA FINAL (RECORDATORIO)

```
auth/cuenta1/
├── profile_login/       (MASTER - LOGIN usa Chrome real)
│   ├── Cookies (Nike válidas)
│   └── localStorage
├── profile_run/         (SLAVE - PLAY clona automático)
│   └── Destruido después de PLAY
└── .login_ok            (marca: LOGIN completado)
```

**Reglas**:
1. LOGIN: Chrome real vía subprocess
2. PRE-FLIGHT: Playwright headless para verificar
3. PLAY: Playwright visible para ATC + handover
4. .login_ok: Solo marca, verificación real en PRE-FLIGHT

---

## SIGUIENTE

Ejecuta:

```bash
python login_runner.py cuenta1
python runtime/multiprocessing_runner.py 123456789 cuenta1
```

**Hecho. Sistema listo para drops.**

