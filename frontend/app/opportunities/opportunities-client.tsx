"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";

import { useApiStatus } from "@/components/api-status-context";
import { PageHeader } from "@/components/page-header";
import { SectionRule } from "@/components/section-rule";
import { StatusLabel } from "@/components/status-label";
import { getOpportunities } from "@/lib/api/opportunities";
import { getOverview } from "@/lib/api/overview";
import type {
  OpportunityListItem,
  OpportunityListResponse,
  OverviewResponse,
} from "@/lib/api/types";

const PAGE_SIZE = 10;
const LOADING_ROWS = Array.from({ length: PAGE_SIZE }, (_, index) => index);

export interface OpportunityFilters {
  search: string;
  sector: string;
  region: string;
  recommendation: string;
  minScore: string;
  maxScore: string;
  page: number;
}

interface ParsedScore {
  value?: number;
  valid: boolean;
}

function parseScore(value: string): ParsedScore {
  if (value.trim() === "") return { valid: true };

  const parsed = Number(value);
  return {
    value: parsed,
    valid: Number.isFinite(parsed) && parsed >= 0 && parsed <= 100,
  };
}

function formatMetric(value: number) {
  return value.toFixed(2);
}

function resultRange(result: OpportunityListResponse | null) {
  if (!result || result.total === 0) return "Showing 0 of 0 records";

  const first = (result.page - 1) * result.page_size + 1;
  const last = Math.min(result.page * result.page_size, result.total);
  return `Showing ${first.toLocaleString()}–${last.toLocaleString()} of ${result.total.toLocaleString()} records`;
}

function opportunityHref(row: OpportunityListItem) {
  return `/opportunities/${row.opportunity_id}`;
}

export function OpportunitiesClient({
  initialFilters,
}: {
  initialFilters: OpportunityFilters;
}) {
  const { setApiStatus, setDatasetRows } = useApiStatus();
  const [search, setSearch] = useState(initialFilters.search);
  const [debouncedSearch, setDebouncedSearch] = useState(initialFilters.search.trim());
  const [sector, setSector] = useState(initialFilters.sector);
  const [region, setRegion] = useState(initialFilters.region);
  const [recommendation, setRecommendation] = useState(initialFilters.recommendation);
  const [minScore, setMinScore] = useState(initialFilters.minScore);
  const [maxScore, setMaxScore] = useState(initialFilters.maxScore);
  const [page, setPage] = useState(initialFilters.page);
  const [result, setResult] = useState<OpportunityListResponse | null>(null);
  const [filterOptions, setFilterOptions] = useState<OverviewResponse | null>(null);
  const [requestState, setRequestState] = useState<"loading" | "ready" | "error">("loading");
  const optionsLoaded = useRef(false);

  const parsedMinimum = useMemo(() => parseScore(minScore), [minScore]);
  const parsedMaximum = useMemo(() => parseScore(maxScore), [maxScore]);
  const scoreOrderValid =
    parsedMinimum.value === undefined ||
    parsedMaximum.value === undefined ||
    parsedMinimum.value <= parsedMaximum.value;
  const scoresValid = parsedMinimum.valid && parsedMaximum.valid && scoreOrderValid;

  useEffect(() => {
    const timeout = window.setTimeout(() => setDebouncedSearch(search.trim()), 300);
    return () => window.clearTimeout(timeout);
  }, [search]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (search.trim()) params.set("search", search.trim());
    if (sector) params.set("sector", sector);
    if (region) params.set("region", region);
    if (recommendation) params.set("recommendation", recommendation);
    if (parsedMinimum.valid && parsedMinimum.value !== undefined) {
      params.set("min_score", minScore);
    }
    if (parsedMaximum.valid && parsedMaximum.value !== undefined) {
      params.set("max_score", maxScore);
    }
    if (page > 1) params.set("page", String(page));

    const query = params.toString();
    window.history.replaceState(null, "", query ? `/opportunities?${query}` : "/opportunities");
  }, [maxScore, minScore, page, parsedMaximum, parsedMinimum, recommendation, region, search, sector]);

  useEffect(() => {
    if (!scoresValid) return;

    const controller = new AbortController();
    let active = true;
    queueMicrotask(() => {
      if (!active) return;
      setRequestState("loading");
      setApiStatus("checking");
    });

    const optionsRequest = optionsLoaded.current
      ? Promise.resolve<OverviewResponse | null>(null)
      : getOverview(controller.signal);

    Promise.all([
      getOpportunities(
        {
          search: debouncedSearch || undefined,
          sector: sector || undefined,
          region: region || undefined,
          recommendation: recommendation || undefined,
          minScore: parsedMinimum.value,
          maxScore: parsedMaximum.value,
          page,
          pageSize: PAGE_SIZE,
        },
        controller.signal,
      ),
      optionsRequest,
    ])
      .then(([opportunities, overview]) => {
        if (!active) return;

        if (overview) {
          optionsLoaded.current = true;
          setFilterOptions(overview);
          setDatasetRows(overview.total_opportunities);
        }
        const lastPage = Math.max(opportunities.total_pages, 1);
        if (page > lastPage) {
          setPage(lastPage);
          return;
        }

        setResult(opportunities);
        setRequestState("ready");
        setApiStatus("online");
      })
      .catch((error: unknown) => {
        if (!active || (error instanceof DOMException && error.name === "AbortError")) return;
        setRequestState("error");
        setApiStatus("offline");
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [
    debouncedSearch,
    page,
    parsedMaximum.value,
    parsedMinimum.value,
    recommendation,
    region,
    scoresValid,
    sector,
    setApiStatus,
    setDatasetRows,
  ]);

  function resetPage() {
    setPage(1);
  }

  function updateSearch(value: string) {
    setSearch(value);
    resetPage();
  }

  const tableCount =
    requestState === "loading"
      ? "Loading ranked records…"
      : requestState === "error"
        ? "API data unavailable"
        : `${result?.items.length ?? 0} ${(result?.items.length ?? 0) === 1 ? "row" : "rows"} / ${(result?.total ?? 0).toLocaleString()} matches`;

  const universeSize = filterOptions?.total_opportunities ?? 5000;
  const displayPage = result?.page ?? page;
  const displayTotalPages = Math.max(result?.total_pages ?? 1, 1);

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Screening terminal · Live API dataset"
        title="Opportunity Universe"
        description="Filter and compare synthetic deals across score, return, risk, strategy, and sustainability."
        aside={
          <div className="as-of-block">
            <span>Universe size</span>
            <strong>{universeSize.toLocaleString()} records</strong>
          </div>
        }
      />

      <section className="filter-workbench" aria-label="Opportunity filters">
        <label className="field field-search">
          <span>Search</span>
          <input
            type="search"
            placeholder="Opportunity name or ID"
            value={search}
            onChange={(event) => updateSearch(event.target.value)}
          />
        </label>
        <label className="field">
          <span>Sector</span>
          <select
            value={sector}
            onChange={(event) => {
              setSector(event.target.value);
              resetPage();
            }}
          >
            <option value="">All sectors</option>
            {filterOptions?.available_sectors.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Region</span>
          <select
            value={region}
            onChange={(event) => {
              setRegion(event.target.value);
              resetPage();
            }}
          >
            <option value="">All regions</option>
            {filterOptions?.available_regions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Recommendation</span>
          <select
            value={recommendation}
            onChange={(event) => {
              setRecommendation(event.target.value);
              resetPage();
            }}
          >
            <option value="">All decisions</option>
            {filterOptions?.recommendation_options.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </label>
        <div className="field score-range-field">
          <span>Score range</span>
          <div>
            <input
              aria-label="Minimum score"
              aria-invalid={!parsedMinimum.valid || !scoreOrderValid}
              type="number"
              min="0"
              max="100"
              placeholder="0"
              value={minScore}
              onChange={(event) => {
                setMinScore(event.target.value);
                resetPage();
              }}
            />
            <i aria-hidden="true" />
            <input
              aria-label="Maximum score"
              aria-invalid={!parsedMaximum.valid || !scoreOrderValid}
              type="number"
              min="0"
              max="100"
              placeholder="100"
              value={maxScore}
              onChange={(event) => {
                setMaxScore(event.target.value);
                resetPage();
              }}
            />
          </div>
        </div>
      </section>

      <section className="table-panel">
        <SectionRule title="Ranked Opportunity Set" note="Score ↓ · ROI ↓ · Risk ↑">
          <span className="table-count">{tableCount}</span>
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
              {requestState === "loading" &&
                LOADING_ROWS.map((row) => (
                  <tr className="opportunity-loading-row" key={row} aria-hidden="true">
                    {Array.from({ length: 9 }, (_, column) => (
                      <td key={column}>
                        <span className="terminal-data-placeholder opportunity-cell-placeholder" />
                      </td>
                    ))}
                  </tr>
                ))}

              {requestState === "error" && (
                <tr>
                  <td className="opportunity-table-message opportunity-table-error" colSpan={9}>
                    Unable to load opportunities from the API.
                  </td>
                </tr>
              )}

              {requestState === "ready" && result?.items.length === 0 && (
                <tr>
                  <td className="opportunity-table-message" colSpan={9}>
                    No opportunities match the current filters.
                  </td>
                </tr>
              )}

              {requestState === "ready" && result?.items.map((row) => {
                const href = opportunityHref(row);
                const tone = row.recommendation.toLowerCase() as "invest" | "review" | "reject";
                const metrics = [
                  `${formatMetric(row.expected_roi_percent)}%`,
                  formatMetric(row.overall_risk_score),
                  formatMetric(row.strategic_impact_score),
                  formatMetric(row.sustainability_score),
                ];

                return (
                  <tr key={row.opportunity_id}>
                    <td>
                      <Link className="opportunity-link" href={href}>
                        <strong>{row.opportunity_name}</strong>
                        <span>{row.opportunity_id}</span>
                      </Link>
                    </td>
                    <td>
                      <Link className="cell-link" href={href}>
                        <span className="table-primary">{row.sector}</span>
                      </Link>
                    </td>
                    <td><Link className="cell-link" href={href}>{row.region}</Link></td>
                    <td className="numeric-cell score-cell">
                      <Link className="cell-link" href={href}>{formatMetric(row.investment_score)}</Link>
                    </td>
                    <td>
                      <Link className="cell-link" href={href}>
                        <StatusLabel tone={tone}>{row.recommendation}</StatusLabel>
                      </Link>
                    </td>
                    {metrics.map((value, index) => (
                      <td className="numeric-cell" key={`${row.opportunity_id}-${index}`}>
                        <Link className="cell-link" href={href}>{value}</Link>
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="pagination-shell">
          <span>{requestState === "error" ? "Records unavailable" : resultRange(result)}</span>
          <div>
            <button
              type="button"
              disabled={requestState === "loading" || page <= 1}
              onClick={() => setPage((current) => Math.max(1, current - 1))}
            >
              Previous
            </button>
            <span>Page {displayPage} of {displayTotalPages}</span>
            <button
              type="button"
              disabled={
                requestState === "loading" ||
                requestState === "error" ||
                !result ||
                result.total_pages === 0 ||
                page >= result.total_pages
              }
              onClick={() => setPage((current) => current + 1)}
            >
              Next
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
