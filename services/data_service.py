"""
Camada Unificada de Dados e Persistência
Supabase PostgreSQL (SaaS Multi-tenant) + Fallback Google Sheets
"""

from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime
import time
import uuid
import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

from config import (
    SHEET_COLUMNS,
    CRONOGRAMA_COLUMNS,
    TreinoExtracao,
    PlanoSemanalPrescrito,
    parse_float_br,
    get_secret_val,
)
from services.auth_service import (
    get_current_user_id,
    get_supabase_client,
    get_supabase_admin,
)


# ==============================================================================
# OPERAÇÕES DE DADOS NO SUPABASE
# ==============================================================================
def load_workouts_from_supabase(user_id: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega os treinos do atleta logado diretamente do Supabase PostgreSQL."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return None, "Serviço de dados não conectado."
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
        return None, f"Erro ao consultar histórico: {str(e)}"


def append_workout_to_supabase(
    analysis: TreinoExtracao,
    rpe: int,
    user_notes: str,
    user_id: str,
) -> Tuple[bool, str]:
    """Salva com segurança uma nova atividade no Supabase vinculada ao user_id."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return False, "Serviço de dados não configurado."
    try:
        now_dt = datetime.now()
        payload = {
            "user_id": user_id,
            "data": now_dt.strftime("%d/%m/%Y"),
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
        return True, "Treino registrado com sucesso na nuvem!"
    except Exception as e:
        return False, f"Erro ao gravar atividade: {str(e)}"


def load_cronograma_from_supabase(user_id: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega o cronograma do atleta logado a partir do Supabase."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return None, "Serviço de dados não conectado."
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
        return None, f"Erro ao carregar Cronograma: {str(e)}"


def mark_workout_as_completed_supabase(workout_id: str, user_id: str) -> Tuple[bool, str]:
    """Marca o treino como Concluído no Supabase."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return False, "Serviço de dados não configurado."
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sb.table("schedules").update({
            "status": "Concluído",
            "data_conclusao": now_str,
        }).eq("id", workout_id).eq("user_id", user_id).execute()
        st.cache_data.clear()
        return True, "Treino marcado como Concluído com sucesso!"
    except Exception as e:
        return False, f"Erro ao marcar treino como concluído: {str(e)}"


def save_weekly_plan_to_supabase(plano: PlanoSemanalPrescrito, user_id: str) -> Tuple[bool, str]:
    """Salva os 7 dias gerados da planilha no Supabase com status 'Pendente'."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return False, "Serviço de dados não configurado."
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
        return True, f"Plano com {len(novas_linhas)} sessões sincronizado com sucesso!"
    except Exception as e:
        return False, f"Erro ao salvar plano: {str(e)}"


def clear_cronograma_in_supabase(user_id: str) -> Tuple[bool, str]:
    """Limpa todas as sessões agendadas do atleta no Supabase."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return False, "Serviço de dados não configurado."
    try:
        sb.table("schedules").delete().eq("user_id", user_id).execute()
        st.cache_data.clear()
        return True, "Cronograma limpo com sucesso!"
    except Exception as e:
        return False, f"Erro ao limpar cronograma: {str(e)}"


def delete_workout_from_supabase(workout_id: str, user_id: str) -> Tuple[bool, str]:
    """Remove uma sessão específica do cronograma no Supabase (pular treino)."""
    sb = get_supabase_admin() or get_supabase_client()
    if not sb:
        return False, "Serviço de dados não configurado."
    try:
        sb.table("schedules").delete().eq("id", workout_id).eq("user_id", user_id).execute()
        st.cache_data.clear()
        return True, "Sessão removida do planejamento."
    except Exception as e:
        return False, f"Erro ao remover sessão: {str(e)}"


# ==============================================================================
# CONTINGÊNCIA GOOGLE SHEETS
# ==============================================================================
def get_gspread_client() -> Optional[gspread.Client]:
    """Cria e autentica o cliente gspread via Service Account."""
    try:
        if "gcp_service_account" in st.secrets:
            sa_info = dict(st.secrets["gcp_service_account"])
        else:
            sa_json_path = get_secret_val("gcp_service_account_file")
            if sa_json_path and os.path.exists(sa_json_path):
                import json
                with open(sa_json_path, "r", encoding="utf-8") as f:
                    sa_info = json.load(f)
            else:
                return None

        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception:
        return None


def run_with_retry(func, max_retries: int = 3, base_delay: float = 2.0):
    """Executa uma chamada com recuo exponencial para tolerar falhas de rede."""
    last_ex = None
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_ex = e
            time.sleep(base_delay * (2 ** attempt))
    raise last_ex


def get_cached_worksheet(sheet_url: str, title: str) -> Optional[gspread.Worksheet]:
    """Obtém aba específica da planilha Google."""
    gc = get_gspread_client()
    if not gc:
        return None
    try:
        sh = run_with_retry(lambda: gc.open_by_url(sheet_url))
        try:
            return run_with_retry(lambda: sh.worksheet(title))
        except gspread.WorksheetNotFound:
            if title == "Treinos":
                ws = run_with_retry(lambda: sh.add_worksheet(title=title, rows=1000, cols=len(SHEET_COLUMNS)))
                run_with_retry(lambda: ws.append_row(SHEET_COLUMNS))
                return ws
            elif title == "Cronograma":
                ws = run_with_retry(lambda: sh.add_worksheet(title=title, rows=500, cols=len(CRONOGRAMA_COLUMNS)))
                run_with_retry(lambda: ws.append_row(CRONOGRAMA_COLUMNS))
                return ws
            raise
    except Exception:
        return None


def append_workout_to_sheets(
    analysis: TreinoExtracao,
    rpe: int,
    user_notes: str,
) -> Tuple[bool, str]:
    """Grava atividade no Google Sheets (fallback)."""
    sheet_url = get_secret_val("sheet_url")
    if not sheet_url:
        return False, "Planilha Google não configurada."
    try:
        ws = get_cached_worksheet(sheet_url, "Treinos")
        if not ws:
            return False, "Não foi possível acessar a aba 'Treinos'."

        nova_linha = [
            datetime.now().strftime("%d/%m/%Y"),
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
        return True, "Treino registrado com sucesso na planilha!"
    except Exception as e:
        return False, f"Erro ao gravar na planilha: {str(e)}"


@st.cache_data(ttl=60, show_spinner=False)
def _load_workouts_cached(sheet_url: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega as atividades da aba 'Treinos' mantendo cache por 60 segundos."""
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

        return df, None
    except Exception as e:
        return None, f"Erro ao consultar planilha: {str(e)}"


def load_workouts_from_sheets() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega as atividades concluídas da aba 'Treinos'."""
    sheet_url = get_secret_val("sheet_url")
    if not sheet_url:
        return None, "Configure 'sheet_url' para carregar histórico do Google Sheets."
    return _load_workouts_cached(sheet_url)


def load_cronograma_from_sheets() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega o cronograma a partir do Google Sheets."""
    sheet_url = get_secret_val("sheet_url")
    if not sheet_url:
        return None, "Configure 'sheet_url' para carregar cronograma."
    try:
        ws = get_cached_worksheet(sheet_url, "Cronograma")
        if not ws:
            return None, "Aba 'Cronograma' não encontrada."
        vals = run_with_retry(lambda: ws.get_all_values())
        if not vals or len(vals) <= 1:
            return pd.DataFrame(columns=CRONOGRAMA_COLUMNS), None
        headers = vals[0]
        rows = [r for r in vals[1:] if any(str(c).strip() for c in r)]
        df = pd.DataFrame(rows, columns=headers)
        return df, None
    except Exception as e:
        return None, f"Erro ao ler cronograma: {str(e)}"


def save_weekly_plan_to_sheets(plano: PlanoSemanalPrescrito) -> Tuple[bool, str]:
    """Salva os 7 dias na aba 'Cronograma' do Google Sheets."""
    sheet_url = get_secret_val("sheet_url")
    if not sheet_url:
        return False, "Planilha não configurada."
    try:
        ws = get_cached_worksheet(sheet_url, "Cronograma")
        if not ws:
            return False, "Aba 'Cronograma' não encontrada."

        novas_linhas = []
        for d in plano.dias:
            novas_linhas.append([
                f"TR-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
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
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ])
        run_with_retry(lambda: ws.append_rows(novas_linhas, value_input_option="USER_ENTERED"))
        st.cache_data.clear()
        return True, f"Plano com {len(novas_linhas)} sessões sincronizado com sucesso!"
    except Exception as e:
        return False, f"Erro ao salvar na planilha: {str(e)}"


def clear_cronograma_in_sheets() -> Tuple[bool, str]:
    """Limpa sessões agendadas na planilha."""
    sheet_url = get_secret_val("sheet_url")
    if not sheet_url:
        return False, "Planilha não configurada."
    try:
        ws = get_cached_worksheet(sheet_url, "Cronograma")
        if not ws:
            return False, "Aba não encontrada."
        run_with_retry(lambda: ws.clear())
        run_with_retry(lambda: ws.append_row(CRONOGRAMA_COLUMNS))
        st.cache_data.clear()
        return True, "Cronograma limpo com sucesso!"
    except Exception as e:
        return False, f"Erro ao limpar: {str(e)}"


def mark_workout_as_completed_sheets(workout_id: str) -> Tuple[bool, str]:
    """Marca treino como concluído na planilha."""
    sheet_url = get_secret_val("sheet_url")
    if not sheet_url:
        return False, "Planilha não configurada."
    try:
        ws = get_cached_worksheet(sheet_url, "Cronograma")
        if not ws:
            return False, "Aba não encontrada."
        vals = run_with_retry(lambda: ws.get_all_values())
        if not vals:
            return False, "Cronograma vazio."
        for idx, row in enumerate(vals[1:], start=2):
            if row and row[0] == workout_id:
                ws.update_cell(idx, 10, "Concluído")
                ws.update_cell(idx, 11, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                st.cache_data.clear()
                return True, "Treino marcado como Concluído!"
        return False, "Treino não encontrado."
    except Exception as e:
        return False, f"Erro ao atualizar: {str(e)}"


def delete_workout_from_sheets(workout_id: str) -> Tuple[bool, str]:
    """Remove uma sessão específica do cronograma no Google Sheets (pular treino)."""
    sheet_url = get_secret_val("sheet_url")
    if not sheet_url:
        return False, "Planilha não configurada."
    try:
        ws = get_cached_worksheet(sheet_url, "Cronograma")
        if not ws:
            return False, "Aba não encontrada."
        vals = run_with_retry(lambda: ws.get_all_values())
        if not vals:
            return False, "Cronograma vazio."
        for idx, row in enumerate(vals[1:], start=2):
            if row and row[0] == workout_id:
                ws.delete_rows(idx)
                st.cache_data.clear()
                return True, "Sessão removida do planejamento."
        return False, "Treino não encontrado."
    except Exception as e:
        return False, f"Erro ao remover: {str(e)}"


# ==============================================================================
# CAMADA DE DADOS UNIFICADA (ROTEAMENTE INTELIGENTE)
# ==============================================================================
def load_workouts_data() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Carrega treinos do atleta: Supabase (se logado) ou Google Sheets como fallback."""
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
    """Marca treino como concluído."""
    uid = get_current_user_id()
    if uid:
        return mark_workout_as_completed_supabase(workout_id, uid)
    return mark_workout_as_completed_sheets(workout_id)


def delete_workout_from_cronograma_data(workout_id: str) -> Tuple[bool, str]:
    """Remove uma sessão específica do cronograma (pular treino)."""
    uid = get_current_user_id()
    if uid:
        return delete_workout_from_supabase(workout_id, uid)
    return delete_workout_from_sheets(workout_id)


def save_weekly_plan_data(plano: PlanoSemanalPrescrito) -> Tuple[bool, str]:
    """Salva periodização semanal."""
    uid = get_current_user_id()
    if uid:
        return save_weekly_plan_to_supabase(plano, uid)
    return save_weekly_plan_to_sheets(plano)


def clear_cronograma_data() -> Tuple[bool, str]:
    """Limpa cronograma."""
    uid = get_current_user_id()
    if uid:
        return clear_cronograma_in_supabase(uid)
    return clear_cronograma_in_sheets()
