from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pandas as pd
import pytest

from tests.parity_helpers import load_streamlit_feature_builder


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def raw_data(project_root: Path) -> pd.DataFrame:
    return pd.read_csv(
        project_root / "data" / "raw" / "synthetic_investment_opportunities.csv"
    )


@pytest.fixture(scope="session")
def simplified_feature_builder(project_root: Path):
    return load_streamlit_feature_builder(project_root)


@pytest.fixture(scope="session")
def model_and_preprocessor():
    from predict import load_model_and_preprocessor

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return load_model_and_preprocessor()
