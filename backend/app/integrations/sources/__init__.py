"""Source adapters — the machinery of Doc 09.

One adapter per catalogue source (Doc 05 SS6) implementing a common protocol
(fetch -> observe -> propose Evidence with provenance), the shared politeness
engine (per-domain rate limits, robots honour, circuit breakers, honest
user-agent — N2's single enforcement point), the content-addressed snapshot
store, per-source trust scoring, and the quarantine switch.

V1 alpha families (Doc 09 SS13's cut): Companies House, ad transparency
libraries, company websites, hiring surfaces. Built from Epic 3/4
(Sprints 5-8). Empty by design in the skeleton.
"""
