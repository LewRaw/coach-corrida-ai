'use client';

import React from 'react';
import { Schedule } from '@/lib/types';
import { CheckCircle2, Clock3, Route } from 'lucide-react';

interface WeeklyProgressProps {
  schedules: Schedule[];
}

export default function WeeklyProgress({ schedules }: WeeklyProgressProps) {
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
    <section className="bg-white dark:bg-[#141d18] border border-slate-200 dark:border-[#23312a] rounded-3xl p-4 shadow-sm">
      <div className="flex items-center justify-between mb-2.5">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
          Progresso Semanal
        </h3>
        <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/40">
          {adherencePercent}% Concluído
        </span>
      </div>

      {/* Visual Progress Bar */}
      <div className="w-full bg-slate-100 dark:bg-[#0e1411] rounded-full h-2.5 mb-3 overflow-hidden">
        <div
          className="bg-emerald-500 h-full rounded-full transition-all duration-500"
          style={{ width: `${Math.min(100, Math.max(0, adherencePercent))}%` }}
        />
      </div>

      {/* Progress Cards */}
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="bg-slate-50 dark:bg-[#0e1411] border border-slate-100 dark:border-[#1d2922] rounded-2xl p-2.5">
          <div className="flex items-center justify-center gap-1 text-slate-400 mb-0.5">
            <CheckCircle2 className="w-3 h-3 text-emerald-500" />
            <span className="text-[10px] font-semibold uppercase">Feitos</span>
          </div>
          <div className="text-sm font-extrabold text-slate-900 dark:text-white">
            {completedWorkouts} <span className="text-slate-400 font-normal text-xs">/ {totalWorkouts}</span>
          </div>
        </div>

        <div className="bg-slate-50 dark:bg-[#0e1411] border border-slate-100 dark:border-[#1d2922] rounded-2xl p-2.5">
          <div className="flex items-center justify-center gap-1 text-slate-400 mb-0.5">
            <Clock3 className="w-3 h-3 text-amber-500" />
            <span className="text-[10px] font-semibold uppercase">Restam</span>
          </div>
          <div className="text-sm font-extrabold text-slate-900 dark:text-white">
            {pendingWorkouts} <span className="text-slate-400 font-normal text-xs">treinos</span>
          </div>
        </div>

        <div className="bg-slate-50 dark:bg-[#0e1411] border border-slate-100 dark:border-[#1d2922] rounded-2xl p-2.5">
          <div className="flex items-center justify-center gap-1 text-slate-400 mb-0.5">
            <Route className="w-3 h-3 text-teal-500" />
            <span className="text-[10px] font-semibold uppercase">Volume</span>
          </div>
          <div className="text-sm font-extrabold text-slate-900 dark:text-white">
            {totalDistanceCompleted.toFixed(1)} <span className="text-slate-400 font-normal text-[10px]">/{totalDistancePlanned.toFixed(0)}k</span>
          </div>
        </div>
      </div>
    </section>
  );
}
