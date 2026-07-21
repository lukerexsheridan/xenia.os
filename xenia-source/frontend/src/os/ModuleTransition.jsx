import { useEffect, useState, useRef } from "react";
import BlackHoleMark from "@/components/BlackHoleMark";

// Brief page-transition overlay shown when the active module changes inside
// XeniaOS. The black hole mark is the whole story — it flashes on, holds ~250ms,
// then fades out. Fires only after the first module change (not on initial mount).
export default function ModuleTransition({ moduleId, label }) {
  const [visible, setVisible] = useState(false);
  const firstRun = useRef(true);
  const hideTimer = useRef();

  useEffect(() => {
    if (firstRun.current) {
      firstRun.current = false;
      return;
    }
    setVisible(true);
    clearTimeout(hideTimer.current);
    hideTimer.current = setTimeout(() => setVisible(false), 520);
    return () => clearTimeout(hideTimer.current);
  }, [moduleId]);

  return (
    <div
      data-testid="module-transition"
      aria-hidden={!visible}
      className={`os-transition ${visible ? "os-transition-on" : ""}`}
    >
      <BlackHoleMark size={44} />
      <div className="os-transition-label">{label}</div>
    </div>
  );
}
