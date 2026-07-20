"""Fixture-driven adapter contracts (Doc 10 Sprint 7: the harness).

Recorded responses in, canonical shapes out: adapters break in CI before
they break in production. Cleaning is golden-file tested — deterministic
output is what makes the content cache honest (Doc 09 §4).
"""

import random
from datetime import date
from pathlib import Path

import pytest

from app.integrations.sources import ad_library, companies_house, hiring, websites
from app.integrations.sources.canonical import (
    AdapterParseError,
    Posting,
    dedupe_postings,
)

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sources"


def fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


# ── Companies House (S2) ─────────────────────────────────────────────────────


def test_companies_house_profile_yields_the_skeleton_facts() -> None:
    (filing,) = companies_house.parse(
        f"{companies_house.API_BASE}/company/12345678",
        fixture("companies_house_profile.json"),
    )
    assert filing.register_number == "12345678"
    assert filing.company_name == "BRIGHTPATH LTD"
    assert filing.category == "company-profile"
    assert "active" in filing.description.lower()
    assert "47910" in filing.description
    assert filing.filed_at == date(2019, 3, 1)


def test_companies_house_filing_history_yields_typed_filings() -> None:
    filings = companies_house.parse(
        f"{companies_house.API_BASE}/company/12345678/filing-history",
        fixture("companies_house_filing_history.json"),
    )
    assert [item.category for item in filings] == ["accounts", "confirmation-statement"]
    assert all(item.register_number == "12345678" for item in filings)
    assert filings[0].filed_at == date(2026, 1, 31)


def test_companies_house_dialect_change_is_an_ops_event() -> None:
    with pytest.raises(AdapterParseError):
        companies_house.parse(f"{companies_house.API_BASE}/company/1", b"<html>maintenance</html>")
    with pytest.raises(AdapterParseError):
        companies_house.parse(f"{companies_house.API_BASE}/company/1", b'{"unexpected": true}')


# ── Ad library (S3) ──────────────────────────────────────────────────────────


def test_ad_library_yields_ad_records() -> None:
    records = ad_library.parse("https://graph.example/ads", fixture("ad_library_response.json"))
    assert len(records) == 2
    running, stopped = records
    assert running.external_id == "784512930011223"
    assert running.page_name == "Brightpath"
    assert running.platforms == ("facebook", "instagram")
    assert running.started_at == date(2026, 6, 1)
    assert running.stopped_at is None  # still running at observation
    assert stopped.stopped_at == date(2026, 6, 10)


def test_ad_library_dialect_change_is_an_ops_event() -> None:
    with pytest.raises(AdapterParseError):
        ad_library.parse("https://graph.example/ads", b'{"error": {"code": 190}}')


# ── Websites (S1) ────────────────────────────────────────────────────────────


def test_website_cleaning_matches_the_golden_file() -> None:
    (page,) = websites.parse("https://brightpath.example/", fixture("website_home.html"))
    golden = (FIXTURES / "website_home_cleaned.txt").read_text().strip()
    assert page.text == golden
    assert page.title == "Brightpath — DTC skincare that works"
    # Deterministic: the same bytes always clean to the same content key.
    (again,) = websites.parse("https://brightpath.example/", fixture("website_home.html"))
    assert again.content_key == page.content_key


def test_website_boilerplate_never_survives_cleaning() -> None:
    (page,) = websites.parse("https://brightpath.example/", fixture("website_home.html"))
    for boilerplate in ("console.log", ".hero", "© 2026", "email"):
        assert boilerplate not in page.text


def test_sitemap_rules_bound_the_plan_to_key_pages() -> None:
    urls = websites.plan_urls("brightpath.example", fixture("sitemap.xml"))
    assert urls[0] == "https://brightpath.example/"
    assert "https://brightpath.example/about" in urls
    assert "https://brightpath.example/blog/glow-guide" in urls
    assert "https://brightpath.example/basket" not in urls  # not a key page
    assert not any("elsewhere.example" in url for url in urls)  # off-domain excluded
    assert len(urls) <= 10  # bounded by construction — nothing explores


def test_without_a_sitemap_the_fixed_key_pages_apply() -> None:
    urls = websites.plan_urls("brightpath.example", None)
    assert urls == [
        "https://brightpath.example/",
        "https://brightpath.example/about",
        "https://brightpath.example/pricing",
        "https://brightpath.example/careers",
        "https://brightpath.example/blog",
    ]


# ── Hiring (S4) ──────────────────────────────────────────────────────────────


def test_hiring_parses_json_ld_job_postings() -> None:
    postings = hiring.parse("https://brightpath.example/careers", fixture("careers_page.html"))
    assert [posting.title for posting in postings] == ["Marketing Manager", "Warehouse Assistant"]
    marketing = postings[0]
    assert marketing.company_name == "Brightpath Ltd"
    assert marketing.location == "Manchester"
    assert marketing.posted_at == date(2026, 7, 1)
    assert marketing.url == "https://brightpath.example/careers/marketing-manager"


def test_hiring_skips_non_posting_structured_data() -> None:
    postings = hiring.parse("https://brightpath.example/careers", fixture("careers_page.html"))
    assert all(isinstance(posting, Posting) for posting in postings)


# ── Aggregator dedup (Doc 09 §5) ─────────────────────────────────────────────


def make_posting(
    title: str = "Marketing Manager", posted: date | None = date(2026, 7, 1), url: str = "u1"
) -> Posting:
    return Posting(
        title=title, company_name="Brightpath Ltd", location=None, posted_at=posted, url=url
    )


def test_dedup_collapses_aggregator_duplicates_within_the_window() -> None:
    postings = [
        make_posting(url="careers-page"),
        make_posting(posted=date(2026, 7, 5), url="job-board-a"),
        make_posting(posted=date(2026, 7, 9), url="job-board-b"),
    ]
    deduped = dedupe_postings(postings)
    assert len(deduped) == 1
    assert deduped[0].url == "careers-page"  # the earliest sighting is kept


def test_dedup_keeps_a_genuine_repost_outside_the_window() -> None:
    postings = [
        make_posting(posted=date(2026, 1, 10), url="old"),
        make_posting(posted=date(2026, 7, 1), url="new"),
    ]
    assert len(dedupe_postings(postings)) == 2


def test_dedup_is_order_independent_and_idempotent() -> None:
    postings = [
        make_posting(url="a"),
        make_posting(posted=date(2026, 7, 3), url="b"),
        make_posting(title="Warehouse Assistant", posted=date(2026, 6, 20), url="c"),
        make_posting(posted=None, url="d"),
    ]
    rng = random.Random(42)
    baseline = dedupe_postings(list(postings))
    for _ in range(10):
        shuffled = list(postings)
        rng.shuffle(shuffled)
        assert dedupe_postings(shuffled) == baseline
    assert dedupe_postings(baseline) == baseline
