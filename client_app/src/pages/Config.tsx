import { UserSession, Theme } from "../types";
import { T, PLAN_COLORS } from "../theme";

interface ConfigProps {
  t: T; theme: Theme; toggleTheme: () => void;
  session: UserSession; onLogout: () => void;
}

export function Config({ t, theme, toggleTheme, session, onLogout }: ConfigProps) {
  const pc = PLAN_COLORS[session.plan];
  return (
    <div style={{ padding: 28, maxWidth: 480 }}>
      <h2 style={{ color: t.text, fontSize: 20, fontWeight: 700, marginBottom: 24 }}>Configuracion</h2>
      <div style={{ background: t.panel, border: `1px solid ${pc}`, borderRadius: 12, padding: "18px 20px", marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <p style={{ color: t.textDim, fontSize: 11, marginBottom: 4 }}>Plan activo</p>
            <p style={{ color: pc, fontSize: 18, fontWeight: 700, textTransform: "uppercase" }}>{session.plan}</p>
            <p style={{ color: t.textDim, fontSize: 11, marginTop: 4 }}>{session.max_accounts} cuentas · Expira {session.expires}</p>
          </div>
          <button style={{ background: t.row, border: `1px solid ${t.border}`, color: t.textMed, borderRadius: 8, padding: "8px 14px", fontSize: 12, cursor: "pointer" }}>Renovar</button>
        </div>
      </div>
      <div style={{ background: t.panel, border: `1px solid ${t.border}`, borderRadius: 12, padding: "16px 20px", marginBottom: 16, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <p style={{ color: t.text, fontSize: 13, fontWeight: 500 }}>Tema</p>
          <p style={{ color: t.textDim, fontSize: 11 }}>{theme === "dark" ? "Modo oscuro" : "Modo claro"}</p>
        </div>
        <button onClick={toggleTheme} style={{ background: t.row, border: `1px solid ${t.border}`, borderRadius: 8, padding: "8px 16px", color: t.text, fontSize: 13, cursor: "pointer" }}>
          {theme === "dark" ? "Light" : "Dark"}
        </button>
      </div>
      <div style={{ background: t.panel, border: `1px solid ${t.border}`, borderRadius: 12, padding: "16px 20px", marginBottom: 16 }}>
        <p style={{ color: t.text, fontSize: 13, fontWeight: 500, marginBottom: 8 }}>Token</p>
        <div style={{ display: "flex", gap: 8 }}>
          <input readOnly value={session.token} style={{ flex: 1, background: t.row, border: `1px solid ${t.border}`, borderRadius: 6, padding: "8px 12px", color: t.textMed, fontSize: 12, fontFamily: "Consolas", outline: "none" }} />
          <button style={{ background: t.row, border: `1px solid ${t.border}`, color: t.textMed, borderRadius: 6, padding: "8px 12px", fontSize: 12, cursor: "pointer" }}>Copiar</button>
        </div>
      </div>
      <button onClick={onLogout} style={{ width: "100%", background: t.redDim, border: `1px solid ${t.red}`, color: t.red, borderRadius: 10, padding: "12px 0", fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
        Cerrar sesion
      </button>
    </div>
  );
}