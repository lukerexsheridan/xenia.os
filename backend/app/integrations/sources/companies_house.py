"""Companies House adapter (Doc 09 §3 S2): the register, at attestation grade.

Explicitly public records via the open API; near-free; the highest-trust
seed in the catalogue. The adapter plans API URLs and parses recorded JSON
into canonical Filings — fetching happens outside, through the politeness
engine, so this module never touches the network (Doc 09 §5's harness
demand: adapters break in CI before they break in production).
"""

import json
from datetime import date

from app.integrations.sources.canonical import AdapterParseError, Filing

API_BASE = "https://api.company-information.service.gov.uk"
SOURCE_FAMILY = "companies_house"


def plan_urls(register_number: str) -> list[str]:
    return [
        f"{API_BASE}/company/{register_number}",
        f"{API_BASE}/company/{register_number}/filing-history",
    ]


def parse(url: str, content: bytes) -> list[Filing]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise AdapterParseError(f"Companies House response is not JSON: {exc}") from exc
    if url.endswith("/filing-history"):
        return _parse_filing_history(payload)
    return _parse_profile(payload)


def _parse_profile(payload: dict[str, object]) -> list[Filing]:
    try:
        number = str(payload["company_number"])
        name = str(payload["company_name"])
    except KeyError as exc:
        raise AdapterParseError(f"profile missing {exc}") from exc
    status = str(payload.get("company_status", "unknown"))
    created = _parse_date(payload.get("date_of_creation"))
    sic_codes = payload.get("sic_codes") or []
    description = f"Status {status}; incorporated {created.isoformat() if created else 'unknown'}"
    if isinstance(sic_codes, list) and sic_codes:
        description += "; SIC " + ", ".join(str(code) for code in sic_codes)
    return [
        Filing(
            register_number=number,
            company_name=name,
            category="company-profile",
            description=description,
            filed_at=created,
        )
    ]


def _parse_filing_history(payload: dict[str, object]) -> list[Filing]:
    items = payload.get("items")
    if not isinstance(items, list):
        raise AdapterParseError("filing history has no items list")
    filings: list[Filing] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        filings.append(
            Filing(
                register_number=str(payload.get("company_number", "")),
                company_name=str(payload.get("company_name", "")),
                category=str(raw.get("category", "unknown")),
                description=str(raw.get("description", "")),
                filed_at=_parse_date(raw.get("date")),
            )
        )
    return filings


def _parse_date(value: object) -> date | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None
