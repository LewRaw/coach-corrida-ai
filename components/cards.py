"""
Componentes de Cards Visuais Nativos (Streamlit Containers com Borda)
Substitui injeções de HTML bruto e classes CSS customizadas
"""

from typing import Callable, Any
import pandas as pd
import streamlit as st
from config import TreinoExtracao, PlanoSemanalPrescrito


def render_next_workout_card(
    proximo: Any,
    on_concluir: Callable[[Any], None],
):
    """
    Renderiza o card de Treino Atual / Próxima Sessão utilizando st.container(border=True) nativo.
    """
    proximo_id = str(proximo["ID"]) if "ID" in proximo else (str(proximo["id"]) if "id" in proximo else str(proximo.name))
    dist_val = float(proximo.get("Distância (km)", 0.0) or 0.0)
    dur_val = float(proximo.get("Duração (min)", 0.0) or 0.0)

    with st.container(border=True):
        st.caption(f"PRÓXIMA SESSÃO • {proximo.get('Dia da Semana', '')} ({proximo.get('Data Prevista', '')})")
        st.subheader(str(proximo.get("Tipo de Treino", "Treino Prescrito")))

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Distância", f"{dist_val:.1f} km" if dist_val > 0 else "--")
        m2.metric("Duração", f"{dur_val:.0f} min" if dur_val > 0 else "--")
        m3.metric("Ritmo Alvo", str(proximo.get("Pace Alvo", "--")))
        m4.metric("Esforço Alvo", f"{proximo.get('RPE Alvo', '--')}/10")

        st.markdown(f"**Estrutura da Sessão:**\n\n{proximo.get('Estrutura do Treino', '')}")

        btn_col1, btn_col2 = st.columns([2, 1])
        with btn_col1:
            if st.button(
                "Concluir Treino",
                type="primary",
                use_container_width=True,
                key="btn_complete_hero",
                icon=":material/check_circle:",
                help="Conclua enviando o print da atividade ou inserindo os dados manualmente",
            ):
                on_concluir(proximo)

        with btn_col2:
            if st.button(
                "Pular Sessão",
                use_container_width=True,
                key="btn_skip_hero",
                icon=":material/skip_next:",
                help="Pula esta sessão e avança para a próxima da semana",
            ):
                on_concluir(proximo)


def render_feedback_card(res: TreinoExtracao):
    """
    Renderiza o parecer técnico de uma atividade recém-analisada via st.container(border=True).
    """
    with st.container(border=True):
        st.caption(f"ANÁLISE TÉCNICA • {res.zona_predominante} • Modalidade: {res.modalidade}")
        st.subheader("Parecer Técnico do Treinador")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Distância", f"{res.distancia_km:.2f} km")
        m2.metric("Duração", f"{res.tempo_min:.1f} min")
        m3.metric("Ritmo Médio", f"{res.pace_medio}")
        m4.metric("FC Média", f"{res.fc_media} bpm" if res.fc_media > 0 else "--")

        st.markdown(f"**Avaliação:**\n\n{res.parecer_treinador}")


def render_plan_card(plano: PlanoSemanalPrescrito):
    """
    Renderiza o diagnóstico e metodologia do plano semanal em container nativo.
    """
    with st.container(border=True):
        st.subheader(plano.titulo_ciclo)
        st.markdown(f"**Diagnóstico e Metodologia:**\n\n{plano.diagnostico_metodologia}")
        st.markdown(f"**Ritmos de Referência:**\n\n{plano.paces_referencia}")
        st.markdown(f"**Orientações Gerais:**\n\n{plano.orientacoes_gerais}")
