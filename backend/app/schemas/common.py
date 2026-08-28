"""Shared API schemas and constants."""

from __future__ import annotations

from pydantic import BaseModel


SYNTHETIC_DATA_DISCLAIMER = (
    "This application uses a synthetic dataset for educational and portfolio "
    "purposes. It is not financial advice."
)


class HealthResponse(BaseModel):
    status: str
    data_loaded: bool
    model_loaded: bool
    preprocessor_loaded: bool
    dataset_rows: int


class RecommendationCount(BaseModel):
    recommendation: str
    count: int


class HistogramBin(BaseModel):
    bin_start: float
    bin_end: float
    count: int


class CategoryAverage(BaseModel):
    category: str
    average_investment_score: float
