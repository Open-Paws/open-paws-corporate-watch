"""Data models for corporate welfare commitments."""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from enum import Enum


class CommitmentStatus(str, Enum):
    ON_TRACK = "ON_TRACK"
    DELAYED = "DELAYED"
    REVERSED = "REVERSED"
    COMPLETED = "COMPLETED"
    UNVERIFIED = "UNVERIFIED"


class CommitmentCategory(str, Enum):
    CAGE_FREE = "CAGE_FREE"
    GESTATION_CRATE_FREE = "GESTATION_CRATE_FREE"
    ANTIBIOTIC_REDUCTION = "ANTIBIOTIC_REDUCTION"
    SLAUGHTER_METHOD = "SLAUGHTER_METHOD"
    TRANSPORT = "TRANSPORT"
    THIRD_PARTY_AUDIT = "THIRD_PARTY_AUDIT"


@dataclass
class WelfareCommitment:
    """A corporate animal welfare commitment."""
    commitment_id: str
    company_name: str
    company_domain: str
    category: CommitmentCategory

    # The commitment itself
    description: str
    original_announcement_url: Optional[str]
    announced_date: Optional[date]
    target_date: Optional[date]  # When they committed to complete by

    # Current status
    status: CommitmentStatus = CommitmentStatus.UNVERIFIED
    percent_complete: Optional[float] = None
    last_verified_date: Optional[date] = None
    verification_source: Optional[str] = None

    # Alert history
    status_changes: list[dict] = field(default_factory=list)


@dataclass
class Company:
    """A company being tracked for welfare commitment follow-through."""
    company_id: str
    name: str
    domain: str
    sector: str  # "fast food", "grocery", "food manufacturer", "hotel", etc.
    revenue_tier: str  # "Fortune 500", "Fortune 1000", "mid-market", "regional"
    commitments: list[WelfareCommitment] = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        """0–100 accountability score based on commitment follow-through.

        Scoring reflects degree of actual follow-through:
        - COMPLETED: 100 — commitment fulfilled
        - ON_TRACK: 70 — meeting interim milestones
        - DELAYED: 30 — pushed back without reversal
        - REVERSED: 0 — explicitly abandoned
        - UNVERIFIED: 20 — made but no verification mechanism
        """
        if not self.commitments:
            return 0.0
        scores = []
        for c in self.commitments:
            if c.status == CommitmentStatus.COMPLETED:
                scores.append(100.0)
            elif c.status == CommitmentStatus.ON_TRACK:
                scores.append(70.0)
            elif c.status == CommitmentStatus.DELAYED:
                scores.append(30.0)
            elif c.status == CommitmentStatus.REVERSED:
                scores.append(0.0)
            else:
                scores.append(20.0)  # UNVERIFIED
        return sum(scores) / len(scores)
