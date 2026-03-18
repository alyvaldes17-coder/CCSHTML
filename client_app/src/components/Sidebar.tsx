import { Section, UserSession } from "../types";
import { T, PLAN_COLORS } from "../theme";
import { SnakeLogo } from "./SnakeLogo";

const NAV: { id: Section; label: string }[] = [
  { id: "home",   label: "Home"   },
  { id: "skus",   label: "SKUs"   },
  { id: "drop",   label: "Drop"   },
  { id: "wallet", label: "Wallet" },
  { id: "config", label: "Config" },
];

const NAV_ICONS: Record<Section, string> = {
  home:   "⌂",
  skus:   "◈",
  drop:   "▸",
  wallet: "◉",
  config: "◎",
};

interface SidebarProps {
  section: Section;
  setSection: (s: Section) => void;
  t: T;
  session: UserSession;
}

export function Sidebar({ section, setSection, t, session }: SidebarProps) {
  const pc = PLAN_COLORS[session.plan];
  return (
    <div style={{
      width: 72, background: t.sidebar, borderRight: `1px solid ${t.border}`,
      display: "flex", flexDirection: "column", alignItems: "center",
      padding: "16px 0", gap: 4, flexShrink: 0,
    }}>
      <div style={{ marginBottom: 16 }}><SnakeLogo size={36} /></div>
      {NAV.map(item => (
        <button
          key={item.id}
          onClick={() => setSection(item.id)}
          title={item.label}
          style={{
            width: 48, height: 48, borderRadius: 12,
            background: section === item.id ? t.greenDim : "transparent",
            border: section === item.id ? `1px solid ${t.green}` : "1px solid transparent",
            cursor: "pointer", fontSize: 18, color: section === item.id ? t.green : t.textMed,
            display: "flex", alignItems: "center", justifyContent: "center",
          }}
        >
          {NAV_ICONS[item.id]}
        </button>
      ))}
      <div style={{ marginTop: "auto" }}>
        <div style={{
          width: 36, height: 36, borderRadius: "50%",
          background: t.row, border: `2px solid ${pc}`,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 10, color: pc, fontWeight: 700, textTransform: "uppercase",
        }}>
          {session.plan[0]}
        </div>
      </div>
    </div>
  );
}