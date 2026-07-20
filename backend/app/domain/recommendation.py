"""Recommendation — the accountable judgment (Doc 08 §5; Doc 03 C5).

The loop's back half as pure rules (Doc 10, Epic 8):

- scoring is deterministic and *decomposed*: every point of a score names
  the DNA element and the evidence-backed signal that produced it
  (Doc 04 §2's explainability property — the reasoning survives being read
  aloud to a sceptical colleague);
- disqualifiers are absolute: exclusion happens before scoring exists, via
  `excluded_by_disqualifier`, whose signature takes no score — a violation
  is unrepresentable, not merely discouraged (Doc 02 §7.10);
- the queue is bounded and never padded: when discovery runs thin, Xenia
  delivers fewer and says so (Doc 03 P3 — the temptation to pad must be
  structurally impossible);
- the visible exclusion is a Recommendation with negative polarity — same
  object, same audit trail, different verdict (Doc 08 §5);
- rank is explained ("above Brightpath because the timing signal is
  fresher", Doc 06 §7) — the reason is computed here and shipped as data,
  never derived in a client (AP5);
- the chip taxonomy is the launch teaching vocabulary (Doc 06 §6, ratified
  per Doc 10 Sprint 15), and the named effect — what a teaching event did —
  is a deterministic diff of the queue before and after (Doc 08 §4).
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.confidence import ConfidenceBand, band_for
from app.domain.dna import Dna, DnaCategory, DnaElement, excluded_by_disqualifier
from app.domain.rules import DomainRuleViolation
from app.domain.signal import Signal, SignalFamily, decayed_confidence, is_stale

# Which signal family each active DNA category consumes (Doc 09 §13's cut,
# already stated in the DNA's own charter).
CATEGORY_CONSUMES: dict[DnaCategory, SignalFamily] = {
    DnaCategory.BUSINESS_ATTRIBUTES: SignalFamily.FACTS,
    DnaCategory.SERVICE_NEED_EVIDENCE: SignalFamily.ADS_TECHNOLOGY,
    DnaCategory.BUYING_SIGNALS: SignalFamily.HIRING,
    DnaCategory.DISQUALIFIERS: SignalFamily.DISQUALIFIER_TRIGGERS,
}

# [calibrates] — Doc 03 P3: "order of ten, not hundreds".
QUEUE_CAPACITY = 10

# Rank-reason threshold: below this score gap, adjacent items are explained
# by signal freshness rather than fit strength. [calibrates]
_MATERIAL_SCORE_GAP = 0.05


class RecommendationPolarity(StrEnum):
    RECOMMENDED = "recommended"
    EXCLUDED = "excluded"  # the engineered visible judgment (Doc 03 §5)


@dataclass(frozen=True)
class ScoreComponent:
    """One named point of judgment: this DNA element, met by this signal,
    resting on this evidence. The decomposition is the accountability."""

    dna_element_id: UUID
    dna_statement: str
    dna_confidence: float
    signal_id: UUID
    signal_name: str
    signal_family: SignalFamily
    signal_confidence: float  # decayed to the scoring moment
    supporting_evidence_ids: tuple[UUID, ...]
    contribution: float


@dataclass(frozen=True)
class ScoreBreakdown:
    components: tuple[ScoreComponent, ...]

    @property
    def total(self) -> float:
        """The mean of the component contributions — deliberately simple:
        every arithmetic step is narratable. [calibrates]"""
        if not self.components:
            return 0.0
        return sum(component.contribution for component in self.components) / len(self.components)

    @property
    def band(self) -> ConfidenceBand:
        return band_for(self.total)

    @property
    def freshest_signal(self) -> ScoreComponent | None:
        if not self.components:
            return None
        return max(self.components, key=lambda c: (c.signal_confidence, str(c.signal_id)))


@dataclass(frozen=True)
class DisqualifierMatch:
    """The pairing behind a visible exclusion: which law, which trigger."""

    element: DnaElement
    signal: Signal


def score_against_dna(dna: Dna, signals: tuple[Signal, ...], *, now: datetime) -> ScoreBreakdown:
    """Deterministic DNA x signals scoring, decomposed per element.

    Each active-category element pairs with every fresh signal of the family
    it consumes; a stale signal has demoted from scoring input to research
    prompt (Doc 09 §7) and contributes nothing. Disqualifier elements never
    score — they exclude (see `find_disqualifier_matches`); letting a law
    also add points would make it negotiable arithmetic."""
    components: list[ScoreComponent] = []
    fresh = [signal for signal in signals if not is_stale(signal, now=now)]
    for element in dna.elements:
        if element.category is DnaCategory.DISQUALIFIERS:
            continue
        family = CATEGORY_CONSUMES.get(element.category)
        if family is None:
            continue
        for signal in fresh:
            if signal.family is not family:
                continue
            signal_confidence = decayed_confidence(
                signal.confidence,
                family=signal.family,
                newest_observation_at=signal.newest_observation_at,
                now=now,
            )
            components.append(
                ScoreComponent(
                    dna_element_id=element.id,
                    dna_statement=element.statement,
                    dna_confidence=element.confidence,
                    signal_id=signal.id,
                    signal_name=signal.name,
                    signal_family=signal.family,
                    signal_confidence=signal_confidence,
                    supporting_evidence_ids=signal.supporting_evidence_ids,
                    contribution=element.confidence * signal_confidence,
                )
            )
    # Deterministic order: by element then signal, so stored decompositions
    # and their diffs are stable across runs.
    components.sort(key=lambda c: (str(c.dna_element_id), str(c.signal_id)))
    return ScoreBreakdown(components=tuple(components))


def find_disqualifier_matches(
    dna: Dna, signals: tuple[Signal, ...], *, now: datetime
) -> tuple[DisqualifierMatch, ...]:
    """Disqualifier elements x fresh disqualifier-trigger signals.

    Matching is family-level at V1 — the alpha trigger family is small and
    every trigger signal is a lawyer for every disqualifier law; per-law
    trigger taxonomies arrive with calibration data. [calibrates]"""
    laws = [element for element in dna.elements if element.category is DnaCategory.DISQUALIFIERS]
    triggers = [
        signal
        for signal in signals
        if signal.family is SignalFamily.DISQUALIFIER_TRIGGERS and not is_stale(signal, now=now)
    ]
    return tuple(
        DisqualifierMatch(element=law, signal=trigger) for law in laws for trigger in triggers
    )


@dataclass(frozen=True)
class Recommendation:
    """This Prospect, now, because — with the decomposed score, its rank in
    the bounded weekly set, and the week it belongs to (Doc 08 §5)."""

    id: UUID
    workspace_id: UUID
    prospect_id: UUID
    week_key: str  # ISO week, e.g. "2026-W30"
    polarity: RecommendationPolarity
    rank: int | None  # None for exclusions — an exclusion has no place in line
    score: ScoreBreakdown
    rank_reason: str | None  # why above the item below; None for the last item / exclusions
    exclusion_reason: str | None  # which law, which trigger; RECOMMENDED -> None
    created_at: datetime

    def __post_init__(self) -> None:
        if self.polarity is RecommendationPolarity.RECOMMENDED:
            if self.rank is None or self.rank < 1:
                raise DomainRuleViolation("a recommendation carries its place in the queue")
            if self.exclusion_reason is not None:
                raise DomainRuleViolation("a positive recommendation has no exclusion reason")
        else:
            if self.rank is not None:
                raise DomainRuleViolation("an exclusion holds no rank — it is out, not last")
            if not self.exclusion_reason:
                raise DomainRuleViolation(
                    "a visible exclusion must name its reasoning (Doc 03 §5: "
                    "'ruled out X — franchise model, your disqualifier')"
                )


@dataclass(frozen=True)
class Candidate:
    """A scored prospect awaiting queue assembly."""

    prospect_id: UUID
    business_name: str
    score: ScoreBreakdown
    disqualified_by: tuple[DisqualifierMatch, ...]


@dataclass(frozen=True)
class AssembledQueue:
    week_key: str
    ranked: tuple[Candidate, ...]  # in rank order, bounded
    excluded: tuple[Candidate, ...]

    def rank_of(self, prospect_id: UUID) -> int | None:
        for index, candidate in enumerate(self.ranked, start=1):
            if candidate.prospect_id == prospect_id:
                return index
        return None


def assemble_queue(
    candidates: tuple[Candidate, ...], *, week_key: str, capacity: int = QUEUE_CAPACITY
) -> AssembledQueue:
    """Bounded ranking with the disqualifier gate first and no padding.

    Disqualified candidates are excluded regardless of score — the gate runs
    before ranking exists, so no arithmetic can argue with a law. Candidates
    with no scoring components at all are simply absent (nothing to say is
    not a recommendation). Fewer qualifying candidates than capacity means a
    shorter queue, never a padded one (Doc 03 P3)."""
    excluded = tuple(candidate for candidate in candidates if _gated(candidate))
    scoreable = [
        candidate
        for candidate in candidates
        if not _gated(candidate) and candidate.score.components
    ]
    scoreable.sort(key=lambda c: (-c.score.total, str(c.prospect_id)))
    return AssembledQueue(week_key=week_key, ranked=tuple(scoreable[:capacity]), excluded=excluded)


def _gated(candidate: Candidate) -> bool:
    """The absolute gate, delegating to the constitutional rule whose
    signature takes no score (Doc 02 §7.10)."""
    return excluded_by_disqualifier(match.element for match in candidate.disqualified_by)


def rank_reason(above: Candidate, below: Candidate) -> str:
    """Why this item sits above the next one (Doc 06 §7) — plain words,
    computed server-side, shipped as data (AP5)."""
    if above.score.total - below.score.total >= _MATERIAL_SCORE_GAP:
        return f"above {below.business_name} because the fit against your DNA is stronger"
    above_fresh = above.score.freshest_signal
    below_fresh = below.score.freshest_signal
    if (
        above_fresh is not None
        and below_fresh is not None
        and above_fresh.signal_confidence > below_fresh.signal_confidence
    ):
        return (
            f"above {below.business_name} because the "
            f"{above_fresh.signal_family.value.replace('_', ' ')} signal is fresher"
        )
    return f"above {below.business_name} on a near-tie — the order is stable, not meaningful"


def exclusion_reason(candidate: Candidate) -> str:
    """'Ruled out X — franchise model, your disqualifier' (Doc 03 §5)."""
    match = candidate.disqualified_by[0]
    return (
        f"ruled out {candidate.business_name} — "
        f"{match.signal.name.replace('_', ' ')}, your disqualifier: "
        f"{match.element.statement}"
    )


@dataclass(frozen=True)
class NamedEffect:
    """What a teaching event did, computed synchronously and said plainly —
    'removes two from this week's queue' (Doc 08 §4). The sentence is built
    here because it encodes a rule; clients render it verbatim (AP5)."""

    summary: str
    removed_prospect_ids: tuple[UUID, ...]
    added_prospect_ids: tuple[UUID, ...]
    reranked_count: int


def named_effect(before: AssembledQueue, after: AssembledQueue) -> NamedEffect:
    before_ids = {candidate.prospect_id for candidate in before.ranked}
    after_ids = {candidate.prospect_id for candidate in after.ranked}
    removed = tuple(
        candidate.prospect_id
        for candidate in before.ranked
        if candidate.prospect_id not in after_ids
    )
    added = tuple(
        candidate.prospect_id
        for candidate in after.ranked
        if candidate.prospect_id not in before_ids
    )
    reranked = sum(
        1
        for prospect_id in before_ids & after_ids
        if before.rank_of(prospect_id) != after.rank_of(prospect_id)
    )
    parts: list[str] = []
    if removed:
        parts.append(f"removes {_count(len(removed))} from this week's queue")
    if added:
        parts.append(f"adds {_count(len(added))} to this week's queue")
    if reranked and not removed and not added:
        parts.append(f"re-ranks {_count(reranked)} in this week's queue")
    summary = (
        "; ".join(parts).capitalize()
        if parts
        else "No change to this week's queue — noted, and it will shape the next assembly"
    )
    return NamedEffect(
        summary=summary,
        removed_prospect_ids=removed,
        added_prospect_ids=added,
        reranked_count=reranked,
    )


_COUNT_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}


def _count(n: int) -> str:
    return _COUNT_WORDS.get(n, str(n))


def week_key_for(now: datetime) -> str:
    """The queue's home week, ISO-numbered: '2026-W30'."""
    year, week, _ = now.isocalendar()
    return f"{year}-W{week:02d}"
