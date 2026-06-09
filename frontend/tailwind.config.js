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
        canvas: "#0a0e17",
        surface: "#111827",
        elevated: "#1a2234",
        line: "#2a3548",
      },
      boxShadow: {
        glow: "0 0 20px rgba(59, 130, 246, 0.25)",
        "glow-success": "0 0 12px rgba(34, 197, 94, 0.3)",
      },
      animation: {
        "pulse-slow": "pulse 2.5s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
};
