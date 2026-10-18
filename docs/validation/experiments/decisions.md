# Keep / cut / add decisions

Every change to the check catalogue, the profile plan and the scoring is logged
here with its evidence. Sources used below:

- **Dev ablation:** `ablation-dev-8707b70.json`, leave-one-out on the three
  development suites (53 seeded defects).
- **Adjudication:** `docs/validation/adjudication-round1.json`, 68 sampled findings,
  2 judges, κ 0.72.
- **Reviews:** six Opus cross-reviews (human factors, UX design, QA practice, game
  accessibility, methodology, code correctness).
- **Research:** the briefs in `docs/qa-discipline/`, cited by candidate ID
  (UEM-, STF-, AP-, LAT-).

The development suites are training data, so every decision here is post-hoc for
them. The out-of-sample test is `heldout-2`, pre-registered in
`heldout-2-preregistration.md`.

**Decision rule:**

- **KEEP:** the item finds seeded defects that nothing else finds (unique
  detections), or it is a normative check with a measured basis.
- **CUT or demote to hypothesis:** no unique detection on dev, and either
  adjudicated validity ≤ 1/6 or clean-control noise ≥ 5 findings.
- **CHANGE:** judges named a concrete cause of invalid findings, so the cause is
  fixed rather than the check removed.
- **ADD:** a candidate that research ranks high and that can be measured by the
  driver. It is evaluated on heldout-2 per category, never tuned on it.

## Demoted to hypothesis (computed, listed for review, never counted as defects)

| Item | Evidence | Decision |
| --- | --- | --- |
| GZ-01 primary not fixated early | 0 unique on 53 dev defects; 17 clean-control P3; 0/6 judged valid (wrong state, free-viewing artefact); STF-01, UEM-03 | hypothesis |
| GZ-04 competing emphasis | 0 unique; 7 clean-control P3; 1/6 valid | hypothesis |
| PC-05 bright-sun contrast | 0 unique; 17 clean-control P3; judges split (1 valid, 3 split); the bright-sun stratum adds 31 findings and no defect | hypothesis |
| PT-05 Fitts ID > 6 bits | no normative threshold; no dev finding (STF-22) | hypothesis |
| GM-06 button mashing | counts the presses the script needed, not what the game requires (game review); its one dev detection is a scripting artefact | hypothesis until a press-rate sweep exists |
| PJ-01 persona notes, uncorroborated | an agent's self-declared corroboration is not evidence (STF-23, LAT-03) | hypothesis unless runs of a different model family or input channel note the same anchor |

## Narrowed (cause fixed, check kept)

| Item | Unique dev detections | What was wrong (adjudication or review) | Change |
| --- | --- | --- | --- |
| All position and perception checks | – | findings on elements covered by a sheet or behind a modal | skip elements ≥ 50 % covered by a *painting* layer or inert behind a modal; transparent click layers and `pointer-events:none` overlays do not count |
| RH-01 reach | 6 | phone model applied to tablets; reach scored at the target's centre | tablets use side grips (HGR-9); easiest point of the target |
| RH-02 destructive in easy zone | 0 | a link that opens a confirmation is not a risk (0/2 valid) | only `irreversible` actions |
| PT-02, PT-04 size and miss | 1 (PT-04) | label hit area ignored; 60 × 8.8 mm fields flagged; profile-only P2 on off-path controls | label-extended targets; flag only targets harder to hit than a 9.2 mm square; profile-only P2 only for primary or used controls |
| PC-02 boundary contrast | 2 | container colour measured against the page base; text-labelled radio cards; icon glyph ignored | driver composites the layer below; labelled cards exempt, switches and sliders not; icon glyph at 3:1 passes |
| PC-03 colour-only states | 4 | 입금/출금 and signed amounts not treated as state cues; status severity ignored | state words and signs are cues; status, warning and error encodings ≥ P2 |
| PC-04 text visual angle | 3 (critical print size tier) | critical print size applied to button labels, table cells, Latin text and inherited sizes | Hangul prose only (≥ 12 syllables; not interactive, heading or cell); elements must own their text. Cutting the tier would lose all 3 defects. |
| CG-01 choice overload | 1 | unrelated controls grouped by size; PIN pads; set truncated at the fold | group by container; keypads exempt; whole rendered group |
| CG-02 toast reading time | 4 | 4 000 ms toast measured as 3 995 ms; game pop-ups treated as messages; off-screen toasts not recorded | 50 ms tolerance; undeclared game pop-ups are decorative; off-screen appearances are recorded and flagged |
| CG-03 feedback latency | 1 | taps on closed QTEs or on focused fields; target resolved in the wrong snapshot | skip non-actionable targets and text fields; resolve in the before snapshot |
| GZ-02 feedback noticing | 4 | eccentricity to the centroid; salience from box fill only; redundant feedback; screen replacement | nearest point; bold or icon text at 4.5:1 is salient; redundancy and screen-replacement rules; off-screen feedback flagged (P1 for errors) |
| GM-02 landscape reach | 2 | pause flagged in the top band, where Apple HIG puts it | secondary controls (pause, menu, settings) exempt by name |
| GM-03 QTE window | 2 | model-only P1; declared QTE chains routed to flash screening | P1 only when a typical young adult misses the window, else P2; declared QTEs are always scored by GM-03 |
| GM-05 game control size | 1 | 9.6 mm serial size applied to pause | serial size for gameplay controls only |
| GM-04 flash | 1 | whole-frame mean luminance misses local, counter-phase and red flashes; no sampling during waits; a 3 Hz flicker counted as 3.5 flashes; red tested on gamma-encoded values | per-block tracking summed within 10° fields, sampling during waits, capture jitter, half-open 1 s window with 50 ms sampling tolerance, linear red test, `inconclusive` on poor sampling. Live check 30/30 (`docs/validation/flash-screening/`) |

## Profile plan

| Item | Evidence | Decision |
| --- | --- | --- |
| Floors: left hand (per input kind), deutan, presbyopia, walking | removing each lost unique defects in ≥ 2 dev suites (left one-hand 3–5, deutan 4, presbyopia 3 via PC-04, walking 2); AP-02 | keep as floors |
| Fallback strata: bright sun, first use, protan, large hand | 0 unique; bright sun +31 findings; no deterministic check reads familiarity (AP-03, AP-04) | removed from the fallback plan; audience composition adds them only with evidence |
| Tremor | 0 unique on dev, but an edge condition that has a model (AP-02) | kept |
| Touch σ multipliers (walking 1.4, tremor 1.5/2.25, age) | multipliers off: 0 dev defects lost, 29 fewer findings; judges: profile-only P2 too high off-path | kept, but profile-only severity is limited (see PT-04). Calibration brief pending. |
| Bottom-up conspicuity in gaze | the "gaze disabled changes nothing" toggle ran with a stale cache (code review) | **decision withdrawn**; rerun with the cache fix |
| Stratified vs random sampling | same recall at about a third of the profiles (dev); UEM-12 | keep stratified as the fallback; audience composition is the default |
| Audience composition, one facet per variation, presbyopia not tied to age facets | AP-01, AP-14 | adopted |

## Scoring and reporting

| Item | Evidence | Decision |
| --- | --- | --- |
| Coverage denominators | 203/225 held-out findings had tested == triggered (UEM-01) | the denominator is every evaluated profile the check applies to; the differential counts out-of-scope profiles as untriggered (AP-05) |
| Problem units | 225 findings → about 63 units (UEM-02, STF-03) | reports lead with units |
| Viewport wildcard matching | page-level findings matched any selector (UEM-10) | exact matching is available and is the heldout-2 headline |
| Precision "lower bound" | excluded unlabelled findings (methodology review) | `validity_lb_units` counts all units; labelled-subset precision is reported under its own name |
| Condition identification, recall by operating point, unconditioned recall | methodology review | added to `bench.score` |
| Held-out result | the id-prefix scorer rule was added after the freeze | reported with both scorers (0.60 / 0.80) |

## Pending additions (evaluated on heldout-2 per category, not tuned on it)

- Semantics and layout checks (accessible name, clipped text, focus, reflow): added
  in rounds 6, 10, 11 and 12 and pre-registered in amendments 1 and 7.
- Deterministic twins for agent notes (dead end, unclear error):
  `llm-agents-as-test-users.md` LAT-09.
- GM-03 acceptance-window measurement and a GM-06 press-rate sweep (game review).
- Browser chrome offset for mobile web viewports (human-factors review).

## Development-suite effect of the changes so far

| Recording | Detector | Strict recall (53) | Findings | Clean-control findings | Units | Clean-control units |
| --- | --- | --- | --- | --- | --- | --- |
| exp (before fixes) | `8707b70` | 0.906 | 518 | 213 | – | – |
| exp2 (round 1) | `782a15c` | 0.811 | 354 | 143 | 148 | 57 |
| exp3 (round 2) | `4dbdc37` | 0.849 | 186 | 51 | 96 | 26 |

| exp4 (rounds 3-4, flash rework) | `a11ef18` | 0.906 (95 % CI 0.80-0.96) | 193 | 53 | 97 | 26 |
| exp5 (semantics checks, RH-01 secondary controls) | `5b6e8fb` | 0.906 | 200 | 54 | 101 | 27 |
| exp6 (rounds 8-10: touch cap, IRIS rule, focus walk with viewport fallback, GM-06 cut) | `38cc073` | 0.906 (95 % CI 0.80-0.96) | 213 | 61 | 108 | 30 (P2 3, P3 27) |
| exp13 (rounds 11-12: new semantics/layout checks, screen-capture and feedback fixes, two pre-freeze reviews; `ergo_bench.py` swarm) | `cf7310d` | 0.906 (48/53) | 254 | 63 | 114 | 33 (P2 6, P3 27) |

exp6 detail (`ablation-dev-38cc073.json`, new recordings with the current driver): single default persona
0.642, measured checks only 0.302. At P0-P2 the swarm detects 39 of 53 defects; 40 are detected with the
condition named (or unconditioned). Clean-control P0-P2 units per clean scenario: 0.30 (EVD-05 gate 0.35).
The four desktop runs carry focus walks (end state and fresh load; the admin end-state walk stopped at its
8 s budget after 30 stops); the dev suites have no focus defect and SM-05/SM-06 report nothing on them.

exp4 detail (`ablation-dev-def157e.json`): single default persona 0.642, measured
checks only 0.302. Stratified coverage reaches 0.906 at 8 profiles per device;
random draws need 40 (0.904). Clean-control units by check: RH-01 7, PT-04 6,
PC-04 6, PT-02 4, CG-01 1, CG-02 1, GM-05 1; seven are P2, none P0-P1.

## Round 5 (from exp4)

| Item | Evidence | Decision |
| --- | --- | --- |
| Strict matching credits condition presence | The walking-conditioned defects (mobile D-07, mixed D-03) and one right-hand defect (mobile D-10) are found by PT-02/PT-04/RH-01 findings that fire for every profile (14/14, 13/13; no differential). The condition's profile only satisfies the key's condition. Deutan (PC-03 at 1/14) and left one-hand (RH-01 at 5/13) are real model contributions. | Add `recall_condition_attributed` (a conditioned defect counts only when the finding names its condition). Reported next to strict recall; the headline stays as pre-registered. The walking floor's dev evidence was presence, not modelling. |
| Touch σ multipliers | Off: 0 dev defects lost, 19 fewer findings, 6 fewer clean-control units. Four of the seven clean-control P2 units are 44 × 44 CSS px (8.1 mm) targets flagged only for walking or tremor profiles (miss probability 6-16 %). | Pending `situational-and-age-effects-on-touch.md` (calibrate, cap or cut). |
| Gaze conspicuity map | Disabling it (cache fixed) changes no counted finding; it feeds only the hypothesis-tier GZ-01 and GZ-04. | Keep for the hypothesis list; no effect on counted results. Candidate to switch off by default for speed. |
| RH-01 on secondary game controls | A pause hotspot out of one-thumb reach was P2 on a clean page; GM-02 already treats pause, menu and settings as secondary (Apple HIG). | Secondary game controls are not key controls in RH-01: out of reach is P3. |
| small_hand stratum | 0 unique defects in exp4 (was 1-2); 2-4 extra findings | Kept (low noise, reach model input); re-check on heldout-2. |
| GM-05 | 0 unique in exp4 (PT-04 covers the same controls); 1 clean-control unit | Kept (normative, low noise). |

## Round 6: semantics and layout checks on the dev suites (exp5, before dev-2)

The dev suites carry no semantics or layout keys, so this only measures noise and
cross-category hits. Single-profile analysis (the checks are profile-independent).

| Check | Defect variants | Clean controls | Review | Decision |
| --- | --- | --- | --- | --- |
| SM-04 (first rule: error > 48 px from every field and unlinked) | 4 (all real defects keyed as gaze/cognition: errors shown far from the user or generic) | 4 | 3 clean hits named their field in the text ("휴대폰 번호를 확인해 주세요"), which meets WCAG 3.3.1; 1 was a system notice declared `critical_message` | Narrowed: the text must name no field, and declared system notices are skipped. Result: 2 defect-variant hits, 0 clean. |
| SM-03 | 4 (unlabelled required checkboxes, keyed as a pointing defect) | 0 | real | Keep |
| SM-02 | 0 | 1 (a game radar item: visible "아군", aria-label "대상 2") | plausible true positive the key does not list | Keep; count as unlabelled |
| SM-01, LY-01 | 0 | 0 | – | Keep; recall is measured on dev-2 |

## Round 7: external precision gate (W3C ACT rule examples)

`skills/remorsearch-ux-qa/scripts/ergo_act.py` opens every example of seven ACT
rules (act-rules.github.io at `7e46818`, examples written by the ACT task force)
in the real driver and analyses it with the default persona. An implementation
is correct for a rule only if no Passed or Inapplicable example is reported.

| Rule | Check | First run: false alarms | Fixes | Final: false alarms | Final: detected (Failed examples) |
| --- | --- | --- | --- | --- | --- |
| 97a4e1 button name | SM-01 | 0/12 | – | 0/12 | 4/5 |
| c487ae link name | SM-01 | 3/17 (names of child images with aria-label, title, aria-labelledby) | name from content includes descendant image and labelled-element names | 0/17 | 7/11 |
| e086e5 field name | SM-03 | 1/12 (placeholder is an accessible name) | SM-03 only for no name; placeholder/title-only moved to SM-07 (best practice, P3); role-based fields (div role=textbox) collected; disabled fields at P3; presentational non-focusable skipped | 0/12 | 6/9 |
| 2ee8b8 label in name | SM-02 | 2/22 (visually hidden text; parenthesised text) | ACT label-in-name algorithm; visible inner text; abbreviations and hyphenation out of scope as ACT defines | 0/22 | 16/16 |
| 59br37 clipped text | LY-01 | 0/9 | – | 0/9 | 2/5 (the rest clip only at 200 % zoom, which is not rendered yet) |
| oj04fd focus visible | SM-05 | 0/6 | test assets served | 0/6 | 1/1 |
| 36b590 error text (informational) | SM-04 | 0/4 | – | 0/4 | 0/5 (SM-04 checks location and linkage, not wording) |

Undetected by design (not in the snapshot): zero-size links and buttons,
image-map areas, images whose source fails to load. AUT-20 (apply name rules to
focusable elements of any size) and AUT-07 (200 % zoom re-render) are post-freeze
candidates.

## Round 8: situational touch effects (SIT-01..03, exp5 re-analysis)

From `docs/qa-discipline/situational-and-age-effects-on-touch.md`. The stratified
swarm was re-analysed on the exp5 recordings once per variant with the current
detector (`touch-variants-dev.json`; `ergo_experiments.py touch-variants`). The
reference row ("before") uses the multiplier values before SIT-03, with factors
multiplied and no cap. 53 dev defects, 10 clean scenarios.

| Variant | Strict | P0–P2 | Attributed | Findings | Units | Clean units (P2) | PT-04 findings | Profile-only PT-04 at P2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| before | 0.906 | 0.736 | 0.755 | 213 | 108 | 30 (7) | 25 | 148 |
| SIT-03 values | 0.906 | 0.736 | 0.755 | 213 | 108 | 30 (7) | 25 | 154 |
| SIT-03 values − 0.1 | 0.906 | 0.736 | 0.755 | 213 | 108 | 30 (7) | 25 | 60 |
| SIT-03 values + 0.1 | 0.906 | 0.736 | 0.755 | 213 | 108 | 30 (7) | 25 | 171 |
| SIT-01 + SIT-03 | 0.906 | 0.736 | 0.755 | 213 | 108 | 30 (3) | 25 | 72 |
| SIT-01 + SIT-02 + SIT-03 | 0.906 | 0.736 | 0.755 | 213 | 108 | 30 (3) | 25 | 78 |
| SIT-02 + SIT-03 | 0.906 | 0.736 | 0.755 | 213 | 108 | 30 (7) | 25 | 160 |
| multipliers off | 0.906 | 0.736 | 0.755 | 194 | 98 | 24 (3) | 6 | 0 |

"Profile-only" counts observations (profile × snapshot × element) that fail only
because of the σ multiplier. These counts can move either way when values fall,
because PT-04 applies only to targets that are harder to hit than a 9.2 mm square
at the same multiplier.

| Item | Pass rule (brief) | Result | Decision |
| --- | --- | --- | --- |
| SIT-01: profile-only PT-04/PT-03 on targets ≥ 7.0 mm (`TOUCH_TARGET_MIN_MM`) are P3 at most | no dev defect lost at any operating point; clean-control P2 units ≤ 3 | 0 lost (strict, P0–P2 and attributed recall unchanged). Clean P2 units 7 → 3. The four removed are the 44 × 44 CSS px targets flagged only for walking or tremor (booking date, promo close, marketing toggle, amount clear); they stay listed at P3. The three left are CG-02, SM-02 (game radar) and RH-01. | **Adopted.** The cap uses `TOUCH_TARGET_MIN_MM`. Critical targets below it already get P2 from PT-02, so a separate 44 CSS px path (6.9 mm on Flip 6 and Pixel 8) was tried, changed nothing, and was removed. The brief's audience-linked P2 exception is not implemented: no dev data can test it, and it would let a weak Stage 0 raise severity. |
| SIT-02: factors add in variance instead of multiplying | 0 lost, PT-04 findings −30 % or more, Kendall τ ≥ 0.9 | 0 lost, τ = 0.92 against SIT-01 + SIT-03, PT-04 findings **0 %** (25 → 25). The swarm rarely stacks conditions, and each element is already flagged by some single-condition profile. | **Not adopted.** Kept as a sensitivity switch (`TOUCH_SIGMA_COMBINE`), default multiplicative. |
| SIT-03: multiplier values and citations | the same defects are detected under every value set | Identical detection under {before, recommended, recommended ± 0.1}. | **Adopted.** The values are a documentation matter: walking 1.4 re-cited to Conradi et al. 2015 (Ng et al. 2014's +40 % is an encumbrance effect), tremor 1.3 / 1.8, age 60s 1.10 from the Findlater & Zhang open data, age 70+ 1.3 marked as an assumption, `encumbered` 1.4 added (unused). |
| Multipliers off (SIT-04 evidence) | – | 0 dev defects lost again; −19 findings, −6 clean units (all P3 after SIT-01). Attributed recall is the same, so the condition names come from other models (reach, colour, grip), not from σ. | SIT-04 is decided once on heldout-2 (amendment 4). |

EVD-05 noise gate on dev (P0–P2 clean units per clean scenario ≤ 0.35, no P0–P1):
0.70 before, **0.30** with SIT-01. This is the effect the evaluating-detectors
brief predicted.

## Round 9: game brief items before the freeze (GQA-02, GQA-03)

| Item | Evidence | Decision |
| --- | --- | --- |
| GQA-03 (a) IRIS wording | The GM-04 message told users to "re-test with a certified tool (EA IRIS/Harding)". IRIS's README says it does not certify, and its default `FlashDetection.AreaProportion` 0.25 counts a transition only when a quarter of the frame changes, so a local flash that fails the 10° field rule can pass IRIS. | Message and reference text changed: an IRIS pass does not overturn GM-04; certification goes through a certified process such as Harding FPA. |
| GQA-03 (b, c) extended failure | The P1 rule was described as IRIS's but was a count rule (10 flashes within 5 s). IRIS's rule, read from `src/TransitionTracker.cpp` and `config/appsettings.json` at `d96978a` (BSD-3), is frame-based: a frame is in band at 4–6 transitions in the last second; failure when 4 s of the last 5 s are in band and the current count is ≥ 4. | Both rules kept and named: `sustained_5s` and `iris_extended` (ported on a 10 ms frame clock with IRIS's exact 1 s window; the WCAG rule's 50 ms tolerance would make a 2 Hz flicker read 3 transitions a fifth of the time). Either gives P1. `iris_warning` is recorded only. Pass rule met: the port equals an independent frame-by-frame restatement on 60 trains (regular 1.5–3 flashes/s × 3–6 s and 40 random), and the brief's boundary trains give 2 × 4 s no, 3 × 3.4 s no, 2.5 × 5 s yes, 2 × 3 s no, 2 × 5 s yes. The rules differ on uneven trains (3 flashes/s for 2.5 s then 1/s: sustained yes, IRIS no). Dev recordings: GM-04 verdicts unchanged (game-run P0, clean pass). |
| GQA-02 GM-06 | Already hypothesis-tier since round 1 (counts script presses). | No change before the freeze; the press-rate and hold-time sweep is post-freeze. |
| GQA-13 cut the GM-06 rule | Pass rule: every scoring metric unchanged. On the exp5 cache without GM-06: strict detections, findings (76, 44, 80) and clean-control units (17, 5, 5) are identical on all three dev suites; 49 GM-06 hypothesis observations on game-desktop disappear. | **Cut.** GM-06 stays registered but emits nothing until the sweep exists; `MASH_MIN_PRESSES` and the burst counter are removed. |

## Round 10: focus checks before the freeze (AUT-09, AUT-13)

| Item | Evidence | Decision |
| --- | --- | --- |
| AUT-09 SM-05 like ACT oj04fd | The walk compared only the element's box and small wrappers, so an indicator drawn elsewhere failed, and an animation inside the box could pass as an indicator. | Near the element: focused vs two blurred captures, and a pixel counts only if it differs from both while the two blurred captures agree (channel change < 4; animation mask). When fewer than 4 pixels change there, the whole viewport is compared (CDP capture downscaled to about 480 px wide, at most 6 stops per walk; focus restored by Shift+Tab, Tab so `:focus-visible` applies; kept only at the same element and scroll position; the focused capture is bracketed by two blurred ones). SM-05 fails only when both counts are below 4. Driver self-test: an indicator drawn 700 px away passes (87 px), an element with a colour-cycling dot and no indicator still fails (≤ 5 px masked noise below 4 is not guaranteed on every page, so the threshold stays). ACT gate after the change: 0/82 false alarms; oj04fd 0/6 and 1/1. The brief's GOV.UK check needs network access (not available) and the dev-2 focus-visible defect is scored when dev-2 is recorded. |
| AUT-13 SM-06 and the 2.4.11 note | WCAG Understanding for 2.4.11 (w3c/wcag `understanding/22/focus-not-obscured-minimum.html`, read 2026-09-29): the note about revealing the focused item without moving focus (for example with Escape) applies only to content the user opened; a sticky cookie banner that entirely hides the focused item fails; non-modal dialogs are named as a typical cover. The brief proposed an Escape test for any cover, which would pass cookie banners. | A cover is "user-opened" when it is tied to an expanded trigger (`aria-expanded="true"` + `aria-controls`) or an open `popovertarget` popover, and only in the end-state walk (nothing is user-opened on a fresh load). Only then the driver presses Escape; if the same element stays focused and is no longer fully covered, the stop is not obscured. Author covers fail as before. Non-modal dialogs with `position: absolute` now count as covers. Partly covered (2.4.12 AAA) is a hypothesis, not a finding. Self-test: a menu that closes on Escape passes, a chat that stays fails, an absolute dialog fails. dev-2 check pending. |
| Walk cost | One more small capture per stop and at most 6 viewport comparisons. | The fixture walk (21 stops) ends within the 8 s budget; the budget is unchanged. |

## Round 11: names of zero-size and author-named controls (AUT-20, name-from-content fix)

| Item | Evidence | Decision |
| --- | --- | --- |
| Name from content for author-only roles | ACT e086e5 failed example 7 (`<div role="textbox">first name</div>`) was missed: the driver named the textbox from its text. ARIA 1.2 gives textbox, combobox, listbox, slider, spinbutton, grid, tree, dialog, img, group and similar roles their name from the author only; their text is a value or content, not a name. | The driver no longer takes a name from content for those roles. |
| AUT-20 zero-size controls | The other misses were empty controls with no box: `<span role="button"></span>`, `<a href="…"></a>`, an empty `div role=textbox` under a label that cannot label it. They are in the accessibility tree, and the link takes focus. | The driver records `a11y.rendered` (not `display:none` or `visibility:hidden`; opacity ignored). SM-01 and SM-03 now apply to rendered, non-hidden controls with no box. The finding carries `visible_to_sighted: false` and is P2 at most (P3 when the control cannot take focus). Other rules still need a box. `<a>` without `href` is excluded (it has no link role; ACT c487ae inapplicable example 6 caught the first version). Recordings made before the field existed produce no such finding. |
| ACT gate after both | 97a4e1 5/5 (was 4/5), e086e5 9/9 (was 6/9), c487ae 10/11 (was 7/11; the image-map area is not collected), 0 false alarms on all seven rules; driver self-test 188/188. | Adopted. The brief's second condition (dev-2 clean-control units at most +0.2 per scenario) is checked on the dev-2 recordings, which have the new field. |

## Round 12: candidate checks from dev-2, driver capture fixes, two pre-freeze reviews

`benchmarks/dev-2` (36 defects, 12 decoys, 3 clean scenarios; civil, delivery, lms)
was written for the semantics, layout and task-flow checks. dev-2 numbers are the
stratified swarm (C3: 14 profiles per touch device, 7 per pointer device), strict
recall; clean-control units are counted on the 3 clean scenarios.

| dev-2 recording | Detector | Strict (36) | P0–P2 | Clean-control units (P1 / P2 / P3) |
| --- | --- | --- | --- | --- |
| first recording | `5b3d379` | 0.472 | – | – |
| candidate checks + SM-05 probe | `3a01137` | 0.583 | 0.528 | 23 (3 / 5 / 15) |
| + low-vision stratum (same recordings, analysis only) | `c097f30` plan | 0.611 | 0.556 | 23 (3 / 5 / 15) |
| new recordings after the screen-capture fixes | `c097f30` | 0.611 | 0.556 | 25 (0 / 10 / 15) |
| after review 2 (driver and checks) | `0e7f7fd` | 0.611 | 0.556 | 21 (0 / 8 / 13) |
| freeze candidate after review 3 | `cf7310d` | 0.611 | 0.556 | 21 (0 / 7 / 14) |

The 14 dev-2 defects still missed are the same at every point from `c097f30`: nine
heuristic (task-flow) defects, which the measured checks do not target (C6 persona
agents do), plus a tab order that differs from the visual order (D-delivery-07, no
check), an error text not linked to its field although it names it (D-delivery-09),
a caption hidden under a control bar (D-lms-02), 28 px option rows for tremor
(D-civil-09) and colour-only step dots (D-delivery-12). None was tuned for.

The three older dev suites (53 defects) stayed at 0.906 strict recall through every
recording of this round (exp10–exp13); their clean-control units went 35 → 33 and
all clean units are P2 or P3.

| Item | Evidence | Decision |
| --- | --- | --- |
| SM-08 clicked element that is not a control (WCAG 2.1.1, 4.1.2) | dev-2 keys two role-less clickable elements on the task path; a snapshot cannot tell a clicked div from decoration, the step can. Review: no-feedback taps, game surfaces, hotspots, `aria-hidden` scrims and card parts were false alarms. | **Kept (P1).** The driver records what each click landed on (`target_control`, through shadow roots). Exempt: clicks with no feedback at all, game surfaces, hotspots, `game_control`, hidden content, and the image or text of a card whose own link (or its one control) the keyboard reaches, unless the clicked element looks operable on its own or is a peer of a control (a chip row). |
| FM-02 focus not moved into an opened layer (2.4.3) | dev-2 keys an address sheet that opens without moving focus. Reviews: busy overlays, scrims, APG disclosures and MUI overlay roots were false alarms; dialogs that take focus after their transition and dialogs that open after a request were misses; a trigger inside the same fixed bar hid a real miss. | **Kept (P2).** Only layers with something to operate; a backdrop around a dialog (new or already open) is the dialog's; disclosures the trigger controls or the next Tab reaches are fine; focus reached within 1 s (0.7 s more after a wait) counts; a layer first seen at a wait within 3 s of a click, with no input between, counts for that click; the overlay root counts only when it wraps the layer. Clean FM-02 on mobile-commerce: 3 → 0. |
| RF-01 reflow at 320 CSS px (1.4.10) | dev-2 keys a fixed-width fee box, a summary table with fixed columns and a quiz bar whose timer is cut. Reviews: a ticking timer used up the 12 screen slots before the confirmation screens; copies lost CSS-in-JS rules, shadow DOM and crossorigin CSS; collapsed menus, off-canvas drawers, carousels and table-only overflow were false alarms; fixed bars were a miss. | **Kept (P2).** Screens keyed by a fingerprint (newest copy kept); copies serialised from the live DOM and loaded under their own URL; exemptions as listed in `human-factors-checks.md`; more than three boxes on one screen give one finding for the screen (game-desktop admin page, a desktop-only layout 813 px wide at 320: 9 findings → 1). |
| SM-06 at a step (2.4.11) | A validation error that scrolls a field under a sticky header. Review: it fired on user scrolls and pre-action snapshots. | **Kept (P2)** only for a focus the step moved. |
| SM-05 on mid-task screens (2.4.7) | The walks see only the first and last screens; dev-2 keys a mid-task control without a ring. Reviews and dev re-records found probe artefacts: a restored focus ring passing for click feedback, a mask over a whole focused container or a sibling group, Shift ignored by modality scripts, suggestion lists hidden by the pre-probe blur, pulsing buttons. | **Kept.** Probe before each click (≤ 16 per run): F24 key for modality, root attributes put back, three unfocused captures, previous ring masked only where it cannot cover the target, focus restored only where losing it changes the page, text fields blurred first only before a button and not from a field with suggestions, inconclusive when most of the target is masked, never overriding a walk that measured a ring. dev-2 clean SM-05 P2 ('답안 제출' next to '임시 저장'): 1 → 0. |
| LY-01 clipping by an ancestor, ACT 59br37 | dev-2 keys chips whose price is cut by a fixed-width label. 59br37 is defined at 640 × 512. | **Kept.** Clean cuts (59br37's exceptions: a nowrap line whose marker is drawn, a one-line-high box with the measured line height) are P3 truncation notes. ACT gate at 1920 and at 640 × 512: 0 false alarms on all seven rules; 59br37 detects 5/5 failed examples at 640 × 512 (2/5 at 1920); 2 notes on Passed examples 2 and 3. |
| GZ-02 new versus changed messages | dev-2 clean runs had P1 GZ-02 for messages that were already on screen and were scrolled away or re-texted. | Only messages with text, absent before, are new (P1/P2 off-screen); changed ones are P3; after an app scroll of ≥ half a screen the old tap point is not used. Clean P1 units 3 → 0. |
| low_vision stratum | dev-2 keys one defect conditioned on low vision (a quiz bar cut at magnification). Same recordings: no stratum 0.583, with it 0.611 (+1 defect, +1 clean P3 unit); placed before 70s+ and with touch-only strata skipped on pointer devices, one clean unit fewer. | **Adopted.** Reported as coverage of the condition, not prevalence. |
| Driver: screen capture | CDP clips are document coordinates: frames of scrolled pages showed the document top; downscaling clips moved the pan of wide pages and stopped inner-scroll gestures. | Fixed; flash validation re-run (33/33, then 36/36 with an oscillating-scroll page). |
| Driver: visual and DOM feedback | A blinking caret counted as feedback and typed characters did not; slow animations and no-op or root-attribute writes (a modality script after typing) passed for a response; a script filling the focused field did not count. | Caret masked; input events of text-like fields count; pixels moving before the input are left out; no-op writes and `<html>`/`<body>` attributes are not a response; a script's change of a field's `value` is. mobile-commerce clean CG-03 on an amount chip: gone. |
| GM-04 oscillating scroll | Review: page scroll that reverses direction was motion-matched away (ITC/Ofcom and ISO 9241-391 exempt smooth motion in one direction only). | More than 3 reversals within 1 s (after ≥ 4 CSS px of travel) are not motion. New validation page `scroll-shake.html`: fail 3/3 with the guard; 3.5 and 2.0 flashes/s (fail, pass) without it. |

Reviews: a pre-freeze review workflow (40 findings, 38 confirmed; all fixed or
documented as limits) and two further independent reviews of the fix range (one Opus, one Sonnet;
their high and medium findings fixed). Every fix has a driver self-test case that
fails on the code before it (243 cases). Final checks at `cf7310d`: Python tests
484, driver self-test 243/243, flash validation 36/36, ACT gate 0 false alarms at
1920 and 640 × 512.

Known limits kept (documented, not fixed before the freeze): modality scripts that
react only to Tab are not triggered by the probe (the walks use Tab); a layer that
takes focus and gives it back between two reads is not seen; layouts switched by
scripts (`matchMedia`) are not re-evaluated at 320 px; a toggled checkbox whose own
look never changes is judged by mutations and pixels only.

