"""
Generate public accountability scorecard for companies.
Embeddable widget for campaign pages.
"""
from ..commitments.models import Company, CommitmentStatus


def generate_scorecard(company: Company) -> dict:
    """Generate a comprehensive accountability scorecard for a company.

    Returns a dict safe to serialize as JSON and embed in campaign pages.
    """
    return {
        "company_id": company.company_id,
        "company_name": company.name,
        "sector": company.sector,
        "overall_score": round(company.overall_score, 1),
        "score_label": _score_label(company.overall_score),
        "total_commitments": len(company.commitments),
        "commitments_completed": sum(
            1 for c in company.commitments if c.status == CommitmentStatus.COMPLETED
        ),
        "commitments_on_track": sum(
            1 for c in company.commitments if c.status == CommitmentStatus.ON_TRACK
        ),
        "commitments_delayed": sum(
            1 for c in company.commitments if c.status == CommitmentStatus.DELAYED
        ),
        "commitments_reversed": sum(
            1 for c in company.commitments if c.status == CommitmentStatus.REVERSED
        ),
        "commitments_unverified": sum(
            1 for c in company.commitments if c.status == CommitmentStatus.UNVERIFIED
        ),
        "by_category": _by_category(company),
        "commitment_detail": _commitment_detail(company),
    }


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


def _by_category(company: Company) -> dict:
    """One entry per category showing the most recent commitment status."""
    result: dict = {}
    for commitment in company.commitments:
        cat = commitment.category.value
        if cat not in result:
            result[cat] = {
                "status": commitment.status.value,
                "percent_complete": commitment.percent_complete,
                "target_date": (
                    commitment.target_date.isoformat()
                    if commitment.target_date
                    else None
                ),
                "description": commitment.description,
            }
    return result


def _commitment_detail(company: Company) -> list[dict]:
    """Full list of commitments with all fields for the detail view."""
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
