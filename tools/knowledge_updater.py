# -*- coding: utf-8 -*-
"""
knowledge_updater.py -- self-improving crawl pipeline for Skill #160
(Smart Travel Planner -- cost/experience optimization; cluster: lifestyle-personal).

Pipeline
--------
1. Discover candidate documents from configured sources using the best available
   fetcher (crawl4ai when installed, otherwise the Python standard library).
2. Parse each candidate into a normalized ``Entry`` (title, authors, year,
   venue, url, doi, abstract).
3. Score relevance from domain keywords plus publication recency.
4. Deduplicate against the existing knowledge brain by URL/DOI hash.
5. Append surviving entries to ``SECOND-KNOWLEDGE-BRAIN.md`` inside a
   date-stamped section, leaving the hand-curated content above intact.

Usage
-----
    python tools/knowledge_updater.py                 # live crawl + append
    python tools/knowledge_updater.py --dry-run        # preview, no writes
    python tools/knowledge_updater.py --no-network    # offline smoke test
    python tools/knowledge_updater.py -v              # info logging

Design
------
* Graceful degradation: missing optional dependencies or unreachable networks
  never crash the run -- they are logged and the existing brain keeps working.
* All writes are atomic (temp file + ``os.replace``) so a crash cannot corrupt
  the brain. The dry-run path touches nothing on disk.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import html
import logging
import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Dict, Iterable, List, Optional, Sequence

LOG = logging.getLogger("knowledge_updater")

DEFAULT_BRAIN = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "SECOND-KNOWLEDGE-BRAIN.md"
)

DEFAULT_WEB_SOURCES = [
    "https://www.lonelyplanet.com",
    "https://skift.com",
    "https://www.unwto.org",
    "https://www.tripadvisor.com",
]

DEFAULT_SEARCH_QUERIES = [
    "travel itinerary optimization research",
    "budget travel trends 2026",
    "destination safety advisory",
    "experience design tourism",
]

# Tourism has no dedicated arXiv track; kept configurable for future use.
DEFAULT_ARXIV_CATEGORIES: List[str] = []

HASH_RE = re.compile(r"<!--hash:([0-9a-f]{16})-->")


@dataclass
class Entry:
    """A normalized piece of domain evidence."""

    title: str
    url: str
    authors: str = "-"
    year: str = "-"
    venue: str = "-"
    abstract: str = ""
    doi: str = ""

    def hash(self) -> str:
        key = self.doi or self.url
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]

    def hostname(self) -> str:
        try:
            return urllib.parse.urlparse(self.url).netloc or self.url
        except ValueError:
            return self.url

    def to_log_line(self, relevance: float, today: str) -> str:
        venue = self.venue or self.hostname()
        return (
            f"- {today} -- **{self.title}** "
            f"({self.authors}, {self.year}, {venue}) "
            f"[{self.url}] relevance={relevance:.2f} "
            f"<!--hash:{self.hash()}-->"
        )


@dataclass
class Config:
    """Runtime configuration for a single updater run."""

    brain: str = DEFAULT_BRAIN
    web_sources: List[str] = field(default_factory=lambda: list(DEFAULT_WEB_SOURCES))
    search_queries: List[str] = field(default_factory=lambda: list(DEFAULT_SEARCH_QUERIES))
    arxiv_categories: List[str] = field(default_factory=lambda: list(DEFAULT_ARXIV_CATEGORIES))
    limit: int = 25
    dry_run: bool = False
    network: bool = True
    timeout: float = 20.0
    user_agent: str = "smart-travel-planner-knowledge-updater/1.0 (+opensource)"

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Config":
        sources = args.sources.split(",") if args.sources else list(DEFAULT_WEB_SOURCES)
        queries = args.queries.split(",") if args.queries else list(DEFAULT_SEARCH_QUERIES)
        return cls(
            brain=args.brain,
            web_sources=[s.strip() for s in sources if s.strip()],
            search_queries=[q.strip() for q in queries if q.strip()],
            limit=args.limit,
            dry_run=args.dry_run,
            network=not args.no_network,
            timeout=args.timeout,
        )


# --- scoring ---------------------------------------------------------------

def relevance_score(
    entry: Entry,
    keywords: Sequence[str],
    today: Optional[datetime.date] = None,
) -> float:
    """Return 0..1 relevance from keyword coverage (70%) and recency (30%)."""
    today = today or datetime.date.today()
    blob = f"{entry.title} {entry.abstract}".lower()
    kws = [k.lower() for k in keywords]
    if not kws:
        return 0.0
    coverage = sum(1 for k in kws if k in blob) / len(kws)
    recency = 0.0
    match = re.search(r"(?:19|20)\d{2}", entry.year or "")
    if match:
        year = int(match.group(0))
        age = max(0, today.year - year)
        recency = max(0.0, 1.0 - age / 10.0)
    return round(0.7 * coverage + 0.3 * recency, 3)


# --- brain io --------------------------------------------------------------

def read_brain(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def existing_hashes(text: str) -> set:
    return set(HASH_RE.findall(text))


def _atomic_write(path: str, content: str) -> None:
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)
    os.replace(tmp, path)


def append_entries(entries: Iterable[Entry], config: Config) -> int:
    """Append deduplicated, scored entries to the brain. Returns count added."""
    text = read_brain(config.brain)
    seen = existing_hashes(text)
    today = datetime.date.today().isoformat()
    keywords = list(config.search_queries)
    scored = sorted(entries, key=lambda e: relevance_score(e, keywords), reverse=True)
    lines: List[str] = []
    added = 0
    for entry in scored:
        if added >= config.limit:
            break
        if not entry.url:
            continue
        digest = entry.hash()
        if digest in seen:
            continue
        relevance = relevance_score(entry, keywords)
        if relevance <= 0:
            continue
        lines.append(entry.to_log_line(relevance, today))
        seen.add(digest)
        added += 1
    if config.dry_run:
        LOG.info("dry-run: would append %d entries", added)
        for line in lines:
            print(line)
        return added
    if added:
        block = f"\n### Auto-crawl {today}\n" + "\n".join(lines) + "\n"
        _atomic_write(config.brain, text + block)
    LOG.info("appended %d new entries to %s", added, config.brain)
    return added


# --- fetching --------------------------------------------------------------

class _TitleMetaParser(HTMLParser):
    """Extract ``<title>`` text and named meta content from an HTML document."""

    def __init__(self) -> None:
        super().__init__()
        self._in_title = False
        self._title_parts: List[str] = []
        self.meta: Dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            attrs_dict = dict(attrs)
            name = (attrs_dict.get("name") or attrs_dict.get("property") or "").lower()
            if name:
                self.meta[name] = html.unescape(attrs_dict.get("content", ""))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self._title_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self._title_parts).split())


def _http_get(url: str, config: Config) -> Optional[str]:
    """Fetch a text body with the standard library; return None on any failure."""
    request = urllib.request.Request(url, headers={"User-Agent": config.user_agent})
    try:
        with urllib.request.urlopen(request, timeout=config.timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            if not any(token in content_type for token in ("text", "html", "xml", "json")):
                return None
            raw = response.read(2_000_000)
            charset = response.headers.get_content_charset() or "utf-8"
            try:
                return raw.decode(charset, errors="replace")
            except LookupError:
                return raw.decode("utf-8", errors="replace")
    except Exception as exc:  # network/HTTP/encoding errors are non-fatal here
        LOG.debug("HTTP fetch failed for %s: %s", url, exc)
        return None


def _entry_from_html(url: str, html_text: str) -> Entry:
    parser = _TitleMetaParser()
    try:
        parser.feed(html_text)
    except Exception as exc:  # malformed HTML should not abort the run
        LOG.debug("html parse %s: %s", url, exc)
    return Entry(
        title=parser.title or f"Update scan: {url}",
        url=url,
        abstract=parser.meta.get("description", "")[:600],
        venue=urllib.parse.urlparse(url).netloc,
        year=str(datetime.date.today().year),
    )


def _fetch_with_crawl4ai(urls: Sequence[str], config: Config) -> List[Entry]:
    """Use crawl4ai when available; return [] otherwise (graceful degradation)."""
    try:
        from crawl4ai import AsyncWebCrawler  # type: ignore
    except Exception as exc:
        LOG.info("crawl4ai unavailable (%s); using stdlib fallback.", exc)
        return []
    import asyncio

    async def _run() -> List[Entry]:
        results: List[Entry] = []
        async with AsyncWebCrawler() as crawler:
            for url in urls:
                try:
                    result = await crawler.arun(url=url)
                    html_text = getattr(result, "html", "") or ""
                    markdown = getattr(result, "markdown", "") or ""
                    entry = _entry_from_html(url, html_text)
                    if markdown and not entry.abstract:
                        entry.abstract = markdown[:600]
                    results.append(entry)
                except Exception as exc:
                    LOG.debug("crawl4ai %s: %s", url, exc)
        return results

    try:
        return asyncio.run(_run())
    except Exception as exc:
        LOG.warning("crawl4ai run aborted: %s", exc)
        return []


def _fetch_with_stdlib(urls: Sequence[str], config: Config) -> List[Entry]:
    results: List[Entry] = []
    for url in urls:
        body = _http_get(url, config)
        if body:
            results.append(_entry_from_html(url, body))
    return results


def _parse_arxiv(markdown: str) -> List[Entry]:
    out: List[Entry] = []
    for match in re.finditer(r"(?:arXiv:)?(\d{4}\.\d{4,5})(?:v\d+)?", markdown):
        aid = match.group(1)
        out.append(
            Entry(
                title=f"ArXiv:{aid}",
                url=f"https://arxiv.org/abs/{aid}",
                venue="arXiv",
                year=str(datetime.date.today().year),
            )
        )
    return out


def _arxiv_list_url(category: str) -> str:
    return f"https://arxiv.org/list/{category}/recent"


def _discover_via_search(config: Config) -> List[Entry]:
    """Best-effort query expansion through a keyless search HTML endpoint."""
    out: List[Entry] = []
    for query in config.search_queries:
        search_url = "https://duckduckgo.com/html/?q=" + urllib.parse.quote_plus(query)
        body = _http_get(search_url, config)
        if not body:
            continue
        for encoded in re.findall(r'uddg=([^&"]+)', body)[:5]:
            real = urllib.parse.unquote(html.unescape(encoded))
            if real.startswith("http"):
                out.append(
                    Entry(
                        title=f"Search result: {query}",
                        url=real,
                        year=str(datetime.date.today().year),
                    )
                )
    return out


def fetch_entries(config: Config) -> List[Entry]:
    """Discover and return a deduplicated batch of candidate entries."""
    if not config.network:
        LOG.info("network disabled; producing no live entries.")
        return []
    entries: List[Entry] = []
    crawled = _fetch_with_crawl4ai(config.web_sources, config)
    entries.extend(crawled if crawled else _fetch_with_stdlib(config.web_sources, config))
    for category in config.arxiv_categories:
        body = _http_get(_arxiv_list_url(category), config)
        if body:
            entries.extend(_parse_arxiv(body))
    entries.extend(_discover_via_search(config))

    seen: set = set()
    unique: List[Entry] = []
    for entry in entries:
        digest = entry.hash()
        if digest in seen:
            continue
        seen.add(digest)
        unique.append(entry)
    return unique


# --- cli -------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="knowledge_updater",
        description="Grow SECOND-KNOWLEDGE-BRAIN.md for the Smart Travel Planner skill.",
    )
    parser.add_argument("--brain", default=DEFAULT_BRAIN, help="path to the knowledge brain markdown")
    parser.add_argument("--sources", default=None, help="comma-separated web source URLs (overrides defaults)")
    parser.add_argument("--queries", default=None, help="comma-separated search queries (overrides defaults)")
    parser.add_argument("--limit", type=int, default=25, help="max entries appended per run")
    parser.add_argument("--timeout", type=float, default=20.0, help="per-request timeout in seconds")
    parser.add_argument("--dry-run", action="store_true", help="print what would be appended; do not write")
    parser.add_argument("--no-network", action="store_true", help="skip all network access (offline smoke test)")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase logging verbosity")
    return parser


def _configure_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity >= 1:
        level = logging.INFO
    if verbosity >= 2:
        level = logging.DEBUG
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=level
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    _configure_logging(args.verbose)
    config = Config.from_args(args)
    LOG.info("knowledge_updater run (dry_run=%s network=%s)", config.dry_run, config.network)
    entries = fetch_entries(config)
    added = append_entries(entries, config)
    if added == 0:
        LOG.info("no new entries this run (network/dedup/relevance).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
