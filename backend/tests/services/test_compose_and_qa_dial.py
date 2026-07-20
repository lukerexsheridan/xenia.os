"""Machine composition end-to-end + the QA-delta dial (Doc 10, Sprints 12-13)."""

from uuid import UUID

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.ai.pipelines.compose_brief import ComposeBrief
from app.domain.rubric import RubricScore
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.identity import SqlIdentityRepo
from app.repositories.knowledge import SqlKnowledgeRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.research_briefs import BriefStatus, SqlResearchBriefRepo
from app.services.compose_research_brief import ComposeResearchBrief
from app.services.create_prospect import CreateProspect
from tests.ai.test_compose_brief import ScriptedProvider, valid_payload
from tests.services.test_evidence_pipeline import make_extract, seed_canonical


def compose_for(session: Session) -> tuple[UUID, UUID]:
    """Provision workspace + prospect + evidence; return (workspace, brief)."""
    workspace, _ = SqlIdentityRepo(session).provision_workspace(
        name="QA Dial Agency", auth_subject=f"qa-{id(session)}", email=None
    )
    business_id = seed_canonical(session)
    make_extract(session, None).execute(business_id)
    prospect = CreateProspect(
        SqlProspectRepo(session, workspace.id),
        SqlBusinessRecordRepo(session),
        SqlAuditEntryRepo(session, workspace.id),
    ).execute(workspace_id=workspace.id, business_record_id=business_id, binding_confidence=0.95)

    outcome = ComposeResearchBrief(
        ComposeBrief(ScriptedProvider([valid_payload()])),
        SqlResearchBriefRepo(session, workspace.id),
        SqlProspectRepo(session, workspace.id),
        SqlEvidenceRepo(session),
        SqlDnaRepo(session, workspace.id),
        SqlKnowledgeRepo(session),
    ).execute(workspace_id=workspace.id, prospect_id=prospect.id, business_name="Brightpath Ltd")
    assert outcome.stored is not None
    return workspace.id, outcome.stored.brief.id


def test_doc10_sprint12_machine_briefs_are_drafts_with_full_derivation(db: Engine) -> None:
    with Session(db) as session:
        workspace_id, brief_id = compose_for(session)
        stored = SqlResearchBriefRepo(session, workspace_id).get(brief_id)
        session.commit()
    assert stored is not None
    assert stored.status is BriefStatus.DRAFT  # the Editor gate is the only exit
    assert stored.derivation is not None
    assert stored.derivation["pipeline_version"] == "compose_brief/1"
    assert stored.derivation["l0"] == "passed"
    assert stored.derivation["receipt_table_evidence_ids"]
    # Citations mapped from receipt numbers to real evidence ids.
    cited = stored.brief.cited_evidence_ids()
    assert cited
    assert {str(item) for item in cited} <= set(stored.derivation["receipt_table_evidence_ids"])


def test_doc10_sprint13_the_qa_delta_dial_computes_unedited_pass(db: Engine) -> None:
    from app.domain.rubric import RubricDimension

    with Session(db) as session:
        workspace_id, brief_id = compose_for(session)
        repo = SqlResearchBriefRepo(session, workspace_id)

        # Scored at the bar, no edits: an unedited pass.
        repo.record_rubric_score(
            brief_id,
            RubricScore(accuracy=4, evidence=4, insight=3, fit_reasoning=3, actionability=3),
        )
        report_before_edit = repo.quality_report()

        # A founder edit removes the "unedited" from the pass.
        repo.add_edit(brief_id, dimension=RubricDimension.INSIGHT, note="sharpened B4")
        report_after_edit = repo.quality_report()
        session.commit()

    assert report_before_edit["briefs_scored"] == 1
    assert report_before_edit["unedited_passed"] == 1
    assert report_before_edit["unedited_pass_rate"] == 1.0
    assert report_after_edit["unedited_passed"] == 0
    assert report_after_edit["ship_bar_passed"] == 1


def test_doc04_s3_an_accuracy_zero_zeroes_the_brief(db: Engine) -> None:
    with Session(db) as session:
        workspace_id, brief_id = compose_for(session)
        repo = SqlResearchBriefRepo(session, workspace_id)
        repo.record_rubric_score(
            brief_id,
            RubricScore(accuracy=0, evidence=4, insight=4, fit_reasoning=4, actionability=4),
        )
        report = repo.quality_report()
        session.commit()
    assert report["ship_bar_passed"] == 0  # 16/20 total, but fabrication zeroes it
