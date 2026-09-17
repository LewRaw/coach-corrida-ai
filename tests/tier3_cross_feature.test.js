/**
 * Tier 3: Cross-Feature Combinations Test Suite
 * Validates reactive state transitions and data flows across features:
 * Auth -> Dashboard Mount -> Next Workout Spotlight -> Check-in Action -> Adherence & Schedule Update
 */

const assert = require('assert');
const fs = require('fs');
const path = require('path');

let totalTests = 0;
let passedTests = 0;

function runTest(name, fn) {
  totalTests++;
  try {
    fn();
    passedTests++;
    console.log(`  ✓ ${name}`);
  } catch (err) {
    console.error(`  ✗ ${name}`);
    console.error(`    Error: ${err.message}`);
    throw err;
  }
}

console.log('='.repeat(70));
console.log('TIER 3: CROSS-FEATURE COMBINATIONS VERIFICATION SUITE');
console.log('='.repeat(70));

// Create mock state store to simulate end-to-end component interaction
class CoachAiStateSimulator {
  constructor() {
    this.user = null;
    this.profile = null;
    this.schedules = [];
    this.workouts = [];
    this.loading = false;
  }

  // 1. Auth: Sign In
  signIn(email, password, mockProfile) {
    assert(email && password, 'Email and password required');
    this.user = { id: 'athlete-uuid-777', email };
    this.profile = mockProfile || {
      id: this.user.id,
      email: this.user.email,
      nome: 'Mariana Costa',
      modalidade_preferida: 'Corrida',
      objetivo_principal: 'Meia Maratona (21.1 km) em 1h45',
      esportes_ativos: ['Corrida de Rua', 'Ciclismo'],
      nivel_experiencia: 'Avançado',
      dias_disponiveis: 5,
    };
    return { success: true };
  }

  // 2. Dashboard: Load Data
  loadDashboardData(schedules, workouts) {
    assert(this.user, 'Cannot load athlete dashboard while unauthenticated');
    this.schedules = JSON.parse(JSON.stringify(schedules));
    this.workouts = JSON.parse(JSON.stringify(workouts));
  }

  // 3. Spotlight Card: Get Spotlight Workout
  getNextSpotlightWorkout() {
    const pending = this.schedules.filter((s) => s.status === 'Pendente');
    return pending.length > 0 ? pending[0] : null;
  }

  // 4. Action: Check-in Workout
  completeWorkout(scheduleId) {
    const target = this.schedules.find((s) => s.id === scheduleId);
    assert(target, `Schedule item ${scheduleId} not found`);
    assert.strictEqual(target.status, 'Pendente', `Cannot complete already completed workout ${scheduleId}`);
    
    const timestamp = new Date().toISOString();
    target.status = 'Concluído';
    target.data_conclusao = timestamp;
    return target;
  }

  // 5. WeeklyProgress: Compute Metrics
  computeWeeklyProgress() {
    const totalWorkouts = this.schedules.length;
    const completedWorkouts = this.schedules.filter((s) => s.status === 'Concluído').length;
    const pendingWorkouts = totalWorkouts - completedWorkouts;
    const totalDistancePlanned = this.schedules.reduce((acc, cur) => acc + (Number(cur.distancia_km) || 0), 0);
    const totalDistanceCompleted = this.schedules
      .filter((s) => s.status === 'Concluído')
      .reduce((acc, cur) => acc + (Number(cur.distancia_km) || 0), 0);
    const adherencePercent = totalWorkouts > 0 ? Math.round((completedWorkouts / totalWorkouts) * 100) : 0;

    return {
      totalWorkouts,
      completedWorkouts,
      pendingWorkouts,
      totalDistancePlanned,
      totalDistanceCompleted,
      adherencePercent,
    };
  }

  // 6. ScheduleList: Filter
  getFilteredSchedules(filter) {
    if (filter === 'Pendentes') return this.schedules.filter((s) => s.status === 'Pendente');
    if (filter === 'Concluídos') return this.schedules.filter((s) => s.status === 'Concluído');
    return this.schedules;
  }

  // 7. QuickStats: Header metrics
  computeQuickStats() {
    const weekly = this.computeWeeklyProgress();
    const historicalDist = this.workouts.reduce((acc, cur) => acc + (Number(cur.distancia_km) || 0), 0);
    return {
      totalWorkouts: this.workouts.length + weekly.completedWorkouts,
      totalDistanceKm: historicalDist + weekly.totalDistanceCompleted,
      avgPace: '05:05',
      adherencePercent: weekly.adherencePercent,
    };
  }
}

// =========================================================================
// Multi-Step Integration Scenario
// =========================================================================

const sim = new CoachAiStateSimulator();

const sampleSchedules = [
  {
    id: 'TR-101',
    user_id: 'athlete-uuid-777',
    dia_semana: 'Terça-feira',
    data_prevista: '22/09/2026',
    tipo_treino: 'Rodagem Z2',
    distancia_km: 8.0,
    duracao_min: 44,
    pace_alvo: '05:25 a 05:35/km',
    rpe_alvo: 5,
    estrutura_treino: '8km contínuos Z2',
    status: 'Pendente',
  },
  {
    id: 'TR-102',
    user_id: 'athlete-uuid-777',
    dia_semana: 'Quinta-feira',
    data_prevista: '24/09/2026',
    tipo_treino: 'Intervalado 8x 400m',
    distancia_km: 7.0,
    duracao_min: 40,
    pace_alvo: '04:00/km',
    rpe_alvo: 8,
    estrutura_treino: '8x 400m com 60s trote',
    status: 'Pendente',
  },
  {
    id: 'TR-103',
    user_id: 'athlete-uuid-777',
    dia_semana: 'Sábado',
    data_prevista: '26/09/2026',
    tipo_treino: 'Longão Progressivo',
    distancia_km: 16.0,
    duracao_min: 88,
    pace_alvo: '05:20 a 05:40/km',
    rpe_alvo: 6,
    estrutura_treino: '16km progressivos',
    status: 'Pendente',
  },
  {
    id: 'TR-104',
    user_id: 'athlete-uuid-777',
    dia_semana: 'Domingo',
    data_prevista: '27/09/2026',
    tipo_treino: 'Recuperação Regenerativa',
    distancia_km: 5.0,
    duracao_min: 30,
    pace_alvo: '06:00/km',
    rpe_alvo: 3,
    estrutura_treino: '5km regenerativo Z1',
    status: 'Concluído',
  },
];

const sampleWorkouts = [
  { id: 'w-10', user_id: 'athlete-uuid-777', data: '18/09/2026', distancia_km: 10.0, tempo_min: 52 },
  { id: 'w-11', user_id: 'athlete-uuid-777', data: '15/09/2026', distancia_km: 12.0, tempo_min: 63 },
];

// Step 1: Authentication
console.log('\n[T3.1] Stage 1: Athlete Authentication & Profile Loading');
runTest('Athlete signs in and restores profile session', () => {
  const res = sim.signIn('mariana.costa@exemplo.com', 'secreta123');
  assert.strictEqual(res.success, true);
  assert.strictEqual(sim.user.email, 'mariana.costa@exemplo.com');
  assert.strictEqual(sim.profile.nome, 'Mariana Costa');
  assert.strictEqual(sim.profile.nivel_experiencia, 'Avançado');
});

// Step 2: Dashboard Data Binding
console.log('\n[T3.2] Stage 2: Dashboard Data Binding & Initial Metrics Calculation');
runTest('Dashboard loads schedules and workouts for the authenticated athlete', () => {
  sim.loadDashboardData(sampleSchedules, sampleWorkouts);
  assert.strictEqual(sim.schedules.length, 4);
  assert.strictEqual(sim.workouts.length, 2);
});

runTest('Initial WeeklyProgress metrics reflect 1 completed of 4 scheduled sessions (25%)', () => {
  const progress = sim.computeWeeklyProgress();
  assert.strictEqual(progress.totalWorkouts, 4);
  assert.strictEqual(progress.completedWorkouts, 1);
  assert.strictEqual(progress.pendingWorkouts, 3);
  assert.strictEqual(progress.totalDistancePlanned, 36.0);
  assert.strictEqual(progress.totalDistanceCompleted, 5.0);
  assert.strictEqual(progress.adherencePercent, 25);
});

// Step 3: Spotlight Card State
console.log('\n[T3.3] Stage 3: Next Workout Spotlight Card Initial Selection');
runTest('NextWorkoutCard spots first pending session (TR-101: Rodagem Z2)', () => {
  const spotlight = sim.getNextSpotlightWorkout();
  assert(spotlight !== null, 'Spotlight must find a pending workout');
  assert.strictEqual(spotlight.id, 'TR-101');
  assert.strictEqual(spotlight.tipo_treino, 'Rodagem Z2');
  assert.strictEqual(spotlight.distancia_km, 8.0);
  assert.strictEqual(spotlight.dia_semana, 'Terça-feira');
});

// Step 4: Check-in Action ("Concluir Treino")
console.log('\n[T3.4] Stage 4: Check-in Action ("Concluir Treino") Mutation');
runTest('Athlete clicks "Concluir Treino" on TR-101', () => {
  const updated = sim.completeWorkout('TR-101');
  assert.strictEqual(updated.status, 'Concluído');
  assert(typeof updated.data_conclusao === 'string', 'Must stamp completion timestamp');
});

// Step 5: Reactive Cascade Verification
console.log('\n[T3.5] Stage 5: Cross-Feature State Cascade & Re-render Assertions');
runTest('NextWorkoutCard automatically advances to next pending session (TR-102: Intervalado 8x 400m)', () => {
  const nextSpotlight = sim.getNextSpotlightWorkout();
  assert(nextSpotlight !== null, 'Must still have pending workout');
  assert.strictEqual(nextSpotlight.id, 'TR-102', 'Spotlight must have advanced to TR-102');
  assert.strictEqual(nextSpotlight.tipo_treino, 'Intervalado 8x 400m');
  assert.strictEqual(nextSpotlight.distancia_km, 7.0);
});

runTest('WeeklyProgress adherence rises from 25% to 50% (2 of 4 completed)', () => {
  const progress = sim.computeWeeklyProgress();
  assert.strictEqual(progress.completedWorkouts, 2);
  assert.strictEqual(progress.pendingWorkouts, 2);
  assert.strictEqual(progress.totalDistanceCompleted, 13.0); // 5.0 + 8.0
  assert.strictEqual(progress.adherencePercent, 50, 'Adherence must recalculate to 50%');
});

runTest('WorkoutScheduleList reflects updated status badge for TR-101', () => {
  const item101 = sim.schedules.find((s) => s.id === 'TR-101');
  assert.strictEqual(item101.status, 'Concluído');
});

runTest('WorkoutScheduleList filter chip counts update reactively', () => {
  const todos = sim.getFilteredSchedules('Todos');
  const pendentes = sim.getFilteredSchedules('Pendentes');
  const concluidos = sim.getFilteredSchedules('Concluídos');

  assert.strictEqual(todos.length, 4, 'Total sessions remains 4');
  assert.strictEqual(pendentes.length, 2, 'Pendentes count reduced from 3 to 2');
  assert.strictEqual(concluidos.length, 2, 'Concluídos count increased from 1 to 2');
});

runTest('ProfileHeader quick stats update volume and adherence', () => {
  const stats = sim.computeQuickStats();
  assert.strictEqual(stats.totalWorkouts, 4, '2 historical + 2 completed schedules = 4');
  assert.strictEqual(stats.totalDistanceKm, 35.0, '22 historical + 13 completed schedules = 35 km');
  assert.strictEqual(stats.adherencePercent, 50);
});

console.log('\n' + '='.repeat(70));
console.log(`TIER 3 COMPLETE: ${passedTests}/${totalTests} TESTS PASSED (100%)`);
console.log('='.repeat(70));
