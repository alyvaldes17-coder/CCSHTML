import { UserSession } from "../types";
import { T } from "../theme";

export function Wallet({ t, session }: { t: T; session: UserSession }) {
  const accounts = Array.from({ length: session.max_accounts }, (_, i) => ({
    id: i + 1,
    name: `cuenta${i + 1}`,
    email: i < 7 ? `cuenta${i + 1}@gmail.com` : null,
    status: i < 7 ? "READY" : "NO_AUTH",
    sku: i < 5 ? "190765" : null,
  }));

  return (
    <div style={{ padding: 28 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
        <h2 style={{ color: t.text, fontSize: 20, fontWeight: 700 }}>Wallet</h2>
        <button style={{ background: t.greenDim, border: `1px solid ${t.green}`, color: t.green, borderRadius: 8, padding: "8px 16px", fontSize: 12, fontWeight: 600, cursor: "pointer" }}>+ Agregar cuenta</button>
      </div>
      <div style={{ background: t.panel, border: `1px solid ${t.border}`, borderRadius: 12, overflow: "hidden" }}>
        <div style={{ padding: "10px 20px", borderBottom: `1px solid ${t.border}`, display: "grid", gridTemplateColumns: "20px 1fr 1fr 80px 100px", gap: 12 }}>
          {["", "Cuenta", "Email", "SKU", "Acciones"].map((h, i) => (
            <span key={i} style={{ color: t.textDim, fontSize: 11, fontWeight: 600 }}>{h}</span>
          ))}
        </div>
        {accounts.map(acc => (
          <div key={acc.id} style={{ padding: "12px 20px", borderBottom: `1px solid ${t.row}`, display: "grid", gridTemplateColumns: "20px 1fr 1fr 80px 100px", gap: 12, alignItems: "center" }}>
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: acc.status === "READY" ? t.green : t.red }} />
            <span style={{ color: t.text, fontSize: 13 }}>{acc.name}</span>
            <span style={{ color: t.textMed, fontSize: 12 }}>{acc.email || "Sin sesion"}</span>
            <span style={{ color: acc.sku ? t.green : t.textDim, fontSize: 12, fontFamily: "Consolas" }}>{acc.sku || "—"}</span>
            <div style={{ display: "flex", gap: 6 }}>
              <button style={{ background: t.row, border: `1px solid ${t.border}`, color: t.textMed, borderRadius: 5, padding: "3px 8px", fontSize: 11, cursor: "pointer" }}>Editar</button>
              <button style={{ background: t.row, border: `1px solid ${t.border}`, color: t.red, borderRadius: 5, padding: "3px 8px", fontSize: 11, cursor: "pointer" }}>X</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}