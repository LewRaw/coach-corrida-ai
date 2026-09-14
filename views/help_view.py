"""
Aba: Ajuda & Glossário do Atleta
Instalação no celular (PWA) e dicionário técnico esportivo
"""

import streamlit as st


def render():
    """Renderiza a central de ajuda e glossário."""
    st.subheader("Ajuda e Glossário do Atleta")
    st.caption("Orientações para transformar o aplicativo em atalho no celular e conceitos fundamentais de treinamento.")

    tab_mobile, tab_glossario = st.tabs(["Instalação no Celular", "Dicionário Esportivo"])

    with tab_mobile:
        st.markdown(
            """
            ### Como salvar o Coach AI como aplicativo no smartphone:

            **No iPhone (Safari):**
            1. Abra o link do Coach AI no Safari.
            2. Toque no ícone de **Compartilhar** (quadrado com uma seta para cima).
            3. Role para baixo e selecione **Adicionar à Tela de Início**.
            4. Confirme tocando em **Adicionar**. O ícone aparecerá como um app nativo.

            **No Android (Google Chrome):**
            1. Abra o link no Chrome.
            2. Toque nos três pontos no canto superior direito.
            3. Selecione **Instalar aplicativo** ou **Adicionar à tela inicial**.
            4. Confirme para criar o atalho direto.

            ---
            ### Rotina de Uso Recomendada:
            - **Ver a próxima sessão:** No **Painel**, consulte o card com ritmo alvo, distância e estrutura.
            - **Concluir o treino:** Ao terminar, clique em **Concluir Treino** para atualizar sua planilha.
            - **Registrar com print:** Clique em **Anexar Print** para carregar a captura do relógio ou app e obter análise técnica detalhada.
            - **Consultar o Treinador:** Acesse a aba **Coach AI** para tirar dúvidas sobre dores, estratégias de ritmo e nutrição básica.
            """
        )

    with tab_glossario:
        st.markdown(
            """
            ### Conceitos Fundamentais de Corrida e Triatlo:

            **Ritmo / Pace (min/km):**
            Tempo gasto para percorrer 1 quilômetro. Quanto menor o número, maior a velocidade. Exemplo: ritmo de `05:30/km` representa 5 minutos e 30 segundos por quilômetro.

            **Escala de Borg (RPE - Percepção Subjetiva de Esforço):**
            Avaliação de 1 a 10 da intensidade do esforço:
            - **1 a 2:** Muito leve / Descanso ativo.
            - **3 a 4:** Zona 2 aeróbica confortável (conversa fácil).
            - **5 a 6:** Ritmo moderado / Ritmo de Maratona.
            - **7 a 8:** Ritmo forte / Limiar anaeróbico / Tiros longos.
            - **9 a 10:** Esforço máximo / Exaustão.

            **Frequência Cardíaca (FC / BPM):**
            Batimentos cardíacos por minuto registrados pelo relógio ou cinta peitoral.

            **Zonas de Treinamento Cardíaco (Z1 a Z5):**
            - **Z1 (Regenerativo):** Trote levíssimo ou soltura em bicicleta para acelerar a recuperação pós-esforço.
            - **Z2 (Base Aeróbica):** Ritmo conversacional, respiração fácil e estabilizada. Constrói a eficiência mitocondrial e resistência cardiovascular.
            - **Z3 (Tempo Run / Moderado):** Ritmo de Meia Maratona ou prova de 10 km sustentável.
            - **Z4 (Limiar de Lactato):** Ritmo forte sustentável por 30 a 60 minutos. Respiração pesada.
            - **Z5 (VO2 Máx / Anaeróbico):** Intensidade máxima para tiros curtos e explosivos.

            **Transição Brick (Triatlo):**
            Sessão que combina Ciclismo de intensidade seguido imediatamente de Corrida a pé para habituar o sistema neuromuscular a correr com pernas pesadas.

            **Cadência:**
            - *Na Corrida:* Passos por minuto (faixa ideal recomendada: 165 a 180 passos/minuto).
            - *No Ciclismo:* Rotações por minuto dos pedais (RPM, ideal entre 85 e 95 RPM).
            """
        )
