/**
 * Nike Bot Extension - Background Service Worker
 * Gestiona eventos de la extensión
 */

console.log('[EXT] Background service worker iniciado');

// Escuchar mensajes desde content.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'PAYMENT_COMPLETE') {
    console.log('[EXT] Pago completado en:', request.url);
    
    // Aquí puedes enviar notificaciones al bot si es necesario
    // Por ahora solo registramos
    
    sendResponse({ success: true });
  }
});

// Escuchar cuando una pestaña se abre/cierra
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && tab.url.includes('nike.cl')) {
    console.log('[EXT] Pestaña Nike actualizada:', tab.url);
  }
});
