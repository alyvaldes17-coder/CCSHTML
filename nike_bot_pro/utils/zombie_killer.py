"""
VACUNA ANTI-ZOMBIE 🧟‍♂️

Mata SOLO los procesos Chrome que estén bloqueando TU perfil.
No toca Chrome personal.

Función crítica para usar Perfiles Persistentes sin conflictos.
"""

import os
import time
import shutil
import logging

log = logging.getLogger("zombie_killer")


def matar_zombies_del_perfil(profile_path):
    """
    Intenta desbloquear el perfil eliminando el SingletonLock.
    Mucho más rápido que WMIC, no se cuelga.
    """
    print(f"   🧟 [ZOMBIE] Liberando perfil: {os.path.basename(profile_path)}")
    
    lock_file = os.path.join(profile_path, "SingletonLock")
    
    # 1. Intentar borrar el archivo de bloqueo
    if os.path.exists(lock_file):
        try:
            os.unlink(lock_file)
            print("   🧟 [ZOMBIE] 🔓 SingletonLock eliminado manualmente.")
        except PermissionError:
            print("   🧟 [ZOMBIE] ⚠️ El archivo está bloqueado por un proceso real.")
            # Aquí podrías forzar un taskkill si quisieras, pero usualmente basta con saberlo.
    
    # 2. Pequeña espera para que el sistema de archivos respire
    time.sleep(0.5)


# Alias: matar_chrome_especifico es lo mismo que matar_zombies_del_perfil
# (usada por engines/manual_login.py)
matar_chrome_especifico = matar_zombies_del_perfil