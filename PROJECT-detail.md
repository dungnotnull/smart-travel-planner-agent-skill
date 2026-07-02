# PROJECT-detail.md — Smart Travel Planner (cost/experience optimization) (Skill #160)

## Executive Summary
Plans self-guided trips that optimize cost and experience using real-time price,
weather, and event data plus traveler preferences. This skill is a full Claude
harness in the **lifestyle-personal** cluster. It runs a research-first,
framework-grounded workflow that scores the subject against named world-renowned
methodologies, challenges its own assumptions, and returns a prioritized
improvement roadmap, while continuously updating its knowledge base.

## Problem Statement
DIY trip planning over- or under-packs the itinerary and overspends because
cost, experience fit, and logistics are balanced by guesswork. This skill builds
an optimized itinerary and scores it for cost, experience, and feasibility.

## Target Users & Use Cases
Practitioners, reviewers, and decision-makers who need an expert-grade,
evidence-based assessment in this domain. Trigger examples:
1. **Trip plan** — "7 days in Japan on a budget" → build itinerary, score cost/experience/feasibility.
2. **Optimize** — "Cut my trip cost without losing fun" → reallocate spend, score value.
3. **Family trip** — "Plan a kid-friendly beach week" → pace for kids, score fit/risk.
4. **Reroute** — "Rain forecast — adjust day 3" → swap to indoor options, update contingency.
5. **Degraded mode** — "Plan offline" → fall back to brain heuristics, flag stale signals.
6. **Missing inputs** — "Plan a trip to Europe" → ask targeted questions, never invent facts.

## Harness Architecture
```
/smart-travel-planner (main.md)
   |-- sub-intake .................... Intake & Context Gathering
   |-- sub-framework-selector ....... Evaluation Framework Selector
   |-- [research] WebSearch/WebFetch + SECOND-KNOWLEDGE-BRAIN
   |-- sub-scoring-engine ........... Scoring Engine
   |-- [challenge] devil's-advocate assumption review
   |-- sub-improvement-roadmap ...... Improvement Roadmap
   +-- synthesize ................... professional deliverable + Quality Gates
```

## Full Sub-Skill Catalog
### sub-intake — Intake & Context Gathering
- **Purpose:** Collect the structured inputs, scope, and goals needed to run the analysis; ask clarifying questions when key facts are missing.
- **Inputs:** the raw user request and any context from a prior harness invocation.
- **Outputs:** a validated case context (every field labeled provided / inferred / missing) with clarifying questions and a consistency-check summary.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** every required field is provided, explicitly inferred with a stated basis, or accompanied by a clarifying question; no required fact is silently invented.

### sub-framework-selector — Evaluation Framework Selector
- **Purpose:** Pick the smallest set of named world-renowned framework(s) that fully covers the case and justify the choice.
- **Inputs:** the validated case context from `sub-intake`.
- **Outputs:** the selected framework set, a per-framework justification, the framework → dimension map, and the exclusion list with reasons.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** all five scoring dimensions are grounded by at least one selected framework; inclusions and exclusions are justified.

### sub-scoring-engine — Scoring Engine
- **Purpose:** Apply the multi-dimensional rubric to produce weighted scores with evidence citations for each dimension.
- **Inputs:** case context, selected frameworks, and gathered research evidence.
- **Outputs:** per-dimension scores with citations and rationale, the weighted total, the letter grade, and a list of conflicts/uncertainties.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** every dimension has a 0–100 score and at least one citation; stale/offline-derived scores are labeled.

### sub-improvement-roadmap — Improvement Roadmap
- **Purpose:** Generate a prioritized, effort/impact-ranked set of recommendations traceable to the scored findings.
- **Inputs:** case context, per-dimension scores, and challenge-stage notes.
- **Outputs:** a ranked action list (effort × impact, traceable) plus a top-3 summary.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** every action is traceable to a finding, has explicit effort/impact ratings, and is sorted by the priority rule.

## Evaluation Frameworks (World-Renowned, Citable)
| Framework / Standard | Role in this skill |
|---|---|
| Travel motivation (push/pull, Maslow) | Match itinerary to traveler needs. |
| Total cost of trip optimization | Transport/lodging/activity trade-offs. |
| Itinerary density balancing | Avoid over/under-scheduling. |
| Experience design (peak-end rule) | Sequence highlights for memorability. |
| Risk & contingency planning | Weather, closures, safety buffers. |
| Logistics feasibility (routing/transfer modeling) | Realistic transfers, clustering, hours. |

## Scoring Model
| Dimension | Weight | What is assessed |
|---|---|---|
| Cost optimization | 25% | budget fit, value per spend |
| Experience quality & fit | 25% | alignment to interests, peak-end design |
| Logistics feasibility | 20% | routing, transfers, opening hours realistic |
| Time & pacing balance | 15% | density not exhausting/wasteful |
| Risk & contingency | 15% | weather/safety buffers, backups |
Each dimension is scored 0–100 with cited evidence; the weighted total yields an
overall grade (A ≥ 90, B 75–89, C 60–74, D < 60).

## E2E Execution Flow
1. Parse the user request; `sub-intake` asks targeted questions if inputs are insufficient — missing inputs are never silently invented.
2. `sub-framework-selector` picks the smallest covering framework set and justifies it.
3. Research stage gathers highest-tier evidence (see evidence hierarchy); degrade gracefully to `SECOND-KNOWLEDGE-BRAIN.md` if offline, and label scores `offline-derived`.
4. `sub-scoring-engine` scores each dimension with citations and computes the weighted total + letter grade.
5. Challenge stage stress-tests load-bearing assumptions and grades certainty.
6. `sub-improvement-roadmap` produces ranked, traceable actions.
7. Synthesize the deliverable; run Quality Gates; present.

**Error handling:** missing inputs → ask; conflicting evidence → present both and grade certainty; tool failure → fallback + explicit limitation notice.

## SECOND-KNOWLEDGE-BRAIN Integration
- Sources: https://www.lonelyplanet.com, https://skift.com, https://www.unwto.org, https://www.tripadvisor.com
- ArXiv categories: (none — tourism has no dedicated track)
- Crawl queries: travel itinerary optimization research; budget travel trends 2026; destination safety advisory; experience design tourism
- Append format: dated `### Auto-crawl YYYY-MM-DD` section with Title, Authors, Year, Venue, URL, relevance, and a `<!--hash:...-->` marker.
- Dedup: by URL/DOI hash; writes are atomic; offline mode exits cleanly.

## Supporting Tools Spec
`tools/knowledge_updater.py`:
- **Inputs:** source list + queries (defaults overridable via CLI flags).
- **Outputs:** appended `SECOND-KNOWLEDGE-BRAIN.md` entries under a dated section.
- **Schedule:** weekly cron recommended.
- **Modes:** live crawl (default), `--dry-run` (no writes), `--no-network` (offline smoke test).
- **Resilience:** graceful degradation when `crawl4ai` or the network is unavailable; atomic writes prevent corruption.

## Quality Gates (must all pass before final output)
- Every score cites at least one source or the chosen framework.
- The challenge stage is completed; load-bearing assumptions are tested.
- Roadmap items are prioritized by effort and impact and traceable to findings.
- Limitations and evidence certainty are stated explicitly.
- Missing inputs were resolved via intake, never silently invented.

## Test Scenarios
See `tests/test-scenarios.md` for 7 scenarios (happy path, optimize, family,
reroute, degraded mode, missing inputs, and an automated offline pipeline test)
and `tests/test_knowledge_updater.py` for the offline pytest suite.

## Key Design Decisions
1. Framework-grounded scoring (no ad-hoc criteria).
2. Research-first with graceful degradation to the local knowledge brain.
3. Mandatory challenge stage to counter confirmation bias.
4. Standard quality gates enforced before delivery.
5. Self-improving knowledge base via weekly crawl, with offline-safe operation.
