import pytest

from backend.app.services.scoring import get_recommendation
from predict import assign_recommendation


@pytest.mark.parametrize(
    "score",
    [
        pytest.param(44.99, id="below-review"),
        pytest.param(45.00, id="at-review"),
        pytest.param(74.99, id="below-invest"),
        pytest.param(75.00, id="at-invest"),
    ],
)
def test_backend_recommendation_matches_current_logic(score):
    assert get_recommendation(score) == assign_recommendation(score)
