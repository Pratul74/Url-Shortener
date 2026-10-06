import api, { TOKEN_KEY } from "./axios";

export async function login(email, password) {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    const response = await api.post("/auth/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    localStorage.setItem(TOKEN_KEY, response.data.access_token);
    return response.data;
}

export async function register(data) {
    const response = await api.post("/auth/register", data);

    return response.data;
}

export function logout() {
    localStorage.removeItem(TOKEN_KEY);
    window.dispatchEvent(new Event("auth:logout"));
}
