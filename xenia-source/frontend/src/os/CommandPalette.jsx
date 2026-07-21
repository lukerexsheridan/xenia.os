import { useState, useMemo, useEffect, useRef } from "react";
import { useOS } from "@/os/OSContext";
import { modules, companies, contacts } from "@/os/data";
import { interpretQuery } from "@/os/paletteAutopilot";

// ⌘K command palette. Filters modules + companies + a few quick actions,
// and surfaces a natural-language autopilot command at the top when a query
// like "draft outreach to Northlake" or "open pipeline" is recognised.
export default function CommandPalette() {
  const {
    setPaletteOpen,
    setActiveModule,
    openCompany,
    draftFor,
    paletteRecents,
    rememberPaletteHit,
  } = useOS();
  const [q, setQ] = useState("");
  const inputRef = useRef();

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const autopilot = useMemo(
    () =>
      q.trim()
        ? interpretQuery(q, {
            companies,
            contacts,
            modules,
            draftFor,
            openCompany,
            setActiveModule,
            setPaletteOpen,
          })
        : null,
    [q, draftFor, openCompany, setActiveModule, setPaletteOpen]
  );

  const items = useMemo(() => {
    const modItems = modules.map((m) => ({
      id: `mod-${m.id}`,
      label: m.label,
      hint: "Go to module",
      kind: "module",
      action: () => {
        setActiveModule(m.id);
        setPaletteOpen(false);
      },
    }));
    const compItems = companies.map((c) => ({
      id: `co-${c.id}`,
      label: c.name,
      hint: `Open · ${c.industry}`,
      kind: "company",
      action: () => {
        openCompany(c.id);
        setPaletteOpen(false);
      },
    }));
    const actions = [
      {
        id: "action-newsearch",
        label: "Start a new intelligence search",
        hint: "Run",
        kind: "action",
        action: () => {
          setActiveModule("dashboard");
          setPaletteOpen(false);
        },
      },
      {
        id: "action-draft",
        label: "Draft outreach to top-signal company",
        hint: "Run",
        kind: "action",
        action: () => {
          setActiveModule("email");
          setPaletteOpen(false);
        },
      },
    ];
    const all = [...actions, ...modItems, ...compItems];
    if (!q.trim()) {
      const recentIds = new Set((paletteRecents || []).map((r) => r.id));
      const recentItems = (paletteRecents || [])
        .map((r) => all.find((a) => a.id === r.id))
        .filter(Boolean);
      const fresh = all.filter((a) => !recentIds.has(a.id));
      return [...recentItems, ...fresh].slice(0, 12);
    }
    const query = q.toLowerCase();
    return all.filter(
      (i) =>
        i.label.toLowerCase().includes(query) ||
        i.hint.toLowerCase().includes(query)
    );
  }, [q, setActiveModule, setPaletteOpen, openCompany, paletteRecents]);

  const runItem = (it) => {
    rememberPaletteHit({ id: it.id, kind: it.kind, label: it.label });
    it.action();
  };

  const showingRecents = !q.trim() && (paletteRecents || []).length > 0;
  const showingAutopilot = !!autopilot;

  return (
    <div
      className="os-palette-backdrop"
      onClick={() => setPaletteOpen(false)}
      data-testid="command-palette"
    >
      <div
        className="os-palette"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 px-4 py-3 border-b border-white/[0.06]">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-white/50">
            <circle cx="11" cy="11" r="7" />
            <path d="M20 20l-3.5-3.5" strokeLinecap="round" />
          </svg>
          <input
            ref={inputRef}
            data-testid="palette-input"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                if (autopilot) runItem(autopilot);
                else if (items[0]) runItem(items[0]);
              }
            }}
            placeholder="Search or ask — 'draft outreach to Northlake', 'open pipeline'"
            className="flex-1 bg-transparent border-0 outline-none text-white placeholder:text-white/30 text-[14px]"
          />
          <span className="text-[10px] font-mono-xn text-white/30">esc</span>
        </div>
        <div className="max-h-[380px] overflow-y-auto py-2">
          {showingAutopilot && (
            <div data-testid="palette-autopilot" className="px-3 pb-2 pt-1">
              <button
                data-testid={`palette-item-${autopilot.id}`}
                onClick={() => runItem(autopilot)}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-royal text-white shadow-[0_10px_30px_-10px_rgba(76,108,255,0.6)] hover:brightness-110 active:scale-[0.99] transition-all text-left group"
              >
                <span className="os-palette-kind kind-autopilot">→</span>
                <span className="text-[13px] font-medium">{autopilot.label}</span>
                <span className="ml-auto text-[10px] font-mono-xn text-white/70 tracking-wider uppercase">
                  {autopilot.hint}
                </span>
                <span className="text-[10px] font-mono-xn text-white/60 tracking-wider">
                  ↵
                </span>
              </button>
            </div>
          )}
          {showingRecents && (
            <div className="px-4 pb-1 pt-1 text-[9.5px] font-mono-xn text-white/30 tracking-widest">
              Recents
            </div>
          )}
          {items.length === 0 ? (
            <div className="px-4 py-8 text-center text-white/40 text-[12px]">
              Nothing matches.
            </div>
          ) : (
            items.map((it) => (
              <button
                key={it.id}
                data-testid={`palette-item-${it.id}`}
                onClick={() => runItem(it)}
                className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-white/[0.04] text-left group"
              >
                <span className={`os-palette-kind kind-${it.kind}`}>
                  {it.kind === "module" ? "M" : it.kind === "company" ? "C" : "→"}
                </span>
                <span className="text-white text-[13px]">{it.label}</span>
                <span className="ml-auto text-[10.5px] text-white/35 group-hover:text-white/60 transition-colors">
                  {it.hint}
                </span>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
