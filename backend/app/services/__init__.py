"""Reusable data, scoring, feature, inference, and explanation services."""

from .data_service import (
    OpportunityPage,
    filter_opportunities,
    get_opportunity_by_id,
    get_investment_score_distribution,
    get_overview_aggregates,
    get_recommendation_distribution,
    get_region_averages,
    get_sector_averages,
    load_opportunities,
    paginate_opportunities,
    query_opportunities,
    rank_opportunities,
)
from .feature_builder import build_simplified_prediction_input
from .inference import InferenceService, get_inference_service
from .scoring import get_recommendation

__all__ = [
    "InferenceService",
    "OpportunityPage",
    "build_simplified_prediction_input",
    "filter_opportunities",
    "get_inference_service",
    "get_investment_score_distribution",
    "get_opportunity_by_id",
    "get_overview_aggregates",
    "get_recommendation",
    "get_recommendation_distribution",
    "get_region_averages",
    "get_sector_averages",
    "load_opportunities",
    "paginate_opportunities",
    "query_opportunities",
    "rank_opportunities",
]
