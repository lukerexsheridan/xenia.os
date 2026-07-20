"""The DNA interview — conversational, resumable, homework-first (Doc 03 C1;
Doc 10 Sprint 18).

The alpha interview is a deterministic script, by design (the AI Philosophy:
prefer deterministic software; AI assists judgement, it does not gatekeep
onboarding). The conversation shape, the resumability, and the
homework-first opening are all here; the questions cover exactly the four
active DNA categories (Doc 10 Epic 2's cut), and the customer's own words
become the elements verbatim — nothing is more plain-language and
customer-readable (N4) than what the customer themselves said. Distillation
of rambling answers into crisper statements is an assistive AI candidate
for later, behind review, never a blocker.

Element confidences: disqualifiers are absolute (1.0, ICP schema law);
other interview statements start high but not absolute [calibrates] — the
founder's Tuesday-afternoon answer is strong evidence, not gospel.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from app.domain.dna import DecayClass, DnaCategory, DnaElement, ElementOrigin
from app.domain.rules import DomainRuleViolation

INTERVIEW_STATEMENT_CONFIDENCE = 0.8  # [calibrates]

# [calibrates] — a one-per-line answer mints one element per line; a bound
# keeps a paste-accident from flooding the founding DNA with hundreds of
# laws (each becomes constitutional and needs a correction to remove).
MAX_ELEMENTS_PER_ANSWER = 20


@dataclass(frozen=True)
class InterviewQuestion:
    key: str
    prompt: str  # Xenia's voice, senior-analyst register (Doc 06 §2)
    category: DnaCategory | None  # None -> context only, produces no element
    one_per_line: bool = False  # each line becomes its own element


INTERVIEW_SCRIPT: tuple[InterviewQuestion, ...] = (
    # The homework-first opening (Doc 06 §4): Xenia arrives having thought
    # about them, and asks them to correct her, not to fill a form.
    InterviewQuestion(
        key="homework",
        prompt=(
            "Before we talk about your ideal clients, tell me about your own "
            "shop in a sentence or two — what does your agency do best? "
            "I'll check my homework against your words."
        ),
        category=None,
    ),
    InterviewQuestion(
        key="business_attributes",
        prompt=(
            "Picture the clients you most enjoy serving. What kind of "
            "businesses are they — sector, size, business model?"
        ),
        category=DnaCategory.BUSINESS_ATTRIBUTES,
    ),
    InterviewQuestion(
        key="service_need_evidence",
        prompt=(
            "When a business genuinely needs what you sell, what visible "
            "signs give it away — what are they doing, or failing at, in "
            "their marketing?"
        ),
        category=DnaCategory.SERVICE_NEED_EVIDENCE,
    ),
    InterviewQuestion(
        key="buying_signals",
        prompt=(
            "Think about the moment a good-fit business actually buys. "
            "What's usually happening inside their company right then — "
            "hiring, growth, a launch?"
        ),
        category=DnaCategory.BUYING_SIGNALS,
    ),
    InterviewQuestion(
        key="disqualifiers",
        prompt=(
            "Now the hard lines. Which businesses will you never take on, "
            "no matter how good the numbers look? One per line — these "
            "become laws I will not argue with."
        ),
        category=DnaCategory.DISQUALIFIERS,
        one_per_line=True,
    ),
)


def next_question(answers: dict[str, str]) -> InterviewQuestion | None:
    """Resumability as a property: the next question is simply the first
    unanswered one — a closed tab loses nothing (Doc 06 §4)."""
    for question in INTERVIEW_SCRIPT:
        if question.key not in answers:
            return question
    return None


def question_by_key(key: str) -> InterviewQuestion | None:
    return next((question for question in INTERVIEW_SCRIPT if question.key == key), None)


def record_answer(answers: dict[str, str], *, key: str, text: str) -> dict[str, str]:
    """New answers arrive in order; answered questions may be amended freely
    while the interview is open — the log begins where meaning begins
    (Doc 13 I6): nothing is founded until the final answer, so an amendment
    is an edit, not a revision of history."""
    expected = next_question(answers)
    if expected is None:
        raise DomainRuleViolation("the interview is already complete")
    amending = key in answers
    question = question_by_key(key) if amending else expected
    if question is None or (not amending and key != expected.key):
        raise DomainRuleViolation(
            f"the conversation is at {expected.key!r}, not {key!r} — answers "
            "arrive in order so the transcript reads as one conversation"
        )
    if not text.strip():
        raise DomainRuleViolation("an empty answer teaches nothing — say it in your words")
    if question.one_per_line:
        lines = [line for line in text.splitlines() if line.strip()]
        if len(lines) > MAX_ELEMENTS_PER_ANSWER:
            raise DomainRuleViolation(
                f"that's {len(lines)} lines — keep it to the {MAX_ELEMENTS_PER_ANSWER} "
                "hard lines that truly never bend; the rest can be taught later"
            )
    return {**answers, key: text.strip()}


def elements_from_answers(answers: dict[str, str], *, now: datetime) -> tuple[DnaElement, ...]:
    """The transcription moment: the customer's words become the founding
    DNA, every element customer-voiced (origin INTERVIEW, Doc 04 §4)."""
    if next_question(answers) is not None:
        raise DomainRuleViolation("the interview is not finished — the DNA waits for all of it")
    elements: list[DnaElement] = []
    for question in INTERVIEW_SCRIPT:
        if question.category is None:
            continue
        statements = (
            [line.strip() for line in answers[question.key].splitlines() if line.strip()]
            if question.one_per_line
            else [answers[question.key]]
        )
        is_law = question.category is DnaCategory.DISQUALIFIERS
        for statement in statements:
            elements.append(
                DnaElement(
                    id=uuid4(),
                    category=question.category,
                    statement=statement,
                    confidence=1.0 if is_law else INTERVIEW_STATEMENT_CONFIDENCE,
                    decay_class=DecayClass.CUSTOMER_LAW,
                    origin=ElementOrigin.INTERVIEW,
                    created_at=now,
                    last_reinforced_at=now,
                )
            )
    return tuple(elements)
