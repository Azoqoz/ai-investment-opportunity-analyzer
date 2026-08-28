from __future__ import annotations

import inspect

import pandas as pd
import pytest

from backend.app.services.feature_builder import (
    build_simplified_prediction_input,
)
from tests.parity_helpers import (
    GOLDEN_PREDICTION_CASES,
    RAW_MODEL_FIELDS,
    SIMPLIFIED_INPUT_FIELDS,
)


def test_backend_builder_exposes_current_ten_field_contract():
    parameters = [
        name
        for name in inspect.signature(
            build_simplified_prediction_input
        ).parameters
        if name != "base_df"
    ]
    assert parameters == SIMPLIFIED_INPUT_FIELDS


@pytest.mark.parametrize(
    "case_name",
    [
        pytest.param("lower", id="low-profile"),
        pytest.param("review", id="medium-profile"),
        pytest.param("higher", id="high-profile"),
    ],
)
def test_backend_builder_matches_current_streamlit_builder(
    raw_data,
    simplified_feature_builder,
    case_name,
):
    inputs = GOLDEN_PREDICTION_CASES[case_name]["inputs"]
    expected = simplified_feature_builder(raw_data, **inputs)
    actual = build_simplified_prediction_input(raw_data, **inputs)
    pd.testing.assert_frame_equal(actual, expected)


def test_backend_builder_preserves_exact_38_field_order(raw_data):
    built = build_simplified_prediction_input(
        raw_data,
        **GOLDEN_PREDICTION_CASES["review"]["inputs"],
    )
    assert built.shape == (1, 38)
    assert built.columns.tolist() == RAW_MODEL_FIELDS


@pytest.mark.parametrize(
    ("level", "expected"),
    [
        pytest.param(
            "Low",
            {
                "market_growth_percent": 3.0,
                "demand_score": 35.0,
                "customer_adoption_score": 30.0,
                "scalability_score": 38.0,
                "overall_risk_score": 23.4,
                "strategic_impact_score": 38.0,
                "sustainability_score": 40.0,
            },
            id="low",
        ),
        pytest.param(
            "Medium",
            {
                "market_growth_percent": 8.0,
                "demand_score": 65.0,
                "customer_adoption_score": 60.0,
                "scalability_score": 68.0,
                "overall_risk_score": 48.4,
                "strategic_impact_score": 68.0,
                "sustainability_score": 70.0,
            },
            id="medium",
        ),
        pytest.param(
            "High",
            {
                "market_growth_percent": 14.0,
                "demand_score": 90.0,
                "customer_adoption_score": 85.0,
                "scalability_score": 93.0,
                "overall_risk_score": 73.4,
                "strategic_impact_score": 88.0,
                "sustainability_score": 90.0,
            },
            id="high",
        ),
    ],
)
def test_backend_builder_preserves_level_mappings(raw_data, level, expected):
    inputs = dict(GOLDEN_PREDICTION_CASES["review"]["inputs"])
    inputs.update(
        market_demand_level=level,
        risk_level=level,
        strategic_alignment_level=level,
        sustainability_level=level,
    )
    row = build_simplified_prediction_input(raw_data, **inputs).iloc[0]
    for field, value in expected.items():
        assert row[field] == value


def test_backend_builder_preserves_all_risk_strategic_and_esg_fields(raw_data):
    row = build_simplified_prediction_input(
        raw_data,
        **GOLDEN_PREDICTION_CASES["review"]["inputs"],
    ).iloc[0]

    assert tuple(
        row[field]
        for field in [
            "financial_risk_score",
            "regulatory_risk_score",
            "execution_risk_score",
            "market_risk_score",
            "dependency_risk_score",
            "overall_risk_score",
        ]
    ) == (50.0, 45.0, 55.0, 50.0, 42.0, 48.4)
    assert tuple(
        row[field]
        for field in [
            "vision_2030_alignment_score",
            "economic_diversification_score",
            "job_creation_score",
            "localization_score",
            "quality_of_life_score",
            "strategic_impact_score",
        ]
    ) == (70.0, 67.0, 65.0, 68.0, 70.0, 68.0)
    assert tuple(
        row[field]
        for field in [
            "environmental_impact_score",
            "social_impact_score",
            "governance_score",
            "sustainability_score",
        ]
    ) == (70.0, 68.0, 72.0, 70.0)


def test_backend_builder_preserves_financial_derived_fields(raw_data):
    row = build_simplified_prediction_input(
        raw_data,
        **GOLDEN_PREDICTION_CASES["review"]["inputs"],
    ).iloc[0]
    expected = {
        "capex_million": 128.23,
        "opex_million": 24.24,
        "irr_percent": 14.0,
        "npv_million": 120.0,
        "revenue_growth_percent": 7.8,
        "profit_margin_percent": 18.0,
        "risk_adjusted_roi": 0.2429,
        "profitability_index": 0.4781,
        "payback_efficiency": 1.7143,
        "market_attractiveness_score": 58.25,
        "financial_strength_score": 42.45,
    }
    for field, value in expected.items():
        assert row[field] == pytest.approx(value, abs=1e-12)


def test_backend_builder_preserves_sector_market_size_medians(raw_data):
    technology_inputs = dict(GOLDEN_PREDICTION_CASES["review"]["inputs"])
    renewable_inputs = dict(technology_inputs, sector="Renewable Energy")

    technology = build_simplified_prediction_input(
        raw_data,
        **technology_inputs,
    ).iloc[0]
    renewable = build_simplified_prediction_input(
        raw_data,
        **renewable_inputs,
    ).iloc[0]

    assert technology["market_size_billion"] == 24.11
    assert renewable["market_size_billion"] == 23.63
