"""
Detect commitment progress, delays, or reversals from news and corporate communications.
Adapted from Corporate-Commitment-Monitor's HuggingFace ML classification approach,
simplified to deterministic signal matching. LLM classification can be layered on top.
"""
import re
from .models import WelfareCommitment, CommitmentStatus


# Signal phrases indicating a company is abandoning a commitment
REVERSAL_SIGNALS = [
    "walking back",
    "reversing",
    "no longer committed",
    "suspended",
    "paused indefinitely",
    "dropped pledge",
    "abandoning",
    "cost concerns",
    "supply chain challenges",
    "no longer able",
    "revising our commitment",
    "not feasible",
    "unable to meet",
]

# Signal phrases indicating a commitment timeline has been pushed back
DELAY_SIGNALS = [
    "extending timeline",
    "pushing back deadline",
    "behind schedule",
    "delayed",
    "new target date",
    "revised commitment",
    "updated timeline",
    "extended our",
    "adjustment to",
    "revised our goal",
]

# Signal phrases indicating measurable progress toward fulfilling a commitment
PROGRESS_SIGNALS = [
    "percent cage-free",
    "% cage-free",
    "completed transition",
    "ahead of schedule",
    "milestone achieved",
    "third-party verified",
    "certified",
    "fulfilled",
    "completed our",
    "met our commitment",
    "achieved our goal",
    "on track to",
]


class CommitmentDetector:
    """
    Classifies news articles and corporate announcements as progress, delay,
    or reversal for a given welfare commitment.

    Reversal detection takes priority over delay, which takes priority over progress.
    This ordering prevents companies from burying reversals in progress-framed language.
    """

    def classify_article(self, article_text: str, commitment: WelfareCommitment) -> str:
        """
        Returns 'PROGRESS', 'DELAY', 'REVERSAL', or 'UNRELATED'.

        Reversal signals override delay and progress signals — a company cannot
        frame a reversal as progress.
        """
        text_lower = article_text.lower()
        company_mentioned = commitment.company_name.lower() in text_lower

        if not company_mentioned:
            return "UNRELATED"

        reversal_score = sum(1 for s in REVERSAL_SIGNALS if s in text_lower)
        delay_score = sum(1 for s in DELAY_SIGNALS if s in text_lower)
        progress_score = sum(1 for s in PROGRESS_SIGNALS if s in text_lower)

        if reversal_score > 0:
            return "REVERSAL"
        elif delay_score > progress_score:
            return "DELAY"
        elif progress_score > 0:
            return "PROGRESS"
        else:
            return "UNRELATED"

    def extract_percent_complete(self, text: str) -> float | None:
        """Extract cage-free completion percentage from text if present."""
        patterns = [
            r"(\d+(?:\.\d+)?)\s*%\s*cage.free",
            r"cage.free[:\s]+(\d+(?:\.\d+)?)\s*%",
            r"(\d+(?:\.\d+)?)\s*percent\s*cage.free",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def update_status_from_classification(
        self,
        commitment: WelfareCommitment,
        classification: str,
        percent_complete: float | None,
        source_url: str,
    ) -> WelfareCommitment:
        """Apply a classification result to a commitment, recording the status change."""
        from datetime import date

        new_status: CommitmentStatus | None = None
        if classification == "REVERSAL":
            new_status = CommitmentStatus.REVERSED
        elif classification == "DELAY":
            new_status = CommitmentStatus.DELAYED
        elif classification == "PROGRESS":
            if percent_complete and percent_complete >= 100.0:
                new_status = CommitmentStatus.COMPLETED
            else:
                new_status = CommitmentStatus.ON_TRACK

        if new_status and new_status != commitment.status:
            commitment.status_changes.append({
                "from": commitment.status.value,
                "to": new_status.value,
                "date": date.today().isoformat(),
                "source": source_url,
            })
            commitment.status = new_status

        if percent_complete is not None:
            commitment.percent_complete = percent_complete

        commitment.last_verified_date = date.today()
        commitment.verification_source = source_url

        return commitment
