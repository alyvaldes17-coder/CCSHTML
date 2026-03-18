import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { UserSession, Theme } from "../types";
import { THEMES } from "../theme";
import { apiValidateToken, loadSession, isSessionVerified, validateTokenOffline } from "../services/api";
import { SnakeLogo } from "../components/SnakeLogo";
import { Toast } from "../components/Toast";

interface LoginProps {
  onLogin: (s: UserSession) => void;
  theme: Theme;
  toggleTheme: () => void;
}

export function Login({ onLogin, theme, toggleTheme }: LoginProps) {
  const t = THEMES[theme];
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const handleValidate = async () => {
    if (!token.trim()) { setToast({ message: "Ingresa tu token", type: "error" }); return; }
    setLoading(true);
    try {
      const hwid = await invoke<string>("get_hwid");
      console.log("HWID:", hwid);
      const session = await apiValidateToken(token.trim());
      setToast({ message: `Bienvenido — Plan ${session.plan.toUpperCase()}`, type: "success" });
      setTimeout(() => onLogin(session), 700);
    } catch {
      // Railway caído → solo aceptar si ESTE MISMO token ya fue validado antes
      const stored = await loadSession();
      const verified = await isSessionVerified();
      if (verified && stored && stored.token === token.trim()) {
        const offline = validateTokenOffline(token.trim());
        if (offline) {
          setToast({ message: `Validado offline — Plan ${offline.plan.toUpperCase()}`, type: "success" });
          setTimeout(() => onLogin(offline), 700);
          return;
        }
      }
      setToast({ message: "Sin conexión al servidor — intenta de nuevo", type: "error" });
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: t.bg, display: "flex", alignItems: "center", justifyContent: "center", position: "relative" }}>
      <button onClick={toggleTheme} style={{ position: "absolute", top: 20, right: 20, background: t.panel, border: `1px solid ${t.border}`, borderRadius: 8, padding: "6px 14px", cursor: "pointer", color: t.textMed, fontSize: 13 }}>
        {theme === "dark" ? "Light" : "Dark"}
      </button>
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} t={t} />}

      <div style={{ background: t.panel, border: `1px solid ${t.border}`, borderRadius: 16, padding: "24px 40px 40px 40px", width: 380, display: "flex", flexDirection: "column", gap: 20, boxShadow: "0 20px 60px rgba(0,0,0,0.3)" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ display: "flex", justifyContent: "center", marginBottom: 8 }}>
            <SnakeLogo size={120} />
          </div>
          <h1 style={{ color: t.green, fontSize: 28, fontWeight: 800, letterSpacing: 6 }}>AODA</h1>
          <p style={{ color: t.textDim, fontSize: 12, marginTop: 4 }}>Nike Bot Pro — Ingresa tu token</p>
        </div>
        <input
          type="text" placeholder="eyJ0eXAiOiJKV1Qi..." value={token}
          onChange={e => setToken(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !loading && handleValidate()}
          style={{ background: t.row, border: `1px solid ${t.border}`, borderRadius: 8, padding: "12px 16px", color: t.text, fontSize: 13, outline: "none", fontFamily: "Consolas, monospace" }}
        />
        <button onClick={handleValidate} disabled={loading} style={{
          background: loading ? t.greenDim : t.green,
          color: loading ? t.green : "#000", border: "none", borderRadius: 8,
          padding: "13px 0", fontSize: 14, fontWeight: 700,
          cursor: loading ? "not-allowed" : "pointer",
          transition: "background 0.2s ease",
        }}>
          {loading ? "Validando..." : "INGRESAR"}
        </button>
        <p style={{ color: t.textDim, fontSize: 11, textAlign: "center" }}>
          Sin acceso? <span style={{ color: t.textMed, cursor: "pointer" }}>Contactanos</span>
        </p>
      </div>
    </div>
  );
}