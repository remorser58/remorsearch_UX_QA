# Handedness, Grip & Reach — research brief for an ergonomic persona-swarm QA

SLUG: `handedness-grip-reach` · Date: 2026-09-28 · Scope: phones (5–7"), tablets, foldables, web on mobile, desktop mouse/keyboard, landscape mobile games, physical game controllers, TV remotes.

## How to read this brief

**Evidence-access tags** (every number carries one):

- **[FT]**: full text was read at the time of writing.
- **[AB]**: only the abstract or search-engine snippet was available.
- **[2nd]**: taken from a secondary summary (blog, news, magazine) and less reliable.
- **UNCONFIRMED**: could not be verified. Do not hard-code it as fact.

Most publisher hosts (ACM DL, ScienceDirect, UXmatters, PMC, arXiv, NN/g, W3C, sizekorea.kr) were blocked by the egress proxy at the time of writing. Only microsoft.com (Parhi 2006 PDF), developer.apple.com (HIG JSON), developer.android.com and github.com could be fetched. Many values are therefore [AB] or [2nd]. The Bergstrom-Lehtovirta & Oulasvirta (2014) model coefficients, which are the most important missing piece, could **not** be read.

**Evidence rule for the QA system.** Every reach or grip finding in this domain is **inferred** from geometry plus a persona profile. It is never *observed*: an automation driver taps pixel-perfectly and has no thumb. The findings that count as **observed** are trace events such as mis-taps, repeated attempts, accidental system-gesture exits and unintended activations. Synthetic personas give coverage, not prevalence. The base rates below are literature context and must not be recomputed from persona counts.

---

## 1. Summary

1. **Grip is a distribution, not a constant.** Hoober's public-space observation study (n = 1,333, North America) found 49% one-handed, 36% cradled and 15% two-handed [Hoober2013, AB]. Among one-handed users, 67% used the right thumb and 33% the left [Hoober2013, AB]. People switch grips often [Hoober2017, 2nd]. The QA engine must therefore evaluate every screen under several grip models (one-thumb R, one-thumb L, cradled, two-thumb, on-surface), not one "thumb zone".
2. **The holding hand is not the same as handedness.** Korea has low left-handedness: 3.9–7% depending on survey, age and criterion. Yet left-hand phone operation is common: 33% of one-handed users in Hoober 2013, and 37% in a self-selected Korean community poll of 667 [Cetizen/FN 2014, 2nd]. **Mirror testing (left-hand grip) is therefore required even for a Korean audience.**
3. **The thumb's functional area is bounded and predictable in aggregate.** The functional area depends on hand size (finger span), device size and index-finger position on the back. Bergstrom-Lehtovirta & Oulasvirta (CHI 2014, n = 20) modelled it with quadratic (parabolic) boundaries, mean R² = .958 [BL2014, AB]. Two regions are consistently hard for a one-handed grip:
   - The **far-side top corner** (top-left for a right-hand grip).
   - The **grip-side bottom corner near the palm**: Trudeau 2014 found worst performance at the bottom-right for right-handers [AB], and Xiong & Muraki 2016 found more unreachable space at the right and bottom for long thumbs and older users [AB].
   The centre is best: in Parhi 2006 [FT] the centre scored 5.7/7 on comfort against 3.7/7 for the NW and SW cells.
4. **Big phones move the top band out of one-handed reach.** 2025 flagships are 70.5–77.6 mm wide and 147–163 mm tall. Platforms respond with Reachability (iOS), one-handed mode (Android 12+), Samsung One UI's "viewing area (top) / interaction area (bottom)" split, and bottom address bars (Safari since iOS 15; Chrome Android since 2025). These are **mitigations with an extra step**, not a pass.
5. **Target size must depend on position.** Parhi 2006 [FT] recommends 9.2 mm (discrete) and 9.6 mm (serial) for one-handed thumb use. Hoober reports about 7 mm at the centre versus 11–12 mm at the edges/corners [2nd]. Platform minimums are 44 pt (iOS), 48 dp ≈ 9 mm (Material), 24 CSS px (WCAG 2.5.8 AA) and a 6.0 mm diagonal (KWCAG 2.2 item 6.1.3).
6. **Other form factors translate reach into a different cost.**
   - Tablets and unfolded foldables: two-thumb side zones, or device set down [Hoober/ALA, 2nd].
   - Landscape games: left thumb for movement, right thumb for camera/actions, ≥44×44 pt frequent buttons [Apple HIG, FT].
   - Controllers: hand-size effects on ease of use [Brown & MacKenzie 2013, AB]; chords, holds and mashing as barriers [XAG 107, AB].
   - Desktop: mouse side and keyboard chords [Hoffmann 1997; Delisle 2004, AB].
   - TV: D-pad press count, safe areas of 60/80 pt, and 66/56 pt control sizes [Apple HIG, FT].
7. **A concrete, mirrored reach-difficulty algorithm is given in §4, with a sanity check.** Its geometric parameters are **UNCONFIRMED heuristics** and must be calibrated against B-L 2014 or new thumb-trace data before any P1 finding relies on them alone.

---

## 2. Shared conventions and inputs

### 2.1 Physical units (required for every check in this domain)

The conversion is:

```
mm_per_css_px = 25.4 * DPR / PPI          (web; DPR = devicePixelRatio)
mm_per_pt     = 25.4 * scale / PPI        (iOS; scale = 2 or 3)
mm_per_dp     = 25.4 * (densityDpi/160) / xdpi   (Android; use DisplayMetrics.xdpi/ydpi, not the nominal 160 dpi)
```

Worked example: iPhone 16 Pro Max, 2868×1320 px at 460 ppi, DPR 3 [dimensions.com, 2nd].
- 1 CSS px = 0.1657 mm.
- 44 px = 7.3 mm; 24 px = 4.0 mm.
- Active screen ≈ 72.9 × 158.4 mm; body 163 × 77.6 mm.

Device body and screen dimensions come from a **device table** maintained by the tool, because emulators expose pixels and not millimetres. Values used here:

| Device | Body | Source |
|---|---|---|
| iPhone 16 | 147.6 × 71.6 × 7.8 mm | [2nd] |
| Galaxy S25 | 146.9 × 70.5 × 7.2 mm | [2nd] |
| Galaxy S25 Ultra | 162.8 × 77.6 × 8.2 mm | [2nd] |
| iPhone 16 Pro Max | 163 × 77.6 mm | [2nd] |
| Z Fold7, folded | 158.4 × 72.8 × 8.9 mm | [2nd] |
| Z Fold7, unfolded | 158.4 × 143.2 × 4.2 mm | [2nd] |

**Web caveat.** An element's position *on the physical screen* equals its viewport position plus the browser-chrome offset, and the chrome moves: Safari's address bar is at the bottom by default since iOS 15, and Chrome Android offers a bottom bar since 2025. Calibrate the viewport origin from a full-device screenshot (for example `adb exec-out screencap`, or the iOS simulator screenshot) instead of assuming (0,0) is the screen top.

### 2.2 Coordinate frame and mirroring

- Origin is the top-left of the active screen, x to the right, y down, in mm.
- Compute everything in a **right-hand frame**. For a left-hand persona, set `x' = screen_w − x`, run the same code, and report under L.
- For RTL locales, mirror the UI and not the hand. Handedness and reading direction are independent axes; Material mirrors buttons for RTL [Material bidirectionality, AB].

### 2.3 Inputs the tool needs

- **Element geometry:** bounding boxes (CSS px, pt or dp) with role, label and actionability. Sources are the accessibility tree, uiautomator dump, XCUITest frames or the DOM.
- **Action trace:** each entry is `(t_ms, type ∈ {tap, long_press, swipe(start,end), key(code), chord([codes]), button(id, down/up)}, target_id, x, y)`.
- **Task model:** which elements are *critical* (task-completing, irreversible, safety), *frequent* (used on most steps), *occasional* or *rare*. An LLM proposes the labels; a human confirms them.
- **Device profile:** body mm, screen mm, screen offset in the body, PPI, DPR, OS navigation mode (gesture vs 3-button), whether Reachability or one-handed mode is available.
- **Persona ergonomic profile:** see §5.

---

## 3. Principles

### HGR-1. Grip mode is a context-dependent distribution. Evaluate the UI under several grip models.

**Statement.** People hold phones one-handed, cradled (one hand holds, the other hand's thumb or finger taps) or two-handed, and they shift between these within a session. No single "thumb zone" represents users.

**Parameters and sources**

- Hoober 2013: n = 1,333 observations in public places, several North American locations.
  - 49% one-handed, 36% cradled, 15% two-handed [Hoober2013, AB; location detail 2nd].
  - One-handed users: 67% right thumb, 33% left [AB].
  - The cradled breakdown (thumb vs finger, which hand) is UNCONFIRMED.
- Hoober 2017, UXmatters "Design for Fingers, Touch, and People", Part 2:
  - ~75% of touches by a single thumb; fewer than half hold one-handed; ~36% cradle; ~10% hold in one hand and tap with a finger [2nd].
  - A "41% two-thumb when typing" figure appeared in a summary; its context is UNCONFIRMED.
  - Grips change constantly [2nd].
- Tablets (Hoober, A List Apart "How We Hold Our Gadgets") [2nd]:
  - Large tablets are put down in ~2/3 of sessions: 40% flat, 22% in a stand.
  - 69% of small-tablet (7–8") use is handheld.
  - Phablet owners use both hands 70% of the time (Hoober & Shank).
- Two-handed grip performance (Trudeau et al. 2016, Applied Ergonomics) [AB]: Fitts effective index of performance +9%, movement time 7% faster and taps 4% more precise than one-handed; device-movement variability 36–63% lower.
- Grip postures by size (Choi et al. 2020, Applied Sciences; 45 participants, 9 mock-ups from 3.0 to 7.0") [AB]:
  - Dominant one-handed grips were L3-R1-K1 (index finger on the back) at 70.0%, L4-R1 at 13.3% and L3-R1-T1 at 12.0%.
  - Larger phones and larger hands increase L3-R1-K1.

**Operationalization**

1. Inputs: persona `grip_modes` probabilities per context (§5), device class, element boxes, task model.
2. For each screen and required action, compute the reach score (§4) under each grip model in the persona's set:
   - `one_thumb_R` and `one_thumb_L` use the §4 model.
   - `two_thumb` uses two pivots (HGR-9).
   - `cradle_*` and `on_surface` have no reach penalty; apply only target-size and occlusion checks.
3. Report the **worst grip the persona plausibly uses in the task context**, plus a grip-weighted expected cost `E[D] = Σ p(grip)·D(grip)`.
4. Severity is driven by the persona's most constrained plausible grip (see the §6 matrix), not by the expectation.

**Applicability.** Mobile app and mobile web: primary. Tablets and foldables: yes, with different models. Desktop, TV and consoles: not applicable; see HGR-12 to HGR-14.

**Validity limits.**
- The base rates are dated (2013–2017), mostly North American and observational, and they predate 6.7–6.9" phones.
- Korean grip base rates are UNCONFIRMED; no peer-reviewed Korean observation study was found.
- The rates describe populations, not individuals.

### HGR-2. The holding or operating hand is not the same as handedness. Always run the mirror (left-grip) test.

**Statement.** Many right-handers operate phones with the left hand, for example while the right hand is busy or when the left hand holds and the right hand taps. Left-hand operation is therefore far more common than left-handedness.

**Parameters and sources**

- Global left-handedness: best estimate 10.6%; range 9.3% (strict criterion) to 18.1% (non-right-handedness, lenient) [Papadatou-Pastou et al. 2020, Psychol Bull 146(6):481–524, AB].
- Sex difference: male-to-female odds ratio 1.23 (95% CI 1.19–1.27), from 144 studies and 1,787,629 participants [Papadatou-Pastou et al. 2008, AB].
- Korea (see §5 for the full table): 3.9% (KoGES cohort, aged 40–69) to 7% (Gallup Korea 2025, aged 13+), with 12–13% among teens and people in their 20s [2nd].
- Phone hand versus handedness:
  - Seidman et al. 2013, JAMA Otolaryngology, n = 717 online survey [AB]: right-handers held the phone to the right ear 68%, left ear 25%. Left-handers held it to the left ear 72%, right ear 23%.
  - Hoober 2013: 33% of one-handed operation used the left thumb [AB].
  - Nelavelli & Plötz 2018 (arXiv) summarize left one-handed interaction as 22–37% of observations [AB].
  - Korean community poll (Cetizen, 11–25 Aug 2014, 667 self-selected members): 63% right hand, 37% left hand for smartphone use [FN 2014, 2nd]. It is **not** a random sample.
- Platforms treat mirroring as first-class:
  - One-handed keyboards on iOS and Gboard offer both a left and a right mode [2nd how-to sources].
  - Parhi 2006 recommends that targets on the grip side extend to the edge, "right side for right-handed users (and left for left-handed people)" [FT].
- Automatic handedness detection is feasible: 98.51% accuracy classifying one- vs two-handed and left vs right unlocking from phone sensors [Löchtefeld et al. 2015, MUM, AB]. Adaptive layouts are therefore possible, and their absence is a *design choice*.

**Operationalization**

1. For every element with role ∈ {critical, frequent}, compute `D_R` and `D_L` (§4).
2. Compute asymmetry `A = D_L − D_R`.
3. Flag a **left-grip disadvantage** when `D_R` is natural or mild and `D_L` is stretch or out, or when `A ≥ 0.4`. The 0.4 is an UNCONFIRMED heuristic.
4. Flag the reverse (right-grip disadvantage) too. For example, a top-left back button is out of reach for R while a left-grip user can reach it along the grip edge on smaller phones.
5. Swipe-gesture variant: a required edge swipe (for example back-swipe from the left edge) starts at the far edge for R and the grip edge for L. Check whether any part of the start edge lies inside the reachable zone; iOS edge swipes can start low on the edge.
6. Severity follows §6. An asymmetry alone is at most **P2** unless the control is critical and has no alternative.

**Applicability.** Mobile app and web: primary. Tablets: two-thumb zones are symmetric, but single-hand-hold tablets have mirror effects. Landscape games: HUD mirroring (HGR-11). Desktop: mouse side (HGR-13). TV: largely not applicable.

**Validity limits.**
- Ear-side data are a proxy for phone laterality, not for touch-hand.
- The Hoober percentages are by observation, not per person.
- No Korean observational data on holding hand were found.

### HGR-3. One-handed thumb functional area: zones and a reach-difficulty score

**Statement.** With the device held in one hand, the thumb reaches a bounded region of the screen. The region is hardest at the far-side top and awkward right next to the thumb base (palm). Its size scales with hand size and shrinks relative to the screen as the device grows.

**Parameters and sources**

- Bergstrom-Lehtovirta & Oulasvirta 2014 (CHI) [AB; model details via secondary summaries]:
  - n = 20.
  - Inputs: hand size as finger span *s* (thumb tip to index tip), device surface size, and index-finger distance *d* from the device edge.
  - The functional area is bounded by a **parabolic/quadratic curve** whose range depends on *d*; mean R² = .958.
  - The model can also be used inversely to infer grips from a layout.
  - A blog reports that the test device was an iPhone 5c (124.4 × 59.2 mm) [2nd].
  - **Coefficients: UNCONFIRMED (paper not accessible here).**
- Parhi, Karlson & Bederson 2006 (MobileHCI) [FT]:
  - Setup: 20 right-handed participants (17 men, 3 women), aged 19–42, standing. HP iPAQ h4155 (71 × 114 mm body; 240 × 320 px screen, 0.24 mm pitch ≈ 57.6 × 76.8 mm). Thumb length 99–125 mm (μ 115, σ 5.75). Hand width 75–97 mm (μ 88).
  - All 9 regions of the 3×3 grid were tapped.
  - **Location had no significant effect on error rate** in discrete tasks.
  - Comfort: centre best (5.7/7); NW and SW worst (3.7/7).
  - Perceived required target size was largest at the NW, SW and SE corners (7.7, 7.6 and 7.5 mm) versus 6.0 mm at the centre.
- Trudeau et al. 2014 (PLoS ONE, "A Data-Driven Design Evaluation Tool for Handheld Device Soft Keyboards") [AB]:
  - For right-handed users, tapping at the top-right was associated with the best performance and the bottom-right corner with the lowest.
  - Movement toward the top-right was best and toward the bottom-right worst.
- Trudeau et al. 2012 (Human Factors 54:52–59; 20 right-handed participants, 4 phones) [AB]:
  - Index of performance was better on smaller devices.
  - Abduction/adduction movements performed better than flexion/extension.
- Karlson, Bederson & Contreras-Vidal 2006/2008 [AB]: NW–SE thumb movement is difficult for right-handers; NE–SW is better.
- Xiong & Muraki 2016 (IJIE; 48 right-handed participants) [AB]:
  - Elderly users and users with longer thumbs leave more unreachable space at the right side and bottom.
  - Coverage area increases with screen size, but not in proportion to it.
- Otten, Karn & Parsons 2013 (Human Factors; 90 participants in 3 groups) [2nd via Ergoweb]:
  - Method: hold securely, then sweep the thumb without changing grip; produces reach envelopes and heat-map grids.
  - Hand length: young fathers 192 ± 7.1 mm, young mothers 174 ± 7.1 mm, adolescent females 167 ± 12 mm.
  - Thumb length, fathers: 72.8 mm (as reported).
  - The maximum reach values themselves are UNCONFIRMED.
- Le, Mayer, Bader & Henze 2018 (CHI; Galaxy S3 mini, S4, OnePlus One, Nexus 6) [AB]: the grip shifts toward the top edge as phone size increases, and the comfortable areas of the back-of-device fingers shift linearly.
- A Korean usability study (KCI, "한 손 조작할 때 스마트폰 화면 크기 변화에 따른 사용성 평가") [AB]: one-handed use allowed diverse inputs at 3.5", but only limited inputs from 4.0" upward.

**Operationalization.** Compute the reach score `D ∈ [0,1]` for each element centre with the §4 algorithm. Zones:

| Zone | Score |
|---|---|
| natural | D = 0 |
| mild | 0 < D < 0.4 |
| stretch | 0.4 ≤ D < 1 |
| out of reach | D = 1: needs a grip shift, the second hand or OS reachability |

Thresholds for findings:

- **R-1:** a critical or frequent element whose centre is `out` for a one-thumb grip the persona plausibly uses.
- **R-2:** a frequent element in `stretch`.
- **R-3:** an element in the cramped zone (near the thumb base) that is smaller than the zone-specific minimum (HGR-7).

Severity follows §6.

**Applicability.** Phones: primary. Small tablets held in one hand: yes, but reach is mostly impossible, so treat as two-handed. Desktop and TV: not applicable.

**Validity limits.**
- These are aggregate models (B-L n = 20; Parhi n = 20, mostly men and US) and do not predict an individual.
- Most data were collected on devices of 3.5–6" and predate 6.7–6.9" phones.
- Grip varies with case, pop-socket, ring, phone weight and posture (standing, walking, lying down).
- The zone labels are **predictions of effort**, not of task failure. Parhi found no location effect on errors on a small device.

### HGR-4. Device size to reachable area: large phones push the top band out of one-handed reach

**Statement.** Reachable screen area grows much less than screen area. On 6.1–6.9" phones the top band, especially the far-side top corner, is not reachable without a grip shift for typical hands. Both the OS and design systems respond by moving interaction to the bottom.

**Parameters and sources**

- Average smartphone screen: 6.5" in 2023 versus 5.5" in 2018 [ScientiaMobile, 2nd].
- 2025 flagship widths: 70.5 mm (Galaxy S25), 71.6 mm (iPhone 16), 77.6 mm (iPhone 16 Pro Max and Galaxy S25 Ultra) [2nd].
- Grip comfort (Lee et al. 2019, Human Factors 61:90–104) [AB]:
  - A phone of 140 × 65 (or 70) × 8 mm with 2.5 mm edge roundness gave high grip comfort and design attractiveness; target mass 122 g, with 106–137 g comparable.
  - Hand length × phone width interaction was significant.
- Rear index-finger reach (Lee et al. 2016, Ergonomics) [AB]: at 90 mm width discomfort was 12.3% higher than at 60 mm; the small-hand group reported 11.9–18.2% higher discomfort.
- Platform responses:
  - iOS Reachability: swipe down on the bottom edge (Face ID models) to lower the top half [Apple Support, AB].
  - Android 12+ one-handed mode: swipe down near the bottom edge; requires gesture navigation, not 3-button [2nd].
  - Samsung One UI: the "viewing area" sits above the height a finger can most easily reach, and the "interaction area" below it holds frequently used controls, tabs and dialogs [One UI guide, AB]. The exact height is UNCONFIRMED.
  - Browsers: Safari moved the address bar to the bottom in iOS 15 [2nd]; Chrome Android added a bottom address-bar option in 2025 [TechCrunch, 2nd].
- Model illustration: §4.4 table (uncalibrated).

**Operationalization**

1. **Size-conditioned expectations.**
   - Screen height ≥ ~140 mm (≈6.1"+): expect the top ~20–30% to be `out` for L ≈ 115 mm under the §4 defaults.
   - Screen height ≤ ~80 mm (Parhi-class devices): expect nothing `out` for L ≥ 106 mm.
   - Both are model outputs, UNCONFIRMED.
2. **Check "top-anchored frequent controls on large phones."** Count frequent/critical controls that sit only in the top band (for example a hamburger menu, top-right close, top tabs, top-right "Next/Done"). For each, look for a reachable equivalent: a bottom bar, a pull-down gesture, a swipe-back from the grip edge, or keyboard Enter for forms.
3. **Reachability-mode compatibility.**
   - Positional constraint: none on iOS.
   - Android one-handed mode is unavailable under 3-button navigation, so treat `out` as harder for Android personas with 3-button navigation.
   - Time-limited interactions (timers, games) cannot use reachability gracefully; treat as no mitigation.

**Applicability.** Mobile app and web: yes. Foldables: the folded cover screen behaves like a phone (Fold7 cover 72.8 mm wide). Others: not applicable.

**Validity limits.**
- Pivot height, grip shift and case effects are uncalibrated.
- The One UI viewing/interaction boundary is a design convention, not an anthropometric measurement.

### HGR-5. The grip-side bottom corner near the palm is awkward (the "cramped" zone)

**Statement.** Targets very close to the thumb base force extreme flexion. This zone is slow and error-prone even though it is "near". Popular thumb-zone graphics often wrongly paint the whole bottom green.

**Parameters and sources**

- Trudeau 2014: bottom-right worst for right-handers [AB].
- Xiong & Muraki 2016 [AB]: more unreachable space at the right side and bottom for long thumbs and elderly users.
- Tablet pointing study ("Ergonomics of thumb-based pointing while holding tablets", MobileHCI 2016 adjunct) [AB]: targets very close to the palm need joints bent to their limit and take longer to select.
- Parhi 2006 [FT]:
  - The SE corner was among the regions where participants wanted larger targets (7.5 mm).
  - In the serial task, SE was the least comfortable keypad region (5.0/7).
- Trudeau 2014 (PLoS ONE) [AB]: the worst keyboard design placed the spacebar in the bottom-right corner (performance index 0.09 out of 2).

**Operationalization**

- Condition: the element is in the `mild` zone because ρ < ρ_near (§4), and its physical size is below the edge/corner minimum (HGR-7).
- Result: finding "small target in cramped zone". **P2** if the element is frequent; **P3** otherwise.
- The mirror applies: the bottom-left is cramped for left-grip personas.
- A common case: a bottom-right FAB or send button sits just inside the grip corner. It is usually large enough (56 dp FAB), so it only passes if its size is ≥ the corner minimum.

**Applicability.** Phones, one-thumb grip.

**Validity limits.** The ρ_near threshold is UNCONFIRMED. Edge proximity may *help* when the target touches the edge (HGR-7), so do not penalize edge-flush grip-side targets for accuracy.

### HGR-6. Movement direction and sequence cost: count grip shifts, and penalize flexion/extension (NW–SE) travel

**Statement.** In one-handed use, thumb movements along the flexion/extension axis are slower than abduction/adduction movements. For a right-hand grip that axis is roughly NW–SE (mirrored to NE–SW for the left hand). Alternating between far regions forces repeated grip shifts.

**Parameters and sources**

- Trudeau 2012: abduction/adduction beat flexion/extension [AB].
- Karlson 2008: NW–SE is difficult for right-handers [AB].
- Xiong & Muraki 2016 (SpringerPlus, elderly) [AB]: flexion–extension was slower; small buttons (3.0 mm) caused faster fatigue than 9.0 mm buttons.

**Operationalization**

- Input: the action trace, in order.
- For consecutive taps i → i+1:
  - Compute the vector in the right-hand frame (mirror x for L).
  - Direction class: `NW–SE` if the angle is within ±30° of the 135°/315° diagonal (for R). The ±30° band is UNCONFIRMED.
  - Distance in mm.
- Metrics per task:
  - (a) `grip_shifts` = number of transitions *into* an `out` element from a non-`out` element. Consecutive `out` taps share one shift.
  - (b) Share of the path length on the NW–SE axis.
  - (c) Count of top↔bottom alternations whose Δy exceeds 60% of the screen height. The 60% is UNCONFIRMED.
- Thresholds (UNCONFIRMED heuristics): `grip_shifts ≥ 2` in a single core task → **P2**; `grip_shifts ≥ 1` on *every* step of a repeated flow (for example per item in a list edit) → **P2**, escalating to **P1** when the persona is hard-one-handed.

**Applicability.** Phones. Tablets held in one hand: not recommended. Games: sequence cost matters for combos.

**Validity limits.** Direction effects were measured in lab reciprocal-tapping tasks. Transfer to real tasks is plausible but not quantified.

### HGR-7. Minimum target size depends on position: centre versus edges/corners, and grip-side edge-flush targets

**Statement.** Thumb touch accuracy is best at the centre and worse at the edges and corners, so required size grows away from the centre. Targets on the grip side should extend to the physical edge.

**Parameters and sources**

| Source | Value | Context |
|---|---|---|
| Parhi 2006 [FT] | Discrete 9.2 mm; serial ≥ 9.6 mm. The 95% hit box for 9.6 mm targets is 9.1 × 8.9 mm. | One-handed thumb; 20 right-handed, standing, PDA |
| Hoober 2017 (Part 3) [2nd] | ~7 mm at the centre; ~11 mm top; ~12 mm bottom/corners | Field-derived guideline |
| Park & Han 2010, IJIE 40(1):68–76 [AB] | Tested 4, 7 and 10 mm keys at 25 locations; success rate rose with size; central region fastest and most satisfying | One-handed right thumb (Korean authors; affiliation and sample not verified) |
| Apple HIG accessibility [FT] | iOS/iPadOS default 44×44 pt, minimum 28×28 pt. Spacing ~12 pt around bezelled and ~24 pt around bezel-less controls. macOS 28/20, tvOS 66/56, visionOS 60/28, watchOS 44/28 pt. | Platform guideline |
| Android dev [FT] / Material 3 [AB] | ≥ 48×48 dp (≈ 9 mm); 7–10 mm recommended | Platform guideline |
| WCAG 2.2 [AB] | 2.5.8 (AA): 24×24 CSS px, or a 24 px-diameter spacing circle. 2.5.5 (AAA): 44×44 CSS px | Web standard |
| KWCAG 2.2, item 6.1.3 [AB] | Control diagonal ≥ 6.0 mm; ≥ 1 px non-reactive inner margin recommended | Korean web standard |
| Yamanaka et al. 2026 (CHI) [AB] | Near an edge the tap distribution skews toward the edge; success improves when the target *touches* the edge | Touch pointing |
| Parhi 2006 [FT] | Rightmost-column hits leaned right, so grip-side targets should extend to the edge (mirror for left-handers) | One-handed thumb |

**Operationalization**

Physical size of an element = min(width, height) in mm (§2.1). Zone-dependent minimum:
- Centre third: 7 mm [Hoober, 2nd].
- Mid band: 9.2 mm [Parhi].
- Edges and corners (within one-sixth of the screen width or height of an edge): 11–12 mm [Hoober, 2nd].
- Serial-entry keys: ≥ 9.6 mm [Parhi].

Always also check the platform minimum (44 pt / 48 dp) and WCAG/KWCAG.

Severity:
- Below WCAG 2.5.8 (24 CSS px without spacing) or below KWCAG 6.0 mm on a critical control → **P1** (standards failure plus inaccessibility for motor-impaired users).
- Below the platform minimum on a frequent control → **P2**.
- Below the zone-dependent guideline only → **P3**, raised to **P2** if trace evidence shows mis-taps.

Grip-side edge-flush check: a grip-side target within 1–5 mm of the edge but not touching it gives a **P3** suggestion. The 1–5 mm band is UNCONFIRMED.

**Applicability.** Mobile app and web: yes. Tablets: platform minima apply. Desktop: pointer targets can be smaller per Android guidance, but WCAG still applies. TV: tvOS 66/56 pt.

**Validity limits.** Hoober's region values come from secondary summaries. Parhi's device was small, participants mostly male, and all stood. The 2006-era capacitive/resistive hardware differed from modern screens.

### HGR-8. The thumb and hand occlude content below and toward the grip side of the touch point

**Statement.** In one-handed right-thumb use, the thumb and hand hide screen content toward the bottom-right of the touch point. Feedback, validation messages or adjacent options placed there go unseen.

**Parameters and sources**

- Park & Han 2010 [AB]: buttons in the left region had fewer errors because they were less hidden by the right hand.
- Hoober 2017 heuristic: "People only tap what they see". Keep room around targets so users see state changes [2nd].

**Operationalization**

1. After a tap in the trace, detect newly appearing or changed UI (screenshot diff or DOM mutation) within 1 s.
2. Test whether that UI's bounding box intersects the *occlusion sector*: in the right-hand frame, the region from the touch point toward the pivot (down and grip-side). Default wedge: ±35° around the tap→pivot vector, up to the thumb length L. Both values are UNCONFIRMED.
3. Flag confirmations or errors that appear only inside the sector and disappear in less than 3 s (UNCONFIRMED): **P2** when the message is critical (error, irreversible action) and **P3** otherwise.
4. Run the check for both L and R.

**Applicability.** Mobile app and web, and tablets during direct touch. Not applicable to desktop mouse or TV.

**Validity limits.** The occlusion geometry is not quantified in the sources found here. A vision-LLM or human should confirm.

### HGR-9. Two-handed, tablet and foldable grips: side thumb zones and an unreachable centre

**Statement.** Handheld tablets and unfolded foldables are held with two hands, and thumbs reach only side bands near the grip points. Otherwise users set the device down and use an index finger.

**Parameters and sources**

- Wagner, Huot & Mackay 2012, CHI (BiTouch/BiPad) [AB]: five holds that allow simultaneous support and interaction; users change position to fight fatigue; thumbs outperformed fingers but were more tiring and less stable.
- Trudeau et al. 2013, PLoS ONE [AB]:
  - Typing speed: standard layout 127 ± 5 chars/min, split 113 ± 4.
  - Discomfort: portrait standard 2.9 ± 0.6, landscape standard 4.5 ± 0.7, landscape split 2.7 ± 0.6.
  - The split keyboard reduced thumb reach (range of motion, MCP extension).
- Odell & Chandrasekaran 2012, HFES [AB]: a method for tablet thumb-reach heat maps (anthropometric measure → grips → reach per group). The numbers are UNCONFIRMED.
- Tablet usage context: Hoober (see HGR-1) [2nd].
- Foldables:
  - Z Fold7 is 143.2 mm wide unfolded and 72.8 mm folded [2nd].
  - Open foldables feel heavier one-handed because of leverage [2nd review].
  - A single-handed folding study on a modified clamshell phone exists (CHI 2024) [AB].
  - Ergonomic grip research on foldables is sparse (UNCONFIRMED).

**Operationalization**

- **two_thumb model:** pivots at the left and right body edges at persona-specific heights (defaults as §4, mirrored). `D = min(D_left_thumb, D_right_thumb)`.
- Flag frequent controls in the central band that neither thumb reaches (`out` for both) when the persona context is handheld tablet or unfolded foldable. **P2** by default; **P3** if the task is normally done with the device set down (reading, video).
- **Split-keyboard check:** in landscape two-thumb text-entry flows on tablets, if the app forces a full-width custom keyboard with no split option, raise **P3** (with Trudeau 2013 as context).
- **Foldable state check:** re-evaluate every screen after a fold or unfold. Confirm that critical controls keep a reachable instance in both states and that state changes preserve task state. Continuity is covered by another domain; here only reachability is checked.

**Applicability.** Tablets, foldables, and landscape phones (games, video).

**Validity limits.** Tablet reach numbers are UNCONFIRMED. The model assumes a symmetric grip, but real grips often have one hand supporting and one tapping (cradled).

### HGR-10. OS reachability features and bottom anchoring are mitigations. Do not count them as a pass.

**Statement.** System reachability features lower the top of the screen at the cost of an extra gesture. They mitigate out-of-reach controls but do not remove the cost.

**Parameters and sources.** Apple Support "Reach the top of the iPhone screen with one hand" [AB]; Android 12 one-handed mode [2nd]; Samsung One UI viewing/interaction areas [AB]; Safari and Chrome bottom address bars [2nd].

**Operationalization.** If the only access to a frequent or critical control is out-of-reach and the persona `uses_os_reachability = true`, downgrade severity by one level but add +1 step per use to the task's step count. Unknown usage means no downgrade. Android with 3-button navigation means no downgrade.

**Applicability.** Phones only.

**Validity limits.** No usage-rate data for Reachability or one-handed mode were found (UNCONFIRMED).

### HGR-11. Landscape mobile games: virtual joystick, action buttons and HUD handedness

**Statement.** In landscape, both thumbs work from the side edges. Movement conventionally goes on the left and camera/actions on the right. Frequent actions must sit near the thumbs, large enough and clear of system-gesture areas. Left-handed players need mirroring or HUD customization.

**Parameters and sources**

- Apple HIG, Game controls [FT]:
  - "Place frequently used buttons near a player's thumb, avoiding the circular regions where players expect movement and camera input."
  - Place secondary controls such as menus at the top.
  - Avoid overlapping the Home indicator and Dynamic Island.
  - Frequent controls ≥ 44×44 pt; less important controls ≥ 28×28 pt.
  - Movement on the left, camera on the right. Prefer a floating thumbstick where the thumb lands, and direct-touch camera panning.
- Baldauf et al. 2015, ACM TOMM (four on-screen gamepads) [AB]: directional buttons need the most attention but are precise for direction-restricted tasks; the floating joystick reduces glances at the device; tilt was not precise or fast enough.
- Large-scale virtual-joystick study (MIG 2023) [AB]: touch patterns on the joystick varied across players, but performance was not significantly affected.

**Operationalization**

- Inputs: HUD element boxes in landscape (vision detection when the game renders to a canvas), device safe-area insets, and a touch trace.
- Checks:
  - (a) Frequent action buttons are ≥ 44 pt, menus ≥ 28 pt. A violation is **P2**, or **P1** if the trace shows repeated misses.
  - (b) A HUD button overlapping the system-gesture or safe-area inset → **P1** (accidental exits are observable in the trace as app-backgrounding events).
  - (c) The distance from each action button to the right-thumb pivot is ≤ the stretch radius under the two-thumb model (§4, landscape pivots).
  - (d) A fixed joystick placed where small-hand personas' thumbs rest outside its activation area → **P3**.
  - (e) Left-handed support: a vision-LLM inspects settings for a mirror or HUD-layout editor. Absence is **P3** by default and **P2** for competitive real-time genres. This severity mapping is an UNCONFIRMED heuristic.

**Applicability.** Mobile games. Also tablet games.

**Validity limits.** The HIG is a guideline, not experimental data. No peer-reviewed data on left-handed HUD usage rates were found.

### HGR-12. Physical game controllers: hand size, chords, holds, mashing and remapping

**Statement.** Controller usability depends on hand size. Mechanics that need simultaneous buttons, long holds or rapid repeats exclude players with small hands, one hand or limited endurance. Remapping is the baseline mitigation.

**Parameters and sources**

- Brown & MacKenzie 2013, MHCI (n = 13; Xbox 360, PS3 and Wii Remote + Nunchuk) [AB]: hand size had a significant relationship with ease of use across all controllers; larger hands operated more controls easily; preference did not relate to hand size.
- Xbox Accessibility Guideline 107 (Input) [AB]:
  - Offer full in-game remapping.
  - Let a simultaneous-press action be remapped to a single button.
  - Provide alternatives to long holds (for example holding RT to accelerate) and to repeated presses.
- Game Accessibility Guidelines [AB]: remappable controls are **basic**; one-handed control options are **intermediate**; avoid repeated inputs and QTEs.
- Apple HIG default controller mapping [FT]: A activates, B cancels/back, Menu opens settings/pause, Home is reserved.
- Excluded: specific controller-dimension claims found in search, such as "68 mm stick spacing" and "+67% EMG", came from unverifiable blog content.

**Operationalization (from a controller action trace)**

- **Chord detection:** ≥ 2 distinct buttons down within a 100 ms window (UNCONFIRMED threshold) that is required to progress.
- **Hold detection:** one button held longer than 2 s (UNCONFIRMED) as a requirement.
- **Mashing:** more than 5 presses per second (UNCONFIRMED) required.
- **Remap availability:** a vision-LLM inspects the settings menu.

Severity:
- A required chord, hold or mash with no remap or toggle alternative in the critical path → **P1** for a persona with `needs_one_handed_controls`, **P2** otherwise.
- No remapping at all → **P2**.
- Non-standard A/B semantics in menus (for example B confirms) → **P3**. Regional conventions may differ (UNCONFIRMED for Korea).

**Applicability.** Console and PC games with a controller.

**Validity limits.** Brown & MacKenzie had n = 13. The thresholds are heuristics that need calibration against play-testing.

### HGR-13. Desktop: mouse handedness, keyboard layout and one-handed shortcuts

**Statement.** Most workstations put the mouse on the right. Left-handers largely cope, but a right-side mouse beside a numeric keypad raises shoulder load. For software QA, the controllable issues are chords that need two hands, hard-coded "right-click" instructions, and drag-only interactions.

**Parameters and sources**

- Hoffmann, Chang & Yim 1997, Applied Ergonomics 28(4):245–248 [AB]: 100% of University of Melbourne student computers surveyed had the mouse on the right. Left-handers were not significantly disadvantaged in cursor-movement time and were as good with their non-preferred hand.
- Cook & Kothiyal 1998, Applied Ergonomics [AB]: operating the mouse in extreme shoulder abduction/flexion positions increased deltoid EMG.
- Delisle et al. 2004, Applied Ergonomics 35:21–28 [AB]: a left-side mouse (keyboard with a right numeric keypad) reduced shoulder flexion/abduction and wrist extension. 16 of 27 subjects converted; after 1 month task time was still longer than with the right hand.
- Sticky Keys (Windows and macOS) serializes modifier chords for one-handed users [AbilityNet, AB]. Mouse-side prevalence for Korea: UNCONFIRMED. A Kensington LinkedIn poll is non-scientific and was excluded.

**Operationalization**

- **(a) Keyboard-only critical path:** every critical function reachable without simultaneous non-modifier multi-key chords. Modifier+key is acceptable because Sticky Keys exists.
- **(b) One-hand span:** flag essential shortcuts whose keys span both halves of the keyboard with no alternative. **P3**. Heuristic: keys more than 7 columns apart (UNCONFIRMED).
- **(c) Content check:** text instructs "right-click" or "left-click" rather than "secondary/primary click". This confuses users with swapped buttons. **P3** (heuristic).
- **(d) Drag-only operations with no single-pointer alternative:** link to WCAG 2.5.7. **P2**, handled by another domain.

**Applicability.** Desktop web and apps.

**Validity limits.** The ergonomic studies concern physical workstation setup, which the software cannot control.

### HGR-14. TV remote and focus navigation: reach becomes D-pad press count

**Statement.** On TV, "reach" means the number of focus moves from the default focus to the target, plus safe-area visibility. Handedness is mostly irrelevant with a symmetric remote held in either hand.

**Parameters and sources**

- Apple HIG [FT]:
  - tvOS content inset 60 pt from top/bottom and 80 pt from the sides.
  - Control sizes: default 66×66 pt, minimum 56×56 pt.
  - Remote: distinguish press from tap and avoid responding to inadvertent taps from a resting thumb; Back opens the parent screen.
- Korean studies: button layout grouping matters for integrated-remote usability [DBpia, AB]; an inclusive-design study of TV remotes covered users in their 60s and 70s [AB].
- The claim "80% of remote use is power, channel, volume and input" is [2nd] and UNCONFIRMED.

**Operationalization**

- **Focus graph:** from the default focus, BFS over the D-pad to each critical target; record press count.
- **Findings:**
  - Critical target more than N presses away (UNCONFIRMED heuristic N = 8), or unreachable by D-pad (focus trap) → **P1**.
  - Primary content outside the 60/80 pt safe area → **P2**.
  - Focusable control smaller than 56 pt → **P2**.
- Hardware remote layout is out of scope for app QA.

**Applicability.** TV apps and web on TV.

**Validity limits.** N is a heuristic, and the KLM-style press cost needs calibration.

---

## 4. Algorithm: reach difficulty for a right- vs left-handed one-handed user

### 4.1 Model (polar, thumb-base pivot, mirrored)

```
Inputs: body_w, body_h (mm); screen rect in body (sx0, sy0, sw, sh) (mm);
        element centre (x, y) in screen mm; hand ∈ {R, L}; thumb length L (mm);
        parameters Θ (table 4.2)

1. Mirror:  if hand == L: x = sw − x                      # right-hand frame
2. Pivot (thumb CMC projection), body coordinates:
      g  = clamp(g_frac · body_h, g_min, g_max)          # height above the body bottom
      Px = body_w + e_x − sx0 ;  Py = (body_h − g) − sy0 # converted to screen coordinates
3. Polar coordinates:  dx = Px − x (across),  dy = Py − y (up)
      d = hypot(dx, dy);  ρ = d / L
      θ = atan2(dx, dy) in degrees                        # 0 = straight up the grip edge, 90 = across, >90 = down-across
4. Radial term:
      ρ > ρ_max           → rad = 1   (out of reach)
      ρ_comf < ρ ≤ ρ_max  → rad = 0.4 + 0.5·(ρ − ρ_comf)/(ρ_max − ρ_comf)    (stretch)
      ρ < ρ_near          → rad = 0.2 + 0.3·(ρ_near − ρ)/ρ_near              (cramped, near palm)
      else                → rad = 0
5. Angular term (far AND down-across only):
      if θ > θ_comf and ρ > 0.45: ang = min(0.8, 0.2 + 0.6·(θ − θ_comf)/(θ_max − θ_comf)) else ang = 0
6. D = min(1, max(rad, ang) + 0.5·min(rad, ang))
   Zones: natural D=0 · mild 0<D<0.4 · stretch 0.4≤D<1 · out D=1
7. Report D_R, D_L, the asymmetry D_L − D_R, the zone, and the raw ρ and θ (for audit).
```

Implementation: `ergoqa/hf/reach.py` (`thumb-reach-v3-uncalibrated`); unit tests in `tests/test_ergo_models.py` cover the mirror identity and the direction constraints above.

**Preferred replacement.** Implement the Bergstrom-Lehtovirta & Oulasvirta 2014 quadratic functional-area model. Its inputs are finger span *s*, index-finger distance *d* from the edge and the device surface. Use it as the boundary between `out` and not-`out` once the paper's coefficients are obtained. Keep ρ_near and the angular term for the cramped and down-across effects, which the functional-area boundary does not express.

### 4.2 Parameters (all UNCONFIRMED heuristics unless noted)

| Param | v3 default | Meaning | Status and evidence constraint |
|---|---|---|---|
| L | persona thumb length; 99–125 mm range, μ 115 | thumb tip to base | Range from Parhi 2006 [FT], US, mostly men. **The landmark definition differs across sources.** Size Korea's "thumb length" (~8.1 cm, [2nd]) and Otten's 72.8 mm clearly use shorter landmarks. Scale by hand length relative to a reference and calibrate. |
| e_x | 3 mm | pivot outside the grip-side body edge | UNCONFIRMED |
| g_frac, g_min, g_max | 0.20, 20 mm, 35 mm | pivot height above the body bottom | UNCONFIRMED; should rise with device size (Le 2018 grip shift [AB]) |
| ρ_near | 0.30 | cramped threshold | UNCONFIRMED; direction from Trudeau 2014, Xiong 2016, Parhi (SE) |
| ρ_comf | 0.70 | natural→stretch | UNCONFIRMED |
| ρ_max | 0.85 | reachable limit | UNCONFIRMED; with L = 115 gives NW reachable on Parhi's screen |
| θ_comf, θ_max | 80°, 135° | down-across angular limits | UNCONFIRMED; direction from Parhi (SW), Hoober (bottom-far "stretch") |

### 4.3 Validation of the heuristic (internal consistency only, not empirical)

The literature-derived acceptance tests and the v3 results:

| Test | Source | v3 result |
|---|---|---|
| T1: centre is not harder than any corner | Parhi; Hoober | ✅ |
| T2: the far-side top corner is the hardest cell under one-thumb grip | all sources | ✅ |
| T3: the grip-side bottom corner is harder than the centre | Trudeau 2014; Xiong 2016; Parhi SE | ✅ (0.20–0.33) |
| T4: mirror identity, `D_R(x,y) = D_L(sw−x,y)` | by construction | ✅ |
| T5: Parhi screen (57.6 × 76.8 mm) has no `out` cell for thumbs 99–125 mm (all were tapped) | Parhi | ⚠️ passes for L ≥ 106 mm; **fails for L < 106**, where NW becomes `out` |
| T6: Parhi SW is as uncomfortable as NW | Parhi | ❌ v3 scores SW as natural (0.00). A single pivot height cannot satisfy both Parhi's SW result and the bottom-row reachability of large phones (T7). |
| T7: bottom row of large phones stays reachable, since One UI and Safari put interaction there | vendor practice | ✅ bottom-centre natural; bottom-far corner ≈ 0.4 |
| T8: top row of ≥6.1" phones is `out` for L = 115 | reason OS reachability features exist | ✅ |

**Conclusion.** The heuristic reproduces the *direction* of 6 of 8 constraints. It is usable for **ordinal ranking** (which of two layouts puts frequent controls in easier zones) and for P2/P3 findings. It is **not** good enough to support P0/P1 findings without calibration or corroborating trace evidence.

### 4.4 Illustrative output: share of screen area by zone, right hand (v3, uncalibrated)

| Device (active screen, mm) | L = 100 | L = 115 | L = 125 |
|---|---|---|---|
| iPAQ h4155 (57.6 × 76.8) | natural 55 / mild 11 / stretch 24 / out 11 | 69 / 14 / 16 / **1** | 76 / 16 / 8 / 0 |
| iPhone 16 (~65.6 × 141.6, bezels assumed) | 33 / 15 / 21 / **30** | 42 / 18 / 20 / **20** | 47 / 20 / 20 / 13 |
| Galaxy S25 (~66.5 × 141.9, bezels assumed) | 33 / 16 / 21 / 30 | 42 / 18 / 20 / 20 | 48 / 20 / 20 / 13 |
| iPhone 16 Pro Max (72.9 × 158.4) | 28 / 13 / 22 / **37** | 36 / 17 / 20 / **27** | 41 / 18 / 20 / 21 |
| Galaxy S25 Ultra (~73.6 × 157.8) | 28 / 13 / 22 / 37 | 36 / 17 / 20 / 27 | 41 / 18 / 20 / 21 |
| Z Fold7 cover (~66.8 × 148.4) | 31 / 15 / 21 / 34 | 40 / 17 / 19 / 24 | 45 / 19 / 19 / 17 |

The left hand gives identical fractions by symmetry, but they fall on different elements.

Example on iPhone 16 Pro Max (440 × 956 CSS px viewport, L = 115):

| Element | Right hand | Left hand |
|---|---|---|
| Top-left back button at (30, 76) px | out (ρ 1.13) | out (ρ 0.94) |
| Top-right close button at (410, 76) px | out | out |
| Bottom-centre CTA at (220, 900) px | natural | natural |

On this device class both top corners are `out` for both hands. On smaller phones or with larger thumbs the grip-side top corner becomes reachable first, so the asymmetry appears there.

### 4.5 Calibration protocol (recommended before relying on P1)

1. Obtain B-L 2014 (netlab.tkk.fi/~oulasvir/pubs/paper2117.pdf, blocked here) and port the model.
2. Collect thumb-sweep data using the Otten 2013 / Le 2018 method: hold securely, then sweep maximum and comfortable areas without re-gripping.
   - Stratify by hand-length tercile × sex, both hands.
   - Use at least 2 current phone classes (~6.1" and ~6.9") and 1 foldable cover screen.
   - Use Korean adults for Korean-market personas. B-L used n = 20, which gives a floor.
3. Fit the pivot (e_x, g), ρ and θ limits per device class. Report cross-validated cell agreement.
4. Cross-check against task-level outcomes (grip-shift counts, time) in moderated sessions.

---

## 5. Persona ergonomic profile dimensions

Sampling guidance for Korean personas from Nemotron-Personas-Korea: assign these attributes for **coverage** (stratify so that each run includes left-grip, small-hand, older, hard-one-handed and two-thumb personas), not to reproduce prevalence. Keep literature base rates as metadata only.

| Dimension | Values | Base rate (source, context) | Effect on testing |
|---|---|---|---|
| **Handedness (self-report)** | right / left / mixed (ambidextrous) | Global 10.6% left (9.3–18.1% by criterion) [Papadatou-Pastou 2020]. Korea: 5.8% left + 7.9% ambidextrous (n = 2,437, 2009 survey) [Jung et al. 2009, Ergonomics 52(11)]; 5% left (Gallup Korea 2013, n = 1,217, aged 19+; 20s 8%, 30s–40s 6%, 50s 3%, 60+ 2%; 4% in 2002) [2nd]; 7% left (Gallup Korea Nov 2025, n = 1,700, aged 13+; teens 13%, 20s 12%) [2nd]; 3.9% left + 8.4% ambidextrous (KoGES cohort, n = 8,806, aged 40–69, 2001–02) [Song et al. 2023, AB]. Male:female OR 1.23 [2008 meta]. | Prior for the holding hand. Use the age gradient when assigning: younger Korean personas are more often left-handed. |
| **Phone operating hand (one-handed)** | right / left / switches by context | Hoober 2013: 67% R / 33% L of one-handed observations [AB]. Summary range for left one-handed use: 22–37% [Nelavelli 2018, AB]. Korea: 63% R / 37% L, self-selected poll n = 667 [2nd]. Ear side: right-handers 68% right / 25% left; left-handers 72% left [Seidman 2013, AB]. | Selects mirror frame (§2.2). **Always include ≥ 1 left-grip persona** per run. |
| **Grip mode set** | one_thumb, cradle_thumb, cradle_index, two_thumb, on_surface; plus per-context probabilities | 49/36/15% one-handed/cradled/two-handed [Hoober2013, AB]; ~75% of touches by one thumb [Hoober2017, 2nd]; tablets put down ~2/3 of sessions, 69% of small-tablet use handheld, phablet both hands 70% [2nd]. Korean: UNCONFIRMED. | Chooses reach model (HGR-1, HGR-9). |
| **Hand-occupied contexts (situational one-handedness)** | none / commute-standing (strap or bag) / carrying child / eating / walking | UNCONFIRMED (no Korean data found) | Forces one_thumb; raises severity (§6, "hard one-handed"). |
| **Hand size** | hand length mm (or S/M/L tercile), hand breadth, finger span *s* (for B-L) | Korea 8th Size Korea survey (2020–21, n = 6,839, aged 20–69, 3D hand scan): mean hand length ~18.5 cm for ages 20–39 [2nd; **sex split UNCONFIRMED**; pull the official table from sizekorea.kr]. Korean hands are wider with shorter fingers than those of 8 other nations, and hand length is ~4% shorter than Japanese [JKIIE, AB]. Male hand dimensions fell 2–5% from 1979 to 2004 [JKIIE 2010, AB]. US reference: fathers 192 ± 7.1, mothers 174 ± 7.1, adolescent females 167 ± 12 mm [Otten 2013, 2nd]. | Scales L and *s*. Small hands: more `out`, and 11.9–18.2% more discomfort in rear reach [Lee 2016, AB]. Large hands: bigger cramped zone [Xiong 2016, AB]; more controller buttons easy [Brown 2013, AB]. |
| **Thumb length L** | mm, **with a declared landmark definition** | US lab sample 99–125 mm, μ 115 [Parhi 2006, FT]. Size Korea ~8.1 cm (ages 20–39) [2nd, different landmark]. | Direct model input (§4). |
| **Age band / range of motion** | <40 / 40–64 / 65+; ROM limitation none, mild, severe; tremor | Older users: larger unreachable zones at right and bottom [Xiong 2016 IJIE, AB]; faster fatigue on 3 mm vs 9 mm buttons and slower flexion–extension [Xiong 2016 SpringerPlus, AB]. Korean prevalence: UNCONFIRMED here. | Shrinks ρ_max and raises zone-size minima (P2 → P1 for frequent small far targets). |
| **Device class and size** | phone W × H mm (e.g. 70.5 × 146.9 up to 77.6 × 163); foldable folded or unfolded; tablet; desktop; TV; controller | Average screen 6.5" in 2023 [2nd]. Korean device mix: UNCONFIRMED. | Selects geometry; run each persona on ≥ 2 phone sizes. |
| **OS reachability usage** | uses / doesn't / unknown; Android nav mode gesture or 3-button | UNCONFIRMED | Severity downgrade by one level only if `uses` (HGR-10). |
| **Mouse hand (desktop)** | right / left (buttons swapped?) | Labs: 100% mouse on the right (Melbourne 1997) [AB]; Korea: UNCONFIRMED | HGR-13 content and shortcut checks. |
| **Controller needs** | hand-size class; needs_one_handed_controls; hold/mash tolerance | UNCONFIRMED | HGR-12 severity. |

---

## 6. Severity matrix for reach and grip findings

Definitions: **critical** = completes or commits the task, is irreversible, or concerns safety. **Frequent** = used on most steps or screens. **Hard one-handed** = the persona cannot use a second hand in context (permanent, temporary or situational).

| Condition | Severity |
|---|---|
| Critical control `out` for a hard one-handed persona, **and** no reachable in-app alternative, **and** OS reachability unavailable or ineffective (Android 3-button navigation, timed interaction) | **P0** (predicted; label "inferred", recommend confirmation) |
| Critical or frequent control `out` for one_thumb grips on phones ≥ 6.1" with no reachable alternative; or the trace **observes** repeated mis-taps or accidental system-gesture exits on a reach-constrained control; or a WCAG 2.5.8 / KWCAG 6.1.3 size failure on a critical control | **P1** |
| Frequent control in `stretch`; critical control `out` but with an alternative that costs an extra step; ≥ 2 grip shifts per core task; left/right asymmetry that puts a frequent control `out` for only one hand; small target in the cramped zone; missing split keyboard or HUD mirroring in real-time competitive play | **P2** |
| Occasional control in stretch or out; grip-side target not flush to the edge; minor asymmetry; "right-click" wording; non-standard controller A/B in menus | **P3** |

Evidence labels:
- Geometry-based findings are **inferred**; state the model version and parameters.
- Trace events (mis-taps, exits, retries) are **observed**.
- Anything depending on grip or behaviour prevalence is **unknown** unless a cited base rate is given as context.

---

## 7. Non-automatable judgments (need a human or vision-LLM)

- Whether a control is critical, frequent or rare in the real task. An LLM proposes and a human confirms.
- What grip real users adopt in a given context (subway, walking, lying down, with a case or pop-socket). This needs field observation or diary studies; synthetic personas cannot substitute.
- Whether a grip shift is acceptable versus a **safety** risk (drop risk while walking or on stairs, driving-adjacent contexts).
- Subjective comfort and fatigue over long sessions, and pain in people with thumb/wrist conditions.
- Whether an in-app alternative is truly *equivalent* (discoverable, same outcome).
- Occlusion effects on comprehension: did the user actually miss the message?
- Game design intent versus barrier (a chord as intended skill expression), and the quality of a left-handed HUD. Both need play-testing.
- Canvas- or WebGL-rendered game HUD element identification. A vision-LLM can box elements, but a human should verify.
- Foldable hinge/crease feel and the unfolded one-hand weight leverage.
- Cultural context in Korea (right-hand etiquette, historical suppression of left-handedness) as it bears on persona narratives. It does not change UI geometry.

---

## 8. Contradictions and uncertainties

1. **Hoober 2013 vs 2017 figures.** The 49/36/15 grip split and the ~75% one-thumb touch share are different taxonomies (grip vs touching digit). Do not mix them in one prior.
2. **Thumb-zone heat maps vs lab data.**
   - Popular diagrams paint the whole bottom as easy.
   - Lab data show the grip-side bottom corner is poor for right-handers: Trudeau 2014 (worst performance), Parhi (SE least comfortable in the serial task; larger targets wanted) and Xiong 2016 (unreachable near-palm space).
   - Parhi found **no location effect on errors or time** in discrete tapping on a small device: location affected comfort, not accuracy.
   - Trudeau 2014 found the grip-side top-right corner best, which differs from the "bottom = best" simplification.
3. **Target-size numbers disagree.** Report the range with both sources, and choose the check tier by severity (§3 HGR-7):
   - WCAG 2.5.8: 24 CSS px ≈ 4 mm on iPhone.
   - KWCAG: 6.0 mm diagonal.
   - Hoober: 7 mm centre, 11–12 mm edges/corners.
   - iOS: 44 pt ≈ 7.3 mm.
   - Material: 48 dp ≈ 9 mm (7–10 mm).
   - Parhi: 9.2 mm discrete, 9.6 mm serial.
4. **Korean left-handedness** ranges from 3.9% (KoGES, aged 40–69, 2001–02) to 7% (Gallup 2025, aged 13+). The ambidextrous category is 7.9–8.4% where offered and absent in Gallup. Criteria differ (self-label vs task inventory).
5. **Korean hand anthropometry by sex and age is UNCONFIRMED.** The only figure found is a secondary "18.5 cm hand length, ages 20–39" from the 8th Size Korea survey. Thumb-length landmark definitions differ across sources (Parhi ~115 mm vs Size Korea ~81 mm vs Otten 72.8 mm), so L cannot be copied across sources.
6. **The B-L 2014 coefficients were not accessible.** The §4 geometry is an explicitly uncalibrated heuristic. It fails Parhi's SW comfort result (T6) and misclassifies NW as `out` for thumbs under 106 mm (T5).
7. **Old devices.** Most reach studies used 3.5–6" devices (2006–2018). Extrapolation to 6.9" phones and foldables is untested.
8. **Excluded claims.** Controller-geometry claims (thumbstick spacing, EMG percentages attributed to a "University of Michigan Human Factors Lab 2023"), a blog's "comfortable reach 64–76 mm" and the "80% of remote use on 4 buttons" were found only in unverifiable web content and are excluded.
9. **Unknown usage rates.** No usage-rate data for OS Reachability or one-handed mode were found, and none for left-handed HUD settings in games.

---

## 9. Sources

Access key: FT = full text read here; AB = abstract or snippet; 2nd = secondary.

1. Parhi, P., Karlson, A. K., Bederson, B. B. (2006). *Target Size Study for One-Handed Thumb Use on Small Touchscreen Devices.* MobileHCI. https://www.microsoft.com/en-us/research/wp-content/uploads/2006/01/parhi-mobileHCI06.pdf [FT]
2. Bergstrom-Lehtovirta, J., Oulasvirta, A. (2014). *Modeling the Functional Area of the Thumb on Mobile Touchscreen Surfaces.* CHI, 1991–2000. https://dl.acm.org/doi/10.1145/2556288.2557354 ; PDF http://www.netlab.tkk.fi/~oulasvir/pubs/paper2117.pdf ; project page https://old.hiit.fi/thumb_functional_area.html [AB; model form via secondary summaries incl. https://arxiv.org/html/2208.08734v1 and https://3osman.com/2016/05/10/how-far-can-your-thumb-reach/]
3. Hoober, S. (2013). *How Do Users Really Hold Mobile Devices?* UXmatters. https://www.uxmatters.com/mt/archives/2013/02/how-do-users-really-hold-mobile-devices.php [AB]
4. Hoober, S. (2017). *Design for Fingers, Touch, and People,* Parts 1–3. UXmatters. https://www.uxmatters.com/mt/archives/2017/03/design-for-fingers-touch-and-people-part-1.php · https://www.uxmatters.com/mt/archives/2017/05/design-for-fingers-touch-and-people-part-2.php · https://www.uxmatters.com/mt/archives/2017/07/design-for-fingers-touch-and-people-part-3.php [2nd]
5. Hoober, S. (c. 2015). *How We Hold Our Gadgets.* A List Apart. https://alistapart.com/article/how-we-hold-our-gadgets/ [2nd]
6. Trudeau, M. B., Udtamadilok, T., Karlson, A. K., Dennerlein, J. T. (2012). *Thumb Motor Performance Varies by Movement Orientation, Direction, and Device Size During Single-Handed Mobile Phone Use.* Human Factors 54(1):52–59. https://journals.sagepub.com/doi/10.1177/0018720811423660 [AB]
7. Trudeau, M. B., Catalano, P. J., Jindrich, D. L., Dennerlein, J. T. (2013). *Tablet Keyboard Configuration Affects Performance, Discomfort and Task Difficulty for Thumb Typing in a Two-Handed Grip.* PLoS ONE 8(6):e67525. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0067525 [AB]
8. Trudeau, M. B., et al. (2014). *A Data-Driven Design Evaluation Tool for Handheld Device Soft Keyboards.* PLoS ONE. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0107070 [AB]
9. Trudeau, M. B., et al. (2016). *Two-handed grip on a mobile phone affords greater thumb motor performance, decreased variability, and a more extended thumb posture than a one-handed grip.* Applied Ergonomics. https://pubmed.ncbi.nlm.nih.gov/26360191/ [AB]
10. Karlson, A. K., Bederson, B. B., Contreras-Vidal, J. L. (2006/2008). *Understanding One-Handed Use of Mobile Devices.* https://www.cs.umd.edu/hcil/trs/2006-02/2006-02.htm [AB]
11. Xiong, J., Muraki, S. (2016). *Effects of age, thumb length and screen size on thumb movement coverage on smartphone touchscreens.* Int J Industrial Ergonomics. https://www.sciencedirect.com/science/article/abs/pii/S0169814115300512 [AB]
12. Xiong, J., Muraki, S. (2016). *Thumb performance of elderly users on smartphone touchscreen.* SpringerPlus. https://springerplus.springeropen.com/articles/10.1186/s40064-016-2877-y [AB]
13. Park, Y. S., Han, S. H. (2010). *Touch key design for one-handed thumb interaction with a mobile phone: Effects of touch key size and touch key location.* Int J Industrial Ergonomics 40(1):68–76. https://www.sciencedirect.com/science/article/abs/pii/S0169814109001036 [AB]
14. Le, H. V., Mayer, S., Bader, P., Henze, N. (2018). *Fingers' Range and Comfortable Area for One-Handed Smartphone Interaction Beyond the Touchscreen.* CHI. https://dl.acm.org/doi/10.1145/3173574.3173605 [AB]
15. Otten, E. W., Karn, K. S., Parsons, K. S. (2013). *Defining Thumb Reach Envelopes for Handheld Devices.* Human Factors. https://journals.sagepub.com/doi/10.1177/0018720812470689 ; summary https://ergoweb.com/thumb-reach-distances-and-envelopes-for-handheld-devices/ [2nd]
16. Lee, S., Kyung, G., et al. (2019). *Determining Ergonomic Smartphone Forms With High Grip Comfort and Attractive Design.* Human Factors 61:90–104. https://journals.sagepub.com/doi/abs/10.1177/0018720818792758 [AB]
17. Lee, S., Kyung, G., Lee, J., Moon, S. K., Park, K. J. (2016). *Grasp and index finger reach zone during one-handed smartphone rear interaction.* Ergonomics 59(11). https://pubmed.ncbi.nlm.nih.gov/26943492/ [AB]
18. Choi, Y., et al. (2020). *Effects of Smartphone Size and Hand Size on Grip Posture in One-Handed Hard Key Operations.* Applied Sciences 10(23):8374. https://www.mdpi.com/2076-3417/10/23/8374 [AB]
19. *Ergonomics of thumb-based pointing while holding tablets* (2016). MobileHCI Adjunct. https://dl.acm.org/doi/10.1145/2957265.2961864 [AB]
20. Odell, D., Chandrasekaran, V. (2012). *Enabling comfortable thumb interaction in tablet computers: a Windows 8 case study.* HFES Annual Meeting 56:1907–1911. https://journals.sagepub.com/doi/abs/10.1177/1071181312561278 [AB]
21. Wagner, J., Huot, S., Mackay, W. (2012). *BiTouch and BiPad: Designing Bimanual Interaction for Hand-held Tablets.* CHI. https://hal.science/hal-00663972 [AB]
22. Yamanaka, S., et al. (2026). *Skewed Dual Normal Distribution Model: Predicting Touch Pointing Success Rates for Targets Near Screen Edges and Corners.* CHI. https://dl.acm.org/doi/10.1145/3772318.3791183 [AB]
23. Papadatou-Pastou, M., et al. (2020). *Human handedness: A meta-analysis.* Psychological Bulletin 146(6):481–524. https://research-information.bris.ac.uk/en/publications/human-handedness-a-meta-analysis/ [AB]
24. Papadatou-Pastou, M., et al. (2008). *Sex differences in left-handedness: a meta-analysis of 144 studies.* Psychological Bulletin. https://pubmed.ncbi.nlm.nih.gov/18729568/ [AB]
25. Jung, H. S., et al. (2009). *Hand dominance and hand use behaviour reported in a survey of 2437 Koreans.* Ergonomics 52(11):1362–1371. https://pubmed.ncbi.nlm.nih.gov/19851904/ [AB]
26. Song, et al. (2023). *Genome-wide association and replication studies for handedness in a Korean community-based cohort.* Brain and Behavior. https://onlinelibrary.wiley.com/doi/full/10.1002/brb3.3121 [AB]
27. Gallup Korea (2013). 왼손잡이 조사. https://www.gallup.co.kr/gallupdb/reportContent.asp?seqNo=491 [AB]
28. Gallup Korea (2025) left-handedness survey, via news: https://www.wbcb.co.kr/news/articleView.html?idxno=99202 [2nd]
29. Seidman, M. D., et al. (2013). *Hemispheric Dominance and Cell Phone Use.* JAMA Otolaryngology–Head & Neck Surgery. https://jamanetwork.com/journals/jamaotolaryngology/fullarticle/1688129 [AB]
30. Financial News / Cetizen poll (2014). "스마트폰 주로 어느 손으로 사용하십니까?" https://www.fnnews.com/news/201408291741263956 [2nd]
31. Löchtefeld, M., et al. (2015). *Detecting users handedness for ergonomic adaptation of mobile user interfaces.* MUM. https://dblp.org/rec/conf/mum/LochtefeldSKB15.html [AB]
32. Nelavelli, K., Plötz, T. (2018). *Adaptive App Design by Detecting Handedness.* arXiv:1805.08367. https://arxiv.org/abs/1805.08367 [AB]
33. Mehrotra, S., Das, S., Zanwar, S. (2022). *Action Bar Adaptations for One-Handed Use of Smartphones.* arXiv:2208.08734. https://arxiv.org/html/2208.08734v1 [AB]
34. Jee, S.-C., Yun, M. H. (2016). *An anthropometric survey of Korean hand and hand shape types.* Int J Industrial Ergonomics 53:10–18. https://www.sciencedirect.com/science/article/abs/pii/S016981411530041X [AB]
35. *Trend of hand dimensions for Koreans and Comparison with foreigners' data* (2010). J Korean Inst Industrial Engineers. https://koreascience.kr/article/JAKO201013351013682.page [AB]
36. Size Korea / KATS: 8th Korean anthropometric survey (2020–2021). https://sizekorea.kr/measurement-data/hand ; https://sizekorea.kr/human-info/meas-report?measDegree=8 [blocked; figures 2nd]
37. Hoffmann, E. R., Chang, W. Y., Yim, K. Y. (1997). *Computer mouse operation: is the left-handed user disadvantaged?* Applied Ergonomics 28(4):245–248. https://pubmed.ncbi.nlm.nih.gov/9414363/ [AB]
38. Delisle, A., et al. (2004). *Left-handed versus right-handed computer mouse use: effect on upper-extremity posture.* Applied Ergonomics 35:21–28. https://www.sciencedirect.com/science/article/abs/pii/S0003687003001157 [AB]
39. Cook, C., Kothiyal, K. (1998). *Influence of mouse position on muscular activity in the neck, shoulder and arm in computer users.* Applied Ergonomics. https://www.sciencedirect.com/science/article/abs/pii/S0003687098000088 [AB]
40. Brown, M., MacKenzie, I. S. (2013). *Evaluating video game controller usability as related to user hand size.* MHCI. https://www.yorku.ca/mack/mhci2013c.html [AB]
41. Baldauf, M., et al. (2015). *Investigating On-Screen Gamepad Designs for Smartphone-Controlled Video Games.* ACM TOMM. https://dl.acm.org/doi/10.1145/2808202 [AB]
42. *Virtual Joystick Control Sensitivity and Usage Patterns in a Large-Scale Touchscreen-Based Mobile Game Study* (2023). ACM MIG. https://dl.acm.org/doi/10.1145/3623264.3624461 [AB]
43. Microsoft. *Xbox Accessibility Guideline 107: Input.* https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/107 [AB]
44. *Game Accessibility Guidelines* (full list). https://gameaccessibilityguidelines.com/full-list/ [AB]
45. Apple. Human Interface Guidelines: *Game controls; Accessibility; Layout; Remotes.* JSON at https://developer.apple.com/tutorials/data/design/human-interface-guidelines/{game-controls,accessibility,layout,remotes}.json [FT]
46. Android Developers. *Make apps more accessible* (48 dp). https://developer.android.com/guide/topics/ui/accessibility/apps [FT]
47. Material Design 3. *Accessibility – structure* (48 dp ≈ 9 mm). https://m3.material.io/foundations/designing/structure [AB]; Material 2 *Bidirectionality* https://m2.material.io/design/usability/bidirectionality.html [AB]
48. W3C. *WCAG 2.2 SC 2.5.8 Target Size (Minimum)* and *2.5.5 Target Size (Enhanced).* https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html [AB]
49. KWCAG 2.2 (한국형 웹 콘텐츠 접근성 지침), 6.1.3 컨트롤 크기. https://a11ykr.github.io/kwcag22/ [AB]
50. Samsung. *One UI Design Guidelines.* https://design.samsung.com/global/contents/one-ui/download/oneui_design_guide_eng.pdf [AB]
51. Apple Support. *Reach the top of the iPhone screen with one hand (Reachability).* https://support.apple.com/guide/iphone/use-reachability-iph145eba8e9/ios [AB]
52. Android 12 one-handed mode (how-to). https://www.androidcentral.com/how-enable-one-handed-mode-android-12 [2nd]
53. TechCrunch (2025). *Chrome for Android now lets you move the address bar to the bottom.* https://techcrunch.com/2025/06/24/chrome-for-android-now-lets-you-move-the-address-bar-to-the-bottom-too [2nd]
54. Device dimensions: https://www.dimensions.com/element/apple-iphone-16-pro-max-18th-gen ; https://www.samsung.com/ca/smartphones/galaxy-s25-ultra/specs/ ; https://www.dimensions.com/element/apple-iphone-16-18th-gen ; https://www.gsmarena.com/samsung_galaxy_s25-13610.php ; https://www.samsung.com/levant/smartphones/galaxy-z-fold7/specs/ [2nd]
55. *GazeSwipe: Enhancing Mobile Touchscreen Reachability through Seamless Gaze and Finger-Swipe Integration* (2025). CHI. https://dl.acm.org/doi/10.1145/3706598.3713739 [AB]
56. AbilityNet. *Sticky Keys one-handed (Windows 11 / macOS).* https://mcmw.abilitynet.org.uk/how-to-use-sticky-keys-to-operate-the-keyboard-one-handed-in-windows-11 [AB]
