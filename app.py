"""
==============================================================================
Coach de Corrida AI - Running Coach & Training Analytics
Streamlit + Google GenAI (gemini-2.5-flash) + Google Sheets (gspread)
==============================================================================
"""

import io
import json
import os
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List

import gspread
from google.oauth2.service_account import Credentials
from google import genai
from google.genai import types
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from pydantic import BaseModel, Field
import streamlit as st

# ==============================================================================
# CONFIGURAÇÃO GERAL DA PÁGINA STREAMLIT (Mobile & Desktop Responsive)
# ==============================================================================
st.set_page_config(
    page_title="AI Running Coach | Treinador Inteligente",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS para otimização visual limpa, cards destacados e responsividade mobile
st.markdown(
    """
    <style>
    /* Estilização Geral e Fontes */
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
        color: #1E293B;
    }
    .main-subtitle {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    @media (prefers-color-scheme: dark) {
        .main-title { color: #F8FAFC; }
        .main-subtitle { color: #94A3B8; }
    }

    /* Card do Parecer Técnico do Treinador */
    .coach-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #F8FAFC !important;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-left: 6px solid #10B981;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }
    .coach-card h3 {
        color: #10B981 !important;
        margin-top: 0 !important;
        font-size: 1.3rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .coach-card p {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #E2E8F0 !important;
    }
    .coach-badge {
        display: inline-block;
        background-color: rgba(16, 185, 129, 0.2);
        color: #34D399;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }

    /* Ajustes para Métricas em telas pequenas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #64748B;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SHEET_COLUMNS = [
    "Data",
    "Distância (km)",
    "Tempo (min)",
    "Pace Médio",
    "FC Média (bpm)",
    "Zona Predominante",
    "RPE (1-10)",
    "Notas do Atleta",
    "Parecer do Treinador",
    "Registrado Em",
]

# ==============================================================================
# MODELO PYDANTIC PARA STRUCTURED OUTPUT
# ==============================================================================
class TreinoExtracao(BaseModel):
    data: str = Field(description="Data da atividade extraída da imagem no formato DD/MM/AAAA. Se o ano não for visível, use o ano corrente.")
    distancia_km: float = Field(description="Distância total percorrida em quilômetros com até 2 casas decimais (ex: 10.55)")
    tempo_min: float = Field(description="Duração total do treino convertida para minutos decimais (ex: 52 minutos e 30 segundos = 52.5)")
    pace_medio: str = Field(description="Ritmo/pace médio por km no formato mm:ss (ex: '05:12')")
    fc_media: int = Field(description="Frequência cardíaca média em bpm. Se ausente no print, retorne 0.")
    zona_predominante: str = Field(description="Zona de esforço predominante estimada (ex: 'Zona 2 - Aeróbico Leve', 'Zona 3 - Ritmo', 'Zona 4 - Limiar de Lactato', 'Zona 5 - VO2 Máx')")
    parecer_treinador: str = Field(
        description=(
            "Parecer técnico do treinador experiente. Deve conter: "
            "1. Diagnóstico objetivo da sessão (volume x pace x altimetria); "
            "2. Avaliação da resposta cardíaca e desgaste cardiovascular com base no RPE e FC; "
            "3. Recomendação prática e direta para a próxima sessão de treino (ex: regenerativo, descanso ativo, treino de força)."
        )
    )

COACH_SYSTEM_INSTRUCTION = """
Você é um Treinador de Corrida de Rua e Maratonas de elite com mais de 20 anos de experiência na preparação de atletas amadores e competitivos.
Sua comunicação é direta, motivadora, técnica e sem rodeios.
Ao analisar a imagem (print do Garmin Connect, Strava, Polar ou Coros):
1. Extraia meticulosamente os números: distância (km), tempo total (min), ritmo médio (pace mm:ss) e frequência cardíaca média (FC em bpm).
2. Analise a correlação entre os dados da imagem, a Percepção Subjetiva de Esforço (RPE na escala de Borg 1-10) e os comentários do atleta.
3. Elabore um parecer técnico do treinador estruturado em três tópicos claros:
   - [Diagnóstico do Treino]: Análise objetiva da execução em relação ao volume e ritmo.
   - [Intensidade Cardíaca]: Avaliação da resposta fisiológica e eficiência cardiovascular.
   - [Próximo Passo]: Orientação prática e prescritiva para a sessão seguinte (ex: descanso, rodagem leve Z1/Z2, ou hidratação/mobilidade).
Responda ESTRITAMENTE em conformidade com o esquema JSON solicitado.
"""

# ==============================================================================
# SERVIÇOS E CLIENTES COM CACHE (@st.cache_resource)
# ==============================================================================
def get_secret_val(key: str, default: Any = None) -> Any:
    """Busca chave primeiro em st.secrets, depois em os.environ."""
    if key in st.secrets:
        return st.secrets[key]
    return os.environ.get(key, default)


@st.cache_resource
def get_gemini_client(api_key: Optional[str] = None) -> Optional[genai.Client]:
    """Inicializa e armazena em cache o cliente oficial do Google GenAI SDK."""
    final_key = api_key or get_secret_val("GEMINI_API_KEY")
    if not final_key:
        return None
    try:
        return genai.Client(api_key=final_key)
    except Exception as e:
        st.error(f"Erro ao inicializar o cliente Gemini: {e}")
        return None


@st.cache_resource
def get_gspread_client() -> Optional[gspread.Client]:
    """Inicializa o cliente do gspread com as credenciais da Service Account do GCP."""
    try:
        if "gcp_service_account" not in st.secrets:
            return None
        
        sa_info = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = Credentials.from_service_account_info(sa_info, scopes=scopes)
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Erro na autenticação com Google Sheets: {e}")
        return None


def get_or_create_worksheet(gc: gspread.Client, sheet_url: str) -> Optional[gspread.Worksheet]:
    """Abre a planilha e garante a existência da aba 'Treinos' com cabeçalhos."""
    try:
        sh = gc.open_by_url(sheet_url)
        try:
            ws = sh.worksheet("Treinos")
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title="Treinos", rows=500, cols=12)
            ws.append_row(SHEET_COLUMNS)
            return ws
        
        # Se a planilha estiver vazia, adiciona o cabeçalho
        existing_values = ws.get_all_values()
        if not existing_values or len(existing_values) == 0:
            ws.append_row(SHEET_COLUMNS)
        return ws
    except Exception as e:
        st.error(f"Falha ao acessar a planilha do Google Sheets: {e}")
        return None


def append_workout_to_sheets(
    analysis: TreinoExtracao,
    rpe: int,
    user_notes: str
) -> Tuple[bool, str]:
    """Salva com segurança uma nova atividade na aba 'Treinos'."""
    sheet_url = get_secret_val("sheet_url")
    if not sheet_url:
        return False, "URL da planilha ('sheet_url') não configurada nos segredos."

    gc = get_gspread_client()
    if not gc:
        return False, "Credenciais da Service Account ('gcp_service_account') não configuradas ou inválidas."

    try:
        ws = get_or_create_worksheet(gc, sheet_url)
        if not ws:
            return False, "Não foi possível abrir a aba 'Treinos' na planilha."

        nova_linha = [
            analysis.data,
            analysis.distancia_km,
            analysis.tempo_min,
            analysis.pace_medio,
            analysis.fc_media,
            analysis.zona_predominante,
            rpe,
            user_notes.strip(),
            analysis.parecer_treinador.strip(),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ]
        ws.append_row(nova_linha, value_input_option="USER_ENTERED")
        return True, "Treino registrado com sucesso no Google Sheets!"
    except Exception as e:
        return False, f"Erro ao gravar no Google Sheets: {str(e)}"


def load_workouts_from_sheets() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega as atividades salvas no Google Sheets para um DataFrame do Pandas."""
    sheet_url = get_secret_val("sheet_url")
    if not sheet_url:
        return None, "Configure o parâmetro 'sheet_url' em .streamlit/secrets.toml para carregar o histórico."

    gc = get_gspread_client()
    if not gc:
        return None, "Configure 'gcp_service_account' em .streamlit/secrets.toml para sincronizar com o Google Sheets."

    try:
        ws = get_or_create_worksheet(gc, sheet_url)
        if not ws:
            return None, "Não foi possível conectar com a aba 'Treinos'."

        rows = ws.get_all_records()
        if not rows:
            return pd.DataFrame(columns=SHEET_COLUMNS), None

        df = pd.DataFrame(rows)
        # Normalização de tipos numéricos
        if "Distância (km)" in df.columns:
            df["Distância (km)"] = pd.to_numeric(df["Distância (km)"], errors="coerce").fillna(0.0)
        if "Tempo (min)" in df.columns:
            df["Tempo (min)"] = pd.to_numeric(df["Tempo (min)"], errors="coerce").fillna(0.0)
        if "FC Média (bpm)" in df.columns:
            df["FC Média (bpm)"] = pd.to_numeric(df["FC Média (bpm)"], errors="coerce").fillna(0).astype(int)
        if "RPE (1-10)" in df.columns:
            df["RPE (1-10)"] = pd.to_numeric(df["RPE (1-10)"], errors="coerce").fillna(0).astype(int)
        
        # Tenta ordenar por data cronológica se possível
        try:
            df["_data_dt"] = pd.to_datetime(df["Data"], format="%d/%m/%Y", errors="coerce")
            df = df.sort_values(by="_data_dt", ascending=True).reset_index(drop=True)
        except Exception:
            pass

        return df, None
    except Exception as e:
        return None, f"Erro ao consultar o Google Sheets: {str(e)}"


# ==============================================================================
# FUNÇÃO DE ANÁLISE COM GEMINI 2.5 FLASH (Structured Outputs)
# ==============================================================================
def analyze_workout_image(
    image_bytes: bytes,
    mime_type: str,
    rpe: int,
    user_notes: str,
    gemini_client: genai.Client
) -> TreinoExtracao:
    """Invoca o Gemini 2.5 Flash com schema estruturado e dados da atividade."""
    prompt_usuario = (
        f"Analise o print de treino anexo.\n"
        f"Dados informados pelo atleta:\n"
        f"- Percepção Subjetiva de Esforço (RPE): {rpe}/10\n"
        f"- Notas e sensações do atleta: {user_notes if user_notes.strip() else 'Nenhuma nota informada.'}\n\n"
        f"Extraia todas as métricas com precisão e formule seu parecer técnico especializado de treinador."
    )

    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[image_part, prompt_usuario],
        config=types.GenerateContentConfig(
            system_instruction=COACH_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=TreinoExtracao,
            temperature=0.2,
        ),
    )

    # Processamento seguro da resposta estruturada
    if hasattr(response, "parsed") and response.parsed is not None:
        return response.parsed
    elif hasattr(response, "text") and response.text:
        dados_json = json.loads(response.text)
        return TreinoExtracao(**dados_json)
    else:
        raise ValueError("O modelo não retornou uma estrutura JSON válida.")


# ==============================================================================
# CABEÇALHO DA INTERFACE
# ==============================================================================
col_title, col_status = st.columns([4, 1])
with col_title:
    st.markdown('<div class="main-title">🏃 Coach de Corrida AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Consultoria técnica para maratonistas e corredores de rua com Gemini 2.5 & Google Sheets</div>',
        unsafe_allow_html=True,
    )

with col_status:
    # Indicador sutil de configuração
    api_ready = bool(get_secret_val("GEMINI_API_KEY"))
    sheet_ready = bool(get_secret_val("sheet_url")) and ("gcp_service_account" in st.secrets)
    
    if api_ready and sheet_ready:
        st.caption("🟢 **Sistema Conectado**")
    else:
        st.caption("🟡 **Modo Parcial / Demo**")

# ==============================================================================
# ABAS PRINCIPAIS
# ==============================================================================
tab_novo_treino, tab_historico = st.tabs(["🏃 Novo Treino", "📊 Histórico e Gráficos"])

# ------------------------------------------------------------------------------
# ABA 1: NOVO TREINO
# ------------------------------------------------------------------------------
with tab_novo_treino:
    st.markdown("### 📤 Registrar Nova Sessão de Corrida")
    st.write("Envie um print do seu aplicativo de corrida (Garmin Connect, Strava, Polar) para receber a análise imediata do treinador.")

    col_upload, col_inputs = st.columns([1.2, 1], gap="medium")

    with col_upload:
        uploaded_file = st.file_uploader(
            "Print do Treino (Garmin, Strava, etc.)",
            type=["png", "jpg", "jpeg", "webp"],
            help="Certifique-se de que a imagem mostre distância, tempo, ritmo médio (pace) e frequência cardíaca se disponível.",
        )

        if uploaded_file:
            st.image(uploaded_file, caption="Visualização do Print Enviado", use_container_width=True)

    with col_inputs:
        rpe = st.slider(
            "Percepção Subjetiva de Esforço (RPE - Escala de Borg)",
            min_value=1,
            max_value=10,
            value=6,
            help="1: Extremamente fácil (regenerativo) | 5: Ritmo confortável | 7-8: Ritmo de prova / limiar | 10: Esforço máximo exaustivo",
        )
        
        # Legenda dinâmica do RPE
        rpe_labels = {
            1: "1 - Muito Leve (Recuperação Ativa)",
            2: "2 - Leve (Conversacional tranquilo)",
            3: "3 - Moderado Leve (Zona 2 pura)",
            4: "4 - Moderado (Ritmo confortável contínuo)",
            5: "5 - Moderado Firme (Ritmo de Maratona)",
            6: "6 - Firme (Início da Zona de Ritmo)",
            7: "7 - Forte (Ritmo de Meia Maratona)",
            8: "8 - Muito Forte (Limiar de Lactato / 10k)",
            9: "9 - Severo (Tiros de VO2 Máx / 5k)",
            10: "10 - Esforço Máximo Exaustivo",
        }
        st.caption(f"**Intensidade Selecionada:** {rpe_labels.get(rpe, '')}")

        user_notes = st.text_area(
            "Sensações e Notas do Atleta (Opcional)",
            placeholder="Ex: Treino sob calor de 28°C; pernas pesadas nos últimos 2km; hidratação a cada 3km; sem dores articulares.",
            height=130,
        )

        btn_analisar = st.button("🚀 Analisar Treino com Coach AI", type="primary", use_container_width=True)

    # Ação de Análise
    if btn_analisar:
        if not uploaded_file:
            st.warning("⚠️ Por favor, selecione e faça o upload de um print de corrida antes de iniciar a análise.")
        else:
            client = get_gemini_client()
            if not client:
                st.error("🔑 Chave de API do Gemini não configurada! Adicione `GEMINI_API_KEY` em `.streamlit/secrets.toml`.")
            else:
                with st.spinner("🤖 O Treinador está avaliando seu print, métricas cardíacas e gerando o parecer técnico..."):
                    try:
                        image_bytes = uploaded_file.getvalue()
                        mime_type = uploaded_file.type or "image/jpeg"
                        
                        resultado = analyze_workout_image(
                            image_bytes=image_bytes,
                            mime_type=mime_type,
                            rpe=rpe,
                            user_notes=user_notes,
                            gemini_client=client,
                        )

                        # Exibição das Métricas Extraídas em Cards
                        st.markdown("---")
                        st.markdown("### 📈 Métricas Oficiais Extraídas")
                        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                        with m_col1:
                            st.metric("📏 Distância", f"{resultado.distancia_km:.2f} km")
                        with m_col2:
                            st.metric("⏱️ Pace Médio", f"{resultado.pace_medio} /km")
                        with m_col3:
                            fc_display = f"{resultado.fc_media} bpm" if resultado.fc_media > 0 else "Não detectada"
                            st.metric("❤️ FC Média", fc_display)
                        with m_col4:
                            minutos = int(resultado.tempo_min)
                            segundos = int((resultado.tempo_min - minutos) * 60)
                            st.metric("⏳ Duração", f"{minutos}m {segundos:02d}s")

                        # Card de Destaque: Parecer Técnico do Treinador
                        st.markdown(
                            f"""
                            <div class="coach-card">
                                <span class="coach-badge">🎯 {resultado.zona_predominante} • Data: {resultado.data}</span>
                                <h3>📋 Parecer Técnico de Consultoria</h3>
                                <p>{resultado.parecer_treinador.replace(chr(10), '<br>')}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Persistência no Google Sheets
                        with st.spinner("💾 Persistindo sessão no Google Sheets..."):
                            salvo, msg_sheets = append_workout_to_sheets(resultado, rpe, user_notes)
                            if salvo:
                                st.success(f"✅ {msg_sheets}")
                            else:
                                st.warning(f"⚠️ Análise concluída com sucesso, porém: {msg_sheets}")

                    except Exception as e:
                        st.error(f"❌ Ocorreu um erro durante o processamento da atividade: {str(e)}")

# ------------------------------------------------------------------------------
# ABA 2: HISTÓRICO E GRÁFICOS
# ------------------------------------------------------------------------------
with tab_historico:
    st.markdown("### 📊 Histórico de Atividades & Evolução Fisiológica")
    
    col_btn_refresh, _ = st.columns([1, 4])
    with col_btn_refresh:
        refresh = st.button("🔄 Atualizar Dados", use_container_width=True)

    df_treinos, erro_carregamento = load_workouts_from_sheets()

    if erro_carregamento:
        st.info(f"ℹ️ {erro_carregamento}")
        st.markdown(
            """
            > **Dica para ativação completa:**
            > 1. Crie uma planilha no Google Sheets com uma aba chamada `Treinos`.
            > 2. Compartilhe a planilha com o e-mail da sua Service Account como **Editor**.
            > 3. Configure a URL da planilha e o bloco de credenciais em `.streamlit/secrets.toml`.
            """
        )
    elif df_treinos is None or df_treinos.empty:
        st.warning("Nenhum treino registrado ainda na planilha. Registre sua primeira atividade na aba 'Novo Treino'!")
    else:
        # Métricas Globais Consolidadas
        total_km = df_treinos["Distância (km)"].sum()
        total_treinos = len(df_treinos)
        
        # Cálculo de FC média desconsiderando zeros
        fc_series = df_treinos[df_treinos["FC Média (bpm)"] > 0]["FC Média (bpm)"]
        fc_global = int(fc_series.mean()) if not fc_series.empty else 0

        tot_col1, tot_col2, tot_col3, tot_col4 = st.columns(4)
        with tot_col1:
            st.metric("🏃 Volume Total", f"{total_km:.1f} km")
        with tot_col2:
            st.metric("🎯 Total de Sessões", f"{total_treinos} treinos")
        with tot_col3:
            st.metric("❤️ FC Média Geral", f"{fc_global} bpm" if fc_global > 0 else "--")
        with tot_col4:
            km_por_treino = (total_km / total_treinos) if total_treinos > 0 else 0
            st.metric("📊 Média por Sessão", f"{km_por_treino:.1f} km")

        st.markdown("---")

        # Gráficos Analíticos
        tab_g1, tab_g2 = st.columns(2)

        with tab_g1:
            st.markdown("#### 🏃 Volume de Quilometragem por Treino")
            fig_volume = px.bar(
                df_treinos,
                x="Data",
                y="Distância (km)",
                text_auto=".1f",
                color="Distância (km)",
                color_continuous_scale="Viridis",
                labels={"Distância (km)": "Distância (km)", "Data": "Data do Treino"},
                title="Volume de Rodagem (km)",
            )
            fig_volume.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                coloraxis_showscale=False,
                xaxis_tickangle=-45,
            )
            st.plotly_chart(fig_volume, use_container_width=True)

        with tab_g2:
            st.markdown("#### ❤️ Evolução da Frequência Cardíaca Média")
            df_fc = df_treinos[df_treinos["FC Média (bpm)"] > 0]
            if not df_fc.empty:
                fig_fc = px.line(
                    df_fc,
                    x="Data",
                    y="FC Média (bpm)",
                    markers=True,
                    labels={"FC Média (bpm)": "FC Média (bpm)", "Data": "Data do Treino"},
                    title="Monitoramento Cardiovascular",
                )
                fig_fc.update_traces(line_color="#EF4444", line_width=3, marker=dict(size=8, color="#B91C1C"))
                fig_fc.update_layout(margin=dict(l=20, r=20, t=40, b=20), xaxis_tickangle=-45)
                st.plotly_chart(fig_fc, use_container_width=True)
            else:
                st.info("Nenhuma frequência cardíaca registrada para exibir o gráfico temporal.")

        # Tabela Detalhada com visualizador Pandas
        st.markdown("---")
        st.markdown("#### 📋 Registro Geral de Atividades")
        cols_to_show = [
            c for c in [
                "Data", "Distância (km)", "Tempo (min)", "Pace Médio",
                "FC Média (bpm)", "Zona Predominante", "RPE (1-10)", "Notas do Atleta", "Parecer do Treinador"
            ] if c in df_treinos.columns
        ]
        st.dataframe(
            df_treinos[cols_to_show],
            use_container_width=True,
            hide_index=True,
        )
