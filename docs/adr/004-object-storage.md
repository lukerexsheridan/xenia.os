# ADR-004: S3-compatible object storage, MinIO locally

Status: Accepted
Date: 2026-07-19

## Context

Doc 08 §2 requires object storage for brief PDFs, source snapshots (the provenance
contract's re-findability), and export bundles — "S3-compatible bucket; referenced by
key from Postgres, never the reverse". Doc 08 §13 (decision 7) defers the vendor
(Supabase Storage vs S3/R2) to ADR.

## Decision

Code against the S3 API only. **Local/dev/CI: MinIO** (in docker-compose).
**Staging/production: Cloudflare R2** (S3-compatible, zero egress fees — snapshots and
PDFs are read-heavy).

## Alternatives considered

- **Supabase Storage**: convenient, but couples a second concern to the auth vendor,
  against the "auth vendor is swappable by construction" posture (Doc 08 §2).
- **AWS S3**: the default; egress pricing penalises exactly our access pattern.
  Remains the fallback since the API surface is identical.

## Consequences

- No vendor SDK types outside `app/integrations`; switching R2 ↔ S3 is configuration.
- The bucket emulator keeps the one-command local stack honest (AP8).
