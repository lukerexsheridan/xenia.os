"""The pure business model: entities, value objects, domain rules (Doc 08 SS3).

This package imports NOTHING but itself and the standard library — no
SQLAlchemy, no FastAPI, no Pydantic, no OpenAI types (AP2, enforced by
import-linter). It is where the constitutional documents literally become
code, and every citable rule here has a named test in tests/domain with its
document reference in the test name (Doc 10, Sprint 4).

The ontology so far (named verbatim, never renamed without a document
amendment): Workspace, User (Epic 1); IdealClientDna (`dna.Dna`) with
DnaElement, DnaChangeEvent, DnaProposal; DelegationGrant with the
never-automatic floor; the confidence vocabulary; Prospect and the Ring-2
BusinessRecord; SuppressionEntry (the one documented tenancy-spanning class);
Decision, Correction, Outcome; the AuditEntry stream (Epic 2); Evidence with
the E1-E5 taxonomy and the deterministic receipt table, ResearchBrief with
the B1-B8 structure and its completeness floor, the rubric dimensions
(Epic 3).

Still to arrive with their epics: the evidence graph and span-grounding
(Epic 5), machine composition and the L0 battery (Epic 7), Recommendation
(Epic 8), Draft, Memory.
"""
