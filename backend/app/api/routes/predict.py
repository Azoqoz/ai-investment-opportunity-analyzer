"""Simplified model-prediction endpoint."""

from fastapi import APIRouter, HTTPException, Request

from ...schemas.common import SYNTHETIC_DATA_DISCLAIMER
from ...schemas.prediction import PredictionRequest, PredictionResponse
from ...services.explanations import (
    explain_model_contributions,
    summarize_model_contributions,
)
from ...services.feature_builder import build_simplified_prediction_input


router = APIRouter(tags=["Prediction"])
SUMMARY_FIELDS = [
    "sector",
    "region",
    "competition_level",
    "investment_size_million",
    "expected_roi_percent",
    "irr_percent",
    "npv_million",
    "payback_period_years",
    "overall_risk_score",
    "market_attractiveness_score",
    "financial_strength_score",
    "strategic_impact_score",
    "sustainability_score",
]


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict a simplified opportunity score",
)
def predict(request: Request, payload: PredictionRequest) -> dict:
    """Build 38 fields and run the cached preprocessor and Ridge model."""
    try:
        prediction_input = build_simplified_prediction_input(
            request.app.state.opportunities,
            **payload.model_dump(),
        )
        inference = request.app.state.inference_service
        prediction = inference.predict(prediction_input).iloc[0]
        explanation = explain_model_contributions(
            prediction_input,
            inference.model,
            inference.preprocessor,
        )
        positive, negative = summarize_model_contributions(explanation)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Prediction service is unavailable",
        ) from exc

    contributions = []
    for row in explanation.to_dict(orient="records"):
        contributions.append(
            {
                "feature": row["feature"],
                "readable_feature": row["readable_feature"],
                "value": float(row["value"]),
                "coefficient": float(row["coefficient"]),
                "contribution": float(row["contribution"]),
                "direction": (
                    "positive" if row["contribution"] > 0 else "negative"
                ),
            }
        )

    input_row = prediction_input.iloc[0]
    return {
        "predicted_investment_score": float(
            prediction["predicted_investment_score"]
        ),
        "recommendation": prediction["recommendation"],
        "estimated_overall_risk_score": float(
            input_row["overall_risk_score"]
        ),
        "positive_contributions": positive,
        "negative_contributions": negative,
        "contributions": contributions,
        "generated_feature_summary": {
            field: input_row[field] for field in SUMMARY_FIELDS
        },
        "disclaimer": SYNTHETIC_DATA_DISCLAIMER,
    }
