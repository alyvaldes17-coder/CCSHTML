"""
================================================================================
CHROME LAUNCHER OPTIMIZED - Lanzamiento de Chrome con flags de rendimiento
================================================================================
Optimizaciones extremas de Chrome para máxima velocidad en drops.

IMPACTO:
- --blink-settings=imagesEnabled=false: -2-3s por página
- GPU acceleration: -1-2s en rendering
- Memoria: Reduce 500MB por Chrome con caché mínimo
================================================================================
"""

import subprocess
import os
import psutil
from typing import List, Dict, Any
import time


class ChromeLauncherOptimized:
    """Lanza Chrome con optimizaciones extremas"""
    
    # Ubicación típica de Chrome en Windows
    CHROME_PATHS = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{user}\AppData\Local\Google\Chrome\Application\chrome.exe",
    ]
    
    # Flags óptimos para drops
    FLAGS_OPTIMIZACION = [
        # Performance
        "--blink-settings=imagesEnabled=false",  # Deshabilitar imágenes
        "--disable-extensions",
        "--disable-sync",
        "--disable-default-apps",
        "--disable-background-networking",
        "--disable-component-extensions",
        
        # GPU & Rendering
        "--enable-gpu-rasterization",
        "--enable-zero-copy",
        "--use-gl=desktop",
        
        # Memory
        "--disk-cache-size=1",
        "--media-cache-size=1",
        "--disable-dev-shm-usage",
        
        # Network
        "--disable-http2-server-push",
        "--disable-preconnect",
        
        # Seguridad (pero rápido)
        "--no-first-run",
        "--no-default-browser-check",
        
        # Rendering
        "--disable-software-rasterizer",
        "--disable-hang-monitor",
    ]
    
    @staticmethod
    def encontrar_chrome() -> str:
        """Encuentra la ruta de Chrome en el sistema"""
        
        usuario = os.getenv('USERNAME')
        
        for path_template in ChromeLauncherOptimized.CHROME_PATHS:
            path = path_template.format(user=usuario)
            
            if os.path.exists(path):
                return path
        
        # Fallback: buscar en PATH
        try:
            result = subprocess.run(['where', 'chrome.exe'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        raise FileNotFoundError("Chrome no encontrado en el sistema")
    
    @staticmethod
    def lanzar_chrome_optimizado(
        puerto_debug: int,
        perfil: str,
        url_inicial: str = "about:blank",
        headless: bool = False
    ) -> subprocess.Popen:
        """
        Lanza Chrome con optimizaciones
        
        Args:
            puerto_debug: Puerto para DevTools (ej: 9224)
            perfil: Ruta del perfil (user data dir)
            url_inicial: URL a cargar al inicio
            headless: Modo headless (para testing)
        
        Returns:
            Proceso de Chrome
        
        EJEMPLO:
            >>> proceso = ChromeLauncherOptimized.lanzar_chrome_optimizado(
            ...     puerto_debug=9224,
            ...     perfil=r"C:\Nike\profiles\cuenta1"
            ... )
        """
        
        chrome_path = ChromeLauncherOptimized.encontrar_chrome()
        
        cmd = [
            chrome_path,
            f"--remote-debugging-port={puerto_debug}",
            f"--user-data-dir={perfil}",
            "--remote-allow-origins=*",
            "--window-size=1280,900",
        ]
        
        # Agregar flags de optimización
        cmd.extend(ChromeLauncherOptimized.FLAGS_OPTIMIZACION)
        
        # Headless si es necesario
        if headless:
            cmd.append("--headless=new")
        
        # URL inicial
        cmd.append(url_inicial)
        
        print(f"🚀 Lanzando Chrome en puerto {puerto_debug}...")
        
        try:
            proceso = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Esperar a que escuche en el puerto
            time.sleep(2)
            
            print(f"  ✅ Chrome iniciado (PID: {proceso.pid})")
            
            return proceso
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
            raise
    
    @staticmethod
    def lanzar_13_chromes_optimizados(
        base_puerto: int = 9224,
        base_perfil: str = r"C:\Nike\profiles",
        nombres_cuentas: List[str] = None
    ) -> Dict[str, subprocess.Popen]:
        """
        Lanza 13 Chrome simultáneamente con optimizaciones
        
        Args:
            base_puerto: Puerto inicial (ej: 9224 → 9224-9236)
            base_perfil: Carpeta base de perfiles
            nombres_cuentas: Nombres de las cuentas (ej: ['cuenta1', 'cuenta2', ...])
        
        Returns:
            Dict {nombre_cuenta: proceso}
        
        EJEMPLO:
            >>> procesos = ChromeLauncherOptimized.lanzar_13_chromes_optimizados()
            >>> print(f"Lanzados {len(procesos)} Chromes")
        """
        
        if nombres_cuentas is None:
            nombres_cuentas = [f'cuenta{i}' for i in range(1, 14)]
        
        procesos = {}
        
        print(f"\n{'='*70}")
        print(f"🚀 LANZANDO 13 CHROMES OPTIMIZADOS")
        print(f"{'='*70}\n")
        
        for i, nombre in enumerate(nombres_cuentas[:13], 1):
            puerto = base_puerto + i - 1
            perfil = os.path.join(base_perfil, nombre)
            
            # Crear carpeta de perfil si no existe
            os.makedirs(perfil, exist_ok=True)
            
            try:
                print(f"  [{i:2d}/13] {nombre:12s} → puerto {puerto}", end='')
                
                proceso = ChromeLauncherOptimized.lanzar_chrome_optimizado(
                    puerto_debug=puerto,
                    perfil=perfil,
                    url_inicial="https://www.nike.cl"
                )
                
                procesos[nombre] = proceso
                
                print(" ✅")
                
                # Delay entre lanzamientos para evitar picos de CPU/RAM
                time.sleep(0.3)
            
            except Exception as e:
                print(f" ❌ {e}")
        
        print(f"\n✅ {len(procesos)}/13 Chromes lanzados\n")
        
        return procesos
    
    @staticmethod
    def obtener_stats_memoria():
        """Obtiene estadísticas de memoria actual"""
        
        proceso = psutil.Process()
        memoria = proceso.memory_info()
        
        chrome_procesos = [p for p in psutil.process_iter(['pid', 'name']) 
                          if 'chrome' in p.info['name'].lower()]
        
        memoria_total_chrome = sum(p.memory_info()[0] for p in chrome_procesos) / (1024**2)  # MB
        memoria_sistema = psutil.virtual_memory()
        
        return {
            'chrome_procesos': len(chrome_procesos),
            'memoria_chrome_mb': memoria_total_chrome,
            'memoria_sistema_total_mb': memoria_sistema.total / (1024**2),
            'memoria_sistema_usada_mb': memoria_sistema.used / (1024**2),
            'memoria_sistema_disponible_mb': memoria_sistema.available / (1024**2),
            'porcentaje_sistema': memoria_sistema.percent,
        }
    
    @staticmethod
    def imprimir_stats_memoria():
        """Imprime estadísticas de memoria formateado"""
        
        stats = ChromeLauncherOptimized.obtener_stats_memoria()
        
        print(f"\n{'='*70}")
        print(f"💾 MEMORIA")
        print(f"{'='*70}")
        print(f"  Chrome procesos:        {stats['chrome_procesos']}")
        print(f"  Memoria Chrome total:   {stats['memoria_chrome_mb']:.0f} MB")
        print(f"  Sistema usado:          {stats['memoria_sistema_usada_mb']:.0f} / {stats['memoria_sistema_total_mb']:.0f} MB")
        print(f"  Disponible:             {stats['memoria_sistema_disponible_mb']:.0f} MB")
        print(f"  Porcentaje uso:         {stats['porcentaje_sistema']:.1f}%")
        print(f"{'='*70}\n")
        
        # Advertencias
        if stats['porcentaje_sistema'] > 90:
            print("  ⚠️  ALERTA: +90% memoria en uso → Posible congelamiento")
        elif stats['porcentaje_sistema'] > 80:
            print("  ⚠️  ADVERTENCIA: +80% memoria → Monitor de próxima")


def test_chrome_launcher():
    """Test del lanzador de Chrome"""
    
    print("🧪 Testing Chrome Launcher\n")
    
    try:
        chrome_path = ChromeLauncherOptimized.encontrar_chrome()
        print(f"✅ Chrome encontrado: {chrome_path}\n")
        
        # Verificar flags
        print("📋 Flags de optimización que se usarán:\n")
        for i, flag in enumerate(ChromeLauncherOptimized.FLAGS_OPTIMIZACION, 1):
            print(f"  {i:2d}. {flag}")
        
        print("\n✅ Sistema listo para lanzar Chromes\n")
        
    except FileNotFoundError as e:
        print(f"❌ {e}\n")


if __name__ == "__main__":
    test_chrome_launcher()
