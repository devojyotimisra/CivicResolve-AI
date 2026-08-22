import axios from "axios";

const client = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    timeout: 30000,
});

client.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("civic_auth_token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

client.interceptors.response.use(
    (response) => {
        const refreshedToken = response.headers["x-refresh-token"];
        if (refreshedToken) {
            localStorage.setItem("civic_auth_token", refreshedToken);

            const SESSION_KEY = "civic_current_session";
            const sessionRaw = localStorage.getItem(SESSION_KEY);
            if (sessionRaw) {
                try {
                    const session = JSON.parse(sessionRaw);
                    session.token = refreshedToken;
                    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
                } catch (error) {
                    console.error(error);
                }
            }
        }
        return response;
    },
    (error) => {
        if (error.response && error.response.status === 401) {
            localStorage.removeItem("civic_auth_token");
            localStorage.removeItem("civic_current_session");

            if (window.location.pathname !== "/login") {
                window.location.href = "/login";
            }
        }
        return Promise.reject(error);
    }
);

export default client;
