import type { Metadata } from "next";

import {
  OpportunitiesClient,
  type OpportunityFilters,
} from "@/app/opportunities/opportunities-client";

export const metadata: Metadata = {
  title: "Opportunities",
  description: "Research and compare synthetic investment opportunities.",
};

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

function firstValue(value: string | string[] | undefined) {
  return Array.isArray(value) ? (value[0] ?? "") : (value ?? "");
}

function positivePage(value: string) {
  const parsed = Number.parseInt(value, 10);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : 1;
}

function validScore(value: string) {
  if (value.trim() === "") return "";

  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 0 && parsed <= 100 ? value : "";
}

export default async function OpportunitiesPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const query = await searchParams;
  const initialFilters: OpportunityFilters = {
    search: firstValue(query.search),
    sector: firstValue(query.sector),
    region: firstValue(query.region),
    recommendation: firstValue(query.recommendation),
    minScore: validScore(firstValue(query.min_score)),
    maxScore: validScore(firstValue(query.max_score)),
    page: positivePage(firstValue(query.page)),
  };

  return <OpportunitiesClient initialFilters={initialFilters} />;
}
