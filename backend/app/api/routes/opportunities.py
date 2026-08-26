"""Stored synthetic opportunity query endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request

from ...schemas.common import SYNTHETIC_DATA_DISCLAIMER
from ...schemas.opportunity import (
    OpportunityDetailResponse,
    OpportunityListResponse,
)
from ...schemas.prediction import Recommendation, Region, Sector
from ...services.data_service import get_opportunity_by_id, query_opportunities


router = APIRouter(prefix="/opportunities", tags=["Opportunities"])
LIST_FIELDS = [
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
]


@router.get(
    "",
    response_model=OpportunityListResponse,
    summary="Filter and rank opportunities",
)
def list_opportunities(
    request: Request,
    sector: Sector | None = None,
    region: Region | None = None,
    recommendation: Recommendation | None = None,
    min_score: Annotated[float, Query(ge=0, le=100)] = 0,
    max_score: Annotated[float, Query(ge=0, le=100)] = 100,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> dict:
    """Apply inclusive filters and the current three-key ranking."""
    if min_score > max_score:
        raise HTTPException(
            status_code=422,
            detail="min_score must be less than or equal to max_score",
        )

    result = query_opportunities(
        request.app.state.opportunities,
        sector=sector or "All",
        region=region or "All",
        recommendation=recommendation or "All",
        minimum_score=min_score,
        maximum_score=max_score,
        page=page,
        page_size=page_size,
    )
    return {
        "items": result.items[LIST_FIELDS].to_dict(orient="records"),
        "page": result.page,
        "page_size": result.page_size,
        "total": result.total,
        "total_pages": result.total_pages,
    }


@router.get(
    "/{opportunity_id}",
    response_model=OpportunityDetailResponse,
    summary="Get one stored synthetic opportunity",
)
def opportunity_detail(request: Request, opportunity_id: str) -> dict:
    """Return a dataset opportunity without describing its score as predicted."""
    row = get_opportunity_by_id(
        request.app.state.opportunities,
        opportunity_id,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    return {
        "identity": {
            field: row[field]
            for field in [
                "opportunity_id",
                "opportunity_name",
                "sector",
                "region",
            ]
        },
        "financials": {
            field: row[field]
            for field in [
                "investment_size_million",
                "expected_roi_percent",
                "payback_period_years",
                "profit_margin_percent",
            ]
        },
        "stored_synthetic_evaluation": {
            field: row[field]
            for field in [
                "investment_score",
                "recommendation",
                "overall_risk_score",
                "strategic_impact_score",
                "sustainability_score",
                "market_attractiveness_score",
                "financial_strength_score",
            ]
        },
        "disclaimer": SYNTHETIC_DATA_DISCLAIMER,
    }
