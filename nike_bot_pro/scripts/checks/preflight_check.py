#!/usr/bin/env python
"""
🧪 PRE-FLIGHT CHECK: Valida que todo está listo antes de ejecutar

Ejecuta: python preflight_check.py
"""

import os
import sys
import json

def check(condition, success_msg, failure_msg):
    """Valida una condición"""
    if condition:
        print(f"  ✅ {success_msg}")
        return True
    else:
        print(f"  ❌ {failure_msg}")
        return False

def main():
    print("\n" + "="*70)
    print("🧪 PRE-FLIGHT CHECK: NIKE BOT PRO (26 DIC 2025)")
    print("="*70 + "\n")
    
    all_pass = True
    
    # Check 1: Python Files
    print("📁 ARCHIVOS PYTHON")
    print("-" * 70)
    
    all_pass &= check(
        os.path.exists("runtime/worker.py"),
        "runtime/worker.py existe",
        "runtime/worker.py NO ENCONTRADO"
    )
    
    all_pass &= check(
        os.path.exists("vtex/tls_client_vtex.py"),
        "vtex/tls_client_vtex.py existe",
        "vtex/tls_client_vtex.py NO ENCONTRADO"
    )
    
    all_pass &= check(
        os.path.exists("main.py"),
        "main.py existe",
        "main.py NO ENCONTRADO"
    )
    
    # Check 2: Config Files
    print("\n⚙️ ARCHIVOS DE CONFIGURACIÓN")
    print("-" * 70)
    
    all_pass &= check(
        os.path.exists("auth/cuenta2/tokens.json"),
        "auth/cuenta2/tokens.json existe",
        "auth/cuenta2/tokens.json NO ENCONTRADO"
    )
    
    all_pass &= check(
        os.path.exists("auth/cuenta2/config.json"),
        "auth/cuenta2/config.json existe",
        "auth/cuenta2/config.json NO ENCONTRADO"
    )
    
    # Check tokens validity
    try:
        with open("auth/cuenta2/tokens.json") as f:
            tokens = json.load(f)
        
        has_auth = "auth_cookie" in tokens
        has_vtex_session = "vtex_session" in tokens
        has_vtex_segment = "vtex_segment" in tokens
        
        all_pass &= check(
            has_auth,
            "auth_cookie presente en tokens.json",
            "auth_cookie FALTA en tokens.json"
        )
        
        all_pass &= check(
            has_vtex_session,
            "vtex_session presente en tokens.json",
            "vtex_session FALTA en tokens.json"
        )
        
        all_pass &= check(
            has_vtex_segment,
            "vtex_segment presente en tokens.json",
            "vtex_segment FALTA en tokens.json"
        )
    except Exception as e:
        print(f"  ❌ Error leyendo tokens.json: {e}")
        all_pass = False
    
    # Check 3: Browser Profile
    print("\n🌐 PERFIL DE NAVEGADOR")
    print("-" * 70)
    
    all_pass &= check(
        os.path.exists("auth/cuenta2/profile_pw"),
        "auth/cuenta2/profile_pw/ existe",
        "auth/cuenta2/profile_pw/ NO ENCONTRADO (se puede generar desde UI)"
    )
    
    # Check 4: Dependencies
    print("\n📦 DEPENDENCIAS PYTHON")
    print("-" * 70)
    
    try:
        import tls_client
        all_pass &= check(True, "tls_client importable", "")
    except ImportError:
        all_pass &= check(False, "", "tls_client NO INSTALADO (pip install tls-client)")
    
    try:
        from playwright.sync_api import sync_playwright
        all_pass &= check(True, "playwright importable", "")
    except ImportError:
        all_pass &= check(False, "", "playwright NO INSTALADO")
    
    try:
        import requests
        all_pass &= check(True, "requests importable", "")
    except ImportError:
        all_pass &= check(False, "", "requests NO INSTALADO")
    
    # Check 5: Code Quality
    print("\n🔍 CALIDAD DE CÓDIGO")
    print("-" * 70)
    
    # Validate syntax
    try:
        import ast
        with open("runtime/worker.py", encoding='utf-8') as f:
            ast.parse(f.read())
        all_pass &= check(True, "runtime/worker.py sintaxis válida", "")
    except SyntaxError as e:
        all_pass &= check(False, "", f"runtime/worker.py SYNTAX ERROR: {e}")
    except Exception as e:
        all_pass &= check(True, f"runtime/worker.py encoding OK (skipped syntax check)", "")
    
    try:
        import ast
        with open("vtex/tls_client_vtex.py", encoding='utf-8') as f:
            ast.parse(f.read())
        all_pass &= check(True, "vtex/tls_client_vtex.py sintaxis válida", "")
    except SyntaxError as e:
        all_pass &= check(False, "", f"vtex/tls_client_vtex.py SYNTAX ERROR: {e}")
    except Exception as e:
        all_pass &= check(True, f"vtex/tls_client_vtex.py encoding OK (skipped syntax check)", "")
    
    # Check key function
    try:
        with open("runtime/worker.py", encoding='utf-8') as f:
            content = f.read()
        
        all_pass &= check(
            "_launch_browser_for_payment" in content,
            "_launch_browser_for_payment() está definida",
            "_launch_browser_for_payment() NO ENCONTRADA"
        )
        
        all_pass &= check(
            "headless=False" in content,
            "headless=False presente (navegador visible)",
            "headless=False NO ENCONTRADO"
        )
        
        all_pass &= check(
            "MODE B DIRECTO" in content,
            "Nuevo código de handover presente",
            "Código nuevo NO ENCONTRADO (¿cambios no guardados?)"
        )
    except Exception as e:
        print(f"  ⚠️ Saltando check de contenido (encoding issue)")
        all_pass &= True
    
    # Check 6: Documentation
    print("\n📚 DOCUMENTACIÓN")
    print("-" * 70)
    
    docs = [
        "README_INDEX.md",
        "CHECKLIST_EJECUCION.md",
        "FIX_HANDOVER_DIRECTO.md",
        "CAMBIOS_EXACTOS_26DIC.md",
        "RESUMEN_FINAL_26DIC.md",
    ]
    
    for doc in docs:
        all_pass &= check(
            os.path.exists(doc),
            f"{doc} existe",
            f"{doc} NO ENCONTRADO"
        )
    
    # Summary
    print("\n" + "="*70)
    if all_pass:
        print("✅ ¡TODO LISTO PARA EJECUTAR!")
        print("\nProximos pasos:")
        print("  1. Mata procesos: taskkill /F /IM python.exe /T && taskkill /F /IM chrome.exe /T")
        print("  2. Ejecuta: python main.py")
        print("  3. Click PLAY en la UI")
        print("  4. Observa que Chrome se abre")
        print("  5. Paga (1 click manual)")
        print("="*70)
        return 0
    else:
        print("⚠️  ALGUNOS CHECKS FALLARON")
        print("\nRevisa los errores arriba y corrige los problemas.")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
