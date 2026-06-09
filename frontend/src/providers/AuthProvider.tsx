import { createContext, ReactNode, useCallback, useContext, useMemo, useState } from "react";
import { config } from "../lib/config";

const AUTH_KEY = "canonical_runtime_auth";

interface AuthContextValue {
  isAuthenticated: boolean;
  username: string | null;
  login: (username: string, password: string) => boolean;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function readSession(): string | null {
  return sessionStorage.getItem(AUTH_KEY);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [username, setUsername] = useState<string | null>(() => readSession());

  const login = useCallback((user: string, password: string) => {
    if (user === config.authUser && password === config.authPass) {
      sessionStorage.setItem(AUTH_KEY, user);
      setUsername(user);
      return true;
    }
    return false;
  }, []);

  const logout = useCallback(() => {
    sessionStorage.removeItem(AUTH_KEY);
    setUsername(null);
  }, []);

  const value = useMemo(
    () => ({
      isAuthenticated: Boolean(username),
      username,
      login,
      logout,
    }),
    [username, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
