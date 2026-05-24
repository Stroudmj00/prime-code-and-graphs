# Improvement Log

## One-second scorecard

The reference video, [One second to find the BILLIONth PRIME](https://www.youtube.com/watch?v=uJkoI5TnKzA), sets the one-second billion-prime challenge. This repo follows the upstream QueenJewels convention `prime(0) = 2`, so its benchmark rows use zero-indexed `n`.

This portable C++ reproduction does not claim to beat the video's final LLVM/Linux result with the same low-level method. The measured improvement is within this repo's local Windows-friendly benchmark:

Hardware note: the exact one-second prime index is relative to the processor, compiler, operating system, and background load. The percentage improvement is the durable claim because it compares algorithms inside the same benchmark run on the same machine.

Spirit-of-the-video note: this project is aligned with the video's algorithmic speedrun idea, but it is not a full reproduction of every low-level implementation detail or every algorithm in the reference repo. The baseline group is a video-inspired subset; the "mine" group contains portable C++ variants added here.

For the method-by-method explanation and reference links, see [METHODS.md](METHODS.md). This file is the measurement log: what changed, what improved, and what did not get promoted.

Indexing note: the conventional 1,000,000,000th prime is `prime(999,999,999) = 22,801,763,489` in this repo's zero-indexed notation. The checked benchmark milestone `prime(1,000,000,000) = 22,801,763,513` is one index later.

Integrity note: the fastest variants are exact formula-assisted segmented sieves. They compute exact `pi(base - 1)` with Legendre/Lehmer-style counting, fast-forward the marking state to a near-target segment, and still sieve/count candidates until the requested zero-indexed `prime(n)` is reached. The `pi_lookup` table is generated from base primes at runtime for prime-count subproblems; it is not a stored table of final nth-prime answers.

| Comparison | Estimated one-second reach |
|---|---:|
| Pre-bitset wheel-30 segmented baseline | `26,896,738` |
| Formula skip, `sieve-lagrange-fsm` | `2,145,258,257` |
| Lehmer + pi table, `sieve-lagrange-lehmer-fsm` | `32,471,825,139` |
| Previous best, `sieve-lagrange-lehmer-axler-fsm` | `34,308,358,230` |
| Best, `sieve-lagrange-lehmer-axler-phi7-fsm` | `37,415,030,844` |

That is a `139006.2%` increase over the pre-bitset local baseline in the latest same-run benchmark. The current best reach method proves the repo's zero-indexed billion-scale milestone `n = 1,000,000,000` in `0.050801s`. Its interpolated one-second reach is `3741.50%` of that milestone.

Compared with the previous checked-in best (`sieve-lagrange-lehmer-axler-fsm`), the new `phi7` method moves the same-run one-second reach from `34,308,358,230` to `37,415,030,844`, a `9.1%` lift.

## Implemented: deeper phi cache for Lehmer fast-forward

Added `sieve-lagrange-lehmer-axler-phi7-fsm`, which keeps the same Axler-bounded wheel-30 FSM segmented sieve but changes the exact Lehmer prime-count fast-forward.

The prior Lehmer counter cached `phi(x, a)` for the first six primes. The new method adds a seven-prime cache (`2*3*5*7*11*13*17 = 510,510`) and builds both phi cache tables with a linear sieve-style prefix pass instead of repeated modulo testing. The larger table has a startup cost, so it is slower at small `n`; it wins near the one-second crossing where exact prime counting is large enough to amortize that cost.

### Same-run: Axler against Axler + phi7

Comparison from the latest same-run benchmark:

```text
output/data/benchmark.csv
```

| n | `sieve-lagrange-lehmer-axler-fsm` | `sieve-lagrange-lehmer-axler-phi7-fsm` | phi7 delta |
|---:|---:|---:|---:|
| 1,000,000,000 | 0.037714 | 0.050801 | 34.7% slower |
| 16,000,000,000 | 0.474028 | 0.447935 | 5.5% faster |
| 32,000,000,000 | 0.934285 | 0.865979 | 7.3% faster |
| 40,000,000,000 | 1.161590 | 1.063420 | 8.5% faster |

The headline `n = 37,415,030,844` is an interpolated crossing, not a directly measured row. It comes from log-log interpolation between `n = 32,000,000,000` at `0.865979s` and `n = 40,000,000,000` at `1.063420s`; the interpolation assumes locally smooth power-law-like scaling near the crossing.

## Implemented: pi_lookup + Axler bounds for Lehmer fast-forward

Added `sieve-lagrange-lehmer-axler-fsm`, which keeps the formula-assisted wheel-30 FSM segmented sieve but removes the largest remaining bottleneck in the fast-forward phase.

The two changes:

1. `make_prime_pi_lookup` builds a dense `pi(x)` prefix table from the base primes for each Lehmer-counting context, so recursive Lehmer calls can answer small prime-count subproblems in constant time instead of repeatedly binary-searching the base-prime list.
2. `BoundStrategy::axler` uses Axler nth-prime upper/lower bounds to tighten the range between the fast-forward starting segment and the final search bound.

The correctness contract is unchanged: the algorithm still computes exact zero-indexed `prime(n)`. The lookup table is only an internal prime-count accelerator generated from base primes for the current run; it is not a table of final prime answers.

### Same-run: pi_lookup Lehmer against pi_lookup + Axler

Comparison from the latest same-run benchmark:

```text
output/data/benchmark.csv
```

| n | `sieve-lagrange-lehmer-fsm` | `sieve-lagrange-lehmer-axler-fsm` | Axler delta |
|---:|---:|---:|---:|
| 1,000,000,000 | 0.043673 | 0.037714 | 13.6% faster |
| 2,000,000,000 | 0.075549 | 0.071029 | 6.0% faster |
| 4,000,000,000 | 0.141960 | 0.126826 | 10.7% faster |
| 8,000,000,000 | 0.255945 | 0.249138 | 2.7% faster |
| 16,000,000,000 | 0.506308 | 0.474028 | 6.4% faster |
| 32,000,000,000 | 0.985613 | 0.934285 | 5.2% faster |

The current same-run Lehmer + pi table path estimates `n = 32,471,825,139` at one second. Adding Axler bounds moves that estimate to `n = 34,308,358,230`, a `5.7%` same-run reach gain.

The Axler-only headline `n = 34,308,358,230` is interpolated between `n = 32,000,000,000` at `0.934285s` and `n = 40,000,000,000` at `1.161590s`.

## Implemented: Lehmer fast-forward plus FSM bitset sieve

Added `sieve-lagrange-lehmer-fsm`, which keeps the same final wheel-30 FSM bitset sieve but replaces the exact `pi(base - 1)` computation with Lehmer prime counting.

The original formula-assisted variant used Legendre's formula:

```text
pi(x) = phi(x, pi(sqrt(x))) + pi(sqrt(x)) - 1
```

That works, but at billion-scale targets its recursive `phi` term dominates the fast-forward cost. The Lehmer variant computes the same exact prime count with fewer expensive partial-sieve calls, then starts the final sieve from the same conservative Dusart lower-bound segment.

### Before / After: Lehmer against Legendre fast-forward

Comparison from the same 3-repeat reach benchmark run:

```text
output/data/benchmark.csv
```

| n | `sieve-lagrange-fsm` | `sieve-lagrange-lehmer-fsm` | Speedup | Faster |
|---:|---:|---:|---:|---:|
| 1,000,000,000 | 0.451025 | 0.043673 | 10.33x | 90.3% |
| 2,000,000,000 | 0.934983 | 0.075549 | 12.38x | 91.9% |
| 4,000,000,000 | 1.817370 | 0.141960 | 12.80x | 92.2% |

In the latest benchmark CSV, `sieve-lagrange-fsm` is already over one second by `n = 4,000,000,000`, while `sieve-lagrange-lehmer-fsm` remains under one second through `n = 16,000,000,000` and crosses between `32,000,000,000` and `40,000,000,000`.

Two researched variants were not promoted:

- Approximation-centered tight start was slower because the extra prime-count calls cost more than the final sieve work they saved.
- Larger segment-size variants were roughly tied and not a durable enough improvement to replace the default `1 << 16` wheel-period segment.

## Implemented: Lagrange/Legendre fast-forward plus FSM bitset sieve

Added `sieve-lagrange-fsm`, a portable C++ version of the reference repo's Lagrange-formula idea, but grafted onto this repo's fastest wheel-30 FSM bitset marker.

The method:

1. Builds sieving primes up to `sqrt(upper_bound(n))`.
2. Uses a Dusart-style lower bound to choose a segment base near the target prime.
3. Computes exact `pi(base - 1)` with Legendre's partial sieve function `phi(x, a)`.
4. Fast-forwards each wheel-30 FSM sieving state to the first composite multiple in the target segment.
5. Sieves forward from there until the requested zero-indexed `prime(n)` is reached.

The first draft exposed a major implementation bottleneck: the small `phi` cache was initialized with quadratic counting. Replacing that with a linear prefix table made the formula path viable.

### Before / After: formula fast-forward against previous fastest

Comparison from the same 3-repeat reach benchmark run:

```text
output/data/benchmark.csv
```

| n | Previous `sieve-wheel30-bitset-fsm` | New `sieve-lagrange-fsm` | Speedup | Faster |
|---:|---:|---:|---:|---:|
| 10,000,000 | 0.073174 | 0.006715 | 10.90x | 90.8% |
| 40,000,000 | 0.339875 | 0.020059 | 16.94x | 94.1% |
| 100,000,000 | 0.952201 | 0.047067 | 20.23x | 95.1% |
| 160,000,000 | 1.596870 | 0.073733 | 21.66x | 95.4% |

At the repo's zero-indexed billion-scale milestone in the latest benchmark CSV, `sieve-lagrange-fsm` computes `prime(1,000,000,000) = 22,801,763,513` in `0.451025s`, before the later Lehmer, Axler, and phi7 refinements.

## Earlier implementation layers

The current benchmark CSV keeps the repo focused on one canonical evidence set, so older exploratory CSV snapshots are no longer tracked. The earlier optimization layers remain implemented and are still represented in `output/data/benchmark.csv` and `output/graphs/summary.md`:

- `sieve-wheel30-bitset-fsm`: precomputes an eight-state wheel transition table so each base prime marks wheel-30 candidate bytes with table lookups and additions instead of repeated multiply/divide/modulo work.
- `sieve-erat-odd` and `sieve-erat-segm-odd`: store and mark only odd candidates, with `2` handled separately.
- `sieve-wheel30-bitset`: compresses one modulo-30 wheel period into a byte, using bits for `{1, 7, 11, 13, 17, 19, 23, 29}`.
- `sieve-wheel30-indexed`: allocates only the eight valid modulo-30 candidates per period and walks the wheel delta pattern `{6, 4, 2, 4, 2, 4, 6, 2}`.
- tiered deterministic Miller-Rabin: selects smaller deterministic base sets for bounded candidate ranges before falling back to the full 64-bit deterministic base set.

This keeps the repo readable for recruiters: the current story is benchmarked from one CSV, and the lower-level implementation history explains what changed without mixing stale timing snapshots into the headline result.

## Validation

```console
py -3 scripts/build.py
py -3 scripts/verify.py --fast
py -3 scripts/bench.py --repeats 3 --timeout 8 --full --reach-one-second -o output/data/benchmark.csv
py -3 scripts/compare.py --algorithms sieve-lagrange-lehmer-axler-fsm,sieve-lagrange-lehmer-axler-phi7-fsm --n 16000000000,32000000000,40000000000 --repeats 3 --timeout 20
py -3 scripts/plot.py
```

## Researched but not promoted

- Exact Lehmer `pi(x)` inversion was correct but much slower than the segmented nth-prime path.
- Approximation-centered Miller-Rabin scanning was correct but lost at large `n`.
- A wheel-210 FSM sieve, pre-sieved wheel-30 segments, chunked popcount scanning, segment-size tuning, and a parallel final-window sieve were prototyped and benchmarked. None produced a repeatable enough same-run lift to replace `phi7`.
- Future candidates should focus on reducing the final segmented-sieve scan without adding extra exact prime-count calls, or on a more advanced prime-counting method if the project intentionally moves beyond the video's simple C++ speedrun spirit.
