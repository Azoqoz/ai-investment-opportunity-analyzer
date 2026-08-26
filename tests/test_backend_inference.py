from __future__ import annotations

import warnings

import pandas as pd
import pytest

from backend.app.services.feature_builder import (
    build_simplified_prediction_input,
)
from backend.app.services.inference import (
    ARTIFACT_SKLEARN_VERSION,
    InferenceService,
    get_inference_service,
)
from tests.parity_helpers import GOLDEN_PREDICTION_CASES, RAW_MODEL_FIELDS


@pytest.fixture(scope="module")
def backend_inference_service():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return InferenceService()


def test_backend_records_artifact_sklearn_compatibility_version():
    assert ARTIFACT_SKLEARN_VERSION == "1.8.0"


def test_default_backend_inference_service_is_cached():
    get_inference_service.cache_clear()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        first = get_inference_service()
        second = get_inference_service()
    assert first is second


def test_backend_inference_artifact_contract(
    raw_data,
    backend_inference_service,
):
    model_input = build_simplified_prediction_input(
        raw_data,
        **GOLDEN_PREDICTION_CASES["review"]["inputs"],
    )
    transformed = backend_inference_service.transform(model_input)

    assert model_input.columns.tolist() == RAW_MODEL_FIELDS
    assert backend_inference_service.preprocessor.n_features_in_ == 38
    assert (
        backend_inference_service.preprocessor.feature_names_in_.tolist()
        == RAW_MODEL_FIELDS
    )
    assert transformed.shape == (1, 56)
    assert backend_inference_service.model.n_features_in_ == 56


@pytest.mark.parametrize(
    "case_name",
    [
        pytest.param("lower", id="lower-reject"),
        pytest.param("review", id="mid-range-review"),
        pytest.param("higher", id="higher-invest"),
    ],
)
def test_backend_golden_predictions_are_exact_and_repeatable(
    raw_data,
    backend_inference_service,
    case_name,
):
    case = GOLDEN_PREDICTION_CASES[case_name]
    model_input = build_simplified_prediction_input(raw_data, **case["inputs"])

    first = backend_inference_service.predict(model_input)
    second = backend_inference_service.predict(model_input)

    assert float(first.iloc[0]["predicted_investment_score"]) == case["score"]
    assert first.iloc[0]["recommendation"] == case["recommendation"]
    assert 0.0 <= float(first.iloc[0]["predicted_investment_score"]) <= 100.0
    pd.testing.assert_frame_equal(first, second)


def test_backend_inference_clips_both_raw_model_extremes(
    raw_data,
    backend_inference_service,
):
    lower_input = build_simplified_prediction_input(
        raw_data,
        **GOLDEN_PREDICTION_CASES["lower"]["inputs"],
    )
    higher_input = build_simplified_prediction_input(
        raw_data,
        **GOLDEN_PREDICTION_CASES["higher"]["inputs"],
    )

    lower_raw = float(
        backend_inference_service.model.predict(
            backend_inference_service.transform(lower_input)
        )[0]
    )
    higher_raw = float(
        backend_inference_service.model.predict(
            backend_inference_service.transform(higher_input)
        )[0]
    )
    lower_result = backend_inference_service.predict(lower_input)
    higher_result = backend_inference_service.predict(higher_input)

    assert lower_raw < 0.0
    assert higher_raw > 100.0
    assert float(lower_result.iloc[0]["predicted_investment_score"]) == 0.0
    assert lower_result.iloc[0]["recommendation"] == "Reject"
    assert float(higher_result.iloc[0]["predicted_investment_score"]) == 100.0
    assert higher_result.iloc[0]["recommendation"] == "Invest"
