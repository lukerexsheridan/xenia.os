import { activity } from "@/os/data";

const TONE_STYLES = {
  signal: "bg-white",
  draft: "bg-white/70",
  action: "bg-white/50",
  enrich: "bg-white/40",
  learn: "bg-white/60",
};

export default function ActivityFeed() {
  return (
    <div className="p-8" data-testid="module-activity">
      <div className="os-card p-2">
        {activity.map((a) => (
          <div
            key={a.id}
            className="flex items-center gap-4 px-4 py-3 border-b border-white/[0.05] last:border-0"
            data-testid={`activity-${a.id}`}
          >
            <span className="text-[10.5px] font-mono-xn text-white/40 w-16 tabular-nums">
              {a.ts}
            </span>
            <span className={`w-1.5 h-1.5 rounded-full ${TONE_STYLES[a.tone] || "bg-white/60"}`} />
            <div className="text-[13px] text-white/90">
              <span className="text-white">{a.who}</span>{" "}
              <span className="text-white/70">{a.what}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
