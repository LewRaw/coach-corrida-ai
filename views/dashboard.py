"""
Aba: Painel do Atleta
Treino atual em destaque, progresso da semana e grade de cronograma com st.column_config
"""

import pandas as pd
import streamlit as st

from services.auth_service import get_athlete_profile, dismiss_pwa_banner
from services.data_service import (
    load_cronograma_data,
    mark_workout_as_completed_data,
    clear_cronograma_data,
)
from components.cards import render_next_workout_card, render_feedback_card
from components.dialogs import modal_concluir_treino, modal_atalho_celular


def render():
    """Renderiza o Painel do Atleta."""
    # 1. BANNER PWA MOBILE (Instalação em Tela de Início com Login Permanente)
    perf = get_athlete_profile()
    pwa_dispensado = perf.get("pwa_aviso_dispensado", False) or st.session_state.get("pwa_aviso_dispensado", False)

    if not pwa_dispensado:
        with st.container(border=True):
            col_pwa_txt, col_pwa_act = st.columns([3.2, 1.8])
            with col_pwa_txt:
                st.markdown("**Adicione o Coach AI à tela de início do seu celular**")
                st.caption(
                    "Crie um atalho com login memorizado para abrir direto no seu painel sem pedir senha toda vez."
                )
            with col_pwa_act:
                st.write("")
                col_pwa_b1, col_pwa_b2 = st.columns(2)
                with col_pwa_b1:
                    if st.button("Gerar Atalho", key="btn_abrir_modal_pwa", use_container_width=True, icon=":material/smartphone:"):
                        modal_atalho_celular()
                with col_pwa_b2:
                    if st.button("Dispensar", key="btn_dispensar_pwa", use_container_width=True, icon=":material/check:"):
                        dismiss_pwa_banner()
                        st.rerun()

    # 2. CARREGAMENTO DO CRONOGRAMA
    df_crono, erro_crono = load_cronograma_data()

    # 3. TREINO ATUAL EM DESTAQUE (SPOTLIGHT CARD)
    st.subheader("Treino em Destaque")

    if erro_crono:
        st.info(erro_crono)
    elif df_crono is None or df_crono.empty:
        st.info(
            "Você ainda não possui treinos agendados no Cronograma. "
            "Acesse a aba 'Montador de Treinos' para planejar sua semana sob medida."
        )
    else:
        df_pendentes = df_crono[df_crono["Status"] == "Pendente"]
        if not df_pendentes.empty:
            proximo = df_pendentes.iloc[0]

            render_next_workout_card(
                proximo=proximo,
                on_concluir=modal_concluir_treino,
            )
        else:
            st.success("Parabéns! Todas as sessões prescritas desta semana foram concluídas.")

    # 4. PARECER DO ÚLTIMO TREINO REGISTRADO
    if "ultimo_treino" in st.session_state and st.session_state["ultimo_treino"]:
        st.write("")
        render_feedback_card(st.session_state["ultimo_treino"])

    # 5. MÉTRICAS DE ADESÃO DA SEMANA
    if df_crono is not None and not df_crono.empty:
        st.divider()
        st.subheader("Progresso da Semana")

        total_sessoes = len(df_crono)
        concluidos = len(df_crono[df_crono["Status"].str.contains("Concluído", na=False)])
        pendentes = total_sessoes - concluidos
        pct_conclusao = (concluidos / total_sessoes) if total_sessoes > 0 else 0.0

        km_planejados = df_crono["Distância (km)"].sum()
        km_feitos = df_crono[df_crono["Status"].str.contains("Concluído", na=False)]["Distância (km)"].sum()

        st.progress(pct_conclusao)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pendentes", f"{pendentes} sessões")
        c2.metric("Concluídos", f"{concluidos} sessões")
        c3.metric("Distância Realizada", f"{km_feitos:.1f} / {km_planejados:.1f} km")
        c4.metric("Taxa de Adesão", f"{pct_conclusao * 100:.0f}%")

        # 6. GRADE COMPLETA DO CRONOGRAMA COM st.column_config
        st.divider()
        col_crono_title, col_crono_acts = st.columns([3, 2])
        with col_crono_title:
            st.subheader("Grade de Treinos")

        with col_crono_acts:
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("Atualizar Grade", icon=":material/refresh:", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()
            with col_b2:
                with st.popover("Limpar Grade", icon=":material/delete:"):
                    st.write("Deseja apagar os treinos agendados para planejar uma nova semana?")
                    if st.button("Confirmar Limpeza", type="primary", use_container_width=True, icon=":material/delete_forever:"):
                        ok_cl, msg_cl = clear_cronograma_data()
                        if ok_cl:
                            st.toast("Cronograma limpo com sucesso!")
                            st.rerun()
                        else:
                            st.error(msg_cl)

        filtro_status = st.radio(
            "Filtrar grade:",
            options=["Todos", "Apenas Pendentes", "Apenas Concluídos"],
            horizontal=True,
            label_visibility="collapsed",
        )

        df_exibir_crono = df_crono.copy()
        if filtro_status == "Apenas Pendentes":
            df_exibir_crono = df_exibir_crono[df_exibir_crono["Status"] == "Pendente"]
        elif filtro_status == "Apenas Concluídos":
            df_exibir_crono = df_exibir_crono[df_exibir_crono["Status"].str.contains("Concluído", na=False)]

        colunas_ordenadas = [
            c for c in [
                "Status",
                "Dia da Semana",
                "Data Prevista",
                "Tipo de Treino",
                "Distância (km)",
                "Duração (min)",
                "Pace Alvo",
                "RPE Alvo",
                "Estrutura do Treino",
                "Data Conclusão",
            ] if c in df_exibir_crono.columns
        ]

        st.dataframe(
            df_exibir_crono[colunas_ordenadas],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Pendente", "Concluído"],
                    required=True,
                    width="small",
                ),
                "Dia da Semana": st.column_config.TextColumn(
                    "Dia",
                    width="small",
                ),
                "Data Prevista": st.column_config.TextColumn(
                    "Data",
                    width="small",
                ),
                "Tipo de Treino": st.column_config.TextColumn(
                    "Treino",
                    width="medium",
                ),
                "Distância (km)": st.column_config.NumberColumn(
                    "Distância",
                    format="%.1f km",
                    width="small",
                ),
                "Duração (min)": st.column_config.NumberColumn(
                    "Duração",
                    format="%d min",
                    width="small",
                ),
                "Pace Alvo": st.column_config.TextColumn(
                    "Ritmo Alvo",
                    width="small",
                ),
                "RPE Alvo": st.column_config.ProgressColumn(
                    "Intensidade (RPE)",
                    min_value=1,
                    max_value=10,
                    format="%d/10",
                    width="small",
                ),
                "Estrutura do Treino": st.column_config.TextColumn(
                    "Estrutura da Sessão",
                    width="large",
                ),
                "Data Conclusão": st.column_config.TextColumn(
                    "Concluído Em",
                    width="small",
                ),
            },
        )
