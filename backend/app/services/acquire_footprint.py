"""AcquireFootprint — a business's four-family footprint, acquired and
normalised automatically (Doc 10, Epic 4 deliverable).

For each alpha family (ADR-007): plan URLs, fetch through the politeness
engine leaving replayable snapshots, parse with the family's adapter into
canonical shapes, deduplicate at ingestion, persist referenced to their
snapshots, and record source-health telemetry (Doc 09 §10). Failures degrade
honestly into typed couldn't-see entries — a refused or broken source never
blocks the rest of the footprint (Doc 09 §2's uniform failure handling).

Items acquired from the business's own strong keys bind at attestation
grade; name-keyed families (the ad library) route through ResolveEntity and
its human floor (ADR-008).
"""

from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any
from uuid import UUID

from app.core.errors import NotFoundError
from app.integrations.sources import (
    ad_library,
    companies_house,
    hiring,
    websites,
)
from app.integrations.sources.canonical import (
    AdapterParseError,
    CanonicalItem,
    dedupe_postings,
    item_kind,
)
from app.repositories.acquisition import (
    SqlCanonicalContentRepo,
    SqlSourceHealthRepo,
)
from app.repositories.business_records import SqlBusinessRecordRepo
from app.services.capture_snapshot import CaptureSnapshot, FetchRefusedError
from app.services.resolve_entity import ResolveEntity


def _serialise(item: CanonicalItem) -> dict[str, Any]:
    def json_safe(value: Any) -> Any:
        if isinstance(value, datetime | date):
            return value.isoformat()
        if isinstance(value, tuple):
            return list(value)
        return value

    return {key: json_safe(value) for key, value in asdict(item).items()}


@dataclass
class FamilyResult:
    family: str
    items_stored: int = 0
    duplicates_collapsed: int = 0
    queued_for_binding: int = 0
    couldnt_see: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FootprintReport:
    business_record_id: UUID
    families: tuple[FamilyResult, ...]


class AcquireFootprint:
    def __init__(
        self,
        capture: CaptureSnapshot,
        business_repo: SqlBusinessRecordRepo,
        canonical_repo: SqlCanonicalContentRepo,
        health_repo: SqlSourceHealthRepo,
        resolve_entity: ResolveEntity,
        *,
        ad_library_access_token: str = "",
    ) -> None:
        self._capture = capture
        self._business_repo = business_repo
        self._canonical_repo = canonical_repo
        self._health_repo = health_repo
        self._resolve_entity = resolve_entity
        self._ad_library_access_token = ad_library_access_token

    def execute(self, business_record_id: UUID) -> FootprintReport:
        business = self._business_repo.get(business_record_id)
        if business is None:
            raise NotFoundError("business record not found")

        results: list[FamilyResult] = []
        results.append(self._acquire_register(business_record_id, business.register_number))
        results.append(self._acquire_website(business_record_id, business.website_domain))
        results.append(self._acquire_hiring(business_record_id, business.website_domain))
        results.append(self._acquire_ads(business.canonical_name))
        return FootprintReport(business_record_id=business_record_id, families=tuple(results))

    # ── families ─────────────────────────────────────────────────────────

    def _acquire_register(
        self, business_record_id: UUID, register_number: str | None
    ) -> FamilyResult:
        result = FamilyResult(family=companies_house.SOURCE_FAMILY)
        if not register_number:
            result.couldnt_see.append("no register number on record — register facts unavailable")
            return result
        for url in companies_house.plan_urls(register_number):
            self._fetch_and_store(
                url, companies_house.parse, result, business_record_id=business_record_id
            )
        return result

    def _acquire_website(
        self, business_record_id: UUID, website_domain: str | None
    ) -> FamilyResult:
        result = FamilyResult(family=websites.SOURCE_FAMILY)
        if not website_domain:
            result.couldnt_see.append("no website domain on record — site unobservable")
            return result
        sitemap_content = self._try_fetch(websites.sitemap_url(website_domain), result)
        for url in websites.plan_urls(website_domain, sitemap_content):
            self._fetch_and_store(
                url, websites.parse, result, business_record_id=business_record_id
            )
        return result

    def _acquire_hiring(self, business_record_id: UUID, website_domain: str | None) -> FamilyResult:
        result = FamilyResult(family=hiring.SOURCE_FAMILY)
        if not website_domain:
            result.couldnt_see.append("no website domain on record — careers page unobservable")
            return result
        url = hiring.careers_url(website_domain)
        content_and_snapshot = self._fetch(url, result, family=hiring.SOURCE_FAMILY)
        if content_and_snapshot is None:
            return result
        content, snapshot_id = content_and_snapshot
        try:
            postings = dedupe_postings(hiring.parse(url, content))
        except AdapterParseError as exc:
            self._record_parse_failure(hiring.SOURCE_FAMILY, result, exc)
            return result
        self._store_items(postings, result, snapshot_id, business_record_id)
        return result

    def _acquire_ads(self, canonical_name: str) -> FamilyResult:
        result = FamilyResult(family=ad_library.SOURCE_FAMILY)
        if not self._ad_library_access_token:
            result.couldnt_see.append("ad library access not configured — ad activity unobservable")
            return result
        for url in ad_library.plan_urls(canonical_name, access_token=self._ad_library_access_token):
            content_and_snapshot = self._fetch(url, result, family=ad_library.SOURCE_FAMILY)
            if content_and_snapshot is None:
                continue
            content, snapshot_id = content_and_snapshot
            try:
                records = ad_library.parse(url, content)
            except AdapterParseError as exc:
                self._record_parse_failure(ad_library.SOURCE_FAMILY, result, exc)
                continue
            # Name-keyed identity: stored unbound, then queued for the human
            # floor (ADR-008) — never bound by name alone.
            stored_ids: list[UUID] = []
            for record in records:
                stored = self._canonical_repo.store(
                    item_kind=item_kind(record),
                    content_key=record.content_key,
                    payload=_serialise(record),
                    source_family=ad_library.SOURCE_FAMILY,
                    snapshot_id=snapshot_id,
                    business_record_id=None,
                )
                if stored is None:
                    result.duplicates_collapsed += 1
                else:
                    stored_ids.append(stored)
                    result.items_stored += 1
            if stored_ids:
                self._resolve_entity.execute(
                    candidate_name=records[0].page_name or canonical_name,
                    canonical_item_ids=stored_ids,
                )
                result.queued_for_binding += len(stored_ids)
        return result

    # ── shared plumbing ──────────────────────────────────────────────────

    def _fetch_and_store(
        self,
        url: str,
        parse: Callable[[str, bytes], Sequence[CanonicalItem]],
        result: FamilyResult,
        *,
        business_record_id: UUID,
    ) -> None:
        content_and_snapshot = self._fetch(url, result, family=result.family)
        if content_and_snapshot is None:
            return
        content, snapshot_id = content_and_snapshot
        try:
            items = parse(url, content)
        except AdapterParseError as exc:
            self._record_parse_failure(result.family, result, exc)
            return
        self._store_items(items, result, snapshot_id, business_record_id)

    def _store_items(
        self,
        items: Sequence[CanonicalItem],
        result: FamilyResult,
        snapshot_id: UUID,
        business_record_id: UUID,
    ) -> None:
        for item in items:
            stored = self._canonical_repo.store(
                item_kind=item_kind(item),
                content_key=item.content_key,
                payload=_serialise(item),
                source_family=result.family,
                snapshot_id=snapshot_id,
                business_record_id=business_record_id,
            )
            if stored is None:
                result.duplicates_collapsed += 1
            else:
                result.items_stored += 1
        self._health_repo.record(
            source_family=result.family, event="items_emitted", detail=str(len(items))
        )

    def _fetch(self, url: str, result: FamilyResult, *, family: str) -> tuple[bytes, UUID] | None:
        try:
            snapshot = self._capture.execute(url)
        except FetchRefusedError as refusal:
            self._health_repo.record(source_family=family, event="refused", detail=refusal.message)
            result.couldnt_see.append(f"{url}: {refusal.message}")
            return None
        self._health_repo.record(source_family=family, event="fetched", detail=url)
        content = self._capture.content_for(snapshot)
        return content, snapshot.id

    def _try_fetch(self, url: str, result: FamilyResult) -> bytes | None:
        fetched = self._fetch(url, result, family=result.family)
        return fetched[0] if fetched else None

    def _record_parse_failure(
        self, family: str, result: FamilyResult, exc: AdapterParseError
    ) -> None:
        self._health_repo.record(source_family=family, event="parse_failed", detail=str(exc))
        result.couldnt_see.append(f"{family}: source dialect changed — {exc}")
