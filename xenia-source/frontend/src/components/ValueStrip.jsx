import { motion } from "framer-motion";
import BlackHoleMark from "@/components/BlackHoleMark";

// Condensed value strip that lives directly under the product.
// Every card supports the product story — no cinematic filler.
const ITEMS = [
  {
    title: "Signal, not noise",
    body: "Xenia continuously reads funding rounds, hiring shifts, stack changes and quiet intent — so your pipeline hears what matters, and nothing else.",
  },
  {
    title: "Draft in your voice",
    body: "Every outreach is written by a Claude Sonnet layer trained on your best replies. The reasoning panel shows exactly why each line was chosen.",
  },
  {
    title: "Runs like software you love",
    body: "⌘K palette, keyboard-first flows, glassmorphic detail panes. Xenia feels like the tool you'd design if you never had to compromise.",
  },
];

export default function ValueStrip() {
  return (
    <section
      data-testid="value-strip"
      className="relative w-full px-4 sm:px-6 lg:px-10 py-10"
    >
      <div className="max-w-[1440px] mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {ITEMS.map((it, i) => (
            <motion.div
              key={it.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1], delay: i * 0.06 }}
              className="glass rounded-2xl p-5 relative overflow-hidden group"
            >
              <div className="flex items-center gap-2.5 mb-3">
                <BlackHoleMark size={18} />
                <div className="font-mono-xn text-[10px] text-white/40">
                  0{i + 1}
                </div>
              </div>
              <div className="font-display text-[19px] text-white leading-tight tracking-tight">
                {it.title}
              </div>
              <p className="mt-2 text-white/55 text-[13px] leading-relaxed">
                {it.body}
              </p>
              <span className="absolute -bottom-px left-4 right-4 h-px bg-gradient-to-r from-transparent via-[rgba(76,108,255,0.35)] to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
