# AI Investment Opportunity Analyzer

A machine learning decision-support dashboard for evaluating synthetic investment opportunities.  
The project estimates an **Investment Score (0–100)** and classifies each opportunity as:

- **Invest**
- **Review**
- **Reject**

The project is built as a complete end-to-end machine learning workflow, starting from synthetic data generation and ending with an interactive Streamlit dashboard.

---

## Project Overview

This project simulates an investment opportunity evaluation system using machine learning.

It analyzes multiple opportunity factors, including:

- Financial strength
- Market attractiveness
- Strategic impact
- Risk profile
- Sustainability and ESG indicators
- Sector and region information
- Competition level
- Expected ROI and payback period

The final output is an investment score and a recommendation category.

---

## Important Disclaimer

This project uses a **fully synthetic dataset** created for educational and portfolio purposes.

It does **not** use real investment data and should **not** be used for real financial or investment decisions.

---

## Key Features

- Synthetic investment opportunity dataset
- Exploratory data analysis
- Feature engineering
- Data preprocessing pipeline
- Regression model training and comparison
- Best model selection
- Prediction pipeline
- Model explainability using feature contributions
- Interactive Streamlit dashboard
- Simplified prediction form for non-technical users

---

## Machine Learning Workflow

The project follows these main steps:

1. **Data Generation**  
   Synthetic investment opportunities are generated across different sectors and regions.

2. **Exploratory Data Analysis**  
   The dataset is analyzed using summary statistics, score distributions, sector comparisons, region comparisons, and correlations.

3. **Feature Engineering**  
   Additional features are created to represent financial strength, market attractiveness, strategic impact, sustainability, and risk.

4. **Preprocessing**  
   Numerical features are scaled using `StandardScaler`, and categorical features are encoded using `OneHotEncoder`.

5. **Model Training and Comparison**  
   Multiple regression models are trained and compared using MAE, RMSE, and R².

6. **Best Model Selection**  
   The best model is selected based on the lowest Mean Absolute Error.

7. **Explainability**  
   Feature contributions are calculated to explain why a prediction received a specific score.

8. **Dashboard Development**  
   The final system is deployed locally using Streamlit.

---

## Models Compared

The following regression models were tested:

- Linear Regression
- Ridge Regression
- Random Forest Regressor
- Gradient Boosting Regressor
- Extra Trees Regressor

The selected model is:

```text
Ridge Regression
```

Ridge Regression was selected because it achieved the best performance based on Mean Absolute Error in the model comparison.