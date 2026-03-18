import { T } from "../theme";

interface ToastProps {
  message: string;
  type: "success" | "error";
  onClose: () => void;
  t: T;
}

export function Toast({ message, type, onClose, t }: ToastProps) {
  return (
    <div style={{
      position: "fixed", top: 20, right: 20, zIndex: 9999,
      background: type === "success" ? t.greenDim : t.redDim,
      border: `1px solid ${type === "success" ? t.green : t.red}`,
      borderRadius: 10, padding: "12px 18px",
      display: "flex", alignItems: "center", gap: 10, minWidth: 240,
      boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
    }}>
      <span style={{ color: type === "success" ? t.green : t.red, fontSize: 13, fontWeight: 500 }}>
        {type === "success" ? "✓" : "✗"} {message}
      </span>
      <button onClick={onClose} style={{ marginLeft: "auto", background: "none", border: "none", color: t.textDim, cursor: "pointer", fontSize: 16 }}>✕</button>
    </div>
  );
}