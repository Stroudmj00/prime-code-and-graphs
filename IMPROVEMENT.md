# Improvement Log

## One-second scorecard

The reference video, [One second to find the BILLIONth PRIME](https://www.youtube.com/watch?v=uJkoI5TnKzA), targets `n = 1,000,000,000` within one second.

This portable C++ reproduction does not claim to beat the video's final LLVM/Linux result. The measured improvement is within this repo's local Windows-friendly benchmark:

Hardware note: the exact one-second prime index is relative to the processor, compiler, operating system, and background load. The percentage improvement is the durable claim because it compares algorithms inside the same benchmark run on the same machine.

Spirit-of-the-video note: this project is aligned with the video's algorithmic speedrun idea, but it is not a full reproduction of every low-level implementation detail or every algorithm in the reference repo. The baseline group is a video-inspired subset; the "mine" group contains portable C++ variants added here.

| Comparison | Estimated one-second reach |
|---|---:|
| Pre-bitset wheel-30 segmented baseline | `27,007,283` |
| Previous best, `sieve-lagrange-fsm` | `2,392,780,010` |
| Current best, `sieve-lagrange-lehmer-fsm` | `12,230,629,361` |

That is a `45186.4%` increase over the pre-bitset local baseline. The current best local run proves `n = 1,000,000,000` in `0.120388s`, which is exactly the video's billion-prime headline target. Its interpolated one-second reach is `1223.06%` of that target.

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

| n | Previous `sieve-lagrange-fsm` | New `sieve-lagrange-lehmer-fsm` | Speedup | Faster |
|---:|---:|---:|---:|---:|
| 1,000,000,000 | 0.419406 | 0.120388 | 3.48x | 71.3% |
| 2,000,000,000 | 0.835971 | 0.211634 | 3.95x | 74.7% |
| 4,000,000,000 | 1.670990 | 0.377699 | 4.42x | 77.4% |

At `n = 8,000,000,000`, the Lehmer variant still runs under one second at `0.690345s`. Its next measured sample, `n = 16,000,000,000`, takes `1.264290s`, giving a log-interpolated one-second reach of `n = 12,230,629,361`.

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

At the video headline target, `sieve-lagrange-fsm` computes `prime(1,000,000,000) = 22,801,763,513` in `0.419406s`. The older FSM method returns the same prime in a direct check, but takes about `11.2s` on this machine.

## Implemented: wheel-30 FSM bitset segmented sieve

Added `sieve-wheel30-bitset-fsm`, which keeps the compact one-byte-per-wheel-period layout but removes repeated multiply/divide/modulo work from the marking loop.

For each base prime, the implementation precomputes an eight-state wheel transition table:

```text
state -> mark bit, byte-period advance, next multiple delta
```

The inner marking loop now updates the composite byte with table lookups and additions. This preserves the same wheel-30 candidate set as `sieve-wheel30-bitset`, but makes marking much cheaper at high `n`.

### Before / After: FSM bitset against previous fastest

Comparison from the same 3-repeat reach benchmark run:

```text
output/data/benchmark.reach-100m-fsm.csv
```

| n | Previous `sieve-wheel30-bitset` | New `sieve-wheel30-bitset-fsm` | Speedup | Faster |
|---:|---:|---:|---:|---:|
| 10,000,000 | 0.126758 | 0.062832 | 2.02x | 50.4% |
| 20,000,000 | 0.270713 | 0.137084 | 1.97x | 49.4% |
| 40,000,000 | 0.570602 | 0.283833 | 2.01x | 50.3% |
| 80,000,000 | 1.224690 | 0.622193 | 1.97x | 49.2% |

At the target milestone, `sieve-wheel30-bitset-fsm` computed `prime(100,000,000) = 2,038,074,751` in `0.798666s` in the earlier `benchmark.reach-100m-fsm.csv` run. A separate direct seven-run target check also returned the same prime every time, with a median around `0.793s`.

## Implemented: packed odd-only Sieve of Eratosthenes

Added `sieve-erat-odd`, which keeps the dense Sieve of Eratosthenes but stores and marks only odd candidates. The composite table maps:

```text
index i => 2*i + 3
```

`2` is handled up front, and the mark loop advances by `2*p`, avoiding every even multiple. The implementation uses a packed `std::vector<bool>` table so the odd-only candidate reduction also cuts memory pressure at larger bounds.

### Before / After: dense sieve against odd-only dense sieve

Comparison from the same 7-repeat benchmark run:

```text
output/data/benchmark.after-odd-sieves.csv
```

| n | Previous `sieve-erat` | New `sieve-erat-odd` | Speedup | Faster |
|---:|---:|---:|---:|---:|
| 524,288 | 0.019443 | 0.011117 | 1.75x | 42.8% |
| 1,000,000 | 0.042692 | 0.021991 | 1.94x | 48.5% |
| 2,000,000 | 0.098308 | 0.053648 | 1.83x | 45.4% |
| 5,000,000 | 0.306420 | 0.155944 | 1.96x | 49.1% |
| 10,000,000 | 0.736943 | 0.351471 | 2.10x | 52.3% |

## Implemented: odd-only segmented Sieve of Eratosthenes

Added `sieve-erat-segm-odd`, which applies the same odd-only indexing to the segmented sieve. Each segment stores only odd offsets, skips prime `2` in the base-prime marking loop, adjusts the first multiple to an odd multiple, then marks by `2*p`.

### Before / After: segmented sieve against odd-only segmented sieve

Comparison from the same 7-repeat benchmark run:

```text
output/data/benchmark.after-odd-sieves.csv
```

| n | Previous `sieve-erat-segm` | New `sieve-erat-segm-odd` | Speedup | Faster |
|---:|---:|---:|---:|---:|
| 524,288 | 0.020275 | 0.009618 | 2.11x | 52.6% |
| 1,000,000 | 0.039731 | 0.018584 | 2.14x | 53.2% |
| 2,000,000 | 0.082207 | 0.037888 | 2.17x | 53.9% |
| 5,000,000 | 0.220443 | 0.101519 | 2.17x | 53.9% |
| 10,000,000 | 0.457694 | 0.210510 | 2.17x | 54.0% |

## Implemented: wheel-30 bitset segmented sieve

Added `sieve-wheel30-bitset`, which compresses a full wheel period into one byte:

```text
bit 0..7 => {1, 7, 11, 13, 17, 19, 23, 29} mod 30
```

Compared with `sieve-wheel30-indexed`, this reduces the segment array from eight bytes per period to one byte per period and counts complete periods with `std::popcount()`.

### Before / After: compact bitset against previous fastest

Comparison from the same 7-repeat benchmark run:

```text
output/data/benchmark.after-wheel-bitset.csv
```

| n | Previous `sieve-wheel30-indexed` | New `sieve-wheel30-bitset` | Speedup | Faster |
|---:|---:|---:|---:|---:|
| 16,384 | 0.000243 | 0.000101 | 2.41x | 58.4% |
| 65,536 | 0.000989 | 0.000476 | 2.08x | 51.9% |
| 262,144 | 0.004405 | 0.002278 | 1.93x | 48.3% |
| 524,288 | 0.009362 | 0.004744 | 1.97x | 49.3% |
| 1,000,000 | 0.018271 | 0.009857 | 1.85x | 46.1% |
| 2,000,000 | 0.036836 | 0.022145 | 1.66x | 39.9% |
| 5,000,000 | 0.096865 | 0.060201 | 1.61x | 37.9% |
| 10,000,000 | 0.210786 | 0.135409 | 1.56x | 35.8% |

Against the older `sieve-wheel30-segm` path in the same run, the bitset path improves `n=10,000,000` from `0.393875s` to `0.135409s`, a `2.91x` speedup.

Against the plain segmented sieve in the same run, it improves `n=10,000,000` from `0.473282s` to `0.135409s`, a `3.50x` speedup.

The current graph dataset now uses:

```text
output/data/benchmark.csv
```

## Implemented: wheel-indexed segmented sieve

Added `sieve-wheel30-indexed`, a true modulo-30 candidate layout. Instead of allocating one composite slot per integer and checking `n % 30` while counting, it allocates eight candidate slots per period of thirty integers.

Composite marking also walks only wheel-valid multipliers, using the wheel delta pattern:

```text
{6, 4, 2, 4, 2, 4, 6, 2}
```

At `n=10,000,000`, this improved the old `sieve-wheel30-segm` path from `0.360887s` to `0.213921s` in `output/data/benchmark.after-wheel-indexed.csv`, a `1.69x` speedup.

## Implemented: tiered Miller-Rabin bases

The original portable C++ reproduction always tested the same 12 Miller-Rabin bases. The reference notes use smaller deterministic base sets for bounded input ranges, so `is_prime_miller_rabin()` now selects a base tier by candidate value.

Comparison uses the same sample matrix and `--repeats 3` data files:

```text
output/data/benchmark.before-mr-tiering.csv
output/data/benchmark.after-mr-tiering.r3.csv
```

| n | Before seconds | After seconds | Speedup | Faster |
|---:|---:|---:|---:|---:|
| 512 | 0.001293500 | 0.000128000 | 10.10x | 90.1% |
| 2,048 | 0.006494400 | 0.001107000 | 5.87x | 83.0% |
| 8,192 | 0.032232400 | 0.006458300 | 4.99x | 80.0% |
| 16,384 | 0.069365400 | 0.014740900 | 4.71x | 78.7% |
| 32,768 | 0.150694000 | 0.032188300 | 4.68x | 78.6% |
| 65,536 | 0.344786000 | 0.071993700 | 4.79x | 79.1% |

## Validation

```console
py -3 scripts/build.py
py -3 scripts/verify.py --fast
py -3 scripts/bench.py --repeats 7 --timeout 8 --full -o output/data/benchmark.after-mr-tiering.csv
py -3 scripts/bench.py --repeats 7 --timeout 8 --full -o output/data/benchmark.after-wheel-indexed.csv
py -3 scripts/bench.py --repeats 7 --timeout 8 --full -o output/data/benchmark.after-wheel-bitset.csv
py -3 scripts/bench.py --repeats 7 --timeout 8 --full -o output/data/benchmark.after-odd-sieves.csv
py -3 scripts/bench.py --repeats 3 --timeout 8 --full --reach-one-second -o output/data/benchmark.csv
py -3 scripts/compare.py --algorithms sieve-lagrange-fsm,sieve-lagrange-lehmer-fsm --n 1000000000,4000000000,8000000000 --repeats 3 --timeout 20
py -3 scripts/plot.py
```

## Next Candidates

- A carried-state wheel-30 bitset variant was implemented and benchmarked, but it was not counted as an improvement because it measured slower than `sieve-wheel30-bitset` at large `n`.
- Pre-sieve the wheel-30 FSM segments for small primes to reduce hot-loop marking.
- Count complete wheel-period chunks with wider words before drilling into bytes near the target.
- Try a wheel-210 bitset variant to reduce candidate density below wheel-30.
- Consider a reusable Lehmer counter object only if future bracketing or multi-count strategies are revived.
- Extend `scripts/compare.py` to store raw samples and emit before/after comparison reports.
