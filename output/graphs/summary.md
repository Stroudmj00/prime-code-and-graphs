# Benchmark Summary

Video context: [One second to find the BILLIONth PRIME](https://www.youtube.com/watch?v=uJkoI5TnKzA) sets the one-second billion-prime challenge.

Indexing note: this repo follows the upstream zero-indexed convention `prime(0) = 2`. The conventional 1,000,000,000th prime is `prime(999,999,999) = 22,801,763,489`; the checked benchmark milestone `prime(1,000,000,000) = 22,801,763,513` is one index later.

All comparisons below are same-run. Exact prime-index values are hardware-relative; the meaningful claim is relative lift between algorithms measured together.
The fastest variants use exact prime-count fast-forwarding plus a final segmented sieve; the `pi_lookup` accelerator is not a stored table of final nth-prime answers.

Local best: `Lehmer + Axler + phi7` reaches an estimated `n = 37,415,030,844` at one second.
Measured under-one-second anchor: `n = 32,000,000,000` at `0.865979s`.
Interpolation bracket: log-log interpolation between `n = 32,000,000,000` at `0.865979s` and `n = 40,000,000,000` at `1.063420s`.
Index note: benchmark rows use zero-indexed `n`; interpolation is performed on `n + 1` and converted back to zero-indexed `n`.
Best vs. pre-bitset wheel-30 baseline: `139006.2%` higher estimated one-second reach.
This run reaches `~3741.50%` of the repo's zero-indexed billion-scale milestone at the estimated one-second crossing.

## Estimated One-Second Reach

| Group | Algorithm | Estimated n at 1s | Last measured under 1s | Next measured over 1s |
|---|---|---:|---:|---:|
| My C++ variants | Lehmer + Axler + phi7 | `37,415,030,844` | `32,000,000,000` at `0.865979s` | `40,000,000,000` at `1.063420s` |
| My C++ variants | Lehmer + pi table + Axler | `34,308,358,230` | `32,000,000,000` at `0.934285s` | `40,000,000,000` at `1.161590s` |
| My C++ variants | Lehmer + pi table FSM | `32,471,825,139` | `32,000,000,000` at `0.985613s` | `64,000,000,000` at `1.957700s` |
| My C++ variants | Lagrange + FSM | `2,145,258,257` | `2,000,000,000` at `0.934983s` | `4,000,000,000` at `1.817370s` |
| My C++ variants | Wheel-30 FSM bitset | `104,553,081` | `100,000,000` at `0.952201s` | `160,000,000` at `1.596870s` |
| My C++ variants | Wheel-30 bitset | `66,110,091` | `40,000,000` at `0.580449s` | `80,000,000` at `1.229320s` |
| My C++ variants | Wheel-30 stateful bitset | `62,453,648` | `40,000,000` at `0.613063s` | `80,000,000` at `1.312470s` |
| My C++ variants | Odd-only segmented | `45,192,387` | `40,000,000` at `0.878655s` | `80,000,000` at `1.831840s` |
| My C++ variants | Wheel-30 indexed | `43,474,714` | `40,000,000` at `0.916014s` | `80,000,000` at `1.900720s` |
| Video-inspired baseline | Wheel-30 segmented | `26,896,738` | `20,000,000` at `0.734395s` | `40,000,000` at `1.512150s` |
| My C++ variants | Odd-only Eratosthenes | `22,312,996` | `20,000,000` at `0.867854s` | `40,000,000` at `2.129660s` |
| Video-inspired baseline | Segmented sieve | `21,178,157` | `20,000,000` at `0.941471s` | `40,000,000` at `1.954350s` |
| Video-inspired baseline | Sieve of Eratosthenes | `12,625,926` | `10,000,000` at `0.736293s` | `20,000,000` at `1.829260s` |
| Video-inspired baseline | Miller-Rabin iteration | `667,458` | `524,288` at `0.762552s` | `1,048,576` at `1.660610s` |
| Video-inspired baseline | Sqrt iteration | `378,405` | `262,144` at `0.559639s` | `524,288` at `1.674700s` |
| Video-inspired baseline | Naive iteration | `12,272` | `8,192` at `0.426656s` | `16,384` at `1.838520s` |

## Largest Sampled Rows

| Group | Algorithm | Largest sampled n | prime(n) | Seconds |
|---|---|---:|---:|---:|
| Video-inspired baseline | Naive iteration | `16,384` | `180,511` | `1.838520` |
| Video-inspired baseline | Sqrt iteration | `524,288` | `7,754,081` | `1.674700` |
| Video-inspired baseline | Miller-Rabin iteration | `1,048,576` | `16,290,073` | `1.660610` |
| Video-inspired baseline | Sieve of Eratosthenes | `20,000,000` | `373,587,911` | `1.829260` |
| My C++ variants | Odd-only Eratosthenes | `40,000,000` | `776,531,419` | `2.129660` |
| Video-inspired baseline | Segmented sieve | `40,000,000` | `776,531,419` | `1.954350` |
| My C++ variants | Odd-only segmented | `80,000,000` | `1,611,623,887` | `1.831840` |
| Video-inspired baseline | Wheel-30 segmented | `40,000,000` | `776,531,419` | `1.512150` |
| My C++ variants | Wheel-30 indexed | `80,000,000` | `1,611,623,887` | `1.900720` |
| My C++ variants | Wheel-30 bitset | `80,000,000` | `1,611,623,887` | `1.229320` |
| My C++ variants | Wheel-30 stateful bitset | `80,000,000` | `1,611,623,887` | `1.312470` |
| My C++ variants | Wheel-30 FSM bitset | `160,000,000` | `3,340,200,043` | `1.596870` |
| My C++ variants | Lagrange + FSM | `4,000,000,000` | `97,011,687,221` | `1.817370` |
| My C++ variants | Lehmer + pi table FSM | `64,000,000,000` | `1,737,172,372,387` | `1.957700` |
| My C++ variants | Lehmer + pi table + Axler | `40,000,000,000` | `1,066,173,339,607` | `1.161590` |
| My C++ variants | Lehmer + Axler + phi7 | `40,000,000,000` | `1,066,173,339,607` | `1.063420` |
