import BlackHoleMark from "@/components/BlackHoleMark";

export default function Footer() {
  return (
    <footer
      data-testid="footer"
      className="relative w-full px-6 sm:px-10 lg:px-16 py-10 border-t border-white/[0.06]"
    >
      <div className="max-w-[1440px] mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <BlackHoleMark size={18} />
          <span className="font-display text-[15px] tracking-tight">Xenia</span>
          <span className="text-white/25 text-[11px] font-mono-xn ml-2">
            An unveiling · 2026
          </span>
        </div>
        <div className="flex items-center gap-6 text-[11.5px] text-white/40 font-mono-xn">
          <a data-testid="footer-x" href="#" className="hover:text-white/80 transition-colors">
            X
          </a>
          <a data-testid="footer-linkedin" href="#" className="hover:text-white/80 transition-colors">
            LinkedIn
          </a>
          <a data-testid="footer-contact" href="mailto:hello@xenia.ai" className="hover:text-white/80 transition-colors">
            hello@xenia.ai
          </a>
        </div>
      </div>
      <div className="max-w-[1440px] mx-auto mt-6 text-[10px] font-mono-xn text-white/25">
        Xenia is a private research preview. Nothing here is a public offering.
      </div>
    </footer>
  );
}
