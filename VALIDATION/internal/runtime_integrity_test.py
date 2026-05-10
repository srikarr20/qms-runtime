"""
Runtime integrity validation
"""

import subprocess
import sys


TESTS = [

    (
        "Boundary Enforcement",
        [
            sys.executable,
            "tools/check_qms_import_boundaries.py",
        ]
    ),

    (
        "Runtime Orchestrator",
        [
            sys.executable,
            "-m",
            "qos.runtime.orchestrator",
        ]
    ),

]


def run_test(name, cmd):

    print(f"\n=== {name} ===")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        print(f"[FAIL] {name}")
        return False

    print(f"[PASS] {name}")
    return True


def main():

    passed = 0

    for name, cmd in TESTS:

        ok = run_test(name, cmd)

        if ok:
            passed += 1

    print("\n===================")
    print(f"Passed {passed}/{len(TESTS)} tests")
    print("===================\n")


if __name__ == "__main__":
    main()
