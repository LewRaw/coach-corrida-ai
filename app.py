"""
Coach AI - Assessoria Esportiva e Periodização Inteligente Multi-Esportes
Ponto de Entrada Principal (Orquestração de Sessão e Navegação)
"""

import streamlit as st

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Coach AI",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 1.1 REDIRECIONAMENTO AUTOMÁTICO PARA O NOVO APP VERCEL
try:
    from urllib.parse import urlencode
    query_dict = dict(st.query_params)
    target_url = "https://coach-corrida-ai.vercel.app/"
    if query_dict:
        target_url = f"https://coach-corrida-ai.vercel.app/?{urlencode(query_dict)}"
except Exception:
    target_url = "https://coach-corrida-ai.vercel.app/"

if st.query_params.get("legacy") != "true":
    st.markdown(
        f"""
        <meta http-equiv="refresh" content="0; url={target_url}">
        <script>
            window.location.replace("{target_url}");
        </script>
        <div style="max-width: 480px; margin: 60px auto; padding: 32px; background: #141414; border: 1px solid #262626; border-radius: 24px; text-align: center; color: white; font-family: sans-serif;">
            <div style="width: 56px; height: 56px; background: #11C76F; border-radius: 18px; margin: 0 auto 16px; display: flex; align-items: center; justify-content: center; font-size: 26px;">
                🏃
            </div>
            <h2 style="margin: 0 0 8px; font-size: 20px; font-weight: 800;">Coach AI Mudou!</h2>
            <p style="margin: 0 0 24px; font-size: 13px; color: #8E8E93; line-height: 1.5;">
                Estamos te redirecionando automaticamente para a nova versão na Vercel...
            </p>
            <a href="{target_url}" style="display: block; padding: 14px 20px; background: #11C76F; color: white; text-decoration: none; border-radius: 16px; font-weight: bold; font-size: 14px;">
                Acessar Novo App
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# 2. IMPORTAÇÃO DOS MÓDULOS ARQUITETURAIS
from services.auth_service import (
    restore_user_from_token,
    get_current_user,
    get_athlete_profile,
    render_login_screen,
)
from components.header import render_header
from components.dialogs import modal_onboarding, modal_meus_esportes
from views import (
    dashboard,
    workout_builder,
    history,
    chat,
    help_view,
)

# 3. RESTAURAÇÃO DE SESSÃO PERSISTENTE (MOBILE / PWA)
restore_user_from_token()

# 4. CONTROLE DE ACESSO OBRIGATÓRIO (GATE DE AUTENTICAÇÃO E RECUPERAÇÃO DE SENHA)
is_recovery_link = (
    st.query_params.get("recovery") == "true"
    or st.query_params.get("type") == "recovery"
    or "code" in st.query_params
)
user = get_current_user()
if not user or is_recovery_link:
    render_login_screen()
    st.stop()

# 5. ONBOARDING AUTOMÁTICO PARA PRIMEIRO ACESSO
perf = get_athlete_profile()
if not perf.get("onboarding_concluido") and not st.session_state.get("onboarding_shown"):
    st.session_state["onboarding_shown"] = True
    modal_onboarding()

# 6. CABEÇALHO UNIFICADO COM MENU DO ATLETA (POPOVER)
render_header(on_edit_profile=modal_meus_esportes)

# 7. NAVEGAÇÃO ENTRE ABAS PRINCIPAIS (ZERO EMOJIS OPERACIONAIS)
tab_painel, tab_planilha, tab_historico, tab_chat, tab_ajuda = st.tabs([
    "Painel",
    "Montador de Treinos",
    "Histórico e Gráficos",
    "Coach AI",
    "Ajuda e Glossário",
])

with tab_painel:
    dashboard.render()

with tab_planilha:
    workout_builder.render()

with tab_historico:
    history.render()

with tab_chat:
    chat.render()

with tab_ajuda:
    help_view.render()
