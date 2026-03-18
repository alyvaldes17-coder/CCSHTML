import { useState, useEffect, useRef } from "react";
import { T } from "../theme";
import { useBotSocket, checkBotApi, BotAccount } from "../services/botSocket";

/* ═══════════════════════════════════════════════════════════════
   CONSTANTES
   ═══════════════════════════════════════════════════════════════ */

const METODOS: Record<string, string> = {
  transfer: "Fintoc",
  credit_card: "Crédito",
  debit: "Débito",
  mercadopago: "M.Pago",
  tenpo: "Tenpo",
};

const STATE_COLORS: Record<string, string> = {
  READY: "#00e676", running: "#ffd600", playing: "#ffd600",
  starting: "#2979ff", paused: "#ff9800", stopped: "#888",
  failed: "#ff1744", done: "#00e676", NO_AUTH: "#ff1744",
  MONITORING: "#2979ff", monitoring: "#2979ff",
  carting: "#ab47bc", checkout: "#ffd600", paying: "#ff9800",
  success: "#00e676", error: "#ff1744",
};

const STATE_LABELS: Record<string, string> = {
  READY: "LISTO", running: "CORRIENDO", playing: "ATACANDO",
  starting: "INICIANDO", paused: "PAUSADO", stopped: "DETENIDO",
  failed: "ERROR", done: "COMPRA OK", NO_AUTH: "SIN LOGIN",
  MONITORING: "MONITOR", monitoring: "MONITOR",
  carting: "CARRITO", checkout: "CHECKOUT", paying: "PAGANDO",
  success: "COMPRADO", error: "ERROR",
};

function getSavedSkus(): string[] {
  try { return JSON.parse(sessionStorage.getItem("aoda_skus") || "[]"); }
  catch { return []; }
}

/* ═══════════════════════════════════════════════════════════════
   BADGE — estado de cuenta compacto
   ═══════════════════════════════════════════════════════════════ */
function StateBadge({ state }: { state: string }) {
  const color = STATE_COLORS[state] || "#888";
  const label = STATE_LABELS[state] || state;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 4,
      background: `${color}15`, border: `1px solid ${color}35`,
      borderRadius: 10, padding: "2px 8px",
      color, fontSize: 9, fontWeight: 700,
      letterSpacing: 0.3, whiteSpace: "nowrap",
    }}>
      <span style={{ width: 5, height: 5, borderRadius: "50%", background: color }} />
      {label}
    </span>
  );
}

/* ═══════════════════════════════════════════════════════════════
   COMPONENTE DROP
   ═══════════════════════════════════════════════════════════════ */
export function Drop({ t }: { t: T }) {
  const {
    connected, accounts, logs,
    monitorLogs, monitorStatus, lastStockEvent,
    play, stop, playAll, stopAll,
    refreshAccounts, monitorStart, monitorStop,
  } = useBotSocket();

  const [selectedAccount, setSelectedAccount] = useState<string | null>(null);
  const [apiAlive, setApiAlive] = useState<boolean | null>(null);
  const [targetSku, setTargetSku] = useState("");
  const [targetSize, setTargetSize] = useState("");
  const [logFilter, setLogFilter] = useState<"all" | "ok" | "err" | "warn">("all");
  const [monitorInterval, setMonitorInterval] = useState(15);
  const logEndRef = useRef<HTMLDivElement>(null);

  // health check cada 10s
  useEffect(() => {
    checkBotApi().then(setApiAlive);
    const iv = setInterval(() => checkBotApi().then(setApiAlive), 10000);
    return () => clearInterval(iv);
  }, []);

  // auto-select primera cuenta
  useEffect(() => {
    if (!selectedAccount && accounts.length > 0) setSelectedAccount(accounts[0].name);
  }, [accounts, selectedAccount]);

  // auto-scroll logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs, selectedAccount]);

  // cargar SKU guardado al seleccionar
  useEffect(() => {
    const skus = getSavedSkus();
    if (skus.length > 0 && !targetSku) setTargetSku(skus[0]);
  }, [targetSku]);

  // ── Derivados ──
  const savedSkus = getSavedSkus();
  const isRunning = accounts.some(a => ["running", "playing", "starting", "monitoring", "carting", "checkout", "paying"].includes(a.state));
  const selectedAcc = accounts.find(a => a.name === selectedAccount);
  const selectedLogs = selectedAccount ? (logs[selectedAccount] || []) : [];
  const filteredLogs = logFilter === "all" ? selectedLogs : selectedLogs.filter(l => {
    if (logFilter === "ok") return l.msg.includes("✅") || l.msg.includes("🔥");
    if (logFilter === "err") return l.msg.includes("❌");
    if (logFilter === "warn") return l.msg.includes("⚠");
    return true;
  });

  const stats = {
    total: accounts.length,
    auth: accounts.filter(a => a.login_ok).length,
    active: accounts.filter(a => ["running", "playing", "starting", "carting", "checkout", "paying"].includes(a.state)).length,
    done: accounts.filter(a => ["done", "success"].includes(a.state)).length,
    failed: accounts.filter(a => a.state === "failed" || a.state === "error").length,
  };

  const handlePlayAll = () => {
    if (isRunning) {
      stopAll();
    } else {
      playAll(targetSku || undefined);
    }
  };

  const handlePlaySingle = (acc: BotAccount) => {
    play(acc.name, targetSku || undefined);
  };

  const handleMonitorToggle = () => {
    if (monitorStatus?.running) {
      monitorStop();
    } else {
      const skus = targetSku ? [targetSku] : savedSkus.length > 0 ? savedSkus : undefined;
      monitorStart(skus, monitorInterval);
    }
  };

  // ── Estilos reutilizables ──
  const btnBase = {
    border: "none", borderRadius: 6, fontWeight: 700 as const,
    fontSize: 11, cursor: "pointer" as const, transition: "all 0.15s",
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", background: t.bg }}>

      {/* ═══════════════ TOP BAR ═══════════════ */}
      <div style={{
        padding: "10px 20px", borderBottom: `1px solid ${t.border}`,
        display: "flex", alignItems: "center", gap: 12, background: t.panel,
        flexShrink: 0,
      }}>
        {/* Titulo + estado */}
        <span style={{ color: t.text, fontSize: 15, fontWeight: 800, letterSpacing: 0.5, marginRight: 4 }}>
          DROP
        </span>

        <span style={{
          display: "inline-flex", alignItems: "center", gap: 4,
          background: connected ? "#00e67612" : "#ff174412",
          border: `1px solid ${connected ? "#00e67630" : "#ff174430"}`,
          borderRadius: 10, padding: "2px 8px",
          color: connected ? "#00e676" : "#ff1744",
          fontSize: 9, fontWeight: 700,
        }}>
          <span style={{
            width: 5, height: 5, borderRadius: "50%",
            background: connected ? "#00e676" : "#ff1744",
          }} />
          {connected ? "ONLINE" : apiAlive === false ? "OFFLINE" : "..."}
        </span>

        {/* Stats pills */}
        <div style={{ display: "flex", gap: 6, marginLeft: 4 }}>
          {[
            { label: "AUTH", val: `${stats.auth}/${stats.total}`, color: t.textMed },
            { label: "ACTIVAS", val: stats.active, color: stats.active > 0 ? "#ffd600" : t.textDim },
            { label: "OK", val: stats.done, color: stats.done > 0 ? t.green : t.textDim },
            { label: "FAIL", val: stats.failed, color: stats.failed > 0 ? t.red : t.textDim },
          ].map(s => (
            <span key={s.label} style={{
              background: t.row, border: `1px solid ${t.border}`,
              borderRadius: 8, padding: "2px 8px",
              fontSize: 9, fontWeight: 600, color: s.color,
              display: "inline-flex", alignItems: "center", gap: 3,
            }}>
              <span style={{ color: t.textDim, fontSize: 8 }}>{s.label}</span> {s.val}
            </span>
          ))}
        </div>

        <div style={{ flex: 1 }} />

        {/* SKU target + Size */}
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ color: t.textDim, fontSize: 9, fontWeight: 700 }}>SKU</span>
          {savedSkus.length > 0 ? (
            <select
              value={targetSku}
              onChange={e => setTargetSku(e.target.value)}
              style={{
                background: t.row, border: `1px solid ${t.border}`,
                borderRadius: 6, padding: "5px 8px", color: t.green,
                fontSize: 11, fontFamily: "Consolas, monospace",
                outline: "none", minWidth: 100,
              }}
            >
              <option value="">— seleccionar —</option>
              {savedSkus.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          ) : (
            <input
              value={targetSku}
              onChange={e => setTargetSku(e.target.value)}
              placeholder="ej: 134427"
              style={{
                background: t.row, border: `1px solid ${t.border}`,
                borderRadius: 6, padding: "5px 8px", color: t.green,
                fontSize: 11, fontFamily: "Consolas, monospace",
                outline: "none", width: 90,
              }}
            />
          )}
          <span style={{ color: t.textDim, fontSize: 9, fontWeight: 700 }}>TALLA</span>
          <input
            value={targetSize}
            onChange={e => setTargetSize(e.target.value)}
            placeholder="8.5"
            style={{
              background: t.row, border: `1px solid ${t.border}`,
              borderRadius: 6, padding: "5px 8px", color: t.text,
              fontSize: 11, fontFamily: "Consolas, monospace",
              outline: "none", width: 50,
            }}
          />
        </div>

        {/* Botones acción */}
        <div style={{ display: "flex", gap: 6 }}>
          <button onClick={handleMonitorToggle} disabled={!connected} style={{
            ...btnBase,
            background: monitorStatus?.running ? `${t.blue}18` : t.row,
            border: `1px solid ${monitorStatus?.running ? t.blue : t.border}`,
            color: monitorStatus?.running ? t.blue : t.textMed,
            padding: "6px 10px",
            opacity: connected ? 1 : 0.4,
          }}>
            {monitorStatus?.running ? `● MON ${monitorStatus.checks}` : "○ MON"}
          </button>

          <button onClick={() => refreshAccounts()} style={{
            ...btnBase, background: t.row, border: `1px solid ${t.border}`,
            color: t.textMed, padding: "6px 10px",
          }}>↻</button>

          <button onClick={handlePlayAll} disabled={!connected} style={{
            ...btnBase,
            background: isRunning ? t.redDim : t.greenDim,
            border: `1px solid ${isRunning ? t.red : t.green}`,
            color: isRunning ? t.red : t.green,
            padding: "6px 16px", fontSize: 12,
            opacity: connected ? 1 : 0.4,
          }}>
            {isRunning ? "■ STOP ALL" : "▶ LAUNCH"}
          </button>
        </div>
      </div>

      {/* ═══════════════ STOCK ALERT ═══════════════ */}
      {lastStockEvent && (
        <div style={{
          padding: "6px 20px", display: "flex", alignItems: "center", gap: 10,
          background: "#ffd60008", borderBottom: `1px solid #ffd60020`,
          flexShrink: 0,
        }}>
          <span style={{ color: "#ffd600", fontSize: 11, fontWeight: 800 }}>STOCK</span>
          <span style={{ color: t.text, fontSize: 11 }}>{lastStockEvent.name}</span>
          <span style={{ color: t.green, fontSize: 11, fontFamily: "Consolas" }}>{lastStockEvent.sku}</span>
          <span style={{ color: t.textMed, fontSize: 11 }}>
            {lastStockEvent.quantity} uds — ${lastStockEvent.price?.toLocaleString()}
          </span>
          <span style={{ color: t.textDim, fontSize: 10, marginLeft: "auto" }}>{lastStockEvent.timestamp}</span>
        </div>
      )}

      {/* ═══════════════ MAIN CONTENT: 2 columns ═══════════════ */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>

        {/* ── LEFT: Accounts table ── */}
        <div style={{
          flex: 1, display: "flex", flexDirection: "column",
          borderRight: `1px solid ${t.border}`, minWidth: 0,
        }}>

          {/* Table header */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "32px 1fr 70px 70px 90px 60px",
            gap: 4, padding: "8px 16px",
            borderBottom: `1px solid ${t.border}`, background: t.panel, flexShrink: 0,
          }}>
            {["#", "CUENTA", "MÉTODO", "SKU", "ESTADO", ""].map((h, i) => (
              <span key={i} style={{
                color: t.textDim, fontSize: 9, fontWeight: 700,
                letterSpacing: 0.6,
              }}>{h}</span>
            ))}
          </div>

          {/* Table body */}
          <div style={{ flex: 1, overflowY: "auto" }}>
            {!connected && accounts.length === 0 ? (
              <div style={{
                display: "flex", flexDirection: "column", alignItems: "center",
                justifyContent: "center", height: "100%", gap: 10,
              }}>
                <span style={{ fontSize: 28, opacity: 0.6 }}>⚡</span>
                <span style={{ color: t.textDim, fontSize: 12 }}>Sin conexión al bot</span>
                <code style={{ color: t.green, fontSize: 11 }}>python bot_api.py</code>
              </div>
            ) : accounts.map((acc, i) => {
              const active = ["running", "playing", "starting", "monitoring", "carting", "checkout", "paying"].includes(acc.state);
              const selected = selectedAccount === acc.name;

              return (
                <div
                  key={acc.name}
                  onClick={() => setSelectedAccount(acc.name)}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "32px 1fr 70px 70px 90px 60px",
                    gap: 4, padding: "8px 16px",
                    borderBottom: `1px solid ${t.border}08`,
                    background: selected ? `${t.green}08` : "transparent",
                    borderLeft: selected ? `2px solid ${t.green}` : "2px solid transparent",
                    cursor: "pointer", alignItems: "center",
                    transition: "background 0.1s",
                  }}
                  onMouseEnter={e => { if (!selected) (e.currentTarget.style.background = t.row); }}
                  onMouseLeave={e => { if (!selected) (e.currentTarget.style.background = "transparent"); }}
                >
                  <span style={{ color: t.textDim, fontSize: 10 }}>{i + 1}</span>

                  <div style={{ display: "flex", flexDirection: "column", minWidth: 0 }}>
                    <span style={{
                      color: t.text, fontSize: 11, fontWeight: 600,
                      overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                    }}>{acc.name}</span>
                    {acc.display_name && acc.display_name !== acc.name && (
                      <span style={{ color: t.textDim, fontSize: 9 }}>{acc.display_name}</span>
                    )}
                  </div>

                  <span style={{ color: t.textMed, fontSize: 10 }}>
                    {METODOS[acc.payment_mode] || acc.payment_mode || "—"}
                  </span>

                  <span style={{ color: t.green, fontSize: 10, fontFamily: "Consolas" }}>
                    {acc.sku || "—"}
                  </span>

                  <StateBadge state={acc.state} />

                  <div style={{ display: "flex", gap: 4 }} onClick={e => e.stopPropagation()}>
                    {active ? (
                      <button onClick={() => stop(acc.name)} style={{
                        ...btnBase, background: t.redDim, border: `1px solid ${t.red}40`,
                        color: t.red, padding: "4px 8px",
                      }}>■</button>
                    ) : (
                      <button
                        onClick={() => handlePlaySingle(acc)}
                        disabled={!acc.login_ok || !connected}
                        style={{
                          ...btnBase,
                          background: acc.login_ok ? t.greenDim : t.row,
                          border: `1px solid ${acc.login_ok ? `${t.green}40` : t.border}`,
                          color: acc.login_ok ? t.green : t.textDim,
                          padding: "4px 8px",
                          opacity: acc.login_ok ? 1 : 0.4,
                          cursor: acc.login_ok && connected ? "pointer" : "not-allowed",
                        }}
                      >▶</button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Bottom summary */}
          <div style={{
            padding: "6px 16px", borderTop: `1px solid ${t.border}`,
            display: "flex", alignItems: "center", gap: 10,
            background: t.panel, flexShrink: 0, fontSize: 10,
          }}>
            {targetSku && (
              <span style={{ color: t.green, fontFamily: "Consolas" }}>
                Target: {targetSku}{targetSize ? ` / ${targetSize}` : ""}
              </span>
            )}
            {monitorStatus?.running && (
              <span style={{ color: t.blue }}>
                Monitor: {monitorStatus.skus?.join(", ")} cada {monitorStatus.interval}s
              </span>
            )}
            {!targetSku && !monitorStatus?.running && (
              <span style={{ color: t.textDim }}>
                Selecciona un SKU arriba o guárdalos desde la pestaña SKUs
              </span>
            )}
          </div>
        </div>

        {/* ── RIGHT: Logs + Monitor ── */}
        <div style={{
          width: 420, display: "flex", flexDirection: "column",
          background: t.panel, minWidth: 320,
        }}>

          {/* Log header */}
          <div style={{
            padding: "8px 14px", borderBottom: `1px solid ${t.border}`,
            display: "flex", alignItems: "center", gap: 8, flexShrink: 0,
          }}>
            {selectedAcc ? (
              <>
                <span style={{
                  width: 6, height: 6, borderRadius: "50%",
                  background: STATE_COLORS[selectedAcc.state] || "#888",
                }} />
                <span style={{ color: t.text, fontSize: 11, fontWeight: 700 }}>
                  {selectedAccount}
                </span>
                <StateBadge state={selectedAcc.state} />
                <span style={{ color: t.textDim, fontSize: 9, marginLeft: "auto" }}>
                  {filteredLogs.length} logs
                </span>
              </>
            ) : (
              <span style={{ color: t.textDim, fontSize: 11 }}>
                Selecciona una cuenta para ver logs
              </span>
            )}
          </div>

          {/* Log filters */}
          {selectedAccount && (
            <div style={{
              padding: "5px 14px", borderBottom: `1px solid ${t.border}`,
              display: "flex", gap: 4, flexShrink: 0,
            }}>
              {([
                { key: "all", label: "Todo" },
                { key: "ok", label: "OK" },
                { key: "err", label: "Error" },
                { key: "warn", label: "Warn" },
              ] as const).map(f => (
                <button key={f.key} onClick={() => setLogFilter(f.key)} style={{
                  ...btnBase,
                  background: logFilter === f.key ? `${t.green}15` : "transparent",
                  border: logFilter === f.key ? `1px solid ${t.green}30` : `1px solid transparent`,
                  color: logFilter === f.key ? t.green : t.textDim,
                  padding: "2px 8px", fontSize: 9,
                }}>
                  {f.label}
                </button>
              ))}
            </div>
          )}

          {/* Log body */}
          <div style={{
            flex: 1, overflowY: "auto", padding: "8px 14px",
            display: "flex", flexDirection: "column", gap: 1,
          }}>
            {!selectedAccount ? (
              <div style={{
                flex: 1, display: "flex", flexDirection: "column",
                alignItems: "center", justifyContent: "center", gap: 8,
              }}>
                <span style={{ fontSize: 24, opacity: 0.4 }}>📋</span>
                <span style={{ color: t.textDim, fontSize: 11 }}>
                  Click en una cuenta para ver logs
                </span>
              </div>
            ) : filteredLogs.length === 0 ? (
              <div style={{
                flex: 1, display: "flex", alignItems: "center",
                justifyContent: "center", color: t.textDim, fontSize: 11,
              }}>
                Sin actividad
              </div>
            ) : (
              <>
                {filteredLogs.map((log, i) => (
                  <div key={i} style={{
                    display: "flex", gap: 8, padding: "2px 0",
                    borderBottom: `1px solid ${t.border}08`,
                  }}>
                    <span style={{
                      color: t.textDim, fontSize: 10, fontFamily: "Consolas",
                      minWidth: 55, flexShrink: 0,
                    }}>{log.time}</span>
                    <span style={{
                      color: log.color, fontSize: 11, fontFamily: "Consolas",
                      wordBreak: "break-word",
                    }}>{log.msg}</span>
                  </div>
                ))}
                <div ref={logEndRef} />
              </>
            )}
          </div>

          {/* ── Monitor mini panel ── */}
          {monitorStatus?.running && (
            <div style={{
              borderTop: `1px solid ${t.blue}30`,
              padding: "8px 14px", flexShrink: 0,
              background: `${t.blue}08`,
            }}>
              <div style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                marginBottom: monitorLogs.length > 0 ? 6 : 0,
              }}>
                <span style={{ color: t.blue, fontSize: 10, fontWeight: 700 }}>
                  MONITOR — {monitorStatus.checks} checks
                </span>
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span style={{ color: t.textDim, fontSize: 9 }}>
                    cada {monitorStatus.interval}s
                  </span>
                  <button onClick={() => monitorStop()} style={{
                    ...btnBase, background: t.redDim, color: t.red,
                    border: `1px solid ${t.red}40`, padding: "2px 8px",
                  }}>■</button>
                </div>
              </div>
              {monitorLogs.length > 0 && (
                <div style={{
                  maxHeight: 80, overflowY: "auto",
                  display: "flex", flexDirection: "column", gap: 1,
                }}>
                  {monitorLogs.slice(0, 15).map((log, i) => (
                    <div key={i} style={{ display: "flex", gap: 8 }}>
                      <span style={{ color: t.textDim, fontSize: 9, fontFamily: "Consolas", minWidth: 50 }}>
                        {log.time}
                      </span>
                      <span style={{ color: t.blue, fontSize: 9, fontFamily: "Consolas" }}>{log.msg}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Monitor config when NOT running */}
          {!monitorStatus?.running && connected && (
            <div style={{
              borderTop: `1px solid ${t.border}`,
              padding: "8px 14px", display: "flex", alignItems: "center", gap: 8,
              flexShrink: 0,
            }}>
              <span style={{ color: t.textDim, fontSize: 9, fontWeight: 700 }}>MONITOR</span>
              <span style={{ color: t.textDim, fontSize: 9 }}>cada</span>
              <input
                type="number" min={5} max={120}
                value={monitorInterval}
                onChange={e => setMonitorInterval(Number(e.target.value) || 15)}
                style={{
                  background: t.row, border: `1px solid ${t.border}`,
                  borderRadius: 4, padding: "3px 6px", color: t.text,
                  fontSize: 10, width: 40, outline: "none",
                  fontFamily: "Consolas",
                }}
              />
              <span style={{ color: t.textDim, fontSize: 9 }}>seg</span>
              <button onClick={handleMonitorToggle} style={{
                ...btnBase, background: t.greenDim,
                border: `1px solid ${t.green}40`, color: t.green,
                padding: "3px 10px", marginLeft: "auto",
              }}>
                ▶ Iniciar
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
