import api from "./axios";

export async function createShortUrl(payload) {
    const response = await api.post("/urls", payload);
    return response.data;
}

export async function listUrls() {
    const response = await api.get("/urls/get_all");
    return response.data;
}

export async function deleteUrl(shortCode) {
    const response = await api.delete(`/urls/delete/${encodeURIComponent(shortCode)}`);
    return response.data;
}

export async function permanentlyDeleteUrl(shortCode) {
    const response = await api.delete(`/urls/permanent_delete/${encodeURIComponent(shortCode)}`);
    return response.data;
}

export async function getAnalytics(urlId) {
    const response = await api.get(`/analytics/${urlId}/dashboard`);
    return response.data;
}
