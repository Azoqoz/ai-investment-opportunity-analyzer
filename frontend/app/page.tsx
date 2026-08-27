"use client";

import { useEffect, useState, type CSSProperties } from "react";

import { useApiStatus } from "@/components/api-status-context";
import { PageHeader } from "@/components/page-header";
import { SectionRule } from "@/components/section-rule";
import { getOverview } from "@/lib/api/overview";
import type {
  CategoryAverage,
  OverviewResponse,
  RecommendationCount,
} from "@/lib/api/types";

type LoadState = "loading" | "ready" | "error";

const numberFormatter = new Intl.NumberFormat("en-US");
const recommendationOrder = ["Invest", "Review", "Reject"];
const loadingRankingRows = Array.from({ length: 5 }, () => null);
const loadingHistogramBins = Array.from({ length: 20 }, () => null);

function formatScore(value: number) {
  return value.toFixed(2);
}

function recommendationClass(recommendation: string) {
  const normalized = recommendation.toLowerCase();
  return recommendationOrder.some((item) => item.toLowerCase() === normalized)
    ? normalized
    : "review";
}

function DataPlaceholder({ className = "" }: { className?: string }) {
  return <span className={`terminal-data-placeholder ${className}`.trim()} aria-hidden="true" />;
}

function RankingPanel({
  title,
  rows,
}: {
  title: string;
  rows: CategoryAverage[] | null;
}) {
  const displayedRows = rows?.slice(0, 5) ?? loadingRankingRows;

  return (
    <section className="terminal-panel ranking-panel">
      <SectionRule title={title} note="Average investment score">
        <span className="quiet-meta">TOP 5</span>
      </SectionRule>
      <div className="ranking-ledger">
        {displayedRows.map((row, index) => (
          <div className="ranking-row" key={row?.category ?? `${title}-${index}`}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <strong>{row ? row.category : <DataPlaceholder className="ranking-label-placeholder" />}</strong>
            <i>{row ? <b style={{ width: `${row.average_investment_score}%` }} /> : null}</i>
            <code>{row ? formatScore(row.average_investment_score) : "—"}</code>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function OverviewPage() {
  const [data, setData] = useState<OverviewResponse | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const { setApiStatus, setDatasetRows } = useApiStatus();

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    setApiStatus("checking");
    setDatasetRows(null);

    async function loadOverview() {
      try {
        const overview = await getOverview(controller.signal);
        if (!active) return;

        setData(overview);
        setLoadState("ready");
        setDatasetRows(overview.total_opportunities);
        setApiStatus("online");
      } catch (error) {
        if (!active || (error instanceof DOMException && error.name === "AbortError")) return;

        setData(null);
        setLoadState("error");
        setDatasetRows(null);
        setApiStatus("offline");
      }
    }

    void loadOverview();

    return () => {
      active = false;
      controller.abort();
    };
  }, [setApiStatus, setDatasetRows]);

  const summaryItems = [
    {
      label: "Opportunities",
      value: data ? numberFormatter.format(data.total_opportunities) : null,
      note: "Synthetic universe",
    },
    {
      label: "Avg Score",
      value: data ? formatScore(data.average_investment_score) : null,
      note: "Investment score",
    },
    {
      label: "Avg Risk",
      value: data ? formatScore(data.average_overall_risk_score) : null,
      note: "Composite risk",
    },
    {
      label: "Invest",
      value: data ? numberFormatter.format(data.invest_opportunities) : null,
      note: data
        ? `${((data.invest_opportunities / data.total_opportunities) * 100).toFixed(1)}% of universe`
        : "Share of universe",
    },
  ];

  const recommendationRows: Array<RecommendationCount | null> = data
    ? data.recommendation_distribution
    : recommendationOrder.map((recommendation) => ({ recommendation, count: 0 }));
  const maximumRecommendationCount = Math.max(
    ...(data?.recommendation_distribution.map((item) => item.count) ?? [1]),
  );
  const maximumHistogramCount = Math.max(
    ...(data?.investment_score_distribution.map((item) => item.count) ?? [1]),
  );

  const aside = (() => {
    if (loadState === "error") {
      return (
        <div className="as-of-block overview-request-error" role="alert">
          <span>API unavailable</span>
          <strong>Unable to load the research universe.</strong>
        </div>
      );
    }

    if (loadState === "loading") {
      return (
        <div className="as-of-block" role="status" aria-live="polite">
          <span>API status</span>
          <strong>Loading research universe</strong>
        </div>
      );
    }

    return (
      <div className="as-of-block">
        <span>Workspace mode</span>
        <strong>Live research universe</strong>
      </div>
    );
  })();

  return (
    <div className="page-stack overview-page">
      <PageHeader
        eyebrow="Universe snapshot · Synthetic baseline"
        title="Investment Universe"
        description="Screening summary across decision outcomes, score bands, sectors, and regions."
        aside={aside}
      />

      <section className="summary-strip" aria-label="Portfolio summary" aria-busy={loadState === "loading"}>
        {summaryItems.map((item) => (
          <div className="summary-item" key={item.label}>
            <strong>{item.value ?? <DataPlaceholder className="summary-value-placeholder" />}</strong>
            <span>{item.label}</span>
            <small>{item.note}</small>
          </div>
        ))}
      </section>

      <div className="terminal-grid terminal-grid-primary">
        <section className="terminal-panel recommendation-panel">
          <SectionRule title="Decision Distribution" note="Count / share of universe" />
          <div className="recommendation-shell" aria-label="Decision distribution">
            {recommendationRows.map((row, index) => {
              const recommendation = row?.recommendation ?? recommendationOrder[index];
              const count = data && row ? row.count : null;
              const className = recommendationClass(recommendation);
              const width = count === null ? 0 : (count / maximumRecommendationCount) * 100;
              const share = count === null ? null : (count / data!.total_opportunities) * 100;

              return (
                <div
                  className="mix-row"
                  style={{ "--mix-width": `${width}%` } as CSSProperties}
                  key={recommendation}
                >
                  <span className={`mix-marker mix-${className}`} />
                  <span>{recommendation}</span>
                  <span className="mix-track">{count === null ? null : <i />}</span>
                  <strong>{count === null ? "—" : numberFormatter.format(count)}</strong>
                  <small>{share === null ? "—" : `${share.toFixed(1)}%`}</small>
                </div>
              );
            })}
          </div>
        </section>

        <section className="terminal-panel score-panel">
          <SectionRule title="Score Distribution" note="Five-point score bands" />
          <div className="distribution-shell" aria-label="Score distribution structure">
            <div className="distribution-field">
              {(data?.investment_score_distribution ?? loadingHistogramBins).map((bin, index) =>
                bin ? (
                  <span
                    key={`${bin.bin_start}-${bin.bin_end}`}
                    style={{ height: `${(bin.count / maximumHistogramCount) * 100}%` }}
                    title={`${bin.bin_start.toFixed(0)}–${bin.bin_end.toFixed(0)}: ${numberFormatter.format(bin.count)}`}
                  />
                ) : (
                  <span className="terminal-chart-placeholder" key={index} />
                ),
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
        <RankingPanel title="Sector Ranking" rows={data?.average_score_by_sector ?? null} />
        <RankingPanel title="Region Ranking" rows={data?.average_score_by_region ?? null} />
      </div>
    </div>
  );
}
