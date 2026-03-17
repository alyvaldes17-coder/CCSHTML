"""
engines/card_payment_js.py — v3.0 PRODUCCIÓN

Cambios vs v2:
  - Protocolo anti-descuento nuclear ANTES de llenar campos
  - Verificación de precio > $0 ANTES del click — aborta si Nike bajó a $0
  - Fail-fast: detecta modal de rechazo en <100ms
  - async/await secuencial + waitFor polling
  - btnFin.click() con retry automático
  - MAX_MS subido a 25s para dar margen a la purga
"""


def build_card_js(card_data: dict, card_type: str = "debit") -> str:
    """
    Genera JS para llenar formulario de tarjeta Nike.cl y hacer click en Finalizar.

    Args:
        card_data: {
            "card_number":    "1234567890123456",
            "card_cvv":       "123",
            "card_expiry_mm": "12",
            "card_expiry_aa": "27",
            "card_name":      "NOMBRE APELLIDO",
            "card_rut":       "12345678-9",
        }
        card_type: "debit" | "credit"
    """
    number = card_data.get("card_number", "").replace(" ", "")
    cvv    = card_data.get("card_cvv", "")
    mm     = card_data.get("card_expiry_mm", "").zfill(2)
    aa     = card_data.get("card_expiry_aa", "")[-2:]
    name   = card_data.get("card_name", "").upper()
    rut    = card_data.get("card_rut", "")

    return f"""
    (() => {{
        const NUMERO  = "{number}";
        const CVV     = "{cvv}";
        const MM      = "{mm}";
        const AA      = "{aa}";
        const NOMBRE  = "{name}";
        const RUT     = "{rut}";
        const TIPO    = "{card_type}";
        const MAX_MS  = 25000;
        const t0      = Date.now();

        // ── Helpers ──────────────────────────────────────────────────────────

        function elapsed() {{ return Date.now() - t0; }}

        // Llena un input de forma que React/VTEX lo detecte como escritura real
        function fill(input, value) {{
            if (!input) return false;
            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            input.focus();
            setter.call(input, value);
            ['input','change','blur'].forEach(ev =>
                input.dispatchEvent(new Event(ev, {{bubbles:true}}))
            );
            input.dispatchEvent(new KeyboardEvent('keyup', {{bubbles:true, key:'Tab'}}));
            return true;
        }}

        // Llena un select por valor o texto parcial
        function fillSelect(sel, value) {{
            if (!sel || !value) return false;
            for (const opt of sel.options) {{
                if (opt.value === value ||
                    opt.text.trim() === value ||
                    opt.text.trim().startsWith(value)) {{
                    sel.value = opt.value;
                    sel.dispatchEvent(new Event('change', {{bubbles:true}}));
                    return true;
                }}
            }}
            return false;
        }}

        function byPlaceholder(ph) {{
            return [...document.querySelectorAll('input')].find(i =>
                i.placeholder?.toLowerCase().includes(ph.toLowerCase())
            );
        }}

        function byLabel(txt) {{
            const lbl = [...document.querySelectorAll('label')].find(
                l => l.innerText?.includes(txt)
            );
            if (!lbl) return null;
            const id = lbl.getAttribute('for');
            return id ? document.getElementById(id) : lbl.querySelector('input');
        }}

        function findSelectByOptions(...keywords) {{
            return [...document.querySelectorAll('select')].find(s =>
                [...s.options].some(o =>
                    keywords.some(k => o.text.toLowerCase().includes(k.toLowerCase()))
                )
            );
        }}

        // Espera a que una función retorne truthy, con retry cada `ms`
        function waitFor(fn, ms, maxMs) {{
            return new Promise((resolve, reject) => {{
                const check = () => {{
                    const r = fn();
                    if (r) {{ resolve(r); return; }}
                    if (elapsed() > maxMs) {{ reject('timeout'); return; }}
                    setTimeout(check, ms);
                }};
                check();
            }});
        }}

        // ── Buscar campo número de tarjeta ────────────────────────────────────
        function findNumberInput() {{
            return (
                document.querySelector('input[data-card-field="number"]') ||
                document.querySelector('input[autocomplete="cc-number"]') ||
                byPlaceholder('tarjeta') ||
                byLabel('Número de tarjeta') ||
                byLabel('Número') ||
                (() => {{
                    const lbl = [...document.querySelectorAll('label,span')].find(
                        e => e.innerText?.trim().includes('Número de tarjeta')
                    );
                    return lbl?.closest('div')?.querySelector('input');
                }})()
            );
        }}

        // ── Buscar botón Finalizar (ignorando botones de error) ───────────────
        function findFinBtn() {{
            const candidates = [...document.querySelectorAll('button')].filter(b => {{
                const txt = b.textContent?.trim() || '';
                if (b.disabled) return false;
                if (txt.includes('sin el item') ||
                    txt.includes('sin los item')) return false;
                return (
                    txt === 'Guardar las modificaciones' ||
                    txt === 'Finalizar compra' ||
                    txt === 'Finalizar la compra' ||
                    txt.toLowerCase().startsWith('finalizar') ||
                    b.id === 'payment-data-submit'
                );
            }});
            return candidates[0] || null;
        }}

        // ── PURGA ANTI-DESCUENTO ──────────────────────────────────────────
        async function purgaAntiDescuento() {{
            console.log('[CARD] Purga anti-descuento...');
            try {{
                const r0 = await fetch('/api/checkout/pub/orderForm', {{
                    credentials: 'include',
                    headers: {{'Accept': 'application/json', 'Cache-Control': 'no-cache'}}
                }});
                const d0 = await r0.json();
                const id = d0.orderFormId;
                if (!id) {{ console.log('[CARD] WARN: sin orderFormId'); return -1; }}

                const totalAntes = d0.value || 0;
                console.log('[CARD] Total antes: $' + (totalAntes/100) + ' t=' + elapsed() + 'ms');

                // Capa 1: limpiar cupones
                await fetch('/api/checkout/pub/orderForm/' + id + '/coupons', {{
                    method: 'POST', credentials: 'include',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{text: ''}})
                }}).catch(() => {{}});

                // Capa 2: limpiar marketingData (UTMs, tags)
                await fetch('/api/checkout/pub/orderForm/' + id + '/attachments/marketingData', {{
                    method: 'POST', credentials: 'include',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        attachmentId: 'marketingData',
                        utmSource: null, utmMedium: null, utmCampaign: null,
                        utmiPage: null, utmiPart: null, utmiCampaign: null,
                        coupon: null, marketingTags: []
                    }})
                }}).catch(() => {{}});

                // Capa 3: limpiar mensajes/alertas
                await fetch('/api/checkout/pub/orderForm/' + id + '/messages/clear', {{
                    method: 'POST', credentials: 'include',
                    headers: {{'Content-Type': 'application/json'}}
                }}).catch(() => {{}});

                // Verificar resultado
                const r1 = await fetch('/api/checkout/pub/orderForm', {{
                    credentials: 'include',
                    headers: {{'Accept': 'application/json', 'Cache-Control': 'no-cache'}}
                }});
                const d1 = await r1.json();
                const totalFinal = d1.value || 0;
                console.log('[CARD] Total post-purga: $' + (totalFinal/100) + ' t=' + elapsed() + 'ms');
                return totalFinal;
            }} catch(e) {{
                console.log('[CARD] WARN: purga error: ' + e);
                return -1;
            }}
        }}

        // ── FLUJO PRINCIPAL ───────────────────────────────────────────────────
        async function run() {{
            console.log('[CARD] Iniciando flujo tarjeta ' + TIPO + ' t=0ms');

            // 0. Purga anti-descuento ANTES de tocar el formulario
            const totalPurga = await purgaAntiDescuento();
            if (totalPurga === 0) {{
                console.log('CARD_CLICK_ERROR');
                console.log('[CARD] Total $0 — cuenta marcada por Nike. Abortando.');
                return;
            }}

            // 1. Esperar formulario
            let inputNum;
            try {{
                inputNum = await waitFor(findNumberInput, 200, MAX_MS);
                console.log('[CARD] Formulario detectado t=' + elapsed() + 'ms');
            }} catch(e) {{
                console.log('[CARD] ERROR: Formulario no apareció en ' + MAX_MS + 'ms');
                return;
            }}

            // 2. Número de tarjeta
            fill(inputNum, NUMERO);
            console.log('[CARD] Número llenado t=' + elapsed() + 'ms');

            // 3. CVV (esperar que aparezca)
            try {{
                const inputCVV = await waitFor(() =>
                    document.querySelector('input[data-card-field="cvv"]') ||
                    document.querySelector('input[autocomplete="cc-csc"]') ||
                    byPlaceholder('seguridad') ||
                    byLabel('Código seguridad') ||
                    byLabel('CVV'),
                200, 5000);
                fill(inputCVV, CVV);
                console.log('[CARD] CVV llenado t=' + elapsed() + 'ms');
            }} catch(e) {{
                console.log('[CARD] WARN: CVV no encontrado, continuando...');
            }}

            // 4. Vencimiento MM/AA — esperar que los selects carguen opciones reales
            try {{
                const selMM = await waitFor(
                    () => findSelectByOptions('MM', '01', '1'),
                    200, 8000
                );
                fillSelect(selMM, MM);
                console.log('[CARD] MM=' + MM + ' t=' + elapsed() + 'ms');

                const selAA = await waitFor(
                    () => findSelectByOptions('AA', '25', '26', '27', '28'),
                    200, 4000
                );
                fillSelect(selAA, AA);
                console.log('[CARD] AA=' + AA + ' t=' + elapsed() + 'ms');
            }} catch(e) {{
                console.log('[CARD] WARN: Selects vencimiento no encontrados: ' + e);
            }}

            // 5. Nombre en tarjeta
            try {{
                const inputNombre = await waitFor(() =>
                    document.querySelector('input[data-card-field="name"]') ||
                    document.querySelector('input[autocomplete="cc-name"]') ||
                    byLabel('Nombre y apellido') ||
                    byLabel('Nombre') ||
                    byPlaceholder('nombre'),
                200, 4000);
                fill(inputNombre, NOMBRE);
                console.log('[CARD] Nombre llenado t=' + elapsed() + 'ms');
            }} catch(e) {{
                console.log('[CARD] WARN: Nombre no encontrado');
            }}

            // 6. Cuotas — CRÍTICO: esperar DESPUÉS de que Nike valide el número
            try {{
                const selCuotas = await waitFor(
                    () => findSelectByOptions('Total', 'cuota', 'Pago total'),
                    300, 10000
                );
                selCuotas.selectedIndex = 0;
                selCuotas.dispatchEvent(new Event('change', {{bubbles:true}}));
                console.log('[CARD] Cuotas: "' + selCuotas.options[0].text + '" t=' + elapsed() + 'ms');
            }} catch(e) {{
                console.log('[CARD] WARN: Select cuotas no apareció en 10s: ' + e);
            }}

            // 7. RUT del pagador
            try {{
                const inputRut = await waitFor(() =>
                    byLabel('RUT del pagador') ||
                    byLabel('RUT') ||
                    byPlaceholder('RUT') ||
                    byPlaceholder('rut'),
                200, 4000);
                fill(inputRut, RUT);
                console.log('[CARD] RUT llenado t=' + elapsed() + 'ms');
            }} catch(e) {{
                console.log('[CARD] WARN: RUT no encontrado');
            }}

            // 8. Checkbox dirección de facturación (si existe)
            const checkbox = [...document.querySelectorAll('input[type="checkbox"]')]
                .find(cb => {{
                    const lbl = cb.closest('label') ||
                        document.querySelector('label[for="' + cb.id + '"]');
                    return lbl?.innerText?.toLowerCase().includes('factur');
                }});
            if (checkbox && !checkbox.checked) {{
                checkbox.click();
                console.log('[CARD] Checkbox facturación marcado');
            }}

            // 9. Verificar precio final ANTES del click
            try {{
                const rFinal = await fetch('/api/checkout/pub/orderForm', {{
                    credentials: 'include',
                    headers: {{'Accept': 'application/json', 'Cache-Control': 'no-cache'}}
                }});
                const dFinal = await rFinal.json();
                const precioFinal = dFinal.value || 0;
                console.log('[CARD] Precio pre-click: $' + (precioFinal/100) + ' t=' + elapsed() + 'ms');
                if (precioFinal < 1000) {{
                    console.log('CARD_CLICK_ERROR');
                    console.log('[CARD] Precio $' + (precioFinal/100) + ' — descuento persistente. Abortando.');
                    return;
                }}
            }} catch(e) {{
                console.log('[CARD] WARN: No se pudo verificar precio: ' + e);
            }}

            // 10. Esperar y clickear Finalizar — con retry si queda disabled
            console.log('[CARD] Buscando botón Finalizar...');
            let intentos = 0;
            while (elapsed() < MAX_MS) {{
                intentos++;
                const btn = findFinBtn();

                if (!btn) {{
                    if (intentos % 10 === 0)
                        console.log('[CARD] Esperando botón... t=' + elapsed() + 'ms');
                    await new Promise(r => setTimeout(r, 200));
                    continue;
                }}

                if (btn.disabled) {{
                    console.log('[CARD] Botón disabled, esperando t=' + elapsed() + 'ms');
                    await new Promise(r => setTimeout(r, 300));
                    continue;
                }}

                // Scroll al botón y click
                btn.scrollIntoView({{behavior: 'instant', block: 'center'}});
                await new Promise(r => setTimeout(r, 150));

                btn.dispatchEvent(new MouseEvent('mousedown', {{bubbles:true, cancelable:true}}));
                btn.dispatchEvent(new MouseEvent('mouseup',   {{bubbles:true, cancelable:true}}));
                btn.dispatchEvent(new MouseEvent('click',     {{bubbles:true, cancelable:true}}));
                btn.click();

                console.log('[CARD] Click "' + btn.textContent?.trim() + '" t=' + elapsed() + 'ms (intento ' + intentos + ')');

                // Esperar 2s — si el botón sigue habilitado y no navegó, reintentar
                await new Promise(r => setTimeout(r, 2000));

                // FAIL-FAST: detectar modal de rechazo de pago
                const bodyText = document.body.innerText.toLowerCase();
                if (bodyText.includes('pago ha sido rechazado') ||
                    bodyText.includes('informaci\u00f3n incorrecta') ||
                    bodyText.includes('saldo insuficiente') ||
                    bodyText.includes('transacci\u00f3n rechazada') ||
                    bodyText.includes('tarjeta fue rechazada') ||
                    bodyText.includes('no se pudo procesar') ||
                    document.querySelector('.vtex-modal__confirmation') ||
                    document.querySelector('[class*="error"][class*="payment"]')) {{

                    const errorMsg = bodyText.match(/(rechazad[oa]|insuficiente|incorrecta|no se pudo)[^.{{}}]{{0,80}}/i);
                    console.log('CARD_CLICK_ERROR');
                    console.log('[CARD] Pago rechazado: ' + (errorMsg ? errorMsg[0].trim() : 'modal detectado') + ' t=' + elapsed() + 'ms');
                    return;
                }}

                if (window.location.href.includes('orderPlaced')) {{
                    console.log('CARD_CLICK_OK');
                    console.log('[CARD] orderPlaced t=' + elapsed() + 'ms');
                    return;
                }}

                // Si Fintoc abrió → también es éxito
                const fintocVisible = [...document.querySelectorAll('iframe')].some(f =>
                    f.src?.includes('fintoc') &&
                    f.getBoundingClientRect().height > 100
                );
                if (fintocVisible) {{
                    console.log('CARD_CLICK_OK');
                    console.log('[CARD] Fintoc abierto t=' + elapsed() + 'ms');
                    return;
                }}

                // Si el botón sigue ahí y no navegó → el form puede tener error
                const btnStillThere = findFinBtn();
                if (btnStillThere && !btnStillThere.disabled) {{
                    console.log('[CARD] Botón aún visible, reintentando...');
                    continue;
                }}

                // Botón desapareció = procesando
                console.log('CARD_CLICK_OK');
                console.log('[CARD] Click procesado t=' + elapsed() + 'ms');
                return;
            }}

            console.log('[CARD] TIMEOUT — no se pudo completar en ' + MAX_MS + 'ms');
        }}

        run().catch(e => console.log('[CARD] ERROR FATAL: ' + e));
    }})();
    """


def parse_expiry(expiry_str: str) -> tuple[str, str]:
    """'12/27' → ('12', '27'). Acepta MM/AA o MM/AAAA."""
    if "/" not in expiry_str:
        return "", ""
    parts = expiry_str.split("/")
    return parts[0].strip().zfill(2), parts[1].strip()[-2:]
