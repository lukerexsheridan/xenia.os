import { useOS } from "@/os/OSContext";

export default function Topbar({ label }) {
  const { setPaletteOpen, setActiveModule } = useOS();
  return (
    <div className="os-topbar" data-testid="os-topbar">
      <div className="flex items-center gap-3">
        <div className="font-display text-[18px] text-white">{label}</div>
        <span className="text-white/25 text-[11px] font-mono-xn">·</span>
        <span className="text-white/45 text-[11px] font-mono-xn">
          Live · continuously learning
        </span>
      </div>
      <div className="flex items-center gap-2 ml-auto">
        <button
          data-testid="topbar-command"
          onClick={() => setPaletteOpen(true)}
          className="os-chip"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="7" />
            <path d="M20 20l-3.5-3.5" strokeLinecap="round" />
          </svg>
          <span className="text-white/50">Search or run…</span>
          <span className="text-white/30 text-[10px] font-mono-xn ml-2">⌘K</span>
        </button>
        <button
          data-testid="topbar-notifications"
          onClick={() => setActiveModule("notifications")}
          className="os-icon-btn"
          aria-label="Notifications"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
            <path d="M6 8a6 6 0 0112 0c0 7 3 8 3 8H3s3-1 3-8" />
            <path d="M10 21a2 2 0 004 0" />
          </svg>
          <span className="os-badge">5</span>
        </button>
        <button
          data-testid="topbar-new"
          className="os-cta"
        >
          + New search
        </button>
      </div>
    </div>
  );
}
