# Xenia — Test credentials

The homepage (`/`) is public — no auth required.

## Admin dashboard (`/admin`)

Single-password gate. JWT session (24 hour expiry).

| Field    | Value                |
| -------- | -------------------- |
| Password | `xenia-admin-2026`   |

- Route: `/admin` (frontend)
- Backend endpoints:
  - `POST /api/admin/login` `{ "password": "..." }` → `{ token, expires_at }`
  - `GET  /api/admin/leads` (requires `Authorization: Bearer <token>`) → list of access requests

Env vars (already set in `/app/backend/.env`):
- `ADMIN_PASSWORD="xenia-admin-2026"`
- `JWT_SECRET="c8f2a7e1b5d94a6c8e3f1b7a5d2c9e4f8b6a3d1c7e5f2a8b4d6c9e1f3a7b5d2c"`
