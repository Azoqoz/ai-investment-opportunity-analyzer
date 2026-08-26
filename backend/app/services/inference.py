"""Cached, framework-neutral inference for scikit-learn 1.8.0 artifacts."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .scoring import get_recommendation


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "best_model.pkl"
DEFAULT_PREPROCESSOR_PATH = PROJECT_ROOT / "models" / "preprocessor.pkl"
ARTIFACT_SKLEARN_VERSION = "1.8.0"


def get_processed_feature_names(preprocessor) -> list[str]:
    """Return the current 56 processed feature names in model order."""
    numerical_features = preprocessor.transformers_[0][2]
    categorical_features = preprocessor.transformers_[1][2]

    encoded_categorical_features = (
        preprocessor.named_transformers_["cat"]
        .named_steps["onehot"]
        .get_feature_names_out(categorical_features)
        .tolist()
    )

    return list(numerical_features) + encoded_categorical_features


class InferenceService:
    """Load trusted artifacts once and reproduce the current prediction behavior."""

    def __init__(
        self,
        model_path: str | Path = DEFAULT_MODEL_PATH,
        preprocessor_path: str | Path = DEFAULT_PREPROCESSOR_PATH,
    ) -> None:
        self.model_path = Path(model_path)
        self.preprocessor_path = Path(preprocessor_path)
        self.model = joblib.load(self.model_path)
        self.preprocessor = joblib.load(self.preprocessor_path)
        self.processed_feature_names = get_processed_feature_names(
            self.preprocessor
        )

    def transform(self, input_data: pd.DataFrame) -> pd.DataFrame:
        """Apply the fitted preprocessor and preserve trained feature names."""
        processed_data = self.preprocessor.transform(input_data)
        return pd.DataFrame(
            processed_data,
            columns=self.processed_feature_names,
        )

    def predict(self, input_data: pd.DataFrame) -> pd.DataFrame:
        """Predict, clip, round, and categorize exactly like the current app."""
        processed_data = self.transform(input_data)
        predicted_scores = self.model.predict(processed_data)
        predicted_scores = np.clip(predicted_scores, 0, 100)

        results = input_data.copy()
        results["predicted_investment_score"] = np.round(predicted_scores, 2)
        results["recommendation"] = results[
            "predicted_investment_score"
        ].apply(get_recommendation)
        return results


@lru_cache(maxsize=1)
def get_inference_service() -> InferenceService:
    """Return the process-wide default service without reloading artifacts."""
    return InferenceService()
