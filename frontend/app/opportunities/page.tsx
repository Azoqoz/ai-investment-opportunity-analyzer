import type { Metadata } from "next";
import Link from "next/link";

import { PageHeader } from "@/components/page-header";
import { SectionRule } from "@/components/section-rule";
import { StatusLabel } from "@/components/status-label";

export const metadata: Metadata = {
  title: "Opportunities",
  description: "Research and compare synthetic investment opportunities.",
};

const sampleRows = [
  {
    id: "INV-01702",
    name: "Riyadh Renewable Energy Opportunity",
    sector: "Renewable Energy",
    region: "Riyadh",
    score: "91.40",
    recommendation: "Invest" as const,
    roi: "25.8%",
    risk: "22.3",
    strategic: "88.4",
    sustainability: "91.2",
  },
  {
    id: "INV-00418",
    name: "Eastern Province Technology Opportunity",
    sector: "Technology",
    region: "Eastern Province",
    score: "86.75",
    recommendation: "Invest" as const,
    roi: "21.4%",
    risk: "28.7",
    strategic: "84.6",
    sustainability: "76.9",
  },
  {
    id: "INV-02841",
    name: "Makkah Healthcare Opportunity",
    sector: "Healthcare",
    region: "Makkah",
    score: "68.20",
    recommendation: "Review" as const,
    roi: "15.2%",
    risk: "44.1",
    strategic: "79.8",
    sustainability: "72.5",
  },
  {
    id: "INV-00977",
    name: "Tabuk Tourism Opportunity",
    sector: "Tourism",
    region: "Tabuk",
    score: "43.10",
    recommendation: "Reject" as const,
    roi: "8.6%",
    risk: "71.8",
    strategic: "58.3",
    sustainability: "61.7",
  },
];

export default function OpportunitiesPage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Screening terminal · Static interface sample"
        title="Opportunity Universe"
        description="Filter and compare synthetic deals across score, return, risk, strategy, and sustainability."
        aside={
          <div className="as-of-block">
            <span>Universe size</span>
            <strong>5,000 records</strong>
          </div>
        }
      />

      <section className="filter-workbench" aria-label="Opportunity filters">
        <label className="field field-search">
          <span>Search</span>
          <input type="search" placeholder="Opportunity name or ID" />
        </label>
        <label className="field">
          <span>Sector</span>
          <select defaultValue="All sectors">
            <option>All sectors</option>
            <option>Technology</option>
            <option>Healthcare</option>
            <option>Renewable Energy</option>
          </select>
        </label>
        <label className="field">
          <span>Region</span>
          <select defaultValue="All regions">
            <option>All regions</option>
            <option>Riyadh</option>
            <option>Makkah</option>
            <option>Eastern Province</option>
          </select>
        </label>
        <label className="field">
          <span>Recommendation</span>
          <select defaultValue="All decisions">
            <option>All decisions</option>
            <option>Invest</option>
            <option>Review</option>
            <option>Reject</option>
          </select>
        </label>
        <div className="field score-range-field">
          <span>Score range</span>
          <div>
            <input aria-label="Minimum score" type="number" min="0" max="100" placeholder="0" />
            <i aria-hidden="true" />
            <input aria-label="Maximum score" type="number" min="0" max="100" placeholder="100" />
          </div>
        </div>
      </section>

      <section className="table-panel">
        <SectionRule title="Ranked Opportunity Set" note="Score ↓ · ROI ↓ · Risk ↑">
          <span className="table-count">4 sample rows / 5,000 records</span>
        </SectionRule>
        <div className="table-scroll">
          <table className="research-table">
            <thead>
              <tr>
                <th scope="col">Opportunity</th>
                <th scope="col">Sector</th>
                <th scope="col">Region</th>
                <th scope="col" className="numeric-cell">Score</th>
                <th scope="col">Decision</th>
                <th scope="col" className="numeric-cell">Expected ROI</th>
                <th scope="col" className="numeric-cell">Risk</th>
                <th scope="col" className="numeric-cell">Strategic</th>
                <th scope="col" className="numeric-cell">Sustainability</th>
              </tr>
            </thead>
            <tbody>
              {sampleRows.map((row) => (
                <tr key={row.id}>
                  <td>
                    <Link className="opportunity-link" href={`/opportunities/${row.id}`}>
                      <strong>{row.name}</strong>
                      <span>{row.id}</span>
                    </Link>
                  </td>
                  <td>
                    <Link className="cell-link" href={`/opportunities/${row.id}`}>
                      <span className="table-primary">{row.sector}</span>
                    </Link>
                  </td>
                  <td>
                    <Link className="cell-link" href={`/opportunities/${row.id}`}>{row.region}</Link>
                  </td>
                  <td className="numeric-cell score-cell">
                    <Link className="cell-link" href={`/opportunities/${row.id}`}>{row.score}</Link>
                  </td>
                  <td>
                    <Link className="cell-link" href={`/opportunities/${row.id}`}>
                      <StatusLabel tone={row.recommendation.toLowerCase() as "invest" | "review" | "reject"}>
                        {row.recommendation}
                      </StatusLabel>
                    </Link>
                  </td>
                  {[row.roi, row.risk, row.strategic, row.sustainability].map((value, index) => (
                    <td className="numeric-cell" key={`${row.id}-${index}`}>
                      <Link className="cell-link" href={`/opportunities/${row.id}`}>{value}</Link>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="pagination-shell">
          <span>Showing 1–4 of 4 sample records</span>
          <div>
            <button type="button" disabled>Previous</button>
            <span>Page 1</span>
            <button type="button" disabled>Next</button>
          </div>
        </div>
      </section>
    </div>
  );
}
