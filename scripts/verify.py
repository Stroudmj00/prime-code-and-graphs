#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
EXE = ROOT / "output" / "bin" / ("prime_bench.exe" if os.name == "nt" else "prime_bench")
ALGORITHMS = [
    "naive-iterate",
    "sqrt-iterate",
    "miller-rabin-iterate",
    "sieve-erat",
    "sieve-erat-odd",
    "sieve-erat-segm",
    "sieve-erat-segm-odd",
    "sieve-wheel30-segm",
    "sieve-wheel30-indexed",
    "sieve-wheel30-bitset",
    "sieve-wheel30-bitset-state",
    "sieve-wheel30-bitset-fsm",
    "sieve-lagrange-fsm",
    "sieve-lagrange-lehmer-fsm",
    "sieve-lagrange-lehmer-tight-fsm",
    "sieve-lagrange-lehmer-fsm-s17",
    "sieve-lagrange-lehmer-fsm-s18",
    "sieve-lagrange-lehmer-fsm-s19",
]

# zero-indexed prime(n), matching the upstream QueenJewels convention.
EXPECTED = {
    0: 2,
    1: 3,
    2: 5,
    3: 7,
    4: 11,
    5: 13,
    10: 31,
    100: 547,
    1_000: 7927,
    10_000: 104_743,
    100_000: 1_299_721,
}

HIGH_CONFIDENCE_EXPECTED = {
    # Values also appear in the upstream reference benchmark table.
    67_108_864: 1_339_484_207,
    268_435_456: 5_750_079_077,
    # Cross-checked against the previous formula-assisted implementation and the
    # current canonical benchmark data.
    1_000_000_000: 22_801_763_513,
}


def run_case(algorithm: str, n: int) -> int:
    proc = subprocess.run(
        [str(EXE), algorithm, str(n)],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return int(proc.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify prime algorithms")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip the slowest checks for the iterative algorithms",
    )
    args = parser.parse_args()

    if not EXE.exists():
        raise SystemExit(f"Missing binary: {EXE}. Run scripts/build.py first.")

    for algorithm in ALGORITHMS:
        for n, expected in EXPECTED.items():
            if args.fast and algorithm in {"naive-iterate", "sqrt-iterate", "miller-rabin-iterate"} and n > 1_000:
                continue
            if algorithm == "naive-iterate" and n > 1_000:
                continue
            actual = run_case(algorithm, n)
            if actual != expected:
                raise AssertionError(f"{algorithm} prime({n}) = {actual}; expected {expected}")
            print(f"{algorithm:22s} prime({n:>7,d}) = {actual:,}")

    for algorithm in {"sieve-lagrange-fsm", "sieve-lagrange-lehmer-fsm"}:
        for n, expected in HIGH_CONFIDENCE_EXPECTED.items():
            actual = run_case(algorithm, n)
            if actual != expected:
                raise AssertionError(f"{algorithm} prime({n}) = {actual}; expected {expected}")
            print(f"{algorithm:22s} prime({n:>11,d}) = {actual:,}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
