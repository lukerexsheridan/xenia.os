"""Seed a design-partner world for the E2E loop walk (Doc 10, Sprint 19).

Provisions a workspace for the given auth subject and two businesses with
fresh signals: one that will rank (hiring + register facts) and one carrying
a disqualifier trigger (the visible exclusion). No DNA — the interview
founds it, which is the point of the walk.

Usage: python -m app.scripts.seed_e2e --subject e2e-partner-123
"""

import argparse
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.db import get_engine
from app.domain.signal import Signal, SignalFamily
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.identity import SqlIdentityRepo
from app.repositories.knowledge import SqlKnowledgeRepo
from app.repositories.prospects import SqlProspectRepo
from app.services.create_prospect import CreateProspect


def _signal(business_record_id: UUID, family: SignalFamily, name: str) -> Signal:
    now = datetime.now(UTC)
    return Signal(
        id=uuid4(),
        business_record_id=business_record_id,
        family=family,
        name=name,
        confidence=0.9,
        supporting_evidence_ids=(uuid4(),),
        newest_observation_at=now - timedelta(days=1),
        rule_version="signals/1",
        derived_at=now,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True)
    args = parser.parse_args()

    with Session(get_engine()) as session:
        workspace, _ = SqlIdentityRepo(session).provision_workspace(
            name="E2E Partner Agency", auth_subject=args.subject, email=None
        )
        knowledge = SqlKnowledgeRepo(session)
        businesses = SqlBusinessRecordRepo(session)
        create_prospect = CreateProspect(
            SqlProspectRepo(session, workspace.id),
            businesses,
            SqlAuditEntryRepo(session, workspace.id),
        )

        brightpath = businesses.find_or_create(
            canonical_name="Brightpath Ltd",
            website_domain="brightpath.example",
            register_number=None,
        )
        knowledge.upsert_signal(
            _signal(brightpath.id, SignalFamily.HIRING, "hiring_marketing_role")
        )
        knowledge.upsert_signal(_signal(brightpath.id, SignalFamily.FACTS, "company_active"))
        create_prospect.execute(
            workspace_id=workspace.id, business_record_id=brightpath.id, binding_confidence=0.95
        )

        franchico = businesses.find_or_create(
            canonical_name="Franchico",
            website_domain="franchico.example",
            register_number=None,
        )
        knowledge.upsert_signal(
            _signal(franchico.id, SignalFamily.DISQUALIFIER_TRIGGERS, "in_house_marketing_team")
        )
        knowledge.upsert_signal(_signal(franchico.id, SignalFamily.HIRING, "hiring_marketing_role"))
        create_prospect.execute(
            workspace_id=workspace.id, business_record_id=franchico.id, binding_confidence=0.95
        )
        session.commit()
        print(workspace.id)


if __name__ == "__main__":
    main()
