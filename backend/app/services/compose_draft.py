"""ComposeDraft — assisted first contact, always a draft (Doc 03 C6).

The gate is inherited, not re-argued: a draft exists only where an approved
brief exists (`deliverable_for_prospect` is the only read), so nothing
unreviewed ever becomes outreach material. The founder's interview words are
the voice sample; the brief's frozen receipts are the entire evidence world;
usage is metered like every AI call (AP6).
"""

from dataclasses import dataclass
from uuid import UUID

from app.ai.pipelines.compose_opener import ComposeOpener
from app.core.errors import NotFoundError, XeniaError
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.drafts import SqlDraftRepo
from app.repositories.interview import SqlInterviewRepo
from app.repositories.knowledge import SqlKnowledgeRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.research_briefs import SqlResearchBriefRepo


@dataclass(frozen=True)
class DraftResult:
    body: str | None  # None -> every bounded attempt failed validation
    problems: tuple[str, ...]


class ComposeDraft:
    def __init__(
        self,
        pipeline: ComposeOpener | None,
        brief_repo: SqlResearchBriefRepo,
        prospect_repo: SqlProspectRepo,
        business_record_repo: SqlBusinessRecordRepo,
        interview_repo: SqlInterviewRepo,
        draft_repo: SqlDraftRepo,
        knowledge_repo: SqlKnowledgeRepo,
    ) -> None:
        self._pipeline = pipeline
        self._brief_repo = brief_repo
        self._prospect_repo = prospect_repo
        self._business_record_repo = business_record_repo
        self._interview_repo = interview_repo
        self._draft_repo = draft_repo
        self._knowledge_repo = knowledge_repo

    def execute(self, *, prospect_id: UUID) -> DraftResult:
        if self._pipeline is None:
            raise XeniaError("drafting is not configured in this environment")
        stored = self._brief_repo.deliverable_for_prospect(prospect_id)
        if stored is None:
            raise NotFoundError(
                "no approved brief for this prospect — drafts rest on reviewed evidence only"
            )
        prospect = self._prospect_repo.get(prospect_id)
        record = self._business_record_repo.get(prospect.business_record_id) if prospect else None
        business_name = record.canonical_name if record else "this business"
        voice_sample = self._interview_repo.get_answers().get(
            "homework", "A UK performance-marketing agency, plain-spoken."
        )
        receipts = "\n".join(f"[{row.number}] {row.claim}" for row in (stored.receipt_table or ()))
        result = self._pipeline.execute(
            business_name=business_name, voice_sample=voice_sample, receipts=receipts
        )
        for usage in result.usages:
            self._knowledge_repo.record_ai_call(
                pipeline=result.pipeline_version,
                prompt_version=result.prompt_version,
                model=usage.model,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
            )
        if result.opener is not None:
            self._draft_repo.save(prospect_id, result.opener)
        return DraftResult(body=result.opener, problems=result.problems)
