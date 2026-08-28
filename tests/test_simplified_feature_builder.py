from __future__ import annotations

import pytest

from tests.parity_helpers import (
    GOLDEN_PREDICTION_CASES,
    RAW_MODEL_FIELDS,
    SIMPLIFIED_INPUT_FIELDS,
    simplified_builder_parameter_names,
)


def test_simplified_input_contract_has_current_ten_fields(
    simplified_feature_builder,
):
    assert simplified_builder_parameter_names(simplified_feature_builder) == (
        SIMPLIFIED_INPUT_FIELDS
    )


def test_builder_produces_exact_38_field_contract_in_order(
    raw_data, simplified_feature_builder
):
    built = simplified_feature_builder(
        raw_data, **GOLDEN_PREDICTION_CASES["review"]["inputs"]
    )
    assert built.shape == (1, 38)
    assert built.columns.tolist() == RAW_MODEL_FIELDS


@pytest.mark.parametrize(
    (
        "level",
        "market_values",
        "risk_values",
        "strategic_values",
        "sustainability_values",
    ),
    [
        pytest.param(
            "Low",
            (3.0, 35.0, 30.0, 38.0),
            (25.0, 20.0, 30.0, 25.0, 17.0, 23.4),
            (40.0, 37.0, 35.0, 38.0, 40.0, 38.0),
            (40.0, 38.0, 42.0, 40.0),
            id="low",
        ),
        pytest.param(
            "Medium",
            (8.0, 65.0, 60.0, 68.0),
            (50.0, 45.0, 55.0, 50.0, 42.0, 48.4),
            (70.0, 67.0, 65.0, 68.0, 70.0, 68.0),
            (70.0, 68.0, 72.0, 70.0),
            id="medium",
        ),
        pytest.param(
            "High",
            (14.0, 90.0, 85.0, 93.0),
            (75.0, 70.0, 80.0, 75.0, 67.0, 73.4),
            (90.0, 87.0, 85.0, 88.0, 90.0, 88.0),
            (90.0, 88.0, 92.0, 90.0),
            id="high",
        ),
    ],
)
def test_low_medium_high_feature_mappings(
    raw_data,
    simplified_feature_builder,
    level,
    market_values,
    risk_values,
    strategic_values,
    sustainability_values,
):
    inputs = dict(GOLDEN_PREDICTION_CASES["review"]["inputs"])
    inputs.update(
        market_demand_level=level,
        risk_level=level,
        strategic_alignment_level=level,
        sustainability_level=level,
    )
    row = simplified_feature_builder(raw_data, **inputs).iloc[0]

    assert tuple(
        row[field]
        for field in [
            "market_growth_percent",
            "demand_score",
            "customer_adoption_score",
            "scalability_score",
        ]
    ) == market_values
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
    ) == risk_values
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
    ) == strategic_values
    assert tuple(
        row[field]
        for field in [
            "environmental_impact_score",
            "social_impact_score",
            "governance_score",
            "sustainability_score",
        ]
    ) == sustainability_values


def test_generated_financial_and_composite_fields_match_current_behavior(
    raw_data, simplified_feature_builder
):
    row = simplified_feature_builder(
        raw_data, **GOLDEN_PREDICTION_CASES["review"]["inputs"]
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


def test_sector_controls_market_size_using_current_sector_median(
    raw_data, simplified_feature_builder
):
    technology_inputs = dict(GOLDEN_PREDICTION_CASES["review"]["inputs"])
    renewable_inputs = dict(technology_inputs, sector="Renewable Energy")

    technology = simplified_feature_builder(raw_data, **technology_inputs).iloc[0]
    renewable = simplified_feature_builder(raw_data, **renewable_inputs).iloc[0]

    assert technology["market_size_billion"] == 24.11
    assert renewable["market_size_billion"] == 23.63
    assert technology["market_size_billion"] != renewable["market_size_billion"]
