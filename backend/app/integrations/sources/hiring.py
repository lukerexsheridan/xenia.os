"""Hiring surfaces adapter (Doc 09 §3 S4): the highest-value E4.

Parses JSON-LD JobPosting structured data from careers pages — the
deterministic, schema-published channel companies themselves emit — into
canonical Postings. Aggregator deduplication lives in the canonical model
(`dedupe_postings`), applied at acquisition.
"""

import json
from datetime import date
from typing import Any

from bs4 import BeautifulSoup

from app.integrations.sources.canonical import Posting

SOURCE_FAMILY = "hiring"


def careers_url(domain: str) -> str:
    return f"https://{domain}/careers"


def parse(url: str, content: bytes) -> list[Posting]:
    soup = BeautifulSoup(content, "html.parser")
    postings: list[Posting] = []
    for script in soup.find_all("script", type="application/ld+json"):
        payload = _load_json(script.get_text())
        if payload is None:
            continue
        for node in _job_posting_nodes(payload):
            posting = _to_posting(node, url)
            if posting is not None:
                postings.append(posting)
    return postings


def _load_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None  # malformed structured data is skipped, not fatal


def _job_posting_nodes(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        nodes = payload
    elif isinstance(payload, dict) and isinstance(payload.get("@graph"), list):
        nodes = payload["@graph"]
    else:
        nodes = [payload]
    return [node for node in nodes if isinstance(node, dict) and node.get("@type") == "JobPosting"]


def _to_posting(node: dict[str, Any], page_url: str) -> Posting | None:
    title = node.get("title")
    organisation = node.get("hiringOrganization")
    company = organisation.get("name") if isinstance(organisation, dict) else organisation
    if not isinstance(title, str) or not isinstance(company, str):
        return None
    location = None
    job_location = node.get("jobLocation")
    if isinstance(job_location, dict):
        address = job_location.get("address")
        if isinstance(address, dict):
            location = address.get("addressLocality")
    posted_at = None
    date_posted = node.get("datePosted")
    if isinstance(date_posted, str):
        try:
            posted_at = date.fromisoformat(date_posted[:10])
        except ValueError:
            posted_at = None
    url = node.get("url") if isinstance(node.get("url"), str) else page_url
    return Posting(
        title=title,
        company_name=company,
        location=location if isinstance(location, str) else None,
        posted_at=posted_at,
        url=str(url),
    )
