/**
 * useBotSocket — Hook WebSocket para comunicación con bot_api.py local
 *
 * Maneja: conexión, reconexión, envío de comandos, recepción de logs y estados.
 */
import { useEffect, useRef, useState, useCallback } from "react";

const BOT_WS_URL = "ws://127.0.0.1:8000/ws";
const BOT_API_URL = "http://127.0.0.1:8000";
const RECONNECT_MS = 3000;

export interface BotAccount {
  name: string;
  display_name: string;
  sku: string;
  payment_mode: string;
  state: string;
  login_ok: boolean;
}

export interface BotLog {
  time: string;
  msg: string;
  color: string;
  account: string;
}

export interface StockEvent {
  sku: string;
  name: string;
  quantity: number;
  price: number;
  timestamp: string;
}

export interface MonitorStatus {
  running: boolean;
  skus: string[];
  checks: number;
  errors: number;
  interval: number;
}

export function useBotSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout>>(undefined);
  const [connected, setConnected] = useState(false);
  const [accounts, setAccounts] = useState<BotAccount[]>([]);
  const [logs, setLogs] = useState<Record<string, BotLog[]>>({});
  const [monitorLogs, setMonitorLogs] = useState<BotLog[]>([]);
  const [monitorStatus, setMonitorStatus] = useState<MonitorStatus | null>(null);
  const [lastStockEvent, setLastStockEvent] = useState<StockEvent | null>(null);

  // ── Actualizar estado de una cuenta ──
  const updateAccountState = useCallback((name: string, state: string) => {
    setAccounts(prev =>
      prev.map(a => (a.name === name ? { ...a, state } : a))
    );
  }, []);

  // ── Agregar log a una cuenta ──
  const addLog = useCallback((account: string, time: string, msg: string) => {
    const color = msg.includes("✅") ? "#00e676"
      : msg.includes("❌") ? "#ff1744"
      : msg.includes("⚠") ? "#ff9800"
      : msg.includes("🔥") ? "#ffd600"
      : "#888";

    setLogs(prev => {
      const current = prev[account] || [];
      const entry: BotLog = { time, msg, color, account };
      return { ...prev, [account]: [entry, ...current].slice(0, 200) };
    });
  }, []);

  // ── Conectar WebSocket ──
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(BOT_WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      // Pedir cuentas al conectar
      ws.send(JSON.stringify({ action: "accounts" }));
    };

    ws.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data);

        if (data.type === "accounts") {
          setAccounts(data.data);
        } else if (data.type === "log") {
          addLog(data.account, data.time, data.msg);
        } else if (data.type === "state") {
          updateAccountState(data.account, data.state);
        } else if (data.type === "monitor_log") {
          setMonitorLogs(prev => [
            { time: data.time, msg: data.msg, color: "#2979ff", account: "_monitor" },
            ...prev,
          ].slice(0, 200));
        } else if (data.type === "stock") {
          setLastStockEvent(data as unknown as StockEvent);
        } else if (data.type === "monitor_status") {
          setMonitorStatus(data as unknown as MonitorStatus);
        }
      } catch {
        // ignore
      }
    };

    ws.onclose = () => {
      setConnected(false);
      reconnectRef.current = setTimeout(connect, RECONNECT_MS);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [addLog, updateAccountState]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  // ── Comandos ──
  const send = useCallback((cmd: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(cmd));
    }
  }, []);

  const play = useCallback((account: string, sku?: string) => {
    send({ action: "play", account, sku });
  }, [send]);

  const stop = useCallback((account: string) => {
    send({ action: "stop", account });
  }, [send]);

  const playAll = useCallback((sku?: string) => {
    send({ action: "play-all", sku });
  }, [send]);

  const stopAll = useCallback(() => {
    send({ action: "stop-all" });
  }, [send]);

  const refreshAccounts = useCallback(() => {
    send({ action: "accounts" });
  }, [send]);

  const monitorStart = useCallback((skus?: string[], interval?: number) => {
    send({ action: "monitor-start", skus, interval });
  }, [send]);

  const monitorStop = useCallback(() => {
    send({ action: "monitor-stop" });
  }, [send]);

  const monitorGetStatus = useCallback(() => {
    send({ action: "monitor-status" });
  }, [send]);

  return {
    connected,
    accounts,
    logs,
    monitorLogs,
    monitorStatus,
    lastStockEvent,
    play,
    stop,
    playAll,
    stopAll,
    refreshAccounts,
    monitorStart,
    monitorStop,
    monitorGetStatus,
  };
}

/** Fetch REST para health check */
export async function checkBotApi(): Promise<boolean> {
  try {
    const r = await fetch(`${BOT_API_URL}/health`, { signal: AbortSignal.timeout(2000) });
    return r.ok;
  } catch {
    return false;
  }
}
