"""
engines/limpiar_rastro.py — v1.0

DOS funciones independientes que puedes llamar desde bot_controller.py:

1. js_limpiar_descuentos()
   - Limpia cupones, marketingData, UTMs, ratesAndBenefits
   - Usa API VTEX + vtexjs nativo
   - Retorna el total final en CLP

2. js_limpiar_rastro()
   - Borra localStorage/sessionStorage keys de tracking Nike
   - Randomiza fingerprint canvas/WebGL
   - Limpia historial de comportamiento bot
   - NO cierra sesión — cookies intactas

3. js_verificar_total()
   - Verifica el total actual del carrito
"""


def js_limpiar_descuentos() -> str:
    """
    JS nuclear para eliminar CUALQUIER descuento/cupón del orderForm.

    Capas:
    1. API coupons con text vacío
    2. API marketingData con todo null (limpia UTMs y promo tracking)
    3. vtexjs.checkout.removeDiscount() — método nativo VTEX
    4. Limpiar messages del orderForm
    5. Verificación final del total

    Retorna string: 'OK:<total_en_pesos>:<descuentos_restantes>' o 'ERROR:<mensaje>'
    """
    return """
    (() => {
        return new Promise((resolve) => {
            const BASE = 'https://www.nike.cl';

            // ── Paso 1: Obtener orderFormId ────────────────────────────
            fetch(BASE + '/api/checkout/pub/orderForm', {
                credentials: 'include',
                headers: {'Accept': 'application/json', 'Cache-Control': 'no-cache'}
            })
            .then(r => r.json())
            .then(async (data) => {
                const id = data.orderFormId;
                if (!id) { resolve('ERROR:NO_ORDERFORM'); return; }

                const totalAntes = data.value || 0;
                const descuentos = (data.ratesAndBenefitsData?.rateAndBenefitsIdentifiers || []).length;
                console.log('[BOT] Total antes: $' + totalAntes + ' | descuentos: ' + descuentos);

                // ── Paso 2: Limpiar cupón (text vacío) ────────────────
                try {
                    await fetch(BASE + '/api/checkout/pub/orderForm/' + id + '/coupons', {
                        method: 'POST',
                        credentials: 'include',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify({text: ''})
                    });
                    console.log('[BOT] Cupón limpiado');
                } catch(e) {
                    console.log('[BOT] Cupón: ' + e.message);
                }

                // ── Paso 3: Limpiar marketingData (UTMs + promo tracking) ─
                try {
                    await fetch(BASE + '/api/checkout/pub/orderForm/' + id + '/attachments/marketingData', {
                        method: 'POST',
                        credentials: 'include',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify({
                            attachmentId: 'marketingData',
                            utmSource:    null,
                            utmMedium:    null,
                            utmCampaign:  null,
                            utmiPage:     null,
                            utmiPart:     null,
                            utmiCampaign: null,
                            coupon:       null,
                            marketingTags: []
                        })
                    });
                    console.log('[BOT] marketingData limpiado');
                } catch(e) {
                    console.log('[BOT] marketingData: ' + e.message);
                }

                // ── Paso 4: vtexjs nativo removeDiscount ──────────────
                try {
                    if (window.vtexjs && window.vtexjs.checkout) {
                        await new Promise((res) => {
                            window.vtexjs.checkout.removeDiscount()
                                .done(() => { console.log('[BOT] vtexjs removeDiscount OK'); res(); })
                                .fail(() => { console.log('[BOT] vtexjs removeDiscount fail'); res(); });
                        });
                    } else {
                        console.log('[BOT] vtexjs no disponible — skip');
                    }
                } catch(e) {
                    console.log('[BOT] vtexjs: ' + e.message);
                }

                // ── Paso 5: Limpiar messages del orderForm ────────────
                try {
                    await fetch(BASE + '/api/checkout/pub/orderForm/' + id + '/messages/clear', {
                        method: 'POST',
                        credentials: 'include',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        body: '{}'
                    });
                    console.log('[BOT] Messages limpiados');
                } catch(e) {}

                // ── Paso 6: Verificar total final ─────────────────────
                const r2 = await fetch(BASE + '/api/checkout/pub/orderForm', {
                    credentials: 'include',
                    headers: {'Accept': 'application/json', 'Cache-Control': 'no-cache'}
                });
                const data2 = await r2.json();
                const totalFinal = data2.value || 0;
                const descFinal  = (data2.ratesAndBenefitsData?.rateAndBenefitsIdentifiers || []).length;

                console.log('[BOT] Total final: $' + totalFinal + ' | descuentos restantes: ' + descFinal);
                resolve('OK:' + totalFinal + ':' + descFinal);
            })
            .catch(e => resolve('ERROR:' + e.message));
        });
    })();
    """


def js_limpiar_rastro() -> str:
    """
    JS para limpiar rastro de comportamiento bot en el browser.

    Limpia:
    - localStorage keys de Nike/VTEX tracking
    - sessionStorage completo
    - Fingerprint canvas (randomiza pixel)
    - Performance entries (timing fingerprint)
    - Cookies de tracking (GA, FB, Hotjar, etc.)
    - IndexedDB de VTEX

    NO toca: cookies de sesión, datos de cuenta Nike
    """
    return """
    (() => {
        let limpiado = 0;

        // ── 1. localStorage — keys de tracking Nike/VTEX ─────────────
        const keysEliminar = [];
        for (let i = 0; i < localStorage.length; i++) {
            const k = localStorage.key(i);
            if (!k) continue;
            const kl = k.toLowerCase();
            if (
                kl.includes('vtex')      ||
                kl.includes('checkout')  ||
                kl.includes('analytics') ||
                kl.includes('track')     ||
                kl.includes('fingerp')   ||
                kl.includes('session')   ||
                kl.includes('behavior')  ||
                kl.includes('bot')       ||
                kl.includes('pixel')     ||
                kl.includes('segment')   ||
                kl.includes('amplitude') ||
                kl.includes('hotjar')    ||
                kl.includes('gtm')       ||
                kl.includes('ga_')       ||
                kl.includes('_ga')       ||
                kl.includes('_gid')      ||
                kl.includes('heap')
            ) {
                keysEliminar.push(k);
            }
        }
        keysEliminar.forEach(k => { localStorage.removeItem(k); limpiado++; });
        console.log('[BOT] localStorage: ' + limpiado + ' keys eliminadas');

        // ── 2. sessionStorage completo ────────────────────────────────
        const sCount = sessionStorage.length;
        sessionStorage.clear();
        console.log('[BOT] sessionStorage: ' + sCount + ' keys eliminadas');

        // ── 3. Randomizar canvas fingerprint ──────────────────────────
        try {
            const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                const ctx = this.getContext('2d');
                if (ctx) {
                    const imageData = ctx.getImageData(0, 0, this.width || 1, this.height || 1);
                    imageData.data[0] = (imageData.data[0] + Math.floor(Math.random() * 3)) % 256;
                    ctx.putImageData(imageData, 0, 0);
                }
                return origToDataURL.apply(this, arguments);
            };
            console.log('[BOT] Canvas fingerprint randomizado');
        } catch(e) {
            console.log('[BOT] Canvas: ' + e.message);
        }

        // ── 4. Limpiar performance entries (timing fingerprint) ───────
        try {
            if (performance && performance.clearResourceTimings) {
                performance.clearResourceTimings();
                performance.clearMarks && performance.clearMarks();
                performance.clearMeasures && performance.clearMeasures();
                console.log('[BOT] Performance timings limpiados');
            }
        } catch(e) {}

        // ── 5. Limpiar cookies de tracking (NO de sesión Nike) ────────
        let cookiesLimpiadas = 0;
        document.cookie.split(';').forEach(c => {
            const name = c.trim().split('=')[0];
            if (!name) return;
            const nl = name.toLowerCase();
            if (
                nl.startsWith('_ga')    ||
                nl.startsWith('_gid')   ||
                nl.startsWith('_fbp')   ||
                nl.startsWith('_fbc')   ||
                nl.includes('hotjar')   ||
                nl.includes('hj')       ||
                nl.includes('segment')  ||
                nl.includes('amplitude')
            ) {
                document.cookie = name + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';
                cookiesLimpiadas++;
            }
        });
        console.log('[BOT] Cookies tracking: ' + cookiesLimpiadas + ' eliminadas');

        // ── 6. Limpiar indexedDB de VTEX ──────────────────────────────
        try {
            if (window.indexedDB) {
                ['vtex_checkout', 'vtex_session', 'checkout'].forEach(dbName => {
                    try { indexedDB.deleteDatabase(dbName); } catch(e) {}
                });
                console.log('[BOT] IndexedDB limpiado');
            }
        } catch(e) {}

        console.log('[BOT] ✅ Rastro limpiado — sesión Nike intacta');
        return 'OK:' + limpiado;
    })();
    """


def js_verificar_total() -> str:
    """Verifica el total actual del carrito. Retorna 'TOTAL:<valor>:ITEMS:<n>:DESC:<nombres>'."""
    return """
    (() => {
        return new Promise((resolve) => {
            fetch('https://www.nike.cl/api/checkout/pub/orderForm', {
                credentials: 'include',
                headers: {'Accept': 'application/json', 'Cache-Control': 'no-cache'}
            })
            .then(r => r.json())
            .then(data => {
                const total      = data.value || 0;
                const items      = (data.items || []).length;
                const descuentos = (data.ratesAndBenefitsData?.rateAndBenefitsIdentifiers || []).map(d => d.name).join(',');
                resolve('TOTAL:' + total + ':ITEMS:' + items + ':DESC:' + descuentos);
            })
            .catch(e => resolve('ERROR:' + e.message));
        });
    })();
    """
