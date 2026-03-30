from __future__ import annotations

import asyncio
import os
from typing import Any

from .tools import (
    build_fallback_report,
    classify_credit_decision,
    compute_credit_metrics,
    explain_credit_decision,
    get_application_context,
    suggest_credit_conditions,
)

try:
    from semantic_kernel import Kernel
    from semantic_kernel.agents.chat_completion.chat_completion_agent import ChatCompletionAgent, ChatHistoryAgentThread
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    from semantic_kernel.functions import kernel_function
except Exception:  # pragma: no cover - optional runtime dependency
    Kernel = None
    ChatCompletionAgent = None
    ChatHistoryAgentThread = None
    OpenAIChatCompletion = None
    kernel_function = None


if kernel_function is None:  # pragma: no cover - local fallback compatibility
    def kernel_function(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class CreditAnalysisPlugin:
    @kernel_function(description="Get the application context by application id.")
    def get_application_context(self, application_id: str) -> str:
        return str(get_application_context(application_id))

    @kernel_function(description="Compute heuristic credit metrics for the application.")
    def compute_credit_metrics(self, application_id: str) -> str:
        return str(compute_credit_metrics(application_id))

    @kernel_function(description="Classify the credit decision and risk band.")
    def classify_credit_decision(self, application_id: str) -> str:
        return str(classify_credit_decision(application_id))

    @kernel_function(description="Explain the credit decision.")
    def explain_credit_decision(self, application_id: str) -> str:
        return explain_credit_decision(application_id)

    @kernel_function(description="Suggest approval conditions or mitigants.")
    def suggest_credit_conditions(self, application_id: str) -> str:
        return str(suggest_credit_conditions(application_id))


def _build_semantic_kernel_agent(model_name: str = "gpt-4.1-mini"):
    if not (
        Kernel
        and ChatCompletionAgent
        and ChatHistoryAgentThread
        and OpenAIChatCompletion
        and kernel_function
        and os.getenv("OPENAI_API_KEY")
    ):
        return None

    kernel = Kernel()
    kernel.add_service(OpenAIChatCompletion(service_id="credit-analysis", ai_model_id=model_name, api_key=os.getenv("OPENAI_API_KEY")))
    kernel.add_plugin(CreditAnalysisPlugin(), plugin_name="credit_tools")

    agent = ChatCompletionAgent(
        service=kernel.get_service("credit-analysis"),
        kernel=kernel,
        name="credit_analysis_agent",
        instructions=(
            "Você é um agente de análise de crédito. Sempre use as funções disponíveis para consultar o contexto da "
            "proposta, calcular métricas, classificar risco e sugerir condições. Não invente dados."
        ),
    )
    return agent


async def _run_semantic_kernel(application_id: str, user_question: str, model_name: str) -> dict[str, Any]:
    agent = _build_semantic_kernel_agent(model_name=model_name)
    if agent is None:
        report = build_fallback_report(application_id=application_id, user_question=user_question)
        return {"runtime_mode": "deterministic_fallback", **report}

    report = build_fallback_report(application_id=application_id, user_question=user_question)
    try:
        thread = ChatHistoryAgentThread()
        result = await agent.get_response(
            messages=f"application_id={application_id}\nuser_question={user_question}\nAnalise a proposta e responda com decisão, racional e condições.",
            thread=thread,
        )
        content = str(getattr(result, "content", "")) or report["final_message"]
        report["final_message"] = content
        return {"runtime_mode": "semantic_kernel_agent", **report}
    except Exception:
        return {"runtime_mode": "deterministic_fallback", **report}


def ask_credit_analysis_agent(
    application_id: str,
    user_question: str,
    model_name: str = "gpt-4.1-mini",
) -> dict[str, Any]:
    return asyncio.run(_run_semantic_kernel(application_id=application_id, user_question=user_question, model_name=model_name))
