import { useState, useRef, useEffect, useMemo } from "react";
import BlackHoleMark from "@/components/BlackHoleMark";
import { extractMemory } from "@/os/chatMemory";
import MemorySummary from "@/os/MemorySummary";
import { useOS } from "@/os/OSContext";
import { companyById } from "@/os/data";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SEED = [
  {
    from: "xenia",
    text: "Good evening, Sara. I have the last 72 hours of activity ready. Ask for a briefing, an outreach draft, or a meeting slot — I'll answer live.",
  },
];

const SUGGESTIONS = [
  "Give me a briefing",
  "Draft outreach to Northlake",
  "Where's my next best meeting?",
];

// Stable session id per browser so multi-turn context accumulates in the backend.
function getSessionId() {
  const KEY = "xenia.chat.session";
  let id = localStorage.getItem(KEY);
  if (!id) {
    id = `xn-chat-${Math.random().toString(36).slice(2, 10)}-${Date.now()}`;
    localStorage.setItem(KEY, id);
  }
  return id;
}

export default function AIChat() {
  const { openCompany } = useOS();
  const [msgs, setMsgs] = useState(SEED);
  const [q, setQ] = useState("");
  const [streaming, setStreaming] = useState(false);
  const listRef = useRef();
  const abortRef = useRef();
  const sessionRef = useRef(getSessionId());

  const memory = useMemo(() => extractMemory(msgs), [msgs]);

  const resetConversation = () => {
    abortRef.current?.abort();
    // Fresh session so Claude context resets server-side too.
    const id = `xn-chat-${Math.random().toString(36).slice(2, 10)}-${Date.now()}`;
    localStorage.setItem("xenia.chat.session", id);
    sessionRef.current = id;
    setMsgs(SEED);
    setQ("");
    setStreaming(false);
  };

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [msgs]);

  const send = async (text) => {
    const outgoing = (text ?? q).trim();
    if (!outgoing || streaming) return;
    setQ("");
    setMsgs((m) => [...m, { from: "user", text: outgoing }]);
    // Append a placeholder xenia message that will fill in as tokens stream
    setMsgs((m) => [...m, { from: "xenia", text: "" }]);
    setStreaming(true);

    const controller = new AbortController();
    abortRef.current = controller;
    let accumulated = "";
    try {
      const res = await fetch(`${API}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionRef.current, text: outgoing }),
        signal: controller.signal,
      });
      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";
        for (const part of parts) {
          const lines = part.split("\n");
          let evType = "message";
          let dataLine = "";
          for (const line of lines) {
            if (line.startsWith("event: ")) evType = line.slice(7).trim();
            else if (line.startsWith("data: ")) dataLine += line.slice(6);
          }
          if (evType === "done") break;
          if (evType === "error") throw new Error(dataLine || "Chat stream failed");
          if (dataLine) {
            accumulated += dataLine;
            setMsgs((m) => {
              const copy = [...m];
              copy[copy.length - 1] = { from: "xenia", text: accumulated };
              return copy;
            });
          }
        }
      }
    } catch (err) {
      if (err?.name !== "AbortError") {
        setMsgs((m) => {
          const copy = [...m];
          const last = copy[copy.length - 1];
          copy[copy.length - 1] = {
            from: "xenia",
            text:
              (last?.text || "") +
              (last?.text ? "" : "Xenia couldn't reach the model just now."),
          };
          return copy;
        });
      }
    } finally {
      setStreaming(false);
    }
  };

  return (
    <div className="p-8 h-full flex gap-6 min-h-0" data-testid="module-chat">
      <div className="flex-1 flex flex-col min-w-0">
        <div ref={listRef} className="flex-1 os-card p-6 overflow-y-auto space-y-4">
        {msgs.map((m, i) => (
          <div
            key={i}
            className={`flex gap-3 ${m.from === "user" ? "flex-row-reverse" : ""}`}
          >
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-mono-xn shrink-0 ${
                m.from === "xenia"
                  ? "bg-transparent"
                  : "bg-white/[0.08] text-white"
              }`}
            >
              {m.from === "xenia" ? <BlackHoleMark size={22} /> : "SN"}
            </div>
            <div
              className={`max-w-[75%] px-4 py-3 rounded-2xl text-[13.5px] leading-relaxed whitespace-pre-wrap ${
                m.from === "xenia"
                  ? "bg-white/[0.03] text-white/90"
                  : "bg-royal text-white"
              }`}
            >
              {m.text || (
                <span className="inline-flex items-center gap-2 text-white/50">
                  <BlackHoleMark size={12} />
                  <span className="text-[11.5px] font-mono-xn tracking-wider">Xenia is thinking…</span>
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {msgs.length <= 1 && !streaming && (
        <div className="mt-3 flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              className="os-chip"
              data-testid={`chat-suggest-${s.split(" ")[0].toLowerCase()}`}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="mt-4 os-card p-3 flex items-center gap-3">
        <input
          className="flex-1 bg-transparent border-0 outline-none text-white placeholder:text-white/35 text-[13.5px] px-2"
          placeholder="Ask Xenia anything about your pipeline"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          disabled={streaming}
          data-testid="chat-input"
        />
        <button
          onClick={() => send()}
          className="os-cta"
          disabled={streaming}
          data-testid="chat-send"
        >
          {streaming ? (
            <span className="inline-flex items-center gap-2">
              <BlackHoleMark size={12} />
              Streaming
            </span>
          ) : (
            "Send →"
          )}
        </button>
      </div>
      <div className="mt-2 text-right text-[10px] font-mono-xn text-white/30">
        {streaming ? "live · claude sonnet 4.6" : "multi-turn · claude sonnet 4.6"}
      </div>
      </div>

      {/* Chat Memory sidebar — what Xenia has picked up this session */}
      <aside
        className="hidden lg:flex flex-col w-[240px] shrink-0 os-card p-5 gap-4 overflow-y-auto"
        data-testid="chat-memory-panel"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BlackHoleMark size={16} />
            <div className="text-[10px] font-mono-xn tracking-widest text-white/45 uppercase">
              Xenia remembers
            </div>
          </div>
          <button
            data-testid="chat-memory-clear"
            onClick={resetConversation}
            className="text-[10px] font-mono-xn text-white/35 hover:text-white/70 transition-colors"
            title="Reset conversation and memory"
          >
            clear
          </button>
        </div>

        {memory.companies.length === 0 && memory.contacts.length === 0 && memory.topics.length === 0 ? (
          <div className="text-[12px] leading-relaxed text-white/40">
            Nothing yet. Xenia will surface the companies, people, and topics you mention here as we go.
          </div>
        ) : (
          <>
            {memory.companies.length > 0 && (
              <div data-testid="memory-companies">
                <div className="text-[9.5px] font-mono-xn tracking-widest text-white/30 mb-2">
                  Companies
                </div>
                <div className="space-y-1.5">
                  {memory.companies.map((c) => {
                    const known = companyById(c.id);
                    return (
                      <button
                        key={c.id}
                        onClick={() => known && openCompany(c.id)}
                        className="w-full text-left flex items-center justify-between gap-2 px-2 py-1.5 rounded hover:bg-white/[0.04] transition-colors"
                        data-testid={`memory-co-${c.id}`}
                      >
                        <div className="min-w-0">
                          <div className="text-[12.5px] text-white truncate">{c.name}</div>
                          <div className="text-[10px] text-white/40 truncate">{c.industry}</div>
                        </div>
                        <span className="text-[10px] font-mono-xn text-white/35 shrink-0">
                          ×{c.mentions}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {memory.contacts.length > 0 && (
              <div data-testid="memory-contacts">
                <div className="text-[9.5px] font-mono-xn tracking-widest text-white/30 mb-2">
                  People
                </div>
                <div className="space-y-1.5">
                  {memory.contacts.map((p) => (
                    <div
                      key={p.id}
                      className="flex items-center justify-between gap-2 px-2 py-1"
                      data-testid={`memory-p-${p.id}`}
                    >
                      <div className="text-[12.5px] text-white truncate">{p.name}</div>
                      <span className="text-[10px] font-mono-xn text-white/35 shrink-0">
                        ×{p.mentions}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {memory.topics.length > 0 && (
              <div data-testid="memory-topics">
                <div className="text-[9.5px] font-mono-xn tracking-widest text-white/30 mb-2">
                  Topics
                </div>
                <ul className="space-y-1.5">
                  {memory.topics.map((t, i) => (
                    <li
                      key={t + i}
                      className="flex items-start gap-2 text-[12px] text-white/70 leading-snug"
                    >
                      <span className="mt-1.5 w-1 h-1 rounded-full bg-[color:var(--xn-royal-2)] shrink-0" />
                      <span className="min-w-0 flex-1">{t}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <MemorySummary messages={msgs} />
          </>
        )}
      </aside>
    </div>
  );
}
