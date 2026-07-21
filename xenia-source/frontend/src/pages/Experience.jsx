import { useEffect, useState } from "react";
import Lenis from "lenis";
import Nav from "@/components/Nav";
import CursorTrail from "@/components/CursorTrail";
import AmbientAudio from "@/components/AmbientAudio";
import ProductHero from "@/components/ProductHero";
import ValueStrip from "@/components/ValueStrip";
import RequestAccess from "@/components/RequestAccess";
import Footer from "@/components/Footer";
import SplashLoader from "@/components/SplashLoader";

// Product-first layout. No fullscreen cosmic 3D scene — the black hole
// lives on as Xenia's brand mark (nav, splash, loading states, AI indicators).
// The interactive XeniaOS is the hero.
export default function Experience() {
  const [reducedMotion, setReducedMotion] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const mql = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReducedMotion(mql.matches);
    const listener = (e) => setReducedMotion(e.matches);
    mql.addEventListener?.("change", listener);
    return () => mql.removeEventListener?.("change", listener);
  }, []);

  // Splash — 1.2s reveal so the black hole mark is the first thing seen.
  useEffect(() => {
    const t = setTimeout(() => setReady(true), reducedMotion ? 200 : 1200);
    return () => clearTimeout(t);
  }, [reducedMotion]);

  useEffect(() => {
    if (reducedMotion) return;
    const lenis = new Lenis({
      duration: 1.05,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
    });
    let raf;
    const tick = (t) => {
      lenis.raf(t);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf);
      lenis.destroy();
    };
  }, [reducedMotion]);

  return (
    <div
      className="relative min-h-screen bg-[#030305] text-white vignette grain"
      data-testid="experience-root"
    >
      {/* Ambient royal-blue backdrop — supports the product, never competes with it. */}
      <div className="fixed inset-0 z-0 pointer-events-none" aria-hidden>
        <div className="absolute inset-0 ambient-royal" />
        <div className="absolute inset-0 star-field" />
      </div>

      <Nav />
      <AmbientAudio />
      <CursorTrail />

      <main className="relative z-10">
        <ProductHero />
        <ValueStrip />
        <RequestAccess />
        <Footer />
      </main>

      {!ready && <SplashLoader />}
    </div>
  );
}
