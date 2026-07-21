/**
 * Xenia's brand mark — the Gargantua-style black hole (ADR-014; ported
 * from xenia-source). Pure CSS/SVG: renders identically from 18px topbar
 * to 200px loading moments at negligible cost. Its slow disc rotation is
 * the brand's one ambient motion and obeys the global reduced-motion law.
 */
import "./black-hole-mark.css";

export function BlackHoleMark({
  size = 24,
  spin = true,
  glow = true,
  className = "",
}: {
  size?: number;
  spin?: boolean;
  glow?: boolean;
  className?: string;
}) {
  return (
    <span
      className={`bh-mark ${spin ? "bh-mark-spin" : ""} ${className}`}
      style={{ width: size, height: size }}
      data-testid="bh-mark"
      aria-hidden
    >
      {glow && <span className="bh-halo" />}
      <span className="bh-disc" />
      <span className="bh-arch" />
      <span className="bh-disc-inner" />
      <span className="bh-photon" />
      <span className="bh-core" />
    </span>
  );
}
