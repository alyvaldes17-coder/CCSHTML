#!/usr/bin/env python3
"""
Verificar qué programa está usando el puerto 9223.
Windows only.
"""

import subprocess
import re

def check_port(port=9223):
    """Verifica qué programa está usando un puerto en Windows."""
    try:
        # netstat -ano: muestra conexiones y PIDs
        result = subprocess.check_output(
            f"netstat -ano | findstr :{port}",
            shell=True,
            text=True
        )
        
        if result.strip():
            print(f"\n🔍 Puerto {port} ESTÁ EN USO:")
            print(result)
            
            # Intentar extraer PID
            lines = result.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    print(f"\n   PID: {pid}")
                    
                    # Obtener nombre del proceso
                    try:
                        proc_result = subprocess.check_output(
                            f"tasklist /FI \"PID eq {pid}\" /NH",
                            shell=True,
                            text=True
                        ).strip()
                        print(f"   Proceso: {proc_result}")
                    except:
                        pass
        else:
            print(f"\n✅ Puerto {port} ESTÁ LIBRE (no hay nada usando)")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    print(f"Verificando puerto 9223...")
    check_port(9223)
