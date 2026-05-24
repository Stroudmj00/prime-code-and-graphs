#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "prime_bench.cpp"
BIN_DIR = ROOT / "output" / "bin"
EXE = BIN_DIR / ("prime_bench.exe" if os.name == "nt" else "prime_bench")
BUILD_META = BIN_DIR / "build_meta.json"


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
    parser.add_argument(
        "--portable",
        action="store_true",
        help="Build an optimized generic binary without -march=native",
    )
    args = parser.parse_args()

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    cxx = find_compiler(args.cxx)
    flags = ["-std=c++20", "-Wall", "-Wextra", "-pedantic"]
    if args.debug:
        flags += ["-O0", "-g"]
    elif args.portable:
        flags += ["-O3"]
    else:
        flags += ["-O3", "-march=native"]
    cmd = [cxx, *flags, str(SRC), "-o", str(EXE)]
    print(" ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)
    BUILD_META.write_text(
        json.dumps(
            {
                "built_at_utc": dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z"),
                "compiler": cxx,
                "flags": flags,
                "portable": bool(args.portable),
                "debug": bool(args.debug),
                "platform": platform.platform(),
                "machine": platform.machine(),
                "python": sys.version.split()[0],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(EXE)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
