/**
 * Tier 4: Real-World Application Scenarios Test Suite
 * Simulates a realistic athlete microcycle workflow over a full training week:
 * Athlete signs in, views prescribed training microcycle, progressively completes
 * 4 training sessions (Base, Intervals, Tempo, Long Run), observes dynamic adherence
 * and volume progression from 0% to 100%, and verifies celebration completion state
 * and schedule list filtering.
 */

const assert = require('assert');

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
console.log('TIER 4: REAL-WORLD APPLICATION SCENARIO VERIFICATION SUITE');
console.log('='.repeat(70));

class AthleteMicrocycleWorkflow {
  constructor(athleteName, targetGoal) {
    this.athlete = {
      name: athleteName,
      goal: targetGoal,
      experience: 'Intermediário',
      sports: ['Corrida de Rua'],
    };

    this.schedules = [
      {
        id: 'MIC-01',
        dia_semana: 'Terça-feira',
        data_prevista: '22/09/2026',
        tipo_treino: 'Rodagem Base Aeróbica Z2',
        distancia_km: 8.0,
        duracao_min: 45,
        pace_alvo: '05:35 a 05:45/km',
        rpe_alvo: 4,
        estrutura_treino: 'Aquecimento 1km Z1 + 6km contínuos Z2 + Soltura 1km',
        status: 'Pendente',
        data_conclusao: null,
      },
      {
        id: 'MIC-02',
        dia_semana: 'Quinta-feira',
        data_prevista: '24/09/2026',
        tipo_treino: 'Intervalado VO2 Max (6x 800m)',
        distancia_km: 9.0,
        duracao_min: 50,
        pace_alvo: '04:15 a 04:25/km',
        rpe_alvo: 8,
        estrutura_treino: '2km Z2 + 6x 800m a 04:20 com 90s trote + 1.5km Z1',
        status: 'Pendente',
        data_conclusao: null,
      },
      {
        id: 'MIC-03',
        dia_semana: 'Sábado',
        data_prevista: '26/09/2026',
        tipo_treino: 'Treino Ritmo / Limiar Anaeróbio',
        distancia_km: 12.0,
        duracao_min: 60,
        pace_alvo: '04:55 a 05:05/km',
        rpe_alvo: 7,
        estrutura_treino: '2km Z2 + 8km ritmo firme limiar + 2km soltura',
        status: 'Pendente',
        data_conclusao: null,
      },
      {
        id: 'MIC-04',
        dia_semana: 'Domingo',
        data_prevista: '27/09/2026',
        tipo_treino: 'Longão Aeróbico de Resistência',
        distancia_km: 18.0,
        duracao_min: 105,
        pace_alvo: '05:45 a 06:00/km',
        rpe_alvo: 6,
        estrutura_treino: '18km contínuos Z2 com hidratação a cada 3km',
        status: 'Pendente',
        data_conclusao: null,
      },
    ];

    this.historicalWorkouts = [
      { id: 'h-1', distancia_km: 10.0, pace_medio: '05:15' },
      { id: 'h-2', distancia_km: 15.0, pace_medio: '05:30' },
      { id: 'h-3', distancia_km: 8.0, pace_medio: '05:10' },
    ];
  }

  getSpotlightWorkout() {
    const pendentes = this.schedules.filter((s) => s.status === 'Pendente');
    return pendentes.length > 0 ? pendentes[0] : null;
  }

  isCelebrationActive() {
    return this.schedules.length > 0 && this.getSpotlightWorkout() === null;
  }

  completeSession(scheduleId) {
    const session = this.schedules.find((s) => s.id === scheduleId);
    assert(session, `Session ${scheduleId} not found`);
    session.status = 'Concluído';
    session.data_conclusao = new Date().toISOString();
  }

  getWeeklyMetrics() {
    const total = this.schedules.length;
    const completed = this.schedules.filter((s) => s.status === 'Concluído').length;
    const pending = total - completed;
    const totalDistPlanned = this.schedules.reduce((acc, cur) => acc + cur.distancia_km, 0);
    const totalDistDone = this.schedules
      .filter((s) => s.status === 'Concluído')
      .reduce((acc, cur) => acc + cur.distancia_km, 0);
    const adherence = total > 0 ? Math.round((completed / total) * 100) : 0;

    return {
      total,
      completed,
      pending,
      totalDistPlanned,
      totalDistDone,
      adherence,
    };
  }

  filterList(filter) {
    if (filter === 'Pendentes') return this.schedules.filter((s) => s.status === 'Pendente');
    if (filter === 'Concluídos') return this.schedules.filter((s) => s.status === 'Concluído');
    return this.schedules;
  }
}

const cycle = new AthleteMicrocycleWorkflow(
  'Lucas Mendonça',
  'Meia Maratona (21.1 km) sub 1h45'
);

// Scenario Step 0: Initial Microcycle State
console.log('\n[T4.1] Stage 0: Microcycle Setup & Initial Baseline');
runTest('Initial state: 0/4 completed, 0% adherence, 0.0/47.0 km done', () => {
  const m = cycle.getWeeklyMetrics();
  assert.strictEqual(m.total, 4);
  assert.strictEqual(m.completed, 0);
  assert.strictEqual(m.pending, 4);
  assert.strictEqual(m.totalDistPlanned, 47.0);
  assert.strictEqual(m.totalDistDone, 0.0);
  assert.strictEqual(m.adherence, 0);
});

runTest('Initial spotlight hero targets Tuesday Base Run (MIC-01)', () => {
  const spotlight = cycle.getSpotlightWorkout();
  assert(spotlight !== null);
  assert.strictEqual(spotlight.id, 'MIC-01');
  assert.strictEqual(spotlight.tipo_treino, 'Rodagem Base Aeróbica Z2');
  assert.strictEqual(spotlight.distancia_km, 8.0);
  assert.strictEqual(cycle.isCelebrationActive(), false);
});

// Scenario Step 1: Tuesday Workout
console.log('\n[T4.2] Stage 1: Tuesday Workout Completion (Base Run)');
runTest('Lucas completes Tuesday Base Run (8.0 km)', () => {
  cycle.completeSession('MIC-01');
  const m = cycle.getWeeklyMetrics();
  assert.strictEqual(m.completed, 1);
  assert.strictEqual(m.pending, 3);
  assert.strictEqual(m.totalDistDone, 8.0);
  assert.strictEqual(m.adherence, 25);
});

runTest('Spotlight advances to Thursday Intervals (MIC-02)', () => {
  const spotlight = cycle.getSpotlightWorkout();
  assert.strictEqual(spotlight.id, 'MIC-02');
  assert.strictEqual(spotlight.tipo_treino, 'Intervalado VO2 Max (6x 800m)');
  assert.strictEqual(spotlight.distancia_km, 9.0);
  assert.strictEqual(spotlight.rpe_alvo, 8);
});

// Scenario Step 2: Thursday Workout
console.log('\n[T4.3] Stage 2: Thursday Workout Completion (VO2 Max Intervals)');
runTest('Lucas completes Thursday Interval Session (9.0 km)', () => {
  cycle.completeSession('MIC-02');
  const m = cycle.getWeeklyMetrics();
  assert.strictEqual(m.completed, 2);
  assert.strictEqual(m.pending, 2);
  assert.strictEqual(m.totalDistDone, 17.0);
  assert.strictEqual(m.adherence, 50);
});

runTest('Spotlight advances to Saturday Tempo Run (MIC-03)', () => {
  const spotlight = cycle.getSpotlightWorkout();
  assert.strictEqual(spotlight.id, 'MIC-03');
  assert.strictEqual(spotlight.tipo_treino, 'Treino Ritmo / Limiar Anaeróbio');
  assert.strictEqual(spotlight.distancia_km, 12.0);
  assert.strictEqual(spotlight.pace_alvo, '04:55 a 05:05/km');
});

// Scenario Step 3: Saturday Workout
console.log('\n[T4.4] Stage 3: Saturday Workout Completion (Tempo / Threshold)');
runTest('Lucas completes Saturday Tempo Session (12.0 km)', () => {
  cycle.completeSession('MIC-03');
  const m = cycle.getWeeklyMetrics();
  assert.strictEqual(m.completed, 3);
  assert.strictEqual(m.pending, 1);
  assert.strictEqual(m.totalDistDone, 29.0);
  assert.strictEqual(m.adherence, 75);
});

runTest('Spotlight advances to Sunday Long Run (MIC-04)', () => {
  const spotlight = cycle.getSpotlightWorkout();
  assert.strictEqual(spotlight.id, 'MIC-04');
  assert.strictEqual(spotlight.tipo_treino, 'Longão Aeróbico de Resistência');
  assert.strictEqual(spotlight.distancia_km, 18.0);
  assert.strictEqual(spotlight.duracao_min, 105);
});

// Scenario Step 4: Sunday Workout & Celebration
console.log('\n[T4.5] Stage 4: Sunday Long Run & Microcycle Celebration');
runTest('Lucas completes Sunday Long Run (18.0 km) reaching 100% adherence', () => {
  cycle.completeSession('MIC-04');
  const m = cycle.getWeeklyMetrics();
  assert.strictEqual(m.completed, 4);
  assert.strictEqual(m.pending, 0);
  assert.strictEqual(m.totalDistDone, 47.0);
  assert.strictEqual(m.adherence, 100);
});

runTest('Spotlight transitions to Celebration Mode', () => {
  const spotlight = cycle.getSpotlightWorkout();
  assert.strictEqual(spotlight, null, 'No pending workouts remain');
  assert.strictEqual(cycle.isCelebrationActive(), true, 'Celebration banner must activate');
});

// Scenario Step 5: Schedule Filtering State Verification
console.log('\n[T4.6] Stage 5: Final Schedule List Filtering & Adherence Auditing');
runTest('Filter "Todos" returns all 4 prescribed workouts', () => {
  const todos = cycle.filterList('Todos');
  assert.strictEqual(todos.length, 4);
  assert(todos.every((s) => s.status === 'Concluído'));
});

runTest('Filter "Pendentes" returns 0 workouts', () => {
  const pendentes = cycle.filterList('Pendentes');
  assert.strictEqual(pendentes.length, 0);
});

runTest('Filter "Concluídos" returns all 4 workouts with valid completion timestamps', () => {
  const concluidos = cycle.filterList('Concluídos');
  assert.strictEqual(concluidos.length, 4);
  for (const s of concluidos) {
    assert(s.data_conclusao !== null);
    assert(typeof s.data_conclusao === 'string');
    assert(!Number.isNaN(Date.parse(s.data_conclusao)));
  }
});

console.log('\n' + '='.repeat(70));
console.log(`TIER 4 COMPLETE: ${passedTests}/${totalTests} TESTS PASSED (100%)`);
console.log('='.repeat(70));
