import { createClient } from '@supabase/supabase-js';
import { Profile, Schedule, Workout } from './types';

const supabaseUrl =
  process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://vkkbvvpjfomxwawggsel.supabase.co';
const supabaseAnonKey =
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
  'sb_publishable_xVNZgXHQFKeKvDxKlonDoQ_dgsh-e0D';

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});

// Demo / Offline fallback mock data matching Streamlit athlete schemas
export const DEMO_PROFILE: Profile = {
  id: 'demo-athlete-001',
  email: 'atleta.demo@coachai.com.br',
  nome: 'Carlos Silva',
  modalidade_preferida: 'Corrida',
  objetivo_principal: 'Meia Maratona (21.1 km) sub 1h50',
  esportes_ativos: ['Corrida de Rua', 'Fortalecimento'],
  nivel_experiencia: 'Intermediário',
  dias_disponiveis: 4,
  pwa_aviso_dispensado: false,
  onboarding_concluido: true,
  created_at: new Date().toISOString(),
};

export const DEMO_SCHEDULES: Schedule[] = [
  {
    id: 'TR-20260916-01',
    user_id: 'demo-athlete-001',
    dia_semana: 'Terça-feira',
    data_prevista: '16/09/2026',
    tipo_treino: 'Rodagem Regenerativa Z1/Z2',
    distancia_km: 6.0,
    duracao_min: 36,
    pace_alvo: '05:55 a 06:10/km',
    rpe_alvo: 4,
    estrutura_treino:
      'Aquecimento: 5min caminhada acelerada + mobilidade articular.\nParte Principal: 5km contínuos em Zona 2 confortável, respiração nasal.\nSoltura: 5min trote leve + alongamento dinâmico.',
    status: 'Concluído',
    data_conclusao: '2026-09-16T10:30:00Z',
    created_at: '2026-09-15T00:00:00Z',
  },
  {
    id: 'TR-20260918-02',
    user_id: 'demo-athlete-001',
    dia_semana: 'Quinta-feira',
    data_prevista: '18/09/2026',
    tipo_treino: 'Intervalado VO2 Max (6x 800m)',
    distancia_km: 8.5,
    duracao_min: 48,
    pace_alvo: '04:25 a 04:35/km',
    rpe_alvo: 8,
    estrutura_treino:
      'Aquecimento: 2km leve (Z2) + 4x retas progressivas de 80m.\nParte Principal: 6 séries de 800m no ritmo alvo (04:30/km) com 90s de recuperação ativa em trote leve.\nSoltura: 1.5km trote bem suave (Z1) para desaquecimento.',
    status: 'Pendente',
    data_conclusao: null,
    created_at: '2026-09-15T00:00:00Z',
  },
  {
    id: 'TR-20260920-03',
    user_id: 'demo-athlete-001',
    dia_semana: 'Sábado',
    data_prevista: '20/09/2026',
    tipo_treino: 'Treino Tempo / Ritmo de Limiar',
    distancia_km: 10.0,
    duracao_min: 52,
    pace_alvo: '04:55 a 05:05/km',
    rpe_alvo: 7,
    estrutura_treino:
      'Aquecimento: 2km progressivos de Z1 para Z2.\nParte Principal: 6km contínuos cravados no ritmo de limiar anaeróbio (Z4 baixa).\nSoltura: 2km leve Z1.',
    status: 'Pendente',
    data_conclusao: null,
    created_at: '2026-09-15T00:00:00Z',
  },
  {
    id: 'TR-20260921-04',
    user_id: 'demo-athlete-001',
    dia_semana: 'Domingo',
    data_prevista: '21/09/2026',
    tipo_treino: 'Longão de Construção Aeróbica',
    distancia_km: 15.0,
    duracao_min: 85,
    pace_alvo: '05:35 a 05:50/km',
    rpe_alvo: 6,
    estrutura_treino:
      'Aquecimento: 1km Z1 muito leve.\nParte Principal: 13km em Zona 2 com hidratação a cada 3km e consumo de gel aos 40min e 70min.\nSoltura: 1km caminhada e alongamento.',
    status: 'Pendente',
    data_conclusao: null,
    created_at: '2026-09-15T00:00:00Z',
  },
];

export const DEMO_WORKOUTS: Workout[] = [
  {
    id: 'w-1',
    user_id: 'demo-athlete-001',
    data: '14/09/2026',
    distancia_km: 7.2,
    tempo_min: 38.5,
    pace_medio: '05:21',
    fc_media: 146,
    zona_predominante: 'Z2 Rodagem Aeróbica',
    rpe: 5,
    notas_atleta: 'Treino com ótima sensação térmica e ritmo estável.',
  },
  {
    id: 'w-2',
    user_id: 'demo-athlete-001',
    data: '12/09/2026',
    distancia_km: 12.0,
    tempo_min: 64.0,
    pace_medio: '05:20',
    fc_media: 152,
    zona_predominante: 'Z2/Z3 Aeróbica Média',
    rpe: 6,
    notas_atleta: 'Sensação boa no longão de sábado.',
  },
  {
    id: 'w-3',
    user_id: 'demo-athlete-001',
    data: '09/09/2026',
    distancia_km: 8.0,
    tempo_min: 41.2,
    pace_medio: '05:09',
    fc_media: 158,
    zona_predominante: 'Z3 Tempo',
    rpe: 7,
    notas_atleta: 'Tiros moderados com boa resposta muscular.',
  },
];

// Helper functions connecting to Supabase tables
export async function getProfile(userId: string): Promise<Profile | null> {
  try {
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .maybeSingle();

    if (error) {
      console.warn('Supabase fetch profile warning:', error.message);
      return null;
    }
    return data as Profile;
  } catch (err) {
    console.warn('Network or Supabase error fetching profile:', err);
    return null;
  }
}

export async function upsertProfile(profile: Partial<Profile> & { id: string }): Promise<boolean> {
  try {
    const { error } = await supabase.from('profiles').upsert(profile);
    if (error) {
      console.error('Supabase upsert profile error:', error);
      return false;
    }
    return true;
  } catch (err) {
    console.error('Exception during profile upsert:', err);
    return false;
  }
}

export async function getSchedules(userId: string): Promise<Schedule[]> {
  try {
    const { data, error } = await supabase
      .from('schedules')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: true });

    if (error) {
      console.warn('Supabase fetch schedules error:', error.message);
      return [];
    }
    return (data || []) as Schedule[];
  } catch (err) {
    console.warn('Exception fetching schedules:', err);
    return [];
  }
}

export async function markWorkoutCompleted(scheduleId: string): Promise<boolean> {
  try {
    const timestamp = new Date().toISOString();
    const { error } = await supabase
      .from('schedules')
      .update({
        status: 'Concluído',
        data_conclusao: timestamp,
      })
      .eq('id', scheduleId);

    if (error) {
      console.error('Error marking schedule as completed:', error);
      return false;
    }
    return true;
  } catch (err) {
    console.error('Exception marking schedule completed:', err);
    return false;
  }
}

export async function getWorkouts(userId: string): Promise<Workout[]> {
  try {
    const { data, error } = await supabase
      .from('workouts')
      .select('*')
      .eq('user_id', userId)
      .order('data', { ascending: false });

    if (error) {
      console.warn('Supabase fetch workouts error:', error.message);
      return [];
    }
    return (data || []) as Workout[];
  } catch (err) {
    console.warn('Exception fetching workouts:', err);
    return [];
  }
}
