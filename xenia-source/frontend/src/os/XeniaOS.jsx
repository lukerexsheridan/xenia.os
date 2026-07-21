import { useEffect } from "react";
import { OSProvider, useOS } from "@/os/OSContext";
import { modules } from "@/os/data";
import Sidebar from "@/os/Sidebar";
import Topbar from "@/os/Topbar";
import CommandPalette from "@/os/CommandPalette";
import CompanyDetail from "@/os/CompanyDetail";
import ModuleTransition from "@/os/ModuleTransition";

import Dashboard from "@/os/modules/Dashboard";
import Leads from "@/os/modules/Leads";
import Companies from "@/os/modules/Companies";
import Contacts from "@/os/modules/Contacts";
import AIResearch from "@/os/modules/AIResearch";
import BuyingSignals from "@/os/modules/BuyingSignals";
import Campaigns from "@/os/modules/Campaigns";
import EmailWriter from "@/os/modules/EmailWriter";
import AIChat from "@/os/modules/AIChat";
import Tasks from "@/os/modules/Tasks";
import Pipeline from "@/os/modules/Pipeline";
import Analytics from "@/os/modules/Analytics";
import Reports from "@/os/modules/Reports";
import Team from "@/os/modules/Team";
import Integrations from "@/os/modules/Integrations";
import Notifications from "@/os/modules/Notifications";
import ActivityFeed from "@/os/modules/ActivityFeed";
import Settings from "@/os/modules/Settings";

const MODULES = {
  dashboard: Dashboard,
  leads: Leads,
  companies: Companies,
  contacts: Contacts,
  research: AIResearch,
  signals: BuyingSignals,
  campaigns: Campaigns,
  email: EmailWriter,
  chat: AIChat,
  tasks: Tasks,
  pipeline: Pipeline,
  analytics: Analytics,
  reports: Reports,
  team: Team,
  integrations: Integrations,
  notifications: Notifications,
  activity: ActivityFeed,
  settings: Settings,
};

function OSInner() {
  const { activeModule, paletteOpen, setPaletteOpen, selectedCompany } = useOS();

  useEffect(() => {
    const onKey = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setPaletteOpen((o) => !o);
      } else if (e.key === "Escape") {
        setPaletteOpen(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [setPaletteOpen]);

  const Module = MODULES[activeModule] || Dashboard;
  const label = modules.find((m) => m.id === activeModule)?.label || "Dashboard";

  return (
    <div
      className="os-frame relative w-full max-w-[1360px] mx-auto rounded-2xl overflow-hidden"
      data-testid="xenia-os"
    >
      {/* Realistic app chrome */}
      <div className="os-titlebar">
        <div className="flex items-center gap-2 pl-3">
          <span className="tl-dot bg-white/25" />
          <span className="tl-dot bg-white/15" />
          <span className="tl-dot bg-white/10" />
        </div>
        <div className="flex-1 text-center text-[11px] font-mono-xn text-white/40">
          xenia · {label}
        </div>
        <div className="pr-3 text-[11px] font-mono-xn text-white/40">
          v0.1 · preview
        </div>
      </div>

      <div className="os-body">
        <Sidebar />
        <div className="os-main">
          <Topbar label={label} />
          <div className="os-scroll">
            <Module />
          </div>
        </div>
      </div>

      {selectedCompany && <CompanyDetail />}
      {paletteOpen && <CommandPalette />}
      <ModuleTransition moduleId={activeModule} label={label} />
    </div>
  );
}

export default function XeniaOS() {
  return (
    <OSProvider>
      <OSInner />
    </OSProvider>
  );
}
