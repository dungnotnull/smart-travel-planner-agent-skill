# Test Scenarios — Smart Travel Planner (cost/experience optimization) (Skill #160)

These scenarios validate the harness end-to-end: stage order, framework
grounding, scoring with citations, the challenge stage, the roadmap, quality
gates, and graceful degradation. Scenarios 1–6 are manual; scenario 7 is an
automated offline pipeline test run with `pytest`.

## Scenario 1: Trip plan
- **User input:** "7 days in Japan on a budget"
- **Expected behavior:** Skill builds a day-by-day itinerary and scores
  cost / experience / feasibility.
- **Expected stage order:** intake → framework-selector → research → scoring →
  challenge → roadmap → synthesize.
- **Pass criteria:**
  - Correct stage order is followed and visible in the report.
  - At least one framework is named and justified.
  - Every dimension score cites a source or framework.
  - The roadmap is prioritized by effort × impact and traceable to findings.
  - Limitations and evidence certainty are stated.

## Scenario 2: Optimize
- **User input:** "Cut my trip cost without losing fun"
- **Expected behavior:** Skill reallocates spend across transport/lodging/
  activities and re-scores value per spend.
- **Pass criteria:**
  - Total cost of trip optimization is selected and justified.
  - Cost optimization score improves while experience quality does not collapse.
  - The trade-off and its certainty are stated explicitly.

## Scenario 3: Family trip
- **User input:** "Plan a kid-friendly beach week"
- **Expected behavior:** Skill paces for children and scores experience fit and
  risk.
- **Pass criteria:**
  - Travel motivation (push/pull) is applied to the family profile.
  - Pacing reflects child energy and rest buffers.
  - Risk & contingency covers water safety and weather.

## Scenario 4: Reroute
- **User input:** "Rain forecast — adjust day 3"
- **Expected behavior:** Skill swaps day 3 to indoor options and updates the
  contingency plan.
- **Pass criteria:**
  - Risk & contingency planning drives the swap.
  - Updated scores reflect the new day 3 plan.
  - The original and revised plans are both shown for traceability.

## Scenario 5: Degraded mode
- **User input:** "Plan offline"
- **Expected behavior:** Falls back to `SECOND-KNOWLEDGE-BRAIN.md` heuristics
  and flags live price/weather as stale.
- **Pass criteria:**
  - Stage order is unchanged (only the evidence tier changes).
  - Every score is labeled `offline-derived` / stale.
  - A prominent limitation notice is present in the report.

## Scenario 6: Missing inputs
- **User input:** "Plan a trip to Europe" (no dates, budget, or travelers)
- **Expected behavior:** `sub-intake` asks targeted clarifying questions before
  proceeding; it never invents the missing facts.
- **Pass criteria:**
  - The skill asks for dates, budget, and travelers.
  - No required field is silently filled with a guess.
  - Inferred defaults (if the user declines to answer) are flagged for the
    Challenge stage.

## Scenario 7: Knowledge pipeline offline smoke (automated)
- **Command:** `python tools/knowledge_updater.py --no-network` and
  `pytest tests/test_knowledge_updater.py -q`
- **Expected behavior:** The pipeline imports with no optional dependencies,
  performs no network access, and all unit tests pass.
- **Pass criteria:**
  - `--no-network` exits 0 and writes nothing to the brain.
  - `--dry-run` prints candidate lines without writing.
  - Deduplication, atomic writes, scoring and the CLI contract pass under pytest.

## Regression Notes
- Add real user runs here as regression cases (input → expected grade deltas).
- After each `tools/knowledge_updater.py` live run, verify dedup by URL/DOI hash
  and that new entries land under a date-stamped `### Auto-crawl` section.
