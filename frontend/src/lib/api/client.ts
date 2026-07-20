/**
 * API client seam (AP4/AP5): every server interaction goes through here.
 *
 * Types come from the generated OpenAPI schema (`make openapi` then
 * `npm run generate:api` — ADR-003). Hand-written request code outside this
 * module is a review failure. The client renders what the API says and
 * never derives a rule: confidence words, rank reasons, effect sentences,
 * and lesson narrations are all server-authored strings (AP5).
 */

import type { components } from "@/lib/api/schema";

export const API_BASE_URL: string = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const TOKEN_KEY = "xenia_access_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

/** The plain-voice error (Doc 06 §9): what happened, in words. */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });
  if (!response.ok) {
    let code = "error";
    let message = "Something went wrong on our side. Nothing you did caused this.";
    try {
      const body = (await response.json()) as { code?: string; message?: string };
      code = body.code ?? code;
      message = body.message ?? message;
    } catch {
      // A non-JSON failure keeps the plain-voice default.
    }
    throw new ApiError(response.status, code, message);
  }
  return (await response.json()) as T;
}

// ── Types (generated schema, aliased for the features) ──────────────────────

export type MeResponse = components["schemas"]["MeResponse"];
export type QueueResponse = components["schemas"]["QueueResponse"];
export type QueueItem = components["schemas"]["QueueItemResponse"];
export type DecisionResponse = components["schemas"]["DecisionResponse"];
export type CorrectionResponse = components["schemas"]["CorrectionResponse"];
export type OutcomeResponse = components["schemas"]["OutcomeResponse"];
export type DeliveredBrief = components["schemas"]["DeliveredBriefResponse"];
export type DnaResponse = components["schemas"]["DnaResponse"];
export type ProposalSummary = components["schemas"]["ProposalSummaryResponse"];
export type InterviewState = components["schemas"]["InterviewStateResponse"];
export type DecisionKind = components["schemas"]["DecisionKind"];
export type DeclineChip = components["schemas"]["DeclineChip"];
export type CorrectionTargetKind = components["schemas"]["CorrectionTargetKind"];
export type OutcomeKind = components["schemas"]["OutcomeKind"];

// ── Resources ───────────────────────────────────────────────────────────────

export const api = {
  me: () => request<MeResponse>("/v1/me"),

  queue: () => request<QueueResponse>("/v1/queue"),

  decide: (recommendationId: string, kind: DecisionKind, chip?: DeclineChip, reason?: string) =>
    request<DecisionResponse>(`/v1/recommendations/${recommendationId}/decision`, {
      method: "POST",
      body: JSON.stringify({ kind, chip: chip ?? null, reason: reason ?? null }),
    }),

  correct: (targetKind: CorrectionTargetKind, targetId: string, reason?: string) =>
    request<CorrectionResponse>("/v1/corrections", {
      method: "POST",
      body: JSON.stringify({
        target_kind: targetKind,
        target_id: targetId,
        reason: reason ?? null,
      }),
    }),

  recordOutcome: (prospectId: string, kind: OutcomeKind, occurredAt: string, reason?: string) =>
    request<OutcomeResponse>(`/v1/prospects/${prospectId}/outcomes`, {
      method: "POST",
      body: JSON.stringify({ kind, occurred_at: occurredAt, reason: reason ?? null }),
    }),

  brief: (prospectId: string) => request<DeliveredBrief>(`/v1/prospects/${prospectId}/brief`),

  dna: () => request<DnaResponse>("/v1/dna"),

  endorseDna: () => request<DnaResponse>("/v1/dna/endorse", { method: "POST", body: "{}" }),

  decideProposal: (proposalId: string, endorse: boolean) =>
    request<ProposalSummary>(`/v1/dna/proposals/${proposalId}/decision`, {
      method: "POST",
      body: JSON.stringify({ endorse }),
    }),

  interview: () => request<InterviewState>("/v1/interview"),

  answerInterview: (questionKey: string, text: string) =>
    request<InterviewState>("/v1/interview/answers", {
      method: "POST",
      body: JSON.stringify({ question_key: questionKey, text }),
    }),

  briefPdfUrl: (prospectId: string) => `${API_BASE_URL}/v1/prospects/${prospectId}/brief.pdf`,
  dnaPdfUrl: () => `${API_BASE_URL}/v1/dna/document.pdf`,
  prospectsCsvUrl: () => `${API_BASE_URL}/v1/prospects/export.csv`,
};
