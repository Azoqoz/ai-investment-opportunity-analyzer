"""Framework-neutral access and query operations for the synthetic dataset."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "synthetic_investment_opportunities.csv"
)
RECOMMENDATION_ORDER = ["Invest", "Review", "Reject"]


@dataclass(frozen=True)
class OpportunityPage:
    """Pagination-ready result for an opportunity query."""

    items: pd.DataFrame
    page: int
    page_size: int
    total: int
    total_pages: int


def load_opportunities(data_file: str | Path | None = None) -> pd.DataFrame:
    """Load the current raw synthetic opportunity CSV from a robust path."""
    path = Path(data_file) if data_file is not None else DEFAULT_DATA_FILE
    return pd.read_csv(path)


def get_overview_aggregates(frame: pd.DataFrame) -> dict[str, int | float]:
    """Return the four aggregates currently displayed by the application."""
    return {
        "total_opportunities": len(frame),
        "average_investment_score": float(frame["investment_score"].mean()),
        "average_overall_risk_score": float(frame["overall_risk_score"].mean()),
        "invest_opportunities": int((frame["recommendation"] == "Invest").sum()),
    }


def get_recommendation_distribution(frame: pd.DataFrame) -> pd.DataFrame:
    """Return recommendation counts in the application's display order."""
    distribution = (
        frame["recommendation"]
        .value_counts()
        .reindex(RECOMMENDATION_ORDER)
        .fillna(0)
        .astype(int)
        .rename_axis("recommendation")
        .reset_index(name="count")
    )
    return distribution


def get_sector_averages(frame: pd.DataFrame) -> pd.DataFrame:
    """Return average investment score by sector, highest first."""
    return (
        frame.groupby("sector")["investment_score"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )


def get_region_averages(frame: pd.DataFrame) -> pd.DataFrame:
    """Return average investment score by region, highest first."""
    return (
        frame.groupby("region")["investment_score"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
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
    """Apply the current sector, region, recommendation, and score filters."""
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


def rank_opportunities(frame: pd.DataFrame) -> pd.DataFrame:
    """Apply the current score, ROI, then risk ranking semantics."""
    return frame.sort_values(
        by=[
            "investment_score",
            "expected_roi_percent",
            "overall_risk_score",
        ],
        ascending=[False, False, True],
    )


def paginate_opportunities(
    frame: pd.DataFrame,
    *,
    page: int = 1,
    page_size: int = 10,
) -> OpportunityPage:
    """Return one page without changing opportunity ordering."""
    if page < 1:
        raise ValueError("page must be at least 1")
    if page_size < 1:
        raise ValueError("page_size must be at least 1")

    total = len(frame)
    start = (page - 1) * page_size
    stop = start + page_size
    total_pages = (total + page_size - 1) // page_size

    return OpportunityPage(
        items=frame.iloc[start:stop].copy(),
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


def query_opportunities(
    frame: pd.DataFrame,
    *,
    sector: str = "All",
    region: str = "All",
    recommendation: str = "All",
    minimum_score: float = 0,
    maximum_score: float = 100,
    page: int = 1,
    page_size: int = 10,
) -> OpportunityPage:
    """Filter, rank, and paginate opportunities using current semantics."""
    filtered = filter_opportunities(
        frame,
        sector=sector,
        region=region,
        recommendation=recommendation,
        minimum_score=minimum_score,
        maximum_score=maximum_score,
    )
    ranked = rank_opportunities(filtered)
    return paginate_opportunities(ranked, page=page, page_size=page_size)


def get_opportunity_by_id(
    frame: pd.DataFrame,
    opportunity_id: str,
) -> pd.Series | None:
    """Return the stored dataset row for an opportunity ID, if present."""
    matches = frame[frame["opportunity_id"] == opportunity_id]
    if matches.empty:
        return None
    return matches.iloc[0].copy()
