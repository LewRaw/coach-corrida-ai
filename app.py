"""
==============================================================================
Coach de Corrida AI - Running Coach & Training Analytics
Streamlit + Google GenAI (gemini-2.5-flash) + Google Sheets (gspread)
==============================================================================
"""

import io
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any, List

import gspread
from gspread.exceptions import APIError
import time
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

    /* Card do Treino Atual / Próxima Sessão */
    .next-workout-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%);
        color: #F8FAFC !important;
        border-radius: 14px;
        padding: 1.6rem;
        margin: 1rem 0 1.5rem 0;
        border-left: 6px solid #6366F1;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.25);
    }
    .next-workout-card h3 {
        color: #A5B4FC !important;
        margin-top: 0 !important;
        font-size: 1.4rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .next-workout-card p {
        font-size: 1.02rem;
        line-height: 1.6;
        color: #E2E8F0 !important;
    }

    /* Box de Plano de Treino */
    .plan-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    @media (prefers-color-scheme: dark) {
        .plan-card {
            background: #1E293B;
            border-color: #334155;
            color: #F8FAFC;
        }
    }

    /* Ajustes para Métricas e Responsividade Mobile */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #64748B;
    }

    /* Otimizações Específicas para Smartphones / Telas Pequenas */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.65rem !important;
        }
        .main-subtitle {
            font-size: 0.92rem !important;
            margin-bottom: 0.9rem !important;
        }
        .coach-card, .next-workout-card, .plan-card {
            padding: 1.1rem !important;
            border-radius: 10px !important;
            margin: 0.8rem 0 !important;
        }
        .next-workout-card h3 {
            font-size: 1.25rem !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.35rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.78rem !important;
        }
        /* Botões com altura ideal de toque (min 48px) */
        .stButton > button {
            min-height: 48px !important;
            font-size: 1rem !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
        }
        /* Abas com scroll horizontal suave sem quebrar layout */
        div[data-baseweb="tab-list"] {
            gap: 4px !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }
        div[data-baseweb="tab"] {
            padding-left: 10px !important;
            padding-right: 10px !important;
            font-size: 0.88rem !important;
            white-space: nowrap !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Colunas da aba de treinos executados
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

# Colunas da aba de cronograma / treinos prescritos
CRONOGRAMA_COLUMNS = [
    "ID",
    "Dia da Semana",
    "Data Prevista",
    "Tipo de Treino",
    "Distância (km)",
    "Duração (min)",
    "Pace Alvo",
    "RPE Alvo",
    "Estrutura do Treino",
    "Status",
    "Data Conclusão",
    "Criado Em",
]

# ==============================================================================
# MODELOS PYDANTIC PARA STRUCTURED OUTPUT
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

class TreinoDiarioPrescrito(BaseModel):
    dia_semana: str = Field(description="Dia da semana (ex: Segunda-feira, Terça-feira, Quarta-feira, Quinta-feira, Sexta-feira, Sábado, Domingo)")
    data_prevista: str = Field(description="Data futura obrigatória no formato DD/MM/AAAA para a sessão no ano de 2026")
    tipo_treino: str = Field(description="Ex: Rodagem Z2, Tiros de VO2 (Intervalado), Tempo Run (Ritmo), Descanso Ativo, Longão Progressivo")
    distancia_km: float = Field(description="Distância total prevista em km (ex: 8.5; informe 0.0 caso seja dia de descanso)")
    duracao_min: float = Field(description="Duração estimada em minutos (ex: 45.0; 0.0 caso descanso)")
    pace_alvo: str = Field(description="Faixa de pace alvo prescrita (ex: '05:15 - 05:30 /km' ou 'Descanso')")
    rpe_alvo: int = Field(description="Percepção de esforço planejada na escala Borg de 1 a 10")
    estrutura_treino: str = Field(description="Aquecimento detalhado + Treino Principal com orientações + Desaquecimento")

class PlanoSemanalPrescrito(BaseModel):
    titulo_ciclo: str = Field(description="Título do ciclo (ex: Semana 1 - Construção de Base e Adaptação Neuromuscular)")
    diagnostico_metodologia: str = Field(description="Diagnóstico da condição atual do atleta baseada no histórico da planilha e metodologia adotada")
    paces_referencia: str = Field(description="Resumo dos paces de referência: Z1 Regenerativo, Z2 Rodagem, Z3 Tempo Run, Z4/Z5 Limiar e Tiros")
    dias: List[TreinoDiarioPrescrito] = Field(description="Lista com os 7 dias completos da semana")
    orientacoes_gerais: str = Field(description="Orientações essenciais de recuperação, hidratação, sono e prevenção de lesões para esta semana")

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


# ==============================================================================
# GESTÃO RESILIENTE DE PLANILHAS (CACHE @st.cache_data + RETRY CONTRA ERRO 429)
# ==============================================================================
def run_with_retry(func, max_retries: int = 4, base_delay: float = 2.0):
    """Executa chamadas do gspread com backoff exponencial contra limites 429 da API."""
    for attempt in range(max_retries):
        try:
            return func()
        except APIError as e:
            if "429" in str(e) and attempt < max_retries - 1:
                sleep_time = base_delay * (2 ** attempt)
                time.sleep(sleep_time)
            else:
                raise
        except Exception:
            raise


@st.cache_resource(ttl=3600)
def get_cached_worksheet(sheet_url: str, title: str) -> Optional[gspread.Worksheet]:
    """Mantém em cache os objetos de Worksheet para evitar chamadas de abertura repetidas."""
    gc = get_gspread_client()
    if not gc:
        return None
    try:
        sh = run_with_retry(lambda: gc.open_by_url(sheet_url))
        try:
            return run_with_retry(lambda: sh.worksheet(title))
        except gspread.WorksheetNotFound:
            cols = SHEET_COLUMNS if title == "Treinos" else CRONOGRAMA_COLUMNS
            ws = run_with_retry(lambda: sh.add_worksheet(title=title, rows=500, cols=len(cols) + 3))
            run_with_retry(lambda: ws.append_row(cols))
            return ws
    except Exception as e:
        st.error(f"Erro ao obter aba '{title}': {e}")
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

    try:
        ws = get_cached_worksheet(sheet_url, "Treinos")
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
        run_with_retry(lambda: ws.append_row(nova_linha, value_input_option="USER_ENTERED"))
        st.cache_data.clear()
        return True, "Treino registrado com sucesso no Google Sheets!"
    except Exception as e:
        return False, f"Erro ao gravar no Google Sheets: {str(e)}"


@st.cache_data(ttl=60, show_spinner=False)
def _load_workouts_cached(sheet_url: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega as atividades da aba 'Treinos' mantendo cache em memória por 60 segundos."""
    try:
        ws = get_cached_worksheet(sheet_url, "Treinos")
        if not ws:
            return None, "Não foi possível conectar com a aba 'Treinos'."

        vals = run_with_retry(lambda: ws.get_all_values())
        if not vals or len(vals) <= 1:
            return pd.DataFrame(columns=SHEET_COLUMNS), None

        headers = vals[0]
        rows = [r for r in vals[1:] if any(str(c).strip() for c in r)]

        if not rows:
            return pd.DataFrame(columns=headers), None

        num_cols = len(headers)
        clean_rows = []
        for r in rows:
            if len(r) < num_cols:
                r = r + [""] * (num_cols - len(r))
            elif len(r) > num_cols:
                r = r[:num_cols]
            clean_rows.append(r)

        df = pd.DataFrame(clean_rows, columns=headers)

        for c in df.columns:
            if "Dist" in c:
                df[c] = df[c].apply(parse_float_br)
            elif "Tempo" in c:
                df[c] = df[c].apply(parse_float_br)
            elif "FC" in c:
                df[c] = df[c].apply(parse_float_br).astype(int)
            elif "RPE" in c:
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

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


def load_workouts_from_sheets() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega as atividades concluídas da aba 'Treinos' aproveitando o cache."""
    sheet_url = get_secret_val("sheet_url")
    if not sheet_url:
        return None, "Configure o parâmetro 'sheet_url' em .streamlit/secrets.toml para carregar o histórico."
    if "gcp_service_account" not in st.secrets:
        return None, "Configure 'gcp_service_account' em .streamlit/secrets.toml para sincronizar com o Google Sheets."
    return _load_workouts_cached(sheet_url)


def save_weekly_plan_to_sheets(plano: PlanoSemanalPrescrito) -> Tuple[bool, str]:
    """Salva os 7 dias gerados da planilha na aba 'Cronograma' com status 'Pendente'."""
    sheet_url = get_secret_val("sheet_url")
    if not sheet_url:
        return False, "Credenciais do Google Sheets não configuradas."

    try:
        ws = get_cached_worksheet(sheet_url, "Cronograma")
        if not ws:
            return False, "Não foi possível abrir a aba 'Cronograma'."

        timestamp_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        novas_linhas = []
        for d in plano.dias:
            treino_id = f"TR-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            linha = [
                treino_id,
                d.dia_semana,
                d.data_prevista,
                d.tipo_treino,
                d.distancia_km,
                d.duracao_min,
                d.pace_alvo,
                d.rpe_alvo,
                d.estrutura_treino,
                "Pendente",
                "",
                timestamp_criacao,
            ]
            novas_linhas.append(linha)

        run_with_retry(lambda: ws.append_rows(novas_linhas, value_input_option="USER_ENTERED"))
        st.cache_data.clear()
        return True, f"Plano com {len(novas_linhas)} sessões sincronizado com o Cronograma no Google Sheets!"
    except Exception as e:
        return False, f"Erro ao gravar cronograma: {str(e)}"


@st.cache_data(ttl=60, show_spinner=False)
def _load_cronograma_cached(sheet_url: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega as sessões prescritas da aba 'Cronograma' mantendo cache de 60s."""
    try:
        ws = get_cached_worksheet(sheet_url, "Cronograma")
        if not ws:
            return None, "Não foi possível conectar com a aba 'Cronograma'."

        vals = run_with_retry(lambda: ws.get_all_values())
        if not vals or len(vals) <= 1:
            return pd.DataFrame(columns=CRONOGRAMA_COLUMNS), None

        headers = vals[0]
        rows = [r for r in vals[1:] if any(str(c).strip() for c in r)]

        if not rows:
            return pd.DataFrame(columns=headers), None

        num_cols = len(headers)
        clean_rows = []
        for r in rows:
            if len(r) < num_cols:
                r = r + [""] * (num_cols - len(r))
            elif len(r) > num_cols:
                r = r[:num_cols]
            clean_rows.append(r)

        df = pd.DataFrame(clean_rows, columns=headers)

        if "Distância (km)" in df.columns:
            df["Distância (km)"] = df["Distância (km)"].apply(parse_float_br)
        if "Duração (min)" in df.columns:
            df["Duração (min)"] = df["Duração (min)"].apply(parse_float_br)
        if "RPE Alvo" in df.columns:
            df["RPE Alvo"] = pd.to_numeric(df["RPE Alvo"], errors="coerce").fillna(0).astype(int)

        return df, None
    except Exception as e:
        return None, f"Erro ao carregar Cronograma: {str(e)}"


def load_cronograma_from_sheets() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega as sessões prescritas da aba 'Cronograma' aproveitando o cache de 60s."""
    sheet_url = get_secret_val("sheet_url")
    if not sheet_url:
        return None, "Google Sheets não configurado."
    if "gcp_service_account" not in st.secrets:
        return None, "Credenciais do Google Sheets não configuradas."
    return _load_cronograma_cached(sheet_url)


def mark_workout_as_completed(workout_id: str) -> Tuple[bool, str]:
    """Localiza o treino pelo ID na aba 'Cronograma' e atualiza para 'Concluído ✅'."""
    sheet_url = get_secret_val("sheet_url")
    if not sheet_url:
        return False, "Google Sheets não configurado."

    try:
        ws = get_cached_worksheet(sheet_url, "Cronograma")
        if not ws:
            return False, "Não foi possível abrir o Cronograma."

        cell = run_with_retry(lambda: ws.find(workout_id))
        if not cell:
            return False, f"Treino com ID {workout_id} não encontrado na planilha."

        headers = run_with_retry(lambda: ws.row_values(1))
        col_status = headers.index("Status") + 1 if "Status" in headers else 10
        col_conclusao = headers.index("Data Conclusão") + 1 if "Data Conclusão" in headers else 11

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        run_with_retry(lambda: ws.update_cell(cell.row, col_status, "Concluído ✅"))
        run_with_retry(lambda: ws.update_cell(cell.row, col_conclusao, now_str))

        st.cache_data.clear()
        return True, "Treino marcado como Concluído na planilha com sucesso!"
    except Exception as e:
        return False, f"Erro ao marcar treino: {str(e)}"


def clear_cronograma_in_sheets() -> Tuple[bool, str]:
    """Limpa todas as sessões da aba 'Cronograma' mantendo a linha de cabeçalho."""
    sheet_url = get_secret_val("sheet_url")
    if not sheet_url:
        return False, "Google Sheets não configurado."

    try:
        ws = get_cached_worksheet(sheet_url, "Cronograma")
        if not ws:
            return False, "Não foi possível abrir a aba 'Cronograma'."

        run_with_retry(lambda: ws.clear())
        run_with_retry(lambda: ws.append_row(CRONOGRAMA_COLUMNS))
        st.cache_data.clear()
        return True, "Cronograma limpo com sucesso! Todas as sessões antigas foram removidas."
    except Exception as e:
        return False, f"Erro ao limpar cronograma: {str(e)}"


def format_athlete_history_for_prompt(df: Optional[pd.DataFrame]) -> str:
    """Gera um prontuário textual estruturado dos treinos do atleta para alimentar os prompts."""
    if df is None or df.empty:
        return "Nenhum treino registrado ainda na planilha. O atleta está iniciando ou ainda não sincronizou atividades."

    col_dist = next((c for c in df.columns if "Dist" in c), "Distância (km)")
    col_tempo = next((c for c in df.columns if "Tempo" in c), "Tempo (min)")
    col_pace = next((c for c in df.columns if "Pace" in c), "Pace Médio")
    col_fc = next((c for c in df.columns if "FC" in c), "FC Média (bpm)")
    col_zona = next((c for c in df.columns if "Zona" in c), "Zona Predominante")
    col_rpe = next((c for c in df.columns if "RPE" in c), "RPE (1-10)")
    col_notas = next((c for c in df.columns if "Notas" in c), "Notas do Atleta")
    col_parecer = next((c for c in df.columns if "Parecer" in c), "Parecer do Treinador")
    col_data = next((c for c in df.columns if "Data" in c), "Data")

    total_km = df[col_dist].sum()
    total_treinos = len(df)
    fc_series = df[df[col_fc] > 0][col_fc]
    fc_media = int(fc_series.mean()) if not fc_series.empty else "N/D"

    linhas = [
        "=== PRONTUARIO HISTORICO REAL DO ATLETA (DO GOOGLE SHEETS) ===",
        f"- Total de sessoes registradas: {total_treinos}",
        f"- Volume total acumulado: {total_km:.2f} km",
        f"- Frequencia Cardiaca media global: {fc_media} bpm",
        "",
        "=== ULTIMOS TREINOS REGISTRADOS (do mais recente para o mais antigo) ===",
    ]

    for idx, row in df.iloc[::-1].head(15).iterrows():
        linhas.append(
            f"Data: {row.get(col_data, 'N/D')} | Distancia: {row.get(col_dist, 0):.2f} km | "
            f"Pace: {row.get(col_pace, 'N/D')} /km | FC Media: {row.get(col_fc, 0)} bpm | "
            f"Zona: {row.get(col_zona, 'N/D')} | RPE: {row.get(col_rpe, 0)}/10\n"
            f"   - Notas do Atleta: {row.get(col_notas, 'Nenhuma')}\n"
            f"   - Parecer do Treinador: {row.get(col_parecer, 'Nenhum')}\n"
        )

    return "\n".join(linhas)


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
        '<div class="main-subtitle">Consultoria de corrida, análise de prints, cronograma inteligente e check-in com Gemini 2.5 & Google Sheets</div>',
        unsafe_allow_html=True,
    )

with col_status:
    api_ready = bool(get_secret_val("GEMINI_API_KEY"))
    sheet_ready = bool(get_secret_val("sheet_url")) and ("gcp_service_account" in st.secrets)
    
    if api_ready and sheet_ready:
        st.caption("🟢 **Sistema Conectado**")
    else:
        st.caption("🟡 **Modo Parcial / Demo**")

# Expander de Apoio e Guia para o Atleta / Celular
with st.expander("📱 Dica para o Celular & Guia Rápido do Atleta (Clique para abrir)"):
    st.markdown(
        """
        ##### 📲 Como transformar em app no seu celular:
        - **No iPhone (Safari):** Toque no ícone de compartilhar (quadrado com seta) e selecione **"Adicionar à Tela de Início"**.
        - **No Android (Chrome):** Toque nos 3 pontinhos e selecione **"Adicionar à tela inicial"** ou **"Instalar aplicativo"**.

        ---
        ##### 🏃 Guia em 4 Passos:
        1. **📅 Ver o Treino do Dia:** Na aba *Treino Atual & Cronograma*, veja o que está agendado e como executar.
        2. **✅ Fazer Check-in:** Terminou a corrida? Clique no botão *Marcar como Feito* para atualizar sua planilha.
        3. **📤 Subir o Print (Opcional):** Na aba *Novo Treino*, envie o print do Strava ou Garmin para receber o parecer técnico da IA.
        4. **💬 Conversar com o Coach:** Na aba *Conversar com o Coach*, tire dúvidas sobre ritmo, dores, descanso e nutrição.

        ---
        ##### ⚠️ Dicas e Limites:
        - **Prints nítidos:** O print deve mostrar pelo menos distância, tempo total e pace médio.
        - **Atualização rápida:** O app sincroniza a cada 60s. Para forçar a busca imediata, use o botão **🔄 Atualizar**.
        - **Saúde primeiro:** A consultoria do Coach AI auxilia nos treinos amadores e maratonas; em caso de dor aguda persistente, procure sempre um fisioterapeuta ou médico.
        """
    )

# ==============================================================================
# ABAS PRINCIPAIS (5 ABAS COMPLETAS)
# ==============================================================================
tab_novo_treino, tab_cronograma, tab_historico, tab_chat, tab_planilha = st.tabs([
    "🏃 Novo Treino",
    "📅 Treino Atual & Cronograma",
    "📊 Histórico e Gráficos",
    "💬 Conversar com o Coach",
    "📋 Montador de Treinos",
])

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

                        st.session_state["ultimo_treino"] = resultado
                        st.session_state["sheets_salvo"] = salvo
                        st.session_state["sheets_msg"] = msg_sheets

                    except Exception as e:
                        status_box.update(label="❌ Erro durante o processamento da atividade", state="error", expanded=True)
                        st.error(f"Detalhes do erro: {str(e)}")

    # Exibição dos Resultados Análises
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
# ABA 2: TREINO ATUAL & CRONOGRAMA (NOVA FUNCIONALIDADE)
# ------------------------------------------------------------------------------
with tab_cronograma:
    st.markdown("### 📅 Cronograma de Treinos & Sessão do Dia")
    st.write("Acompanhe o que está agendado na sua planilha, marque os treinos concluídos com 1 clique e monitore sua taxa de adesão.")

    col_btn_refresh_crono, col_btn_clear_crono, _ = st.columns([1.5, 1.5, 3])
    with col_btn_refresh_crono:
        btn_refresh_crono = st.button("🔄 Atualizar Cronograma", use_container_width=True)
        if btn_refresh_crono:
            st.cache_data.clear()
            st.rerun()

    with col_btn_clear_crono:
        with st.popover("🗑️ Limpar Cronograma"):
            st.write("Deseja apagar todos os treinos agendados na aba 'Cronograma'?")
            if st.button("⚠️ Confirmar e Limpar", type="primary", use_container_width=True):
                with st.spinner("Limpando sessões da planilha..."):
                    ok_cl, msg_cl = clear_cronograma_in_sheets()
                    if ok_cl:
                        st.success(msg_cl)
                        st.rerun()
                    else:
                        st.error(msg_cl)

    df_crono, erro_crono = load_cronograma_from_sheets()

    if erro_crono:
        st.info(f"ℹ️ {erro_crono}")
    elif df_crono is None or df_crono.empty:
        st.info(
            "📋 Você ainda não possui treinos agendados no Cronograma. "
            "Acesse a aba **'📋 Montador de Treinos'** para prescrever sua planilha semanal e sincronizá-la automaticamente com esta aba!"
        )
    else:
        # Métricas de Progresso da Planilha Prescrita
        total_sessoes = len(df_crono)
        concluidos = len(df_crono[df_crono["Status"].str.contains("Concluído", na=False)])
        pendentes = total_sessoes - concluidos
        pct_conclusao = (concluidos / total_sessoes) if total_sessoes > 0 else 0.0

        km_planejados = df_crono["Distância (km)"].sum()
        km_feitos = df_crono[df_crono["Status"].str.contains("Concluído", na=False)]["Distância (km)"].sum()

        st.markdown(f"#### 🎯 Meta do Ciclo: {concluidos}/{total_sessoes} Sessões Concluídas ({pct_conclusao * 100:.0f}%)")
        st.progress(pct_conclusao)

        c_col1, c_col2, c_col3, c_col4 = st.columns(4)
        with c_col1:
            st.metric("⏳ Pendentes", f"{pendentes} treinos")
        with c_col2:
            st.metric("✅ Concluídos", f"{concluidos} treinos")
        with c_col3:
            st.metric("🏃 Km Concluídos", f"{km_feitos:.1f} / {km_planejados:.1f} km")
        with c_col4:
            st.metric("📊 Taxa de Adesão", f"{pct_conclusao * 100:.1f}%")

        st.markdown("---")

        # Localiza o próximo treino pendente (Hero Card)
        df_pendentes = df_crono[df_crono["Status"] == "Pendente"]
        if not df_pendentes.empty:
            proximo = df_pendentes.iloc[0]
            proximo_id = proximo["ID"]
            dist_str = f"{proximo['Distância (km)']:.1f} km" if proximo["Distância (km)"] > 0 else "Descanso / Mobilidade"
            dur_str = f"{proximo['Duração (min)']:.0f} min" if proximo["Duração (min)"] > 0 else "--"

            st.markdown(
                f"""
                <div class="next-workout-card">
                    <span class="coach-badge" style="background: rgba(99, 102, 241, 0.3); color: #C7D2FE;">
                        🔥 PRÓXIMO TREINO • {proximo['Dia da Semana']} ({proximo['Data Prevista']})
                    </span>
                    <h3>🏃 {proximo['Tipo de Treino']}</h3>
                    <p>
                        <strong>Distância Prevista:</strong> {dist_str} &nbsp;|&nbsp; 
                        <strong>Duração Estimada:</strong> {dur_str} &nbsp;|&nbsp; 
                        <strong>Pace Alvo:</strong> {proximo['Pace Alvo']} &nbsp;|&nbsp; 
                        <strong>RPE Alvo:</strong> {proximo['RPE Alvo']}/10
                    </p>
                    <p><strong>Estrutura da Sessão:</strong><br>{proximo['Estrutura do Treino'].replace(chr(10), '<br>')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_checkin, _ = st.columns([1.5, 3])
            with col_checkin:
                if st.button("✅ Marcar este Treino como Feito / Concluído", type="primary", use_container_width=True):
                    with st.spinner("Atualizando status na planilha Google Sheets..."):
                        sucesso_ck, msg_ck = mark_workout_as_completed(proximo_id)
                        if sucesso_ck:
                            st.balloons()
                            st.success(f"🎉 Parabéns atleta! {msg_ck}")
                            st.rerun()
                        else:
                            st.error(msg_ck)
        else:
            st.success("🎉 Parabéns! Você concluiu todos os treinos prescritos para este ciclo. Que tal gerar uma nova planilha no 'Montador de Treinos'?")

        # Tabela Geral do Cronograma
        st.markdown("---")
        st.markdown("#### 📋 Visão Completa do Cronograma")
        
        filtro_status = st.radio(
            "Filtrar por Status:",
            ["Todos", "Apenas Pendentes ⏳", "Apenas Concluídos ✅"],
            horizontal=True,
        )

        df_exibir_crono = df_crono.copy()
        if filtro_status == "Apenas Pendentes ⏳":
            df_exibir_crono = df_exibir_crono[df_exibir_crono["Status"] == "Pendente"]
        elif filtro_status == "Apenas Concluídos ✅":
            df_exibir_crono = df_exibir_crono[df_exibir_crono["Status"].str.contains("Concluído", na=False)]

        colunas_exibir = [
            c for c in [
                "Dia da Semana", "Data Prevista", "Tipo de Treino", "Distância (km)",
                "Duração (min)", "Pace Alvo", "RPE Alvo", "Estrutura do Treino", "Status", "Data Conclusão"
            ] if c in df_exibir_crono.columns
        ]
        st.dataframe(
            df_exibir_crono[colunas_exibir],
            use_container_width=True,
            hide_index=True,
        )

# ------------------------------------------------------------------------------
# ABA 3: HISTÓRICO E GRÁFICOS
# ------------------------------------------------------------------------------
with tab_historico:
    st.markdown("### 📊 Histórico de Atividades & Evolução Fisiológica")
    
    col_btn_refresh, _ = st.columns([1.5, 4])
    with col_btn_refresh:
        btn_refresh = st.button("🔄 Atualizar / Recarregar Planilha", use_container_width=True)
        if btn_refresh:
            st.cache_data.clear()
            st.rerun()

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
        col_dist = next((c for c in df_treinos.columns if "Dist" in c), "Distância (km)")
        col_fc = next((c for c in df_treinos.columns if "FC" in c), "FC Média (bpm)")
        
        total_km = df_treinos[col_dist].sum()
        total_treinos = len(df_treinos)
        
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
            st.plotly_chart(
                fig_volume,
                use_container_width=True,
                config={"displayModeBar": False, "scrollZoom": False, "responsive": True},
            )

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
                st.plotly_chart(
                    fig_fc,
                    use_container_width=True,
                    config={"displayModeBar": False, "scrollZoom": False, "responsive": True},
                )
            else:
                st.info("Nenhuma frequência cardíaca registrada ainda para traçar a evolução temporal.")

        st.markdown("---")
        st.markdown("#### 📋 Tabela Geral de Atividades")
        cols_to_show = [c for c in SHEET_COLUMNS if c in df_treinos.columns]
        st.dataframe(
            df_treinos[cols_to_show],
            use_container_width=True,
            hide_index=True,
        )

# ------------------------------------------------------------------------------
# ABA 4: CONVERSAR COM O COACH (CHAT INTELIGENTE COM ACESSO AO HISTÓRICO)
# ------------------------------------------------------------------------------
with tab_chat:
    st.markdown("### 💬 Consultoria Direta com o Treinador")
    st.write("Converse com o Coach sobre suas sensações, peça análises da sua evolução ou tire dúvidas sobre ritmo, nutrição e descanso. **O Treinador analisa o histórico de treinos da sua planilha em tempo real!**")

    df_contexto, _ = load_workouts_from_sheets()
    historico_texto = format_athlete_history_for_prompt(df_contexto)

    if "chat_messages" not in st.session_state:
        msg_inicial = (
            "Fala atleta! 🏃‍♂️ Sou seu treinador de corrida com inteligência artificial. "
            "Tenho acesso a todo o seu histórico registrado na planilha do Google Sheets. "
            "Pode me perguntar sobre sua evolução de pace, como foi seu último treino, "
            "se você está pronto para subir de distância ou o que fazer na sessão de amanhã. "
            "Como posso te ajudar hoje?"
        )
        st.session_state["chat_messages"] = [{"role": "assistant", "content": msg_inicial}]

    st.markdown("###### ⚡ Perguntas Frequentes:")
    chip_cols = st.columns(4)
    quick_query = None
    with chip_cols[0]:
        if st.button("📈 Analisar evolução de pace", use_container_width=True):
            quick_query = "Analise minha evolução de pace e consistência com base no meu histórico de treinos."
    with chip_cols[1]:
        if st.button("🎯 Estou pronto para Meia Maratona?", use_container_width=True):
            quick_query = "Com base no meu volume e treinos registrados, estou pronto para correr uma Meia Maratona (21k)?"
    with chip_cols[2]:
        if st.button("💤 O que treinar amanhã?", use_container_width=True):
            quick_query = "Considerando meu último treino registrado e o desgaste cardiovascular, qual treino devo fazer amanhã?"
    with chip_cols[3]:
        if st.button("❤️ Avaliar eficiência cardíaca", use_container_width=True):
            quick_query = "Avalie minha eficiência cardíaca relacionando meu ritmo (pace), frequência cardíaca média e RPE nos meus treinos."

    st.markdown("---")

    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"], avatar="🏃‍♂️" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    user_prompt = st.chat_input("Digite sua dúvida ou pedido para o Treinador...")
    texto_a_enviar = quick_query or user_prompt

    if texto_a_enviar:
        st.session_state["chat_messages"].append({"role": "user", "content": texto_a_enviar})
        with st.chat_message("user", avatar="👤"):
            st.markdown(texto_a_enviar)

        client = get_gemini_client()
        if not client:
            st.error("Chave de API do Gemini não configurada.")
        else:
            with st.chat_message("assistant", avatar="🏃‍♂️"):
                with st.spinner("O Treinador está consultando seu histórico e formulando a resposta..."):
                    try:
                        chat_system_instruction = f"""Você é o Treinador Chefe de Corrida de Rua do atleta.
Você possui vasta experiência com atletas de 5k, 10k, 21k e maratonistas, aplicando fisiologia do exercício (Jack Daniels VDOT, Lydiard, Pfitzinger).
Sua missão é fornecer respostas técnicas, assertivas, empáticas e altamente personalizadas.

CONTEXTO REAL DO ATLETA (HISTÓRICO ATUALIZADO DO GOOGLE SHEETS):
{historico_texto}

DIRETRIZES DA RESPOSTA:
1. Sempre cite e cruze dados reais dos treinos do atleta (datas, quilometragens, FC e paces reais registrados).
2. Se o atleta perguntar se está pronto para uma meta, seja honesto com base no volume e evolução observados.
3. Se perguntar sobre o próximo treino, recomende com base na recuperação e no princípio da supercompensação.
4. Mantenha tom motivador, profissional e esportivo.
"""
                        gemini_contents = []
                        for m in st.session_state["chat_messages"][-8:]:
                            role = "user" if m["role"] == "user" else "model"
                            gemini_contents.append(f"{role.upper()}: {m['content']}")

                        prompt_completo = (
                            f"{chat_system_instruction}\n\n"
                            f"DIÁLOGO RECENTE:\n" + "\n".join(gemini_contents) + "\n\n"
                            f"RESPONDA DIRETAMENTE AO ATLETA:"
                        )

                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt_completo,
                            config=types.GenerateContentConfig(
                                temperature=0.5,
                            ),
                        )

                        resposta_coach = response.text
                        st.markdown(resposta_coach)
                        st.session_state["chat_messages"].append({"role": "assistant", "content": resposta_coach})
                    except Exception as e:
                        st.error(f"Erro ao conversar com o treinador: {str(e)}")

# ------------------------------------------------------------------------------
# ABA 5: MONTADOR DE TREINOS (PERIODIZAÇÃO E ENVIO AO CRONOGRAMA)
# ------------------------------------------------------------------------------
with tab_planilha:
    st.markdown("### 📋 Montador Inteligente de Planilhas de Treino")
    st.write("Gere um ciclo semanal de treinamentos estruturado sob medida e envie para o seu Cronograma oficial com 1 clique.")

    col_p1, col_p2 = st.columns([1, 1], gap="large")

    with col_p1:
        objetivo_selecionado = st.selectbox(
            "🎯 Qual é o seu objetivo principal?",
            options=[
                "🏃 Estreia em Meia Maratona (21.1 km)",
                "🏅 Sub 50 minutos nos 10 km",
                "⚡ Recorde Pessoal nos 5 km",
                "🏆 Preparação Completa para Maratona (42.2 km)",
                "🫀 Construção Sólida de Base Aeróbica (Zona 2)",
                "⚖️ Condicionamento Geral & Emagrecimento Saudável",
            ],
        )

        dias_semana = st.slider(
            "📅 Quantos dias por semana você pode treinar corrida?",
            min_value=3,
            max_value=6,
            value=4,
            help="Recomendado: 3 a 4 dias para 5k/10k; 4 a 5 dias para Meia Maratona; 4 a 6 dias para Maratona.",
        )

        dia_longao = st.selectbox(
            "🏃 Qual o seu dia preferido para o Treino Longo (Longão)?",
            options=["Domingo", "Sábado", "Outro dia da semana"],
        )

    with col_p2:
        ciclo_horizonte = st.selectbox(
            "⏳ Período do Planejamento:",
            options=[
                "Microciclo Imediato (Semana 1 / Próximos 7 dias)",
                "Bloco de Base Aeróbica (4 Semanas)",
                "Ciclo de Polimento Pré-Prova (2 Semanas)",
            ],
        )

        obs_lesoes = st.text_area(
            "🩺 Observações Físicas, Dores Recentes ou Restrições:",
            placeholder="Ex: Leve desconforto na tíbia direita após treinos em asfalto; preferência por treinar musculação nas terças; sem lesões graves.",
            height=125,
        )

        btn_gerar_plano = st.button("🚀 Gerar Planilha de Treinos com Coach AI", type="primary", use_container_width=True)

    if btn_gerar_plano:
        client = get_gemini_client()
        if not client:
            st.error("Chave de API do Gemini não configurada.")
        else:
            with st.status("📋 Construindo sua periodização personalizada com o Coach AI...", expanded=True) as status_plan:
                try:
                    status_plan.write("🔍 **Etapa 1/3:** Lendo histórico de treinos e calculando média de volume e paces...")
                    df_historico_plano, _ = load_workouts_from_sheets()
                    historico_resumo = format_athlete_history_for_prompt(df_historico_plano)

                    status_plan.write("🧠 **Etapa 2/3:** Gemini 2.5 Flash aplicando fórmulas de periodização e cálculo de zonas...")
                    
                    # Cálculo explícito e determinístico das próximas 7 datas futuras (Ano 2026)
                    hoje = datetime.now()
                    dias_nomes = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
                    dia_hoje_nome = dias_nomes[hoje.weekday()]
                    datas_proximas = []
                    for i in range(1, 8):
                        dt = hoje + timedelta(days=i)
                        nome_d = dias_nomes[dt.weekday()]
                        datas_proximas.append(f"- Dia {i} ({nome_d}): {dt.strftime('%d/%m/%Y')}")
                    calendario_datas_str = "\n".join(datas_proximas)

                    prompt_plano = f"""Atue como um Treinador de Corrida de Rua e Maratonas de elite.
Elabore uma planilha de treinamento estruturada para as próximas 7 sessões para este atleta, respeitando a fisiologia do esporte (máximo de 10% de evolução semanal).

CONTEXTO TEMPORAL RIGOROSO:
- DATA ATUAL DE REFERÊNCIA: {dia_hoje_nome}, {hoje.strftime('%d/%m/%Y')} (ANO CORRENTE: {hoje.year}).
- CALENDÁRIO OBRIGATÓRIO PARA AS PRÓXIMAS 7 SESSÕES FUTURAS ({hoje.year}):
{calendario_datas_str}

ATENÇÃO CRÍTICA SOBRE AS DATAS:
O ano é {hoje.year}. As datas previstas para cada um dos 7 dias DEVEM SER OBRIGATORIAMENTE as datas futuras listadas no calendário acima (Ano {hoje.year}).
NUNCA utilize o ano de 2024 ou datas passadas do histórico do atleta! O histórico serve estritamente para dosar volume e ritmo, NUNCA as datas!

DADOS DO ATLETA E HISTÓRICO REAL NA PLANILHA:
{historico_resumo}

PARÂMETROS DEFINIDOS PELO ATLETA:
- Objetivo: {objetivo_selecionado}
- Frequência Semanal: {dias_semana} dias de treino de corrida (os outros {7 - dias_semana} dias devem ser 'Descanso' ou 'Descanso Ativo / Mobilidade')
- Dia do Longão: {dia_longao}
- Período: {ciclo_horizonte}
- Restrições / Dores: {obs_lesoes if obs_lesoes.strip() else 'Nenhuma restrição. Atleta 100% saudável.'}

Forneça os 7 dias completos (utilizando estritamente as 7 datas futuras informadas acima) em formato JSON de acordo com o esquema solicitado.
"""

                    resp_plano = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt_plano,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=PlanoSemanalPrescrito,
                            temperature=0.3,
                        ),
                    )

                    status_plan.write("✅ **Etapa 3/3:** Planilha de treino gerada e estruturada com sucesso!")
                    status_plan.update(label="✅ Planilha de treino construída com sucesso!", state="complete", expanded=False)

                    plano_objeto: PlanoSemanalPrescrito = resp_plano.parsed if hasattr(resp_plano, "parsed") and resp_plano.parsed else PlanoSemanalPrescrito(**json.loads(resp_plano.text))
                    st.session_state["plano_estruturado"] = plano_objeto

                except Exception as e:
                    status_plan.update(label="❌ Erro na geração da planilha", state="error", expanded=True)
                    st.error(f"Erro: {str(e)}")

    # Exibe plano estruturado gerado
    if "plano_estruturado" in st.session_state:
        plano: PlanoSemanalPrescrito = st.session_state["plano_estruturado"]
        st.markdown("---")
        st.markdown(f"### 🏆 {plano.titulo_ciclo}")
        
        st.markdown(
            f"""
            <div class="plan-card">
                <h4>🎯 Diagnóstico e Metodologia</h4>
                <p>{plano.diagnostico_metodologia}</p>
                <h4>⏱️ Paces de Referência</h4>
                <p>{plano.paces_referencia}</p>
                <h4>💡 Orientações Gerais do Treinador</h4>
                <p>{plano.orientacoes_gerais}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 🗓️ Cronograma dos 7 Dias da Semana:")
        for d in plano.dias:
            dist_label = f"📏 {d.distancia_km:.1f} km" if d.distancia_km > 0 else "💤 Descanso"
            dur_label = f"⏳ {d.duracao_min:.0f} min" if d.duracao_min > 0 else ""
            with st.expander(f"{d.dia_semana} ({d.data_prevista}) — {d.tipo_treino} ({dist_label})", expanded=True):
                st.write(f"**Pace Alvo:** {d.pace_alvo} | **RPE Alvo:** {d.rpe_alvo}/10 {dur_label}")
                st.write(f"**Estrutura:** {d.estrutura_treino}")

        substituir_existente = st.checkbox(
            "Substituir cronograma atual (limpar treinos antigos antes de salvar)",
            value=True,
            help="Se marcado, limpa as sessões antigas da aba 'Cronograma' e grava os novos 7 dias prescritos.",
        )

        col_save_crono, col_dl_crono = st.columns([1.5, 1])
        with col_save_crono:
            if st.button("💾 Sincronizar esta Planilha com o Cronograma do Google Sheets", type="primary", use_container_width=True):
                with st.spinner("Gravando as 7 sessões no Cronograma do Google Sheets..."):
                    if substituir_existente:
                        clear_cronograma_in_sheets()
                    sucesso_sync, msg_sync = save_weekly_plan_to_sheets(plano)
                    if sucesso_sync:
                        st.balloons()
                        st.success(f"✅ {msg_sync}")
                    else:
                        st.error(msg_sync)

        with col_dl_crono:
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
                label="📥 Baixar em Markdown (.md)",
                data=texto_md,
                file_name=f"planilha_treinos_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
