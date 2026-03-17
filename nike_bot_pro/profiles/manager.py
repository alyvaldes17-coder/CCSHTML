#!/usr/bin/env python3
"""
profile_manager.py - Gestor de Perfiles (Master/Slave Architecture)

Solución definitiva a SingletonLock en Windows:
- profile_login  → Master (donde el usuario se loguea manualmente)
- profile_run    → Slave (copia fresca, desechable)

Flujo:
1. Usuario loguea UNA VEZ en profile_login
2. Antes de cada bot run: clonar profile_login → profile_run
3. Playwright abre profile_run (limpio, sin locks)
4. Después: destruir profile_run (el master sigue seguro)
5. Repetir

Ventajas:
✅ Master nunca se corrompe
✅ Locks se limpian automáticamente
✅ Cookies persisten (no hay que revolver)
✅ Velocidad (ignora caché basura)
"""
import shutil
import os
import time
from pathlib import Path
from config.settings import AUTH_ROOT


class ProfileManager:
    """Gestor de clonación de perfiles"""
    
    def __init__(self, account_name: str, base_path: str = None):
        """
        Args:
            account_name: Nombre de la cuenta (ej: "cuenta2")
            base_path: IGNORADO - Usa AUTH_ROOT de config.settings por definición
        """
        self.account_name = account_name
        self.account_path = os.path.join(AUTH_ROOT, account_name)
        
        # Rutas de perfiles (SIEMPRE absolutas desde AUTH_ROOT)
        self.profile_login = os.path.join(self.account_path, "profile_login")
        self.profile_run = os.path.join(self.account_path, "profile_run")
    
    def cleanup_run_profile(self, force: bool = False):
        """
        Elimina el perfil de ejecución anterior (profile_run).
        
        ⚠️ CRÍTICO para limpiar SingletonLock
        
        Args:
            force: Si True, intenta más agresivamente (matar procesos)
        """
        if not os.path.exists(self.profile_run):
            return True
        
        print(f"[{self.account_name}] 🧹 Limpiando perfil anterior...")
        
        try:
            # Intento 1: Borrado simple
            shutil.rmtree(self.profile_run)
            print(f"[{self.account_name}] ✅ Limpieza exitosa")
            return True
            
        except PermissionError as e:
            print(f"[{self.account_name}] ⚠️ Permiso denegado: {e}")
            
            if force:
                print(f"[{self.account_name}] 🔨 Intentando fuerza bruta...")
                
                # Intento 2: Esperar y reintentar
                time.sleep(2)
                try:
                    shutil.rmtree(self.profile_run)
                    print(f"[{self.account_name}] ✅ Limpieza exitosa (intento 2)")
                    return True
                except Exception as e2:
                    print(f"[{self.account_name}] ❌ Falló intento 2: {e2}")
                    print(f"[{self.account_name}] 💡 Sugerencia: Cierra todos los chrome.exe en Task Manager")
                    return False
            
            return False
    
    def clone_login_to_run(self) -> bool:
        """
        Clona profile_login a profile_run.
        
        Ignora caché basura para velocidad:
        - Cache
        - Code Cache
        - Crashpad
        - ShaderCache
        - etc
        
        Returns:
            True si clonación exitosa
        """
        # Verificar que profile_login existe
        if not os.path.exists(self.profile_login):
            print(f"[{self.account_name}] ❌ ERROR: Master profile no existe")
            print(f"[{self.account_name}]    Ruta: {self.profile_login}")
            print(f"[{self.account_name}]    Debes loguearte primero en login_runner.py")
            return False
        
        # Limpiar perfil anterior
        if not self.cleanup_run_profile(force=True):
            return False
        
        print(f"[{self.account_name}] 🧬 Clonando master → run...")
        
        try:
            # Carpetas basura a ignorar (acelera clonación)
            ignore_patterns = shutil.ignore_patterns(
                "Cache",
                "Code Cache",
                "Crashpad",
                "ShaderCache",
                "GrShaderCache",
                "hyphen-data",
                "Dictionaries",
                "lockfile",  # ← CRÍTICO
                ".lock",     # ← CRÍTICO
                "SingletonLock",  # ← CRÍTICO
            )
            
            # Clonar
            start = time.time()
            shutil.copytree(
                self.profile_login,
                self.profile_run,
                ignore=ignore_patterns,
                dirs_exist_ok=False
            )
            elapsed = time.time() - start
            
            print(f"[{self.account_name}] ✅ Clonación exitosa ({elapsed:.2f}s)")
            print(f"[{self.account_name}]    Master: {self.profile_login}")
            print(f"[{self.account_name}]    Run:    {self.profile_run}")
            
            return True
            
        except Exception as e:
            print(f"[{self.account_name}] ❌ Error clonando: {type(e).__name__}: {e}")
            return False
    
    def get_run_profile_path(self) -> str:
        """Retorna la ruta del perfil de ejecución"""
        return self.profile_run
    
    def get_login_profile_path(self) -> str:
        """Retorna la ruta del perfil de login"""
        return self.profile_login
    
    def verify_master_profile(self) -> bool:
        """
        Verifica que el master profile tiene cookies válidas.
        
        Returns:
            True si hay signos de sesión válida
        """
        cookies_path = os.path.join(self.profile_login, "Cookies")
        
        if not os.path.exists(cookies_path):
            print(f"[{self.account_name}] ❌ No hay cookies en master profile")
            return False
        
        # Verificar que archivo no está vacío
        size = os.path.getsize(cookies_path)
        if size < 1000:  # Menos de 1KB = probablemente vacío
            print(f"[{self.account_name}] ⚠️ Archivo de cookies muy pequeño ({size} bytes)")
            return False
        
        print(f"[{self.account_name}] ✅ Master profile tiene cookies válidas ({size} bytes)")
        return True


# Test del módulo
if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST: ProfileManager (Master/Slave Architecture)")
    print("="*60)
    
    # Test con cuenta2
    manager = ProfileManager("cuenta2")
    
    print("\n1️⃣ Verificar rutas:")
    print(f"   Master: {manager.profile_login}")
    print(f"   Run:    {manager.profile_run}")
    
    print("\n2️⃣ Verificar master profile:")
    manager.verify_master_profile()
    
    print("\n3️⃣ Clonar a run profile:")
    success = manager.clone_login_to_run()
    
    if success:
        print("\n✅ ProfileManager funciona correctamente")
    else:
        print("\n❌ Hay errores que corregir")
    
    print("="*60)
