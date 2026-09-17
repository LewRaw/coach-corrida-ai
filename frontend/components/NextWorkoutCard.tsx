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

  // State 1: No workouts
  if (schedules.length === 0) {
    return (
      <div className="bg-white dark:bg-[#141d18] border border-slate-200 dark:border-[#23312a] rounded-3xl p-6 text-center shadow-sm">
        <div className="w-12 h-12 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto mb-3">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h3 className="text-base font-bold text-slate-900 dark:text-white mb-1">
          Nenhum treino agendado
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs mx-auto">
          Você ainda não possui treinos agendados. Use o botão abaixo para gerar uma nova planilha com IA!
        </p>
      </div>
    );
  }

  // State 2: All completed
  if (!nextWorkout) {
    return (
      <div className="relative overflow-hidden bg-gradient-to-br from-emerald-500/15 via-white to-teal-500/10 dark:from-emerald-950/40 dark:via-[#141d18] dark:to-teal-950/30 border border-emerald-500/30 rounded-3xl p-6 shadow-sm text-center">
        <div className="w-14 h-14 rounded-2xl bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto mb-3.5 border border-emerald-500/30">
          <Trophy className="w-7 h-7" />
        </div>
        <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-1">
          Semana Concluída! 🎉
        </h3>
        <p className="text-xs text-slate-600 dark:text-emerald-200/80 max-w-sm mx-auto leading-relaxed">
          Parabéns! Todas as sessões prescritas desta semana foram concluídas.
        </p>
      </div>
    );
  }

  // State 3: Next Workout Spotlight
  return (
    <div
      onClick={() => onSelectWorkout(nextWorkout)}
      className="group relative cursor-pointer overflow-hidden rounded-3xl bg-white dark:bg-[#141d18] border-2 border-emerald-500/30 dark:border-emerald-500/40 hover:border-emerald-500 transition-all p-5 shadow-sm"
    >
      {/* Subtle emerald glow */}
      <div className="absolute -top-16 -right-16 w-36 h-36 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header Tag */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800/60 text-emerald-700 dark:text-emerald-300 text-[11px] font-bold tracking-wide uppercase">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          Próximo Treino
        </div>

        <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1">
          <CalendarCheck className="w-3.5 h-3.5 text-emerald-500" />
          {nextWorkout.dia_semana} • {nextWorkout.data_prevista}
        </div>
      </div>

      {/* Workout Title */}
      <div className="mb-3">
        <h2 className="text-lg font-extrabold text-slate-900 dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors flex items-center justify-between">
          <span className="truncate">{nextWorkout.tipo_treino}</span>
          <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-emerald-500 transition-transform group-hover:translate-x-1 shrink-0 ml-2" />
        </h2>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4 bg-slate-50 dark:bg-[#0e1411] p-3 rounded-2xl border border-slate-100 dark:border-[#1d2922]">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
            <Gauge className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-400">
              Distância
            </div>
            <div className="text-sm font-bold text-slate-900 dark:text-white">
              {nextWorkout.distancia_km.toFixed(1)} km
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-amber-500/10 text-amber-500">
            <Flame className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-400">
              Pace Alvo
            </div>
            <div className="text-xs font-bold text-slate-900 dark:text-white truncate max-w-[90px]">
              {nextWorkout.pace_alvo}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-teal-500/10 text-teal-600 dark:text-teal-400">
            <Clock className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-400">
              Duração
            </div>
            <div className="text-sm font-bold text-slate-900 dark:text-white">
              {nextWorkout.duracao_min} min
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-purple-500/10 text-purple-500">
            <Info className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-400">
              Esforço
            </div>
            <div className="text-sm font-bold text-slate-900 dark:text-white">
              RPE {nextWorkout.rpe_alvo}/10
            </div>
          </div>
        </div>
      </div>

      {/* Snippet of Structure */}
      {nextWorkout.estrutura_treino && (
        <div className="mb-4 text-xs text-slate-600 dark:text-slate-300 line-clamp-2 bg-slate-50 dark:bg-[#0e1411] p-2.5 rounded-xl border border-slate-100 dark:border-[#1d2922] leading-relaxed">
          {nextWorkout.estrutura_treino}
        </div>
      )}

      {/* Action Button: Concluir Treino */}
      <button
        type="button"
        onClick={(e) => handleComplete(e, nextWorkout.id)}
        disabled={completingId === nextWorkout.id}
        className="w-full min-h-[46px] py-2.5 px-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 active:scale-[0.99] text-white font-bold text-sm shadow-md shadow-emerald-600/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
      >
        <CheckCircle2 className="w-4 h-4" />
        {completingId === nextWorkout.id ? 'Gravando...' : 'Concluir Treino'}
      </button>
    </div>
  );
}
