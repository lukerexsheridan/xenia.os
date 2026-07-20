# Runbook — Deploy rollback

*A bad deploy reached staging or production.*

1. **App first:** Railway keeps previous deployments — redeploy the last
   good image for api and worker together (one image, two entrypoints: never
   roll one without the other). Vercel: promote the previous frontend build.
2. **Migrations:** expand -> migrate -> contract discipline means the last
   good app version runs against the newer schema — additive changes don't
   break the previous release, so rolling back the app alone is usually
   enough. Only run `alembic downgrade` when the migration itself is the
   fault, and only after confirming the downgrade path was CI-tested (every
   revision is reversible by policy).
3. **Jobs:** the queue is resilient by design — claimed jobs released by a
   killed worker resume; check the dead-letter count after the roll.
4. **Tell the truth:** if customers saw the breakage, the Sev1 honesty rule
   applies in spirit — say so first.
5. Post-incident note with the offending commit, in
   `docs/runbooks/incidents/`.
