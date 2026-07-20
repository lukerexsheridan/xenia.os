# Runbook — Deletion / rights request

*A customer asks for their data, or for it to be gone (UK GDPR; Doc 05).*

1. **Access request:** the offboarding export answers it without leaving:
   `GET /internal/workbench/workspaces/{id}/offboarding-export` returns
   everything that is theirs (DNA + history, prospects-in-relationship,
   approved briefs, teaching events, audit trail, interview transcript).
   Send it to the verified owner address only.
2. **Erasure / departure:** export first, always — then
   `POST /internal/workbench/workspaces/{id}/offboard` with the exact
   workspace name as confirmation. Deletion cascades from the workspace row;
   the departure-rule E2E in CI proves nothing Ring-1 survives.
3. **What remains, and why that's right:** Ring-2 world facts (public
   business records, snapshots, evidence) carry no workspace reference —
   they are public-source observations about businesses, not the customer's
   personal data. Billing records remain at Stripe under its own retention.
4. **Verify:** run `python -m app.scripts.rls_audit` (structure) and the
   departure E2E's count query (content) if in doubt.
5. Respond within the statutory window; log request, date, and completion in
   `docs/runbooks/incidents/`.
