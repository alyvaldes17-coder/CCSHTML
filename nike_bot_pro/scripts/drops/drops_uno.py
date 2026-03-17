"""
👑 V20 - PRE-INYECCIÓN (Minority Report)

El código se instala ANTES de que cargue la página.
Cuando Nike trata de mostrar /cart, el navegador ya tiene orden:
"Si ves cart, salta a payment. PUNTO."

Combinamos:
✅ Smart launch (abre Chrome automáticamente)
✅ Pre-inyección (Page.addScriptToEvaluateOnNewDocument)
✅ Tu truco (window.location.hash = '/payment')
"""

import time
from engines.hybrid_engine import HybridAssassin

# CONFIGURACIÓN
PORT = 9224
SKU = "184016" 
PROFILE = r"C:\Users\beriann\Documents\Repos\nikebotprofuncionalv1\nike_bot_pro\auth\cuenta2\profile_login"

def menu():
    print("\n" + "="*60)
    print("👑 V20 - PRE-INYECCIÓN (Minority Report)")
    print("="*60)
    print("✅ Chrome abierto? Se conecta sin tocar nada.")
    print("❌ Chrome cerrado? Lo abre automáticamente.")
    print("🧠 Instala código ANTES de cargar la página.")
    print("="*60)
    print("1. 🗑️  VACIAR CARRITO")
    print("2. 🚀 ATAQUE (Code Pre-Loading)")
    print("0. ❌ SALIR")
    print("="*60)
    
    op = input("\n👉 Opción: ")
    
    if op == "0":
        print("👋 Hasta luego!")
        return
    
    bot = HybridAssassin(PORT, SKU, PROFILE)
    
    if op == "1":
        print("\n🧹 Vaciando carrito...")
        # bot.limpiar_carrito_vtex()  # Por ahora solo el ataque
    elif op == "2":
        print("\n🚀 EJECUTANDO ATAQUE (PRE-INYECCIÓN)...")
        time.sleep(0.5)
        bot.ejecutar_ataque()
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    while True:
        menu()
