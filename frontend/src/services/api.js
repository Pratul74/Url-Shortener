const BASE_URL = import.meta.env.VITE_API_URL;

if (!BASE_URL) {
    throw new Error("VITE_API_URL is not defined. Check your .env file.");
}

const DEFAULT_TIMEOUT_MS = 15000;

export class ApiError extends Error {
    constructor(message, status, data) {
        super(message);
        this.name = "ApiError";
        this.status = status;
        this.data = data;
    }
}

function extractMessage(data, status) {
    const detail = data?.detail;
    if (Array.isArray(detail)) {
        return detail
            .map((e) => {
                const field = Array.isArray(e.loc) ? e.loc.slice(1).join(".") : "";
                return field ? `${field}: ${e.msg}` : e.msg;
            })
            .join(", ");
    }

    if (typeof detail === "string") return detail;
    if (typeof data?.message === "string") return data.message;

    return `Request failed with status ${status}`;
}

function isPlainBody(body) {
    return (
        body !== null &&
        typeof body === "object" &&
        !(body instanceof FormData) &&
        !(body instanceof Blob) &&
        !(body instanceof ArrayBuffer) &&
        !(body instanceof URLSearchParams) &&
        !(typeof ReadableStream !== "undefined" && body instanceof ReadableStream)
    );
}

export async function apiRequest(endpoint, options = {}) {
    const { timeout = DEFAULT_TIMEOUT_MS, signal, ...fetchOptions } = options;

    const headers = new Headers(fetchOptions.headers);

    let body = fetchOptions.body;
    if (isPlainBody(body)) {
        body = JSON.stringify(body);
    }

    if (body && !(body instanceof FormData) && !headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }

    let token = null;
    try {
        token = localStorage.getItem("access_token");
    } catch {
    }

    if (token && !headers.has("Authorization")) {
        headers.set("Authorization", `Bearer ${token}`);
    }
    const timeoutSignal = AbortSignal.timeout(timeout);
    const finalSignal = signal
        ? AbortSignal.any([signal, timeoutSignal])
        : timeoutSignal;

    let response;
    try {
        response = await fetch(`${BASE_URL}${endpoint}`, {
            ...fetchOptions,
            body,
            headers,
            signal: finalSignal,
        });
    } catch (err) {
        if (err.name === "TimeoutError") {
            throw new ApiError("Request timed out", 0, null);
        }
        if (err.name === "AbortError") {
            throw err;
        }
        throw new ApiError("Network error. Please check your connection.", 0, null);
    }

    if (!response.ok) {
        const data = await response.json().catch(() => null);

        if (response.status === 401) {
            try {
                localStorage.removeItem("access_token");
            } catch {
                // ignore
            }
            if (window.location.pathname !== "/login") {
                window.location.href = "/login";
            }
        }

        throw new ApiError(
            extractMessage(data, response.status),
            response.status,
            data
        );
    }

    if (response.status === 204 || response.status === 205) {
        return null;
    }

    const contentType = response.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
        const text = await response.text();
        return text ? JSON.parse(text) : null;
    }

    return response.text();
}

export default apiRequest;
