"""
Supply chain risk scoring for animal agriculture sourcing.

Adapted from EcoTrace-Risk-Engine's deterministic commodity/region risk matrix.
Scores a company's animal ag supply chain exposure based on:
  - Commodity base weights (beef, pork, poultry, eggs, dairy)
  - Regional risk tiers (factory farming intensity by country)
  - Welfare policy score reduction for verified third-party audits

All commodity weights encode the scale of farmed animal suffering, not
environmental metrics. A score of 100 means maximum factory farm exposure.
"""
from dataclasses import dataclass
from typing import Optional


# Commodity base weights (0.0–1.0)
# Higher = greater factory farm exposure at industrial scale
COMMODITY_WEIGHTS: dict[str, float] = {
    "beef": 0.88,         # Feedlots, slaughterhouse scale
    "pork": 0.95,         # Gestation crates, extreme confinement
    "poultry": 0.97,      # Battery cages, broiler density conditions
    "eggs": 0.96,         # Battery cage systems still dominant globally
    "dairy": 0.82,        # Separation of calves, veal linkage
    "farmed_fish": 0.78,  # Net pen density, high mortality rates
    "turkey": 0.90,       # Industrial breeding, high welfare risk
}

# Regional risk tiers (0.0–1.0)
# Based on factory farming intensity, welfare regulation weakness, enforcement gaps
REGION_RISK_TIERS: dict[str, float] = {
    # Critical — minimal welfare regulation, high factory farm density
    "BR": 0.95,  # Brazil
    "CN": 0.95,  # China
    "VN": 0.92,  # Vietnam
    "TH": 0.90,  # Thailand
    "ID": 0.90,  # Indonesia
    "IN": 0.88,  # India
    "MX": 0.85,  # Mexico
    # High — some regulation, weak enforcement
    "US": 0.75,  # USA — ag-gag laws, limited federal farmed animal protections
    "CA": 0.65,  # Canada
    "AU": 0.65,  # Australia
    # Moderate — more regulation, inconsistent enforcement
    "AR": 0.72,  # Argentina
    "PL": 0.68,  # Poland
    "DE": 0.55,  # Germany
    "FR": 0.55,  # France
    "GB": 0.50,  # UK
    # Lower risk — stronger welfare frameworks
    "SE": 0.35,  # Sweden
    "NO": 0.35,  # Norway
    "NL": 0.40,  # Netherlands
    "CH": 0.38,  # Switzerland
}

DEFAULT_REGION_RISK = 0.70  # Unknown region defaults to high risk


@dataclass
class SupplyChainRiskResult:
    """Result of a supply chain risk assessment."""
    company_id: str
    company_name: str
    overall_risk_score: float   # 0–100
    confidence_score: float     # 0–100 — how much data backs this score
    pathways: list[dict]        # Individual commodity/region risk vectors
    welfare_policy_reduction: float  # Points deducted for third-party audit coverage
    notes: list[str]            # Human-readable explanation fragments


class SupplyChainRiskScorer:
    """
    Scores a company's animal agriculture supply chain risk.

    Final score pulls toward highest-risk pathway (same aggregation as EcoTrace)
    to prevent companies from masking factory farm exposure with low-risk sourcing.
    Third-party audit coverage provides a score reduction.
    """

    def score(
        self,
        company_id: str,
        company_name: str,
        sourcing_vectors: list[dict],  # [{"commodity": "eggs", "regions": ["US", "CN"]}]
        has_third_party_audit: bool = False,
        audit_coverage_pct: float = 0.0,  # 0–100
    ) -> SupplyChainRiskResult:
        """
        Score supply chain risk from known sourcing vectors.

        sourcing_vectors: list of dicts with "commodity" and "regions" keys.
        has_third_party_audit: True if company has any third-party welfare audit.
        audit_coverage_pct: what % of supply chain is covered by that audit.
        """
        pathways: list[dict] = []
        notes: list[str] = []

        for vector in sourcing_vectors:
            commodity = vector.get("commodity", "").lower()
            regions = vector.get("regions", [])

            commodity_weight = COMMODITY_WEIGHTS.get(commodity)
            if commodity_weight is None:
                notes.append(f"Unknown commodity '{commodity}' skipped — verify against domain dictionary")
                continue

            for region in regions:
                region_risk = REGION_RISK_TIERS.get(region.upper(), DEFAULT_REGION_RISK)
                pathway_score = commodity_weight * region_risk * 100

                pathways.append({
                    "commodity": commodity,
                    "region": region.upper(),
                    "commodity_weight": commodity_weight,
                    "region_risk": region_risk,
                    "pathway_score": round(pathway_score, 1),
                })

        if not pathways:
            return SupplyChainRiskResult(
                company_id=company_id,
                company_name=company_name,
                overall_risk_score=0.0,
                confidence_score=0.0,
                pathways=[],
                welfare_policy_reduction=0.0,
                notes=notes + ["No valid sourcing vectors found — score is 0 but confidence is 0"],
            )

        pathway_scores = [p["pathway_score"] for p in pathways]
        max_score = max(pathway_scores)
        mean_score = sum(pathway_scores) / len(pathway_scores)

        # Weighted toward max to prevent greenwashing via low-risk sourcing dilution
        overall_risk = (max_score * 0.6) + (mean_score * 0.4)

        # Welfare policy score reduction for verified third-party audits
        welfare_reduction = 0.0
        if has_third_party_audit and audit_coverage_pct > 0:
            welfare_reduction = min(15.0, (audit_coverage_pct / 100) * 15.0)
            notes.append(
                f"Third-party audit covers {audit_coverage_pct:.0f}% of supply chain "
                f"(score reduced by {welfare_reduction:.1f} points)"
            )

        final_score = max(0.0, overall_risk - welfare_reduction)

        confidence = _compute_confidence(sourcing_vectors, pathways)

        return SupplyChainRiskResult(
            company_id=company_id,
            company_name=company_name,
            overall_risk_score=round(final_score, 1),
            confidence_score=round(confidence, 1),
            pathways=pathways,
            welfare_policy_reduction=round(welfare_reduction, 1),
            notes=notes,
        )


def _compute_confidence(sourcing_vectors: list[dict], pathways: list[dict]) -> float:
    """
    Estimate confidence based on data density.
    More sourcing vectors with known regions = higher confidence.
    """
    if not sourcing_vectors:
        return 0.0
    vectors_with_regions = sum(
        1 for v in sourcing_vectors if v.get("regions")
    )
    known_commodities = sum(
        1 for p in pathways if p["commodity_weight"] > 0
    )
    base = (vectors_with_regions / max(len(sourcing_vectors), 1)) * 60
    density_bonus = min(40, known_commodities * 5)
    return min(100.0, base + density_bonus)
