import { useMemo, useState, useRef } from "react";
import { useOS } from "@/os/OSContext";
import { companyById, contactById, contacts as ALL_CONTACTS } from "@/os/data";
import BlackHoleMark from "@/components/BlackHoleMark";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Realistic outreach draft with a "reasoning" panel showing why Xenia wrote every line.
export default function EmailWriter() {
  const { draftContext } = useOS();
  const initialCompany = draftContext?.companyId || "c-northlake";
  const initialContactId =
    draftContext?.contactId ||
    ALL_CONTACTS.find((p) => p.company === initialCompany)?.id ||
    "p-amelia";

  const [companyId, setCompanyId] = useState(initialCompany);
  const [contactId, setContactId] = useState(initialContactId);
  const [tone, setTone] = useState("Reserved");
  const [aiBody, setAiBody] = useState("");
  const [generating, setGenerating] = useState(false);
  const abortRef = useRef();

  const c = companyById(companyId);
  const p = contactById(contactId);

  const subject = useMemo(() => {
    if (!c) return "";
    const s = c.signals[0]?.label || "the opportunity ahead";
    return `Re: ${s} — a thought`;
  }, [c]);

  const staticBody = useMemo(() => {
    if (!c || !p) return "";
    const first = p.name.split(" ")[0];
    const signal = c.signals[0]?.label || "your recent traction";
    const stack = c.stack.slice(0, 2).join(" and ");
    const openings = {
      Reserved: `${first} — congratulations on ${signal.toLowerCase()}. Quietly watching, but couldn't resist reaching out.`,
      Direct: `${first} — saw ${signal.toLowerCase()}. That's a meaningful moment.`,
      Warm: `${first} — genuine congratulations on ${signal.toLowerCase()}. It's been a joy watching ${c.name} from the outside.`,
    };
    return `${openings[tone]}

Two of our agency clients hit the same inflection point you're about to encounter — the pipeline strain when a ${stack}-heavy team scales from ${c.employees} to roughly 2x that headcount within 18 months.

If it's useful, I can share the exact playbook we used with them (nothing to sell, just the working notes). No calendar link, no attachment — just reply "send it" and I will.

— Sara`;
  }, [c, p, tone]);

  const body = aiBody || staticBody;

  const regenerate = async () => {
    if (!c || !p || generating) return;
    setGenerating(true);
    setAiBody("");
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch(`${API}/email/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_name: c.name,
          industry: c.industry,
          hq: c.hq,
          employees: c.employees,
          stack: c.stack,
          recent_signal: c.signals[0]?.label || null,
          contact_name: p.name,
          contact_title: p.title,
          tone,
          sender_name: "Sara",
        }),
        signal: controller.signal,
      });
      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let accumulated = "";
      // Parse SSE stream — each event is "data: <chunk>\n\n" or "event: done/error\ndata: ...".
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
          if (evType === "done") {
            // finish
          } else if (evType === "error") {
            throw new Error(dataLine || "Generation failed");
          } else if (dataLine) {
            accumulated += dataLine;
            setAiBody(accumulated);
          }
        }
      }
    } catch (err) {
      if (err?.name !== "AbortError") {
        setAiBody(staticBody + "\n\n[Xenia couldn't reach the model just now.]");
      }
    } finally {
      setGenerating(false);
    }
  };

  const reasons = useMemo(() => {
    if (!c || !p) return [];
    return [
      { label: "Opening references", value: c.signals[0]?.label || "no recent signal" },
      { label: "Stack cited", value: c.stack.slice(0, 2).join(", ") },
      { label: "Headcount context", value: `${c.employees} employees today` },
      { label: "Tone", value: tone },
      { label: "Ask", value: 'Zero-friction reply ("send it")' },
      { label: "Author", value: aiBody ? "Claude Sonnet 4.6 · live" : "Xenia · template" },
      { label: "Confidence", value: "82%" },
    ];
  }, [c, p, tone, aiBody]);

  return (
    <div className="p-8 grid grid-cols-[1fr_320px] gap-6" data-testid="module-email">
      <div>
        <div className="os-card p-6">
          <div className="grid grid-cols-3 gap-3 mb-6">
            <Field label="To">
              <select
                value={contactId}
                onChange={(e) => setContactId(e.target.value)}
                className="os-select"
                data-testid="email-contact"
              >
                {ALL_CONTACTS.filter((x) => x.company === companyId).map((x) => {
                  const label = `${x.name} — ${x.title}`;
                  return (
                    <option key={x.id} value={x.id}>{label}</option>
                  );
                })}
              </select>
            </Field>
            <Field label="Company">
              <select
                value={companyId}
                onChange={(e) => {
                  setCompanyId(e.target.value);
                  const first = ALL_CONTACTS.find((x) => x.company === e.target.value);
                  if (first) setContactId(first.id);
                }}
                className="os-select"
                data-testid="email-company"
              >
                {[...new Set(ALL_CONTACTS.map((x) => x.company))].map((cid) => {
                  const label = companyById(cid)?.name || cid;
                  return (
                    <option key={cid} value={cid}>{label}</option>
                  );
                })}
              </select>
            </Field>
            <Field label="Tone">
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="os-select"
                data-testid="email-tone"
              >
                <option>Reserved</option>
                <option>Direct</option>
                <option>Warm</option>
              </select>
            </Field>
          </div>

          <div className="border-t border-white/[0.06] pt-5">
            <div className="text-[10px] font-mono-xn text-white/40 mb-1">Subject</div>
            <div className="text-white text-[15px]">{subject}</div>
          </div>

          <pre className="whitespace-pre-wrap text-white/85 text-[13.5px] leading-[1.7] mt-6 font-sans">
            {body}
          </pre>

          <div className="flex items-center gap-3 mt-6 pt-5 border-t border-white/[0.06]">
            <button className="os-cta" data-testid="email-approve">
              Approve &amp; queue
            </button>
            <button
              className="os-ghost"
              onClick={() => setAiBody("")}
              data-testid="email-revise"
            >
              Reset to template
            </button>
            <button
              className="os-ghost"
              onClick={regenerate}
              disabled={generating}
              data-testid="email-regenerate"
            >
              {generating ? (
                <span className="inline-flex items-center gap-2">
                  <BlackHoleMark size={14} />
                  Xenia is writing…
                </span>
              ) : (
                "Regenerate with AI ↻"
              )}
            </button>
            <div className="ml-auto text-[10.5px] font-mono-xn text-white/40">
              {aiBody ? "live · claude sonnet 4.6" : "draft · 1.2s"}
            </div>
          </div>
        </div>
      </div>

      <div className="os-card p-5" data-testid="email-reasoning">
        <div className="text-[10px] font-mono-xn text-white/40 mb-3">Why Xenia wrote this</div>
        {reasons.map((r, i) => (
          <div key={i} className="flex items-start gap-3 py-2.5 border-b border-white/[0.05] last:border-0">
            <div className="text-[10.5px] font-mono-xn text-white/40 w-24 shrink-0">
              {r.label}
            </div>
            <div className="text-[12.5px] text-white/85">{r.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <div>
      <div className="text-[10px] font-mono-xn text-white/40 mb-1.5">{label}</div>
      {children}
    </div>
  );
}
