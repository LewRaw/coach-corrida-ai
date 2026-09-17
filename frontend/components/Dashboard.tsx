'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Schedule, Workout, QuickStats } from '@/lib/types';
import {
  DEMO_SCHEDULES,
  DEMO_WORKOUTS,
  getSchedules,
  getWorkouts,
  markWorkoutCompleted,
} from '@/lib/supabase';
import ProfileHeader from './ProfileHeader';
import NextWorkoutCard from './NextWorkoutCard';
import WeeklyProgress from './WeeklyProgress';
import WorkoutScheduleList from './WorkoutScheduleList';
import WorkoutDetailModal from './WorkoutDetailModal';
import BottomNav from './BottomNav';
import ChatPopup from './ChatPopup';
import { Activity, Download, Smartphone } from 'lucide-react';

export default function Dashboard() {
  const { user, profile, isDemoMode } = useAuth();
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [selectedWorkout, setSelectedWorkout] = useState<Schedule | null>(null);
  const [currentTab, setCurrentTab] = useState<'home' | 'schedule' | 'stats'>('home');
  const [loading, setLoading] = useState(true);

  // Load schedules and workouts
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      if (isDemoMode || !user) {
        setSchedules(DEMO_SCHEDULES);
        setWorkouts(DEMO_WORKOUTS);
      } else {
        const [fetchedSchedules, fetchedWorkouts] = await Promise.all([
          getSchedules(user.id),
          getWorkouts(user.id),
        ]);

        if (fetchedSchedules.length === 0) {
          setSchedules(DEMO_SCHEDULES);
        } else {
          setSchedules(fetchedSchedules);
        }

        if (fetchedWorkouts.length === 0) {
          setWorkouts(DEMO_WORKOUTS);
        } else {
          setWorkouts(fetchedWorkouts);
        }
      }
    } catch (err) {
      console.warn('Error loading dashboard data, falling back to demo data:', err);
      setSchedules(DEMO_SCHEDULES);
      setWorkouts(DEMO_WORKOUTS);
    } finally {
      setLoading(false);
    }
  }, [user, isDemoMode]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle completing a workout
  const handleCompleteWorkout = async (scheduleId: string) => {
    const timestamp = new Date().toISOString();

    setSchedules((prev) =>
      prev.map((s) =>
        s.id === scheduleId
          ? { ...s, status: 'Concluído', data_conclusao: timestamp }
          : s
      )
    );

    if (selectedWorkout && selectedWorkout.id === scheduleId) {
      setSelectedWorkout((prev) =>
        prev ? { ...prev, status: 'Concluído', data_conclusao: timestamp } : null
      );
    }

    if (!isDemoMode && user) {
      await markWorkoutCompleted(scheduleId);
    }
  };

  // Compute QuickStats
  const totalCompletedSchedules = schedules.filter((s) => s.status === 'Concluído').length;
  const totalSchedules = schedules.length;
  const adherencePercent =
    totalSchedules > 0 ? Math.round((totalCompletedSchedules / totalSchedules) * 100) : 0;

  const totalHistoricalDist = workouts.reduce(
    (acc, cur) => acc + (Number(cur.distancia_km) || 0),
    0
  );
  const totalScheduleCompletedDist = schedules
    .filter((s) => s.status === 'Concluído')
    .reduce((acc, cur) => acc + (Number(cur.distancia_km) || 0), 0);

  const quickStats: QuickStats = {
    totalWorkouts: workouts.length + totalCompletedSchedules,
    totalDistanceKm: totalHistoricalDist + totalScheduleCompletedDist,
    avgPace: '05:18',
    adherencePercent,
  };

  const handleCreateShortcut = () => {
    if (profile?.auth_token) {
      const pwaUrl = `${window.location.origin}/?token=${profile.auth_token}`;
      navigator.clipboard?.writeText(pwaUrl);
      alert(`Link de atalho permanente copiado para a área de transferência!\n\n${pwaUrl}\n\nCole no seu navegador e selecione "Adicionar à Tela de Início" para login automático.`);
    } else {
      alert('Para gerar atalho com login permanente, faça login com sua conta.');
    }
  };

  return (
    <div className="max-w-md mx-auto min-h-screen pb-28 pt-2 px-3.5 transition-colors duration-200">
      {/* PWA Banner */}
      <div className="mb-3 bg-emerald-50/80 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/40 rounded-2xl p-3 flex items-center justify-between gap-2.5 shadow-sm">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-8 h-8 rounded-xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
            <Smartphone className="w-4 h-4" />
          </div>
          <p className="text-[11px] text-emerald-800 dark:text-emerald-200/90 leading-tight font-medium truncate">
            Instale o app na sua tela de início
          </p>
        </div>
        <button
          onClick={handleCreateShortcut}
          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition-all shrink-0 flex items-center gap-1 shadow-sm"
        >
          <Download className="w-3.5 h-3.5" />
          Atalho
        </button>
      </div>

      <ProfileHeader stats={quickStats} />

      <main className="space-y-4 mt-3">
        {/* Tab 1: Home View */}
        {currentTab === 'home' && (
          <>
            <NextWorkoutCard
              schedules={schedules}
              onCompleteWorkout={handleCompleteWorkout}
              onSelectWorkout={(w) => setSelectedWorkout(w)}
            />

            <WeeklyProgress schedules={schedules} />

            <WorkoutScheduleList
              schedules={schedules}
              onCompleteWorkout={handleCompleteWorkout}
              onSelectWorkout={(w) => setSelectedWorkout(w)}
              userId={user?.id || 'demo-athlete-001'}
              onReload={loadData}
            />
          </>
        )}

        {/* Tab 2: Cronograma View */}
        {currentTab === 'schedule' && (
          <>
            <WeeklyProgress schedules={schedules} />
            <WorkoutScheduleList
              schedules={schedules}
              onCompleteWorkout={handleCompleteWorkout}
              onSelectWorkout={(w) => setSelectedWorkout(w)}
              userId={user?.id || 'demo-athlete-001'}
              onReload={loadData}
            />
          </>
        )}

        {/* Tab 3: Evolução / Stats View */}
        {currentTab === 'stats' && (
          <section className="space-y-3">
            <div className="bg-white dark:bg-[#141d18] border border-slate-200 dark:border-[#23312a] rounded-3xl p-5 shadow-sm">
              <h3 className="text-base font-bold text-slate-900 dark:text-white mb-1 flex items-center gap-2">
                <Activity className="w-4 h-4 text-emerald-500" />
                Histórico & Evolução Física
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mb-4">
                Sessões de corrida executadas e evolução aeróbica calculada pela assessoria.
              </p>

              <div className="grid grid-cols-2 gap-2 mb-4">
                <div className="bg-slate-50 dark:bg-[#0e1411] p-3 rounded-2xl border border-slate-100 dark:border-[#1d2922] text-center">
                  <div className="text-[10px] uppercase font-bold text-slate-400 mb-0.5">Volume Total</div>
                  <div className="text-xl font-black text-slate-900 dark:text-white">{quickStats.totalDistanceKm.toFixed(1)} km</div>
                </div>
                <div className="bg-slate-50 dark:bg-[#0e1411] p-3 rounded-2xl border border-slate-100 dark:border-[#1d2922] text-center">
                  <div className="text-[10px] uppercase font-bold text-slate-400 mb-0.5">Pace Médio</div>
                  <div className="text-xl font-black text-slate-900 dark:text-white">{quickStats.avgPace}/km</div>
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                  Últimos Treinos Registrados
                </h4>
                {workouts.map((w) => (
                  <div
                    key={w.id}
                    className="p-3 rounded-2xl bg-slate-50 dark:bg-[#0e1411] border border-slate-100 dark:border-[#1d2922] flex items-center justify-between text-xs"
                  >
                    <div>
                      <div className="font-bold text-slate-900 dark:text-white">{w.data}</div>
                      <div className="text-slate-400 text-[11px]">{w.zona_predominante || 'Rodagem'}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-emerald-600 dark:text-emerald-400">{Number(w.distancia_km).toFixed(1)} km</div>
                      <div className="text-slate-400 text-[11px]">{w.pace_medio}/km</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}
      </main>

      {/* Workout Detail Modal */}
      <WorkoutDetailModal
        workout={selectedWorkout}
        onClose={() => setSelectedWorkout(null)}
        onComplete={handleCompleteWorkout}
        userId={user?.id || 'demo-athlete-001'}
      />

      {/* Floating Chat */}
      <ChatPopup />

      {/* Bottom Navigation */}
      <BottomNav currentTab={currentTab} onTabChange={setCurrentTab} />
    </div>
  );
}
