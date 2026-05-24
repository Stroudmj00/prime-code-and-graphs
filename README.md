# Prime Code and Graphs

Portable reproduction of the algorithm/code-and-graphs side of
["One second to find the BILLIONth PRIME"](https://www.youtube.com/watch?v=uJkoI5TnKzA).

The video asks a simple performance question: how large can `n` get if a program has one second to compute `prime(n)`? The video's headline target is the billionth prime, `n = 1,000,000,000`.

The upstream reference repo, `SheafificationOfG/QueenJewels`, uses Linux-specific LLVM IR and raw Linux syscalls. This folder keeps the same zero-indexed `prime(n)` convention and makes an inspectable Windows-friendly C++ version, then improves that portable version with measured before/after benchmarks. The current portable implementation reaches the video's headline `n = 1,000,000,000` target in under one second on this machine.

## Is This In The Spirit Of The Video?

Yes, with a specific scope. The spirit of the video is an algorithmic speedrun: start with simple prime-finding methods, keep the one-second budget fixed, and improve how far `prime(n)` can go through better algorithms and tighter implementation.

This project follows that spirit because it:

- keeps the same `prime(n)` task and zero-indexed convention;
- measures every algorithm against a one-second budget;
- shows the progression from trial division to sieving to wheel-based segmented sieving;
- adds new implementation ideas only when they still compute the prime directly, not by table lookup.

The scope is different from the video. This repo is portable C++ on Windows, while the reference project is low-level LLVM IR with Linux-specific runtime choices. The honest claim is: within this portable local reproduction, the added formula-assisted variant improves the same-run baseline by `45186.4%`, and the current implementation reaches `n = 1,000,000,000` in well under one second on this machine.

## Current Local Score

Important disclaimer: the exact one-second prime index is hardware-relative. CPU, compiler, operating system, thermals, and background load can all move the absolute `n`. The useful comparison is the percentage improvement between algorithms measured in the same local benchmark run.

The latest one-second reach benchmark on this machine estimates:

```text
best local method:      sieve-lagrange-lehmer-fsm
video target proof:     n = 1,000,000,000 in 0.120388s
prime(1,000,000,000):   22,801,763,513
estimated 1s reach:     n = 12,230,629,361
measured over 1s:       n = 16,000,000,000 in 1.264290s
```

The pre-bitset wheel-30 segmented baseline reaches an estimated `n = 27,007,283` at one second. The Lehmer-assisted FSM method reaches `n = 12,230,629,361`, which is `45186.4%` higher on this machine.

The concrete milestone `n = 1,000,000,000` is exactly the video's headline target. The interpolated one-second reach, `n = 12,230,629,361`, is `1223.06%` of that target. The exact index is still hardware-relative; the durable claim is the same-run improvement between algorithms in this repo.

## Visualization Guide

The lead graph is the story scorecard. It is designed to answer four questions without needing to read the benchmark table first:

- what the video was targeting: `n = 1,000,000,000` in one second;
- where the portable baseline landed: `n = 27,007,283` estimated at one second;
- where my best method landed: `n = 12,230,629,361` estimated at one second;
- what was directly measured: `n = 1,000,000,000` in `0.120388s`.

The runtime plot is the audit view: it cleanly separates the video-inspired baseline subset from my portable C++ improvements, and both panels keep the one-second line visible. The one-second reach plot is the ranking view: it shows how far each algorithm gets in one second, grouped into video-inspired algorithms and my added variants.

![Story scorecard](output/graphs/story_scorecard.png)

![Runtime curves](output/graphs/runtime_curves.png)

![One-second reach](output/graphs/one_second_reach.png)

## Algorithms

This project now separates the video-inspired baseline subset from the variants added in this repo.

Video-inspired baseline subset:

- naive iteration
- square-root trial division
- deterministic Miller-Rabin iteration
- Sieve of Eratosthenes
- segmented Sieve of Eratosthenes
- wheel-30 segmented sieve

My portable C++ improvements:

- odd-only Sieve of Eratosthenes
- odd-only segmented Sieve of Eratosthenes
- wheel-30 indexed segmented sieve
- wheel-30 bitset segmented sieve
- wheel-30 stateful bitset segmented sieve
- wheel-30 FSM bitset segmented sieve
- Lagrange/Legendre fast-forward plus wheel-30 FSM bitset segmented sieve
- Lehmer fast-forward plus wheel-30 FSM bitset segmented sieve

## Build

Requirements:

- Python 3
- `clang++`, `g++`, or another C++20 compiler passed with `--cxx`
- Python plotting dependency: `py -3 -m pip install -r requirements.txt`

```console
py -3 scripts/build.py
```

## Verify

```console
py -3 scripts/verify.py --fast
```

## Run One Algorithm

```console
output\bin\prime_bench.exe sieve-lagrange-lehmer-fsm 1000000000
```

The program prints the zero-indexed nth prime.

## Generate Benchmark Data and Graphs

```console
py -3 scripts/bench.py --repeats 3 --timeout 8 --full --reach-one-second -o output\data\benchmark.csv
py -3 scripts/plot.py
```

For quick candidate comparisons without regenerating every graph:

```console
py -3 scripts/compare.py --algorithms sieve-lagrange-fsm,sieve-lagrange-lehmer-fsm --n 1000000000,4000000000,8000000000 --repeats 3
```

Generated files:

```text
output/data/benchmark.csv
output/graphs/story_scorecard.png
output/graphs/runtime_curves.png
output/graphs/one_second_reach.png
output/graphs/prime_growth.png
output/graphs/summary.md
```

## Notes

The one-second reach values are log-interpolated between measured samples around the one-second crossing. The summary file also shows the last measured point below one second and the next measured point above one second for each algorithm.

See `IMPROVEMENT.md` for the measured implementation improvements: Lehmer fast-forwarding, Lagrange/Legendre fast-forwarding, Miller-Rabin base tiering, wheel-30 indexing, wheel-30 bitset packing, wheel-30 FSM marking, packed odd-only dense sieving, and odd-only segmented sieving.
