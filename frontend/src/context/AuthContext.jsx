import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { TOKEN_KEY } from "../api/axios";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));

    const login = useCallback((newToken) => {
        localStorage.setItem(TOKEN_KEY, newToken);
        setToken(newToken);
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem(TOKEN_KEY);
        setToken(null);
    }, []);

    useEffect(() => {
        const onStorage = (e) => {
            if (e.key === TOKEN_KEY) setToken(e.newValue);
        };
        window.addEventListener("auth:logout", logout);
        window.addEventListener("storage", onStorage);
        return () => {
            window.removeEventListener("auth:logout", logout);
            window.removeEventListener("storage", onStorage);
        };
    }, [logout]);

    const value = useMemo(
        () => ({ token, login, logout, isAuthenticated: !!token }),
        [token, login, logout]
    );

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
    return ctx;
}
