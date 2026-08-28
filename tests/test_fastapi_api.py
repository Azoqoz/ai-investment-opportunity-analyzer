from __future__ import annotations

import warnings

import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import DEFAULT_ALLOWED_ORIGINS, Settings
from backend.app.main import app
from tests.parity_helpers import GOLDEN_PREDICTION_CASES


@pytest.fixture(scope="module")
def api_client():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with TestClient(app) as client:
            yield client


def test_health_reports_all_startup_resources_ready(api_client):
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "data_loaded": True,
        "model_loaded": True,
        "preprocessor_loaded": True,
        "dataset_rows": 5000,
    }


def test_overview_matches_exact_current_dataset_baseline(api_client):
    response = api_client.get("/overview")

    assert response.status_code == 200
    body = response.json()
    assert body["total_opportunities"] == 5000
    assert body["average_investment_score"] == 51.67429
    assert body["average_overall_risk_score"] == 43.360994000000005
    assert body["invest_opportunities"] == 845
    assert body["recommendation_distribution"] == [
        {"recommendation": "Invest", "count": 845},
        {"recommendation": "Review", "count": 2235},
        {"recommendation": "Reject", "count": 1920},
    ]


def test_overview_exposes_frontend_options_histogram_and_disclaimer(api_client):
    body = api_client.get("/overview").json()

    assert sum(item["count"] for item in body["investment_score_distribution"]) == 5000
    assert len(body["investment_score_distribution"]) == 20
    assert len(body["average_score_by_sector"]) == 10
    assert len(body["average_score_by_region"]) == 8
    assert body["available_sectors"] == sorted(body["available_sectors"])
    assert body["available_regions"] == sorted(body["available_regions"])
    assert body["recommendation_options"] == ["Invest", "Review", "Reject"]
    assert "synthetic dataset" in body["disclaimer"].lower()
    assert "not financial advice" in body["disclaimer"].lower()


def test_opportunities_default_pagination(api_client):
    response = api_client.get("/opportunities")

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 10
    assert body["page"] == 1
    assert body["page_size"] == 10
    assert body["total"] == 5000
    assert body["total_pages"] == 500
    assert set(body["items"][0]) == {
        "opportunity_id",
        "opportunity_name",
        "sector",
        "region",
        "investment_score",
        "recommendation",
        "expected_roi_percent",
        "overall_risk_score",
        "strategic_impact_score",
        "sustainability_score",
    }


@pytest.mark.parametrize(
    ("params", "expected_field", "expected_value"),
    [
        ({"sector": "Technology"}, "sector", "Technology"),
        ({"region": "Riyadh"}, "region", "Riyadh"),
        ({"recommendation": "Invest"}, "recommendation", "Invest"),
    ],
    ids=["sector", "region", "recommendation"],
)
def test_opportunities_categorical_filters(
    api_client,
    params,
    expected_field,
    expected_value,
):
    response = api_client.get(
        "/opportunities",
        params={**params, "page_size": 100},
    )

    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    assert all(item[expected_field] == expected_value for item in items)


def test_opportunities_score_range_is_inclusive(api_client):
    response = api_client.get(
        "/opportunities",
        params={"min_score": 45, "max_score": 45, "page_size": 100},
    )

    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    assert all(item["investment_score"] == 45.0 for item in items)


def test_opportunities_combined_filters(api_client):
    params = {
        "sector": "Technology",
        "region": "Riyadh",
        "recommendation": "Review",
        "min_score": 50,
        "max_score": 60,
        "page_size": 100,
    }
    response = api_client.get("/opportunities", params=params)

    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    assert all(item["sector"] == "Technology" for item in items)
    assert all(item["region"] == "Riyadh" for item in items)
    assert all(item["recommendation"] == "Review" for item in items)
    assert all(50 <= item["investment_score"] <= 60 for item in items)


def test_opportunities_preserve_exact_three_key_ranking(api_client, raw_data):
    body = api_client.get(
        "/opportunities",
        params={"page": 1, "page_size": 100},
    ).json()
    expected_ids = (
        raw_data.sort_values(
            by=[
                "investment_score",
                "expected_roi_percent",
                "overall_risk_score",
            ],
            ascending=[False, False, True],
        )
        .head(100)["opportunity_id"]
        .tolist()
    )

    assert [item["opportunity_id"] for item in body["items"]] == expected_ids


def test_opportunities_search_by_exact_id(api_client):
    body = api_client.get(
        "/opportunities",
        params={"search": "INV-00001"},
    ).json()

    assert body["total"] == 1
    assert [item["opportunity_id"] for item in body["items"]] == ["INV-00001"]


def test_opportunities_search_by_partial_id(api_client):
    body = api_client.get(
        "/opportunities",
        params={"search": "INV-000"},
    ).json()

    assert body["items"]
    assert all("INV-000" in item["opportunity_id"] for item in body["items"])


def test_opportunities_search_by_name(api_client):
    body = api_client.get(
        "/opportunities",
        params={"search": "Tabuk Technology"},
    ).json()

    assert body["items"]
    assert all(
        "Tabuk Technology" in item["opportunity_name"]
        for item in body["items"]
    )


def test_opportunities_search_is_trimmed_and_case_insensitive(api_client):
    body = api_client.get(
        "/opportunities",
        params={"search": "  tAbUk tEcHnOlOgY  "},
    ).json()

    assert body["items"]
    assert all(
        "tabuk technology" in item["opportunity_name"].lower()
        for item in body["items"]
    )


def test_opportunities_search_combines_with_sector_filter(api_client):
    body = api_client.get(
        "/opportunities",
        params={"search": "Tabuk", "sector": "Technology", "page_size": 100},
    ).json()

    assert body["items"]
    assert all(item["sector"] == "Technology" for item in body["items"])
    assert all("Tabuk" in item["opportunity_name"] for item in body["items"])


def test_opportunities_search_returns_empty_page_for_no_matches(api_client):
    body = api_client.get(
        "/opportunities",
        params={"search": "definitely-no-opportunity"},
    ).json()

    assert body == {
        "items": [],
        "page": 1,
        "page_size": 10,
        "total": 0,
        "total_pages": 0,
    }


def test_opportunities_search_is_applied_before_pagination(api_client, raw_data):
    body = api_client.get(
        "/opportunities",
        params={"search": "Technology Opportunity", "page": 2, "page_size": 3},
    ).json()
    matching = raw_data[
        raw_data["opportunity_name"].str.contains(
            "Technology Opportunity",
            case=False,
            regex=False,
        )
    ].sort_values(
        by=[
            "investment_score",
            "expected_roi_percent",
            "overall_risk_score",
        ],
        ascending=[False, False, True],
    )

    assert body["total"] == len(matching)
    assert [item["opportunity_id"] for item in body["items"]] == (
        matching.iloc[3:6]["opportunity_id"].tolist()
    )


@pytest.mark.parametrize("search", ["", "   "])
def test_opportunities_empty_search_does_not_filter(api_client, search):
    body = api_client.get(
        "/opportunities",
        params={"search": search},
    ).json()

    assert body["total"] == 5000


@pytest.mark.parametrize(
    "params",
    [
        {"sector": "Oil"},
        {"region": "Unknown"},
        {"recommendation": "Maybe"},
        {"min_score": -0.01},
        {"max_score": 100.01},
        {"min_score": 80, "max_score": 20},
        {"page": 0},
        {"page_size": 0},
        {"page_size": 101},
    ],
    ids=[
        "sector",
        "region",
        "recommendation",
        "minimum-score",
        "maximum-score",
        "inverted-score-range",
        "page",
        "page-size-low",
        "page-size-high",
    ],
)
def test_opportunities_reject_invalid_queries(api_client, params):
    response = api_client.get("/opportunities", params=params)

    assert response.status_code == 422
    assert "detail" in response.json()


def test_known_opportunity_returns_grouped_stored_data(api_client, raw_data):
    expected = raw_data.loc[
        raw_data["opportunity_id"] == "INV-00001"
    ].iloc[0]
    response = api_client.get("/opportunities/INV-00001")

    assert response.status_code == 200
    body = response.json()
    assert body["identity"]["opportunity_id"] == "INV-00001"
    assert body["financials"]["expected_roi_percent"] == float(
        expected["expected_roi_percent"]
    )
    evaluation = body["stored_synthetic_evaluation"]
    assert evaluation["investment_score"] == 80.1
    assert evaluation["recommendation"] == expected["recommendation"]
    assert evaluation["score_label"] == "Stored synthetic opportunity score"
    assert "predicted" not in str(evaluation).lower()


def test_unknown_opportunity_returns_clean_404(api_client):
    response = api_client.get("/opportunities/NOT-A-REAL-ID")

    assert response.status_code == 404
    assert response.json() == {"detail": "Opportunity not found"}


@pytest.mark.parametrize(
    "case_name",
    ["lower", "review", "higher"],
    ids=["lower-reject", "mid-range-review", "higher-invest"],
)
def test_prediction_endpoint_preserves_all_golden_outputs(
    api_client,
    case_name,
):
    case = GOLDEN_PREDICTION_CASES[case_name]
    first = api_client.post("/predict", json=case["inputs"])
    second = api_client.post("/predict", json=case["inputs"])

    assert first.status_code == 200
    assert first.json() == second.json()
    body = first.json()
    assert body["predicted_investment_score"] == case["score"]
    assert body["recommendation"] == case["recommendation"]
    assert 0 <= body["predicted_investment_score"] <= 100


def test_prediction_response_contains_model_contributions_and_generated_fields(
    api_client,
):
    response = api_client.post(
        "/predict",
        json=GOLDEN_PREDICTION_CASES["review"]["inputs"],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["estimated_overall_risk_score"] == 48.4
    assert body["positive_contributions"]
    assert body["negative_contributions"]
    assert len(body["contributions"]) == 8
    assert all(
        "model contribution" in item.lower()
        for item in (
            body["positive_contributions"] + body["negative_contributions"]
        )
    )
    assert body["generated_feature_summary"]["npv_million"] == 120.0
    assert "not financial advice" in body["disclaimer"].lower()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sector", "Oil"),
        ("risk_level", "Extreme"),
    ],
    ids=["sector", "level"],
)
def test_prediction_rejects_invalid_categories(api_client, field, value):
    payload = dict(GOLDEN_PREDICTION_CASES["review"]["inputs"])
    payload[field] = value

    response = api_client.post("/predict", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("investment_size_million", 19.99),
        ("investment_size_million", 5000.01),
        ("expected_roi_percent", -5.01),
        ("expected_roi_percent", 30.01),
        ("payback_period_years", 0.99),
        ("payback_period_years", 15.01),
    ],
    ids=[
        "investment-low",
        "investment-high",
        "roi-low",
        "roi-high",
        "payback-low",
        "payback-high",
    ],
)
def test_prediction_rejects_invalid_numeric_boundaries(
    api_client,
    field,
    value,
):
    payload = dict(GOLDEN_PREDICTION_CASES["review"]["inputs"])
    payload[field] = value

    response = api_client.post("/predict", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize("origin", DEFAULT_ALLOWED_ORIGINS)
def test_default_local_cors_origins_are_allowed(api_client, origin):
    response = api_client.options(
        "/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin


def test_environment_origins_extend_explicit_local_defaults(monkeypatch):
    monkeypatch.setenv(
        "ALLOWED_ORIGINS",
        "https://investment.example.com, https://preview.example.com",
    )

    settings = Settings.from_environment()

    assert settings.allowed_origins == (
        *DEFAULT_ALLOWED_ORIGINS,
        "https://investment.example.com",
        "https://preview.example.com",
    )
    assert "*" not in settings.allowed_origins


def test_standard_openapi_and_docs_endpoints_are_available(api_client):
    docs = api_client.get("/docs")
    schema = api_client.get("/openapi.json")

    assert docs.status_code == 200
    assert "swagger-ui" in docs.text.lower()
    assert schema.status_code == 200
    assert set(schema.json()["paths"]) == {
        "/health",
        "/overview",
        "/opportunities",
        "/opportunities/{opportunity_id}",
        "/predict",
    }
