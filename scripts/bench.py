#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import pathlib
import platform
import statistics
import subprocess
import sys
import time


ROOT = pathlib.Path(__file__).resolve().parents[1]
EXE = ROOT / "output" / "bin" / ("prime_bench.exe" if os.name == "nt" else "prime_bench")
BUILD_META = ROOT / "output" / "bin" / "build_meta.json"
OUT_DIR = ROOT / "output" / "data"
OUT_CSV = OUT_DIR / "benchmark.csv"

ALGORITHMS = {
    "naive-iterate": [0, 16, 64, 128, 256, 512, 1_024],
    "sqrt-iterate": [0, 256, 1_024, 4_096, 8_192, 16_384, 32_768],
    "miller-rabin-iterate": [0, 512, 2_048, 8_192, 16_384, 32_768, 65_536],
    "sieve-erat": [0, 4_096, 16_384, 65_536, 262_144, 524_288, 1_000_000],
    "sieve-erat-odd": [0, 4_096, 16_384, 65_536, 262_144, 524_288, 1_000_000],
    "sieve-erat-segm": [0, 16_384, 65_536, 262_144, 524_288, 1_000_000, 2_000_000],
    "sieve-erat-segm-odd": [0, 16_384, 65_536, 262_144, 524_288, 1_000_000, 2_000_000],
    "sieve-wheel30-segm": [0, 16_384, 65_536, 262_144, 524_288, 1_000_000, 2_000_000],
    "sieve-wheel30-indexed": [0, 16_384, 65_536, 262_144, 524_288, 1_000_000, 2_000_000],
    "sieve-wheel30-bitset": [0, 16_384, 65_536, 262_144, 524_288, 1_000_000, 2_000_000],
    "sieve-wheel30-bitset-state": [0, 16_384, 65_536, 262_144, 524_288, 1_000_000, 2_000_000],
    "sieve-wheel30-bitset-fsm": [0, 16_384, 65_536, 262_144, 524_288, 1_000_000, 2_000_000],
    "sieve-lagrange-fsm": [0, 16_384, 65_536, 262_144, 524_288, 1_000_000, 2_000_000],
    "sieve-lagrange-lehmer-fsm": [0, 16_384, 65_536, 262_144, 524_288, 1_000_000, 2_000_000],
    "sieve-lagrange-lehmer-axler-fsm": [0, 16_384, 65_536, 262_144, 524_288, 1_000_000, 2_000_000],
}


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
    elapsed = float(proc.stderr.strip())
    return int(proc.stdout.strip()), elapsed


def run_case(algorithm: str, n: int, repeats: int, timeout: float) -> tuple[int, float] | None:
    values: list[float] = []
    prime: int | None = None
    for _ in range(repeats):
        try:
            result, elapsed = run_once(algorithm, n, timeout)
        except subprocess.TimeoutExpired:
            return None
        if prime is None:
            prime = result
        elif prime != result:
            raise AssertionError(f"{algorithm} prime({n}) changed from {prime} to {result}")
        values.append(elapsed)
    assert prime is not None
    return prime, statistics.median(values)


def git_output(*args: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return proc.stdout.strip()


def metadata_path(csv_path: pathlib.Path) -> pathlib.Path:
    return csv_path.with_name(f"{csv_path.stem}.meta.json")


def write_metadata(args: argparse.Namespace, started_at: dt.datetime) -> pathlib.Path:
    build_meta = None
    if BUILD_META.exists():
        build_meta = json.loads(BUILD_META.read_text(encoding="utf-8"))

    try:
        benchmark_data_file = str(args.output.relative_to(ROOT))
    except ValueError:
        benchmark_data_file = str(args.output)

    meta = {
        "benchmark_data_file": benchmark_data_file,
        "started_at_utc": started_at.isoformat().replace("+00:00", "Z"),
        "finished_at_utc": dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z"),
        "command": " ".join(sys.argv),
        "repeats": args.repeats,
        "timeout_seconds": args.timeout,
        "full": bool(args.full),
        "reach_one_second": bool(args.reach_one_second),
        "max_n": args.max_n,
        "git_commit": git_output("rev-parse", "HEAD"),
        "git_dirty": bool(git_output("status", "--porcelain")),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "build": build_meta,
        "notes": "Absolute one-second reach is hardware-relative; same-run relative lift is the primary comparison.",
    }
    out = metadata_path(args.output)
    out.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate prime benchmark data")
    parser.add_argument("-o", "--output", type=pathlib.Path, default=OUT_CSV)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument(
        "--reach-one-second",
        action="store_true",
        help="Keep extending each algorithm until it has a sampled point at or above one second",
    )
    parser.add_argument(
        "--max-n",
        type=int,
        default=64_000_000_000,
        help="Largest n to try when --reach-one-second is enabled",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Use larger sample points for the faster sieves",
    )
    args = parser.parse_args()

    if not EXE.exists():
        raise SystemExit(f"Missing binary: {EXE}. Run scripts/build.py first.")

    started_at = dt.datetime.now(dt.UTC)
    algorithms = {key: list(value) for key, value in ALGORITHMS.items()}
    if args.full:
        algorithms["sieve-erat"].extend([2_000_000, 5_000_000, 10_000_000])
        algorithms["sieve-erat-odd"].extend([2_000_000, 5_000_000, 10_000_000])
        algorithms["sieve-erat-segm"].extend([5_000_000, 10_000_000])
        algorithms["sieve-erat-segm-odd"].extend([5_000_000, 10_000_000])
        algorithms["sieve-wheel30-segm"].extend([5_000_000, 10_000_000])
        algorithms["sieve-wheel30-indexed"].extend([5_000_000, 10_000_000])
        algorithms["sieve-wheel30-bitset"].extend([5_000_000, 10_000_000])
        algorithms["sieve-wheel30-bitset-state"].extend([5_000_000, 10_000_000])
        algorithms["sieve-wheel30-bitset-fsm"].extend(
            [5_000_000, 10_000_000, 20_000_000, 40_000_000, 80_000_000, 100_000_000, 160_000_000]
        )
        algorithms["sieve-lagrange-fsm"].extend(
            [5_000_000, 10_000_000, 20_000_000, 40_000_000, 80_000_000, 100_000_000, 160_000_000, 1_000_000_000]
        )
        algorithms["sieve-lagrange-lehmer-fsm"].extend(
            [
                5_000_000,
                10_000_000,
                20_000_000,
                40_000_000,
                80_000_000,
                100_000_000,
                160_000_000,
                1_000_000_000,
                2_000_000_000,
                4_000_000_000,
                8_000_000_000,
            ]
        )
        algorithms["sieve-lagrange-lehmer-axler-fsm"].extend(
            [
                5_000_000,
                10_000_000,
                20_000_000,
                40_000_000,
                80_000_000,
                100_000_000,
                160_000_000,
                1_000_000_000,
                2_000_000_000,
                4_000_000_000,
                8_000_000_000,
                16_000_000_000,
                32_000_000_000,
                40_000_000_000,
            ]
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["algorithm", "n", "prime", "seconds"], lineterminator="\n")
        writer.writeheader()

        for algorithm, initial_samples in algorithms.items():
            samples = list(initial_samples)
            seen: set[int] = set()
            index = 0
            while index < len(samples):
                n = samples[index]
                index += 1
                if n in seen:
                    continue
                seen.add(n)
                result = run_case(algorithm, n, args.repeats, args.timeout)
                if result is None:
                    print(f"{algorithm:22s} n={n:,}: timeout", flush=True)
                    break
                prime, seconds = result
                print(f"{algorithm:22s} n={n:>10,d} prime={prime:>12,d} seconds={seconds:.6f}", flush=True)
                writer.writerow(
                    {
                        "algorithm": algorithm,
                        "n": n,
                        "prime": prime,
                        "seconds": f"{seconds:.9f}",
                    }
                )
                file.flush()
                if (
                    args.reach_one_second
                    and seconds < 1.0
                    and index == len(samples)
                    and n < args.max_n
                ):
                    samples.append(min(args.max_n, max(n + 1, n * 2)))

    meta_path = write_metadata(args, started_at)
    print(args.output)
    print(meta_path)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
