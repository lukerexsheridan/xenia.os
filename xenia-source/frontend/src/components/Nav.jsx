import { motion } from "framer-motion";
import BlackHoleMark from "@/components/BlackHoleMark";

// Permanent floating glass navigation. Black hole mark is Xenia's identity.
export default function Nav() {
  return (
    <motion.header
      data-testid="xn-nav"
      initial={{ y: -30, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 1, ease: [0.16, 1, 0.3, 1], delay: 0.25 }}
      className="fixed top-5 left-1/2 -translate-x-1/2 z-40"
    >
      <div className="glass rounded-full pl-3 pr-4 py-2 flex items-center gap-5 min-w-[340px]">
        <a
          href="#"
          data-testid="nav-logo"
          className="flex items-center gap-2.5 group"
          aria-label="Xenia"
        >
          <BlackHoleMark size={26} />
          <span className="font-display text-[15px] tracking-tight text-white">
            Xenia
          </span>
        </a>
        <span className="h-3 w-px bg-white/10" />
        <nav className="hidden sm:flex items-center gap-5 text-[12px] text-white/60">
          <a
            data-testid="nav-product"
            href="#product"
            className="hover:text-white transition-colors nav-link"
          >
            Product
          </a>
          <a
            data-testid="nav-access"
            href="#access"
            className="hover:text-white transition-colors nav-link"
          >
            Access
          </a>
        </nav>
        <span className="h-3 w-px bg-white/10 hidden sm:block" />
        <a
          data-testid="nav-cta"
          href="#access"
          className="inline-flex items-center gap-1.5 rounded-full bg-royal text-white px-3.5 py-1.5 text-[11.5px] font-mono-xn shadow-[0_6px_28px_-8px_rgba(76,108,255,0.55)] hover:brightness-110 transition-all"
        >
          Request access
          <span className="opacity-80">→</span>
        </a>
      </div>
    </motion.header>
  );
}
