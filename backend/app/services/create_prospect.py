"""CreateProspect — bind a workspace to a verified BusinessRecord (Doc 08 §5).

A Prospect is the identity claim "this business is one company, in
relationship to this workspace" carried with binding confidence. Created
surfaced; the lifecycle only moves forward from there.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.core.errors import NotFoundError
from app.domain.audit import AuditAction, AuditEntryRepo
from app.domain.prospect import Prospect, ProspectStatus
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.prospects import SqlProspectRepo


class CreateProspect:
    def __init__(
        self,
        prospect_repo: SqlProspectRepo,
        business_repo: SqlBusinessRecordRepo,
        audit_repo: AuditEntryRepo,
    ) -> None:
        self._prospect_repo = prospect_repo
        self._business_repo = business_repo
        self._audit_repo = audit_repo

    def execute(
        self,
        *,
        workspace_id: UUID,
        business_record_id: UUID,
        binding_confidence: float,
        request_id: str | None = None,
    ) -> Prospect:
        if self._business_repo.get(business_record_id) is None:
            raise NotFoundError("business record not found")
        prospect = self._prospect_repo.add(
            Prospect(
                id=uuid4(),
                workspace_id=workspace_id,
                business_record_id=business_record_id,
                binding_confidence=binding_confidence,
                status=ProspectStatus.SURFACED,
                surfaced_at=datetime.now(UTC),
            )
        )
        self._audit_repo.append(
            action=AuditAction.PROSPECT_CREATED,
            target_type="prospect",
            target_id=str(prospect.id),
            actor_user_id=None,  # the Editor acts through the internal console
            request_id=request_id,
        )
        return prospect
