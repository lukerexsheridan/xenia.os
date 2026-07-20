"""The canonical content model (Doc 09 §5) — the anti-corruption boundary.

Adapters own the mapping from each source's dialect into these small typed
shapes; the rest of the pipeline consumes only canonical shapes, so when a
source changes its HTML exactly one adapter changes. Four shapes for the
four alpha families (ADR-007); ReviewSet/Article arrive with their families.

`content_key` is the near-duplicate collapse (Doc 09 §5): a hash of the
normalised substance, so boilerplate re-fetches and syndicated copies
deduplicate at ingestion, where it is cheap.
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import date


class AdapterParseError(Exception):
    """The source's dialect changed — an ops event, not a crash (Doc 09 §10).
    Raised by any adapter whose input no longer matches its contract."""


def normalise_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _key(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(normalise_text(part) for part in parts).encode()).hexdigest()


@dataclass(frozen=True)
class Filing:
    """A typed register fact (Companies House and equivalents) — E2 at
    attestation grade when it becomes Evidence (Epic 5)."""

    register_number: str
    company_name: str
    category: str  # e.g. "company-profile", "accounts", "confirmation-statement"
    description: str
    filed_at: date | None

    @property
    def content_key(self) -> str:
        return _key("filing", self.register_number, self.category, self.description)


@dataclass(frozen=True)
class AdRecord:
    """One advertising-transparency entry — the beachhead's killer E1."""

    external_id: str
    page_name: str
    platforms: tuple[str, ...]
    started_at: date | None
    stopped_at: date | None  # None = running at observation time
    creative_summary: str

    @property
    def content_key(self) -> str:
        return _key("ad_record", self.external_id)


@dataclass(frozen=True)
class Page:
    """A cleaned web page: readable text + structure, boilerplate removed."""

    url: str
    title: str
    text: str

    @property
    def content_key(self) -> str:
        return _key("page", self.text)


@dataclass(frozen=True)
class Posting:
    """A hiring surface entry — the highest-signal E4 source (Doc 05 §6)."""

    title: str
    company_name: str
    location: str | None
    posted_at: date | None
    url: str

    @property
    def content_key(self) -> str:
        return _key("posting", self.title, self.company_name, self.url)


CanonicalItem = Filing | AdRecord | Page | Posting

_KIND_BY_TYPE: dict[type, str] = {
    Filing: "filing",
    AdRecord: "ad_record",
    Page: "page",
    Posting: "posting",
}


def item_kind(item: CanonicalItem) -> str:
    return _KIND_BY_TYPE[type(item)]


def dedupe_postings(postings: list[Posting], *, window_days: int = 14) -> list[Posting]:
    """Aggregator dedup (Doc 09 §5): the same role at the same company posted
    across boards within a window is one posting — keyed on normalised
    role + company, keeping the earliest sighting. Deterministic and
    order-independent."""
    by_key: dict[str, Posting] = {}
    for posting in sorted(postings, key=lambda p: (p.posted_at or date.max, p.url)):
        key = _key("dedup", posting.title, posting.company_name)
        held = by_key.get(key)
        if held is None:
            by_key[key] = posting
            continue
        both_dated = held.posted_at is not None and posting.posted_at is not None
        within_window = (
            both_dated
            and held.posted_at is not None
            and posting.posted_at is not None
            and abs((posting.posted_at - held.posted_at).days) <= window_days
        )
        if not both_dated or within_window:
            continue  # a duplicate sighting — the earliest is already held
        # Same role re-posted outside the window: a genuinely new posting.
        by_key[_key("dedup", posting.title, posting.company_name, str(posting.posted_at))] = posting
    return sorted(by_key.values(), key=lambda p: (p.posted_at or date.max, p.url))
