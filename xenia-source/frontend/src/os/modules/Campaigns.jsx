import { campaigns } from "@/os/data";

export default function Campaigns() {
  return (
    <div className="p-8" data-testid="module-campaigns">
      <div className="os-table">
        <div className="os-thead grid grid-cols-[1.6fr_0.7fr_0.7fr_0.7fr_0.7fr_0.6fr]">
          <div>Campaign</div>
          <div>Sent</div>
          <div>Opened</div>
          <div>Replied</div>
          <div>Meetings</div>
          <div>Status</div>
        </div>
        {campaigns.map((c) => (
          <div
            key={c.id}
            className="os-trow grid grid-cols-[1.6fr_0.7fr_0.7fr_0.7fr_0.7fr_0.6fr] items-center"
            data-testid={`campaign-${c.id}`}
          >
            <div className="text-white text-[13px]">{c.name}</div>
            <div className="text-white/80 text-[12px] tabular-nums">{c.sent}</div>
            <div className="text-white/80 text-[12px] tabular-nums">
              {c.opened} <span className="text-white/40">· {Math.round((c.opened / c.sent) * 100)}%</span>
            </div>
            <div className="text-white/80 text-[12px] tabular-nums">
              {c.replied} <span className="text-white/40">· {Math.round((c.replied / c.sent) * 100)}%</span>
            </div>
            <div className="text-white/80 text-[12px] tabular-nums">{c.meetings}</div>
            <div>
              <span
                className={`os-pill ${
                  c.status === "Live" ? "os-pill-ok" : c.status === "Draft" ? "os-pill-warn" : "os-pill-muted"
                }`}
              >
                {c.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
