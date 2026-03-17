## ✅ FIX CRÍTICO IMPLEMENTADO

### Problema identificado
PlaywrightEngine.launch_checkout_mission() cerraba Chrome inmediatamente porque:
1. El `with sync_playwright()` terminaba el bloque
2. No había loop para mantener el proceso vivo
3. El browser se cerraba cuando el contexto salía del `with`

### Solución implementada

**Archivo**: `engines/playwright_engine_v2.py`
**Método**: `launch_checkout_mission()`

**Cambios:**
```python
# ❌ ANTES (cierra Chrome inmediatamente)
with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(...)
    page.goto(sku_url)
    try:
        page.wait_for_event("close", timeout=0)
    except Exception:
        pass
# <-- with termina, Chrome cierra


# ✅ DESPUÉS (mantiene Chrome abierto)
with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(...)
    page.goto(sku_url)
    
    # 🔴 BLOQUEO ABSOLUTO
    try:
        while True:
            time.sleep(1)  # <-- Mantiene vivo indefinidamente
    except KeyboardInterrupt:
        print("Cierre manual detectado")
```

### Garantías de la solución

✅ Chrome NO se cierra automáticamente
✅ El método es BLOQUEANTE (espera hasta cierre manual)
✅ Magic URL se imprime (visible en logs)
✅ headless=False (navegador visible)
✅ Usa profile_path absoluto (inyecta cookies correctas)
✅ NO se ejecuta en thread (se ejecuta en hilo principal)

### Validación de integración

**Punto de llamada**: `runtime/bot_controller.py` línea 212

```python
self.state = AccountState.EXECUTING
print(f"[{self.account_name}] 🚀 ESTADO: EXECUTING")

self.engine.launch_checkout_mission(sku_url)  # ← BLOQUEANTE, sin thread

print(f"[{self.account_name}] ✅ Worker finalizado")
break
```

✅ **CORRECTO**: Se llama directamente, no en thread

### Logs esperados ahora

```
[cuenta2] 🚀 ESTADO: EXECUTING
[PlaywrightEngine] 🚀 Iniciando CHECKOUT (Chrome real)...
[PlaywrightEngine] Profile: C:\...\auth\cuenta2\profile_run
[PlaywrightEngine] Magic URL: https://www.nike.cl/checkout/cart/add?sku=170369...
[PlaywrightEngine] ⚙️ Lanzando navegador persistente...
[PlaywrightEngine] 🌐 Navegando a magic link...
[PlaywrightEngine] ✅ Chrome ABIERTO. Control humano.
[PlaywrightEngine] 💳 Completa el pago en tu banco
[PlaywrightEngine] ❗ NO se cerrará automáticamente
[PlaywrightEngine] ⏳ Esperando cierre manual...
```

**Ahora Chrome debería ABRIRSE y QUEDARSE ABIERTO.**

### Checklist final

- [x] launch_checkout_mission() tiene while True con time.sleep(1)
- [x] headless=False
- [x] magic_url se imprime (URL completa visible)
- [x] NO se ejecuta en thread (se ejecuta directamente)
- [x] profile_path es absoluto
- [x] Se bloquea hasta cierre manual (Ctrl+C)

---

**ESTADO**: ✅ LISTO PARA TESTING

Ejecuta ahora y deberías ver Chrome abrirse y quedarse abierto hasta que cierres manualmente.
