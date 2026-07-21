import { useOS } from "@/os/OSContext";
import { companyById, contactById } from "@/os/data";

export default function CompanyDetail() {
  const { selectedCompany, closeCompany, draftFor } = useOS();
  const c = companyById(selectedCompany);
  if (!c) return null;

  return (
    <div
      className="os-detail-backdrop"
      onClick={closeCompany}
      data-testid="company-detail"
    >
      <aside
        className="os-detail"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-5 border-b border-white/[0.06]">
          <div>
            <div className="text-[10.5px] font-mono-xn text-white/40">
              {c.industry} · {c.hq}
            </div>
            <div className="font-display text-2xl text-white mt-1">{c.name}</div>
          </div>
          <button
            onClick={closeCompany}
            className="os-icon-btn"
            data-testid="company-detail-close"
            aria-label="Close"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M6 6l12 12M18 6L6 18" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        <div className="px-6 py-5 overflow-y-auto flex-1">
          <div className="grid grid-cols-3 gap-3 text-[12px]">
            <Stat k="ICP fit" v={`${c.icp}%`} />
            <Stat k="Employees" v={c.employees} />
            <Stat k="ARR" v={c.arr} />
            <Stat k="Stage" v={c.stage} />
            <Stat k="Owner" v={c.owner} />
            <Stat k="Stack" v={c.stack.slice(0, 3).join(" · ")} />
          </div>

          <Section title="Buying signals">
            {c.signals.length === 0 && (
              <div className="text-white/40 text-[12px]">No signals yet.</div>
            )}
            {c.signals.map((s) => (
              <div
                key={s.id}
                className="flex items-center gap-3 py-2 border-b border-white/[0.05] last:border-0"
              >
                <span
                  className="w-1.5 h-1.5 rounded-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)]"
                  style={{ opacity: 0.4 + s.weight * 0.6 }}
                />
                <div className="text-[13px] text-white/90">{s.label}</div>
                <div className="ml-auto text-[10.5px] font-mono-xn text-white/35">
                  {s.ts}
                </div>
              </div>
            ))}
          </Section>

          <Section title="Recent news">
            {c.news.length === 0 && (
              <div className="text-white/40 text-[12px]">Nothing this week.</div>
            )}
            {c.news.map((n, i) => (
              <div key={i} className="py-2">
                <div className="text-[13px] text-white/85">{n.title}</div>
                <div className="text-[10.5px] font-mono-xn text-white/35 mt-0.5">
                  {n.src}
                </div>
              </div>
            ))}
          </Section>

          <Section title="Decision makers">
            {c.contacts.length === 0 && (
              <div className="text-white/40 text-[12px]">Xenia is enriching…</div>
            )}
            {c.contacts.map((id) => {
              const p = contactById(id);
              if (!p) return null;
              return (
                <div
                  key={id}
                  className="flex items-center gap-3 py-2 border-b border-white/[0.05] last:border-0"
                  data-testid={`detail-contact-${id}`}
                >
                  <div className="w-7 h-7 rounded-full bg-white/[0.06] flex items-center justify-center text-[10px] font-mono-xn">
                    {p.name.split(" ").map((x) => x[0]).slice(0, 2).join("")}
                  </div>
                  <div className="text-[13px]">
                    <div className="text-white">{p.name}</div>
                    <div className="text-white/40 text-[11px]">{p.title}</div>
                  </div>
                  <button
                    className="ml-auto os-mini-cta"
                    onClick={() => draftFor(c.id, p.id)}
                    data-testid={`detail-draft-${id}`}
                  >
                    Draft →
                  </button>
                </div>
              );
            })}
          </Section>
        </div>

        <div className="px-6 py-4 border-t border-white/[0.06] flex items-center gap-3">
          <button
            className="os-cta"
            onClick={() => draftFor(c.id)}
            data-testid="detail-draft-outreach"
          >
            Draft outreach →
          </button>
          <button className="os-ghost">Add to campaign</button>
          <div className="ml-auto text-[10.5px] font-mono-xn text-white/30">
            Enriched 4m ago
          </div>
        </div>
      </aside>
    </div>
  );
}

function Stat({ k, v }) {
  return (
    <div className="os-stat">
      <div className="text-[10px] font-mono-xn text-white/40">{k}</div>
      <div className="text-white text-[13px] mt-1">{v}</div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="mt-8">
      <div className="text-[10px] font-mono-xn text-white/40 mb-3">{title}</div>
      {children}
    </div>
  );
}
