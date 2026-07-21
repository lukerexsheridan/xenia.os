import { reports } from "@/os/data";

export default function Reports() {
  return (
    <div className="p-8 grid grid-cols-2 gap-4" data-testid="module-reports">
      {reports.map((r) => (
        <div key={r.id} className="os-card p-5" data-testid={`report-${r.id}`}>
          <div className="text-[10.5px] font-mono-xn text-white/40">{r.period}</div>
          <div className="font-display text-xl text-white mt-1">{r.name}</div>
          <div className="mt-4 text-[12px] text-white/60">
            {r.insights} insights · compiled by Xenia
          </div>
          <div className="mt-4 flex items-center gap-2">
            <button className="os-ghost">Open</button>
            <button className="os-ghost">Export PDF</button>
          </div>
        </div>
      ))}
    </div>
  );
}
