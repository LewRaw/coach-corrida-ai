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
import { Award, Zap, History, Flame, Activity } from 'lucide-react';

export default function Dashboard() {
  const { user, isDemoMode } = useAuth();
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
          // Fallback to sample microcycle if user has none yet
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

    // Optimistic / local update
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-slate-400 font-medium">Carregando painel do atleta...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-slate-100 pb-24">
      <main className="max-w-md mx-auto px-4 space-y-5">
        {/* Profile Header and Quick Stats */}
        <ProfileHeader stats={quickStats} />

        {/* Tab 1: Home View */}
        {currentTab === 'home' && (
          <>
            {/* Next Workout Spotlight Hero Card */}
            <NextWorkoutCard
              schedules={schedules}
              onCompleteWorkout={handleCompleteWorkout}
              onSelectWorkout={(w) => setSelectedWorkout(w)}
            />

            {/* Weekly Adherence Progress */}
            <WeeklyProgress schedules={schedules} />

            {/* Schedule List */}
            <WorkoutScheduleList
              schedules={schedules}
              onCompleteWorkout={handleCompleteWorkout}
              onSelectWorkout={(w) => setSelectedWorkout(w)}
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
            />
          </>
        )}

        {/* Tab 3: Evolução / Stats View */}
        {currentTab === 'stats' && (
          <section className="space-y-4">
            <div className="bg-surface-card border border-surface-border rounded-2xl p-5">
              <h3 className="text-base font-bold text-white mb-2 flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary-400" />
                Histórico & Evolução Física
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Registro detalhado das sessões de corrida executadas e evolução aeróbica calculada pela assessoria.
              </p>

              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-surface p-3 rounded-xl border border-surface-border text-center">
                  <div className="text-[10px] uppercase font-bold text-slate-400 mb-1">Volume Total</div>
                  <div className="text-xl font-black text-white">{quickStats.totalDistanceKm.toFixed(1)} km</div>
                </div>
                <div className="bg-surface p-3 rounded-xl border border-surface-border text-center">
                  <div className="text-[10px] uppercase font-bold text-slate-400 mb-1">Pace Médio</div>
                  <div className="text-xl font-black text-white">{quickStats.avgPace}/km</div>
                </div>
              </div>

              <div className="space-y-2.5">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Últimos Treinos Registrados
                </h4>
                {workouts.map((w) => (
                  <div
                    key={w.id}
                    className="p-3 rounded-xl bg-surface border border-surface-border flex items-center justify-between text-xs"
                  >
                    <div>
                      <div className="font-bold text-white">{w.data}</div>
                      <div className="text-slate-400 text-[11px]">{w.zona_predominante || 'Rodagem'}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-primary-400">{w.distancia_km.toFixed(1)} km</div>
                      <div className="text-slate-400 text-[11px]">{w.pace_medio}/km</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}
      </main>

      {/* Workout Detail Modal / Drawer */}
      <WorkoutDetailModal
        workout={selectedWorkout}
        onClose={() => setSelectedWorkout(null)}
        onComplete={handleCompleteWorkout}
      />

      {/* Bottom Navigation */}
      <BottomNav currentTab={currentTab} onTabChange={setCurrentTab} />
    </div>
  );
}
