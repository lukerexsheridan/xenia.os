/**
 * API client seam (AP4/AP5): every server interaction goes through here.
 *
 * Once the API grows real resources, types are generated from the OpenAPI
 * contract (`make openapi` then `npm run generate:api` — ADR-003) and this
 * module wraps them in typed fetch helpers consumed by per-feature hooks
 * (useQueue, useBrief, ...). Hand-written request code outside this module
 * is a review failure.
 */

export const API_BASE_URL: string = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface HealthResponse {
  status: string;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/health`);
  if (!response.ok) throw new Error(`Health check failed: ${response.status}`);
  return (await response.json()) as HealthResponse;
}
