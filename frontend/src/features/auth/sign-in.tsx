/**
 * Alpha sign-in: paste a Supabase access token (ADR-012 — a GA blocker by
 * its own terms; the hosted flow arrives in V1.1 Phase 3). Identity
 * verification stays entirely server-side — this screen only stores the
 * bearer token the API will verify.
 */
import { useNavigate } from "@tanstack/react-router";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { api, setToken } from "@/lib/api/client";

export function SignIn() {
  const navigate = useNavigate();
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function submit() {
    setPending(true);
    setToken(value.trim());
    try {
      await api.me();
      await navigate({ to: "/" });
    } catch {
      setPending(false);
      setError("That token didn't verify. Nothing you did caused this — check it and try again.");
    }
  }

  return (
    <main className="animate-settle-in mx-auto max-w-md px-6 py-24">
      <h1 className="text-ink font-serif text-2xl">Xenia</h1>
      <p className="text-ink-muted mt-2 text-sm leading-relaxed">
        Your access token, please — your account team will have sent it.
      </p>
      <textarea
        data-testid="token-input"
        className="rounded-card border-hairline bg-surface text-ink mt-4 w-full border p-3 font-mono text-xs"
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
    </main>
  );
}
