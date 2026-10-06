import axios from "axios";
import { toast } from "sonner";

export const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export const TOKEN_KEY = "access_token";

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem(TOKEN_KEY);
            window.dispatchEvent(new Event("auth:logout"));
            if (window.location.pathname !== "/login") {
                window.location.href = "/login";
            }
        }
        return Promise.reject(error);
    }
);

export function getApiErrorMessage(error, fallback = "Something went wrong") {
    const detail = error.response?.data?.detail;

    if (Array.isArray(detail)) {
        return detail
            .map((item) => {
                const path = Array.isArray(item.loc) ? item.loc.slice(1).join(".") : "";
                return path ? `${path}: ${item.msg}` : item.msg;
            })
            .join(", ");
    }

    if (typeof detail === "string") return detail;
    if (typeof error.response?.data?.message === "string") return error.response.data.message;
    if (error.code === "ECONNABORTED") return "Request timed out";
    if (error.message === "Network Error") return "API is unreachable. Check the backend URL.";

    return fallback;
}

export function toastApiError(error, fallback) {
    toast.error(getApiErrorMessage(error, fallback));
}

export default api;
