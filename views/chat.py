"""
Aba: Coach AI (Chat Interativo Especializado)
Consultoria esportiva em tempo real com histórico do atleta
"""

import streamlit as st
from services.ai_coach import get_gemini_client, generate_coach_chat_response


def render():
    """Renderiza a interface centralizada de chat com o Treinador."""
    st.subheader("Coach AI")
    st.caption("Tire dúvidas sobre ritmo, adaptação cardiovascular, recuperação e ajustes de planilha.")

    if "chat_messages" not in st.session_state:
        msg_inicial = (
            "Olá, atleta! Sou seu Treinador de Corrida e Multi-Esportes. "
            "Tenho acesso a todo o seu histórico registrado na nuvem. "
            "Você pode me perguntar sobre sua evolução de ritmo, sensações do último treino, "
            "se está pronto para subir de distância ou qual a recomendação para a próxima sessão. "
            "Como posso orientá-lo hoje?"
        )
        st.session_state["chat_messages"] = [{"role": "assistant", "content": msg_inicial}]

    # CHIPS DE CONSULTAS RÁPIDAS COM ÍCONES MATERIAL DESIGN
    st.markdown("**Perguntas Frequentes:**")
    c1, c2, c3, c4 = st.columns(4)
    quick_query = None

    with c1:
        if st.button("Evolução de ritmo", icon=":material/trending_up:", use_container_width=True):
            quick_query = "Analise minha evolução de ritmo (pace) e consistência com base no meu histórico de treinos."
    with c2:
        if st.button("Pronto para Meia?", icon=":material/flag:", use_container_width=True):
            quick_query = "Com base no meu volume e treinos registrados, estou pronto para correr uma Meia Maratona (21k)?"
    with c3:
        if st.button("O que treinar amanhã?", icon=":material/event:", use_container_width=True):
            quick_query = "Considerando meu último treino registrado e o desgaste cardiovascular, qual treino devo fazer amanhã?"
    with c4:
        if st.button("Eficiência cardíaca", icon=":material/favorite:", use_container_width=True):
            quick_query = "Avalie minha eficiência cardíaca relacionando ritmo, frequência cardíaca média e RPE nos meus treinos."

    st.divider()

    # MENSAGENS ANTERIORES
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ENTRADA DO USUÁRIO
    user_prompt = st.chat_input("Digite sua dúvida para o Treinador...")
    texto_enviar = quick_query or user_prompt

    if texto_enviar:
        st.session_state["chat_messages"].append({"role": "user", "content": texto_enviar})
        with st.chat_message("user"):
            st.markdown(texto_enviar)

        client = get_gemini_client()
        if not client:
            st.error("Chave de Inteligência Artificial não configurada.")
        else:
            with st.chat_message("assistant"):
                with st.spinner("O Treinador está analisando seus dados..."):
                    try:
                        resposta = generate_coach_chat_response(
                            messages=st.session_state["chat_messages"],
                            gemini_client=client,
                        )
                        st.markdown(resposta)
                        st.session_state["chat_messages"].append({"role": "assistant", "content": resposta})
                    except Exception as e:
                        st.error(f"Erro ao consultar o Treinador: {str(e)}")
