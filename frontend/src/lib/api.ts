const API_BASE =
  (import.meta.env.VITE_API_URL as string) || "http://localhost:8000/api";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  token?: string | null;
}

async function request<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (opts.token) {
    headers["Authorization"] = `Bearer ${opts.token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method: opts.method ?? "GET",
    headers,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail || JSON.stringify(data);
    } catch {
      /* keep statusText */
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  login: (username: string, password: string) =>
    request<{ access: string; refresh: string }>("/auth/login/", {
      method: "POST",
      body: { username, password },
    }),

  logout: (token: string, refresh: string) =>
    request<void>("/auth/logout/", {
      method: "POST",
      token,
      body: { refresh },
    }),

  getClients: (token: string) =>
    request<import("../types").Client[]>("/clients/", { token }),

  getClient: (id: number, token: string) =>
    request<import("../types").Client>(`/clients/${id}/`, { token }),

  getClientResults: (id: number, token: string) =>
    request<import("../types").TourResult[]>(`/clients/${id}/results/`, {
      token,
    }),
};
