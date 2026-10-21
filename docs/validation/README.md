# Validation records

Each record names the suite, the detector or skill version it measured, and the command that produces it. Prepare the browser driver once before any benchmark command: `(cd skills/remorsearch-ux-qa/drivers/web && npm ci && npx playwright install chromium)`, plus `npx playwright install-deps chromium` on Linux. A benchmark whose recordings fail exits with an error instead of reporting a score. Benchmark answer keys live in `benchmarks/`; they are read only by the scorer.

## Rendered-layout detector

| Record | What it measures | Reproduce |
| --- | --- | --- |
| [`visual-layout-20261018.md`](visual-layout-20261018.md) | Measured scan checks (LY-01 to LY-05 with contrast, target size and reflow) on 28 seeded rendered defects, 11 decoys and four clean twins written blind to the detector, and the earlier suites before and after | `python3 skills/remorsearch-ux-qa/scripts/ergo_bench.py --suite benchmarks/visual-layout --out .ergo-bench/visual-layout` |
| [`agent-comparison-20261018/`](agent-comparison-20261018/README.md) | The same agent with and without the skill on the same pages, tools and budget: defects found, false alarms and time | Prompts, raw findings and the scoring rule are in the folder |
| [`real-layout-bugs/`](real-layout-bugs/README.md) | Agent QA with and without the frozen 1.0.0 skill on 12 layout bugs fixed in open-source projects: two models, three paired runs each, preregistered and scored blind to arm, plus the scan on its own | Protocol, sealed answer key, prompts, raw findings, verdicts and scores are in the folder |
| [`real-layout-bugs-2/`](real-layout-bugs-2/README.md) | Round 2 on 4 new bugs from other projects, with the scan fixed for `file://` stylesheets and `--single-process`: the same two models and design, and the scan on its own with 1.0.0 and the fixed skill | Protocol, screening of 257 candidates, sealed answer key, prompts, raw findings, verdicts and scores are in the folder |
| [`real-layout-bugs-3/`](real-layout-bugs-3/README.md), [`-4/`](real-layout-bugs-4/README.md), [`-5/`](real-layout-bugs-5/README.md), [`-6/`](real-layout-bugs-6/README.md) | Rounds 3 to 6 on 4, 8, 10 and 8 new bugs, each from projects no earlier round used and each with the skill frozen at the commit that added the checks under test, plus the scan on its own (rounds 4 to 6 also with the skill frozen for the round before); round 6 ran GPT-6.1 Sol only and also records a development rerun after its fixes | Protocol, screening record, sealed answer key, prompts, raw findings, verdicts, scores and times are in each folder |

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
