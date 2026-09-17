'use server';

import { getProfile, getWorkouts, supabase } from '@/lib/supabase';
import { Schedule, Workout } from '@/lib/types';

// Initialize SDK
function getGenAI() {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) throw new Error('GEMINI_API_KEY environment variable is not set');
  const { GoogleGenerativeAI } = require('@google/generative-ai');
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
    const profile = await getProfile(userId);
    const workouts = await getWorkouts(userId);

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
Sua missão é fornecer respostas técnicas, assertivas, motivadoras e personalizadas.

HISTÓRICO ATUALIZADO DO ATLETA:
${historicoTexto}

DIRETRIZES:
1. Considere todos os esportes praticados.
2. Cite dados reais dos treinos do atleta.
3. Seja honesto e profissional.
4. REGRA DE FORMATAÇÃO: NUNCA utilize caracteres '<' ou '>' para indicar comparações, ritmos ou zonas. Use palavras como 'abaixo de', 'até' ou 'menor que'.
`;

    const genAI = getGenAI();
    const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash', systemInstruction: chatSystemInstruction });

    const chat = model.startChat({
      history: messages.slice(0, -1).map((m) => ({
        role: m.role === 'user' ? 'user' : 'model',
        parts: [{ text: m.content }],
      })),
    });

    const result = await chat.sendMessage(messages[messages.length - 1].content);
    return result.response.text();
  } catch (error: any) {
    console.error('Chat error:', error);
    throw new Error('Erro ao processar mensagem com a IA');
  }
}

export async function generateWeeklyPlanAction(userId: string, tipoModalidade: string, diasSemana: number) {
  try {
    const profile = await getProfile(userId);
    const workouts = await getWorkouts(userId);
    const historicoResumo = formatAthleteHistory(workouts);

    const esportes = profile?.esportes_ativos || ['Corrida de Rua'];
    const objetivo = profile?.objetivo_principal || 'Meia Maratona';
    const diaLongao = 'Sábado';

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

    const diretrizes = `
MISSÃO: TREINADOR MESTRE MULTI-ESPORTES E FISIOLOGIA DO EXERCÍCIO.
Meta / Foco da Semana: ${objetivo}.
Frequência: ${diasSemana} sessões ativas na semana. Os outros ${7 - diasSemana} dias devem ser 'Descanso' ou 'Descanso Ativo'.
Dia Chave / Mais Exigente da Semana: ${diaLongao}.
Modalidades: ${esportes.join(', ')}
`;

    const promptPlano = `${diretrizes}

CONTEXTO TEMPORAL RIGOROSO:
- CALENDÁRIO OBRIGATÓRIO PARA AS PRÓXIMAS 7 SESSÕES FUTURAS:
${calendarioDatasStr}

DADOS E HISTÓRICO DO ATLETA:
${historicoResumo}

Retorne um JSON de array contendo 7 objetos de treino para cada um dos dias (um objeto por dia) com os seguintes campos:
- dia_semana (ex: "Sábado")
- data_prevista (ex: "18/09/2026")
- tipo_treino
- distancia_km (number)
- duracao_min (number)
- pace_alvo
- rpe_alvo (number)
- estrutura_treino

O JSON deve começar com [ e terminar com ]. Não use marcações markdown (como \`\`\`json).
REGRA CRÍTICA DE FORMATAÇÃO: NUNCA utilize caracteres '<' ou '>'!`;

    const genAI = getGenAI();
    const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });
    const result = await model.generateContent(promptPlano);
    let text = result.response.text();
    text = text.replace(/\`\`\`json/g, '').replace(/\`\`\`/g, '').trim();
    
    const prescricao = JSON.parse(text);
    
    // Inserir no Supabase (primeiro limpar antigos e adicionar novos)
    await supabase.from('schedules').delete().eq('user_id', userId).eq('status', 'Pendente');
    
    const insertData = prescricao.map((item: any) => ({
      user_id: userId,
      dia_semana: item.dia_semana,
      data_prevista: item.data_prevista,
      tipo_treino: item.tipo_treino,
      distancia_km: item.distancia_km || 0,
      duracao_min: item.duracao_min || 0,
      pace_alvo: item.pace_alvo || '',
      rpe_alvo: item.rpe_alvo || 5,
      estrutura_treino: item.estrutura_treino || '',
      status: 'Pendente',
    }));

    await supabase.from('schedules').insert(insertData);
    
    return true;
  } catch (error: any) {
    console.error('Generate Weekly Plan error:', error);
    throw new Error('Erro ao gerar planilhas');
  }
}

export async function analyzeWorkoutPrintAction(userId: string, base64Image: string, mimeType: string) {
  try {
    const prompt = `
      Analise minuciosamente este print de treino exportado de relógio ou aplicativo esportivo.
      Retorne um JSON puro (sem markdown) contendo os seguintes campos extraídos:
      - data_treino (string formato DD/MM/YYYY)
      - distancia_km (number)
      - tempo_min (number)
      - pace_medio (string formato MM:SS)
      - fc_media (number, opcional)
      - notas (string ressaltando destaques ou "Nenhuma nota")
    `;

    const genAI = getGenAI();
    const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });
    
    const result = await model.generateContent([
      {
        inlineData: {
          data: base64Image,
          mimeType: mimeType
        }
      },
      prompt
    ]);
    
    let text = result.response.text();
    text = text.replace(/\`\`\`json/g, '').replace(/\`\`\`/g, '').trim();
    
    return JSON.parse(text);
  } catch (error: any) {
    console.error('Analyze image error:', error);
    throw new Error('Erro ao analisar imagem com IA');
  }
}
