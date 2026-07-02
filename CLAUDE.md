# CLAUDE.md — Smart Travel Planner (cost/experience optimization) (Skill #160)

**Slug:** `smart-travel-planner` · **Cluster:** `lifestyle-personal` · **Source idea:** 160 · **Phase:** Built (v1, production-ready)

## Tagline
Plans self-guided trips that optimize cost and experience using real-time price, weather, and event data plus traveler preferences.

## Problem This Skill Solves
DIY trip planning over- or under-packs the itinerary and overspends because cost, experience fit, and logistics are balanced by guesswork. This skill builds an optimized itinerary and scores it for cost, experience, and feasibility.

## Harness Flow Summary
1. **Intake** (`sub-intake`) — gather structured inputs, scope, goals.
2. **Framework selection** (`sub-framework-selector`) — choose named world-renowned framework(s).
3. **Research** (WebSearch/WebFetch + SECOND-KNOWLEDGE-BRAIN) — gather highest-tier evidence.
4. **Scoring** (`sub-scoring-engine`) — multi-dimensional weighted scores with citations.
5. **Challenge** — devil's-advocate review of assumptions and weak evidence.
6. **Roadmap** (`sub-improvement-roadmap`) — prioritized effort/impact recommendations.
7. **Synthesize** — assemble the professional deliverable; pass Quality Gates.

## Gates
- No mandatory safety/compliance gate for this cluster, but the standard Quality Gates below still apply.

## Sub-skills
- `skills/sub-intake.md` — Intake & Context Gathering: collect the structured inputs, scope, and goals; ask clarifying questions when key facts are missing.
- `skills/sub-framework-selector.md` — Evaluation Framework Selector: pick the smallest set of world-renowned framework(s) that covers all scoring dimensions and justify it.
- `skills/sub-scoring-engine.md` — Scoring Engine: apply the multi-dimensional rubric to produce weighted, cited scores and a letter grade.
- `skills/sub-improvement-roadmap.md` — Improvement Roadmap: generate a prioritized, effort/impact-ranked, traceable action plan.

## Tools Required
- `WebSearch`, `WebFetch` — live evidence and standards updates
- `Read`, `Write` — load knowledge base, emit deliverables
- `Bash` — run `tools/knowledge_updater.py`
- Skill tool — invoke sub-skills in sequence

## Knowledge Sources
- ArXiv: (none — non-paper domain; rely on authoritative web sources)
- Authoritative domain sources:
  - https://www.lonelyplanet.com
  - https://skift.com
  - https://www.unwto.org
  - https://www.tripadvisor.com
- Crawl queries: travel itinerary optimization research; budget travel trends 2026; destination safety advisory; experience design tourism

## Supporting Tools
- `tools/knowledge_updater.py` — crawl4ai + stdlib pipeline that grows `SECOND-KNOWLEDGE-BRAIN.md` (weekly cron recommended). Offline-safe: `python tools/knowledge_updater.py --no-network`.

## Active Development Tasks
- [x] Scaffold full deliverable set
- [x] Define 4 sub-skills with detailed logic
- [x] Production-grade `tools/knowledge_updater.py` with CLI, dedup, atomic writes, graceful degradation
- [x] Offline pytest suite for the pipeline (`tests/test_knowledge_updater.py`)
- [x] Open-source packaging (README, LICENSE, pyproject.toml, requirements.txt, .gitignore)
- [x] Expand SECOND-KNOWLEDGE-BRAIN with verifiable seed references
- [x] Phase 5 cross-skill wiring within the `lifestyle-personal` cluster
- [ ] First live crawl at production runtime (deferred by design to save resources pre-launch)
- [ ] Add regression cases from real user runs

## Cross-Skill Wiring (Phase 5, cluster: lifestyle-personal)
This skill exposes reusable, composable patterns for sibling skills in the
`lifestyle-personal` cluster:
- **Intake pattern** — `sub-intake` schema (required/inferred/missing labeling,
  max-3 clarifying questions, consistency check) is reusable by any planning
  skill that starts from a loose user request.
- **Framework-grounded scoring pattern** — `sub-framework-selector` +
  `sub-scoring-engine` (smallest covering framework set, weighted cited scores,
  letter grade) is reusable by any evaluative skill in the cluster.
- **Self-improving knowledge brain pattern** — `tools/knowledge_updater.py`
  (discover → score → dedup → atomic append, with offline degradation) is
  reusable by any skill that maintains a `SECOND-KNOWLEDGE-BRAIN.md`.
Sibling skills may import these sub-skill specs and the pipeline module by
relative path; no cluster-level shared package is required.

## Related Root Docs
- `PROJECT-detail.md` — full technical spec
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — phase roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — self-improving knowledge base
- `README.md` — install, usage, testing
- `tests/test-scenarios.md` — end-to-end manual + automated scenarios
