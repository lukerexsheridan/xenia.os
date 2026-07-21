import { useState } from "react";
import { tasks as SEED, companyById } from "@/os/data";
import { useOS } from "@/os/OSContext";

export default function Tasks() {
  const { openCompany } = useOS();
  const [list, setList] = useState(SEED);
  const toggle = (id) =>
    setList((l) => l.map((t) => (t.id === id ? { ...t, done: !t.done } : t)));

  const open = list.filter((t) => !t.done);
  const done = list.filter((t) => t.done);

  return (
    <div className="p-8" data-testid="module-tasks">
      <Group title={`Open · ${open.length}`}>
        {open.map((t) => (
          <TaskRow key={t.id} t={t} toggle={toggle} openCompany={openCompany} />
        ))}
      </Group>
      <div className="mt-8">
        <Group title={`Done · ${done.length}`}>
          {done.map((t) => (
            <TaskRow key={t.id} t={t} toggle={toggle} openCompany={openCompany} />
          ))}
        </Group>
      </div>
    </div>
  );
}

function TaskRow({ t, toggle, openCompany }) {
  const c = companyById(t.company);
  return (
    <div className="flex items-center gap-3 py-3 border-b border-white/[0.05] last:border-0" data-testid={`task-${t.id}`}>
      <button
        onClick={() => toggle(t.id)}
        className={`w-4 h-4 rounded border ${t.done ? "bg-white border-white" : "border-white/25 hover:border-white/60"} flex items-center justify-center`}
        data-testid={`task-toggle-${t.id}`}
      >
        {t.done && (
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#000" strokeWidth="3">
            <path d="M4 12l5 5L20 6" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        )}
      </button>
      <div className={`text-[13px] ${t.done ? "text-white/40 line-through" : "text-white/90"}`}>
        {t.label}
      </div>
      <button
        onClick={() => openCompany(t.company)}
        className="ml-auto text-[11px] font-mono-xn text-white/40 hover:text-white/80"
      >
        {c?.name}
      </button>
      <div className="text-[10.5px] font-mono-xn text-white/40 w-16 text-right">{t.due}</div>
    </div>
  );
}

function Group({ title, children }) {
  return (
    <div>
      <div className="text-[10px] font-mono-xn text-white/40 mb-3">{title}</div>
      <div className="os-card p-3">{children}</div>
    </div>
  );
}
