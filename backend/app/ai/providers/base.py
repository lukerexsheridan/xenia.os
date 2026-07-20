"""The provider interface (AP6): the rest of the codebase calls pipelines the
way it calls repositories — through interfaces, ignorant of providers."""

from dataclasses import dataclass
from typing import Any, Protocol


class ProviderError(Exception):
    """The provider could not complete the call (transport, refusal, quota)."""


@dataclass(frozen=True)
class ProviderUsage:
    """The raw material of the unit-cost ledger (Doc 08 §6)."""

    model: str
    input_tokens: int
    output_tokens: int


class StructuredProvider(Protocol):
    """One structured-output call: a prompt in, schema-conforming JSON out."""

    def structured(
        self, *, prompt: str, schema: dict[str, Any], schema_name: str
    ) -> tuple[dict[str, Any], ProviderUsage]: ...
