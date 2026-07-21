import { notifications } from "@/os/data";

export default function Notifications() {
  return (
    <div className="p-8" data-testid="module-notifications">
      <div className="os-card">
        {notifications.map((n) => (
          <div
            key={n.id}
            className="flex items-start gap-4 px-5 py-4 border-b border-white/[0.05] last:border-0"
            data-testid={`notif-${n.id}`}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-white mt-2" />
            <div className="flex-1">
              <div className="text-white text-[13.5px]">{n.label}</div>
              <div className="text-white/55 text-[12px] mt-0.5">{n.detail}</div>
            </div>
            <div className="text-[10.5px] font-mono-xn text-white/40 pt-1">
              {n.ts}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
