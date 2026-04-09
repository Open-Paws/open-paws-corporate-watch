import React from "react";

interface CategoryStatus {
  status: string;
  percent_complete: number | null;
  target_date: string | null;
  description: string;
}

interface ScoreCardProps {
  company_id: string;
  company_name: string;
  sector?: string;
  overall_score: number;
  score_label: string;
  total_commitments: number;
  commitments_completed: number;
  commitments_on_track: number;
  commitments_delayed: number;
  commitments_reversed: number;
  commitments_unverified?: number;
  by_category: Record<string, CategoryStatus>;
  show_share_button?: boolean;
}

const STATUS_COLORS: Record<string, string> = {
  COMPLETED: "#22c55e",
  ON_TRACK: "#84cc16",
  DELAYED: "#f97316",
  REVERSED: "#ef4444",
  UNVERIFIED: "#94a3b8",
};

const CATEGORY_LABELS: Record<string, string> = {
  CAGE_FREE: "Cage-Free Eggs",
  GESTATION_CRATE_FREE: "Gestation Crate-Free Pork",
  ANTIBIOTIC_REDUCTION: "Antibiotic Reduction",
  SLAUGHTER_METHOD: "Higher-Welfare Slaughter",
  TRANSPORT: "Transport Conditions",
  THIRD_PARTY_AUDIT: "Third-Party Audit",
};

function scoreToColor(score: number): string {
  if (score >= 80) return "#22c55e";
  if (score >= 60) return "#84cc16";
  if (score >= 40) return "#f97316";
  if (score >= 20) return "#ef4444";
  return "#7f1d1d";
}

export function ScoreCard({
  company_id,
  company_name,
  sector,
  overall_score,
  score_label,
  total_commitments,
  commitments_completed,
  commitments_on_track,
  commitments_delayed,
  commitments_reversed,
  by_category,
  show_share_button = true,
}: ScoreCardProps): React.ReactElement {
  const scoreColor = scoreToColor(overall_score);

  const handleShare = () => {
    const url = `${window.location.origin}/company/${company_id}`;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(url);
    }
  };

  return (
    <div
      style={{
        fontFamily: "system-ui, sans-serif",
        maxWidth: 480,
        border: "1px solid #e2e8f0",
        borderRadius: 8,
        overflow: "hidden",
        backgroundColor: "#fff",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "20px 24px 16px",
          borderBottom: "1px solid #e2e8f0",
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: 12,
        }}
      >
        <div>
          <h2 style={{ margin: 0, fontSize: 20, fontWeight: 700, color: "#0f172a" }}>
            {company_name}
          </h2>
          {sector && (
            <p style={{ margin: "4px 0 0", fontSize: 13, color: "#64748b", textTransform: "capitalize" }}>
              {sector}
            </p>
          )}
        </div>
        <div style={{ textAlign: "right", flexShrink: 0 }}>
          <div
            style={{
              fontSize: 36,
              fontWeight: 800,
              lineHeight: 1,
              color: scoreColor,
            }}
          >
            {overall_score}
          </div>
          <div
            style={{
              fontSize: 12,
              fontWeight: 600,
              color: scoreColor,
              marginTop: 2,
            }}
          >
            {score_label.toUpperCase()}
          </div>
          <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 2 }}>/ 100</div>
        </div>
      </div>

      {/* Commitment summary row */}
      <div
        style={{
          display: "flex",
          padding: "12px 24px",
          gap: 16,
          borderBottom: "1px solid #e2e8f0",
          backgroundColor: "#f8fafc",
        }}
      >
        {[
          { label: "Completed", count: commitments_completed, color: STATUS_COLORS.COMPLETED },
          { label: "On Track", count: commitments_on_track, color: STATUS_COLORS.ON_TRACK },
          { label: "Delayed", count: commitments_delayed, color: STATUS_COLORS.DELAYED },
          { label: "Reversed", count: commitments_reversed, color: STATUS_COLORS.REVERSED },
        ].map(({ label, count, color }) => (
          <div key={label} style={{ textAlign: "center", flex: 1 }}>
            <div style={{ fontSize: 20, fontWeight: 700, color }}>{count}</div>
            <div style={{ fontSize: 11, color: "#64748b" }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Category breakdown */}
      <div style={{ padding: "16px 24px" }}>
        <h3 style={{ margin: "0 0 12px", fontSize: 13, fontWeight: 600, color: "#475569", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          By Commitment Area
        </h3>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {Object.entries(by_category).map(([cat, data]) => (
            <div
              key={cat}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 8,
              }}
            >
              <span style={{ fontSize: 13, color: "#334155", flex: 1 }}>
                {CATEGORY_LABELS[cat] || cat}
              </span>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                {data.percent_complete != null && (
                  <span style={{ fontSize: 12, color: "#64748b" }}>
                    {data.percent_complete}%
                  </span>
                )}
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 600,
                    color: STATUS_COLORS[data.status] || "#94a3b8",
                    backgroundColor: `${STATUS_COLORS[data.status]}1a`,
                    padding: "2px 8px",
                    borderRadius: 4,
                  }}
                >
                  {data.status.replace("_", " ")}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div
        style={{
          padding: "12px 24px",
          borderTop: "1px solid #e2e8f0",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <span style={{ fontSize: 11, color: "#94a3b8" }}>
          {total_commitments} commitment{total_commitments !== 1 ? "s" : ""} tracked
        </span>
        {show_share_button && (
          <button
            onClick={handleShare}
            style={{
              fontSize: 12,
              color: "#6366f1",
              background: "none",
              border: "1px solid #e0e7ff",
              borderRadius: 4,
              padding: "4px 10px",
              cursor: "pointer",
            }}
          >
            Share scorecard
          </button>
        )}
      </div>
    </div>
  );
}
