from __future__ import annotations

import pandas as pd
import pytest

from backend.app.services.data_service import (
    DEFAULT_DATA_FILE,
    filter_opportunities,
    get_opportunity_by_id,
    get_overview_aggregates,
    get_recommendation_distribution,
    get_region_averages,
    get_sector_averages,
    load_opportunities,
    paginate_opportunities,
    query_opportunities,
    rank_opportunities,
)
from tests.parity_helpers import (
    filter_opportunities as baseline_filter_opportunities,
)


def test_backend_loads_current_csv_from_repository_path(raw_data, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    loaded = load_opportunities()
    assert DEFAULT_DATA_FILE.is_absolute()
    pd.testing.assert_frame_equal(loaded, raw_data)


def test_backend_overview_aggregates_match_current_values(raw_data):
    assert get_overview_aggregates(raw_data) == {
        "total_opportunities": 5000,
        "average_investment_score": 51.67429,
        "average_overall_risk_score": 43.360994000000005,
        "invest_opportunities": 845,
    }


def test_backend_recommendation_distribution_matches_current_csv(raw_data):
    distribution = get_recommendation_distribution(raw_data)
    assert distribution.to_dict(orient="records") == [
        {"recommendation": "Invest", "count": 845},
        {"recommendation": "Review", "count": 2235},
        {"recommendation": "Reject", "count": 1920},
    ]


def test_backend_sector_and_region_averages_match_current_operations(raw_data):
    expected_sector = (
        raw_data.groupby("sector")["investment_score"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    expected_region = (
        raw_data.groupby("region")["investment_score"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    pd.testing.assert_frame_equal(get_sector_averages(raw_data), expected_sector)
    pd.testing.assert_frame_equal(get_region_averages(raw_data), expected_region)


def test_backend_filtering_matches_phase_1_baseline(raw_data):
    filters = {
        "sector": "Technology",
        "region": "Riyadh",
        "recommendation": "Review",
        "minimum_score": 45.0,
        "maximum_score": 74.99,
    }
    expected = baseline_filter_opportunities(raw_data, **filters)
    actual = filter_opportunities(raw_data, **filters)
    pd.testing.assert_frame_equal(actual, expected)


def test_backend_ranking_preserves_three_key_tie_breaking():
    controlled = pd.DataFrame(
        [
            {
                "opportunity_id": "A",
                "investment_score": 90.0,
                "expected_roi_percent": 12.0,
                "overall_risk_score": 30.0,
            },
            {
                "opportunity_id": "B",
                "investment_score": 90.0,
                "expected_roi_percent": 12.0,
                "overall_risk_score": 20.0,
            },
            {
                "opportunity_id": "C",
                "investment_score": 90.0,
                "expected_roi_percent": 15.0,
                "overall_risk_score": 80.0,
            },
            {
                "opportunity_id": "D",
                "investment_score": 80.0,
                "expected_roi_percent": 30.0,
                "overall_risk_score": 10.0,
            },
        ]
    )
    assert rank_opportunities(controlled)["opportunity_id"].tolist() == [
        "C",
        "B",
        "A",
        "D",
    ]


def test_backend_pagination_preserves_order_and_metadata():
    controlled = pd.DataFrame({"opportunity_id": ["A", "B", "C", "D", "E"]})
    result = paginate_opportunities(controlled, page=2, page_size=2)
    assert result.items["opportunity_id"].tolist() == ["C", "D"]
    assert result.page == 2
    assert result.page_size == 2
    assert result.total == 5
    assert result.total_pages == 3


@pytest.mark.parametrize(
    ("page", "page_size"),
    [
        pytest.param(0, 10, id="invalid-page"),
        pytest.param(1, 0, id="invalid-page-size"),
    ],
)
def test_backend_pagination_rejects_non_positive_values(page, page_size):
    with pytest.raises(ValueError):
        paginate_opportunities(pd.DataFrame(), page=page, page_size=page_size)


def test_backend_query_filters_ranks_and_paginates(raw_data):
    result = query_opportunities(
        raw_data,
        sector="Technology",
        recommendation="Invest",
        page=1,
        page_size=5,
    )
    expected = rank_opportunities(
        filter_opportunities(
            raw_data,
            sector="Technology",
            recommendation="Invest",
        )
    )
    assert result.total == len(expected)
    pd.testing.assert_frame_equal(result.items, expected.iloc[:5].copy())


def test_backend_opportunity_lookup_returns_stored_row(raw_data):
    result = get_opportunity_by_id(raw_data, "INV-00001")
    assert result is not None
    assert result["opportunity_id"] == "INV-00001"
    assert float(result["investment_score"]) == 80.1
    assert get_opportunity_by_id(raw_data, "NOT-A-REAL-ID") is None
