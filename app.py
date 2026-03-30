from __future__ import annotations

import streamlit as st

from src.agent import ask_credit_analysis_agent
from src.sample_data import load_applications


st.set_page_config(page_title="Agente de Análise de Crédito Inteligente", layout="wide")
st.title("Agente de Análise de Crédito Inteligente")
st.caption("MVP com Semantic Kernel para underwriting heurístico, explicação de decisão e condições sugeridas.")

applications = load_applications()
options = applications.set_index("application_id")["customer_name"].to_dict()

with st.sidebar:
    st.header("Stack Técnica")
    st.markdown(
        """
        - `Semantic Kernel` para orquestração agentic
        - `ChatCompletionAgent` como runtime previsto
        - plugin com `kernel_function` para underwriting
        - fallback determinístico para execução local
        - `Streamlit` para inspeção técnica
        """
    )
    st.header("Camadas do MVP")
    st.markdown(
        """
        - contexto da proposta
        - métricas heurísticas de crédito
        - classificação e banda de risco
        - explicação e condições recomendadas
        """
    )

application_id = st.selectbox(
    "Selecione a proposta",
    options=list(options.keys()),
    format_func=lambda aid: f"{aid} - {options[aid]}",
)

question = st.text_area(
    "Pergunta analítica",
    value="Qual decisão deveríamos recomendar para esta proposta e quais condições fariam sentido?",
    height=120,
)

if st.button("Executar agente", type="primary"):
    result = ask_credit_analysis_agent(application_id=application_id, user_question=question)

    c1, c2, c3 = st.columns(3)
    c1.metric("Runtime mode", result["runtime_mode"])
    c2.metric("Decisão", result["classification"]["decision"])
    c3.metric("Banda de risco", result["classification"]["risk_band"])

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Mensagem final", "Métricas", "Classificação e condições", "Proposta consultada"]
    )
    with tab1:
        st.markdown(result["final_message"])
    with tab2:
        st.write(result["decision_explanation"])
        st.json(result["credit_metrics"])
    with tab3:
        st.json(result["classification"])
        st.json(result["recommended_conditions"])
    with tab4:
        st.json(result["application"])

st.divider()
st.subheader("Arquitetura resumida")
st.code(
    """Analista -> Semantic Kernel Agent -> plugin de análise de crédito -> decisão + condições
          \\-> fallback determinístico local (sem OPENAI_API_KEY / sem runtime Semantic Kernel)""",
    language="text",
)
