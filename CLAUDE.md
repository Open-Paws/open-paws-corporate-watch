# open-paws-corporate-watch — Agent Instructions

Corporate animal welfare commitment tracker and accountability scorecard.
Monitors whether companies follow through on public welfare commitments.

## Architecture
- `backend/src/commitments/` — Track commitment status (on-track, delayed, reversed)
- `backend/src/supply_chain/` — Supply chain risk scoring for animal ag sourcing
- `backend/src/monitoring/` — Scrapling-based continuous monitoring of corporate sites
- `backend/src/scoring/` — Public accountability scorecard generation
- `frontend/` — Public-facing company search and scorecard pages

## Domain Language
- "commitment" — a public corporate pledge with a timeline (cage-free by 2025, etc.)
- "follow-through" — actual implementation of a commitment
- "reversal" — a company walking back a commitment
- "factory farm" not "farm" or "supplier facility"
- "farmed animal" not "livestock"
- "cage-free" — eggs from hens not confined to battery cages (specific term, do not generalize)
- "gestation crate" — individual metal stall confining pregnant pigs (use precisely)

## Commitment Categories
- CAGE_FREE: cage-free egg sourcing commitments
- GESTATION_CRATE_FREE: pork supply chain commitments
- ANTIBIOTIC_REDUCTION: reducing prophylactic antibiotic use
- SLAUGHTER_METHOD: commitment to higher-welfare slaughter (controlled atmosphere vs. electrical)
- TRANSPORT: improved transport conditions and time limits
- THIRD_PARTY_AUDIT: independent welfare certification

## Status Values
- ON_TRACK: company is meeting interim milestones
- DELAYED: company has pushed back timeline without reversal
- REVERSED: company has explicitly abandoned the commitment
- COMPLETED: commitment fulfilled
- UNVERIFIED: commitment made but no verification mechanism

## Running
```bash
cd backend && uvicorn src.api.server:app --reload
cd frontend && npm run dev

# Monitor scrape (run as cron)
python -m src.monitoring.scraper --companies all
```

## Strategic Context — Investor Briefs (Current State as of 2026-04-09)

Two investor briefs are complete and in distribution:

**PLF Investor Brief** (`open-paws-strategy/strategy/plf-investor-brief.md`) — DONE
- 5-page ESG analyst brief (159 lines)
- Covers: EU AI Act compliance exposure, Theranos parallel, farmer dispossession risk, cage-free headwind, 5 due diligence questions
- Status: Sam distributing to ESG analyst contacts now

**Aquaculture Investor Brief** (`open-paws-strategy/strategy/aquaculture-investor-brief.md`) — DONE
- Covers: Norway 2027 regulatory stress test, validation gap, eFishery precedent, $1.5-2B impact fund exposure map
- Status: Complete, in distribution

If you are working on investor brief content, check both files first — they are the canonical source. Do not create new briefs without reading these.

## Funding Decision — Coefficient Giving Fish Welfare RFP

**DO NOT apply to the Coefficient Giving fish welfare RFP ($7M).**

Reason: The scope is humane slaughter technology. This fails the economic test — same category as PLF. Funding humane slaughter tech makes industrial aquaculture more welfare-defensible and extends its operational lifespan. It does not reduce the scale of exploitation; it legitimizes it. This decision is settled.

If asked to draft an application or explore this opportunity: decline and explain the economic test failure.

## Seven Concerns
This repo carries all seven Open Paws concerns. Key notes for this domain:
- **Security**: Corporate monitoring data is not activist data — lower sensitivity, but sourcing strategies and reversal alerts should not leak to industry.
- **Privacy**: No activist identity data in this repo. Company data is public.
- **Advocacy domain**: Use domain terminology. "Factory farm" not "farm". "Farmed animal" not "livestock". "Gestation crate" not "individual stall".
- **Cost optimization**: Scraping runs on schedule (not real-time). Cache aggressively. LLM extraction only when deterministic signals fail.
- **Accessibility**: Scorecard embeds must work in low-bandwidth contexts for campaign partners in the global south.

## Task Routing
| Doing... | Read... |
|----------|---------|
| Adding a new company | `data/commitments/seed.json` for format, `backend/src/commitments/models.py` for schema |
| Adding a commitment category | `backend/src/commitments/models.py` → CommitmentCategory enum, then `backend/src/scoring/scorecard.py` |
| Changing scoring weights | `backend/src/scoring/scorecard.py` — overall_score on Company model |
| Adding a new scrape target | `backend/src/monitoring/scraper.py` |
| Building a new frontend component | `frontend/src/components/` |
| Filing a new issue | Check `open-decisions.md` in strategy repo first |
| Investor brief work | `open-paws-strategy/strategy/plf-investor-brief.md`, `open-paws-strategy/strategy/aquaculture-investor-brief.md` |

## Every Session

Read the strategy repo for current priorities before acting:

```bash
gh api repos/Open-Paws/open-paws-strategy/contents/priorities.md --jq '.content' | base64 -d
gh api repos/Open-Paws/open-paws-strategy/contents/closed-decisions.md --jq '.content' | base64 -d
```

## Quality Gates

Run before every PR:

```bash
pip install "git+https://github.com/Open-Paws/desloppify.git#egg=desloppify[full]"
desloppify scan --path .
desloppify next
```

Minimum passing score: ≥85

Speciesist language scan:
```bash
semgrep --config semgrep-no-animal-violence.yaml .
```

All PRs must pass CI before merge.
