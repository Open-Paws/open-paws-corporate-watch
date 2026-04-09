"""
Commitment status tracker — loads companies from seed data,
applies classification results, and persists updated state.

In production this will write to PostgreSQL. Currently uses in-memory state
with JSON seed loading for the initial implementation.
"""
import json
from pathlib import Path
from datetime import date
from typing import Optional

from .models import Company, WelfareCommitment, CommitmentStatus, CommitmentCategory
from .detector import CommitmentDetector


SEED_PATH = Path(__file__).parent.parent.parent.parent / "data" / "commitments" / "seed.json"


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return date.fromisoformat(value)


def load_companies_from_seed(path: Path = SEED_PATH) -> list[Company]:
    """Load company and commitment data from seed JSON."""
    with open(path) as f:
        raw = json.load(f)

    companies = []
    for entry in raw["companies"]:
        commitments = [
            WelfareCommitment(
                commitment_id=c["commitment_id"],
                company_name=entry["name"],
                company_domain=entry["domain"],
                category=CommitmentCategory(c["category"]),
                description=c["description"],
                original_announcement_url=c.get("original_announcement_url"),
                announced_date=_parse_date(c.get("announced_date")),
                target_date=_parse_date(c.get("target_date")),
                status=CommitmentStatus(c.get("status", "UNVERIFIED")),
                percent_complete=c.get("percent_complete"),
                last_verified_date=_parse_date(c.get("last_verified_date")),
                verification_source=c.get("verification_source"),
            )
            for c in entry.get("commitments", [])
        ]
        companies.append(
            Company(
                company_id=entry["company_id"],
                name=entry["name"],
                domain=entry["domain"],
                sector=entry["sector"],
                revenue_tier=entry["revenue_tier"],
                commitments=commitments,
            )
        )
    return companies


class CommitmentTracker:
    """In-memory commitment tracker backed by seed data.

    Intended to be replaced with a PostgreSQL-backed implementation.
    The interface is stable — swap the backing store without changing callers.
    """

    def __init__(self, companies: list[Company] | None = None) -> None:
        self._companies: dict[str, Company] = {}
        for company in (companies or load_companies_from_seed()):
            self._companies[company.company_id] = company
        self._detector = CommitmentDetector()

    def all_companies(self) -> list[Company]:
        return list(self._companies.values())

    def get_company(self, company_id: str) -> Optional[Company]:
        return self._companies.get(company_id)

    def search_companies(self, query: str) -> list[Company]:
        q = query.lower()
        return [c for c in self._companies.values() if q in c.name.lower() or q in c.domain.lower()]

    def recent_reversals(self, limit: int = 20) -> list[dict]:
        """Return recent commitment reversals across all companies, newest first."""
        reversals = []
        for company in self._companies.values():
            for commitment in company.commitments:
                if commitment.status == CommitmentStatus.REVERSED:
                    reversals.append({
                        "company_id": company.company_id,
                        "company_name": company.name,
                        "commitment_id": commitment.commitment_id,
                        "category": commitment.category.value,
                        "description": commitment.description,
                        "last_verified_date": (
                            commitment.last_verified_date.isoformat()
                            if commitment.last_verified_date
                            else None
                        ),
                        "verification_source": commitment.verification_source,
                    })
        # Most recently verified reversals first
        reversals.sort(key=lambda r: r["last_verified_date"] or "", reverse=True)
        return reversals[:limit]

    def process_article(
        self,
        article_text: str,
        company_id: str,
        commitment_id: str,
        source_url: str,
    ) -> Optional[str]:
        """
        Run article through the detector and update commitment status.
        Returns the classification string, or None if company/commitment not found.
        """
        company = self._companies.get(company_id)
        if not company:
            return None

        commitment = next(
            (c for c in company.commitments if c.commitment_id == commitment_id),
            None,
        )
        if not commitment:
            return None

        classification = self._detector.classify_article(article_text, commitment)
        percent_complete = self._detector.extract_percent_complete(article_text)

        self._detector.update_status_from_classification(
            commitment, classification, percent_complete, source_url
        )
        return classification
