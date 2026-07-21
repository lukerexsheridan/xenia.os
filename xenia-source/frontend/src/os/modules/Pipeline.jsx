import { useState } from "react";
import { companies, pipelineStages } from "@/os/data";
import { useOS } from "@/os/OSContext";

export default function Pipeline() {
  const { openCompany } = useOS();
  const [items, setItems] = useState(companies);
  const [dragId, setDragId] = useState(null);

  const move = (id, stage) => {
    setItems((list) => list.map((c) => (c.id === id ? { ...c, stage } : c)));
  };

  return (
    <div className="p-8" data-testid="module-pipeline">
      <div className="grid grid-cols-5 gap-3">
        {pipelineStages.map((s) => {
          const col = items.filter((c) => c.stage === s.id);
          return (
            <div
              key={s.id}
              className="os-column"
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => {
                if (dragId) move(dragId, s.id);
                setDragId(null);
              }}
              data-testid={`pipeline-col-${s.id}`}
            >
              <div className="flex items-center justify-between px-2 py-2 mb-1">
                <div className="text-[11px] font-mono-xn text-white/50">{s.label}</div>
                <div className="text-[10.5px] font-mono-xn text-white/35 tabular-nums">
                  {col.length}
                </div>
              </div>
              <div className="space-y-2 min-h-[40px]">
                {col.map((c) => (
                  <div
                    key={c.id}
                    draggable
                    onDragStart={() => setDragId(c.id)}
                    onClick={() => openCompany(c.id)}
                    className="os-card-sm p-3 cursor-grab active:cursor-grabbing"
                    data-testid={`pipeline-card-${c.id}`}
                  >
                    <div className="text-[13px] text-white">{c.name}</div>
                    <div className="text-[10.5px] font-mono-xn text-white/40 mt-1">
                      ICP {c.icp}% · {c.owner.split(" ")[0]}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-4 text-[10.5px] font-mono-xn text-white/35">
        Drag cards between columns. Xenia relearns from every move.
      </div>
    </div>
  );
}
