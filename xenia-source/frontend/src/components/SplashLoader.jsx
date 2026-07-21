import { motion, AnimatePresence } from "framer-motion";
import BlackHoleMark from "@/components/BlackHoleMark";

// Splash / loading screen — the black hole mark is the whole story.
// Also usable as an inline loader by passing `size`.
export default function SplashLoader({ size = 96, label = "Xenia" }) {
  return (
    <AnimatePresence>
      <motion.div
        data-testid="splash-loader"
        initial={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        className="fixed inset-0 z-[80] flex flex-col items-center justify-center bg-[#030305]"
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.85 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
        >
          <BlackHoleMark size={size} />
        </motion.div>
        {label && (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.35, ease: [0.16, 1, 0.3, 1] }}
            className="mt-7 font-mono-xn text-[10.5px] tracking-[0.32em] text-white/45"
          >
            {label}
          </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
