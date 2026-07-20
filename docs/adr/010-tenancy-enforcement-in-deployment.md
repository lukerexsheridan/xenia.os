# ADR-010: Tenancy enforcement model in deployment

Status: Accepted
Date: 2026-07-20

## Context

Doc 08 §8 mandates belt-and-braces tenancy: workspace-scoped repositories
(the belt) plus Postgres RLS, enabled and forced on every Ring-1 table (the
braces), keyed on the transaction-local setting `app.workspace_id`. The
hardening review found that the braces only bind for roles subject to RLS:
local and CI database users are superusers (RLS-exempt), and nothing
documented the production role model. Worker jobs also ran without setting
the tenancy context at all — invisible under a superuser, broken or leaky
under a least-privileged role.

## Decision

1. **Every transaction that touches Ring-1 data attaches its workspace
   context** — API requests via the auth dependencies (as before), and now
   every per-workspace worker job (`assemble_workspace_queue`,
   `weekly_brief_send`, `outcome_prompt`, the Stripe billing sync) via
   `set_app_context` at the top of its handler. A source-level test pins
   this contract for all Ring-1-touching handlers.
2. **Cross-tenant sweeps are worker-only and enumerate IDs, never
   content.** The Monday sweep and the weekly-brief sweep read workspace
   ids/timezones and fan out one per-workspace job each; all tenant-scoped
   work then runs under that tenant's context.
3. **The production role model is two-tier.** The API service should run as
   a dedicated non-superuser role subject to RLS wherever the platform
   permits creating one; the worker requires either the same role with the
   sweeps' tables readable, or (pragmatically, on managed Postgres that
   hands out an owner role) an owner/`BYPASSRLS` role. In the latter
   configuration RLS functions as an audited canary and a raw-SQL backstop
   for the API path, and the *enforced* guarantee is the repository belt +
   the context contract above. `python -m app.scripts.rls_audit` verifies
   the structural half in any environment.

## Consequences

- Worker behaviour is now identical under superuser and least-privileged
  roles, so the role can be tightened later without code change.
- Signup provisioning and cross-tenant sweeps still require a role that can
  write/read outside an existing tenancy context; a fully RLS-subject
  single role is not supported and is not claimed.
- Residual risk, recorded in DEBT.md: no CI job yet exercises the suite
  under a non-superuser application role beyond the RLS canary's probe.
