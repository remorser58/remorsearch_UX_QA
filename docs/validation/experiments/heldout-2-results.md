# heldout-2 results (C1–C5)

Scored at the frozen detector `0a4fd68` (`provenance.commit`, `dirty: false`), with
the pre-registered settings (`heldout-2-preregistration.md`, amendments 1–7).
Aggregates only: `docs/validation/heldout-2-aggregate-0a4fd68.json`. Per-defect
results stay sealed until this file is committed. C6 (persona agents) and the
round-2 adjudication are reported separately.

Suite: 4 products (clinic, expense, kiosk, rhythm), 48 defects, 16 decoys,
4 clean scenarios. Recording: 26 runs, 25 completed; 1 run stopped on a failed
scripted step (exit 3, a landscape phone run) and is counted as failed, not
re-run.

## Recall and noise

| Config | Strict recall (48) | 95 % CI | P0–P2 | Unconditioned | Clean-control units (P0/P1/P2/P3) |
| --- | --- | --- | --- | --- | --- |
| C1 measured-only | 0.229 (11) | 0.13–0.37 | 0.146 | 0.458 | 6 (0/0/3/3) |
| C2 single persona | 0.292 (14) | 0.18–0.43 | 0.208 | 0.542 | 19 (0/0/7/12) |
| C3 stratified | **0.562 (27)** | 0.42–0.69 | 0.375 | 0.542 | 23 (0/0/8/15) |
| C4 audience @6 | 0.417 (20) | 0.29–0.56 | 0.292 | 0.542 | 24 (0/0/7/17) |
| C4 audience @10 | 0.500 (24) | 0.36–0.64 | 0.333 | 0.542 | 24 (0/0/7/17) |
| C4 audience @14 | 0.542 (26) | 0.40–0.67 | 0.333 | 0.542 | 24 (0/0/7/17) |
| C4 floors only @10/@14 | 0.438 (21) | 0.31–0.58 | 0.250 | 0.542 | 23 |
| C4 swapped audience @10/@14 | 0.312 (15) | 0.20–0.45 | 0.188 | 0.333 | 18 |
| C5 random @6 / @10 / @14 (20 seeds, mean) | 0.373 / 0.381 / 0.392 | – | – | – | 23.7 / 23.1 / 22.8 |

Baselines: a trivial detector that flags every element in every category reaches
0.896 with 36 clean units; findings moved to random elements (chance) reach 0.145
for C3 (95th percentile 0.208), so C3 is 0.417 above chance (κ-style 0.49).

## Hypotheses

| Hypothesis | Result | Verdict |
| --- | --- | --- |
| H1 semantics/layout recall (reported; not blind discovery, see amendment 1) | C3 10/14 (0.71), C4@14 9/14 (0.64) | reported |
| H2 audience beats random at budget 10 | overall +0.119 (0.036–0.21); primary defects +0.083 (0.00–0.21) | inconclusive (overall part passes, primary part inconclusive) |
| H3 C4@14 not worse than C3 − 0.05 | −0.021 (−0.104 to 0.042) | inconclusive |
| H4 noise (C4@14): P0–P1 ≤ 1 and P0–P2 ≤ 5 per clean scenario | 0.0 and 1.75 | pass |
| H5 condition identified ≥ 0.5 (C3, C4@14) | 0.083 and 0.125 | fail |
| H6 persona agents | scored separately (C6) | – |
| H7 C3 unconditioned ≥ C2 | +0.000 | pass |

Confirmatory sequence (amendment 3, fixed order): the noise gate N (P0–P2 clean
units per clean scenario ≤ 0.35) fails at 1.75, so the sequence stops there and
H7′, HA, H3′ and H2′ are descriptive: H7′ pass, HA 3/13 (fail), H3′ pass,
H2′ +0.167 (−0.005 to 0.331, fail).

SIT-04 (amendment 4): no conditioned defect is detected through the touch
multipliers and no clean unit depends on them; the rule to cut does not hold, so
the multipliers stay.

## Reading

- Stratified coverage (C3) finds 27 of 48 blind defects, 2.5 times the measured
  checks alone and about 0.17 more than random profile sets of the same size; no
  clean-control finding is P0 or P1.
- Audience composition at 14 profiles is level with stratified coverage (within
  its interval) and clearly beats a swapped audience (0.54 vs 0.31), so the
  audience research carries information, but the pre-registered "beats random on
  the defects that matter to the audience" is not shown at this sample size.
- Findings rarely name the condition that makes a defect a problem (H5 fails):
  most conditioned defects are found by findings that fire for every profile.
- The noise gate from the detector-evaluation brief (≤ 0.35 P0–P2 units per clean
  scenario) is not met (1.75); all of those units are P2.
