'use client';

import React from 'react';
import { useAuth } from '@/context/AuthContext';
import AuthModal from '@/components/AuthModal';
import Dashboard from '@/components/Dashboard';

export default function HomePage() {
  const { user, isDemoMode, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-slate-400 font-medium">Iniciando Coach AI...</p>
        </div>
      </div>
    );
  }

  if (!user && !isDemoMode) {
    return <AuthModal />;
  }

  return <Dashboard />;
}
