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
