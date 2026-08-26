"""Small test-only helpers that mirror current Streamlit data behavior."""

from __future__ import annotations

import ast
import inspect
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SIMPLIFIED_INPUT_FIELDS = [
    "sector",
    "region",
    "competition_level",
    "investment_size_million",
    "expected_roi_percent",
    "payback_period_years",
    "market_demand_level",
    "risk_level",
    "strategic_alignment_level",
    "sustainability_level",
]

RAW_MODEL_FIELDS = [
    "sector",
    "region",
    "competition_level",
    "investment_size_million",
    "capex_million",
    "opex_million",
    "expected_roi_percent",
    "irr_percent",
    "payback_period_years",
    "revenue_growth_percent",
    "profit_margin_percent",
    "npv_million",
    "market_size_billion",
    "market_growth_percent",
    "demand_score",
    "customer_adoption_score",
    "scalability_score",
    "financial_risk_score",
    "regulatory_risk_score",
    "execution_risk_score",
    "market_risk_score",
    "dependency_risk_score",
    "overall_risk_score",
    "vision_2030_alignment_score",
    "economic_diversification_score",
    "job_creation_score",
    "localization_score",
    "quality_of_life_score",
    "strategic_impact_score",
    "environmental_impact_score",
    "social_impact_score",
    "governance_score",
    "sustainability_score",
    "risk_adjusted_roi",
    "profitability_index",
    "payback_efficiency",
    "market_attractiveness_score",
    "financial_strength_score",
]

GOLDEN_PREDICTION_CASES = {
    "lower": {
        "inputs": {
            "sector": "Retail",
            "region": "Jazan",
            "competition_level": "High",
            "investment_size_million": 100.0,
            "expected_roi_percent": 0.0,
            "payback_period_years": 15.0,
            "market_demand_level": "Low",
            "risk_level": "High",
            "strategic_alignment_level": "Low",
            "sustainability_level": "Low",
        },
        "score": 0.0,
        "recommendation": "Reject",
    },
    "review": {
        "inputs": {
            "sector": "Technology",
            "region": "Riyadh",
            "competition_level": "Medium",
            "investment_size_million": 250.0,
            "expected_roi_percent": 12.0,
            "payback_period_years": 6.0,
            "market_demand_level": "Medium",
            "risk_level": "Medium",
            "strategic_alignment_level": "Medium",
            "sustainability_level": "Medium",
        },
        "score": 55.22,
        "recommendation": "Review",
    },
    "higher": {
        "inputs": {
            "sector": "Renewable Energy",
            "region": "Riyadh",
            "competition_level": "Low",
            "investment_size_million": 1000.0,
            "expected_roi_percent": 25.0,
            "payback_period_years": 2.0,
            "market_demand_level": "High",
            "risk_level": "Low",
            "strategic_alignment_level": "High",
            "sustainability_level": "High",
        },
        "score": 100.0,
        "recommendation": "Invest",
    },
}


def load_streamlit_feature_builder(project_root: Path):
    """Load only the current builder and its helpers without importing Streamlit."""
    app_path = project_root / "app" / "streamlit_app.py"
    tree = ast.parse(app_path.read_text(encoding="utf-8"), filename=str(app_path))
    wanted_names = {
        "score_from_level",
        "risk_from_level",
        "clip_value",
        "build_simplified_prediction_input",
    }
    function_nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in wanted_names
    ]
    found_names = {node.name for node in function_nodes}
    if found_names != wanted_names:
        missing = sorted(wanted_names - found_names)
        raise AssertionError(f"Missing Streamlit feature-builder functions: {missing}")

    namespace: dict[str, Any] = {"np": np, "pd": pd}
    module = ast.Module(body=function_nodes, type_ignores=[])
    exec(compile(module, filename=str(app_path), mode="exec"), namespace)
    return namespace["build_simplified_prediction_input"]


def simplified_builder_parameter_names(builder) -> list[str]:
    """Return the public simplified fields, excluding the internal base DataFrame."""
    return [
        name
        for name in inspect.signature(builder).parameters
        if name != "base_df"
    ]


def rank_opportunities(frame: pd.DataFrame) -> pd.DataFrame:
    """Apply the exact three-key ranking currently used by Streamlit."""
    return frame.sort_values(
        by=[
            "investment_score",
            "expected_roi_percent",
            "overall_risk_score",
        ],
        ascending=[False, False, True],
    )


def filter_opportunities(
    frame: pd.DataFrame,
    *,
    sector: str = "All",
    region: str = "All",
    recommendation: str = "All",
    minimum_score: float = 0,
    maximum_score: float = 100,
) -> pd.DataFrame:
    """Apply the inclusive filtering semantics currently used by Streamlit."""
    result = frame.copy()

    if sector != "All":
        result = result[result["sector"] == sector]
    if region != "All":
        result = result[result["region"] == region]
    if recommendation != "All":
        result = result[result["recommendation"] == recommendation]

    return result[
        result["investment_score"].between(minimum_score, maximum_score)
    ]


def select_existing_opportunity(
    frame: pd.DataFrame, opportunity_id: str
) -> pd.Series:
    """Mirror the current existing-opportunity lookup against the stored CSV row."""
    return frame[frame["opportunity_id"] == opportunity_id].iloc[0]


def predict_without_version_warnings(predict_function, input_frame: pd.DataFrame):
    """Run current inference while suppressing environment-only pickle warnings."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return predict_function(input_frame)
