import { apiPost } from "@/lib/api/client";
import type { PredictionRequest, PredictionResponse } from "@/lib/api/types";

export function predictOpportunity(payload: PredictionRequest, signal?: AbortSignal) {
  return apiPost<PredictionResponse, PredictionRequest>("/predict", payload, signal);
}
