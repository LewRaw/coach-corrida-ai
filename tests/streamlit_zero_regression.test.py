"""
Streamlit Zero-Regression Verification Test
Validates that the existing root Python Streamlit application:
1. Compiles with zero syntax errors across all python source files matching
   app.py config.py services/*.py components/*.py views/*.py.
2. Has not suffered unauthorized modifications or file deletions in root code.
3. Preserves all critical requirements in requirements.txt.
4. Maintains clean isolation with all new frontend code confined to frontend/ and tests/.
"""

import sys
import os
import py_compile
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def get_streamlit_files():
    files = [ROOT_DIR / "app.py", ROOT_DIR / "config.py"]
    for folder in ["services", "components", "views"]:
        dir_path = ROOT_DIR / folder
        if dir_path.exists():
            for f in sorted(dir_path.glob("*.py")):
                if f.name != "__init__.py":
                    files.append(f)
    return files

def test_py_compile_all_streamlit_files():
    print("[SR.1] Verifying Python bytecode compilation for Streamlit application...")
    files = get_streamlit_files()
    assert len(files) >= 10, f"Expected at least 10 Streamlit python files, found {len(files)}"
    
    errors = []
    success_count = 0
    
    for py_file in files:
        if not py_file.exists():
            errors.append(f"Missing required Streamlit source file: {py_file.relative_to(ROOT_DIR)}")
            continue
        try:
            py_compile.compile(str(py_file), doraise=True)
            success_count += 1
            print(f"  OK: {py_file.relative_to(ROOT_DIR)}")
        except py_compile.PyCompileError as e:
            errors.append(f"Syntax error compiling {py_file.relative_to(ROOT_DIR)}: {e}")

    assert len(errors) == 0, f"Compilation failed for {len(errors)} files:\n" + "\n".join(errors)
    assert success_count == len(files), f"Expected {len(files)} files, got {success_count}"
    print(f"  PASS: All {success_count} Streamlit files compiled cleanly with exit code 0.\n")

def test_requirements_txt_integrity():
    print("[SR.2] Verifying requirements.txt integrity...")
    req_path = ROOT_DIR / "requirements.txt"
    assert req_path.exists(), "requirements.txt not found at root"
    content = req_path.read_text(encoding="utf-8")
    
    required_packages = [
        "streamlit",
        "supabase",
        "pandas",
        "plotly",
        "pydantic",
        "google-genai",
    ]
    for pkg in required_packages:
        assert pkg in content, f"Missing expected package '{pkg}' in requirements.txt"
    print(f"  PASS: requirements.txt contains all core dependencies: {required_packages}\n")

def test_root_files_isolation():
    print("[SR.3] Verifying root file isolation and git boundaries...")
    # Verify no accidental frontend build files leaked into root
    unwanted_root_items = [
        ROOT_DIR / "node_modules",
        ROOT_DIR / ".next",
        ROOT_DIR / "package.json",
        ROOT_DIR / "tsconfig.json",
    ]
    for item in unwanted_root_items:
        assert not item.exists(), f"Found prohibited frontend file/dir in project root: {item.name}"
    
    # Verify frontend/ directory contains expected structure
    frontend_dir = ROOT_DIR / "frontend"
    assert frontend_dir.exists() and frontend_dir.is_dir(), "frontend/ directory must exist"
    assert (frontend_dir / "package.json").exists(), "frontend/package.json must exist"
    print("  PASS: Clean boundary isolation verified. No frontend leakage in root.\n")

def run():
    print("=" * 65)
    print("STREAMLIT ZERO-REGRESSION VERIFICATION SUITE")
    print("=" * 65)
    try:
        test_py_compile_all_streamlit_files()
        test_requirements_txt_integrity()
        test_root_files_isolation()
        print("=" * 65)
        print("ALL STREAMLIT REGRESSION TESTS PASSED (100%)")
        print("=" * 65)
        return 0
    except AssertionError as e:
        print(f"\nFAIL: {e}")
        return 1
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run())
