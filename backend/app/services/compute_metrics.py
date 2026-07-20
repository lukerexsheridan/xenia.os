"""The five-metric panel (Doc 10, Sprint 20): the five numbers on one page.

The Doc 03 loop metrics, computed live: acceptance rate (the KPI),
teaching rate (corrections + reasoned declines), the unedited-pass rate
(the automation-readiness dial), the capture rate (ground truth arriving),
and unit cost as honest tokens per composed brief. Cohort figures iterate
workspaces through workspace-scoped repositories — there is no cross-tenant
query, only a sum of tenant-scoped ones.
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.repositories.identity import SqlIdentityRepo
from app.repositories.knowledge import SqlKnowledgeRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.research_briefs import SqlResearchBriefRepo
from app.repositories.teaching import SqlTeachingRepo


@dataclass(frozen=True)
class FiveMetrics:
    acceptance_rate: float  # (accept + pursue) / decisions
    teaching_events: int  # corrections + chip-carrying declines
    unedited_pass_rate: float  # the QA-delta dial (Doc 03 §11)
    capture_rate: float  # pursued prospects with >=1 outcome / pursued
    tokens_per_brief: float  # unit cost, in tokens (prices vary; tokens don't)


class ComputeMetrics:
    def __init__(self, session: Session) -> None:
        self._session = session

    def cohort(self) -> FiveMetrics:
        decisions = 0
        accepted = 0
        teaching = 0
        scored = 0
        unedited = 0
        pursued = 0
        captured = 0
        for workspace_id in SqlIdentityRepo(self._session).list_workspace_ids():
            teaching_repo = SqlTeachingRepo(self._session, workspace_id)
            counts = teaching_repo.decision_counts()
            decisions += sum(counts.values())
            accepted += counts.get("accept", 0) + counts.get("pursue", 0)
            teaching += teaching_repo.correction_count()
            report = SqlResearchBriefRepo(self._session, workspace_id).quality_report()
            scored += int(report["briefs_scored"])
            unedited += int(report["unedited_passed"])
            with_outcomes = teaching_repo.prospects_with_outcomes()
            for prospect in SqlProspectRepo(self._session, workspace_id).list():
                if prospect.status.name in ("PURSUED", "RESOLVED"):
                    pursued += 1
                    if prospect.id in with_outcomes:
                        captured += 1
        usage = SqlKnowledgeRepo(self._session).ai_usage_totals()
        return FiveMetrics(
            acceptance_rate=accepted / decisions if decisions else 0.0,
            teaching_events=teaching,
            unedited_pass_rate=unedited / scored if scored else 0.0,
            capture_rate=captured / pursued if pursued else 0.0,
            tokens_per_brief=(
                usage["total_tokens"] / usage["brief_compositions"]
                if usage["brief_compositions"]
                else 0.0
            ),
        )
