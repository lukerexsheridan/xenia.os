import { useState } from "react";
import { companies, pipelineStages } from "@/os/data";
import { useOS } from "@/os/OSContext";

export default function Leads() {
  const { openCompany } = useOS();
  const [filter, setFilter] = useState("all");
  const filtered =
    filter === "all"
      ? companies
      : companies.filter((c) => c.stage === filter);

  return (
    <div className="p-8" data-testid="module-leads">
      <div className="flex items-center gap-2 mb-5">
        <button
          onClick={() => setFilter("all")}
          className={`os-chip ${filter === "all" ? "os-chip-active" : ""}`}
        >
          All · {companies.length}
        </button>
        {pipelineStages.map((s) => (
          <button
            key={s.id}
            onClick={() => setFilter(s.id)}
            className={`os-chip ${filter === s.id ? "os-chip-active" : ""}`}
          >
            {s.label} · {companies.filter((c) => c.stage === s.id).length}
          </button>
        ))}
      </div>
      <div className="os-table" data-testid="leads-table">
        <div className="os-thead grid grid-cols-[1.6fr_1fr_0.6fr_0.6fr_0.8fr_0.8fr]">
          <div>Company</div>
          <div>Industry</div>
          <div>ICP</div>
          <div>Employees</div>
          <div>Stage</div>
          <div>Owner</div>
        </div>
        {filtered.map((c) => (
          <button
            key={c.id}
            onClick={() => openCompany(c.id)}
            className="os-trow grid grid-cols-[1.6fr_1fr_0.6fr_0.6fr_0.8fr_0.8fr] items-center"
            data-testid={`lead-${c.id}`}
          >
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-md bg-white/[0.06] flex items-center justify-center text-[10px] font-mono-xn text-white/70">
                {c.name.split(" ").map((x) => x[0]).slice(0, 2).join("")}
              </div>
              <span className="text-white text-[13px]">{c.name}</span>
            </div>
            <div className="text-white/60 text-[12px]">{c.industry}</div>
            <div className="text-white/85 text-[12px] tabular-nums">{c.icp}%</div>
            <div className="text-white/60 text-[12px] tabular-nums">{c.employees}</div>
            <div className="text-white/70 text-[12px]">{c.stage}</div>
            <div className="text-white/60 text-[12px]">{c.owner}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
