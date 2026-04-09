import React, { useEffect, useState } from "react";
import { ScoreCard } from "../components/ScoreCard";

interface CompanyListItem {
  company_id: string;
  name: string;
  domain: string;
  sector: string;
  revenue_tier: string;
  overall_score: number;
  score_label: string;
  commitment_count: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function HomePage(): React.ReactElement {
  const [query, setQuery] = useState("");
  const [companies, setCompanies] = useState<CompanyListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    const url = query.trim()
      ? `${API_BASE}/companies?q=${encodeURIComponent(query.trim())}`
      : `${API_BASE}/companies`;

    fetch(url, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        return res.json();
      })
      .then((data: CompanyListItem[]) => {
        setCompanies(data);
        setLoading(false);
      })
      .catch((err) => {
        if (err.name !== "AbortError") {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, [query]);

  return (
    <main
      style={{
        fontFamily: "system-ui, sans-serif",
        maxWidth: 900,
        margin: "0 auto",
        padding: "32px 16px",
      }}
    >
      <header style={{ marginBottom: 32 }}>
        <h1 style={{ margin: 0, fontSize: 28, fontWeight: 800, color: "#0f172a" }}>
          Corporate Watch
        </h1>
        <p style={{ margin: "8px 0 0", fontSize: 15, color: "#475569" }}>
          Tracking whether companies follow through on animal welfare commitments.
        </p>
      </header>

      <div style={{ marginBottom: 24 }}>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search companies (e.g. McDonald's, Walmart)"
          style={{
            width: "100%",
            padding: "10px 14px",
            fontSize: 15,
            border: "1px solid #cbd5e1",
            borderRadius: 6,
            outline: "none",
            boxSizing: "border-box",
          }}
          aria-label="Search companies"
        />
      </div>

      {error && (
        <div
          role="alert"
          style={{
            padding: "12px 16px",
            backgroundColor: "#fef2f2",
            border: "1px solid #fecaca",
            borderRadius: 6,
            color: "#dc2626",
            marginBottom: 24,
          }}
        >
          Could not load company data: {error}
        </div>
      )}

      {loading ? (
        <p style={{ color: "#94a3b8" }}>Loading companies...</p>
      ) : companies.length === 0 ? (
        <p style={{ color: "#94a3b8" }}>No companies found matching your search.</p>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
            gap: 20,
          }}
        >
          {companies.map((company) => (
            <a
              key={company.company_id}
              href={`/company/${company.company_id}`}
              style={{ textDecoration: "none" }}
            >
              <div
                style={{
                  border: "1px solid #e2e8f0",
                  borderRadius: 8,
                  padding: "16px 20px",
                  backgroundColor: "#fff",
                  cursor: "pointer",
                  transition: "box-shadow 0.15s",
                }}
                onMouseEnter={(e) =>
                  ((e.currentTarget as HTMLDivElement).style.boxShadow =
                    "0 2px 12px rgba(0,0,0,0.08)")
                }
                onMouseLeave={(e) =>
                  ((e.currentTarget as HTMLDivElement).style.boxShadow = "none")
                }
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 16, color: "#0f172a" }}>
                      {company.name}
                    </div>
                    <div
                      style={{
                        fontSize: 12,
                        color: "#64748b",
                        marginTop: 2,
                        textTransform: "capitalize",
                      }}
                    >
                      {company.sector} · {company.revenue_tier}
                    </div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div
                      style={{
                        fontSize: 24,
                        fontWeight: 800,
                        color: scoreColor(company.overall_score),
                        lineHeight: 1,
                      }}
                    >
                      {company.overall_score}
                    </div>
                    <div
                      style={{
                        fontSize: 10,
                        fontWeight: 600,
                        color: scoreColor(company.overall_score),
                      }}
                    >
                      {company.score_label.toUpperCase()}
                    </div>
                  </div>
                </div>
                <div style={{ marginTop: 10, fontSize: 12, color: "#94a3b8" }}>
                  {company.commitment_count} commitment{company.commitment_count !== 1 ? "s" : ""} tracked
                </div>
              </div>
            </a>
          ))}
        </div>
      )}
    </main>
  );
}

function scoreColor(score: number): string {
  if (score >= 80) return "#22c55e";
  if (score >= 60) return "#84cc16";
  if (score >= 40) return "#f97316";
  if (score >= 20) return "#ef4444";
  return "#7f1d1d";
}
