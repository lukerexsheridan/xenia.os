import { useEffect, useRef } from "react";

// Luminous cursor with a fading light trail.
// Draws to a full-screen canvas layered above the 3D scene but under the UI/toasts.
// - Softly lit dot follows the pointer with slight lag (spring).
// - Positions are recorded to a ring buffer and rendered as a decaying poly-line + glowing points.
// - Hidden on touch devices and when prefers-reduced-motion is set.
export default function CursorTrail() {
  const canvasRef = useRef();
  const dotRef = useRef();

  useEffect(() => {
    const rm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const touch = window.matchMedia("(pointer: coarse)").matches;
    if (rm || touch) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    let raf;
    const DPR = Math.min(window.devicePixelRatio || 1, 2);
    const resize = () => {
      canvas.width = window.innerWidth * DPR;
      canvas.height = window.innerHeight * DPR;
      canvas.style.width = `${window.innerWidth}px`;
      canvas.style.height = `${window.innerHeight}px`;
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    };
    resize();
    window.addEventListener("resize", resize);

    const state = {
      x: window.innerWidth / 2,
      y: window.innerHeight / 2,
      tx: window.innerWidth / 2,
      ty: window.innerHeight / 2,
      moved: false,
      trail: [], // {x, y, life}
      lastRecord: 0,
    };

    const onMove = (e) => {
      state.tx = e.clientX;
      state.ty = e.clientY;
      state.moved = true;
      // Show custom cursor by hiding default when trail is engaged
      document.documentElement.classList.add("xn-cursor-active");
    };
    window.addEventListener("mousemove", onMove);

    const render = (t) => {
      // Spring toward target
      state.x += (state.tx - state.x) * 0.16;
      state.y += (state.ty - state.y) * 0.16;

      // Record trail sample every ~16ms
      if (t - state.lastRecord > 14) {
        state.trail.push({ x: state.x, y: state.y, life: 1 });
        if (state.trail.length > 55) state.trail.shift();
        state.lastRecord = t;
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (state.moved) {
        // Trail — polyline with tapered stroke and additive blend
        ctx.globalCompositeOperation = "lighter";
        for (let i = 1; i < state.trail.length; i++) {
          const p0 = state.trail[i - 1];
          const p1 = state.trail[i];
          const frac = i / state.trail.length;
          const alpha = frac * 0.35;
          ctx.strokeStyle = `rgba(255, 240, 220, ${alpha})`;
          ctx.lineWidth = 1 + frac * 2;
          ctx.beginPath();
          ctx.moveTo(p0.x, p0.y);
          ctx.lineTo(p1.x, p1.y);
          ctx.stroke();
        }
        // Decay trail (visually happens via re-record; positions also drift a touch)
        state.trail.forEach((p) => {
          p.life *= 0.965;
        });

        // Glow dot at head
        const grad = ctx.createRadialGradient(state.x, state.y, 0, state.x, state.y, 22);
        grad.addColorStop(0, "rgba(255, 255, 255, 0.85)");
        grad.addColorStop(0.35, "rgba(255, 230, 200, 0.35)");
        grad.addColorStop(1, "rgba(255, 230, 200, 0)");
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(state.x, state.y, 22, 0, Math.PI * 2);
        ctx.fill();

        // Crisp core dot
        ctx.globalCompositeOperation = "source-over";
        ctx.fillStyle = "rgba(255, 255, 255, 0.95)";
        ctx.beginPath();
        ctx.arc(state.x, state.y, 2.4, 0, Math.PI * 2);
        ctx.fill();
      }

      raf = requestAnimationFrame(render);
    };
    raf = requestAnimationFrame(render);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("resize", resize);
      document.documentElement.classList.remove("xn-cursor-active");
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-[60] pointer-events-none"
      data-testid="cursor-trail"
    />
  );
}
