import { contacts, companyById } from "@/os/data";
import { useOS } from "@/os/OSContext";

export default function Contacts() {
  const { draftFor, openCompany } = useOS();
  return (
    <div className="p-8" data-testid="module-contacts">
      <div className="os-table">
        <div className="os-thead grid grid-cols-[1.4fr_1fr_1fr_1.4fr_0.6fr_0.6fr]">
          <div>Contact</div>
          <div>Title</div>
          <div>Company</div>
          <div>Email</div>
          <div>Verified</div>
          <div></div>
        </div>
        {contacts.map((p) => {
          const c = companyById(p.company);
          return (
            <div
              key={p.id}
              className="os-trow grid grid-cols-[1.4fr_1fr_1fr_1.4fr_0.6fr_0.6fr] items-center"
              data-testid={`contact-${p.id}`}
            >
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full bg-white/[0.06] flex items-center justify-center text-[10px] font-mono-xn text-white/70">
                  {p.name.split(" ").map((x) => x[0]).slice(0, 2).join("")}
                </div>
                <span className="text-white text-[13px]">{p.name}</span>
              </div>
              <div className="text-white/70 text-[12px]">{p.title}</div>
              <button
                className="text-white/85 text-[12px] hover:text-white text-left"
                onClick={() => openCompany(p.company)}
              >
                {c?.name}
              </button>
              <div className="text-white/60 text-[12px] tabular-nums truncate">{p.email}</div>
              <div className="text-[11px]">
                {p.verified ? (
                  <span className="os-pill os-pill-ok">Verified</span>
                ) : (
                  <span className="os-pill os-pill-warn">Pending</span>
                )}
              </div>
              <div>
                <button
                  className="os-mini-cta"
                  onClick={() => draftFor(p.company, p.id)}
                  data-testid={`contact-draft-${p.id}`}
                >
                  Draft →
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
