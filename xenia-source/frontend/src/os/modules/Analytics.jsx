import { analyticsSeries } from "@/os/data";

// Minimal but real chart drawn with inline SVG.
function LineChart({ series, color = "#ffffff", label }) {
  const w = 520;
  const h = 140;
  const pad = 12;
  const max = Math.max(...series);
  const step = (w - pad * 2) / (series.length - 1);
  const points = series
    .map((v, i) => `${pad + i * step},${h - pad - (v / max) * (h - pad * 2)}`)
    .join(" ");
  const areaPoints = `${pad},${h - pad} ${points} ${pad + (series.length - 1) * step},${h - pad}`;

  return (
    <div className="os-card p-5">
      <div className="text-[11px] font-mono-xn text-white/40 mb-1">{label}</div>
      <div className="font-display text-3xl text-white">{series[series.length - 1]}</div>
      <div className="text-[11px] text-white/45 mt-1">
        +{Math.round(((series[series.length - 1] - series[0]) / series[0]) * 100)}% · 12 weeks
      </div>
      <svg width="100%" viewBox={`0 0 ${w} ${h}`} className="mt-4">
        <polygon points={areaPoints} fill="url(#areaFill)" opacity="0.18" />
        <defs>
          <linearGradient id="areaFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.9" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
        <polyline points={points} fill="none" stroke={color} strokeWidth="1.5" />
        {series.map((v, i) => (
          <circle
            key={i}
            cx={pad + i * step}
            cy={h - pad - (v / max) * (h - pad * 2)}
            r="2"
            fill={color}
            opacity="0.7"
          />
        ))}
      </svg>
    </div>
  );
}

export default function Analytics() {
  return (
    <div className="p-8 grid gap-5" data-testid="module-analytics">
      <div className="grid grid-cols-4 gap-3">
        <KPI k="Reply rate" v="23.4%" delta="+4.1 pt" />
        <KPI k="Meetings booked" v="12" delta="+2 wk" />
        <KPI k="Avg. thread length" v="3.2" delta="+0.4" />
        <KPI k="Deals influenced" v="€1.8M" delta="+€420k" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <LineChart series={analyticsSeries.replies} label="Replies · weekly" />
        <LineChart series={analyticsSeries.meetings} label="Meetings · weekly" />
      </div>
    </div>
  );
}

function KPI({ k, v, delta }) {
  return (
    <div className="os-card p-4">
      <div className="text-[10.5px] font-mono-xn text-white/40">{k}</div>
      <div className="font-display text-2xl text-white mt-2 tabular-nums">{v}</div>
      <div className="text-[11px] text-white/50 mt-1">{delta}</div>
    </div>
  );
}
