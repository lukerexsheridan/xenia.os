/**
 * Route tree (ADR-002: TanStack Router): a minimal public layout (sign-in)
 * and the authenticated workspace shell — queue, DNA, interview, prospects
 * (Doc 08 §4). Guards redirect unauthenticated sessions to /signin.
 */
import {
  createRootRoute,
  createRoute,
  createRouter,
  Link,
  Outlet,
  redirect,
} from "@tanstack/react-router";

import { SignIn } from "@/features/auth/sign-in";
import { DnaView } from "@/features/dna/dna-view";
import { InterviewView } from "@/features/onboarding/interview-view";
import { ProspectView } from "@/features/prospects/prospect-view";
import { QueueView } from "@/features/queue/queue-view";
import { api, clearToken, getToken } from "@/lib/api/client";

const rootRoute = createRootRoute({
  component: () => (
    <div className="bg-paper text-ink min-h-screen">
      <Outlet />
    </div>
  ),
});

const signInRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/signin",
  component: SignIn,
});

const shellRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: "shell",
  beforeLoad: () => {
    if (!getToken()) throw redirect({ to: "/signin" });
  },
  component: () => (
    <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6 sm:py-8">
      <header className="border-hairline flex items-baseline justify-between border-b pb-4">
        <h1 className="text-ink font-serif text-xl">Xenia</h1>
        <nav className="text-ink-muted flex flex-wrap gap-x-5 gap-y-2 text-sm">
          <Link
            to="/"
            className="transition-settle hover:text-ink"
            activeProps={{ className: "font-medium text-ink" }}
          >
            This week
          </Link>
          <Link
            to="/dna"
            className="transition-settle hover:text-ink"
            activeProps={{ className: "font-medium text-ink" }}
          >
            Your DNA
          </Link>
          <Link
            to="/interview"
            className="transition-settle hover:text-ink"
            activeProps={{ className: "font-medium text-ink" }}
          >
            Interview
          </Link>
          <button
            className="transition-settle hover:text-ink"
            onClick={() => void api.downloadProspectsCsv()}
          >
            Export
          </button>
          <button
            className="transition-settle text-ink-faint hover:text-ink"
            onClick={() => {
              clearToken();
              window.location.assign("/signin");
            }}
          >
            Sign out
          </button>
        </nav>
      </header>
      <main className="py-6">
        <Outlet />
      </main>
    </div>
  ),
});

const queueRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: "/",
  component: QueueView,
});

const dnaRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: "/dna",
  component: DnaView,
});

const interviewRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: "/interview",
  component: InterviewView,
});

const prospectRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: "/prospects/$prospectId",
  component: function ProspectRoute() {
    const { prospectId } = prospectRoute.useParams();
    return <ProspectView prospectId={prospectId} />;
  },
});

const routeTree = rootRoute.addChildren([
  signInRoute,
  shellRoute.addChildren([queueRoute, dnaRoute, interviewRoute, prospectRoute]),
]);

export const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
