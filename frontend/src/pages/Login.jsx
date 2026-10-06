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

    if (isAuthenticated) return <Navigate to="/" replace />;

    async function handleSubmit(event) {
        event.preventDefault();
        setIsSubmitting(true);

        try {
            const data = await loginRequest(form.email, form.password);
            login(data.access_token);
            toast.success("Welcome back");
            navigate("/", { replace: true });
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
                    <span>Url Shortener</span>
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
                        <input
                            autoComplete="current-password"
                            minLength={8}
                            name="password"
                            onChange={(event) => setForm((value) => ({ ...value, password: event.target.value }))}
                            placeholder="At least 8 characters"
                            required
                            type="password"
                            value={form.password}
                        />
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
