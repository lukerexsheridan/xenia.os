import { companies } from "@/os/data";
import { useOS } from "@/os/OSContext";

export default function Companies() {
  const { openCompany } = useOS();
  return (
    <div className="p-8" data-testid="module-companies">
      <div className="grid grid-cols-3 gap-4">
        {companies.map((c) => (
          <button
            key={c.id}
            onClick={() => openCompany(c.id)}
            className="os-card p-5 text-left hover:border-white/20 transition-colors group"
            data-testid={`company-${c.id}`}
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="text-[10.5px] font-mono-xn text-white/40">
                  {c.industry}
                </div>
                <div className="font-display text-lg text-white mt-1">{c.name}</div>
              </div>
              <div className="text-[10.5px] font-mono-xn text-white/40">
                ICP {c.icp}%
              </div>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-2 text-[12px]">
              <div>
                <div className="text-[10px] font-mono-xn text-white/35">HQ</div>
                <div className="text-white/85">{c.hq}</div>
              </div>
              <div>
                <div className="text-[10px] font-mono-xn text-white/35">Employees</div>
                <div className="text-white/85 tabular-nums">{c.employees}</div>
              </div>
              <div>
                <div className="text-[10px] font-mono-xn text-white/35">Stage</div>
                <div className="text-white/85">{c.stage}</div>
              </div>
              <div>
                <div className="text-[10px] font-mono-xn text-white/35">ARR</div>
                <div className="text-white/85">{c.arr}</div>
              </div>
            </div>
            {c.signals[0] && (
              <div className="mt-4 pt-3 border-t border-white/[0.05] flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-white/80 shadow-[0_0_8px_rgba(255,255,255,0.6)]" />
                <span className="text-[11.5px] text-white/75 truncate">
                  {c.signals[0].label}
                </span>
                <span className="ml-auto text-[10.5px] font-mono-xn text-white/35">
                  {c.signals[0].ts}
                </span>
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
