/**
 * Tier 1: Feature Coverage Test Suite
 * Validates baseline contracts, props, schemas, and DOM structures across all 8 features.
 * At least 5 assertions per feature.
 */

const assert = require('assert');
const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');
const FRONTEND_DIR = path.join(ROOT_DIR, 'frontend');

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
console.log('TIER 1: FEATURE COVERAGE VERIFICATION SUITE');
console.log('='.repeat(70));

// =========================================================================
// 1. PWA Web App Manifest (>= 5 assertions)
// =========================================================================
console.log('\n[T1.1] Feature 1: PWA Web App Manifest');
const manifestPath = path.join(FRONTEND_DIR, 'public', 'manifest.json');

runTest('Manifest file exists and is readable', () => {
  assert(fs.existsSync(manifestPath), 'manifest.json does not exist at frontend/public/manifest.json');
});

const manifestContent = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

runTest('Manifest specifies valid app name and short name', () => {
  assert(typeof manifestContent.name === 'string' && manifestContent.name.includes('Coach AI'), 'Name must include "Coach AI"');
  assert.strictEqual(manifestContent.short_name, 'Coach AI', 'short_name must be "Coach AI"');
});

runTest('Manifest display mode is set to standalone', () => {
  assert.strictEqual(manifestContent.display, 'standalone', 'display must be "standalone" for PWA');
});

runTest('Manifest start_url is root "/"', () => {
  assert.strictEqual(manifestContent.start_url, '/', 'start_url must be "/"');
});

runTest('Manifest defines valid background and theme colors', () => {
  assert(manifestContent.background_color && manifestContent.background_color.startsWith('#'), 'background_color must be a hex color');
  assert(manifestContent.theme_color && manifestContent.theme_color.startsWith('#'), 'theme_color must be a hex color');
});

runTest('Manifest defines 192x192 and 512x512 icons with valid types', () => {
  assert(Array.isArray(manifestContent.icons), 'icons must be an array');
  assert(manifestContent.icons.length >= 2, 'icons array must contain at least 2 icon specifications');
  const has192 = manifestContent.icons.some((i) => i.sizes === '192x192' && i.src.includes('192'));
  const has512 = manifestContent.icons.some((i) => i.sizes === '512x512' && i.src.includes('512'));
  assert(has192, 'Missing 192x192 icon specification');
  assert(has512, 'Missing 512x512 icon specification');
  
  // Verify physical icon files exist
  for (const icon of manifestContent.icons) {
    const iconPath = path.join(FRONTEND_DIR, 'public', icon.src.replace(/^\//, ''));
    assert(fs.existsSync(iconPath), `Icon file declared in manifest missing on disk: ${icon.src}`);
  }
});

// =========================================================================
// 2. Mobile Viewport & Ergonomics (>= 5 assertions)
// =========================================================================
console.log('\n[T1.2] Feature 2: Mobile Viewport & Ergonomics');
const layoutPath = path.join(FRONTEND_DIR, 'app', 'layout.tsx');
const globalsCssPath = path.join(FRONTEND_DIR, 'app', 'globals.css');

runTest('Root layout file exists', () => {
  assert(fs.existsSync(layoutPath), 'frontend/app/layout.tsx not found');
  assert(fs.existsSync(globalsCssPath), 'frontend/app/globals.css not found');
});

const layoutSource = fs.readFileSync(layoutPath, 'utf8');
const globalsCssSource = fs.readFileSync(globalsCssPath, 'utf8');

runTest('Layout exports Viewport meta with device-width', () => {
  assert(layoutSource.includes("width: 'device-width'") || layoutSource.includes('device-width'), 'Viewport must define device-width');
});

runTest('Layout enforces non-zoomable mobile viewport constraints', () => {
  assert(layoutSource.includes('initialScale: 1'), 'Viewport must specify initialScale: 1');
  assert(layoutSource.includes('maximumScale: 1') || layoutSource.includes('userScalable: false'), 'Viewport must restrict maximumScale or userScalable');
});

runTest('Globals CSS applies touch-action manipulation for lag-free mobile taps', () => {
  assert(globalsCssSource.includes('touch-action: manipulation'), 'globals.css must specify touch-action: manipulation');
});

runTest('Globals CSS disables tap highlight flash on mobile touch devices', () => {
  assert(globalsCssSource.includes('-webkit-tap-highlight-color: transparent'), 'globals.css must disable tap highlight');
});

runTest('Globals CSS defines safe-area-inset padding for mobile notches and gesture bars', () => {
  assert(globalsCssSource.includes('env(safe-area-inset-bottom)'), 'globals.css must handle safe-area-inset-bottom');
  assert(globalsCssSource.includes('env(safe-area-inset-top)'), 'globals.css must handle safe-area-inset-top');
});

// =========================================================================
// 3. Supabase Client & Config (>= 5 assertions)
// =========================================================================
console.log('\n[T1.3] Feature 3: Supabase Client & Config');
const supabasePath = path.join(FRONTEND_DIR, 'lib', 'supabase.ts');
const typesPath = path.join(FRONTEND_DIR, 'lib', 'types.ts');

runTest('Supabase client module and types definition exist', () => {
  assert(fs.existsSync(supabasePath), 'frontend/lib/supabase.ts not found');
  assert(fs.existsSync(typesPath), 'frontend/lib/types.ts not found');
});

const supabaseSource = fs.readFileSync(supabasePath, 'utf8');
const typesSource = fs.readFileSync(typesPath, 'utf8');

runTest('Supabase client creates and exports singleton client instance', () => {
  assert(supabaseSource.includes('createClient('), 'Must invoke createClient');
  assert(supabaseSource.includes('export const supabase ='), 'Must export supabase singleton instance');
});

runTest('Supabase client binds to environment variables with fallback', () => {
  assert(supabaseSource.includes('process.env.NEXT_PUBLIC_SUPABASE_URL'), 'Must read NEXT_PUBLIC_SUPABASE_URL');
  assert(supabaseSource.includes('process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY'), 'Must read NEXT_PUBLIC_SUPABASE_ANON_KEY');
  assert(supabaseSource.includes('https://vkkbvvpjfomxwawggsel.supabase.co'), 'Must include resilient fallback URL');
});

runTest('Types file exports authoritative Profile interface matching DB schema', () => {
  assert(typesSource.includes('export interface Profile'), 'Missing Profile interface');
  assert(typesSource.includes('nome: string;'), 'Profile must have nome');
  assert(typesSource.includes('email: string;'), 'Profile must have email');
  assert(typesSource.includes('esportes_ativos: string[];'), 'Profile must have esportes_ativos array');
  assert(typesSource.includes('objetivo_principal: string;'), 'Profile must have objetivo_principal');
  assert(typesSource.includes('nivel_experiencia: string;'), 'Profile must have nivel_experiencia');
});

runTest('Types file exports Schedule interface with required workout fields', () => {
  assert(typesSource.includes('export interface Schedule'), 'Missing Schedule interface');
  assert(typesSource.includes('tipo_treino: string;'), 'Schedule must have tipo_treino');
  assert(typesSource.includes('distancia_km: number;'), 'Schedule must have distancia_km');
  assert(typesSource.includes('pace_alvo: string;'), 'Schedule must have pace_alvo');
  assert(typesSource.includes('duracao_min: number;'), 'Schedule must have duracao_min');
  assert(typesSource.includes('status: \'Pendente\' | \'Concluído\''), 'Schedule status must be union Pendente | Concluído');
});

runTest('Supabase module provides required query and mutation helpers', () => {
  assert(supabaseSource.includes('getProfile('), 'Must provide getProfile helper');
  assert(supabaseSource.includes('upsertProfile('), 'Must provide upsertProfile helper');
  assert(supabaseSource.includes('getSchedules('), 'Must provide getSchedules helper');
  assert(supabaseSource.includes('markWorkoutCompleted('), 'Must provide markWorkoutCompleted helper');
});

// =========================================================================
// 4. Athlete Authentication (>= 5 assertions)
// =========================================================================
console.log('\n[T1.4] Feature 4: Athlete Authentication Forms & Contract');
const authModalPath = path.join(FRONTEND_DIR, 'components', 'AuthModal.tsx');
const authContextPath = path.join(FRONTEND_DIR, 'context', 'AuthContext.tsx');

runTest('Auth component and context files exist', () => {
  assert(fs.existsSync(authModalPath), 'frontend/components/AuthModal.tsx not found');
  assert(fs.existsSync(authContextPath), 'frontend/context/AuthContext.tsx not found');
});

const authModalSource = fs.readFileSync(authModalPath, 'utf8');
const authContextSource = fs.readFileSync(authContextPath, 'utf8');

runTest('AuthModal provides tabs for both Sign In and Sign Up', () => {
  assert(authModalSource.includes("'login'"), 'Must support login tab');
  assert(authModalSource.includes("'register'"), 'Must support register tab');
  assert(authModalSource.includes('Entrar'), 'Must contain Entrar tab trigger');
  assert(authModalSource.includes('Criar Conta'), 'Must contain Criar Conta tab trigger');
});

runTest('Sign In form includes email and password fields with required validation', () => {
  assert(authModalSource.includes('type="email"'), 'Must contain email input');
  assert(authModalSource.includes('type="password"'), 'Must contain password input');
  assert(authModalSource.includes('Informe seu e-mail e senha cadastrados.'), 'Must validate non-empty login fields');
});

runTest('Sign Up form includes full athlete registration fields', () => {
  assert(authModalSource.includes('regNome'), 'Must capture athlete full name');
  assert(authModalSource.includes('regEmail'), 'Must capture athlete email');
  assert(authModalSource.includes('regPassword'), 'Must capture athlete password');
  assert(authModalSource.includes('regConfirmPassword'), 'Must capture password confirmation');
});

runTest('Sign Up enforces password length >= 6 and matching confirmation', () => {
  assert(authModalSource.includes('regPassword.length < 6'), 'Must validate password length >= 6');
  assert(authModalSource.includes('A senha deve conter pelo menos 6 caracteres.'), 'Must provide short password warning');
  assert(authModalSource.includes('regPassword !== regConfirmPassword'), 'Must validate matching passwords');
  assert(authModalSource.includes('As senhas digitadas não coincidem.'), 'Must provide password mismatch warning');
});

runTest('AuthContext provisions initial athlete profile record on registration', () => {
  assert(authContextSource.includes('signUp = async'), 'Must define signUp method');
  assert(authContextSource.includes('upsertProfile(initialProfile)'), 'Must provision initialProfile into public.profiles');
  assert(authContextSource.includes('modalidade_preferida: \'Corrida\''), 'Default preferred modality must be Corrida');
  assert(authContextSource.includes('nivel_experiencia: \'Intermediário\''), 'Default experience level must be Intermediário');
});

// =========================================================================
// 5. ProfileHeader Component (>= 5 assertions)
// =========================================================================
console.log('\n[T1.5] Feature 5: ProfileHeader Component');
const profileHeaderPath = path.join(FRONTEND_DIR, 'components', 'ProfileHeader.tsx');

runTest('ProfileHeader component file exists', () => {
  assert(fs.existsSync(profileHeaderPath), 'frontend/components/ProfileHeader.tsx not found');
});

const profileHeaderSource = fs.readFileSync(profileHeaderPath, 'utf8');

runTest('ProfileHeader renders personalized greeting with athlete name', () => {
  assert(profileHeaderSource.includes('Olá, {athleteName}'), 'Must render personalized greeting');
  assert(profileHeaderSource.includes("profile?.nome || 'Atleta'"), 'Must fallback gracefully if nome is missing');
});

runTest('ProfileHeader displays sport badges, experience level, and goal', () => {
  assert(profileHeaderSource.includes('{sports.map('), 'Must render sport badges list');
  assert(profileHeaderSource.includes('{experienceLevel}'), 'Must display athlete experience level');
  assert(profileHeaderSource.includes('{primaryGoal}'), 'Must display athlete primary goal');
});

runTest('ProfileHeader renders 4-item Quick Stats grid', () => {
  assert(profileHeaderSource.includes('stats.totalWorkouts'), 'Must render total workouts count');
  assert(profileHeaderSource.includes('stats.totalDistanceKm'), 'Must render total distance in km');
  assert(profileHeaderSource.includes('stats.avgPace'), 'Must render average pace');
  assert(profileHeaderSource.includes('stats.adherencePercent'), 'Must render adherence percentage');
});

runTest('ProfileHeader includes sign out action hook', () => {
  assert(profileHeaderSource.includes('signOut()'), 'Must connect to signOut function');
  assert(profileHeaderSource.includes('title="Sair"'), 'Must provide accessible sign out title');
  assert(profileHeaderSource.includes('min-h-[44px]'), 'Sign out button must meet min 44px mobile touch target');
});

runTest('ProfileHeader displays Demo indicator when running in preview mode', () => {
  assert(profileHeaderSource.includes('isDemoMode &&'), 'Must check demo mode');
  assert(profileHeaderSource.includes('Demo'), 'Must render Demo badge in preview mode');
});

// =========================================================================
// 6. NextWorkoutCard Component (>= 5 assertions)
// =========================================================================
console.log('\n[T1.6] Feature 6: NextWorkoutCard Component');
const nextWorkoutCardPath = path.join(FRONTEND_DIR, 'components', 'NextWorkoutCard.tsx');

runTest('NextWorkoutCard component file exists', () => {
  assert(fs.existsSync(nextWorkoutCardPath), 'frontend/components/NextWorkoutCard.tsx not found');
});

const nextWorkoutCardSource = fs.readFileSync(nextWorkoutCardPath, 'utf8');

runTest('NextWorkoutCard queries and isolates first pending workout', () => {
  assert(nextWorkoutCardSource.includes("s.status === 'Pendente'"), 'Must filter by status Pendente');
  assert(nextWorkoutCardSource.includes('pendingWorkouts[0]'), 'Must select first pending workout as spotlight');
});

runTest('NextWorkoutCard renders workout title and scheduled date', () => {
  assert(nextWorkoutCardSource.includes('nextWorkout.tipo_treino'), 'Must display workout type');
  assert(nextWorkoutCardSource.includes('nextWorkout.dia_semana'), 'Must display day of week');
  assert(nextWorkoutCardSource.includes('nextWorkout.data_prevista'), 'Must display scheduled date');
});

runTest('NextWorkoutCard renders full prescription metrics grid', () => {
  assert(nextWorkoutCardSource.includes('nextWorkout.distancia_km'), 'Must display target distance');
  assert(nextWorkoutCardSource.includes('nextWorkout.pace_alvo'), 'Must display target pace');
  assert(nextWorkoutCardSource.includes('nextWorkout.duracao_min'), 'Must display target duration');
  assert(nextWorkoutCardSource.includes('nextWorkout.rpe_alvo'), 'Must display target RPE / effort');
});

runTest('NextWorkoutCard renders workout structure prescription', () => {
  assert(nextWorkoutCardSource.includes('nextWorkout.estrutura_treino'), 'Must display structured prescription');
});

runTest('NextWorkoutCard features interactive "Concluir Treino" action button', () => {
  assert(nextWorkoutCardSource.includes('Concluir Treino'), 'Must include Concluir Treino button');
  assert(nextWorkoutCardSource.includes('handleComplete'), 'Must wire to handleComplete handler');
  assert(nextWorkoutCardSource.includes('onCompleteWorkout(id)'), 'Must trigger parent onCompleteWorkout callback');
});

runTest('NextWorkoutCard renders celebration banner when all workouts are completed', () => {
  assert(nextWorkoutCardSource.includes('Semana Concluída com Sucesso!'), 'Must include celebration title');
  assert(nextWorkoutCardSource.includes('Parabéns! Todas as sessões prescritas desta semana foram concluídas.'), 'Must include celebration text');
});

// =========================================================================
// 7. WeeklyProgress Component (>= 5 assertions)
// =========================================================================
console.log('\n[T1.7] Feature 7: WeeklyProgress Component');
const weeklyProgressPath = path.join(FRONTEND_DIR, 'components', 'WeeklyProgress.tsx');

runTest('WeeklyProgress component file exists', () => {
  assert(fs.existsSync(weeklyProgressPath), 'frontend/components/WeeklyProgress.tsx not found');
});

const weeklyProgressSource = fs.readFileSync(weeklyProgressPath, 'utf8');

runTest('WeeklyProgress computes completed vs total sessions', () => {
  assert(weeklyProgressSource.includes('schedules.length'), 'Must count total workouts');
  assert(weeklyProgressSource.includes("s.status === 'Concluído'"), 'Must count completed workouts');
  assert(weeklyProgressSource.includes('{completedWorkouts}'), 'Must display completed count');
  assert(weeklyProgressSource.includes('{totalWorkouts}'), 'Must display total count');
});

runTest('WeeklyProgress computes pending workouts count', () => {
  assert(weeklyProgressSource.includes('totalWorkouts - completedWorkouts'), 'Must calculate pending count');
  assert(weeklyProgressSource.includes('{pendingWorkouts}'), 'Must display pending count');
});

runTest('WeeklyProgress aggregates planned and completed distances in km', () => {
  assert(weeklyProgressSource.includes('totalDistancePlanned'), 'Must aggregate planned distance');
  assert(weeklyProgressSource.includes('totalDistanceCompleted'), 'Must aggregate completed distance');
});

runTest('WeeklyProgress implements mathematical adherence rate formula', () => {
  assert(
    weeklyProgressSource.includes('(completedWorkouts / totalWorkouts) * 100') ||
    weeklyProgressSource.includes('(completedWorkouts / totalWorkouts)'),
    'Must calculate adherence percentage via completed / total'
  );
  assert(weeklyProgressSource.includes('{adherencePercent}% Concluído'), 'Must render formatted percentage');
});

runTest('WeeklyProgress dynamically styles progress bar width percentage', () => {
  assert(weeklyProgressSource.includes('style={{ width:'), 'Progress bar must bind dynamic width style');
  assert(weeklyProgressSource.includes('adherencePercent'), 'Progress bar width must reflect adherencePercent');
});

// =========================================================================
// 8. WorkoutScheduleList Component (>= 5 assertions)
// =========================================================================
console.log('\n[T1.8] Feature 8: WorkoutScheduleList Component');
const scheduleListPath = path.join(FRONTEND_DIR, 'components', 'WorkoutScheduleList.tsx');

runTest('WorkoutScheduleList component file exists', () => {
  assert(fs.existsSync(scheduleListPath), 'frontend/components/WorkoutScheduleList.tsx not found');
});

const scheduleListSource = fs.readFileSync(scheduleListPath, 'utf8');

runTest('WorkoutScheduleList provides filter chips for Todos, Pendentes, and Concluídos', () => {
  assert(scheduleListSource.includes("'Todos'"), 'Must include Todos filter');
  assert(scheduleListSource.includes("'Pendentes'"), 'Must include Pendentes filter');
  assert(scheduleListSource.includes("'Concluídos'"), 'Must include Concluídos filter');
});

runTest('WorkoutScheduleList displays badge count for each filter category', () => {
  assert(scheduleListSource.includes("chip === 'Todos'"), 'Must calculate count for Todos');
  assert(scheduleListSource.includes("x.status === 'Pendente'"), 'Must calculate count for Pendentes');
  assert(scheduleListSource.includes("x.status === 'Concluído'"), 'Must calculate count for Concluídos');
});

runTest('WorkoutScheduleList renders distinct visual badges for status', () => {
  assert(scheduleListSource.includes('✓ Concluído'), 'Must render Concluído status badge');
  assert(scheduleListSource.includes('⏳ Pendente'), 'Must render Pendente status badge');
});

runTest('WorkoutScheduleList provides direct completion button for pending items', () => {
  assert(scheduleListSource.includes('onCompleteWorkout(s.id)'), 'Must invoke onCompleteWorkout callback');
  assert(scheduleListSource.includes('Concluir'), 'Must render Concluir button label');
  assert(scheduleListSource.includes('min-h-[44px]'), 'Check-in button must meet min 44px mobile touch ergonomics');
});

runTest('WorkoutScheduleList wires card click to select workout modal', () => {
  assert(scheduleListSource.includes('onSelectWorkout(schedule)'), 'Card click must trigger onSelectWorkout');
});

console.log('\n' + '='.repeat(70));
console.log(`TIER 1 COMPLETE: ${passedTests}/${totalTests} TESTS PASSED (100%)`);
console.log('='.repeat(70));
