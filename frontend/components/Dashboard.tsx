'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useToast } from '@/context/ToastContext';
import { Schedule, Workout, QuickStats } from '@/lib/types';
import { DEMO_SCHEDULES, DEMO_WORKOUTS } from '@/lib/supabase';
import {
  getSchedulesServerAction,
  getWorkoutsServerAction,
  markWorkoutCompletedServerAction,
} from '@/app/actions/auth-actions';
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
  const { showToast } = useToast();
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [selectedWorkout, setSelectedWorkout] = useState<Schedule | null>(null);
  const [currentTab, setCurrentTab] = useState<'home' | 'schedule' | 'stats'>('home');
  const [loading, setLoading] = useState(true);

  // Load schedules and workouts directly via Server Actions (Bypassing browser RLS)
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      if (isDemoMode || !user) {
        setSchedules(DEMO_SCHEDULES);
        setWorkouts(DEMO_WORKOUTS);
      } else {
        const [schedRes, workRes] = await Promise.all([
          getSchedulesServerAction(user.id),
          getWorkoutsServerAction(user.id),
        ]);

        if (schedRes.success && schedRes.schedules.length > 0) {
          setSchedules(schedRes.schedules as Schedule[]);
        } else if (isDemoMode) {
          setSchedules(DEMO_SCHEDULES);
        } else {
          setSchedules([]);
        }

        if (workRes.success && workRes.workouts.length > 0) {
          setWorkouts(workRes.workouts as Workout[]);
        } else if (isDemoMode) {
          setWorkouts(DEMO_WORKOUTS);
        } else {
          setWorkouts([]);
        }
      }
    } catch (err) {
      console.warn('Error loading dashboard data, falling back:', err);
      if (isDemoMode) {
        setSchedules(DEMO_SCHEDULES);
        setWorkouts(DEMO_WORKOUTS);
      }
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
      await markWorkoutCompletedServerAction(scheduleId, user.id);
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
      showToast('Link de login permanente copiado para a área de transferência!', 'success');
    } else {
      showToast('Faça login com sua conta para gerar o atalho permanente.', 'info');
    }
  };

  return (
    <div className="max-w-md mx-auto min-h-screen pb-28 pt-2 px-3.5 transition-colors duration-150">
      {/* PWA Banner (Flat PicPay Neutral Style) */}
      <div className="mb-3 bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] rounded-2xl p-3 flex items-center justify-between gap-2.5 shadow-xs">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-8 h-8 rounded-xl bg-[#11C76F]/15 text-[#11C76F] flex items-center justify-center shrink-0">
            <Smartphone className="w-4 h-4" />
          </div>
          <p className="text-[11px] text-slate-800 dark:text-white leading-tight font-medium truncate">
            Instale o app na sua tela de início
          </p>
        </div>
        <button
          onClick={handleCreateShortcut}
          className="px-3 py-1.5 bg-[#11C76F] hover:bg-[#0ea85d] text-white rounded-xl text-xs font-bold transition-all shrink-0 flex items-center gap-1 shadow-xs"
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
            <div className="bg-white dark:bg-[#141414] border border-slate-200 dark:border-[#262626] rounded-3xl p-5 shadow-xs">
              <h3 className="text-base font-bold text-slate-900 dark:text-white mb-1 flex items-center gap-2">
                <Activity className="w-4 h-4 text-[#11C76F]" />
                Histórico & Evolução Física
              </h3>
              <p className="text-xs text-slate-500 dark:text-[#8E8E93] leading-relaxed mb-4">
                Sessões de corrida executadas e evolução aeróbica calculada pela assessoria.
              </p>

              <div className="grid grid-cols-2 gap-2 mb-4">
                <div className="bg-slate-50 dark:bg-[#1c1c1c] p-3 rounded-2xl border border-slate-100 dark:border-[#242424] text-center">
                  <div className="text-[10px] uppercase font-bold text-slate-400 mb-0.5">Volume Total</div>
                  <div className="text-xl font-black text-slate-900 dark:text-white">{quickStats.totalDistanceKm.toFixed(1)} km</div>
                </div>
                <div className="bg-slate-50 dark:bg-[#1c1c1c] p-3 rounded-2xl border border-slate-100 dark:border-[#242424] text-center">
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
                    className="p-3 rounded-2xl bg-slate-50 dark:bg-[#1c1c1c] border border-slate-100 dark:border-[#242424] flex items-center justify-between text-xs"
                  >
                    <div>
                      <div className="font-bold text-slate-900 dark:text-white">{w.data}</div>
                      <div className="text-slate-400 text-[11px]">{w.zona_predominante || 'Rodagem'}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-[#11C76F]">{Number(w.distancia_km).toFixed(1)} km</div>
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
