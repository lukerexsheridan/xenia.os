"""ComposeResearchBrief — machine briefs behind the wall (Doc 10, Sprint 12).

Deterministic context assembly (the frozen receipt table, the DNA in plain
language), the versioned composition pipeline, inline blocking L0, bounded
regeneration with failures fed back, and the full derivation stored with the
artefact — nothing customer-facing is stored without its derivation
(Doc 08 §6). The result is always a DRAFT: the Editor gate (100% at MVP)
remains the human act of finalisation, so a machine brief cannot reach any
delivery surface unreviewed.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.ai.pipelines.compose_brief import ComposeBrief
from app.core.errors import NotFoundError
from app.domain.dna import Dna, DnaCategory
from app.domain.evidence import build_receipt_table
from app.domain.research_brief import BriefSection, ResearchBrief
from app.repositories.dna import SqlDnaRepo
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.knowledge import SqlKnowledgeRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.research_briefs import SqlResearchBriefRepo, StoredResearchBrief

CURRENT_FORMAT_VERSION = 1


@dataclass(frozen=True)
class CompositionOutcome:
    stored: StoredResearchBrief | None  # None -> every bounded attempt failed L0
    l0_problems: tuple[str, ...]
    attempts: int


def dna_summary(dna: Dna | None) -> str:
    if dna is None or not dna.elements:
        return "(no DNA on file — write generally, declare the gap in couldnt_see)"
    lines = []
    for element in dna.elements:
        marker = "LAW" if element.category is DnaCategory.DISQUALIFIERS else element.category.value
        lines.append(f"- [{marker}] {element.statement}")
    return "\n".join(lines)


class ComposeResearchBrief:
    def __init__(
        self,
        pipeline: ComposeBrief,
        brief_repo: SqlResearchBriefRepo,
        prospect_repo: SqlProspectRepo,
        evidence_repo: SqlEvidenceRepo,
        dna_repo: SqlDnaRepo,
        knowledge_repo: SqlKnowledgeRepo,
    ) -> None:
        self._pipeline = pipeline
        self._brief_repo = brief_repo
        self._prospect_repo = prospect_repo
        self._evidence_repo = evidence_repo
        self._dna_repo = dna_repo
        self._knowledge_repo = knowledge_repo

    def execute(
        self, *, workspace_id: UUID, prospect_id: UUID, business_name: str
    ) -> CompositionOutcome:
        prospect = self._prospect_repo.get(prospect_id)
        if prospect is None:
            raise NotFoundError("prospect not found in this workspace")
        evidence = self._evidence_repo.list_for_business(prospect.business_record_id)
        receipt_table = build_receipt_table(evidence)
        number_to_evidence = {row.number: row.evidence_id for row in receipt_table}

        result = self._pipeline.execute(
            business_name=business_name,
            dna_summary=dna_summary(self._dna_repo.get()),
            receipt_table=receipt_table,
        )
        for usage in result.usages:
            self._knowledge_repo.record_ai_call(
                pipeline=result.pipeline_version,
                prompt_version=result.prompt_version,
                model=usage.model,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
            )
        if result.composed is None:
            # Repeated failure routes to the Editor queue, never a customer.
            return CompositionOutcome(
                stored=None, l0_problems=result.l0_report.problems, attempts=result.attempts
            )

        sections = tuple(
            BriefSection(
                code=section.code,
                content=section.content,
                cited_evidence_ids=tuple(
                    number_to_evidence[number]
                    for number in section.cited_receipts
                    if number in number_to_evidence
                ),
            )
            for section in result.composed.sections
        )
        brief = ResearchBrief(
            id=uuid4(),
            workspace_id=workspace_id,
            prospect_id=prospect_id,
            format_version=CURRENT_FORMAT_VERSION,
            sections=sections,
            couldnt_see=result.composed.couldnt_see,
            confidence_score=result.composed.confidence_proposal,
            created_at=datetime.now(UTC),
        )
        derivation = {
            "pipeline_version": result.pipeline_version,
            "prompt_version": result.prompt_version,
            "attempts": result.attempts,
            "receipt_table_evidence_ids": [str(row.evidence_id) for row in receipt_table],
            "l0": "passed",
            "composed_at": brief.created_at.isoformat(),
        }
        stored = self._brief_repo.add(brief, derivation=derivation)
        return CompositionOutcome(stored=stored, l0_problems=(), attempts=result.attempts)
