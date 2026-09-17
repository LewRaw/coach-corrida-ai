"""
Diálogos Modais (@st.dialog) do Coach AI
Onboarding, Ajuste de Focos/Esportes e Conclusão de Treinos (Print, Manual ou Pular)
"""

from typing import Any, Optional
import time
import streamlit as st
from config import ESPORTES_OPCOES, TreinoExtracao
from services.auth_service import (
    get_current_user_id,
    get_athlete_profile,
    update_user_profile,
    get_user_session_token,
    auth_update_password,
)
from services.data_service import (
    append_workout_data,
    mark_workout_as_completed_data,
    delete_workout_from_cronograma_data,
)
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


@st.dialog("Concluir Treino")
def modal_concluir_treino(proximo: Any = None):
    """
    Modal para conclusão de treino obrigatória com 3 opções:
    1. Enviar Print (relógio/app com análise de IA)
    2. Inserir Manualmente (esteira, sem relógio, esportes coletivos)
    3. Pular Treino (remove do planejamento e avança para a próxima sessão)
    """
    proximo_id = ""
    tipo_treino_str = "Treino Prescrito"
    dia_str = ""
    dist_sugerida = 0.0
    dur_sugerida = 45.0
    pace_sugerido = ""
    rpe_sugerido = 5

    if proximo is not None:
        proximo_id = str(proximo["ID"]) if "ID" in proximo else (str(proximo["id"]) if "id" in proximo else str(proximo.name))
        tipo_treino_str = str(proximo.get("Tipo de Treino", "Treino"))
        dia_str = f"{proximo.get('Dia da Semana', '')} ({proximo.get('Data Prevista', '')})"
        dist_sugerida = float(proximo.get("Distância (km)", 0.0) or 0.0)
        dur_sugerida = float(proximo.get("Duração (min)", 45.0) or 45.0)
        pace_sugerido = str(proximo.get("Pace Alvo", "") or "")
        rpe_sugerido = int(proximo.get("RPE Alvo", 5) or 5)

        st.caption(f"Sessão: **{tipo_treino_str}** • {dia_str}")

    tab_print, tab_manual, tab_skip = st.tabs([
        "Enviar Print",
        "Inserir Manualmente",
        "Pular Treino",
    ])

    # ==========================================
    # ABA 1: ENVIAR PRINT (GALERIA / FOTO)
    # ==========================================
    with tab_print:
        st.markdown("Carregue a captura de tela do Garmin Connect, Strava, Polar ou Apple Fitness para a IA extrair ritmo, FC e fornecer parecer técnico.")

        uploaded_file = st.file_uploader(
            "Captura de tela da atividade:",
            type=["png", "jpg", "jpeg", "webp"],
            key="upload_concluir_print",
        )

        if uploaded_file:
            st.image(uploaded_file, caption="Visualização do Print Enviado", use_container_width=True)

        rpe_print = st.slider(
            "Esforço Percebido (Escala Borg 1 a 10):",
            min_value=1,
            max_value=10,
            value=rpe_sugerido,
            key="rpe_concluir_print",
            help="1: Muito leve | 3: Zona 2 confortável | 5: Ritmo de prova | 7-8: Limiar / Tiros | 10: Exaustão",
        )

        notes_print = st.text_area(
            "Comentários ou sensações da sessão:",
            placeholder="Ex: Treino concluído conforme o planejamento; hidratação constante.",
            height=80,
            key="notes_concluir_print",
        )

        if st.button("Analisar Print e Concluir Treino", type="primary", use_container_width=True, icon=":material/analytics:", key="btn_exec_concluir_print"):
            if not uploaded_file:
                st.warning("Por favor, selecione uma captura de tela da atividade antes de concluir.")
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
                                rpe=rpe_print,
                                user_notes=notes_print,
                                gemini_client=client,
                            )
                            append_workout_data(analise, rpe_print, notes_print)
                            if proximo_id:
                                mark_workout_as_completed_data(proximo_id)
                            st.session_state["ultimo_treino"] = analise
                            st.cache_data.clear()
                            st.toast("Treino concluído com análise técnica da IA!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro na análise: {str(e)}")

    # ==========================================
    # ABA 2: INSERIR DADOS MANUALMENTE
    # ==========================================
    with tab_manual:
        st.markdown("Correu na esteira, esqueceu o relógio ou participou de esporte coletivo? Informe os dados reais abaixo:")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            modalidades = ["Corrida", "Ciclismo", "Natação", "Futebol", "Basquete", "Vôlei", "Musculação", "Outro"]
            idx_mod = 0
            for i, m in enumerate(modalidades):
                if m.lower() in tipo_treino_str.lower():
                    idx_mod = i
                    break
            modalidade_man = st.selectbox("Modalidade executada:", options=modalidades, index=idx_mod, key="mod_concluir_man")

        with col_m2:
            zona_man = st.selectbox(
                "Zona / Intensidade Predominante:",
                options=[
                    "Z1 Regenerativo",
                    "Z2 Rodagem Aeróbica",
                    "Z3 Tempo / Ritmo",
                    "Z4 Limiar",
                    "Z5 VO2 Máx / Explosão",
                    "Força / Mobilidade",
                    "Intensidade de Partida",
                ],
                index=1 if "Z2" in pace_sugerido or dist_sugerida > 0 else 0,
                key="zona_concluir_man",
            )

        col_m3, col_m4, col_m5 = st.columns(3)
        with col_m3:
            dist_man = st.number_input(
                "Distância (km):",
                min_value=0.0,
                max_value=250.0,
                value=dist_sugerida,
                step=0.1,
                format="%.2f",
                key="dist_concluir_man",
            )
        with col_m4:
            dur_man = st.number_input(
                "Duração (minutos):",
                min_value=1.0,
                max_value=600.0,
                value=dur_sugerida if dur_sugerida > 0 else 45.0,
                step=1.0,
                format="%.0f",
                key="dur_concluir_man",
            )
        with col_m5:
            # Cálculo automático do ritmo médio estimado se preenchido km e tempo
            pace_estimado = pace_sugerido
            if dist_man > 0 and dur_man > 0:
                min_km = dur_man / dist_man
                min_i = int(min_km)
                sec_i = int(round((min_km - min_i) * 60))
                if sec_i >= 60:
                    min_i += 1
                    sec_i = 0
                pace_estimado = f"{min_i:02d}:{sec_i:02d}/km"

            pace_man = st.text_input(
                "Ritmo Médio / Pace:",
                value=pace_estimado or "05:30/km",
                placeholder="Ex: 05:30/km",
                key="pace_concluir_man",
            )

        col_m6, col_m7 = st.columns(2)
        with col_m6:
            fc_man = st.number_input(
                "FC Média (bpm, opcional):",
                min_value=0,
                max_value=240,
                value=0,
                step=1,
                help="Deixe 0 se não utilizou monitor de frequência cardíaca.",
                key="fc_concluir_man",
            )
        with col_m7:
            rpe_man = st.slider(
                "Esforço Percebido (RPE 1-10):",
                min_value=1,
                max_value=10,
                value=rpe_sugerido,
                key="rpe_concluir_man_slider",
            )

        notes_man = st.text_area(
            "Notas e comentários da sessão:",
            placeholder="Ex: Treino na esteira da academia com inclinação leve. Ritmo confortável.",
            height=70,
            key="notes_concluir_man",
        )

        if st.button("Salvar Dados e Concluir Treino", type="primary", use_container_width=True, icon=":material/check_circle:", key="btn_exec_concluir_man"):
            analise_manual = TreinoExtracao(
                distancia_km=float(dist_man),
                tempo_min=float(dur_man),
                pace_medio=str(pace_man).strip() or f"{dur_man:.0f} min",
                fc_media=int(fc_man),
                zona_predominante=str(zona_man),
                modalidade=str(modalidade_man),
                parecer_treinador=(
                    f"Sessão de {modalidade_man} registrada manualmente pelo atleta ({dist_man:.1f} km em {dur_man:.0f} min, "
                    f"RPE {rpe_man}/10). Treino validado e computado com sucesso no volume de treinamento."
                ),
            )
            append_workout_data(analise_manual, rpe_man, notes_man)
            if proximo_id:
                mark_workout_as_completed_data(proximo_id)
            st.session_state["ultimo_treino"] = analise_manual
            st.cache_data.clear()
            st.toast("Treino registrado manualmente com sucesso!")
            st.rerun()

    # ==========================================
    # ABA 3: PULAR TREINO
    # ==========================================
    with tab_skip:
        st.markdown(
            "Imprevistos acontecem na rotina (chuva, compromissos ou necessidade de descanso extra). "
            "Ao pular esta sessão, ela será **removida do planejamento** desta semana e a próxima sessão assumirá o destaque do seu Painel imediatamente."
        )

        st.warning(f"Confirma a remoção da sessão **'{tipo_treino_str}'** do seu cronograma?")

        if st.button("Confirmar e Pular este Treino", type="secondary", use_container_width=True, icon=":material/delete_sweep:", key="btn_exec_pular_treino"):
            if proximo_id:
                delete_workout_from_cronograma_data(proximo_id)
                st.cache_data.clear()
                st.toast("Sessão pulada! A próxima sessão já assumiu o topo do seu Painel.")
                st.rerun()
            else:
                st.info("Nenhuma sessão pendente selecionada para pular.")


def modal_registrar_treino_print():
    """Compatibilidade para upload direto de print sem sessão agendada."""
    modal_concluir_treino(None)


@st.dialog("Atalho na Tela de Início do Celular")
def modal_atalho_celular():
    """Exibe instruções detalhadas e o link permanente com chave de acesso para o atalho mobile."""
    uid = get_current_user_id()
    token = get_user_session_token(uid) if uid else None

    st.markdown("### 📲 Acesso Permanente Sem Senha")
    st.markdown(
        "No iOS (iPhone) e Android, os atalhos de tela inicial rodam em um ambiente isolado do navegador. "
        "Para que o ícone no seu celular **nunca peça login novamente**, adicione o seu link pessoal com chave persistente:"
    )

    if token:
        app_url = f"https://coach-corrida-ai.streamlit.app/?token={token}"
        st.markdown("**Seu link pessoal exclusivo com token de acesso:**")
        st.code(app_url, language=None)

        st.info(
            "**Passo a passo no seu celular:**\n\n"
            "1. **Copie o link acima** e envie para seu WhatsApp ou abra direto no navegador do celular.\n"
            "2. **No iPhone (Safari):** Abra o link, toque no ícone de **Compartilhar** (quadrado com seta para cima) ➔ **'Adicionar à Tela de Início'**.\n"
            "3. **No Android (Chrome):** Abra o link, toque no menu **(⋮ três pontos)** ➔ **'Adicionar à tela inicial'** ou **'Instalar aplicativo'**.\n\n"
            "✅ O atalho criado terá sua chave memorizada permanentemente e entrará direto no seu Painel de Treinos!"
        )
    else:
        st.warning("Não foi possível carregar sua chave de acesso. Verifique sua conexão com o servidor.")


@st.dialog("Alterar Senha de Acesso")
def modal_alterar_senha():
    """Modal para o atleta logado atualizar sua senha com segurança."""
    st.markdown("Defina uma nova senha para sua conta:")

    with st.form("form_change_password_dialog"):
        p1 = st.text_input("Nova Senha (mínimo 6 dígitos)", type="password", placeholder="••••••••", key="dlg_chg_pass1")
        p2 = st.text_input("Confirmar Nova Senha", type="password", placeholder="••••••••", key="dlg_chg_pass2")
        btn_salvar = st.form_submit_button("Atualizar Minha Senha", type="primary", use_container_width=True, icon=":material/key:")

        if btn_salvar:
            if not p1 or len(p1) < 6:
                st.warning("A nova senha deve ter pelo menos 6 caracteres.")
            elif p1 != p2:
                st.error("As senhas digitadas não coincidem.")
            else:
                with st.spinner("Atualizando senha no servidor..."):
                    ok_u, msg_u = auth_update_password(p1)
                    if ok_u:
                        st.success("Senha alterada com sucesso!")
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error(msg_u)
