import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { api } from "../lib/api";
import type { Client } from "../types";

export default function Dashboard() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    api
      .getClients(token)
      .then(setClients)
      .catch(() => setError("Could not load clients."))
      .finally(() => setLoading(false));
  }, [token]);

  return (
    <Layout>
      <h1 className="mb-6 text-2xl font-semibold text-slate-800">Clients</h1>

      {loading && <p className="text-slate-500">Loading…</p>}
      {error && <p className="text-red-600">{error}</p>}

      {!loading && !error && clients.length === 0 && (
        <p className="text-slate-500">
          No clients yet. Add one in the Django admin.
        </p>
      )}

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {clients.map((c) => (
          <button
            key={c.id}
            onClick={() => navigate(`/clients/${c.id}`)}
            className="group flex flex-col items-start rounded-xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:shadow-md"
            style={{ borderTopColor: c.primary_color, borderTopWidth: 4 }}
          >
            <div className="mb-4 flex h-12 w-full items-center">
              {c.logo_url ? (
                <img
                  src={c.logo_url}
                  alt={c.name}
                  className="max-h-12 max-w-[160px] object-contain"
                />
              ) : (
                <div
                  className="flex h-10 w-10 items-center justify-center rounded-md text-sm font-bold text-white"
                  style={{ backgroundColor: c.primary_color }}
                >
                  {c.name.charAt(0)}
                </div>
              )}
            </div>
            <h2 className="text-base font-semibold text-slate-800 group-hover:text-blue-600">
              {c.name}
            </h2>
            <p className="text-sm text-slate-500">{c.company}</p>
            <p className="mt-3 text-xs text-slate-400">
              {c.results_count} result{c.results_count === 1 ? "" : "s"}
            </p>
          </button>
        ))}
      </div>
    </Layout>
  );
}
