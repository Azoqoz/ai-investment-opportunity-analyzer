import pandas as pd


def clean_feature_name(feature: str) -> str:
    """
    Convert technical feature names into readable text.
    """
    return feature.replace("_", " ")


def explain_linear_prediction(row: pd.Series, model, top_n: int = 5) -> pd.DataFrame:
    """
    Explain a single prediction from a linear model using feature contributions.
    Contribution = processed feature value * model coefficient.
    """
    coefficients = model.coef_

    contributions = pd.DataFrame({
        "feature": row.index,
        "value": row.values,
        "coefficient": coefficients,
        "contribution": row.values * coefficients
    })

    contributions["absolute_contribution"] = contributions["contribution"].abs()

    return contributions.sort_values(
        by="absolute_contribution",
        ascending=False
    ).head(top_n)


def generate_reason_text(local_explanation: pd.DataFrame):
    """
    Generate readable positive and negative explanation text.
    """
    positive_reasons = []
    negative_reasons = []

    for _, row in local_explanation.iterrows():
        feature = clean_feature_name(row["feature"])
        contribution = row["contribution"]

        if contribution > 0:
            positive_reasons.append(
                f"{feature} contributed positively to the predicted investment score."
            )
        else:
            negative_reasons.append(
                f"{feature} contributed negatively to the predicted investment score."
            )

    return positive_reasons, negative_reasons