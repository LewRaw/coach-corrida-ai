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
  Wand2,
  Loader2,
} from 'lucide-react';
import { generateWeeklyPlanAction } from '@/app/actions/ai-actions';

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
  const [isGenerating, setIsGenerating] = useState(false);

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

  const handleGenerateAI = async () => {
    try {
      setIsGenerating(true);
      const res = await generateWeeklyPlanAction(userId || 'demo-athlete-001', 'Corrida de Rua', 4);
      if (res.success) {
        alert('Planilha para os próximos 7 dias gerada com sucesso pela IA!');
        onReload();
      } else {
        alert(`Não foi possível gerar os treinos: ${res.error}`);
      }
    } catch (error: any) {
      alert('Erro de conexão ao gerar plano.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <section className="space-y-3">
      {/* Generate AI Button */}
      <button
        onClick={handleGenerateAI}
        disabled={isGenerating}
        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 rounded-2xl font-bold text-sm text-white shadow-md shadow-emerald-600/20 active:scale-[0.99] transition-all disabled:opacity-50"
      >
        {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
        {isGenerating ? 'Montando planilhas com IA...' : '✨ Gerar Treinos com IA'}
      </button>

      {/* Header & Filter Chips */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
          <Calendar className="w-4 h-4 text-emerald-500" />
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
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'bg-white dark:bg-[#141d18] border border-slate-200 dark:border-[#23312a] text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
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
        <div className="bg-white dark:bg-[#141d18] border border-slate-200 dark:border-[#23312a] rounded-2xl p-6 text-center text-slate-400 text-xs">
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
                className={`group cursor-pointer rounded-2xl border p-3.5 transition-all flex items-center justify-between gap-3 shadow-sm ${
                  isCompleted
                    ? 'bg-slate-50/60 dark:bg-[#111714]/60 border-slate-200/60 dark:border-[#1c2621] hover:border-emerald-500/40'
                    : 'bg-white dark:bg-[#141d18] border-slate-200 dark:border-[#23312a] hover:border-emerald-500'
                }`}
              >
                {/* Left: Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 mb-1">
                    <span
                      className={`inline-flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${
                        isCompleted
                          ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/40'
                          : 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300 border border-amber-200 dark:border-amber-800/40'
                      }`}
                    >
                      {isCompleted ? '✓ Concluído' : '⏳ Pendente'}
                    </span>
                    <span className="text-[11px] text-slate-400 font-medium">
                      {schedule.dia_semana} • {schedule.data_prevista}
                    </span>
                  </div>

                  <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors truncate">
                    {schedule.tipo_treino}
                  </h4>

                  <div className="flex flex-wrap items-center gap-x-3 gap-y-0.5 mt-1 text-xs text-slate-500 dark:text-slate-400">
                    <span className="flex items-center gap-1 font-semibold text-slate-700 dark:text-slate-300">
                      <Gauge className="w-3.5 h-3.5 text-emerald-500" />
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
                      className="px-3 py-1.5 rounded-xl bg-emerald-50 hover:bg-emerald-100 dark:bg-emerald-950/40 dark:hover:bg-emerald-900/40 border border-emerald-200 dark:border-emerald-800/40 text-emerald-700 dark:text-emerald-300 text-xs font-bold transition-all min-h-[40px] flex items-center gap-1"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      <span>{loadingId === schedule.id ? '...' : 'Concluir'}</span>
                    </button>
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
                      <CheckCircle2 className="w-5 h-5" />
                    </div>
                  )}

                  <div className="text-slate-400 group-hover:text-emerald-500 transition-colors p-1">
                    <ChevronRight className="w-5 h-5" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
