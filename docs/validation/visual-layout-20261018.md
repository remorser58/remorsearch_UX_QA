# Visual-layout benchmark, 2026-10-18

The rendered-layout checks were measured on `benchmarks/visual-layout`, a suite of four Korean product pages with 28 seeded defects in nine families, 11 decoys and a clean twin of every page. A separate agent wrote the suite from the benchmark spec and one example suite without reading the detector, driver or analyser code. Its README records the authoring model, date and how every number in the key was measured.

## Results

Strict scoring (`bench.score` with exact page-level matching): a finding counts when its scenario, category and element (or the element's container) match a seeded defect.

| Detector | Measured checks only | With one default profile | Decoys flagged, measured / profile | Findings on clean twins, measured / profile |
| --- | ---: | ---: | ---: | ---: |
| Before the layout checks | 3 / 28 | 6 / 28 | 3 / 4 | 6 / 18 |
| First blind score | 19 / 28 | 22 / 28 | 3 / 4 | 6 / 18 |
| After fixes made on seeing the misses | 25 / 28 | 28 / 28 | 3 / 4 | 6 / 18 |

The suite has 11 decoys and four clean twins. The decoy and clean-twin counts did not change: the new checks added no finding on a decoy or a clean page. The first blind score is the held-out number. The last row is a development fit; four fixes followed the misses (an `overflow-x: hidden` wrapper read as a scroll container, a cell whose text had already run past the edge, a ribbon over one word, a list too long for one screen). Changes made after the second review (floating fixed elements, row alignment by the container's alignment, squeezed gaps only) left every score unchanged, and so did the release fixes (scaled boxes compared at their drawn size, text that paints nothing skipped, a control's words measured wherever they are drawn and reported through the control). Repeated runs of the release candidates matched defect by defect. Every number on this page is in [`visual-layout-20261018.json`](visual-layout-20261018.json).

By family at the final score, measured checks find all of cut text (own box, clipping ancestor, past the screen edge), text under fixed bars, badge and margin overlap, overlapping heading lines, near-miss alignment and uneven list spacing. Text below 11 px is found only by the profile-based reading-size check (PC-04), since whether small print matters (a coupon condition versus a legal footer) needs judgment.

## No regression on the earlier suites

Same command, same scorer, before and after (dev-2 through `ergo_eval.py`; four of its twelve recordings end in a failed task step, before and after alike):

| Suite | Recall, measured / profile swarm | Findings on clean controls, measured / swarm |
| --- | --- | --- |
| mobile-commerce | 0.353 / 0.824, unchanged | 7 / 23, unchanged |
| game-desktop | 0.375 / 0.938, unchanged | 19 / 28, unchanged |
| heldout-mixed | 0.150 / 0.900, unchanged | 31 / 50, unchanged |
| dev-2 (development suite, keys read while tuning) | 0.250 → 0.278 / 0.472 → 0.500 | 32 / 99, unchanged |

## On Linux

The same tree, copied without its git history to Ubuntu 24.04 (arm64) in a virtual machine and installed with `scripts/install.py` after `npx -y playwright@1.56.1 install-deps chromium`, reported the same analyser and driver hashes and the same recall: 25 / 28 with measured checks only, 28 / 28 with one default profile and with the swarm, missing the same three small-text defects. It flagged 2 / 3 decoys (macOS 3 / 4) and reported 10 / 22 findings on the clean twins (macOS 6 / 18); the difference is reflow notes (RF-02) on five installment-table cells of the clean checkout page, where macOS noted one sheet subtitle instead. Korean text rendered in WenQuanYi Zen Hei, which `install-deps` adds. Fonts move these measurements: in another Linux environment a seeded two-line heading fitted on one line, which removes its seeded overlap, so install the fonts that `install-deps` adds.

## Reproduce

```sh
(cd skills/remorsearch-ux-qa/drivers/web && npm ci && npx playwright install chromium)
python3 skills/remorsearch-ux-qa/scripts/ergo_bench.py --suite benchmarks/visual-layout --out .ergo-bench/visual-layout
```

The command serves `benchmarks/` on 127.0.0.1, records every scenario in Chromium with the pinned Playwright 1.56.1 driver, analyses it and scores it. `summary.json` holds the three configurations; `score-measured_only.json` lists each defect. If any recording fails (no run file, no snapshot, a blocked run or a driver error), including a run reused with `--reuse-runs`, the command exits with an error and its scores are void. `summary.json` also records `code_sha256` (analyser and scorer), `driver_sha256` (browser driver and its pinned lockfile) and `recordings_driver_sha256` (the driver that made each scored recording): `final_provenance` and `final_linux_provenance` in the JSON give the values behind the release numbers, so matching hashes mean the same code. Expect small differences on another machine: the suite was measured with macOS system fonts, and the smallest seeded cut and overlap (16.8 px and 9.6 px) leave room for font metrics.

## Limits

One suite of four products written by one agent, with families chosen in advance. It shows that the checks find these defect kinds on unseen pages; it says nothing about how often such defects occur or how many other defect kinds exist. Chromium only, on macOS and one Linux virtual machine.
