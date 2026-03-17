import os
import glob

# Buscar y eliminar Lockfiles en todos los perfiles
auth_path = os.path.abspath('auth')
for profile_dir in glob.glob(os.path.join(auth_path, '*/profile_pw')):
    lockfile = os.path.join(profile_dir, 'Singleton Lock')
    if os.path.exists(lockfile):
        try:
            os.remove(lockfile)
            print(f'✅ Eliminado: {lockfile}')
        except Exception as e:
            print(f'⚠️ Error: {e}')
    else:
        print(f'ℹ️ No hay Lockfile en: {profile_dir}')
