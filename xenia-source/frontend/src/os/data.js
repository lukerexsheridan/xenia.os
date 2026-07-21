// Mock but coherent data powering every module in XeniaOS.
// Cross-referenced by id so a Company can be opened from Companies, Leads, Pipeline, etc.

export const companies = [
  {
    id: "c-northlake",
    name: "Northlake Robotics",
    industry: "Robotics / Perception AI",
    hq: "Berlin, DE",
    employees: 84,
    arr: "€6.4M",
    stack: ["PyTorch", "Ray", "Kubernetes", "gRPC", "React"],
    icp: 94,
    stage: "Qualified",
    signals: [
      { id: "s1", label: "Series B €38M · Balderton", ts: "2d ago", weight: 0.94 },
      { id: "s2", label: "3 Sr. ML Engineers hired", ts: "5d ago", weight: 0.82 },
      { id: "s3", label: "New warehouse pilot · Rotterdam", ts: "2w ago", weight: 0.63 },
    ],
    news: [
      { title: "Northlake closes €38M Series B to scale warehouse perception", src: "Sifted" },
      { title: "Interview: Amelia Roux on the physics of picking systems", src: "The Robot Report" },
    ],
    contacts: ["p-amelia", "p-jonas"],
    owner: "Sara Ndiaye",
  },
  {
    id: "c-driftmark",
    name: "Driftmark Logistics",
    industry: "Freight / SaaS",
    hq: "Rotterdam, NL",
    employees: 210,
    arr: "€22M",
    stack: ["Go", "Postgres", "AWS", "Kafka"],
    icp: 81,
    stage: "Researching",
    signals: [
      { id: "s4", label: "New CMO announced", ts: "1d ago", weight: 0.88 },
      { id: "s5", label: "Opened 2 US offices", ts: "3w ago", weight: 0.61 },
    ],
    news: [
      { title: "Driftmark hires ex-DHL CMO to lead US expansion", src: "Reuters" },
    ],
    contacts: ["p-lena"],
    owner: "Sara Ndiaye",
  },
  {
    id: "c-halcyon",
    name: "Halcyon Bio",
    industry: "Biotech / Diagnostics",
    hq: "Boston, US",
    employees: 46,
    arr: "$3.1M",
    stack: ["Python", "R", "GCP", "Snowflake"],
    icp: 76,
    stage: "New",
    signals: [
      { id: "s6", label: "FDA breakthrough designation", ts: "4d ago", weight: 0.9 },
    ],
    news: [],
    contacts: ["p-shreya"],
    owner: "Marcus Lin",
  },
  {
    id: "c-kestrel",
    name: "Kestrel Aviation",
    industry: "Electric aircraft",
    hq: "Toulouse, FR",
    employees: 132,
    arr: "€14M",
    stack: ["C++", "ROS", "Azure"],
    icp: 71,
    stage: "Contacted",
    signals: [
      { id: "s7", label: "Type certificate filing", ts: "1w ago", weight: 0.72 },
    ],
    news: [],
    contacts: ["p-tomas"],
    owner: "Marcus Lin",
  },
  {
    id: "c-obsidian",
    name: "Obsidian Analytics",
    industry: "Data platform",
    hq: "London, UK",
    employees: 320,
    arr: "£41M",
    stack: ["TypeScript", "Rust", "Snowflake"],
    icp: 68,
    stage: "Meeting booked",
    signals: [
      { id: "s8", label: "Q3 hiring freeze lifted", ts: "6d ago", weight: 0.55 },
    ],
    news: [],
    contacts: ["p-jules"],
    owner: "Sara Ndiaye",
  },
  {
    id: "c-solstice",
    name: "Solstice Energy",
    industry: "Grid / storage",
    hq: "Copenhagen, DK",
    employees: 68,
    arr: "€8M",
    stack: ["Python", "InfluxDB", "AWS"],
    icp: 88,
    stage: "Qualified",
    signals: [
      { id: "s9", label: "Grid contract with Ørsted", ts: "3d ago", weight: 0.87 },
    ],
    news: [],
    contacts: ["p-frida"],
    owner: "Sara Ndiaye",
  },
  {
    id: "c-arden",
    name: "Arden Health",
    industry: "Digital health",
    hq: "Austin, US",
    employees: 55,
    arr: "$2.4M",
    stack: ["Elixir", "Postgres", "GCP"],
    icp: 64,
    stage: "New",
    signals: [{ id: "s10", label: "New series A", ts: "5d ago", weight: 0.7 }],
    news: [],
    contacts: [],
    owner: "Marcus Lin",
  },
  {
    id: "c-vessel",
    name: "Vessel Studio",
    industry: "AI infrastructure",
    hq: "Zurich, CH",
    employees: 22,
    arr: "CHF 1.4M",
    stack: ["Rust", "WASM", "CUDA"],
    icp: 92,
    stage: "Researching",
    signals: [{ id: "s11", label: "Seed extension +€5M", ts: "9d ago", weight: 0.79 }],
    news: [],
    contacts: [],
    owner: "Sara Ndiaye",
  },
  {
    id: "c-marlow",
    name: "Marlow Foods",
    industry: "CPG / DTC",
    hq: "Manchester, UK",
    employees: 190,
    arr: "£28M",
    stack: ["Shopify", "Ruby"],
    icp: 42,
    stage: "New",
    signals: [],
    news: [],
    contacts: [],
    owner: "Marcus Lin",
  },
  {
    id: "c-plume",
    name: "Plume Media",
    industry: "Ad tech",
    hq: "Paris, FR",
    employees: 110,
    arr: "€18M",
    stack: ["Node", "BigQuery"],
    icp: 58,
    stage: "Contacted",
    signals: [],
    news: [],
    contacts: [],
    owner: "Sara Ndiaye",
  },
  {
    id: "c-cinder",
    name: "Cinder Semi",
    industry: "Semiconductors",
    hq: "Eindhoven, NL",
    employees: 410,
    arr: "€67M",
    stack: ["VHDL", "C", "Python"],
    icp: 77,
    stage: "Qualified",
    signals: [{ id: "s12", label: "New foundry partnership", ts: "12d ago", weight: 0.78 }],
    news: [],
    contacts: [],
    owner: "Marcus Lin",
  },
  {
    id: "c-orbit",
    name: "Orbit & Co.",
    industry: "Space tech",
    hq: "Munich, DE",
    employees: 63,
    arr: "€5M",
    stack: ["C++", "ROS", "OpenCV"],
    icp: 85,
    stage: "Meeting booked",
    signals: [{ id: "s13", label: "ESA contract award", ts: "1d ago", weight: 0.93 }],
    news: [],
    contacts: [],
    owner: "Sara Ndiaye",
  },
];

export const contacts = [
  { id: "p-amelia", name: "Amelia Roux", title: "CTO", company: "c-northlake", email: "amelia.roux@northlake.ai", verified: true },
  { id: "p-jonas", name: "Jonas Weber", title: "VP Engineering", company: "c-northlake", email: "j.weber@northlake.ai", verified: true },
  { id: "p-lena", name: "Lena Vos", title: "CMO", company: "c-driftmark", email: "lena@driftmark.co", verified: true },
  { id: "p-shreya", name: "Dr. Shreya Kapoor", title: "Head of R&D", company: "c-halcyon", email: "shreya@halcyon.bio", verified: false },
  { id: "p-tomas", name: "Tomás Alvear", title: "Chief Product Officer", company: "c-kestrel", email: "tomas@kestrel.aero", verified: true },
  { id: "p-jules", name: "Jules Ashwin", title: "SVP Growth", company: "c-obsidian", email: "j.ashwin@obsidian.io", verified: true },
  { id: "p-frida", name: "Frida Holm", title: "Head of Data", company: "c-solstice", email: "frida@solstice.energy", verified: true },
];

export const buyingSignals = [
  { id: "b1", company: "c-northlake", label: "Series B closed", detail: "€38M · Balderton lead", ts: "2m ago", strength: "high" },
  { id: "b2", company: "c-orbit", label: "ESA contract award", detail: "Deep-space imaging", ts: "8m ago", strength: "high" },
  { id: "b3", company: "c-driftmark", label: "New CMO announced", detail: "ex-DHL", ts: "24m ago", strength: "medium" },
  { id: "b4", company: "c-solstice", label: "Grid deal · Ørsted", detail: "12-year framework", ts: "1h ago", strength: "high" },
  { id: "b5", company: "c-cinder", label: "Foundry partnership", detail: "TSMC 3nm", ts: "3h ago", strength: "medium" },
  { id: "b6", company: "c-vessel", label: "Seed extension", detail: "+€5M", ts: "6h ago", strength: "medium" },
  { id: "b7", company: "c-halcyon", label: "FDA breakthrough", detail: "Class II diagnostic", ts: "9h ago", strength: "high" },
  { id: "b8", company: "c-kestrel", label: "Type-cert filing", detail: "EASA · pathfinder", ts: "1d ago", strength: "medium" },
];

export const campaigns = [
  { id: "cmp1", name: "Q1 · Fintech Series B", sent: 128, opened: 78, replied: 21, meetings: 8, status: "Live" },
  { id: "cmp2", name: "Robotics · warehouse ops", sent: 92, opened: 61, replied: 18, meetings: 6, status: "Live" },
  { id: "cmp3", name: "Semiconductors EU", sent: 54, opened: 33, replied: 6, meetings: 2, status: "Paused" },
  { id: "cmp4", name: "Climate infra US", sent: 210, opened: 132, replied: 34, meetings: 12, status: "Live" },
  { id: "cmp5", name: "Biotech FDA breakthrough", sent: 41, opened: 27, replied: 11, meetings: 4, status: "Draft" },
];

export const tasks = [
  { id: "t1", label: "Approve outreach to Amelia @ Northlake", due: "Today", done: false, company: "c-northlake" },
  { id: "t2", label: "Review 3 new intro drafts · Driftmark thread", due: "Today", done: false, company: "c-driftmark" },
  { id: "t3", label: "Call recap · Solstice Energy", due: "Tomorrow", done: false, company: "c-solstice" },
  { id: "t4", label: "Flag Orbit & Co. to Marcus", due: "Tomorrow", done: false, company: "c-orbit" },
  { id: "t5", label: "Verify Shreya Kapoor's email", due: "Fri", done: true, company: "c-halcyon" },
  { id: "t6", label: "Send pricing to Jules @ Obsidian", due: "Fri", done: false, company: "c-obsidian" },
];

export const pipelineStages = [
  { id: "New", label: "New" },
  { id: "Researching", label: "Researching" },
  { id: "Qualified", label: "Qualified" },
  { id: "Contacted", label: "Contacted" },
  { id: "Meeting booked", label: "Meeting" },
];

export const notifications = [
  { id: "n1", label: "Northlake · Series B closed", detail: "Xenia surfaced a high-signal opportunity", ts: "just now" },
  { id: "n2", label: "New reply · Jules @ Obsidian", detail: "\"Send pricing when convenient.\"", ts: "12m ago" },
  { id: "n3", label: "Amelia opened your draft", detail: "3rd view · dwell 42s", ts: "34m ago" },
  { id: "n4", label: "Campaign · Q1 Fintech", detail: "reached 128 sends", ts: "1h ago" },
  { id: "n5", label: "Frida (Solstice) accepted your meeting", detail: "Tue 10:30 CET", ts: "3h ago" },
];

export const activity = [
  { id: "a1", ts: "23:41", who: "Xenia", what: "wrote 6 drafts for Q1 Fintech campaign", tone: "draft" },
  { id: "a2", ts: "23:12", who: "Xenia", what: "detected buying signal at Orbit & Co. (ESA award)", tone: "signal" },
  { id: "a3", ts: "22:58", who: "Sara", what: "approved outreach to Frida @ Solstice", tone: "action" },
  { id: "a4", ts: "22:41", who: "Xenia", what: "enriched 42 new contacts across 6 companies", tone: "enrich" },
  { id: "a5", ts: "21:20", who: "Marcus", what: "qualified Cinder Semi as ICP 77%", tone: "action" },
  { id: "a6", ts: "20:50", who: "Xenia", what: "revised 4 messages after negative reply signal", tone: "learn" },
];

export const team = [
  { id: "u1", name: "Sara Ndiaye", role: "Managing Director", online: true },
  { id: "u2", name: "Marcus Lin", role: "Head of Growth", online: true },
  { id: "u3", name: "Priya Anand", role: "Account Director", online: false },
  { id: "u4", name: "Rowan Kelly", role: "Copy Lead", online: true },
  { id: "u5", name: "Yosef Halevi", role: "RevOps", online: false },
];

export const integrations = [
  { id: "int1", name: "HubSpot", status: "Connected" },
  { id: "int2", name: "Salesforce", status: "Connected" },
  { id: "int3", name: "Gmail", status: "Connected" },
  { id: "int4", name: "Outlook", status: "Not connected" },
  { id: "int5", name: "LinkedIn Sales Navigator", status: "Connected" },
  { id: "int6", name: "Slack", status: "Connected" },
  { id: "int7", name: "Notion", status: "Connected" },
  { id: "int8", name: "Segment", status: "Not connected" },
];

export const reports = [
  { id: "r1", name: "Weekly signal digest", period: "Feb 12 – Feb 19", insights: 12 },
  { id: "r2", name: "Reply-rate by industry", period: "Q1 2026", insights: 7 },
  { id: "r3", name: "ICP fit vs meeting-to-close", period: "Q4 2025", insights: 5 },
  { id: "r4", name: "Campaign performance", period: "Last 30d", insights: 9 },
];

// A small chart series for analytics: replies per week over 12 weeks
export const analyticsSeries = {
  replies: [8, 11, 14, 12, 17, 19, 22, 25, 24, 27, 31, 34],
  meetings: [2, 3, 4, 3, 6, 6, 7, 9, 8, 10, 11, 12],
};

export const modules = [
  { id: "dashboard", label: "Dashboard" },
  { id: "leads", label: "Leads" },
  { id: "companies", label: "Companies" },
  { id: "contacts", label: "Contacts" },
  { id: "research", label: "AI Research" },
  { id: "signals", label: "Buying Signals" },
  { id: "campaigns", label: "Campaigns" },
  { id: "email", label: "Email Writer" },
  { id: "chat", label: "AI Chat" },
  { id: "tasks", label: "Tasks" },
  { id: "pipeline", label: "Pipeline" },
  { id: "analytics", label: "Analytics" },
  { id: "reports", label: "Reports" },
  { id: "team", label: "Team" },
  { id: "integrations", label: "Integrations" },
  { id: "notifications", label: "Notifications" },
  { id: "activity", label: "Activity" },
  { id: "settings", label: "Settings" },
];

export const companyById = (id) => companies.find((c) => c.id === id);
export const contactById = (id) => contacts.find((p) => p.id === id);
