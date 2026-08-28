"""Schemas for overview and stored synthetic opportunities."""

from __future__ import annotations

from pydantic import BaseModel

from .common import CategoryAverage, HistogramBin, RecommendationCount


class OverviewResponse(BaseModel):
    total_opportunities: int
    average_investment_score: float
    average_overall_risk_score: float
    invest_opportunities: int
    recommendation_distribution: list[RecommendationCount]
    investment_score_distribution: list[HistogramBin]
    average_score_by_sector: list[CategoryAverage]
    average_score_by_region: list[CategoryAverage]
    available_sectors: list[str]
    available_regions: list[str]
    recommendation_options: list[str]
    disclaimer: str


class OpportunityListItem(BaseModel):
    opportunity_id: str
    opportunity_name: str
    sector: str
    region: str
    investment_score: float
    recommendation: str
    expected_roi_percent: float
    overall_risk_score: float
    strategic_impact_score: float
    sustainability_score: float


class OpportunityListResponse(BaseModel):
    items: list[OpportunityListItem]
    page: int
    page_size: int
    total: int
    total_pages: int


class OpportunityIdentity(BaseModel):
    opportunity_id: str
    opportunity_name: str
    sector: str
    region: str


class OpportunityFinancials(BaseModel):
    investment_size_million: float
    expected_roi_percent: float
    payback_period_years: float
    profit_margin_percent: float


class StoredSyntheticEvaluation(BaseModel):
    score_label: str = "Stored synthetic opportunity score"
    investment_score: float
    recommendation: str
    overall_risk_score: float
    strategic_impact_score: float
    sustainability_score: float
    market_attractiveness_score: float
    financial_strength_score: float


class OpportunityDetailResponse(BaseModel):
    identity: OpportunityIdentity
    financials: OpportunityFinancials
    stored_synthetic_evaluation: StoredSyntheticEvaluation
    disclaimer: str
