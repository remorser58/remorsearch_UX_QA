# Validation records

Each record names the suite, the detector or skill version it measured, and the command that produces it. Prepare the browser driver once before any benchmark command: `(cd skills/remorsearch-ux-qa/drivers/web && npm ci && npx playwright install chromium)`, plus `npx playwright install-deps chromium` on Linux. A benchmark whose recordings fail exits with an error instead of reporting a score. Benchmark answer keys live in `benchmarks/`; they are read only by the scorer.

## Rendered-layout detector

| Record | What it measures | Reproduce |
| --- | --- | --- |
| [`visual-layout-20261018.md`](visual-layout-20261018.md) | Measured scan checks (LY-01 to LY-05 with contrast, target size and reflow) on 28 seeded rendered defects, 11 decoys and four clean twins written blind to the detector, and the earlier suites before and after | `python3 skills/remorsearch-ux-qa/scripts/ergo_bench.py --suite benchmarks/visual-layout --out .ergo-bench/visual-layout` |
| [`agent-comparison-20261018/`](agent-comparison-20261018/README.md) | The same agent with and without the skill on the same pages, tools and budget: defects found, false alarms and time | Prompts, raw findings and the scoring rule are in the folder |

## Ergonomics engine

| Record | What it measures |
| --- | --- |
| [`mobile-commerce-v1.json`](mobile-commerce-v1.json), [`mobile-commerce-v2.json`](mobile-commerce-v2.json), [`game-desktop-v1.json`](game-desktop-v1.json) to [`game-desktop-v3.json`](game-desktop-v3.json) | Development-suite scores across detector versions |
| [`heldout-mixed-frozen-8c1de02.json`](heldout-mixed-frozen-8c1de02.json) | Held-out mixed suite, scored once at a frozen detector |
| [`heldout-2-aggregate-0a4fd68.json`](heldout-2-aggregate-0a4fd68.json), [`experiments/heldout-2-preregistration.md`](experiments/heldout-2-preregistration.md), [`experiments/heldout-2-results.md`](experiments/heldout-2-results.md) | Pre-registered held-out evaluation; its pages were kept outside the repository, so only the aggregate is published |
| [`experiments/decisions.md`](experiments/decisions.md), `experiments/ablation-dev-*.json` | Check-by-check decisions and ablations on the development suites |
| [`adjudication-round1.json`](adjudication-round1.json) | Independent adjudication of sampled findings |
| [`flash-screening/`](flash-screening/) | Flash (photosensitivity) screening validation |
| [`subagent-model-benchmark.md`](subagent-model-benchmark.md) | Which subagent model tier gives adequate persona-QA results |

Scores from development suites are fits, since the detector was tuned on them. Held-out numbers are the ones to quote, with their sample sizes.
