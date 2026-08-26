from __future__ import annotations

import warnings

import pandas as pd
import pytest

from predict import (
    get_processed_feature_names,
    predict_investment_opportunity,
)
from tests.parity_helpers import (
    GOLDEN_PREDICTION_CASES,
    RAW_MODEL_FIELDS,
    predict_without_version_warnings,
)


@pytest.mark.parametrize(
    "case_name",
    [
        pytest.param("lower", id="lower-reject"),
        pytest.param("review", id="mid-range-review"),
        pytest.param("higher", id="higher-invest"),
    ],
)
def test_golden_predictions_are_exact_and_repeatable(
    raw_data, simplified_feature_builder, case_name
):
    case = GOLDEN_PREDICTION_CASES[case_name]
    model_input = simplified_feature_builder(raw_data, **case["inputs"])

    first = predict_without_version_warnings(
        predict_investment_opportunity, model_input
    )
    second = predict_without_version_warnings(
        predict_investment_opportunity, model_input
    )

    assert float(first.iloc[0]["predicted_investment_score"]) == case["score"]
    assert first.iloc[0]["recommendation"] == case["recommendation"]
    assert 0.0 <= first.iloc[0]["predicted_investment_score"] <= 100.0
    pd.testing.assert_frame_equal(first, second)


def test_public_inference_clips_raw_model_extremes(
    raw_data, simplified_feature_builder, model_and_preprocessor
):
    model, preprocessor = model_and_preprocessor
    processed_feature_names = get_processed_feature_names(preprocessor)

    def raw_prediction(case_name):
        model_input = simplified_feature_builder(
            raw_data, **GOLDEN_PREDICTION_CASES[case_name]["inputs"]
        )
        transformed = pd.DataFrame(
            preprocessor.transform(model_input),
            columns=processed_feature_names,
        )
        return model_input, float(model.predict(transformed)[0])

    lower_input, lower_raw_score = raw_prediction("lower")
    higher_input, higher_raw_score = raw_prediction("higher")
    lower_result = predict_without_version_warnings(
        predict_investment_opportunity, lower_input
    )
    higher_result = predict_without_version_warnings(
        predict_investment_opportunity, higher_input
    )

    assert lower_raw_score < 0.0
    assert higher_raw_score > 100.0
    assert float(lower_result.iloc[0]["predicted_investment_score"]) == 0.0
    assert float(higher_result.iloc[0]["predicted_investment_score"]) == 100.0


def test_model_and_preprocessor_artifacts_load(model_and_preprocessor):
    model, preprocessor = model_and_preprocessor
    assert type(model).__name__ == "Ridge"
    assert type(preprocessor).__name__ == "ColumnTransformer"


def test_artifact_feature_contract_is_38_raw_to_56_processed(
    raw_data,
    simplified_feature_builder,
    model_and_preprocessor,
):
    model, preprocessor = model_and_preprocessor
    model_input = simplified_feature_builder(
        raw_data, **GOLDEN_PREDICTION_CASES["review"]["inputs"]
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        transformed = preprocessor.transform(model_input)

    assert preprocessor.n_features_in_ == 38
    assert preprocessor.feature_names_in_.tolist() == RAW_MODEL_FIELDS
    assert model_input.columns.tolist() == RAW_MODEL_FIELDS
    assert transformed.shape == (1, 56)
    assert model.n_features_in_ == 56
    assert len(get_processed_feature_names(preprocessor)) == 56
