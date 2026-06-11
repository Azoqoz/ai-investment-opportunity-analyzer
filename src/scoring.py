def assign_recommendation(score: float) -> str:
    """
    Convert investment score into recommendation category.
    """
    if score >= 75:
        return "Invest"
    elif score >= 45:
        return "Review"
    else:
        return "Reject"


def format_score(score: float) -> str:
    """
    Format score as a user-friendly 0-100 score.
    """
    return f"{round(score, 2)}/100"