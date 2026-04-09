import React, { useEffect, useState } from "react";
import { ScoreCard } from "../../components/ScoreCard";
import { CommitmentTimeline } from "../../components/CommitmentTimeline";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Scorecard {
  company_id: string;
  company_name: string;
  sector: string;
  overall_score: number;
  score_label: string;
  total_commitments: number;
  commitments_completed: number;
  commitments_on_track: number;
  commitments_delayed: number;
  commitments_reversed: number;
  commitments_unverified: number;
  by_category: Record<string, {
    status: string;
    percent_complete: number | null;
    target_date: string | null;
    description: string;
  }>;
  commitment_detail: Array<{
    commitment_id: string;
    category: string;
    description: string;
    status: string;
    percent_complete: number | null;
    target_date: string | null;
    announced_date: string | null;
    last_verified_date: string | null;
    verification_source: string | null;
    original_announcement_url: string | null;
    status_changes: Array<{ from: string; to: string; date: string; source: string }>;
  }>;
}

export default function CompanyPage(): React.ReactElement {
  const [scorecard, setScorecard] = useState<Scorecard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Extract company ID from path in a Next.js-compatible way
    const pathParts = window.location.pathname.split("/");
    const companyId = pathParts[pathParts.length - 1];
    if (!companyId) return;

    fetch(`${API_BASE}/companies/${companyId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Company not found (${res.status})`);
        return res.json();
      })
      .then((data: Scorecard) => {
        setScorecard(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <main style={{ fontFamily: "system-ui, sans-serif", maxWidth: 760, margin: "0 auto", padding: "48px 16px" }}>
        <p style={{ color: "#94a3b8" }}>Loading...</p>
      </main>
    );
  }

  if (error || !scorecard) {
    return (
      <main style={{ fontFamily: "system-ui, sans-serif", maxWidth: 760, margin: "0 auto", padding: "48px 16px" }}>
        <p role="alert" style={{ color: "#dc2626" }}>
          {error || "Company not found."}
        </p>
        <a href="/" style={{ color: "#6366f1" }}>Back to all companies</a>
      </main>
    );
  }

  return (
    <main
      style={{
        fontFamily: "system-ui, sans-serif",
        maxWidth: 760,
        margin: "0 auto",
        padding: "32px 16px",
      }}
    >
      <nav style={{ marginBottom: 20 }}>
        <a href="/" style={{ fontSize: 13, color: "#6366f1", textDecoration: "none" }}>
          ← All companies
        </a>
      </nav>

      {/* Scorecard */}
      <section style={{ marginBottom: 32 }}>
        <ScoreCard
          company_id={scorecard.company_id}
          company_name={scorecard.company_name}
          sector={scorecard.sector}
          overall_score={scorecard.overall_score}
          score_label={scorecard.score_label}
          total_commitments={scorecard.total_commitments}
          commitments_completed={scorecard.commitments_completed}
          commitments_on_track={scorecard.commitments_on_track}
          commitments_delayed={scorecard.commitments_delayed}
          commitments_reversed={scorecard.commitments_reversed}
          by_category={scorecard.by_category}
        />
      </section>

      {/* Timeline */}
      <section
        style={{
          border: "1px solid #e2e8f0",
          borderRadius: 8,
          padding: "20px 24px",
          backgroundColor: "#fff",
          marginBottom: 32,
          overflowX: "auto",
        }}
      >
        <CommitmentTimeline
          company_name={scorecard.company_name}
          commitments={scorecard.commitment_detail.map((c) => ({
            commitment_id: c.commitment_id,
            category: c.category,
            description: c.description,
            status: c.status,
            percent_complete: c.percent_complete,
            target_date: c.target_date,
            announced_date: c.announced_date,
          }))}
        />
      </section>

      {/* Commitment detail cards */}
      <section>
        <h2 style={{ fontSize: 17, fontWeight: 700, color: "#0f172a", marginBottom: 16 }}>
          All commitments
        </h2>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {scorecard.commitment_detail.map((c) => (
            <div
              key={c.commitment_id}
              style={{
                border: "1px solid #e2e8f0",
                borderRadius: 6,
                padding: "14px 16px",
                backgroundColor: "#fff",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: "#6366f1", marginBottom: 4 }}>
                    {c.category.replace(/_/g, " ")}
                  </div>
                  <div style={{ fontSize: 14, color: "#0f172a", lineHeight: 1.5 }}>
                    {c.description}
                  </div>
                </div>
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: statusColor(c.status),
                    backgroundColor: `${statusColor(c.status)}1a`,
                    padding: "3px 8px",
                    borderRadius: 4,
                    flexShrink: 0,
                  }}
                >
                  {c.status.replace(/_/g, " ")}
                </span>
              </div>

              <div
                style={{
                  display: "flex",
                  gap: 16,
                  marginTop: 10,
                  fontSize: 11,
                  color: "#64748b",
                  flexWrap: "wrap",
                }}
              >
                {c.announced_date && <span>Announced: {c.announced_date}</span>}
                {c.target_date && <span>Target: {c.target_date}</span>}
                {c.percent_complete != null && (
                  <span style={{ fontWeight: 600, color: statusColor(c.status) }}>
                    {c.percent_complete}% complete
                  </span>
                )}
                {c.last_verified_date && <span>Last verified: {c.last_verified_date}</span>}
              </div>

              {c.original_announcement_url && (
                <a
                  href={c.original_announcement_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ display: "block", marginTop: 6, fontSize: 11, color: "#6366f1" }}
                >
                  Original announcement
                </a>
              )}

              {c.status_changes.length > 0 && (
                <details style={{ marginTop: 8 }}>
                  <summary style={{ fontSize: 11, color: "#64748b", cursor: "pointer" }}>
                    {c.status_changes.length} status change{c.status_changes.length !== 1 ? "s" : ""}
                  </summary>
                  <ul style={{ margin: "6px 0 0", paddingLeft: 16 }}>
                    {c.status_changes.map((ch, i) => (
                      <li key={i} style={{ fontSize: 11, color: "#475569", marginBottom: 4 }}>
                        {ch.date}: {ch.from} → {ch.to}
                        {ch.source && (
                          <a href={ch.source} target="_blank" rel="noopener noreferrer" style={{ marginLeft: 6, color: "#6366f1" }}>
                            source
                          </a>
                        )}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

function statusColor(status: string): string {
  const map: Record<string, string> = {
    COMPLETED: "#22c55e",
    ON_TRACK: "#84cc16",
    DELAYED: "#f97316",
    REVERSED: "#ef4444",
    UNVERIFIED: "#94a3b8",
  };
  return map[status] || "#94a3b8";
}
