#!/usr/bin/env python
"""Test que verifican que el flujo puede iniciarse (sin abrir UI)"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("[TEST] === Testando estructura de Nike Bot ===\n")

# 1. Import
print("[1/5] Importando modules...")
try:
    from manager.account_manager import AccountManager
    from controller.controller import Controller
    from manager.supervisor import Supervisor
    print("  ✅ Imports OK")
except Exception as e:
    print(f"  ❌ Error: {e}")
    sys.exit(1)

# 2. Create AccountManager
print("[2/5] Creando AccountManager...")
try:
    manager = AccountManager()
    manager.load_accounts()
    print(f"  ✅ {len(manager.accounts)} cuentas cargadas: {list(manager.accounts.keys())}")
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Create Controller
print("[3/5] Creando Controller...")
try:
    controller = Controller(manager)
    print("  ✅ Controller OK")
except Exception as e:
    print(f"  ❌ Error: {e}")
    sys.exit(1)

# 4. Create Supervisor
print("[4/5] Iniciando Supervisor...")
try:
    sup = Supervisor(manager)
    sup.start()
    time.sleep(0.5)
    print("  ✅ Supervisor running")
except Exception as e:
    print(f"  ❌ Error: {e}")
    sys.exit(1)

# 5. Test AppUI creation (sin ejecutar mainloop)
print("[5/5] Validando AppUI...")
try:
    from ui.app import AppUI
    # No ejecutar, solo verificar que se puede crear
    print("  ✅ AppUI puede importarse")
    print("\n[✅] ÉXITO - Todo funciona, puedes ejecutar: python main.py")
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[STATUS] Sistema listo para ejecutar")
