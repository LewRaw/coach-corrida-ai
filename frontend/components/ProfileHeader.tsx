'use client';

import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useTheme } from '@/context/ThemeContext';
import { QuickStats } from '@/lib/types';
import { Award, Compass, LogOut, Flame, Activity, Zap, TrendingUp, Sun, Moon, ChevronDown } from 'lucide-react';

interface ProfileHeaderProps {
  stats: QuickStats;
}

export default function ProfileHeader({ stats }: ProfileHeaderProps) {
  const { profile, signOut, isDemoMode } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [isExpanded, setIsExpanded] = useState(false);

  const athleteName = profile?.nome || 'Atleta';
  const experienceLevel = profile?.nivel_experiencia || 'Intermediário';
  const primaryGoal = profile?.objetivo_principal || 'Construção Aeróbica';
  const sports = profile?.esportes_ativos?.length
    ? profile.esportes_ativos
    : ['Corrida de Rua'];

  return (
    <header className="pt-2 pb-2">
      {/* Top Bar: Athlete Info + Theme Switcher + Logout */}
      <div className="flex items-center justify-between gap-3 mb-3">
        <div
          className="flex items-center gap-3 cursor-pointer select-none flex-1 group"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {/* Solid PicPay Green Avatar */}
          <div className="w-12 h-12 rounded-2xl bg-[#11C76F] flex items-center justify-center font-bold text-lg text-white shadow-sm shrink-0">
            {athleteName.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight truncate">
                Olá, {athleteName}
              </h1>
              {isDemoMode && (
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                  Demo
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500 dark:text-[#8E8E93] flex items-center gap-1">
              <span>Painel do Atleta</span>
              <ChevronDown
                className={`w-3.5 h-3.5 transition-transform duration-200 text-[#11C76F] ${
                  isExpanded ? 'rotate-180' : ''
                }`}
              />
            </p>
          </div>
        </div>

        {/* Action Buttons: Theme toggle + Sign Out */}
        <div className="flex items-center gap-1.5 shrink-0">
          <button
            onClick={toggleTheme}
            title={theme === 'dark' ? 'Mudar para Tema Claro' : 'Mudar para Tema Escuro'}
            aria-label="Alternar tema"
            className="p-2.5 rounded-2xl bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] text-slate-600 dark:text-slate-300 hover:text-[#11C76F] shadow-sm transition-all min-w-[42px] min-h-[42px] flex items-center justify-center"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
          </button>

          <button
            onClick={() => signOut()}
            title="Sair"
            aria-label="Sair da conta"
            className="p-2.5 rounded-2xl bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] text-slate-400 hover:text-rose-500 shadow-sm transition-all min-w-[42px] min-h-[42px] flex items-center justify-center"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Badges & Goal Section (Collapsible) */}
      {isExpanded && (
        <div className="bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] rounded-2xl p-4 mb-3 shadow-sm animate-in slide-in-from-top-2 fade-in duration-150">
          <div className="flex flex-wrap items-center gap-1.5 mb-2.5">
            {sports.map((sport, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-[#11C76F]/15 text-[#11C76F]"
              >
                🏃 {sport}
              </span>
            ))}
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-slate-100 dark:bg-[#202020] text-slate-700 dark:text-slate-300">
              <Award className="w-3 h-3 text-amber-500" />
              {experienceLevel}
            </span>
          </div>

          <div className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-300">
            <Compass className="w-4 h-4 text-[#11C76F] shrink-0" />
            <span className="font-semibold text-slate-900 dark:text-white">Objetivo:</span>
            <span className="truncate text-slate-600 dark:text-[#8E8E93]">{primaryGoal}</span>
          </div>
        </div>
      )}

      {/* Quick Stats Grid (Solid Flat PicPay Cards) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <div className="bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] rounded-2xl p-3 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 dark:text-[#8E8E93] mb-1">
            <span className="text-[10px] font-semibold uppercase tracking-wider">Treinos</span>
            <Activity className="w-3.5 h-3.5 text-[#11C76F]" />
          </div>
          <div className="text-xl font-extrabold text-slate-900 dark:text-white">
            {stats.totalWorkouts}
            <span className="text-xs font-normal text-slate-400 ml-1">sessões</span>
          </div>
        </div>

        <div className="bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] rounded-2xl p-3 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 dark:text-[#8E8E93] mb-1">
            <span className="text-[10px] font-semibold uppercase tracking-wider">Volume</span>
            <Zap className="w-3.5 h-3.5 text-[#11C76F]" />
          </div>
          <div className="text-xl font-extrabold text-slate-900 dark:text-white">
            {stats.totalDistanceKm.toFixed(1)}
            <span className="text-xs font-normal text-slate-400 ml-1">km</span>
          </div>
        </div>

        <div className="bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] rounded-2xl p-3 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 dark:text-[#8E8E93] mb-1">
            <span className="text-[10px] font-semibold uppercase tracking-wider">Pace Médio</span>
            <Flame className="w-3.5 h-3.5 text-amber-500" />
          </div>
          <div className="text-xl font-extrabold text-slate-900 dark:text-white">
            {stats.avgPace}
            <span className="text-xs font-normal text-slate-400 ml-1">/km</span>
          </div>
        </div>

        <div className="bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] rounded-2xl p-3 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 dark:text-[#8E8E93] mb-1">
            <span className="text-[10px] font-semibold uppercase tracking-wider">Adesão</span>
            <TrendingUp className="w-3.5 h-3.5 text-[#11C76F]" />
          </div>
          <div className="text-xl font-extrabold text-[#11C76F]">
            {stats.adherencePercent}%
          </div>
        </div>
      </div>
    </header>
  );
}
