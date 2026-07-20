"""Company website adapter (Doc 09 §3 S1): the richest single source.

Sitemap-guided key-page discovery (home, about, pricing, careers, blog —
Doc 09 §5's rules) and deterministic readability cleaning into canonical
Pages: boilerplate elements dropped, text whitespace-normalised, so the
same page always yields the same content key (cache determinism —
"AI here would poison cache determinism", Doc 09 §4).

Headless rendering is deliberately absent: the rendering budget hook waits
for measured need (Doc 09 §13 prices it as a real unknown), and JS-walled
content is declared in couldn't-see rather than chased.
"""

import re
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree

from bs4 import BeautifulSoup

from app.integrations.sources.canonical import Page

SOURCE_FAMILY = "website"

KEY_PAGE_PATHS = ("/", "/about", "/pricing", "/careers", "/blog")
_KEY_PATTERNS = re.compile(r"/(about|pricing|careers|jobs|blog|contact|services)(/|$)", re.I)
_MAX_SITEMAP_PAGES = 10
_BOILERPLATE_TAGS = ("script", "style", "noscript", "nav", "header", "footer", "aside", "form")


def sitemap_url(domain: str) -> str:
    return f"https://{domain}/sitemap.xml"


def plan_urls(domain: str, sitemap_content: bytes | None) -> list[str]:
    """Key pages from the sitemap when one exists; the fixed rules otherwise.
    Bounded by construction — discovery can never expand unboundedly
    (Doc 09 §9: nothing explores)."""
    base = f"https://{domain}"
    if sitemap_content:
        from_sitemap = _parse_sitemap(sitemap_content, domain)
        if from_sitemap:
            urls = [base + "/", *from_sitemap]
            return list(dict.fromkeys(urls))[:_MAX_SITEMAP_PAGES]
    return [urljoin(base, path) for path in KEY_PAGE_PATHS]


def _parse_sitemap(content: bytes, domain: str) -> list[str]:
    try:
        root = ElementTree.fromstring(content)
    except ElementTree.ParseError:
        return []
    urls: list[str] = []
    for element in root.iter():
        if element.tag.endswith("loc") and element.text:
            url = element.text.strip()
            if urlsplit(url).netloc.lower().endswith(domain.lower()) and _KEY_PATTERNS.search(url):
                urls.append(url)
    return sorted(urls)[: _MAX_SITEMAP_PAGES - 1]


def parse(url: str, content: bytes) -> list[Page]:
    soup = BeautifulSoup(content, "html.parser")
    for tag in soup.find_all(_BOILERPLATE_TAGS):
        tag.decompose()
    title = soup.title.get_text(strip=True) if soup.title else ""
    text = re.sub(r"\s+", " ", " ".join(soup.stripped_strings)).strip()
    if not text:
        return []
    return [Page(url=url, title=title, text=text)]
