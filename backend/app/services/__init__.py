"""Use-cases: one file per named operation (AP3) — ComposeBrief,
ApplyCorrection, ResolveOutcome, ProposeDnaChange...

Never entity-managers (a ProspectService with forty methods is where domain
logic goes to hide). Each use-case fetches through repository protocols,
decides through domain rules, acts through AI pipelines and integrations,
records through repositories + the audit log. Transactions are drawn at the
use-case boundary.

May import: app.domain, app.repositories, app.ai, app.integrations,
app.evaluation, app.core. May be imported by: app.api, app.workers.
"""
