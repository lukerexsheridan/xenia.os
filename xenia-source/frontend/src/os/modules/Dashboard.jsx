import { buyingSignals, campaigns, activity, companyById } from "@/os/data";
import { useOS } from "@/os/OSContext";

export default function Dashboard() {
  const { openCompany, setActiveModule } = useOS();
  const kpis = [
    { k: "Signals surfaced · today", v: "342", delta: "+18%" },
    { k: "Reply rate · 30d", v: "23.4%", delta: "+4.1 pt" },
    { k: "Meetings booked · 7d", v: "12", delta: "+2" },
    { k: "New qualified · 7d", v: "27", delta: "+9" },
  ];

  return (
    <div className="p-8 grid gap-6" data-testid="module-dashboard">
      <div>
        <div className="text-[11px] font-mono-xn text-white/40 mb-2">Good evening, Sara</div>
        <div className="font-display text-2xl text-white">
          Xenia surfaced <span className="text-white">8</span> high-signal opportunities while you were away.
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        {kpis.map((k) => (
          <div key={k.k} className="os-card p-4">
            <div className="text-[10.5px] font-mono-xn text-white/40">{k.k}</div>
            <div className="font-display text-2xl mt-2 text-white tabular-nums">{k.v}</div>
            <div className="text-[11px] text-white/50 mt-1">{k.delta}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 os-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="text-[12px] text-white">Top buying signals right now</div>
            <button
              className="text-[10.5px] font-mono-xn text-white/40 hover:text-white/80"
              onClick={() => setActiveModule("signals")}
            >
              See all →
            </button>
          </div>
          <div>
            {buyingSignals.slice(0, 5).map((s) => {
              const c = companyById(s.company);
              return (
                <button
                  key={s.id}
                  onClick={() => openCompany(s.company)}
                  className="w-full grid grid-cols-[16px_1fr_auto_auto] items-center gap-3 py-2 border-b border-white/[0.05] last:border-0 hover:bg-white/[0.02] px-2 -mx-2 rounded-md text-left"
                  data-testid={`dash-signal-${s.id}`}
                >
                  <span
                    className="w-1.5 h-1.5 rounded-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)]"
                    style={{ opacity: s.strength === "high" ? 0.95 : 0.6 }}
                  />
                  <div className="text-[13px] text-white/90 truncate">
                    <span className="text-white">{c?.name}</span>
                    <span className="text-white/45"> · {s.label}</span>
                  </div>
                  <span className="text-[11px] text-white/45">{s.detail}</span>
                  <span className="text-[10.5px] font-mono-xn text-white/35 w-14 text-right">
                    {s.ts}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="os-card p-5">
          <div className="text-[12px] text-white mb-4">Live campaigns</div>
          <div className="space-y-3">
            {campaigns.slice(0, 3).map((c) => (
              <div key={c.id}>
                <div className="flex items-center justify-between text-[12px]">
                  <span className="text-white/85">{c.name}</span>
                  <span className="text-white/40 tabular-nums">
                    {c.replied}/{c.sent}
                  </span>
                </div>
                <div className="os-bar mt-1.5">
                  <div className="os-bar-fill" style={{ width: `${(c.replied / c.sent) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="os-card p-5">
          <div className="text-[12px] text-white mb-3">Xenia's activity · last hours</div>
          <div>
            {activity.slice(0, 5).map((a) => (
              <div key={a.id} className="flex items-center gap-3 py-2 border-b border-white/[0.05] last:border-0">
                <span className="w-1 h-1 rounded-full bg-white/70" />
                <span className="text-[10.5px] font-mono-xn text-white/40 w-14">{a.ts}</span>
                <span className="text-[12.5px] text-white/85">
                  <span className="text-white">{a.who}</span> {a.what}
                </span>
              </div>
            ))}
          </div>
        </div>
        <div className="os-card p-5">
          <div className="text-[12px] text-white mb-3">Watchlist</div>
          <div className="grid grid-cols-2 gap-2">
            {["c-northlake", "c-solstice", "c-orbit", "c-vessel"].map((id) => {
              const c = companyById(id);
              return (
                <button
                  key={id}
                  onClick={() => openCompany(id)}
                  className="os-card-sm p-3 text-left"
                  data-testid={`watch-${id}`}
                >
                  <div className="text-[13px] text-white">{c.name}</div>
                  <div className="text-[10.5px] font-mono-xn text-white/40 mt-1">
                    ICP {c.icp}% · {c.stage}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
