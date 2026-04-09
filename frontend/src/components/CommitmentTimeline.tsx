import React from "react";

export interface TimelineCommitment {
  commitment_id: string;
  category: string;
  description: string;
  status: string;
  percent_complete: number | null;
  target_date: string | null;
  announced_date: string | null;
}

interface CommitmentTimelineProps {
  commitments: TimelineCommitment[];
  company_name: string;
}

const STATUS_CONFIG: Record<string, { color: string; label: string }> = {
  COMPLETED: { color: "#22c55e", label: "Completed" },
  ON_TRACK: { color: "#84cc16", label: "On Track" },
  DELAYED: { color: "#f97316", label: "Delayed" },
  REVERSED: { color: "#ef4444", label: "Reversed" },
  UNVERIFIED: { color: "#94a3b8", label: "Unverified" },
};

const CATEGORY_LABELS: Record<string, string> = {
  CAGE_FREE: "Cage-Free Eggs",
  GESTATION_CRATE_FREE: "Gestation Crate-Free Pork",
  ANTIBIOTIC_REDUCTION: "Antibiotic Reduction",
  SLAUGHTER_METHOD: "Higher-Welfare Slaughter",
  TRANSPORT: "Transport Conditions",
  THIRD_PARTY_AUDIT: "Third-Party Audit",
};

function formatYear(dateStr: string | null): string {
  if (!dateStr) return "—";
  return new Date(dateStr).getFullYear().toString();
}

export function CommitmentTimeline({
  commitments,
  company_name,
}: CommitmentTimelineProps): React.ReactElement {
  const currentYear = new Date().getFullYear();

  // Compute year range across all commitment dates
  const allYears = commitments.flatMap((c) => {
    const years: number[] = [];
    if (c.announced_date) years.push(new Date(c.announced_date).getFullYear());
    if (c.target_date) years.push(new Date(c.target_date).getFullYear());
    return years;
  });

  const minYear = allYears.length ? Math.min(...allYears) : currentYear - 2;
  const maxYear = allYears.length ? Math.max(...allYears, currentYear) : currentYear + 2;
  const yearSpan = maxYear - minYear;

  function xPercent(year: number): string {
    return `${Math.max(0, Math.min(100, ((year - minYear) / yearSpan) * 100))}%`;
  }

  return (
    <div style={{ fontFamily: "system-ui, sans-serif", padding: "8px 0" }}>
      <h3 style={{ margin: "0 0 20px", fontSize: 15, fontWeight: 600, color: "#0f172a" }}>
        Commitment timeline — {company_name}
      </h3>

      {/* Year axis */}
      <div
        style={{
          position: "relative",
          height: 24,
          marginBottom: 16,
          marginLeft: 160,
          marginRight: 16,
        }}
      >
        {Array.from({ length: yearSpan + 1 }, (_, i) => minYear + i).map((year) => (
          <div
            key={year}
            style={{
              position: "absolute",
              left: xPercent(year),
              transform: "translateX(-50%)",
              fontSize: 11,
              color: year === currentYear ? "#6366f1" : "#94a3b8",
              fontWeight: year === currentYear ? 700 : 400,
            }}
          >
            {year}
          </div>
        ))}
        {/* Current year marker */}
        <div
          style={{
            position: "absolute",
            left: xPercent(currentYear),
            top: 16,
            bottom: 0,
            width: 2,
            backgroundColor: "#6366f133",
          }}
        />
      </div>

      {/* Commitment rows */}
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {commitments.map((c) => {
          const cfg = STATUS_CONFIG[c.status] || STATUS_CONFIG.UNVERIFIED;
          const startYear = c.announced_date
            ? new Date(c.announced_date).getFullYear()
            : minYear;
          const endYear = c.target_date
            ? new Date(c.target_date).getFullYear()
            : currentYear;

          const barLeft = xPercent(startYear);
          const barWidth = `${Math.max(2, ((endYear - startYear) / yearSpan) * 100)}%`;

          return (
            <div
              key={c.commitment_id}
              style={{ display: "flex", alignItems: "center", gap: 8 }}
            >
              {/* Label */}
              <div
                style={{
                  width: 152,
                  flexShrink: 0,
                  fontSize: 12,
                  color: "#334155",
                  textAlign: "right",
                  paddingRight: 8,
                  lineHeight: 1.3,
                }}
              >
                {CATEGORY_LABELS[c.category] || c.category}
              </div>

              {/* Bar area */}
              <div style={{ flex: 1, position: "relative", height: 28 }}>
                <div
                  style={{
                    position: "absolute",
                    left: barLeft,
                    width: barWidth,
                    top: 4,
                    height: 20,
                    backgroundColor: cfg.color,
                    borderRadius: 4,
                    opacity: 0.85,
                    display: "flex",
                    alignItems: "center",
                    paddingLeft: 6,
                    minWidth: 8,
                    overflow: "hidden",
                  }}
                  title={c.description}
                >
                  {c.percent_complete != null && (
                    <span style={{ fontSize: 10, color: "#fff", fontWeight: 600, whiteSpace: "nowrap" }}>
                      {c.percent_complete}%
                    </span>
                  )}
                </div>

                {/* Deadline marker */}
                {c.target_date && (
                  <div
                    style={{
                      position: "absolute",
                      left: xPercent(endYear),
                      top: 0,
                      height: 28,
                      width: 2,
                      backgroundColor: cfg.color,
                      opacity: 0.5,
                    }}
                    title={`Deadline: ${c.target_date}`}
                  />
                )}
              </div>

              {/* Status badge */}
              <div
                style={{
                  flexShrink: 0,
                  fontSize: 10,
                  fontWeight: 600,
                  color: cfg.color,
                  backgroundColor: `${cfg.color}1a`,
                  padding: "2px 6px",
                  borderRadius: 4,
                  width: 70,
                  textAlign: "center",
                }}
              >
                {cfg.label.toUpperCase()}
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div style={{ display: "flex", gap: 16, marginTop: 20, flexWrap: "wrap" }}>
        {Object.entries(STATUS_CONFIG).map(([key, val]) => (
          <div key={key} style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: 2,
                backgroundColor: val.color,
                opacity: 0.85,
              }}
            />
            <span style={{ fontSize: 11, color: "#64748b" }}>{val.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
