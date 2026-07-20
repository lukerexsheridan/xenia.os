"""The four-family footprint, acquired and normalised (Doc 10 Epic 4 DoD)."""

from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app.integrations.sources.politeness import (
    FetchedContent,
    FetchOutcome,
    FetchRefusal,
    RefusalReason,
)
from app.repositories.acquisition import (
    SqlCanonicalContentRepo,
    SqlEntityBindingReviewRepo,
    SqlSourceHealthRepo,
)
from app.repositories.business_records import SqlBusinessRecordRepo
from app.repositories.orm import CanonicalContentRow
from app.repositories.snapshots import SqlSourceSnapshotRepo
from app.services.acquire_footprint import AcquireFootprint
from app.services.capture_snapshot import CaptureSnapshot
from app.services.resolve_entity import ResolveEntity
from tests.services.test_capture_snapshot import InMemoryObjectStore

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sources"


@dataclass
class MappedEngine:
    """URL-keyed scripted fetches; unknown URLs are honest refusals."""

    responses: dict[str, bytes]
    fetched: list[str] = field(default_factory=list)

    def fetch(self, url: str) -> FetchOutcome:
        self.fetched.append(url)
        content = self.responses.get(url)
        if content is None:
            return FetchRefusal(url=url, reason=RefusalReason.UNREACHABLE, detail="not scripted")
        return FetchedContent(url=url, status=200, content=content, content_type="text/html")


def scripted_responses() -> dict[str, bytes]:
    return {
        "https://api.company-information.service.gov.uk/company/12345678": (
            FIXTURES / "companies_house_profile.json"
        ).read_bytes(),
        "https://api.company-information.service.gov.uk/company/12345678/filing-history": (
            FIXTURES / "companies_house_filing_history.json"
        ).read_bytes(),
        "https://brightpath.example/sitemap.xml": (FIXTURES / "sitemap.xml").read_bytes(),
        "https://brightpath.example/": (FIXTURES / "website_home.html").read_bytes(),
        "https://brightpath.example/careers": (FIXTURES / "careers_page.html").read_bytes(),
    }


def make_service(session: Session, responses: dict[str, bytes]) -> AcquireFootprint:
    capture = CaptureSnapshot(
        MappedEngine(responses), InMemoryObjectStore(), SqlSourceSnapshotRepo(session)
    )
    return AcquireFootprint(
        capture,
        SqlBusinessRecordRepo(session),
        SqlCanonicalContentRepo(session),
        SqlSourceHealthRepo(session),
        ResolveEntity(SqlBusinessRecordRepo(session), SqlEntityBindingReviewRepo(session)),
        ad_library_access_token="",  # unconfigured -> declared couldn't-see
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


def test_doc10_epic4_a_four_family_footprint_acquires_and_normalises(db: Engine) -> None:
    with Session(db) as session:
        business_id = register_business(session)
        report = make_service(session, scripted_responses()).execute(business_id)
        session.commit()

        by_family = {result.family: result for result in report.families}
        assert by_family["companies_house"].items_stored == 3  # profile + 2 filings
        assert by_family["website"].items_stored >= 1
        assert by_family["hiring"].items_stored == 2
        # Ads: unconfigured token degrades honestly, never guesses.
        assert by_family["ad_library"].items_stored == 0
        assert any("unobservable" in entry for entry in by_family["ad_library"].couldnt_see)

        # Everything stored is bound to the business and referenced to a snapshot.
        counts = SqlCanonicalContentRepo(session).count_for_business(business_id)
        assert counts["filing"] == 3
        assert counts["posting"] == 2
        rows = session.execute(select(CanonicalContentRow)).scalars().all()
        assert all(row.snapshot_id is not None for row in rows)

        # Source health emitted (Doc 09 §10).
        health = SqlSourceHealthRepo(session).counts()
        assert health["companies_house"]["fetched"] == 2
        assert "items_emitted" in health["website"]


def test_doc09_s5_a_second_acquisition_collapses_duplicates(db: Engine) -> None:
    with Session(db) as session:
        business_id = register_business(session)
        make_service(session, scripted_responses()).execute(business_id)
        report = make_service(session, scripted_responses()).execute(business_id)
        session.commit()

        by_family = {result.family: result for result in report.families}
        assert by_family["companies_house"].items_stored == 0
        assert by_family["companies_house"].duplicates_collapsed == 3
        counts = SqlCanonicalContentRepo(session).count_for_business(business_id)
        assert counts["filing"] == 3  # unchanged — one world, one copy


def test_doc09_s2_failures_degrade_into_couldnt_see_not_blockage(db: Engine) -> None:
    responses = scripted_responses()
    responses.pop("https://brightpath.example/careers")  # careers page unreachable
    with Session(db) as session:
        business_id = register_business(session)
        report = make_service(session, responses).execute(business_id)
        session.commit()

        by_family = {result.family: result for result in report.families}
        assert by_family["hiring"].items_stored == 0
        assert any("careers" in entry for entry in by_family["hiring"].couldnt_see)
        # The rest of the footprint still acquired.
        assert by_family["companies_house"].items_stored == 3
        health = SqlSourceHealthRepo(session).counts()
        assert health["hiring"]["refused"] >= 1
