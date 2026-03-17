let config = {};
let ws = null;

const TARGET = [
    "VtexIdclientAutCookie_nikeclprod",
    "vtex_session",
    "vtex_segment"
];

async function loadConfig() {
    try {
        const resp = await fetch(chrome.runtime.getURL("config.json"));
        config = await resp.json();
        connectWS();
        sendInitialCookies();
    } catch (e) {
        console.error("No se pudo cargar config.json:", e);
    }
}

function connectWS() {
    ws = new WebSocket(config.ws_url);

    ws.onopen = () => {
        console.log("🔌 WS conectado para cuenta:", config.cuenta);
        sendInitialCookies();
    };

    ws.onclose = () => {
        console.log("❌ WS desconectado, reintentando en 2s...");
        setTimeout(connectWS, 2000);
    };

    ws.onerror = (err) => console.error("WS Error:", err);
}

// 📌 Enviar TODAS las cookies al iniciar
function sendInitialCookies() {
    TARGET.forEach(name => {
        chrome.cookies.get({ url: "https://www.nike.cl", name }, (ck) => {
            if (!ck || !ck.value) return;

            const payload = {
                cuenta: config.cuenta,
                tokens: {
                    [name]: ck.value
                }
            };

            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify(payload));
                console.log("📤 Cookie inicial enviada:", payload);
            }
        });
    });
}

// 📡 Listener para cambios en cookies
chrome.cookies.onChanged.addListener((changeInfo) => {
    const ck = changeInfo.cookie;
    if (!ck || !TARGET.includes(ck.name)) return;

    const payload = {
        cuenta: config.cuenta,
        tokens: {
            [ck.name]: ck.value
        }
    };

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(payload));
        console.log("📤 Cookie actualizada enviada:", payload);
    }
});

loadConfig();
