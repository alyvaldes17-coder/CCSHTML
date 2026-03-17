#!/usr/bin/env python3
"""
pdp_seeder.py

PROPÓSITO: Preparar sesión "dorada" limpia visitando PDP real en Playwright.

RESPONSABILIDADES:
1. Abre Chromium persistente (perfil Nike con cookies válidas)
2. Navega a PDP de SKU específico
3. Espera a que VTEX runtime cargue completamente (vtexjs.checkout)
4. Extrae orderFormId CON FALLBACK si no existe aún
5. Filtra solo 5 cookies críticas (sin ruido)
6. Guarda en session_golden.json para que Worker use sin Playwright

SALIDA: auth/<account>/session_golden.json
{
  "orderFormId": "94cca206...",
  "userAgent": "Mozilla/5.0...",
  "cookies": {"vtex_session": "...", ...},
  "timestamp": 1735000000,
  "seeded_url": "https://www.nike.cl/..."
}

NOTA: Worker NO debe ejecutar esto. Solo ejecutar UNA VEZ por cuenta.
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime

from playwright.async_api import async_playwright, BrowserContext, Page


async def pdp_seeder(
    account_name: str,
    sku: str,
    base_url: str = "https://www.nike.cl",
    headless: bool = False,
):
    """
    Seeder principal: abre Playwright, navega PDP, extrae sesión golden.
    
    Args:
        account_name: nombre de la cuenta (e.g., "cuenta1")
        sku: SKU a navegar (e.g., "DZ4373-100")
        base_url: base URL de Nike (default: https://www.nike.cl)
        headless: ejecutar en headless (default: False para debug visual)
    
    Returns:
        dict con sesión golden o None si falló
    """
    
    print(f"\n🌱 PDP SEEDER para {account_name} (SKU={sku})")
    print(f"   Base URL: {base_url}")
    print(f"   Headless: {headless}")
    
    profile_path = Path(f"profile_pw")
    profile_path.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as playwright:
        print(f"   Lanzando Chromium persistente...")
        
        browser = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        
        # Extraer User-Agent del navegador (será sincronizado con Worker)
        user_agent = await browser.evaluate("() => navigator.userAgent")
        print(f"   User-Agent: {user_agent[:60]}...")
        
        # PASO 1: Navegar a PDP
        page = await browser.new_page()
        pdp_url = f"{base_url}/p/{sku}"
        
        print(f"\n   📄 Navegando a PDP: {pdp_url}")
        await page.goto(pdp_url, wait_until="domcontentloaded")
        print(f"   ✅ PDP cargado")
        
        # Guardar la URL del PDP ORIGINAL (no la de checkout después)
        original_pdp_url = pdp_url
        
        # PASO 2: Esperar a que VTEX runtime cargue completamente
        print(f"\n   ⏳ Esperando runtime VTEX...")
        try:
            await page.wait_for_function(
                "() => window.vtexjs && vtexjs.checkout",
                timeout=15000
            )
            print(f"   ✅ window.vtexjs.checkout detectado")
        except Exception as e:
            print(f"   ⚠️  Timeout esperando vtexjs: {e}")
            print(f"   Continuando (puede estar en error)")
        
        # PASO 3: Extraer orderFormId CON FALLBACK
        print(f"\n   🔑 Extrayendo orderFormId...")
        
        order_form_id = await page.evaluate("""() => {
            try {
                const id = window.vtexjs?.checkout?.orderFormId || null;
                return id;
            } catch(e) {
                return null;
            }
        }""")
        
        if order_form_id:
            print(f"   ✅ orderFormId encontrado: {order_form_id}")
        else:
            print(f"   ⚠️  orderFormId no existe aún (fallback)")
            print(f"   Navegando a /checkout para forzar creación...")
            
            checkout_url = f"{base_url}/checkout"
            await page.goto(checkout_url, wait_until="domcontentloaded")
            print(f"   ✅ Checkout cargado")
            
            # Esperar nuevamente
            try:
                await page.wait_for_function(
                    "() => window.vtexjs && vtexjs.checkout && vtexjs.checkout.orderFormId",
                    timeout=10000
                )
                order_form_id = await page.evaluate("() => window.vtexjs.checkout.orderFormId")
                print(f"   ✅ orderFormId creado por fallback: {order_form_id}")
            except Exception as e:
                print(f"   ❌ No se pudo obtener orderFormId: {e}")
                order_form_id = None
        
        if not order_form_id:
            print(f"   ⛔ FATAL: orderFormId sigue siendo None")
            await browser.close()
            return None
        
        # PASO 4: Extraer cookies RELEVANTES (sin ruido)
        print(f"\n   🍪 Extrayendo cookies (filtrado quirúrgico)...")
        
        CRITICAL_COOKIES = (
            "vtex_session",
            "vtex_segment",
            "checkout",
            "VtexIdclientAutCookie",
            "VtexIdclientAutCookie_nikeclprod",
        )
        
        all_cookies = await browser.cookies()
        
        # Filtrar solo las cookies críticas
        golden_cookies = {}
        for cookie in all_cookies:
            cookie_name = cookie.get("name", "")
            # Buscar si alguna clave crítica está en el nombre (case-insensitive)
            for critical in CRITICAL_COOKIES:
                if critical.lower() in cookie_name.lower():
                    golden_cookies[cookie_name] = cookie.get("value", "")
                    print(f"      ✅ {cookie_name}")
                    break
        
        print(f"   ✅ Total cookies filtradas: {len(golden_cookies)}")
        
        # PASO 5: Construir sesión golden
        timestamp = int(time.time())
        # Usar la URL del PDP ORIGINAL (no la del checkout si navegamos allá)
        
        golden_session = {
            "orderFormId": order_form_id,
            "userAgent": user_agent,
            "cookies": golden_cookies,
            "timestamp": timestamp,
            "seeded_url": original_pdp_url,  # Usar URL original del PDP
        }
        
        # PASO 6: Guardar en auth/<account>/session_golden.json
        account_path = Path(f"auth/{account_name}")
        account_path.mkdir(parents=True, exist_ok=True)
        
        golden_path = account_path / "session_golden.json"
        
        with open(golden_path, "w", encoding="utf-8") as f:
            json.dump(golden_session, f, indent=2, ensure_ascii=False)
        
        print(f"\n   ✅ Sesión dorada guardada: {golden_path}")
        print(f"   📋 orderFormId: {order_form_id}")
        print(f"   🍪 cookies: {len(golden_cookies)} items")
        print(f"   ⏰ timestamp: {datetime.fromtimestamp(timestamp)}")
        
        await browser.close()
        return golden_session


async def batch_seed(accounts: list[dict], base_url: str = "https://www.nike.cl", headless: bool = False):
    """
    Seed múltiples cuentas secuencialmente.
    
    Args:
        accounts: lista de dicts con {"name": "cuenta1", "sku": "DZ4373-100"}
        base_url: base URL
        headless: modo headless
    """
    
    print(f"\n🌱🌱🌱 SEEDING BATCH ({len(accounts)} cuentas)")
    results = {}
    
    for acc in accounts:
        acc_name = acc.get("name")
        sku = acc.get("sku")
        
        if not acc_name or not sku:
            print(f"   ⚠️  Cuenta incompleta: {acc}")
            continue
        
        print(f"\n{'='*60}")
        try:
            result = await pdp_seeder(acc_name, sku, base_url, headless)
            results[acc_name] = {
                "status": "OK" if result else "FAILED",
                "orderFormId": result.get("orderFormId") if result else None,
            }
        except Exception as e:
            print(f"   ❌ Error en {acc_name}: {e}")
            results[acc_name] = {"status": "ERROR", "error": str(e)}
    
    print(f"\n{'='*60}")
    print(f"🌱 RESUMEN:")
    for acc_name, status_dict in results.items():
        status = status_dict.get("status")
        icon = "✅" if status == "OK" else "❌"
        print(f"   {icon} {acc_name}: {status}")
    
    return results


if __name__ == "__main__":
    import sys
    
    # Uso simple:
    # python pdp_seeder.py cuenta1 DZ4373-100
    # python pdp_seeder.py --batch accounts.json
    
    if len(sys.argv) > 2:
        # Modo individual
        acc_name = sys.argv[1]
        sku = sys.argv[2]
        
        result = asyncio.run(pdp_seeder(acc_name, sku, headless=False))
        sys.exit(0 if result else 1)
    
    elif "--batch" in sys.argv:
        # Modo batch desde JSON
        import json
        
        # Buscar archivo accounts.json o usar default
        accounts_file = "accounts.json"
        for arg in sys.argv[1:]:
            if arg.endswith(".json"):
                accounts_file = arg
                break
        
        accounts_path = Path(accounts_file)
        if not accounts_path.exists():
            print(f"❌ Archivo no encontrado: {accounts_file}")
            print(f"\nUso: python pdp_seeder.py --batch accounts.json")
            print(f"O individual: python pdp_seeder.py cuenta1 DZ4373-100")
            sys.exit(1)
        
        with open(accounts_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        accounts = config.get("accounts", [])
        base_url = config.get("base_url", "https://www.nike.cl")
        
        results = asyncio.run(batch_seed(accounts, base_url, headless=False))
        
        # Guardar resultados
        results_file = Path("seeding_results.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📊 Resultados guardados: {results_file}")
        sys.exit(0)
    
    else:
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║              PDP SEEDER - Preparar sesión dorada              ║
╚══════════════════════════════════════════════════════════════╝

PROPÓSITO:
  Abre Playwright, navega PDP, extrae sesión limpia para Worker.

USO INDIVIDUAL:
  python pdp_seeder.py <cuenta> <sku>
  
  Ejemplo:
    python pdp_seeder.py cuenta1 DZ4373-100
    python pdp_seeder.py cuenta2 FZ4373-200

USO BATCH (múltiples cuentas):
  python pdp_seeder.py --batch accounts.json
  
  Formato accounts.json:
  {{
    "base_url": "https://www.nike.cl",
    "accounts": [
      {{"name": "cuenta1", "sku": "DZ4373-100"}},
      {{"name": "cuenta2", "sku": "FZ4373-200"}}
    ]
  }}

SALIDA:
  auth/<cuenta>/session_golden.json
  
  Contiene:
    - orderFormId (carrito legítimo)
    - userAgent (sincronizado con Worker)
    - cookies (solo 5 críticas, filtrado)
    - timestamp
    - seeded_url

NOTA:
  ⚠️  Ejecutar ANTES de arrancar Worker
  ⚠️  Una sola vez por cuenta (reutilizable múltiples drops)
  ⚠️  Worker valida que exista session_golden.json
""")
        sys.exit(0)
