import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { toast } from "sonner";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function RequestAccess() {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!email || submitting) return;
    setSubmitting(true);
    try {
      await axios.post(`${API}/access`, { email, role: role || null });
      setSubmitted(true);
      toast.success("You're on the list. We'll be in touch.");
    } catch (err) {
      const msg = err?.response?.data?.detail?.[0]?.msg || "Something went wrong. Try again.";
      toast.error(typeof msg === "string" ? msg : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section
      id="access"
      data-testid="request-access"
      className="relative w-full flex items-center justify-center px-6 sm:px-10 py-20"
    >
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
        className="max-w-2xl w-full text-center"
      >
        <div className="font-mono-xn text-[10px] text-white/45 mb-4">
          Private access · By invitation
        </div>
        <h2 className="font-display text-3xl sm:text-4xl lg:text-5xl leading-[1.04] tracking-tight text-white">
          Be among the first to run{" "}
          <span className="text-blue-signature">Xenia</span>.
        </h2>
        <p className="mt-4 text-white/55 text-[14px] leading-relaxed max-w-lg mx-auto">
          We are inviting a small number of modern agencies to shape the earliest
          version of the platform. Leave your email — we read every request.
        </p>

        {!submitted ? (
          <form
            onSubmit={submit}
            className="mt-8 max-w-md mx-auto"
            data-testid="access-form"
          >
            <div className="grid gap-4">
              <input
                data-testid="access-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@agency.com"
                className="underline-input text-center"
                autoComplete="email"
              />
              <input
                data-testid="access-role"
                type="text"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                placeholder="Your role (optional)"
                className="underline-input text-center"
              />
              <button
                data-testid="access-submit"
                type="submit"
                disabled={submitting}
                className="group mt-2 inline-flex items-center justify-center gap-2 self-center mx-auto rounded-full bg-royal text-white px-6 py-3 text-[13px] font-mono-xn shadow-[0_10px_40px_-10px_rgba(76,108,255,0.6)] hover:brightness-110 active:scale-[0.98] transition-all disabled:opacity-50"
              >
                {submitting ? "Sending" : "Request access"}
                <span className="transition-transform group-hover:translate-x-1">
                  →
                </span>
              </button>
            </div>
            <p className="mt-4 text-[10.5px] font-mono-xn text-white/30">
              We never share your email. One message. No follow-ups.
            </p>
          </form>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
            className="mt-8 glass-strong rounded-2xl px-8 py-8 max-w-md mx-auto"
            data-testid="access-confirmation"
          >
            <div className="w-10 h-10 rounded-full bg-royal border border-white/20 flex items-center justify-center mx-auto mb-4 shadow-[0_0_24px_rgba(76,108,255,0.5)]">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.8">
                <path d="M4 12l5 5L20 6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <div className="font-display text-2xl text-white">You&apos;re on the list.</div>
            <p className="mt-3 text-white/50 text-[13.5px] leading-relaxed">
              We will reach out from a human, not a system, when your invitation is ready.
            </p>
          </motion.div>
        )}
      </motion.div>
    </section>
  );
}
