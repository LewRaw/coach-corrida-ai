"""
Aba: Montador de Treinos
Prescrição de microciclos semanais personalizados com Inteligência Artificial
"""

from datetime import datetime
import json
import streamlit as st

from config import (
    ESPORTES_OPCOES,
    PlanoSemanalPrescrito,
)
from services.auth_service import get_athlete_profile
from services.data_service import (
    save_weekly_plan_data,
    clear_cronograma_data,
)
from services.ai_coach import get_gemini_client, generate_weekly_plan
from components.cards import render_plan_card


def render():
    """Renderiza a aba de Montagem de Planilhas e Periodização."""
    st.subheader("Montador de Treinos")
    st.caption("Planejamento semanal inteligente baseado no seu histórico e objetivos esportivos.")

    perf = get_athlete_profile()
    esportes_perfil = perf.get("esportes_ativos") or ["Corrida de Rua"]

    tem_triatlo = any("Triatlo" in s for s in esportes_perfil)
    tem_coletivo = any(any(c in s for c in ["Futebol", "Basquete", "Vôlei"]) for s in esportes_perfil)
    tem_multi = len(esportes_perfil) > 1

    opcoes_arquitetura = [
        "Rotina Multi-Esportes Integrada (Corrida, Ciclismo, Natação, Força)",
        "Corrida de Rua (Foco Específico em Quilometragem e Ritmo)",
        "Especialista em Triatlo (Swim, Bike & Run + Transição Brick)",
        "Esportes Coletivos & Condicionamento (Futebol, Basquete ou Vôlei)",
    ]

    default_idx = 0
    if tem_triatlo:
        default_idx = 2
    elif tem_multi:
        default_idx = 0
    elif tem_coletivo:
        default_idx = 3
    else:
        default_idx = 1

    tipo_modalidade = st.radio(
        "Arquitetura do planejamento:",
        options=opcoes_arquitetura,
        index=default_idx,
        horizontal=True,
    )

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        if "Multi-Esportes" in tipo_modalidade:
            esportes_selecionados = st.multiselect(
                "Modalidades incluídas nesta semana:",
                options=ESPORTES_OPCOES,
                default=[e for e in esportes_perfil if e in ESPORTES_OPCOES] or [ESPORTES_OPCOES[0]],
            )
            objetivo_selecionado = st.selectbox(
                "Foco da semana:",
                options=[
                    "Equilíbrio Global: Resistência Aeróbica + Força Funcional",
                    "Prioridade Corrida com Manutenção das Outras Modalidades",
                    "Prioridade Ciclismo com Treinos Cruzados de Suporte",
                    "Preservação Muscular e Condicionamento para Jogos Coletivos",
                    "Ênfase em Fortalecimento e Prevenção de Lesões",
                    "Condicionamento Geral e Queima Calórica",
                ],
            )
            dias_semana = st.slider(
                "Frequência semanal (dias de atividade):",
                min_value=3,
                max_value=7,
                value=int(perf.get("dias_disponiveis", 4) or 4),
            )
            dia_longao = st.selectbox(
                "Dia do treino mais exigente / longo:",
                options=["Sábado", "Domingo", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Segunda-feira", "Terça-feira"],
            )

        elif "Coletivos" in tipo_modalidade:
            esporte_coletivo = st.selectbox(
                "Modalidade coletiva principal:",
                options=["Futebol (Society / Campo / Futsal)", "Basquete (Quadra / Meia Quadra)", "Vôlei (Quadra / Areia / Futevôlei)"],
            )
            dia_longao = st.selectbox(
                "Dia do jogo / partida principal:",
                options=["Quarta-feira", "Sábado", "Domingo", "Terça-feira", "Quinta-feira", "Sexta-feira", "Segunda-feira"],
            )
            objetivo_selecionado = st.selectbox(
                "Objetivo de preparação física:",
                options=[
                    "Fôlego e Resistência para suportar a partida em alta intensidade",
                    "Explosão e Agilidade em tiros curtos com rápida recuperação",
                    "Prevenção de Lesões em adutores, isquiotibiais e joelhos",
                    "Condicionamento Geral intercalando corridas e partidas",
                ],
            )
            esportes_selecionados = [esporte_coletivo, "Corrida de Rua", "Musculação / Fortalecimento"]
            dias_semana = st.slider(
                "Total de dias ativos (jogo + treinos físicos):",
                min_value=3,
                max_value=6,
                value=4,
            )

        elif "Triatlo" in tipo_modalidade:
            objetivo_selecionado = st.selectbox(
                "Meta / Distância no Triatlo:",
                options=[
                    "Triatlo Sprint (750m / 20km / 5km)",
                    "Triatlo Olímpico / Standard (1.500m / 40km / 10km)",
                    "Meio Ironman 70.3 (1.9km / 90km / 21.1km)",
                    "Ironman Completo 140.6 (3.8km / 180km / 42.2km)",
                    "Transição e Brick (Adaptação neuromuscular bike-corrida)",
                ],
            )
            disciplinas = st.multiselect(
                "Disciplinas com treinos prescritos:",
                options=["Natação", "Ciclismo", "Corrida", "Transição Brick", "Fortalecimento"],
                default=["Natação", "Ciclismo", "Corrida"],
            )
            esportes_selecionados = disciplinas or ["Corrida"]
            dias_semana = st.slider(
                "Dias de treino na semana:",
                min_value=4,
                max_value=7,
                value=6,
            )
            dia_longao = st.selectbox(
                "Dia do treino longo (Bike longa ou Brick):",
                options=["Sábado", "Domingo", "Outro dia"],
            )

        else: # Corrida de Rua
            objetivo_selecionado = st.selectbox(
                "Objetivo principal de corrida:",
                options=[
                    "Construção Sólida de Base Aeróbica (Zona 2)",
                    "Recorde Pessoal nos 5 km",
                    "Sub 50 minutos nos 10 km",
                    "Estreia em Meia Maratona (21.1 km)",
                    "Preparação Completa para Maratona (42.2 km)",
                    "Condicionamento Geral e Saúde Cardiovascular",
                ],
            )
            esportes_selecionados = ["Corrida de Rua"]
            dias_semana = st.slider(
                "Quantos dias por semana você pode treinar corrida?",
                min_value=3,
                max_value=6,
                value=4,
            )
            dia_longao = st.selectbox(
                "Dia do Treino Longo (Longão):",
                options=["Domingo", "Sábado", "Quarta-feira", "Outro dia"],
            )

    with col2:
        ciclo_horizonte = st.selectbox(
            "Período do Planejamento:",
            options=[
                "Microciclo Imediato (Próximos 7 dias)",
                "Bloco de Base Aeróbica (4 Semanas)",
                "Polimento Pré-Competição (2 Semanas)",
            ],
        )

        obs_lesoes = st.text_area(
            "Observações, dores recentes ou restrições:",
            placeholder="Ex: Jogo futebol na quarta-feira à noite; leve desconforto no tendão de Aquiles; preferência por pedalar no sábado.",
            height=125,
        )

        st.write("")
        btn_gerar_plano = st.button(
            "Gerar Planilha de Treinos",
            type="primary",
            use_container_width=True,
            icon=":material/auto_awesome:",
        )

    if btn_gerar_plano:
        client = get_gemini_client()
        if not client:
            st.error("Chave de Inteligência Artificial não configurada.")
        else:
            with st.status("Elaborando periodização semanal personalizada...", expanded=True) as status_box:
                try:
                    status_box.write("Analisando histórico de treinos e dosagem de volume...")
                    plano_objeto = generate_weekly_plan(
                        tipo_modalidade=tipo_modalidade,
                        esportes_selecionados=esportes_selecionados,
                        objetivo_selecionado=objetivo_selecionado,
                        dias_semana=dias_semana,
                        dia_longao=dia_longao,
                        ciclo_horizonte=ciclo_horizonte,
                        obs_lesoes=obs_lesoes,
                        gemini_client=client,
                    )
                    st.session_state["plano_estruturado"] = plano_objeto
                    status_box.update(label="Planilha de treinos gerada com sucesso!", state="complete", expanded=False)
                except Exception as e:
                    status_box.update(label="Erro na prescrição da planilha", state="error", expanded=True)
                    st.error(f"Erro: {str(e)}")

    # EXIBIÇÃO DO PLANO GERADO
    if "plano_estruturado" in st.session_state and st.session_state["plano_estruturado"]:
        plano: PlanoSemanalPrescrito = st.session_state["plano_estruturado"]
        st.divider()

        render_plan_card(plano)

        st.subheader("Cronograma das 7 Sessões:")
        for d in plano.dias:
            dist_label = f"{d.distancia_km:.1f} km" if d.distancia_km > 0 else d.modalidade
            dur_label = f"{d.duracao_min:.0f} min" if d.duracao_min > 0 else ""
            header_str = f"{d.dia_semana} ({d.data_prevista}) — {d.tipo_treino} • {dist_label} {dur_label}".strip()

            with st.expander(header_str, expanded=True):
                col_d1, col_d2, col_d3 = st.columns([1.5, 1, 1])
                with col_d1:
                    st.markdown(f"**Ritmo / Intensidade Alvo:** `{d.pace_alvo}`")
                with col_d2:
                    st.markdown(f"**RPE Alvo:** `{d.rpe_alvo}/10`")
                with col_d3:
                    st.markdown(f"**Modalidade:** `{d.modalidade}`")
                st.markdown(f"**Estrutura da Sessão:**\n\n{d.estrutura_treino}")

        substituir_existente = st.checkbox(
            "Substituir cronograma atual (limpar treinos antigos antes de salvar)",
            value=True,
        )

        col_save, col_dl = st.columns([1.5, 1])
        with col_save:
            if st.button("Sincronizar com meu Cronograma", type="primary", use_container_width=True, icon=":material/save:"):
                with st.spinner("Gravando sessões no Cronograma..."):
                    if substituir_existente:
                        clear_cronograma_data()
                    sucesso_sync, msg_sync = save_weekly_plan_data(plano)
                    if sucesso_sync:
                        st.toast("Planilha sincronizada com seu cronograma!")
                        st.success(msg_sync)
                    else:
                        st.error(msg_sync)

        with col_dl:
            texto_md = (
                f"# {plano.titulo_ciclo}\n\n"
                f"## Metodologia\n{plano.diagnostico_metodologia}\n\n"
                f"## Paces de Referência\n{plano.paces_referencia}\n\n"
                f"## Cronograma Semanal\n"
            )
            for d in plano.dias:
                texto_md += f"### {d.dia_semana} ({d.data_prevista}) - {d.tipo_treino}\n"
                texto_md += f"- Distância: {d.distancia_km:.1f} km | Duração: {d.duracao_min:.0f} min | Pace: {d.pace_alvo} | RPE: {d.rpe_alvo}/10\n"
                texto_md += f"- Estrutura: {d.estrutura_treino}\n\n"
            texto_md += f"## Orientações Gerais\n{plano.orientacoes_gerais}\n"

            st.download_button(
                label="Baixar em Markdown (.md)",
                data=texto_md,
                file_name=f"planilha_treinos_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True,
                icon=":material/download:",
            )
