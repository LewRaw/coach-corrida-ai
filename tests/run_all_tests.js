/**
 * Master Node.js Test Runner
 * Executes Tier 1, Tier 2, Tier 3, and Tier 4 test suites.
 * Exits with code 0 on 100% pass, code 1 on any failure.
 */

const { spawnSync } = require('child_process');
const path = require('path');

const suites = [
  { name: 'Tier 1: Feature Coverage', script: 'tier1_feature_coverage.test.js' },
  { name: 'Tier 2: Boundary & Corner Cases', script: 'tier2_boundary_corner.test.js' },
  { name: 'Tier 3: Cross-Feature Combinations', script: 'tier3_cross_feature.test.js' },
  { name: 'Tier 4: Real-World Scenarios', script: 'tier4_real_world_scenario.test.js' },
  { name: 'Challenger 1: Adversarial Stress & Boundary Suite', script: 'stress_adversarial_challenge.test.js' },
];

console.log('='.repeat(75));
console.log('  COACH AI E2E AUTOMATED TEST RUNNER (TIERS 1 - 4)');
console.log('='.repeat(75));

let allPassed = true;
const summary = [];
const startTime = Date.now();

for (const suite of suites) {
  const scriptPath = path.join(__dirname, suite.script);
  console.log(`\n>>> Executing [${suite.name}] (${suite.script})...\n`);

  const res = spawnSync('node', [scriptPath], {
    stdio: 'inherit',
    cwd: path.resolve(__dirname, '..'),
  });

  const passed = res.status === 0;
  if (!passed) {
    allPassed = false;
  }
  summary.push({ name: suite.name, passed, exitCode: res.status });
}

const elapsedMs = Date.now() - startTime;

console.log('\n' + '='.repeat(75));
console.log('  OVERALL TEST SUITE EXECUTION SUMMARY');
console.log('='.repeat(75));

for (const item of summary) {
  const statusMark = item.passed ? '✓ PASSED' : '✗ FAILED';
  console.log(`  ${statusMark.padEnd(10)} | ${item.name} (exit: ${item.exitCode})`);
}

console.log('-'.repeat(75));
console.log(`  Total Execution Time: ${elapsedMs}ms`);
console.log(`  Overall Status: ${allPassed ? 'ALL TEST TIERS PASSED (100%)' : 'SOME TEST TIERS FAILED'}`);
console.log('='.repeat(75));

process.exit(allPassed ? 0 : 1);
