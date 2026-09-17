"""
Componente de Cabeçalho e Menu do Atleta
Coach AI
"""

from typing import Callable
import streamlit as st
from services.auth_service import get_current_user, get_athlete_profile, auth_sign_out
from components.dialogs import modal_atalho_celular, modal_alterar_senha


def render_header(on_edit_profile: Callable[[], None]):
    """
    Renderiza o cabeçalho superior unificado com título, subtítulo e menu popover do atleta.
    """
    user = get_current_user()
    perf = get_athlete_profile()
    nome_display = perf.get("nome") or (user.get("nome") if user else None) or (user.get("email") if user else "Atleta")
    esportes_list = perf.get("esportes_ativos") or ["Corrida de Rua"]

    col_brand, col_user = st.columns([3.2, 1.3])

    with col_brand:
        st.title("Coach AI")
        st.caption("Consultoria esportiva e periodização personalizada")

    with col_user:
        st.write("")
        with st.popover(f"{nome_display}", icon=":material/account_circle:", use_container_width=True):
            st.markdown(f"**Atleta:** {nome_display}")
            st.caption(f"Modalidades: {', '.join(esportes_list)}")
            st.caption(f"Meta: {perf.get('objetivo_principal', 'Meia Maratona')}")
            st.divider()

            if st.button("Ajustar Objetivos", icon=":material/tune:", use_container_width=True):
                on_edit_profile()

            if st.button("Atalho no Celular", icon=":material/smartphone:", use_container_width=True):
                modal_atalho_celular()

            if st.button("Alterar Senha", icon=":material/lock_reset:", use_container_width=True):
                modal_alterar_senha()

            if st.button("Encerrar Sessão", icon=":material/logout:", use_container_width=True):
                auth_sign_out()
                st.rerun()
