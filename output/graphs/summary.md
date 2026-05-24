# Benchmark Summary

Video target: [One second to find the BILLIONth PRIME](https://www.youtube.com/watch?v=uJkoI5TnKzA) targets `n = 1,000,000,000`.

All comparisons below are same-run. Exact prime-index values are hardware-relative; the meaningful claim is relative lift between algorithms measured together.

Local best: `Lehmer + pi table + Axler` reaches an estimated `n = 32,747,821,786` at one second.
Measured under-one-second anchor: `n = 32,000,000,000` at `0.978487s`.
Interpolation bracket: log-log interpolation between `n = 32,000,000,000` at `0.978487s` and `n = 40,000,000,000` at `1.207230s`.
Index note: benchmark rows use zero-indexed `n`; interpolation is performed on `n + 1` and converted back to zero-indexed `n`.
Best vs. pre-bitset wheel-30 baseline: `124126.3%` higher estimated one-second reach.
This run reaches `~3274.78%` of the video's one-billion headline target at the estimated one-second crossing.

## Estimated One-Second Reach

| Group | Algorithm | Estimated n at 1s | Last measured under 1s | Next measured over 1s |
|---|---|---:|---:|---:|
| My C++ variants | Lehmer + pi table + Axler | `32,747,821,786` | `32,000,000,000` at `0.978487s` | `40,000,000,000` at `1.207230s` |
| My C++ variants | Lehmer + pi table FSM | `31,167,475,494` | `16,000,000,000` at `0.518202s` | `32,000,000,000` at `1.026330s` |
| My C++ variants | Lagrange + FSM | `2,142,928,499` | `2,000,000,000` at `0.931976s` | `4,000,000,000` at `1.890760s` |
| My C++ variants | Wheel-30 FSM bitset | `106,500,234` | `100,000,000` at `0.932400s` | `160,000,000` at `1.572040s` |
| My C++ variants | Wheel-30 bitset | `63,653,762` | `40,000,000` at `0.604198s` | `80,000,000` at `1.281320s` |
| My C++ variants | Wheel-30 stateful bitset | `60,682,342` | `40,000,000` at `0.641609s` | `80,000,000` at `1.342160s` |
| My C++ variants | Odd-only segmented | `44,394,230` | `40,000,000` at `0.895076s` | `80,000,000` at `1.870680s` |
| My C++ variants | Wheel-30 indexed | `42,760,014` | `40,000,000` at `0.930322s` | `80,000,000` at `1.970060s` |
| Video-inspired baseline | Wheel-30 segmented | `26,361,427` | `20,000,000` at `0.744569s` | `40,000,000` at `1.561010s` |
| Video-inspired baseline | Segmented sieve | `20,623,802` | `20,000,000` at `0.968101s` | `40,000,000` at `2.012170s` |
| My C++ variants | Odd-only Eratosthenes | `20,261,103` | `20,000,000` at `0.984129s` | `40,000,000` at `2.313920s` |
| Video-inspired baseline | Sieve of Eratosthenes | `11,522,094` | `10,000,000` at `0.840223s` | `20,000,000` at `1.969150s` |
| Video-inspired baseline | Miller-Rabin iteration | `661,387` | `524,288` at `0.769308s` | `1,048,576` at `1.682530s` |
| Video-inspired baseline | Sqrt iteration | `382,063` | `262,144` at `0.566096s` | `524,288` at `1.612860s` |
| Video-inspired baseline | Naive iteration | `12,190` | `8,192` at `0.435116s` | `16,384` at `1.857430s` |

## Largest Sampled Rows

| Group | Algorithm | Largest sampled n | prime(n) | Seconds |
|---|---|---:|---:|---:|
| Video-inspired baseline | Naive iteration | `16,384` | `180,511` | `1.857430` |
| Video-inspired baseline | Sqrt iteration | `524,288` | `7,754,081` | `1.612860` |
| Video-inspired baseline | Miller-Rabin iteration | `1,048,576` | `16,290,073` | `1.682530` |
| Video-inspired baseline | Sieve of Eratosthenes | `20,000,000` | `373,587,911` | `1.969150` |
| My C++ variants | Odd-only Eratosthenes | `40,000,000` | `776,531,419` | `2.313920` |
| Video-inspired baseline | Segmented sieve | `40,000,000` | `776,531,419` | `2.012170` |
| My C++ variants | Odd-only segmented | `80,000,000` | `1,611,623,887` | `1.870680` |
| Video-inspired baseline | Wheel-30 segmented | `40,000,000` | `776,531,419` | `1.561010` |
| My C++ variants | Wheel-30 indexed | `80,000,000` | `1,611,623,887` | `1.970060` |
| My C++ variants | Wheel-30 bitset | `80,000,000` | `1,611,623,887` | `1.281320` |
| My C++ variants | Wheel-30 stateful bitset | `80,000,000` | `1,611,623,887` | `1.342160` |
| My C++ variants | Wheel-30 FSM bitset | `160,000,000` | `3,340,200,043` | `1.572040` |
| My C++ variants | Lagrange + FSM | `4,000,000,000` | `97,011,687,221` | `1.890760` |
| My C++ variants | Lehmer + pi table FSM | `32,000,000,000` | `845,505,378,527` | `1.026330` |
| My C++ variants | Lehmer + pi table + Axler | `40,000,000,000` | `1,066,173,339,607` | `1.207230` |
