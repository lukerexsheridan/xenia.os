"""Research orchestration (Doc 10, Sprint 11; Doc 09 §8).

The planner is rules, not an agent: recipes are versioned, testable, and
cost-bounded by construction — a warm BusinessRecord yields a delta recipe
(re-verify the stale, fetch the gaps), never a full crawl. The run executes
acquire → extract → derive as one accountable process; every stage is
idempotent (content-addressed snapshots, content-derived Evidence IDs,
signal upserts), which is what makes a resumed or replayed run converge on
the identical state — checkpointing as a property, not a procedure.

The coverage report is computed from the plan: the recipe knows what it
tried, so declared blindness is computed, not remembered (Doc 09 §6). The
ledger prices every stage (Doc 09 §9): fetches are the cheap flat cost, AI
tokens the expensive variable one.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from app.domain.signal import Signal, SignalFamily, is_stale
from app.repositories.knowledge import SqlKnowledgeRepo
from app.services.acquire_footprint import AcquireFootprint, FamilyResult
from app.services.derive_signals import DeriveSignals
from app.services.extract_evidence import ExtractEvidence

RECIPE_VERSION = "recipes/1"

# [calibrates] — recipe fetch budgets (Doc 09 §9's governors).
COLD_MAX_FETCHES = 20
DELTA_MAX_FETCHES = 8

# Which source family re-verifies which signal family (the freshness economy:
# decay and acquisition are two halves of one system, Doc 09 §7).
SOURCE_FOR_SIGNAL_FAMILY: dict[SignalFamily, str] = {
    SignalFamily.FACTS: "companies_house",
    SignalFamily.ADS_TECHNOLOGY: "ad_library",
    SignalFamily.HIRING: "hiring",
    SignalFamily.DISQUALIFIER_TRIGGERS: "hiring",
}

EXPECTED_KINDS_BY_SOURCE: dict[str, str] = {
    "companies_house": "filing",
    "ad_library": "ad_record",
    "website": "page",
    "hiring": "posting",
}


class RecipeTrigger(StrEnum):
    COLD = "cold"
    DELTA = "delta"
    REFRESH = "refresh"


@dataclass(frozen=True)
class ResearchRecipe:
    trigger: RecipeTrigger
    source_families: frozenset[str]
    max_fetches: int
    recipe_version: str = RECIPE_VERSION


def plan_recipe(
    *, existing_signals: list[Signal], now: datetime, force_refresh: bool = False
) -> ResearchRecipe:
    """Deterministic recipe rules (Doc 09 §8): cold when nothing is known,
    delta re-verifying only stale or absent signal families when warm, and
    refresh (everything, delta budget) on explicit demand."""
    all_sources = frozenset(EXPECTED_KINDS_BY_SOURCE)
    if force_refresh:
        return ResearchRecipe(
            trigger=RecipeTrigger.REFRESH,
            source_families=all_sources,
            max_fetches=COLD_MAX_FETCHES,
        )
    if not existing_signals:
        return ResearchRecipe(
            trigger=RecipeTrigger.COLD, source_families=all_sources, max_fetches=COLD_MAX_FETCHES
        )
    present = {signal.family for signal in existing_signals}
    stale = {signal.family for signal in existing_signals if is_stale(signal, now=now)}
    absent = set(SignalFamily) - present
    to_reverify = frozenset(SOURCE_FOR_SIGNAL_FAMILY[family] for family in (stale | absent))
    return ResearchRecipe(
        trigger=RecipeTrigger.DELTA, source_families=to_reverify, max_fetches=DELTA_MAX_FETCHES
    )


@dataclass(frozen=True)
class CoverageEntry:
    source_family: str
    achieved: bool
    couldnt_see: tuple[str, ...]


@dataclass
class ResearchRunReport:
    business_record_id: UUID
    recipe: ResearchRecipe
    coverage: list[CoverageEntry] = field(default_factory=list)
    couldnt_see: list[str] = field(default_factory=list)
    signals: list[Signal] = field(default_factory=list)
    ledger: dict[str, int] = field(default_factory=dict)


class RunResearch:
    """One queued command: research this business (Doc 10, Epic 6)."""

    def __init__(
        self,
        acquire: AcquireFootprint,
        extract: ExtractEvidence,
        derive: DeriveSignals,
        knowledge_repo: SqlKnowledgeRepo,
    ) -> None:
        self._acquire = acquire
        self._extract = extract
        self._derive = derive
        self._knowledge_repo = knowledge_repo

    def execute(
        self,
        business_record_id: UUID,
        *,
        force_refresh: bool = False,
        now: datetime | None = None,
    ) -> ResearchRunReport:
        current = now or datetime.now(UTC)
        recipe = plan_recipe(
            existing_signals=self._knowledge_repo.signals_for_business(business_record_id),
            now=current,
            force_refresh=force_refresh,
        )
        report = ResearchRunReport(business_record_id=business_record_id, recipe=recipe)

        footprint = self._acquire.execute(
            business_record_id,
            families=recipe.source_families,
            max_fetches=recipe.max_fetches,
        )
        extraction = self._extract.execute(business_record_id)
        report.couldnt_see.extend(extraction.couldnt_see)
        report.signals = self._derive.execute(business_record_id, now=current)
        report.coverage = _coverage(footprint.families, self._counts(business_record_id))

        report.ledger = {
            "fetches": self._acquire.fetches_used,
            "canonical_items_stored": sum(r.items_stored for r in footprint.families),
            "evidence_stored": extraction.stored,
            "evidence_already_known": extraction.already_known,
            "candidates_dropped": extraction.dropped,
            "signals_derived": len(report.signals),
        }
        return report

    def _counts(self, business_record_id: UUID) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self._knowledge_repo.canonical_items_for_business(business_record_id):
            counts[item.item_kind] = counts.get(item.item_kind, 0) + 1
        return counts


def _coverage(
    families: tuple[FamilyResult, ...], canonical_counts: dict[str, int]
) -> list[CoverageEntry]:
    """Expected-versus-achieved per planned family: warm cache counts as
    covered (one world, one copy); a family with nothing acquired and nothing
    cached is honestly uncovered, with its reasons attached."""
    entries: list[CoverageEntry] = []
    for result in families:
        expected_kind = EXPECTED_KINDS_BY_SOURCE.get(result.family, "")
        achieved = (
            result.items_stored > 0
            or result.duplicates_collapsed > 0
            or canonical_counts.get(expected_kind, 0) > 0
        )
        entries.append(
            CoverageEntry(
                source_family=result.family,
                achieved=achieved,
                couldnt_see=tuple(result.couldnt_see),
            )
        )
    return entries
