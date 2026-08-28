from __future__ import annotations

import csv
from collections import Counter
from decimal import Decimal


def test_raw_dataset_row_count_and_unique_opportunity_ids(raw_data):
    assert len(raw_data) == 5000
    assert raw_data["opportunity_id"].is_unique


def test_raw_dataset_recommendation_distribution(raw_data):
    assert raw_data["recommendation"].value_counts().to_dict() == {
        "Invest": 845,
        "Review": 2235,
        "Reject": 1920,
    }


def test_raw_dataset_exact_average_scores(project_root):
    data_path = (
        project_root
        / "data"
        / "raw"
        / "synthetic_investment_opportunities.csv"
    )
    with data_path.open(encoding="utf-8", newline="") as data_file:
        rows = list(csv.DictReader(data_file))

    row_count = Decimal(len(rows))
    average_investment_score = (
        sum(Decimal(row["investment_score"]) for row in rows) / row_count
    )
    average_overall_risk_score = (
        sum(Decimal(row["overall_risk_score"]) for row in rows) / row_count
    )

    assert average_investment_score == Decimal("51.67429")
    assert average_overall_risk_score == Decimal("43.360994")


def test_distribution_baseline_is_computed_from_current_csv(project_root):
    data_path = (
        project_root
        / "data"
        / "raw"
        / "synthetic_investment_opportunities.csv"
    )
    with data_path.open(encoding="utf-8", newline="") as data_file:
        current_counts = Counter(
            row["recommendation"] for row in csv.DictReader(data_file)
        )

    assert current_counts == Counter(Invest=845, Review=2235, Reject=1920)
