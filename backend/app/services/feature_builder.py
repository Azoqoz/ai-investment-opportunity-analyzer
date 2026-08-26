"""Framework-neutral extraction of the current simplified feature builder."""

from __future__ import annotations

import numpy as np
import pandas as pd


EXCLUDED_MODEL_COLUMNS = [
    "opportunity_id",
    "opportunity_name",
    "investment_score",
    "recommendation",
]


def score_from_level(
    level: str,
    low: float = 35,
    medium: float = 60,
    high: float = 85,
) -> float:
    """Preserve the current qualitative score mapping helper."""
    mapping = {
        "Low": low,
        "Medium": medium,
        "High": high,
    }
    return mapping[level]


def risk_from_level(level: str) -> float:
    """Preserve the current qualitative risk mapping helper."""
    mapping = {
        "Low": 25,
        "Medium": 50,
        "High": 75,
    }
    return mapping[level]


def clip_value(value: float, lower: float, upper: float) -> float:
    """Clip a scalar using the current feature-builder semantics."""
    return max(lower, min(value, upper))


def build_simplified_prediction_input(
    base_df: pd.DataFrame,
    sector: str,
    region: str,
    competition_level: str,
    investment_size_million: float,
    expected_roi_percent: float,
    payback_period_years: float,
    market_demand_level: str,
    risk_level: str,
    strategic_alignment_level: str,
    sustainability_level: str,
) -> pd.DataFrame:
    """Convert the current ten simplified inputs into 38 raw model fields."""
    feature_columns = [
        col for col in base_df.columns if col not in EXCLUDED_MODEL_COLUMNS
    ]

    input_row = {}

    for col in feature_columns:
        if pd.api.types.is_numeric_dtype(base_df[col]):
            input_row[col] = base_df[col].median()
        else:
            input_row[col] = base_df[col].mode()[0]

    input_row["sector"] = sector
    input_row["region"] = region
    input_row["competition_level"] = competition_level

    market_score = score_from_level(
        market_demand_level,
        low=35,
        medium=65,
        high=90,
    )
    risk_score = risk_from_level(risk_level)
    strategic_score = score_from_level(
        strategic_alignment_level,
        low=40,
        medium=70,
        high=90,
    )
    sustainability_score = score_from_level(
        sustainability_level,
        low=40,
        medium=70,
        high=90,
    )

    input_row["investment_size_million"] = investment_size_million
    input_row["expected_roi_percent"] = expected_roi_percent
    input_row["irr_percent"] = clip_value(expected_roi_percent + 2, -5, 35)
    input_row["payback_period_years"] = payback_period_years

    input_row["npv_million"] = round(
        investment_size_million * (expected_roi_percent / 100) * 4,
        2,
    )

    input_row["npv_million"] = clip_value(
        input_row["npv_million"],
        -500,
        3000,
    )

    input_row["revenue_growth_percent"] = clip_value(
        expected_roi_percent * 0.65,
        -5,
        25,
    )

    input_row["profit_margin_percent"] = clip_value(
        expected_roi_percent + 6,
        -10,
        40,
    )

    sector_median_market_size = base_df[base_df["sector"] == sector][
        "market_size_billion"
    ].median()

    if np.isnan(sector_median_market_size):
        sector_median_market_size = base_df["market_size_billion"].median()

    input_row["market_size_billion"] = round(sector_median_market_size, 2)

    input_row["market_growth_percent"] = {
        "Low": 3,
        "Medium": 8,
        "High": 14,
    }[market_demand_level]

    input_row["demand_score"] = market_score
    input_row["customer_adoption_score"] = clip_value(market_score - 5, 0, 100)
    input_row["scalability_score"] = clip_value(market_score + 3, 0, 100)

    input_row["financial_risk_score"] = clip_value(risk_score, 0, 100)
    input_row["regulatory_risk_score"] = clip_value(risk_score - 5, 0, 100)
    input_row["execution_risk_score"] = clip_value(risk_score + 5, 0, 100)
    input_row["market_risk_score"] = clip_value(risk_score, 0, 100)
    input_row["dependency_risk_score"] = clip_value(risk_score - 8, 0, 100)

    input_row["overall_risk_score"] = round(
        (
            input_row["financial_risk_score"]
            + input_row["regulatory_risk_score"]
            + input_row["execution_risk_score"]
            + input_row["market_risk_score"]
            + input_row["dependency_risk_score"]
        )
        / 5,
        2,
    )

    input_row["vision_2030_alignment_score"] = strategic_score
    input_row["economic_diversification_score"] = clip_value(
        strategic_score - 3,
        0,
        100,
    )
    input_row["job_creation_score"] = clip_value(strategic_score - 5, 0, 100)
    input_row["localization_score"] = clip_value(strategic_score - 2, 0, 100)
    input_row["quality_of_life_score"] = clip_value(strategic_score, 0, 100)

    input_row["strategic_impact_score"] = round(
        (
            input_row["vision_2030_alignment_score"]
            + input_row["economic_diversification_score"]
            + input_row["job_creation_score"]
            + input_row["localization_score"]
            + input_row["quality_of_life_score"]
        )
        / 5,
        2,
    )

    input_row["environmental_impact_score"] = sustainability_score
    input_row["social_impact_score"] = clip_value(
        sustainability_score - 2,
        0,
        100,
    )
    input_row["governance_score"] = clip_value(
        sustainability_score + 2,
        0,
        100,
    )

    input_row["sustainability_score"] = round(
        (
            input_row["environmental_impact_score"]
            + input_row["social_impact_score"]
            + input_row["governance_score"]
        )
        / 3,
        2,
    )

    input_row["risk_adjusted_roi"] = round(
        expected_roi_percent / (input_row["overall_risk_score"] + 1),
        4,
    )

    input_row["profitability_index"] = round(
        input_row["npv_million"] / (investment_size_million + 1),
        4,
    )

    input_row["payback_efficiency"] = round(
        expected_roi_percent / (payback_period_years + 1),
        4,
    )

    input_row["market_attractiveness_score"] = round(
        (
            (max(input_row["market_growth_percent"], 0) / 20) * 25
            + (input_row["demand_score"] / 100) * 25
            + (input_row["customer_adoption_score"] / 100) * 25
            + (input_row["scalability_score"] / 100) * 25
        ),
        2,
    )

    input_row["financial_strength_score"] = round(
        (
            ((input_row["expected_roi_percent"] + 5) / 35) * 25
            + ((input_row["irr_percent"] + 5) / 40) * 25
            + ((input_row["npv_million"] + 500) / 3500) * 25
            + ((input_row["profit_margin_percent"] + 10) / 50) * 25
        ),
        2,
    )

    prediction_input = pd.DataFrame([input_row])
    prediction_input = prediction_input[feature_columns]

    return prediction_input
