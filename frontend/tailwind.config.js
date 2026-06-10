/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["IBM Plex Sans", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
      colors: {
        canvas: "#070b12",
        surface: "#0d111c",
        elevated: "#141c2e",
        line: "#1e2a3f",
        glass: "rgba(20, 28, 46, 0.55)",
        neon: {
          blue: "#3b9eff",
          green: "#22d3a0",
          amber: "#f5b942",
        },
      },
      boxShadow: {
        glow: "0 0 24px rgba(59, 158, 255, 0.22)",
        "glow-success": "0 0 16px rgba(34, 211, 160, 0.28)",
        "glow-warning": "0 0 16px rgba(245, 185, 66, 0.25)",
        glass: "0 8px 32px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255,255,255,0.04)",
      },
      animation: {
        "pulse-slow": "pulse 2.5s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "flow-line": "flow-line 2.4s ease-in-out infinite",
        "node-glow": "node-glow 2s ease-in-out infinite",
      },
      keyframes: {
        "flow-line": {
          "0%, 100%": { opacity: "0.35" },
          "50%": { opacity: "1" },
        },
        "node-glow": {
          "0%, 100%": { boxShadow: "0 0 8px rgba(59, 158, 255, 0.15)" },
          "50%": { boxShadow: "0 0 20px rgba(59, 158, 255, 0.35)" },
        },
      },
    },
  },
  plugins: [],
};
