"""S3-compatible object storage adapter (ADR-004; Doc 08 §2).

Brief PDFs, source snapshots (the provenance contract's re-findability), and
export bundles live here — referenced by key from Postgres, never the
reverse. Code targets the S3 API only: MinIO locally, Cloudflare R2 in
staging/production; the boto3 dialect never leaves this package.

May import: app.core. May be imported by: app.services.
"""

from app.integrations.object_storage.client import ObjectStore, S3ObjectStore

__all__ = ["ObjectStore", "S3ObjectStore"]
