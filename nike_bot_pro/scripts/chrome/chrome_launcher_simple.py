#!/usr/bin/env python3
"""
SIMPLE CHROME LAUNCHER - Abre Chrome en puerto 9224 Y LO MANTIENE VIVO
"""

import subprocess
import sys
import time
import socket

PORT = 9224
PROFILE = r"c:\Users\beriann\Documents\Repos\nikebotprofuncionalv1\nike_bot_pro\auth\cuenta2\profile_login"

print("=" * 70)
print("🚀 CHROME LAUNCHER - Abriendo Chrome en puerto 9224")
print("=" * 70)

# Lanzar Chrome
cmd = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    f"--remote-debugging-port={PORT}",
    f"--user-data-dir={PROFILE}",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-gpu",
]

print(f"\n📍 Perfil: {PROFILE}")
print(f"🔌 Puerto: {PORT}")
print(f"⏳ Lanzando Chrome...\n")

# Lanzar en background (no esperar)
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(f"✅ Chrome lanzado (PID: {proc.pid})")

# Esperar a que escuche en el puerto
print(f"⏳ Esperando que Chrome escuche en puerto {PORT}...")
for intento in range(1, 21):  # 20 intentos = 20 segundos
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect(('127.0.0.1', PORT))
        s.close()
        elapsed = intento * 1
        print(f"✅ Puerto {PORT} escuchando (después de {elapsed}s)")
        break
    except:
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1)
else:
    print(f"\n❌ Chrome no escucha en puerto {PORT} después de 20s")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ Chrome está listo. Ahora puedes usar el bot.")
print("=" * 70)
print("\n⏸️  Presiona Ctrl+C para cerrar Chrome")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Cerrando Chrome...")
    proc.terminate()
    time.sleep(2)
    if proc.poll() is None:
        proc.kill()
    print("✅ Chrome cerrado")
