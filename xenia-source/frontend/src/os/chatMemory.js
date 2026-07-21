import { companies, contacts } from "@/os/data";

// Lightweight, deterministic "memory" extractor for the AI Chat panel.
// Scans user + assistant messages for:
//   • known company mentions (matched against XeniaOS mock data)
//   • known contact mentions
//   • distilled topics (short summaries of what the user asked about)
// Everything is client-side; no server call. Order = most recent first.

const KNOWN_COMPANIES = companies.map((c) => ({
  id: c.id,
  name: c.name,
  short: c.name.split(/[\s&]+/)[0], // "Northlake Robotics" → "Northlake"
  industry: c.industry,
}));

const KNOWN_CONTACTS = contacts.map((c) => ({
  id: c.id,
  name: c.name,
  first: c.name.split(" ")[0],
  companyId: c.company,
}));

const STOP = new Set([
  "the","a","an","and","or","of","to","in","on","for","with","from","at","by",
  "is","it","this","that","these","those","be","are","was","were","have","has",
  "give","me","tell","show","what","which","how","who","why","when","please",
  "just","about","up","down","out","into","over","under","between","us","our",
  "your","my","i","we","you","they","them","he","she","his","her",
]);

function topicFromUserMessage(text, cap = 44) {
  if (!text) return "";
  const cleaned = text.replace(/["'`]/g, "").replace(/\s+/g, " ").trim();
  // Prefer a natural, short phrase — first clause up to a comma/period
  const first = cleaned.split(/[.?!,;]/)[0].trim();
  const words = first.split(" ").filter((w) => w && !STOP.has(w.toLowerCase()));
  const phrase = (words.slice(0, 7).join(" ") || first).trim();
  if (!phrase) return "";
  const cap1 = phrase.charAt(0).toUpperCase() + phrase.slice(1);
  return cap1.length > cap ? cap1.slice(0, cap - 1).trim() + "…" : cap1;
}

export function extractMemory(messages) {
  const companyHits = new Map(); // id → { name, mentions, industry }
  const contactHits = new Map();
  const topics = []; // preserves order

  for (const m of messages) {
    const text = m?.text || "";
    if (!text) continue;
    const lc = text.toLowerCase();

    for (const c of KNOWN_COMPANIES) {
      if (lc.includes(c.name.toLowerCase()) || lc.includes(c.short.toLowerCase())) {
        const cur = companyHits.get(c.id) || { id: c.id, name: c.name, industry: c.industry, mentions: 0 };
        cur.mentions += 1;
        companyHits.set(c.id, cur);
      }
    }
    for (const p of KNOWN_CONTACTS) {
      if (lc.includes(p.name.toLowerCase()) || new RegExp(`\\b${p.first.toLowerCase()}\\b`).test(lc)) {
        const cur = contactHits.get(p.id) || { id: p.id, name: p.name, companyId: p.companyId, mentions: 0 };
        cur.mentions += 1;
        contactHits.set(p.id, cur);
      }
    }
    if (m.from === "user") {
      const t = topicFromUserMessage(text);
      if (t && !topics.includes(t)) topics.push(t);
    }
  }

  const companyList = [...companyHits.values()].sort((a, b) => b.mentions - a.mentions);
  const contactList = [...contactHits.values()].sort((a, b) => b.mentions - a.mentions);

  return {
    companies: companyList,
    contacts: contactList,
    topics: topics.slice(-6).reverse(), // most recent first, cap at 6
  };
}
