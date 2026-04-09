"""
FastAPI application for open-paws-corporate-watch.

Endpoints:
  GET  /companies                        — search companies
  GET  /companies/{company_id}           — company scorecard
  GET  /companies/{company_id}/commitments — all commitments
  POST /commitments/{id}/update-status   — update status from monitoring pipeline
  GET  /reversals                        — recent commitment reversals (campaign feed)
  GET  /embed/{company_id}               — embeddable scorecard widget data
"""
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..commitments.tracker import CommitmentTracker
from ..scoring.scorecard import generate_scorecard


# Module-level tracker instance (seeded from JSON on startup)
_tracker: Optional[CommitmentTracker] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _tracker
    _tracker = CommitmentTracker()
    print(f"[startup] Loaded {len(_tracker.all_companies())} companies from seed data")
    yield
    print("[shutdown] Done")


app = FastAPI(
    title="Open Paws Corporate Watch",
    description="Corporate animal welfare commitment tracker and accountability scorecard",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _get_tracker() -> CommitmentTracker:
    if _tracker is None:
        raise RuntimeError("Tracker not initialized — lifespan not running")
    return _tracker


# --- Request / response models ---

class StatusUpdateRequest(BaseModel):
    article_text: str
    source_url: str
    company_id: str


# --- Routes ---

@app.get("/companies", summary="Search companies")
async def list_companies(
    q: Optional[str] = Query(default=None, description="Search query (name or domain)"),
    sector: Optional[str] = Query(default=None, description="Filter by sector"),
):
    """List or search tracked companies with their overall accountability scores."""
    tracker = _get_tracker()

    if q:
        companies = tracker.search_companies(q)
    else:
        companies = tracker.all_companies()

    if sector:
        companies = [c for c in companies if c.sector.lower() == sector.lower()]

    return [
        {
            "company_id": c.company_id,
            "name": c.name,
            "domain": c.domain,
            "sector": c.sector,
            "revenue_tier": c.revenue_tier,
            "overall_score": round(c.overall_score, 1),
            "score_label": _score_label(c.overall_score),
            "commitment_count": len(c.commitments),
        }
        for c in sorted(companies, key=lambda x: x.name)
    ]


@app.get("/companies/{company_id}", summary="Company scorecard")
async def get_company_scorecard(company_id: str):
    """Full accountability scorecard for a single company."""
    tracker = _get_tracker()
    company = tracker.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{company_id}' not found")
    return generate_scorecard(company)


@app.get("/companies/{company_id}/commitments", summary="Company commitments")
async def get_company_commitments(company_id: str):
    """All welfare commitments for a company with current status."""
    tracker = _get_tracker()
    company = tracker.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{company_id}' not found")

    return [
        {
            "commitment_id": c.commitment_id,
            "category": c.category.value,
            "description": c.description,
            "status": c.status.value,
            "percent_complete": c.percent_complete,
            "target_date": c.target_date.isoformat() if c.target_date else None,
            "announced_date": c.announced_date.isoformat() if c.announced_date else None,
            "last_verified_date": (
                c.last_verified_date.isoformat() if c.last_verified_date else None
            ),
            "verification_source": c.verification_source,
            "original_announcement_url": c.original_announcement_url,
            "status_changes": c.status_changes,
        }
        for c in company.commitments
    ]


@app.post("/commitments/{commitment_id}/update-status", summary="Update commitment status")
async def update_commitment_status(commitment_id: str, body: StatusUpdateRequest):
    """
    Process a news article or corporate announcement through the commitment detector.
    Updates commitment status in-place.
    Returns the classification result.
    """
    tracker = _get_tracker()
    classification = tracker.process_article(
        article_text=body.article_text,
        company_id=body.company_id,
        commitment_id=commitment_id,
        source_url=body.source_url,
    )
    if classification is None:
        raise HTTPException(
            status_code=404,
            detail=f"Commitment '{commitment_id}' not found for company '{body.company_id}'",
        )
    return {"commitment_id": commitment_id, "classification": classification}


@app.get("/reversals", summary="Recent commitment reversals")
async def get_recent_reversals(limit: int = Query(default=20, le=100)):
    """
    High-urgency feed of recent commitment reversals.
    Intended for campaign alert pipelines and coalition notification systems.
    """
    tracker = _get_tracker()
    return tracker.recent_reversals(limit=limit)


@app.get("/embed/{company_id}", summary="Embeddable scorecard widget data")
async def get_embed_scorecard(company_id: str):
    """
    Minimal scorecard payload for embedding in campaign pages.
    Iframe-safe JSON — does not include full commitment history.
    """
    tracker = _get_tracker()
    company = tracker.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{company_id}' not found")

    scorecard = generate_scorecard(company)
    # Return only the fields needed for a compact embed widget
    return JSONResponse(
        content={
            "company_id": scorecard["company_id"],
            "company_name": scorecard["company_name"],
            "overall_score": scorecard["overall_score"],
            "score_label": scorecard["score_label"],
            "total_commitments": scorecard["total_commitments"],
            "commitments_completed": scorecard["commitments_completed"],
            "commitments_reversed": scorecard["commitments_reversed"],
            "by_category": scorecard["by_category"],
            "embed_url": f"/embed/{company_id}",
        },
        headers={"X-Frame-Options": "ALLOWALL"},
    )


def _score_label(score: float) -> str:
    if score >= 80:
        return "Leading"
    elif score >= 60:
        return "Progressing"
    elif score >= 40:
        return "Lagging"
    elif score >= 20:
        return "Failing"
    else:
        return "No Follow-Through"
