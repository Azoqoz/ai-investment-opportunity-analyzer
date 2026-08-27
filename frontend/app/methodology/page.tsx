import type { Metadata } from "next";

import { PageHeader } from "@/components/page-header";
import { SectionRule } from "@/components/section-rule";

export const metadata: Metadata = {
  title: "Methodology",
  description: "Technical model documentation for the synthetic investment research workstation.",
};

const contractRows = [
  ["Public input", "10 simplified fields", "Sector, region, finance, market, strategy"],
  ["Raw feature frame", "38 fields", "Generated in trained column order"],
  ["Transformed frame", "56 features", "Numerical scaling + categorical encoding"],
  ["Estimator", "Ridge Regression", "Saved scikit-learn 1.8.0 artifact"],
];

export default function MethodologyPage() {
  return (
    <div className="page-stack methodology-page">
      <PageHeader
        eyebrow="Technical documentation · Baseline contract"
        title="Model Methodology"
        description="System boundaries, feature contract, recommendation semantics, and interpretation limits."
        aside={<div className="as-of-block"><span>Document state</span><strong>Phase 4 shell</strong></div>}
      />

      <div className="method-terminal-grid">
        <section className="terminal-panel method-model-panel">
          <SectionRule title="Model" note="Current saved estimator" />
          <div className="model-identity">
            <span>Estimator</span><strong>Ridge Regression</strong>
            <span>Artifact runtime</span><code>scikit-learn 1.8.0</code>
            <span>Output</span><code>0.00 — 100.00</code>
          </div>
        </section>

        <section className="terminal-panel method-data-panel">
          <SectionRule title="Data" note="Research universe" />
          <div className="data-readout"><strong>5,000</strong><span>Synthetic opportunities</span></div>
          <div className="data-readout-secondary"><span>Stored evaluations</span><code>845 / 2,235 / 1,920</code></div>
        </section>
      </div>

      <section className="terminal-panel contract-panel">
        <SectionRule title="Input Contract" note="Validated transformation path" />
        <div className="contract-table" role="table" aria-label="Model input contract">
          <div className="contract-head" role="row"><span>Stage</span><span>Shape</span><span>Contract</span></div>
          {contractRows.map(([stage, shape, detail]) => (
            <div className="contract-row" role="row" key={stage}>
              <strong>{stage}</strong><code>{shape}</code><span>{detail}</span>
            </div>
          ))}
        </div>
      </section>

      <div className="method-terminal-grid method-bottom-grid">
        <section className="terminal-panel thresholds-panel">
          <SectionRule title="Thresholds" note="Canonical decision assignment" />
          <div className="threshold-ledger">
            <div><i className="threshold-invest" /><strong>Invest</strong><code>score ≥ 75.00</code></div>
            <div><i className="threshold-review" /><strong>Review</strong><code>45.00 — 74.99</code></div>
            <div><i className="threshold-reject" /><strong>Reject</strong><code>score &lt; 45.00</code></div>
          </div>
        </section>

        <section className="terminal-panel limitations-panel">
          <SectionRule title="Limitations" note="Interpretation controls" />
          <ul>
            <li><span>01</span>Synthetic target and opportunity records</li>
            <li><span>02</span>Educational and portfolio demonstration only</li>
            <li><span>03</span>Model contributions do not establish causation</li>
            <li><span>04</span>Not financial advice or a real-outcome forecast</li>
          </ul>
        </section>
      </div>

      <aside className="terminal-disclaimer">
        <span>Use constraint</span>
        <p>This project uses synthetic data for educational and portfolio purposes. It does not predict real investment outcomes and is not financial advice.</p>
      </aside>
    </div>
  );
}
