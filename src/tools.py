from __future__ import annotations

import json
from typing import Any

from .sample_data import load_application


def get_application_context(application_id: str) -> dict[str, Any]:
    """Retorna o contexto estruturado da proposta de crédito."""
    return load_application(application_id)


def compute_credit_metrics(application_id: str) -> dict[str, Any]:
    """Calcula métricas heurísticas de underwriting."""
    app = load_application(application_id)
    income = float(app["monthly_income_br"])
    monthly_debt = float(app["monthly_debt_obligations_br"])
    requested = float(app["requested_amount_br"])
    term = max(int(app["term_months"]), 1)

    installment_estimate = round(requested / term, 2)
    debt_to_income = round(monthly_debt / income, 4)
    installment_to_income = round(installment_estimate / income, 4)

    risk_flags: list[str] = []
    if float(app["credit_score"]) < 620:
        risk_flags.append("score_baixo")
    if int(app["delinquencies_12m"]) >= 2:
        risk_flags.append("inadimplencia_recente")
    if float(app["credit_utilization_pct"]) >= 75:
        risk_flags.append("utilizacao_alta")
    if debt_to_income >= 0.4:
        risk_flags.append("endividamento_elevado")
    if installment_to_income >= 0.3:
        risk_flags.append("parcela_pesada")
    if int(app["employment_months"]) < 12:
        risk_flags.append("estabilidade_profissional_curta")

    return {
        "application_id": application_id,
        "installment_estimate_br": installment_estimate,
        "debt_to_income_ratio": debt_to_income,
        "installment_to_income_ratio": installment_to_income,
        "risk_flags": risk_flags,
    }


def classify_credit_decision(application_id: str) -> dict[str, Any]:
    """Classifica decisão de crédito com score heurístico simples."""
    app = load_application(application_id)
    metrics = compute_credit_metrics(application_id)

    score = 0
    score += 2 if float(app["credit_score"]) < 620 else 1 if float(app["credit_score"]) < 680 else 0
    score += 2 if "inadimplencia_recente" in metrics["risk_flags"] else 0
    score += 1 if "utilizacao_alta" in metrics["risk_flags"] else 0
    score += 1 if "endividamento_elevado" in metrics["risk_flags"] else 0
    score += 1 if "parcela_pesada" in metrics["risk_flags"] else 0
    score += 1 if "estabilidade_profissional_curta" in metrics["risk_flags"] else 0

    if score >= 5:
        decision = "decline"
        risk_band = "alto"
    elif score >= 2:
        decision = "manual_review"
        risk_band = "moderado"
    else:
        decision = "approve"
        risk_band = "baixo"

    return {
        "application_id": application_id,
        "decision": decision,
        "risk_band": risk_band,
        "risk_score": score,
    }


def explain_credit_decision(application_id: str) -> str:
    """Gera explicação executiva grounded na proposta."""
    app = load_application(application_id)
    metrics = compute_credit_metrics(application_id)
    classification = classify_credit_decision(application_id)
    flags = ", ".join(metrics["risk_flags"]) if metrics["risk_flags"] else "sem alertas críticos"

    return (
        f"A proposta {application_id} de {app['customer_name']} foi classificada como risco {classification['risk_band']} "
        f"com decisão sugerida `{classification['decision']}`. Os principais fatores observados foram: {flags}. "
        f"A parcela estimada corresponde a {metrics['installment_to_income_ratio']:.1%} da renda mensal."
    )


def suggest_credit_conditions(application_id: str) -> dict[str, Any]:
    """Sugere condições ou mitigantes a partir da decisão."""
    app = load_application(application_id)
    classification = classify_credit_decision(application_id)

    if classification["decision"] == "approve":
        conditions = [
            "seguir com aprovação nas condições solicitadas",
            "monitorar comportamento pós-concessão no ciclo inicial",
        ]
    elif classification["decision"] == "manual_review":
        conditions = [
            "avaliar redução de limite ou prazo",
            "solicitar documentação complementar de renda",
            "considerar alçada manual antes da decisão final",
        ]
    else:
        conditions = [
            "não prosseguir com aprovação nas condições atuais",
            "reavaliar em cenário de menor valor solicitado ou maior entrada",
            "orientar cliente sobre fatores de elegibilidade futura",
        ]

    return {
        "application_id": application_id,
        "recommended_conditions": conditions,
        "requested_amount_br": float(app["requested_amount_br"]),
    }


def build_fallback_report(application_id: str, user_question: str) -> dict[str, Any]:
    context = get_application_context(application_id)
    metrics = compute_credit_metrics(application_id)
    classification = classify_credit_decision(application_id)
    explanation = explain_credit_decision(application_id)
    conditions = suggest_credit_conditions(application_id)

    final_message = (
        f"Pergunta analítica: {user_question}\n\n"
        f"Contexto da proposta:\n{json.dumps(context, ensure_ascii=False, indent=2)}\n\n"
        f"Métricas derivadas:\n{json.dumps(metrics, ensure_ascii=False, indent=2)}\n\n"
        f"Classificação:\n{json.dumps(classification, ensure_ascii=False, indent=2)}\n\n"
        f"Explicação:\n{explanation}\n\n"
        f"Condições sugeridas:\n{json.dumps(conditions, ensure_ascii=False, indent=2)}"
    )

    return {
        "application_id": application_id,
        "application": context,
        "credit_metrics": metrics,
        "classification": classification,
        "decision_explanation": explanation,
        "recommended_conditions": conditions,
        "final_message": final_message,
    }
