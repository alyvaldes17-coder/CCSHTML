/**
 * Nike Bot Extension - Content Script
 * Se ejecuta en la página de Nike.cl
 * 
 * Responsabilidades:
 * 1. Matar modales molestos
 * 2. Auto-advance /cart → /payment
 * 3. Seleccionar método de pago
 * 4. Notificar cuando pago completa
 */

// ═══════════════════════════════════════════════════════════════
// CERRAR MODALES (lo que más molesta)
// ═══════════════════════════════════════════════════════════════

function closeModals() {
  // Selectors comunes de modales/overlays en React
  const modalSelectors = [
    '[role="dialog"]',
    '.ReactModal__Overlay',
    '.react-modal',
    '.modal',
    '.overlay',
    '[class*="Modal"]',
    '[class*="modal"]',
    '.cookie-banner',
    '[data-testid*="modal"]'
  ];

  modalSelectors.forEach(selector => {
    try {
      document.querySelectorAll(selector).forEach(element => {
        // Buscar botón cerrar dentro del modal
        const closeBtn = element.querySelector('[aria-label="Close"], button[title="Close"], .close');
        if (closeBtn) {
          closeBtn.click();
          console.log('[EXT] Modal cerrado:', selector);
          return;
        }
        // Si no hay botón, ocultar directamente
        element.style.display = 'none';
      });
    } catch (e) {
      // ignorar
    }
  });
}

// ═══════════════════════════════════════════════════════════════
// AUTO-ADVANCE: /cart → /payment
// ═══════════════════════════════════════════════════════════════

function autoAdvanceIfInCart() {
  const url = window.location.href;
  
  if (url.includes('/checkout') && url.includes('cart')) {
    console.log('[EXT] Detectada página /cart - redirigiendo a /payment');
    
    setTimeout(() => {
      window.location.href = 'https://www.nike.cl/checkout/#/payment';
    }, 500);
  }
}

// ═══════════════════════════════════════════════════════════════
// SELECCIONAR MÉTODO DE PAGO
// ═══════════════════════════════════════════════════════════════

function selectPaymentMethod() {
  // Esperar a que cargue la página
  setTimeout(() => {
    const paymentMethods = {
      'credit': ['Tarjeta de crédito', 'Crédito'],
      'debit': ['Tarjeta de débito', 'Débito'],
      'mercadopago': ['Mercado Pago'],
      'transferencia': ['Transferencia']
    };

    // Buscar botones de método de pago
    const buttons = document.querySelectorAll('button, div[role="button"], [class*="Payment"]');
    
    buttons.forEach(btn => {
      const text = btn.innerText || btn.textContent || '';
      
      // Prioridad: Mercado Pago (si está configurado)
      if (text.includes('Mercado Pago')) {
        btn.click();
        console.log('[EXT] Método de pago seleccionado: Mercado Pago');
        return;
      }
      
      // Si no, buscar tarjeta de crédito (la más común)
      if (text.includes('Tarjeta') && text.includes('crédito')) {
        btn.click();
        console.log('[EXT] Método de pago seleccionado: Tarjeta de crédito');
        return;
      }
    });
  }, 1000);
}

// ═══════════════════════════════════════════════════════════════
// FOCUS EN BOTÓN PAGAR (cuando aparezca)
// ═══════════════════════════════════════════════════════════════

function focusPayButton() {
  // Esperar a que el botón PAGAR aparezca
  const observer = new MutationObserver(() => {
    const payButton = document.querySelector(
      'button:contains("Pagar"), button:contains("PAGAR"), [class*="payButton"]'
    );
    
    if (payButton) {
      payButton.focus();
      payButton.scrollIntoView({ behavior: 'smooth', block: 'center' });
      console.log('[EXT] Botón PAGAR en focus');
      observer.disconnect();
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  // Timeout: si no aparece en 15s, dejar
  setTimeout(() => observer.disconnect(), 15000);
}

// ═══════════════════════════════════════════════════════════════
// NOTIFICAR AL BOT
// ═══════════════════════════════════════════════════════════════

function notifyPaymentComplete() {
  // Detectar si la compra fue exitosa
  const successIndicators = [
    'Pedido confirmado',
    'Compra realizada',
    'Thank you',
    'Gracias por tu compra',
    'order received'
  ];

  const pageText = document.body.innerText.toLowerCase();
  
  successIndicators.forEach(indicator => {
    if (pageText.includes(indicator.toLowerCase())) {
      console.log('[EXT] PAGO COMPLETADO');
      
      // Notificar al bot (si existe comunicación)
      chrome.runtime.sendMessage({
        type: 'PAYMENT_COMPLETE',
        url: window.location.href,
        timestamp: Date.now()
      }).catch(() => {
        // Si falla, no es crítico
      });
      
      return;
    }
  });
}

// ═══════════════════════════════════════════════════════════════
// MAIN - Ejecutar al cargar la página
// ═══════════════════════════════════════════════════════════════

(function init() {
  console.log('[EXT] Nike Bot Extension - Iniciada');

  // 1. Cerrar modales inmediatamente
  closeModals();
  
  // 2. Auto-advance si está en /cart
  autoAdvanceIfInCart();
  
  // 3. Esperar y seleccionar pago
  selectPaymentMethod();
  
  // 4. Focus en botón pagar
  focusPayButton();
  
  // 5. Monitorear pago completado
  notifyPaymentComplete();

  // Ejecutar closeModals periodicamente (porque Nike agrega overlays)
  setInterval(closeModals, 2000);
})();
