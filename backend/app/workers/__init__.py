"""Job definitions, queue consumer, schedules (Doc 08 SS7).

Jobs are thin: a named payload + a service call + retry semantics. No business
logic in job bodies (the same rule as route handlers, for the same reason).
The queue is Postgres-backed at V1 (FOR UPDATE SKIP LOCKED, transactional
enqueue) — no broker until the measured profile demands it.

May import: app.services, app.repositories (the job queue itself),
app.integrations (adapter wiring at this composition boundary), app.core.
May be imported by: nothing.
"""
