# Architecture Decision Records

Per [Doc 08 §11](../08_SYSTEM_ARCHITECTURE.md): numbered, in-repo, one page — context,
decision, alternatives, consequences. ADR-000 summarises the architecture document;
every open decision in Doc 08 §13 / Doc 10 §12 becomes an ADR when taken; **any
deviation from Documents 01–10 requires one** (the amendment procedure's engineering
face). Constitutional deviations escalate to a document amendment.

## Index

| # | Title | Status |
|---|---|---|
| [000](000-technical-architecture-summary.md) | Technical architecture summary | Accepted |
| [001](001-monorepo.md) | Monorepo | Accepted |
| [002](002-frontend-router.md) | TanStack Router for the SPA | Accepted |
| [003](003-openapi-codegen.md) | openapi-typescript for client types | Accepted |
| [004](004-object-storage.md) | S3-compatible object storage, MinIO locally | Accepted |
| [005](005-observability-vendors.md) | Sentry + deferred tracing backend | Accepted |
| [006](006-synthetic-fixtures.md) | Synthetic fixture strategy for non-production data | Accepted |

## Writing a new ADR

Copy the template below into `NNN-kebab-title.md`, number sequentially, add to the index.

```markdown
# ADR-NNN: Title

Status: Proposed | Accepted | Superseded by ADR-XXX
Date: YYYY-MM-DD

## Context
## Decision
## Alternatives considered
## Consequences
```
