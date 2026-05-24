#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import pathlib
import statistics
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
EXE = ROOT / "output" / "bin" / ("prime_bench.exe" if os.name == "nt" else "prime_bench")


def parse_csv_list(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def run_once(algorithm: str, n: int, timeout: float) -> tuple[int, float]:
    proc = subprocess.run(
        [str(EXE), algorithm, str(n), "--time"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=True,
    )
    return int(proc.stdout.strip()), float(proc.stderr.strip())


def run_case(algorithm: str, n: int, repeats: int, timeout: float) -> tuple[int, float]:
    prime: int | None = None
    samples: list[float] = []
    for _ in range(repeats):
        result, seconds = run_once(algorithm, n, timeout)
        if prime is None:
            prime = result
        elif result != prime:
            raise AssertionError(f"{algorithm} prime({n}) changed from {prime} to {result}")
        samples.append(seconds)
    assert prime is not None
    return prime, statistics.median(samples)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare selected prime benchmark algorithms quickly")
    parser.add_argument(
        "--algorithms",
        default="sieve-lagrange-fsm,sieve-lagrange-lehmer-fsm,sieve-lagrange-lehmer-axler-fsm",
        help="Comma-separated algorithms to compare",
    )
    parser.add_argument(
        "--n",
        default="1000000000,4000000000,8000000000",
        help="Comma-separated zero-indexed n values",
    )
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    if not EXE.exists():
        raise SystemExit(f"Missing binary: {EXE}. Run scripts/build.py first.")

    algorithms = parse_csv_list(args.algorithms)
    ns = [int(item.replace("_", "").replace(",", "")) for item in parse_csv_list(args.n)]

    print("| n | algorithm | prime(n) | median seconds | speedup vs first |")
    print("|---:|---|---:|---:|---:|")
    for n in ns:
        baseline_seconds: float | None = None
        for algorithm in algorithms:
            prime, seconds = run_case(algorithm, n, args.repeats, args.timeout)
            if baseline_seconds is None:
                baseline_seconds = seconds
            speedup = baseline_seconds / seconds if seconds > 0 else 0.0
            print(f"| {n:,} | `{algorithm}` | {prime:,} | {seconds:.6f} | {speedup:.2f}x |")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
