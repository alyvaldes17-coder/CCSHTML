import { useState, useEffect } from "react";
import { T } from "../theme";
import { useBotSocket, checkBotApi } from "../services/botSocket";

const METODOS: Record<string, string> = {
  transfer: "Transferencia Fintoc",
  credit_card: "Tarjeta de crédito",
  debit: "Tarjeta de débito",
  mercadopago: "Mercado Pago",
  tenpo: "Tenpo",
};

const STATE_COLORS: Record<string, string> = {
  READY: "#00e676",
  running: "#ffd600",
  playing: "#ffd600",
  starting: "#2979ff",
  paused: "#ff9800",
  stopped: "#888",
  failed: "#ff1744",
  done: "#00e676",
  NO_AUTH: "#ff1744",
  MONITORING: "#2979ff",
  monitoring: "#2979ff",
};

const STATE_LABELS: Record<string, string> = {
  READY: "LISTO",
  running: "CORRIENDO",
  playing: "ATACANDO",
  starting: "INICIANDO",
  paused: "PAUSADO",
  stopped: "DETENIDO",
  failed: "ERROR",
  done: "COMPRA OK",
  NO_AUTH: "SIN LOGIN",
  MONITORING: "MONITOR",
  monitoring: "MONITOR",
};

export function Drop({ t }: { t: T }) {
  const {
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
  } = useBotSocket();

  const [selectedAccount, setSelectedAccount] = useState<string | null>(null);
  const [apiAlive, setApiAlive] = useState<boolean | null>(null);
  const [showMonitor, setShowMonitor] = useState(false);

  useEffect(() => {
    checkBotApi().then(setApiAlive);
    const interval = setInterval(() => checkBotApi().then(setApiAlive), 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!selectedAccount && accounts.length > 0) {
      setSelectedAccount(accounts[0].name);
    }
  }, [accounts, selectedAccount]);

  const isRunning = accounts.some(a =>
    ["running", "playing", "starting", "monitoring"].includes(a.state)
  );

  const selectedLogs = selectedAccount ? (logs[selectedAccount] || []) : [];
  const selectedAcc = accounts.find(a => a.name === selectedAccount);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", background: t.bg }}>

      {/* ═══ HEADER ═══ */}
      <div style={{
        padding: "14px 24px", borderBottom: `1px solid ${t.border}`,
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: t.panel,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ color: t.text, fontSize: 16, fontWeight: 700, letterSpacing: 0.3 }}>
            Drop Engine
          </span>
          <span style={{
            display: "inline-flex", alignItems: "center", gap: 5,
            background: connected ? "#00e67615" : "#ff174415",
            border: `1px solid ${connected ? "#00e67640" : "#ff174440"}`,
            borderRadius: 10, padding: "2px 10px",
            color: connected ? "#00e676" : "#ff1744",
            fontSize: 10, fontWeight: 600,
          }}>
            <span style={{
              width: 6, height: 6, borderRadius: "50%",
              background: connected ? "#00e676" : "#ff1744",
            }} />
            {connected ? "API CONECTADA" : apiAlive === false ? "API OFFLINE — ejecuta bot_api.py" : "CONECTANDO..."}
          </span>
          <span style={{
            background: t.row, border: `1px solid ${t.border}`,
            borderRadius: 10, padding: "2px 10px",
            color: t.textMed, fontSize: 11, fontWeight: 600,
          }}>
            {accounts.filter(a => a.login_ok).length}/{accounts.length} cuentas
          </span>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button onClick={() => setShowMonitor(v => !v)} style={{
            background: monitorStatus?.running ? "#2979ff15" : t.row,
            border: `1px solid ${monitorStatus?.running ? "#2979ff" : t.border}`,
            color: monitorStatus?.running ? "#2979ff" : t.textMed,
            borderRadius: 8, padding: "8px 14px",
            fontSize: 12, fontWeight: 600, cursor: "pointer",
          }}>
            {monitorStatus?.running ? `📡 Monitor (${monitorStatus.checks})` : "📡 Monitor"}
          </button>
          <button onClick={() => refreshAccounts()} style={{
            background: t.row, border: `1px solid ${t.border}`,
            color: t.textMed, borderRadius: 8, padding: "8px 14px",
            fontSize: 12, fontWeight: 600, cursor: "pointer",
          }}>↻</button>
          <button
            onClick={() => isRunning ? stopAll() : playAll()}
            disabled={!connected}
            style={{
              background: isRunning ? t.redDim : t.greenDim,
              border: `1px solid ${isRunning ? t.red : t.green}`,
              color: isRunning ? t.red : t.green,
              borderRadius: 8, padding: "8px 20px",
              fontSize: 12, fontWeight: 700,
              cursor: connected ? "pointer" : "not-allowed",
              opacity: connected ? 1 : 0.5,
            }}
          >
            {isRunning ? "■ DETENER TODO" : "▶ LANZAR TODO"}
          </button>
        </div>
      </div>

      {/* ═══ STOCK ALERT BAR ═══ */}
      {lastStockEvent && (
        <div style={{
          padding: "10px 24px", display: "flex", alignItems: "center", gap: 12,
          background: "#ffd60010", borderBottom: `1px solid #ffd60030`,
        }}>
          <span style={{ fontSize: 18 }}>🔥</span>
          <span style={{ color: "#ffd600", fontSize: 13, fontWeight: 700 }}>
            ¡STOCK DETECTADO!
          </span>
          <span style={{ color: t.text, fontSize: 12 }}>{lastStockEvent.name}</span>
          <span style={{ color: t.green, fontSize: 12, fontFamily: "Consolas" }}>
            SKU {lastStockEvent.sku}
          </span>
          <span style={{ color: t.textMed, fontSize: 12 }}>
            {lastStockEvent.quantity} uds — ${lastStockEvent.price?.toLocaleString()}
          </span>
          <span style={{ color: t.textDim, fontSize: 11 }}>{lastStockEvent.timestamp}</span>
        </div>
      )}

      {/* ═══ MONITOR PANEL ═══ */}
      {showMonitor && (
        <div style={{
          padding: "14px 24px", borderBottom: `1px solid ${t.border}`,
          background: t.panel, display: "flex", flexDirection: "column", gap: 10,
        }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ color: t.text, fontSize: 13, fontWeight: 700 }}>📡 Stock Monitor</span>
              <span style={{
                background: monitorStatus?.running ? "#2979ff15" : t.row,
                border: `1px solid ${monitorStatus?.running ? "#2979ff40" : t.border}`,
                borderRadius: 10, padding: "2px 10px",
                color: monitorStatus?.running ? "#2979ff" : t.textDim,
                fontSize: 10, fontWeight: 600,
              }}>
                {monitorStatus?.running ? `ACTIVO — ${monitorStatus.checks} checks` : "INACTIVO"}
              </span>
              {monitorStatus?.running && (
                <span style={{ color: t.textDim, fontSize: 10 }}>
                  SKUs: {monitorStatus.skus?.join(", ")} — cada {monitorStatus.interval}s
                </span>
              )}
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              {monitorStatus?.running ? (
                <button onClick={() => monitorStop()} style={{
                  background: t.redDim, border: `1px solid ${t.red}`,
                  color: t.red, borderRadius: 8, padding: "6px 16px",
                  fontSize: 11, fontWeight: 700, cursor: "pointer",
                }}>■ Detener</button>
              ) : (
                <button
                  onClick={() => monitorStart()}
                  disabled={!connected}
                  style={{
                    background: t.greenDim, border: `1px solid ${t.green}`,
                    color: t.green, borderRadius: 8, padding: "6px 16px",
                    fontSize: 11, fontWeight: 700,
                    cursor: connected ? "pointer" : "not-allowed",
                    opacity: connected ? 1 : 0.5,
                  }}
                >▶ Iniciar Monitor</button>
              )}
            </div>
          </div>
          {monitorLogs.length > 0 && (
            <div style={{
              maxHeight: 120, overflowY: "auto",
              background: t.bg, borderRadius: 6, padding: "8px 12px",
              display: "flex", flexDirection: "column", gap: 2,
            }}>
              {monitorLogs.slice(0, 30).map((log, i) => (
                <div key={i} style={{ display: "flex", gap: 10 }}>
                  <span style={{ color: t.textDim, fontSize: 10, fontFamily: "Consolas", minWidth: 60 }}>
                    {log.time}
                  </span>
                  <span style={{ color: log.color, fontSize: 11, fontFamily: "Consolas" }}>{log.msg}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ═══ TABLE ═══ */}
      <div style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }}>

        <div style={{
          display: "grid",
          gridTemplateColumns: "40px 1fr 150px 160px 100px 130px 80px",
          gap: 8, padding: "10px 20px",
          borderBottom: `1px solid ${t.border}`,
          background: t.panel,
        }}>
          {["#", "CUENTA", "DISPLAY", "MÉTODO", "SKU", "ESTADO", ""].map((h, i) => (
            <span key={i} style={{
              color: t.textDim, fontSize: 10, fontWeight: 700,
              letterSpacing: 0.8, textTransform: "uppercase",
            }}>{h}</span>
          ))}
        </div>

        <div style={{ flex: 1, overflowY: "auto" }}>
          {!connected && accounts.length === 0 ? (
            <div style={{
              display: "flex", flexDirection: "column", alignItems: "center",
              justifyContent: "center", padding: "48px 20px", gap: 12,
            }}>
              <span style={{ fontSize: 32 }}>🔌</span>
              <span style={{ color: t.textDim, fontSize: 13, fontWeight: 500 }}>Sin conexión al bot</span>
              <span style={{ color: t.textDim, fontSize: 11 }}>
                Ejecuta <code style={{ color: t.green, fontFamily: "Consolas" }}>python bot_api.py</code> en nike_bot_pro/
              </span>
            </div>
          ) : accounts.map((acc, i) => {
            const stColor = STATE_COLORS[acc.state] || "#888";
            const stLabel = STATE_LABELS[acc.state] || acc.state;
            const active = ["running", "playing", "starting", "monitoring"].includes(acc.state);

            return (
              <div
                key={acc.name}
                onClick={() => setSelectedAccount(acc.name)}
                style={{
                  display: "grid",
                  gridTemplateColumns: "40px 1fr 150px 160px 100px 130px 80px",
                  gap: 8, padding: "12px 20px",
                  borderBottom: `1px solid ${t.border}`,
                  background: selectedAccount === acc.name ? t.row : "transparent",
                  borderLeft: selectedAccount === acc.name ? `2px solid ${t.green}` : "2px solid transparent",
                  cursor: "pointer", alignItems: "center",
                }}
              >
                <span style={{ color: t.textDim, fontSize: 12 }}>#{i + 1}</span>
                <span style={{ color: t.text, fontSize: 12, fontWeight: 600 }}>{acc.name}</span>
                <span style={{ color: t.textMed, fontSize: 11 }}>{acc.display_name}</span>
                <span style={{ color: t.textMed, fontSize: 11 }}>{METODOS[acc.payment_mode] || acc.payment_mode}</span>
                <span style={{ color: t.green, fontSize: 11, fontFamily: "Consolas" }}>{acc.sku || "—"}</span>

                <span style={{
                  display: "inline-flex", alignItems: "center", gap: 5,
                  background: `${stColor}15`, border: `1px solid ${stColor}40`,
                  borderRadius: 12, padding: "3px 10px",
                  color: stColor, fontSize: 10, fontWeight: 700,
                  letterSpacing: 0.3, whiteSpace: "nowrap",
                }}>
                  <span style={{ width: 6, height: 6, borderRadius: "50%", background: stColor }} />
                  {stLabel}
                </span>

                <div style={{ display: "flex", gap: 6 }} onClick={e => e.stopPropagation()}>
                  {active ? (
                    <button onClick={() => stop(acc.name)} title="Detener" style={{
                      background: t.redDim, border: `1px solid ${t.red}`,
                      color: t.red, borderRadius: 6, padding: "6px 10px",
                      fontSize: 12, cursor: "pointer",
                    }}>■</button>
                  ) : (
                    <button
                      onClick={() => play(acc.name)}
                      disabled={!acc.login_ok || !connected}
                      title="Ejecutar"
                      style={{
                        background: acc.login_ok ? t.greenDim : t.row,
                        border: `1px solid ${acc.login_ok ? t.green : t.border}`,
                        color: acc.login_ok ? t.green : t.textDim,
                        borderRadius: 6, padding: "6px 10px", fontSize: 12,
                        cursor: acc.login_ok && connected ? "pointer" : "not-allowed",
                        opacity: acc.login_ok ? 1 : 0.5,
                      }}
                    >▶</button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* ═══ LOG PANEL ═══ */}
        {selectedAccount && (
          <div style={{
            borderTop: `2px solid ${t.green}20`,
            background: t.panel, maxHeight: 260, minHeight: 100,
            display: "flex", flexDirection: "column",
          }}>
            <div style={{
              padding: "10px 20px", borderBottom: `1px solid ${t.border}`,
              display: "flex", alignItems: "center", justifyContent: "space-between",
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{
                  width: 7, height: 7, borderRadius: "50%",
                  background: STATE_COLORS[selectedAcc?.state || ""] || "#888",
                }} />
                <span style={{ color: t.text, fontSize: 12, fontWeight: 600 }}>{selectedAccount}</span>
                <span style={{ color: t.textDim, fontSize: 12 }}>—</span>
                <span style={{ color: t.textMed, fontSize: 12, fontFamily: "Consolas" }}>
                  {selectedAcc?.sku || "sin sku"}
                </span>
                <span style={{
                  color: t.textDim, fontSize: 10,
                  background: t.row, borderRadius: 8, padding: "2px 8px",
                }}>{selectedLogs.length} logs</span>
              </div>
              <button onClick={() => setSelectedAccount(null)} style={{
                background: t.row, border: `1px solid ${t.border}`,
                borderRadius: 6, padding: "4px 10px",
                color: t.textDim, cursor: "pointer", fontSize: 13,
              }}>✕</button>
            </div>

            {selectedLogs.length === 0 ? (
              <div style={{
                padding: "24px 20px", color: t.textDim, fontSize: 12,
                display: "flex", alignItems: "center", gap: 8,
              }}>
                <span style={{ fontSize: 16 }}>💤</span>
                Sin logs — ejecuta la cuenta para ver actividad en tiempo real
              </div>
            ) : (
              <div style={{
                overflowY: "auto", padding: "10px 20px",
                display: "flex", flexDirection: "column", gap: 2,
              }}>
                <div style={{
                  display: "grid", gridTemplateColumns: "80px 1fr",
                  borderBottom: `1px solid ${t.border}`, paddingBottom: 6, marginBottom: 6,
                }}>
                  <span style={{ color: t.textDim, fontSize: 10, fontWeight: 700, letterSpacing: 0.8 }}>HORA</span>
                  <span style={{ color: t.textDim, fontSize: 10, fontWeight: 700, letterSpacing: 0.8 }}>MENSAJE</span>
                </div>
                {selectedLogs.map((log, i) => (
                  <div key={i} style={{
                    display: "grid", gridTemplateColumns: "80px 1fr", gap: 8, padding: "3px 0",
                  }}>
                    <span style={{ color: t.textDim, fontSize: 11, fontFamily: "Consolas" }}>{log.time}</span>
                    <span style={{ color: log.color, fontSize: 12, fontFamily: "Consolas" }}>{log.msg}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
