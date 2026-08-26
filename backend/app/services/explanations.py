"""Framework-neutral Ridge model-contribution calculations."""

from __future__ import annotations

import pandas as pd

from .inference import get_processed_feature_names


READABLE_FEATURE_NAMES = {
    "competition_level_Low": "Low competition",
    "competition_level_Medium": "Medium competition",
    "competition_level_High": "High competition",
    "expected_roi_percent": "Expected ROI",
    "irr_percent": "IRR",
    "npv_million": "NPV",
    "payback_period_years": "Payback period",
    "overall_risk_score": "Overall risk",
    "market_attractiveness_score": "Market attractiveness",
    "financial_strength_score": "Financial strength",
    "strategic_impact_score": "Strategic impact",
    "sustainability_score": "Sustainability",
    "market_growth_percent": "Market growth",
    "demand_score": "Market demand",
    "customer_adoption_score": "Customer adoption",
    "scalability_score": "Scalability",
    "profit_margin_percent": "Profit margin",
    "job_creation_score": "Job creation",
    "quality_of_life_score": "Quality of life",
    "localization_score": "Localization",
    "economic_diversification_score": "Economic diversification",
    "vision_2030_alignment_score": "Vision 2030 alignment",
    "region_Riyadh": "Region: Riyadh",
    "region_Asir": "Region: Asir",
    "region_Makkah": "Region: Makkah",
    "region_Madinah": "Region: Madinah",
    "region_Tabuk": "Region: Tabuk",
    "region_Qassim": "Region: Qassim",
    "region_Jazan": "Region: Jazan",
    "region_Eastern Province": "Region: Eastern Province",
    "sector_Technology": "Sector: Technology",
    "sector_Real Estate": "Sector: Real Estate",
    "sector_Tourism": "Sector: Tourism",
    "sector_Entertainment": "Sector: Entertainment",
    "sector_Healthcare": "Sector: Healthcare",
    "sector_Logistics": "Sector: Logistics",
    "sector_Renewable Energy": "Sector: Renewable Energy",
    "sector_Education": "Sector: Education",
    "sector_Retail": "Sector: Retail",
    "sector_Infrastructure": "Sector: Infrastructure",
}


def clean_feature_name(feature: str) -> str:
    """Convert a processed feature name into the current readable label."""
    return READABLE_FEATURE_NAMES.get(feature, feature.replace("_", " "))


def explain_model_contributions(
    input_data: pd.DataFrame,
    model,
    preprocessor,
    top_n: int = 8,
) -> pd.DataFrame:
    """Calculate the current Ridge value × coefficient model contributions."""
    processed_data = preprocessor.transform(input_data)
    processed_feature_names = get_processed_feature_names(preprocessor)
    processed_frame = pd.DataFrame(
        processed_data,
        columns=processed_feature_names,
    )

    row = processed_frame.iloc[0]
    contributions = pd.DataFrame(
        {
            "feature": row.index,
            "value": row.values,
            "coefficient": model.coef_,
            "contribution": row.values * model.coef_,
        }
    )
    contributions["absolute_contribution"] = contributions[
        "contribution"
    ].abs()
    contributions = contributions.sort_values(
        by="absolute_contribution",
        ascending=False,
    ).head(top_n)
    contributions["readable_feature"] = contributions["feature"].apply(
        clean_feature_name
    )
    return contributions


def summarize_model_contributions(
    model_contributions: pd.DataFrame,
) -> tuple[list[str], list[str]]:
    """Return safe positive- and negative-contribution descriptions."""
    positive_contributions = []
    negative_contributions = []

    for _, row in model_contributions.iterrows():
        feature = row["readable_feature"]
        contribution = row["contribution"]

        if contribution > 0:
            positive_contributions.append(
                f"{feature} had a positive model contribution to the predicted score."
            )
        else:
            negative_contributions.append(
                f"{feature} had a negative model contribution to the predicted score."
            )

    return positive_contributions, negative_contributions
