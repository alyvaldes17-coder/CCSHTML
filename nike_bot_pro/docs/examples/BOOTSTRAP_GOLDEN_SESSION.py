#!/usr/bin/env python3
"""
BOOTSTRAP_GOLDEN_SESSION.py

Script de entrada única para salir del estancamiento ORD002.

Flujo:
  1. Validar que todas las cuentas tienen session_golden.json
  2. Si no, ejecutar pdp_seeder.py automáticamente
  3. Validar contrato con HANDOVER_CONTRACT.py
  4. Mostrar status y recomendaciones

PROPÓSITO: "Punto de entrada" para no olvidar pasos
"""

import subprocess
import sys
import json
from pathlib import Path


def run_command(cmd, description: str):
    """Ejecuta comando y retorna (success, output)"""
    print(f"\n{'='*70}")
    print(f"▶️  {description}")
    print(f"{'='*70}")
    print(f"$ {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True, check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False


def check_golden_sessions() -> dict:
    """
    Chequea qué cuentas tienen session_golden.json
    
    Returns:
        {"cuenta1": True/False, ...}
    """
    auth_path = Path("auth")
    if not auth_path.exists():
        print("❌ Carpeta 'auth/' no existe")
        return {}
    
    results = {}
    for account_dir in auth_path.iterdir():
        if account_dir.is_dir() and not account_dir.name.startswith("."):
            golden_path = account_dir / "session_golden.json"
            results[account_dir.name] = golden_path.exists()
    
    return results


def read_accounts_json() -> list:
    """Lee accounts.json si existe"""
    accounts_file = Path("accounts.json")
    if not accounts_file.exists():
        return []
    
    try:
        with open(accounts_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("accounts", [])
    except:
        return []


def main():
    """Flujo principal"""
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║     🚀 BOOTSTRAP GOLDEN SESSION - Salir del estancamiento ORD002      ║
╚══════════════════════════════════════════════════════════════════════╝

OBJETIVO: Preparar sesiones doradas para todas las cuentas.

""")
    
    # PASO 1: Detectar cuentas
    print("1️⃣  DETECTANDO CUENTAS...")
    
    accounts_json = read_accounts_json()
    if accounts_json:
        print(f"\n   📄 accounts.json encontrado ({len(accounts_json)} cuentas)")
        accounts_config = {acc["name"]: acc for acc in accounts_json}
    else:
        print(f"\n   ⚠️  accounts.json no existe")
        print(f"   Buscando en auth/...")
        accounts_config = {acc: {"name": acc} for acc in check_golden_sessions().keys()}
    
    if not accounts_config:
        print(f"\n   ❌ No hay cuentas en auth/")
        sys.exit(1)
    
    print(f"\n   ✅ Cuentas encontradas: {list(accounts_config.keys())}")
    
    # PASO 2: Verificar sesiones doradas
    print(f"\n2️⃣  VERIFICANDO SESIONES DORADAS...")
    
    golden_status = check_golden_sessions()
    missing_golden = [name for name, has_golden in golden_status.items() if not has_golden]
    
    for account_name, has_golden in golden_status.items():
        icon = "✅" if has_golden else "❌"
        print(f"   {icon} {account_name}: {'OK' if has_golden else 'FALTA session_golden.json'}")
    
    # PASO 3: Crear sesiones faltantes con pdp_seeder
    if missing_golden:
        print(f"\n3️⃣  PREPARANDO SESIONES FALTANTES ({len(missing_golden)} cuentas)...")
        
        for account_name in missing_golden:
            acc_config = accounts_config.get(account_name, {})
            sku = acc_config.get("sku", "DZ4373-100")  # SKU default
            
            print(f"\n   🌱 Preparando {account_name} (SKU={sku})...")
            
            success = run_command(
                ["python", "pdp_seeder.py", account_name, sku],
                f"pdp_seeder.py {account_name} {sku}"
            )
            
            if not success:
                print(f"   ⚠️  pdp_seeder falló para {account_name}")
                print(f"   Intenta manualmente: python pdp_seeder.py {account_name} {sku}")
    else:
        print(f"\n3️⃣  ✅ TODAS LAS SESIONES DORADAS YA EXISTEN")
    
    # PASO 4: Validar contrato con HANDOVER_CONTRACT.py
    print(f"\n4️⃣  VALIDANDO CONTRATO DE HANDOVER...")
    
    run_command(
        ["python", "HANDOVER_CONTRACT.py"] + list(accounts_config.keys()),
        f"HANDOVER_CONTRACT.py para {len(accounts_config)} cuentas"
    )
    
    # PASO 5: Resumen y recomendaciones
    print(f"\n{'='*70}")
    print(f"📊 RESUMEN Y PRÓXIMOS PASOS")
    print(f"{'='*70}\n")
    
    final_status = check_golden_sessions()
    all_ready = all(final_status.values())
    
    if all_ready:
        print(f"✅ TODAS LAS SESIONES DORADAS ESTÁN LISTAS\n")
        print(f"Próximos pasos:")
        print(f"  1. Ejecutar Worker:")
        print(f"     python run.py")
        print(f"\n  2. Validar que ORD002 desaparece:")
        print(f"     grep 'ORD002' logs/*.log")
        print(f"\n  3. Si todo OK, avanzar a WAITING_STABILITY")
    else:
        print(f"⚠️  ALGUNAS SESIONES AÚN FALTAN\n")
        print(f"Cuentas incompletas:")
        for acc, ready in final_status.items():
            if not ready:
                sku = accounts_config.get(acc, {}).get("sku", "DZ4373-100")
                print(f"  - {acc}: python pdp_seeder.py {acc} {sku}")
    
    print(f"\n{'='*70}")
    print(f"📖 Documentación: TRES_AJUSTES_QUIRURGICOS.md")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Interrumpido por usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
