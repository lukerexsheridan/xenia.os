import "./BlackHoleMark.css";

// Xenia's brand mark — a Gargantua-style photoreal black hole.
// Layers (back → front):
//   1. Halo — warm ambient bloom around the whole object
//   2. Disc — nearly edge-on accretion disc extending beyond the sphere
//      as horizontal streaks; slow rotation makes matter appear to stream
//   3. Disc inner — a faster inner streak layer just outside the horizon
//   4. Photon ring — the razor-thin bright edge hugging the event horizon
//   5. Core — deep, perfect black event horizon
// Scales cleanly from ~18px (topbar) to 200px+ (splash / loading screens).
export default function BlackHoleMark({
  size = 28,
  className = "",
  style = {},
  glow = true,
  spin = true,
}) {
  return (
    <span
      className={`bh-mark ${spin ? "bh-mark-spin" : ""} ${className}`}
      style={{ width: size, height: size, ...style }}
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
