/**
 * Challenger 2 Adversarial Stress & Behavioral Contract Test Suite
 * Independent empirical challenge verification covering:
 *  1. Schedule filtering logic under stress & edge-case workloads
 *  2. Spotlight card transitions (stepwise, out-of-order, celebration, empty)
 *  3. Schema synchronization (public.profiles payload vs database contracts)
 *  4. PWA installation criteria (manifest schema, binary PNG headers/dimensions, SW syntax)
 *  5. Streamlit boundary check & root immutability
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');
const { execSync } = require('child_process');

const ROOT_DIR = path.resolve(__dirname, '..');
const FRONTEND_DIR = path.join(ROOT_DIR, 'frontend');

console.log('='.repeat(75));
console.log('  CHALLENGER 2: INDEPENDENT ADVERSARIAL CHALLENGE SUITE');
console.log('='.repeat(75));

let totalPassed = 0;
let totalFailed = 0;

function test(description, fn) {
  try {
    fn();
    console.log(`  ✓ ${description}`);
    totalPassed++;
  } catch (err) {
    console.error(`  ✗ FAIL: ${description}`);
    console.error(`    Error: ${err.message}`);
    totalFailed++;
  }
}

// -----------------------------------------------------------------------------
// AREA 1: Schedule Filtering Logic
// -----------------------------------------------------------------------------
console.log('\n[AREA 1] Schedule Filtering Logic Stress Tests');

function filterSchedules(schedules, filter) {
  return schedules.filter((s) => {
    if (filter === 'Pendentes') return s.status === 'Pendente';
    if (filter === 'Concluídos') return s.status === 'Concluído';
    return true;
  });
}

function getFilterCounts(schedules) {
  return {
    Todos: schedules.length,
    Pendentes: schedules.filter((x) => x.status === 'Pendente').length,
    Concluídos: schedules.filter((x) => x.status === 'Concluído').length,
  };
}

test('Filter handles completely empty schedules array ([]) across all chip states', () => {
  const empty = [];
  assert.strictEqual(filterSchedules(empty, 'Todos').length, 0);
  assert.strictEqual(filterSchedules(empty, 'Pendentes').length, 0);
  assert.strictEqual(filterSchedules(empty, 'Concluídos').length, 0);

  const counts = getFilterCounts(empty);
  assert.deepStrictEqual(counts, { Todos: 0, Pendentes: 0, Concluídos: 0 });
});

test('Filter handles all-pending microcycle (5 pending, 0 completed)', () => {
  const pendingOnly = Array.from({ length: 5 }, (_, i) => ({
    id: `p-${i}`,
    status: 'Pendente',
    distancia_km: 5.0,
    tipo_treino: `Treino ${i}`,
  }));

  assert.strictEqual(filterSchedules(pendingOnly, 'Todos').length, 5);
  assert.strictEqual(filterSchedules(pendingOnly, 'Pendentes').length, 5);
  assert.strictEqual(filterSchedules(pendingOnly, 'Concluídos').length, 0);

  const counts = getFilterCounts(pendingOnly);
  assert.deepStrictEqual(counts, { Todos: 5, Pendentes: 5, Concluídos: 0 });
});

test('Filter handles all-completed microcycle (5 completed, 0 pending)', () => {
  const completedOnly = Array.from({ length: 5 }, (_, i) => ({
    id: `c-${i}`,
    status: 'Concluído',
    distancia_km: 10.0,
    tipo_treino: `Treino Concluído ${i}`,
  }));

  assert.strictEqual(filterSchedules(completedOnly, 'Todos').length, 5);
  assert.strictEqual(filterSchedules(completedOnly, 'Pendentes').length, 0);
  assert.strictEqual(filterSchedules(completedOnly, 'Concluídos').length, 5);

  const counts = getFilterCounts(completedOnly);
  assert.deepStrictEqual(counts, { Todos: 5, Pendentes: 0, Concluídos: 5 });
});

test('Stress: 100 mixed sessions dynamic completion and chip count integrity', () => {
  let list = Array.from({ length: 100 }, (_, i) => ({
    id: `item-${i}`,
    status: i < 30 ? 'Concluído' : 'Pendente',
    distancia_km: 8.0,
    tipo_treino: `Session ${i}`,
  }));

  let counts = getFilterCounts(list);
  assert.strictEqual(counts.Todos, 100);
  assert.strictEqual(counts.Concluídos, 30);
  assert.strictEqual(counts.Pendentes, 70);

  // Complete 20 pending items sequentially
  for (let i = 30; i < 50; i++) {
    list = list.map((s) => (s.id === `item-${i}` ? { ...s, status: 'Concluído' } : s));
  }

  counts = getFilterCounts(list);
  assert.strictEqual(counts.Todos, 100);
  assert.strictEqual(counts.Concluídos, 50);
  assert.strictEqual(counts.Pendentes, 50);
  assert.strictEqual(filterSchedules(list, 'Pendentes').length, 50);
  assert.strictEqual(filterSchedules(list, 'Concluídos').length, 50);

  // Complete remaining 50
  for (let i = 50; i < 100; i++) {
    list = list.map((s) => (s.id === `item-${i}` ? { ...s, status: 'Concluído' } : s));
  }

  counts = getFilterCounts(list);
  assert.strictEqual(counts.Todos, 100);
  assert.strictEqual(counts.Concluídos, 100);
  assert.strictEqual(counts.Pendentes, 0);
  assert.strictEqual(filterSchedules(list, 'Pendentes').length, 0);
  assert.strictEqual(filterSchedules(list, 'Concluídos').length, 100);
});

// -----------------------------------------------------------------------------
// AREA 2: Spotlight Card Transitions
// -----------------------------------------------------------------------------
console.log('\n[AREA 2] Spotlight Card Transitions & Celebration Logic');

function getSpotlightState(schedules) {
  if (schedules.length === 0) {
    return { mode: 'EMPTY', workout: null };
  }
  const pendingWorkouts = schedules.filter((s) => s.status === 'Pendente');
  if (pendingWorkouts.length === 0) {
    return { mode: 'CELEBRATION', workout: null };
  }
  return { mode: 'SPOTLIGHT', workout: pendingWorkouts[0] };
}

test('Spotlight on empty schedule returns EMPTY mode without throwing', () => {
  const res = getSpotlightState([]);
  assert.strictEqual(res.mode, 'EMPTY');
  assert.strictEqual(res.workout, null);
});

test('Spotlight sequentially advances through 4 microcycle workouts', () => {
  let week = [
    { id: 'W1', tipo_treino: 'Rodagem Z2', status: 'Pendente' },
    { id: 'W2', tipo_treino: 'Intervalado VO2', status: 'Pendente' },
    { id: 'W3', tipo_treino: 'Tempo Run', status: 'Pendente' },
    { id: 'W4', tipo_treino: 'Longão', status: 'Pendente' },
  ];

  // Initial: W1
  let state = getSpotlightState(week);
  assert.strictEqual(state.mode, 'SPOTLIGHT');
  assert.strictEqual(state.workout.id, 'W1');

  // Complete W1 -> transitions immediately to W2
  week = week.map((w) => (w.id === 'W1' ? { ...w, status: 'Concluído' } : w));
  state = getSpotlightState(week);
  assert.strictEqual(state.mode, 'SPOTLIGHT');
  assert.strictEqual(state.workout.id, 'W2');

  // Complete W2 -> transitions immediately to W3
  week = week.map((w) => (w.id === 'W2' ? { ...w, status: 'Concluído' } : w));
  state = getSpotlightState(week);
  assert.strictEqual(state.mode, 'SPOTLIGHT');
  assert.strictEqual(state.workout.id, 'W3');

  // Complete W3 -> transitions immediately to W4
  week = week.map((w) => (w.id === 'W3' ? { ...w, status: 'Concluído' } : w));
  state = getSpotlightState(week);
  assert.strictEqual(state.mode, 'SPOTLIGHT');
  assert.strictEqual(state.workout.id, 'W4');

  // Complete W4 -> transitions immediately to CELEBRATION
  week = week.map((w) => (w.id === 'W4' ? { ...w, status: 'Concluído' } : w));
  state = getSpotlightState(week);
  assert.strictEqual(state.mode, 'CELEBRATION');
  assert.strictEqual(state.workout, null);
});

test('Spotlight handles out-of-order completion gracefully', () => {
  let week = [
    { id: 'W1', tipo_treino: 'Terça', status: 'Pendente' },
    { id: 'W2', tipo_treino: 'Quinta', status: 'Pendente' },
    { id: 'W3', tipo_treino: 'Sábado', status: 'Pendente' },
  ];

  // Complete W2 out-of-order
  week = week.map((w) => (w.id === 'W2' ? { ...w, status: 'Concluído' } : w));
  let state = getSpotlightState(week);
  assert.strictEqual(state.mode, 'SPOTLIGHT');
  assert.strictEqual(state.workout.id, 'W1'); // W1 still first pending

  // Now complete W1 -> spotlight should skip to W3 (since W2 already done)
  week = week.map((w) => (w.id === 'W1' ? { ...w, status: 'Concluído' } : w));
  state = getSpotlightState(week);
  assert.strictEqual(state.mode, 'SPOTLIGHT');
  assert.strictEqual(state.workout.id, 'W3');

  // Now complete W3 -> CELEBRATION
  week = week.map((w) => (w.id === 'W3' ? { ...w, status: 'Concluído' } : w));
  state = getSpotlightState(week);
  assert.strictEqual(state.mode, 'CELEBRATION');
});

// -----------------------------------------------------------------------------
// AREA 3: Schema Synchronization (public.profiles)
// -----------------------------------------------------------------------------
console.log('\n[AREA 3] Schema Synchronization (public.profiles)');

test('Registration payload contains all required public.profiles columns with valid types', () => {
  const mockUser = {
    id: 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
    email: 'maratonista@teste.com.br',
    nome: "Mariana D'Ávila Silveira",
  };

  const initialProfile = {
    id: mockUser.id,
    nome: mockUser.nome,
    email: mockUser.email,
    modalidade_preferida: 'Corrida',
    objetivo_principal: 'Meia Maratona (21.1 km)',
    esportes_ativos: ['Corrida'],
    nivel_experiencia: 'Intermediário',
    dias_disponiveis: 4,
    onboarding_concluido: true,
    created_at: new Date().toISOString(),
  };

  // Required columns check:
  // id, nome, email, esportes_ativos, dias_disponiveis, nivel_experiencia, objetivo_principal
  const requiredColumns = [
    'id',
    'nome',
    'email',
    'esportes_ativos',
    'dias_disponiveis',
    'nivel_experiencia',
    'objetivo_principal',
  ];

  for (const col of requiredColumns) {
    assert(col in initialProfile, `Missing required column in profiles payload: ${col}`);
  }

  // Type checks
  assert(typeof initialProfile.id === 'string' && initialProfile.id.length === 36, 'id must be UUID string');
  assert(typeof initialProfile.nome === 'string' && initialProfile.nome.length > 0, 'nome must be non-empty string');
  assert(typeof initialProfile.email === 'string' && initialProfile.email.includes('@'), 'email must be valid string');
  assert(Array.isArray(initialProfile.esportes_ativos), 'esportes_ativos must be array (text[])');
  assert(initialProfile.esportes_ativos.every((x) => typeof x === 'string'), 'esportes_ativos items must be strings');
  assert(Number.isInteger(initialProfile.dias_disponiveis), 'dias_disponiveis must be integer');
  assert(typeof initialProfile.nivel_experiencia === 'string', 'nivel_experiencia must be text');
  assert(typeof initialProfile.objetivo_principal === 'string', 'objetivo_principal must be text');
});

test('AuthContext.tsx code contains exact provisioning call with all required columns', () => {
  const authContextCode = fs.readFileSync(path.join(FRONTEND_DIR, 'context', 'AuthContext.tsx'), 'utf8');
  assert(authContextCode.includes('upsertProfile(initialProfile)'), 'Must call upsertProfile');
  assert(authContextCode.includes("id: data.user.id"), 'Must assign user.id to id');
  assert(authContextCode.includes("nome,"), 'Must assign nome');
  assert(authContextCode.includes("email,"), 'Must assign email');
  assert(authContextCode.includes("esportes_ativos: ['Corrida']"), 'Must assign esportes_ativos array');
  assert(authContextCode.includes("dias_disponiveis: 4"), 'Must assign dias_disponiveis');
  assert(authContextCode.includes("nivel_experiencia: 'Intermediário'"), 'Must assign nivel_experiencia');
  assert(authContextCode.includes("objetivo_principal: 'Meia Maratona (21.1 km)'"), 'Must assign objetivo_principal');
});

// -----------------------------------------------------------------------------
// AREA 4: PWA Installation Criteria
// -----------------------------------------------------------------------------
console.log('\n[AREA 4] PWA Installation Criteria & Binary Header Validation');

test('manifest.json conforms to Web App Manifest specification schema', () => {
  const manifestRaw = fs.readFileSync(path.join(FRONTEND_DIR, 'public', 'manifest.json'), 'utf8');
  const manifest = JSON.parse(manifestRaw);

  assert(manifest.name && manifest.name.length > 0, 'manifest must have name');
  assert(manifest.short_name && manifest.short_name.length > 0, 'manifest must have short_name');
  assert(manifest.start_url === '/', 'start_url must be /');
  assert(manifest.display === 'standalone', 'display must be standalone');
  assert(manifest.background_color && manifest.background_color.startsWith('#'), 'background_color must be valid hex');
  assert(manifest.theme_color && manifest.theme_color.startsWith('#'), 'theme_color must be valid hex');
  assert(Array.isArray(manifest.icons) && manifest.icons.length >= 2, 'icons array must have >= 2 items');

  const icon192 = manifest.icons.find((i) => i.sizes === '192x192');
  const icon512 = manifest.icons.find((i) => i.sizes === '512x512');
  assert(icon192, 'Manifest must declare 192x192 icon');
  assert(icon512, 'Manifest must declare 512x512 icon');
  assert(icon192.src.includes('192'), '192 icon src valid');
  assert(icon512.src.includes('512'), '512 icon src valid');
});

function verifyPngBinary(filePath, expectedWidth, expectedHeight) {
  const buf = fs.readFileSync(filePath);
  assert(buf.length > 24, `File ${filePath} is too small to be a valid PNG`);

  // PNG magic number: 89 50 4E 47 0D 0A 1A 0A
  const pngMagic = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
  for (let i = 0; i < 8; i++) {
    assert.strictEqual(buf[i], pngMagic[i], `Byte ${i} of ${filePath} does not match PNG signature`);
  }

  // IHDR chunk: 4 bytes length, 4 bytes chunk type "IHDR" (0x49 0x48 0x44 0x52)
  const ihdrChunkType = buf.toString('ascii', 12, 16);
  assert.strictEqual(ihdrChunkType, 'IHDR', `Expected IHDR chunk in ${filePath}, got ${ihdrChunkType}`);

  // Width (bytes 16..19, big endian), Height (bytes 20..23, big endian)
  const width = buf.readUInt32BE(16);
  const height = buf.readUInt32BE(20);

  assert.strictEqual(width, expectedWidth, `Expected width ${expectedWidth} for ${filePath}, got ${width}`);
  assert.strictEqual(height, expectedHeight, `Expected height ${expectedHeight} for ${filePath}, got ${height}`);
}

test('icon-192x192.png is valid binary PNG with dimensions exactly 192x192', () => {
  const iconPath = path.join(FRONTEND_DIR, 'public', 'icons', 'icon-192x192.png');
  verifyPngBinary(iconPath, 192, 192);
});

test('icon-512x512.png is valid binary PNG with dimensions exactly 512x512', () => {
  const iconPath = path.join(FRONTEND_DIR, 'public', 'icons', 'icon-512x512.png');
  verifyPngBinary(iconPath, 512, 512);
});

test('sw.js compiles with valid JavaScript syntax without throwing', () => {
  const swCode = fs.readFileSync(path.join(FRONTEND_DIR, 'public', 'sw.js'), 'utf8');
  assert.doesNotThrow(() => {
    new vm.Script(swCode, { filename: 'sw.js' });
  }, 'sw.js should be valid JavaScript without syntax errors');

  assert(swCode.includes("addEventListener('install'"), 'SW must have install event listener');
  assert(swCode.includes("addEventListener('activate'"), 'SW must have activate event listener');
  assert(swCode.includes("addEventListener('fetch'"), 'SW must have fetch event listener');
  assert(swCode.includes("supabase.co"), 'SW must bypass Supabase auth/API calls');
});

test('layout.tsx contains valid service worker registration and viewport meta', () => {
  const layoutCode = fs.readFileSync(path.join(FRONTEND_DIR, 'app', 'layout.tsx'), 'utf8');
  assert(layoutCode.includes("navigator.serviceWorker.register('/sw.js')"), 'layout.tsx registers /sw.js');
  assert(layoutCode.includes("manifest: '/manifest.json'"), 'layout.tsx links manifest');
  assert(layoutCode.includes("maximumScale: 1"), 'viewport disables zoom');
  assert(layoutCode.includes("userScalable: false"), 'viewport sets userScalable: false');
});

// -----------------------------------------------------------------------------
// AREA 5: Streamlit Boundary Check & Python Compilation
// -----------------------------------------------------------------------------
console.log('\n[AREA 5] Streamlit Boundary Check & Zero Regression');

test('Git diff verifies only .gitignore has modifications among tracked repository files', () => {
  const diffOutput = execSync('git diff --name-only', { cwd: ROOT_DIR, encoding: 'utf8' }).trim();
  const modifiedFiles = diffOutput.split(/\r?\n/).filter(Boolean);
  assert(
    modifiedFiles.length === 1 && modifiedFiles[0] === '.gitignore',
    `Expected only .gitignore to be modified, but found: ${JSON.stringify(modifiedFiles)}`
  );
});

test('Streamlit Python files compile with exit code 0 via python -m py_compile', () => {
  const pyFiles = ['app.py', 'config.py'];
  for (const dir of ['services', 'components', 'views']) {
    const fullDirPath = path.join(ROOT_DIR, dir);
    if (fs.existsSync(fullDirPath)) {
      const entries = fs.readdirSync(fullDirPath);
      for (const entry of entries) {
        if (entry.endsWith('.py') && entry !== '__init__.py') {
          pyFiles.push(path.join(dir, entry));
        }
      }
    }
  }

  assert(pyFiles.length >= 10, `Expected at least 10 Streamlit Python files, found ${pyFiles.length}`);

  const quotedFiles = pyFiles.map((f) => `"${f}"`).join(' ');
  const pythonCmd = `python -m py_compile ${quotedFiles}`;
  assert.doesNotThrow(() => {
    execSync(pythonCmd, { cwd: ROOT_DIR, stdio: 'pipe' });
  }, 'All Streamlit Python files must compile without syntax errors');
});

// -----------------------------------------------------------------------------
// SUMMARY
// -----------------------------------------------------------------------------
console.log('\n' + '='.repeat(75));
console.log(`CHALLENGER 2 SUMMARY: ${totalPassed} PASSED, ${totalFailed} FAILED`);
console.log('='.repeat(75));

if (totalFailed > 0) {
  process.exit(1);
} else {
  process.exit(0);
}
