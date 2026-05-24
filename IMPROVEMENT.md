# Improvement Log

## One-second scorecard

The reference video, [One second to find the BILLIONth PRIME](https://www.youtube.com/watch?v=uJkoI5TnKzA), targets `n = 1,000,000,000` within one second.

This portable C++ reproduction does not claim to beat the video's final LLVM/Linux result. The measured improvement is within this repo's local Windows-friendly benchmark:

Hardware note: the exact one-second prime index is relative to the processor, compiler, operating system, and background load. The percentage improvement is the durable claim because it compares algorithms inside the same benchmark run on the same machine.

Spirit-of-the-video note: this project is aligned with the video's algorithmic speedrun idea, but it is not a full reproduction of every low-level implementation detail or every algorithm in the reference repo. The baseline group is a video-inspired subset; the "mine" group contains portable C++ variants added here.

| Comparison | Estimated one-second reach |
|---|---:|
| Pre-bitset wheel-30 segmented baseline | `26,361,427` |
| Formula skip, `sieve-lagrange-fsm` | `2,142,928,499` |
| Lehmer + pi table, `sieve-lagrange-lehmer-fsm` | `31,167,475,494` |
| Best, `sieve-lagrange-lehmer-axler-fsm` | `32,747,821,786` |

That is a `124126.3%` increase over the pre-bitset local baseline in the latest same-run benchmark. The current best local run proves `n = 1,000,000,000` in `0.039975s`, which is exactly the video's billion-prime headline target. Its interpolated one-second reach is `3274.78%` of that target.

## Implemented: pi_lookup + Axler bounds for Lehmer fast-forward

Added `sieve-lagrange-lehmer-axler-fsm`, which keeps the formula-assisted wheel-30 FSM segmented sieve but removes the largest remaining bottleneck in the fast-forward phase.

The two changes:

1. `make_prime_pi_lookup` builds a dense `pi(x)` prefix table from the base primes for each Lehmer-counting context, so recursive Lehmer calls can answer small prime-count subproblems in constant time instead of repeatedly binary-searching the base-prime list.
2. `BoundStrategy::axler` uses Axler nth-prime upper/lower bounds to tighten the range between the fast-forward starting segment and the final search bound.

The correctness contract is unchanged: the algorithm still computes exact zero-indexed `prime(n)`. The lookup table is only an internal prime-count accelerator; it is not a table of final prime answers.

### Same-run: pi_lookup Lehmer against pi_lookup + Axler

Comparison from the latest same-run benchmark:

```text
output/data/benchmark.csv
```

| n | `sieve-lagrange-lehmer-fsm` | `sieve-lagrange-lehmer-axler-fsm` | Axler delta |
|---:|---:|---:|---:|
| 1,000,000,000 | 0.040638 | 0.039975 | 1.6% faster |
| 2,000,000,000 | 0.073609 | 0.074160 | 0.7% slower |
| 4,000,000,000 | 0.136432 | 0.133154 | 2.4% faster |
| 8,000,000,000 | 0.267871 | 0.257033 | 4.0% faster |
| 16,000,000,000 | 0.518202 | 0.495567 | 4.4% faster |
| 32,000,000,000 | 1.026330 | 0.978487 | 4.7% faster |

The current same-run Lehmer + pi table path estimates `n = 31,167,475,494` at one second. Adding Axler bounds moves that estimate to `n = 32,747,821,786`, a `5.1%` same-run reach gain. Compared with the previous checked-in best before this optimization pass (`n = 12,230,629,361`), the new method is `167.8%` higher and `2.68x` larger.

The headline `n = 32,747,821,786` is an interpolated crossing, not a directly measured row. It comes from log-log interpolation between `n = 32,000,000,000` at `0.978487s` and `n = 40,000,000,000` at `1.207230s`; the interpolation assumes locally smooth power-law-like scaling near the crossing.

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
| 1,000,000,000 | 0.476752 | 0.040638 | 11.73x | 91.5% |
| 2,000,000,000 | 0.931976 | 0.073609 | 12.66x | 92.1% |
| 4,000,000,000 | 1.890760 | 0.136432 | 13.86x | 92.8% |

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
| 10,000,000 | 0.071440 | 0.006427 | 11.12x | 91.0% |
| 40,000,000 | 0.329311 | 0.018745 | 17.57x | 94.3% |
| 100,000,000 | 0.892365 | 0.042828 | 20.84x | 95.2% |
| 160,000,000 | 1.476400 | 0.072368 | 20.40x | 95.1% |

At the video headline target in the latest benchmark CSV, `sieve-lagrange-fsm` computes `prime(1,000,000,000) = 22,801,763,513` in `0.476752s`, before the later Lehmer and Axler refinements.

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
py -3 scripts/compare.py --algorithms sieve-lagrange-lehmer-fsm,sieve-lagrange-lehmer-axler-fsm --n 1000000000,4000000000,8000000000,16000000000,32000000000 --repeats 3 --timeout 20
py -3 scripts/plot.py
```

## Next Candidates

- A carried-state wheel-30 bitset variant was implemented and benchmarked, but it was not counted as an improvement because it measured slower than `sieve-wheel30-bitset` at large `n`.
- Pre-sieve the wheel-30 FSM segments for small primes to reduce hot-loop marking.
- Count complete wheel-period chunks with wider words before drilling into bytes near the target.
- Try a wheel-210 bitset variant to reduce candidate density below wheel-30.
- Consider a reusable Lehmer counter object only if future bracketing or multi-count strategies are revived.
- Extend `scripts/compare.py` to store raw samples and emit before/after comparison reports.
