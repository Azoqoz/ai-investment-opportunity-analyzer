"""Canonical recommendation scoring semantics for the migrated backend."""


def get_recommendation(score: float) -> str:
    """Map a 0-100 score to the current recommendation category."""
    if score >= 75:
        return "Invest"
    if score >= 45:
        return "Review"
    return "Reject"
