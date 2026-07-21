import { modules } from "@/os/data";
import { useOS } from "@/os/OSContext";
import BlackHoleMark from "@/components/BlackHoleMark";

// Grouped for hierarchy
const GROUPS = [
  { title: "Work", ids: ["dashboard", "tasks", "pipeline"] },
  { title: "Intelligence", ids: ["signals", "research", "companies", "contacts", "leads"] },
  { title: "Outreach", ids: ["campaigns", "email", "chat"] },
  { title: "Insights", ids: ["analytics", "reports", "activity"] },
  { title: "System", ids: ["team", "integrations", "notifications", "settings"] },
];

export default function Sidebar() {
  const { activeModule, setActiveModule } = useOS();

  return (
    <aside className="os-sidebar" data-testid="os-sidebar">
      <div className="px-4 pt-5 pb-3 flex items-center gap-2.5">
        <BlackHoleMark size={20} />
        <span className="font-display text-[15px] tracking-tight text-white">Xenia</span>
      </div>
      <div className="px-3 pb-2">
        <div className="os-search text-[12px] flex items-center gap-2">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="7" />
            <path d="M20 20l-3.5-3.5" strokeLinecap="round" />
          </svg>
          <span className="text-white/40">Search everything</span>
          <span className="ml-auto text-white/30 text-[10px] font-mono-xn">⌘K</span>
        </div>
      </div>

      <nav className="px-2 pt-2 pb-4 flex-1 overflow-y-auto">
        {GROUPS.map((g) => (
          <div key={g.title} className="mt-4 first:mt-0">
            <div className="px-3 pb-1.5 text-[10px] font-mono-xn text-white/30">
              {g.title}
            </div>
            {g.ids.map((id) => {
              const m = modules.find((x) => x.id === id);
              if (!m) return null;
              const active = activeModule === id;
              return (
                <button
                  key={id}
                  data-testid={`nav-${id}`}
                  onClick={() => setActiveModule(id)}
                  className={`os-nav-item ${active ? "os-nav-active" : ""}`}
                >
                  <span className="os-nav-dot" />
                  <span>{m.label}</span>
                  {id === "notifications" && (
                    <span className="ml-auto text-[10px] text-white/50 tabular-nums">5</span>
                  )}
                  {id === "signals" && (
                    <span className="ml-auto text-[10px] text-white/50 tabular-nums">8</span>
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="px-3 py-3 border-t border-white/[0.06] flex items-center gap-2">
        <div className="w-7 h-7 rounded-full bg-white/[0.08] flex items-center justify-center text-[11px] font-mono-xn">
          SN
        </div>
        <div className="text-[12px] leading-tight">
          <div className="text-white">Sara Ndiaye</div>
          <div className="text-white/40 text-[10.5px]">Managing Director</div>
        </div>
      </div>
    </aside>
  );
}
