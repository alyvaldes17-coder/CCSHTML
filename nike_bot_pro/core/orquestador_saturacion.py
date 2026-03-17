"""
================================================================================
ORQUESTADOR DE SATURACIÓN
================================================================================
Lanza múltiples cuentas simultáneamente para maximizar probabilidad de compra.

ESTRATEGIA:
- Nike NO reserva stock hasta que la orden se completa (pago confirmado)
- Lanzar 13 cuentas simultáneamente = 13 intentos independientes
- Primera que pague gana el stock, las demás fallan (esperado)
- Probabilidad de éxito: ~50-80% vs ~5% con 1 sola cuenta

AUTOR: Nike Bot Pro - Saturación Edition
FECHA: 2025-02-20
================================================================================
"""

import threading
import time
from queue import Queue
from datetime import datetime
from typing import List, Dict, Any

# IMPORTANTE: NO modificar imports si ya tienes configurado Playwright
# Este código respeta tu configuración actual de puertos
from utils.stock_checker import verificar_stock_nike


class OrquestadorSaturacion:
    """
    Orquestador que lanza múltiples cuentas simultáneamente
    para maximizar probabilidad de compra en drops
    """
    
    def __init__(self, bot_controllers: List[Any]):
        """
        Args:
            bot_controllers: Lista de BotController ya configurados
                           (con sus puertos asignados)
        """
        self.controllers = bot_controllers
        self.resultado_queue = Queue()
        self.tiempo_inicio = None
        
        print(f"⚡ [ORQUESTADOR] Inicializado con {len(self.controllers)} cuentas")
    
    def ataque_saturacion(self, sku: str) -> bool:
        """
        Ejecuta ataque de saturación con todas las cuentas disponibles
        
        Args:
            sku: SKU del producto a comprar
        
        Returns:
            bool: True si al menos una cuenta llegó a Fintoc
        
        FLUJO:
        1. Verificar stock en API Nike
        2. Lanzar todas las cuentas simultáneamente (threads)
        3. Cada cuenta ejecuta su bot independientemente
        4. Monitorear resultados en tiempo real
        5. Reportar cuántas llegaron a Fintoc
        6. Usuario paga manualmente en la más rápida
        """
        
        print(f"\n{'='*70}")
        print(f"🔥 ATAQUE DE SATURACIÓN ACTIVADO")
        print(f"{'='*70}")
        print(f"   SKU: {sku}")
        print(f"   Cuentas: {len(self.controllers)}")
        print(f"   Estrategia: Lanzamiento simultáneo")
        print(f"{'='*70}\n")
        
        # ════════════════════════════════════════════════════════
        # FASE 1: VERIFICACIÓN DE STOCK
        # ════════════════════════════════════════════════════════
        
        print("🔍 [FASE 1] Verificando stock antes de atacar...\n")
        
        stock_info = verificar_stock_nike(sku)
        
        if not stock_info['tiene_stock']:
            print(f"\n{'='*70}")
            print(f"🚫 ATAQUE ABORTADO - SIN STOCK")
            print(f"{'='*70}")
            print(f"   Producto: {stock_info.get('nombre', 'Desconocido')}")
            print(f"   SKU: {sku}")
            print(f"   Razón: {stock_info.get('error', 'Sin inventario')}")
            print(f"{'='*70}\n")
            return False
        
        cantidad_disponible = stock_info['cantidad']
        print(f"\n✅ Stock confirmado: {cantidad_disponible} unidades")
        print(f"💰 Precio: ${stock_info['precio']:,}")
        print(f"🎯 Estrategia: Saturar con {len(self.controllers)} cuentas\n")
        
        # Countdown dramático
        print("🚀 Iniciando lanzamiento en...")
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        print("   ¡GO!\n")
        
        # ════════════════════════════════════════════════════════
        # FASE 2: LANZAMIENTO SIMULTÁNEO
        # ════════════════════════════════════════════════════════
        
        print(f"{'='*70}")
        print(f"🚀 [FASE 2] LANZAMIENTO SIMULTÁNEO")
        print(f"{'='*70}\n")
        
        self.tiempo_inicio = time.time()
        threads = []
        
        for i, controller in enumerate(self.controllers, 1):
            nombre_cuenta = getattr(controller, 'account_name', f'cuenta{i}')
            
            print(f"  [{i:2d}/{len(self.controllers)}] Lanzando {nombre_cuenta}...")
            
            thread = threading.Thread(
                target=self._worker_cuenta,
                args=(controller, sku, i, nombre_cuenta),
                daemon=True,
                name=f"Worker-{nombre_cuenta}"
            )
            
            thread.start()
            threads.append(thread)
            
            # Delay mínimo entre lanzamientos (300ms)
            # Esto evita saturar tu PC/red al inicio
            time.sleep(0.3)
        
        tiempo_lanzamiento = time.time() - self.tiempo_inicio
        print(f"\n✅ {len(self.controllers)} cuentas lanzadas en {tiempo_lanzamiento:.1f}s")
        print(f"\n{'='*70}\n")
        
        # ════════════════════════════════════════════════════════
        # FASE 3: MONITOREO EN TIEMPO REAL
        # ════════════════════════════════════════════════════════
        
        print(f"{'='*70}")
        print(f"📊 [FASE 3] MONITOREO EN TIEMPO REAL")
        print(f"{'='*70}\n")
        
        # Contadores
        cuentas_en_fintoc = 0
        cuentas_sin_stock = 0
        cuentas_error = 0
        resultados = []
        
        # Timeout de 90 segundos para esperar resultados
        timeout = 90
        tiempo_monitoreo_inicio = time.time()
        
        while (time.time() - tiempo_monitoreo_inicio) < timeout:
            try:
                # Chequear si hay resultados en la queue
                resultado = self.resultado_queue.get(timeout=1)
                resultados.append(resultado)
                
                cuenta = resultado['cuenta']
                estado = resultado['estado']
                tiempo = resultado['tiempo']
                
                if estado == 'FINTOC':
                    cuentas_en_fintoc += 1
                    print(f"  🏦 [{cuentas_en_fintoc}] {cuenta} → Fintoc abierto ({tiempo:.1f}s)")
                
                elif estado == 'SIN_STOCK':
                    cuentas_sin_stock += 1
                    print(f"  🚫 {cuenta} → Sin stock detectado")
                
                elif estado == 'ERROR':
                    cuentas_error += 1
                    error_msg = resultado.get('error', 'Desconocido')
                    print(f"  ❌ {cuenta} → Error: {error_msg}")
                
            except:
                # Timeout esperando en queue (normal)
                pass
            
            # Si todas las cuentas reportaron, salir
            total_reportadas = cuentas_en_fintoc + cuentas_sin_stock + cuentas_error
            if total_reportadas >= len(self.controllers):
                break
        
        # ════════════════════════════════════════════════════════
        # FASE 4: REPORTE FINAL
        # ════════════════════════════════════════════════════════
        
        tiempo_total = time.time() - self.tiempo_inicio
        
        print(f"\n{'='*70}")
        print(f"📊 REPORTE FINAL - ATAQUE COMPLETADO")
        print(f"{'='*70}")
        print(f"  Tiempo total:     {tiempo_total:.1f}s")
        print(f"  {'─'*68}")
        print(f"  🏦 En Fintoc:     {cuentas_en_fintoc}/{len(self.controllers)}")
        print(f"  🚫 Sin stock:     {cuentas_sin_stock}/{len(self.controllers)}")
        print(f"  ❌ Errores:       {cuentas_error}/{len(self.controllers)}")
        print(f"{'='*70}\n")
        
        # ════════════════════════════════════════════════════════
        # FASE 5: INSTRUCCIONES AL USUARIO
        # ════════════════════════════════════════════════════════
        
        if cuentas_en_fintoc > 0:
            print(f"{'='*70}")
            print(f"🎯 ¡ÉXITO! {cuentas_en_fintoc} VENTANAS DE FINTOC ABIERTAS")
            print(f"{'='*70}\n")
            
            print("💡 INSTRUCCIONES:")
            print("   1. Ve a las ventanas de Chrome que se abrieron")
            print("   2. Cada una tiene el selector de banco de Fintoc")
            print("   3. Elige la ventana más rápida en cargar")
            print("   4. Selecciona tu banco (BancoEstado = más rápido)")
            print("   5. Ingresa RUT y clave")
            print("   6. ¡PAGA LO MÁS RÁPIDO POSIBLE!")
            print(f"\n⚠️  IMPORTANTE:")
            print(f"   - Primera que pagues GANA el stock")
            print(f"   - Las otras {cuentas_en_fintoc-1} fallarán con 'Sin stock' (NORMAL)")
            print(f"   - No te preocupes si fallan, eso significa que ya compraste\n")
            
            print(f"{'='*70}\n")
            
            input("⏸️  Presiona ENTER cuando hayas completado el pago...")
            
            print("\n✅ Pago reportado como completado")
            print("🎉 ¡Felicitaciones si conseguiste la zapatilla!\n")
            
            return True
        
        else:
            print(f"{'='*70}")
            print(f"❌ ATAQUE FALLIDO - Ninguna cuenta llegó a Fintoc")
            print(f"{'='*70}\n")
            
            if cuentas_sin_stock > cuentas_error:
                print("💡 Causa probable: El producto se agotó muy rápido")
                print("   Intenta activar el bot ANTES del drop la próxima vez\n")
            else:
                print("💡 Causa probable: Errores técnicos")
                print("   Revisa los logs arriba para ver qué falló\n")
            
            return False
    
    def _worker_cuenta(self, controller: Any, sku: str, numero: int, nombre: str):
        """
        Worker thread que ejecuta el bot para una cuenta específica
        
        Args:
            controller: BotController de la cuenta
            sku: SKU del producto
            numero: Número de la cuenta (para logging)
            nombre: Nombre de la cuenta
        """
        
        tiempo_inicio_worker = time.time()
        
        try:
            # Ejecutar el bot (tu método existente)
            # IMPORTANTE: Esto usa el puerto que YA está configurado en el controller
            resultado = controller.ejecutar_bot(sku)
            
            tiempo_worker = time.time() - tiempo_inicio_worker
            
            # Interpretar resultado
            if resultado in ['HANDOFF_MANUAL', 'COMPRANDO_MANUAL', 'ESPERANDO_FINTOC']:
                # Éxito - llegó a Fintoc
                self.resultado_queue.put({
                    'cuenta': nombre,
                    'estado': 'FINTOC',
                    'tiempo': tiempo_worker
                })
            
            elif resultado == 'SIN_STOCK':
                # Sin stock detectado
                self.resultado_queue.put({
                    'cuenta': nombre,
                    'estado': 'SIN_STOCK',
                    'tiempo': tiempo_worker
                })
            
            else:
                # Error genérico
                self.resultado_queue.put({
                    'cuenta': nombre,
                    'estado': 'ERROR',
                    'error': resultado,
                    'tiempo': tiempo_worker
                })
        
        except KeyboardInterrupt:
            # Usuario canceló
            raise
        
        except Exception as e:
            # Error inesperado
            tiempo_worker = time.time() - tiempo_inicio_worker
            self.resultado_queue.put({
                'cuenta': nombre,
                'estado': 'ERROR',
                'error': str(e),
                'tiempo': tiempo_worker
            })


class FrancoTiradorV2:
    """
    Monitor de stock que lanza ataque de saturación cuando detecta disponibilidad
    
    OPTIMIZADO PARA:
    - Rate limiting seguro (2s entre checks)
    - Manejo robusto de errores
    - Logging detallado
    """
    
    def __init__(self, sku: str, interval: int = 2):
        """
        Args:
            sku: SKU a monitorear
            interval: Segundos entre checks (default: 2 = seguro, no banneable)
        """
        self.sku = sku
        self.interval = interval
        self.running = False
        self.errores_consecutivos = 0
        self.max_errores = 5
        
        print(f"👁️ [FRANCO TIRADOR] Inicializado")
        print(f"   SKU: {sku}")
        print(f"   Intervalo: {interval}s entre checks")
    
    def start_monitoring(self, on_stock_callback):
        """
        Inicia monitoreo continuo de stock
        
        Args:
            on_stock_callback: Función a ejecutar cuando detecta stock
                             (debe aceptar un argumento: sku)
        """
        
        self.running = True
        intentos = 0
        
        print(f"\n{'='*70}")
        print(f"🎯 FRANCO TIRADOR ACTIVADO")
        print(f"{'='*70}")
        print(f"   Modo: Monitoreo continuo")
        print(f"   Rate limit: {self.interval}s (seguro para tu IP)")
        print(f"   Presiona Ctrl+C para detener\n")
        
        while self.running:
            intentos += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            try:
                print(f"[{timestamp}] 🔍 Check #{intentos} - Verificando stock...")
                
                # Verificar stock en API
                stock_info = verificar_stock_nike(self.sku)
                
                if stock_info['tiene_stock']:
                    cantidad = stock_info['cantidad']
                    nombre = stock_info['nombre']
                    
                    print(f"\n{'='*70}")
                    print(f"🔥 ¡STOCK DETECTADO!")
                    print(f"{'='*70}")
                    print(f"   Producto: {nombre}")
                    print(f"   Cantidad: {cantidad} unidades")
                    print(f"   SKU: {self.sku}")
                    print(f"{'='*70}\n")
                    
                    # Ejecutar callback (lanzar saturación)
                    on_stock_callback(self.sku)
                    
                    # Pausa post-ataque (60s)
                    print(f"\n⏸️  Pausando 60s post-ataque...")
                    time.sleep(60)
                else:
                    print(f"   💤 Sin stock - Próximo check en {self.interval}s\n")
                
                # Reset contador de errores
                self.errores_consecutivos = 0
            
            except KeyboardInterrupt:
                print("\n⚠️ Franco Tirador detenido por usuario")
                self.running = False
                break
            
            except Exception as e:
                self.errores_consecutivos += 1
                print(f"   ⚠️ Error: {e}")
                print(f"   Errores consecutivos: {self.errores_consecutivos}/{self.max_errores}\n")
                
                if self.errores_consecutivos >= self.max_errores:
                    print(f"❌ Demasiados errores consecutivos - Abortando Franco Tirador")
                    self.running = False
                    break
            
            # Rate limiting (CRÍTICO para no ser banneado)
            time.sleep(self.interval)
        
        print("\n🛑 Franco Tirador detenido\n")
    
    def stop(self):
        """Detiene el monitoreo"""
        self.running = False


# ════════════════════════════════════════════════════════════════════════════
# TESTING
# ════════════════════════════════════════════════════════════════════════════

def test_orquestador():
    """Test del orquestador (requiere controllers configurados)"""
    
    print("🧪 Test del Orquestador de Saturación\n")
    print("⚠️ Este test requiere que tengas controllers configurados")
    print("   Para test real, usar desde main.py\n")


if __name__ == "__main__":
    test_orquestador()
