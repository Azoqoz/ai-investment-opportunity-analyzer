import type { Metadata } from "next";

import { PageHeader } from "@/components/page-header";
import { SectionRule } from "@/components/section-rule";

export const metadata: Metadata = {
  title: "New Analysis",
  description: "Structure a simplified synthetic opportunity for future model evaluation.",
};

const levelOptions = ["Low", "Medium", "High"];

export default function NewAnalysisPage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Deal entry terminal · 10-field contract"
        title="New Analysis"
        description="Enter a simplified opportunity profile and review the evaluation-output structure."
        aside={
          <div className="as-of-block">
            <span>API state</span>
            <strong>Offline · Static output</strong>
          </div>
        }
      />

      <div className="analysis-layout">
        <form className="analysis-form">
          <fieldset className="form-section">
            <legend>Opportunity</legend>
            <p>Market position and operating context.</p>
            <div className="form-grid form-grid-three">
              <label className="field">
                <span>Sector</span>
                <select defaultValue="Technology">
                  <option>Technology</option>
                  <option>Renewable Energy</option>
                  <option>Healthcare</option>
                  <option>Infrastructure</option>
                  <option>Tourism</option>
                </select>
              </label>
              <label className="field">
                <span>Region</span>
                <select defaultValue="Riyadh">
                  <option>Riyadh</option>
                  <option>Eastern Province</option>
                  <option>Makkah</option>
                  <option>Tabuk</option>
                  <option>Asir</option>
                </select>
              </label>
              <label className="field">
                <span>Competition Level</span>
                <select defaultValue="Medium">
                  {levelOptions.map((level) => <option key={level}>{level}</option>)}
                </select>
              </label>
            </div>
          </fieldset>

          <fieldset className="form-section">
            <legend>Financial</legend>
            <p>Scale, return expectation, and capital recovery.</p>
            <div className="form-grid form-grid-three">
              <label className="field field-with-unit">
                <span>Investment Size</span>
                <div><input type="number" min="20" max="5000" defaultValue="250" /><small>SAR M</small></div>
              </label>
              <label className="field field-with-unit">
                <span>Expected ROI</span>
                <div><input type="number" min="-5" max="30" defaultValue="12" /><small>%</small></div>
              </label>
              <label className="field field-with-unit">
                <span>Payback Period</span>
                <div><input type="number" min="1" max="15" defaultValue="6" /><small>years</small></div>
              </label>
            </div>
          </fieldset>

          <fieldset className="form-section">
            <legend>Market</legend>
            <p>Qualitative demand and risk conditions.</p>
            <div className="form-grid form-grid-two">
              {[
                ["Market Demand", "Medium"],
                ["Risk Level", "Medium"],
              ].map(([label, defaultValue]) => (
                <label className="field" key={label}>
                  <span>{label}</span>
                  <select defaultValue={defaultValue}>
                    {levelOptions.map((level) => <option key={level}>{level}</option>)}
                  </select>
                </label>
              ))}
            </div>
          </fieldset>

          <fieldset className="form-section">
            <legend>Strategy</legend>
            <p>Alignment and sustainability inputs.</p>
            <div className="form-grid form-grid-two">
              {[
                ["Strategic Alignment", "Medium"],
                ["Sustainability", "Medium"],
              ].map(([label, defaultValue]) => (
                <label className="field" key={label}>
                  <span>{label}</span>
                  <select defaultValue={defaultValue}>
                    {levelOptions.map((level) => <option key={level}>{level}</option>)}
                  </select>
                </label>
              ))}
            </div>
          </fieldset>

          <div className="form-action-row">
            <p>Static shell only · evaluation request disabled</p>
            <button className="primary-action" type="button">Evaluate Opportunity</button>
          </div>
        </form>

        <aside className="prediction-rail">
          <SectionRule title="Evaluation Output" note="Static Review example" />
          <div className="result-placeholder">
            <span>Model Score</span>
            <strong>55.22</strong>
            <small>Decision <b>Review</b></small>
          </div>
          <dl className="result-ledger">
            <div><dt>Estimated Risk</dt><dd>48.40</dd></div>
            <div><dt>Input Features</dt><dd>10</dd></div>
            <div><dt>Raw Features</dt><dd>38</dd></div>
          </dl>
          <div className="contribution-block">
            <span>Positive Model Contributions</span>
            <div><i className="contribution-positive" style={{ width: "72%" }} /><b>Expected ROI</b><code>+12.8</code></div>
            <div><i className="contribution-positive" style={{ width: "51%" }} /><b>Strategic impact</b><code>+8.4</code></div>
          </div>
          <div className="contribution-block">
            <span>Negative Model Contributions</span>
            <div><i className="contribution-negative" style={{ width: "64%" }} /><b>Overall risk</b><code>−10.6</code></div>
            <div><i className="contribution-negative" style={{ width: "32%" }} /><b>Payback period</b><code>−5.1</code></div>
          </div>
          <p className="rail-note">
            Model contributions describe arithmetic influence, not causation. No prediction request has been made.
          </p>
        </aside>
      </div>
    </div>
  );
}
