"""Entity binding v1 (ADR-008): strong keys bind, everything else queues.

Includes the binding precision suite (Doc 10 Sprint 7 DoD ≥95%): on a
labelled sample, every automatic binding must point at the labelled truth —
the floor design makes precision structural, and this suite is the proof
that stays green as heuristics grow."""

from uuid import uuid4

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.repositories.acquisition import BindingReviewStatus, SqlEntityBindingReviewRepo
from app.repositories.business_records import SqlBusinessRecordRepo
from app.services.resolve_entity import (
    BINDING_CONFIDENCE_FLOOR,
    NAME_MATCH_CONFIDENCE,
    STRONG_KEY_CONFIDENCE,
    BindingMethod,
    ResolveEntity,
    normalise_company_name,
)


def make_service(session: Session) -> ResolveEntity:
    return ResolveEntity(SqlBusinessRecordRepo(session), SqlEntityBindingReviewRepo(session))


def test_adr008_domain_is_a_strong_key_and_binds_automatically(db: Engine) -> None:
    with Session(db) as session:
        existing = SqlBusinessRecordRepo(session).find_or_create(
            canonical_name="Brightpath Ltd",
            website_domain="brightpath.example",
            register_number=None,
        )
        decision = make_service(session).execute(
            candidate_name="BRIGHTPATH", website_domain="brightpath.example"
        )
        session.commit()
    assert decision.method is BindingMethod.DOMAIN
    assert decision.confidence == STRONG_KEY_CONFIDENCE
    assert decision.business_record is not None
    assert decision.business_record.id == existing.id


def test_adr008_register_number_is_a_strong_key(db: Engine) -> None:
    with Session(db) as session:
        decision = make_service(session).execute(
            candidate_name="Brightpath Ltd", register_number="12345678"
        )
        session.commit()
    assert decision.method is BindingMethod.REGISTER_NUMBER
    assert decision.business_record is not None
    assert decision.business_record.register_number == "12345678"


def test_adr008_a_name_alone_queues_below_the_floor_never_binds(db: Engine) -> None:
    """Same-name-different-company is the Class-A misattribution vector
    (Doc 04 §8 A2): a bare name never binds automatically."""
    with Session(db) as session:
        SqlBusinessRecordRepo(session).find_or_create(
            canonical_name="Brightpath Ltd",
            website_domain="brightpath.example",
            register_number=None,
        )
        item_id = uuid4()
        decision = make_service(session).execute(
            candidate_name="Brightpath Ltd", canonical_item_ids=[item_id]
        )
        session.commit()
    assert decision.method is BindingMethod.QUEUED_FOR_REVIEW
    assert decision.confidence < BINDING_CONFIDENCE_FLOOR
    assert decision.business_record is None
    assert decision.review is not None
    assert decision.review.status is BindingReviewStatus.PENDING
    assert decision.review.canonical_item_ids == (item_id,)


def test_adr008_the_floor_separates_strong_keys_from_heuristics() -> None:
    assert STRONG_KEY_CONFIDENCE > BINDING_CONFIDENCE_FLOOR > NAME_MATCH_CONFIDENCE


def test_legal_suffixes_never_distinguish_companies() -> None:
    assert normalise_company_name("Brightpath Ltd.") == "brightpath"
    assert normalise_company_name("BRIGHTPATH LIMITED") == "brightpath"
    assert normalise_company_name("Brightpath & Co, PLC") == "brightpath"


def test_doc10_sprint7_binding_precision_is_at_least_95_percent(db: Engine) -> None:
    """The labelled sample: every automatic binding must match its label.
    Ambiguous candidates queueing (not binding) never costs precision."""
    labelled = [
        (f"Agency {index} Ltd", f"agency-{index}.example", f"0000{index:04d}")
        for index in range(20)
    ]
    with Session(db) as session:
        business_repo = SqlBusinessRecordRepo(session)
        truth = {
            domain: business_repo.find_or_create(
                canonical_name=name, website_domain=domain, register_number=register
            ).id
            for name, domain, register in labelled
        }
        service = make_service(session)

        correct = 0
        automatic = 0
        for name, domain, register in labelled:
            by_domain = service.execute(candidate_name=name.upper(), website_domain=domain)
            by_register = service.execute(candidate_name=name, register_number=register)
            for decision in (by_domain, by_register):
                if decision.business_record is not None:
                    automatic += 1
                    if decision.business_record.id == truth[domain]:
                        correct += 1
        # Ambiguous candidates (name only) must queue, not pollute precision.
        ambiguous = service.execute(candidate_name="Agency 3 Ltd")
        session.commit()

    assert ambiguous.business_record is None
    assert automatic == 40
    assert correct / automatic >= 0.95
