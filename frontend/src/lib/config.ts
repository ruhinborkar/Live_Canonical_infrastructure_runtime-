function envLabel(raw: string): string {
  const map: Record<string, string> = {
    development: "Development",
    dev: "Development",
    staging: "Staging",
    stage: "Staging",
    production: "Production",
    prod: "Production",
  };
  return map[raw.toLowerCase()] ?? raw.charAt(0).toUpperCase() + raw.slice(1);
}

export const config = {
  apiUrl: import.meta.env.VITE_API_URL || "/api",
  appEnv: import.meta.env.VITE_APP_ENV || import.meta.env.MODE,
  appEnvLabel: envLabel(import.meta.env.VITE_APP_ENV || import.meta.env.MODE || "development"),
  runtimeVersion: import.meta.env.VITE_RUNTIME_VERSION || "1.0.0",
  authUser: import.meta.env.VITE_AUTH_USER || "admin",
  authPass: import.meta.env.VITE_AUTH_PASS || "runtime",
  isProduction: import.meta.env.PROD,
  healthPollMs: 15_000,
  runsStaleMs: 10_000,
} as const;
