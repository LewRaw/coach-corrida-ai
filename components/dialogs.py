"""
Diálogos Modais (@st.dialog) do Coach AI
Onboarding, Ajuste de Focos/Esportes e Upload de Print de Atividade
"""

import streamlit as st
from config import ESPORTES_OPCOES
from services.auth_service import (
    get_current_user_id,
    get_athlete_profile,
    update_user_profile,
)
from services.data_service import append_workout_data
from services.ai_coach import get_gemini_client, analyze_workout_image


@st.dialog("Bem-vindo ao Coach AI")
def modal_onboarding():
    """Modal de configuração inicial obrigatório para novos atletas."""
    st.markdown("Vamos calibrar sua assessoria esportiva para prescrever treinos precisos.")

    esportes_sel = st.multiselect(
        "Quais modalidades você pratica?",
        options=ESPORTES_OPCOES,
        default=["Corrida de Rua"],
        help="Selecione todas as modalidades que você pratica com regularidade.",
    )
    if not esportes_sel:
        esportes_sel = ["Corrida de Rua"]

    col1, col2 = st.columns(2)
    with col1:
        nivel_sel = st.selectbox(
            "Nível de experiência:",
            options=["Iniciante", "Intermediário", "Avançado", "Competitivo"],
            index=1,
        )
    with col2:
        dias_sel = st.slider(
            "Quantos dias por semana deseja treinar?",
            min_value=2,
            max_value=7,
            value=4,
        )

    objetivo_sel = st.selectbox(
        "Qual seu objetivo principal?",
        options=[
            "Construção de Base Aeróbica (Zona 2)",
            "Primeiros 5 km ou 10 km",
            "Estreia em Meia Maratona (21.1 km)",
            "Preparação para Maratona (42.2 km)",
            "Triatlo Sprint / Olímpico",
            "Meio Ironman (70.3) / Ironman",
            "Condicionamento Físico e Queima de Gordura",
            "Preparação Física para Futebol / Coletivos",
        ],
        index=2,
    )

    if st.button("Começar Minha Preparação", type="primary", use_container_width=True, icon=":material/rocket_launch:"):
        uid = get_current_user_id()
        if uid:
            update_user_profile(uid, {
                "esportes_ativos": esportes_sel,
                "nivel_experiencia": nivel_sel,
                "dias_disponiveis": dias_sel,
                "objetivo_principal": objetivo_sel,
                "onboarding_concluido": True,
            })
        st.session_state["onboarding_concluido"] = True
        st.toast("Perfil configurado com sucesso!")
        st.rerun()


@st.dialog("Ajustar Modalidades e Objetivos")
def modal_meus_esportes():
    """Modal para atualizar esportes ativos, metas e rotina de treinos."""
    perf = get_athlete_profile()
    esportes_atuais = perf.get("esportes_ativos") or ["Corrida de Rua"]

    novos_esportes = st.multiselect(
        "Suas modalidades ativas:",
        options=ESPORTES_OPCOES,
        default=[e for e in esportes_atuais if e in ESPORTES_OPCOES] or [ESPORTES_OPCOES[0]],
    )

    col1, col2 = st.columns(2)
    with col1:
        niveis = ["Iniciante", "Intermediário", "Avançado", "Competitivo"]
        nivel_atual = perf.get("nivel_experiencia", "Intermediário")
        idx_niv = niveis.index(nivel_atual) if nivel_atual in niveis else 1
        novo_nivel = st.selectbox("Nível de experiência:", options=niveis, index=idx_niv)

    with col2:
        novo_dias = st.slider(
            "Dias disponíveis por semana:",
            min_value=2,
            max_value=7,
            value=int(perf.get("dias_disponiveis", 4) or 4),
        )

    todas_metas = [
        "Construção de Base Aeróbica (Zona 2)",
        "Primeiros 5 km ou 10 km",
        "Estreia em Meia Maratona (21.1 km)",
        "Preparação para Maratona (42.2 km)",
        "Triatlo Sprint / Olímpico",
        "Meio Ironman (70.3) / Ironman",
        "Condicionamento Físico e Queima de Gordura",
        "Preparação Física para Futebol / Coletivos",
    ]
    meta_atual = perf.get("objetivo_principal", "Meia Maratona")
    idx_m = todas_metas.index(meta_atual) if meta_atual in todas_metas else 2
    nova_meta = st.selectbox("Objetivo esportivo principal:", options=todas_metas, index=idx_m)

    if st.button("Salvar Objetivos", type="primary", use_container_width=True, icon=":material/save:"):
        uid = get_current_user_id()
        if uid:
            update_user_profile(uid, {
                "esportes_ativos": novos_esportes or ["Corrida de Rua"],
                "nivel_experiencia": novo_nivel,
                "dias_disponiveis": novo_dias,
                "objetivo_principal": nova_meta,
            })
        st.toast("Objetivos e modalidades atualizados!")
        st.rerun()


@st.dialog("Registrar Treino com Print")
def modal_registrar_treino_print():
    """Modal de envio e análise de imagem da atividade (Garmin, Strava, Polar, etc.)."""
    st.markdown("Carregue a captura de tela do seu relógio ou aplicativo para receber parecer técnico e salvar no histórico.")

    uploaded_file = st.file_uploader(
        "Captura de tela da atividade:",
        type=["png", "jpg", "jpeg", "webp"],
        key="upload_print_modal",
    )

    if uploaded_file:
        st.image(uploaded_file, caption="Visualização do Print Enviado", use_container_width=True)

    rpe = st.slider(
        "Esforço Percebido (Escala Borg 1 a 10):",
        min_value=1,
        max_value=10,
        value=5,
        help="1: Muito leve | 3: Zona 2 confortável | 5: Ritmo de prova | 7-8: Limiar / Tiros | 10: Exaustão",
    )

    user_notes = st.text_area(
        "Comentários ou sensações:",
        placeholder="Ex: Foco em manter Z2; calor elevado no km final; boa resposta nas pernas.",
        height=90,
    )

    if st.button("Analisar e Salvar Atividade", type="primary", use_container_width=True, icon=":material/analytics:"):
        if not uploaded_file:
            st.warning("Selecione uma imagem de treino antes de continuar.")
        else:
            client = get_gemini_client()
            if not client:
                st.error("Chave de Inteligência Artificial não configurada.")
            else:
                with st.spinner("Analisando atividade com o Treinador..."):
                    try:
                        analise = analyze_workout_image(
                            image_bytes=uploaded_file.getvalue(),
                            mime_type=uploaded_file.type or "image/jpeg",
                            rpe=rpe,
                            user_notes=user_notes,
                            gemini_client=client,
                        )
                        salvo, msg_salvo = append_workout_data(analise, rpe, user_notes)
                        st.session_state["ultimo_treino"] = analise
                        st.cache_data.clear()
                        if salvo:
                            st.toast("Treino registrado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro na análise: {str(e)}")
