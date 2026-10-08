// AuthContext — single owner of auth state (REQ-FE-031, REQ-ARCH-012).
//
// The token lives in localStorage under the exact key `token`
// (REQ-ARCH-042); on mount a stored token is validated against
// /auth/me and cleared when the backend rejects it. login/register
// persist the returned token + user (register auto-logs-in); logout
// clears both (FR-AUTH-4).

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode
} from 'react';
import { getMe, login as loginApi, register as registerApi } from '../api/auth';
import type { LoginPayload, RegisterPayload, User } from '../api/auth';
import { TOKEN_KEY } from '../api/client';

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }): JSX.Element => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [isLoading, setIsLoading] = useState<boolean>(() =>
    Boolean(localStorage.getItem(TOKEN_KEY))
  );

  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (!stored) {
      return;
    }
    let cancelled = false;
    const validate = async (): Promise<void> => {
      try {
        const me = await getMe();
        if (!cancelled) {
          setUser(me);
        }
      } catch {
        if (!cancelled) {
          // A rejected token (401 / TOKEN_INVALID / ...) is stale state:
          // drop it and stay logged out. The client interceptor already
          // removed the key on 401; remove again defensively.
          localStorage.removeItem(TOKEN_KEY);
          setToken(null);
          setUser(null);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };
    void validate();
    return () => {
      cancelled = true;
    };
  }, []);

  const persistSession = useCallback((nextToken: string, nextUser: User): void => {
    localStorage.setItem(TOKEN_KEY, nextToken);
    setToken(nextToken);
    setUser(nextUser);
  }, []);

  const login = useCallback(
    async (payload: LoginPayload): Promise<void> => {
      const result = await loginApi(payload);
      persistSession(result.access_token, result.user);
    },
    [persistSession]
  );

  const register = useCallback(
    async (payload: RegisterPayload): Promise<void> => {
      const result = await registerApi(payload);
      persistSession(result.access_token, result.user);
    },
    [persistSession]
  );

  const logout = useCallback((): void => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, token, isLoading, login, register, logout }),
    [user, token, isLoading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/** Access the auth state; throws outside an AuthProvider tree. */
export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
