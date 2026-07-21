import { useState } from "react";
import { toast } from "sonner";
import BlackHoleMark from "@/components/BlackHoleMark";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Auto-summarise the current chat into a shareable paragraph.
// Rendered inside the Chat Memory sidebar, below the entity lists.
export default function MemorySummary({ messages }) {
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const hasUserMessage = messages.some((m) => m.from === "user" && m.text.trim());

  const generate = async () => {
    if (!hasUserMessage || loading) return;
    setLoading(true);
    setSummary("");
    try {
      const res = await fetch(`${API}/chat/summarise`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: messages.map((m) => ({ from: m.from, text: m.text })) }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setSummary(data.summary || "");
    } catch (err) {
      toast.error(typeof err?.message === "string" ? err.message : "Couldn't summarise.");
    } finally {
      setLoading(false);
    }
  };

  const copy = async () => {
    if (!summary) return;
    try {
      await navigator.clipboard.writeText(summary);
      toast.success("Copied to clipboard.");
    } catch {
      toast.error("Copy failed.");
    }
  };

  const share = async () => {
    if (!summary) return;
    if (typeof navigator.share === "function") {
      try {
        await navigator.share({ title: "Xenia session summary", text: summary });
      } catch {
        /* user cancelled */
      }
    } else {
      copy();
    }
  };

  return (
    <div className="mt-1" data-testid="memory-summary">
      <div className="text-[9.5px] font-mono-xn tracking-widest text-white/30 mb-2">
        Highlights
      </div>

      {!summary && !loading && (
        <button
          data-testid="memory-summarise"
          onClick={generate}
          disabled={!hasUserMessage}
          className="w-full inline-flex items-center justify-center gap-2 rounded-full bg-royal text-white px-3 py-2 text-[11.5px] font-mono-xn shadow-[0_6px_24px_-8px_rgba(76,108,255,0.55)] hover:brightness-110 active:scale-[0.98] transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          title={hasUserMessage ? "Distil this session into a paragraph" : "Say something first"}
        >
          Summarise session
        </button>
      )}

      {loading && (
        <div className="flex items-center gap-2 px-2 py-2 text-[12px] text-white/60">
          <BlackHoleMark size={14} />
          <span className="font-mono-xn text-[11px] tracking-wider">Distilling…</span>
        </div>
      )}

      {summary && !loading && (
        <div data-testid="memory-summary-result" className="space-y-2">
          <div className="text-[12.5px] leading-relaxed text-white/80 bg-white/[0.03] border border-white/[0.06] rounded-lg p-3">
            {summary}
          </div>
          <div className="flex items-center gap-2">
            <button
              data-testid="memory-summary-copy"
              onClick={copy}
              className="flex-1 text-[10.5px] font-mono-xn text-white/60 hover:text-white rounded-full border border-white/10 hover:border-white/25 px-3 py-1.5 transition-colors"
            >
              Copy
            </button>
            <button
              data-testid="memory-summary-share"
              onClick={share}
              className="flex-1 text-[10.5px] font-mono-xn text-white/60 hover:text-white rounded-full border border-white/10 hover:border-white/25 px-3 py-1.5 transition-colors"
            >
              Share
            </button>
            <button
              data-testid="memory-summary-regen"
              onClick={generate}
              className="text-[10.5px] font-mono-xn text-white/40 hover:text-white/80 transition-colors"
              title="Regenerate"
            >
              ↻
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
