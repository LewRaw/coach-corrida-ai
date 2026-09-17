'use client';

import React from 'react';
import { Home, Calendar, Activity } from 'lucide-react';

interface BottomNavProps {
  currentTab: 'home' | 'schedule' | 'stats';
  onTabChange: (tab: 'home' | 'schedule' | 'stats') => void;
}

export default function BottomNav({ currentTab, onTabChange }: BottomNavProps) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 bg-surface/95 backdrop-blur-md border-t border-surface-border pb-safe-bottom">
      <div className="max-w-md mx-auto flex items-center justify-around px-2 py-1.5">
        <button
          type="button"
          onClick={() => onTabChange('home')}
          className={`flex-1 flex flex-col items-center justify-center py-1.5 px-2 rounded-xl transition-all min-h-[48px] ${
            currentTab === 'home'
              ? 'text-primary-400 font-bold'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Home className="w-5 h-5 mb-0.5" />
          <span className="text-[11px]">Início</span>
        </button>

        <button
          type="button"
          onClick={() => onTabChange('schedule')}
          className={`flex-1 flex flex-col items-center justify-center py-1.5 px-2 rounded-xl transition-all min-h-[48px] ${
            currentTab === 'schedule'
              ? 'text-primary-400 font-bold'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Calendar className="w-5 h-5 mb-0.5" />
          <span className="text-[11px]">Cronograma</span>
        </button>

        <button
          type="button"
          onClick={() => onTabChange('stats')}
          className={`flex-1 flex flex-col items-center justify-center py-1.5 px-2 rounded-xl transition-all min-h-[48px] ${
            currentTab === 'stats'
              ? 'text-primary-400 font-bold'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Activity className="w-5 h-5 mb-0.5" />
          <span className="text-[11px]">Evolução</span>
        </button>
      </div>
    </nav>
  );
}
