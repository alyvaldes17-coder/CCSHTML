export const THEMES = {
  dark: {
    bg: "#0a0a0a", panel: "#111111", row: "#161616", border: "#2a2a2a",
    text: "#e8e8e8", textDim: "#555555", textMed: "#888888",
    green: "#00e676", greenDim: "#0d2e1a", red: "#ff1744", redDim: "#2e0010",
    blue: "#2979ff", sidebar: "#0d0d0d",
  },
  light: {
    bg: "#f4f4f4", panel: "#ffffff", row: "#f0f0f0", border: "#e0e0e0",
    text: "#111111", textDim: "#aaaaaa", textMed: "#666666",
    green: "#00a854", greenDim: "#e6f7ef", red: "#d32f2f", redDim: "#fce4ec",
    blue: "#1565c0", sidebar: "#fafafa",
  },
};

export type T = typeof THEMES.dark;

export const PLAN_COLORS = {
  starter: "#2979ff",
  pro:     "#ffd600",
  elite:   "#00e676",
};