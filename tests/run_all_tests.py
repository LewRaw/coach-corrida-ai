"""
Master Unified Test Runner (Python)
Executes:
1. Streamlit Zero-Regression Suite (Bytecode compilation & file isolation)
2. Frontend Next.js Build Verification (npm.cmd run build)
3. Node.js Multi-Tier E2E Verification Suites (Tiers 1-4)
"""

import sys
import os
import subprocess
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def run_step(title, cmd, cwd=ROOT_DIR):
    print("\n" + "=" * 75)
    print(f"  STEP: {title}")
    print(f"  COMMAND: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    print("=" * 75)
    
    start = time.time()
    res = subprocess.run(cmd, cwd=str(cwd), shell=isinstance(cmd, str))
    duration = time.time() - start
    
    status = "PASSED" if res.returncode == 0 else f"FAILED (exit: {res.returncode})"
    print(f"\n  -> {title}: {status} in {duration:.2f}s")
    return res.returncode == 0

def main():
    print("#" * 75)
    print("  COACH AI - COMPREHENSIVE REPOSITORY VERIFICATION PIPELINE")
    print("#" * 75)

    results = []

    # Step 1: Streamlit Zero Regression Test
    sr_ok = run_step(
        "Streamlit Zero-Regression Verification",
        [sys.executable, str(ROOT_DIR / "tests" / "streamlit_zero_regression.test.py")]
    )
    results.append(("Streamlit Zero-Regression", sr_ok))

    # Step 2: Next.js Frontend Production Build Check
    build_cmd = "npm.cmd run build" if sys.platform == "win32" else "npm run build"
    build_ok = run_step(
        "Next.js Frontend Production Build Verification",
        build_cmd,
        cwd=ROOT_DIR / "frontend"
    )
    results.append(("Next.js Frontend Build", build_ok))

    # Step 3: Node Multi-Tier Test Runner (Tiers 1 - 4)
    tiers_ok = run_step(
        "Node.js Multi-Tier E2E Test Runner (Tiers 1-4)",
        ["node", str(ROOT_DIR / "tests" / "run_all_tests.js")]
    )
    results.append(("Multi-Tier E2E Suites (Tiers 1-4)", tiers_ok))

    # Summary
    print("\n" + "#" * 75)
    print("  FINAL EXECUTION SUMMARY")
    print("#" * 75)
    all_passed = True
    for name, passed in results:
        mark = "[PASS]" if passed else "[FAIL]"
        print(f"  {mark.ljust(8)} | {name}")
        if not passed:
            all_passed = False

    print("-" * 75)
    print(f"  Overall Verification Status: {'SUCCESS (100% PASS)' if all_passed else 'FAILURE'}")
    print("#" * 75)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
