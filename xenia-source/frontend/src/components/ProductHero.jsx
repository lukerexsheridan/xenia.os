import { motion } from "framer-motion";
import XeniaOS from "@/os/XeniaOS";

// Product-first hero: a compact headline strip sits above the live XeniaOS,
// which dominates the viewport. Every animation here supports the product;
// nothing competes with it.
export default function ProductHero() {
  return (
    <section
      data-testid="product-hero"
      id="product"
      className="relative w-full pt-24 pb-6 px-4 sm:px-6 lg:px-10"
    >
      <div className="max-w-[1440px] mx-auto">
        <div className="flex items-end justify-between gap-8 mb-5">
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1], delay: 0.35 }}
            className="min-w-0"
          >
            <div className="font-mono-xn text-[10px] text-white/40 mb-2.5 flex items-center gap-2.5">
              <span className="pulse-dot-blue" />
              <span>Private preview</span>
              <span className="text-white/20">·</span>
              <span>Feb 2026</span>
            </div>
            <h1 className="font-display text-3xl sm:text-4xl lg:text-[46px] leading-[1.02] tracking-tight text-white max-w-3xl">
              The AI operating system for{" "}
              <span className="text-blue-signature">modern agencies</span>.
            </h1>
            <p className="mt-3 text-white/55 text-[13.5px] sm:text-[14px] leading-relaxed max-w-xl">
              Below is Xenia, running live. Navigate the modules, open a company,
              press ⌘K, draft an email with real Claude Sonnet. It is the product,
              not a picture of it.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1], delay: 0.55 }}
            className="hidden lg:flex items-center gap-3 shrink-0"
          >
            <a
              data-testid="hero-cta"
              href="#access"
              className="inline-flex items-center gap-2 rounded-full bg-royal text-white px-5 py-2.5 text-[12px] font-mono-xn shadow-[0_10px_40px_-10px_rgba(76,108,255,0.6)] hover:brightness-110 transition-all"
            >
              Request access
              <span className="opacity-70">→</span>
            </a>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 24, scale: 0.995 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 1.05, ease: [0.16, 1, 0.3, 1], delay: 0.65 }}
        >
          <XeniaOS />
        </motion.div>
      </div>
    </section>
  );
}
