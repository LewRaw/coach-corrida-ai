'use client';

import React from 'react';
import { Home, Calendar, Activity } from 'lucide-react';

interface BottomNavProps {
  currentTab: 'home' | 'schedule' | 'stats';
  onTabChange: (tab: 'home' | 'schedule' | 'stats') => void;
}

export default function BottomNav({ currentTab, onTabChange }: BottomNavProps) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 bg-white/85 dark:bg-[#0b0f0e]/85 backdrop-blur-lg border-t border-slate-200 dark:border-[#1f2d26] pb-safe-bottom">
      <div className="max-w-md mx-auto flex items-center justify-around px-3 py-1.5">
        <button
          type="button"
          onClick={() => onTabChange('home')}
          className={`flex-1 flex flex-col items-center justify-center py-1.5 px-2 rounded-2xl transition-all min-h-[44px] ${
            currentTab === 'home'
              ? 'text-emerald-600 dark:text-emerald-400 font-bold scale-[1.03]'
              : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200'
          }`}
        >
          <Home className="w-5 h-5 mb-0.5" />
          <span className="text-[11px]">Início</span>
        </button>

        <button
          type="button"
          onClick={() => onTabChange('schedule')}
          className={`flex-1 flex flex-col items-center justify-center py-1.5 px-2 rounded-2xl transition-all min-h-[44px] ${
            currentTab === 'schedule'
              ? 'text-emerald-600 dark:text-emerald-400 font-bold scale-[1.03]'
              : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200'
          }`}
        >
          <Calendar className="w-5 h-5 mb-0.5" />
          <span className="text-[11px]">Cronograma</span>
        </button>

        <button
          type="button"
          onClick={() => onTabChange('stats')}
          className={`flex-1 flex flex-col items-center justify-center py-1.5 px-2 rounded-2xl transition-all min-h-[44px] ${
            currentTab === 'stats'
              ? 'text-emerald-600 dark:text-emerald-400 font-bold scale-[1.03]'
              : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200'
          }`}
        >
          <Activity className="w-5 h-5 mb-0.5" />
          <span className="text-[11px]">Evolução</span>
        </button>
      </div>
    </nav>
  );
}
