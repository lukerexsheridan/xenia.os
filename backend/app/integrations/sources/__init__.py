"""Source acquisition machinery (Doc 09 §5).

The politeness engine (Epic 3) is N2's single enforcement point: every fetch
in the system flows through it — per-domain rate limits, robots honour, an
honest User-Agent, circuit breakers that back off and never evade. The
HttpxTransport is its plumbing.

Per-source adapters (Companies House, ad transparency libraries, company
websites, hiring surfaces — Doc 09 §13's alpha cut) arrive in Epic 4 and all
sit on top of the engine, along with per-source trust scoring and the
quarantine switch.

May import: app.domain, app.core. May be imported by: app.services.
"""
