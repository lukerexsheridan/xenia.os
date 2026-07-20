"""The Ideal Client DNA — the versioned aggregate at the system's centre.

The Doc 02 §7 ten-category schema with the laws of Docs 03 §8, 04 §4-5 and
08 §5 as code:

- decay asymmetry as a *type distinction* (DecayClass): customer-stated laws
  never decay without the customer; learned statistical preferences always
  decay toward neutral without corroboration — with the log retained;
- every mutation is an append-only DnaChangeEvent (cause, before/after,
  author, reversibility) — an unexplainable DNA change violates N4 at the
  moat's own centre;
- structural changes (a new disqualifier, a customer-law rewrite) exist first
  as DnaProposals and apply only on customer endorsement — the
  human-in-the-loop zone as a state machine;
- the conflict hierarchy ranks signal classes, and the sovereignty rule
  surfaces stated-law-versus-evidence tensions instead of resolving them
  silently, in either direction;
- learned generalisations require a pattern, never a single event ("third
  occurrence — adjusting");
- disqualifiers are constitutional, not statistical: absolute precedence,
  never overridden by score — the precedence rule's signature takes no score,
  structurally.

Per Doc 10 (Epic 2), the schema ships with ten slots and *four* active
categories — the ones consuming Doc 09's alpha signal families: business
attributes ← facts, service-need evidence ← ads/technology, buying signals ←
hiring, disqualifiers ← disqualifier triggers. The other six earn activation
from concierge evidence.
"""

from collections.abc import Iterable
from dataclasses import dataclass, replace
from datetime import datetime
from enum import IntEnum, StrEnum
from uuid import UUID, uuid4

from app.domain.rules import DomainRuleViolation


class DnaCategory(StrEnum):
    """The ten-slot schema, verbatim from Doc 02 §7."""

    BUSINESS_ATTRIBUTES = "business_attributes"
    FOUNDER_LEADERSHIP = "founder_leadership"
    SERVICE_NEED_EVIDENCE = "service_need_evidence"
    MARKET_TRAJECTORY = "market_trajectory"
    BUYING_SIGNALS = "buying_signals"
    BUDGET_INDICATORS = "budget_indicators"
    NEGATIVE_SIGNALS = "negative_signals"
    RISK_INDICATORS = "risk_indicators"
    RELATIONSHIP_INDICATORS = "relationship_indicators"
    DISQUALIFIERS = "disqualifiers"


# The four signal-consuming categories active at V1 (Doc 10 Epic 2, Doc 09 §13).
ACTIVE_CATEGORIES_V1 = frozenset(
    {
        DnaCategory.BUSINESS_ATTRIBUTES,
        DnaCategory.SERVICE_NEED_EVIDENCE,
        DnaCategory.BUYING_SIGNALS,
        DnaCategory.DISQUALIFIERS,
    }
)


class DecayClass(StrEnum):
    """Doc 04 §4's asymmetry as a type distinction, not a flag (Doc 08 §5)."""

    CUSTOMER_LAW = "customer_law"  # persists until the customer says otherwise
    LEARNED_PREFERENCE = "learned_preference"  # decays without corroboration


class ElementOrigin(StrEnum):
    """Which kind of event produced an element (its provenance)."""

    INTERVIEW = "interview"
    CORRECTION = "correction"
    OUTCOME_PATTERN = "outcome_pattern"
    BEHAVIOUR_PATTERN = "behaviour_pattern"
    VERTICAL_PRIOR = "vertical_prior"


# Origins that carry the customer's explicit voice: only these can found a
# customer law (patterns and priors produce learned preferences — structural
# memory requires the customer's hand, Doc 05 §4's confirmation rule).
_CUSTOMER_VOICED_ORIGINS = frozenset({ElementOrigin.INTERVIEW, ElementOrigin.CORRECTION})

NEUTRAL_CONFIDENCE = 0.5

# [calibrates] — Doc 04 §5: "minimum-evidence thresholds before any learned
# generalisation", narrated as "third occurrence — adjusting".
MINIMUM_PATTERN_OCCURRENCES = 3

# [calibrates] — per-sweep retention of a learned preference's distance from
# neutral, and the corroboration step size. The real half-lives await decay
# data (Doc 04 §10).
DECAY_RETENTION = 0.9
REINFORCEMENT_RATE = 0.2

# [calibrates] — a newly learned preference starts modestly above neutral
# (it moved on a pattern, not a proof), and a score-factor correction
# ("this overweights size") demotes an element's weight by half its distance
# from neutral — a firm step, reversible like everything else.
LEARNED_INITIAL_CONFIDENCE = 0.6
DEMOTION_RATE = 0.5

_MATERIAL_CONFIDENCE_DELTA = 1e-9


@dataclass(frozen=True)
class DnaElement:
    id: UUID
    category: DnaCategory
    statement: str  # plain language, always customer-readable (N4)
    confidence: float
    decay_class: DecayClass
    origin: ElementOrigin
    created_at: datetime
    last_reinforced_at: datetime

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise DomainRuleViolation(
                f"element confidence must be within [0, 1], got {self.confidence}"
            )
        if (
            self.category is DnaCategory.DISQUALIFIERS
            and self.decay_class is not DecayClass.CUSTOMER_LAW
        ):
            raise DomainRuleViolation(
                "disqualifiers are constitutional, not statistical (Doc 02 §7.10): "
                "they must be customer law"
            )
        if (
            self.decay_class is DecayClass.CUSTOMER_LAW
            and self.origin not in _CUSTOMER_VOICED_ORIGINS
        ):
            raise DomainRuleViolation(
                "a customer law can only originate from the customer's own voice "
                "(interview or correction, Doc 04 §4)"
            )


class ChangeAuthor(StrEnum):
    CUSTOMER = "customer"
    XENIA = "xenia"


class ChangeCause(StrEnum):
    INTERVIEW = "interview"
    CORRECTION = "correction"
    OUTCOME_PATTERN = "outcome_pattern"
    BEHAVIOUR_PATTERN = "behaviour_pattern"
    VERTICAL_PRIOR = "vertical_prior"
    DECAY = "decay"
    ENDORSEMENT = "endorsement"
    REVERSION = "reversion"


@dataclass(frozen=True)
class DnaChangeEvent:
    """One entry in the append-only changelog: cause, before/after, author,
    reversibility (Doc 08 §5). Reverted elements stay in the log — an
    employee remembers being corrected (Doc 04 §4)."""

    id: UUID
    dna_id: UUID
    element_id: UUID | None  # None for whole-DNA moments (endorsement)
    cause: ChangeCause
    author: ChangeAuthor
    before: DnaElement | None
    after: DnaElement | None
    occurred_at: datetime

    @property
    def reversible(self) -> bool:
        return self.before is not None


class ProposalStatus(StrEnum):
    PROPOSED = "proposed"
    ENDORSED = "endorsed"
    DECLINED = "declined"


@dataclass(frozen=True)
class DnaProposal:
    """A structural change awaiting the customer's signature (Doc 03 §8).

    Only the customer endorses or declines — services enforce the identity;
    this state machine enforces the sequence (no deciding twice, no applying
    the undecided or the declined)."""

    id: UUID
    dna_id: UUID
    element: DnaElement  # the element as it would exist if endorsed
    rationale: str  # proposed with reasoning, always (N4)
    proposed_by: ChangeAuthor
    status: ProposalStatus
    proposed_at: datetime
    decided_at: datetime | None = None

    def endorse(self, *, now: datetime) -> "DnaProposal":
        self._require_undecided()
        return replace(self, status=ProposalStatus.ENDORSED, decided_at=now)

    def decline(self, *, now: datetime) -> "DnaProposal":
        self._require_undecided()
        return replace(self, status=ProposalStatus.DECLINED, decided_at=now)

    def _require_undecided(self) -> None:
        if self.status is not ProposalStatus.PROPOSED:
            raise DomainRuleViolation(
                f"proposal already {self.status.value}; a decision is not revisited in place"
            )


class SignalClass(IntEnum):
    """The conflict hierarchy, ranked (Doc 04 §4): lower value prevails."""

    EXPLICIT_DISQUALIFIER = 1
    EXPLICIT_CORRECTION = 2
    RESOLVED_OUTCOME = 3
    SUSTAINED_BEHAVIOUR = 4
    INTERVIEW_STATEMENT = 5
    VERTICAL_PRIOR = 6


_STATED_CLASSES = frozenset(
    {
        SignalClass.EXPLICIT_DISQUALIFIER,
        SignalClass.EXPLICIT_CORRECTION,
        SignalClass.INTERVIEW_STATEMENT,
    }
)
_EVIDENCE_CLASSES = frozenset({SignalClass.RESOLVED_OUTCOME, SignalClass.SUSTAINED_BEHAVIOUR})


@dataclass(frozen=True)
class ConflictResolution:
    """The hierarchy's verdict plus the sovereignty rule (Doc 04 §4).

    Every conflict between the customer's stated intent and observed evidence
    is surfaced for the customer, whichever side the hierarchy favours: when
    outcomes contradict a stated law, the law stands and the tension is
    reported; when sustained behaviour contradicts an old interview answer,
    the reconciliation is proposed ("I've noticed…"). Quietly overriding
    stated intent to chase statistics is sycophancy's mirror-image failure —
    silent resolution is banned in both directions."""

    prevailing: SignalClass
    surfaced_to_customer: bool


def resolve_conflict(a: SignalClass, b: SignalClass) -> ConflictResolution:
    prevailing = min(a, b)
    surfaced = ({a, b} & _STATED_CLASSES != set()) and ({a, b} & _EVIDENCE_CLASSES != set())
    return ConflictResolution(prevailing=prevailing, surfaced_to_customer=surfaced)


def excluded_by_disqualifier(matched_elements: Iterable[DnaElement]) -> bool:
    """Absolute suppression, never overridden by score (Doc 02 §7.10).

    The signature is the rule: no score parameter exists, so no score can
    participate in the verdict."""
    return any(element.category is DnaCategory.DISQUALIFIERS for element in matched_elements)


_PATTERN_ORIGINS = frozenset({ElementOrigin.OUTCOME_PATTERN, ElementOrigin.BEHAVIOUR_PATTERN})

_CAUSE_FOR_ORIGIN: dict[ElementOrigin, ChangeCause] = {
    ElementOrigin.INTERVIEW: ChangeCause.INTERVIEW,
    ElementOrigin.CORRECTION: ChangeCause.CORRECTION,
    ElementOrigin.OUTCOME_PATTERN: ChangeCause.OUTCOME_PATTERN,
    ElementOrigin.BEHAVIOUR_PATTERN: ChangeCause.BEHAVIOUR_PATTERN,
    ElementOrigin.VERTICAL_PRIOR: ChangeCause.VERTICAL_PRIOR,
}


@dataclass(frozen=True)
class Dna:
    """The aggregate. Immutable: every operation returns the evolved DNA with
    the change event(s) that explain it — there is no mutation path without a
    changelog entry (Doc 04 §4: the changelog is total)."""

    id: UUID
    workspace_id: UUID
    version: int
    elements: tuple[DnaElement, ...]
    endorsed: bool = False

    @classmethod
    def create(
        cls,
        *,
        workspace_id: UUID,
        elements: tuple[DnaElement, ...],
        now: datetime,
    ) -> tuple["Dna", tuple[DnaChangeEvent, ...]]:
        """The founding moment (Doc 03 C1/C2): the interview's transcription
        becomes the first DNA, every element logged from birth. Customer-voiced
        elements are authored by the customer; vertical-prior template elements
        by Xenia. The DNA starts unendorsed — endorsement is its own moment."""
        if len({element.id for element in elements}) != len(elements):
            raise DomainRuleViolation("duplicate element ids in the founding set")
        dna = cls(id=uuid4(), workspace_id=workspace_id, version=1, elements=elements)
        events = tuple(
            dna._event(
                element_id=element.id,
                cause=_CAUSE_FOR_ORIGIN[element.origin],
                author=(
                    ChangeAuthor.CUSTOMER
                    if element.origin in _CUSTOMER_VOICED_ORIGINS
                    else ChangeAuthor.XENIA
                ),
                before=None,
                after=element,
                now=now,
            )
            for element in elements
        )
        return dna, events

    def element(self, element_id: UUID) -> DnaElement:
        for candidate in self.elements:
            if candidate.id == element_id:
                return candidate
        raise DomainRuleViolation(f"no element {element_id} in this DNA")

    def endorse(self, *, now: datetime) -> tuple["Dna", DnaChangeEvent]:
        """The C2 endorsement moment: the customer converts Xenia's model into
        a shared agreement (Doc 03 §3)."""
        evolved = replace(self, version=self.version + 1, endorsed=True)
        return evolved, self._event(
            element_id=None,
            cause=ChangeCause.ENDORSEMENT,
            author=ChangeAuthor.CUSTOMER,
            before=None,
            after=None,
            now=now,
        )

    def add_learned_element(
        self, element: DnaElement, *, occurrences: int, now: datetime
    ) -> tuple["Dna", DnaChangeEvent]:
        """Xenia's autonomous evolution path: learned preferences only, and a
        pattern-born element needs a pattern, never a single event (Doc 04 §5:
        "third occurrence — adjusting"). Structural material — customer laws,
        disqualifiers — must travel the proposal road instead."""
        if element.decay_class is not DecayClass.LEARNED_PREFERENCE:
            raise DomainRuleViolation(
                "customer laws are structural: proposed and endorsed, never "
                "self-applied (Doc 03 §8)"
            )
        if element.origin in _PATTERN_ORIGINS and occurrences < MINIMUM_PATTERN_OCCURRENCES:
            raise DomainRuleViolation(
                f"a learned generalisation needs ≥{MINIMUM_PATTERN_OCCURRENCES} "
                f"occurrences, got {occurrences} — one event never becomes law (Doc 04 §5)"
            )
        self._require_new(element.id)
        evolved = replace(self, version=self.version + 1, elements=(*self.elements, element))
        return evolved, self._event(
            element_id=element.id,
            cause=_CAUSE_FOR_ORIGIN[element.origin],
            author=ChangeAuthor.XENIA,
            before=None,
            after=element,
            now=now,
        )

    def apply_endorsed_proposal(
        self, proposal: DnaProposal, *, now: datetime
    ) -> tuple["Dna", DnaChangeEvent]:
        """The structural path: applied only on endorsement — proposed, never
        imposed (Doc 03 §8; Doc 08 §5's state machine)."""
        if proposal.dna_id != self.id:
            raise DomainRuleViolation("proposal belongs to a different DNA")
        if proposal.status is not ProposalStatus.ENDORSED:
            raise DomainRuleViolation(
                "structural changes apply only on customer endorsement (Doc 03 §8); "
                f"this proposal is {proposal.status.value}"
            )
        existing = self._find(proposal.element.id)
        elements = (
            tuple(
                proposal.element if candidate.id == proposal.element.id else candidate
                for candidate in self.elements
            )
            if existing is not None
            else (*self.elements, proposal.element)
        )
        evolved = replace(self, version=self.version + 1, elements=elements)
        return evolved, self._event(
            element_id=proposal.element.id,
            cause=ChangeCause.ENDORSEMENT,
            author=ChangeAuthor.CUSTOMER,
            before=existing,
            after=proposal.element,
            now=now,
        )

    def reinforce_element(
        self, element_id: UUID, *, cause: ChangeCause, now: datetime
    ) -> tuple["Dna", DnaChangeEvent]:
        """Corroboration raises confidence, bounded, and resets the decay
        clock (Doc 09 §7's confidence evolution, applied to the DNA)."""
        before = self.element(element_id)
        raised = before.confidence + (1.0 - before.confidence) * REINFORCEMENT_RATE
        after = replace(before, confidence=min(raised, 1.0), last_reinforced_at=now)
        return self._replace_element(before, after, cause=cause, author=ChangeAuthor.XENIA, now=now)

    def decay_sweep(
        self, *, now: datetime, retention: float = DECAY_RETENTION
    ) -> tuple["Dna", tuple[DnaChangeEvent, ...]]:
        """The asymmetry law (Doc 04 §4): customer laws are untouched without
        the customer; learned preferences decay toward neutral — demoted,
        never deleted, with every step in the log."""
        events: list[DnaChangeEvent] = []
        elements: list[DnaElement] = []
        version = self.version
        for element in self.elements:
            if element.decay_class is DecayClass.CUSTOMER_LAW:
                elements.append(element)
                continue
            decayed_confidence = (
                NEUTRAL_CONFIDENCE + (element.confidence - NEUTRAL_CONFIDENCE) * retention
            )
            if abs(decayed_confidence - element.confidence) < _MATERIAL_CONFIDENCE_DELTA:
                elements.append(element)
                continue
            decayed = replace(element, confidence=decayed_confidence)
            elements.append(decayed)
            version += 1
            events.append(
                self._event(
                    element_id=element.id,
                    cause=ChangeCause.DECAY,
                    author=ChangeAuthor.XENIA,
                    before=element,
                    after=decayed,
                    now=now,
                )
            )
        evolved = replace(self, version=version, elements=tuple(elements))
        return evolved, tuple(events)

    def demote_element(self, element_id: UUID, *, now: datetime) -> tuple["Dna", DnaChangeEvent]:
        """A score-factor correction (Doc 04 §5: 'this score overweights
        size'): the element's weight steps toward neutral, immediately and
        customer-authored — the element itself stays, because the customer
        questioned its weight, not its truth."""
        before = self.element(element_id)
        lowered = NEUTRAL_CONFIDENCE + (before.confidence - NEUTRAL_CONFIDENCE) * DEMOTION_RATE
        after = replace(before, confidence=lowered)
        return self._replace_element(
            before, after, cause=ChangeCause.CORRECTION, author=ChangeAuthor.CUSTOMER, now=now
        )

    def withdraw_element(self, element_id: UUID, *, now: datetime) -> tuple["Dna", DnaChangeEvent]:
        """The correction path (Doc 06 §6): the customer says an element is
        wrong and it goes, immediately and without argument — the customer is
        sovereign over their own strategy (Doc 04 §4). Customer-authored,
        cause CORRECTION, and the withdrawn element stays in the log with its
        full before-state (an employee remembers being corrected)."""
        before = self.element(element_id)
        elements = tuple(candidate for candidate in self.elements if candidate.id != element_id)
        evolved = replace(self, version=self.version + 1, elements=elements)
        return evolved, self._event(
            element_id=element_id,
            cause=ChangeCause.CORRECTION,
            author=ChangeAuthor.CUSTOMER,
            before=before,
            after=None,
            now=now,
        )

    def revert(self, event: DnaChangeEvent, *, now: datetime) -> tuple["Dna", DnaChangeEvent]:
        """Revert restores the event's before-state via a *new* event — the
        original stays in the log forever (Doc 04 §4: reverted changes stay;
        an employee remembers being corrected)."""
        if not event.reversible or event.before is None or event.element_id is None:
            raise DomainRuleViolation("this change recorded no before-state to restore")
        current = self.element(event.element_id)
        return self._replace_element(
            current,
            event.before,
            cause=ChangeCause.REVERSION,
            author=ChangeAuthor.CUSTOMER,
            now=now,
        )

    def _replace_element(
        self,
        before: DnaElement,
        after: DnaElement,
        *,
        cause: ChangeCause,
        author: ChangeAuthor,
        now: datetime,
    ) -> tuple["Dna", DnaChangeEvent]:
        elements = tuple(
            after if candidate.id == before.id else candidate for candidate in self.elements
        )
        evolved = replace(self, version=self.version + 1, elements=elements)
        return evolved, self._event(
            element_id=before.id, cause=cause, author=author, before=before, after=after, now=now
        )

    def _event(
        self,
        *,
        element_id: UUID | None,
        cause: ChangeCause,
        author: ChangeAuthor,
        before: DnaElement | None,
        after: DnaElement | None,
        now: datetime,
    ) -> DnaChangeEvent:
        return DnaChangeEvent(
            id=uuid4(),
            dna_id=self.id,
            element_id=element_id,
            cause=cause,
            author=author,
            before=before,
            after=after,
            occurred_at=now,
        )

    def _find(self, element_id: UUID) -> DnaElement | None:
        for candidate in self.elements:
            if candidate.id == element_id:
                return candidate
        return None

    def _require_new(self, element_id: UUID) -> None:
        if self._find(element_id) is not None:
            raise DomainRuleViolation(f"element {element_id} already exists in this DNA")
