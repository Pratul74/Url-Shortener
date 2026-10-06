import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Loader2, RefreshCw } from "lucide-react";
import { toast } from "sonner";

import { getAnalytics } from "../api/url";
import { getApiErrorMessage } from "../api/axios";

function TopList({ title, data }) {
    const entries = Object.entries(data ?? {}).sort((a, b) => b[1] - a[1]).slice(0, 6);

    return (
        <article className="analytics-card">
            <h2>{title}</h2>
            {entries.length === 0 ? (
                <p className="muted-copy">No click data yet</p>
            ) : (
                <div className="rank-list">
                    {entries.map(([label, value]) => (
                        <div className="rank-row" key={label || "unknown"}>
                            <span>{label || "Unknown"}</span>
                            <strong>{value}</strong>
                        </div>
                    ))}
                </div>
            )}
        </article>
    );
}

export default function Analytics() {
    const { urlId } = useParams();
    const [analytics, setAnalytics] = useState(null);
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(true);

    const loadAnalytics = useCallback(async () => {
        setIsLoading(true);
        setError("");
        try {
            setAnalytics(await getAnalytics(urlId));
        } catch (error) {
            const message = getApiErrorMessage(error, "Unable to load analytics");
            setError(message);
            setAnalytics(null);
            toast.error(message);
        } finally {
            setIsLoading(false);
        }
    }, [urlId]);

    useEffect(() => {
        loadAnalytics();
    }, [loadAnalytics]);

    return (
        <main className="app-shell">
            <header className="topbar">
                <div>
                    <p className="eyebrow">Analytics</p>
                    <h1>Link #{urlId}</h1>
                </div>
                <Link className="ghost-button" to="/">
                    <ArrowLeft size={16} />
                    Dashboard
                </Link>
                <button className="ghost-button" onClick={loadAnalytics} type="button">
                    <RefreshCw size={16} />
                    Refresh
                </button>
            </header>

            {isLoading ? (
                <div className="empty-state">
                    <Loader2 className="spin" size={24} />
                    Loading analytics
                </div>
            ) : !analytics ? (
                <div className="empty-state">
                    {error || "No analytics available for this link."}
                </div>
            ) : (
                <>
                    <section className="metric-grid">
                        <article className="metric-panel accent-panel">
                            <span>Total clicks</span>
                            <strong>{analytics.total_clicks}</strong>
                        </article>
                        <article className="metric-panel">
                            <span>Countries</span>
                            <strong>{Object.keys(analytics.country ?? {}).length}</strong>
                        </article>
                        <article className="metric-panel">
                            <span>Referrers</span>
                            <strong>{Object.keys(analytics.referrer ?? {}).length}</strong>
                        </article>
                    </section>

                    <section className="analytics-grid">
                        <TopList title="Countries" data={analytics.country} />
                        <TopList title="Cities" data={analytics.city} />
                        <TopList title="Browsers" data={analytics.browser} />
                        <TopList title="Operating systems" data={analytics.os} />
                        <TopList title="Devices" data={analytics.device} />
                        <TopList title="Referrers" data={analytics.referrer} />
                    </section>
                </>
            )}
        </main>
    );
}
