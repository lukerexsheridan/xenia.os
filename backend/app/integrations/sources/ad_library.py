"""Ad transparency library adapter (Doc 09 §3 S3): the beachhead's killer E1.

Purpose-built public transparency surfaces — the cleanest source in the
catalogue. Parses recorded ads-archive JSON into canonical AdRecords; the
identity is name-keyed (a page name, not a strong key), so binding routes
through the human floor queue (ADR-008) rather than guessing.
"""

import json
from datetime import date, datetime
from urllib.parse import quote

from app.integrations.sources.canonical import AdapterParseError, AdRecord

API_BASE = "https://graph.facebook.com/v19.0/ads_archive"
SOURCE_FAMILY = "ad_library"


def plan_urls(search_terms: str, *, access_token: str) -> list[str]:
    return [
        f"{API_BASE}?search_terms={quote(search_terms)}"
        f"&ad_reached_countries=GB&fields=id,page_name,publisher_platforms,"
        f"ad_delivery_start_time,ad_delivery_stop_time,ad_creative_bodies"
        f"&access_token={access_token}"
    ]


def parse(url: str, content: bytes) -> list[AdRecord]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise AdapterParseError(f"ad library response is not JSON: {exc}") from exc
    data = payload.get("data")
    if not isinstance(data, list):
        raise AdapterParseError("ad library response has no data list")
    records: list[AdRecord] = []
    for raw in data:
        if not isinstance(raw, dict) or "id" not in raw:
            continue
        bodies = raw.get("ad_creative_bodies") or []
        summary = str(bodies[0])[:200] if isinstance(bodies, list) and bodies else ""
        platforms = raw.get("publisher_platforms") or []
        records.append(
            AdRecord(
                external_id=str(raw["id"]),
                page_name=str(raw.get("page_name", "")),
                platforms=tuple(str(item) for item in platforms)
                if isinstance(platforms, list)
                else (),
                started_at=_parse_datetime(raw.get("ad_delivery_start_time")),
                stopped_at=_parse_datetime(raw.get("ad_delivery_stop_time")),
                creative_summary=summary,
            )
        )
    return records


def _parse_datetime(value: object) -> date | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None
