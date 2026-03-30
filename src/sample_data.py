from __future__ import annotations

from pathlib import Path

import pandas as pd


RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
APPLICATIONS_PATH = RAW_DIR / "credit_applications.csv"


DEFAULT_APPLICATIONS = [
    {
        "application_id": "CR-1001",
        "customer_name": "Bruna Almeida",
        "requested_amount_br": 28000,
        "term_months": 24,
        "monthly_income_br": 7200,
        "monthly_debt_obligations_br": 1650,
        "credit_score": 742,
        "employment_months": 36,
        "delinquencies_12m": 0,
        "credit_utilization_pct": 34,
        "existing_loans": 1,
        "customer_segment": "prime",
    },
    {
        "application_id": "CR-1002",
        "customer_name": "Diego Pereira",
        "requested_amount_br": 45000,
        "term_months": 36,
        "monthly_income_br": 5100,
        "monthly_debt_obligations_br": 2300,
        "credit_score": 598,
        "employment_months": 11,
        "delinquencies_12m": 2,
        "credit_utilization_pct": 82,
        "existing_loans": 3,
        "customer_segment": "mass_market",
    },
    {
        "application_id": "CR-1003",
        "customer_name": "Fernanda Costa",
        "requested_amount_br": 18000,
        "term_months": 18,
        "monthly_income_br": 6400,
        "monthly_debt_obligations_br": 900,
        "credit_score": 681,
        "employment_months": 18,
        "delinquencies_12m": 0,
        "credit_utilization_pct": 57,
        "existing_loans": 2,
        "customer_segment": "near_prime",
    },
]


def ensure_sample_data() -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if not APPLICATIONS_PATH.exists():
        pd.DataFrame(DEFAULT_APPLICATIONS).to_csv(APPLICATIONS_PATH, index=False)
    return pd.read_csv(APPLICATIONS_PATH)


def load_applications() -> pd.DataFrame:
    return ensure_sample_data()


def load_application(application_id: str) -> dict:
    dataset = ensure_sample_data()
    match = dataset.loc[dataset["application_id"] == application_id]
    if match.empty:
        raise KeyError(f"Application id not found: {application_id}")
    return match.iloc[0].to_dict()
