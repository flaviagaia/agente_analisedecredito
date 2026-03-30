from __future__ import annotations

import json
from pathlib import Path

from src.agent import ask_credit_analysis_agent
from src.sample_data import ensure_sample_data


def main() -> None:
    ensure_sample_data()
    result = ask_credit_analysis_agent(
        application_id="CR-1002",
        user_question="Deveríamos aprovar essa proposta ou encaminhar para revisão manual?",
    )
    output_path = Path(__file__).resolve().parent / "data" / "processed" / "credit_analysis_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Agente Analise de Credito")
    print(f"runtime_mode: {result['runtime_mode']}")
    print(f"application_id: {result['application_id']}")
    print(f"decision: {result['classification']['decision']}")
    print(f"risk_band: {result['classification']['risk_band']}")
    print(f"output_path: {output_path}")


if __name__ == "__main__":
    main()
