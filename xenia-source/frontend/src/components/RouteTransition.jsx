import { useEffect, useState, useRef } from "react";
import { useLocation } from "react-router-dom";
import BlackHoleMark from "@/components/BlackHoleMark";

// Route-level transition. Watches `pathname` changes and flashes an overlay
// with the black hole mark + a route label for ~600ms. Skipped on first mount
// so entering the site never double-covers the SplashLoader.
const LABELS = {
  "/": "Xenia",
  "/admin": "Admin",
};

export default function RouteTransition() {
  const { pathname } = useLocation();
  const [visible, setVisible] = useState(false);
  const [label, setLabel] = useState(LABELS[pathname] || "");
  const firstRun = useRef(true);
  const hideTimer = useRef();

  useEffect(() => {
    if (firstRun.current) {
      firstRun.current = false;
      return;
    }
    setLabel(LABELS[pathname] || pathname.replace("/", "") || "Xenia");
    setVisible(true);
    clearTimeout(hideTimer.current);
    hideTimer.current = setTimeout(() => setVisible(false), 620);
    return () => clearTimeout(hideTimer.current);
  }, [pathname]);

  return (
    <div
      data-testid="route-transition"
      aria-hidden={!visible}
      className={`route-transition ${visible ? "route-transition-on" : ""}`}
    >
      <BlackHoleMark size={72} />
      <div className="route-transition-label">{label}</div>
    </div>
  );
}
