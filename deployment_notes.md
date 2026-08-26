# Deployment Notes

## Project Name

AI Investment Opportunity Analyzer

## App Entry Point

The Streamlit application entry point is:

```text
app/streamlit_app.py
```

## Required Files for Deployment

The following files and folders are required for the deployed app to work:

```text
app/streamlit_app.py
src/predict.py
src/scoring.py
src/explanations.py
data/raw/synthetic_investment_opportunities.csv
models/best_model.pkl
models/preprocessor.pkl
models/model_metadata.json
reports/model_comparison_results.csv
requirements.txt
README.md
```

## Required Python Packages

The main dependencies are listed in `requirements.txt`:

```text
streamlit
pandas
numpy
scikit-learn
joblib
plotly
matplotlib
seaborn
```

## Local Run Command

To run the app locally:

```bash
streamlit run app/streamlit_app.py
```

## Deployment Platform

Recommended deployment platform:

```text
Streamlit Community Cloud
```

## Streamlit Community Cloud Settings

When deploying the app, use the following settings:

```text
Repository: ai-investment-opportunity-analyzer
Branch: main
Main file path: app/streamlit_app.py
```

## Deployment Checklist

Before deployment, confirm that the following files exist:

```text
app/streamlit_app.py
data/raw/synthetic_investment_opportunities.csv
models/best_model.pkl
models/preprocessor.pkl
src/predict.py
requirements.txt
README.md
```

The app should also run successfully locally using:

```bash
streamlit run app/streamlit_app.py
```

## Important Notes

This project uses a fully synthetic dataset for educational and portfolio purposes.

The model and dashboard should not be used for real investment decisions.

Real-world deployment would require:

- Real verified investment data
- Financial domain expert validation
- Risk governance
- Legal and compliance review
- Continuous monitoring
- Data security controls

## Known Limitations

- The dataset is synthetic.
- The recommendation logic is simplified.
- The model was trained only on generated data.
- The app is intended for portfolio demonstration and educational use.
- Real investment decisions require validated data and expert review.

## Deployment Goal

The goal of deployment is to make the dashboard accessible online as a portfolio project that demonstrates:

- Data generation
- Exploratory data analysis
- Feature engineering
- Machine learning model training
- Model comparison
- Model explainability
- Streamlit dashboard development