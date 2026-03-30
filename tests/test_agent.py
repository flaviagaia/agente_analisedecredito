from __future__ import annotations

import unittest

from src.agent import ask_credit_analysis_agent
from src.sample_data import ensure_sample_data
from src.tools import classify_credit_decision, compute_credit_metrics


class CreditAnalysisAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        ensure_sample_data()

    def test_metrics_return_risk_flags(self) -> None:
        metrics = compute_credit_metrics("CR-1002")
        self.assertIn("risk_flags", metrics)
        self.assertGreaterEqual(len(metrics["risk_flags"]), 1)

    def test_classification_returns_decision(self) -> None:
        classification = classify_credit_decision("CR-1001")
        self.assertIn(classification["decision"], {"approve", "manual_review", "decline"})

    def test_agent_returns_final_message(self) -> None:
        result = ask_credit_analysis_agent(
            application_id="CR-1003",
            user_question="Qual decisão deveríamos sugerir para essa proposta?",
        )
        self.assertIn("runtime_mode", result)
        self.assertIn("final_message", result)
        self.assertIn("classification", result)


if __name__ == "__main__":
    unittest.main()
