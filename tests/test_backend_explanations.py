from __future__ import annotations

import pandas as pd

from backend.app.services.explanations import (
    explain_model_contributions,
    summarize_model_contributions,
)
from backend.app.services.feature_builder import (
    build_simplified_prediction_input,
)
from tests.parity_helpers import GOLDEN_PREDICTION_CASES


def test_backend_explanation_preserves_ridge_contribution_calculation(
    raw_data,
    model_and_preprocessor,
):
    model, preprocessor = model_and_preprocessor
    model_input = build_simplified_prediction_input(
        raw_data,
        **GOLDEN_PREDICTION_CASES["review"]["inputs"],
    )
    actual = explain_model_contributions(
        model_input,
        model,
        preprocessor,
        top_n=8,
    )

    processed = preprocessor.transform(model_input)
    numerical = list(preprocessor.transformers_[0][2])
    categorical = preprocessor.transformers_[1][2]
    encoded = (
        preprocessor.named_transformers_["cat"]
        .named_steps["onehot"]
        .get_feature_names_out(categorical)
        .tolist()
    )
    row = pd.Series(processed[0], index=numerical + encoded)
    expected = pd.DataFrame(
        {
            "feature": row.index,
            "value": row.values,
            "coefficient": model.coef_,
            "contribution": row.values * model.coef_,
        }
    )
    expected["absolute_contribution"] = expected["contribution"].abs()
    expected = expected.sort_values(
        "absolute_contribution",
        ascending=False,
    ).head(8)

    pd.testing.assert_frame_equal(
        actual[
            [
                "feature",
                "value",
                "coefficient",
                "contribution",
                "absolute_contribution",
            ]
        ],
        expected,
    )


def test_backend_explanation_uses_safe_model_contribution_language(
    raw_data,
    model_and_preprocessor,
):
    model, preprocessor = model_and_preprocessor
    model_input = build_simplified_prediction_input(
        raw_data,
        **GOLDEN_PREDICTION_CASES["review"]["inputs"],
    )
    contributions = explain_model_contributions(
        model_input,
        model,
        preprocessor,
        top_n=8,
    )
    positive, negative = summarize_model_contributions(contributions)
    text = " ".join(positive + negative).casefold()

    assert positive
    assert negative
    assert "model contribution" in text
    assert "caused" not in text
    assert "guarantees" not in text
    assert "investment success" not in text
