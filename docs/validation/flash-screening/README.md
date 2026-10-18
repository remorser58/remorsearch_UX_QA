# GM-04 flash screening: live check

Twelve small pages, each recorded three times in real Chromium (Galaxy S24
emulation, `--flash-sample-ms 1500`) and evaluated by GM-04 for the default
profile (300 mm viewing distance). First run at commit `697ce28`; the table below is the re-run after the screen-capture fixes.

    python3 docs/validation/flash-screening/validate.py --repeat 3

| Page | What it shows | Expected |
| --- | --- | --- |
| `box.html` | 190 × 120 CSS px box, white/black at 5 Hz (~0.0085 sr) | fail |
| `box-small.html` | the same flash on a smaller box (~0.0035 sr) | pass |
| `halves.html` | two halves swapping black/white at 5 Hz; the mean luminance stays constant | fail |
| `red.html` | full screen `#ff0000` ↔ `#7f7f7f` at 5 Hz (almost equal luminance) | fail (red flash) |
| `wait-flash.html` | a full-screen flash that starts while the script waits | fail |
| `flicker30.html` | 30 Hz full-screen flicker (aliases to a still image without capture jitter) | fail |
| `scroll-text.html` | high-contrast text scrolling | pass |
| `feed-scroll.html` | the user scrolls a feed | pass |
| `feed-scroll-inner.html` | the same feed in an app-shell scroll box (the page itself does not scroll) | pass |
| `static.html` | static page | pass |
| `slow.html` | full-screen change at 1 Hz | pass |
| `scroll-shake.html` | a script shakes the page scroll back and forth (a reversal every 100 ms) over black and white bands | fail |

Before the rework, `box`, `halves`, `red` and `wait-flash` passed (whole-viewport
mean luminance, no red test, no sampling during waits).

## Result: 36 of 36 as expected

Re-run after two driver fixes (September 2026). CDP screenshot clips are in document
coordinates: frames were clipped at 0,0, so once a page scrolled they showed the top of
the document (mostly unpainted) instead of the screen. The earlier `feed-scroll`
passes (30 of 30 table, commit `697ce28`) were therefore measured on nearly blank
frames. With frames of the real screen, a feed of equal cards scrolled at about half a
card per frame made the motion estimate ambiguous, and on a tablet 3 of 8 stress runs
failed GM-04 on plain scrolling. The driver now uses the page's measured scroll between
frames as the motion, and captures whole frames (no downscaling clip, which also
stopped scroll gestures on inner scroll boxes) during gesture steps. Stress runs after
the fix (4 per variant, long and short strokes): tablet window scroll 8/8 pass, tablet
and phone app-shell scroll 16/16 pass, no flash candidate area.

Re-run after the oscillation guard (September 2026): page scroll counts as motion
only while it keeps one direction (ITC/Ofcom and ISO 9241-391 exempt smooth motion
in one direction only). Scroll that reverses more than 3 times within 1 s is not
motion-matched. On `scroll-shake.html` the guard gives 5.0 flashes/s (fail) on
every run; without it the same page read 3.5 and 2.0 flashes/s in two runs (fail,
then pass). The scroll controls (`scroll-text`, `feed-scroll`, `feed-scroll-inner`)
set no oscillation flag.

| scenario | rep | driver exit | expected | verdict | kind | flashes/s | area sr | mean fps | max gap ms | sampled ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SC-flash-a-box | 0 | 0 | fail | fail | general | 5.0 | 0.00836 | 26.5 | 58.4 | 3472.4 |
| SC-flash-a-box | 1 | 0 | fail | fail | general | 5.0 | 0.00836 | 26.5 | 50.9 | 3466.9 |
| SC-flash-a-box | 2 | 0 | fail | fail | general | 5.0 | 0.00836 | 26.5 | 51.7 | 3506.4 |
| SC-flash-a2-box-small | 0 | 0 | pass | pass | general | 5.0 | 0.00352 | 24.8 | 55.2 | 3470.1 |
| SC-flash-a2-box-small | 1 | 0 | pass | pass | general | 5.5 | 0.00352 | 25.4 | 50.8 | 3430.7 |
| SC-flash-a2-box-small | 2 | 0 | pass | pass | general | 5.0 | 0.00352 | 26.0 | 68.2 | 3467.7 |
| SC-flash-b-halves | 0 | 0 | fail | fail | general | 5.5 | 0.02457 | 25.9 | 51.0 | 3437.5 |
| SC-flash-b-halves | 1 | 0 | fail | fail | general | 5.5 | 0.02457 | 25.5 | 51.9 | 3488.2 |
| SC-flash-b-halves | 2 | 0 | fail | fail | general | 5.0 | 0.02457 | 25.4 | 55.6 | 3465.1 |
| SC-flash-c-red | 0 | 0 | fail | fail | red | 5.0 | 0.02457 | 27.5 | 51.8 | 3491.3 |
| SC-flash-c-red | 1 | 0 | fail | fail | red | 5.5 | 0.02457 | 25.7 | 53.6 | 3463.7 |
| SC-flash-c-red | 2 | 0 | fail | fail | red | 5.5 | 0.02457 | 26.2 | 52.7 | 3467.8 |
| SC-flash-d-wait | 0 | 0 | fail | fail | general | 5.0 | 0.02457 | 26.6 | 56.1 | 6454.5 |
| SC-flash-d-wait | 1 | 0 | fail | fail | general | 5.0 | 0.02457 | 25.6 | 58.6 | 6476.0 |
| SC-flash-d-wait | 2 | 0 | fail | fail | general | 5.0 | 0.02457 | 25.9 | 51.4 | 6474.3 |
| SC-flash-e-flicker30 | 0 | 0 | fail | fail | general | 6.0 | 0.02457 | 26.1 | 62.8 | 3452.8 |
| SC-flash-e-flicker30 | 1 | 0 | fail | fail | general | 5.0 | 0.02457 | 25.8 | 66.4 | 3455.7 |
| SC-flash-e-flicker30 | 2 | 0 | fail | fail | general | 7.0 | 0.02457 | 25.2 | 59.5 | 3453.5 |
| SC-flash-f-scroll-text | 0 | 0 | pass | pass |  | 1.0 | 0.0 | 25.6 | 68.6 | 4415.1 |
| SC-flash-f-scroll-text | 1 | 0 | pass | pass |  | 1.0 | 0.0 | 25.4 | 65.7 | 4417.6 |
| SC-flash-f-scroll-text | 2 | 0 | pass | pass |  | 1.0 | 0.0 | 24.8 | 67.4 | 4434.5 |
| SC-flash-g-static | 0 | 0 | pass | pass |  | 0.0 | 0.0 | 26.3 | 52.9 | 5394.0 |
| SC-flash-g-static | 1 | 0 | pass | pass |  | 0.0 | 0.0 | 25.6 | 58.3 | 5432.0 |
| SC-flash-g-static | 2 | 0 | pass | pass |  | 0.0 | 0.0 | 27.1 | 51.7 | 5427.5 |
| SC-flash-h-feed-scroll | 0 | 0 | pass | pass |  | 2.0 | 0.0 | 23.2 | 78.8 | 5915.7 |
| SC-flash-h-feed-scroll | 1 | 0 | pass | pass |  | 2.0 | 0.0 | 23.2 | 58.8 | 5867.7 |
| SC-flash-h-feed-scroll | 2 | 0 | pass | pass |  | 2.0 | 0.0 | 23.2 | 60.0 | 5951.5 |
| SC-flash-i-slow | 0 | 0 | pass | pass |  | 1.5 | 0.0 | 25.3 | 52.5 | 4433.1 |
| SC-flash-i-slow | 1 | 0 | pass | pass |  | 1.5 | 0.0 | 25.4 | 51.4 | 4447.7 |
| SC-flash-i-slow | 2 | 0 | pass | pass |  | 1.5 | 0.0 | 25.3 | 52.2 | 4460.1 |
| SC-flash-j-feed-scroll-inner | 0 | 0 | pass | pass |  | 2.0 | 0.0 | 23.0 | 62.6 | 5910.5 |
| SC-flash-j-feed-scroll-inner | 1 | 0 | pass | pass |  | 2.0 | 0.0 | 22.6 | 56.9 | 5941.9 |
| SC-flash-j-feed-scroll-inner | 2 | 0 | pass | pass |  | 1.5 | 0.0 | 23.2 | 58.0 | 5910.7 |
| SC-flash-k-scroll-shake | 0 | 0 | fail | fail | general | 5.0 | 0.02282 | 26.1 | 59.5 | 6435.1 |
| SC-flash-k-scroll-shake | 1 | 0 | fail | fail | general | 5.0 | 0.02273 | 26.7 | 68.6 | 6479.7 |
| SC-flash-k-scroll-shake | 2 | 0 | fail | fail | general | 5.0 | 0.02284 | 26.5 | 51.9 | 6454.1 |

`flashes/s` for `flicker30` is the aliased rate (4-5/s), not the true 30 Hz: the
sampler (~25 fps with 0-15 ms jitter) sees that the region flashes, not how
fast. The verdict does not depend on the exact rate above 3/s.

Limits: frames are downscaled to ~160 CSS px wide, so patterns finer than a
block (22 × 40 CSS px on phones) average out; spatial-pattern rules (IRIS
pattern check) are not screened. This is screening, not certification. EA IRIS
is not a certification either: its defaults need 25 % of the frame to change, so
a local flash that fails here can pass IRIS, and that pass does not clear it.
For broadcast or certification, use a certified process such as Harding FPA.
