# ATC EXACTO - LA VERDAD DEL ENDPOINT

## Status
**CONGELADO** - Esta es la definición final, no se cambia nunca más.

---

## ENDPOINT EXACTO

```
GET https://www.nike.cl/checkout/cart/add?sku=SKU&qty=1&seller=1&sc=1
```

**Componentes:**
- **Protocol**: HTTPS (no HTTP)
- **Host**: www.nike.cl (no nike.cl)
- **Path**: /checkout/cart/add (no /checkout, no /api, no /payment)
- **Method**: GET (no POST)
- **Query Params**:
  - `sku`: String del SKU (ej: "123456789")
  - `qty`: Integer 1 (siempre 1)
  - `seller`: Integer 1 (siempre 1)
  - `sc`: Integer 1 (siempre 1 - subcategory flag)

---

## RESPUESTAS VÁLIDAS

### Éxito (Status 200)
```json
{
  "items": [
    {
      "id": "123456789",
      "name": "Nike React Phantom Run",
      "price": 79990,
      "quantity": 1,
      "seller": 1
    }
  ]
}
```

**Validación**: price > 0 ✅

### Éxito (Status 302 - Redirect)
```
Location: https://www.nike.cl/checkout/#/cart
```

**Validación**: Status 302 solo ocurre si redirige a cart → ✅

### Falla (Status 400 - Bad Request)
```json
{
  "error": "sku_not_found"
}
```

**Validación**: Status ≠ 200 y ≠ 302 → ❌

### Falla (Status 500 - Server Error)
```
Internal Server Error
```

**Validación**: Status 500 → ❌

### Falla (Status 408 - Timeout)
```
Request Timeout
```

**Validación**: Timeout después de 2s → ❌

---

## COOKIES REQUERIDAS

**Mínimas necesarias:**
```
vtex_session=<session_id>
__vid=<visitor_id>
VtexIdcClientAutCookie=<auth_id>
```

**Origen**: profile_run (clonado desde profile_login después de .login_ok)

**Validación**: PRE-FLIGHT verifica que Nike.cl/mi-cuenta reconoce al usuario

---

## LÓGICA EXACTA DE VALIDACIÓN

```python
def is_atc_success(status_code: int, response_body: dict) -> bool:
    # Regla 1: Status code debe ser 200 o 302
    if status_code not in (200, 302):
        return False
    
    # Regla 2: Si 200, validar price > 0
    if status_code == 200:
        try:
            items = response_body.get("items", [])
            if not items:
                return False
            
            price = items[0].get("price", 0)
            if price <= 0:
                return False
        except:
            return False
    
    # Regla 3: Si 302, es redirect → OK
    # (no validar body, solo status)
    
    return True
```

---

## TIMEOUT

**Máximo**: 2 segundos por intento

**Retries**: Máx 1 (solo en timeout)

**Total**: 4 segundos máx (2s + 2s)

```python
session.get(
    url,
    params=params,
    timeout=2,  # 2 segundos
    allow_redirects=False  # Capturar el 302, no seguir redirect
)
```

---

## MAGIC LINK (LINK AL MISMO ENDPOINT)

```
https://www.nike.cl/checkout/cart/add?sku=SKU&qty=1&seller=1&sc=1
```

**¿Es el mismo que el GET backend?**

Sí, EXACTAMENTE igual.

**¿Por qué?**

- GET backend agrega al carrito (VTEX side)
- Magic link lleva el browser al mismo sitio (user side)
- Nike.cl reconoce el item ya en carrito y lo muestra
- User termina checkout desde allí

**¿No /checkout/#/payment?**

No. Eso es routing client-side que puede no funcionar si no hay cookies correctas.

**¿No /checkout?**

No. Eso es el cart view, pero no te asegura que el item esté ahí.

**Resumen**: 
- ATC backend: GET /checkout/cart/add?... → agrega item
- Magic link: MISMO URL → browser va al mismo sitio, item ya está ahí
- No hay 2 caminos, hay 1 camino usado de 2 formas (backend + browser)

---

## FLOW EXACTO (CONGELADO)

### Paso 4: ATC_BACKEND

```python
# GET backend
GET https://www.nike.cl/checkout/cart/add?sku=..&qty=1&seller=1&sc=1
# Response: 200 con items, o 302 redirect
# Validación: price > 0 (si 200) o status 302
# Timeout: 2s max
# Retries: 1 (solo timeout)
```

### Paso 5: PRICE_CHECK

```python
# Verificar que price > 0 en response
# Si status 200: extraer items[0].price
# Si status 302: asumir OK (redirect a checkout)
# Si price ≤ 0: FAIL
```

### Paso 6: FREEZE_BACKEND

```python
# session.close()
# NO MÁS REQUESTS
# Fin del backend
```

### Paso 7: HANDOVER

```
Magic link: https://www.nike.cl/checkout/cart/add?sku=...&qty=1&seller=1&sc=1
Browser abre link
```

---

## QUÉ NO ES VÁLIDO

❌ POST /checkout/cart/add (no GET)
❌ GET /checkout (sin /cart/add)
❌ GET /checkout/#/payment (client-side routing)
❌ GET /checkout/#/cart (client-side routing)
❌ GET /checkout/cart/add sin parámetros
❌ GET /checkout/cart/add?sku=... (falta qty, seller, sc)
❌ GET /api/checkout/cart/add (/api no existe en Nike.cl)
❌ GET /checkout/cart/add con qty=2
❌ GET /checkout/cart/add con seller=2
❌ Usar session seed (sesión abierta del browser)
❌ Iterar/reintentar después de FREEZE
❌ Cambiar el endpoint durante drops

---

## FUENTE DE VERDAD

**Obtenido de**: Nike.cl/checkout network intercept (real drops)

**Validado en**: Nike.cl login + preflight + backend

**Última actualización**: [AHORA - CONGELADO]

**Cambios futuros**: NONE

---

## CONCLUSIÓN

**ATC en Nike.cl es simple:**
- GET endpoint + parámetros exactos
- VTEX agrega al carrito
- Frontend abierto en browser, item ya está
- User completa checkout

**El secreto no es la complejidad, es la CONSISTENCIA.**

El endpoint no cambia. Las cookies no cambian. El flujo no se itera.

**Eso es todo lo que necesitas.**
