// Shared scroll progress state. Populated by the Lenis scroll listener in Experience.jsx.
// Values are updated imperatively (no React re-renders) so the R3F frame loop can read them cheaply.
export const scrollState = {
  progress: 0, // 0..1 across the whole page
  act: 0, // 0..6 (7 acts)
  actProgress: 0, // 0..1 within the current act
};

export const mouseState = {
  x: 0, // -1..1
  y: 0, // -1..1
  tx: 0, // smoothed
  ty: 0,
};
