from __future__ import annotations

import pandas as pd
import pytest

from predict import predict_investment_opportunity
from tests.parity_helpers import (
    filter_opportunities,
    predict_without_version_warnings,
    rank_opportunities,
    select_existing_opportunity,
)


@pytest.fixture
def controlled_opportunities() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "opportunity_id": "A",
                "sector": "Technology",
                "region": "Riyadh",
                "recommendation": "Invest",
                "investment_score": 90.0,
                "expected_roi_percent": 12.0,
                "overall_risk_score": 30.0,
            },
            {
                "opportunity_id": "B",
                "sector": "Technology",
                "region": "Riyadh",
                "recommendation": "Invest",
                "investment_score": 90.0,
                "expected_roi_percent": 12.0,
                "overall_risk_score": 20.0,
            },
            {
                "opportunity_id": "C",
                "sector": "Healthcare",
                "region": "Makkah",
                "recommendation": "Review",
                "investment_score": 90.0,
                "expected_roi_percent": 15.0,
                "overall_risk_score": 80.0,
            },
            {
                "opportunity_id": "D",
                "sector": "Healthcare",
                "region": "Riyadh",
                "recommendation": "Review",
                "investment_score": 45.0,
                "expected_roi_percent": 20.0,
                "overall_risk_score": 10.0,
            },
            {
                "opportunity_id": "E",
                "sector": "Retail",
                "region": "Jazan",
                "recommendation": "Reject",
                "investment_score": 44.99,
                "expected_roi_percent": 5.0,
                "overall_risk_score": 70.0,
            },
        ]
    )


def test_ranking_uses_score_then_roi_then_risk(controlled_opportunities):
    ranked = rank_opportunities(controlled_opportunities)
    assert ranked["opportunity_id"].tolist() == ["C", "B", "A", "D", "E"]


@pytest.mark.parametrize(
    ("filters", "expected_ids"),
    [
        pytest.param({"sector": "Technology"}, ["A", "B"], id="sector"),
        pytest.param({"region": "Makkah"}, ["C"], id="region"),
        pytest.param(
            {"recommendation": "Review"}, ["C", "D"], id="recommendation"
        ),
        pytest.param({"minimum_score": 90.0}, ["A", "B", "C"], id="minimum"),
        pytest.param({"maximum_score": 45.0}, ["D", "E"], id="maximum"),
    ],
)
def test_individual_filters(controlled_opportunities, filters, expected_ids):
    filtered = filter_opportunities(controlled_opportunities, **filters)
    assert filtered["opportunity_id"].tolist() == expected_ids


def test_combined_filters_and_inclusive_score_boundaries(controlled_opportunities):
    filtered = filter_opportunities(
        controlled_opportunities,
        sector="Healthcare",
        region="Riyadh",
        recommendation="Review",
        minimum_score=45.0,
        maximum_score=45.0,
    )
    assert filtered["opportunity_id"].tolist() == ["D"]


def test_existing_opportunity_uses_stored_score_not_model_prediction(raw_data):
    selected = select_existing_opportunity(raw_data, "INV-00001")
    raw_model_input = selected.drop(
        labels=[
            "opportunity_id",
            "opportunity_name",
            "investment_score",
            "recommendation",
        ]
    ).to_frame().T
    prediction = predict_without_version_warnings(
        predict_investment_opportunity, raw_model_input
    )

    stored_score = float(selected["investment_score"])
    predicted_score = float(prediction.iloc[0]["predicted_investment_score"])

    assert stored_score == 80.1
    assert predicted_score == 71.4
    assert stored_score != predicted_score
