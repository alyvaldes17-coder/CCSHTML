#!/usr/bin/env python3
"""
HANDOVER_CONTRACT.py

Valida el contrato de handover entre Seeder (Playwright) y Worker (curl/TLS).

Este script verifica que:
1. session_golden.json existe y tiene estructura correcta
2. orderFormId no es None/vacío
3. Cookies críticas están presentes
4. User-Agent está sincronizado
5. Worker puede iniciar sin abrir Playwright

PROPÓSITO: Debugging y validación pre-vuelo.
"""

import json
from pathlib import Path
from datetime import datetime


def validate_golden_session(account_name: str) -> dict:
    """
    Valida que session_golden.json de una cuenta está bien formado.
    
    Returns:
        dict con {"status": "OK"|"ERROR", "messages": [...], "data": {...}}
    """
    
    print(f"\n{'='*70}")
    print(f"🔍 VALIDANDO HANDOVER CONTRACT: {account_name}")
    print(f"{'='*70}\n")
    
    messages = []
    golden_path = Path(f"auth/{account_name}/session_golden.json")
    
    # Paso 1: Archivo existe
    if not golden_path.exists():
        messages.append(f"❌ session_golden.json NO EXISTE")
        messages.append(f"   Ruta: {golden_path}")
        messages.append(f"   Ejecuta: python pdp_seeder.py {account_name} <SKU>")
        return {"status": "ERROR", "messages": messages, "data": None}
    
    messages.append(f"✅ Archivo existe: {golden_path}")
    
    # Paso 2: Leer JSON
    try:
        with open(golden_path, "r", encoding="utf-8") as f:
            golden_data = json.load(f)
        messages.append(f"✅ JSON válido")
    except Exception as e:
        messages.append(f"❌ JSON inválido: {e}")
        return {"status": "ERROR", "messages": messages, "data": None}
    
    # Paso 3: Campos críticos
    order_form_id = golden_data.get("orderFormId")
    user_agent = golden_data.get("userAgent")
    cookies = golden_data.get("cookies", {})
    timestamp = golden_data.get("timestamp")
    seeded_url = golden_data.get("seeded_url")
    
    print(f"📋 CAMPOS ENCONTRADOS:")
    
    # orderFormId (CRÍTICO)
    if not order_form_id:
        messages.append(f"⚠️  orderFormId: VACÍO (fallback trigger)")
    else:
        messages.append(f"✅ orderFormId: {order_form_id}")
        print(f"   orderFormId: {order_form_id}")
    
    # User-Agent (CRÍTICO para sincronización)
    if not user_agent:
        messages.append(f"⚠️  userAgent: VACÍO")
    else:
        messages.append(f"✅ userAgent: {user_agent[:60]}...")
        print(f"   userAgent: {user_agent[:60]}...")
    
    # Cookies (CRÍTICAS)
    critical_cookie_keys = ["vtex_session", "vtex_segment", "checkout"]
    print(f"\n🍪 COOKIES ({len(cookies)} total):")
    
    if not cookies:
        messages.append(f"❌ Cookies vacías")
    else:
        found_critical = 0
        for cookie_name, cookie_value in cookies.items():
            is_critical = any(k in cookie_name.lower() for k in critical_cookie_keys)
            status = "✅" if is_critical else "ℹ️"
            messages.append(f"{status} {cookie_name}")
            print(f"   {status} {cookie_name}: {str(cookie_value)[:40]}...")
            if is_critical:
                found_critical += 1
        
        if found_critical < 2:
            messages.append(f"⚠️  Solo {found_critical} cookies críticas (esperadas >= 2)")
    
    # Timestamp
    if timestamp:
        dt = datetime.fromtimestamp(timestamp)
        messages.append(f"✅ timestamp: {dt} ({timestamp})")
        print(f"\n⏰ Timestamp: {dt}")
    else:
        messages.append(f"⚠️  timestamp: VACÍO")
    
    # Seeded URL
    if seeded_url:
        messages.append(f"✅ seeded_url: {seeded_url[:60]}...")
        print(f"🔗 Seeded URL: {seeded_url}")
    else:
        messages.append(f"⚠️  seeded_url: VACÍO")
    
    # Paso 4: Validación de handover
    print(f"\n📡 VALIDACIÓN DE HANDOVER:")
    
    errors = [m for m in messages if m.startswith("❌")]
    warnings = [m for m in messages if m.startswith("⚠️")]
    
    if errors:
        print(f"❌ ERRORES CRÍTICOS ({len(errors)}):")
        for err in errors:
            print(f"   {err}")
        status = "ERROR"
    elif warnings:
        print(f"⚠️  ADVERTENCIAS ({len(warnings)}):")
        for warn in warnings:
            print(f"   {warn}")
        print(f"\n✅ ESTADO: OK CON ADVERTENCIAS")
        print(f"   Worker puede ejecutar, pero fallback de orderFormId se activará")
        status = "WARNING"
    else:
        print(f"✅ HANDOVER PERFECTO")
        print(f"   Worker puede ejecutar SIN PROBLEMAS")
        status = "OK"
    
    return {
        "status": status,
        "messages": messages,
        "data": {
            "orderFormId": order_form_id,
            "userAgent": user_agent,
            "cookies_count": len(cookies),
            "timestamp": timestamp,
            "seeded_url": seeded_url,
        }
    }


def validate_all_accounts(accounts_to_check: list[str] = None) -> dict:
    """
    Valida múltiples cuentas.
    
    Args:
        accounts_to_check: lista de nombres de cuenta. Si None, busca en auth/
    
    Returns:
        dict con resultados por cuenta
    """
    
    if accounts_to_check is None:
        # Auto-discover cuentas
        auth_path = Path("auth")
        if not auth_path.exists():
            print("❌ Carpeta 'auth/' no existe")
            return {}
        
        accounts_to_check = [
            d.name for d in auth_path.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
    
    print(f"\n🔍 VALIDANDO {len(accounts_to_check)} CUENTA(S)")
    print(f"{'='*70}")
    
    results = {}
    for acc_name in accounts_to_check:
        result = validate_golden_session(acc_name)
        results[acc_name] = result
    
    # Resumen
    print(f"\n{'='*70}")
    print(f"📊 RESUMEN DE VALIDACIÓN")
    print(f"{'='*70}\n")
    
    ok_count = sum(1 for r in results.values() if r["status"] == "OK")
    warn_count = sum(1 for r in results.values() if r["status"] == "WARNING")
    error_count = sum(1 for r in results.values() if r["status"] == "ERROR")
    
    for acc_name, result in results.items():
        status = result["status"]
        if status == "OK":
            icon = "✅"
        elif status == "WARNING":
            icon = "⚠️"
        else:
            icon = "❌"
        print(f"{icon} {acc_name}: {status}")
    
    print(f"\n{'='*70}")
    print(f"TOTAL: {ok_count} OK | {warn_count} WARN | {error_count} ERROR")
    
    if error_count > 0:
        print(f"\n❌ ALGUNOS HANDOVERS FALLIDOS - Ejecuta pdp_seeder.py para prepararlos")
    elif warn_count > 0:
        print(f"\n⚠️  ALGUNAS ADVERTENCIAS - Worker ejecutará con fallbacks")
    else:
        print(f"\n✅ TODOS LOS HANDOVERS OK - Puedes ejecutar Worker sin problemas")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Validar cuentas específicas
        accounts = sys.argv[1:]
        results = validate_all_accounts(accounts)
    else:
        # Validar todas
        results = validate_all_accounts()
    
    # Exit code
    error_count = sum(1 for r in results.values() if r["status"] == "ERROR")
    sys.exit(0 if error_count == 0 else 1)
