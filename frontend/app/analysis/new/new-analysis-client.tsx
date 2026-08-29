"use client";

import { useState, type FormEvent } from "react";

import { useApiStatus } from "@/components/api-status-context";
import { PageHeader } from "@/components/page-header";
import { SectionRule } from "@/components/section-rule";
import { ApiRequestError } from "@/lib/api/client";
import { predictOpportunity } from "@/lib/api/predict";
import type { PredictionRequest, PredictionResponse } from "@/lib/api/types";

const levelOptions = ["Low", "Medium", "High"] as const;
type Level = (typeof levelOptions)[number];
type RequestState = "idle" | "loading" | "success" | "validation-error" | "unavailable";

interface FormValues {
  sector: string;
  region: string;
  competition_level: Level;
  investment_size_million: string;
  expected_roi_percent: string;
  payback_period_years: string;
  market_demand_level: Level;
  risk_level: Level;
  strategic_alignment_level: Level;
  sustainability_level: Level;
}

const initialValues: FormValues = {
  sector: "Technology",
  region: "Riyadh",
  competition_level: "Medium",
  investment_size_million: "250",
  expected_roi_percent: "12",
  payback_period_years: "6",
  market_demand_level: "Medium",
  risk_level: "Medium",
  strategic_alignment_level: "Medium",
  sustainability_level: "Medium",
};

function formatMetric(value: number) {
  return value.toFixed(2);
}

function formatContribution(value: number | undefined) {
  if (value === undefined) return "—";
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}`;
}

function validationMessage(detail: unknown) {
  if (!detail || typeof detail !== "object" || !("detail" in detail)) {
    return "The submitted values do not satisfy the prediction contract.";
  }

  const issues = detail.detail;
  if (!Array.isArray(issues)) {
    return "The submitted values do not satisfy the prediction contract.";
  }

  const messages = issues.flatMap((issue) => {
    if (!issue || typeof issue !== "object" || !("msg" in issue) || typeof issue.msg !== "string") {
      return [];
    }
    return [issue.msg];
  });

  return messages.length > 0
    ? messages.join(" ")
    : "The submitted values do not satisfy the prediction contract.";
}

function requestNote(state: RequestState, message: string | null) {
  if (state === "loading") return "Submitting the current 10-field contract to FastAPI.";
  if (state === "validation-error") return `Validation error · ${message}`;
  if (state === "unavailable") return "Prediction service unavailable. Check the API connection, then retry.";
  if (state === "success") {
    return "Live FastAPI response. Model contributions describe arithmetic influence, not causation.";
  }
  return "No prediction request has been made.";
}

export function NewAnalysisClient() {
  const { apiStatus, setApiStatus } = useApiStatus();
  const [values, setValues] = useState<FormValues>(initialValues);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [requestState, setRequestState] = useState<RequestState>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const positiveRows = prediction?.contributions.filter(
    (item) => item.direction === "positive",
  ) ?? [];
  const negativeRows = prediction?.contributions.filter(
    (item) => item.direction === "negative",
  ) ?? [];
  const largestContribution = Math.max(
    1,
    ...positiveRows.map((item) => Math.abs(item.contribution)),
    ...negativeRows.map((item) => Math.abs(item.contribution)),
  );

  const recommendationTone = prediction?.recommendation.toLowerCase() ?? "review";

  function updateValue<Key extends keyof FormValues>(key: Key, value: FormValues[Key]) {
    setValues((current) => ({ ...current, [key]: value }));
  }

  async function submitPrediction(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const payload: PredictionRequest = {
      sector: values.sector,
      region: values.region,
      competition_level: values.competition_level,
      investment_size_million: Number(values.investment_size_million),
      expected_roi_percent: Number(values.expected_roi_percent),
      payback_period_years: Number(values.payback_period_years),
      market_demand_level: values.market_demand_level,
      risk_level: values.risk_level,
      strategic_alignment_level: values.strategic_alignment_level,
      sustainability_level: values.sustainability_level,
    };

    setPrediction(null);
    setErrorMessage(null);
    setRequestState("loading");
    setApiStatus("checking");

    try {
      const response = await predictOpportunity(payload);
      setPrediction(response);
      setRequestState("success");
      setApiStatus("online");
    } catch (error: unknown) {
      if (error instanceof ApiRequestError && error.status === 422) {
        setErrorMessage(validationMessage(error.detail));
        setRequestState("validation-error");
        setApiStatus("online");
        return;
      }

      setRequestState("unavailable");
      setApiStatus("offline");
    }
  }

  const outputNote = requestState === "success"
    ? "Live FastAPI response"
    : requestState === "loading"
      ? "Submitting contract"
      : requestState === "validation-error"
        ? "Validation error"
        : requestState === "unavailable"
          ? "Service unavailable"
          : "Awaiting request";
  const apiStateText = apiStatus === "online"
    ? "Online · Live prediction"
    : apiStatus === "checking"
      ? "Checking · Request in progress"
      : apiStatus === "offline"
        ? "Offline · Retry available"
        : "Idle · Awaiting request";

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Deal entry terminal · 10-field contract"
        title="New Analysis"
        description="Enter a simplified opportunity profile and submit it to the current prediction pipeline."
        aside={
          <div className="as-of-block">
            <span>API state</span>
            <strong>{apiStateText}</strong>
          </div>
        }
      />

      <div className="analysis-layout">
        <form className="analysis-form" noValidate onSubmit={submitPrediction}>
          <fieldset className="form-section">
            <legend>Opportunity</legend>
            <p>Market position and operating context.</p>
            <div className="form-grid form-grid-three">
              <label className="field">
                <span>Sector</span>
                <select
                  name="sector"
                  value={values.sector}
                  onChange={(event) => updateValue("sector", event.target.value)}
                >
                  <option>Technology</option>
                  <option>Renewable Energy</option>
                  <option>Healthcare</option>
                  <option>Infrastructure</option>
                  <option>Tourism</option>
                </select>
              </label>
              <label className="field">
                <span>Region</span>
                <select
                  name="region"
                  value={values.region}
                  onChange={(event) => updateValue("region", event.target.value)}
                >
                  <option>Riyadh</option>
                  <option>Eastern Province</option>
                  <option>Makkah</option>
                  <option>Tabuk</option>
                  <option>Asir</option>
                </select>
              </label>
              <label className="field">
                <span>Competition Level</span>
                <select
                  name="competition_level"
                  value={values.competition_level}
                  onChange={(event) => updateValue("competition_level", event.target.value as Level)}
                >
                  {levelOptions.map((level) => <option key={level}>{level}</option>)}
                </select>
              </label>
            </div>
          </fieldset>

          <fieldset className="form-section">
            <legend>Financial</legend>
            <p>Scale, return expectation, and capital recovery.</p>
            <div className="form-grid form-grid-three">
              <label className="field field-with-unit">
                <span>Investment Size</span>
                <div>
                  <input
                    name="investment_size_million"
                    type="number"
                    min="20"
                    max="5000"
                    value={values.investment_size_million}
                    onChange={(event) => updateValue("investment_size_million", event.target.value)}
                  />
                  <small>SAR M</small>
                </div>
              </label>
              <label className="field field-with-unit">
                <span>Expected ROI</span>
                <div>
                  <input
                    name="expected_roi_percent"
                    type="number"
                    min="-5"
                    max="30"
                    value={values.expected_roi_percent}
                    onChange={(event) => updateValue("expected_roi_percent", event.target.value)}
                  />
                  <small>%</small>
                </div>
              </label>
              <label className="field field-with-unit">
                <span>Payback Period</span>
                <div>
                  <input
                    name="payback_period_years"
                    type="number"
                    min="1"
                    max="15"
                    value={values.payback_period_years}
                    onChange={(event) => updateValue("payback_period_years", event.target.value)}
                  />
                  <small>years</small>
                </div>
              </label>
            </div>
          </fieldset>

          <fieldset className="form-section">
            <legend>Market</legend>
            <p>Qualitative demand and risk conditions.</p>
            <div className="form-grid form-grid-two">
              <label className="field">
                <span>Market Demand</span>
                <select
                  name="market_demand_level"
                  value={values.market_demand_level}
                  onChange={(event) => updateValue("market_demand_level", event.target.value as Level)}
                >
                  {levelOptions.map((level) => <option key={level}>{level}</option>)}
                </select>
              </label>
              <label className="field">
                <span>Risk Level</span>
                <select
                  name="risk_level"
                  value={values.risk_level}
                  onChange={(event) => updateValue("risk_level", event.target.value as Level)}
                >
                  {levelOptions.map((level) => <option key={level}>{level}</option>)}
                </select>
              </label>
            </div>
          </fieldset>

          <fieldset className="form-section">
            <legend>Strategy</legend>
            <p>Alignment and sustainability inputs.</p>
            <div className="form-grid form-grid-two">
              <label className="field">
                <span>Strategic Alignment</span>
                <select
                  name="strategic_alignment_level"
                  value={values.strategic_alignment_level}
                  onChange={(event) => updateValue("strategic_alignment_level", event.target.value as Level)}
                >
                  {levelOptions.map((level) => <option key={level}>{level}</option>)}
                </select>
              </label>
              <label className="field">
                <span>Sustainability</span>
                <select
                  name="sustainability_level"
                  value={values.sustainability_level}
                  onChange={(event) => updateValue("sustainability_level", event.target.value as Level)}
                >
                  {levelOptions.map((level) => <option key={level}>{level}</option>)}
                </select>
              </label>
            </div>
          </fieldset>

          <div className="form-action-row">
            <p>{requestNote(requestState, errorMessage)}</p>
            <button className="primary-action" disabled={requestState === "loading"} type="submit">
              {requestState === "loading"
                ? "Evaluating…"
                : requestState === "validation-error" || requestState === "unavailable"
                  ? "Retry Evaluation"
                  : "Evaluate Opportunity"}
            </button>
          </div>
        </form>

        <aside className="prediction-rail" aria-live="polite">
          <SectionRule title="Evaluation Output" note={outputNote} />
          <div className="result-placeholder">
            <span>Model Score</span>
            <strong>
              {requestState === "loading"
                ? "…"
                : prediction
                  ? formatMetric(prediction.predicted_investment_score)
                  : "—"}
            </strong>
            <small>
              Decision <b className={`prediction-${recommendationTone}`}>
                {prediction?.recommendation ?? "Pending"}
              </b>
            </small>
          </div>
          <dl className="result-ledger">
            <div>
              <dt>Estimated Risk</dt>
              <dd>{prediction ? formatMetric(prediction.estimated_overall_risk_score) : "—"}</dd>
            </div>
            <div>
              <dt>Positive Contributions</dt>
              <dd>{prediction?.positive_contributions.length ?? 0}</dd>
            </div>
            <div>
              <dt>Negative Contributions</dt>
              <dd>{prediction?.negative_contributions.length ?? 0}</dd>
            </div>
          </dl>
          <div className="contribution-block">
            <span>Positive Model Contributions</span>
            {positiveRows.length > 0 ? positiveRows.map((item) => (
              <div key={item.feature}>
                <b title={item.readable_feature}>{item.readable_feature}</b>
                <i
                  className="contribution-positive"
                  style={{ width: `${(Math.abs(item.contribution) / largestContribution) * 100}%` }}
                />
                <code>{formatContribution(item.contribution)}</code>
              </div>
            )) : <p className="contribution-empty">Awaiting live response</p>}
          </div>
          <div className="contribution-block">
            <span>Negative Model Contributions</span>
            {negativeRows.length > 0 ? negativeRows.map((item) => (
              <div key={item.feature}>
                <b title={item.readable_feature}>{item.readable_feature}</b>
                <i
                  className="contribution-negative"
                  style={{ width: `${(Math.abs(item.contribution) / largestContribution) * 100}%` }}
                />
                <code>{formatContribution(item.contribution)}</code>
              </div>
            )) : <p className="contribution-empty">Awaiting live response</p>}
          </div>
          <p className="rail-note">
            Model contributions indicate arithmetic influence on the predicted score, not causation.
          </p>
        </aside>
      </div>
    </div>
  );
}
