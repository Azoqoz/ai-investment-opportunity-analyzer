"""Current-dataset overview endpoint."""

from fastapi import APIRouter, Request

from ...schemas.common import SYNTHETIC_DATA_DISCLAIMER
from ...schemas.opportunity import OverviewResponse
from ...services.data_service import (
    RECOMMENDATION_ORDER,
    get_investment_score_distribution,
    get_overview_aggregates,
    get_recommendation_distribution,
    get_region_averages,
    get_sector_averages,
)


router = APIRouter(tags=["Overview"])


def _average_records(frame, category_column: str) -> list[dict]:
    return [
        {
            "category": row[category_column],
            "average_investment_score": float(row["investment_score"]),
        }
        for row in frame.to_dict(orient="records")
    ]


@router.get(
    "/overview",
    response_model=OverviewResponse,
    summary="Get current dataset overview",
)
def overview(request: Request) -> dict:
    """Compute frontend-ready overview data from the current raw dataset."""
    dataset = request.app.state.opportunities
    aggregates = get_overview_aggregates(dataset)
    distribution = get_recommendation_distribution(dataset)
    histogram = get_investment_score_distribution(dataset)
    sectors = get_sector_averages(dataset)
    regions = get_region_averages(dataset)

    return {
        **aggregates,
        "recommendation_distribution": distribution.to_dict(
            orient="records"
        ),
        "investment_score_distribution": histogram.to_dict(
            orient="records"
        ),
        "average_score_by_sector": _average_records(sectors, "sector"),
        "average_score_by_region": _average_records(regions, "region"),
        "available_sectors": sorted(dataset["sector"].unique().tolist()),
        "available_regions": sorted(dataset["region"].unique().tolist()),
        "recommendation_options": RECOMMENDATION_ORDER,
        "disclaimer": SYNTHETIC_DATA_DISCLAIMER,
    }
