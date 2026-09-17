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
      <div className="bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] rounded-3xl p-6 text-center shadow-sm">
        <div className="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-[#202020] text-[#11C76F] flex items-center justify-center mx-auto mb-3">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h3 className="text-base font-bold text-slate-900 dark:text-white mb-1">
          Nenhum treino agendado
        </h3>
        <p className="text-xs text-slate-500 dark:text-[#8E8E93] max-w-xs mx-auto">
          Você ainda não possui treinos agendados. Use o botão abaixo para montar uma nova planilha com IA!
        </p>
      </div>
    );
  }

  // State 2: All completed
  if (!nextWorkout) {
    return (
      <div className="bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] rounded-3xl p-6 shadow-sm text-center">
        <div className="w-14 h-14 rounded-2xl bg-[#11C76F]/15 text-[#11C76F] flex items-center justify-center mx-auto mb-3.5">
          <Trophy className="w-7 h-7" />
        </div>
        <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-1">
          Semana Concluída! 🎉
        </h3>
        <p className="text-xs text-slate-500 dark:text-[#8E8E93] max-w-sm mx-auto leading-relaxed">
          Parabéns! Todas as sessões prescritas desta semana foram concluídas.
        </p>
      </div>
    );
  }

  // State 3: Next Workout Spotlight (Flat PicPay / Nubank Style)
  return (
    <div
      onClick={() => onSelectWorkout(nextWorkout)}
      className="group cursor-pointer rounded-3xl bg-white dark:bg-[#141414] border-2 border-slate-200 dark:border-[#262626] hover:border-[#11C76F] transition-all p-5 shadow-sm"
    >
      {/* Header Tag */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#11C76F]/15 text-[#11C76F] text-[11px] font-bold tracking-wide uppercase">
          <span className="w-2 h-2 rounded-full bg-[#11C76F]" />
          Próximo Treino
        </div>

        <div className="text-xs font-semibold text-slate-500 dark:text-[#8E8E93] flex items-center gap-1">
          <CalendarCheck className="w-3.5 h-3.5 text-[#11C76F]" />
          {nextWorkout.dia_semana} • {nextWorkout.data_prevista}
        </div>
      </div>

      {/* Workout Title */}
      <div className="mb-3">
        <h2 className="text-lg font-extrabold text-slate-900 dark:text-white group-hover:text-[#11C76F] transition-colors flex items-center justify-between">
          <span className="truncate">{nextWorkout.tipo_treino}</span>
          <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-[#11C76F] transition-transform group-hover:translate-x-1 shrink-0 ml-2" />
        </h2>
      </div>

      {/* Key Metrics Grid (Flat Neutral Boxes) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4 bg-slate-50 dark:bg-[#1c1c1c] p-3 rounded-2xl border border-slate-100 dark:border-[#242424]">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-white dark:bg-[#282828] text-[#11C76F] shadow-xs">
            <Gauge className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-400 dark:text-[#8E8E93]">
              Distância
            </div>
            <div className="text-sm font-bold text-slate-900 dark:text-white">
              {nextWorkout.distancia_km.toFixed(1)} km
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-white dark:bg-[#282828] text-amber-500 shadow-xs">
            <Flame className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-400 dark:text-[#8E8E93]">
              Pace Alvo
            </div>
            <div className="text-xs font-bold text-slate-900 dark:text-white truncate max-w-[90px]">
              {nextWorkout.pace_alvo}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-white dark:bg-[#282828] text-[#11C76F] shadow-xs">
            <Clock className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-400 dark:text-[#8E8E93]">
              Duração
            </div>
            <div className="text-sm font-bold text-slate-900 dark:text-white">
              {nextWorkout.duracao_min} min
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-white dark:bg-[#282828] text-purple-500 shadow-xs">
            <Info className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-semibold text-slate-400 dark:text-[#8E8E93]">
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
        <div className="mb-4 text-xs text-slate-600 dark:text-slate-300 line-clamp-2 bg-slate-50 dark:bg-[#1c1c1c] p-2.5 rounded-xl border border-slate-100 dark:border-[#242424] leading-relaxed">
          {nextWorkout.estrutura_treino}
        </div>
      )}

      {/* Action Button: Concluir Treino (Solid PicPay Green) */}
      <button
        type="button"
        onClick={(e) => handleComplete(e, nextWorkout.id)}
        disabled={completingId === nextWorkout.id}
        className="w-full min-h-[46px] py-2.5 px-4 rounded-2xl bg-[#11C76F] hover:bg-[#0ea85d] active:scale-[0.99] text-white font-bold text-sm shadow-sm flex items-center justify-center gap-2 transition-all disabled:opacity-50"
      >
        <CheckCircle2 className="w-4 h-4" />
        {completingId === nextWorkout.id ? 'Gravando...' : 'Concluir Treino'}
      </button>
    </div>
  );
}
