from pathlib import Path
import joblib
import pandas as pd
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_PATH = PROJECT_ROOT / "models"

MODEL_PATH = MODELS_PATH / "best_model.pkl"
PREPROCESSOR_PATH = MODELS_PATH / "preprocessor.pkl"


def load_model_and_preprocessor():
    """
    Load the trained model and fitted preprocessor.
    """
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    return model, preprocessor


def assign_recommendation(score: float) -> str:
    """
    Convert predicted investment score into recommendation category.
    """
    if score >= 75:
        return "Invest"
    elif score >= 45:
        return "Review"
    else:
        return "Reject"


def get_processed_feature_names(preprocessor):
    """
    Get feature names after preprocessing.

    This is needed because the model was trained using a DataFrame
    with processed feature names.
    """
    numerical_features = preprocessor.transformers_[0][2]
    categorical_features = preprocessor.transformers_[1][2]

    encoded_categorical_features = (
        preprocessor
        .named_transformers_["cat"]
        .named_steps["onehot"]
        .get_feature_names_out(categorical_features)
        .tolist()
    )

    processed_feature_names = list(numerical_features) + encoded_categorical_features

    return processed_feature_names


def predict_investment_opportunity(input_data: pd.DataFrame) -> pd.DataFrame:
    """
    Predict investment score and recommendation for new investment opportunities.

    Parameters
    ----------
    input_data : pd.DataFrame
        Raw input data containing the same feature columns used during training.

    Returns
    -------
    pd.DataFrame
        DataFrame with predicted investment score and recommendation.
    """
    model, preprocessor = load_model_and_preprocessor()

    processed_data = preprocessor.transform(input_data)

    processed_feature_names = get_processed_feature_names(preprocessor)

    processed_data_df = pd.DataFrame(
        processed_data,
        columns=processed_feature_names
    )

    predicted_scores = model.predict(processed_data_df)
    predicted_scores = np.clip(predicted_scores, 0, 100)

    results = input_data.copy()
    results["predicted_investment_score"] = np.round(predicted_scores, 2)
    results["recommendation"] = results["predicted_investment_score"].apply(
        assign_recommendation
    )

    return results