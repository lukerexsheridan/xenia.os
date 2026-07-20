"""Extraction + signals against real Postgres (Doc 10, Sprints 9-10 DoD)."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app.ai.pipelines.extract_page_evidence import ExtractPageEvidence
from app.domain.evidence import build_receipt_table
from app.domain.signal import SignalFamily
from app.repositories.acquisition import SqlCanonicalContentRepo, SqlSourceHealthRepo
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.evidence import SqlEvidenceRepo
from app.repositories.knowledge import SqlKnowledgeRepo
from app.repositories.orm import AiCallRecordRow
from app.repositories.snapshots import SqlSourceSnapshotRepo
from app.services.derive_signals import DeriveSignals
from app.services.extract_evidence import ExtractEvidence
from tests.ai.test_extract_page_evidence import FakeProvider, grounded_claim

PAGE_TEXT = (
    "Brightpath — DTC skincare that works. We sell direct-to-consumer skincare "
    "for sensitive skin. Founded in Manchester, we now serve over 40,000 customers."
)


def seed_canonical(session: Session) -> UUID:
    business = SqlBusinessRecordRepo(session).find_or_create(
        canonical_name="Brightpath Ltd",
        website_domain="brightpath.example",
        register_number="12345678",
    )
    snapshots = SqlSourceSnapshotRepo(session)
    canonical = SqlCanonicalContentRepo(session)

    def snap(url: str) -> UUID:
        return snapshots.add(
            url=url,
            content_sha256="e5" * 32,
            content_type="text/html",
            http_status=200,
            size_bytes=100,
            fetcher_version="test/1",
        ).id

    canonical.store(
        item_kind="filing",
        content_key="f" * 64,
        payload={
            "register_number": "12345678",
            "company_name": "BRIGHTPATH LTD",
            "category": "company-profile",
            "description": "Status active; incorporated 2019-03-01; SIC 47910",
            "filed_at": "2019-03-01",
        },
        source_family="companies_house",
        snapshot_id=snap("https://api.company-information.service.gov.uk/company/12345678"),
        business_record_id=business.id,
    )
    canonical.store(
        item_kind="ad_record",
        content_key="a" * 64,
        payload={
            "external_id": "784512930011223",
            "page_name": "Brightpath",
            "platforms": ["facebook", "instagram"],
            "started_at": "2026-06-01",
            "stopped_at": None,
            "creative_summary": "Glow like never before.",
        },
        source_family="ad_library",
        snapshot_id=snap("https://graph.facebook.com/v19.0/ads_archive?x"),
        business_record_id=business.id,
    )
    canonical.store(
        item_kind="posting",
        content_key="p" * 64,
        payload={
            "title": "Marketing Manager",
            "company_name": "Brightpath Ltd",
            "location": "Manchester",
            "posted_at": "2026-07-01",
            "url": "https://brightpath.example/careers/mm",
        },
        source_family="hiring",
        snapshot_id=snap("https://brightpath.example/careers"),
        business_record_id=business.id,
    )
    canonical.store(
        item_kind="page",
        content_key="w" * 64,
        payload={"url": "https://brightpath.example/", "title": "Brightpath", "text": PAGE_TEXT},
        source_family="website",
        snapshot_id=snap("https://brightpath.example/"),
        business_record_id=business.id,
    )
    return business.id


def make_extract(session: Session, pipeline: ExtractPageEvidence | None) -> ExtractEvidence:
    return ExtractEvidence(
        SqlKnowledgeRepo(session),
        SqlEvidenceRepo(session),
        SqlBusinessRecordRepo(session),
        SqlSourceHealthRepo(session),
        pipeline,
    )


def test_doc10_sprint9_receipt_tables_assemble_deterministically_twice(db: Engine) -> None:
    with Session(db) as session:
        business_id = seed_canonical(session)
        pipeline = ExtractPageEvidence(FakeProvider([grounded_claim()]))
        first = make_extract(session, pipeline).execute(business_id)
        table_one = build_receipt_table(SqlEvidenceRepo(session).list_for_business(business_id))
        second = make_extract(
            session, ExtractPageEvidence(FakeProvider([grounded_claim()]))
        ).execute(business_id)
        table_two = build_receipt_table(SqlEvidenceRepo(session).list_for_business(business_id))
        session.commit()

    assert first.stored == 4  # filing + ad + posting + grounded page claim
    assert second.stored == 0
    assert second.already_known == 4  # content-derived IDs make re-runs no-ops
    assert table_one == table_two  # the Sprint 9 DoD, verbatim


def test_doc09_s2_absent_provider_declares_page_prose_unread(db: Engine) -> None:
    with Session(db) as session:
        business_id = seed_canonical(session)
        report = make_extract(session, None).execute(business_id)
        session.commit()
    assert report.stored == 3  # deterministic families still extract
    assert any("not configured" in note for note in report.couldnt_see)


def test_doc08_s6_extraction_cost_is_metered_per_call(db: Engine) -> None:
    with Session(db) as session:
        business_id = seed_canonical(session)
        make_extract(session, ExtractPageEvidence(FakeProvider([grounded_claim()]))).execute(
            business_id
        )
        session.commit()
        records = session.execute(select(AiCallRecordRow)).scalars().all()
    assert len(records) == 1
    assert records[0].pipeline == "extract_page_evidence/1"
    assert records[0].input_tokens == 100


def test_doc10_sprint10_signals_derive_with_stored_derivations(db: Engine) -> None:
    with Session(db) as session:
        business_id = seed_canonical(session)
        make_extract(session, None).execute(business_id)
        signals = DeriveSignals(SqlEvidenceRepo(session), SqlKnowledgeRepo(session)).execute(
            business_id
        )
        session.commit()
        stored = SqlKnowledgeRepo(session).signals_for_business(business_id)

    by_name = {signal.name: signal for signal in stored}
    assert set(by_name) == {"company_active", "active_paid_media", "hiring_marketing_role"}
    assert by_name["company_active"].family is SignalFamily.FACTS
    assert all(signal.supporting_evidence_ids for signal in stored)  # derivations stored
    assert all(signal.rule_version == "signals/1" for signal in stored)
    assert len(signals) == 3


def test_doc10_sprint10_the_decay_sweep_demotes_stale_signals(db: Engine) -> None:
    with Session(db) as session:
        business_id = seed_canonical(session)
        make_extract(session, None).execute(business_id)
        derive = DeriveSignals(SqlEvidenceRepo(session), SqlKnowledgeRepo(session))
        now = datetime.now(UTC)
        fresh = {s.name: s.confidence for s in derive.execute(business_id, now=now)}
        later = {
            s.name: s.confidence for s in derive.execute(business_id, now=now + timedelta(days=90))
        }
        session.commit()
    assert later["active_paid_media"] < fresh["active_paid_media"] * 0.2  # weeks-class rot
    assert later["company_active"] > fresh["company_active"] * 0.8  # years-class endures
