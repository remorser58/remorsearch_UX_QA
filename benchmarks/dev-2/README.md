# dev-2 (development suite: semantics, layout and task flow)

Three Korean products written by benchmark authors to develop the semantics,
layout and task-flow checks (SM-*, LY-01, RF-01, FM-02) before the heldout-2
freeze. It is a **development** suite: the tool author reads its keys and tunes on
it, so its scores are training fits.

| Product | Surface | Devices | Defects | Decoys |
| --- | --- | --- | --- | --- |
| civil | civil-service application (주민등록표 등본 우편 발급) | galaxy-s24, galaxy-s24-ultra | 12 | 4 |
| delivery | food delivery order | galaxy-s24-ultra, iphone-15 | 12 | 4 |
| lms | online course with a timed quiz | laptop-1440, galaxy-tab-s9 | 12 | 4 |

Layout: `products/<slug>/brief.md` (product brief), `site/<slug>/` (two page
variants of one flow; `keys/<slug>.json` names the defect variant),
`scenarios/SC-d2-<slug>-{a,b}.json` (identical steps), `keys/<slug>.json`
(defects, decoys, clean control; spec 12.1). Authored in four stages (plan, build,
scenarios, independent verification); Opus planned and verified, and the
civil and lms scenario stage ran on Sonnet.

Run: `python3 skills/remorsearch-ux-qa/scripts/ergo_eval.py record|analyse|score --suite benchmarks/dev-2 --out .ergo-bench/d2`.
