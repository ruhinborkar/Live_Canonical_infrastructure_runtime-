export const config = {
  apiUrl: import.meta.env.VITE_API_URL || "/api",
  appEnv: import.meta.env.VITE_APP_ENV || import.meta.env.MODE,
  authUser: import.meta.env.VITE_AUTH_USER || "admin",
  authPass: import.meta.env.VITE_AUTH_PASS || "runtime",
  isProduction: import.meta.env.PROD,
  healthPollMs: 15_000,
  runsStaleMs: 10_000,
} as const;
