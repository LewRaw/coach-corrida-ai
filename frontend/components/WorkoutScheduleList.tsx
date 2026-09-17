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
  Filter,
  Wand2,
  Loader2
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
  onReload
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
        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 rounded-xl font-bold text-sm text-white shadow-lg transition-all disabled:opacity-50"
      >
        {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Wand2 className="w-5 h-5" />}
        {isGenerating ? 'Montando planilhas...' : '✨ Gerar Treinos com IA'}
      </button>

      {/* Header & Filter Chips */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Calendar className="w-4 h-4 text-primary-400" />
          Cronograma do Microciclo
        </h3>

        {/* Filter Chips */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
          {(['Todos', 'Pendentes', 'Concluídos'] as const).map((chip) => (
            <button
              key={chip}
              onClick={() => setFilter(chip)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all min-h-[36px] ${
                filter === chip
                  ? 'bg-primary-600 text-white shadow-md'
                  : 'bg-surface-card border border-surface-border text-slate-400 hover:text-white'
              }`}
            >
              {chip}
              <span className="ml-1.5 opacity-70">
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
        <div className="bg-surface-card border border-surface-border rounded-xl p-6 text-center text-slate-400 text-xs">
          Nenhum treino encontrado com o filtro selecionado ({filter}).
        </div>
      ) : (
        <div className="space-y-2.5">
          {filteredSchedules.map((schedule) => {
            const isCompleted = schedule.status === 'Concluído';

            return (
              <div
                key={schedule.id}
                onClick={() => onSelectWorkout(schedule)}
                className={`group cursor-pointer rounded-xl border p-3.5 transition-all flex items-center justify-between gap-3 ${
                  isCompleted
                    ? 'bg-surface-card/60 border-surface-border/60 hover:border-emerald-500/40'
                    : 'bg-surface-card border-surface-border hover:border-primary-500/50'
                }`}
              >
                {/* Left: Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className={`inline-flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${
                        isCompleted
                          ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                          : 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                      }`}
                    >
                      {isCompleted ? '✓ Concluído' : '⏳ Pendente'}
                    </span>
                    <span className="text-xs text-slate-400 font-medium">
                      {schedule.dia_semana} • {schedule.data_prevista}
                    </span>
                  </div>

                  <h4 className="text-sm font-bold text-white group-hover:text-primary-100 transition-colors truncate">
                    {schedule.tipo_treino}
                  </h4>

                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1 text-xs text-slate-300">
                    <span className="flex items-center gap-1">
                      <Gauge className="w-3.5 h-3.5 text-primary-400" />
                      {schedule.distancia_km.toFixed(1)} km
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      {schedule.duracao_min} min
                    </span>
                    <span className="flex items-center gap-1 text-slate-300">
                      <Flame className="w-3.5 h-3.5 text-brand-amber" />
                      {schedule.pace_alvo}
                    </span>
                  </div>
                </div>

                {/* Right: Quick Action & Details Chevron */}
                <div className="flex items-center gap-2 shrink-0">
                  {!isCompleted ? (
                    <button
                      type="button"
                      onClick={(e) => handleToggle(e, schedule)}
                      disabled={loadingId === schedule.id}
                      className="px-3 py-2 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-300 hover:text-emerald-200 text-xs font-bold transition-all min-h-[44px] flex items-center gap-1"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      <span>{loadingId === schedule.id ? '...' : 'Concluir'}</span>
                    </button>
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                      <CheckCircle2 className="w-5 h-5" />
                    </div>
                  )}

                  <div className="text-slate-500 group-hover:text-slate-300 transition-colors p-1">
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
