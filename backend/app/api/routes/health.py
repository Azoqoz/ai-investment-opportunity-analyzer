"""Service readiness endpoint."""

from fastapi import APIRouter, Request

from ...schemas.common import HealthResponse


router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check backend readiness",
)
def health(request: Request) -> HealthResponse:
    """Report whether startup resources are ready without exposing paths."""
    dataset = request.app.state.opportunities
    inference = request.app.state.inference_service
    return HealthResponse(
        status="ok",
        data_loaded=dataset is not None,
        model_loaded=inference.model is not None,
        preprocessor_loaded=inference.preprocessor is not None,
        dataset_rows=len(dataset),
    )
