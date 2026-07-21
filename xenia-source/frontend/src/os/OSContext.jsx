import { createContext, useContext, useState, useMemo, useCallback, useEffect } from "react";

const OSContext = createContext(null);

const LS_KEY = "xenia.os.state";
const MAX_PALETTE_RECENTS = 8;

function loadPersisted() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return null;
    return parsed;
  } catch {
    return null;
  }
}

function savePersisted(state) {
  try {
    localStorage.setItem(LS_KEY, JSON.stringify(state));
  } catch {
    /* localStorage full or blocked — silent */
  }
}

export function OSProvider({ children }) {
  const persisted = typeof window !== "undefined" ? loadPersisted() : null;

  const [activeModule, setActiveModule] = useState(persisted?.activeModule || "dashboard");
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [draftContext, setDraftContext] = useState(null);
  const [paletteRecents, setPaletteRecents] = useState(
    Array.isArray(persisted?.paletteRecents) ? persisted.paletteRecents.slice(0, MAX_PALETTE_RECENTS) : []
  );

  // Persist activeModule + paletteRecents on change
  useEffect(() => {
    savePersisted({ activeModule, paletteRecents });
  }, [activeModule, paletteRecents]);

  const openCompany = useCallback((id) => setSelectedCompany(id), []);
  const closeCompany = useCallback(() => setSelectedCompany(null), []);

  const draftFor = useCallback((companyId, contactId = null) => {
    setDraftContext({ companyId, contactId });
    setActiveModule("email");
    setSelectedCompany(null);
  }, []);

  const rememberPaletteHit = useCallback((entry) => {
    // entry: { id, kind, label }
    if (!entry?.id) return;
    setPaletteRecents((cur) => {
      const filtered = cur.filter((r) => r.id !== entry.id);
      return [entry, ...filtered].slice(0, MAX_PALETTE_RECENTS);
    });
  }, []);

  const value = useMemo(
    () => ({
      activeModule,
      setActiveModule,
      selectedCompany,
      openCompany,
      closeCompany,
      paletteOpen,
      setPaletteOpen,
      draftContext,
      draftFor,
      paletteRecents,
      rememberPaletteHit,
    }),
    [
      activeModule,
      selectedCompany,
      paletteOpen,
      draftContext,
      openCompany,
      closeCompany,
      draftFor,
      paletteRecents,
      rememberPaletteHit,
    ]
  );

  return <OSContext.Provider value={value}>{children}</OSContext.Provider>;
}

export function useOS() {
  const ctx = useContext(OSContext);
  if (!ctx) throw new Error("useOS must be used inside OSProvider");
  return ctx;
}
