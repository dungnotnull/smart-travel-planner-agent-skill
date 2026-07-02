# SECOND-KNOWLEDGE-BRAIN.md — Smart Travel Planner (cost/experience optimization) (Skill #160)

> Self-improving domain knowledge base. Grown by `tools/knowledge_updater.py`
> (weekly cron recommended). Newest evidence is preferred per the evidence
> hierarchy (Systematic Review > Meta-Analysis > RCT > Cohort > Expert Opinion >
> Blog). Entries appended by the pipeline are deduplicated by URL/DOI hash and
> live under dated `### Auto-crawl` sections below the hand-curated content.

## Core Concepts & Frameworks
- **Travel motivation (push/pull, Maslow)** — Match itinerary to traveler needs.
  Push factors are internal (rest, escape, self-discovery); pull factors are
  destination attributes (landscape, culture, events). An itinerary is
  well-motivated when each day serves at least one push and one pull factor.
- **Total cost of trip optimization** — Treat transport, lodging and activities
  as a joint optimization: minimize total spend subject to a value-per-spend
  floor, rather than minimizing any one line item in isolation.
- **Itinerary density balancing** — Schedule against a target pace (packed /
  balanced / relaxed). Measure density as scheduled-hours per day plus transfer
  load; flag days above 1.4× or below 0.6× the target as over- or under-packed.
- **Experience design (peak-end rule)** — Memory of an experience is dominated
  by its peak moment and its ending. Sequence a clear peak per day and close
  each day with a positive anchor; avoid a flat or anti-climactic close.
- **Risk & contingency planning** — Carry one indoor/backup activity per
  weather-exposed day, a contingency budget headroom (~10% of total), and an
  advisory check per destination before finalizing.

## Key References & Frameworks
| Reference | Authors / Source | Year | Venue / URL | Relevance |
|---|---|---|---|---|
| A Theory of Human Motivation | Maslow, A. H. | 1943 | Psychological Review, 50(4), 370–396 · DOI: 10.1037/h0054346 | Grounds push/pull travel motivation. |
| International Tourism Highlights | UNWTO | ongoing | https://www.unwto.org | Global demand, cost benchmarks and advisory context. |
| Skift Megatrends | Skift | ongoing | https://skift.com | Travel-industry trends affecting cost and experience. |
| Destination guides | Lonely Planet | ongoing | https://www.lonelyplanet.com | Logistics, opening hours and experience-fit data. |
| Traveler reviews | TripAdvisor | ongoing | https://www.tripadvisor.com | Experience quality and risk signals from recent visitors. |

## State-of-the-Art Methods & Tools
- Apply the frameworks above as the scoring backbone; never use ad-hoc criteria.
- Prefer primary standards documents and authoritative sources over blogs.
- Combine the quantitative weighted score with a qualitative challenge stage.
- Re-check live signals (price, weather, events, advisories) at run time; label
  any score derived only from this brain as `offline-derived` / stale.

## Authoritative Data Sources
- https://www.lonelyplanet.com
- https://skift.com
- https://www.unwto.org
- https://www.tripadvisor.com
- ArXiv: (none — tourism has no dedicated arXiv track)

## Analytical Frameworks (Scoring Backbone)
| Framework / Standard | Role in this skill |
|---|---|
| Travel motivation (push/pull, Maslow) | Match itinerary to traveler needs. |
| Total cost of trip optimization | Transport/lodging/activity trade-offs. |
| Itinerary density balancing | Avoid over/under-scheduling. |
| Experience design (peak-end rule) | Sequence highlights for memorability. |
| Risk & contingency planning | Weather, closures, safety buffers. |
| Logistics feasibility (routing/transfer modeling) | Realistic transfers, clustering, hours. |

## Self-Update Protocol (crawl4ai config)
- **Sources:** the authoritative URLs above + any configured arXiv categories.
- **Search queries:**
  - `travel itinerary optimization research`
  - `budget travel trends 2026`
  - `destination safety advisory`
  - `experience design tourism`
- **Frequency:** weekly (cron recommended).
- **Append format:** dated `### Auto-crawl YYYY-MM-DD` section with Title,
  Authors, Year, Venue, URL, relevance score, and a `<!--hash:...-->` marker.
- **Dedup:** skip entries whose URL/DOI hash already exists anywhere in this file.
- **Graceful degradation:** if `crawl4ai` / network is unavailable, the updater
  logs the limitation and exits cleanly; this brain keeps working unchanged.

## Knowledge Update Log
- 2026-06-18 — Knowledge base seeded at skill creation (frameworks + sources).
- 2026-07-02 — Knowledge base hardened with verifiable seed references and the
  production-grade `tools/knowledge_updater.py` pipeline. First live crawl is
  deferred to the production runtime (by design, to save resources pre-launch).
