/**
 * Sign-in entry point (ADR-015): the real hosted flow when a Supabase
 * project is configured, the developer fallback otherwise. Nothing else
 * in the app needs to know which one is active.
 */
import { DevTokenSignIn } from "@/features/auth/dev-token-sign-in";
import { MagicLinkSignIn } from "@/features/auth/magic-link-sign-in";
import { isSupabaseConfigured } from "@/lib/auth/client";

export function SignIn() {
  return (
    <main className="mx-auto max-w-md px-6 py-24">
      {isSupabaseConfigured() ? <MagicLinkSignIn /> : <DevTokenSignIn />}
    </main>
  );
}
