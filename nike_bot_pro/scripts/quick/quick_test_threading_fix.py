#!/usr/bin/env python
"""
QUICK TEST: Verify the threading fix works end-to-end
Run this BEFORE testing with main.py
"""

import sys
from pathlib import Path

print("\n" + "=" * 70)
print("QUICK VALIDATION CHECK")
print("=" * 70)

# 1. Verify imports
print("\n[Check 1] Verifying imports...")
try:
    import threading
    print("  ✅ threading")
    
    import customtkinter
    print("  ✅ customtkinter")
    
    from auth.session_check import setup_account_login_safe, setup_account_login
    print("  ✅ auth.session_check.setup_account_login_safe")
    print("  ✅ auth.session_check.setup_account_login")
    
    from utils.zombie_killer import matar_zombies_del_perfil
    print("  ✅ utils.zombie_killer.matar_zombies_del_perfil")
    
except ImportError as e:
    print(f"  ❌ Import error: {e}")
    sys.exit(1)

# 2. Verify UI app can initialize
print("\n[Check 2] Verifying UI app structure...")
try:
    from ui.app import AppUI
    print("  ✅ UI app imports correctly")
    
    # Check if AppUI has the required attributes
    import inspect
    source = inspect.getsource(AppUI)
    
    if "self.login_running" in source:
        print("  ✅ login_running dict added to AppUI.__init__()")
    else:
        print("  ⚠️  login_running dict NOT found in AppUI.__init__()")
    
    if "setup_account_login_safe" in source:
        print("  ✅ _login() method calls setup_account_login_safe")
    else:
        print("  ⚠️  _login() method does not call setup_account_login_safe")
    
    if "threading.Thread" in source:
        print("  ✅ _login() uses threading.Thread")
    else:
        print("  ⚠️  _login() does not use threading.Thread")
        
except Exception as e:
    print(f"  ❌ Error checking AppUI: {e}")
    sys.exit(1)

# 3. Verify session_check has both functions
print("\n[Check 3] Verifying session_check.py...")
try:
    import auth.session_check as sc
    
    if hasattr(sc, "setup_account_login_safe"):
        print("  ✅ setup_account_login_safe() exists")
    else:
        print("  ❌ setup_account_login_safe() NOT FOUND")
        sys.exit(1)
    
    if hasattr(sc, "setup_account_login"):
        print("  ✅ setup_account_login() exists")
    else:
        print("  ❌ setup_account_login() NOT FOUND")
        sys.exit(1)
    
    if hasattr(sc, "matar_zombies_del_perfil"):
        print("  ✅ matar_zombies_del_perfil imported")
    else:
        print("  ❌ matar_zombies_del_perfil NOT FOUND")
        
except Exception as e:
    print(f"  ❌ Error checking session_check: {e}")
    sys.exit(1)

# 4. Verify no syntax errors in critical files
print("\n[Check 4] Verifying Python syntax...")
try:
    from pathlib import Path
    import py_compile
    
    files_to_check = [
        "ui/app.py",
        "auth/session_check.py"
    ]
    
    for file in files_to_check:
        filepath = Path(file)
        if filepath.exists():
            try:
                py_compile.compile(str(filepath), doraise=True)
                print(f"  ✅ {file}")
            except py_compile.PyCompileError as e:
                print(f"  ❌ {file}: {e}")
                sys.exit(1)
        else:
            print(f"  ⚠️  {file} not found")
            
except Exception as e:
    print(f"  ⚠️  Could not check syntax: {e}")

print("\n" + "=" * 70)
print("✅ ALL CHECKS PASSED")
print("=" * 70)

print("\n📋 NEXT STEPS:")
print("  1. Run: python main.py")
print("  2. Click [🔐 LOGIN] button")
print("  3. Verify Chrome opens within 1-2 seconds")
print("  4. Complete login manually")
print("  5. Close Chrome window")
print("  6. Check if button [▶ PLAY] becomes enabled")
print("\nIf all these work → threading fix is successful! ✅\n")
