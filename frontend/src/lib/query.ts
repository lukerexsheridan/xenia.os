/**
 * TanStack Query is the ONLY server-state mechanism (Doc 08 §4).
 * No Redux, no global store of server data. Cache keys are standardised per
 * resource; invalidation rules are colocated with their mutations.
 */
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // The weekly rhythm means most sessions open on warm, fresh-enough
      // data; background refetch keeps Monday's queue honest (Doc 08 §4).
      staleTime: 30_000,
      retry: 1,
    },
  },
});
