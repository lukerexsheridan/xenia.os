"""The OpenAI Responses provider — V1's provider behind the interface
(Doc 08 §2/§6). Nothing outside app/ai imports the SDK (AP6); pipeline logic
is tested against recorded fixtures, never against the network."""

import json
from typing import Any

from openai import OpenAI, OpenAIError

from app.ai.providers.base import ProviderError, ProviderUsage


class OpenAIResponsesProvider:
    def __init__(self, *, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def structured(
        self, *, prompt: str, schema: dict[str, Any], schema_name: str
    ) -> tuple[dict[str, Any], ProviderUsage]:  # pragma: no cover — network path
        try:
            response = self._client.responses.create(
                model=self._model,
                input=prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "schema": schema,
                        "strict": True,
                    }
                },
            )
        except OpenAIError as exc:
            raise ProviderError(str(exc)) from exc
        usage = ProviderUsage(
            model=self._model,
            input_tokens=getattr(response.usage, "input_tokens", 0) if response.usage else 0,
            output_tokens=getattr(response.usage, "output_tokens", 0) if response.usage else 0,
        )
        try:
            parsed: dict[str, Any] = json.loads(response.output_text)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ProviderError(f"provider returned non-JSON output: {exc}") from exc
        return parsed, usage
