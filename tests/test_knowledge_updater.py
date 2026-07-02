# -*- coding: utf-8 -*-
"""Unit tests for the Smart Travel Planner knowledge pipeline.

These tests exercise the pure, offline parts of ``tools/knowledge_updater`` so
they run anywhere without network access or optional dependencies. They guard
the scoring, deduplication, atomic-append and CLI contract that the live crawl
relies on.
"""
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.normpath(os.path.join(HERE, "..", "tools"))
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import knowledge_updater as ku


def test_entry_hash_stable_and_url_based():
    a = ku.Entry(title="x", url="https://example.com/a")
    b = ku.Entry(title="y", url="https://example.com/a")
    assert a.hash() == b.hash()
    assert a.hash() != ku.Entry(title="x", url="https://example.com/b").hash()
    assert len(a.hash()) == 16


def test_doi_overrides_url_for_hash():
    e = ku.Entry(title="x", url="https://example.com/a", doi="10.1000/xyz")
    other = ku.Entry(title="x", url="https://example.com/different", doi="10.1000/xyz")
    assert e.hash() == other.hash()


def test_relevance_score_keywords_and_recency():
    e_new = ku.Entry(title="budget travel optimization", url="u", year="2025", abstract="itinerary density")
    e_old = ku.Entry(title="budget travel optimization", url="u", year="2000", abstract="itinerary density")
    keywords = ["budget", "travel", "optimization"]
    today = datetime.date(2026, 1, 1)
    assert 0 < ku.relevance_score(e_new, keywords, today=today) <= 1.0
    assert ku.relevance_score(e_new, keywords, today=today) > ku.relevance_score(e_old, keywords, today=today)


def test_relevance_zero_when_no_match_and_no_year():
    e = ku.Entry(title="nothing relevant", url="u", abstract="zzz")
    assert ku.relevance_score(e, ["budget", "travel"]) == 0.0


def test_relevance_zero_when_no_keywords():
    e = ku.Entry(title="budget travel", url="u", year="2025")
    assert ku.relevance_score(e, []) == 0.0


def test_existing_hashes_parsing():
    text = "line <!--hash:abcdef0123456789--> other <!--hash:0000000000000000-->"
    assert ku.existing_hashes(text) == {"abcdef0123456789", "0000000000000000"}


def test_append_entries_dedup_and_atomic_write(tmp_path):
    brain = tmp_path / "BRAIN.md"
    brain.write_text("# Brain\n\nExisting <!--hash:abcdef0123456789-->\n", encoding="utf-8")
    cfg = ku.Config(brain=str(brain), search_queries=["budget travel"], network=False, limit=10)
    entries = [
        ku.Entry(title="budget travel trends", url="https://example.com/new", year="2025"),
        ku.Entry(title="budget travel trends", url="https://example.com/new", year="2025"),
    ]
    added = ku.append_entries(entries, cfg)
    assert added == 1
    content = brain.read_text(encoding="utf-8")
    assert "### Auto-crawl" in content
    assert "https://example.com/new" in content
    assert "<!--hash:" in content
    # no leftover temp file from the atomic write
    assert not (tmp_path / "BRAIN.md.tmp").exists()


def test_append_dry_run_writes_nothing(tmp_path):
    brain = tmp_path / "BRAIN.md"
    original = "# Brain\n"
    brain.write_text(original, encoding="utf-8")
    cfg = ku.Config(brain=str(brain), search_queries=["budget travel"], network=False, dry_run=True)
    entries = [ku.Entry(title="budget travel trends", url="https://example.com/x", year="2025")]
    assert ku.append_entries(entries, cfg) == 1
    assert brain.read_text(encoding="utf-8") == original


def test_append_skips_zero_relevance(tmp_path):
    brain = tmp_path / "BRAIN.md"
    brain.write_text("# Brain\n", encoding="utf-8")
    cfg = ku.Config(brain=str(brain), search_queries=["budget travel"], network=False)
    entries = [ku.Entry(title="unrelated topic", url="https://example.com/y")]
    assert ku.append_entries(entries, cfg) == 0
    assert brain.read_text(encoding="utf-8") == "# Brain\n"


def test_append_respects_limit(tmp_path):
    brain = tmp_path / "BRAIN.md"
    brain.write_text("# Brain\n", encoding="utf-8")
    cfg = ku.Config(brain=str(brain), search_queries=["budget travel"], network=False, limit=2)
    entries = [
        ku.Entry(title=f"budget travel item {i}", url=f"https://example.com/{i}", year="2025")
        for i in range(5)
    ]
    assert ku.append_entries(entries, cfg) == 2


def test_append_skips_entries_without_url(tmp_path):
    brain = tmp_path / "BRAIN.md"
    brain.write_text("# Brain\n", encoding="utf-8")
    cfg = ku.Config(brain=str(brain), search_queries=["budget travel"], network=False)
    entries = [ku.Entry(title="budget travel trends", url="", year="2025")]
    assert ku.append_entries(entries, cfg) == 0


def test_fetch_no_network_returns_empty():
    cfg = ku.Config(brain=os.devnull, network=False)
    assert ku.fetch_entries(cfg) == []


def test_title_meta_parser():
    parser = ku._TitleMetaParser()
    parser.feed(
        "<html><head><title>Hello World</title>"
        "<meta name='description' content='desc here'></head><body></body></html>"
    )
    assert parser.title == "Hello World"
    assert parser.meta.get("description") == "desc here"


def test_parse_arxiv():
    entries = ku._parse_arxiv("see arXiv:2401.12345 and also 1902.54321v2")
    assert len(entries) == 2
    assert entries[0].url == "https://arxiv.org/abs/2401.12345"
    assert entries[1].url == "https://arxiv.org/abs/1902.54321"


def test_to_log_line_contains_hash_marker():
    entry = ku.Entry(title="budget travel", url="https://example.com/a", year="2025", authors="Anon")
    line = entry.to_log_line(0.55, "2026-07-02")
    assert entry.hash() in line
    assert "2026-07-02" in line
    assert "https://example.com/a" in line


def test_main_offline_smoke(tmp_path):
    brain = tmp_path / "BRAIN.md"
    brain.write_text("# Brain\n", encoding="utf-8")
    assert ku.main(["--brain", str(brain), "--no-network"]) == 0
    assert brain.read_text(encoding="utf-8") == "# Brain\n"
