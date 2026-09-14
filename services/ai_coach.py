"""
Serviço de Inteligência Artificial do Coach AI
Google GenAI SDK (gemini-2.5-flash) + Structured Outputs + Prompts Especializados
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
import pandas as pd
import streamlit as st
from google import genai
from google.genai import types

from config import (
    TreinoExtracao,
    PlanoSemanalPrescrito,
    COACH_SYSTEM_INSTRUCTION,
    get_secret_val,
)
from services.auth_service import get_athlete_profile
from services.data_service import load_workouts_data


def get_gemini_client(api_key: Optional[str] = None) -> Optional[genai.Client]:
    """Inicializa o cliente oficial da biblioteca google-genai."""
    final_key = api_key or get_secret_val("GEMINI_API_KEY")
    if not final_key:
        return None
    try:
        return genai.Client(api_key=final_key)
    except Exception as e:
        st.error(f"Erro ao inicializar o cliente de Inteligência Artificial: {e}")
        return None


def format_athlete_history_for_prompt(df: Optional[pd.DataFrame]) -> str:
    """Gera um prontuário textual estruturado dos treinos do atleta para alimentar os prompts."""
    if df is None or df.empty:
        return "NENHUM TREINO REGISTRADO AINDA. Atleta iniciando agora a periodização."

    linhas_prontuario = [
        "=== PRONTUÁRIO HISTÓRICO REAL DO ATLETA ===",
        f"Total de Atividades Concluídas: {len(df)}",
    ]

    ultimos = df.tail(10)
    for idx, row in ultimos.iterrows():
        dt = row.get("Data", "N/D")
        dist = row.get("Distância (km)", 0.0)
        tempo = row.get("Tempo (min)", 0.0)
        pace = row.get("Pace Médio", "N/D")
        fc = row.get("FC Média (bpm)", "N/D")
        zona = row.get("Zona Predominante", "N/D")
        rpe = row.get("RPE (1-10)", "N/D")
        modalidade = row.get("Tipo de Treino", "Corrida")
        linhas_prontuario.append(
            f"- Data: {dt} | {modalidade} | Distância: {dist}km | Tempo: {tempo}min | "
            f"Pace: {pace} | FC Média: {fc} bpm | Zona: {zona} | RPE: {rpe}/10"
        )
    return "\n".join(linhas_prontuario)


def analyze_workout_image(
    image_bytes: bytes,
    mime_type: str,
    rpe: int,
    user_notes: str,
    gemini_client: genai.Client,
) -> TreinoExtracao:
    """Invoca o Gemini 2.5 Flash com schema estruturado para analisar print da atividade."""
    df_contexto, _ = load_workouts_data()
    historico_texto = format_athlete_history_for_prompt(df_contexto)
    perf_atleta = get_athlete_profile()
    esportes_praticados = ", ".join(perf_atleta.get("esportes_ativos", ["Corrida de Rua"]))

    prompt_usuario = (
        f"Analise minuciosamente este print de treino exportado de relógio ou aplicativo esportivo.\n\n"
        f"PERFIL DO ATLETA:\n"
        f"- Modalidades Praticadas: {esportes_praticados}\n"
        f"- Nível: {perf_atleta.get('nivel_experiencia', 'Intermediário')}\n"
        f"- Meta: {perf_atleta.get('objetivo_principal', 'Meia Maratona')}\n\n"
        f"INFORMAÇÕES FORNECIDAS PELO ATLETA SOBRE ESTA SESSÃO:\n"
        f"- Percepção Subjetiva de Esforço (RPE Borg): {rpe}/10\n"
        f"- Notas e sensações do atleta: {user_notes if user_notes.strip() else 'Nenhuma nota informada.'}\n\n"
        f"{historico_texto}\n\n"
        f"Compare este treino com as últimas sessões do atleta e elabore um parecer técnico objetivo, "
        f"avaliando a resposta cardíaca e a progressão sem utilizar caracteres '<' ou '>'."
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

    if hasattr(response, "parsed") and response.parsed:
        return response.parsed
    return TreinoExtracao(**json.loads(response.text))


def generate_weekly_plan(
    tipo_modalidade: str,
    esportes_selecionados: List[str],
    objetivo_selecionado: str,
    dias_semana: int,
    dia_longao: str,
    ciclo_horizonte: str,
    obs_lesoes: str,
    gemini_client: genai.Client,
) -> PlanoSemanalPrescrito:
    """Gera periodização personalizada determinística para os próximos 7 dias."""
    df_historico_plano, _ = load_workouts_data()
    historico_resumo = format_athlete_history_for_prompt(df_historico_plano)

    hoje = datetime.now()
    dias_nomes = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    datas_proximas = []
    for i in range(1, 8):
        dt = hoje + timedelta(days=i)
        nome_d = dias_nomes[dt.weekday()]
        datas_proximas.append(f"- Dia {i} ({nome_d}): {dt.strftime('%d/%m/%Y')}")
    calendario_datas_str = "\n".join(datas_proximas)

    if "Multi-Esportes" in tipo_modalidade:
        diretrizes_metodologia = f"""
MISSÃO: TREINADOR MESTRE MULTI-ESPORTES E FISIOLOGIA DO EXERCÍCIO:
Você é um Treinador de Elite especializado em periodização integrativa para atletas que praticam múltiplos esportes.
Modalidades selecionadas para esta semana: {', '.join(esportes_selecionados)}.
Meta / Foco da Semana: {objetivo_selecionado}.
Frequência: {dias_semana} sessões ativas na semana. Os outros {7 - dias_semana} dias devem ser 'Descanso' ou 'Descanso Ativo'.
Dia Chave / Mais Exigente da Semana: {dia_longao}.

DIRETRIZES:
1. Alterne dias de impacto articular (corrida) com dias de baixo ou zero impacto (bike, natação ou fortalecimento).
2. Se a semana incluir futebol, basquete ou vôlei, o dia imediatamente após o jogo NUNCA deve ser treino de tiros de corrida! Deve ser descanso ou soltura leve.
3. No campo 'modalidade', use: 'Corrida', 'Ciclismo', 'Natação', 'Futebol', 'Basquete', 'Vôlei', 'Musculação' ou 'Descanso'.
4. Para sessões sem metragem linear (jogos, musculação), informe 'distancia_km' como 0.0 e 'duracao_min' com a duração estimada.
"""
    elif "Coletivos" in tipo_modalidade:
        diretrizes_metodologia = f"""
MISSÃO: PREPARADOR FÍSICO DE ESPORTES COLETIVOS E RESISTÊNCIA:
Meta: {objetivo_selecionado}.
Dia da Partida Principal: {dia_longao}.
Frequência Semanal: {dias_semana} sessões no total (partida + treinos físicos).

DIRETRIZES:
1. Dia do Jogo ({dia_longao}): Intensidade máxima competitiva (RPE 8-9).
2. Véspera do Jogo: Descanso ou ativação neural leve.
3. Dia Seguinte ao Jogo: Recuperação ativa sem impacto (pedal leve, soltura de pernas ou caminhada).
4. No campo 'modalidade', use: 'Futebol', 'Basquete', 'Vôlei', 'Corrida', 'Musculação' ou 'Descanso'.
"""
    elif "Triatlo" in tipo_modalidade:
        diretrizes_metodologia = f"""
MISSÃO: TREINADOR DE TRIATLO / MULTIESPORTE:
Foco: {objetivo_selecionado}.
Disciplinas: {', '.join(esportes_selecionados)}.
Frequência: {dias_semana} sessões na semana. Os outros {7 - dias_semana} dias são 'Descanso' ou 'Recuperação Ativa'.
Dia Longo: {dia_longao}.
Alterne dias de impacto com dias de água e pedal. Se aplicável, prescreva 1 sessão de Transição Brick (Bike + Corrida imediata).
No campo 'modalidade', use: 'Natação', 'Ciclismo', 'Corrida', 'Transição' ou 'Descanso'.
"""
    else:
        diretrizes_metodologia = f"""
MISSÃO: TREINADOR DE CORRIDA DE RUA E MARATONAS:
Foco: {objetivo_selecionado}.
Frequência Semanal: {dias_semana} dias de corrida.
Dia do Longão: {dia_longao}.
No campo 'modalidade', use: 'Corrida' ou 'Descanso'.
"""

    prompt_plano = f"""{diretrizes_metodologia}

CONTEXTO TEMPORAL RIGOROSO:
- DATA ATUAL: {hoje.strftime('%d/%m/%Y')} (ANO CORRENTE: {hoje.year}).
- CALENDÁRIO OBRIGATÓRIO PARA AS PRÓXIMAS 7 SESSÕES FUTURAS ({hoje.year}):
{calendario_datas_str}

ATENÇÃO:
As datas previstas para cada um dos 7 dias DEVEM SER OBRIGATORIAMENTE as datas futuras listadas no calendário acima (Ano {hoje.year}).
NUNCA utilize datas passadas! O histórico serve estritamente para dosar volume e ritmo.

DADOS E HISTÓRICO DO ATLETA:
{historico_resumo}

PARÂMETROS DA SEMANA:
- Tipo: {tipo_modalidade}
- Modalidades: {', '.join(esportes_selecionados)}
- Foco: {objetivo_selecionado}
- Frequência: {dias_semana} dias
- Treino Chave: {dia_longao}
- Período: {ciclo_horizonte}
- Restrições: {obs_lesoes if obs_lesoes.strip() else 'Nenhuma restrição.'}

Forneça os 7 dias completos (utilizando estritamente as 7 datas futuras informadas acima) em formato JSON.
REGRA CRÍTICA DE FORMATAÇÃO: NUNCA utilize caracteres '<' ou '>' para indicar comparações, paces ou zonas (por exemplo, nunca escreva '<Z2' ou '<5:30'). Em vez disso, use palavras como 'abaixo de', 'até' ou 'menor que'.
"""

    resp_plano = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_plano,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=PlanoSemanalPrescrito,
            temperature=0.3,
        ),
    )

    if hasattr(resp_plano, "parsed") and resp_plano.parsed:
        return resp_plano.parsed
    return PlanoSemanalPrescrito(**json.loads(resp_plano.text))


def generate_coach_chat_response(
    messages: List[Dict[str, str]],
    gemini_client: genai.Client,
) -> str:
    """Gera resposta no chat do Coach AI com histórico e contexto do atleta."""
    df_contexto, _ = load_workouts_data()
    historico_texto = format_athlete_history_for_prompt(df_contexto)
    perf_chat = get_athlete_profile()
    esportes_chat = ", ".join(perf_chat.get("esportes_ativos", ["Corrida de Rua"]))

    chat_system_instruction = f"""Você é o Treinador Chefe de Corrida de Rua, Maratonas e Multiesporte do atleta.
PERFIL DO ATLETA:
- Modalidades Praticadas: {esportes_chat}
- Nível de Experiência: {perf_chat.get('nivel_experiencia', 'Intermediário')}
- Frequência Semanal: {perf_chat.get('dias_disponiveis', 4)} sessões por semana
- Meta Principal: {perf_chat.get('objetivo_principal', 'Meia Maratona')}

Você possui vasta experiência com corredores, triatletas e atletas multiesporte, aplicando fisiologia esportiva (treinamento cruzado, Jack Daniels VDOT, limiares de lactato e prevenção de sobrecargas articulares).
Sua missão é fornecer respostas técnicas, assertivas, motivadoras e personalizadas.

HISTÓRICO ATUALIZADO DO ATLETA:
{historico_texto}

DIRETRIZES:
1. Considere todos os esportes praticados ({esportes_chat}). Se o atleta mencionar futebol, basquete ou vôlei, lembre do alto estresse excêntrico nas pernas; se pedala ou nada, use como estímulo aeróbico regenerativo sem impacto.
2. Cite dados reais dos treinos do atleta (datas, volumes, FC e paces registrados).
3. Seja honesto e profissional.
4. REGRA DE FORMATAÇÃO: NUNCA utilize caracteres '<' ou '>' para indicar comparações, ritmos ou zonas. Use palavras como 'abaixo de', 'até' ou 'menor que'.
"""

    gemini_contents = []
    for m in messages[-8:]:
        role = "user" if m["role"] == "user" else "model"
        gemini_contents.append(f"{role.upper()}: {m['content']}")

    prompt_completo = (
        f"{chat_system_instruction}\n\n"
        f"DIÁLOGO RECENTE:\n" + "\n".join(gemini_contents) + "\n\n"
        f"RESPONDA DIRETAMENTE AO ATLETA:"
    )

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_completo,
        config=types.GenerateContentConfig(
            temperature=0.4,
        ),
    )
    return response.text
