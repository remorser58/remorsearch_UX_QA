# Subagent model benchmark

This page records the experiment behind the subagent recommendation in
[`references/agent-setup.md`](../../skills/remorsearch-ux-qa/references/agent-setup.md).
Per-run data, with both judges' scores and comments, is in
[`subagent-model-benchmark.json`](subagent-model-benchmark.json).

## Question

From which model tier and reasoning effort does a persona-QA subagent give
adequate results? Adequate means three things:

1. it reaches the task goal on a real page;
2. it finds the seeded UX defects;
3. it raises no false alarms on a page where those defects were fixed.

## Setup

- **Screens.** 11 scenarios from the repository's benchmark suites
  (`benchmarks/mobile-commerce`, `benchmarks/heldout-mixed`,
  `benchmarks/game-desktop`) at commit `c607282`:
  - 8 screens with seeded defects, 40 defects in all;
  - 3 clean controls, the fixed versions of three of those screens.
  - 7 screens are phones or a tablet (touch) and 4 are desktop or laptop (mouse).
    All screens and task goals are in Korean.
- **Arms.** Six model and effort settings, one run per screen: 66 runs.
  - Haiku 4.5 (default effort)
  - Sonnet 5.5 at high and at max effort
  - Opus 5.5 at high and at max effort
  - Fable 5.1 at high effort
- **Operator task.** Every arm got the same prompt.
  - It started the live web driver (`drivers/web/ergo_drive.mjs serve`) and acted
    one step at a time through the driver's HTTP API.
  - It looked only at the screenshots. Reading page HTML, scenario files or
    snapshot JSON was forbidden.
  - The persona was a first-time user with no body or sense profile.
  - A run stopped at the goal, after 20 actions, or after 3 grounding failures in a
    row.
  - It then reported findings with severity (P0–P3), basis (observed or
    judgment), evidence and conditions, and listed its own limitations.
- **Isolation.** Operators ran from a copy of the repository without the answer
  keys. The keys were in a separate folder that only the judges read. Afterwards,
  every operator tool call was scanned for reads of keys, page HTML, snapshot JSON
  or scenario files.
- **Judges.** Two blind judges scored each screen (Opus 5.5 at max effort).
  - Each judge saw the arms under letters, in a different rotation.
  - They read the answer key, each arm's `run.json` and its screenshots.
  - They scored matched defects, decoys flagged, false alarms (decoy flags
    included), valid extra findings, protocol violations, and quality from 1 to 5.
  - In the pilot, a third judge also scored four arms on one screen.
- **Success** is the driver's measured check in `run.json`
  (`success_basis: measured`), not the operator's claim.
- **Cost** counts input, cache-write and cache-read tokens from the agent
  transcripts, at list prices. The transcripts do not record output or thinking
  tokens, so every cost below is a lower bound.

## Results

Counts are the mean of the two judges, summed over the screens.

| Arm | Success (measured) | Defects matched (of 40) | False alarms, 8 defect screens | False alarms, 3 clean controls | Valid extras | Protocol violations | Quality (1–5) | Cost per run, lower bound | Time per run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Haiku 4.5 | 6/11 | 0 | 11.0 | 4.0 | 2.0 | 6.0 | 1.23 | $0.28 | 3.6 min |
| Sonnet 5.5, high | 11/11 | 20.5 | 3.5 | 6.0 | 9.5 | 0 | 2.86 | $0.31 | 1.3 min |
| Sonnet 5.5, max | 11/11 | 22.5 | 2.0 | 1.0 | 16.0 | 0.5 | **4.11** | $0.53 | 4.7 min |
| Opus 5.5, high | 11/11 | 21.5 | 1.0 | 4.0 | 15.0 | 0.5 | 3.57 | $0.55 | 1.8 min |
| Opus 5.5, max | 11/11 | 20.5 | 4.0 | 1.0 | 19.5 | 3.0 | 3.91 | $0.98 | 4.9 min |
| Fable 5.1, high | 11/11 | 12.5 | 3.0 | 5.0 | 13.0 | 1.5 | 2.77 | $1.11 | 2.1 min |

No arm claimed success on a run that the driver measured as failed.

**Grounding.** The driver counts a miss when a text target is not found or when
another element covers the target.

| Arm | Misses | Steps |
| --- | --- | --- |
| Haiku 4.5 | 17 | 169 |
| Sonnet 5.5, high | 3 | 89 |
| Sonnet 5.5, max | 0 | 84 |
| Opus 5.5, high | 0 | 90 |
| Opus 5.5, max | 1 | 94 |
| Fable 5.1, high | 1 | 87 |

Every recorded miss came from a text target (`text=…`). A coordinate tap that
lands on the wrong element is not counted, so these numbers are lower bounds.

**Judge agreement.**

- Quality scores were identical on 49 of 66 runs and never more than 1 point
  apart (Pearson r = 0.93).
- The two judges' matched-defect sets overlapped 96% on average (Jaccard, over the
  37 runs where either judge matched a defect).
- The pilot's third judge matched the same defects and was within half a point on
  quality.

**Paired comparisons** of per-screen quality: mean difference, 95% bootstrap
interval over the 11 screens, and the number of screens that were better or worse.

| Comparison | Quality difference | Better / worse screens |
| --- | --- | --- |
| Sonnet max vs Sonnet high | +1.25 (0.59 to 1.95) | 10 / 1 |
| Opus high vs Sonnet high | +0.70 (0.14 to 1.20) | 8 / 1 |
| Sonnet max vs Opus high | +0.55 (0.20 to 0.95) | 7 / 1 |
| Opus max vs Opus high | +0.34 (−0.27 to 0.86) | 6 / 2 |
| Sonnet max vs Opus max | +0.20 (−0.16 to 0.64) | 4 / 1 |
| Opus high vs Fable high | +0.80 (0.45 to 1.16) | 9 / 0 |

Matched defects per screen did not differ clearly among the Sonnet and Opus arms:
every interval includes zero. Opus high matched 1.1 more defects per screen than
Fable high (0.50 to 1.75).

## What the runs show

- **Haiku 4.5 is below the line.**
  - It failed 5 of 11 tasks, including all 4 mouse screens. Its clicks missed small
    targets.
  - It then reported its own misses as product defects: 15 false alarms, and no
    seeded defect found.
  - It read snapshot JSON 22 times, which the screenshot-only rule forbids. No
    other arm read a forbidden file.
- **Sonnet 5.5 is the first adequate tier.** At high effort it reached every goal
  and matched as many defects as Opus. It also raised the most false alarms on the
  clean controls: 6.0 on 3 screens. For example, it re-reported fixed defects and
  misread 품절 as 품질.
- **Effort matters as much as the model.** Moving Sonnet 5.5 from high to max
  effort had three effects:
  - quality rose by 1.25 points, the best of all arms;
  - false alarms fell from 9.5 to 3.0;
  - the measured cost became about the same as Opus 5.5 at high effort.

  The price is time: 4.7 minutes per screen against 1.8 for Opus at high effort.
- **Opus 5.5 at max effort added nothing over Sonnet 5.5 at max effort.**
  - It cost nearly twice as much.
  - It made the most protocol violations among the capable arms (3.0). It derived a
    viewport height by assumption and used it as evidence for P0 claims, and it
    made prevalence claims such as "most users".
- **Fable 5.1 at high effort** cost the most and found the fewest defects among
  the arms that finished every task. It was not run at max effort.

## Answer and default

Adequate performance starts at Sonnet 5.5. The first-run prompt in
`agent-setup.md` offers these options:

| Option | Why |
| --- | --- |
| Sonnet, max effort (recommended) | Best quality and fewest false alarms; the slowest option. |
| Opus, high effort | About as many defects found, about 2.6 times faster, at a similar measured cost; lower quality (3.57 against 4.11). |
| Sonnet, high effort | Fastest, and it reached every goal. It raises more false alarms, so keep the judge pass. |
| Same as this session | No configuration. |

Haiku 4.5 is not offered.

Judges and verifiers default to Opus at max effort, the setting the benchmark's
judges used. Other judge models were not compared.

## Limits

- **Small sample.** 11 screens and one run per arm and screen. Treat quality
  differences under about half a point as noise.
- **No profiles.** The personas had no body or sense profile, so defects that the
  answer keys tie to a profile were hard to find for every arm. Recall compares
  arms; it is not a detection rate.
- **One judge family.** All judges were Opus 5.5 at max effort. The two judges
  and the pilot's third judge agreed closely, but a judge from another model
  family was not tried.
- **Cost misses output and thinking tokens.** Judging by the size of their
  thinking signatures, the max-effort arms produced about 9 to 19 times more
  thinking than the same models at high effort. Their real cost gap is therefore
  wider than the table shows.
- **Time is relative.** Time per run includes driver start-up. It was measured in
  a shared container with other agents running, so compare the arms with each
  other, not with your machine.
- **Older driver.** The driver was the `c607282` version. Its replies then included
  snapshot file paths, which is how one arm could read them. The current driver
  leaves DOM details out of its replies when the operator is registered as
  screenshot-only (`--agent-json` with `"input_channel": "screenshot"`).
- **Agent-written screens.** Agents wrote the benchmark screens and answer keys,
  like the other suites in this repository.
- **Claude only.** Only Claude models were tested. On Codex or another host,
  choose by analogy and record the choice.
