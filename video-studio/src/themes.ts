export interface GenreTheme {
  accent: string;      // primary accent color (hex)
  secondary: string;   // secondary/bg color
  glow: string;        // accent with alpha for glow effects
  textShadow: string;  // CSS text-shadow for accent text
  logoStyle: "vhs" | "neon" | "gold" | "distressed" | "minimal";
  era: string;         // display label e.g. "שנות ה-80"
}

export const GENRE_THEMES: Record<string, GenreTheme> = {
  jazz: {
    accent: "#C8A84B", secondary: "#0D1A2E",
    glow: "rgba(200,168,75,0.45)", textShadow: "0 0 20px rgba(200,168,75,0.6)",
    logoStyle: "gold", era: "שנות ה-40–50",
  },
  blues: {
    accent: "#4A90D9", secondary: "#0A0A14",
    glow: "rgba(74,144,217,0.4)", textShadow: "0 0 18px rgba(74,144,217,0.6)",
    logoStyle: "minimal", era: "שנות ה-50–60",
  },
  rock: {
    accent: "#CC2200", secondary: "#0A0A0A",
    glow: "rgba(204,34,0,0.5)", textShadow: "0 0 24px rgba(204,34,0,0.7)",
    logoStyle: "distressed", era: "שנות ה-60–70",
  },
  funk: {
    accent: "#F5A800", secondary: "#140800",
    glow: "rgba(245,168,0,0.5)", textShadow: "0 0 20px rgba(245,168,0,0.65)",
    logoStyle: "vhs", era: "שנות ה-70–80",
  },
  disco: {
    accent: "#FFD700", secondary: "#0E0520",
    glow: "rgba(255,215,0,0.55)", textShadow: "0 0 28px rgba(255,215,0,0.8)",
    logoStyle: "gold", era: "שנות ה-70",
  },
  pop_80s: {
    accent: "#FF69B4", secondary: "#0D0025",
    glow: "rgba(255,105,180,0.55)", textShadow: "0 0 28px rgba(255,105,180,0.8)",
    logoStyle: "neon", era: "שנות ה-80",
  },
  synth: {
    accent: "#00FFD0", secondary: "#00050F",
    glow: "rgba(0,255,208,0.5)", textShadow: "0 0 28px rgba(0,255,208,0.8)",
    logoStyle: "neon", era: "שנות ה-80",
  },
  new_wave: {
    accent: "#CC00FF", secondary: "#08000F",
    glow: "rgba(204,0,255,0.5)", textShadow: "0 0 28px rgba(204,0,255,0.75)",
    logoStyle: "neon", era: "שנות ה-80",
  },
  hip_hop: {
    accent: "#FFD700", secondary: "#080808",
    glow: "rgba(255,215,0,0.45)", textShadow: "0 0 20px rgba(255,215,0,0.6)",
    logoStyle: "minimal", era: "שנות ה-90",
  },
  grunge: {
    accent: "#7DAF4A", secondary: "#0A0C0A",
    glow: "rgba(125,175,74,0.35)", textShadow: "0 0 14px rgba(125,175,74,0.5)",
    logoStyle: "distressed", era: "שנות ה-90",
  },
  rnb: {
    accent: "#9B59F5", secondary: "#080010",
    glow: "rgba(155,89,245,0.5)", textShadow: "0 0 24px rgba(155,89,245,0.7)",
    logoStyle: "minimal", era: "שנות ה-90–2000",
  },
  country: {
    accent: "#D4904A", secondary: "#0D0800",
    glow: "rgba(212,144,74,0.4)", textShadow: "0 0 18px rgba(212,144,74,0.6)",
    logoStyle: "gold", era: "שנות ה-50–80",
  },
  reggae: {
    accent: "#4CAF50", secondary: "#041004",
    glow: "rgba(76,175,80,0.45)", textShadow: "0 0 18px rgba(76,175,80,0.6)",
    logoStyle: "minimal", era: "שנות ה-70–80",
  },
  default: {
    accent: "#F5A800", secondary: "#0A0A0A",
    glow: "rgba(245,168,0,0.5)", textShadow: "0 0 20px rgba(245,168,0,0.65)",
    logoStyle: "vhs", era: "",
  },
};

export function getTheme(key: string): GenreTheme {
  return GENRE_THEMES[key] ?? GENRE_THEMES["default"];
}
