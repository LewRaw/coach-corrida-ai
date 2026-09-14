"""
Módulo de Configuração, Schemas e Constantes Globais
Coach AI - Assessoria Esportiva Multi-Esportes
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import streamlit as st
import os


# ==============================================================================
# SCHEMAS PYDANTIC PARA SAÍDAS ESTRUTURADAS (GOOGLE GENAI SDK)
# ==============================================================================
class TreinoExtracao(BaseModel):
    distancia_km: float = Field(
        description="Distância total percorrida em quilômetros (ex: 10.5). Se não aplicável, 0.0"
    )
    tempo_min: float = Field(
        description="Duração total da atividade convertida estritamente em minutos decimais (ex: 52 min e 30 seg = 52.5)"
    )
    pace_medio: str = Field(
        description="Ritmo médio no formato mm:ss (ex: '05:15'). Para outras modalidades, velocidade média (ex: '25.4 km/h') ou 'N/A'"
    )
    fc_media: int = Field(
        description="Frequência cardíaca média em bpm. Se não detectada no print, retorne 0"
    )
    zona_predominante: str = Field(
        description="Zona de esforço predominante: 'Z1 Regenerativo', 'Z2 Rodagem Aeróbica', 'Z3 Tempo/Maratona', 'Z4 Limiar', ou 'Z5 VO2 Máx'"
    )
    modalidade: str = Field(
        description="Modalidade identificada: 'Corrida', 'Ciclismo', 'Natação', 'Futebol', 'Musculação', ou 'Outro'"
    )
    parecer_treinador: str = Field(
        description="Parecer técnico de consultoria de alto nível contendo: Diagnóstico do Treino, Intensidade Cardíaca e Próximo Passo. Sem usar caracteres '<' ou '>'"
    )


class TreinoDiarioPrescrito(BaseModel):
    dia_semana: str = Field(
        description="Nome do dia da semana (ex: 'Segunda-feira', 'Terça-feira', etc.)"
    )
    data_prevista: str = Field(
        description="Data prevista para a sessão estritamente no formato DD/MM/AAAA"
    )
    tipo_treino: str = Field(
        description="Nome técnico do treino (ex: 'Rodagem Z2', 'Intervalado VO2', 'Soltura Bike Z1', 'Partida Coletiva', 'Descanso')"
    )
    distancia_km: float = Field(
        description="Distância alvo em km. Para esportes coletivos, descanso ou musculação, preencha 0.0"
    )
    duracao_min: float = Field(
        description="Duração estimada em minutos da sessão (ex: 50.0 ou 60.0)"
    )
    pace_alvo: str = Field(
        description="Faixa de ritmo ou intensidade (ex: '05:30 a 05:45/km', 'Z2 85-90 RPM', 'RPE 7-8', 'Descanso')"
    )
    rpe_alvo: int = Field(
        description="Nota alvo na Escala de Borg (1 a 10). Ex: 3 para rodagem leve, 8 para tiros fortes, 1 para descanso"
    )
    modalidade: str = Field(
        description="Modalidade da sessão: 'Corrida', 'Ciclismo', 'Natação', 'Futebol', 'Basquete', 'Vôlei', 'Musculação', 'Transição', ou 'Descanso'"
    )
    estrutura_treino: str = Field(
        description="Prescrição detalhada do treino: Aquecimento, Parte Principal e Desaquecimento/Soltura"
    )


class PlanoSemanalPrescrito(BaseModel):
    titulo_ciclo: str = Field(
        description="Título motivador e técnico do microciclo (ex: 'Microciclo de Construção de Base Aeróbica - Semana 1')"
    )
    diagnostico_metodologia: str = Field(
        description="Explicação fisiológica da periodização adotada para esta semana com base no perfil e metas do atleta"
    )
    paces_referencia: str = Field(
        description="Resumo dos ritmos de referência: Z1 Regenerativo, Z2 Rodagem, Z3 Tempo Run, Z4/Z5 Limiar e Tiros"
    )
    dias: List[TreinoDiarioPrescrito] = Field(
        description="Lista com os 7 dias completos da semana"
    )
    orientacoes_gerais: str = Field(
        description="Orientações essenciais de recuperação, hidratação, sono e prevenção de lesões para esta semana"
    )


# ==============================================================================
# CONSTANTES DE TABELAS E COLUNAS
# ==============================================================================
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

ESPORTES_OPCOES = [
    "Corrida de Rua",
    "Ciclismo / Bike",
    "Natação",
    "Futebol",
    "Especialista em Triatlo",
    "Basquete",
    "Vôlei",
    "Musculação / Fortalecimento",
]


# ==============================================================================
# INSTRUÇÃO DO SISTEMA DO TREINADOR (COACH SYSTEM PROMPT)
# ==============================================================================
COACH_SYSTEM_INSTRUCTION = """
Você é um Treinador Chefe de Corrida de Rua, Triatlo e Multiesporte de elite com mais de 20 anos de experiência na preparação de atletas amadores e competitivos.
Sua comunicação é direta, motivadora, técnica e sem rodeios.
Ao analisar a imagem (print do Garmin Connect, Strava, Polar, Coros ou Apple Fitness):
1. Extraia meticulosamente os números: distância (km), tempo total (min), ritmo médio (pace mm:ss) e frequência cardíaca média (FC em bpm).
2. Identifique a modalidade da atividade (Corrida, Ciclismo, Natação ou Multiesporte/Força).
3. Analise a correlação entre os dados da imagem, a Percepção Subjetiva de Esforço (RPE na escala de Borg 1-10) e os comentários do atleta.
4. Elabore um parecer técnico do treinador estruturado em três tópicos claros:
   - Diagnóstico do Treino: Análise objetiva da execução em relação ao volume, ritmo/intensidade e modalidade.
   - Intensidade Cardíaca: Avaliação da resposta fisiológica, zonas de esforço e eficiência cardiovascular.
   - Próximo Passo: Orientação prática e prescritiva para a sessão seguinte (ex: descanso, rodagem regenerativa Z1/Z2, soltura em bike/natação ou mobilidade/musculação).
5. REGRA DE FORMATAÇÃO: NUNCA utilize caracteres '<' ou '>' no parecer técnico ou em qualquer campo descritivo (ex: nunca escreva '<Z2' ou '<5:30'). Em vez disso, use palavras como 'abaixo de', 'até' ou 'menor que'.
Responda ESTRITAMENTE em conformidade com o esquema JSON solicitado.
"""


# ==============================================================================
# FUNÇÕES UTILITÁRIAS
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


from collections.abc import Mapping


def get_secret_val(key: str, default: Any = None) -> Any:
    """Busca chave primeiro em st.secrets (inclusive seções aninhadas), depois em os.environ."""
    target_lower = key.lower()

    def search_mapping(m: Any) -> Any:
        if isinstance(m, Mapping):
            for k, v in m.items():
                if str(k).lower() == target_lower and v is not None:
                    return v
            for v in m.values():
                res = search_mapping(v)
                if res is not None:
                    return res
        return None

    try:
        val = search_mapping(st.secrets)
        if val is not None:
            return val
    except Exception:
        pass

    for env_k, env_v in os.environ.items():
        if env_k.lower() == target_lower and env_v is not None:
            return env_v

    return default
