import { useEffect, useRef, useState } from "react";
import { scrollState } from "@/lib/scrollState";

// Ambient audio designed like a Vangelis / Eno drone:
// Layered sines + a slow low-pass filter modulation that opens as the visitor
// scrolls deeper into the experience. Each act nudges the timbre subtly.
// Off by default (browser autoplay policy); a small nav-adjacent button starts it.
export default function AmbientAudio() {
  const [enabled, setEnabled] = useState(false);
  const engineRef = useRef();

  useEffect(() => {
    if (!enabled) return;
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;

    const ctx = new AudioCtx();
    const master = ctx.createGain();
    master.gain.value = 0;
    master.connect(ctx.destination);

    // Slow fade in
    master.gain.linearRampToValueAtTime(0.12, ctx.currentTime + 3);

    // Low-pass filter as the "eyes" of the drone — its cutoff shifts by act
    const filter = ctx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.value = 380;
    filter.Q.value = 0.9;
    filter.connect(master);

    // Sub-bass — very quiet, adds weight
    const sub = ctx.createOscillator();
    sub.type = "sine";
    sub.frequency.value = 45;
    const subGain = ctx.createGain();
    subGain.gain.value = 0.15;
    sub.connect(subGain).connect(filter);

    // Base drone — root note with slow detuned second oscillator for movement
    const osc1 = ctx.createOscillator();
    osc1.type = "sine";
    osc1.frequency.value = 110; // A2
    const osc2 = ctx.createOscillator();
    osc2.type = "sine";
    osc2.frequency.value = 110.4; // slight detune
    const droneGain = ctx.createGain();
    droneGain.gain.value = 0.42;
    osc1.connect(droneGain);
    osc2.connect(droneGain);
    droneGain.connect(filter);

    // Fifth — layered above for lift
    const osc3 = ctx.createOscillator();
    osc3.type = "sine";
    osc3.frequency.value = 165; // E3
    const fifthGain = ctx.createGain();
    fifthGain.gain.value = 0.14;
    osc3.connect(fifthGain).connect(filter);

    // Bell — a higher harmonic that appears when accretion disc lights up
    const osc4 = ctx.createOscillator();
    osc4.type = "triangle";
    osc4.frequency.value = 440;
    const bellGain = ctx.createGain();
    bellGain.gain.value = 0.0;
    osc4.connect(bellGain).connect(filter);

    // Slow LFO on filter cutoff — organic movement
    const lfo = ctx.createOscillator();
    lfo.type = "sine";
    lfo.frequency.value = 0.06;
    const lfoGain = ctx.createGain();
    lfoGain.gain.value = 160;
    lfo.connect(lfoGain).connect(filter.frequency);

    [sub, osc1, osc2, osc3, osc4, lfo].forEach((o) => o.start());

    // Live-modulate params from scroll progress
    let raf;
    const tick = () => {
      const p = scrollState.progress;
      // Filter opens from ~380Hz to ~2200Hz as visitor scrolls
      filter.frequency.setTargetAtTime(380 + p * 1900, ctx.currentTime, 0.4);
      // Bell rises around Act III-IV (0.3..0.6) then falls
      const bell = Math.max(0, 1 - Math.abs(p - 0.5) / 0.28);
      bellGain.gain.setTargetAtTime(0.06 * bell, ctx.currentTime, 0.4);
      // Fifth swells near neutron-star phase (Acts VI-VII)
      const lift = p > 0.7 ? (p - 0.7) / 0.3 : 0;
      fifthGain.gain.setTargetAtTime(0.14 + lift * 0.14, ctx.currentTime, 0.4);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);

    engineRef.current = { ctx, master, raf, oscs: [sub, osc1, osc2, osc3, osc4, lfo] };

    return () => {
      cancelAnimationFrame(raf);
      try {
        master.gain.cancelScheduledValues(ctx.currentTime);
        master.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.6);
        setTimeout(() => {
          [sub, osc1, osc2, osc3, osc4, lfo].forEach((o) => {
            try { o.stop(); } catch (_e) {}
          });
          ctx.close();
        }, 700);
      } catch (_e) {}
    };
  }, [enabled]);

  return (
    <button
      data-testid="ambient-audio-toggle"
      onClick={() => setEnabled((v) => !v)}
      aria-label={enabled ? "Mute ambient audio" : "Play ambient audio"}
      className="fixed top-6 right-6 z-40 glass rounded-full w-10 h-10 flex items-center justify-center hover:border-white/30 transition-colors"
      style={{ borderColor: enabled ? "rgba(255,255,255,0.35)" : undefined }}
    >
      {enabled ? (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.6" strokeLinecap="round">
          <path d="M4 10v4h4l5 4V6L8 10H4z" />
          <path d="M16 8c1.5 1.5 1.5 6.5 0 8" />
          <path d="M19 5c3 3 3 11 0 14" />
        </svg>
      ) : (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.6" strokeLinecap="round" opacity="0.7">
          <path d="M4 10v4h4l5 4V6L8 10H4z" />
          <path d="M17 9l4 6M21 9l-4 6" />
        </svg>
      )}
    </button>
  );
}
