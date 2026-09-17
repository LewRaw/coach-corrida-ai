'use client';

import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { QuickStats } from '@/lib/types';
import { Award, Compass, LogOut, Flame, Activity, Zap, TrendingUp } from 'lucide-react';

interface ProfileHeaderProps {
  stats: QuickStats;
}

export default function ProfileHeader({ stats }: ProfileHeaderProps) {
  const { profile, signOut, isDemoMode } = useAuth();

  const athleteName = profile?.nome || 'Atleta';
  const experienceLevel = profile?.nivel_experiencia || 'Intermediário';
  const primaryGoal = profile?.objetivo_principal || 'Construção Aeróbica';
  const sports = profile?.esportes_ativos?.length
    ? profile.esportes_ativos
    : ['Corrida de Rua'];

  return (
    <header className="pt-4 pb-2">
      {/* Top Bar with Greeting and Sign Out */}
      <div className="flex items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-primary-600 to-brand-emerald flex items-center justify-center font-bold text-lg text-white shadow-md">
            {athleteName.charAt(0).toUpperCase()}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white tracking-tight">
                Olá, {athleteName}
              </h1>
              {isDemoMode && (
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  Demo
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400">
              Pronto para o treino de hoje?
            </p>
          </div>
        </div>

        <button
          onClick={() => signOut()}
          title="Sair"
          aria-label="Sair da conta"
          className="p-2.5 rounded-xl bg-surface-card border border-surface-border text-slate-400 hover:text-rose-400 hover:border-rose-500/30 transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>

      {/* Badges & Goal Section */}
      <div className="bg-surface-card border border-surface-border rounded-2xl p-4 mb-4 shadow-sm">
        <div className="flex flex-wrap items-center gap-2 mb-2.5">
          {sports.map((sport, idx) => (
            <span
              key={idx}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-primary-500/15 text-primary-100 border border-primary-500/20"
            >
              🏃 {sport}
            </span>
          ))}
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-surface border border-surface-border text-slate-300">
            <Award className="w-3 h-3 text-brand-amber" />
            {experienceLevel}
          </span>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-300">
          <Compass className="w-4 h-4 text-brand-emerald shrink-0" />
          <span className="font-semibold text-white">Objetivo:</span>
          <span className="truncate text-slate-200">{primaryGoal}</span>
        </div>
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        <div className="bg-surface-card border border-surface-border rounded-xl p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-medium uppercase tracking-wider">Treinos</span>
            <Activity className="w-4 h-4 text-primary-500" />
          </div>
          <div className="text-xl font-extrabold text-white">
            {stats.totalWorkouts}
            <span className="text-xs font-normal text-slate-400 ml-1">sessões</span>
          </div>
        </div>

        <div className="bg-surface-card border border-surface-border rounded-xl p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-medium uppercase tracking-wider">Volume</span>
            <Zap className="w-4 h-4 text-brand-emerald" />
          </div>
          <div className="text-xl font-extrabold text-white">
            {stats.totalDistanceKm.toFixed(1)}
            <span className="text-xs font-normal text-slate-400 ml-1">km</span>
          </div>
        </div>

        <div className="bg-surface-card border border-surface-border rounded-xl p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-medium uppercase tracking-wider">Pace Médio</span>
            <Flame className="w-4 h-4 text-brand-amber" />
          </div>
          <div className="text-xl font-extrabold text-white">
            {stats.avgPace}
            <span className="text-xs font-normal text-slate-400 ml-1">/km</span>
          </div>
        </div>

        <div className="bg-surface-card border border-surface-border rounded-xl p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-medium uppercase tracking-wider">Adesão</span>
            <TrendingUp className="w-4 h-4 text-brand-teal" />
          </div>
          <div className="text-xl font-extrabold text-white">
            {stats.adherencePercent}%
          </div>
        </div>
      </div>
    </header>
  );
}
