"""FastAPI entry point for the Investment Opportunity Analyzer."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.routes import health, opportunities, overview, predict
from .core.config import Settings, get_settings
from .services.data_service import load_opportunities
from .services.inference import get_inference_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load and verify reusable dataset and model resources once."""
    try:
        opportunities_data = load_opportunities()
        inference_service = get_inference_service()
        if opportunities_data.empty:
            raise RuntimeError("The opportunity dataset is empty")
        if inference_service.model is None:
            raise RuntimeError("The model artifact did not load")
        if inference_service.preprocessor is None:
            raise RuntimeError("The preprocessor artifact did not load")
    except Exception as exc:
        raise RuntimeError(
            "FastAPI startup failed while loading required resources"
        ) from exc

    app.state.opportunities = opportunities_data
    app.state.inference_service = inference_service
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the configured FastAPI application."""
    runtime_settings = settings or get_settings()
    application = FastAPI(
        title="AI Investment Opportunity Analyzer API",
        description=(
            "HTTP access to current synthetic opportunity data and the "
            "existing Ridge prediction pipeline."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )
    application.state.settings = runtime_settings
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(runtime_settings.allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    application.include_router(health.router)
    application.include_router(overview.router)
    application.include_router(opportunities.router)
    application.include_router(predict.router)

    @application.exception_handler(Exception)
    async def unexpected_error_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        del request, exc
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return application


app = create_app()
