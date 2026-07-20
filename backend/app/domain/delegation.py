"""The delegation ladder as data, and the never-automatic floor (Doc 06 §3, N3).

Rungs L0-L5 — and no L6: silent action does not exist at any trust level,
ever. Grants are per activity, made explicitly by a human (never defaulted
upward, never A/B-tested upward), and revocable instantly — revocation is a
repository deletion with no domain precondition, which is what "instantly"
means here.

The never-automatic floor is hardcoded beneath every grant: no rung, role, or
bug in an upper layer can authorise what Documents 03/06 forbid. That is why
`never_automatic_permits` ignores its grants argument entirely — the
signature is the law.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum, StrEnum
from uuid import UUID

from app.domain.rules import DomainRuleViolation


class DelegationRung(IntEnum):
    """L0-L5 (Doc 06 §3). There is no L6 — an employee who stops reporting
    hasn't been promoted, she's gone rogue."""

    OBSERVE = 0  # watches and learns; always on, never silent about existing
    SUGGEST = 1  # surfaces findings without stake
    RECOMMEND = 2  # the accountable judgment, her name on it
    DRAFT = 3  # prepares work product only a human sends
    PREPARE = 4  # stages complete actions awaiting one tap (earned later)
    ACT_AND_REPORT = 5  # executes within granted scope, reports everything


# Without a grant, every activity sits at the accountable-analysis posture:
# Doc 03 §8's autonomous zone is brain acts only — analysis and
# judgment-proposal, never action-shaped work.
UNGRANTED_RUNG = DelegationRung.RECOMMEND

# V1 ships suggest and draft as the grantable trust decision (Doc 03 §2 P4;
# Doc 06 §3: L4-L5 are visible in the product's language, marked earned-later).
V1_GRANTABLE_CEILING = DelegationRung.DRAFT


@dataclass(frozen=True)
class DelegationGrant:
    """activity x rung x granted-by x granted-at (Doc 08 §5).

    `activity` names a product activity (e.g. "outreach_drafting"); the
    vocabulary crystallises as the acting epics land. `granted_by` is the
    human who made the trust decision — promotion by consent only."""

    id: UUID
    workspace_id: UUID
    activity: str
    rung: DelegationRung
    granted_by: UUID
    granted_at: datetime

    def __post_init__(self) -> None:
        if self.rung > V1_GRANTABLE_CEILING:
            raise DomainRuleViolation(
                f"rung L{self.rung.value} is not grantable at V1 — the ladder above "
                f"draft is visible but earned later (Doc 03 §2 P4, Doc 06 §3)"
            )
        if self.rung <= UNGRANTED_RUNG:
            raise DomainRuleViolation(
                f"rung L{self.rung.value} needs no grant — it is the ungranted "
                f"default posture (Doc 03 §8)"
            )


def rung_for(activity: str, grants: Iterable[DelegationGrant]) -> DelegationRung:
    """The rung Xenia holds for an activity: the highest explicit grant, or
    the ungranted default. Grants for other activities confer nothing —
    delegation is per activity (Doc 06 §3)."""
    granted = [grant.rung for grant in grants if grant.activity == activity]
    return max([UNGRANTED_RUNG, *granted])


class NeverAutomatic(StrEnum):
    """The floor no grant can override (Doc 06 §3's bedrock list; N3)."""

    SEND_EXTERNAL_COMMUNICATION = "send_external_communication"
    OVERRIDE_DISQUALIFIER = "override_disqualifier"
    STRUCTURAL_DNA_CHANGE_WITHOUT_ENDORSEMENT = "structural_dna_change_without_endorsement"
    DELETE_CUSTOMER_DATA = "delete_customer_data"
    SPEND_MONEY = "spend_money"
    IRREVERSIBLE_ACTION_WITHOUT_A_HUMAN = "irreversible_action_without_a_human"


def never_automatic_permits(act: NeverAutomatic, grants: Iterable[DelegationGrant]) -> bool:
    """Always False. The grants argument exists so every authorisation path
    flows through this check and is seen to be ignored — at any delegation
    level, regardless of feature requests (Doc 10's hard floor)."""
    return False
