import { useState } from "react";

export default function Settings() {
  const [notif, setNotif] = useState(true);
  const [autoDraft, setAutoDraft] = useState(true);
  const [autoSend, setAutoSend] = useState(false);
  const [tone, setTone] = useState("Reserved");

  return (
    <div className="p-8 max-w-3xl" data-testid="module-settings">
      <Section title="Workspace">
        <Field label="Agency name">
          <div className="os-input">Meridian &amp; Co.</div>
        </Field>
        <Field label="Timezone">
          <div className="os-input">Europe / Paris — CET</div>
        </Field>
      </Section>

      <Section title="AI behaviour">
        <Row label="Auto-draft outreach for new high-signal companies" checked={autoDraft} onChange={setAutoDraft} />
        <Row label="Auto-send after 24h if unreviewed" checked={autoSend} onChange={setAutoSend} />
        <Field label="Default tone">
          <select className="os-select" value={tone} onChange={(e) => setTone(e.target.value)}>
            <option>Reserved</option>
            <option>Direct</option>
            <option>Warm</option>
          </select>
        </Field>
      </Section>

      <Section title="Notifications">
        <Row label="Send briefing at 08:00 daily" checked={notif} onChange={setNotif} />
      </Section>

      <Section title="Danger zone">
        <button className="os-ghost">Reset Xenia's learning</button>
      </Section>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="mt-8 first:mt-0">
      <div className="text-[10px] font-mono-xn text-white/40 mb-4">{title}</div>
      <div className="os-card p-5 grid gap-4">{children}</div>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <div>
      <div className="text-[11px] text-white/50 mb-1.5">{label}</div>
      {children}
    </div>
  );
}

function Row({ label, checked, onChange }) {
  return (
    <div className="flex items-center justify-between">
      <div className="text-[13px] text-white/85">{label}</div>
      <button
        onClick={() => onChange(!checked)}
        className={`os-toggle ${checked ? "os-toggle-on" : ""}`}
        data-testid={`settings-toggle-${label.slice(0, 10)}`}
      >
        <span className="os-toggle-knob" />
      </button>
    </div>
  );
}
