export interface Profile {
  id: string;
  email: string;
  nome: string;
  modalidade_preferida?: string;
  objetivo_principal: string;
  esportes_ativos: string[];
  nivel_experiencia: string;
  dias_disponiveis: number;
  pwa_aviso_dispensado?: boolean;
  onboarding_concluido?: boolean;
  auth_token?: string;
  created_at?: string;
}

export interface Workout {
  id: string;
  user_id: string;
  data: string;
  distancia_km: number;
  tempo_min: number;
  pace_medio: string;
  fc_media?: number;
  zona_predominante?: string;
  rpe?: number;
  notas_atleta?: string;
  parecer_treinador?: string;
  created_at?: string;
}

export interface Schedule {
  id: string;
  user_id: string;
  dia_semana: string;
  data_prevista: string;
  tipo_treino: string;
  distancia_km: number;
  duracao_min: number;
  pace_alvo: string;
  rpe_alvo: number;
  estrutura_treino: string;
  status: 'Pendente' | 'Concluído';
  data_conclusao?: string | null;
  created_at?: string;
}

export interface WeeklyStats {
  totalWorkouts: number;
  completedWorkouts: number;
  pendingWorkouts: number;
  totalDistancePlanned: number;
  totalDistanceCompleted: number;
  adherencePercent: number;
}

export interface QuickStats {
  totalWorkouts: number;
  totalDistanceKm: number;
  avgPace: string;
  adherencePercent: number;
}
