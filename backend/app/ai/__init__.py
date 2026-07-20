"""The AI runtime (AP6, Doc 08 SS6): AI calls are never sprinkled through
application code. Every model interaction is a typed pipeline with declared
inputs, validated outputs (schemas + L0 checks), cost metering, and
evaluation hooks. The rest of the codebase calls pipelines the way it calls
repositories: through interfaces, ignorant of providers.

Subpackages:
  pipelines/   typed pipelines: interview, discovery, brief, rank, draft, narrate
  prompts/     versioned prompt templates, colocated with their tests
  providers/   provider interface + OpenAI Responses implementation
  validation/  L0 validators: citation binding, vocabulary, structure, entailment

May import: app.domain, app.core. May be imported by: app.services,
app.evaluation.
"""
