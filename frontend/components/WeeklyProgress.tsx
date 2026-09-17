'use client';

import React from 'react';
import { Schedule, WeeklyStats } from '@/lib/types';
import { CheckCircle2, Clock3, Route, Percent } from 'lucide-react';

interface WeeklyProgressProps {
  schedules: Schedule[];
}

export default function WeeklyProgress({ schedules }: WeeklyProgressProps) {
  // Compute metrics
  const totalWorkouts = schedules.length;
  const completedWorkouts = schedules.filter((s) => s.status === 'Concluído').length;
  const pendingWorkouts = totalWorkouts - completedWorkouts;

  const totalDistancePlanned = schedules.reduce(
    (acc, cur) => acc + (Number(cur.distancia_km) || 0),
    0
  );
  const totalDistanceCompleted = schedules
    .filter((s) => s.status === 'Concluído')
    .reduce((acc, cur) => acc + (Number(cur.distancia_km) || 0), 0);

  const adherencePercent =
    totalWorkouts > 0 ? Math.round((completedWorkouts / totalWorkouts) * 100) : 0;

  return (
    <section className="bg-surface-card border border-surface-border rounded-2xl p-4 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          Progresso Semanal
        </h3>
        <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-primary-500/15 text-primary-100 border border-primary-500/20">
          {adherencePercent}% Concluído
        </span>
      </div>

      {/* Visual Progress Bar */}
      <div className="w-full bg-background rounded-full h-3 mb-4 overflow-hidden border border-surface-border/50">
        <div
          className="bg-gradient-to-r from-primary-600 via-primary-500 to-brand-emerald h-full rounded-full transition-all duration-500 shadow-sm"
          style={{ width: `${Math.min(100, Math.max(0, adherencePercent))}%` }}
        />
      </div>

      {/* Progress Cards */}
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="bg-surface/60 border border-surface-border rounded-xl p-2.5">
          <div className="flex items-center justify-center gap-1 text-slate-400 mb-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-brand-emerald" />
            <span className="text-[10px] uppercase font-semibold">Feitos</span>
          </div>
          <div className="text-sm font-extrabold text-white">
            {completedWorkouts} <span className="text-slate-400 font-normal text-xs">/ {totalWorkouts}</span>
          </div>
        </div>

        <div className="bg-surface/60 border border-surface-border rounded-xl p-2.5">
          <div className="flex items-center justify-center gap-1 text-slate-400 mb-1">
            <Clock3 className="w-3.5 h-3.5 text-brand-amber" />
            <span className="text-[10px] uppercase font-semibold">Pendentes</span>
          </div>
          <div className="text-sm font-extrabold text-white">
            {pendingWorkouts} <span className="text-slate-400 font-normal text-xs">sessões</span>
          </div>
        </div>

        <div className="bg-surface/60 border border-surface-border rounded-xl p-2.5">
          <div className="flex items-center justify-center gap-1 text-slate-400 mb-1">
            <Route className="w-3.5 h-3.5 text-primary-400" />
            <span className="text-[10px] uppercase font-semibold">Volume</span>
          </div>
          <div className="text-sm font-extrabold text-white">
            {totalDistanceCompleted.toFixed(1)} <span className="text-slate-400 font-normal text-[11px]">/ {totalDistancePlanned.toFixed(0)}k</span>
          </div>
        </div>
      </div>
    </section>
  );
}
