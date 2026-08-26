"""Schemas for simplified opportunity model predictions."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Sector = Literal[
    "Education",
    "Entertainment",
    "Healthcare",
    "Infrastructure",
    "Logistics",
    "Real Estate",
    "Renewable Energy",
    "Retail",
    "Technology",
    "Tourism",
]
Region = Literal[
    "Asir",
    "Eastern Province",
    "Jazan",
    "Madinah",
    "Makkah",
    "Qassim",
    "Riyadh",
    "Tabuk",
]
Level = Literal["Low", "Medium", "High"]
Recommendation = Literal["Invest", "Review", "Reject"]


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sector: Sector
    region: Region
    competition_level: Level
    investment_size_million: float = Field(ge=20, le=5000)
    expected_roi_percent: float = Field(ge=-5, le=30)
    payback_period_years: float = Field(ge=1, le=15)
    market_demand_level: Level
    risk_level: Level
    strategic_alignment_level: Level
    sustainability_level: Level


class ModelContribution(BaseModel):
    feature: str
    readable_feature: str
    value: float
    coefficient: float
    contribution: float
    direction: Literal["positive", "negative"]


class GeneratedFeatureSummary(BaseModel):
    sector: str
    region: str
    competition_level: str
    investment_size_million: float
    expected_roi_percent: float
    irr_percent: float
    npv_million: float
    payback_period_years: float
    overall_risk_score: float
    market_attractiveness_score: float
    financial_strength_score: float
    strategic_impact_score: float
    sustainability_score: float


class PredictionResponse(BaseModel):
    predicted_investment_score: float
    recommendation: Recommendation
    estimated_overall_risk_score: float
    positive_contributions: list[str]
    negative_contributions: list[str]
    contributions: list[ModelContribution]
    generated_feature_summary: GeneratedFeatureSummary
    disclaimer: str
