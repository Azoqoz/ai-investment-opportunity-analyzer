import { apiGet } from "@/lib/api/client";
import type { OverviewResponse } from "@/lib/api/types";

export function getOverview(signal?: AbortSignal) {
  return apiGet<OverviewResponse>("/overview", signal);
}
