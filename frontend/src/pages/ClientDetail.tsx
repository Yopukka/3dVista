import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { api } from "../lib/api";
import type { Client, TourResult } from "../types";

export default function ClientDetail() {
  const { id } = useParams<{ id: string }>();
  const clientId = Number(id);
  const { token } = useAuth();
  const navigate = useNavigate();
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const enterFullscreen = () => {
    iframeRef.current?.requestFullscreen?.();
  };

  const [client, setClient] = useState<Client | null>(null);
  const [results, setResults] = useState<TourResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !clientId) return;
    setLoading(true);
    Promise.all([
      api.getClient(clientId, token),
      api.getClientResults(clientId, token),
    ])
      .then(([c, r]) => {
        setClient(c);
        setResults(r);
      })
      .catch(() => setError("Could not load this client."))
      .finally(() => setLoading(false));
  }, [token, clientId]);

  return (
    <Layout>
      <button
        onClick={() => navigate("/dashboard")}
        className="mb-4 text-sm text-slate-500 hover:text-slate-700"
      >
        ← Back to clients
      </button>

      {loading && <p className="text-slate-500">Loading…</p>}
      {error && <p className="text-red-600">{error}</p>}

      {client && (
        <>
          <div className="mb-6 flex items-center gap-4">
            {client.logo_url && (
              <img
                src={client.logo_url}
                alt={client.name}
                className="max-h-12 max-w-[160px] object-contain"
              />
            )}
            <div>
              <h1 className="text-2xl font-semibold text-slate-800">
                {client.name}
              </h1>
              <p className="text-sm text-slate-500">{client.company}</p>
            </div>
          </div>

          {/* Section 1: Tour Viewer */}
          <section className="mb-8">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-700">
                Tour Viewer
              </h2>
              {client.tour_url && (
                <div className="flex gap-2">
                  <button
                    onClick={enterFullscreen}
                    className="inline-flex items-center gap-1.5 rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
                  >
                    ⛶ Pantalla completa
                  </button>
                  <a
                    href={client.tour_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
                  >
                    ↗ Abrir en pestaña
                  </a>
                </div>
              )}
            </div>
            {client.tour_url ? (
              <div className="overflow-hidden rounded-xl border border-slate-200 bg-black">
                <iframe
                  ref={iframeRef}
                  src={client.tour_url}
                  title={`${client.name} tour`}
                  className="h-[78vh] min-h-130 w-full"
                  allow="fullscreen; xr-spatial-tracking; gyroscope; accelerometer"
                  sandbox="allow-scripts allow-same-origin allow-fullscreen allow-popups"
                  referrerPolicy="strict-origin-when-cross-origin"
                />
              </div>
            ) : (
              <p className="rounded-lg border border-dashed border-slate-300 p-6 text-sm text-slate-500">
                No tour URL set for this client.
              </p>
            )}
          </section>

          {/* Section 2: Stats Panel */}
          <section>
            <h2 className="mb-3 text-lg font-semibold text-slate-700">
              Stats Panel
            </h2>
            {results.length === 0 ? (
              <p className="rounded-lg border border-dashed border-slate-300 p-6 text-sm text-slate-500">
                No results recorded yet.
              </p>
            ) : (
              <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
                <table className="min-w-full divide-y divide-slate-200 text-sm">
                  <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                    <tr>
                      <th className="px-4 py-3 font-medium">Employee</th>
                      <th className="px-4 py-3 font-medium">Score</th>
                      <th className="px-4 py-3 font-medium">Questions</th>
                      <th className="px-4 py-3 font-medium">Items found</th>
                      <th className="px-4 py-3 font-medium">Completed</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {results.map((r) => (
                      <tr key={r.id} className="hover:bg-slate-50">
                        <td className="px-4 py-3 font-medium text-slate-800">
                          {r.employee_name}
                        </td>
                        <td className="px-4 py-3 text-slate-600">
                          {r.score} / {r.total_score}
                        </td>
                        <td className="px-4 py-3 text-slate-600">
                          {r.answered_questions} / {r.total_questions}
                        </td>
                        <td className="px-4 py-3 text-slate-600">
                          {r.items_found} / {r.total_items}
                        </td>
                        <td className="px-4 py-3 text-slate-500">
                          {new Date(r.completed_at).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </Layout>
  );
}
