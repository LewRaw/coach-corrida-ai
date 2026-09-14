"""
Aba: Histórico & Gráficos de Evolução
Métricas acumuladas, gráficos de consistência e tabela histórica com st.column_config
"""

import pandas as pd
import streamlit as st
import plotly.express as px

from services.data_service import load_workouts_data


def render():
    """Renderiza o histórico completo e gráficos de evolução do atleta."""
    col_hist_t, col_hist_act = st.columns([3, 1])
    with col_hist_t:
        st.subheader("Histórico e Gráficos de Evolução")
        st.caption("Acompanhe o volume acumulado, consistência e resposta cardiovascular ao longo do tempo.")

    with col_hist_act:
        if st.button("Atualizar Dados", icon=":material/refresh:", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    df_treinos, erro_hist = load_workouts_data()

    if erro_hist:
        st.info(erro_hist)
        return

    if df_treinos is None or df_treinos.empty:
        st.info("Nenhuma atividade registrada ainda. Envie o print do seu primeiro treino para iniciar o histórico.")
        return

    # 1. MÉTRICAS CONSOLIDADAS
    total_atividades = len(df_treinos)
    dist_total = df_treinos["Distância (km)"].sum() if "Distância (km)" in df_treinos.columns else 0.0
    tempo_total_min = df_treinos["Tempo (min)"].sum() if "Tempo (min)" in df_treinos.columns else 0.0
    horas_totais = tempo_total_min / 60.0

    fc_series = df_treinos[df_treinos["FC Média (bpm)"] > 0]["FC Média (bpm)"] if "FC Média (bpm)" in df_treinos.columns else pd.Series()
    fc_media_geral = int(round(fc_series.mean())) if not fc_series.empty else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total de Atividades", f"{total_atividades} treinos")
    m2.metric("Distância Acumulada", f"{dist_total:.1f} km")
    m3.metric("Tempo em Movimento", f"{horas_totais:.1f} horas")
    m4.metric("FC Média Geral", f"{fc_media_geral} bpm" if fc_media_geral > 0 else "--")

    st.divider()

    # 2. GRÁFICOS DE EVOLUÇÃO
    col_g1, col_g2 = st.columns(2, gap="medium")

    with col_g1:
        st.markdown("**Progressão de Volume por Sessão**")
        df_plot = df_treinos.copy()
        if "Data" in df_plot.columns:
            df_plot["Sessão"] = [f"#{i+1} ({d})" for i, d in enumerate(df_plot["Data"])]
        else:
            df_plot["Sessão"] = [f"#{i+1}" for i in range(len(df_plot))]

        fig_dist = px.bar(
            df_plot,
            x="Sessão",
            y="Distância (km)",
            color="Distância (km)",
            color_continuous_scale=["#6366F1", "#4338CA"],
            text_auto=".1f",
        )
        fig_dist.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            xaxis_title="",
            yaxis_title="Quilômetros (km)",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_g2:
        st.markdown("**Resposta Cardíaca e Intensidade**")
        df_fc = df_treinos[df_treinos["FC Média (bpm)"] > 0]
        if not df_fc.empty:
            fig_fc = px.scatter(
                df_fc,
                x="Tempo (min)",
                y="FC Média (bpm)",
                size="Distância (km)",
                color="RPE (1-10)",
                color_continuous_scale="Viridis",
                hover_data=["Data", "Pace Médio"],
            )
            fig_fc.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=300,
                xaxis_title="Duração (min)",
                yaxis_title="FC Média (bpm)",
            )
            st.plotly_chart(fig_fc, use_container_width=True)
        else:
            st.info("Nenhum dado de frequência cardíaca detectado nas atividades anteriores.")

    # 3. TABELA DE HISTÓRICO COM st.column_config
    st.divider()
    st.markdown("**Registro Completo de Atividades**")

    colunas_hist = [
        c for c in [
            "Data",
            "Distância (km)",
            "Tempo (min)",
            "Pace Médio",
            "FC Média (bpm)",
            "Zona Predominante",
            "RPE (1-10)",
            "Notas do Atleta",
            "Parecer do Treinador",
        ] if c in df_treinos.columns
    ]

    st.dataframe(
        df_treinos[colunas_hist].iloc[::-1],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Data": st.column_config.TextColumn(
                "Data",
                width="small",
            ),
            "Distância (km)": st.column_config.NumberColumn(
                "Distância",
                format="%.1f km",
                width="small",
            ),
            "Tempo (min)": st.column_config.NumberColumn(
                "Duração",
                format="%.0f min",
                width="small",
            ),
            "Pace Médio": st.column_config.TextColumn(
                "Ritmo Médio",
                width="small",
            ),
            "FC Média (bpm)": st.column_config.NumberColumn(
                "FC Média",
                format="%d bpm",
                width="small",
            ),
            "Zona Predominante": st.column_config.TextColumn(
                "Zona",
                width="medium",
            ),
            "RPE (1-10)": st.column_config.ProgressColumn(
                "Esforço (RPE)",
                min_value=1,
                max_value=10,
                format="%d/10",
                width="small",
            ),
            "Notas do Atleta": st.column_config.TextColumn(
                "Notas",
                width="medium",
            ),
            "Parecer do Treinador": st.column_config.TextColumn(
                "Parecer Técnico",
                width="large",
            ),
        },
    )
