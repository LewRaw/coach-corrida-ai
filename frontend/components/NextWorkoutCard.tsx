'use client';

import React, { useState } from 'react';
import { Schedule } from '@/lib/types';
import {
  Flame,
  Clock,
  Gauge,
  CheckCircle2,
  Trophy,
  ChevronRight,
  Info,
  CalendarCheck,
  AlertCircle,
} from 'lucide-react';

interface NextWorkoutCardProps {
  schedules: Schedule[];
  onCompleteWorkout: (scheduleId: string) => Promise<void>;
  onSelectWorkout: (workout: Schedule) => void;
}

export default function NextWorkoutCard({
  schedules,
  onCompleteWorkout,
  onSelectWorkout,
}: NextWorkoutCardProps) {
  const [completingId, setCompletingId] = useState<string | null>(null);

  // Find first pending workout chronologically
  const pendingWorkouts = schedules.filter((s) => s.status === 'Pendente');
  const nextWorkout = pendingWorkouts.length > 0 ? pendingWorkouts[0] : null;

  const handleComplete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      setCompletingId(id);
      await onCompleteWorkout(id);
    } finally {
      setCompletingId(null);
    }
  };

  // State 1: No workouts in schedule
  if (schedules.length === 0) {
    return (
      <div className="bg-surface-card border border-surface-border rounded-2xl p-6 text-center shadow-md">
        <div className="w-12 h-12 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h3 className="text-base font-bold text-white mb-1">
          Nenhum treino agendado
        </h3>
        <p className="text-xs text-slate-400 max-w-xs mx-auto">
          Você ainda não possui treinos agendados no microciclo atual. Entre em contato com seu treinador para prescrição.
        </p>
      </div>
    );
  }

  // State 2: All workouts completed (Celebration!)
  if (!nextWorkout) {
    return (
      <div className="relative overflow-hidden bg-gradient-to-br from-emerald-950/60 via-surface-card to-primary-950/40 border border-emerald-500/30 rounded-2xl p-6 shadow-xl text-center">
        <div className="w-14 h-14 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto mb-3.5 border border-emerald-500/30 shadow-inner">
          <Trophy className="w-7 h-7" />
        </div>
        <h3 className="text-lg font-bold text-white mb-1">
          Semana Concluída com Sucesso! 🎉
        </h3>
        <p className="text-xs text-emerald-200/80 max-w-sm mx-auto leading-relaxed">
          Parabéns! Todas as sessões prescritas desta semana foram concluídas.
          Descanse, hidrate-se bem e prepare-se para o próximo ciclo de treinos.
        </p>
      </div>
    );
  }

  // State 3: Hero Next Workout Spotlight
  return (
    <div
      onClick={() => onSelectWorkout(nextWorkout)}
      className="group relative cursor-pointer overflow-hidden rounded-2xl bg-gradient-to-br from-primary-950/80 via-surface-card to-surface-card border-2 border-primary-500/50 hover:border-primary-400 transition-all p-5 shadow-xl"
    >
      {/* Glow highlight */}
      <div className="absolute -top-12 -right-12 w-32 h-32 bg-primary-500/20 rounded-full blur-2xl pointer-events-none" />

      {/* Card Header Tag */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary-500/20 border border-primary-500/40 text-primary-100 text-xs font-bold tracking-wide uppercase">
          <span className="w-2 h-2 rounded-full bg-primary-400 animate-pulse" />
          Próximo Treino Prescrito
        </div>

        <div className="text-xs font-semibold text-slate-300 flex items-center gap-1">
          <CalendarCheck className="w-3.5 h-3.5 text-primary-400" />
          {nextWorkout.dia_semana} • {nextWorkout.data_prevista}
        </div>
      </div>

      {/* Workout Title */}
      <div className="mb-4">
        <h2 className="text-xl font-black text-white group-hover:text-primary-100 transition-colors flex items-center justify-between">
          <span>{nextWorkout.tipo_treino}</span>
          <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-white transition-transform group-hover:translate-x-1 shrink-0 ml-2" />
        </h2>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4 bg-background/60 p-3 rounded-xl border border-surface-border">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-primary-500/10 text-primary-400">
            <Gauge className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-400">
              Distância
            </div>
            <div className="text-sm font-bold text-white">
              {nextWorkout.distancia_km.toFixed(1)} km
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-brand-amber/10 text-brand-amber">
            <Flame className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-400">
              Pace Alvo
            </div>
            <div className="text-xs font-bold text-white truncate max-w-[90px]">
              {nextWorkout.pace_alvo}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-brand-emerald/10 text-brand-emerald">
            <Clock className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-400">
              Duração
            </div>
            <div className="text-sm font-bold text-white">
              {nextWorkout.duracao_min} min
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
            <Info className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-400">
              Esforço
            </div>
            <div className="text-sm font-bold text-white">
              RPE {nextWorkout.rpe_alvo}/10
            </div>
          </div>
        </div>
      </div>

      {/* Snippet of Structure */}
      {nextWorkout.estrutura_treino && (
        <div className="mb-4 text-xs text-slate-300 line-clamp-2 bg-surface/50 p-2.5 rounded-lg border border-surface-border leading-relaxed font-mono">
          {nextWorkout.estrutura_treino}
        </div>
      )}

      {/* Action Button: Concluir Treino */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={(e) => handleComplete(e, nextWorkout.id)}
          disabled={completingId === nextWorkout.id}
          className="flex-1 min-h-[48px] py-3 px-4 rounded-xl bg-gradient-to-r from-brand-emerald to-teal-600 hover:from-emerald-400 hover:to-teal-500 active:scale-[0.98] text-white font-bold text-sm shadow-lg shadow-emerald-950/50 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
        >
          <CheckCircle2 className="w-5 h-5" />
          {completingId === nextWorkout.id ? 'Gravando...' : 'Concluir Treino'}
        </button>
      </div>
    </div>
  );
}
