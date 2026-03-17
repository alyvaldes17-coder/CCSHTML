#!/usr/bin/env python
"""Quick syntax check - no runtime"""
import sys
import os

print("[Syntax Check]")

# Check imports
try:
    import auth.session_check as sc
    print("✅ auth.session_check OK")
except Exception as e:
    print(f"❌ auth.session_check: {e}")
    sys.exit(1)

# Check functions
try:
    assert hasattr(sc, 'check_session_nike')
    assert hasattr(sc, 'login_from_ui')
    print("✅ Funciones OK")
except Exception as e:
    print(f"❌ Funciones: {e}")
    sys.exit(1)

# Check ui.app imports
try:
    import ui.app
    print("✅ ui.app imports OK")
except Exception as e:
    print(f"❌ ui.app: {e}")
    sys.exit(1)

print("\n[✅] Todos los imports funcionan")
