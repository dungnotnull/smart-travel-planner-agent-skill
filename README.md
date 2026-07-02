# Smart Travel Planner — cost/experience optimization (Skill #160)

A Claude skill that designs **cost- and experience-optimized self-guided trips**
using real-time price, weather and event signals plus traveler preferences. It
runs a research-first, framework-grounded harness that scores every itinerary
against named world-renowned methodologies, challenges its own assumptions, and
returns a prioritized improvement roadmap — while a self-improving knowledge
brain keeps the skill current.

**Cluster:** `lifestyle-personal` · **Slug:** `smart-travel-planner`

## Why this skill

DIY trip planning over- or under-packs the itinerary and overspends because
cost, experience fit and logistics are balanced by guesswork. This skill
replaces guesswork with an explicit, citable scoring model and a devil's-advocate
challenge stage, so the output is defensible rather than opinionated.

## How it works

```
/smart-travel-planner (skills/main.md)
   |-- sub-intake .................... Intake & Context Gathering
   |-- sub-framework-selector ....... Evaluation Framework Selector
   |-- [research] WebSearch/WebFetch + SECOND-KNOWLEDGE-BRAIN
   |-- sub-scoring-engine ........... Scoring Engine (weighted, cited)
   |-- [challenge] devil's-advocate assumption review
   |-- sub-improvement-roadmap ...... Improvement Roadmap (effort x impact)
   +-- synthesize ................... professional report + Quality Gates
```

### Scoring model

| Dimension | Weight | What is assessed |
|---|---|---|
| Cost optimization | 25% | budget fit, value per spend |
| Experience quality & fit | 25% | alignment to interests, peak-end design |
| Logistics feasibility | 20% | routing, transfers, opening hours realistic |
| Time & pacing balance | 15% | density not exhausting / wasteful |
| Risk & contingency | 15% | weather/safety buffers, backups |

Each dimension is scored 0–100 with at least one cited source or framework
reference. The weighted total maps to a letter grade: **A** ≥ 90, **B** 75–89,
**C** 60–74, **D** < 60.

### Grounding frameworks

- **Travel motivation (push/pull, Maslow)** — match the itinerary to traveler needs.
- **Total cost of trip optimization** — transport / lodging / activity trade-offs.
- **Itinerary density balancing** — avoid over- and under-scheduling.
- **Experience design (peak-end rule)** — sequence highlights for memorability.
- **Risk & contingency planning** — weather, closures and safety buffers.

## Repository layout

```
skills/                      Claude skill definitions (the harness + sub-skills)
  main.md                    main harness, stage order, quality gates
  sub-intake.md              intake & context gathering
  sub-framework-selector.md  evaluation framework selector
  sub-scoring-engine.md      scoring engine
  sub-improvement-roadmap.md improvement roadmap
tools/                       self-improving knowledge pipeline
  knowledge_updater.py       discover / score / dedup / append evidence
tests/                       pytest unit tests + manual test scenarios
  test_knowledge_updater.py  offline unit tests for the pipeline
  test-scenarios.md          end-to-end manual scenarios (incl. degraded mode)
SECOND-KNOWLEDGE-BRAIN.md    self-improving domain knowledge base
PROJECT-detail.md            full technical specification
PROJECT-DEVELOPMENT-PHASE-TRACKING.md  phase status
CLAUDE.md                    skill index & quick reference
```

## Install

```bash
# Core pipeline has no hard dependencies.
pip install -e .

# Optional: richer JS-rendered crawling of authoritative sources.
pip install -e ".[crawl]"

# Tests.
pip install -e ".[test]"
```

## Usage

### Run the skill
Invoke `/smart-travel-planner` in a Claude session, for example:

- "7 days in Japan on a budget"
- "Cut my trip cost without losing fun"
- "Plan a kid-friendly beach week"
- "Rain forecast — adjust day 3"
- "Plan offline" (degraded mode: falls back to the knowledge brain)

### Grow the knowledge brain

```bash
python tools/knowledge_updater.py                 # live crawl + append
python tools/knowledge_updater.py --dry-run        # preview, no writes
python tools/knowledge_updater.py --no-network    # offline smoke test
python tools/knowledge_updater.py -v              # info logging
```

A weekly cron is recommended:

```
0 3 * * 0  /usr/bin/python /path/to/smart-travel-planner/tools/knowledge_updater.py >> /var/log/smart-travel-planner.log 2>&1
```

The pipeline degrades gracefully: if `crawl4ai` or the network is unavailable it
logs the limitation and exits cleanly, leaving the existing brain intact.

## Testing

```bash
pytest -q
```

The unit tests are fully offline and require no network access or optional
dependencies. The manual end-to-end scenarios live in
`tests/test-scenarios.md`.

## Quality gates (enforced before any deliverable)

- Every score cites a source or the chosen framework.
- The challenge stage is completed; key assumptions are tested.
- Roadmap items are prioritized by effort and impact and traceable to findings.
- Limitations and evidence certainty are stated explicitly.

## License

MIT — see [LICENSE](LICENSE).
