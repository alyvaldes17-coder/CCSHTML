import { useEffect, useState } from "react";
import { Page, Section, Theme, UserSession } from "./types";
import { THEMES } from "./theme";
import { Sidebar } from "./components/Sidebar";
import { Login } from "./pages/Login";
import { Home } from "./pages/Home";
import { SKUs } from "./pages/Skus";
import { Drop } from "./pages/Drop";
import { Wallet } from "./pages/Wallet";
import { Config } from "./pages/Config";
import {
  saveSession, loadSession, clearSession,
  apiValidateToken, validateTokenOffline, apiRevoke, isSessionVerified,
} from "./services/api";

export default function App() {
  const [page, setPage]       = useState<Page>("login");
  const [section, setSection] = useState<Section>("home");
  const [session, setSession] = useState<UserSession | null>(null);
  const [theme, setTheme]     = useState<Theme>("dark");
  const [booting, setBooting] = useState(true);

  const t           = THEMES[theme];
  const toggleTheme = () => setTheme(p => p === "dark" ? "light" : "dark");

  /* ── Auto-restore sesión guardada ── */
  useEffect(() => {
    (async () => {
      const stored = await loadSession();
      if (!stored) { setBooting(false); return; }

      try {
        const fresh = await apiValidateToken(stored.token);
        setSession(fresh);
        await saveSession(fresh, true);
        setPage("app");
      } catch {
        const verified = await isSessionVerified();
        if (verified) {
          const offline = validateTokenOffline(stored.token);
          if (offline) {
            setSession(offline);
            setPage("app");
          } else {
            await clearSession();
          }
        } else {
          await clearSession();
        }
      } finally {
        setBooting(false);
      }
    })();
  }, []);

  /* ── Login handler ── */
  const handleLogin = (s: UserSession) => {
    setSession(s);
    saveSession(s, true);
    setPage("app");
  };

  /* ── Logout handler ── */
  const handleLogout = () => {
    if (session) apiRevoke(session.token).catch(() => {});
    clearSession();
    setSession(null);
    setPage("login");
    setSection("home");
  };

  /* ── Loading splash ── */
  if (booting) {
    return (
      <div style={{ height: "100vh", background: t.bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <span style={{ color: t.green, fontSize: 14, fontWeight: 600 }}>Cargando...</span>
      </div>
    );
  }

  if (page === "login" || !session) {
    return (
      <Login
        onLogin={handleLogin}
        theme={theme}
        toggleTheme={toggleTheme}
      />
    );
  }

  const renderSection = () => {
    switch (section) {
      case "home":   return <Home   t={t} session={session} />;
      case "skus":   return <SKUs   t={t} />;
      case "drop":   return <Drop   t={t} />;
      case "wallet": return <Wallet t={t} session={session} />;
      case "config": return <Config t={t} theme={theme} toggleTheme={toggleTheme} session={session} onLogout={handleLogout} />;
    }
  };

  return (
    <div style={{ height: "100vh", background: t.bg, display: "flex", overflow: "hidden" }}>
      <Sidebar section={section} setSection={setSection} t={t} session={session} />
      <div style={{ flex: 1, overflowY: "auto" }}>{renderSection()}</div>
    </div>
  );
}