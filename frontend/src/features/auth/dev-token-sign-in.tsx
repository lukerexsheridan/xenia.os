/**
 * Developer sign-in: paste a Supabase access token directly. Used only
 * when no Supabase project is configured (local development, CI, E2E) —
 * production deployments never render this (see MagicLinkSignIn).
 */
import { useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api/client";
import { setDevToken } from "@/lib/auth/client";

export function DevTokenSignIn() {
  const navigate = useNavigate();
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function submit() {
    setPending(true);
    setDevToken(value.trim());
    try {
      await api.me();
      await navigate({ to: "/" });
    } catch {
      setPending(false);
      setError("That token didn't verify. Nothing you did caused this — check it and try again.");
    }
  }

  return (
    <div className="animate-settle-in">
      <h1 className="text-ink font-display text-2xl">Xenia</h1>
      <p className="text-ink-muted mt-2 text-sm leading-relaxed">
        No hosted auth is configured in this environment. Paste an access token to continue.
      </p>
      <textarea
        data-testid="token-input"
        className="rounded-card border-hairline bg-surface-2 text-ink mt-4 w-full border p-3 font-mono text-xs"
        rows={4}
        value={value}
        onChange={(event) => setValue(event.target.value)}
      />
      <Button
        data-testid="sign-in"
        size="lg"
        className="mt-3"
        disabled={pending}
        onClick={() => void submit()}
      >
        {pending ? "Checking…" : "Sign in"}
      </Button>
      {error && <p className="animate-settle-in text-danger-ink mt-3 text-sm">{error}</p>}
    </div>
  );
}
