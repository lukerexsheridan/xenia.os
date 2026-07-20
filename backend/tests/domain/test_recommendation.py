"""The recommendation rules as named tests (Doc 10, Sprint 14)."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from app.domain.dna import (
    DecayClass,
    Dna,
    DnaCategory,
    DnaElement,
    ElementOrigin,
)
from app.domain.recommendation import (
    QUEUE_CAPACITY,
    AssembledQueue,
    Candidate,
    DisqualifierMatch,
    Recommendation,
    RecommendationPolarity,
    ScoreBreakdown,
    ScoreComponent,
    assemble_queue,
    exclusion_reason,
    find_disqualifier_matches,
    named_effect,
    rank_reason,
    score_against_dna,
    week_key_for,
)
from app.domain.rules import DomainRuleViolation
from app.domain.signal import Signal, SignalFamily

NOW = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)


def element(category: DnaCategory, statement: str, confidence: float = 0.9) -> DnaElement:
    is_law = category is DnaCategory.DISQUALIFIERS
    return DnaElement(
        id=uuid4(),
        category=category,
        statement=statement,
        confidence=confidence,
        decay_class=DecayClass.CUSTOMER_LAW if is_law else DecayClass.LEARNED_PREFERENCE,
        origin=ElementOrigin.CORRECTION if is_law else ElementOrigin.BEHAVIOUR_PATTERN,
        created_at=NOW,
        last_reinforced_at=NOW,
    )


def make_dna(*elements: DnaElement) -> Dna:
    return Dna(id=uuid4(), workspace_id=uuid4(), version=1, elements=tuple(elements))


def signal(family: SignalFamily, name: str, *, age_days: int = 0, base: float = 0.9) -> Signal:
    return Signal(
        id=uuid4(),
        business_record_id=uuid4(),
        family=family,
        name=name,
        confidence=base,
        supporting_evidence_ids=(uuid4(),),
        newest_observation_at=NOW - timedelta(days=age_days),
        rule_version="signals/1",
        derived_at=NOW,
    )


def scored(total_contribution: float, prospect_id: UUID | None = None) -> Candidate:
    component = ScoreComponent(
        dna_element_id=uuid4(),
        dna_statement="stmt",
        dna_confidence=1.0,
        signal_id=uuid4(),
        signal_name="sig",
        signal_family=SignalFamily.HIRING,
        signal_confidence=total_contribution,
        supporting_evidence_ids=(uuid4(),),
        contribution=total_contribution,
    )
    return Candidate(
        prospect_id=prospect_id or uuid4(),
        business_name="Someco",
        score=ScoreBreakdown(components=(component,)),
        disqualified_by=(),
    )


class TestDoc04S2ScoringDecomposition:
    def test_every_score_point_names_its_element_signal_and_evidence(self) -> None:
        buying = element(DnaCategory.BUYING_SIGNALS, "Hiring for marketing roles")
        hiring = signal(SignalFamily.HIRING, "hiring_marketing_role")
        breakdown = score_against_dna(make_dna(buying), (hiring,), now=NOW)
        assert len(breakdown.components) == 1
        component = breakdown.components[0]
        assert component.dna_element_id == buying.id
        assert component.dna_statement == buying.statement
        assert component.signal_name == "hiring_marketing_role"
        assert component.supporting_evidence_ids  # evidence-backed, always

    def test_elements_only_consume_their_documented_family(self) -> None:
        buying = element(DnaCategory.BUYING_SIGNALS, "Hiring for marketing roles")
        ads = signal(SignalFamily.ADS_TECHNOLOGY, "active_paid_media")
        assert score_against_dna(make_dna(buying), (ads,), now=NOW).components == ()

    def test_stale_signals_contribute_nothing(self) -> None:
        buying = element(DnaCategory.BUYING_SIGNALS, "Hiring for marketing roles")
        stale = signal(SignalFamily.HIRING, "hiring_marketing_role", age_days=400)
        assert score_against_dna(make_dna(buying), (stale,), now=NOW).components == ()

    def test_scoring_is_deterministic(self) -> None:
        dna = make_dna(
            element(DnaCategory.BUYING_SIGNALS, "a"),
            element(DnaCategory.SERVICE_NEED_EVIDENCE, "b"),
        )
        signals = (
            signal(SignalFamily.HIRING, "h"),
            signal(SignalFamily.ADS_TECHNOLOGY, "ads"),
        )
        first = score_against_dna(dna, signals, now=NOW)
        second = score_against_dna(dna, signals, now=NOW)
        assert first == second

    def test_no_components_means_zero_not_a_guess(self) -> None:
        assert ScoreBreakdown(components=()).total == 0.0


class TestDoc02S710DisqualifierImpossibility:
    """The exit criterion (Doc 10, Epic 8): violations unrepresentable."""

    def test_disqualified_candidates_never_rank_regardless_of_score(self) -> None:
        law = element(DnaCategory.DISQUALIFIERS, "No franchise businesses", 1.0)
        perfect = scored(1.0)
        disqualified = Candidate(
            prospect_id=perfect.prospect_id,
            business_name=perfect.business_name,
            score=perfect.score,  # a perfect score changes nothing
            disqualified_by=(
                DisqualifierMatch(
                    element=law,
                    signal=signal(SignalFamily.DISQUALIFIER_TRIGGERS, "franchise_model"),
                ),
            ),
        )
        queue = assemble_queue((disqualified,), week_key="2026-W30")
        assert queue.ranked == ()
        assert queue.excluded == (disqualified,)

    def test_disqualifier_elements_never_add_score(self) -> None:
        law = element(DnaCategory.DISQUALIFIERS, "No franchises", 1.0)
        trigger = signal(SignalFamily.DISQUALIFIER_TRIGGERS, "franchise_model")
        assert score_against_dna(make_dna(law), (trigger,), now=NOW).components == ()

    def test_matches_pair_law_with_trigger(self) -> None:
        law = element(DnaCategory.DISQUALIFIERS, "No in-house marketing teams", 1.0)
        trigger = signal(SignalFamily.DISQUALIFIER_TRIGGERS, "in_house_marketing_team")
        matches = find_disqualifier_matches(make_dna(law), (trigger,), now=NOW)
        assert matches == (DisqualifierMatch(element=law, signal=trigger),)

    def test_a_stale_trigger_does_not_exclude(self) -> None:
        law = element(DnaCategory.DISQUALIFIERS, "No in-house marketing teams", 1.0)
        stale = signal(SignalFamily.DISQUALIFIER_TRIGGERS, "in_house_marketing_team", age_days=400)
        assert find_disqualifier_matches(make_dna(law), (stale,), now=NOW) == ()

    def test_the_exclusion_reason_names_law_and_trigger(self) -> None:
        law = element(DnaCategory.DISQUALIFIERS, "No franchise businesses", 1.0)
        candidate = Candidate(
            prospect_id=uuid4(),
            business_name="Brightpath Ltd",
            score=ScoreBreakdown(components=()),
            disqualified_by=(
                DisqualifierMatch(
                    element=law,
                    signal=signal(SignalFamily.DISQUALIFIER_TRIGGERS, "franchise_model"),
                ),
            ),
        )
        reason = exclusion_reason(candidate)
        assert "ruled out Brightpath Ltd" in reason
        assert "franchise model" in reason
        assert "your disqualifier" in reason


class TestDoc03P3BoundedQueue:
    def test_the_queue_is_bounded_at_capacity(self) -> None:
        candidates = tuple(scored(0.5 + i / 100) for i in range(QUEUE_CAPACITY + 5))
        queue = assemble_queue(candidates, week_key="2026-W30")
        assert len(queue.ranked) == QUEUE_CAPACITY

    def test_a_thin_week_ships_thin_never_padded(self) -> None:
        # Two scoreable candidates and one with nothing to say: the queue
        # holds exactly two — nothing here can invent a third.
        empty = Candidate(
            prospect_id=uuid4(),
            business_name="Quietco",
            score=ScoreBreakdown(components=()),
            disqualified_by=(),
        )
        queue = assemble_queue((scored(0.5), scored(0.6), empty), week_key="2026-W30")
        assert len(queue.ranked) == 2

    def test_ranking_is_deterministic_by_score_then_id(self) -> None:
        a, b = scored(0.7), scored(0.7)
        first = assemble_queue((a, b), week_key="2026-W30")
        second = assemble_queue((b, a), week_key="2026-W30")
        assert [c.prospect_id for c in first.ranked] == [c.prospect_id for c in second.ranked]


class TestDoc06S7RankReasons:
    def test_a_material_gap_reads_as_stronger_fit(self) -> None:
        reason = rank_reason(scored(0.9), scored(0.5))
        assert reason == "above Someco because the fit against your DNA is stronger"

    def test_a_near_tie_with_fresher_signal_reads_as_freshness(self) -> None:
        above, below = scored(0.72), scored(0.70)
        assert "signal is fresher" in rank_reason(above, below)

    def test_a_true_tie_is_honest_about_arbitrary_order(self) -> None:
        component = scored(0.7).score.components[0]
        twin = Candidate(
            prospect_id=uuid4(),
            business_name="Someco",
            score=ScoreBreakdown(components=(component,)),
            disqualified_by=(),
        )
        assert "near-tie" in rank_reason(twin, twin)


class TestDoc08S4NamedEffect:
    def queue_of(self, *candidates: Candidate) -> AssembledQueue:
        return AssembledQueue(week_key="2026-W30", ranked=candidates, excluded=())

    def test_a_removal_is_named_in_words_not_numbers(self) -> None:
        kept, dropped = scored(0.9), scored(0.8)
        effect = named_effect(self.queue_of(kept, dropped), self.queue_of(kept))
        assert effect.summary == "Removes one from this week's queue"
        assert effect.removed_prospect_ids == (dropped.prospect_id,)

    def test_a_pure_rerank_is_named_as_rerank(self) -> None:
        a, b = scored(0.9), scored(0.8)
        effect = named_effect(self.queue_of(a, b), self.queue_of(b, a))
        assert effect.summary == "Re-ranks two in this week's queue"

    def test_no_change_still_acknowledges_the_teaching(self) -> None:
        a = scored(0.9)
        effect = named_effect(self.queue_of(a), self.queue_of(a))
        assert "No change to this week's queue" in effect.summary
        assert "next assembly" in effect.summary


class TestRecommendationShape:
    def test_a_recommendation_carries_its_rank(self) -> None:
        with pytest.raises(DomainRuleViolation, match="place in the queue"):
            Recommendation(
                id=uuid4(),
                workspace_id=uuid4(),
                prospect_id=uuid4(),
                week_key="2026-W30",
                polarity=RecommendationPolarity.RECOMMENDED,
                rank=None,
                score=ScoreBreakdown(components=()),
                rank_reason=None,
                exclusion_reason=None,
                created_at=NOW,
            )

    def test_an_exclusion_holds_no_rank_and_must_explain_itself(self) -> None:
        with pytest.raises(DomainRuleViolation, match="name its reasoning"):
            Recommendation(
                id=uuid4(),
                workspace_id=uuid4(),
                prospect_id=uuid4(),
                week_key="2026-W30",
                polarity=RecommendationPolarity.EXCLUDED,
                rank=None,
                score=ScoreBreakdown(components=()),
                rank_reason=None,
                exclusion_reason=None,
                created_at=NOW,
            )


def test_week_key_is_iso_week() -> None:
    assert week_key_for(datetime(2026, 7, 20, tzinfo=UTC)) == "2026-W30"
