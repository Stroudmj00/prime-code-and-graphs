# Image-Generated Scorecard Prompt

This file records the reviewed stats and prompt used for `story_scorecard.png`. The image is a recruiter-facing README asset, not a Matplotlib output from `scripts/plot.py`.

## Reviewed Stats

- External challenge context: one-second billion-prime challenge.
- Zero-indexed proof point: `n = 1,000,000,000` in `0.050801s`.
- `prime(1,000,000,000) = 22,801,763,513`.
- Pre-bitset wheel-30 segmented baseline one-second reach: `26,896,738`.
- Previous checked-in best, `sieve-lagrange-lehmer-axler-fsm`: `34,308,358,230`.
- Current best, `sieve-lagrange-lehmer-axler-phi7-fsm`: `37,415,030,844`.
- Same-run improvement over previous checked-in best: `9.1%`.
- Same-run improvement over pre-bitset wheel-30 baseline: `139006.2%`.
- Current best versus billion-index milestone: `3741.50%`.

## Prompt

```text
Use case: infographic-diagram
Asset type: GitHub README lead scorecard image, 16:9 landscape
Primary request: Create a polished technical benchmark scorecard from the stats below. Do not imitate a Python/Matplotlib chart. Make it look like a clean product dashboard or investor-slide data card for a recruiter-facing GitHub project.

Exact story to communicate: This is a portable C++ one-second nth-prime benchmark inspired by a YouTube challenge. The project uses exact prime-count fast-forwarding plus final segmented sieving; it does not use stored final nth-prime answers. Absolute prime-index values are hardware-relative, so same-run percentage lift matters most.

Required exact visible text and numbers:
Title: "Portable C++ prime benchmark"
Subtitle: "Same-run comparison; exact n is hardware-relative"
Section labels: "Video context + baseline" and "My C++ result"
Metric card 1: "Challenge context" / "1B in 1s"
Metric card 2: "Base local" / "26.9M" / "wheel-30 segmented"
Metric card 3: "Best estimate" / "37.42B" / "+139006.2% vs base"
Metric card 4: "Proof point" / "1.00B in 0.051s" / "prime(1B) = 22,801,763,513"
Small comparison callout: "Previous best: 34.31B -> phi7: 37.42B (+9.1%)"
Ranked ladder rows with these exact labels and numbers: "Deeper phi table 37,415,030,844", "Axler bound 34,308,358,230", "Lehmer + pi table 32,471,825,139", "Legendre skip 2,145,258,257", "FSM marking 104,553,081", "Bitset packing 66,110,091", "Wheel baseline 26,896,738"
Progress text: "Best estimate is 3741.50% of the billion-index milestone"
Footer: "Exact final prime is still found by sieving/counting, not by a stored nth-prime lookup."

Visual direction: premium light theme, lots of whitespace, navy text, red milestone accent, blue baseline accent, green improvement accent. Use clear horizontal bars or structured rows for the ranked ladder. Keep all text sharp, correctly spelled, and legible at GitHub README width. Avoid fake logos, random decorative numbers, watermarks, gradients-as-background, clutter, and dense tiny text.
```
