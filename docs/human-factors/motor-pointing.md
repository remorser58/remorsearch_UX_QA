# Motor control & pointing ergonomics — research brief (`motor-pointing`)

최신 출처 검토는 [2026-10-02 갱신 기록](2026-10-02-research-update.md)에 있습니다.
이 문서에는 당시의 접근 제한과 잠정 주장을 보존합니다.

Prepared 2026-09-28 for the ergonomic persona-swarm QA (`ergoqa`). Scope: Fitts's law and FFitts/dual-Gaussian touch models, target size and spacing, touch offset bias, edge/corner effects, thumb reach as it affects pointing, the steering law, KLM-GOMS, gesture ergonomics, tremor/motor impairment, situational impairment, and accidental activation between adjacent actions.

## How to read this brief

**Evidence tags.** Each number is tagged with how it was checked.
- `[primary]`: I read the primary text myself. That means the PDF, the standard's source text, or platform source code.
- `[snippet]`: the value comes from search-engine excerpts of the primary source. Many publisher, university and W3C hosts were blocked by the egress proxy. Verify these before hard-coding them.
- `[derived]`: I computed the value here from a cited model. It is a model output, not an observation.
- `unconfirmed`: I could not verify the value. Do not use it as a threshold.

**Epistemic mapping to the repository's evidence bundle.**
- **Geometry** (DOM/UIAutomator boxes, device PPI) is `basis: measured` and `epistemic_status: observed`.
- **Model predictions** (Fitts, dual-Gaussian, KLM, reach) are `basis: model` and `epistemic_status: inferred`.
- A synthetic persona's predicted failure is a hypothesis about a situation. It is not evidence that real users fail at that rate.

**Severity policy used throughout.** The P0–P3 thresholds below are team-tunable policy anchored on the cited sources, not literature constants. The rules:
- A model prediction alone can reach P1 at most.
- P0 needs one of two things:
  - an observed blocking failure in a run, for example ≥3 consecutive failed attempts on a critical-path step (policy); or
  - a structural path to irreversible harm, for example a destructive action that fires on a single mis-tap with no confirmation or undo.

**Unit conversions.** Every size check needs these. Standards use CSS px, pt or dp. Research uses mm.

| Unit | Physical size | Source |
|---|---|---|
| Android dp | 1/160 in = 0.159 mm nominal | Android density definition. Real size varies because the density bucket ≠ the panel's actual xdpi. |
| iOS pt | ≈ 0.156 mm @2x/326 ppi, ≈ 0.166 mm @3x/460 ppi | [derived] from device PPI |
| CSS px | Angular reference unit (WCAG). ≈ 0.265 mm on a 96-dpi desktop at 100 % zoom. On phones, ≈ 1 dp/pt ≈ 0.16 mm. | — |

- Physical mm = `css_px × dpr × 25.4 / device_ppi`. `device_ppi` must come from the device catalog, not the density bucket.
- Implication `[derived]`: 24 CSS px ≈ 3.8–4.0 mm on a phone but ≈ 6.35 mm on a 96-dpi desktop. 44 pt ≈ 7.0–7.3 mm. 48 dp ≈ 7.6 mm nominal.

---

## 1. Summary

1. **Target size is the best-supported, most automatable motor check.** Standards set a floor: WCAG 2.2 SC 2.5.8 is 24×24 CSS px, or a 24-px spacing circle. Ergonomic evidence points much higher for touch:
   - platform guidance: 44 pt (Apple), 48 dp (Android), 7.5 mm (Windows);
   - research: 9.2–9.6 mm for one-handed thumb use (Parhi et al. 2006); 10 mm (Park & Han 2010); ≥18 mm for people with upper-body motor impairments (Findlater et al. 2017).
2. **The dual-Gaussian model (Bi & Zhai 2016) turns size into predicted tap success.** Model: σ² = α·W² + σa², with σx² = 0.0075·W² + 1.68 and σy² = 0.0108·W² + 1.33, in mm² `[snippet]`. A persona-specific σ inflation then gives persona-conditional risk.
   - A 24-CSS-px target on a phone (~3.8 mm square) has a predicted ≈74 % 2D success rate for young able-bodied adults `[derived]`.
   - So WCAG AA is legally meaningful but ergonomically weak for touch.
3. **Adjacent-action misfire can be computed.** Integrate the intended target's tap distribution over a neighbour's rectangle. For a 7 mm button abutting a 7 mm destructive button:
   - ≈0.7 % baseline misfire `[derived]`;
   - ≈4 % under a 1.4× σ inflation that approximates walking or encumbrance;
   - ≈0.3 % at 1.4× once there is a 2 mm gap.
4. **Edge effects are contested.** Parhi et al. (2006) say to extend right-edge targets to the edge for right-handers. Avrahami (2015) found edge proximity hurt reaction time. Yamanaka et al. (2023) found that a larger target–edge gap reduces time and errors. Yamanaka et al. (2026) found that success improves when the target touches the edge. The robust part: small non-zero gaps near edges are worst, and system-gesture insets steal edge swipes.
5. **Fitts, steering and KLM compare designs; they don't give pass/fail limits.** Mouse pointing throughput is ~3.7–4.9 bits/s (Soukoreff & MacKenzie 2004). Touch reached 6.95 bits/s in one study (MacKenzie 2015). An analogue-stick controller was 1.48 bits/s (Natapov et al. 2009). Constants are device- and population-specific. Use relative comparisons (flow A vs flow B, or before vs after), not universal limits.
6. **Gesture-only functionality is fully automatable and high-severity.** Checks cover WCAG 2.5.1 (path/multipoint gestures), 2.5.7 (dragging), 2.5.2 (down-event activation) and KWCAG 6.5.1/6.5.2. Dragging errors ran 10.8–17.3 % vs 3.5–4.0 % for pointing across mouse, tablet and trackball (MacKenzie, Sellen & Buxton 1991 `[primary]`).
7. **Persona dimensions with real base rates:**
   - handedness: Korea 5.8 % left + 7.9 % ambidextrous (survey of 2,437 Koreans, 2009); global best estimate 10.6 %;
   - grip: 49 % one-handed, 36 % cradled, 15 % two-handed, N=1,333, North America (Hoober 2013);
   - age: 20 % of Koreans are 65+ (Dec 2024);
   - essential tremor: 4.6 % of people ≥65 (pooled, global);
   - registered disability: 5.1 % of Koreans, 43 % of them physical (2024).
   Everything else (σ multipliers, Korean thumb length, Korean grip mix) is unconfirmed and should be treated as a scenario assumption.

---

## 2. Principles

### MP-01 Target size vs. standards (measured floor check)

**Statement.** An interactive target must meet the applicable minimum hit-region size, or the spacing exception. Minimums differ by platform and by standard.

**Parameters and sources**

| Source | Requirement | Context |
|---|---|---|
| WCAG 2.2 SC 2.5.8 (AA) | ≥ 24×24 CSS px. Exceptions: Spacing, Equivalent, Inline, User-agent control, Essential. Undersized targets pass if a 24-CSS-px circle centred on each bounding box intersects no other target and no other undersized target's circle. Size is independent of zoom. | Web, all pointers `[primary]` (W3C Understanding doc, via github.com/w3c/wcag) |
| WCAG 2.5.5 (AAA) | ≥ 44×44 CSS px (Equivalent, Inline, UA-control and Essential exceptions). Larger is recommended when a control is frequent, hard to undo, near a screen edge or part of a sequential task. | `[primary]` |
| Apple HIG, Accessibility | Default / minimum control size: iOS & iPadOS 44×44 / 28×28 pt; macOS 28×28 / 20×20 pt; tvOS 66×66 / 56×56 pt; visionOS 60×60 / 28×28 pt; watchOS 44×44 / 28×28 pt | `[primary]` (developer.apple.com JSON) |
| Apple HIG, Buttons | "a button needs a hit region of at least 44x44 pt — in visionOS, 60x60 pt" | `[primary]` |
| Android / Material | 48×48 dp touch target. Material: targets "separated by 8dp of space or more"; pointer targets 44×44 dp | Android docs `[primary]`; Material spacing & pointer `[snippet]` (m2.material.io) |
| Android Accessibility Test Framework, `TouchTargetSizeCheck` | 48 dp default; 32 dp for targets against the screen edge or inside an input-method (IME) container. Also considers `TouchDelegate` hit rectangles. | `[primary]` (GitHub source) |
| Microsoft Windows apps | 7.5 mm square (40×40 px at 135 PPI, scale 1.0). Error-consequential targets get more padding and sit further from the content edge. | `[primary]` (MicrosoftDocs) |
| Microsoft Win32 touch UX guide | 7×7 mm recommended minimum when a mistake is correctable in 1–2 gestures or under 5 s. 9×9 mm "when accuracy matters" (close, delete, severe consequences). 5×5 mm only when correctable in one gesture, with 2 mm padding. ≥ 5 px between targets. 6×6 mm cited as "research indicates" minimum; 10×10 mm for speed and comfort. | `[primary]` (MicrosoftDocs) |
| KWCAG 2.2 (KS X OT0003:2022) 6.1.3 조작 가능 | Diagonal ≥ 6.0 mm is "desirable" (바람직). Inner margin ≥ 1 px that does not react to the pointer. Note: 6.0 mm diagonal ≈ 4.24 mm square side `[derived]`. | `[primary]` (a11ykr/kwcag22) |
| KS X 3253:2016 (mobile app accessibility 2.0) | Controls ≥ 9 mm wide and ≥ 9 mm high regardless of screen size; centre-to-centre spacing when there is no visible border | `[snippet]` (webwatch.or.kr PDF blocked) |
| KS X 9211:2022 (kiosk accessibility) | Touch button gaps ≥ 2.5 mm | `[snippet]` |

**Research evidence behind the numbers**

| Study | Setting | Finding |
|---|---|---|
| Parhi, Karlson & Bederson 2006 `[primary]` | 20 right-handed adults aged 19–42, standing. PDA with 8.9 cm screen, 240×320 px, 0.24 mm dot pitch. Targets 3.8–13.4 mm. | Error rates did not differ statistically for targets ≥ 9.6 mm (discrete) or ≥ 7.7 mm (serial). Recommended 9.2 mm (discrete) and 9.6 mm (serial). For 9.6 mm targets, the box enclosing 95 % of hits at any location was 9.1×8.9 mm. |
| Park, Han, Park & Cho 2008 (MobileHCI); Park & Han 2010, IJIE 40(1) `[snippet]` | Korean (POSTECH) studies. Keys 4, 7, 10 mm × 25 locations. Touchscreen 5.3×7.1 cm, one-handed thumb. | 7 and 10 mm best for time; 10 mm alone best for errors and satisfaction. Recommendation: 10 mm. |
| Holz & Baudisch 2010 `[snippet]` | 2010-era hardware | Minimum target for 95 % success: 14.1 mm (capacitive baseline), 7.8 mm (Ridgepad per-user/posture correction), 4.3 mm (optical tracking). Most error is systematic, per user and per posture. |
| Findlater et al. 2017 `[snippet]` | 16 participants with upper-body motor impairments + 16 without | Motor-impaired participants made 3× more pointing errors on a touchscreen than with a mouse. Minimum touchscreen target updated to ≥ 18 mm. |
| NN/g (Budiu) `[snippet]` | Practitioner guidance | 1×1 cm minimum. Fingertip 1.6–2 cm wide; thumb contact ≈ 2.5 cm (MIT Touch Lab via NN/g). |

**Operationalization**

- **Inputs:**
  - per element: `box` (CSS px), `dpr`, `role`, `interactive`, `roles[]` (primary / destructive), and the effective hit rectangle (DOM box ∪ `TouchDelegate`/padding; on web, sample `elementFromPoint` on a 1-CSS-px grid to find the real hit region);
  - `device.ppi` and physical screen size from the catalog;
  - `platform`;
  - whether the target is inline text.
- **Algorithm:**
  1. Compute the largest axis-aligned square inside the hit region. For rectangles that is min(w, h). For rounded or irregular shapes, use grid sampling.
  2. Convert to pt/dp/mm.
  3. Apply the WCAG 2.5.8 spacing-circle test to undersized targets: circle radius 12 CSS px at the bounding-box centre, intersected against other targets and other circles.
  4. Evaluate every applicable standard; report each separately.
  5. axe-core ships a `target-size` rule (`minSize` 24, `target-offset` `minOffset` 24). It is disabled by default and returns "incomplete" for non-tabbable elements `[primary]`. Reuse it on web, but still run the physical-mm check.
- **Thresholds and severity:**
  - **P1:** a critical-path control (scenario `targets` marked critical, or roles `primary`/`destructive`) fails WCAG 2.5.8 after exceptions, or falls below the platform *minimum*: iOS 28 pt, Android 32 dp at an edge or 48 dp elsewhere per ATF, tvOS 56 pt.
  - **P2:** passes the floor but is below the platform *default* (44 pt / 48 dp / 7.5 mm), or below 9 mm when the persona grip is one-handed thumb, on a frequent or critical control.
  - **P3:** below the recommended size on an infrequent, non-critical, easily undone control.
  - Do not auto-assign P0 from size alone.
- **What can't be automated:** whether a target is "inline"; whether an "Equivalent" control exists and is equally discoverable; whether a target is "Essential" (map pins, dense data viz, legally mandated forms). A human or vision-LLM decides these, recorded as `basis: judgment`.

**Applicability.**
- Web: WCAG in CSS px. Mobile: also report mm.
- Mobile app: HIG, Android/ATF and KS X 3253.
- Desktop: HIG macOS 20/28 pt; Windows 40 epx / 7.5 mm for touch.
- Game (touch HUD): same as mobile.
- TV: tvOS 66/56 pt, or focus-based checks (MP-13).

**Validity limits.**
- Guideline minimums are consensus values, not dose–response thresholds.
- The research minima come from small lab samples:
  - Parhi: 20 right-handed participants, 17 of them men, on a 2006 PDA held one-handed while standing;
  - Park & Han: small Korean samples, 2008–2010 phones.
- None of these measure Korean older adults on modern 6–7" phones.

---

### MP-02 Predicted tap success (FFitts / dual-Gaussian model)

**Statement.** Finger-touch endpoints are the sum of two independent Gaussians. One is a speed–accuracy component that scales with target width; the other is an "absolute" finger imprecision component that does not (Bi, Li & Zhai 2013). Success probability can therefore be predicted from target size (Bi & Zhai 2016).

**Parameters**

- **FFitts law.** MT = a + b·log₂(A / √(2πe(σ² − σa²)) + 1). No consensus exists on how to estimate σa (independent task vs fitted) `[snippet]`.
- **Dual-Gaussian success model (Bi & Zhai 2016)** `[snippet]`.
  - Variance terms: σx² = 0.0075·Wx² + 1.68 and σy² = 0.0108·Wy² + 1.33 (mm, mm²). Absolute terms: σa,x ≈ 1.30 mm, σa,y ≈ 1.15 mm `[derived]`.
  - 1D success = erf(W / (2√2·σ)).
  - 2D rectangle ≈ product of the x and y terms, assuming independence and aiming at the centre.
  - Reported prediction error: < 5 % for 4.8 and 7.2 mm targets; < 10 % for 2.4 mm.
- **Replication (Yamanaka & Usuba 2024).** 2–8 mm bar targets in 0.2 mm steps, > 180 participants. Maximum prediction error 2.8 (horizontal bars) / 3.2 (vertical bars) percentage points `[snippet]`.
- **On-screen-start tasks.** Tap variance depends on movement distance A, so the original constants misfit; see Yamanaka & Usuba 2020 `[snippet]`.
- **Existing tooling.** The Tappy Figma plugin (Yamanaka et al. 2024) implements px→mm plus the dual-Gaussian model `[snippet]`.
- **Worked values `[derived]`** from the Bi & Zhai constants, square target, young able-bodied adults, lab:

| Square side W | 3.0 mm | 3.8 mm (≈24 CSS px on phone) | 5.0 mm | 6.0 mm | 7.0 mm (≈44 pt) | 7.6 mm (48 dp) | 9.0 mm | 9.6 mm |
|---|---|---|---|---|---|---|---|---|
| P(hit) 2D | 0.59 | 0.74 | 0.89 | 0.95 | 0.975 | 0.985 | 0.995 | 0.997 |

**Operationalization**

- **Inputs:**
  - target hit rectangle in mm (from MP-01);
  - persona `motor.touch_sigma_mm` for the absolute term (default ≈ 1.2–1.3 mm per the constants above; the current spec default of 1.5 mm is unsourced);
  - persona multipliers from MP-11 and MP-12.
- **Algorithm:**
  1. σ_x,persona² = (0.0075·W² + 1.68)·kx²; the same for y with its constants.
  2. P_hit = erf(Wx / (2√2σx)) · erf(Wy / (2√2σy)).
  3. Also Monte Carlo: sample N=10,000 taps and hit-test them against the real (possibly non-rectangular) hit region.
- **Thresholds (policy):**

| Severity | Condition |
|---|---|
| P1 | Critical-path P_hit < 0.90 for any sampled persona |
| P2 | Critical-path P_hit < 0.95, or frequent-control P_hit < 0.90 |
| P3 | P_hit < 0.97 on a frequent control |

- Aggregate across the swarm as "N of M personas below threshold". Never report it as a prevalence estimate.

**Applicability.**
- Touch surfaces: mobile app, mobile web, tablet, touch game HUDs, kiosks.
- Not valid for mouse or trackpad (use Fitts' effective width), controllers or remotes.

**Validity limits.**
- The model predicts population-average accuracy for young, able-bodied lab participants, mostly tapping with the index finger from an off-screen start. It does not predict individuals.
- Thumb, walking, older and impaired users are outside the fitted range. Multipliers are extrapolations.
- Edge-adjacent targets violate the symmetric-Gaussian assumption; see MP-05.

---

### MP-03 Spacing & accidental activation between adjacent actions (misfire risk)

**Statement.**
- Mis-taps land on neighbours.
- A destructive or irreversible action placed next to a frequent or primary action needs extra separation, extra size, confirmation or undo.
- The destructive action must never be the visually primary or default button.

**Parameters**

| Source | Guidance |
|---|---|
| WCAG 2.5.8 spacing circle | 24 CSS px diameter `[primary]` |
| Apple HIG `[primary]` | "about 12 points of padding around elements that include a bezel … about 24 points … without a bezel". "Don't assign the primary role to a button that performs a destructive action … people sometimes choose a primary button without reading it first." |
| Material | ≥ 8 dp between targets `[snippet]` |
| Microsoft Win32 `[primary]` | "clear physical separation between frequently used commands and destructive commands". ≥ 5 px between targets. 2 mm padding for 5 mm targets. Confirm risky commands initiated by touch. |
| Microsoft Windows apps `[primary]` | Error-consequential targets need more padding and distance from the content edge |
| KS X 9211 | Kiosk gaps ≥ 2.5 mm `[snippet]` |
| Jin, Plocher & Kiff 2007 | Older adults: spacing between 3.17 and 12.7 mm lowered errors `[snippet]`. Recommended button size unconfirmed. |

**Misfire estimates `[derived]`.** Horizontal neighbour of equal width, aim at centre, σ from the Bi & Zhai x-constants.

| W | σ multiplier | gap 0 mm | 1 mm | 2 mm | 4 mm |
|---|---|---|---|---|---|
| 4 mm | 1.0 | 6.8 % | 1.3 % | 0.14 % | ~0 |
| 4 mm | 1.4 | 14.3 % | 5.5 % | 1.7 % | 0.07 % |
| 7 mm | 1.0 | 0.72 % | 0.08 % | 0.01 % | ~0 |
| 7 mm | 1.4 | 4.0 % | 1.2 % | 0.30 % | 0.01 % |
| 7 mm | 2.0 (hypothetical impaired) | 11 % | 5.8 % | 2.7 % | 0.44 % |
| 9 mm | 1.4 | 1.7 % | 0.47 % | 0.11 % | ~0 |

**Operationalization**

- **Inputs:** hit rectangles in mm; `roles` (`primary`, `destructive`); whether the destructive action is reversible (undo toast, confirm dialog, trash). Get reversibility by actually triggering it in a sandboxed test account and observing the next snapshot, or from the scenario spec. Also the persona σ.
- **Algorithm:**
  1. For each ordered pair (intended A, neighbour B) within 3σ, compute P_misfire(A→B) = ∬_B N(center_A, diag(σx², σy²)). Use the closed form for axis-aligned rectangles, Monte Carlo otherwise.
  2. Risk = P_misfire × consequence weight, where irreversible destructive or money-moving = high, reversible = low.
  3. Also flag layout inversions: a destructive action styled as primary or default, or occupying the position where the primary action sits on the previous or next screen (a "position habit" trap across consecutive dialogs).
- **Thresholds and severity (policy):**

| Severity | Condition |
|---|---|
| P0 | B is irreversible destructive or payment, A is a frequent or critical action, B fires on a single tap with no confirmation or undo, and P_misfire ≥ 1 % for any persona. Rationale: a structural path to irreversible harm, per Win32 guidance. |
| P1 | Same pair with confirmation or undo present but P_misfire ≥ 5 %, or a destructive action with primary/default styling |
| P2 | P_misfire ≥ 1 % between any two actions with different outcomes |
| P3 | Spacing below the platform recommendation (8 dp / 12 pt) with no computed risk above 1 % |

- **What can't be automated:** whether the consequence is truly irreversible (server-side effects), and whether the visual hierarchy reads as primary to a user. Both need a vision-LLM or human judgment.

**Applicability.**
- All touch surfaces; kiosks especially.
- Desktop and mouse: use the same computation with mouse effective-width σ (much smaller).
- TV: not applicable to pointing, but apply the "default focus lands on destructive" check.
- Games: HUD buttons such as sell/discard next to use/equip.

**Validity limits.**
- Misfire estimates assume the user aims at A's centre with Gaussian error.
- Real error also includes cognitive slips (wrong target chosen), occlusion and habituation. The model does not capture these.

---

### MP-04 Pointer cancellation (activation on up-event)

**Statement.** Single-pointer functions should not execute on the down-event. At least one of these must hold:
- completion is on up-event with abort possible;
- an undo exists;
- the up-event reverses the down-event;
- down-event activation is essential.

**Sources.**
- WCAG 2.5.2 (A); JavaScript `click` is an implicit up-event `[primary]`.
- KWCAG 2.2 6.5.2 포인터 입력 취소 `[primary]`.
- Trewin, Keates & Moffatt 2006: motor-impaired mouse users "slip" between press and release and click accidentally at high velocity `[snippet]`.

**Operationalization.**
- **Web (Playwright/CDP):**
  1. Dispatch `pointerdown` on the target.
  2. Snapshot the DOM/URL/network.
  3. Move the pointer outside the target's box by ≥ 2× its size, then dispatch `pointerup`.
  4. If state changed at step 2, or the action fired despite the move-away, the check fails.
- **Android:** the same via UIAutomator swipe that starts on the target and ends off it. Check for side effects.
- **Severity:**
  - P1 if a critical or destructive action fires on down or cannot be aborted;
  - P0 if that action is irreversible or payment-related with no undo;
  - P2 for other functions.
- Games may legitimately use down-events (Essential exception). A human confirms.

**Applicability.**
- Web, mobile app, desktop: yes.
- Game: judgment.
- TV (button press): N/A.

**Validity limits.** Only checks the scripted abort path, not every gesture variant.

---

### MP-05 Edge & corner effects; system-gesture conflicts

**Statement.**
- Screen edges change touch accuracy in ways that depend on the gap between target and edge.
- Edges also host OS gestures that take priority over the app.

**Parameters (these conflict; report the range).**

| Source | Finding |
|---|---|
| Parhi et al. 2006 `[primary]` | Right-column hits fell right of centre and bottom-row hits fell above centre (right-handed, one-handed). Comfort was lowest at NW/SW (3.7/7) and highest at centre (5.7). Recommendation: extend right-edge targets to the edge for right-handers (left edge for left-handers). |
| Avrahami 2015 | Proximity to the edge had a significant negative effect on reaction time on touch devices, unlike mouse edge targets `[snippet]` |
| Yamanaka, Usuba & Sato 2023 (crowdsourced) | Increasing the target–edge gap decreased movement time *and* error rate. Earlier guidance recommended a 4 mm gap `[snippet]`. |
| Yamanaka et al. 2026 (CHI; Skewed Dual Normal Distribution) | Near edges the tap distribution skews: the peak shifts toward the edge. Success *improved* when the target touched the edge ("tap the target together with the edge"). The model predicts success for edge-adjacent 1D and 2D targets `[snippet]`. |
| Android ATF | Allows 32 dp at the screen edge vs 48 dp elsewhere `[primary]` |
| Android system gesture insets | "areas of the window where system gestures take priority over your app". Move or pad swipeable views away from them. Apps can request limited exclusion rects via `setSystemGestureExclusionRects` `[primary]`. |
| Apple HIG | "Avoid conflicting with gestures that access system UI". Games may defer system gestures `[primary]`. |
| Win32 | "Avoid placing small controls near the edge of the app or the display" `[primary]` |

**Operationalization.**
- **Inputs:** hit rectangles in mm; screen and safe-area/gesture insets (Android `WindowInsets.systemGestures()`, iOS safe area); element gesture type (tap, swipe, drag, from the scenario or a vision label).
- **Algorithm:**
  1. g = distance from hit rectangle to the nearest physical screen edge, in mm.
  2. Flag a small non-zero gap, 0 < g < 4 mm (policy, anchored on the prior 4 mm guidance), and combine with MP-02. The skewed model is not public in closed form here; until implemented, treat edge targets with an extra σ multiplier as a sensitivity run.
  3. Flag swipe/drag handles, carousels or sliders whose gesture start zone lies inside the system-gesture inset.
- **Severity:**
  - P1: a critical swipe or drag control inside a system-gesture inset. It is likely to trigger OS back/home instead, a repeated failure.
  - P2: a small (< platform default) critical target with 0 < g < 4 mm.
  - P3: same for a non-critical target.
- **What can't be automated:** whether an edge-touching design is intentional and helpful (Fitts-infinite edge on desktop). A human decides.

**Applicability.**
- Mobile app and web on phones: yes.
- Desktop mouse: edges are *beneficial* ("infinite width"), so invert the logic and do not flag.
- Game: HUD corners; allow deferred system gestures.
- TV: N/A.

**Validity limits.** Direct contradiction between 2015–2023 and 2026 results. The effect depends on case/bezel design and whether the target reaches the physical edge. Treat as P2/P3 only.

---

### MP-06 Thumb reach, grip and handedness as pointing modifiers

This overlaps with the grip/reach domain brief. Only the pointing-relevant parts are here.

**Statement.**
- In one-handed use, the thumb's functional area is limited and depends on hand size, device size and grip position.
- Reachability and accuracy degrade toward far corners.
- The difficult corners mirror for left-handers.

**Parameters.**
- **Bergstrom-Lehtovirta & Oulasvirta 2014.** Quadratic functional-area model predicted from surface size, hand size and index-finger position on the back; fitted on 20 participants `[snippet]`. Formula and coefficients not retrieved: unconfirmed.
- **Xiong & Muraki 2016.** Young (23.6 ± 1.8 y) vs older (67.5 ± 3.7 y) adults. Thumb coverage area did not grow as much as screen size. Older users and long-thumbed users had larger unreachable zones at the right and bottom `[snippet]`.
- **Parhi et al. 2006.** Comfort by region (see MP-05). Smallest-comfortable-size perception ranged from 6.0 mm (centre) to 7.7 mm (NW) `[primary]`.
- **Hoober target sizes by position.** ~7 mm centre, 11 mm top, 12 mm bottom `[snippet]`. This is practitioner book guidance from observational data, not peer-reviewed.
- **Trudeau et al. 2012.** Thumb performance varies by movement orientation, direction (CMC flexion/abduction vs extension/adduction) and device size; 20 right-handed participants `[snippet]`. Numeric throughput by direction: unconfirmed.

**Operationalization.**
- Build a persona reach map: a grid over the physical screen with `reach_difficulty ∈ [0, 1]`, mirrored for `one_hand_left`.
- For each critical or frequent target in a one-handed persona run:
  - multiply the MP-02 σ by a region factor (policy, calibrate later);
  - record whether a grip shift is required.
- **Severity:**
  - P2: a frequent primary action sits only in a hard-to-reach zone for a one-handed persona with `free_hands = 1`;
  - P1: a critical action is reachable only with two hands while the scenario context requires one hand and no alternative exists (e.g., no bottom-sheet duplicate).

**Applicability.**
- Phones: yes.
- Tablets: two-handed thumb zones at the lateral edges.
- Handheld consoles and landscape mobile games: two thumbs.
- Desktop and TV: N/A.

**Validity limits.**
- The model is only as good as the unretrieved coefficients.
- Korean hand anthropometry is not retrieved. Jee et al. 2016 report Korean hands as wider with shorter fingers than eight other nations `[snippet]`.
- Grip shifts are frequent in real use (Eardley et al. 2017; Hoober 2013), so reach maps are one state among many.

---

### MP-07 Fitts's law (Shannon form): pointing cost and throughput

**Statement.** Pointing time rises with ID = log₂(A/W + 1). Performance should be compared with effective width (We = 4.133·SDx) and throughput TP = IDe / MT (MacKenzie 1992; Soukoreff & MacKenzie 2004; ISO 9241-9 → ISO/TS 9241-411:2012).

**Parameters (device-specific; never mix)**

| Device / study | Result | Tag |
|---|---|---|
| Mouse, pointing (MacKenzie, Sellen & Buxton 1991) | MT = −107 + 223·ID ms, IP 4.5 bits/s, error 3.5 % | `[primary]` |
| Stylus/tablet, same study | −55 + 204·ID ms, 4.9 bits/s | `[primary]` |
| Trackball, same study | 75 + 300·ID ms, 3.3 bits/s | `[primary]` |
| Dragging, same study | mouse 135 + 249·ID (4.0 bits/s, 10.8 % errors); tablet −27 + 276·ID (3.6 bits/s, 13.6 %); trackball −349 + 688·ID (1.5 bits/s, 17.3 %) | `[primary]` |
| Mouse across ISO-conforming studies (Soukoreff & MacKenzie 2004) | 3.7–4.9 bits/s | `[snippet]` |
| Mouse, Card, English & Burr 1978 | MT = 1.03 + 0.096·ID s, reported ~10.4 bits/s. Not comparable: different ID form, slope-reciprocal method. | `[primary]`, as cited in MSB 1991 |
| Finger touch (MacKenzie 2015) | 6.95 bits/s, ~50 % above the mouse | `[snippet]` |
| Game controllers (Natapov, Castellucci & MacKenzie 2009, ISO 9241-9, N=15) | Mouse 3.78 bits/s (3.53 % errors); Wii Remote IR 2.59 (10.2 %); Classic Controller analogue stick 1.48 (6.58 %) | `[snippet]` |
| FPS device study (search attribution: Zaranek et al., CHI EA 2014) | Mouse 4.73, touchpad 2.98, gyro 2.85, thumbstick 2.39 bits/s | `[snippet]`; attribution unconfirmed |

**Operationalization.**
- **Model use:**
  1. For each step in the scenario action trace, compute A (from the previous focus point or last tap to the target centre) and W (target extent along the approach vector, in mm or CSS px).
  2. Compute ID and predicted MT with device-appropriate constants.
  3. Sum per flow.
  4. Compare design alternatives: current vs proposed, or across personas and devices.
- **Measured use:** with real timestamps (Android `getevent`, CDP input events, or recorded human sessions), compute observed TP per persona or device. For a live human session, compare against the device-class band, e.g., mouse 3.7–4.9.
- **Thresholds (policy, relative only):**
  - P3: a frequent step's predicted MT exceeds the best alternative layout by > 25 %.
  - P2: a critical flow's summed predicted pointing time is ≥ 1 s longer than an existing alternative flow.
  - Do not report absolute "too slow" values.
- **Not automatable:** whether the flow order is logical (cognitive), which is outside Fitts.

**Applicability.**
- Desktop (mouse, trackpad): strong.
- Touch: prefer FFitts / MP-02 for accuracy. Fitts remains fine for relative time.
- Game: cursor pointing with a stick is modelled by Fitts with far lower TP. FPS aiming is angular; Looser, Cockburn & Savage 2005 support Fitts for FPS aiming `[snippet]`.
- TV remote: D-pad focus is not Fitts; use KLM (MP-09).

**Validity limits.**
- Constants vary across devices, gain settings, populations and even task protocols.
- Negative intercepts occur.
- Fitts predicts error-free expert movement time for an average participant, not an individual.

---

### MP-08 Steering law: menus, sliders, cascading/hover paths

**Statement.** Moving through a constrained path of width W and length A takes T = a + b·(A/W) (Accot & Zhai 1997). Cascading pull-down menus combine Fitts and steering. Adding "force fields" cut selection time by 18 % on average with mouse, trackpoint and touchpad (Ahlström 2005) `[snippet]`.

**Parameters.**
- a and b must be calibrated per device. No universal constants were retrieved (unconfirmed).
- Findlater et al. 2013 measured pointing, dragging, crossing and steering in older vs younger adults. Touch cut older adults' movement time by 35 % vs mouse, against 16 % for younger adults `[snippet]`.
- Older adults do better with linear hierarchical navigation than with mixed hierarchies `[snippet]`, a low-confidence secondary source.

**Operationalization.**
- **Cascading hover menus (desktop web and apps).**
  1. For each parent item that opens a submenu on hover, get tunnel width W (item height, CSS px) and the horizontal travel A to the submenu.
  2. Automated behaviour test: move the pointer on a straight diagonal from the parent item's centre to the first submenu item, sampling every 8 ms at realistic speed (policy: 500–1,500 CSS px/s).
  3. The check **fails** if the submenu closes or switches when the path crosses sibling items, meaning there is no hover-intent delay or "safe triangle".
  4. Report the steering index A/W.
  5. Severity: P2 for all users; P1 if the motor or tremor persona repeatedly fails (≥ 2 of 3 simulated trajectories with added jitter).
- **Sliders and range drags.**
  - Steering index = track length / thumb hit height.
  - Verify single-pointer alternatives (MP-10).
  - P2 if the thumb hit height is < 24 CSS px and the track is > 10× that; the policy ratio flags high-precision steering.
- **Hover-only menus on touch:** separate check. Hover has no touch equivalent, so the function is inaccessible: P1.

**Applicability.**
- Desktop web and apps: yes.
- Mobile: sliders, swipe-to-confirm, drawing.
- Games: path-following mini-games; judgment.
- TV: N/A.

**Validity limits.**
- The law holds for constant-width tunnels at expert steady state.
- Jitter-based "tremor simulation" is a heuristic, not a validated tremor model.

---

### MP-09 KLM-GOMS (and touch/TV adaptations): execution-time estimates

**Statement.** Predict error-free expert execution time by summing operator times (Card, Moran & Newell 1980; Kieras).

**Parameters.**
- **Desktop KLM** `[snippet]` (Kieras' KLM guide):
  - K = 0.28 s for an average non-secretarial typist; range 0.12–1.2 s;
  - P (mouse point) = 1.1 s average; range 0.8–1.5 s. Better: replace with Fitts per MP-07;
  - B (button press or release) = 0.1 s;
  - H (hand homing) = 0.4 s;
  - M (mental preparation) = 1.35 s. Some later sources use 1.2 s; unconfirmed here.
  - Place M with Card, Moran & Newell's heuristic rules.
- **Touch adaptations:**
  - El Batran & Dunlop 2014: 51 users, 3,090 observations. ≈ 70 ms short untargeted swipe, ≈ 200 ms half-screen zoom, ≈ 80 ms icon pointing from home position `[snippet]`. These are movement-only values; add M separately.
  - Rice & Lartigue 2014 (Touch-Level Model): operators for distraction, gesture, pinch, zoom, tap, swipe, tilt, rotate, drag. Values unconfirmed.
  - Holleis et al. 2007: mobile-phone operator set, including attention shifts and distraction. Values unconfirmed.
- **TV and D-pad:** no validated per-press constant retrieved. Model each D-pad press as K plus the system response R (measured). Android TV guidance: "minimal number of clicks", "fewest screens" `[primary]`.

**Operationalization.**
- **Inputs:** the scenario action trace (`tap`, `type`, `swipe`, `key`, `dpad`, `wait`) and measured system response times from run timestamps (R = time from input to the next stable snapshot).
- **Algorithm:**
  1. Map each action to operators; use Fitts for P where geometry is known.
  2. Insert M by rule.
  3. Sum per flow. Also report counts: taps, keypresses, D-pad presses, M count.
  4. For TV: compute the shortest D-pad path between frequently used targets on the focus graph. Build the graph by pressing arrows from each focusable element and recording the resulting focus.
- **Thresholds (policy, relative):**
  - P3: a flow ≥ 20 % slower than a competitor or previous version.
  - P2: a critical flow ≥ 50 % slower, or a TV critical action needing > 10 D-pad presses from the landing focus (policy) with no shortcut.
  - P1: a focus trap or unreachable focusable element (focus-graph check). This makes the function inaccessible.
- **Not automatable:** where real users hesitate (M placement is heuristic), and novice exploration time.

**Applicability.**
- Desktop and web: strong.
- Mobile: touch adaptations, with low confidence in constants.
- TV: press-count and focus-graph checks are robust even without time constants.
- Game menus: yes. Gameplay: no.

**Validity limits.** KLM covers skilled, error-free execution only. It excludes errors, learning, fatigue and search. The widely quoted accuracy (~±20 %) is unconfirmed here.

---

### MP-10 Gesture ergonomics: gesture-only functions, timing and distance

**Statement.**
- Every function operable by a path-based or multipoint gesture must also be operable by a single pointer without a path, unless the gesture is essential (WCAG 2.5.1 A; KWCAG 6.5.1).
- Every dragging function needs a single-pointer, non-drag alternative (WCAG 2.5.7 AA). A text input counts; keyboard alone does not.
- Custom gestures must not be the only way to perform an important action (Apple HIG).

**Parameters (platform defaults for recognisers).**

| Platform | Parameter | Value | Tag |
|---|---|---|---|
| Android (AOSP `ViewConfiguration`) | Long-press timeout | 400 ms | `[primary]` |
| | Double-tap timeout | 300 ms (min 40 ms) | `[primary]` |
| | Tap timeout | 100 ms | `[primary]` |
| | Touch slop | 8 dp | `[primary]` |
| | Paging slop | 16 dp | `[primary]` |
| | Double-tap slop | 100 dp | `[primary]` |
| | Minimum fling | 50 dp/s | `[primary]` |
| | Maximum fling | 8,000 dp/s | `[primary]` |
| | Edge slop | 12 dp | `[primary]` |
| | Minimum scaling span | 27 mm (`config_minScalingSpan`) | `[primary]` |
| iOS (`UILongPressGestureRecognizer`) | Minimum press duration | 0.5 s | `[primary]` |
| | Allowable movement | 10 pt | `[primary]` |

**Evidence on difficulty.**
- Dragging errors 10.8–17.3 % vs 3.5–4.0 % for pointing (MacKenzie, Sellen & Buxton 1991) `[primary]`.
- Older adults have difficulty distinguishing gestures and knowing how long to press. They were more accurate at drag-and-drop with a pen than a finger (Motti et al., 24 participants aged 65–86) `[snippet]`.
- Findlater et al. 2017: motor-impaired participants showed high rates of spurious touches `[snippet]`.

**Operationalization.**
- **Detection.** From the scenario or trace, any step whose action is `swipe`, `drag`, `pinch`, `long_press`, `multi_touch` or `double_tap` is a gesture step. For each:
  1. Search the same snapshot for an alternative. Examples: a visible control whose accessible name matches the function ("삭제", "다음", "확대"), a track-tap on sliders, a text input. Then try it.
  2. **Verify the alternative by actually running it** (single tap, no path) and comparing the resulting state with the gesture's result.
- **Timing and distance** (compare with platform defaults above):
  - custom long-press < 400 ms (Android) or < 0.5 s (iOS): accidental-activation risk, P3/P2;
  - any required hold > 2 s with no toggle alternative: P2 (policy; XAG 107 flags hold duration as a barrier `[snippet]`);
  - required drag length in mm longer than the persona's reach envelope (MP-06): P2.
- **Severity:**
  - P1: a gesture-only function (no working alternative);
  - P0: the gesture-only function is on a critical path (login, payment, consent, emergency) and the scenario cannot be completed by the single-pointer persona;
  - P2: an alternative exists but is hidden (menu or long-press only) or takes ≥ 3 extra steps (policy).
- **Not automatable:** whether the path gesture is "essential" (signature, drawing, game mechanic), and whether the alternative is discoverable. Judgment.

**Applicability.**
- Web: WCAG.
- Mobile app: KWCAG/KS X 3253 and platform.
- Desktop: drag-and-drop alternatives.
- Game: gestures are often essential mechanics. Apply GAG/XAG instead: remap, simplify, and avoid button mashing and QTEs, or allow skipping them `[snippet]`.
- TV: N/A (D-pad).

**Validity limits.** Platform defaults are recogniser settings, not ergonomic optima. Users can change them (e.g., accessibility touch-and-hold delay).

---

### MP-11 Situational impairment: walking, encumbrance, transit

**Statement.** Walking and carrying objects degrade touch accuracy. Users partly compensate by slowing down.

**Parameters.**

| Study | Finding | Tag |
|---|---|---|
| Bergstrom-Lehtovirta, Oulasvirta & Brewster 2011 | Users must reduce speed by 26 % from preferred walking speed (PWS) to maintain accuracy. Performance plateaus at 40–80 % PWS. Stable at 74 % PWS despite hand oscillation. | `[snippet]` |
| Ng, Brewster & Williamson 2014 | Walking at PWS with a bag in the dominant hand raised targeting error up to +112 % vs standing. Preferred-thumb targeting error 4.2 mm (+40 % vs unencumbered). Index-finger accuracy 48.1 % when encumbered. | `[snippet]` |
| Conradi, Busch & Alexander 2015 | Buttons 5, 8, 11, 14 mm. Misses M=18 (SD 21) standing vs M=47 (SD 56) walking. 5 mm differed from all other sizes. Walking had no effect on time on task. | `[snippet]` |
| Schildbach & Rukzio 2010 | 6.74, 8.18, 9.50 mm targets. Walking lengthened times, especially for small targets; workload rose. | `[snippet]` |

**Operationalization.**
- Re-run MP-02, MP-03 and MP-05 with a context multiplier on σ. Suggested *sensitivity* values:

| Context | σ multiplier | Basis |
|---|---|---|
| Seated / standing | 1.0 | — |
| Walking | 1.4 | Back-calculated from Conradi et al. 2015 (1.27–1.74 by baseline posture) `[derived]`. Ng et al.'s +40 % is the thumb error with a carried bag (encumbrance), not walking; it is the source of `encumbered` 1.4. Superseded values and the dev test: `situational-and-age-effects-on-touch.md` SIT-03, `decisions.md` round 8. |
| Walking + encumbered | 2.0 | Bounded by the +112 % figure. Assumption. |

- Report as "risk under walking assumption", `epistemic_status: inferred`.
- Severity: the same thresholds as MP-02/03 applied to the walking persona, capped at P1. Escalate only with observed failures from a real walking session.

**Applicability.**
- Mobile app and web: strong.
- Mobile games: yes.
- Kiosk: standing but not walking. Consider gloves and queue pressure (judgment).
- Desktop and TV: N/A.

**Validity limits.**
- The multipliers are my assumption built on the cited effect sizes. They are not fitted σ values.
- Treadmill and track studies differ from street walking.

---

### MP-12 Tremor, motor impairment and ageing

**Statement.**
- Older adults and people with tremor or upper-body motor impairments show larger touch scatter, spurious touches, slips during press-release, and difficulty with drag, hold and precise timing.
- Touch can still beat the mouse for speed.

**Parameters.**

| Study | Finding | Tag |
|---|---|---|
| Findlater et al. 2017 | 3× touchscreen pointing errors vs mouse for motor-impaired participants. Minimum target ≥ 18 mm. | `[snippet]` |
| Findlater et al. 2013 | Touch reduced movement time 35 % for older adults vs 16 % for younger (relative to mouse) and lowered errors | `[snippet]` |
| Sultana & Moffatt 2019 | Older adults made significantly more errors at all widths; errors rose disproportionately as size fell (16 older vs 16 younger) | `[snippet]` |
| Elderly smartphone thumb study (SpringerPlus 2016) | Faster fatigue and slower tapping on 3.0 mm vs 9.0 mm buttons. Minimise flexion–extension thumb movements. | `[snippet]` |
| Error rates for "shaky" participants | 16 % at 56 dp vs 10 % at 64 dp | `[snippet]`; attribution unconfirmed |
| Mott et al. 2016 | Motor-impaired users touch with the back or side of the hand, knuckles or multiple fingers. Template matching (Smart Touch) resolves the intended point. | `[snippet]` |
| Trewin, Keates & Moffatt 2006 | Slip-while-clicking, high-velocity accidental clicks and overlapping presses. Freezing the cursor during clicks helped. | `[snippet]` |
| Louis & Ferreira 2010 | Essential tremor pooled prevalence 4.6 % at age ≥ 65 (0.9 % all ages; range 0.8–20.5 % across studies) | `[snippet]` |

**Operationalization.**
- **Persona profile.**
  - `motor.tremor ∈ {none, mild, moderate}` maps to σ multipliers (assumption, unvalidated; sensitivity analysis only): mild 1.5, moderate 2.0–2.5.
  - `motor_impairment = upper_body` adds an absolute size check: critical targets < 18 mm → P2 finding tagged with the Findlater 2017 recommendation.
- **Behavioural checks.**
  - Pointer cancellation (MP-04).
  - Holds and long-press (MP-10).
  - Timeouts: any auto-dismiss or timed input < 20 s with no extend option belongs to the timing domain (WCAG 2.2.1), but flag it here if it interacts with motor steps.
  - Double-tap requirement → alternative required.
- **Simulated tremor jitter.** Add band-limited noise to scripted pointer paths (policy: 4–12 Hz). This frequency band is for essential/physiological tremor; amplitude is unconfirmed, so keep this exploratory. Use it to exercise hover menus (MP-08) and drag, not to estimate prevalence.

**Applicability.**
- All surfaces.
- Games: XAG 107 asks for remappable inputs, toggle instead of hold, adjustable sensitivity and dead zones, and no simultaneous-press-only actions `[snippet]`.

**Validity limits.**
- Impairments are heterogeneous. Findlater 2017 and Mott 2016 show individual strategies that no Gaussian model captures.
- Simulated personas must not be presented as representing disabled users. Findings are hypotheses for testing with real participants.

---

### MP-13 Non-touch pointing: controllers, remotes, mouse-less desktops

**Statement.**
- Cursor pointing with an analogue stick is far slower than a mouse.
- TV and console UIs should use focus navigation with large targets.
- Games should allow input remapping and avoid inputs that are rapid, repeated, held or simultaneous as the only option.

**Parameters.**
- Controller throughput (MP-07): stick 1.48 bits/s vs mouse 3.78 bits/s (Natapov et al. 2009).
- tvOS 66/56 pt `[primary]`.
- Android TV: the D-pad is the primary navigation; navigation must be predictable and reach all focusable elements `[primary]`.
- XAG 107 and Game Accessibility Guidelines (remap, avoid button mashing/QTEs or allow skipping, toggle vs hold) `[snippet]`.

**Operationalization.**
- **TV:**
  - focus-graph reachability — P1 for unreachable, P1 for traps;
  - press-count (MP-09);
  - focused-element size ≥ tvOS minimum — P2 if below 56 pt equivalent.
- **Games:**
  1. From the action trace, detect required repeated presses. Policy: > 5 presses/s sustained ≥ 2 s = a mash pattern.
  2. Detect required holds > 2 s and required chords.
  3. Check the settings menu for remap / toggle / skip options (vision-LLM reads the settings screens).
  4. Severity: P1 if a mandatory progression step requires mashing or a chord with no option; P2 if an option exists but is buried.
- **Virtual cursor in console or TV web:** use MP-01 with tvOS sizes and MP-07 with stick constants.

**Validity limits.** Throughput values come from small lab samples, 15 participants in Natapov. Mash and hold thresholds are policy.

---

### MP-14 Observed mis-tap and correction detection (from action traces)

**Statement.** Real or simulated runs reveal motor failures directly. Examples:
- a tap outside any target;
- a tap on the wrong adjacent element followed by back or undo;
- repeated taps on an unresponsive element.

**Operationalization.**
- **Inputs:** a timestamped action trace with points in CSS px and mm, plus pre/post snapshots.
- **Detect** (policy thresholds):
  - (a) a tap within 3σ of a target that hit nothing or hit a neighbour;
  - (b) a wrong-element activation followed within 5 s by back, undo or cancel;
  - (c) ≥ 3 taps within 1 s within ~10 mm ("rage tap"; industry notion, threshold unconfirmed).
- **Severity:**
  - P0: a critical step fails ≥ 3 consecutive times (observed blocking);
  - P1: repeated (≥ 2 personas or ≥ 2 sessions) wrong-neighbour activations on a critical step;
  - P2: single occurrences on a critical step;
  - P3: elsewhere.
- **Note:** Simulated agents tap exactly at computed points unless noise is injected. Only human sessions or sessions with noise-injected personas produce meaningful MP-14 data. Label simulated ones `inferred`.

---

## 3. Persona ergonomic profile dimensions (motor/pointing)

| Dimension | Values | Base rate (source) | Effect on testing |
|---|---|---|---|
| Handedness | right / left / mixed | Korea: 5.8 % left, 7.9 % ambidextrous (random survey of 2,437 Koreans, *Ergonomics* 52(11), 2009) `[snippet]`. Korea (Gallup Korea 2013, via a Korean GWAS paper): 8 % left in 20s, 2 % in 60s `[snippet]`. Global best estimate 10.6 % (range 9.3–18.1 % by criterion; Papadatou-Pastou et al. 2020) `[snippet]`. | Mirror reach maps and offset direction (Parhi: right-column rightward hits for right-handers). Mirror edge-extension advice. Guarantee ≥ 1 left-handed persona via stratified coverage regardless of base rate. |
| Grip / input posture | one_hand_right, one_hand_left, cradle (one hand holds, other points), two_thumbs, mouse, trackpad, gamepad, remote | 49 % one-handed, 36 % cradled, 15 % two-handed; of one-handed, 67 % right thumb / 33 % left (Hoober 2013; 1,333 street observations in North America) `[snippet]`. Korean grip distribution: unconfirmed. | Selects the σ model (thumb > index), reach map (MP-06) and which standard applies (touch vs pointer sizes). Grip shifts are common (Eardley et al. 2017), so run several grips. |
| Touch precision σ (absolute term) | numeric mm, x and y | Young able-bodied lab baseline σa,x ≈ 1.30 mm, σa,y ≈ 1.15 mm (from Bi & Zhai 2016 constants) `[snippet]/[derived]`. Korean population value: unconfirmed. | Drives MP-02, MP-03 and MP-05 probabilities. The current spec default of 1.5 mm has no source; replace with the pair above plus multipliers. |
| Tremor | none / mild / moderate | Essential tremor 4.6 % at ≥ 65, pooled global (Louis & Ferreira 2010) `[snippet]`. Korean rate: unconfirmed. | σ multiplier (assumption), jitter on hover and drag paths, pointer-cancellation emphasis. |
| Upper-body motor impairment | none / present | Korea 2024: 2,631,356 registered disabled people = 5.1 % of population; physical disability (지체) is 43 % of them; 55.3 % of registered disabled people are 65+ (MOHW 2025 release) `[snippet]` | ≥ 18 mm critical-target check (Findlater 2017), gesture-alternative checks, spurious-touch tolerance. |
| Age band | 10s … 70s+ | Korea: 65+ = 20 % of residents (10.24 M of 51 M), Dec 2024 (Ministry of the Interior and Safety) `[snippet]` | Older personas: larger σ (magnitude unconfirmed), unreachable right/bottom zones (Xiong & Muraki 2016), gesture confusion (Motti), and the touch-beats-mouse finding (Findlater 2013). |
| Hand / thumb size | percentile, thumb_length_mm | Parhi's US sample: thumb 99–125 mm (mean 115), hand width 75–97 mm (mean 88), N=20; their measurement definition differs from Size Korea `[primary]`. Korean hand dimensions (Size Korea; Jee et al. 2016 wider hands, shorter fingers) not retrieved: unconfirmed. | Reach map (MP-06). Keep as scenario assumption until Size Korea tables are pulled. |
| Mobility context | seated / standing / walking / walking+encumbered / transit | No Korean base rate: unconfirmed | σ multipliers 1.0 / 1.4 / 2.0 (assumptions from Ng et al. 2014), MP-11. |
| Input device | touch / mouse / trackpad / stylus / gamepad stick / IR remote / D-pad | Device TP bands in MP-07 | Selects Fitts constants, size standards, and focus vs pointer model. |
| Expertise | first_use / returning / expert | — | KLM (MP-09) applies to experts only. Add exploration time for first use (judgment). |
| Accessibility settings | touch-and-hold delay, pointer size, switch access | Unconfirmed | Changes recogniser thresholds (MP-10); test at least one non-default setting for motor personas. |

Base rates are for weighting and reporting coverage only. Findings from synthetic personas never imply that "X % of users fail". Report "N of M simulated profiles".

---

## 4. Non-automatable judgments (need human or vision-LLM, `basis: judgment`)

1. Whether a WCAG 2.5.8 exception applies: Inline, Equivalent, Essential (maps, data viz, legally mandated form layout), or User-agent default.
2. Whether a path or multipoint gesture is *essential* (signature, drawing, core game mechanic). Whether an alternative is discoverable, not merely present.
3. The consequence class of an action: truly irreversible? money-moving? server-side side effects? This sets MP-03/MP-04 severity. It can be partially automated in a sandbox account.
4. Visual hierarchy: does the destructive button *look* primary or default? Is the affordance of the hit region visible (a large hit area behind a tiny icon may still look untappable)?
5. Intentional edge-hugging vs accidental edge crowding (MP-05, contested evidence).
6. Real grip behaviour, grip shifts and occlusion by the hand. Simulation cannot see where the palm covers the screen; hand-occlusion rendering exists only as an approximation.
7. Real motor-impaired touch strategies (knuckles, multiple fingers, Mott 2016) and fatigue over a session.
8. Game feel: whether aim assist, dead zones or timing windows are fair. Whether a QTE is optional in practice.
9. Where M (mental) operators really fall for novices (MP-09).
10. Whether a "rage tap" reflects motor failure, latency, or a missing affordance (MP-14).

---

## 5. Contradictions and uncertainties

| Topic | Positions | Handling |
|---|---|---|
| Edge targets on touch | Parhi 2006: extend right-edge targets to the edge. Avrahami 2015: edge proximity hurts reaction time. Yamanaka 2023: a larger gap lowers time and errors (prior advice: 4 mm gap). Yamanaka 2026: touching the edge *improves* success; small gaps skew the distribution. | Flag only small non-zero gaps, at P2/P3. Treat 0-gap edge targets as neutral. Revisit when the Skewed Dual Normal model is implemented. |
| "How big is 48 dp?" | Material (snippet) says ≈ 9 mm. Nominal 48 dp = 7.62 mm (48/160 in) `[derived]`. | Always compute mm from actual device PPI. Never trust unit-to-mm claims. |
| Apple minimum | HIG Buttons: hit region "at least 44x44 pt" as a general rule. HIG Accessibility table: iOS minimum 28×28 pt, default 44×44. | < 28 pt = P1 (below stated minimum); 28–44 pt = P2/P3 by criticality. |
| Standards vs ergonomics | WCAG AA 24 CSS px ≈ 3.8 mm on phones → predicted 2D success ≈ 0.74 for young adults `[derived]`. Research recommends 9–10 mm (18 mm for motor-impaired). | Report compliance and ergonomic risk separately. Passing WCAG never implies ergonomic adequacy. |
| Korean standards | KWCAG 2.2: 6.0 mm diagonal (≈ 4.2 mm side), "desirable". KS X 3253: 9 mm × 9 mm `[snippet]`. KS X 9211 kiosk: gaps ≥ 2.5 mm `[snippet]`. | Cite the right standard per surface (web / app / kiosk). Verify KS X 3253 and 9211 text before using as hard gates. |
| KLM M operator | 1.35 s (Card, Moran & Newell) vs 1.2 s in some later sources (unconfirmed) | Use 1.35 s; report sensitivity. |
| Dual-Gaussian constants | Bi & Zhai 2016 (off-screen start, lab) vs Yamanaka & Usuba 2020 (on-screen start: distance matters) vs Yamanaka & Usuba 2024 (good fit, 2–8 mm) | Use Bi & Zhai for isolated taps. Flag sequential-flow predictions as lower confidence. Primary PDFs were not fetched (blocked); the constants come from multiple consistent snippets. |
| Henze et al. 2011 compensation gain | Snippet says touch offsets/errors reduced by ≈ 7.8 %. Which metric (offset vs error rate) is unconfirmed. | Cite qualitatively: "systematic skew exists; static compensation helps modestly". |
| Holz & Baudisch 2010 | 14.1 mm (capacitive, 95 %) came from 2010-era sensing and a simulated baseline | Do not use as a modern threshold. Use as evidence that error is largely systematic and per-user. |
| Situational and tremor σ multipliers | No source gives σ multipliers directly | All multipliers are declared assumptions for sensitivity analysis. |
| Korean base rates (grip, thumb length, walking use) | Not found | Scenario assumptions; stratified coverage, not base-rate weighting. |

---

## 6. Sources

Retrieval note: many hosts (dl.acm.org, w3.org, yorku.ca, researchgate, pmc, sciencedirect, university sites) were blocked by the egress proxy. W3C, AOSP, ATF, axe-core, Microsoft docs and KWCAG text were read from their GitHub sources. Apple HIG came from developer.apple.com JSON. Parhi 2006 and MacKenzie/Sellen/Buxton 1991 came from microsoft.com PDFs. Everything else relies on search snippets and is tagged `[snippet]` above.

**Standards and platform guidelines**
- W3C, Understanding SC 2.5.8 Target Size (Minimum), WCAG 2.2, 2023 — https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html (source: https://github.com/w3c/wcag)
- W3C, Understanding SC 2.5.5 Target Size (Enhanced) — https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html
- W3C, Understanding SC 2.5.1 Pointer Gestures — https://www.w3.org/WAI/WCAG22/Understanding/pointer-gestures.html
- W3C, Understanding SC 2.5.2 Pointer Cancellation — https://www.w3.org/WAI/WCAG22/Understanding/pointer-cancellation.html
- W3C, Understanding SC 2.5.7 Dragging Movements, 2023 — https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html
- Apple, Human Interface Guidelines — Accessibility (retrieved 2026-09-28) — https://developer.apple.com/design/human-interface-guidelines/accessibility
- Apple, HIG — Buttons — https://developer.apple.com/design/human-interface-guidelines/buttons
- Apple, HIG — Gestures — https://developer.apple.com/design/human-interface-guidelines/gestures
- Apple, UILongPressGestureRecognizer.minimumPressDuration / allowableMovement — https://developer.apple.com/documentation/uikit/uilongpressgesturerecognizer/minimumpressduration
- Android Developers, Make apps more accessible (48dp) — https://developer.android.com/guide/topics/ui/accessibility/apps
- AOSP, ViewConfiguration.java and core/res/values/config.xml (main) — https://github.com/aosp-mirror/platform_frameworks_base/blob/main/core/java/android/view/ViewConfiguration.java
- Google, Accessibility Test Framework for Android — TouchTargetSizeCheck — https://github.com/google/Accessibility-Test-Framework-for-Android
- Android Developers, Edge-to-edge / system gesture insets — https://developer.android.com/develop/ui/views/layout/edge-to-edge ; Gesture navigation — https://developer.android.com/develop/ui/views/touch-and-input/gestures/gesturenav
- Android Developers, Navigation on TV — https://developer.android.com/design/ui/tv/guides/foundations/navigation-on-tv
- Google, Material Design — Accessibility (touch targets) — https://m2.material.io/design/usability/accessibility.html
- Microsoft, Guidelines for touch targets (Windows apps) — https://learn.microsoft.com/en-us/windows/apps/develop/input/guidelines-for-targeting (source: MicrosoftDocs/windows-dev-docs)
- Microsoft, Win32 UX Guide — Touch — https://learn.microsoft.com/en-us/windows/win32/uxguide/inter-touch (source: MicrosoftDocs/win32)
- Deque, axe-core target-size / target-offset rules — https://github.com/dequelabs/axe-core
- KWCAG 2.2 (KS X OT0003:2022) 한국형 웹 콘텐츠 접근성 지침 2.2, 2022 — https://a11ykr.github.io/kwcag22/
- KS X 3253:2016 모바일 애플리케이션 콘텐츠 접근성 지침 2.0 — http://www.webwatch.or.kr/pds/(KS%20X%203253)%EB%AA%A8%EB%B0%94%EC%9D%BC%20%EC%95%A0%ED%94%8C%EB%A6%AC%EC%BC%80%EC%9D%B4%EC%85%98%20%EC%BD%98%ED%85%90%EC%B8%A0%20%EC%A0%91%EA%B7%BC%EC%84%B1%20%20%EC%A7%80%EC%B9%A8%202.0.pdf
- KS X 9211:2022 무인정보단말기 접근성 지침 — https://standard.go.kr/KSCI/standardIntro/getStandardSearchView.do?ksNo=KSX9211
- ISO/TS 9241-411:2012 Evaluation methods for the design of physical input devices — https://www.iso.org/standard/54106.html
- Microsoft, Xbox Accessibility Guideline 107: Input — https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/107
- Game Accessibility Guidelines (full list) — https://gameaccessibilityguidelines.com/full-list/

**Pointing models**
- MacKenzie, Fitts' law as a research and design tool in HCI, HCI 7, 1992 — https://www.yorku.ca/mack/hci1992.html
- Soukoreff & MacKenzie, Towards a standard for pointing device evaluation, IJHCS 61(6), 2004 — https://www.yorku.ca/mack/ijhcs2004.pdf
- MacKenzie, Sellen & Buxton, A comparison of input devices in elemental pointing and dragging tasks, CHI 1991 — https://www.microsoft.com/en-us/research/wp-content/uploads/2016/08/comparison-of-input-91.pdf
- MacKenzie & Soukoreff, Card, English, and Burr (1978) — 25 years later, CHI EA 2003 — https://www.yorku.ca/mack/chi03a.html
- MacKenzie, Fitts' throughput and the remarkable case of touch-based target selection, HCII 2015 — https://www.yorku.ca/mack/hcii2015a.html
- Bi, Li & Zhai, FFitts law: modeling finger touch with Fitts' law, CHI 2013 — https://dl.acm.org/doi/10.1145/2470654.2466180
- Bi & Zhai, Predicting finger-touch accuracy based on the dual Gaussian distribution model, UIST 2016 — https://dl.acm.org/doi/10.1145/2984511.2984546
- Yamanaka & Usuba, Rethinking the dual Gaussian distribution model… on-screen-start pointing, ISS 2020 — https://doi.org/10.1145/3427333
- Yamanaka & Usuba, 0.2-mm-step verification of the dual Gaussian distribution model, PACM HCI (ISS) 2024 — https://dl.acm.org/doi/10.1145/3698153
- Yamanaka et al., Tappy plugin for Figma, 2024 — https://arxiv.org/abs/2411.00381
- Accot & Zhai, Beyond Fitts' law: models for trajectory-based HCI tasks, CHI 1997 — https://research.cs.vt.edu/ns/cs5724papers/2.humanperf.fitts.accot.beyondfitts.pdf
- Ahlström, Modeling and improving selection in cascading pull-down menus using Fitts' law, the steering law and force fields, CHI 2005 — https://dl.acm.org/doi/10.1145/1054972.1054982
- Card, Moran & Newell, The keystroke-level model for user performance time with interactive systems, CACM 1980 — https://dl.acm.org/doi/10.1145/358886.358895
- Kieras, Using the keystroke-level model to estimate execution times, 2001 — https://www.cs.umd.edu/~golbeck/INST631/KSM.pdf
- Holleis, Otto, Hussmann & Schmidt, Keystroke-level model for advanced mobile phone interaction, CHI 2007 — https://dl.acm.org/doi/10.1145/1240624.1240851
- El Batran & Dunlop, Enhancing KLM to fit touch screen mobile devices, MobileHCI 2014 — https://dl.acm.org/doi/10.1145/2628363.2628385
- Rice & Lartigue, Touch-level model (TLM), ACM SE 2014 — https://dl.acm.org/doi/10.1145/2638404.2638532

**Touch accuracy, size, offsets, edges**
- Parhi, Karlson & Bederson, Target size study for one-handed thumb use on small touchscreen devices, MobileHCI 2006 — https://www.microsoft.com/en-us/research/wp-content/uploads/2006/01/parhi-mobileHCI06.pdf
- Park, Han, Park & Cho, Touch key design for target selection on a mobile phone, MobileHCI 2008 — https://www.researchgate.net/publication/221270540_Touch_key_design_for_target_selection_on_a_mobile_phone
- Park & Han, Touch key design for one-handed thumb interaction with a mobile phone, IJIE 40(1), 2010 — https://www.sciencedirect.com/science/article/abs/pii/S0169814109001036
- Park & Han, One-handed thumb interaction of mobile devices from the input accuracy perspective, IJIE 40(6), 2010 — https://www.sciencedirect.com/science/article/abs/pii/S0169814110000806
- Henze, Rukzio & Boll, 100,000,000 taps, MobileHCI 2011 — https://dl.acm.org/doi/10.1145/2037373.2037395
- Holz & Baudisch, The generalized perceived input point model, CHI 2010 — https://www.christianholz.net/generalized_perceived_input_point_model.html
- Holz & Baudisch, Understanding touch, CHI 2011 — https://www.christianholz.net/2011-chi11-holz-baudisch-understanding_touch.pdf
- Weir, Rogers, Murray-Smith & Löchtefeld, A user-specific machine learning approach for improving touch accuracy, UIST 2012 — https://dl.acm.org/doi/10.1145/2380116.2380175
- Avrahami, The effect of edge targets on touch performance, CHI 2015 — https://dl.acm.org/doi/10.1145/2702123.2702439
- Yamanaka, Usuba & Sato, Clarifying the effect of edge targets in touch pointing through crowdsourced experiments, PACM HCI (ISS) 2023 — https://dl.acm.org/doi/10.1145/3626469
- Yamanaka et al., Skewed dual normal distribution model… targets near screen edges, CHI 2026 — https://dl.acm.org/doi/10.1145/3772318.3791183 (preprint https://arxiv.org/abs/2603.23865)
- Budiu (NN/g), Touch targets on touchscreens — https://www.nngroup.com/articles/touch-target-size/
- Hoober target sizes by screen position (summary), Smashing Magazine 2023 — https://www.smashingmagazine.com/2023/04/accessible-tap-target-sizes-rage-taps-clicks/

**Grip, reach, handedness**
- Hoober, How do users really hold mobile devices?, UXmatters 2013 — https://www.uxmatters.com/mt/archives/2013/02/how-do-users-really-hold-mobile-devices.php
- Bergstrom-Lehtovirta & Oulasvirta, Modeling the functional area of the thumb on mobile touchscreen surfaces, CHI 2014 — https://dl.acm.org/doi/10.1145/2556288.2557354
- Xiong & Muraki, Effects of age, thumb length and screen size on thumb movement coverage on smartphone touchscreens, IJIE 2016 — https://www.sciencedirect.com/science/article/abs/pii/S0169814115300512
- Trudeau, Udtamadilok, Karlson & Dennerlein, Thumb motor performance varies by movement orientation, direction, and device size, Human Factors 54, 2012 — https://doi.org/10.1177/0018720811423660
- Karlson, Bederson & Contreras-Vidal, Understanding one-handed use of mobile devices, 2006/2008 — https://www.irma-international.org/chapter/understanding-one-handed-use-mobile/21825/
- Eardley, Roudaut, Gill & Thompson, Understanding grip shifts, CHI 2017 — https://dl.acm.org/doi/10.1145/3025453.3025835
- Le, Mayer, Bader & Henze, Fingers' range and comfortable area for one-handed smartphone interaction, CHI 2018 (not retrieved) — https://dl.acm.org/doi/10.1145/3173574.3173605
- Jee et al., Anthropometric classification of human hand shapes in Korean population, HFES 2016 — https://journals.sagepub.com/doi/abs/10.1177/1541931213601281
- Papadatou-Pastou et al., Human handedness: a meta-analysis, Psychological Bulletin 2020 — https://research-information.bris.ac.uk/en/publications/human-handedness-a-meta-analysis/
- Hand dominance and hand use behaviour reported in a survey of 2437 Koreans, Ergonomics 52(11), 2009 — https://pubmed.ncbi.nlm.nih.gov/19851904/
- Song et al., Genome-wide association and replication studies for handedness in a Korean community-based cohort, Brain and Behavior 2023 (cites Gallup Korea 2013) — https://pmc.ncbi.nlm.nih.gov/articles/PMC10498080/

**Situational impairment**
- Bergstrom-Lehtovirta, Oulasvirta & Brewster, The effects of walking speed on target acquisition on a touchscreen interface, MobileHCI 2011 — https://scholar.google.com/scholar?q=The+effects+of+walking+speed+on+target+acquisition+on+a+touchscreen+interface
- Ng, Brewster & Williamson, Investigating the effects of encumbrance on one- and two-handed interactions with mobile devices, CHI 2014 — https://eprints.gla.ac.uk/117068/1/117068.pdf
- Schildbach & Rukzio, Investigating selection and reading performance on a mobile phone while walking, MobileHCI 2010 — https://dl.acm.org/doi/10.1145/1851600.1851619
- Conradi, Busch & Alexander, Optimal touch button size for the use of mobile devices while walking, Procedia Manufacturing 3, 2015 — https://www.sciencedirect.com/science/article/pii/S2351978915001833

**Ageing, tremor, motor impairment**
- Findlater, Froehlich, Fattal, Wobbrock & Dastyar, Age-related differences in performance with touchscreens compared to traditional mouse input, CHI 2013 — https://dl.acm.org/doi/10.1145/2470654.2470703
- Findlater et al. (full author list not verified here), Comparing touchscreen and mouse input performance by people with and without upper body motor impairments, CHI 2017 — https://dl.acm.org/doi/10.1145/3025453.3025603
- Mott, Vatavu, Kane & Wobbrock, Smart Touch, CHI 2016 — https://dl.acm.org/doi/10.1145/2858036.2858390
- Trewin, Keates & Moffatt, Developing steady clicks, ASSETS 2006 — https://courses.cs.washington.edu/courses/cse590w/06au/resources/p26-trewin.pdf
- Sultana & Moffatt, Effects of aging on small target selection with touch input, TACCESS 2019 — https://dl.acm.org/doi/10.1145/3300178
- Jin, Plocher & Kiff, Touch screen user interfaces for older adults: button size and spacing, UAHCI 2007 — https://link.springer.com/chapter/10.1007/978-3-540-73279-2_104
- Thumb performance of elderly users on smartphone touchscreen, SpringerPlus 2016 — https://springerplus.springeropen.com/articles/10.1186/s40064-016-2877-y
- Motti, Vigouroux & Gorce, Interaction techniques for older adults using touchscreen devices: a literature review, 2013 — https://savie.ca/BaseConnaissances/upload/pdf/3032_mottietal_2013_interaction_techniques_for_older_adults_using_touchscreen_Index3032.pdf
- Louis & Ferreira, How common is the most common adult movement disorder? Update on the worldwide prevalence of essential tremor, Movement Disorders 2010 — https://movementdisorders.onlinelibrary.wiley.com/doi/10.1002/mds.22838
- 보건복지부, 2024년 등록장애인 263만 1천 명, 전체 인구 대비 5.1%, 2025 — https://mohw.go.kr/board.es?act=view&bid=0027&list_no=1485363&mid=a10503010100
- Korea Times, Korea becomes 'super-aged' society as 20% of population are 65 or older, 2024-12-24 — https://www.koreatimes.co.kr/southkorea/society/20241224/korea-becomes-super-aged-society

**Games and controllers**
- Natapov, Castellucci & MacKenzie, ISO 9241-9 evaluation of video game controllers, GI 2009 — https://www.yorku.ca/mack/gi2009.html
- Zaranek, Ramoul, Yu, Yao & Teather, Performance of modern gaming input devices in first-person shooter target acquisition, CHI EA 2014 — https://dl.acm.org/doi/10.1145/2559206.2581291
- Looser, Cockburn & Savage, On the validity of using first-person shooters for Fitts' law studies, 2005 — https://www.csse.canterbury.ac.nz/andrew.cockburn/papers/julian_fitts.pdf
