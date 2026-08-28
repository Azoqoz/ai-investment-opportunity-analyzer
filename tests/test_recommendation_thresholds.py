import pytest

from predict import assign_recommendation


@pytest.mark.parametrize(
    ("score", "expected_recommendation"),
    [
        pytest.param(44.99, "Reject", id="below-review-boundary"),
        pytest.param(45.00, "Review", id="at-review-boundary"),
        pytest.param(74.99, "Review", id="below-invest-boundary"),
        pytest.param(75.00, "Invest", id="at-invest-boundary"),
    ],
)
def test_current_recommendation_boundaries(score, expected_recommendation):
    assert assign_recommendation(score) == expected_recommendation
