import { apiGet } from "@/lib/api/client";
import type { OpportunityListResponse } from "@/lib/api/types";

export interface OpportunityQuery {
  search?: string;
  sector?: string;
  region?: string;
  recommendation?: string;
  minScore?: number;
  maxScore?: number;
  page: number;
  pageSize: number;
}

export function getOpportunities(query: OpportunityQuery, signal?: AbortSignal) {
  const params = new URLSearchParams({
    page: String(query.page),
    page_size: String(query.pageSize),
  });

  if (query.search) params.set("search", query.search);
  if (query.sector) params.set("sector", query.sector);
  if (query.region) params.set("region", query.region);
  if (query.recommendation) params.set("recommendation", query.recommendation);
  if (query.minScore !== undefined) params.set("min_score", String(query.minScore));
  if (query.maxScore !== undefined) params.set("max_score", String(query.maxScore));

  return apiGet<OpportunityListResponse>(`/opportunities?${params.toString()}`, signal);
}
