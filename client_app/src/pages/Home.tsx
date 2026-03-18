import { UserSession } from "../types";
import { T, PLAN_COLORS } from "../theme";

export function Home({ t, session }: { t: T; session: UserSession }) {
  const pc = PLAN_COLORS[session.plan];
  return (
    <div style={{ padding: 28 }}>
      <h2 style={{ color: t.text, fontSize: 20, fontWeight: 700, marginBottom: 6 }}>AODA</h2>
      <p style={{ color: t.textDim, fontSize: 13, marginBottom: 28 }}>Todo bajo control.</p>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 28 }}>
        {[
          { label: "Cuentas activas", value: "7",                          color: t.green   },
          { label: "Drops ganados",   value: "3",                          color: t.blue    },
          { label: "Plan actual",     value: session.plan.toUpperCase(),   color: pc        },
          { label: "Token expira",    value: session.expires,              color: t.textMed },
        ].map((s, i) => (
          <div key={i} style={{ background: t.panel, border: `1px solid ${t.border}`, borderRadius: 12, padding: "18px 20px" }}>
            <p style={{ color: t.textDim, fontSize: 11, marginBottom: 6 }}>{s.label}</p>
            <p style={{ color: s.color, fontSize: 20, fontWeight: 700 }}>{s.value}</p>
          </div>
        ))}
      </div>
      <p style={{ color: t.textMed, fontSize: 12, fontWeight: 600, marginBottom: 12, letterSpacing: 1 }}>ACCIONES RAPIDAS</p>
      <div style={{ display: "flex", gap: 12 }}>
        {[
          { label: "Buscar SKU",      color: t.blue    },
          { label: "Lanzar Drop",     color: t.green   },
          { label: "Limpiar Carrito", color: t.textMed },
        ].map((btn, i) => (
          <button key={i} style={{ background: t.row, border: `1px solid ${t.border}`, borderRadius: 8, padding: "10px 16px", color: btn.color, fontSize: 13, cursor: "pointer", fontWeight: 500 }}>
            {btn.label}
          </button>
        ))}
      </div>
    </div>
  );
}