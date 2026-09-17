'use client';

import React, { useState } from 'react';
import { Schedule } from '@/lib/types';
import {
  CheckCircle2,
  Clock,
  Gauge,
  Flame,
  Calendar,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import WorkoutBuilderModal from './WorkoutBuilderModal';

interface WorkoutScheduleListProps {
  schedules: Schedule[];
  onCompleteWorkout: (scheduleId: string) => Promise<void>;
  onSelectWorkout: (workout: Schedule) => void;
  userId: string;
  onReload: () => void;
}

export default function WorkoutScheduleList({
  schedules,
  onCompleteWorkout,
  onSelectWorkout,
  userId,
  onReload,
}: WorkoutScheduleListProps) {
  const [filter, setFilter] = useState<'Todos' | 'Pendentes' | 'Concluídos'>('Todos');
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [isBuilderOpen, setIsBuilderOpen] = useState(false);

  const filteredSchedules = schedules.filter((s) => {
    if (filter === 'Pendentes') return s.status === 'Pendente';
    if (filter === 'Concluídos') return s.status === 'Concluído';
    return true;
  });

  const handleToggle = async (e: React.MouseEvent, s: Schedule) => {
    e.stopPropagation();
    if (s.status === 'Concluído') return;
    try {
      setLoadingId(s.id);
      await onCompleteWorkout(s.id);
    } finally {
      setLoadingId(null);
    }
  };

  return (
    <section className="space-y-3">
      {/* Montar Planilha com IA (Solid PicPay Green Button) */}
      <button
        onClick={() => setIsBuilderOpen(true)}
        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[#11C76F] hover:bg-[#0ea85d] active:scale-[0.99] rounded-2xl font-bold text-sm text-white shadow-sm transition-all"
      >
        <Sparkles className="w-4 h-4" />
        ✨ Montar Planilha de Treinos com IA
      </button>

      {/* Header & Filter Chips */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-[#8E8E93] flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5 text-[#11C76F]" />
          Cronograma do Microciclo
        </h3>

        {/* Filter Chips in Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-0.5">
          {(['Todos', 'Pendentes', 'Concluídos'] as const).map((chip) => (
            <button
              key={chip}
              onClick={() => setFilter(chip)}
              className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap transition-all min-h-[34px] ${
                filter === chip
                  ? 'bg-[#11C76F] text-white'
                  : 'bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] text-slate-500 dark:text-[#8E8E93] hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              {chip}
              <span className="ml-1 opacity-70">
                (
                {chip === 'Todos'
                  ? schedules.length
                  : chip === 'Pendentes'
                  ? schedules.filter((x) => x.status === 'Pendente').length
                  : schedules.filter((x) => x.status === 'Concluído').length}
                )
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Workout Card List */}
      {filteredSchedules.length === 0 ? (
        <div className="bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] rounded-2xl p-6 text-center text-slate-400 text-xs">
          Nenhum treino encontrado ({filter}).
        </div>
      ) : (
        <div className="space-y-2">
          {filteredSchedules.map((schedule) => {
            const isCompleted = schedule.status === 'Concluído';

            return (
              <div
                key={schedule.id}
                onClick={() => onSelectWorkout(schedule)}
                className={`group cursor-pointer rounded-2xl border p-3.5 transition-all flex items-center justify-between gap-3 ${
                  isCompleted
                    ? 'bg-slate-50 dark:bg-[#111111] border-slate-200 dark:border-[#1f1f1f]'
                    : 'bg-white dark:bg-[#141414] border-slate-200 dark:border-[#262626] hover:border-[#11C76F]'
                }`}
              >
                {/* Left: Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 mb-1">
                    <span
                      className={`inline-flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${
                        isCompleted
                          ? 'bg-[#11C76F]/15 text-[#11C76F]'
                          : 'bg-amber-500/15 text-amber-500'
                      }`}
                    >
                      {isCompleted ? '✓ Concluído' : '⏳ Pendente'}
                    </span>
                    <span className="text-[11px] text-slate-400 font-medium">
                      {schedule.dia_semana} • {schedule.data_prevista}
                    </span>
                  </div>

                  <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-[#11C76F] transition-colors truncate">
                    {schedule.tipo_treino}
                  </h4>

                  <div className="flex flex-wrap items-center gap-x-3 gap-y-0.5 mt-1 text-xs text-slate-500 dark:text-[#8E8E93]">
                    <span className="flex items-center gap-1 font-semibold text-slate-700 dark:text-slate-300">
                      <Gauge className="w-3.5 h-3.5 text-[#11C76F]" />
                      {schedule.distancia_km.toFixed(1)} km
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      {schedule.duracao_min} min
                    </span>
                    <span className="flex items-center gap-1">
                      <Flame className="w-3.5 h-3.5 text-amber-500" />
                      {schedule.pace_alvo}
                    </span>
                  </div>
                </div>

                {/* Right: Quick Action & Details Chevron */}
                <div className="flex items-center gap-1.5 shrink-0">
                  {!isCompleted ? (
                    <button
                      type="button"
                      onClick={(e) => handleToggle(e, schedule)}
                      disabled={loadingId === schedule.id}
                      className="px-3 py-1.5 rounded-xl bg-[#11C76F]/10 hover:bg-[#11C76F]/20 text-[#11C76F] text-xs font-bold transition-all min-h-[40px] flex items-center gap-1"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      <span>{loadingId === schedule.id ? '...' : 'Concluir'}</span>
                    </button>
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-[#11C76F]/10 text-[#11C76F] flex items-center justify-center">
                      <CheckCircle2 className="w-5 h-5" />
                    </div>
                  )}

                  <div className="text-slate-400 group-hover:text-[#11C76F] transition-colors p-1">
                    <ChevronRight className="w-5 h-5" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Workout Builder Modal with Streamlit questions */}
      <WorkoutBuilderModal
        isOpen={isBuilderOpen}
        onClose={() => setIsBuilderOpen(false)}
        userId={userId}
        onSuccess={onReload}
      />
    </section>
  );
}
