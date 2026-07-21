import { useState } from "react";
import { companies, companyById } from "@/os/data";

export default function AIResearch() {
  const [selected, setSelected] = useState(companies[0].id);
  const c = companyById(selected);

  return (
    <div className="p-8 grid grid-cols-[240px_1fr] gap-6" data-testid="module-research">
      <aside>
        <div className="text-[10px] font-mono-xn text-white/40 mb-2 px-1">Files</div>
        <div className="flex flex-col">
          {companies.slice(0, 8).map((x) => (
            <button
              key={x.id}
              onClick={() => setSelected(x.id)}
              className={`text-left px-3 py-2 rounded-md text-[12.5px] ${
                selected === x.id ? "bg-white/[0.06] text-white" : "text-white/60 hover:text-white/90"
              }`}
              data-testid={`research-file-${x.id}`}
            >
              {x.name}
            </button>
          ))}
        </div>
      </aside>

      <div className="os-card p-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-[10.5px] font-mono-xn text-white/40">
              Research file · {c.hq}
            </div>
            <div className="font-display text-2xl mt-1 text-white">{c.name}</div>
          </div>
          <div className="text-[10.5px] font-mono-xn text-white/40">
            Compiled 4m ago · 12 sources
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 mt-6">
          <div className="os-stat">
            <div className="text-[10px] font-mono-xn text-white/40">ICP fit</div>
            <div className="text-white text-[13px] mt-1">{c.icp}%</div>
          </div>
          <div className="os-stat">
            <div className="text-[10px] font-mono-xn text-white/40">Buying score</div>
            <div className="text-white text-[13px] mt-1">
              {Math.round((c.signals[0]?.weight || 0.4) * 100)}
            </div>
          </div>
          <div className="os-stat">
            <div className="text-[10px] font-mono-xn text-white/40">Stack fit</div>
            <div className="text-white text-[13px] mt-1">{c.stack.length} matches</div>
          </div>
        </div>

        <Section title="Summary">
          <p className="text-[13px] leading-relaxed text-white/75">
            {c.name} operates in {c.industry.toLowerCase()} out of {c.hq}. With {c.employees}{" "}
            employees and reported ARR of {c.arr}, they sit within our ideal customer profile.
            Xenia surfaced {c.signals.length} recent buying signals worth reviewing, most
            notably {c.signals[0]?.label.toLowerCase() || "no major signals yet"}.
          </p>
        </Section>

        <Section title="Signals">
          {c.signals.map((s) => (
            <div key={s.id} className="flex items-center gap-3 py-2 border-b border-white/[0.05] last:border-0">
              <span className="w-1.5 h-1.5 rounded-full bg-white" style={{ opacity: 0.4 + s.weight * 0.6 }} />
              <span className="text-[13px] text-white/90">{s.label}</span>
              <span className="ml-auto text-[10.5px] font-mono-xn text-white/35">{s.ts}</span>
            </div>
          ))}
        </Section>

        <Section title="Technology stack">
          <div className="flex flex-wrap gap-2">
            {c.stack.map((s) => (
              <span key={s} className="os-pill">{s}</span>
            ))}
          </div>
        </Section>

        <Section title="Recent news">
          {c.news.length === 0 ? (
            <div className="text-white/40 text-[12px]">Nothing above the fold.</div>
          ) : (
            c.news.map((n, i) => (
              <div key={i} className="py-2">
                <div className="text-[13px] text-white/85">{n.title}</div>
                <div className="text-[10.5px] font-mono-xn text-white/35 mt-0.5">{n.src}</div>
              </div>
            ))
          )}
        </Section>
      </div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="mt-8">
      <div className="text-[10px] font-mono-xn text-white/40 mb-2">{title}</div>
      {children}
    </div>
  );
}
