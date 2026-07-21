import { useState } from "react";
import { integrations as SEED } from "@/os/data";

export default function Integrations() {
  const [list, setList] = useState(SEED);
  const toggle = (id) =>
    setList((l) =>
      l.map((i) =>
        i.id === id
          ? {
              ...i,
              status: i.status === "Connected" ? "Not connected" : "Connected",
            }
          : i
      )
    );
  return (
    <div className="p-8 grid grid-cols-4 gap-3" data-testid="module-integrations">
      {list.map((i) => (
        <div key={i.id} className="os-card p-5" data-testid={`integration-${i.id}`}>
          <div className="flex items-center justify-between">
            <div className="text-white text-[14px]">{i.name}</div>
            <span
              className={`os-pill ${i.status === "Connected" ? "os-pill-ok" : "os-pill-muted"}`}
            >
              {i.status}
            </span>
          </div>
          <button
            onClick={() => toggle(i.id)}
            className="mt-4 os-ghost w-full"
            data-testid={`integration-toggle-${i.id}`}
          >
            {i.status === "Connected" ? "Disconnect" : "Connect"}
          </button>
        </div>
      ))}
    </div>
  );
}
