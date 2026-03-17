#!/usr/bin/env python3
"""
PRE_FLIGHT_CHECK.py

Valida que todos los archivos necesarios existen y están correctos.
Ejecuta ANTES de empezar el flujo de salida del estancamiento.

Uso:
  python PRE_FLIGHT_CHECK.py
"""

import subprocess
import sys
from pathlib import Path
import json


def check_files_exist():
    """Verifica que todos los archivos necesarios existen"""
    print("\n1️⃣  VERIFICANDO ARCHIVOS...")
    
    required_files = {
        # Scripts nuevos
        "pdp_seeder.py": "Seeder Playwright",
        "HANDOVER_CONTRACT.py": "Validador de contrato",
        "BOOTSTRAP_GOLDEN_SESSION.py": "Orquestador",
        
        # Documentación
        "SALIDA_RAPIDA_ORD002.md": "Guía rápida",
        "CHECKLIST_EJECUTABLE.md": "Checklist paso a paso",
        "TRES_AJUSTES_QUIRURGICOS.md": "Detalle técnico",
        "CAMBIOS_IMPLEMENTADOS_AUDITORIA.md": "Auditoría",
        "INDICE_COMPLETO.md": "Índice de documentación",
        "00_COMIENZA_AQUI.txt": "Punto de entrada visual",
        
        # Modificados
        "runtime/worker.py": "Worker (modificado)",
    }
    
    missing = []
    for filepath, description in required_files.items():
        if Path(filepath).exists():
            print(f"   ✅ {filepath:<45} ({description})")
        else:
            print(f"   ❌ {filepath:<45} ({description})")
            missing.append(filepath)
    
    return len(missing) == 0, missing


def check_python_modules():
    """Verifica que módulos Python necesarios están disponibles"""
    print("\n2️⃣  VERIFICANDO MÓDULOS PYTHON...")
    
    required_modules = {
        "playwright": "Para pdp_seeder.py",
        "asyncio": "Async runtime (stdlib)",
        "json": "JSON parsing (stdlib)",
        "pathlib": "Path operations (stdlib)",
    }
    
    missing = []
    for module_name, description in required_modules.items():
        try:
            __import__(module_name)
            print(f"   ✅ {module_name:<30} ({description})")
        except ImportError:
            print(f"   ❌ {module_name:<30} ({description})")
            missing.append(module_name)
    
    return len(missing) == 0, missing


def check_syntax(filepath):
    """Valida sintaxis Python de un archivo"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            compile(f.read(), filepath, "exec")
        return True
    except SyntaxError as e:
        print(f"      ❌ Sintaxis error en línea {e.lineno}: {e.msg}")
        return False


def check_modified_worker():
    """Verifica que los cambios en worker.py están presentes"""
    print("\n3️⃣  VERIFICANDO CAMBIOS EN runtime/worker.py...")
    
    required_strings = {
        "VALIDACIÓN PRE-VUELO": "Validación session_golden.json",
        "golden_session_path": "Carga de path",
        "fallback_needed": "Variable de fallback",
        "User-Agent sincronizado desde seeder": "Sincronización User-Agent",
    }
    
    try:
        with open("runtime/worker.py", "r", encoding="utf-8") as f:
            worker_content = f.read()
        
        missing = []
        for marker, description in required_strings.items():
            if marker in worker_content:
                print(f"   ✅ {description:<50} (encontrado)")
            else:
                print(f"   ❌ {description:<50} (NO ENCONTRADO)")
                missing.append(marker)
        
        return len(missing) == 0
    except Exception as e:
        print(f"   ❌ Error leyendo worker.py: {e}")
        return False


def check_syntax_of_python_files():
    """Valida sintaxis de los scripts nuevos"""
    print("\n4️⃣  VALIDANDO SINTAXIS PYTHON...")
    
    python_files = [
        "pdp_seeder.py",
        "HANDOVER_CONTRACT.py",
        "BOOTSTRAP_GOLDEN_SESSION.py",
    ]
    
    all_ok = True
    for filepath in python_files:
        if Path(filepath).exists():
            if check_syntax(filepath):
                print(f"   ✅ {filepath:<45} (sintaxis OK)")
            else:
                print(f"   ❌ {filepath:<45} (sintaxis ERROR)")
                all_ok = False
        else:
            print(f"   ⚠️  {filepath:<45} (archivo no existe)")
    
    return all_ok


def check_auth_structure():
    """Verifica estructura de carpeta auth/"""
    print("\n5️⃣  VERIFICANDO ESTRUCTURA DE CARPETAS...")
    
    auth_path = Path("auth")
    if not auth_path.exists():
        print(f"   ⚠️  Carpeta 'auth/' NO EXISTE (será creada por pdp_seeder.py)")
        return True  # No es error fatal
    
    accounts = [d for d in auth_path.iterdir() if d.is_dir() and not d.name.startswith(".")]
    
    if not accounts:
        print(f"   ⚠️  No hay cuentas en auth/ (esperando que pdp_seeder.py las cree)")
        return True  # No es error fatal
    
    print(f"   ℹ️  {len(accounts)} cuenta(s) encontrada(s) en auth/")
    for acc in accounts:
        golden_path = acc / "session_golden.json"
        if golden_path.exists():
            print(f"      ✅ {acc.name:<40} (session_golden.json existe)")
        else:
            print(f"      ⚠️  {acc.name:<40} (session_golden.json falta - pdp_seeder.py lo creará)")
    
    return True


def check_playwright_installed():
    """Verifica que Playwright está instalado y con navegadores"""
    print("\n6️⃣  VERIFICANDO PLAYWRIGHT...")
    
    try:
        import playwright
        print(f"   ✅ Playwright módulo instalado")
        
        # Intentar ver si Chromium está descargado
        # Esto es un best-effort check
        browsers_path = Path.home() / ".cache" / "ms-playwright"
        if browsers_path.exists():
            print(f"   ✅ Navegadores Playwright descargados")
            return True
        else:
            print(f"   ⚠️  Navegadores Playwright pueden necesitar descarga")
            print(f"      Ejecuta: playwright install")
            return True  # No es error fatal, se descargarán on-demand
    except ImportError:
        print(f"   ❌ Playwright NO INSTALADO")
        print(f"      Ejecuta: pip install playwright")
        return False


def main():
    """Ejecuta todos los checks"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRE-FLIGHT CHECKS                                   ║
║         Validando que todo está listo para salida de ORD002                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    results = {}
    
    # 1. Archivos
    files_ok, missing_files = check_files_exist()
    results["archivos"] = files_ok
    
    # 2. Módulos
    modules_ok, missing_modules = check_python_modules()
    results["modulos"] = modules_ok
    
    # 3. Worker.py cambios
    worker_ok = check_modified_worker()
    results["worker"] = worker_ok
    
    # 4. Sintaxis Python
    syntax_ok = check_syntax_of_python_files()
    results["sintaxis"] = syntax_ok
    
    # 5. Estructura auth/
    auth_ok = check_auth_structure()
    results["auth"] = auth_ok
    
    # 6. Playwright
    playwright_ok = check_playwright_installed()
    results["playwright"] = playwright_ok
    
    # RESUMEN
    print(f"\n{'='*80}")
    print(f"📊 RESUMEN")
    print(f"{'='*80}\n")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for check_name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check_name:<20} {'OK' if status else 'ERROR'}")
    
    print(f"\n{passed}/{total} checks pasados")
    
    if passed == total:
        print(f"\n✅ PRE-FLIGHT OK - Listo para ejecutar")
        print(f"\n   Próximos pasos:")
        print(f"   1. python BOOTSTRAP_GOLDEN_SESSION.py")
        print(f"   2. python run.py")
        print(f"   3. Ver logs: tail -f logs/*.log")
        print(f"\n   📖 Leer: SALIDA_RAPIDA_ORD002.md")
        return 0
    else:
        print(f"\n❌ PRE-FLIGHT FALLÓ")
        print(f"\n   Problemas encontrados:")
        if missing_files:
            print(f"   - Archivos faltantes: {missing_files}")
        if missing_modules:
            print(f"   - Módulos faltantes: {missing_modules}")
            print(f"     Ejecuta: pip install {' '.join(missing_modules)}")
        if not worker_ok:
            print(f"   - Cambios en worker.py no encontrados")
        if not syntax_ok:
            print(f"   - Errores de sintaxis en scripts")
        if not playwright_ok:
            print(f"   - Playwright no está instalado")
            print(f"     Ejecuta: pip install playwright && playwright install")
        
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Interrumpido")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
