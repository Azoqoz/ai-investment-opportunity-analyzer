from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Investment Opportunity Analyzer",
    page_icon="📊",
    layout="wide"
)


# ---------------------------------------------------------
# Custom styling
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    .main {
        background-color: #0E1117;
    }

    div[data-testid="stAppViewContainer"] {
        overflow: visible;
    }

    .block-container {
        padding-top: 4rem;
        padding-bottom: 2rem;
        max-width: 1500px;
        overflow: visible;
    }

    h1 {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        color: #F8FAFC !important;
        margin-bottom: 0.4rem !important;
    }

    h2, h3, h4 {
        color: #F8FAFC !important;
        font-weight: 700 !important;
    }

    p, li, label, div {
        color: #E5E7EB;
    }

    .hero-card {
        background: linear-gradient(135deg, #111827 0%, #1F2937 60%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        margin-top: 0.4rem;
        margin-bottom: 1.2rem;
        overflow: visible;
    }

    .hero-subtitle {
        font-size: 1rem;
        color: #CBD5E1;
        margin-top: 0.4rem;
        line-height: 1.6;
    }

    .disclaimer-card {
        background-color: rgba(30, 64, 175, 0.22);
        border: 1px solid rgba(96, 165, 250, 0.35);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        margin-top: 1rem;
        margin-bottom: 1.2rem;
        color: #BFDBFE;
    }

    .kpi-card {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.18);
        min-height: 125px;
    }

    .kpi-label {
        color: #9CA3AF;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }

    .kpi-value {
        color: #F9FAFB;
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .kpi-caption {
        color: #94A3B8;
        font-size: 0.78rem;
    }

    .invest-badge {
        background-color: rgba(34, 197, 94, 0.14);
        color: #86EFAC;
        border: 1px solid rgba(34, 197, 94, 0.45);
        border-radius: 999px;
        padding: 0.25rem 0.7rem;
        font-size: 0.85rem;
        font-weight: 700;
    }

    .review-badge {
        background-color: rgba(245, 158, 11, 0.14);
        color: #FCD34D;
        border: 1px solid rgba(245, 158, 11, 0.45);
        border-radius: 999px;
        padding: 0.25rem 0.7rem;
        font-size: 0.85rem;
        font-weight: 700;
    }

    .reject-badge {
        background-color: rgba(239, 68, 68, 0.14);
        color: #FCA5A5;
        border: 1px solid rgba(239, 68, 68, 0.45);
        border-radius: 999px;
        padding: 0.25rem 0.7rem;
        font-size: 0.85rem;
        font-weight: 700;
    }

    div[data-testid="stTabs"] button {
        font-weight: 700;
    }

    div[data-testid="stMetricValue"] {
        color: #F8FAFC;
    }

    div[data-testid="stMetricLabel"] {
        color: #CBD5E1;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #334155;
        border-radius: 12px;
    }

    .stAlert {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"
REPORTS_PATH = PROJECT_ROOT / "reports"
SRC_PATH = PROJECT_ROOT / "src"
MODELS_PATH = PROJECT_ROOT / "models"

sys.path.append(str(SRC_PATH))

from predict import predict_investment_opportunity


DATA_FILE = RAW_DATA_PATH / "synthetic_investment_opportunities.csv"
MODEL_COMPARISON_FILE = REPORTS_PATH / "model_comparison_results.csv"
MODEL_FILE = MODELS_PATH / "best_model.pkl"
PREPROCESSOR_FILE = MODELS_PATH / "preprocessor.pkl"


# ---------------------------------------------------------
# Load data and models
# ---------------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)


@st.cache_data
def load_model_results():
    if MODEL_COMPARISON_FILE.exists():
        return pd.read_csv(MODEL_COMPARISON_FILE)
    return None


@st.cache_resource
def load_model_and_preprocessor():
    model = joblib.load(MODEL_FILE)
    preprocessor = joblib.load(PREPROCESSOR_FILE)
    return model, preprocessor


df = load_data()
model_results = load_model_results()
model, preprocessor = load_model_and_preprocessor()


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------
def format_number(value):
    return f"{value:,.0f}"


def format_score(value):
    return f"{value:.2f}"


def recommendation_badge(recommendation):
    if recommendation == "Invest":
        return '<span class="invest-badge">Invest</span>'
    if recommendation == "Review":
        return '<span class="review-badge">Review</span>'
    return '<span class="reject-badge">Reject</span>'


def get_recommendation_color_map():
    return {
        "Invest": "#22C55E",
        "Review": "#F59E0B",
        "Reject": "#EF4444"
    }


def get_primary_chart_color():
    return "#60A5FA"


def get_processed_feature_names(preprocessor):
    numerical_features = preprocessor.transformers_[0][2]
    categorical_features = preprocessor.transformers_[1][2]

    encoded_categorical_features = (
        preprocessor
        .named_transformers_["cat"]
        .named_steps["onehot"]
        .get_feature_names_out(categorical_features)
        .tolist()
    )

    return list(numerical_features) + encoded_categorical_features


def clean_feature_name(feature):
    readable_names = {
        "competition_level_Low": "Low competition",
        "competition_level_Medium": "Medium competition",
        "competition_level_High": "High competition",
        "expected_roi_percent": "Expected ROI",
        "irr_percent": "IRR",
        "npv_million": "NPV",
        "payback_period_years": "Payback period",
        "overall_risk_score": "Overall risk",
        "market_attractiveness_score": "Market attractiveness",
        "financial_strength_score": "Financial strength",
        "strategic_impact_score": "Strategic impact",
        "sustainability_score": "Sustainability",
        "market_growth_percent": "Market growth",
        "demand_score": "Market demand",
        "customer_adoption_score": "Customer adoption",
        "scalability_score": "Scalability",
        "profit_margin_percent": "Profit margin",
        "job_creation_score": "Job creation",
        "quality_of_life_score": "Quality of life",
        "localization_score": "Localization",
        "economic_diversification_score": "Economic diversification",
        "vision_2030_alignment_score": "Vision 2030 alignment",
        "region_Riyadh": "Region: Riyadh",
        "region_Asir": "Region: Asir",
        "region_Makkah": "Region: Makkah",
        "region_Madinah": "Region: Madinah",
        "region_Tabuk": "Region: Tabuk",
        "region_Qassim": "Region: Qassim",
        "region_Jazan": "Region: Jazan",
        "region_Eastern Province": "Region: Eastern Province",
        "sector_Technology": "Sector: Technology",
        "sector_Real Estate": "Sector: Real Estate",
        "sector_Tourism": "Sector: Tourism",
        "sector_Entertainment": "Sector: Entertainment",
        "sector_Healthcare": "Sector: Healthcare",
        "sector_Logistics": "Sector: Logistics",
        "sector_Renewable Energy": "Sector: Renewable Energy",
        "sector_Education": "Sector: Education",
        "sector_Retail": "Sector: Retail",
        "sector_Infrastructure": "Sector: Infrastructure",
    }

    if feature in readable_names:
        return readable_names[feature]

    return feature.replace("_", " ")


def explain_prediction(input_data, model, preprocessor, top_n=8):
    processed_data = preprocessor.transform(input_data)
    processed_feature_names = get_processed_feature_names(preprocessor)

    processed_df = pd.DataFrame(
        processed_data,
        columns=processed_feature_names
    )

    row = processed_df.iloc[0]
    coefficients = model.coef_

    explanation = pd.DataFrame({
        "feature": row.index,
        "value": row.values,
        "coefficient": coefficients,
        "contribution": row.values * coefficients
    })

    explanation["absolute_contribution"] = explanation["contribution"].abs()

    explanation = explanation.sort_values(
        by="absolute_contribution",
        ascending=False
    ).head(top_n)

    explanation["readable_feature"] = explanation["feature"].apply(clean_feature_name)

    return explanation


def generate_reason_text(local_explanation):
    positive_reasons = []
    negative_reasons = []

    for _, row in local_explanation.iterrows():
        feature = row["readable_feature"]
        contribution = row["contribution"]

        if contribution > 0:
            positive_reasons.append(f"{feature} helped improve the score.")
        else:
            negative_reasons.append(f"{feature} lowered the score.")

    return positive_reasons, negative_reasons


def score_from_level(level, low=35, medium=60, high=85):
    mapping = {
        "Low": low,
        "Medium": medium,
        "High": high
    }
    return mapping[level]


def risk_from_level(level):
    mapping = {
        "Low": 25,
        "Medium": 50,
        "High": 75
    }
    return mapping[level]


def clip_value(value, lower, upper):
    return max(lower, min(value, upper))


def build_simplified_prediction_input(
    base_df,
    sector,
    region,
    competition_level,
    investment_size_million,
    expected_roi_percent,
    payback_period_years,
    market_demand_level,
    risk_level,
    strategic_alignment_level,
    sustainability_level
):
    feature_columns = [
        col for col in base_df.columns
        if col not in [
            "opportunity_id",
            "opportunity_name",
            "investment_score",
            "recommendation"
        ]
    ]

    input_row = {}

    for col in feature_columns:
        if pd.api.types.is_numeric_dtype(base_df[col]):
            input_row[col] = base_df[col].median()
        else:
            input_row[col] = base_df[col].mode()[0]

    input_row["sector"] = sector
    input_row["region"] = region
    input_row["competition_level"] = competition_level

    market_score = score_from_level(market_demand_level, low=35, medium=65, high=90)
    risk_score = risk_from_level(risk_level)
    strategic_score = score_from_level(strategic_alignment_level, low=40, medium=70, high=90)
    sustainability_score = score_from_level(sustainability_level, low=40, medium=70, high=90)

    input_row["investment_size_million"] = investment_size_million
    input_row["expected_roi_percent"] = expected_roi_percent
    input_row["irr_percent"] = clip_value(expected_roi_percent + 2, -5, 35)
    input_row["payback_period_years"] = payback_period_years

    input_row["npv_million"] = round(
        investment_size_million * (expected_roi_percent / 100) * 4,
        2
    )

    input_row["npv_million"] = clip_value(
        input_row["npv_million"],
        -500,
        3000
    )

    input_row["revenue_growth_percent"] = clip_value(
        expected_roi_percent * 0.65,
        -5,
        25
    )

    input_row["profit_margin_percent"] = clip_value(
        expected_roi_percent + 6,
        -10,
        40
    )

    sector_median_market_size = (
        base_df[base_df["sector"] == sector]["market_size_billion"].median()
    )

    if np.isnan(sector_median_market_size):
        sector_median_market_size = base_df["market_size_billion"].median()

    input_row["market_size_billion"] = round(sector_median_market_size, 2)

    input_row["market_growth_percent"] = {
        "Low": 3,
        "Medium": 8,
        "High": 14
    }[market_demand_level]

    input_row["demand_score"] = market_score
    input_row["customer_adoption_score"] = clip_value(market_score - 5, 0, 100)
    input_row["scalability_score"] = clip_value(market_score + 3, 0, 100)

    input_row["financial_risk_score"] = clip_value(risk_score, 0, 100)
    input_row["regulatory_risk_score"] = clip_value(risk_score - 5, 0, 100)
    input_row["execution_risk_score"] = clip_value(risk_score + 5, 0, 100)
    input_row["market_risk_score"] = clip_value(risk_score, 0, 100)
    input_row["dependency_risk_score"] = clip_value(risk_score - 8, 0, 100)

    input_row["overall_risk_score"] = round(
        (
            input_row["financial_risk_score"]
            + input_row["regulatory_risk_score"]
            + input_row["execution_risk_score"]
            + input_row["market_risk_score"]
            + input_row["dependency_risk_score"]
        ) / 5,
        2
    )

    input_row["vision_2030_alignment_score"] = strategic_score
    input_row["economic_diversification_score"] = clip_value(strategic_score - 3, 0, 100)
    input_row["job_creation_score"] = clip_value(strategic_score - 5, 0, 100)
    input_row["localization_score"] = clip_value(strategic_score - 2, 0, 100)
    input_row["quality_of_life_score"] = clip_value(strategic_score, 0, 100)

    input_row["strategic_impact_score"] = round(
        (
            input_row["vision_2030_alignment_score"]
            + input_row["economic_diversification_score"]
            + input_row["job_creation_score"]
            + input_row["localization_score"]
            + input_row["quality_of_life_score"]
        ) / 5,
        2
    )

    input_row["environmental_impact_score"] = sustainability_score
    input_row["social_impact_score"] = clip_value(sustainability_score - 2, 0, 100)
    input_row["governance_score"] = clip_value(sustainability_score + 2, 0, 100)

    input_row["sustainability_score"] = round(
        (
            input_row["environmental_impact_score"]
            + input_row["social_impact_score"]
            + input_row["governance_score"]
        ) / 3,
        2
    )

    input_row["risk_adjusted_roi"] = round(
        expected_roi_percent / (input_row["overall_risk_score"] + 1),
        4
    )

    input_row["profitability_index"] = round(
        input_row["npv_million"] / (investment_size_million + 1),
        4
    )

    input_row["payback_efficiency"] = round(
        expected_roi_percent / (payback_period_years + 1),
        4
    )

    input_row["market_attractiveness_score"] = round(
        (
            (max(input_row["market_growth_percent"], 0) / 20) * 25
            + (input_row["demand_score"] / 100) * 25
            + (input_row["customer_adoption_score"] / 100) * 25
            + (input_row["scalability_score"] / 100) * 25
        ),
        2
    )

    input_row["financial_strength_score"] = round(
        (
            ((input_row["expected_roi_percent"] + 5) / 35) * 25
            + ((input_row["irr_percent"] + 5) / 40) * 25
            + ((input_row["npv_million"] + 500) / 3500) * 25
            + ((input_row["profit_margin_percent"] + 10) / 50) * 25
        ),
        2
    )

    prediction_input = pd.DataFrame([input_row])
    prediction_input = prediction_input[feature_columns]

    return prediction_input


def apply_chart_layout(fig, height=None):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#E5E7EB"),
        title_font=dict(size=18, color="#F8FAFC"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0)"
        ),
        margin=dict(l=20, r=20, t=60, b=30)
    )

    if height is not None:
        fig.update_layout(height=height)

    return fig


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown(
    """
    <div class="hero-card">
        <h1>AI Investment Opportunity Analyzer</h1>
        <div class="hero-subtitle">
            A machine learning decision-support system for evaluating synthetic investment opportunities.
            The system estimates an <b>Investment Score (0–100)</b> and classifies opportunities as
            <b>Invest</b>, <b>Review</b>, or <b>Reject</b>.
        </div>
        <div class="disclaimer-card">
            This dashboard uses a synthetic dataset for educational and portfolio purposes.
            It is not financial advice.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------
overview_tab, ranking_tab, analyzer_tab, prediction_tab, methodology_tab = st.tabs(
    [
        "Overview",
        "Opportunity Ranking",
        "Analyze Existing Opportunity",
        "Predict New Opportunity",
        "Methodology"
    ]
)


# ---------------------------------------------------------
# Tab 1: Overview
# ---------------------------------------------------------
with overview_tab:
    st.subheader("Executive Overview")

    total_opportunities = len(df)
    avg_score = df["investment_score"].mean()
    avg_risk = df["overall_risk_score"].mean()
    invest_count = (df["recommendation"] == "Invest").sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Opportunities</div>
                <div class="kpi-value">{format_number(total_opportunities)}</div>
                <div class="kpi-caption">Synthetic investment records</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Average Investment Score</div>
                <div class="kpi-value">{format_score(avg_score)}</div>
                <div class="kpi-caption">Score range: 0 to 100</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Average Risk Score</div>
                <div class="kpi-value">{format_score(avg_risk)}</div>
                <div class="kpi-caption">Lower risk is generally better</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Invest Opportunities</div>
                <div class="kpi-value">{format_number(invest_count)}</div>
                <div class="kpi-caption">Opportunities classified as Invest</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        recommendation_counts = (
            df["recommendation"]
            .value_counts()
            .reindex(["Invest", "Review", "Reject"])
            .fillna(0)
            .reset_index()
        )

        recommendation_counts.columns = ["Recommendation", "Count"]

        fig_recommendation = px.bar(
            recommendation_counts,
            x="Recommendation",
            y="Count",
            text="Count",
            color="Recommendation",
            color_discrete_map=get_recommendation_color_map(),
            title="Recommendation Distribution"
        )

        fig_recommendation.update_traces(textposition="outside")
        fig_recommendation = apply_chart_layout(fig_recommendation, height=420)
        st.plotly_chart(fig_recommendation, use_container_width=True)

    with chart_col2:
        fig_score_distribution = px.histogram(
            df,
            x="investment_score",
            nbins=30,
            title="Investment Score Distribution",
            color_discrete_sequence=[get_primary_chart_color()]
        )

        fig_score_distribution.update_layout(
            xaxis_title="Investment Score",
            yaxis_title="Number of Opportunities"
        )

        fig_score_distribution = apply_chart_layout(fig_score_distribution, height=420)
        st.plotly_chart(fig_score_distribution, use_container_width=True)

    st.divider()

    sector_col, region_col = st.columns(2)

    with sector_col:
        sector_score = (
            df.groupby("sector")["investment_score"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig_sector = px.bar(
            sector_score,
            x="investment_score",
            y="sector",
            orientation="h",
            title="Average Investment Score by Sector",
            color_discrete_sequence=[get_primary_chart_color()]
        )

        fig_sector.update_layout(
            xaxis_title="Average Investment Score",
            yaxis_title="Sector",
            yaxis={"categoryorder": "total ascending"}
        )

        fig_sector = apply_chart_layout(fig_sector, height=480)
        st.plotly_chart(fig_sector, use_container_width=True)

    with region_col:
        region_score = (
            df.groupby("region")["investment_score"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig_region = px.bar(
            region_score,
            x="investment_score",
            y="region",
            orientation="h",
            title="Average Investment Score by Region",
            color_discrete_sequence=[get_primary_chart_color()]
        )

        fig_region.update_layout(
            xaxis_title="Average Investment Score",
            yaxis_title="Region",
            yaxis={"categoryorder": "total ascending"}
        )

        fig_region = apply_chart_layout(fig_region, height=480)
        st.plotly_chart(fig_region, use_container_width=True)


# ---------------------------------------------------------
# Tab 2: Opportunity Ranking
# ---------------------------------------------------------
with ranking_tab:
    st.subheader("Opportunity Ranking")

    st.markdown(
        "Use the filters below to explore and rank investment opportunities."
    )

    with st.expander("Filter Opportunities", expanded=True):
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

        with filter_col1:
            selected_sector = st.selectbox(
                "Sector",
                options=["All"] + sorted(df["sector"].unique().tolist()),
                index=0,
                key="ranking_sector_filter"
            )

        with filter_col2:
            selected_region = st.selectbox(
                "Region",
                options=["All"] + sorted(df["region"].unique().tolist()),
                index=0,
                key="ranking_region_filter"
            )

        with filter_col3:
            selected_recommendation = st.selectbox(
                "Recommendation",
                options=["All", "Invest", "Review", "Reject"],
                index=0,
                key="ranking_recommendation_filter"
            )

        with filter_col4:
            score_range = st.slider(
                "Investment Score Range",
                min_value=0,
                max_value=100,
                value=(0, 100),
                key="ranking_score_filter"
            )

    ranking_df = df.copy()

    if selected_sector != "All":
        ranking_df = ranking_df[ranking_df["sector"] == selected_sector]

    if selected_region != "All":
        ranking_df = ranking_df[ranking_df["region"] == selected_region]

    if selected_recommendation != "All":
        ranking_df = ranking_df[
            ranking_df["recommendation"] == selected_recommendation
        ]

    ranking_df = ranking_df[
        ranking_df["investment_score"].between(score_range[0], score_range[1])
    ]

    st.caption(f"Showing {len(ranking_df):,} of {len(df):,} opportunities")

    top_n = st.slider(
        "Number of opportunities to display",
        min_value=5,
        max_value=50,
        value=10,
        key="ranking_top_n"
    )

    if ranking_df.empty:
        st.warning("No opportunities match the selected filters.")
    else:
        top_opportunities = (
            ranking_df.sort_values(
                by=[
                    "investment_score",
                    "expected_roi_percent",
                    "overall_risk_score"
                ],
                ascending=[False, False, True]
            )
            [
                [
                    "opportunity_id",
                    "opportunity_name",
                    "sector",
                    "region",
                    "investment_score",
                    "recommendation",
                    "expected_roi_percent",
                    "overall_risk_score",
                    "strategic_impact_score",
                    "sustainability_score"
                ]
            ]
            .head(top_n)
        )

        st.dataframe(
            top_opportunities,
            use_container_width=True,
            hide_index=True
        )

        fig_top = px.bar(
            top_opportunities.sort_values("investment_score"),
            x="investment_score",
            y="opportunity_name",
            orientation="h",
            color="recommendation",
            color_discrete_map=get_recommendation_color_map(),
            title="Top Opportunities by Investment Score"
        )

        fig_top.update_layout(
            xaxis_title="Investment Score",
            yaxis_title="Opportunity"
        )

        fig_top = apply_chart_layout(fig_top, height=520)
        st.plotly_chart(fig_top, use_container_width=True)


# ---------------------------------------------------------
# Tab 3: Analyze Existing Opportunity
# ---------------------------------------------------------
with analyzer_tab:
    st.subheader("Analyze Existing Opportunity")

    st.markdown(
        "Select one existing opportunity from the synthetic dataset and review its decision factors."
    )

    selected_opportunity_id = st.selectbox(
        "Select Opportunity ID",
        options=df["opportunity_id"].tolist()
    )

    selected_opportunity = df[
        df["opportunity_id"] == selected_opportunity_id
    ].iloc[0]

    st.markdown("### Selected Opportunity Summary")

    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

    with summary_col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Investment Score</div>
                <div class="kpi-value">{selected_opportunity['investment_score']:.2f}/100</div>
                <div class="kpi-caption">Model-generated opportunity score</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with summary_col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Recommendation</div>
                <div class="kpi-value">{recommendation_badge(selected_opportunity["recommendation"])}</div>
                <div class="kpi-caption">Decision category</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with summary_col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Expected ROI</div>
                <div class="kpi-value">{selected_opportunity['expected_roi_percent']:.2f}%</div>
                <div class="kpi-caption">Expected return on investment</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with summary_col4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Overall Risk Score</div>
                <div class="kpi-value">{selected_opportunity['overall_risk_score']:.2f}</div>
                <div class="kpi-caption">Composite risk indicator</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:
        st.markdown("#### Opportunity Details")

        details_df = pd.DataFrame({
            "Field": [
                "Opportunity Name",
                "Sector",
                "Region",
                "Competition Level",
                "Investment Size",
                "Payback Period",
                "Profit Margin"
            ],
            "Value": [
                selected_opportunity["opportunity_name"],
                selected_opportunity["sector"],
                selected_opportunity["region"],
                selected_opportunity["competition_level"],
                f"{selected_opportunity['investment_size_million']:.2f} million SAR",
                f"{selected_opportunity['payback_period_years']:.2f} years",
                f"{selected_opportunity['profit_margin_percent']:.2f}%"
            ]
        })

        st.dataframe(
            details_df,
            use_container_width=True,
            hide_index=True
        )

    with detail_col2:
        st.markdown("#### Key Scores")

        key_scores = pd.DataFrame({
            "Factor": [
                "Financial Strength",
                "Market Attractiveness",
                "Strategic Impact",
                "Sustainability",
                "Overall Risk"
            ],
            "Score": [
                selected_opportunity["financial_strength_score"],
                selected_opportunity["market_attractiveness_score"],
                selected_opportunity["strategic_impact_score"],
                selected_opportunity["sustainability_score"],
                selected_opportunity["overall_risk_score"]
            ]
        })

        fig_key_scores = px.bar(
            key_scores,
            x="Score",
            y="Factor",
            orientation="h",
            title="Key Opportunity Scores",
            color_discrete_sequence=[get_primary_chart_color()]
        )

        fig_key_scores.update_layout(
            xaxis_title="Score",
            yaxis_title="Factor",
            yaxis={"categoryorder": "total ascending"}
        )

        fig_key_scores = apply_chart_layout(fig_key_scores, height=420)
        st.plotly_chart(fig_key_scores, use_container_width=True)


# ---------------------------------------------------------
# Tab 4: Predict New Opportunity
# ---------------------------------------------------------
with prediction_tab:
    st.subheader("Predict New Investment Opportunity")

    st.markdown(
        """
        Enter a simplified opportunity profile. The system automatically converts these
        executive-level inputs into the model's full feature set.
        """
    )

    with st.form("simplified_prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Basic Opportunity Information")

            sector = st.selectbox(
                "Sector",
                options=sorted(df["sector"].unique())
            )

            region = st.selectbox(
                "Region",
                options=sorted(df["region"].unique())
            )

            competition_level = st.selectbox(
                "Competition Level",
                options=["Low", "Medium", "High"],
                help="How competitive is the market?"
            )

            investment_size_million = st.number_input(
                "Investment Size (million SAR)",
                min_value=20.0,
                max_value=5000.0,
                value=250.0,
                step=10.0
            )

            expected_roi_percent = st.slider(
                "Expected ROI (%)",
                min_value=-5.0,
                max_value=30.0,
                value=12.0,
                step=0.5
            )

            payback_period_years = st.slider(
                "Payback Period (years)",
                min_value=1.0,
                max_value=15.0,
                value=6.0,
                step=0.5
            )

        with col2:
            st.markdown("#### Strategic and Risk Profile")

            market_demand_level = st.selectbox(
                "Market Demand",
                options=["Low", "Medium", "High"],
                index=1,
                help="Expected demand and adoption potential."
            )

            risk_level = st.selectbox(
                "Overall Risk Level",
                options=["Low", "Medium", "High"],
                index=1,
                help="Overall financial, market, regulatory, and execution risk."
            )

            strategic_alignment_level = st.selectbox(
                "Strategic Alignment",
                options=["Low", "Medium", "High"],
                index=1,
                help="Alignment with long-term strategic objectives."
            )

            sustainability_level = st.selectbox(
                "Sustainability / ESG Potential",
                options=["Low", "Medium", "High"],
                index=1,
                help="Environmental, social, and governance potential."
            )

        submitted = st.form_submit_button("Predict Opportunity")

    if submitted:
        prediction_input = build_simplified_prediction_input(
            base_df=df,
            sector=sector,
            region=region,
            competition_level=competition_level,
            investment_size_million=investment_size_million,
            expected_roi_percent=expected_roi_percent,
            payback_period_years=payback_period_years,
            market_demand_level=market_demand_level,
            risk_level=risk_level,
            strategic_alignment_level=strategic_alignment_level,
            sustainability_level=sustainability_level
        )

        prediction_result = predict_investment_opportunity(prediction_input)

        predicted_score = prediction_result["predicted_investment_score"].iloc[0]
        predicted_recommendation = prediction_result["recommendation"].iloc[0]

        st.markdown("### Prediction Result")

        result_col1, result_col2, result_col3 = st.columns(3)

        with result_col1:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Predicted Investment Score</div>
                    <div class="kpi-value">{predicted_score:.2f}/100</div>
                    <div class="kpi-caption">Estimated by the trained ML model</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with result_col2:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Recommendation</div>
                    <div class="kpi-value">{recommendation_badge(predicted_recommendation)}</div>
                    <div class="kpi-caption">Based on score thresholds</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with result_col3:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Estimated Risk Score</div>
                    <div class="kpi-value">{prediction_input['overall_risk_score'].iloc[0]:.2f}</div>
                    <div class="kpi-caption">Generated from selected risk level</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        if predicted_recommendation == "Invest":
            st.success("The model classifies this opportunity as attractive for investment review.")
        elif predicted_recommendation == "Review":
            st.warning("The model suggests this opportunity requires further review before investment.")
        else:
            st.error("The model classifies this opportunity as weak based on the provided inputs.")

        st.markdown("#### Why this recommendation?")

        local_explanation = explain_prediction(
            input_data=prediction_input,
            model=model,
            preprocessor=preprocessor,
            top_n=8
        )

        positive_reasons, negative_reasons = generate_reason_text(local_explanation)

        reason_col1, reason_col2 = st.columns(2)

        with reason_col1:
            st.markdown("##### Positive Drivers")
            if positive_reasons:
                for reason in positive_reasons:
                    st.write(f"- {reason}")
            else:
                st.write("No major positive drivers found.")

        with reason_col2:
            st.markdown("##### Negative Drivers")
            if negative_reasons:
                for reason in negative_reasons:
                    st.write(f"- {reason}")
            else:
                st.write("No major negative drivers found.")

        fig_explanation = px.bar(
            local_explanation,
            x="contribution",
            y="readable_feature",
            orientation="h",
            title="Top Feature Contributions",
            color="contribution",
            color_continuous_scale=["#EF4444", "#94A3B8", "#22C55E"]
        )

        fig_explanation.update_layout(
            xaxis_title="Score Impact",
            yaxis_title="Feature",
            yaxis={"categoryorder": "total ascending"}
        )

        fig_explanation = apply_chart_layout(fig_explanation, height=460)
        st.plotly_chart(fig_explanation, use_container_width=True)

        st.markdown("#### Simplified Input Summary")

        summary_input = pd.DataFrame({
            "Input": [
                "Sector",
                "Region",
                "Competition Level",
                "Investment Size",
                "Expected ROI",
                "Payback Period",
                "Market Demand",
                "Risk Level",
                "Strategic Alignment",
                "Sustainability / ESG"
            ],
            "Value": [
                sector,
                region,
                competition_level,
                f"{investment_size_million:.2f} million SAR",
                f"{expected_roi_percent:.2f}%",
                f"{payback_period_years:.2f} years",
                market_demand_level,
                risk_level,
                strategic_alignment_level,
                sustainability_level
            ]
        })

        st.dataframe(
            summary_input,
            use_container_width=True,
            hide_index=True
        )

        with st.expander("Show generated model-ready features"):
            display_columns = [
                "sector",
                "region",
                "competition_level",
                "investment_size_million",
                "expected_roi_percent",
                "irr_percent",
                "npv_million",
                "payback_period_years",
                "overall_risk_score",
                "market_attractiveness_score",
                "financial_strength_score",
                "strategic_impact_score",
                "sustainability_score"
            ]

            st.dataframe(
                prediction_input[display_columns],
                use_container_width=True,
                hide_index=True
            )


# ---------------------------------------------------------
# Tab 5: Methodology
# ---------------------------------------------------------
with methodology_tab:
    st.subheader("Model Methodology")

    st.markdown(
        """
        This project follows a complete machine learning workflow:

        1. Synthetic investment opportunity data generation  
        2. Exploratory data analysis  
        3. Feature engineering  
        4. Data preprocessing  
        5. Model training and comparison  
        6. Model evaluation  
        7. Explainability  
        8. Streamlit dashboard deployment preparation  

        **Machine Learning Task:** Regression  
        **Target Variable:** Investment Score from 0 to 100  
        **Selected Model:** Ridge Regression  

        **Recommendation Logic:**

        - `Invest`: score >= 75  
        - `Review`: 45 <= score < 75  
        - `Reject`: score < 45  

        The dataset is synthetic and was generated to simulate investment opportunity evaluation factors, including:

        - Financial strength  
        - Market attractiveness  
        - Strategic alignment  
        - Risk profile  
        - ESG and sustainability indicators  
        """
    )

    st.divider()

    st.subheader("Model Performance")

    if model_results is not None:
        st.dataframe(
            model_results,
            use_container_width=True,
            hide_index=True
        )

        fig_model = px.bar(
            model_results.sort_values("MAE"),
            x="MAE",
            y="model",
            orientation="h",
            title="Model Comparison by Mean Absolute Error",
            color_discrete_sequence=[get_primary_chart_color()]
        )

        fig_model.update_layout(
            xaxis_title="Mean Absolute Error",
            yaxis_title="Model",
            yaxis={"categoryorder": "total ascending"}
        )

        fig_model = apply_chart_layout(fig_model, height=430)
        st.plotly_chart(fig_model, use_container_width=True)
    else:
        st.warning("Model comparison results file was not found.")

    st.divider()

    st.subheader("Important Disclaimer")

    st.warning(
        "This is a portfolio project using synthetic data. "
        "It should not be used for real investment decisions without real data, "
        "domain expert review, validation, and governance."
    )