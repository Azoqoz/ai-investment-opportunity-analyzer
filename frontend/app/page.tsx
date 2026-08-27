import { PageHeader } from "@/components/page-header";
import { SectionRule } from "@/components/section-rule";

const summaryItems = [
  { label: "Opportunities", value: "5,000", note: "Synthetic universe" },
  { label: "Avg Score", value: "51.67", note: "Investment score" },
  { label: "Avg Risk", value: "43.36", note: "Composite risk" },
  { label: "Invest", value: "845", note: "16.9% of universe" },
];

const sectorRanking = [
  ["Renewable Energy", "58.62"],
  ["Healthcare", "53.22"],
  ["Tourism", "53.04"],
  ["Technology", "52.07"],
  ["Infrastructure", "51.84"],
];

const regionRanking = [
  ["Makkah", "52.90"],
  ["Riyadh", "52.88"],
  ["Asir", "52.57"],
  ["Madinah", "51.22"],
  ["Tabuk", "51.18"],
];

export default function OverviewPage() {
  return (
    <div className="page-stack overview-page">
      <PageHeader
        eyebrow="Universe snapshot · Synthetic baseline"
        title="Investment Universe"
        description="Screening summary across decision outcomes, score bands, sectors, and regions."
        aside={
          <div className="as-of-block">
            <span>Workspace mode</span>
            <strong>Static research shell</strong>
          </div>
        }
      />

      <section className="summary-strip" aria-label="Portfolio summary">
        {summaryItems.map((item) => (
          <div className="summary-item" key={item.label}>
            <strong>{item.value}</strong>
            <span>{item.label}</span>
            <small>{item.note}</small>
          </div>
        ))}
      </section>

      <div className="terminal-grid terminal-grid-primary">
        <section className="terminal-panel recommendation-panel">
          <SectionRule title="Decision Distribution" note="Count / share of universe" />
          <div className="recommendation-shell" aria-label="Decision distribution">
            <div className="mix-row" style={{ "--mix-width": "37.8%" } as React.CSSProperties}>
              <span className="mix-marker mix-invest" />
              <span>Invest</span>
              <span className="mix-track"><i /></span>
              <strong>845</strong>
              <small>16.9%</small>
            </div>
            <div className="mix-row" style={{ "--mix-width": "100%" } as React.CSSProperties}>
              <span className="mix-marker mix-review" />
              <span>Review</span>
              <span className="mix-track"><i /></span>
              <strong>2,235</strong>
              <small>44.7%</small>
            </div>
            <div className="mix-row" style={{ "--mix-width": "85.9%" } as React.CSSProperties}>
              <span className="mix-marker mix-reject" />
              <span>Reject</span>
              <span className="mix-track"><i /></span>
              <strong>1,920</strong>
              <small>38.4%</small>
            </div>
          </div>
        </section>

        <section className="terminal-panel score-panel">
          <SectionRule title="Score Distribution" note="Five-point score bands" />
          <div className="distribution-shell" aria-label="Score distribution structure">
            <div className="distribution-field">
              {[18, 25, 33, 45, 58, 69, 78, 88, 96, 100, 92, 81, 68, 51, 35, 22, 14, 9, 5, 2].map(
                (height, index) => <span key={index} style={{ height: `${height}%` }} />,
              )}
            </div>
            <div className="distribution-axis">
              <span>0</span>
              <span>25</span>
              <span>50</span>
              <span>75</span>
              <span>100</span>
            </div>
          </div>
        </section>
      </div>

      <div className="terminal-grid terminal-grid-rankings">
        {[
          ["Sector Ranking", "Average investment score", sectorRanking],
          ["Region Ranking", "Average investment score", regionRanking],
        ].map(([title, note, rows]) => (
          <section className="terminal-panel ranking-panel" key={title as string}>
            <SectionRule title={title as string} note={note as string}>
              <span className="quiet-meta">TOP 5</span>
            </SectionRule>
            <div className="ranking-ledger">
              {(rows as string[][]).map(([label, value], index) => (
                <div className="ranking-row" key={label}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <strong>{label}</strong>
                  <i><b style={{ width: `${Number(value)}%` }} /></i>
                  <code>{value}</code>
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
