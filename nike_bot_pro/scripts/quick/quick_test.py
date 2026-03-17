#!/usr/bin/env python
"""Test simple para ver qué está fallando"""

print("1. Iniciando test...")

try:
    print("2. Importando os...")
    import os
    print("3. OK - os importado")
    
    print("4. Verificando CWD...")
    print(f"   CWD: {os.getcwd()}")
    
    print("5. Importando managers...")
    from manager.account_manager import AccountManager
    print("6. OK - AccountManager importado")
    
    print("7. Cargando cuentas...")
    manager = AccountManager()
    print(f"8. OK - {len(manager.accounts)} cuentas cargadas")
    
    print("\n✅ TODO FUNCIONA")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
