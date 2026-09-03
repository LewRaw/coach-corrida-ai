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
    /* Estilização Geral e Tipografia */
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
        margin: 1.2rem 0;
        border-left: 6px solid #10B981;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
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
        line-height: 1.65;
        color: #E2E8F0 !important;
    }
    .coach-badge {
        display: inline-block;
        background-color: rgba(16, 185, 129, 0.2);
        color: #34D399;
        padding: 0.3rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.85rem;
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
   - Diagnóstico do Treino: Análise objetiva da execução em relação ao volume e ritmo.
   - Intensidade Cardíaca: Avaliação da resposta fisiológica e eficiência cardiovascular.
   - Próximo Passo: Orientação prática e prescritiva para a sessão seguinte (ex: descanso, rodagem leve Z1/Z2, ou hidratação/mobilidade).
Responda ESTRITAMENTE em conformidade com o esquema JSON solicitado.
"""

# ==============================================================================
# FUNÇÕES UTILITÁRIAS E CONVERSÃO NUMÉRICA RESILIENTE
# ==============================================================================
def parse_float_br(val: Any) -> float:
    """Converte strings com vírgula ou ponto para float, prevenindo erros de formato local."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s:
        return 0.0
    if "." in s and "," in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def get_secret_val(key: str, default: Any = None) -> Any:
    """Busca chave primeiro em st.secrets, depois em os.environ."""
    if key in st.secrets:
        return st.secrets[key]
    return os.environ.get(key, default)


# ==============================================================================
# SERVIÇOS E CLIENTES COM CACHE (@st.cache_resource)
# ==============================================================================
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
    """Abre a planilha e garante a existência da aba 'Treinos' com cabeçalhos estruturados."""
    try:
        sh = gc.open_by_url(sheet_url)
        try:
            ws = sh.worksheet("Treinos")
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title="Treinos", rows=500, cols=12)
            ws.append_row(SHEET_COLUMNS)
            return ws
        
        # Garante cabeçalho na linha 1 caso não exista
        all_values = ws.get_all_values()
        if not all_values or len(all_values) == 0:
            ws.append_row(SHEET_COLUMNS)
        else:
            primeira_linha = all_values[0]
            if not primeira_linha or not any("Data" in str(c) for c in primeira_linha):
                ws.insert_row(SHEET_COLUMNS, 1)

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
    """Carrega as atividades do Google Sheets de forma robusta e independente de locale."""
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

        vals = ws.get_all_values()
        if not vals or len(vals) <= 1:
            return pd.DataFrame(columns=SHEET_COLUMNS), None

        headers = vals[0]
        rows = [r for r in vals[1:] if any(str(c).strip() for c in r)]

        if not rows:
            return pd.DataFrame(columns=headers), None

        # Alinha número de colunas
        num_cols = len(headers)
        clean_rows = []
        for r in rows:
            if len(r) < num_cols:
                r = r + [""] * (num_cols - len(r))
            elif len(r) > num_cols:
                r = r[:num_cols]
            clean_rows.append(r)

        df = pd.DataFrame(clean_rows, columns=headers)

        # Conversão numérica resiliente
        for c in df.columns:
            if "Dist" in c:
                df[c] = df[c].apply(parse_float_br)
            elif "Tempo" in c:
                df[c] = df[c].apply(parse_float_br)
            elif "FC" in c:
                df[c] = df[c].apply(parse_float_br).astype(int)
            elif "RPE" in c:
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

        # Ordenação cronológica por data se disponível
        data_col = next((c for c in df.columns if "Data" in c), None)
        if data_col:
            try:
                df["_data_dt"] = pd.to_datetime(df[data_col], format="%d/%m/%Y", errors="coerce")
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

        btn_analisar = st.button(
            "🚀 Analisar Treino com Coach AI",
            type="primary",
            use_container_width=True,
        )

    # Feedback de Processamento Progressivo e Ação
    if btn_analisar:
        if not uploaded_file:
            st.warning("⚠️ Por favor, selecione e faça o upload de um print de corrida antes de iniciar a análise.")
        else:
            client = get_gemini_client()
            if not client:
                st.error("🔑 Chave de API do Gemini não configurada! Verifique `GEMINI_API_KEY` em `.streamlit/secrets.toml`.")
            else:
                # Controle visual de processamento em etapas claras
                with st.status("🏃 Processando treino com o Coach AI...", expanded=True) as status_box:
                    try:
                        status_box.write("📤 **Etapa 1/3:** Preparando imagem e enviando dados para o Gemini 2.5 Flash...")
                        image_bytes = uploaded_file.getvalue()
                        mime_type = uploaded_file.type or "image/jpeg"
                        
                        resultado = analyze_workout_image(
                            image_bytes=image_bytes,
                            mime_type=mime_type,
                            rpe=rpe,
                            user_notes=user_notes,
                            gemini_client=client,
                        )
                        
                        status_box.write("🧠 **Etapa 2/3:** Métricas extraídas e diagnóstico técnico formulado pelo treinador!")
                        
                        status_box.write("💾 **Etapa 3/3:** Sincronizando dados e parecer com o Google Sheets...")
                        salvo, msg_sheets = append_workout_to_sheets(resultado, rpe, user_notes)
                        
                        if salvo:
                            status_box.update(
                                label="✅ Análise concluída e registrada no Google Sheets!",
                                state="complete",
                                expanded=False,
                            )
                        else:
                            status_box.update(
                                label=f"⚠️ Treino analisado, mas atenção na planilha: {msg_sheets}",
                                state="error",
                                expanded=True,
                            )

                        # Armazena na sessão para persistência visual
                        st.session_state["ultimo_treino"] = resultado
                        st.session_state["sheets_salvo"] = salvo
                        st.session_state["sheets_msg"] = msg_sheets

                    except Exception as e:
                        status_box.update(label="❌ Erro durante o processamento da atividade", state="error", expanded=True)
                        st.error(f"Detalhes do erro: {str(e)}")

    # Exibição dos Resultados Análises (se disponível na sessão ou recém-analisado)
    if "ultimo_treino" in st.session_state:
        res: TreinoExtracao = st.session_state["ultimo_treino"]

        st.markdown("---")
        st.markdown("### 📈 Métricas Extraídas da Sessão")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("📏 Distância", f"{res.distancia_km:.2f} km")
        with m_col2:
            st.metric("⏱️ Pace Médio", f"{res.pace_medio} /km")
        with m_col3:
            fc_display = f"{res.fc_media} bpm" if res.fc_media > 0 else "Não detectada"
            st.metric("❤️ FC Média", fc_display)
        with m_col4:
            minutos = int(res.tempo_min)
            segundos = int(round((res.tempo_min - minutos) * 60))
            st.metric("⏳ Duração", f"{minutos}m {segundos:02d}s")

        # Card de Destaque com o Parecer Técnico do Treinador
        st.markdown(
            f"""
            <div class="coach-card">
                <span class="coach-badge">🎯 {res.zona_predominante} • Sessão de {res.data}</span>
                <h3>📋 Parecer Técnico de Consultoria</h3>
                <p>{res.parecer_treinador.replace(chr(10), '<br>')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.get("sheets_salvo"):
            st.success("💾 Atividade registrada com sucesso na aba 'Treinos' da sua planilha!")

# ------------------------------------------------------------------------------
# ABA 2: HISTÓRICO E GRÁFICOS
# ------------------------------------------------------------------------------
with tab_historico:
    st.markdown("### 📊 Histórico de Atividades & Evolução Fisiológica")
    
    col_btn_refresh, _ = st.columns([1.5, 4])
    with col_btn_refresh:
        btn_refresh = st.button("🔄 Atualizar / Recarregar Planilha", use_container_width=True)

    df_treinos, erro_carregamento = load_workouts_from_sheets()

    if erro_carregamento:
        st.info(f"ℹ️ {erro_carregamento}")
        st.markdown(
            """
            > **Dica para ativação completa:**
            > 1. Verifique se a URL da planilha e o bloco `[gcp_service_account]` estão preenchidos no `.streamlit/secrets.toml`.
            > 2. Certifique-se de que a planilha foi compartilhada como **Editor** com o `client_email` da Service Account.
            """
        )
    elif df_treinos is None or df_treinos.empty:
        st.warning("Nenhum treino registrado ainda na planilha. Registre sua primeira atividade na aba 'Novo Treino'!")
    else:
        # Métricas Globais Consolidadas
        col_dist = next((c for c in df_treinos.columns if "Dist" in c), "Distância (km)")
        col_fc = next((c for c in df_treinos.columns if "FC" in c), "FC Média (bpm)")
        
        total_km = df_treinos[col_dist].sum()
        total_treinos = len(df_treinos)
        
        # Média de FC ignorando zeros
        fc_validos = df_treinos[df_treinos[col_fc] > 0][col_fc]
        fc_global = int(fc_validos.mean()) if not fc_validos.empty else 0
        km_por_treino = (total_km / total_treinos) if total_treinos > 0 else 0

        tot_col1, tot_col2, tot_col3, tot_col4 = st.columns(4)
        with tot_col1:
            st.metric("🏃 Volume Total Acumulado", f"{total_km:.2f} km")
        with tot_col2:
            st.metric("🎯 Total de Sessões", f"{total_treinos} treinos")
        with tot_col3:
            st.metric("❤️ FC Média Geral", f"{fc_global} bpm" if fc_global > 0 else "--")
        with tot_col4:
            st.metric("📊 Média por Sessão", f"{km_por_treino:.2f} km")

        st.markdown("---")

        # Gráficos Analíticos
        tab_g1, tab_g2 = st.columns(2)

        data_col = next((c for c in df_treinos.columns if "Data" in c), "Data")

        with tab_g1:
            st.markdown("#### 🏃 Volume de Rodagem por Treino")
            fig_volume = px.bar(
                df_treinos,
                x=data_col,
                y=col_dist,
                text_auto=".2f",
                color=col_dist,
                color_continuous_scale="Viridis",
                labels={col_dist: "Distância (km)", data_col: "Data"},
                title="Volume por Sessão (km)",
            )
            fig_volume.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                coloraxis_showscale=False,
                xaxis_tickangle=-45,
            )
            st.plotly_chart(fig_volume, use_container_width=True)

        with tab_g2:
            st.markdown("#### ❤️ Monitoramento Cardiovascular")
            df_fc = df_treinos[df_treinos[col_fc] > 0]
            if not df_fc.empty:
                fig_fc = px.line(
                    df_fc,
                    x=data_col,
                    y=col_fc,
                    markers=True,
                    labels={col_fc: "FC Média (bpm)", data_col: "Data"},
                    title="Evolução da FC Média",
                )
                fig_fc.update_traces(
                    line_color="#EF4444",
                    line_width=3,
                    marker=dict(size=8, color="#B91C1C"),
                )
                fig_fc.update_layout(
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_tickangle=-45,
                )
                st.plotly_chart(fig_fc, use_container_width=True)
            else:
                st.info("Nenhuma frequência cardíaca registrada ainda para traçar a evolução temporal.")

        # Tabela Detalhada com visualizador interativo
        st.markdown("---")
        st.markdown("#### 📋 Tabela Geral de Atividades")
        cols_to_show = [c for c in SHEET_COLUMNS if c in df_treinos.columns]
        st.dataframe(
            df_treinos[cols_to_show],
            use_container_width=True,
            hide_index=True,
        )
