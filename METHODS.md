# Methods Explained

This document is the plain-English map of the benchmark. It explains what each algorithm is trying to do, why the later methods are still honest `prime(n)` computations, and which references inspired the implementation.

The headline result is not a claim that this repo reproduces the video's Linux/LLVM implementation byte-for-byte. It is a portable C++ implementation of the same one-second nth-prime challenge, with additional exact accelerators layered on top.

## Video Rules / Challenge Contract

This is the rule set used throughout the repo:

- Input: a zero-indexed prime index `n`, matching the upstream convention `prime(0) = 2`.
- Output: the exact value of `prime(n)`.
- Benchmark: estimate how large `n` can be while staying under one second on the same machine.
- Integrity rule: no stored table of final nth-prime answers. Lookup tables in this repo are generated during the run and only accelerate subproblems such as `pi(x)`.
- Hardware rule: the absolute one-second `n` depends on CPU, compiler, OS, thermals, and background load. Same-run relative lift is the durable comparison.

## Score Ladder

The current canonical benchmark is `output/data/benchmark.csv`; the graph summary is `output/graphs/summary.md`.

| Layer | Code id | What changed | Estimated one-second reach |
|---|---|---|---:|
| Wheel baseline | `sieve-wheel30-segm` | Segmented sieve over wheel-30 candidates | `26,896,738` |
| Bitset packing | `sieve-wheel30-bitset` | One byte stores the eight valid residues in each modulo-30 period | `66,110,091` |
| FSM marking | `sieve-wheel30-bitset-fsm` | Precomputed state transition table removes repeated modulo/division during marking | `104,553,081` |
| Legendre skip | `sieve-lagrange-fsm` | Uses exact `pi(base - 1)` to skip wasted middle segments | `2,145,258,257` |
| Lehmer + pi table | `sieve-lagrange-lehmer-fsm` | Replaces Legendre prime counting with Lehmer-style recursive counting and a generated `pi(x)` prefix table | `32,471,825,139` |
| Axler bound | `sieve-lagrange-lehmer-axler-fsm` | Uses tighter nth-prime lower/upper bounds to shrink the final search window | `34,308,358,230` |
| Deeper phi table | `sieve-lagrange-lehmer-axler-phi7-fsm` | Extends the small `phi(x, a)` cache from six primes to seven primes | `37,415,030,844` |

The promoted method proves the repo's zero-indexed billion-scale milestone directly:

```text
prime(1,000,000,000) = 22,801,763,513
time = 0.050801s
```

Its interpolated one-second reach is `37,415,030,844`, between the measured `32B` and `40B` rows.

## Method by Method

### 1. Naive Iteration

Code id: `naive-iterate`

This is the reference floor: walk through integers, test each one for primality by trying possible divisors, and stop when the nth prime is found. It is intentionally simple and slow. It exists to make the first performance jump visible.

### 2. Square-Root Trial Division

Code id: `sqrt-iterate`

A composite number has at least one nontrivial factor no larger than its square root. This method keeps the same iteration shape as the naive method, but each primality check stops once the divisor exceeds `sqrt(candidate)`.

### 3. Deterministic Miller-Rabin Iteration

Code id: `miller-rabin-iterate`

Miller-Rabin is normally a probabilistic primality test, but for bounded machine integers fixed witness sets can make it deterministic. In this repo it is a video-inspired baseline row, not part of the final winning path.

### 4. Sieve of Eratosthenes

Code ids: `sieve-erat`, `sieve-erat-odd`

Instead of testing each candidate independently, the sieve marks composites in bulk. Once a prime `p` is found, multiples of `p` starting at `p*p` are composite. The odd-only version handles `2` separately and stores only odd candidates, halving memory and scanning work.

### 5. Segmented Sieve

Code ids: `sieve-erat-segm`, `sieve-erat-segm-odd`

A full sieve up to the nth-prime upper bound is memory-heavy and cache-unfriendly. Segmentation keeps only one interval in memory at a time, marks it with base primes up to the square root of the global bound, counts primes in that segment, then moves to the next segment.

### 6. Wheel-30 Segmented Sieve

Code id: `sieve-wheel30-segm`

The wheel removes candidates divisible by `2`, `3`, or `5` before marking starts. In each block of 30 integers, only residues `{1, 7, 11, 13, 17, 19, 23, 29}` can contain primes above 5. This cuts candidate density to 8 out of every 30 integers.

### 7. Indexed, Bitset, Stateful, and FSM Wheel Variants

Code ids: `sieve-wheel30-indexed`, `sieve-wheel30-bitset`, `sieve-wheel30-bitset-state`, `sieve-wheel30-bitset-fsm`

These variants keep the same mathematical sieve but improve the representation and marking loop:

- `indexed` stores only wheel-valid candidates.
- `bitset` packs the eight valid residues in one modulo-30 period into one byte.
- `stateful` carries per-prime marking state between segments.
- `fsm` precomputes the eight-step wheel transition pattern so marking avoids repeated division/modulo work.

The FSM row is the best "pure final sieve" variant in this repo.

### 8. Legendre Fast-Forward

Code id: `sieve-lagrange-fsm`

The code id keeps the earlier `lagrange` label for continuity with the existing benchmark CSVs. The math being used here is Legendre-style exact prime counting.

The reference repo's Lagrange/Legendre idea is the first large conceptual jump. A segmented sieve normally walks every segment from the beginning to the target. For large `n`, most middle segments are not interesting: they only contribute to the prime count.

This method:

1. Chooses a conservative lower-bound segment near the target prime.
2. Computes the exact number of primes before that segment, `pi(base - 1)`.
3. Initializes the wheel-30 FSM marker as if earlier segments had already been processed.
4. Sieves forward from that segment until the exact requested `prime(n)` is reached.

This is honest because it does not guess the final prime. It only replaces a long count-through-the-middle pass with an exact prime-counting computation.

### 9. Lehmer Fast-Forward

Code id: `sieve-lagrange-lehmer-fsm`

Legendre counting is exact but expensive for the sizes used here. Lehmer's formula computes the same prime-counting function with fewer recursive partial-sieve calls. In this repo Lehmer counting is only used to answer "how many primes are before this segment?", then the final segmented sieve still finds the exact prime.

### 10. Generated `pi_lookup`

Included in: `sieve-lagrange-lehmer-fsm` and later

The Lehmer recursion repeatedly asks for small `pi(x)` values. This repo builds a dense prefix table from the generated base primes for the current run, so those small subproblems are constant-time lookups.

This is not a final-answer shortcut: it stores counts of primes up to small `x`, not `prime(n)` values.

### 11. Axler Bounds

Code id: `sieve-lagrange-lehmer-axler-fsm`

An nth-prime solver needs a lower bound and an upper bound around the target. Tighter bounds reduce the number of final segments that must be scanned. This variant uses Christian Axler's explicit nth-prime bounds for sufficiently large indices and falls back to the older bound below the validity threshold.

The correctness contract is unchanged: if the final scan reaches the bound without finding the prime, the implementation doubles the bound and continues.

### 12. Deeper `phi7` Cache

Code id: `sieve-lagrange-lehmer-axler-phi7-fsm`

Lehmer counting depends heavily on the partial sieve function `phi(x, a)`. The previous cache handled the first six primes. The promoted method adds a seven-prime cache over the primorial `2*3*5*7*11*13*17 = 510,510` and builds the prefix tables with a linear sieve-style pass.

The larger cache has startup cost, so it is slower at `n = 1B`. It wins near the one-second crossing because the larger prime-counting calls amortize that cost.

## Why the Fast Path Is Still in Spirit

It is in spirit because it keeps the same challenge shape: compute `prime(n)` exactly and race the one-second wall. It also keeps the same broad algorithmic family: sieving, wheel factorization, and exact prime-counting formulas.

It is not the same low-level method as the video/reference repo. The reference implementation is LLVM IR and Linux-syscall oriented; this project is portable C++ and adds Lehmer/Axler/phi-cache accelerators. The README therefore describes the result as a portable, video-inspired extension rather than a direct reproduction of the video's final implementation.

## Code Map

- `src/prime_bench.cpp`: all C++ algorithms and the command-line entrypoint.
- `scripts/build.py`: compiler wrapper and build metadata.
- `scripts/verify.py`: correctness checks, including high-n and Axler-boundary cases.
- `scripts/bench.py`: repeatable timing runner that writes the canonical CSV and metadata.
- `scripts/compare.py`: quick same-run candidate comparison helper.
- `scripts/plot.py`: regenerates audit graphs and `output/graphs/summary.md`; it intentionally does not overwrite the image-generated README scorecard.
- `output/graphs/story_scorecard.prompt.md`: reviewed stats and image-generation prompt for the lead scorecard.

## References

- Video challenge: [One second to find the BILLIONth PRIME](https://www.youtube.com/watch?v=uJkoI5TnKzA)
- Reference repo: [SheafificationOfG/QueenJewels](https://github.com/SheafificationOfG/QueenJewels)
- Sieve background: [Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes)
- Wheel background: [Wheel factorization](https://en.wikipedia.org/wiki/Wheel_factorization)
- Deterministic Miller-Rabin context: [Miller-Rabin SPRP bases](https://miller-rabin.appspot.com/) and Jaeschke, [On strong pseudoprimes to several bases](https://www.ams.org/journals/mcom/1993-61-204/S0025-5718-1993-1192971-8/S0025-5718-1993-1192971-8.pdf)
- Legendre counting: [Legendre's Formula, MathWorld](https://mathworld.wolfram.com/LegendresFormula.html)
- Lehmer counting: [Lehmer's Formula, MathWorld](https://mathworld.wolfram.com/LehmersFormula.html)
- Meissel-Lehmer context: [HandWiki summary with original paper links](https://handwiki.org/wiki/Meissel%E2%80%93Lehmer_algorithm)
- Classic nth-prime bounds: Rosser and Schoenfeld, [Approximate formulas for some functions of prime numbers](https://projecteuclid.org/journals/illinois-journal-of-mathematics/volume-6/issue-1/Approximate-formulas-for-some-functions-of-prime-numbers/10.1215/ijm/1255631807.full)
- Dusart lower-bound context: [Estimates of Some Functions Over Primes without R.H.](https://arxiv.org/abs/1002.0442)
- Axler nth-prime bounds: [New Estimates for the nth Prime Number](https://cs.uwaterloo.ca/journals/JIS/VOL22/Axler/axler17.html) and [arXiv:1706.03651](https://arxiv.org/abs/1706.03651)
