export interface RecommendationCount {
  recommendation: string;
  count: number;
}

export interface HistogramBin {
  bin_start: number;
  bin_end: number;
  count: number;
}

export interface CategoryAverage {
  category: string;
  average_investment_score: number;
}

export interface OverviewResponse {
  total_opportunities: number;
  average_investment_score: number;
  average_overall_risk_score: number;
  invest_opportunities: number;
  recommendation_distribution: RecommendationCount[];
  investment_score_distribution: HistogramBin[];
  average_score_by_sector: CategoryAverage[];
  average_score_by_region: CategoryAverage[];
  available_sectors: string[];
  available_regions: string[];
  recommendation_options: string[];
  disclaimer: string;
}

export interface OpportunityListItem {
  opportunity_id: string;
  opportunity_name: string;
  sector: string;
  region: string;
  investment_score: number;
  recommendation: string;
  expected_roi_percent: number;
  overall_risk_score: number;
  strategic_impact_score: number;
  sustainability_score: number;
}

export interface OpportunityListResponse {
  items: OpportunityListItem[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface OpportunityIdentity {
  opportunity_id: string;
  opportunity_name: string;
  sector: string;
  region: string;
}

export interface OpportunityFinancials {
  investment_size_million: number;
  expected_roi_percent: number;
  payback_period_years: number;
  profit_margin_percent: number;
}

export interface StoredSyntheticEvaluation {
  score_label: string;
  investment_score: number;
  recommendation: string;
  overall_risk_score: number;
  strategic_impact_score: number;
  sustainability_score: number;
  market_attractiveness_score: number;
  financial_strength_score: number;
}

export interface OpportunityDetailResponse {
  identity: OpportunityIdentity;
  financials: OpportunityFinancials;
  stored_synthetic_evaluation: StoredSyntheticEvaluation;
  disclaimer: string;
}

export interface PredictionRequest {
  sector: string;
  region: string;
  competition_level: "Low" | "Medium" | "High";
  investment_size_million: number;
  expected_roi_percent: number;
  payback_period_years: number;
  market_demand_level: "Low" | "Medium" | "High";
  risk_level: "Low" | "Medium" | "High";
  strategic_alignment_level: "Low" | "Medium" | "High";
  sustainability_level: "Low" | "Medium" | "High";
}

export interface ModelContribution {
  feature: string;
  readable_feature: string;
  value: number;
  coefficient: number;
  contribution: number;
  direction: "positive" | "negative";
}

export interface PredictionResponse {
  predicted_investment_score: number;
  recommendation: "Invest" | "Review" | "Reject";
  estimated_overall_risk_score: number;
  positive_contributions: string[];
  negative_contributions: string[];
  contributions: ModelContribution[];
  disclaimer: string;
}
