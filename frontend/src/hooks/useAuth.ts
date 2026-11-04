import { createContext, useContext, useState, useCallback } from 'react';

interface AuthState {
  token: string | null;
  userId: string | null;
}

interface AuthContextValue extends AuthState {
  setAuth: (token: string, userId: string) => void;
  clearAuth: () => void;
}

export const AuthContext = createContext<AuthContextValue>({
  token: null,
  userId: null,
  setAuth: () => undefined,
  clearAuth: () => undefined,
});

export function useAuthState(): AuthContextValue {
  const [state, setState] = useState<AuthState>({ token: null, userId: null });

  const setAuth = useCallback((token: string, userId: string) => {
    setState({ token, userId });
  }, []);

  const clearAuth = useCallback(() => {
    setState({ token: null, userId: null });
  }, []);

  return { ...state, setAuth, clearAuth };
}

export function useAuth(): AuthContextValue {
  return useContext(AuthContext);
}
