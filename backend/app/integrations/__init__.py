"""Outward-facing anti-corruption adapters (Doc 08 SS3): each external system
speaks its own dialect inside its folder and the app's language at the
boundary.

  stripe/         billing (Checkout, portal, idempotent webhooks)
  resend/         the ambient email surface (C8)
  supabase_auth/  JWT verification via JWKS — identity only
  sources/        one adapter per data source (Doc 05 SS6 catalogue), the
                  politeness engine, per-source trust scoring, quarantine.
                  Designed in Doc 09; built from Epic 3/4.

May import: app.domain, app.core. May be imported by: app.services.
"""
