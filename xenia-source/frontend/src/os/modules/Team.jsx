import { team } from "@/os/data";

export default function Team() {
  return (
    <div className="p-8 grid grid-cols-3 gap-4" data-testid="module-team">
      {team.map((u) => (
        <div key={u.id} className="os-card p-5" data-testid={`team-${u.id}`}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-white/[0.06] flex items-center justify-center text-[12px] font-mono-xn">
              {u.name.split(" ").map((x) => x[0]).slice(0, 2).join("")}
            </div>
            <div>
              <div className="text-white text-[14px]">{u.name}</div>
              <div className="text-white/50 text-[11.5px]">{u.role}</div>
            </div>
            <div className={`ml-auto w-2 h-2 rounded-full ${u.online ? "bg-white" : "bg-white/25"}`} />
          </div>
        </div>
      ))}
    </div>
  );
}
