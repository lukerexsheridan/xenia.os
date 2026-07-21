// Natural-language interpreter for the ⌘K palette.
// Given a raw query and the OS entities, returns a single "smart" command
// (or null) that will appear at the top of the palette results.
//
// Patterns handled (case-insensitive):
//   • "draft outreach to X" | "email X" | "write to X" | "reply to X"  → Email Writer, target = X
//   • "open X" | "show X" | "view X" | "go to X"                        → module OR company OR contact
//   • "signals (from|for|on) X"                                          → Buying Signals module
//   • "research X" | "brief on X" | "briefing on X"                      → AI Research module
//   • "call X" | "meet X" | "meeting with X"                             → Contacts module, filter=X
//   • Fallback: a bare token that uniquely matches a company/contact     → open detail / draft

const clean = (s) => s.trim().replace(/\s+/g, " ");

function findCompany(needle, companies) {
  const n = needle.toLowerCase();
  // Exact
  let hit = companies.find((c) => c.name.toLowerCase() === n);
  if (hit) return hit;
  // Starts-with on first word (e.g. "Northlake" → Northlake Robotics)
  hit = companies.find((c) => c.name.toLowerCase().split(" ")[0] === n);
  if (hit) return hit;
  // Includes
  hit = companies.find((c) => c.name.toLowerCase().includes(n));
  if (hit) return hit;
  return null;
}

function findContact(needle, contacts) {
  const n = needle.toLowerCase();
  let hit = contacts.find((c) => c.name.toLowerCase() === n);
  if (hit) return hit;
  hit = contacts.find((c) => c.name.toLowerCase().split(" ")[0] === n);
  if (hit) return hit;
  hit = contacts.find((c) => c.name.toLowerCase().includes(n));
  return hit || null;
}

function findModule(needle, modules) {
  const n = needle.toLowerCase();
  let hit = modules.find((m) => m.label.toLowerCase() === n);
  if (hit) return hit;
  hit = modules.find((m) => m.id.toLowerCase() === n);
  if (hit) return hit;
  hit = modules.find((m) => m.label.toLowerCase().includes(n));
  return hit || null;
}

export function interpretQuery(raw, ctx) {
  const q = clean(raw || "");
  if (!q) return null;

  const { companies, contacts, modules, draftFor, openCompany, setActiveModule, setPaletteOpen } =
    ctx;

  const close = () => setPaletteOpen(false);

  // 1. Draft / email / write / reply → Email Writer targeted at X
  {
    const m = q.match(/^(?:draft(?:\s+outreach)?|email|write|reply)\s+(?:to\s+)?(.+)$/i);
    if (m) {
      const target = clean(m[1]);
      const co = findCompany(target, companies);
      const contact = !co ? findContact(target, contacts) : null;
      if (co) {
        return {
          id: `auto-draft-${co.id}`,
          label: `Draft outreach to ${co.name}`,
          hint: "Autopilot · Email Writer",
          kind: "autopilot",
          action: () => {
            draftFor(co.id);
            close();
          },
        };
      }
      if (contact) {
        return {
          id: `auto-draft-${contact.id}`,
          label: `Draft outreach to ${contact.name}`,
          hint: "Autopilot · Email Writer",
          kind: "autopilot",
          action: () => {
            draftFor(contact.company, contact.id);
            close();
          },
        };
      }
      return null;
    }
  }

  // 2. Signals from/for/on X → Buying Signals
  {
    const m = q.match(/^signals?\s+(?:from|for|on)?\s*(.+)$/i);
    if (m) {
      const target = clean(m[1]);
      const co = findCompany(target, companies);
      return {
        id: `auto-signals-${(co && co.id) || "all"}`,
        label: co ? `Show signals near ${co.name}` : `Open Buying Signals`,
        hint: "Autopilot · Signals",
        kind: "autopilot",
        action: () => {
          setActiveModule("signals");
          if (co) openCompany(co.id);
          close();
        },
      };
    }
  }

  // 3. Research / brief(ing) on X → AI Research
  {
    const m = q.match(/^(?:research|brief|briefing)\s+(?:on\s+)?(.+)$/i);
    if (m) {
      const target = clean(m[1]);
      const co = findCompany(target, companies);
      return {
        id: `auto-research-${(co && co.id) || "all"}`,
        label: co ? `Research ${co.name}` : `Open AI Research`,
        hint: "Autopilot · AI Research",
        kind: "autopilot",
        action: () => {
          setActiveModule("research");
          if (co) openCompany(co.id);
          close();
        },
      };
    }
  }

  // 4. Call / meet / meeting with X → Contacts module (+ optionally open contact)
  {
    const m = q.match(/^(?:call|meet|meeting\s+with)\s+(.+)$/i);
    if (m) {
      const target = clean(m[1]);
      const contact = findContact(target, contacts);
      return {
        id: `auto-contact-${(contact && contact.id) || "all"}`,
        label: contact ? `Open ${contact.name}'s profile` : `Open Contacts`,
        hint: "Autopilot · Contacts",
        kind: "autopilot",
        action: () => {
          setActiveModule("contacts");
          if (contact) openCompany(contact.company);
          close();
        },
      };
    }
  }

  // 5. Open / show / view / go to X → module OR company OR contact
  {
    const m = q.match(/^(?:open|show|view|go\s+to|switch\s+to)\s+(.+)$/i);
    if (m) {
      const target = clean(m[1]);
      const mod = findModule(target, modules);
      if (mod) {
        return {
          id: `auto-mod-${mod.id}`,
          label: `Go to ${mod.label}`,
          hint: "Autopilot · Module",
          kind: "autopilot",
          action: () => {
            setActiveModule(mod.id);
            close();
          },
        };
      }
      const co = findCompany(target, companies);
      if (co) {
        return {
          id: `auto-open-${co.id}`,
          label: `Open ${co.name}`,
          hint: "Autopilot · Company",
          kind: "autopilot",
          action: () => {
            openCompany(co.id);
            close();
          },
        };
      }
      const contact = findContact(target, contacts);
      if (contact) {
        return {
          id: `auto-open-${contact.id}`,
          label: `Open ${contact.name}`,
          hint: "Autopilot · Contact",
          kind: "autopilot",
          action: () => {
            openCompany(contact.company);
            close();
          },
        };
      }
      return null;
    }
  }

  return null;
}
