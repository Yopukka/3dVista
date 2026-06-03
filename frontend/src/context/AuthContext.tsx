import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { api } from "../lib/api";

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

/**
 * Holds the JWT access token in React state ONLY (in memory).
 * It is never written to localStorage or sessionStorage, so it is gone
 * on a full page reload — which is the intended security trade-off here.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  // Refresh token is also kept in memory only, so logout can revoke it
  // server-side (blacklist). Never persisted to storage.
  const [refresh, setRefresh] = useState<string | null>(null);

  const login = useCallback(async (username: string, password: string) => {
    const { access, refresh: refreshToken } = await api.login(username, password);
    setToken(access);
    setRefresh(refreshToken);
  }, []);

  const logout = useCallback(() => {
    // Revoke the refresh token server-side; ignore network errors so logout
    // always succeeds locally even if the call fails.
    if (token && refresh) {
      void api.logout(token, refresh).catch(() => undefined);
    }
    setToken(null);
    setRefresh(null);
  }, [token, refresh]);

  const value = useMemo<AuthState>(
    () => ({ token, isAuthenticated: !!token, login, logout }),
    [token, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
