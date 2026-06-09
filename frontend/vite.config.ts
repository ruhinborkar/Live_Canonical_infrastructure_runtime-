import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const proxyTarget = env.VITE_API_PROXY || "http://127.0.0.1:8002";

  return {
    plugins: [react()],
    server: {
      port: 5173,
      strictPort: false,
      proxy: {
        "/api": proxyTarget,
        "/ws": {
          target: proxyTarget.replace("http", "ws"),
          ws: true,
        },
      },
    },
  };
});
