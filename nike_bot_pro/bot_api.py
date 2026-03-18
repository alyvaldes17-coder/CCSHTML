"""
bot_api.py — FastAPI local + WebSocket bridge para Tauri

Arquitectura:
  [Tauri App] ←WebSocket→ [FastAPI :8000] ←Multiprocessing→ [Workers] ←CDP→ [Chrome] → [Nike VTEX]

Endpoints REST:
  GET  /accounts          → lista cuentas con estado
  POST /play/{cuenta}     → lanzar bot en esa cuenta
  POST /stop/{cuenta}     → detener bot
  POST /stop-all          → detener todos
  POST /play-all          → lanzar todos los READY

WebSocket:
  WS /ws                  → stream de logs y estados en tiempo real
"""

import asyncio
import json
import os
import sys
import multiprocessing
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ── Asegurar que podemos importar módulos del bot ──
BOT_ROOT = os.path.dirname(os.path.abspath(__file__))
if BOT_ROOT not in sys.path:
    sys.path.insert(0, BOT_ROOT)

from manager.account_manager import AccountManager
from stock_monitor import StockMonitor, StockEvent

app = FastAPI(title="Nike Bot Pro — Local API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "http://localhost:5173", "tauri://localhost"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Estado global ──
account_manager = AccountManager()
account_manager.load_accounts()

# Procesos activos: { "cuenta1": Process }
active_workers: Dict[str, multiprocessing.Process] = {}

# Cola compartida para logs (workers → API → WebSocket)
log_queue: multiprocessing.Queue = multiprocessing.Queue()

# Clientes WebSocket conectados
ws_clients: list[WebSocket] = []

# ── Stock Monitor centralizado ──
stock_monitor: Optional[StockMonitor] = None


def _broadcast_json(data: dict):
    """Envía un mensaje JSON a todos los clientes WS via log_queue."""
    log_queue.put(json.dumps(data))


def _on_stock_detected(evt: StockEvent):
    """Callback cuando el monitor detecta stock — dispara todos los workers."""
    _broadcast_json({
        "type": "stock",
        "sku": evt.sku,
        "name": evt.name,
        "quantity": evt.quantity,
        "price": evt.price,
        "timestamp": evt.timestamp,
    })
    # Auto-launch: lanzar todas las cuentas READY con este SKU
    for name, acc in account_manager.accounts.items():
        if acc.state.value != "READY":
            continue
        if name in active_workers and active_workers[name].is_alive():
            continue
        stop_evt = multiprocessing.Event()
        stop_events[name] = stop_evt
        p = multiprocessing.Process(
            target=worker_process,
            args=(name, evt.sku, log_queue, stop_evt),
            daemon=True,
            name=f"worker-{name}",
        )
        p.start()
        active_workers[name] = p
        _broadcast_json({
            "type": "log",
            "account": name,
            "msg": f"🔥 Stock detectado ({evt.name}) — lanzado automáticamente",
            "time": evt.timestamp,
        })


def _on_monitor_log(msg: str):
    """Callback de logs del monitor → WS broadcast."""
    _broadcast_json({
        "type": "monitor_log",
        "msg": msg,
        "time": datetime.now().strftime("%H:%M:%S"),
    })


# ═════════════════════════════════════════════════════════════════════════════
# WORKER — corre en proceso separado
# ═════════════════════════════════════════════════════════════════════════════

def worker_process(account_name: str, sku: str, log_q: Any,
                   stop_event: Any):
    """
    Proceso independiente por cuenta. Usa BotController existente.
    Se comunica con la API via log_queue.
    """
    import time

    # Re-add bot root to sys.path (nuevo proceso)
    bot_root = os.path.dirname(os.path.abspath(__file__))
    if bot_root not in sys.path:
        sys.path.insert(0, bot_root)

    from runtime.bot_controller import BotController

    def send_log(msg: str):
        log_q.put(json.dumps({
            "type": "log",
            "account": account_name,
            "msg": msg,
            "time": datetime.now().strftime("%H:%M:%S"),
        }))

    def send_state(state: str):
        log_q.put(json.dumps({
            "type": "state",
            "account": account_name,
            "state": state,
        }))

    try:
        send_state("starting")
        send_log(f"[{account_name}] Worker iniciado — SKU {sku}")

        ctrl = BotController(account_name)
        ctrl.on_log = send_log
        ctrl.on_state_change = send_state

        # Monitorear stop_event en un thread del worker
        import threading

        def watch_stop():
            stop_event.wait()
            ctrl.stop_signal = True
            ctrl._stop_event.set()
            send_log(f"[{account_name}] Stop signal recibido")

        t = threading.Thread(target=watch_stop, daemon=True)
        t.start()

        ctrl.handle_btn_play_hybrid(sku)

    except Exception as e:
        send_log(f"[{account_name}] Error fatal: {e}")
        send_state("failed")
    finally:
        send_state("stopped")
        send_log(f"[{account_name}] Worker finalizado")


# ═════════════════════════════════════════════════════════════════════════════
# BROADCAST — log_queue → WebSocket clients
# ═════════════════════════════════════════════════════════════════════════════

async def broadcast_logs():
    """Lee log_queue y envía a todos los clientes WebSocket."""
    while True:
        try:
            while not log_queue.empty():
                msg = log_queue.get_nowait()
                dead = []
                for ws in ws_clients:
                    try:
                        await ws.send_text(msg)
                    except Exception:
                        dead.append(ws)
                for ws in dead:
                    ws_clients.remove(ws)
        except Exception:
            pass
        await asyncio.sleep(0.05)  # 50ms — logs en tiempo real


@app.on_event("startup")
async def startup():
    asyncio.create_task(broadcast_logs())


# ═════════════════════════════════════════════════════════════════════════════
# REST ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/accounts")
async def get_accounts():
    """Lista todas las cuentas con su estado."""
    result = []
    for name, acc in account_manager.accounts.items():
        # Leer config para SKU y método de pago
        cfg_path = os.path.join("auth", name, "config.json")
        sku = acc.sku or ""
        payment_mode = "transfer"
        display_name = name

        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            skus = [s for s in cfg.get("skus", []) if s]
            if skus:
                sku = skus[0]
            payment_mode = cfg.get("payment_mode", "transfer")
            display_name = cfg.get("display_name", cfg.get("email", name))
        except Exception:
            pass

        is_running = name in active_workers and active_workers[name].is_alive()

        result.append({
            "name": name,
            "display_name": display_name,
            "sku": sku,
            "payment_mode": payment_mode,
            "state": "running" if is_running else acc.state.value,
            "login_ok": acc.state.value == "READY",
        })

    return result


# Stop events por cuenta
stop_events: Dict[str, Any] = {}


@app.post("/play/{account_name}")
async def play_account(account_name: str, sku: Optional[str] = None):
    """Lanza el bot en una cuenta específica."""
    if account_name not in account_manager.accounts:
        return {"ok": False, "error": f"Cuenta '{account_name}' no existe"}

    acc = account_manager.accounts[account_name]
    if acc.state.value != "READY":
        return {"ok": False, "error": f"Cuenta no está READY (estado: {acc.state.value})"}

    # Si ya hay un worker corriendo, no lanzar otro
    if account_name in active_workers and active_workers[account_name].is_alive():
        return {"ok": False, "error": "Ya está corriendo"}

    # SKU desde parámetro o config
    target_sku = sku or acc.sku or ""
    if not target_sku:
        # Intentar leer de config.json
        cfg_path = os.path.join("auth", account_name, "config.json")
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            skus = [s for s in cfg.get("skus", []) if s]
            target_sku = skus[0] if skus else ""
        except Exception:
            pass

    if not target_sku:
        return {"ok": False, "error": "Sin SKU configurado"}

    # Crear stop event y lanzar proceso
    stop_evt = multiprocessing.Event()
    stop_events[account_name] = stop_evt

    p = multiprocessing.Process(
        target=worker_process,
        args=(account_name, target_sku, log_queue, stop_evt),
        daemon=True,
        name=f"worker-{account_name}",
    )
    p.start()
    active_workers[account_name] = p

    return {"ok": True, "sku": target_sku, "pid": p.pid}


@app.post("/stop/{account_name}")
async def stop_account(account_name: str):
    """Detiene el bot de una cuenta."""
    if account_name in stop_events:
        stop_events[account_name].set()

    if account_name in active_workers:
        p = active_workers[account_name]
        if p.is_alive():
            p.terminate()
            p.join(timeout=3)
            if p.is_alive():
                p.kill()
        del active_workers[account_name]

    return {"ok": True}


@app.post("/stop-all")
async def stop_all():
    """Detiene todos los workers."""
    names = list(active_workers.keys())
    for name in names:
        await stop_account(name)
    return {"ok": True, "stopped": names}


@app.post("/play-all")
async def play_all(sku: Optional[str] = None):
    """Lanza todos los READY."""
    launched = []
    for name, acc in account_manager.accounts.items():
        if acc.state.value == "READY" and (name not in active_workers or not active_workers[name].is_alive()):
            result = await play_account(name, sku)
            if result.get("ok"):
                launched.append(name)
    return {"ok": True, "launched": launched}


@app.get("/health")
async def health():
    running = [n for n, p in active_workers.items() if p.is_alive()]
    return {
        "status": "healthy",
        "accounts_total": len(account_manager.accounts),
        "accounts_running": len(running),
        "running": running,
        "monitor": stock_monitor.stats if stock_monitor else None,
    }


# ═════════════════════════════════════════════════════════════════════════════
# STOCK MONITOR ENDPOINTS
# ═════════════════════════════════════════════════════════════════════════════

@app.post("/monitor/start")
async def monitor_start(skus: Optional[list[str]] = None, interval: Optional[float] = None):
    """Inicia el monitor centralizado de stock."""
    global stock_monitor

    if stock_monitor and stock_monitor.running:
        return {"ok": False, "error": "Monitor ya está corriendo"}

    stock_monitor = StockMonitor(
        on_stock=_on_stock_detected,
        on_log=_on_monitor_log,
        interval=interval or 0.5,
    )

    # SKUs: del body, o recopilar de todas las cuentas
    target_skus = skus or []
    if not target_skus:
        seen = set()
        for name, acc in account_manager.accounts.items():
            s = acc.sku or ""
            if not s:
                cfg_path = os.path.join("auth", name, "config.json")
                try:
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                    sk = [x for x in cfg.get("skus", []) if x]
                    s = sk[0] if sk else ""
                except Exception:
                    pass
            if s and s not in seen:
                seen.add(s)
                target_skus.append(s)

    for s in target_skus:
        stock_monitor.add_sku(s)

    await stock_monitor.start()
    return {"ok": True, "skus": target_skus, "interval": stock_monitor.interval}


@app.post("/monitor/stop")
async def monitor_stop():
    """Detiene el monitor de stock."""
    global stock_monitor
    if stock_monitor:
        stock_monitor.stop()
    return {"ok": True}


@app.get("/monitor/status")
async def monitor_status():
    """Estado actual del monitor."""
    if not stock_monitor:
        return {"running": False, "skus": [], "checks": 0}
    return stock_monitor.stats


# ═════════════════════════════════════════════════════════════════════════════
# WEBSOCKET
# ═════════════════════════════════════════════════════════════════════════════

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    ws_clients.append(ws)
    try:
        while True:
            # Recibir comandos del frontend
            data = await ws.receive_text()
            try:
                cmd = json.loads(data)
                action = cmd.get("action")

                if action == "play":
                    result = await play_account(cmd["account"], cmd.get("sku"))
                    await ws.send_text(json.dumps({"type": "response", **result}))

                elif action == "stop":
                    result = await stop_account(cmd["account"])
                    await ws.send_text(json.dumps({"type": "response", **result}))

                elif action == "play-all":
                    result = await play_all(cmd.get("sku"))
                    await ws.send_text(json.dumps({"type": "response", **result}))

                elif action == "stop-all":
                    result = await stop_all()
                    await ws.send_text(json.dumps({"type": "response", **result}))

                elif action == "accounts":
                    result = await get_accounts()
                    await ws.send_text(json.dumps({"type": "accounts", "data": result}))

                elif action == "monitor-start":
                    result = await monitor_start(cmd.get("skus"), cmd.get("interval"))
                    await ws.send_text(json.dumps({"type": "response", "action": "monitor-start", **result}))

                elif action == "monitor-stop":
                    result = await monitor_stop()
                    await ws.send_text(json.dumps({"type": "response", "action": "monitor-stop", **result}))

                elif action == "monitor-status":
                    result = await monitor_status()
                    await ws.send_text(json.dumps({"type": "monitor_status", **result}))

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        pass
    finally:
        if ws in ws_clients:
            ws_clients.remove(ws)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    multiprocessing.freeze_support()
    print("\n" + "=" * 60)
    print("  NIKE BOT PRO — Local API")
    print("  http://localhost:8000")
    print("  WebSocket: ws://localhost:8000/ws")
    print("  Docs: http://localhost:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("bot_api:app", host="127.0.0.1", port=8000, reload=False)
