import React from "react";

interface SupplyChainPathway {
  commodity: string;
  region: string;
  commodity_weight: number;
  region_risk: number;
  pathway_score: number;
}

interface SupplyChainMapProps {
  company_name: string;
  overall_risk_score: number;
  confidence_score: number;
  pathways: SupplyChainPathway[];
  welfare_policy_reduction: number;
  notes: string[];
}

const COMMODITY_LABELS: Record<string, string> = {
  beef: "Beef",
  pork: "Pork",
  poultry: "Poultry",
  eggs: "Eggs",
  dairy: "Dairy",
  farmed_fish: "Farmed Fish",
  turkey: "Turkey",
};

function riskColor(score: number): string {
  if (score >= 80) return "#ef4444";
  if (score >= 60) return "#f97316";
  if (score >= 40) return "#f59e0b";
  return "#22c55e";
}

function riskLabel(score: number): string {
  if (score >= 80) return "Critical";
  if (score >= 60) return "High";
  if (score >= 40) return "Moderate";
  return "Lower";
}

export function SupplyChainMap({
  company_name,
  overall_risk_score,
  confidence_score,
  pathways,
  welfare_policy_reduction,
  notes,
}: SupplyChainMapProps): React.ReactElement {
  const color = riskColor(overall_risk_score);
  const label = riskLabel(overall_risk_score);

  return (
    <div style={{ fontFamily: "system-ui, sans-serif" }}>
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          marginBottom: 20,
          gap: 12,
        }}
      >
        <div>
          <h3 style={{ margin: 0, fontSize: 15, fontWeight: 600, color: "#0f172a" }}>
            Supply chain risk — {company_name}
          </h3>
          <p style={{ margin: "4px 0 0", fontSize: 12, color: "#64748b" }}>
            Animal agriculture sourcing exposure score
          </p>
        </div>
        <div style={{ textAlign: "right", flexShrink: 0 }}>
          <div style={{ fontSize: 32, fontWeight: 800, color, lineHeight: 1 }}>
            {overall_risk_score}
          </div>
          <div style={{ fontSize: 11, fontWeight: 600, color }}>{label.toUpperCase()} RISK</div>
          <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>
            Confidence: {confidence_score}/100
          </div>
        </div>
      </div>

      {/* Pathway table */}
      {pathways.length > 0 ? (
        <div>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              fontSize: 12,
            }}
          >
            <thead>
              <tr style={{ backgroundColor: "#f8fafc" }}>
                <th style={{ padding: "6px 10px", textAlign: "left", color: "#64748b", fontWeight: 600, borderBottom: "1px solid #e2e8f0" }}>
                  Commodity
                </th>
                <th style={{ padding: "6px 10px", textAlign: "left", color: "#64748b", fontWeight: 600, borderBottom: "1px solid #e2e8f0" }}>
                  Region
                </th>
                <th style={{ padding: "6px 10px", textAlign: "right", color: "#64748b", fontWeight: 600, borderBottom: "1px solid #e2e8f0" }}>
                  Risk Score
                </th>
              </tr>
            </thead>
            <tbody>
              {[...pathways]
                .sort((a, b) => b.pathway_score - a.pathway_score)
                .map((p) => (
                  <tr key={`${p.commodity}-${p.region}`}>
                    <td style={{ padding: "6px 10px", borderBottom: "1px solid #f1f5f9", color: "#334155" }}>
                      {COMMODITY_LABELS[p.commodity] || p.commodity}
                    </td>
                    <td style={{ padding: "6px 10px", borderBottom: "1px solid #f1f5f9", color: "#334155" }}>
                      {p.region}
                    </td>
                    <td
                      style={{
                        padding: "6px 10px",
                        borderBottom: "1px solid #f1f5f9",
                        textAlign: "right",
                        fontWeight: 700,
                        color: riskColor(p.pathway_score),
                      }}
                    >
                      {p.pathway_score}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>

          {welfare_policy_reduction > 0 && (
            <p style={{ fontSize: 11, color: "#22c55e", marginTop: 8 }}>
              Score reduced by {welfare_policy_reduction} points for third-party welfare audit coverage.
            </p>
          )}
        </div>
      ) : (
        <p style={{ fontSize: 13, color: "#94a3b8", textAlign: "center", padding: "20px 0" }}>
          No sourcing pathway data available.
        </p>
      )}

      {notes.length > 0 && (
        <ul style={{ marginTop: 12, paddingLeft: 16 }}>
          {notes.map((note, i) => (
            <li key={i} style={{ fontSize: 11, color: "#64748b", marginBottom: 4 }}>
              {note}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
