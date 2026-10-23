import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { Link2, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { login as loginRequest } from "../api/auth";
import { getApiErrorMessage } from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function Login() {
    const navigate = useNavigate();
    const { isAuthenticated, login } = useAuth();
    const [form, setForm] = useState({ email: "", password: "" });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    if (isAuthenticated) return <Navigate to="/dashboard" replace />;

    async function handleSubmit(event) {
        event.preventDefault();
        setIsSubmitting(true);

        try {
            const data = await loginRequest(form.email, form.password);
            login(data.access_token);
            toast.success("Welcome back");
            navigate("/dashboard", { replace: true });
        } catch (error) {
            toast.error(getApiErrorMessage(error, "Unable to sign in"));
        } finally {
            setIsSubmitting(false);
        }
    }

    return (
        <main className="auth-shell">
            <section className="auth-panel">
                <div className="brand-mark">
                    <Link2 size={22} />
                    <span>Snipp the url shortener</span>
                </div>

                <div>
                    <p className="eyebrow">Workspace sign in</p>
                    <h1>Manage short links without losing the signal.</h1>
                    <p className="lede">
                        Create tracked links, watch click quality, and keep stale redirects out of circulation.
                    </p>
                </div>

                <form className="form-stack" onSubmit={handleSubmit}>
                    <label>
                        <span>Email</span>
                        <input
                            autoComplete="email"
                            inputMode="email"
                            name="email"
                            onChange={(event) => setForm((value) => ({ ...value, email: event.target.value }))}
                            placeholder="you@example.com"
                            required
                            type="email"
                            value={form.email}
                        />
                    </label>

                    <label>
                        <span>Password</span>
                        <div className="relative">
                            <input
                                autoComplete="current-password"
                                className="w-full pr-11"
                                minLength={8}
                                name="password"
                                onChange={(event) => setForm((value) => ({ ...value, password: event.target.value }))}
                                placeholder="At least 8 characters"
                                required
                                type={showPassword ? "text" : "password"}
                                value={form.password}
                            />
                            <button
                                aria-label={showPassword ? "Hide password" : "Show password"}
                                aria-pressed={showPassword}
                                className="absolute right-2 top-1/2 -translate-y-1/2 cursor-pointer rounded p-1 text-lg leading-none"
                                onClick={() => setShowPassword((value) => !value)}
                                type="button"
                            >
                                {showPassword ? "👁️" : "🙈"}
                            </button>
                        </div>
                    </label>

                    <button className="primary-button" disabled={isSubmitting} type="submit">
                        {isSubmitting ? <Loader2 className="spin" size={17} /> : null}
                        Sign in
                    </button>
                </form>

                <p className="switch-copy">
                    New here? <Link to="/register">Create an account</Link>
                </p>
            </section>
        </main>
    );
}
