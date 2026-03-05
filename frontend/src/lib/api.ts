import axios from "axios";

const BASE_URL =
  (import.meta as any).env?.VITE_API_URL?.toString().trim() ||
  "http://localhost:8000/api";

const api = axios.create({
  baseURL: BASE_URL,
});

function getAccessToken() {
  return (
    localStorage.getItem("boxrota_access_token") ||
    localStorage.getItem("access_token") ||
    ""
  );
}

function setAccessToken(token: string) {
  localStorage.setItem("boxrota_access_token", token);
}

function getRefreshToken() {
  return localStorage.getItem("boxrota_refresh_token") || "";
}

function setRefreshToken(token: string) {
  localStorage.setItem("boxrota_refresh_token", token);
}

function clearSession() {
  localStorage.removeItem("boxrota_access_token");
  localStorage.removeItem("access_token");
  localStorage.removeItem("boxrota_refresh_token");
  localStorage.removeItem("boxrota_workshop_id");
}

let isRefreshing = false;
let refreshQueue: Array<(token: string | null) => void> = [];

function queueRequest(cb: (token: string | null) => void) {
  refreshQueue.push(cb);
}

function flushQueue(token: string | null) {
  refreshQueue.forEach((cb) => cb(token));
  refreshQueue = [];
}

// Request: injeta Authorization
api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response: refresh automático em 401
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const originalRequest = error?.config;

    // Se não tiver config, só retorna
    if (!originalRequest) return Promise.reject(error);

    const status = error?.response?.status;

    // Evita loop em endpoints de auth
    const url: string = originalRequest?.url || "";
    const isAuthEndpoint =
      url.includes("/auth/login") ||
      url.includes("/auth/refresh") ||
      url.includes("/auth/setup") ||
      url.includes("/auth/logout");

    // Só tenta refresh em 401, e apenas uma vez por request
    if (status !== 401 || isAuthEndpoint || originalRequest._retry) {
      return Promise.reject(error);
    }

    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      clearSession();
      if (typeof window !== "undefined") window.location.href = "/auth/login";
      return Promise.reject(error);
    }

    // Marcar retry
    originalRequest._retry = true;

    // Se já tem refresh rolando, enfileira e espera
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        queueRequest((newToken) => {
          if (!newToken) return reject(error);
          originalRequest.headers = originalRequest.headers ?? {};
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          resolve(api(originalRequest));
        });
      });
    }

    isRefreshing = true;

    try {
      // Faz refresh
      const refreshRes = await api.post("/auth/refresh", {
        refresh_token: refreshToken,
      });

      const tokens = refreshRes?.data?.tokens;
      const newAccess = tokens?.access_token;
      const newRefresh = tokens?.refresh_token;

      if (!newAccess || !newRefresh) {
        throw new Error("Refresh retornou tokens inválidos.");
      }

      setAccessToken(newAccess);
      setRefreshToken(newRefresh);

      // Libera fila
      flushQueue(newAccess);

      // Re-tenta request original
      originalRequest.headers = originalRequest.headers ?? {};
      originalRequest.headers.Authorization = `Bearer ${newAccess}`;
      return api(originalRequest);
    } catch (e) {
      // Falhou refresh → encerra sessão
      flushQueue(null);
      clearSession();
      if (typeof window !== "undefined") window.location.href = "/auth/login";
      return Promise.reject(e);
    } finally {
      isRefreshing = false;
    }
  }
);

export default api;