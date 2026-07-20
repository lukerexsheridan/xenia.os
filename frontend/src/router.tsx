/**
 * Code-based route tree (ADR-002: TanStack Router).
 *
 * The authenticated shell (queue, DNA, prospects) and the minimal public
 * layout (auth screens, shared-brief view) arrive with Epic 10 (Doc 10,
 * Sprints 17–19). The skeleton ships a single index route.
 */
import { createRootRoute, createRoute, createRouter, Outlet } from "@tanstack/react-router";

import { SkeletonStatus } from "@/features/onboarding/skeleton-status";

const rootRoute = createRootRoute({
  component: () => (
    <div className="bg-background text-foreground min-h-screen">
      <Outlet />
    </div>
  ),
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: SkeletonStatus,
});

const routeTree = rootRoute.addChildren([indexRoute]);

export const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
