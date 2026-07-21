import { buyingSignals, companyById } from "@/os/data";
import { useOS } from "@/os/OSContext";

export default function BuyingSignals() {
  const { openCompany } = useOS();
  return (
    <div className="p-8" data-testid="module-signals">
      <div className="flex items-center justify-between mb-4">
        <div className="text-[12px] text-white/80">Live feed · updated every minute</div>
        <div className="flex items-center gap-2 text-[11px]">
          <span className="pulse-dot" />
          <span className="text-white/60">Streaming</span>
        </div>
      </div>
      <div className="os-card p-2">
        {buyingSignals.map((s) => {
          const c = companyById(s.company);
          return (
            <button
              key={s.id}
              className="w-full flex items-center gap-4 py-3 px-4 rounded-lg hover:bg-white/[0.03] text-left"
              onClick={() => openCompany(s.company)}
              data-testid={`signal-${s.id}`}
            >
              <div className={`os-strength strength-${s.strength}`} />
              <div className="flex-1">
                <div className="text-[13px] text-white/90">
                  <span className="text-white">{c?.name}</span>
                  <span className="text-white/50"> · {s.label}</span>
                </div>
                <div className="text-[11px] text-white/45 mt-0.5">{s.detail}</div>
              </div>
              <div className="text-[10.5px] font-mono-xn text-white/40">{s.ts}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
