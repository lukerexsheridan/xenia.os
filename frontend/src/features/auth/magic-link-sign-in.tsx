/**
 * Seamless onboarding (Doc 11 Phase 4): one field, no password. Entering
 * an email that hasn't signed in before creates the workspace on first
 * use — sign-up and sign-in are the same act, as they should be.
 */
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { signInWithMagicLink } from "@/lib/auth/client";

export function MagicLinkSignIn() {
  const [email, setEmail] = useState("");
  const [pending, setPending] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setPending(true);
    setError(null);
    try {
      await signInWithMagicLink(email.trim());
      setSent(true);
    } catch {
      setError(
        "That link didn't send — nothing you did caused this. Check the address and try again.",
      );
    } finally {
      setPending(false);
    }
  }

  if (sent) {
    return (
      <div className="animate-settle-in" data-testid="magic-link-sent">
        <h1 className="text-ink font-display text-2xl">Check your email</h1>
        <p className="text-ink-muted mt-2 text-sm leading-relaxed">
          We sent a sign-in link to <strong className="text-ink">{email}</strong>. Open it on this
          device and you&apos;re in — nothing to type.
        </p>
      </div>
    );
  }

  return (
    <div className="animate-settle-in">
      <h1 className="text-ink font-display text-2xl">Xenia</h1>
      <p className="text-ink-muted mt-2 text-sm leading-relaxed">
        Your email, please. We&apos;ll send a link — no password to remember.
      </p>
      <input
        data-testid="email-input"
        type="email"
        autoComplete="email"
        placeholder="you@youragency.com"
        className="rounded-card border-hairline bg-surface-2 text-ink mt-4 w-full border p-3 text-sm"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && email.trim() && !pending) void submit();
        }}
      />
      <Button
        data-testid="send-magic-link"
        size="lg"
        className="mt-3"
        disabled={pending || !email.trim()}
        onClick={() => void submit()}
      >
        {pending ? "Sending…" : "Send me a link"}
      </Button>
      {error && <p className="animate-settle-in text-danger-ink mt-3 text-sm">{error}</p>}
    </div>
  );
}
