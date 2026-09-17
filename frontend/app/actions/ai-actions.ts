'use server';

import { GoogleGenerativeAI } from '@google/generative-ai';
import { getProfile, getWorkouts, supabase } from '@/lib/supabase';
import { Schedule, Workout, Profile } from '@/lib/types';

// Initialize SDK with fallback to ensure it always works
function getGenAI() {
  const apiKey =
    process.env.GEMINI_API_KEY ||
    process.env.NEXT_PUBLIC_GEMINI_API_KEY ||
    'AIzaSyAdLmksR76TQF1xgFHhQuv_-iskrawjH5I';
  return new GoogleGenerativeAI(apiKey);
}

function formatAthleteHistory(workouts: Workout[]): string {
  if (!workouts || workouts.length === 0) {
    return 'NENHUM TREINO REGISTRADO AINDA. Atleta iniciando agora a periodização.';
  }

  const linhas = [
    '=== PRONTUÁRIO HISTÓRICO REAL DO ATLETA ===',
    `Total de Atividades Concluídas: ${workouts.length}`,
  ];

  const ultimos = workouts.slice(0, 10);
  ultimos.forEach((row) => {
    const dt = row.data || 'N/D';
    const dist = row.distancia_km || 0.0;
    const tempo = row.tempo_min || 0.0;
    const pace = row.pace_medio || 'N/D';
    const fc = row.fc_media || 'N/D';
    const zona = row.zona_predominante || 'N/D';
    const rpe = row.rpe || 'N/D';
    linhas.push(
      `- Data: ${dt} | Distância: ${dist}km | Tempo: ${tempo}min | Pace: ${pace} | FC Média: ${fc} bpm | Zona: ${zona} | RPE: ${rpe}/10`
    );
  });
  return linhas.join('\n');
}

export async function chatWithCoach(userId: string, messages: { role: string; content: string }[]) {
  try {
    let profile: Profile | null = null;
    let workouts: Workout[] = [];

    if (userId && !userId.startsWith('demo-')) {
      try {
        profile = await getProfile(userId);
        workouts = await getWorkouts(userId);
      } catch (err) {
        console.warn('DB fetch in chatWithCoach fallback:', err);
      }
    }

    const historicoTexto = formatAthleteHistory(workouts);
    const esportesChat = profile?.esportes_ativos?.join(', ') || 'Corrida de Rua';
    const nivel = profile?.nivel_experiencia || 'Intermediário';
    const meta = profile?.objetivo_principal || 'Melhorar Condicionamento';
    const freq = profile?.dias_disponiveis || 4;

    const chatSystemInstruction = `Você é o Treinador Chefe de Corrida de Rua, Maratonas e Multiesporte do atleta.
PERFIL DO ATLETA:
- Modalidades Praticadas: ${esportesChat}
- Nível de Experiência: ${nivel}
- Frequência Semanal: ${freq} sessões por semana
- Meta Principal: ${meta}

Você possui vasta experiência com corredores, triatletas e atletas multiesporte.
Sua missão é fornecer respostas técnicas, assertivas, motivadoras e personalizadas em português.

HISTÓRICO ATUALIZADO DO ATLETA:
${historicoTexto}

DIRETRIZES:
1. Responda de forma empática, profissional e direta ao atleta.
2. NUNCA utilize caracteres '<' ou '>' para comparações ou ritmos (use palavras como 'abaixo de' ou 'até').
`;

    const genAI = getGenAI();
    const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });

    // Format full dialog like Python version to avoid chat history role alternation crashes
    const dialogLines = messages.slice(-10).map((m) => {
      const speaker = m.role === 'user' ? 'ATLETA' : 'TREINADOR';
      return `${speaker}: ${m.content}`;
    });

    const fullPrompt = `${chatSystemInstruction}

DIÁLOGO ATÉ O MOMENTO:
${dialogLines.join('\n')}

RESPONDA DIRETAMENTE AO ATLETA (como o Treinador):`;

    const result = await model.generateContent(fullPrompt);
    const text = result.response.text();
    return { success: true, text };
  } catch (error: any) {
    console.error('Chat error:', error);
    return { success: false, error: error?.message || 'Erro ao processar mensagem com a IA' };
  }
}

export async function generateWeeklyPlanAction(userId: string, tipoModalidade: string, diasSemana: number) {
  try {
    let profile: Profile | null = null;
    let workouts: Workout[] = [];

    if (userId && !userId.startsWith('demo-')) {
      try {
        profile = await getProfile(userId);
        workouts = await getWorkouts(userId);
      } catch (err) {
        console.warn('DB fetch in generateWeeklyPlan fallback:', err);
      }
    }

    const esportes = profile?.esportes_ativos || ['Corrida de Rua'];
    const objetivo = profile?.objetivo_principal || 'Meia Maratona';
    const diaLongao = 'Sábado';
    const historicoResumo = formatAthleteHistory(workouts);

    const hoje = new Date();
    const diasNomes = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado'];

    let calendarioDatasStr = '';
    for (let i = 1; i <= 7; i++) {
      const dt = new Date(hoje);
      dt.setDate(hoje.getDate() + i);
      const nomeD = diasNomes[dt.getDay()];
      const diaFormatado = dt.toLocaleDateString('pt-BR');
      calendarioDatasStr += `- Dia ${i} (${nomeD}): ${diaFormatado}\n`;
    }

    const promptPlano = `Você é um Treinador de Elite.
Gere uma periodização para os próximos 7 dias no formato JSON.
Foco da semana: ${objetivo}
Frequência: ${diasSemana} dias ativos. Outros dias: 'Descanso' ou 'Descanso Ativo'.
Dia Chave: ${diaLongao}
Modalidades: ${esportes.join(', ')}

CALENDÁRIO FUTURO OBRIGATÓRIO:
${calendarioDatasStr}

HISTÓRICO DO ATLETA:
${historicoResumo}

Retorne um array JSON com exatamente 7 objetos (um para cada dia), cada um contendo:
- "dia_semana": string (ex: "Segunda-feira")
- "data_prevista": string (formato DD/MM/AAAA)
- "tipo_treino": string (ex: "Rodagem Z2", "Intervalado 6x800m", "Descanso")
- "distancia_km": number (ex: 8.0, 0 para descanso)
- "duracao_min": number (ex: 45)
- "pace_alvo": string (ex: "05:20 a 05:35/km", ou "Descanso")
- "rpe_alvo": number (1 a 10)
- "estrutura_treino": string (detalhes de aquecimento, principal e desaquecimento)

NUNCA use caracteres '<' ou '>'.`;

    const genAI = getGenAI();
    const model = genAI.getGenerativeModel({
      model: 'gemini-2.5-flash',
      generationConfig: { responseMimeType: 'application/json' },
    });

    const result = await model.generateContent(promptPlano);
    const prescricao = JSON.parse(result.response.text());

    // Se o usuário estiver autenticado e não for demo, salva no Supabase
    if (userId && !userId.startsWith('demo-')) {
      try {
        await supabase.from('schedules').delete().eq('user_id', userId).eq('status', 'Pendente');

        const insertData = prescricao.map((item: any) => ({
          user_id: userId,
          dia_semana: item.dia_semana || 'Treino',
          data_prevista: item.data_prevista || '',
          tipo_treino: item.tipo_treino || 'Rodagem',
          distancia_km: Number(item.distancia_km) || 0,
          duracao_min: Number(item.duracao_min) || 0,
          pace_alvo: String(item.pace_alvo || ''),
          rpe_alvo: Number(item.rpe_alvo) || 5,
          estrutura_treino: String(item.estrutura_treino || ''),
          status: 'Pendente',
        }));

        await supabase.from('schedules').insert(insertData);
      } catch (dbErr) {
        console.error('Database schedule insert error:', dbErr);
      }
    }

    return { success: true, prescricao };
  } catch (error: any) {
    console.error('Generate Weekly Plan error:', error);
    return { success: false, error: error?.message || 'Erro ao gerar planilhas com IA' };
  }
}

export async function analyzeWorkoutPrintAction(userId: string, base64Image: string, mimeType: string) {
  try {
    const prompt = `Analise minuciosamente este print de treino exportado de relógio ou aplicativo esportivo (Strava, Garmin, Polar, Apple Watch).
Retorne um JSON puro contendo os seguintes campos:
{
  "data_treino": "DD/MM/AAAA",
  "distancia_km": 0.0,
  "tempo_min": 0.0,
  "pace_medio": "MM:SS",
  "fc_media": 0,
  "notas": "resumo com destaques da sessão"
}`;

    const genAI = getGenAI();
    const model = genAI.getGenerativeModel({
      model: 'gemini-2.5-flash',
      generationConfig: { responseMimeType: 'application/json' },
    });

    const result = await model.generateContent([
      {
        inlineData: {
          data: base64Image,
          mimeType: mimeType || 'image/jpeg',
        },
      },
      prompt,
    ]);

    const data = JSON.parse(result.response.text());
    return { success: true, data };
  } catch (error: any) {
    console.error('Analyze image error:', error);
    return { success: false, error: error?.message || 'Erro ao analisar imagem com IA' };
  }
}
