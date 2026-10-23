import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { Link2, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { register } from "../api/auth";
import { getApiErrorMessage } from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function Register() {
    const navigate = useNavigate();
    const { isAuthenticated } = useAuth();
    const [form, setForm] = useState({ username: "", email: "", password: "" });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    if (isAuthenticated) return <Navigate to="/dashboard" replace />;

    async function handleSubmit(event) {
        event.preventDefault();
        setIsSubmitting(true);

        try {
            await register(form);
            toast.success("Account created. Sign in to continue.");
            navigate("/login", { replace: true });
        } catch (error) {
            toast.error(getApiErrorMessage(error, "Unable to create account"));
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
                    <p className="eyebrow">Create workspace</p>
                    <h1>Start tracking every link you ship.</h1>
                    <p className="lede">
                        Your links stay private to your account, with expiration, aliases, and click analytics built in.
                    </p>
                </div>

                <form className="form-stack" onSubmit={handleSubmit}>
                    <label>
                        <span>Username</span>
                        <input
                            autoComplete="username"
                            maxLength={30}
                            minLength={3}
                            name="username"
                            onChange={(event) => setForm((value) => ({ ...value, username: event.target.value }))}
                            placeholder="campaign_ops"
                            required
                            value={form.username}
                        />
                    </label>

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
                        Create account
                    </button>
                </form>

                <p className="switch-copy">
                    Already have an account? <Link to="/login">Sign in</Link>
                </p>
            </section>
        </main>
    );
}
