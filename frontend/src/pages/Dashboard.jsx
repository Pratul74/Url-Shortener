import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, BarChart3, Copy, Download, ExternalLink, Loader2, LogOut, Plus, QrCode, RefreshCw, Trash2, X } from "lucide-react";
import { toast } from "sonner";

import { createShortUrl, deleteUrl, getQrCode, listUrls, permanentlyDeleteUrl } from "../api/url";
import { getApiErrorMessage } from "../api/axios";
import { useAuth } from "../context/AuthContext";

function formatDate(value) {
    if (!value) return "Never";
    return new Intl.DateTimeFormat(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(new Date(value));
}

function isExpired(value) {
    return value ? new Date(value).getTime() < Date.now() : false;
}

export default function Dashboard() {
    const navigate = useNavigate();
    const { logout } = useAuth();
    const [links, setLinks] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isCreating, setIsCreating] = useState(false);
    const [qrPreview, setQrPreview] = useState(null);
    const [isLoadingQr, setIsLoadingQr] = useState(false);
    const [form, setForm] = useState({
        original_url: "",
        custom_alias: "",
        expires_at: "",
    });

    const totals = useMemo(() => {
        return links.reduce(
            (acc, link) => {
                acc.clicks += link.clicks ?? 0;
                if (link.is_active && !isExpired(link.expires_at)) acc.active += 1;
                if (!link.is_active) acc.inactive += 1;
                return acc;
            },
            { active: 0, clicks: 0, inactive: 0 }
        );
    }, [links]);

    async function loadLinks() {
        setIsLoading(true);
        try {
            setLinks(await listUrls());
        } catch (error) {
            toast.error(getApiErrorMessage(error, "Unable to load links"));
        } finally {
            setIsLoading(false);
        }
    }

    useEffect(() => {
        loadLinks();
    }, []);

    useEffect(() => {
        return () => {
            if (qrPreview) URL.revokeObjectURL(qrPreview.url);
        };
    }, [qrPreview]);

    async function handleCreate(event) {
        event.preventDefault();
        setIsCreating(true);

        const payload = {
            original_url: form.original_url.trim(),
            custom_alias: form.custom_alias.trim() || null,
            expires_at: form.expires_at ? new Date(form.expires_at).toISOString() : null,
        };

        try {
            const created = await createShortUrl(payload);
            setLinks((current) => [{ ...created, is_active: true }, ...current]);
            setForm({ original_url: "", custom_alias: "", expires_at: "" });
            toast.success("Short link created");
        } catch (error) {
            toast.error(getApiErrorMessage(error, "Unable to create link"));
        } finally {
            setIsCreating(false);
        }
    }

    async function copyLink(shortUrl) {
        try {
            await navigator.clipboard.writeText(shortUrl);
            toast.success("Copied short link");
        } catch {
            toast.error("Unable to copy short link");
        }
    }

    async function showQr(link) {
        setIsLoadingQr(true);
        try {
            const blob = await getQrCode(link.short_code);
            setQrPreview({ url: URL.createObjectURL(blob), shortUrl: link.short_url });
        } catch (error) {
            toast.error(getApiErrorMessage(error, "Unable to generate QR code"));
        } finally {
            setIsLoadingQr(false);
        }
    }

    function closeQr() {
        setQrPreview(null);
    }

    async function handleSoftDelete(shortCode) {
        try {
            await deleteUrl(shortCode);
            setLinks((current) =>
                current.map((link) => (link.short_code === shortCode ? { ...link, is_active: false } : link))
            );
            toast.success("Link deactivated");
        } catch (error) {
            toast.error(getApiErrorMessage(error, "Unable to deactivate link"));
        }
    }

    async function handlePermanentDelete(shortCode) {
        try {
            await permanentlyDeleteUrl(shortCode);
            setLinks((current) => current.filter((link) => link.short_code !== shortCode));
            toast.success("Link permanently deleted");
        } catch (error) {
            toast.error(getApiErrorMessage(error, "Unable to delete link"));
        }
    }

    function handleLogout() {
        logout();
        navigate("/login", { replace: true });
    }

    return (
        <main className="app-shell">
            <header className="topbar">
                <div>
                    <p className="eyebrow">Production dashboard</p>
                    <h1>Short links</h1>
                </div>
                <div className="dashboard-header-actions">
                    <Link className="ghost-button" to="/">
                        <ArrowLeft size={16} />
                        Home
                    </Link>
                    <button className="ghost-button" onClick={handleLogout} type="button">
                        <LogOut size={16} />
                        Sign out
                    </button>
                </div>
            </header>

            <section className="metric-grid">
                <article className="metric-panel">
                    <span>Active links</span>
                    <strong>{totals.active}</strong>
                </article>
                <article className="metric-panel">
                    <span>Total clicks</span>
                    <strong>{totals.clicks}</strong>
                </article>
                <article className="metric-panel">
                    <span>Inactive links</span>
                    <strong>{totals.inactive}</strong>
                </article>
            </section>

            <section className="workspace-grid">
                <form className="create-panel" onSubmit={handleCreate}>
                    <div className="section-heading">
                        <div>
                            <p className="eyebrow">Create</p>
                            <h2>New short link</h2>
                        </div>
                        <Plus size={20} />
                    </div>

                    <label>
                        <span>Destination URL</span>
                        <input
                            onChange={(event) => setForm((value) => ({ ...value, original_url: event.target.value }))}
                            placeholder="https://example.com/landing-page"
                            required
                            type="url"
                            value={form.original_url}
                        />
                    </label>

                    <label>
                        <span>Custom alias</span>
                        <input
                            maxLength={10}
                            minLength={3}
                            onChange={(event) => setForm((value) => ({ ...value, custom_alias: event.target.value }))}
                            placeholder="launch"
                            value={form.custom_alias}
                        />
                    </label>

                    <label>
                        <span>Expiration</span>
                        <input
                            onChange={(event) => setForm((value) => ({ ...value, expires_at: event.target.value }))}
                            type="datetime-local"
                            value={form.expires_at}
                        />
                    </label>

                    <button className="primary-button" disabled={isCreating} type="submit">
                        {isCreating ? <Loader2 className="spin" size={17} /> : null}
                        Create link
                    </button>
                </form>

                <section className="list-panel">
                    <div className="section-heading">
                        <div>
                            <p className="eyebrow">Inventory</p>
                            <h2>Your links</h2>
                        </div>
                        <button className="icon-button" onClick={loadLinks} title="Refresh links" type="button">
                            <RefreshCw size={17} />
                        </button>
                    </div>

                    {isLoading ? (
                        <div className="empty-state">
                            <Loader2 className="spin" size={24} />
                            Loading links
                        </div>
                    ) : links.length === 0 ? (
                        <div className="empty-state">No short links yet. Create your first one from the form.</div>
                    ) : (
                        <div className="link-table">
                            {links.map((link) => {
                                const expired = isExpired(link.expires_at);
                                const status = !link.is_active ? "Inactive" : expired ? "Expired" : "Active";

                                return (
                                    <article className="link-row" key={link.id}>
                                        <div className="link-main">
                                            <div className="link-title">
                                                <a href={link.short_url} rel="noreferrer" target="_blank">
                                                    {link.short_url}
                                                </a>
                                                <span className={`status-pill ${status.toLowerCase()}`}>{status}</span>
                                            </div>
                                            <p>{link.original_url}</p>
                                            <small>Expires {formatDate(link.expires_at)}</small>
                                        </div>
                                        <div className="link-stats">
                                            <strong>{link.clicks}</strong>
                                            <span>clicks</span>
                                        </div>
                                        <div className="row-actions">
                                            <button className="icon-button" onClick={() => copyLink(link.short_url)} title="Copy link" type="button">
                                                <Copy size={16} />
                                            </button>
                                            <button className="icon-button" disabled={isLoadingQr} onClick={() => showQr(link)} title="Show QR code" type="button">
                                                {isLoadingQr ? <Loader2 className="spin" size={16} /> : <QrCode size={16} />}
                                            </button>
                                            <a className="icon-button" href={link.short_url} rel="noreferrer" target="_blank" title="Open link">
                                                <ExternalLink size={16} />
                                            </a>
                                            <Link className="icon-button" to={`/analytics/${link.id}`} title="View analytics">
                                                <BarChart3 size={16} />
                                            </Link>
                                            {link.is_active ? (
                                                <button className="icon-button danger" onClick={() => handleSoftDelete(link.short_code)} title="Deactivate link" type="button">
                                                    <Trash2 size={16} />
                                                </button>
                                            ) : (
                                                <button className="text-button danger" onClick={() => handlePermanentDelete(link.short_code)} type="button">
                                                    Delete
                                                </button>
                                            )}
                                        </div>
                                    </article>
                                );
                            })}
                        </div>
                    )}
                </section>
            </section>

            {qrPreview ? (
                <div className="qr-backdrop" onClick={closeQr} role="presentation">
                    <section className="qr-dialog" onClick={(event) => event.stopPropagation()} role="dialog" aria-modal="true" aria-label="QR code">
                        <div className="section-heading">
                            <div>
                                <p className="eyebrow">Share visually</p>
                                <h2>QR code</h2>
                            </div>
                            <button className="icon-button" onClick={closeQr} title="Close" type="button"><X size={17} /></button>
                        </div>
                        <img className="qr-image" src={qrPreview.url} alt={`QR code for ${qrPreview.shortUrl}`} />
                        <p className="muted-copy qr-url">{qrPreview.shortUrl}</p>
                        <a className="primary-button qr-download" download="snipp-qr-code.png" href={qrPreview.url}>
                            <Download size={17} /> Download QR code
                        </a>
                    </section>
                </div>
            ) : null}
        </main>
    );
}
