#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "prime_bench.cpp"
BIN_DIR = ROOT / "output" / "bin"
EXE = BIN_DIR / ("prime_bench.exe" if os.name == "nt" else "prime_bench")


def find_compiler(preferred: str | None) -> str:
    if preferred:
        return preferred
    for candidate in ("clang++", "g++", "c++"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise SystemExit("No C++ compiler found. Install clang++ or g++.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the prime benchmark binary")
    parser.add_argument("--cxx", help="C++ compiler to use")
    parser.add_argument("--debug", action="store_true", help="Build without optimizations")
    args = parser.parse_args()

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    cxx = find_compiler(args.cxx)
    flags = ["-std=c++20", "-Wall", "-Wextra", "-pedantic"]
    flags += ["-O0", "-g"] if args.debug else ["-O3", "-march=native"]
    cmd = [cxx, *flags, str(SRC), "-o", str(EXE)]
    print(" ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)
    print(EXE)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
