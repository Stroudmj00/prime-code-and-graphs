# Benchmark Summary

Video target: [One second to find the BILLIONth PRIME](https://www.youtube.com/watch?v=uJkoI5TnKzA) targets `n = 1,000,000,000`.

All comparisons below are same-run. Exact prime-index values are hardware-relative; the meaningful claim is relative lift between algorithms measured together.

Local best: `Lehmer + FSM` reaches an estimated `n = 12,230,629,361` at one second.
Measured under-one-second anchor: `n = 8,000,000,000` at `0.690345s`.
Best vs. pre-bitset wheel-30 baseline: `45186.4%` higher estimated one-second reach.
This run reaches `~1223.06%` of the video's one-billion headline target at the estimated one-second crossing.

## Estimated One-Second Reach

| Group | Algorithm | Estimated n at 1s | Last measured under 1s | Next measured over 1s |
|---|---|---:|---:|---:|
| Additional variants | Lehmer + FSM | `12,230,629,361` | `8,000,000,000` at `0.690345s` | `16,000,000,000` at `1.264290s` |
| Additional variants | Lagrange + FSM | `2,392,780,010` | `2,000,000,000` at `0.835971s` | `4,000,000,000` at `1.670990s` |
| Additional variants | Wheel-30 FSM bitset | `111,216,296` | `100,000,000` at `0.892365s` | `160,000,000` at `1.476400s` |
| Additional variants | Wheel-30 bitset | `65,172,037` | `40,000,000` at `0.587388s` | `80,000,000` at `1.250370s` |
| Additional variants | Wheel-30 stateful bitset | `60,958,145` | `40,000,000` at `0.624239s` | `80,000,000` at `1.355330s` |
| Additional variants | Odd-only segmented | `46,238,695` | `40,000,000` at `0.857164s` | `80,000,000` at `1.791340s` |
| Additional variants | Wheel-30 indexed | `43,395,560` | `40,000,000` at `0.915199s` | `80,000,000` at `1.944960s` |
| Video-inspired baseline | Wheel-30 segmented | `27,007,283` | `20,000,000` at `0.718461s` | `40,000,000` at `1.540880s` |
| Video-inspired baseline | Segmented sieve | `20,617,273` | `20,000,000` at `0.967728s` | `40,000,000` at `2.044670s` |
| Additional variants | Odd-only Eratosthenes | `19,315,957` | `10,000,000` at `0.424307s` | `20,000,000` at `1.046360s` |
| Video-inspired baseline | Sieve of Eratosthenes | `11,567,111` | `10,000,000` at `0.842744s` | `20,000,000` at `1.903170s` |
| Video-inspired baseline | Miller-Rabin iteration | `672,052` | `524,288` at `0.754920s` | `1,048,576` at `1.654840s` |
| Video-inspired baseline | Sqrt iteration | `385,823` | `262,144` at `0.557168s` | `524,288` at `1.590570s` |
| Video-inspired baseline | Naive iteration | `12,207` | `8,192` at `0.436517s` | `16,384` at `1.843650s` |

## Largest Sampled Rows

| Group | Algorithm | Largest sampled n | prime(n) | Seconds |
|---|---|---:|---:|---:|
| Video-inspired baseline | Naive iteration | `16,384` | `180,511` | `1.843650` |
| Video-inspired baseline | Sqrt iteration | `524,288` | `7,754,081` | `1.590570` |
| Video-inspired baseline | Miller-Rabin iteration | `1,048,576` | `16,290,073` | `1.654840` |
| Video-inspired baseline | Sieve of Eratosthenes | `20,000,000` | `373,587,911` | `1.903170` |
| Additional variants | Odd-only Eratosthenes | `20,000,000` | `373,587,911` | `1.046360` |
| Video-inspired baseline | Segmented sieve | `40,000,000` | `776,531,419` | `2.044670` |
| Additional variants | Odd-only segmented | `80,000,000` | `1,611,623,887` | `1.791340` |
| Video-inspired baseline | Wheel-30 segmented | `40,000,000` | `776,531,419` | `1.540880` |
| Additional variants | Wheel-30 indexed | `80,000,000` | `1,611,623,887` | `1.944960` |
| Additional variants | Wheel-30 bitset | `80,000,000` | `1,611,623,887` | `1.250370` |
| Additional variants | Wheel-30 stateful bitset | `80,000,000` | `1,611,623,887` | `1.355330` |
| Additional variants | Wheel-30 FSM bitset | `160,000,000` | `3,340,200,043` | `1.476400` |
| Additional variants | Lagrange + FSM | `4,000,000,000` | `97,011,687,221` | `1.670990` |
| Additional variants | Lehmer + FSM | `16,000,000,000` | `411,199,041,131` | `1.264290` |
