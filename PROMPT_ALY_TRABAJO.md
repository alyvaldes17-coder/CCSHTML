# PROMPT PARA ALY — Área SKUs (Frontend + Backend)
## Nike Bot Pro — Trabajo en Paralelo

---

## CÓMO TRABAJAMOS

Trabajamos **en paralelo**, cada uno con su vista completa (UI + backend):

| Quién | Área | Frontend | Backend |
|-------|------|----------|---------|
| **Yo (Brian)** | **DROP** — Motor del bot | `Drop.tsx` | `bot_api.py`, `stock_monitor.py` |
| **Tú (Aly)** | **SKUs** — Búsqueda y catálogo | `Skus.tsx` | Lógica VTEX |

Así cada uno ve su progreso en su pantalla sin interferir con el otro.

---

## CONTEXTO GENERAL

App de escritorio Tauri (React + Rust + Python) para Nike bot. 6 secciones: Login, Home, SKUs, Drop, Wallet, Config.

```
client_app/          ← App Tauri (React + TypeScript + Rust)
├── src/pages/       ← Páginas: Login, Home, SKUs, Drop, Wallet, Config
├── src/services/    ← api.ts (auth Railway), botSocket.ts (WebSocket)
├── src/components/  ← Sidebar, Toast, SnakeLogo
└── src/App.tsx      ← Router + estado sesión

nike_bot_pro/        ← Bot engine Python
├── bot_api.py       ← FastAPI localhost:8000 (WebSocket + REST) — LO MANEJO YO
├── stock_monitor.py ← Monitor stock VTEX — LO MANEJO YO
└── ...
```

### API externa disponible
```
VTEX Nike.cl: https://www.nike.cl/api/catalog_system/pub/products/search
  - Por SKU:    ?fq=skuId:134427
  - Por nombre: ?ft=air+max&_from=0&_to=9
  - Por marca:  ?fq=B:nike
```

---

## TU ÁREA DE TRABAJO

### Archivos que TÚ manejas:
```
client_app/src/pages/Skus.tsx       ← Tu vista principal (ya funcional, mejorar)
```

### Archivos que puedes crear si necesitas:
```
client_app/src/services/skuApi.ts   ← Si quieres extraer la lógica VTEX a un servicio aparte
client_app/src/components/SkuXXX.tsx ← Componentes auxiliares de SKU que necesites
```

### Archivos que NO debes tocar:
```
client_app/src/pages/Drop.tsx        ← MI ÁREA
client_app/src/pages/Login.tsx       ← Compartido (no tocar)
client_app/src/services/botSocket.ts ← MI ÁREA
client_app/src/services/api.ts       ← Compartido (no tocar)
client_app/src/App.tsx               ← Compartido (pedir antes de editar)
nike_bot_pro/bot_api.py              ← MI ÁREA
nike_bot_pro/stock_monitor.py        ← MI ÁREA
```

---

## ESTADO ACTUAL DE Skus.tsx

La página **ya funciona**. Lo que tiene ahora:

- Busca en Nike.cl por SKU numérico o nombre de producto
- Muestra imagen del producto, precio, marca
- Tabla de tallas con stock en tiempo real (disponible/agotado, cantidad, precio)
- Chips de "SKUs guardados" en sessionStorage
- Botón + para guardar SKU, × para eliminar

### Código actual simplificado:
```tsx
// Búsqueda dual
const isSkuId = /^\d+$/.test(query);
const url = isSkuId
  ? `${NIKE_CATALOG}?fq=skuId:${query}`
  : `${NIKE_CATALOG}?ft=${encodeURIComponent(query)}&_from=0&_to=0`;

// Parseo de respuesta VTEX
item.sellers?.[0]?.commertialOffer → { IsAvailable, AvailableQuantity, Price }
item.Talla?.[0] || item.Size?.[0] → talla
item.images?.[0]?.imageUrl → imagen
```

### Tipos que usa:
```tsx
interface SkuItem {
  itemId: string; name: string; size: string;
  available: boolean; quantity: number; price: number; image: string;
}
interface ProductResult {
  productName: string; brand: string; link: string; items: SkuItem[];
}
```

---

## MEJORAS QUE NECESITA Skus.tsx

### Prioridad ALTA

1. **Búsqueda múltiple de productos** — Ahora solo muestra 1 producto. Si buscas por nombre ("air max"), VTEX devuelve un array. Mostrar TODOS los resultados en una grilla/lista, no solo `data[0]`.

2. **Paginación** — La API VTEX soporta `_from=0&_to=9`. Implementar botones "Cargar más" o paginación para navegar resultados.

3. **Filtros** — Agregar filtros útiles:
   - Solo con stock disponible
   - Rango de precios (min-max)
   - Por talla específica
   - Por categoría (`fq=C:/Hombre/Zapatillas/`)

4. **Auto-refresh / Polling** — Botón o toggle para re-chequear stock cada X segundos en los SKUs guardados. Esto es crucial para drops: el usuario guarda SKUs y quiere que se actualicen solos.

5. **Detalle expandible por talla** — Click en una talla para ver más datos: seller info, precio de lista vs precio con descuento, EAN, etc.

### Prioridad MEDIA

6. **Exportar SKUs guardados** — Botón para copiar lista de SKUs al clipboard o exportar como JSON. El Drop necesita recibir estos SKUs.

7. **Historial de búsquedas** — Guardar las últimas N búsquedas para acceso rápido.

8. **Vista grid vs lista** — Toggle entre vista actual (tabla) y vista grid (cards con imagen grande).

9. **Indicador visual de cambio de stock** — Si un SKU pasa de 0 a disponible, destacarlo con animación/color. Esto es el "stock alert" visual.

10. **Link directo al producto** — Botón que abra `product.link` en el navegador externo.

### Prioridad BAJA

11. **Comparador** — Seleccionar 2-3 productos para comparar lado a lado.

12. **Notificaciones** — Integrar con el sistema de Toast cuando cambia stock de un SKU guardado.

---

## CÓMO COMUNICAR SKUs AL DROP

Cuando yo necesite los SKUs guardados desde Drop.tsx, los voy a leer de `sessionStorage.getItem("aoda_skus")`. Ese es nuestro **contrato de datos**:

```tsx
// En sessionStorage, clave "aoda_skus"
// Formato: JSON string de array de strings
// Ejemplo: ["134427", "155832", "201445"]

// TÚ escribes (ya lo haces):
sessionStorage.setItem("aoda_skus", JSON.stringify(savedSkus));

// YO leo desde Drop.tsx:
const skus = JSON.parse(sessionStorage.getItem("aoda_skus") || "[]");
```

Si quieres enviar más info (nombre, talla seleccionada), podemos usar otro key:
```tsx
// sessionStorage key "aoda_sku_details"
// Formato: { [skuId]: { name, size, price } }
```
Proponme el formato si necesitas algo distinto.

---

## REGLAS TÉCNICAS

### Stack
- **React 19** + **TypeScript** strict
- **CSS inline** con objeto `t` del theme — NO librerías UI
- `import { T } from "../theme"` → tu componente recibe `{ t }: { t: T }`
- Toast: `import Toast from "../components/Toast"`
- **NO usar localStorage** en Tauri — usa `sessionStorage` para datos temporales o `@tauri-apps/plugin-store` para persistencia

### Estructura de componente
```tsx
import { useState, useCallback } from "react";
import { T } from "../theme";

export function SKUs({ t }: { t: T }) {
  // tu código...
  return <div style={{ padding: 28, color: t.text }}>...</div>;
}
```

### Colores del theme (lo que tiene `t`)
```
t.text       — texto principal
t.textDim    — texto secundario
t.textMed    — texto medio
t.bg         — fondo
t.panel      — fondo de paneles
t.row        — fondo de filas
t.border     — bordes
t.green      — color de éxito/acción
t.greenDim   — fondo verde suave
t.red        — color de error
t.redDim     — fondo rojo suave
```

---

## GIT WORKFLOW

### Rama
```bash
git checkout feat/tauri-client
git pull origin feat/tauri-client   # SIEMPRE antes de empezar
```

### Commit
```bash
git add client_app/src/pages/Skus.tsx client_app/src/services/skuApi.ts  # etc
git commit -m "feat(skus): búsqueda múltiple + paginación VTEX"
git push origin feat/tauri-client
```

### Prefijos
- `feat(skus):` para nuevas funcionalidades
- `fix(skus):` para correcciones
- `style(skus):` para cambios visuales

### Antes de push
```bash
cd client_app
npm run build    # Verificar que compila
```

---

## CÓMO PROBAR

```bash
# Terminal 1 — Solo frontend (rápido, sin Rust)
cd client_app
npm run dev
# Abre http://localhost:1420

# Terminal 2 — App completa con Tauri
cd client_app
npm run tauri dev
```

La página de SKUs no necesita bot_api.py para funcionar — habla directo con Nike.cl.

---

## REGLAS DE CONVIVENCIA

1. **NO toques archivos fuera de tu área** — si algo te bloquea, avísame
2. **Pull antes de empezar** cada sesión de trabajo
3. **Commits atómicos** — un commit por feature, no mega-commits
4. Si necesitas que App.tsx te pase props nuevos → pídeme
5. El contrato de datos entre SKUs y Drop es via `sessionStorage("aoda_skus")` — si quieres cambiarlo, coordinamos

---

*Rama: `feat/tauri-client` | Repo: CCSHTML*
