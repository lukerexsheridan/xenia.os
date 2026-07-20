"""Research orchestration (Doc 10, Sprint 11 DoD): recipes, budgets binding,
coverage correctness, replay determinism."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.domain.signal import Signal, SignalFamily
from app.repositories.acquisition import (
    SqlCanonicalContentRepo,
    SqlEntityBindingReviewRepo,
    SqlSourceHealthRepo,
)
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.knowledge import SqlKnowledgeRepo
from app.repositories.snapshots import SqlSourceSnapshotRepo
from app.services.acquire_footprint import AcquireFootprint
from app.services.capture_snapshot import CaptureSnapshot
from app.services.derive_signals import DeriveSignals
from app.services.extract_evidence import ExtractEvidence
from app.services.research_run import (
    COLD_MAX_FETCHES,
    DELTA_MAX_FETCHES,
    RecipeTrigger,
    RunResearch,
    plan_recipe,
)
from app.services.resolve_entity import ResolveEntity
from tests.services.test_acquire_footprint import MappedEngine, scripted_responses
from tests.services.test_capture_snapshot import InMemoryObjectStore

NOW = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)


def make_signal(family: SignalFamily, *, observed_at: datetime) -> Signal:
    return Signal(
        id=uuid4(),
        business_record_id=uuid4(),
        family=family,
        name=f"test_{family.value}",
        confidence=0.9,
        supporting_evidence_ids=(uuid4(),),
        newest_observation_at=observed_at,
        rule_version="signals/1",
        derived_at=observed_at,
    )


# ── The planner: rules, not an agent (Doc 09 §8) ─────────────────────────────


def test_doc09_s8_a_cold_business_gets_the_full_recipe() -> None:
    recipe = plan_recipe(existing_signals=[], now=NOW)
    assert recipe.trigger is RecipeTrigger.COLD
    assert recipe.source_families == {"companies_house", "ad_library", "website", "hiring"}
    assert recipe.max_fetches == COLD_MAX_FETCHES


def test_doc09_s8_a_warm_business_gets_a_delta_recipe_for_the_stale_only() -> None:
    """Cache-awareness is the planner's core intelligence: fresh knowledge is
    not re-crawled."""
    signals = [
        make_signal(SignalFamily.FACTS, observed_at=NOW),  # fresh
        make_signal(SignalFamily.ADS_TECHNOLOGY, observed_at=NOW - timedelta(days=120)),  # stale
        make_signal(SignalFamily.HIRING, observed_at=NOW),
        make_signal(SignalFamily.DISQUALIFIER_TRIGGERS, observed_at=NOW),
    ]
    recipe = plan_recipe(existing_signals=signals, now=NOW)
    assert recipe.trigger is RecipeTrigger.DELTA
    assert recipe.source_families == {"ad_library"}
    assert recipe.max_fetches == DELTA_MAX_FETCHES


def test_doc09_s8_absent_signal_families_are_delta_gaps() -> None:
    signals = [make_signal(SignalFamily.FACTS, observed_at=NOW)]
    recipe = plan_recipe(existing_signals=signals, now=NOW)
    assert recipe.trigger is RecipeTrigger.DELTA
    assert recipe.source_families == {"ad_library", "hiring"}


def test_doc09_s8_refresh_is_explicit_and_full() -> None:
    signals = [make_signal(SignalFamily.FACTS, observed_at=NOW)]
    recipe = plan_recipe(existing_signals=signals, now=NOW, force_refresh=True)
    assert recipe.trigger is RecipeTrigger.REFRESH
    assert len(recipe.source_families) == 4


# ── The run (DB) ─────────────────────────────────────────────────────────────


def make_run(session: Session, responses: dict[str, bytes]) -> RunResearch:
    capture = CaptureSnapshot(
        MappedEngine(responses), InMemoryObjectStore(), SqlSourceSnapshotRepo(session)
    )
    acquire = AcquireFootprint(
        capture,
        SqlBusinessRecordRepo(session),
        SqlCanonicalContentRepo(session),
        SqlSourceHealthRepo(session),
        ResolveEntity(SqlBusinessRecordRepo(session), SqlEntityBindingReviewRepo(session)),
        ad_library_access_token="",
    )
    extract = ExtractEvidence(
        SqlKnowledgeRepo(session),
        SqlEvidenceRepo(session),
        SqlBusinessRecordRepo(session),
        SqlSourceHealthRepo(session),
        None,
    )
    return RunResearch(
        acquire,
        extract,
        DeriveSignals(SqlEvidenceRepo(session), SqlKnowledgeRepo(session)),
        SqlKnowledgeRepo(session),
    )


def register_business(session: Session) -> UUID:
    return (
        SqlBusinessRecordRepo(session)
        .find_or_create(
            canonical_name="Brightpath Ltd",
            website_domain="brightpath.example",
            register_number="12345678",
        )
        .id
    )


def test_doc10_sprint11_cold_and_delta_runs_with_correct_ledgers(db: Engine) -> None:
    with Session(db) as session:
        business_id = register_business(session)
        cold = make_run(session, scripted_responses()).execute(business_id, now=NOW)
        warm = make_run(session, scripted_responses()).execute(business_id, now=NOW)
        session.commit()

    assert cold.recipe.trigger is RecipeTrigger.COLD
    assert cold.ledger["fetches"] > 0
    assert cold.ledger["evidence_stored"] > 0
    # Ads are unconfigured here, so two signal families derive (facts, hiring).
    assert cold.ledger["signals_derived"] == 2

    # Warm: fresh families are not re-crawled; only the absent ones (ads,
    # disqualifier triggers) are re-tried under the delta budget, and the
    # ledger proves the cache paid (Doc 09 §9): nothing new stored.
    assert warm.recipe.trigger is RecipeTrigger.DELTA
    assert warm.recipe.source_families == {"ad_library", "hiring"}
    assert warm.ledger["fetches"] < cold.ledger["fetches"]
    assert warm.ledger["evidence_stored"] == 0


def test_doc10_sprint11_replay_converges_on_identical_state(db: Engine) -> None:
    with Session(db) as session:
        business_id = register_business(session)
        make_run(session, scripted_responses()).execute(business_id, now=NOW)
        evidence_one = [e.id for e in SqlEvidenceRepo(session).list_for_business(business_id)]
        make_run(session, scripted_responses()).execute(business_id, force_refresh=True, now=NOW)
        evidence_two = [e.id for e in SqlEvidenceRepo(session).list_for_business(business_id)]
        session.commit()
    assert evidence_one == evidence_two  # replay determinism (Doc 09 §2)


def test_doc09_s9_the_budget_binds_and_degrades_honestly(db: Engine) -> None:
    with Session(db) as session:
        business_id = register_business(session)
        run = make_run(session, scripted_responses())
        report = run.execute(business_id, now=NOW)
        session.commit()
    # Force a tiny budget through a fresh run on a cold second business.
    with Session(db) as session:
        other = (
            SqlBusinessRecordRepo(session)
            .find_or_create(
                canonical_name="Northline Ltd",
                website_domain="brightpath.example2",
                register_number="99999999",
            )
            .id
        )
        acquire = AcquireFootprint(
            CaptureSnapshot(
                MappedEngine(scripted_responses()),
                InMemoryObjectStore(),
                SqlSourceSnapshotRepo(session),
            ),
            SqlBusinessRecordRepo(session),
            SqlCanonicalContentRepo(session),
            SqlSourceHealthRepo(session),
            ResolveEntity(SqlBusinessRecordRepo(session), SqlEntityBindingReviewRepo(session)),
        )
        capped = acquire.execute(other, max_fetches=1)
        session.commit()
    assert report.ledger["fetches"] <= COLD_MAX_FETCHES
    assert acquire.fetches_used == 1
    exhausted_notes = [
        note
        for family in capped.families
        for note in family.couldnt_see
        if "budget exhausted" in note
    ]
    assert exhausted_notes  # the cap degrades honestly, never overruns


def test_doc10_sprint11_coverage_reports_are_correct(db: Engine) -> None:
    responses = scripted_responses()
    responses.pop("https://brightpath.example/careers")  # hiring unreachable
    with Session(db) as session:
        business_id = register_business(session)
        report = make_run(session, responses).execute(business_id, now=NOW)
        session.commit()

    by_family = {entry.source_family: entry for entry in report.coverage}
    assert by_family["companies_house"].achieved
    assert by_family["website"].achieved
    assert not by_family["hiring"].achieved
    assert any("careers" in note for note in by_family["hiring"].couldnt_see)
    assert not by_family["ad_library"].achieved  # unconfigured, declared
