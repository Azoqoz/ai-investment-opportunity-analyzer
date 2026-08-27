import type { Metadata } from "next";
import Link from "next/link";

import { SectionRule } from "@/components/section-rule";
import { StatusLabel } from "@/components/status-label";

type DetailPageProps = {
  params: Promise<{ id: string }>;
};

export async function generateMetadata({ params }: DetailPageProps): Promise<Metadata> {
  const { id } = await params;
  return {
    title: `Opportunity ${id}`,
    description: `Static research layout for synthetic opportunity ${id}.`,
  };
}

const financials = [
  { label: "Investment Size", value: "163.15", unit: "SAR M" },
  { label: "Expected ROI", value: "14.29", unit: "%" },
  { label: "Payback", value: "11.70", unit: "years" },
  { label: "Profit Margin", value: "8.15", unit: "%" },
];

const factors = [
  { label: "Overall Risk", value: 48.96, tone: "risk" },
  { label: "Strategic Impact", value: 81.17, tone: "positive" },
  { label: "Sustainability", value: 77.54, tone: "positive" },
  { label: "Market Attractiveness", value: 58.8, tone: "neutral" },
  { label: "Financial Strength", value: 40.56, tone: "neutral" },
];

const selectedMetrics = [
  ["IRR", "17.19%"],
  ["NPV", "SAR 37.19M"],
  ["Market Size", "SAR 9.97B"],
  ["Demand Score", "81.65"],
  ["Scalability", "68.94"],
  ["Competition", "Low"],
];

export default async function OpportunityDetailPage({ params }: DetailPageProps) {
  const { id } = await params;

  return (
    <div className="page-stack detail-page">
      <Link className="back-link" href="/opportunities">← Back to opportunity set</Link>

      <header className="detail-header">
        <div>
          <span className="eyebrow">Deal analysis · Synthetic record</span>
          <h1>Tabuk Technology Opportunity</h1>
          <p>{id} <span aria-hidden="true">·</span> Technology <span aria-hidden="true">·</span> Tabuk</p>
        </div>
        <div className="decision-lockup">
          <span>Synthetic Opportunity Score</span>
          <strong>80.10</strong>
          <StatusLabel tone="invest">Invest</StatusLabel>
        </div>
      </header>

      <p className="preview-notice">Static dataset baseline · Display shell only · No API request</p>

      <div className="detail-grid">
      <section className="terminal-panel detail-panel">
        <SectionRule title="Financial" note="Core opportunity economics" />
        <div className="financial-ledger">
          {financials.map((item) => (
            <div className="financial-line" key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              <small>{item.unit}</small>
            </div>
          ))}
        </div>
      </section>

      <section className="terminal-panel detail-panel factor-section">
        <SectionRule
          title="Risk & Quality"
          note="Stored synthetic evaluation"
        >
          <span className="scale-key">0 <i /> 100</span>
        </SectionRule>
        <div className="factor-ledger">
          {factors.map((factor) => (
            <div className="factor-line" key={factor.label}>
              <span>{factor.label}</span>
              <div className="factor-track">
                <i className={`factor-fill factor-${factor.tone}`} style={{ width: `${factor.value}%` }} />
              </div>
              <strong>{factor.value.toFixed(2)}</strong>
            </div>
          ))}
        </div>
      </section>
      </div>

      <section className="terminal-panel raw-metrics-panel">
        <SectionRule title="Selected Opportunity Data" note="Stored raw fields" />
        <div className="raw-metrics-grid">
          {selectedMetrics.map(([label, value]) => (
            <div key={label}><span>{label}</span><strong>{value}</strong></div>
          ))}
        </div>
      </section>

      <footer className="detail-footnote">
        <span>Score semantics</span>
        <p>
          Stored dataset scores and model predictions will remain explicitly separated when live data is connected in a later phase.
        </p>
      </footer>
    </div>
  );
}
