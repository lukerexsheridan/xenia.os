"""The loop's back half, end to end (Doc 10, Epic 8 exit criteria).

The flywheel's first automated proof lives here: a correction demonstrably
alters the next queue assembly, with its changelog entry and its named
effect. Real tokens, real Postgres, the real services behind /v1.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session

from app.domain.dna import (
    DecayClass,
    Dna,
    DnaCategory,
    DnaElement,
    ElementOrigin,
)
from app.domain.signal import Signal, SignalFamily
from app.main import create_app
from app.repositories.audit import SqlAuditEntryRepo
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.dna import SqlDnaRepo
from app.repositories.knowledge import SqlKnowledgeRepo
from app.repositories.prospects import SqlProspectRepo
from app.repositories.recommendations import SqlRecommendationRepo
from app.services.assemble_queue import AssembleQueue
from app.services.create_prospect import CreateProspect
from tests.conftest import mint_supabase_token


def client() -> TestClient:
    return TestClient(create_app())


def bearer(subject: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {mint_supabase_token(subject)}"}


def make_element(category: DnaCategory, statement: str) -> DnaElement:
    now = datetime.now(UTC)
    is_law = category is DnaCategory.DISQUALIFIERS
    return DnaElement(
        id=uuid4(),
        category=category,
        statement=statement,
        confidence=1.0 if is_law else 0.9,
        decay_class=DecayClass.CUSTOMER_LAW if is_law else DecayClass.LEARNED_PREFERENCE,
        origin=ElementOrigin.INTERVIEW if is_law else ElementOrigin.BEHAVIOUR_PATTERN,
        created_at=now,
        last_reinforced_at=now,
    )


def seed_signal(session: Session, business_record_id: UUID, family: SignalFamily) -> None:
    now = datetime.now(UTC)
    SqlKnowledgeRepo(session).upsert_signal(
        Signal(
            id=uuid4(),
            business_record_id=business_record_id,
            family=family,
            name=f"seeded_{family.value}",
            confidence=0.9,
            supporting_evidence_ids=(uuid4(),),
            newest_observation_at=now - timedelta(days=1),
            rule_version="signals/1",
            derived_at=now,
        )
    )


class World:
    """One workspace with a DNA and named businesses, seeded directly."""

    def __init__(self, db: Engine, api: TestClient) -> None:
        self.api = api
        self.headers = bearer(f"loop-{uuid4()}")
        self.workspace_id = UUID(api.get("/v1/me", headers=self.headers).json()["workspace"]["id"])
        self.db = db
        self.prospects: dict[str, UUID] = {}
        with Session(db) as session:
            self.buying = make_element(DnaCategory.BUYING_SIGNALS, "Hiring for marketing roles")
            self.law = make_element(DnaCategory.DISQUALIFIERS, "No in-house marketing teams")
            dna, events = Dna.create(
                workspace_id=self.workspace_id,
                elements=(self.buying, self.law),
                now=datetime.now(UTC),
            )
            SqlDnaRepo(session, self.workspace_id).save(dna, events)
            session.commit()

    def add_business(self, name: str, *families: SignalFamily) -> UUID:
        with Session(self.db) as session:
            record = SqlBusinessRecordRepo(session).find_or_create(
                canonical_name=name, website_domain=f"{name.lower()}.example", register_number=None
            )
            for family in families:
                seed_signal(session, record.id, family)
            prospect = CreateProspect(
                SqlProspectRepo(session, self.workspace_id),
                SqlBusinessRecordRepo(session),
                SqlAuditEntryRepo(session, self.workspace_id),
            ).execute(
                workspace_id=self.workspace_id,
                business_record_id=record.id,
                binding_confidence=0.95,
            )
            session.commit()
            self.prospects[name] = prospect.id
            return prospect.id

    def assemble(self) -> None:
        with Session(self.db) as session:
            workspace_id = self.workspace_id
            AssembleQueue(
                SqlDnaRepo(session, workspace_id),
                SqlProspectRepo(session, workspace_id),
                SqlBusinessRecordRepo(session),
                SqlKnowledgeRepo(session),
                SqlRecommendationRepo(session, workspace_id),
                SqlAuditEntryRepo(session, workspace_id),
            ).execute(workspace_id=workspace_id)
            session.commit()

    def queue(self) -> dict[str, Any]:
        response = self.api.get("/v1/queue", headers=self.headers)
        assert response.status_code == 200
        body: dict[str, Any] = response.json()
        return body

    def recommendation_for(self, name: str) -> dict[str, Any] | None:
        return next(
            (
                item
                for item in self.queue()["items"]
                if item["prospect_id"] == str(self.prospects[name])
            ),
            None,
        )


def test_doc10_sprint14_the_queue_is_ranked_explained_and_visibly_judging(db: Engine) -> None:
    api = client()
    world = World(db, api)
    world.add_business("Alpha", SignalFamily.HIRING)
    world.add_business("Quiet")  # no signals: nothing to say, simply absent
    world.add_business("Inhouse", SignalFamily.HIRING, SignalFamily.DISQUALIFIER_TRIGGERS)
    world.assemble()

    body = world.queue()
    ranked = [item for item in body["items"] if item["polarity"] == "recommended"]
    excluded = [item for item in body["items"] if item["polarity"] == "excluded"]
    assert [item["prospect_id"] for item in ranked] == [str(world.prospects["Alpha"])]
    # Decomposition: every point names its DNA element and its evidence.
    component = ranked[0]["components"][0]
    assert component["dna_statement"] == "Hiring for marketing roles"
    assert component["supporting_evidence_ids"]
    assert ranked[0]["confidence_word"] in {"confident", "likely", "possible", "uncertain"}
    # The visible exclusion, at the queue's end, with its law named.
    assert len(excluded) == 1
    assert body["items"][-1]["polarity"] == "excluded"
    assert "your disqualifier" in excluded[0]["exclusion_reason"]
    assert "No in-house marketing teams" in excluded[0]["exclusion_reason"]


def test_doc10_epic8_exit_a_correction_alters_the_next_queue_with_named_effect(
    db: Engine,
) -> None:
    """The flywheel's first automated proof."""
    api = client()
    world = World(db, api)
    world.add_business("Alpha", SignalFamily.HIRING)
    world.assemble()
    assert world.recommendation_for("Alpha") is not None

    response = api.post(
        "/v1/corrections",
        headers=world.headers,
        json={
            "target_kind": "dna_element",
            "target_id": str(world.buying.id),
            "reason": "wrong - we do not weight hiring",
        },
    )
    assert response.status_code == 200
    body = response.json()
    # The named effect, computed synchronously and said plainly (Doc 08 §4).
    assert body["effect_summary"] == "Removes one from this week's queue"
    assert body["removed_prospect_ids"] == [str(world.prospects["Alpha"])]

    # The next queue assembly is demonstrably altered.
    assert world.recommendation_for("Alpha") is None

    # And the changelog carries the cause (Doc 04 §4: the changelog is total).
    with db.connect() as connection:
        causes = (
            connection.execute(
                text("SELECT cause FROM dna_change_events WHERE workspace_id = :w"),
                {"w": str(world.workspace_id)},
            )
            .scalars()
            .all()
        )
    assert "correction" in causes


def test_doc06_s6_decline_chips_teach_at_the_pattern_threshold(db: Engine) -> None:
    api = client()
    world = World(db, api)
    for name in ("Alpha", "Beta", "Gamma"):
        world.add_business(name, SignalFamily.HIRING)
    world.assemble()

    lessons = []
    for name in ("Alpha", "Beta", "Gamma"):
        recommendation = world.recommendation_for(name)
        assert recommendation is not None
        response = api.post(
            f"/v1/recommendations/{recommendation['recommendation_id']}/decision",
            headers=world.headers,
            json={"kind": "decline", "chip": "wrong_industry"},
        )
        assert response.status_code == 200
        lessons.append(response.json()["lesson"])

    # One event never becomes law; the third occurrence adjusts, narrated.
    assert lessons[0] is None
    assert lessons[1] is None
    assert lessons[2] is not None and "adjusting" in lessons[2]
    with Session(db) as session:
        dna = SqlDnaRepo(session, world.workspace_id).get()
    assert dna is not None
    assert any("wrong industry" in element.statement for element in dna.elements)


def test_doc03_s8_the_structural_chip_proposes_never_imposes(db: Engine) -> None:
    api = client()
    world = World(db, api)
    for name in ("Alpha", "Beta", "Gamma"):
        world.add_business(name, SignalFamily.HIRING)
    world.assemble()
    for name in ("Alpha", "Beta", "Gamma"):
        recommendation = world.recommendation_for(name)
        assert recommendation is not None
        api.post(
            f"/v1/recommendations/{recommendation['recommendation_id']}/decision",
            headers=world.headers,
            json={"kind": "decline", "chip": "not_our_kind_of_client"},
        )

    proposals = api.get("/v1/dna/proposals", headers=world.headers).json()
    assert len(proposals) == 1
    assert proposals[0]["status"] == "proposed"
    with Session(db) as session:
        dna_before = SqlDnaRepo(session, world.workspace_id).get()
    assert dna_before is not None
    assert len(dna_before.elements) == 2  # nothing applied without the signature

    endorsed = api.post(
        f"/v1/dna/proposals/{proposals[0]['proposal_id']}/decision",
        headers=world.headers,
        json={"endorse": True},
    )
    assert endorsed.status_code == 200
    with Session(db) as session:
        dna_after = SqlDnaRepo(session, world.workspace_id).get()
    assert dna_after is not None
    assert any(
        element.category is DnaCategory.DISQUALIFIERS and "not our kind" in element.statement
        for element in dna_after.elements
    )


def test_doc03_s7_pursue_advances_the_prospect_and_schedules_the_outcome_prompt(
    db: Engine,
) -> None:
    api = client()
    world = World(db, api)
    world.add_business("Alpha", SignalFamily.HIRING)
    world.assemble()
    recommendation = world.recommendation_for("Alpha")
    assert recommendation is not None

    response = api.post(
        f"/v1/recommendations/{recommendation['recommendation_id']}/decision",
        headers=world.headers,
        json={"kind": "pursue"},
    )
    assert response.status_code == 200

    # Deciding twice is a conflict, not an overwrite.
    again = api.post(
        f"/v1/recommendations/{recommendation['recommendation_id']}/decision",
        headers=world.headers,
        json={"kind": "accept"},
    )
    assert again.status_code == 409

    with Session(db) as session:
        prospect = SqlProspectRepo(session, world.workspace_id).get(world.prospects["Alpha"])
        job_types = session.execute(text("SELECT job_type FROM jobs")).scalars().all()
    assert prospect is not None and prospect.status.name == "PURSUED"
    assert "outcome_prompt" in job_types


def test_doc04_s5_a_won_outcome_reinforces_the_elements_that_argued_for_it(
    db: Engine,
) -> None:
    api = client()
    world = World(db, api)
    world.add_business("Alpha", SignalFamily.HIRING)
    world.assemble()
    recommendation = world.recommendation_for("Alpha")
    assert recommendation is not None
    api.post(
        f"/v1/recommendations/{recommendation['recommendation_id']}/decision",
        headers=world.headers,
        json={"kind": "pursue"},
    )

    response = api.post(
        f"/v1/prospects/{world.prospects['Alpha']}/outcomes",
        headers=world.headers,
        json={"kind": "won", "occurred_at": datetime.now(UTC).isoformat()},
    )
    assert response.status_code == 200
    assert response.json()["reinforced_statements"] == ["Hiring for marketing roles"]

    with Session(db) as session:
        dna = SqlDnaRepo(session, world.workspace_id).get()
        prospect = SqlProspectRepo(session, world.workspace_id).get(world.prospects["Alpha"])
    assert dna is not None and prospect is not None
    assert dna.element(world.buying.id).confidence > 0.9  # the win corroborated it
    assert prospect.status.name == "RESOLVED"


def test_chips_belong_to_declines_only(db: Engine) -> None:
    api = client()
    world = World(db, api)
    world.add_business("Alpha", SignalFamily.HIRING)
    world.assemble()
    recommendation = world.recommendation_for("Alpha")
    assert recommendation is not None
    response = api.post(
        f"/v1/recommendations/{recommendation['recommendation_id']}/decision",
        headers=world.headers,
        json={"kind": "accept", "chip": "wrong_industry"},
    )
    assert response.status_code in (400, 422)
