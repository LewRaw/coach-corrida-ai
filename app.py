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
from supabase import create_client, Client

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

    /* Barra Superior de Ações Rápidas */
    .quick-action-bar {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.06) 0%, rgba(99, 102, 241, 0.08) 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin-bottom: 1.25rem;
    }

    /* Banner PWA Mobile Friendly */
    .pwa-card {
        background: linear-gradient(135deg, #0F172A 0%, #0369A1 100%);
        border: 1px solid #38BDF8;
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.25);
        color: #F8FAFC !important;
    }
    .pwa-card h4 {
        color: #38BDF8 !important;
        font-weight: 700;
        margin-top: 0 !important;
        font-size: 1.15rem;
    }
    .pwa-card p {
        color: #E2E8F0 !important;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .pwa-os-box {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 10px;
        padding: 0.9rem;
        margin-top: 0.4rem;
    }

    /* Box O Porquê do App (Propósito) */
    .purpose-box {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%);
        border: 1px solid #818CF8;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.1rem;
        color: #F8FAFC !important;
    }
    .purpose-box h4 {
        color: #A5B4FC !important;
        margin-top: 0 !important;
        font-size: 1.18rem;
    }
    .purpose-box p, .purpose-box li {
        color: #E2E8F0 !important;
        font-size: 0.94rem;
        line-height: 1.6;
    }
    .purpose-box ul {
        margin-bottom: 0.4rem;
        padding-left: 1.2rem;
    }

    /* Chips de Esportes Ativos */
    .sport-pill {
        display: inline-block;
        background: rgba(99, 102, 241, 0.18);
        border: 1px solid rgba(99, 102, 241, 0.45);
        color: #818CF8;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
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
# OPÇÕES DE ESPORTES, NÍVEIS E METAS (SISTEMA MULTIESPORTE)
# ==============================================================================
ESPORTES_OPCOES = [
    "🏃 Corrida de Rua & Maratona",
    "🚴 Ciclismo / Bike",
    "🏊 Natação",
    "⚽ Futebol",
    "🏊🚴🏃 Especialista em Triatlo",
    "🏀 Basquete",
    "🏐 Vôlei",
    "🏋️ Musculação / Fortalecimento",
]

NIVEIS_EXPERIENCIA = [
    "Iniciante (Começando agora / Sedentário)",
    "Intermediário (Já pratico com regularidade)",
    "Avançado / Competitivo (Busca de performance & pódio)",
]

METAS_OPCOES = [
    "🏃 Estreia em Corrida (5 km ou 10 km)",
    "🏃 Meia Maratona (21.1 km)",
    "🏆 Maratona Completa (42.2 km)",
    "🏊🚴🏃 Triatlo (Sprint, Olímpico ou 70.3)",
    "🚴 Evolução no Ciclismo & Resistência",
    "⚽ Melhorar Explosão e Resistência para Futebol / Basquete / Vôlei",
    "⚖️ Condicionamento Físico Geral & Emagrecimento",
    "🫀 Saúde Cardiovascular & Longevidade",
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
    modalidade: str = Field(default="Corrida", description="Modalidade: 'Corrida', 'Ciclismo', 'Natação', 'Futebol', 'Basquete', 'Vôlei', 'Musculação', 'Transição (Brick)' ou 'Descanso'")
    tipo_treino: str = Field(description="Título do treino com emoji. Ex: '🏃 Rodagem Z2', '🚴 Ciclismo Endurance Z2', '🏊 Natação Séries', '⚽ Partida / Treino de Futebol', '🏀 Basquete / Treino de Quadra', '🏐 Vôlei', '🏋️ Fortalecimento Funcional', '💤 Descanso Ativo'")
    distancia_km: float = Field(description="Distância total prevista em km (ex: 8.5 para corrida; 35.0 para ciclismo; 1.5 para natação; 0.0 caso coletivo, musculação ou descanso)")
    duracao_min: float = Field(description="Duração estimada em minutos (ex: 45.0, 60.0, 90.0; 0.0 caso descanso)")
    pace_alvo: str = Field(description="Faixa de pace ou intensidade alvo (ex: '05:15 - 05:30 /km' corrida; 'Z2 Cadência 85-90 RPM' ciclismo; '01:50 /100m' natação; 'RPE 7-8 / Jogo Intenso' futebol/coletivos; 'Cargas Moderadas / Core' musculação; ou 'Descanso')")
    rpe_alvo: int = Field(description="Percepção de esforço planejada na escala Borg de 1 a 10")
    estrutura_treino: str = Field(description="Aquecimento detalhado + Treino Principal com orientações específicas da modalidade + Desaquecimento")

class PlanoSemanalPrescrito(BaseModel):
    titulo_ciclo: str = Field(description="Título do ciclo (ex: Semana 1 - Construção de Base e Adaptação Neuromuscular)")
    diagnostico_metodologia: str = Field(description="Diagnóstico da condição atual do atleta baseada no histórico da planilha e metodologia adotada")
    paces_referencia: str = Field(description="Resumo dos paces de referência: Z1 Regenerativo, Z2 Rodagem, Z3 Tempo Run, Z4/Z5 Limiar e Tiros")
    dias: List[TreinoDiarioPrescrito] = Field(description="Lista com os 7 dias completos da semana")
    orientacoes_gerais: str = Field(description="Orientações essenciais de recuperação, hidratação, sono e prevenção de lesões para esta semana")

COACH_SYSTEM_INSTRUCTION = """
Você é um Treinador de Corrida de Rua, Triatlo e Multiesporte de elite com mais de 20 anos de experiência na preparação de atletas amadores e competitivos.
Sua comunicação é direta, motivadora, técnica e sem rodeios.
Ao analisar a imagem (print do Garmin Connect, Strava, Polar, Coros ou Apple Fitness):
1. Extraia meticulosamente os números: distância (km), tempo total (min), ritmo médio (pace mm:ss) e frequência cardíaca média (FC em bpm).
2. Identifique a modalidade da atividade (Corrida, Ciclismo, Natação ou Multiesporte/Força).
3. Analise a correlação entre os dados da imagem, a Percepção Subjetiva de Esforço (RPE na escala de Borg 1-10) e os comentários do atleta.
4. Elabore um parecer técnico do treinador estruturado em três tópicos claros:
   - Diagnóstico do Treino: Análise objetiva da execução em relação ao volume, ritmo/intensidade e modalidade.
   - Intensidade Cardíaca: Avaliação da resposta fisiológica, zonas de esforço e eficiência cardiovascular.
   - Próximo Passo: Orientação prática e prescritiva para a sessão seguinte (ex: descanso, rodagem regenerativa Z1/Z2, soltura em bike/natação ou mobilidade/musculação).
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
    """Busca chave primeiro em st.secrets, depois em os.environ com suporte a maiúsculas/minúsculas."""
    try:
        if key in st.secrets:
            return st.secrets[key]
        if key.lower() in st.secrets:
            return st.secrets[key.lower()]
        if key.upper() in st.secrets:
            return st.secrets[key.upper()]
    except Exception:
        pass
    return os.environ.get(key, os.environ.get(key.upper(), os.environ.get(key.lower(), default)))


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


# ==============================================================================
# SERVIÇOS E CLIENTES SUPABASE (POSTGRESQL & AUTH SAAS)
# ==============================================================================
def get_supabase_credentials() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Busca as credenciais do Supabase de forma flexível em st.secrets e os.environ."""
    url, key, secret_key = None, None, None

    # 1. Seção estruturada [supabase] em st.secrets
    try:
        if "supabase" in st.secrets and isinstance(st.secrets["supabase"], dict):
            sb_sec = st.secrets["supabase"]
            url = sb_sec.get("url") or sb_sec.get("supabase_url") or sb_sec.get("URL")
            key = (
                sb_sec.get("key")
                or sb_sec.get("anon_key")
                or sb_sec.get("publishable_key")
                or sb_sec.get("public_key")
                or sb_sec.get("supabase_key")
                or sb_sec.get("KEY")
            )
            secret_key = (
                sb_sec.get("secret_key")
                or sb_sec.get("service_role_key")
                or sb_sec.get("service_key")
                or sb_sec.get("supabase_secret_key")
                or sb_sec.get("SECRET_KEY")
            )
    except Exception:
        pass

    # 2. Chaves top-level em st.secrets ou variáveis de ambiente
    if not url:
        for k in ["supabase_url", "SUPABASE_URL", "supabase_project_url", "SUPABASE_PROJECT_URL"]:
            v = get_secret_val(k)
            if v:
                url = str(v).strip()
                break

    if not key:
        for k in [
            "supabase_key",
            "SUPABASE_KEY",
            "supabase_anon_key",
            "SUPABASE_ANON_KEY",
            "supabase_publishable_key",
            "SUPABASE_PUBLISHABLE_KEY",
            "supabase_public_key",
            "SUPABASE_PUBLIC_KEY",
        ]:
            v = get_secret_val(k)
            if v:
                key = str(v).strip()
                break

    if not secret_key:
        for k in [
            "supabase_secret_key",
            "SUPABASE_SECRET_KEY",
            "supabase_service_role_key",
            "SUPABASE_SERVICE_ROLE_KEY",
            "supabase_service_key",
            "SUPABASE_SERVICE_KEY",
        ]:
            v = get_secret_val(k)
            if v:
                secret_key = str(v).strip()
                break

    # 3. Fallbacks automáticos entre chaves
    if not key and secret_key:
        key = secret_key
    if not secret_key and key:
        secret_key = key

    return url, key, secret_key


@st.cache_resource
def get_supabase_client() -> Optional[Client]:
    """Retorna o cliente Supabase para auth e operações de banco."""
    url, key, _ = get_supabase_credentials()
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception as e:
        st.error(f"Erro ao inicializar Supabase: {e}")
        return None


@st.cache_resource
def get_supabase_admin() -> Optional[Client]:
    """Retorna o cliente Supabase com privilégios de serviço (admin)."""
    url, _, secret_key = get_supabase_credentials()
    if not url or not secret_key:
        return None
    try:
        return create_client(url, secret_key)
    except Exception:
        return None


def get_current_user() -> Optional[Dict[str, Any]]:
    """Retorna o dicionário do usuário logado na sessão atual."""
    return st.session_state.get("user")


def get_current_user_id() -> Optional[str]:
    """Retorna o UUID do usuário logado ou None se visitante."""
    u = get_current_user()
    return u.get("id") if u else None


def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Retorna o perfil do atleta diretamente do Supabase."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return {}
    try:
        res = sb.table("profiles").select("*").eq("id", user_id).single().execute()
        if res and res.data:
            return res.data
    except Exception:
        pass
    return {}


def update_user_profile(user_id: str, updates: Dict[str, Any]) -> bool:
    """Atualiza o perfil do atleta no Supabase e sincroniza o session_state."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return False
    try:
        sb.table("profiles").update(updates).eq("id", user_id).execute()
        if "user_profile" in st.session_state and st.session_state["user_profile"]:
            st.session_state["user_profile"].update(updates)
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar perfil no Supabase: {e}")
        return False


def get_athlete_profile() -> Dict[str, Any]:
    """Retorna o perfil do atleta (do Supabase para logados ou padrão/visitante)."""
    user = get_current_user()
    if not user:
        if "guest_profile" not in st.session_state:
            st.session_state["guest_profile"] = {
                "nome": "Atleta Visitante",
                "esportes_ativos": ["🏃 Corrida de Rua & Maratona"],
                "nivel_experiencia": "Intermediário (Já pratico com regularidade)",
                "dias_disponiveis": 4,
                "objetivo_principal": "🏃 Meia Maratona (21.1 km)",
                "pwa_aviso_dispensado": st.session_state.get("pwa_aviso_dispensado", False),
                "onboarding_concluido": True,
            }
        return st.session_state["guest_profile"]

    if "user_profile" not in st.session_state or not st.session_state["user_profile"]:
        p = get_user_profile(user["id"])
        if not p:
            p = {
                "id": user["id"],
                "nome": user.get("nome", "Atleta"),
                "email": user.get("email", ""),
                "esportes_ativos": ["🏃 Corrida de Rua & Maratona"],
                "nivel_experiencia": "Intermediário (Já pratico com regularidade)",
                "dias_disponiveis": 4,
                "objetivo_principal": "🏃 Meia Maratona (21.1 km)",
                "pwa_aviso_dispensado": False,
                "onboarding_concluido": False,
            }
        st.session_state["user_profile"] = p
    return st.session_state["user_profile"]


def dismiss_pwa_banner():
    """Marca aviso de salvar como app na tela inicial como dispensado."""
    st.session_state["pwa_aviso_dispensado"] = True
    user = get_current_user()
    if user:
        update_user_profile(user["id"], {"pwa_aviso_dispensado": True})
        if "user_profile" in st.session_state and st.session_state["user_profile"]:
            st.session_state["user_profile"]["pwa_aviso_dispensado"] = True


def generate_and_save_session_token(user_id: str) -> str:
    """Gera um token persistente único e salva no Supabase e na URL (PWA / Mobile)."""
    token = str(uuid.uuid4())
    sb_admin = get_supabase_admin() or get_supabase_client()
    if sb_admin:
        try:
            sb_admin.table("profiles").update({"auth_token": token}).eq("id", user_id).execute()
        except Exception:
            pass
    try:
        st.query_params["token"] = token
    except Exception:
        pass
    return token


def restore_user_from_token() -> bool:
    """Restaura a sessão do atleta a partir do token persistente na URL (para uso mobile/PWA)."""
    try:
        token = st.query_params.get("token")
    except Exception:
        token = None
    if not token:
        return False
    sb_admin = get_supabase_admin() or get_supabase_client()
    if not sb_admin:
        return False
    try:
        res = sb_admin.table("profiles").select("*").eq("auth_token", str(token).strip()).limit(1).execute()
        if res and res.data and len(res.data) > 0:
            user_data = res.data[0]
            st.session_state["user"] = {
                "id": str(user_data["id"]),
                "email": user_data.get("email", ""),
                "nome": user_data.get("nome", "Atleta"),
            }
            st.session_state["user_profile"] = user_data
            if user_data.get("pwa_aviso_dispensado") is not None:
                st.session_state["pwa_aviso_dispensado"] = user_data.get("pwa_aviso_dispensado")
            return True
    except Exception:
        pass
    return False


def auth_sign_in(email: str, password: str, remember: bool = True) -> Tuple[bool, str]:
    """Autentica o atleta por e-mail e senha no Supabase Auth com suporte a token persistente."""
    sb = get_supabase_client()
    if not sb:
        return False, "Cliente Supabase não configurado nos segredos do Streamlit Cloud. Verifique App Settings > Secrets."
    try:
        res = sb.auth.sign_in_with_password({"email": email.strip(), "password": password})
        if res and res.user:
            uid = str(res.user.id)
            st.session_state["user"] = {
                "id": uid,
                "email": res.user.email,
            }
            # Carregar perfil do Supabase
            sb_admin = get_supabase_admin() or sb
            try:
                prof_res = sb_admin.table("profiles").select("*").eq("id", uid).single().execute()
                if prof_res and prof_res.data:
                    st.session_state["user_profile"] = prof_res.data
                    st.session_state["user"]["nome"] = prof_res.data.get("nome", "")
                    if prof_res.data.get("pwa_aviso_dispensado") is not None:
                        st.session_state["pwa_aviso_dispensado"] = prof_res.data.get("pwa_aviso_dispensado")
            except Exception:
                pass

            if remember:
                generate_and_save_session_token(uid)

            st.cache_data.clear()
            return True, "Login realizado com sucesso!"
        return False, "Credenciais inválidas."
    except Exception as e:
        err = str(e)
        if "Invalid login credentials" in err:
            return False, "E-mail ou senha incorretos."
        return False, f"Erro ao autenticar: {err}"


def auth_sign_up(email: str, password: str, name: str, remember: bool = True) -> Tuple[bool, str]:
    """Cadastra um novo atleta no Supabase Auth e registra perfil inicial."""
    sb_admin = get_supabase_admin()
    sb = get_supabase_client()
    if not sb and not sb_admin:
        return False, "Cliente Supabase não configurado nos segredos do Streamlit Cloud. Verifique App Settings > Secrets."

    user_id = None
    user_email = email.strip().lower()

    # 1. Tentar criar via Admin API com email_confirm=True (ignora limite de envio de emails e dispensa confirmação)
    if sb_admin:
        try:
            admin_res = sb_admin.auth.admin.create_user({
                "email": user_email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"full_name": name.strip()},
            })
            if admin_res and admin_res.user:
                user_id = str(admin_res.user.id)
        except Exception as admin_err:
            err_str = str(admin_err).lower()
            if "already registered" in err_str or "already been registered" in err_str:
                return False, "Este e-mail já está cadastrado. Por favor, acesse a aba '🔑 Entrar'."
            # Em caso de outro erro na API admin, tenta o fluxo regular abaixo
            pass

    # 2. Fallback para sb.auth.sign_up
    if not user_id and sb:
        try:
            res = sb.auth.sign_up({"email": user_email, "password": password})
            if res and res.user:
                user_id = str(res.user.id)
        except Exception as sb_err:
            err_str = str(sb_err).lower()
            if "already registered" in err_str or "already been registered" in err_str:
                return False, "Este e-mail já está cadastrado. Por favor, acesse a aba '🔑 Entrar'."
            if "rate limit" in err_str:
                return False, "Limite temporário de cadastros atingido no Supabase. Tente novamente em alguns minutos."
            return False, f"Erro ao cadastrar: {str(sb_err)}"

    if not user_id:
        return False, "Não foi possível criar a conta. Verifique os dados informados."

    token = str(uuid.uuid4()) if remember else None
    initial_profile = {
        "id": user_id,
        "email": user_email,
        "nome": name.strip(),
        "modalidade_preferida": "Corrida",
        "esportes_ativos": ["🏃 Corrida de Rua & Maratona"],
        "nivel_experiencia": "Intermediário (Já pratico com regularidade)",
        "dias_disponiveis": 4,
        "objetivo_principal": "🏃 Meia Maratona (21.1 km)",
        "pwa_aviso_dispensado": False,
        "onboarding_concluido": False,
        "auth_token": token,
    }
    target_sb = sb_admin or sb
    try:
        target_sb.table("profiles").upsert(initial_profile).execute()
    except Exception:
        pass
    st.session_state["user"] = {
        "id": user_id,
        "email": user_email,
        "nome": name.strip(),
    }
    st.session_state["user_profile"] = initial_profile
    st.session_state["show_onboarding"] = True
    if remember and token:
        try:
            st.query_params["token"] = token
        except Exception:
            pass
    st.cache_data.clear()
    return True, "Conta criada com sucesso! Você já está conectado."


def auth_sign_out():
    """Encerra a sessão do atleta no Supabase e limpa o estado e tokens do aparelho."""
    uid = get_current_user_id()
    if uid:
        sb_admin = get_supabase_admin() or get_supabase_client()
        if sb_admin:
            try:
                sb_admin.table("profiles").update({"auth_token": None}).eq("id", uid).execute()
            except Exception:
                pass
    sb = get_supabase_client()
    if sb:
        try:
            sb.auth.sign_out()
        except Exception:
            pass
    if "user" in st.session_state:
        del st.session_state["user"]
    if "user_profile" in st.session_state:
        del st.session_state["user_profile"]
    st.session_state.pop("pwa_aviso_dispensado", None)
    st.session_state.pop("onboarding_shown", None)
    st.session_state.pop("show_onboarding", None)
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.cache_data.clear()


def render_login_screen():
    """Renderiza a tela de login/cadastro obrigatório da plataforma SaaS."""
    st.markdown(
        """
        <div style="text-align: center; margin-top: 1.5rem; margin-bottom: 1.8rem;">
            <div style="font-size: 3.5rem; margin-bottom: 0.4rem;">🏃‍♂️⚡</div>
            <h1 class="main-title" style="margin-bottom: 0.4rem;">Coach AI Multi-Esportes</h1>
            <p class="main-subtitle" style="max-width: 580px; margin: 0 auto 1.5rem auto;">
                Sua consultoria esportiva com IA na nuvem. Periodização inteligente, análise de prints do relógio e prescrição integrada para 
                <strong>Corrida, Triatlo, Ciclismo, Futebol, Basquete, Vôlei e Musculação</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l1, col_center, col_l3 = st.columns([1, 1.8, 1])
    with col_center:
        if not get_supabase_client():
            st.error("⚠️ **Supabase não configurado no Streamlit Cloud**")
            st.markdown(
                """
                As credenciais do Supabase ainda não foram adicionadas nos **Secrets** do app no Streamlit Cloud.
                
                **Como resolver (leva 30 segundos):**
                1. No navegador, acesse seu aplicativo em [share.streamlit.io](https://share.streamlit.io)
                2. No canto inferior direito, clique em **Manage app** ➔ **Settings** ➔ **Secrets**
                3. Adicione as chaves `supabase_url`, `supabase_key` e `supabase_secret_key` e clique em **Save**.
                
                Após salvar, a tela recarregará automaticamente e o cadastro/login funcionará no celular e no computador!
                """
            )

        st.markdown(
            """
            <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.04) 0%, rgba(99, 102, 241, 0.08) 100%); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 14px; padding: 1.2rem 1.4rem; margin-bottom: 1.2rem;">
                <h4 style="margin-top: 0; color: #312E81; display: flex; align-items: center; gap: 8px;">
                    🔐 Acesso à Conta do Atleta
                </h4>
                <p style="font-size: 0.92rem; color: #475569; margin-bottom: 0;">
                    Faça login ou crie sua conta para sincronizar seus treinos e acessar seu cronograma em qualquer aparelho.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_in, tab_up = st.tabs(["🔑 Entrar na Minha Conta", "✨ Criar Conta Gratuita"])

        with tab_in:
            with st.form("form_login_main"):
                login_email = st.text_input("Seu E-mail", placeholder="seu@email.com", key="login_main_email")
                login_pass = st.text_input("Sua Senha", type="password", placeholder="••••••••", key="login_main_pass")
                lembrar_login = st.checkbox("Manter conectado neste celular/aparelho", value=True, help="Recomendado: salva o acesso no seu aparelho para abrir direto sem digitar senha.")
                btn_do_login = st.form_submit_button("🚀 Entrar no Meu Treinador", type="primary", use_container_width=True)

                if btn_do_login:
                    if not login_email or not login_pass:
                        st.warning("⚠️ Informe seu e-mail e senha cadastrados.")
                    else:
                        with st.spinner("Autenticando com Supabase..."):
                            ok_in, msg_in = auth_sign_in(login_email, login_pass, remember=lembrar_login)
                            if ok_in:
                                st.success("✅ Login realizado com sucesso!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(f"❌ {msg_in}")

        with tab_up:
            with st.form("form_register_main"):
                reg_nome = st.text_input("Seu Nome Completo", placeholder="Ex: Carlos Oliveira", key="reg_main_nome")
                reg_email = st.text_input("Seu Melhor E-mail", placeholder="seu@email.com", key="reg_main_email")
                reg_pass1 = st.text_input("Criar Senha (mínimo 6 dígitos)", type="password", placeholder="••••••••", key="reg_main_pass1")
                reg_pass2 = st.text_input("Confirmar Senha", type="password", placeholder="••••••••", key="reg_main_pass2")
                btn_do_register = st.form_submit_button("✨ Criar Conta Gratuita", type="primary", use_container_width=True)

                if btn_do_register:
                    if not reg_email or not reg_pass1:
                        st.warning("⚠️ Preencha os campos obrigatórios.")
                    elif len(reg_pass1) < 6:
                        st.warning("⚠️ A senha deve conter pelo menos 6 caracteres.")
                    elif reg_pass1 != reg_pass2:
                        st.error("❌ As senhas digitadas não coincidem.")
                    else:
                        with st.spinner("Criando sua conta no Supabase Cloud..."):
                            ok_reg, msg_reg = auth_sign_up(reg_email, reg_pass1, reg_nome or "Atleta", remember=True)
                            if ok_reg:
                                st.balloons()
                                st.success(msg_reg)
                                time.sleep(0.8)
                                st.rerun()
                            else:
                                st.error(f"❌ {msg_reg}")

        st.caption("🔒 Seus treinos ficam armazenados de forma privada no Supabase com isolamento total por atleta (RLS).")


# ==============================================================================
# OPERAÇÕES DE DADOS NO SUPABASE (SaaS Multi-tenant)
# ==============================================================================
def load_workouts_from_supabase(user_id: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega os treinos do atleta logado diretamente do Supabase PostgreSQL."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return None, "Supabase não conectado."
    try:
        res = sb.table("workouts").select("*").eq("user_id", user_id).order("created_at", desc=False).execute()
        rows = res.data or []
        if not rows:
            return pd.DataFrame(columns=SHEET_COLUMNS), None

        df = pd.DataFrame(rows)
        mapping = {
            "data": "Data",
            "distancia_km": "Distância (km)",
            "tempo_min": "Tempo (min)",
            "pace_medio": "Pace Médio",
            "fc_media": "FC Média (bpm)",
            "zona_predominante": "Zona Predominante",
            "rpe": "RPE (1-10)",
            "notas_atleta": "Notas do Atleta",
            "parecer_treinador": "Parecer do Treinador",
            "created_at": "Registrado Em",
        }
        df = df.rename(columns=mapping)
        for c in SHEET_COLUMNS:
            if c not in df.columns:
                df[c] = ""

        if "Distância (km)" in df.columns:
            df["Distância (km)"] = pd.to_numeric(df["Distância (km)"], errors="coerce").fillna(0.0)
        if "Tempo (min)" in df.columns:
            df["Tempo (min)"] = pd.to_numeric(df["Tempo (min)"], errors="coerce").fillna(0.0)
        if "FC Média (bpm)" in df.columns:
            df["FC Média (bpm)"] = pd.to_numeric(df["FC Média (bpm)"], errors="coerce").fillna(0).astype(int)
        if "RPE (1-10)" in df.columns:
            df["RPE (1-10)"] = pd.to_numeric(df["RPE (1-10)"], errors="coerce").fillna(0).astype(int)

        return df, None
    except Exception as e:
        return None, f"Erro ao consultar treinos no Supabase: {str(e)}"


def append_workout_to_supabase(
    analysis: TreinoExtracao,
    rpe: int,
    user_notes: str,
    user_id: str
) -> Tuple[bool, str]:
    """Salva com segurança uma nova atividade no Supabase vinculada ao user_id."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return False, "Supabase não configurado."
    try:
        payload = {
            "user_id": user_id,
            "data": analysis.data,
            "distancia_km": float(analysis.distancia_km),
            "tempo_min": float(analysis.tempo_min),
            "pace_medio": str(analysis.pace_medio),
            "fc_media": int(analysis.fc_media),
            "zona_predominante": str(analysis.zona_predominante),
            "rpe": int(rpe),
            "notas_atleta": user_notes.strip(),
            "parecer_treinador": analysis.parecer_treinador.strip(),
        }
        sb.table("workouts").insert(payload).execute()
        st.cache_data.clear()
        return True, "Treino registrado com sucesso no Supabase Cloud!"
    except Exception as e:
        return False, f"Erro ao gravar no Supabase: {str(e)}"


def load_cronograma_from_supabase(user_id: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega o cronograma do atleta logado a partir do Supabase."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return None, "Supabase não conectado."
    try:
        res = sb.table("schedules").select("*").eq("user_id", user_id).order("created_at", desc=False).execute()
        rows = res.data or []
        if not rows:
            return pd.DataFrame(columns=CRONOGRAMA_COLUMNS), None

        df = pd.DataFrame(rows)
        mapping = {
            "id": "ID",
            "dia_semana": "Dia da Semana",
            "data_prevista": "Data Prevista",
            "tipo_treino": "Tipo de Treino",
            "distancia_km": "Distância (km)",
            "duracao_min": "Duração (min)",
            "pace_alvo": "Pace Alvo",
            "rpe_alvo": "RPE Alvo",
            "estrutura_treino": "Estrutura do Treino",
            "status": "Status",
            "data_conclusao": "Data Conclusão",
            "created_at": "Criado Em",
        }
        df = df.rename(columns=mapping)
        for c in CRONOGRAMA_COLUMNS:
            if c not in df.columns:
                df[c] = ""

        if "Distância (km)" in df.columns:
            df["Distância (km)"] = pd.to_numeric(df["Distância (km)"], errors="coerce").fillna(0.0)
        if "Duração (min)" in df.columns:
            df["Duração (min)"] = pd.to_numeric(df["Duração (min)"], errors="coerce").fillna(0.0)
        if "RPE Alvo" in df.columns:
            df["RPE Alvo"] = pd.to_numeric(df["RPE Alvo"], errors="coerce").fillna(0).astype(int)

        return df, None
    except Exception as e:
        return None, f"Erro ao carregar Cronograma do Supabase: {str(e)}"


def mark_workout_as_completed_supabase(workout_id: str, user_id: str) -> Tuple[bool, str]:
    """Marca o treino como Concluído no Supabase."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return False, "Supabase não configurado."
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sb.table("schedules").update({
            "status": "Concluído ✅",
            "data_conclusao": now_str
        }).eq("id", workout_id).eq("user_id", user_id).execute()
        st.cache_data.clear()
        return True, "Treino marcado como Concluído no Supabase!"
    except Exception as e:
        return False, f"Erro ao marcar no Supabase: {str(e)}"


def save_weekly_plan_to_supabase(plano: PlanoSemanalPrescrito, user_id: str) -> Tuple[bool, str]:
    """Salva os 7 dias gerados da planilha no Supabase com status 'Pendente'."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return False, "Supabase não configurado."
    try:
        novas_linhas = []
        for d in plano.dias:
            treino_id = f"TR-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            novas_linhas.append({
                "id": treino_id,
                "user_id": user_id,
                "dia_semana": d.dia_semana,
                "data_prevista": d.data_prevista,
                "tipo_treino": d.tipo_treino,
                "distancia_km": float(d.distancia_km),
                "duracao_min": float(d.duracao_min),
                "pace_alvo": str(d.pace_alvo),
                "rpe_alvo": int(d.rpe_alvo),
                "estrutura_treino": str(d.estrutura_treino),
                "status": "Pendente",
                "data_conclusao": "",
            })
        sb.table("schedules").insert(novas_linhas).execute()
        st.cache_data.clear()
        return True, f"Plano com {len(novas_linhas)} sessões sincronizado com o Supabase Cloud!"
    except Exception as e:
        return False, f"Erro ao salvar no Supabase: {str(e)}"


def clear_cronograma_in_supabase(user_id: str) -> Tuple[bool, str]:
    """Limpa todas as sessões agendadas do atleta no Supabase."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return False, "Supabase não configurado."
    try:
        sb.table("schedules").delete().eq("user_id", user_id).execute()
        st.cache_data.clear()
        return True, "Cronograma limpo com sucesso no Supabase!"
    except Exception as e:
        return False, f"Erro ao limpar Supabase: {str(e)}"


# ==============================================================================
# CAMADA DE DADOS UNIFICADA (ROTEAMENTO INTELIGENTE SUPABASE / GOOGLE SHEETS)
# ==============================================================================
def load_workouts_data() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega treinos do Supabase se o usuário estiver logado, ou do Google Sheets como fallback."""
    uid = get_current_user_id()
    if uid:
        return load_workouts_from_supabase(uid)
    return load_workouts_from_sheets()


def append_workout_data(analysis: TreinoExtracao, rpe: int, user_notes: str) -> Tuple[bool, str]:
    """Salva o treino no Supabase (se logado) ou no Google Sheets."""
    uid = get_current_user_id()
    if uid:
        return append_workout_to_supabase(analysis, rpe, user_notes, uid)
    return append_workout_to_sheets(analysis, rpe, user_notes)


def load_cronograma_data() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega o cronograma do Supabase (se logado) ou do Google Sheets."""
    uid = get_current_user_id()
    if uid:
        return load_cronograma_from_supabase(uid)
    return load_cronograma_from_sheets()


def mark_workout_as_completed_data(workout_id: str) -> Tuple[bool, str]:
    """Marca treino concluído no Supabase (se logado) ou no Google Sheets."""
    uid = get_current_user_id()
    if uid:
        return mark_workout_as_completed_supabase(workout_id, uid)
    return mark_workout_as_completed(workout_id)


def save_weekly_plan_data(plano: PlanoSemanalPrescrito) -> Tuple[bool, str]:
    """Salva periodização semanal no Supabase (se logado) ou no Google Sheets."""
    uid = get_current_user_id()
    if uid:
        return save_weekly_plan_to_supabase(plano, uid)
    return save_weekly_plan_to_sheets(plano)


def clear_cronograma_data() -> Tuple[bool, str]:
    """Limpa cronograma no Supabase (se logado) ou no Google Sheets."""
    uid = get_current_user_id()
    if uid:
        return clear_cronograma_in_supabase(uid)
    return clear_cronograma_in_sheets()


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
# CONTROLE DE SESSÃO & LOGIN OBRIGATÓRIO (SaaS MULTI-TENANT)
# ==============================================================================
# 1. Tentar restaurar login persistente via token na URL (Mobile / PWA)
if not get_current_user():
    restore_user_from_token()

# 2. Se ainda não estiver autenticado, exibir tela de Login/Cadastro e parar a execução
if not get_current_user():
    render_login_screen()
    st.stop()


# ==============================================================================
# MODAIS POPUP (STREAMLIT DIALOGS)
# ==============================================================================


@st.dialog("🎯 Boas-vindas ao Coach AI: O Porquê & Seus Esportes", width="large")
def modal_onboarding():
    st.markdown(
        """
        <div class="purpose-box">
            <h4>💡 O Porquê deste App: Treinador Multi-Esportes Integrado</h4>
            <p>
                <strong>Seu corpo não treina em compartimentos isolados.</strong> Se você joga futebol na quarta-feira, 
                pedala no sábado e faz fortalecimento, seu sistema cardiovascular e neuromuscular acumula uma carga cumulativa que afeta diretamente sua corrida e recuperação.
            </p>
            <ul>
                <li><strong>Carga Cumulativa Real:</strong> O Coach AI integra todas as suas atividades para prescrever treinos precisos e dosar o descanso exato.</li>
                <li><strong>Prevenção de Lesões:</strong> Evita overtraining e sobrecarga articular ajustando o volume quando você pratica outros esportes.</li>
                <li><strong>Treinamento Cruzado:</strong> Usa modalidades de baixo impacto (ciclismo e natação) para construir resistência aeróbica e acelerar sua corrida.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### ⚙️ Configure seu Perfil de Atleta:")
    st.caption("Você pode alterar esses focos a qualquer momento no botão **'⚙️ Meus Esportes'**!")

    uid = get_current_user_id()
    perf = get_athlete_profile()
    esportes_atuais = perf.get("esportes_ativos") or ["🏃 Corrida de Rua & Maratona"]
    esportes_validos = [e for e in esportes_atuais if e in ESPORTES_OPCOES] or [ESPORTES_OPCOES[0]]

    escolha_esportes = st.multiselect(
        "Quais esportes você pratica ou deseja incluir na sua rotina semanal?",
        options=ESPORTES_OPCOES,
        default=esportes_validos,
        help="Selecione corrida, bike, natação, futebol, triatlo, etc. O Coach levará todos em consideração.",
    )

    col_ob1, col_ob2 = st.columns(2)
    with col_ob1:
        dias_ob = st.slider(
            "📅 Quantos dias por semana você deseja treinar?",
            min_value=2,
            max_value=7,
            value=int(perf.get("dias_disponiveis", 4) or 4),
            help="Soma total de dias com atividades esportivas ou fortalecimento.",
        )
    with col_ob2:
        n_val = perf.get("nivel_experiencia")
        n_idx = NIVEIS_EXPERIENCIA.index(n_val) if n_val in NIVEIS_EXPERIENCIA else 1
        nivel_ob = st.selectbox(
            "🏅 Seu nível de experiência geral:",
            options=NIVEIS_EXPERIENCIA,
            index=n_idx,
        )

    m_val = perf.get("objetivo_principal")
    m_idx = METAS_OPCOES.index(m_val) if m_val in METAS_OPCOES else 1
    meta_ob = st.selectbox(
        "🎯 Qual é o seu foco esportivo principal no momento?",
        options=METAS_OPCOES,
        index=m_idx,
    )

    col_salvar, col_pular = st.columns([2.5, 1])
    with col_salvar:
        if st.button("🚀 Salvar Perfil & Começar!", type="primary", use_container_width=True, key="btn_save_onboarding"):
            if not escolha_esportes:
                st.warning("⚠️ Selecione pelo menos um esporte ativo.")
            else:
                novos_dados = {
                    "esportes_ativos": escolha_esportes,
                    "dias_disponiveis": dias_ob,
                    "nivel_experiencia": nivel_ob,
                    "objetivo_principal": meta_ob,
                    "onboarding_concluido": True,
                }
                if uid:
                    update_user_profile(uid, novos_dados)
                else:
                    if "guest_profile" not in st.session_state:
                        st.session_state["guest_profile"] = {}
                    st.session_state["guest_profile"].update(novos_dados)
                st.session_state["onboarding_shown"] = True
                st.balloons()
                st.success("🎉 Perfil configurado com sucesso! Vamos aos treinos!")
                time.sleep(0.8)
                st.rerun()

    with col_pular:
        if st.button("✕ Pular", use_container_width=True, key="btn_skip_onboarding", help="Configurar mais tarde"):
            st.session_state["onboarding_shown"] = True
            st.rerun()


@st.dialog("⚙️ Meus Esportes e Metas", width="medium")
def modal_meus_esportes():
    st.markdown("Atualize seus esportes ativos, dias disponíveis e objetivos sempre que quiser:")
    uid = get_current_user_id()
    perf = get_athlete_profile()
    esportes_atuais = perf.get("esportes_ativos") or ["🏃 Corrida de Rua & Maratona"]
    esportes_validos = [e for e in esportes_atuais if e in ESPORTES_OPCOES] or [ESPORTES_OPCOES[0]]

    novos_esportes = st.multiselect(
        "Esportes ativos na sua rotina:",
        options=ESPORTES_OPCOES,
        default=esportes_validos,
        help="Adicione ou remova modalidades de acordo com a sua fase de treinamento.",
    )

    col_me1, col_me2 = st.columns(2)
    with col_me1:
        novos_dias = st.slider(
            "Dias de treino por semana:",
            min_value=2,
            max_value=7,
            value=int(perf.get("dias_disponiveis", 4) or 4),
        )
    with col_me2:
        n_val = perf.get("nivel_experiencia")
        n_idx = NIVEIS_EXPERIENCIA.index(n_val) if n_val in NIVEIS_EXPERIENCIA else 1
        novo_nivel = st.selectbox(
            "Nível esportivo:",
            options=NIVEIS_EXPERIENCIA,
            index=n_idx,
            key="sb_novo_nivel_me",
        )

    m_val = perf.get("objetivo_principal")
    m_idx = METAS_OPCOES.index(m_val) if m_val in METAS_OPCOES else 1
    nova_meta = st.selectbox(
        "Foco / Meta principal:",
        options=METAS_OPCOES,
        index=m_idx,
        key="sb_nova_meta_me",
    )

    if st.button("💾 Salvar Alterações de Foco", type="primary", use_container_width=True, key="btn_save_meus_esportes"):
        if not novos_esportes:
            st.warning("⚠️ Selecione pelo menos 1 esporte ativo.")
        else:
            updates = {
                "esportes_ativos": novos_esportes,
                "dias_disponiveis": novos_dias,
                "nivel_experiencia": novo_nivel,
                "objetivo_principal": nova_meta,
                "onboarding_concluido": True,
            }
            if uid:
                update_user_profile(uid, updates)
            else:
                if "guest_profile" not in st.session_state:
                    st.session_state["guest_profile"] = {}
                st.session_state["guest_profile"].update(updates)
            st.success("✅ Esportes e focos atualizados com sucesso!")
            time.sleep(0.8)
            st.rerun()


@st.dialog("📸 Registrar Treino com Print (Garmin/Strava)", width="large")
def modal_registrar_treino_print():
    st.markdown("Envie o print do seu relógio ou aplicativo de corrida para análise imediata com o Coach AI:")
    col_up, col_in = st.columns([1.1, 1], gap="medium")

    with col_up:
        uploaded_file_m = st.file_uploader(
            "Print do Treino (Garmin Connect, Strava, Polar)",
            type=["png", "jpg", "jpeg", "webp"],
            key="modal_upload_file",
            help="Certifique-se de que a imagem mostre distância, tempo, pace e frequência cardíaca se disponível.",
        )
        if uploaded_file_m:
            st.image(uploaded_file_m, caption="Visualização do Print Enviado", use_container_width=True)

    with col_in:
        rpe_m = st.slider(
            "Percepção de Esforço (RPE - Escala de Borg)",
            min_value=1,
            max_value=10,
            value=6,
            key="modal_slider_rpe",
            help="1: Muito leve | 3: Z2 conversacional | 5: Ritmo de Maratona | 7-8: Forte / Limiar | 10: Máximo",
        )
        rpe_labels_m = {
            1: "1 - Muito Leve",
            2: "2 - Leve (Conversacional)",
            3: "3 - Moderado Leve (Zona 2)",
            4: "4 - Moderado (Confortável)",
            5: "5 - Moderado Firme (Maratona)",
            6: "6 - Firme (Início de Ritmo)",
            7: "7 - Forte (Meia Maratona)",
            8: "8 - Muito Forte (Limiar / 10k)",
            9: "9 - Severo (Tiros VO2 Máx)",
            10: "10 - Esforço Máximo",
        }
        st.caption(f"**Intensidade:** {rpe_labels_m.get(rpe_m, '')}")
        user_notes_m = st.text_area(
            "Sensações e Notas do Atleta (Opcional)",
            placeholder="Ex: Treino em aclive; pernas soltas; hidratação a cada 3km; sem dores articulares.",
            height=110,
            key="modal_user_notes",
        )
        btn_analisar_m = st.button(
            "🚀 Analisar e Gravar Treino",
            type="primary",
            use_container_width=True,
            key="btn_modal_analisar_act",
        )

    if btn_analisar_m:
        if not uploaded_file_m:
            st.warning("⚠️ Selecione e faça upload de um print de corrida antes de analisar.")
        else:
            client = get_gemini_client()
            if not client:
                st.error("🔑 Chave de API do Gemini não configurada.")
            else:
                with st.spinner("🏃 Processando print e salvando dados..."):
                    try:
                        res = analyze_workout_image(
                            image_bytes=uploaded_file_m.getvalue(),
                            mime_type=uploaded_file_m.type or "image/jpeg",
                            rpe=rpe_m,
                            user_notes=user_notes_m,
                            gemini_client=client,
                        )
                        salvo, msg_sheets = append_workout_data(res, rpe_m, user_notes_m)
                        st.session_state["ultimo_treino"] = res
                        st.session_state["sheets_salvo"] = salvo
                        st.session_state["sheets_msg"] = msg_sheets
                        st.cache_data.clear()
                        st.balloons()
                        st.success("✅ Atividade analisada com sucesso e sincronizada!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro no processamento: {str(e)}")


@st.dialog("💬 Conversar com o Coach AI", width="large")
def modal_conversar_coach():
    st.markdown("##### Tire dúvidas rápidas com o Treinador sobre treinos, ritmo e recuperação:")
    df_ctx, _ = load_workouts_data()
    hist_txt = format_athlete_history_for_prompt(df_ctx)

    st.markdown("###### ⚡ Perguntas Rápidas:")
    cols_q = st.columns(2)
    pergunta_selecionada = None
    with cols_q[0]:
        if st.button("📈 Como está meu ritmo (pace)?", use_container_width=True, key="m_btn_pace"):
            pergunta_selecionada = "Como está minha evolução de ritmo (pace) recente com base no meu histórico de treinos?"
        if st.button("💤 O que fazer amanhã?", use_container_width=True, key="m_btn_amanha"):
            pergunta_selecionada = "Qual treino ou descanso você recomenda para amanhã considerando meu último esforço registrado?"
    with cols_q[1]:
        if st.button("❤️ Avaliar meu coração (FC)", use_container_width=True, key="m_btn_fc"):
            pergunta_selecionada = "Avalie minha eficiência cardiovascular e zonas relacionando meu ritmo e FC média."
        if st.button("🎯 Meta de Meia Maratona", use_container_width=True, key="m_btn_meia"):
            pergunta_selecionada = "Estou com volume e consistência adequados para encarar uma Meia Maratona (21.1 km)?"

    pergunta_input = st.text_input(
        "Ou digite sua dúvida personalizada:",
        placeholder="Ex: Como dosar o ritmo nos primeiros 3km?",
        key="modal_input_pergunta",
    )
    btn_enviar_duvida = st.button("Enviar Dúvida", type="primary", use_container_width=True, key="m_btn_enviar")

    pergunta_final = pergunta_selecionada or (pergunta_input if (btn_enviar_duvida and pergunta_input.strip()) else None)

    if pergunta_final:
        client = get_gemini_client()
        if not client:
            st.error("🔑 API Key do Gemini não configurada.")
        else:
            with st.spinner("🏃 O Coach está consultando seu histórico e formulando a orientação..."):
                try:
                    perf = get_athlete_profile()
                    esportes_str = ", ".join(perf.get("esportes_ativos", ["Corrida"]))
                    nivel_str = perf.get("nivel_experiencia", "Intermediário")
                    dias_str = perf.get("dias_disponiveis", 4)
                    meta_str = perf.get("objetivo_principal", "Meia Maratona")

                    sys_prompt = f"""Você é o Treinador Chefe de Corrida e Multiesportes do atleta.
PERFIL DO ATLETA:
- Esportes Praticados: {esportes_str}
- Nível de Experiência: {nivel_str}
- Frequência semanal: {dias_str} dias
- Foco / Meta Principal: {meta_str}

HISTÓRICO REAL DA PLANILHA / SUPABASE:
{hist_txt}

LEMBRE-SE: Como o atleta pratica {esportes_str}, considere a fadiga cumulativa neuromuscular e o princípio do treinamento cruzado ao formular a recomendação.
Responda de forma direta, técnica, motivadora e baseada nesses dados reais:
"""
                    resp = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"{sys_prompt}\n\nDÚVIDA DO ATLETA: {pergunta_final}",
                        config=types.GenerateContentConfig(temperature=0.4),
                    )
                    st.markdown(
                        f"""
                        <div class="coach-card">
                            <span class="coach-badge">🎯 Resposta do Treinador</span>
                            <p>{resp.text.replace(chr(10), '<br>')}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if "chat_messages" in st.session_state:
                        st.session_state["chat_messages"].append({"role": "user", "content": pergunta_final})
                        st.session_state["chat_messages"].append({"role": "assistant", "content": resp.text})
                except Exception as e:
                    st.error(f"Erro: {str(e)}")

    st.caption("💡 *Dica:* Para ter conversas longas e completas com histórico, acesse a aba **'💬 Coach AI'**!")


# ==============================================================================
# CABEÇALHO DA INTERFACE (USUÁRIO AUTENTICADO)
# ==============================================================================
col_title, col_status = st.columns([2.8, 2.2])
with col_title:
    st.markdown('<div class="main-title">🏃 Coach de Corrida AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Treinador inteligente multi-esportes: corrida, triatlo, bike, natação, futebol e mais com Gemini 2.5 & Supabase</div>',
        unsafe_allow_html=True,
    )

with col_status:
    user = get_current_user()
    perf = get_athlete_profile()
    esportes_list = perf.get("esportes_ativos") or ["🏃 Corrida de Rua & Maratona"]
    nome_display = perf.get("nome") or (user.get("nome") if user else None) or (user.get("email") if user else "Atleta")

    st.markdown(f"👤 **{nome_display}**")
    
    # Pílulas dos esportes ativos
    pills = []
    for esp in esportes_list[:3]:
        partes = esp.split()
        emoji_tag = partes[0]
        nome_curto = partes[1] if len(partes) > 1 and len(partes[1]) <= 10 else ""
        pills.append(f'<span class="sport-pill">{emoji_tag} {nome_curto}</span>')
    pills_html = " ".join(pills)
    if len(esportes_list) > 3:
        pills_html += f' <span class="sport-pill">+{len(esportes_list) - 3}</span>'
    st.markdown(pills_html, unsafe_allow_html=True)

    col_h1, col_h2 = st.columns([1.2, 1])
    with col_h1:
        if st.button("⚙️ Focos", key="btn_focos_header", use_container_width=True, help="Alterar meus esportes, dias e meta"):
            modal_meus_esportes()
    with col_h2:
        if st.button("🚪 Sair", key="btn_logout_top", help="Desconectar desta conta e limpar acesso do aparelho", use_container_width=True):
            auth_sign_out()
            st.rerun()


# ==============================================================================
# VERIFICAÇÃO DE ONBOARDING AUTOMÁTICO
# ==============================================================================
user_check = get_current_user()
if user_check:
    perf_check = get_athlete_profile()
    if not perf_check.get("onboarding_concluido") and not st.session_state.get("onboarding_shown"):
        st.session_state["onboarding_shown"] = True
        modal_onboarding()

# ==============================================================================
# BARRA SUPERIOR DE AÇÕES RÁPIDAS
# ==============================================================================
col_qa1, col_qa2, col_qa3 = st.columns([1.2, 1.2, 1.0], gap="small")
with col_qa1:
    if st.button("📸 Registrar com Print", type="primary", use_container_width=True, help="Abre janela rápida para carregar print do Strava, Garmin ou Polar."):
        modal_registrar_treino_print()
with col_qa2:
    if st.button("💬 Conversar com o Coach", use_container_width=True, help="Abre consultoria rápida e tire dúvidas sobre ritmo, dores e treino."):
        modal_conversar_coach()
with col_qa3:
    if st.button("⚙️ Meus Esportes", use_container_width=True, help="Ajustar esportes praticados, dias por semana e meta principal."):
        modal_meus_esportes()

st.write("")

# ==============================================================================
# ABAS PRINCIPAIS (5 ABAS COMPLETAS E INTEGRADAS)
# ==============================================================================
tab_painel, tab_planilha, tab_historico, tab_chat, tab_ajuda = st.tabs([
    "🏠 Meu Painel",
    "📋 Montador de Treinos",
    "📊 Histórico & Gráficos",
    "💬 Coach AI",
    "❓ Ajuda & Glossário",
])

# ------------------------------------------------------------------------------
# ABA 1: MEU PAINEL (HOME / TREINO ATUAL EM DESTAQUE)
# ------------------------------------------------------------------------------
with tab_painel:
    # 0. BANNER PWA MOBILE (Salvar como aplicativo no celular)
    perf_painel = get_athlete_profile()
    pwa_dispensado = perf_painel.get("pwa_aviso_dispensado", False) or st.session_state.get("pwa_aviso_dispensado", False)

    if not pwa_dispensado:
        st.markdown(
            """
            <div class="pwa-card">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.35rem; flex-wrap: wrap; gap: 8px;">
                    <h4 style="margin: 0; display: flex; align-items: center; gap: 8px;">
                        📲 Salve o Coach AI como App no seu Celular!
                    </h4>
                    <span style="font-size: 0.78rem; background: rgba(255,255,255,0.18); padding: 3px 10px; border-radius: 9999px; font-weight: 600;">
                        Acesso com 1 Toque
                    </span>
                </div>
                <p style="margin-bottom: 0.7rem; font-size: 0.93rem;">
                    Instale direto na tela de início do seu smartphone para abrir em tela cheia e registrar seus treinos com máxima velocidade:
                </p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 10px; margin-bottom: 0.75rem;">
                    <div class="pwa-os-box">
                        <strong style="color: #F8FAFC;">🍏 No iPhone (Safari):</strong><br>
                        1. Toque no ícone de <strong>Compartilhar</strong> (quadrado com seta ⬆️ no rodapé)<br>
                        2. Role a lista e toque em <strong>"Adicionar à Tela de Início"</strong> 📲
                    </div>
                    <div class="pwa-os-box">
                        <strong style="color: #F8FAFC;">🤖 No Android (Google Chrome):</strong><br>
                        1. Toque nos <strong>3 pontinhos (⋮)</strong> no canto superior direito<br>
                        2. Toque em <strong>"Adicionar à tela inicial"</strong> ou <strong>"Instalar aplicativo"</strong> 📲
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_pwa_btn, col_pwa_note = st.columns([1.8, 3.2])
        with col_pwa_btn:
            if st.button("✅ Já salvei na tela inicial / Entendi!", key="btn_dispensar_pwa_painel", type="secondary", use_container_width=True):
                dismiss_pwa_banner()
                st.toast("✅ Aviso dispensado! O guia completo continuará na aba '❓ Ajuda'.")
                st.rerun()
        with col_pwa_note:
            st.caption("🔒 Ao confirmar, este aviso não será mais exibido. O passo a passo continuará sempre acessível na aba **'❓ Ajuda & Glossário'**.")
        st.write("")

    df_crono, erro_crono = load_cronograma_data()

    # 1. SPOTLIGHT HERO CARD: TREINO ATUAL / PRÓXIMA SESSÃO
    st.markdown("### 🔥 Treino Atual em Destaque")
    if erro_crono:
        st.info(f"ℹ️ {erro_crono}")
    elif df_crono is None or df_crono.empty:
        st.info(
            "📋 Você ainda não possui treinos agendados no Cronograma. "
            "Acesse a aba **'📋 Montador de Treinos'** para prescrever sua planilha semanal com 1 clique!"
        )
    else:
        df_pendentes = df_crono[df_crono["Status"] == "Pendente"]
        if not df_pendentes.empty:
            proximo = df_pendentes.iloc[0]
            if proximo["Distância (km)"] > 0:
                dist_str = f"{proximo['Distância (km)']:.1f} km"
            elif any(k in str(proximo['Tipo de Treino']) for k in ["Futebol", "Basquete", "Vôlei", "⚽", "🏀", "🏐"]):
                dist_str = "Partida / Jogo Coletivo"
            elif any(k in str(proximo['Tipo de Treino']) for k in ["Musculação", "Fortalecimento", "Força", "🏋️"]):
                dist_str = "Sessão de Força & Mobilidade"
            else:
                dist_str = "Descanso / Recuperação Ativa"
            dur_str = f"{proximo['Duração (min)']:.0f} min" if proximo["Duração (min)"] > 0 else "--"

            tipo_raw = str(proximo['Tipo de Treino']).strip()
            emoji_prefix = "" if any(tipo_raw.startswith(e) for e in ["🏃", "🚴", "🏊", "💤", "⚡", "🏋️", "🏅", "🏆", "🎯", "⚽", "🏀", "🏐", "🌐"]) else "🏃 "

            st.markdown(
                f"""
                <div class="next-workout-card">
                    <span class="coach-badge" style="background: rgba(99, 102, 241, 0.35); color: #C7D2FE;">
                        🔥 PRÓXIMA SESSÃO • {proximo['Dia da Semana']} ({proximo['Data Prevista']})
                    </span>
                    <h3>{emoji_prefix}{tipo_raw}</h3>
                    <p>
                        <strong>Distância Prevista:</strong> {dist_str} &nbsp;|&nbsp; 
                        <strong>Duração Estimada:</strong> {dur_str} &nbsp;|&nbsp; 
                        <strong>Ritmo / Intensidade Alvo:</strong> {proximo['Pace Alvo']} &nbsp;|&nbsp; 
                        <strong>RPE Alvo:</strong> {proximo['RPE Alvo']}/10
                    </p>
                    <p><strong>Estrutura da Sessão:</strong><br>{proximo['Estrutura do Treino'].replace(chr(10), '<br>')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_ck1, col_ck2 = st.columns([1.8, 2.2])
            with col_ck1:
                if st.button(
                    "✅ Marcar como Feito / Concluído",
                    type="primary",
                    use_container_width=True,
                    key="btn_checkin_hero",
                    help="Terminou a atividade? Clique para registrar a conclusão com data e horário no Google Sheets!",
                ):
                    with st.spinner("Atualizando status do treino..."):
                        sucesso_ck, msg_ck = mark_workout_as_completed_data(proximo_id)
                        if sucesso_ck:
                            st.balloons()
                            st.success(f"🎉 Parabéns atleta! {msg_ck}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg_ck)
            with col_ck2:
                if st.button(
                    "📸 Enviar Print deste Treino",
                    use_container_width=True,
                    key="btn_print_hero",
                    help="Envie o print do Garmin/Strava deste treino para receber análise técnica da IA.",
                ):
                    modal_registrar_treino_print()
        else:
            st.success("🎉 Parabéns! Todos os treinos desta planilha foram concluídos. Que tal prescrever um novo ciclo na aba '📋 Montador de Treinos'?")

    # 2. FEEDBACK RECENTE DO TREINADOR (SE HOUVER TREINO ANALISADO RECENTEMENTE)
    if "ultimo_treino" in st.session_state:
        res: TreinoExtracao = st.session_state["ultimo_treino"]
        st.markdown("---")
        st.markdown("### 📋 Último Treino Analisado pelo Coach AI")
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

    # 3. MÉTRICAS DE ADESÃO DA SEMANA
    if df_crono is not None and not df_crono.empty:
        st.markdown("---")
        st.markdown("### 📊 Progresso da Planilha Semanal")
        total_sessoes = len(df_crono)
        concluidos = len(df_crono[df_crono["Status"].str.contains("Concluído", na=False)])
        pendentes = total_sessoes - concluidos
        pct_conclusao = (concluidos / total_sessoes) if total_sessoes > 0 else 0.0

        km_planejados = df_crono["Distância (km)"].sum()
        km_feitos = df_crono[df_crono["Status"].str.contains("Concluído", na=False)]["Distância (km)"].sum()

        st.progress(pct_conclusao)
        c_col1, c_col2, c_col3, c_col4 = st.columns(4)
        with c_col1:
            st.metric("⏳ Pendentes", f"{pendentes} treinos")
        with c_col2:
            st.metric("✅ Concluídos", f"{concluidos} treinos")
        with c_col3:
            st.metric("🏃 Km Realizados", f"{km_feitos:.1f} / {km_planejados:.1f} km")
        with c_col4:
            st.metric("📊 Taxa de Adesão", f"{pct_conclusao * 100:.1f}%")

        # 4. TABELA DO CRONOGRAMA
        st.markdown("---")
        st.markdown("#### 🗓️ Grade Completa do Cronograma")
        col_btn_refresh_crono, col_btn_clear_crono, _ = st.columns([1.5, 1.5, 3])
        with col_btn_refresh_crono:
            btn_refresh_crono = st.button("🔄 Atualizar Grade", use_container_width=True, key="btn_ref_crono_panel")
            if btn_refresh_crono:
                st.cache_data.clear()
                st.rerun()

        with col_btn_clear_crono:
            with st.popover("🗑️ Limpar Grade", help="Clique para apagar os treinos agendados e começar uma planilha nova."):
                st.write("Deseja apagar todos os treinos da planilha 'Cronograma'?")
                if st.button("⚠️ Confirmar e Limpar", type="primary", use_container_width=True, key="btn_confirm_clear_panel"):
                    with st.spinner("Limpando sessões..."):
                        ok_cl, msg_cl = clear_cronograma_data()
                        if ok_cl:
                            st.success(msg_cl)
                            st.rerun()
                        else:
                            st.error(msg_cl)

        filtro_status = st.radio(
            "Filtrar grade:",
            ["Todos", "Apenas Pendentes ⏳", "Apenas Concluídos ✅"],
            horizontal=True,
            key="filtro_status_painel",
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

    # 5. UPLOAD DIRETO OPCIONAL (SEM POPUP)
    with st.expander("📤 Preferir registrar treino com print diretamente nesta tela?"):
        col_up_in, col_inputs_in = st.columns([1.2, 1], gap="medium")
        with col_up_in:
            up_inline = st.file_uploader(
                "Print do Treino",
                type=["png", "jpg", "jpeg", "webp"],
                key="up_inline_painel",
            )
            if up_inline:
                st.image(up_inline, caption="Visualização do Print Enviado", use_container_width=True)
        with col_inputs_in:
            rpe_in = st.slider("RPE (1-10)", 1, 10, 6, key="rpe_inline_painel")
            user_notes_in = st.text_area("Notas e Sensações", height=100, key="notes_inline_painel")
            if st.button("🚀 Analisar Treino Inline", type="primary", use_container_width=True, key="btn_analisar_inline"):
                if not up_inline:
                    st.warning("⚠️ Selecione um print de treino.")
                else:
                    client = get_gemini_client()
                    if client:
                        with st.spinner("🏃 Analisando com Gemini 2.5 Flash..."):
                            try:
                                res_in = analyze_workout_image(
                                    image_bytes=up_inline.getvalue(),
                                    mime_type=up_inline.type or "image/jpeg",
                                    rpe=rpe_in,
                                    user_notes=user_notes_in,
                                    gemini_client=client,
                                )
                                salvo_in, msg_s_in = append_workout_data(res_in, rpe_in, user_notes_in)
                                st.session_state["ultimo_treino"] = res_in
                                st.session_state["sheets_salvo"] = salvo_in
                                st.session_state["sheets_msg"] = msg_s_in
                                st.cache_data.clear()
                                st.balloons()
                                st.success("✅ Treino analisado e registrado com sucesso!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {str(e)}")

# ------------------------------------------------------------------------------
# ABA 3: HISTÓRICO E GRÁFICOS
# ------------------------------------------------------------------------------
with tab_historico:
    st.markdown("### 📊 Histórico de Atividades & Evolução Fisiológica")
    
    col_btn_refresh, _ = st.columns([1.5, 4])
    with col_btn_refresh:
        btn_refresh = st.button("🔄 Atualizar / Recarregar Dados", use_container_width=True)
        if btn_refresh:
            st.cache_data.clear()
            st.rerun()

    df_treinos, erro_carregamento = load_workouts_data()

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
            st.metric("🏃 Volume Total Acumulado", f"{total_km:.2f} km", help="Quilometragem somada de todas as corridas registradas até hoje.")
        with tot_col2:
            st.metric("🎯 Total de Sessões", f"{total_treinos} treinos", help="Número total de atividades já analisadas e guardadas.")
        with tot_col3:
            st.metric("❤️ FC Média Geral", f"{fc_global} bpm" if fc_global > 0 else "--", help="Frequência cardíaca média histórica em Batimentos Por Minuto (BPM).")
        with tot_col4:
            st.metric("📊 Média por Sessão", f"{km_por_treino:.2f} km", help="Distância média percorrida em cada treino (volume dividido pelo total de sessões).")

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
    st.write("Converse com o Coach sobre suas sensações, peça análises da sua evolução ou tire dúvidas sobre ritmo, nutrição e descanso. **O Treinador analisa o histórico de treinos em tempo real!**")

    df_contexto, _ = load_workouts_data()
    historico_texto = format_athlete_history_for_prompt(df_contexto)

    if "chat_messages" not in st.session_state:
        msg_inicial = (
            "Fala atleta! 🏃‍♂️ Sou seu treinador de corrida com inteligência artificial. "
            "Tenho acesso a todo o seu histórico de treinos registrado na nuvem. "
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
                        perf_chat = get_athlete_profile()
                        esportes_chat = ", ".join(perf_chat.get("esportes_ativos", ["Corrida"]))
                        nivel_chat = perf_chat.get("nivel_experiencia", "Intermediário")
                        dias_chat = perf_chat.get("dias_disponiveis", 4)
                        meta_chat = perf_chat.get("objetivo_principal", "Meia Maratona")

                        chat_system_instruction = f"""Você é o Treinador Chefe de Corrida de Rua, Maratonas e Multiesporte do atleta.
PERFIL DO ATLETA:
- Modalidades e Esportes Praticados: {esportes_chat}
- Nível de Experiência: {nivel_chat}
- Frequência Semanal Desejada: {dias_chat} sessões por semana
- Meta / Foco Principal: {meta_chat}

Você possui vasta experiência com corredores, triatletas e atletas multiesporte (futebol, bike, natação, basquete, vôlei, musculação), aplicando fisiologia esportiva (carga neuromuscular cumulativa, treinamento cruzado, Jack Daniels VDOT, limiares de lactato e prevenção de lesões).
Sua missão é fornecer respostas técnicas, assertivas, motivadoras e personalizadas.

CONTEXTO REAL DO ATLETA (HISTÓRICO ATUALIZADO):
{historico_texto}

DIRETRIZES DA RESPOSTA:
1. Sempre considere todos os esportes praticados ({esportes_chat}). Se o atleta mencionar futebol, basquete ou vôlei, lembre do alto estresse excêntrico nas pernas e desacelerações bruscas; se pedala ou nada, use como estímulo aeróbico regenerativo ou de base sem impacto articular.
2. Sempre cite e cruze dados reais dos treinos do atleta (datas, quilometragens, FC e paces reais registrados).
3. Se o atleta perguntar se está pronto para uma meta, seja honesto com base no volume e evolução observados.
4. Se perguntar sobre o próximo treino, recomende com base na recuperação e no princípio da supercompensação.
5. Mantenha tom motivador, profissional e esportivo.
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

    perf_plano = get_athlete_profile()
    esportes_plano = perf_plano.get("esportes_ativos", ["🏃 Corrida de Rua & Maratona"])
    tem_triatlo = any("Triatlo" in s for s in esportes_plano)
    tem_coletivo = any(any(c in s for c in ["Futebol", "Basquete", "Vôlei"]) for s in esportes_plano)
    tem_multi = len(esportes_plano) > 1

    opcoes_modalidades = [
        "🌐 Rotina Multi-Esportes Integrada (Corrida, Bike, Natação, Futebol, Força, etc.)",
        "🏃 Corrida de Rua & Maratona (Foco Específico em Corrida)",
        "🏊🚴🏃 Especialista em Triatlo (Swim, Bike & Run + Transição Brick)",
        "⚽ Esportes Coletivos & Condicionamento (Futebol, Basquete ou Vôlei + Físico)",
    ]

    if tem_triatlo:
        default_mod_idx = 2
    elif tem_multi:
        default_mod_idx = 0
    elif tem_coletivo:
        default_mod_idx = 3
    else:
        default_mod_idx = 1

    tipo_modalidade = st.radio(
        "🏅 Modalidade / Arquitetura do Planejamento:",
        opcoes_modalidades,
        index=default_mod_idx,
        horizontal=True,
        help="Escolha o foco da semana: 'Multi-Esportes' integra suas várias modalidades; 'Corrida' foca em km/pace; 'Triatlo' periodiza swim-bike-run; 'Coletivos' protege contra lesões de futebol/basquete/vôlei.",
    )

    col_p1, col_p2 = st.columns([1, 1], gap="large")

    with col_p1:
        if "Multi-Esportes" in tipo_modalidade:
            esportes_selecionados = st.multiselect(
                "🏅 Modalidades incluídas no seu microciclo:",
                options=ESPORTES_OPCOES,
                default=[e for e in esportes_plano if e in ESPORTES_OPCOES] or [ESPORTES_OPCOES[0]],
                help="Selecione todos os esportes que você planeja praticar ou intercalar nesta semana.",
            )
            objetivo_selecionado = st.selectbox(
                "🎯 Qual é o foco da sua semana multi-esportes?",
                options=[
                    "⚡ Equilíbrio Global: Resistência Aeróbica + Força Funcional Sem Sobrecarga",
                    "🏃 Prioridade Corrida com Manutenção das Outras Modalidades",
                    "🚴 Prioridade Ciclismo / Bike com Treinos Cruzados de Suporte",
                    "⚽ Preservação Muscular e Condicionamento para Jogos Coletivos",
                    "🏋️ Ênfase em Fortalecimento e Prevenção de Lesões com Base Z2 Leve",
                    "⚖️ Condicionamento Físico Geral e Queima Calórica Multi-Atividades",
                ],
                help="O foco principal orientará como a IA distribui as cargas entre as modalidades.",
            )
            dias_semana = st.slider(
                "📅 Quantos dias da semana você deseja realizar atividades?",
                min_value=3,
                max_value=7,
                value=int(perf_plano.get("dias_disponiveis", 4) or 4),
                help="Soma de todos os dias com treinos ou partidas.",
            )
            dia_chave_coletivo = st.selectbox(
                "⚽/🚴 Dia do jogo coletivo, pedal longo ou treino mais exigente:",
                options=["Não tenho dia fixo", "Quarta-feira", "Sábado", "Domingo", "Terça-feira", "Quinta-feira", "Sexta-feira", "Segunda-feira"],
                help="O Coach colocará recuperação ativa ou descanso no dia seguinte a este esforço para evitar lesões.",
            )
            dia_longao = dia_chave_coletivo

        elif "Coletivos" in tipo_modalidade:
            esporte_coletivo = st.selectbox(
                "⚽ Qual seu esporte coletivo principal?",
                options=[
                    "⚽ Futebol (Society / Campo / Futsal)",
                    "🏀 Basquete (Quadra / Meia Quadra)",
                    "🏐 Vôlei (Quadra / Areia / Futevôlei)",
                ],
                help="A modalidade coletiva gera alta fadiga excêntrica (sprints, freadas e saltos).",
            )
            dia_jogo = st.selectbox(
                "🗓️ Dia do seu jogo / partida principal na semana:",
                options=["Quarta-feira", "Sábado", "Domingo", "Terça-feira", "Quinta-feira", "Sexta-feira", "Segunda-feira"],
                help="O Coach calibrará a intensidade da semana para que você chegue 100% no dia do jogo!",
            )
            objetivo_selecionado = st.selectbox(
                "🎯 Qual é o seu objetivo de preparação física?",
                options=[
                    "⚡ Fôlego e Resistência: aguentar o jogo todo em alta intensidade sem cansar no final",
                    "🚀 Explosão e Agilidade: tiros curtos mais rápidos e recuperação acelerada entre lances",
                    "🛡️ Prevenção de Lesões: blindar adutores (pubalgia), isquiotibiais e joelhos",
                    "🫀 Condicionamento Geral: intercalar corridas moderadas com o jogo semanal",
                ],
            )
            esportes_selecionados = [esporte_coletivo, "🏃 Corrida de Rua & Maratona", "🏋️ Musculação / Fortalecimento"]
            dias_semana = st.slider(
                "📅 Quantos dias no total (jogo + treinos físicos de corrida/força)?",
                min_value=3,
                max_value=6,
                value=4,
                help="Recomendado: 1 dia de jogo + 2 a 3 dias de treinos físicos/mobilidade.",
            )
            dia_longao = dia_jogo

        elif "Triatlo" in tipo_modalidade:
            objetivo_selecionado = st.selectbox(
                "🎯 Qual é a sua meta / distância de Triatlo?",
                options=[
                    "🏊🚴🏃 Triatlo Sprint (750m Natação / 20km Ciclismo / 5km Corrida)",
                    "🏊🚴🏃 Triatlo Olímpico / Standard (1.5km Natação / 40km Ciclismo / 10km Corrida)",
                    "🏊🚴🏃 Meio Ironman 70.3 (1.9km Natação / 90km Ciclismo / 21.1km Corrida)",
                    "🏊🚴🏃 Ironman Completo 140.6 (3.8km Natação / 180km Ciclismo / 42.2km Corrida)",
                    "🏊🚴🏃 Condicionamento Multiesporte & Base Aeróbica Tri",
                ],
                help="Distância da sua prova alvo: Sprint (curta e explosiva), Olímpico (padrão dos Jogos), 70.3 (Meio Ironman / 113 km total) ou 140.6 (Ironman / 226 km total).",
            )
            disciplinas_selecionadas = st.multiselect(
                "Disciplinas incluídas na sua rotina semanal:",
                options=["Natação", "Ciclismo", "Corrida", "Transição Brick (Bike + Run)"],
                default=["Natação", "Ciclismo", "Corrida", "Transição Brick (Bike + Run)"],
                help="Escolha quais esportes você quer na semana. 'Brick' é o treino de pedalar e sair correndo logo em seguida para adaptar as pernas.",
            )
            esportes_selecionados = ["🏊 Natação", "🚴 Ciclismo / Bike", "🏃 Corrida de Rua & Maratona"]
            dias_semana = st.slider(
                "📅 Quantas sessões de treino você deseja realizar na semana?",
                min_value=4,
                max_value=7,
                value=6,
                help="No triatlo, treinar de 5 a 6 dias intercalando modalidades preserva as articulações da corrida.",
            )
            dia_longao = st.selectbox(
                "🚴 Qual o seu dia preferido para o treino longo (Bike longa ou Brick)?",
                options=["Sábado", "Domingo", "Outro dia da semana"],
                help="'Longão': o treino com maior tempo ou distância da semana (geralmente o pedal longo no final de semana).",
            )

        else: # Corrida de Rua & Maratona
            objetivo_selecionado = st.selectbox(
                "🎯 Qual é o seu objetivo principal de Corrida?",
                options=[
                    "🏃 Estreia em Meia Maratona (21.1 km)",
                    "🏅 Sub 50 minutos nos 10 km",
                    "⚡ Recorde Pessoal nos 5 km",
                    "🏆 Preparação Completa para Maratona (42.2 km)",
                    "🫀 Construção Sólida de Base Aeróbica (Zona 2)",
                    "⚖️ Condicionamento Geral & Emagrecimento Saudável",
                ],
                help="Meta esportiva principal para o treinador dosar o volume (km) e a intensidade (pace) da semana.",
            )
            disciplinas_selecionadas = ["Corrida"]
            esportes_selecionados = ["🏃 Corrida de Rua & Maratona"]
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
                help="'Longão': a corrida com maior quilometragem da semana, feita em ritmo confortável (Zona 2) para construir resistência.",
            )

    with col_p2:
        ciclo_horizonte = st.selectbox(
            "⏳ Período do Planejamento:",
            options=[
                "Microciclo Imediato (Semana 1 / Próximos 7 dias)",
                "Bloco de Base Aeróbica & Fortalecimento (4 Semanas)",
                "Ciclo de Polimento Pré-Prova / Competição (2 Semanas)",
            ],
            help="Microciclo = prescrição detalhada dos próximos 7 dias. Bloco de Base = foco em construir fôlego aeróbico e resistência.",
        )

        obs_lesoes = st.text_area(
            "🩺 Observações Físicas, Dores Recentes ou Restrições:",
            placeholder="Ex: Jogo futebol na quarta-feira à noite; leve desconforto no tendão de Aquiles; preferência por pedalar no sábado; sem lesões graves.",
            height=125,
            help="Conte sobre dores musculares (canelite, joelho, adutores/pubalgia), dias em que não pode treinar ou se faz musculação.",
        )

        btn_gerar_plano = st.button(
            "🚀 Gerar Planilha de Treinos com Coach AI",
            type="primary",
            use_container_width=True,
            help="O Gemini 2.5 Flash vai analisar seu histórico real da planilha e estruturar os próximos 7 dias sob medida.",
        )

    if btn_gerar_plano:
        client = get_gemini_client()
        if not client:
            st.error("Chave de API do Gemini não configurada.")
        else:
            with st.status("📋 Construindo sua periodização personalizada com o Coach AI...", expanded=True) as status_plan:
                try:
                    status_plan.write("🔍 **Etapa 1/3:** Lendo histórico de treinos e calculando média de volume e paces...")
                    df_historico_plano, _ = load_workouts_data()
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

                    if "Multi-Esportes" in tipo_modalidade:
                        diretrizes_metodologia = f"""
MISSÃO ESPECIALIZADA: TREINADOR MESTRE MULTI-ESPORTES E FISIOLOGIA DO EXERCÍCIO:
Você é um Treinador de Elite especializado em periodização integrativa para atletas que praticam múltiplos esportes.
O atleta selecionou as seguintes modalidades para esta semana: {', '.join(esportes_selecionados)}.
Meta / Foco da Semana: {objetivo_selecionado}.
Frequência: {dias_semana} sessões ativas na semana. Os outros {7 - dias_semana} dias devem ser 'Descanso' ou 'Descanso Ativo / Recuperação'.
Dia Chave / Mais Exigente da Semana: {dia_longao}.

DIRETRIZES FUNDAMENTAIS DE PERIODIZAÇÃO MULTIESPORTES:
1. SINERGIA ENTRE MODALIDADES (TREINAMENTO CRUZADO):
   - Alterne dias de impacto articular no solo (corrida) com dias de baixo ou zero impacto (ciclismo, natação ou fortalecimento).
   - Use o Ciclismo (Zona 2) e Natação como aceleradores da recuperação ativa, estimulando a circulação sem estresse nos tendões.
2. GESTÃO DE DESGASTE NEUROMUSCULAR (FUTEBOL / BASQUETE / VÔLEI):
   - Se a semana incluir futebol, basquete ou vôlei, lembre que esses esportes geram alta sobrecarga excêntrica (freadas bruscas, sprints curtos e saltos).
   - O dia imediatamente após um jogo NUNCA deve ser treino de tiros de alta intensidade na corrida! Deve ser: Descanso, Soltura em Bike Z1 (giro leve 85-90 RPM), Natação solta ou Trote levíssimo Z1.
3. FORTALECIMENTO PREVENTIVO (MUSCULAÇÃO):
   - Prescreva exercícios funcionais de suporte (glúteo médio, core anti-rotação, adutores para evitar pubalgia, panturrilhas e mobilidade).
4. NOMENCLATURA E REGRAS DO ESQUEMA:
   - No campo 'tipo_treino', inicie OBRIGATORIAMENTE com o emoji da modalidade:
     '🏃 Corrida...', '🚴 Ciclismo...', '🏊 Natação...', '⚽ Futebol...', '🏀 Basquete...', '🏐 Vôlei...', '🏋️ Fortalecimento / Mobilidade...', '💤 Descanso...'.
   - No campo 'modalidade', preencha com: 'Corrida', 'Ciclismo', 'Natação', 'Futebol', 'Basquete', 'Vôlei', 'Musculação' ou 'Descanso'.
   - Para sessões que não têm quilometragem métrica (ex: futebol, basquete, musculação), preencha 'distancia_km' com 0.0 e 'duracao_min' com o tempo estimado (ex: 60.0 ou 90.0).
   - No campo 'pace_alvo', preencha de acordo com a modalidade (ex: '05:20/km' para corrida; 'Z2 85 RPM' para ciclismo; '01:55/100m' para natação; 'RPE 7-8 / Intensidade de Jogo' para coletivos; 'Força Funcional e Core' para musculação; ou 'Descanso').
"""
                    elif "Coletivos" in tipo_modalidade:
                        diretrizes_metodologia = f"""
MISSÃO ESPECIALIZADA: PREPARADOR FÍSICO DE ESPORTES COLETIVOS E RESISTÊNCIA:
Você é um Preparador Físico de Futebol, Basquete e Vôlei de alto rendimento.
O atleta joga {esporte_coletivo} e sua meta nesta semana é: {objetivo_selecionado}.
Dia da Partida Principal: {dia_longao}.
Frequência Semanal: {dias_semana} sessões no total (incluindo a partida e os treinos físicos).

DIRETRIZES DE PERIODIZAÇÃO:
1. Dia do Jogo ({dia_longao}): Dia de intensidade máxima competitiva (RPE 8-9).
2. Véspera do Jogo: Descanso ou treino levíssimo de ativação neural (mobilidade rápida, sem fadiga muscular).
3. Dia Seguinte ao Jogo: Recuperação ativa obrigatória (caminhada, pedal Z1 leve, soltura de pernas, sem impacto).
4. Meio de Semana: Treino intervalado de corrida focado em sprints com mudanças de direção (HIIT anaeróbico) + sessão de fortalecimento preventivo (ísquios, adutores/virilha, joelhos e tornozelos).
5. No campo 'tipo_treino', use emojis representativos ('⚽ Partida / Treino de Futebol', '🏀 Jogo de Basquete', '🏐 Partida de Vôlei', '🏃 Treino Físico / Tiros', '🏋️ Prevenção e Core', '💤 Recuperação Ativa').
6. No campo 'modalidade', use 'Futebol', 'Basquete', 'Vôlei', 'Corrida', 'Musculação' ou 'Descanso'.
7. Preencha 'distancia_km' com 0.0 para jogos ou musculação, e 'duracao_min' com o tempo previsto.
"""
                    elif "Triatlo" in tipo_modalidade:
                        diretrizes_metodologia = f"""
MISSÃO ESPECIALIZADA: TREINADOR DE TRIATLO / MULTIESPORTE (SWIM, BIKE & RUN):
Você é um Treinador de Triatlo certificado internacionalmente (Ironman / World Triathlon).
Elabore uma periodização semanal estruturada de 7 sessões focada no objetivo: {objetivo_selecionado}.
- Disciplinas autorizadas pelo atleta: {', '.join(disciplinas_selecionadas)}.
- Frequência: {dias_semana} sessões na semana. Os outros {7 - dias_semana} dias devem ser 'Descanso' ou 'Descanso Ativo / Recuperação'.
- Princípio do Treinamento Cruzado: alterne dias de impacto articular (corrida) com dias sem impacto (natação e ciclismo) para gerar grande adaptação cardiorrespiratória sem sobrecarga.
- Treino de Transição (Brick): caso selecionado, prescreva pelo menos 1 treino de Brick (Ciclismo + corrida imediata em ritmo de prova para adaptação neuromuscular com pernas pesadas).
- NATAÇÃO: Séries detalhadas com metragens exatas (ex: 300m aquec. + 8x100m ritmo c/ 20s desc. + 200m soltura). Pace alvo no formato mm:ss /100m.
- CICLISMO: Especifique quilometragem, tempo, cadência recomendada (ex: 85-95 RPM) e zonas de esforço (Z2 base, Z3 ritmo ou subidas).
- CORRIDA: Especifique quilometragem, aquecimento, ritmo (pace mm:ss /km) e RPE.
- No campo 'tipo_treino', comece OBRIGATORIAMENTE com o emoji da modalidade: '🏊 Natação', '🚴 Ciclismo', '🏃 Corrida', '🚴🏃 Transição Brick' ou '💤 Descanso'.
- No campo 'modalidade', preencha com 'Natação', 'Ciclismo', 'Corrida', 'Transição (Brick)' ou 'Descanso'.
"""
                    else:
                        diretrizes_metodologia = f"""
MISSÃO ESPECIALIZADA: TREINADOR DE CORRIDA DE RUA E MARATONAS:
Você é um Treinador de Corrida de elite aplicando Jack Daniels VDOT e periodização clássica.
Elabore uma planilha para as próximas 7 sessões com foco em {objetivo_selecionado}.
- Frequência Semanal: {dias_semana} dias de corrida (os outros {7 - dias_semana} dias devem ser 'Descanso' ou 'Descanso Ativo').
- Dia do Longão: {dia_longao}.
- No campo 'tipo_treino', comece com emoji (ex: '🏃 Rodagem Z2', '⚡ Intervalado VO2', '🏆 Longão Progressivo', '💤 Descanso').
- No campo 'modalidade', informe 'Corrida' ou 'Descanso'.
"""

                    prompt_plano = f"""{diretrizes_metodologia}

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
- Tipo de Planejamento: {tipo_modalidade}
- Modalidades Selecionadas: {', '.join(esportes_selecionados)}
- Foco / Meta: {objetivo_selecionado}
- Frequência Semanal: {dias_semana} dias
- Dia do Treino Chave / Longo / Jogo: {dia_longao}
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
            if d.distancia_km > 0:
                dist_label = f"📏 {d.distancia_km:.1f} km"
            elif any(k in str(d.tipo_treino) for k in ["Futebol", "Basquete", "Vôlei", "⚽", "🏀", "🏐"]):
                dist_label = "⚽ Partida / Treino de Quadra"
            elif any(k in str(d.tipo_treino) for k in ["Musculação", "Fortalecimento", "Força", "🏋️"]):
                dist_label = "🏋️ Fortalecimento / Mobilidade"
            else:
                dist_label = "💤 Descanso / Recuperação Ativa"

            dur_label = f"⏳ {d.duracao_min:.0f} min" if d.duracao_min > 0 else ""
            header_pill = f"{dist_label} • {dur_label}" if dur_label else dist_label

            with st.expander(f"{d.dia_semana} ({d.data_prevista}) — {d.tipo_treino} ({header_pill})", expanded=True):
                col_d1, col_d2, col_d3 = st.columns([1.6, 1, 1])
                with col_d1:
                    st.markdown(f"**Ritmo / Intensidade Alvo:** `{d.pace_alvo}`")
                with col_d2:
                    st.markdown(f"**RPE Alvo:** `{d.rpe_alvo}/10`")
                with col_d3:
                    st.markdown(f"**Modalidade:** `{d.modalidade}`")
                st.markdown(f"**Estrutura da Sessão:**<br>{d.estrutura_treino.replace(chr(10), '<br>')}", unsafe_allow_html=True)

        substituir_existente = st.checkbox(
            "Substituir cronograma atual (limpar treinos antigos antes de salvar)",
            value=True,
            help="Se marcado, limpa as sessões antigas da aba 'Cronograma' e grava os novos 7 dias prescritos.",
        )

        col_save_crono, col_dl_crono = st.columns([1.5, 1])
        with col_save_crono:
            if st.button("💾 Sincronizar esta Planilha com meu Cronograma", type="primary", use_container_width=True):
                with st.spinner("Gravando as 7 sessões no Cronograma..."):
                    if substituir_existente:
                        clear_cronograma_data()
                    sucesso_sync, msg_sync = save_weekly_plan_data(plano)
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

# ------------------------------------------------------------------------------
# ABA 5: AJUDA, GUIA DO ATLETA & GLOSSÁRIO
# ------------------------------------------------------------------------------
with tab_ajuda:
    st.markdown("### ❓ Central de Ajuda & Glossário do Atleta")
    st.write("Tudo o que você precisa saber para transformar o Coach em app no celular, entender os jargões e aproveitar ao máximo.")

    tab_guia_mobile, tab_glossario_completo = st.tabs([
        "📲 Como Usar no Celular",
        "📖 Dicionário de Corrida & Triatlo",
    ])

    with tab_guia_mobile:
        st.markdown(
            """
            #### 📲 Como transformar em app no seu celular:
            - **No iPhone (Safari):** Toque no ícone de compartilhar (quadrado com seta) e selecione **"Adicionar à Tela de Início"**.
            - **No Android (Chrome):** Toque nos 3 pontinhos no canto superior e selecione **"Adicionar à tela inicial"** ou **"Instalar aplicativo"**.

            ---
            #### 🏃 Rotina Rápida em 4 Passos:
            1. **📅 Ver o Treino do Dia:** Logo na aba **"🏠 Meu Painel"**, confira o card do *Treino Atual* com ritmo, distância e estrutura.
            2. **✅ Fazer Check-in:** Terminou o treino? Dê 1 clique no botão **"✅ Marcar como Feito"** para atualizar sua planilha.
            3. **📸 Subir o Print:** Clique no botão superior **"📸 Registrar Treino com Print"** para que a IA analise ritmo, FC e dê o parecer.
            4. **💬 Conversar com o Coach:** Clique em **"💬 Conversar com o Coach AI"** para tirar dúvidas sobre dores, ritmo e alimentação.

            ---
            #### ⚠️ Dicas e Limites do Sistema:
            - **Prints nítidos:** O print do Garmin, Strava ou Polar deve mostrar claramente distância, tempo e pace médio.
            - **Atualização rápida:** O sistema sincroniza a cada 60s; use o botão **🔄 Atualizar** caso tenha editado a planilha externamente.
            - **Saúde em 1º lugar:** O Coach AI é um assistente de treinamento; dores agudas persistentes exigem avaliação de um fisioterapeuta ou médico.
            """
        )

    with tab_glossario_completo:
        st.markdown(
            """
            #### 🏃 Termos Essenciais da Corrida:
            - **Pace (Ritmo):** Tempo gasto para percorrer **1 quilômetro** (formato mm:ss /km).  
              *Exemplo:* Pace de `05:30/km` significa 5 minutos e 30 segundos por km. **Quanto menor o número, mais rápido você correu!**
            - **RPE (Escala de Borg / Percepção de Esforço):** Nota de **1 a 10** de cansaço:  
              *1:* Muito leve | *3:* Zona 2 aeróbica confortável | *5:* Ritmo de Maratona | *7-8:* Forte / Limiar | *10:* Exaustão máxima.
            - **FC (Frequência Cardíaca) & BPM:** Batimentos Por Minuto do seu coração captados pelo relógio ou cinta.
            - **Longão (Long Run):** Treino com maior distância da semana (geralmente domingo), focado em resistência pura em Zona 2.
            - **Tiros / Intervalado:** Séries de alta velocidade intercaladas com descanso ativo ou parado para aumentar VO2 Máx.
            - **Fartlek:** Treino contínuo com variações livres de velocidade em percurso variado.

            ---
            #### ❤️ Zonas de Frequência Cardíaca (Z1 a Z5):
            - **Z1 (Regenerativo):** Trote levíssimo pós-treino forte ou descanso ativo.
            - **Z2 (Base Aeróbica pura):** Ritmo conversacional, respiração fácil. Constrói a rede mitocondrial e queima gordura.
            - **Z3 (Ritmo / Tempo Run):** Ritmo de prova de Meia Maratona ou Maratona. Moderado-firme contínuo.
            - **Z4 (Limiar de Lactato / Threshold):** Ritmo forte sustentável por 30 a 60 min. Respiração pesada.
            - **Z5 (VO2 Máx / Anaeróbico):** Esforço máximo para tiros curtos e explosivos.

            ---
            #### 🏊🚴🏃 Termos de Triatlo (Multiesporte):
            - **Brick (Transição):** Treino que combina Ciclismo forte seguido imediatamente de Corrida para ensinar o corpo a correr com "pernas de chumbo".
            - **Cadência (RPM / SpM):**
              - *Corrida:* Passos por minuto (ideal entre 165 e 180 passos/min).
              - *Ciclismo:* Giros do pedal por minuto (ideal entre 85 e 95 RPM).
            - **Distâncias de Provas de Triatlo:**
              - *Sprint:* 750m Natação + 20km Ciclismo + 5km Corrida.
              - *Olímpico / Standard:* 1.500m Natação + 40km Ciclismo + 10km Corrida.
              - *Meio Ironman (70.3):* 1,9km Natação + 90km Ciclismo + 21,1km Corrida (113 km total).
              - *Ironman Completo (140.6):* 3,8km Natação + 180km Ciclismo + 42,2km Corrida (226 km total).
            """
        )
