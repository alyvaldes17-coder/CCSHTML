#!/usr/bin/env python
"""
🔍 MONITOR DE BOT EN VIVO
Ver los logs del bot en tiempo real para diagnosticar qué está pasando.
"""

import subprocess
import os
from pathlib import Path

DEBUG_LOG = "logs/cuenta2_debug.log"

print("\n" + "="*70)
print("🔍 MONITOR DE BOT NIKE - LOGS EN VIVO")
print("="*70 + "\n")

if not Path(DEBUG_LOG).exists():
    print(f"❌ Log no existe aún: {DEBUG_LOG}")
    print(f"   Ejecuta primero: python main.py\n")
    exit(1)

print(f"📂 Archivo: {DEBUG_LOG}\n")
print("Últimas 50 líneas (auto-actualiza):\n")
print("─" * 70)

try:
    # Tail -f style (Windows)
    subprocess.run(["powershell", "-Command", f"Get-Content {DEBUG_LOG} -Wait"], check=False)
except KeyboardInterrupt:
    print("\n\n✅ Monitor cerrado")
except FileNotFoundError:
    # Fallback si PowerShell no está
    with open(DEBUG_LOG) as f:
        lines = f.readlines()[-50:]
        for line in lines:
            print(line.rstrip())
