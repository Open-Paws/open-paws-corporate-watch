# open-paws-corporate-watch

Corporate animal welfare commitment tracker and public accountability scorecard.

Monitors whether companies follow through on public pledges — cage-free timelines, gestation crate phase-outs, antibiotic reduction commitments, slaughter method upgrades — and surfaces reversals for campaign response.

## What it does

- Tracks corporate welfare commitments with deadlines and interim milestones
- Detects progress, delays, and reversals from news and corporate communications
- Scores companies 0–100 on commitment follow-through
- Generates embeddable scorecards for campaign pages
- Scores supply chain risk for animal agriculture sourcing
- Monitors corporate websites continuously for commitment page updates

## Commitment categories

| Category | Description |
|----------|-------------|
| CAGE_FREE | Cage-free egg sourcing by a target date |
| GESTATION_CRATE_FREE | Elimination of gestation crates from pork supply chain |
| ANTIBIOTIC_REDUCTION | Reducing prophylactic antibiotic use in animal ag supply |
| SLAUGHTER_METHOD | Higher-welfare slaughter method (controlled atmosphere) |
| TRANSPORT | Improved transport conditions and time limits |
| THIRD_PARTY_AUDIT | Independent welfare certification requirement |

## Accountability scores

| Score | Label |
|-------|-------|
| 80–100 | Leading |
| 60–79 | Progressing |
| 40–59 | Lagging |
| 20–39 | Failing |
| 0–19 | No Follow-Through |

## Stack

- **Backend**: FastAPI + Python 3.12 + PostgreSQL
- **Frontend**: Next.js + TypeScript + React
- **Scraping**: Scrapling (adaptive, anti-bot bypass)
- **Supply chain scoring**: EcoTrace pattern — deterministic commodity/region risk matrix

## Running locally

```bash
# Backend
cd backend
pip install -e ".[dev]"
uvicorn src.api.server:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Monitoring scrape (run as cron)
cd backend
python -m src.monitoring.scraper --companies all
```

## Architecture

```
backend/src/
  commitments/    — Commitment data models, status tracker, reversal detector
  supply_chain/   — Supply chain risk scoring (animal ag commodity/region matrix)
  monitoring/     — Scrapling-based corporate site scraper
  scoring/        — Accountability scorecard generation
  api/            — FastAPI routes

frontend/src/
  pages/          — Company search, individual company scorecard
  components/     — ScoreCard, CommitmentTimeline, SupplyChainMap

data/
  commitments/    — Seed data: 10 major food companies with known commitments
```

## Part of Open Paws

This tool supports Lever 2 (corporate accountability) in the Open Paws strategy. Scorecard data integrates with campaign pages and coalition partner tools.

- Strategy: https://github.com/Open-Paws/open-paws-strategy
- Platform: https://github.com/Open-Paws/open-paws-platform
