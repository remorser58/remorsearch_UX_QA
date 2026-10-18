# heldout-2 pre-registration

This document was written before `benchmarks/heldout-2` is scored. Everything
below is fixed first: the scorer, the configurations, the metrics, the hypotheses
and the pass rules. Changes after scoring must be listed in a dated amendment at
the end, with the reason, and the original analysis must still be reported.

## Custody

- The suite was written by four blind Opus agents from product briefs and public
  taxonomies, using the format in spec §12.1. Their completion messages were
  restricted to counts and file lists.
- The tool author does not open `benchmarks/heldout-2/keys/`,
  `site/` or `scenarios/` content. Scripts read them for recording and scoring.
- Scoring output shown to the author is limited to aggregate metrics. Per-defect
  results are written to a file and opened only after the aggregate report is
  committed.
- **Known limitation:** authors, detector author and adjudicators are all Claude
  models (a project choice). The briefs use public
  taxonomies, but the answer-key schema still uses this tool's categories and
  profile attributes.

## Freeze

- The detector (`ergoqa/`, `drivers/web/`) and the scorer (`ergoqa/bench.py`)
  are frozen at the commit recorded in the scoring summary (`provenance.commit`,
  `dirty: false`) before the first recording of heldout-2.
- No change to checks, thresholds, floors or the composition algorithm is
  allowed between freeze and scoring.

## Configurations (all on the same recorded runs)

| ID | Profiles per device group |
| --- | --- |
| C1 measured-only | This tool's measured checks, default persona (30s, right one-hand / right mouse, no conditions) |
| C2 single persona | All checks, default persona |
| C3 stratified | `sample_profiles` stratified coverage: 14 per touch device, 7 per pointer device (current default fallback) |
| C4 audience-composed | `audience.compose` from the Stage-0 `audience.json` of each product, default floors. Budgets 6, 10 and 14 per product |
| C5 random | `sample_profiles(strategy="base_rate_sample")`, same budgets as C4, 20 seeds, mean and 95 % range |
| C6 persona agents | Opus persona agents in serve mode, composed from the audience (budget 4 per product), `--agent` recorded. Scored on `agent_judgment` defects only |

Stage 0 is run blind to defects. For each product, one Opus agent reads only
`products/<slug>/brief.md` and public sources, following
`skills/remorsearch-ux-qa/references/ergonomics/audience-research.md`, and writes `audience.json`. That file is
committed before any recording.

## Scorer settings

- `bench.score(..., exact_viewport=True, include_hypotheses=False)`.
- Strict matching: scenario, category, selector and condition satisfied by a
  triggered profile.

## Metrics

- `recall_strict` with a Wilson 95 % CI (headline). Reported alongside:
  - `recall_strict_by_operating_point` (P0–P1, P0–P2, all);
  - `recall_strict_unconditioned`;
  - `condition_identified`;
  - `recall_lenient`.
- Recall per category, per `detectable_by` class and per `audience_relevance`
  class.
- Noise:
  - `validity_lb_units` (all units in the denominator);
  - `precision_labelled_subset_units`;
  - `clean_control_units` and per clean scenario, by severity;
  - decoy units;
  - unlabelled units.
- Severity: agreement with `severity_min` (one-sided).

## Hypotheses and pass rules

**H1: Coverage outside the check families is low, and is reported.**
Recall on `semantics` and `layout` defects is expected to be near 0, because
there are no checks for them yet. This is reported and not tuned.

**H2: Audience composition finds the defects that matter to the product's users.**
At a budget of 10 per product:

- C4 recall on `audience_relevance = primary` defects ≥ C5 mean + 0.10;
- C4 overall recall ≥ C5 mean.

Both must hold for "audience composition beats random" to be claimed.

**H3: Audience composition is not worse than stratified coverage at equal or
lower budget.** C4 at budget 14 has overall recall ≥ C3 − 0.05. If it fails, the
report says stratified coverage remains the better default for detection, and
audience composition is kept for prioritisation and agent selection.

**H4: Noise is acceptable for triage.**
C4 at budget 14 has:

- P0–P1 clean-control units per clean scenario ≤ 1;
- P0–P2 clean-control units per clean scenario ≤ 5.

**H5: Condition identification.**
`condition_identified` ≥ 0.5 for C3 and C4 at budget 14.

**H6: The persona-agent layer finds task-flow problems.**
C6 detects ≥ 30 % of `agent_judgment` defects. Uncorroborated PJ-01 notes are
hypotheses and do not count. Round-2 adjudication must find
≤ 1 invalid corroborated PJ-01 finding per clean scenario.

**H7: Unconditioned recall.**
C3 `recall_strict_unconditioned` ≥ C2 `recall_strict_unconditioned`. This is a
sanity check that more profiles do not hide profile-independent defects.

Each hypothesis is reported as pass, fail or inconclusive (CI overlapping the
threshold), with the numbers. There is no tuning between hypotheses.

## Round-2 adjudication

A stratified sample of at least 60 units from C4 budget 14 (unlabelled and
clean-control units, all check families present) is judged. Each unit gets 2
independent Opus judges who see the screenshot, element and rule text but not
the key. The report gives agreement and κ, and valid / invalid / split per check
family and per basis.

## Amendments

### Amendment 1 (2026-09-28, before the freeze and before any heldout-2 recording)

Nothing here was informed by heldout-2 content: its keys, pages and scenarios
have not been opened by the tool author. Development used the three dev suites
(exp4) and the new development suite `benchmarks/dev-2`.

1. **Detector changes since this document was written:** GM-04 flash screening
   rework (block grid, sampling during waits, capture jitter; live check 30/30);
   RH-01 treats pause, menu and settings game controls as secondary; new
   semantics and layout checks SM-01 (unnamed control), SM-02 (label in name),
   SM-03 (unlabelled field), SM-04 (error neither near nor linked to a field) and
   LY-01 (clipped text); screenshot-channel operators get no DOM data from the
   driver.
2. **H1 reinterpreted.** H1 assumed no semantics or layout checks. With SM and
   LY checks, H1 reports their recall, but it is not evidence of blind
   discovery: the tool author wrote the heldout-2 authoring prompt, whose
   examples of rule sets (WCAG 4.1.2, 2.4.3, 2.4.7, 2.4.11, 1.4.10, 1.4.4, ATF,
   XCTest) overlap the rules these checks implement. The checks were built from
   public rule sets and tuned only on dev-2.
3. **Secondary metric added:** `recall_condition_attributed` (a conditioned
   defect counts only when the finding's differential names its condition).
   exp4 showed that strict matching credits condition presence: a finding that
   fires for every profile matches a walking-only defect when a walking profile
   is present. The headline stays `recall_strict`.
4. **Intervals for comparisons** (H2, H3, H7): paired bootstrap over defects,
   2 000 resamples, seed 7; single rates use Wilson intervals. Verdict rule as
   above (pass when the whole interval clears the threshold, fail when it is
   entirely below, otherwise inconclusive).
5. **C6 details:** operators are Opus only (a project choice).
   Four composed profiles per product; input channels alternate between
   `screenshot` and `screenshot+a11y`, so notes can be corroborated across
   channels. Every profile runs both variants of its product in separate
   sessions. A judgment note has no category, so C6 recall uses lenient matching
   (scenario, selector, condition); strict matching is reported too.
6. **Runner:** `skills/remorsearch-ux-qa/scripts/ergo_eval.py` (record,
   analyse, score, agents-plan, score-agents) implements C1-C6 and H1-H7 as
   written here; it prints aggregates only and seals per-defect results.

### Amendment 2 (2026-09-28, before the freeze and before any heldout-2 recording)

1. **C6 operators mix Opus and Sonnet** (Sonnet was added to broaden the
   operator models). Four composed profiles per product cover {Opus, Sonnet} ×
   {screenshot, screenshot+a11y}. Both models are one family (`claude`), so a
   note is corroborated only by another input channel; agreement between Opus
   and Sonnet on the same channel does not count. Results are also reported per
   model.
2. **Stage-0 composition fixes** found while running Stage 0 on the heldout-2
   briefs (no defect content involved): the walking floor attaches only to a
   phone or foldable; scenario stubs skip segments that do not operate the
   product; `evidence[].quote_basis` records whether a quote was read on the page
   or only in a search snippet (this environment's network policy blocks most
   public sites, so Stage-0 quotes are largely snippets and are listed as
   unverified in each persona plan).
3. **Round-2 adjudication judges:** one Opus and one Sonnet judge per unit
   (instead of two Opus judges), to reduce correlated errors within one model.

### Amendment 3 (2026-09-28, before the freeze and before any heldout-2 recording)

From `docs/qa-discipline/evaluating-qa-detectors.md` (EVD-01..06). The original
H1–H7 verdicts are still computed and reported. What is added:

1. **Trivial baselines (EVD-01).** `flag_all` reports every visible element in
   every category for every C3 profile at P0. Chance level moves the tool's own
   findings to random elements of the same scenario, 1 000 times. Both are scored
   with the same scorer. `kappa_recall = (recall − chance) / (1 − chance)`.
   - On the old held-out suite (heldout-mixed recordings, test run), `flag_all`
     reaches strict recall 0.95 with 36 clean-control units against the swarm's
     0.90. Strict recall alone therefore cannot support a usefulness claim. It is
     reported only next to noise, chance-corrected recall and twin discrimination.
2. **Clean-twin discrimination (EVD-02).** A strictly detected defect counts as
   discriminating only when its selector and category are not also flagged in its
   product's clean twin. Reported: `recall_discriminating` and per-category
   Youden J = TPR − FPR(twin).
3. **Product clusters (EVD-04).**
   - Reported: a two-stage product bootstrap (2 000 draws), a leave-one-product-out
     range and recall per product.
   - With 4 products these are descriptive. A claim about "the next product" is
     made only as the number of products where the direction holds.
4. **Noise gate N (EVD-05)** replaces H4 as the confirmatory noise rule.
   - Rule for C4@14: no P0–P1 clean-control unit, and P0–P2 clean-control units per
     clean scenario ≤ 0.35 (point estimate).
   - The Poisson 95 % upper bound and an FROC-style table by severity threshold are
     reported. They are not gated: with 4 clean scenarios, a single unit already
     gives an upper bound of 1.39.
5. **Confirmatory fixed-sequence family (EVD-03).** Each step uses a two-sided 95 %
   interval (one-sided 0.025). Testing stops at the first step that does not pass,
   and the steps after it are descriptive. Margins were set by simulated power
   before any heldout-2 data.

   | Order | Hypothesis | Rule | n expected | Power / MDE |
   | --- | --- | --- | --- | --- |
   | 1 | N | as above | 4 clean scenarios | – |
   | 2 | H7′: C3 not worse than C2 on unconditioned defects | Newcombe paired interval lower ≥ −0.15 | ~22 | 99 % if C3 and C2 agree on every defect; 35 % with 10 % discordance each way |
   | 3 | HA: models name the condition | C4@14 `condition_identified` among detected conditioned defects, Wilson lower ≥ 0.30 | 15–20 | needs a point estimate of about 0.53–0.55 |
   | 4 | H3′: C4@14 not worse than C3 | Newcombe lower ≥ −0.20 | ~45 | 84 % with 10 % discordance each way (margin −0.10: 31 %) |
   | 5 | H2′: audience beats the placebo audience | C4@10 − C4-swap@10 on primary defects: lower > 0 and point ≥ +0.10 | 16–24 | 80 % only if the true effect is about +0.35 or more. Underpowered, so the estimate and its interval are the result |

   The brief's original margins (−0.05, −0.10) had near-zero power at these n.
6. **Placebo arms (EVD-06)**, computed offline on the same recordings.
   - `C4-swap@{10,14}`: each product composed from the next product's audience,
     with the device mix replaced by the product's own devices.
   - `C4-floors@{10,14}`: a neutral audience of one adult segment with the default
     floors.
   - "Audience research adds value beyond the floors" is claimed only if C4 beats
     both arms on primary defects. Otherwise the gain is attributed to floors and
     stratification.
   - `C4-rep` (repeated Stage 0) is not run before the freeze.

### Amendment 4 (2026-09-28, before the freeze and before any heldout-2 recording)

1. **Detector changes from dev round 8** (`decisions.md`): SIT-01 (profile-only
   PT-03/PT-04 on targets of at least 7.0 mm are P3 at most) and SIT-03
   (multiplier values and citations). SIT-02 was not adopted. Both changes were
   judged on dev recordings only, before the freeze.
2. **SIT-04, a conditional cut decided once on heldout-2.** It is exploratory and
   changes no confirmatory verdict. After scoring, compute for C3 and C4@14 the
   `recall_condition_attributed` of defects conditioned on walking, tremor or age
   60+ that are detected through PT-03/PT-04, and the clean-control units that only
   those multipliers produce (multipliers-off re-analysis of the same recordings).
   - **Cut** (after this evaluation, not in the frozen detector) if both hold:
     attributed detections = 0 and clean-control units from those multipliers ≥ 3.
     Profile-only PT-04 then moves to the hypothesis tier. `one_hand_thumb` stays.
   - Otherwise the multipliers stay, with the observed numbers reported.
   - Implementation, fixed before any heldout-2 data (`ergo_eval.py analyse
     --variant condition-multipliers-off`, then `score`; `sit04()`):
     - "attributed" means strictly detected, the finding's differential names the
       key's condition, and PT-03 or PT-04 is among the matched checks;
     - a multiplier-only unit is a clean-control unit none of whose elements the
       same check flags in the multipliers-off analysis;
     - the variant sets walking, transit, tremor, age and encumbrance multipliers to
       1.0 and keeps `one_hand_thumb`;
     - the cut needs the rule to hold in both C3 and C4@14.

### Amendment 5 (2026-09-29, custody incident, before the freeze and before any heldout-2 recording)

Disclosure. The rule is that the tool author reads no heldout-2 key, page or
scenario content and sees aggregates only. It was broken three times, without
opening any suite file:

1. **Stage reports in a workflow notification.** When the authoring workflow
   stopped at the account usage limit, its completion notice carried the authoring
   agents' stage reports into the author's session. Beyond counts, they contained
   build notes:
   - rhythm: an animation on one seeded element was moved so scripted taps reach
     it; DOM order was set so focus order follows the screen order in both
     variants; a settings row was tightened to fit 360 × 780; a shared,
     non-seeded pad border was raised to about 3.7:1 contrast; a data attribute was
     added for the success condition; 38 steps, 3 timing windows, galaxy-s24 and
     galaxy-a55.
   - expense: both variants were checked for text size, click-target size and
     spacing, 320 px and 200 % reflow, keyboard focus handling and focus hidden
     by a fixed bar, plus an axe-core cross-check; counts by evidence type,
     audience relevance, severity and profile condition; a desktop mouse and
     keyboard product; 27 steps, 2 transient-text windows, laptop-1440 and
     desktop-1920.
2. **Journal preview.** The first 150 characters of each stage result in the
   workflow journal, read to check progress (counts only).
3. **File names and modification times** of heldout-2 files, printed by a
   command whose name-masking pattern failed (no content).

No defect identity, selector, profile condition or variant assignment was seen.

Effect on the detector:
- The round 10 focus-check code (AUT-09, AUT-13) was written, self-tested and
  gated on the ACT examples before the notice arrived. Its commit (`197865f`)
  came after the notice, and only its decision-log text was written afterwards.
- From here to the freeze, a detector change must cite a dev-suite result or an
  external source (standard, ACT example, paper), as before. None may cite these
  notes.

Process fixes:
- The blind verification stage reports changes only as counts per file.
- Blind workflows are no longer resumed from their journals by the author. The
  remaining stages are relaunched with an explicit start stage instead.

Addendum to amendment 5 (same day). The relaunched verification stage reported its
changes as counts per file, as the author's revised instruction asked. For expense
this showed which page variant the verifier edited, which may hint at the variant
assignment. rhythm's report showed no page edits. No detector change uses variant
identity: the detector never compares variants, and scoring is automatic from the
key. Later blind stages report only the total number of changes.

### Amendment 6 (2026-09-29, before the freeze and before any heldout-2 recording)

**Composition fix: no-op facets.** The rhythm Stage-0 agent reported that its
persona plan listed "grip two_thumbs" as untested for a segment whose typical member
already holds the phone with two thumbs. The variation would have copied the typical
member. `audience.compose` now drops any facet whose profile equals the segment's
typical member, so it is neither composed nor listed as untested. Recomputed on the
four committed audience files: the C4 profiles at budgets 6, 10 and 14 are identical
before and after the fix; only rhythm's untested list loses that entry. No defect
content was involved.

### Amendment 7 (2026-09-30, before the freeze and before any heldout-2 recording)

Nothing here was informed by heldout-2 content. All changes were judged on the dev
suites (`benchmarks/dev-2` and the three older ones), the driver self-test, the flash
validation pages and the W3C ACT examples; `decisions.md` rounds 9–12 give the
evidence.

1. **Checks added or changed since amendment 1** (all tuned only on dev suites):
   - new: SM-08 (clicked element that is not a control), FM-02 (focus not moved
     into an opened layer), RF-01 (reflow at 320 CSS px), SM-06 at a step, SM-05
     probes before clicks on mid-task screens;
   - changed: SM-01/SM-03 apply to zero-size controls and author-only roles; LY-01
     includes clipping by an ancestor and marks ACT 59br37's clean cuts as P3 notes;
     GZ-02 gives P1/P2 only to new messages and skips the old tap point after an app
     scroll; GM-04 IRIS extended rule and oscillating-scroll guard; GM-06 press rule
     cut.
   H1's reinterpretation (amendment 1) applies to all of them: the authoring prompt
   named the rule sets these checks implement, so their heldout-2 recall is not
   blind discovery.
2. **C3 strata.** `CONDITION_STRATA` gains `low_vision` (placed before `70s_plus`),
   and pointer devices skip the touch-only strata (walking, small_hand, tremor). C3
   keeps 14 profiles per touch device and 7 per pointer device.
3. **Driver changes that affect every check:** frames are taken of the screen (not
   the document top); visual feedback masks the caret and pixels already moving
   before the input; `input` events and script value changes of text-like fields
   count as feedback; no-op writes and `<html>`/`<body>` attributes do not.
4. **ACT gate:** 59br37 is also run at 640 × 512 (`ergo_act.py --viewport`); LY-01
   findings marked `act_59br37: passed` are truncation notes, not gate failures.
5. **Freeze.** The detector and scorer are frozen at the commit that adds this
   amendment; the scoring summary records it (`provenance.commit`, `dirty: false`).

