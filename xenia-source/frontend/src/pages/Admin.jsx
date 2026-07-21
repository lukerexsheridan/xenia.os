import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import { toast } from "sonner";
import Nav from "@/components/Nav";
import BlackHoleMark from "@/components/BlackHoleMark";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const TOKEN_KEY = "xenia.admin.token";
const EXP_KEY = "xenia.admin.exp";

function formatError(detail) {
  if (detail == null) return "Something went wrong. Please try again.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail
      .map((e) => (e && typeof e.msg === "string" ? e.msg : JSON.stringify(e)))
      .filter(Boolean)
      .join(" ");
  if (detail && typeof detail.msg === "string") return detail.msg;
  return String(detail);
}

function readToken() {
  const token = localStorage.getItem(TOKEN_KEY);
  const exp = Number(localStorage.getItem(EXP_KEY) || 0);
  if (!token) return null;
  if (exp && exp * 1000 < Date.now()) {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(EXP_KEY);
    return null;
  }
  return token;
}

export default function Admin() {
  const [token, setToken] = useState(() => readToken());
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [leads, setLeads] = useState(null);
  const [loading, setLoading] = useState(false);

  const login = async (e) => {
    e.preventDefault();
    if (!password || submitting) return;
    setSubmitting(true);
    try {
      const { data } = await axios.post(`${API}/admin/login`, { password });
      localStorage.setItem(TOKEN_KEY, data.token);
      // Store epoch seconds
      const expEpoch = Math.floor(new Date(data.expires_at).getTime() / 1000);
      localStorage.setItem(EXP_KEY, String(expEpoch));
      setToken(data.token);
      setPassword("");
      toast.success("Signed in.");
    } catch (err) {
      toast.error(formatError(err?.response?.data?.detail) || "Login failed.");
    } finally {
      setSubmitting(false);
    }
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(EXP_KEY);
    setToken(null);
    setLeads(null);
  };

  const exportCsv = () => {
    if (!leads || leads.length === 0) {
      toast.info("No requests to export yet.");
      return;
    }
    const escape = (v) => {
      const s = v == null ? "" : String(v);
      // Wrap in quotes if it contains comma, quote, or newline
      if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
      return s;
    };
    const rows = [
      ["id", "email", "role", "company", "created_at"].join(","),
      ...leads.map((r) =>
        [
          escape(r.id),
          escape(r.email),
          escape(r.role || ""),
          escape(r.company || ""),
          escape(new Date(r.created_at).toISOString()),
        ].join(",")
      ),
    ];
    const blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const stamp = new Date().toISOString().slice(0, 10);
    const a = document.createElement("a");
    a.href = url;
    a.download = `xenia-waitlist-${stamp}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success(`Exported ${leads.length} ${leads.length === 1 ? "request" : "requests"}.`);
  };

  const fetchLeads = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const { data } = await axios.get(`${API}/admin/leads`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setLeads(data);
    } catch (err) {
      if (err?.response?.status === 401) {
        toast.error("Session expired.");
        logout();
      } else {
        toast.error(formatError(err?.response?.data?.detail) || "Failed to load.");
      }
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchLeads();
  }, [fetchLeads]);

  return (
    <div
      className="relative min-h-screen bg-[#030305] text-white vignette grain"
      data-testid="admin-root"
    >
      <div className="fixed inset-0 z-0 pointer-events-none" aria-hidden>
        <div className="absolute inset-0 ambient-royal" />
        <div className="absolute inset-0 star-field" />
      </div>
      <Nav />
      <main className="relative z-10 pt-32 pb-16 px-6 sm:px-10 lg:px-16 max-w-[1240px] mx-auto">
        {!token ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="max-w-md mx-auto"
          >
            <div className="flex flex-col items-center gap-3 mb-8">
              <BlackHoleMark size={44} />
              <div className="font-mono-xn text-[10px] text-white/40 tracking-widest">
                Admin · restricted
              </div>
              <h1 className="font-display text-3xl sm:text-4xl leading-tight tracking-tight text-center">
                Sign in
              </h1>
            </div>
            <form onSubmit={login} className="glass rounded-2xl p-6 space-y-5" data-testid="admin-login-form">
              <div>
                <div className="text-[10px] font-mono-xn text-white/40 mb-1.5">Password</div>
                <input
                  data-testid="admin-password"
                  type="password"
                  autoFocus
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="os-input w-full"
                  autoComplete="current-password"
                />
              </div>
              <button
                data-testid="admin-submit"
                type="submit"
                disabled={submitting || !password}
                className="w-full inline-flex items-center justify-center gap-2 rounded-full bg-royal text-white px-5 py-3 text-[12px] font-mono-xn shadow-[0_10px_40px_-10px_rgba(76,108,255,0.6)] hover:brightness-110 active:scale-[0.98] transition-all disabled:opacity-50"
              >
                {submitting ? "Signing in…" : "Sign in →"}
              </button>
            </form>
            <div className="mt-4 text-center text-[10.5px] font-mono-xn text-white/25">
              Sessions expire after 24 hours.
            </div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            data-testid="admin-dashboard"
          >
            <div className="flex items-end justify-between gap-6 mb-6">
              <div>
                <div className="font-mono-xn text-[10px] text-white/40 mb-2 flex items-center gap-2.5">
                  <span className="pulse-dot-blue" />
                  <span>Waitlist</span>
                </div>
                <h1 className="font-display text-3xl sm:text-4xl leading-tight tracking-tight">
                  Requests for access
                </h1>
                <p className="mt-2 text-white/50 text-[13.5px]">
                  {leads == null
                    ? "Loading…"
                    : `${leads.length} ${leads.length === 1 ? "request" : "requests"} received.`}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  data-testid="admin-export-csv"
                  onClick={exportCsv}
                  className="os-cta"
                  disabled={!leads || leads.length === 0}
                >
                  Export CSV ↓
                </button>
                <button
                  data-testid="admin-refresh"
                  onClick={fetchLeads}
                  className="os-ghost"
                  disabled={loading}
                >
                  {loading ? "Refreshing…" : "Refresh"}
                </button>
                <button data-testid="admin-logout" onClick={logout} className="os-ghost">
                  Sign out
                </button>
              </div>
            </div>

            <div className="os-table" data-testid="admin-leads-table">
              <div className="os-thead grid grid-cols-[1fr_180px_160px_180px] gap-4">
                <div>Email</div>
                <div>Role</div>
                <div>Company</div>
                <div>When</div>
              </div>
              {(leads || []).length === 0 && !loading && (
                <div className="px-6 py-14 text-center text-white/40 text-[13px]">
                  No requests yet.
                </div>
              )}
              {(leads || []).map((r) => (
                <div
                  key={r.id}
                  data-testid={`admin-lead-${r.id}`}
                  className="os-trow grid grid-cols-[1fr_180px_160px_180px] gap-4 items-center"
                >
                  <div className="text-white text-[13.5px] truncate">{r.email}</div>
                  <div className="text-white/60 text-[12.5px] truncate">{r.role || "—"}</div>
                  <div className="text-white/60 text-[12.5px] truncate">{r.company || "—"}</div>
                  <div className="text-white/45 text-[11.5px] font-mono-xn">
                    {new Date(r.created_at).toLocaleString(undefined, {
                      dateStyle: "medium",
                      timeStyle: "short",
                    })}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
}
