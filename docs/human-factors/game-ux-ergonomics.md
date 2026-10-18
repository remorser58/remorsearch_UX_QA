# Game UX, Game Accessibility and Play Ergonomics: Research Brief for Screen + Input Persona-Swarm QA

Date: 2026-09-28. Domain: games on console/TV, PC, handheld and mobile. Audience: engineers building (a) automated checks driven by frame capture and input injection, and (b) persona ergonomic profiles.

## 0. Evidence legend and research constraints (read first)

Every number in this brief has one of these tags:

| Tag | Meaning | Can it be a hard threshold? |
|---|---|---|
| **[V1]** | Verified at the time of writing from the primary document's own text. These are mostly GitHub-hosted primary docs: EA IRIS, the Trace Center proposed PSE guidelines, the BBC TTML validator requirements and the DaltonLens source code. | Yes |
| **[V1-3p]** | Verified at the time of writing from a third-party document that restates a standard, such as a practitioner's XAG test notes. | Yes, after a spot check against the official text |
| **[V2]** | Verified only through a web-search result snippet that quotes or summarises the named source. The full page could not be fetched. | Probably yes. Re-read the official page before shipping |
| **[R]** | Recalled from prior knowledge of the literature. It could not be fetched or searched at the time of writing. | **No.** Treat it as a placeholder until someone checks it against the original |
| **[D]** | Derived in this brief by calculation from inputs that carry the tags above. The formula is shown. | Only as strong as its inputs |

**How the research was limited.** The network egress proxy blocked WebFetch for learn.microsoft.com, w3.org, itu.int, ofcom.org.uk, arxiv.org, pmc/ncbi, wikipedia, gameaccessibilityguidelines.com, ian-hamilton.com, gamedeveloper.com, huggingface.co and the scholarly APIs. Only github.com could be fetched. Web search was rate-limited partway through. Microsoft XAG, W3C, ITU and Ofcom values therefore come from search snippets [V2], and the reaction-time, latency, motion-sickness, mobile-ergonomics and Hodent material is mostly [R]. The Sources section lists what needs checking before any [R] value is encoded as a gate.

**Severity scale used in this brief:**
- **P0:** a safety risk (photosensitive seizure) or something that blocks critical-path progress for the target persona, with no workaround in the game.
- **P1:** a major barrier. An affected persona segment is likely to fail or lose essential information.
- **P2:** significant friction, or non-conformance with a guideline, where a workaround exists.
- **P3:** a minor or polish issue.

**Finding record.** Each automated finding must keep three things apart:
- `observed`: frame IDs, pixel measurements, timestamps and the injected input log.
- `inferred`: the impact estimated from the persona model.
- `unknown`: things that were not measured, such as real display luminance, the player's actual viewing distance or the player's intent.

---

## 1. Summary

1. **Photosensitivity is the only principle that is P0 purely from pixels, and it is fully automatable.** Its main measurement gap is coverage: an agent has to provoke explosions, lightning, hit-flashes and menu transitions. Flash-analysis thresholds agree across standards:
   - More than 3 flashes in any 1 s. The Trace formulation says more than 6 transitions.
   - A transition counts at ΔY ≥ 10% of reference when the darker state is below 80% of reference. In absolute units this is 20 cd/m² with the darker state below 160 cd/m², on a 200 cd/m² reference.
   - The flashing area must exceed 25% of the 10° field (0.006 sr). On a TV of unknown size, the area rule is 25% of the screen.
   - A red flash is defined as R/(R+G+B) ≥ 0.8 together with ΔUCS ≥ 0.2.

   Sources for the above: [V1] Trace; [V2] WCAG and ITU. EA's open-source IRIS adds an "extended failure" at 2–3 flashes/s sustained over any 5 s, and flags harmful spatial patterns that last ≥ 0.5 s [V1].
2. **Text size is measurable from frames and must be judged as visual angle, not raw pixels.** XAG 101 requires the following, with text height measured from ascender to descender:
   - Console: at least 26 px at 1080p, scalable to 52 px [V2].
   - PC: at least 18 px at 1080p or 36 px at 4K [V1-3p].
   - A text-size option of up to 200% [V1-3p][V2].

   On a 55" 1080p TV viewed from 2.5 m, 26 px is about 22.7 arcmin. The same 26 px on a 4K panel without scaling is about 11.3 arcmin, which is below any ergonomic minimum [D].
3. **Subtitle-size guidance disagrees because the sources use different metrics.**
   - Channel 4 requires 46 px in HD, via Ian Hamilton [V2].
   - BBC TTML sets the font size to about 6.667% of video height (≈72 px em at 1080p), with a 120–125% line height (≈86 px, which is the "8% line height") [V1].
   - XAG 104 sets subtitle size at no less than the XAG 101 minimum, scalable to 200% [V2].

   Normalise every measurement to one metric: measured ascender-to-descender height in pixels, converted to arcmin.
4. **Contrast (XAG 102):**
   - Text and important visual elements: ≥ 4.5:1.
   - Large-scale text and elements, and inactive elements: ≥ 3:1 [V2].

   Games draw text over moving 3D scenes, so compute the worst-case (low-percentile) contrast across frames. A single screenshot is not enough.
5. **Motor demands** are XAG 107's explicit examples: mashing two buttons to beat a boss, and holding RT for 3 s to open a door [V2]. The fix is to remap actions (not buttons), offer toggle and auto-hold options, and avoid mashing and QTEs. All of these can be checked automatically by sweeping injected hold durations, press rates and response delays against a persona's motor model.
6. **QTE and timing windows.** No published standard window exists. Measure the real window by injecting responses at swept delays after the prompt's first visible frame, subtract the harness latency, and compare the result with the persona's reaction-time distribution. Model that distribution as ex-Gaussian, with age effects from Der & Deary 2006 [R]. The output is P(success) per QTE and per chained sequence, not a pass/fail on a fixed number of milliseconds.
7. **Latency.** Commonly cited genre tolerances are:
   - About 100 ms for first-person games.
   - About 500 ms for third-person games.
   - About 1000 ms for "omnipresent" views such as RTS (Claypool & Claypool 2006) [R].

   Competitive aiming degrades at tens of milliseconds (Spjut et al. 2019, whose title reads "Latency of 30 ms benefits first person targeting tasks more than refresh rate above 60 Hz") [R]. End-to-end latency is only trustworthy when measured with hardware input injection and a timestamped capture card or photodiode.
8. **Motion comfort has no validated per-frame threshold for flat screens.** Automate these three checks and leave the discomfort verdict to humans or persona inference:
   - Check that options exist: FOV, camera shake, head bob and motion blur.
   - Check that each option actually works, using an optical-flow A/B comparison with the setting on and off.
   - Validate with humans using the SSQ. Its weights are Nausea ×9.54, Oculomotor ×7.58, Disorientation ×13.92 and Total ×3.74 [V1 code; primary source Kennedy et al. 1993 [R]].
9. **Color-vision deficiency (CVD).** Simulate on captured frames with DaltonLens's recommended choices [V1]:
   - Brettel 1997 for tritan.
   - Machado 2009 for anomalous trichromacy (severity < 1).
   - Viénot 1999 for dichromacy.

   Then test whether HUD categories stay separable and whether they use redundant encoding (shape, icon or text).
10. **Automated game-playing agents are good at exploration and bad at precision.**
    - On VideoGameBench, which uses screenshots only and plays in real time, the best model in the May 2025 paper completed about 0.48% (1.6% in the paused "Lite" mode) [R; the benchmark's structure is [V1]].
    - BALROG and LMGame-Bench show that harnesses dominate the results [V1/R].

    Design rule: deterministic scripts do the timing, measurement and injection. LLM/VLM agents do navigation, coverage and first-pass semantic triage, and every claim must point to evidence frames. Humans confirm P0 and P1 findings.

### Key-parameter table

| Parameter | Value | Tag and source |
|---|---|---|
| Flash frequency limit | > 3 flashes/s fails (> 6 transitions/s in Trace wording) | [V2] WCAG 2.3.1; [V1] Trace; [V1] IRIS |
| General flash, relative-luminance form | ΔY ≥ 0.10 with the darker state < 0.80 | [V2] WCAG; [V1] Trace |
| General flash, absolute form | ≥ 20 cd/m² with the darker state < 160 cd/m² (reference 200 cd/m²) | [V2] ITU-R BT.1702; [V1] Trace |
| Bright-range rule | When the darker state is ≥ 80% of reference, Michelson contrast ≥ 1/17 | [V1] Trace proposal |
| Area threshold | 0.006 sr = 25% of any 10° field. For a TV of unknown size, 25% of the screen. For an unknown screen, 25% of any 416×416 px subarea | [V1] Trace; [V2] WCAG |
| WCAG 10° proxy | 341×256 px at 1024×768 for a 15–17" screen at 22–26" | [V2] WCAG Understanding |
| Red flash | R/(R+G+B) ≥ 0.8, with Δ ≥ 0.2 on the CIE 1976 UCS diagram | [V2] WCAG 2.2; [V1] Trace |
| Transition qualifies if it takes | ≤ 66 ms. Transitions count as synchronised within 20 ms. Risk is much reduced at ≥ 65 Hz | [V1] Trace |
| PSE response by frequency | Peaks at 16 Hz (about 90% of photosensitive patients respond); about 4% respond at 65 Hz | [V2] Jordan & Vanderheiden 2024 |
| Extended flashing | 2–3 flashes/s in any 5 consecutive seconds is an "extended failure" | [V1] EA IRIS |
| Harmful pattern duration | ≥ 0.5 s | [V1] EA IRIS |
| Console minimum text | 26 px at 1080p, scalable to 52 px | [V2] XAG 101 |
| PC minimum text | 18 px at 1080p or 36 px at 4K, measured ascender to descender | [V1-3p] XAG v3.2 test notes |
| Text scaling | Up to 200% | [V1-3p] XAG 101; [V2] XAG 104 |
| Text block spacing | Line width ≤ 80 characters, line spacing 1.5, letter spacing 0.12× and word spacing 0.16× font size | [V1-3p] XAG 101 |
| 10-foot TV text (Amazon) | ≥ 28 px at 1080p | [V2] snippet |
| Contrast | 4.5:1 for text; 3:1 for large-scale and inactive elements | [V2] XAG 102 |
| Subtitles (Channel 4) | 46 px in HD, 26 px in SD | [V2] Hamilton |
| Subtitles (BBC) | Font size ≈ 6.667% of height (landscape), with an error if below 2% or above 8%. Line height 120–125%. Region at least 5% in from the edges. Colours white, yellow, cyan or green | [V1] BBC TTML validator |
| Subtitle line length | About 37–38 characters per line; 2 lines, 3 only in exceptional cases | [V2] secondary summaries of BBC and Hamilton |
| Title-safe and action-safe areas | 90% (5% margin per side) and 93% (3.5% per side) | [R] SMPTE RP 2046-1; the 5% margin is consistent with BBC [V1] |
| Game latency tolerance | About 100 ms first-person, 500 ms third-person, 1000 ms omnipresent | [R] Claypool & Claypool 2006 |
| A/V sync | Detectable at +45 ms (audio early) and −125 ms (audio late); acceptable at +90 and −185 ms | [R] ITU-R BT.1359 |
| SSQ weights | N 9.54, O 7.58, D 13.92, Total 3.74 | [V1 code] / [R] Kennedy 1993 |
| Touch target minimums | 44×44 pt (iOS) and 48×48 dp (Android). One-thumb targets of 9.2 mm (discrete taps) and 9.6 mm (serial taps) | [R] Apple HIG, Material, Parhi et al. 2006 |
| Male red-green CVD prevalence | About 8% (Northern European ancestry); lower in East Asian populations | [R] Birch 2012 |

---

## 2. Principles

### 2.0 The measurement harness: prerequisites for every check

**Capture**
- Use lossless or near-lossless capture at the display's refresh rate:
  - HDMI capture card for console, TV or handheld docks.
  - DXGI Desktop Duplication or engine-side capture for PC.
  - `adb screenrecord`/scrcpy or engine hooks for Android.
  - Capture of the device under test for iOS.
- Record per-frame timestamps and detect dropped frames. A dropped frame silently hides flashes and shortens timing windows.
- Photosensitivity analysis needs every frame. At 60 fps that is 16.7 ms per frame. Trace defines transitions as lasting ≤ 66 ms, which is about 4 frames at 60 fps [D].
- Engine-side capture is available in EA's IRIS Unreal Engine 5 plugin, which "captures a game's frames during runtime and analyses them asynchronously in real-time" [V2].

**Perception, in order of preference**
1. Engine or UI-tree hooks. Poco (paired with Airtest) "adds the ability to directly access object (UI widget) hierarchy across the major platforms and game engines" [V1]. AltTester and GameDriver cover Unity and Unreal [R].
2. Vision:
   - OCR for text boxes and glyph heights.
   - Template matching for button glyphs and icons. Airtest does this [V1].
   - A detector or VLM for HUD elements, prompts and objectives.

   Store bounding boxes. The in-game equivalent of the DOM is the list of HUD element boxes.

**Input injection**
- Software:
  - ViGEm (a virtual Xbox or DualShock pad) or SendInput on Windows.
  - uinput on Linux.
  - `adb input` or `sendevent` on Android.
  - XCUITest on iOS.
  - Airtest simulates touch, swipe and keyboard [V1].
- Hardware, for timing-critical measurements: a microcontroller that emulates a USB HID gamepad, with a shared clock to the capture card.
- Software injection bypasses controller and USB polling latency, so it under-reports end-to-end latency [R].

**Calibration (run once per rig)**
1. Measure the loopback latency: inject an input that toggles a full-screen test pattern and record the time until capture. Subtract it from later measurements.
2. Record display geometry: diagonal, resolution and viewing distance from the persona. From these compute pixel pitch, pixels per arcmin and the size of the 10° field in pixels. See the table in 2.2.
3. Record display luminance and whether HDR is on. PSE analysis in cd/m² needs the real peak luminance. Otherwise use relative luminance with a 200 cd/m² reference, as Trace proposes for both SDR and HDR [V1].

**Coverage agent**
- An LLM/VLM or RL agent navigates the game to reach states: combat, cutscenes, menus, boss QTEs and weather effects.
- Deterministic analysers run on the recorded frames.
- The agent never self-certifies a measurement. See 2.17.

### 2.1 Photosensitive seizure safety (P0)

**Sources**
- WCAG 2.3.1 and its definitions [V2].
- ITU-R BT.1702, now at version -3 (11/2023) [V2].
- Ofcom/ITC Guidance Note, the Harding-based broadcast rule [V2 existence; details R].
- ISO 9241-391, which IRIS implements [V2].
- The Trace Center proposed guidelines (Jordan & Vanderheiden 2024, ACM TACCESS) [V1].
- EA IRIS, open-sourced in December 2023 [V1/V2].
- Epilepsy Foundation consensus (Fisher et al., Epilepsia 2026), which includes a section of advice for "designers of video games" [V2]. Its thresholds were not retrieved.
- Korean context: KWCAG forbids content that flashes at 3–50 times per second [R; verify the exact KWCAG 2.2 item text].

**Inputs**
- Every captured frame at native resolution and frame rate, with timestamps.
- The display transfer function (sRGB or PQ/HLG) and peak luminance.
- Viewing geometry from the persona, used to get the 10° window in pixels.

**Algorithm.** IRIS implements this; it can also be reimplemented.
1. Linearise each pixel and compute relative luminance: Y = 0.2126R + 0.7152G + 0.0722B on linear sRGB [R, the standard sRGB/WCAG formula]. For HDR, map to cd/m² and normalise to a 200 cd/m² reference [V1 Trace].
2. Downsample to blocks for speed. The Python port of IRIS offers `--resize 0.5` [V1].
3. For each block, track monotonic luminance changes over time. A transition counts when:
   - it spans ΔY ≥ 0.1 of reference and the darker state is < 0.8 [V1/V2], or
   - the darker state is ≥ 0.8 and the Michelson contrast is ≥ 1/17 [V1 Trace].

   The transition must complete within ≤ 66 ms [V1 Trace].
4. Red channel: count a red transition when one state is saturated red (R/(R+G+B) ≥ 0.8) and Δu′v′ ≥ 0.2 [V1/V2]. IRIS documents a "red difference threshold ±20" [V1]. This matches the older WCAG 2.0 formula, (R−G−B)×320 > 20 [R].
5. Area: in each frame, compute the fraction of pixels in transition inside every 10° window. If the geometry is unknown, use a 416×416 px window (Trace) or the full screen (TV) [V1]. The area condition holds if any window exceeds 25%. Transitions within 20 ms of each other count as simultaneous [V1 Trace].
6. Count flashes (pairs of opposing transitions) in a sliding 1 s window. More than 3 flashes/s (more than 6 transitions) with the area condition met is a **FAIL**. 2–3 flashes/s sustained over 5 s is an **EXTENDED FAIL** (IRIS) [V1].
7. Patterns: IRIS detects "spatial patterns with clear contrast and regularity" and flags harmful patterns present for ≥ 0.5 s [V1]. Ofcom-style stripe-count and area rules exist but were not retrieved [R]. For patterns, use the IRIS implementation rather than re-deriving thresholds.
8. Frequencies at or above 65 Hz carry much lower risk [V1 Trace]. Content at 120 Hz or more is still analysed.

**Thresholds and severity**

| Result | Severity |
|---|---|
| FAIL (luminance or red flash, or a harmful pattern) | **P0** |
| EXTENDED FAIL (IRIS) | **P1** |
| No "reduce flashing" or "photosensitivity" option, where flashing effects exist at all | P2 [R: GAG basic "Avoid flickering images and repetitive patterns"] |
| Near threshold (for example, 3 flashes/s and 15–25% area) | P2, with a note that a brighter display or a closer viewing distance can push it over [D] |

**Derived geometry [D]**
- On a 55" 1080p TV at 2.5 m, the 10° field is about 690 px wide. 25% of a 10° circular field is about 93k px², against 518k px² for "25% of the screen". The WCAG-style criterion is therefore about 5.5× stricter than the broadcast criterion at this distance.
- 25% of a 10° circular field = 0.25 × 2π(1 − cos 5°) = 0.00598 sr, which is the 0.006 sr in the standards.

**Not automatable, or limited**
- Certification. IRIS says it "is not intended to guarantee, certify or otherwise validate" compliance [V1]. Harding FPA is the commercial tool used in broadcasting [V2].
- Individual susceptibility.
- The true luminance of the player's display (HDR, brightness settings).
- Whether a textured surface is actually perceived as a discernible stripe pattern.
- Complete coverage of emergent effects, such as 30 simultaneous explosions in multiplayer.

### 2.2 Text size and legibility: HUD, menus, tutorials, subtitles

**Sources**
- XAG 101 [V2, V1-3p].
- GAG basic guideline "Use an easily readable default font size" [V2 title].
- Amazon 10-foot UI guidance [V2 snippet].
- Visual-angle ergonomics: ISO 9241-303 and ANSI/HFES 100 recommend about 16 arcmin minimum and 20–22 arcmin preferred for character height [R; verify].

**Inputs**
- Frame at native resolution.
- OCR line boxes. The ascender-to-descender height is XAG's metric [V1-3p]. Calibrate per font by rendering a known string ("bdpq", or Hangul with 받침) and measuring its glyph box.
- Device geometry and the persona's visual acuity.

**Algorithm**
1. `h_px` is the measured ascender-to-descender height.
2. Compare against the platform floor, scaled with vertical resolution:
   - Console: `h_px ≥ 26 × (H/1080)`.
   - PC: `h_px ≥ 18 × (H/1080)`.
3. Compute the visual angle: `θ = 2·atan(h_px·pitch / 2d)` in arcmin, where `pitch = screen height (m) / H`.
4. Persona check: the requirement is `θ ≥ θ_min(persona)`. The default θ_min is 16 arcmin [R]. Scale it by the persona's acuity (for example, multiply by 10^(logMAR)) [R; a heuristic, calibrate with users].
5. Check the options: a text-size option must reach 200% and must actually rescale the gameplay HUD and subtitles, not only menus. Verify this by toggling the option and re-measuring `h_px`.
6. For text blocks longer than 2 lines, check line width ≤ 80 characters, line spacing 1.5 and paragraph spacing 2× line spacing [V1-3p].

**Derived reference points [D]** (arcmin; 16/20/22 arcmin shown in px)

| Setup | 18 px | 26 px | 46 px | px needed for 16 / 20 / 22 arcmin |
|---|---|---|---|---|
| 55" TV at 1080p, 2.5 m | 15.7 | 22.7 | 40.1 | 18 / 23 / 25 |
| 55" TV at 1080p, 3.0 m | 13.1 | 18.9 | 33.4 | 22 / 28 / 30 |
| 55" TV at 2160p, 2.5 m | 7.8 | 11.3 | 20.1 | 37 / 46 / 51 |
| 24" monitor at 1080p, 0.6 m | 28.5 | 41.2 | 72.9 | 10 / 13 / 14 |
| 6.2" handheld at 720p, 0.35 m | 19.0 | 27.4 | 48.4 | 15 / 19 / 21 |
| 6.1" phone at 2532×1170, 0.35 m | 9.8 | 14.2 | 25.1 | 29 / 37 / 40 |

The table shows that XAG's 26 px console floor gives about 20–23 arcmin at typical living-room geometry. This is consistent with the ergonomic 20–22 arcmin preference, which suggests the floor was derived from visual angle [D, inference]. It also shows that a 4K UI that does not scale fails badly.

**Severity**

| Condition | Severity |
|---|---|
| Critical-path text (objective, warning, QTE prompt, tutorial instruction) below the platform floor or θ_min for the target persona | P1 |
| Non-critical text below the floor | P2 |
| No text scaling, or scaling that skips the HUD or subtitles | P2 |
| Text with low-contrast outlines. An outline only counts toward size if it has ≥ 2:1 contrast [V1-3p] | P3 to P2 |

**Unknown or not automatable**
- The persona's real viewing distance.
- The legibility of Hangul at small sizes. Dense syllable blocks may need more pixels than Latin text; no published game-specific number was found. **Unknown. Test with users.**
- Stylised fonts: legibility needs human or VLM judgment. XAG requires an option for a sans-serif font and to turn off stylised fonts [V1-3p].

### 2.3 Contrast of text and critical HUD over dynamic scenes

**Source:** XAG 102 [V2]. Text and important visual elements need ≥ 4.5:1. Large-scale text and elements need ≥ 3:1. Inactive elements need ≥ 3:1. Remedies XAG lists: a solid or opacity-adjustable background plate, colour options and a high-contrast mode [V2].

**Algorithm**
1. For each text or HUD box, take the foreground pixels (from OCR or a glyph mask) and the background pixels in a ring 2–4 px around each glyph. Do this over N frames of gameplay: sweep camera orientations and times of day.
2. Compute the WCAG contrast ratio `(L1+0.05)/(L2+0.05)` per frame.
3. Report the 5th percentile and the minimum. The percentile choice is a design decision, not sourced. P5 approximates "worst common case".
4. Re-test with the background-plate or high-contrast option turned on. This verifies the option works.

**Severity**

| Condition | Severity |
|---|---|
| Critical text at P5 contrast < 3:1 | P1 |
| Critical text at P5 contrast between 3:1 and 4.5:1 | P2 |
| No background or opacity option, where text is drawn over the 3D scene | P2 |

**Not automatable:** whether a glow or outline style is perceived as legible, and glare or ambient light for mobile players outdoors (context from the persona).

### 2.4 Subtitles and captions

**Sources**
- XAG 104 [V2]: at least the XAG 101 size; scalable to at least 200%.
- GAG basic guidelines "Provide subtitles for all important speech" [R title] and "If any subtitles/captions are used, present them in a clear, easy to read way" [V2 title].
- BBC TTML technical requirements [V1]: font size about 6.667% of the render height for landscape video (3.75% for vertical), with an error if below 2% or above 8%. Line height 120–125%. Regions at least 5% in from the edges. Colours white, yellow, cyan or green. The background colour is applied to spans.
- Channel 4: 46 px in HD [V2].
- About 38 characters per line, 2 lines, 3 only in exceptional cases [V2, secondary]. Reading rate 160–180 wpm [V2, secondary summary of BBC; English only].
- Usage data:
  - Ubisoft reported that 95% of Assassin's Creed Odyssey players and 97% of Far Cry New Dawn players kept subtitles on [V2, secondary].
  - More than 60% activated subtitles in Assassin's Creed Origins (Hamilton, GDC) [V2, secondary].

  Taken together, the data suggests defaults drive usage [inference].

**Algorithm**
1. **Coverage:** run speech/voice activity detection and ASR on the game audio. For every speech segment longer than about 0.5 s (a design choice), require a subtitle box within the segment ± an A/V tolerance. Use +45/−125 ms as a detection-level reference [R, ITU-R BT.1359]. Flag speech that has no subtitle. Also flag diegetic text-only barks and important sound effects that have no caption.
2. **Size and contrast:** reuse 2.2 and 2.3. Also measure the em size against BBC's 6.667% H. Record both metrics.
3. **Layout:** at most 2 lines (3 only in exceptional cases), about 38 characters per line for Latin scripts, and inside the title-safe area (≥ 5% from the edges) [V1/V2].
4. **Speaker identification:** check that a name, colour or position cue exists when more than one speaker is present. The algorithm can detect a cue; a VLM or human judges whether it is correct.
5. **Reading-time sufficiency:** for each subtitle, compute characters ÷ time on screen. Compare with the persona's reading speed. For Korean there is no validated game standard, so treat it as **unknown** and calibrate a characters-per-second value with Korean readers. Do not transfer English wpm values.
6. **Options:** size up to 200%, background opacity, speaker names, and default-on at first launch. First-launch defaults can be verified automatically.

**Severity**

| Condition | Severity |
|---|---|
| Missing subtitles for dialogue that carries objectives or instructions | P1. P0 if progress cannot be inferred any other way for a Deaf persona |
| Size, contrast or line-count failure | P2 |
| Speaker identification missing | P2 |
| Style issues | P3 |

**Not automatable:** translation quality, whether the subtitles are faithful to the audio (ASR against text gives a proxy), and whether a caption conveys the meaning of a sound ("[ominous creak]").

### 2.5 Safe area, HUD placement and occlusion

**Sources**
- SMPTE RP 2046-1: action-safe 93% and title-safe 90% [R].
- UWP 10-foot design: TV-safe margins of 48 epx left/right and 27 epx top/bottom on a 960×540 effective canvas, which is 5% per side [R].
- BBC: subtitle regions at least 5% in from the edges [V1].

**Algorithm**
1. Take all HUD boxes, from the UI tree or from vision.
2. Flag any box outside the title-safe area: at 1080p that means within 96 px of the left or right edge or within 54 px of the top or bottom; at 4K, within 192/108 px [D].
3. Flag boxes in the band between 90% and 93%.
4. Check whether the game has a HUD safe-zone calibration option and whether moving it moves the HUD.
5. For every critical HUD element, measure how often gameplay elements overlap it, and whether the HUD covers the central gameplay region.

**Severity**

| Condition | Severity |
|---|---|
| Critical HUD outside the action-safe area (clipped on overscanning TVs) | P1 |
| Critical HUD in the 90–93% band | P3 |
| No safe-zone option on console | P2 |

**Not automatable:** whether a given TV overscans, and whether the player's peripheral attention reaches corner HUD elements. Hodent's attention and "signs and feedback" pillars are relevant here [R].

### 2.6 Colour independence and colour-vision deficiency

**Sources**
- GAG basic "Ensure no essential information is conveyed by a colour alone" [R title].
- XAG 103, "additional channels for visual and audio cues" [V2 title].
- DaltonLens simulator choice [V1]:
  - Tritan: always Brettel & Mollon 1997.
  - Protanomaly and deuteranomaly (severity < 1): Machado 2009.
  - Protanopia and deuteranopia (severity 1): Viénot 1999.
  - Machado "does not work well for tritanopia".
- Prevalence: about 8% of men and about 0.5% of women of Northern European ancestry; lower in East Asian men [R, Birch 2012; for Korea, verify local survey values].

**Algorithm**
1. Identify colour-coded semantic classes: allies and enemies, loot rarity, map markers, health states, puzzle tiles and team colours. The UI tree, a VLM or a designer-supplied mapping can provide them.
2. For each CVD type and severity in the persona, simulate the frame.
3. For each pair of classes, compute the colour difference ΔE00 and the luminance contrast in the simulated frame. The pair is at risk if **both** of these hold:
   - ΔE00 is below a calibrated threshold. There is no sourced value; start around 10 and tune it with CVD testers.
   - The luminance contrast is < 3:1. The 3:1 non-text contrast figure mirrors XAG 102.
4. Redundancy check: do the classes also differ in shape, icon, pattern or label? Check with template or VLM comparison.
5. If a colourblind mode exists, verify that turning it on changes the at-risk pairs to pass. Do not only check that the menu toggles.

**Severity**

| Condition | Severity |
|---|---|
| Essential gameplay distinction lost under CVD with no redundant cue | P1. P0 if it gates progress, such as a colour-only puzzle with no alternative |
| Non-essential distinction lost | P2 |
| Colourblind mode that only recolours some elements | P2 |

**Not automatable:** whether information is "essential" (design intent), and aesthetic acceptability of the colourblind palettes.

### 2.7 Audio-only cues and redundancy (Deaf and hard-of-hearing players, or sound-off contexts such as commuting)

**Sources**
- XAG 103 [V2 title].
- GAG guidelines on visual alternatives to important sounds [R].

**Algorithm**
1. Run onset and event detection on the audio, such as footsteps, alarms and enemy vocal tells.
2. Correlate each detected event with gameplay consequences in later frames, for example damage taken within N seconds.
3. For each audio event that predicts a gameplay consequence, look for a visual indicator in the frames within ±200 ms. This window is a design choice; tune it against the A/V sync tolerances above.
4. Check whether a sound-visualisation option exists and whether it produces indicators for those events.

**Severity**

| Condition | Severity |
|---|---|
| A threat or instruction delivered only by sound | P1 |
| Ambient information delivered only by sound | P3 |

**Not automatable:** which sounds matter. Causal inference between sound and consequence only gives candidates, so a human confirms them.

### 2.8 Motor demands: holds, mashing, chords, remapping

**Sources**
- XAG 107 [V2]:
  - Remap game actions, not individual controls.
  - Offer toggle holds.
  - Its own examples of exclusionary design: "repeatedly mash two buttons to beat a boss" and "hold down the right trigger for 3 seconds to open a door".
  - It covers speed, complexity, duration, control of game speed, remappable actions, toggles and "auto" holds.
- GAG "Avoid repeated inputs (button-mashing/quick time events)" [V2 title]. GAG "Allow controls to be remapped/reconfigured" (basic) [R].

**Algorithm, with injection sweeps against a detected prompt or objective**

| Probe | Method | Output |
|---|---|---|
| Hold | Binary-search the hold duration until the action completes. Detect completion by a UI change or a state change | `T_hold_req` |
| Mash | Inject presses at rates of 2, 4, 6, 8, 10 and 12 Hz, and at a steady rate for increasing durations | Minimum `r_req` and duration `T_req` to succeed |
| Chord | Detect prompts that need ≥ 2 simultaneous inputs | Count, and whether they are on the critical path |
| Remap | Navigate Settings → Controls. Remap every action to an alternative. Re-run a smoke test, then check that the on-screen glyphs update to the new binding | Remap coverage %, glyph consistency |
| Toggle and auto options | Turn on hold-to-toggle and auto-mash if present, then re-run the hold and mash probes | Whether each option works |

**Persona comparison**
- `T_hold_req > T_hold_max(persona)`, or `r_req > r_tap_sustained(persona, T_req)`, means the persona fails.
- Rough adult capacity for finger tapping is about 5 taps/s for the index finger in young adults, declining with age [R, normative finger-tapping data; verify]. There is no gamepad-thumb standard, so collect that capacity data.

**Severity**

| Condition | Severity |
|---|---|
| A critical-path hold, mash or chord the persona cannot do, with no toggle, auto or skip option | P0 for that persona |
| The same with a workaround only through system-level remapping | P1 |
| A hold > 3 s or any mashing without an in-game alternative | P2. The 3 s comes from XAG's own example, used as an illustration rather than a formal limit |
| Glyphs that do not follow remapping | P2 |

**Not automatable:** pain, fatigue and the RSI experience. Also whether mashing is a fun genre convention, which a design decision settles by offering an option.

### 2.9 Timing windows, QTEs and reaction-time modelling

**Sources**
- Der & Deary 2006, Psychology and Aging [R]. UK Health and Lifestyle Survey, about 7,000 adults.
  - Simple reaction time (SRT) slows little until about age 50, then faster.
  - Four-choice reaction time (CRT) slows roughly linearly across adulthood.
  - Within-person variability increases with age.
  - Sex differences are present.
  - The exact means and SDs by decade are **not retrieved**. Extract them from the paper's tables into the persona priors.
- Rough textbook values:
  - Young-adult visual SRT is about 190–250 ms [R: Kosinski 2008 literature review; Woods et al. 2015].
  - Choice RT grows with log2 of the number of alternatives (Hick–Hyman law) [R].
- Ex-Gaussian distributions (μ, σ, τ) are the standard model for right-skewed reaction times [R].
- XAG 107 and GAG advise adjustable game speed and avoiding QTEs [V2].

**Algorithm**
1. **Detect the prompt onset.** Find the first frame where the QTE glyph or text is visible above 50% opacity (template or VLM). Record `t0`.
2. **Measure the window.** For offsets δ in 0…3000 ms (for example, 50 ms steps with random order and repeats), reload the checkpoint, inject a press at `t0 + δ`, and record success. The window is the set of δ values that succeed, `[δ_min, δ_max]`. Correct it by the harness loopback latency (see 2.0).
3. **Model the human.** `δ_human = RT_persona + motor_time + (L_player_input − L_harness_input) + (L_player_display − L_capture)`. `RT_persona` is drawn from ex-Gaussian(μ, σ, τ), which is age-banded and choice-adjusted (more options mean slower responses).
4. **Estimate the chance of success.** `P_success = F(δ_max) − F(δ_min)` over `δ_human`. For chains of k prompts, `P_chain = Π P_i`. If a failure restarts the chain, report the expected number of attempts, `1/P_chain`.
5. **Flag** when `P_success(persona)` is below the target. The target is not sourced; propose 0.95 for the critical path and tune it. Also flag when the window is shorter for later prompts in a chain.
6. **Check options:** timing extension, auto-complete QTEs, game speed, pause during a QTE.

**Severity**

| Condition | Severity |
|---|---|
| Critical-path QTE with `P_success` < about 0.5 for the target persona and no option | P0 |
| `P_success` < 0.95 on the critical path | P1 |
| Optional content | P2 |

**Not automatable:** the effect of anticipation and learning (people get faster after a few tries), stress effects, and whether a QTE "feels fair".

### 2.10 Latency, frame pacing and A/V sync

**Sources**
- Claypool & Claypool 2006 [R]: about 100 ms for first-person, about 500 ms for third-person and about 1000 ms for "omnipresent" views.
- Spjut et al. 2019 (SIGGRAPH Asia) [R]: title "Latency of 30 ms benefits first person targeting tasks more than refresh rate above 60 Hz".
- Ivkovic et al. 2015 (CHI) [R]: local latencies of a few tens of ms degrade 3D aiming.
- Touch perception [R, low confidence on the exact values]:
  - Ng et al. 2012: users distinguish about 6 ms from 1 ms when dragging.
  - Jota et al. 2013: tap performance and perception thresholds around 25 ms.
- A/V sync, ITU-R BT.1359 [R]: detectable at +45/−125 ms, acceptable at +90/−185 ms.
- Tools: NVIDIA FPSci exists for latency user studies [V1]. PresentMon, LDAT and Reflex analysers are the usual tools [R].

**Algorithm**
1. **End-to-end latency:** inject input through hardware at `t_i`. Find the first captured frame where a region of interest changes (muzzle flash, character pose, menu highlight). The latency is `t_frame − t_i − loopback offset`. Take at least 50 samples per action and report the median and p95.
2. **Frame pacing:** measure frame-time distribution with PresentMon or capture timestamps. Report p50, p99 and the number of frames above 2× the target frame time. The 2× cut-off is a heuristic, not sourced.
3. **A/V sync:** find the offset between audio onsets (gunshot, footstep) and the matching visual event.
4. **Cloud or streaming:** repeat under the network profiles defined by the persona.

**Severity**

| Condition | Severity |
|---|---|
| Core-action latency above the genre threshold [R] | P1 |
| Latency spikes, or frame-time p99 above 2× target in combat | P2 |
| A/V offset outside the "acceptable" band | P2 |
| A/V offset outside the "detectable" band only | P3 |

**Not automatable:** the player's display lag (TV game mode on or off) and perceived "floatiness" in the feel of the game.

### 2.11 Motion comfort: FOV, camera shake, head bob, motion blur

**Sources**
- The SSQ (Kennedy et al. 1993) [R], with weights verified from implementation code [V1]:
  - 16 symptoms, each rated 0–3.
  - Nausea ×9.54, Oculomotor ×7.58, Disorientation ×13.92, Total ×3.74.
- The MSSQ (Golding), for persona susceptibility [R].
- Console-game motion sickness: Stoffregen et al. 2008 (Human Factors) found substantial incidence among standing console players and related it to postural sway [R; the percentages are not retrieved].
- GAG guidelines: an option to adjust FOV, and avoiding or allowing players to turn off background movement, camera shake and head bob [R titles].
- XAG has a "visual distractions and motion settings" guideline [R; the number is not verified].

**Algorithm**
1. Compute dense optical flow (Farnebäck or RAFT) between frames. Estimate global camera motion (a homography or rotation). Decompose it into low-frequency intentional motion and high-frequency jitter (shake). Detect periodic vertical oscillation at walking cadence (head bob).
2. Measure the motion-blur proxy: sharpness (Laplacian variance) during fast pans.
3. **A/B test options:** for each setting (shake, bob, blur, FOV), measure with it on and off along the same injected path. The option "works" if jitter energy and blur drop substantially. A good starting criterion is at least 80% reduction, but that figure is not sourced.
4. **FOV mismatch heuristic [D]:** compute the angle the display subtends at the persona's distance. A 55" TV at 2.5 m subtends about 27° horizontally; a 24" monitor at 0.6 m subtends about 48°. Compare that with the game's camera FOV. A large ratio means a mismatch between visual and vestibular cues, which is a plausible trigger for motion sickness, but **there is no validated threshold**. Report the ratio and whether an FOV slider exists.

**Severity**

| Condition | Severity |
|---|---|
| No option to turn off shake, bob or blur, or an option that does not work | P2 |
| No FOV option in first-person 3D | P2 |
| Forced camera motion that cannot be turned off in VR | P1 |

**Not automatable:** actual sickness. Validate with the SSQ on humans before and after 15–20 minute sessions. The session length is a common protocol choice [R].

### 2.12 Mobile touch controls: size, placement, thumb reach, occlusion

**Sources**
- Apple HIG: minimum 44×44 pt hit targets [R]. Material: 48×48 dp [R].
  - 44 pt ≈ 6.9 mm at 163 pt/in [D from R].
  - 48 dp ≈ 7.6 mm at 160 dp/in [D from R].
- Parhi, Karlson & Bederson 2006: one-thumb targets of 9.2 mm (discrete) and 9.6 mm (serial) [R].
- Hoober 2013, portrait grip in the wild: about 49% one-handed, 36% cradled, 15% two-handed [R]. Games in landscape mostly use a two-thumb grip. **No published norm for landscape thumb-zone maps was retrieved (unknown).**
- On-screen gamepad studies exist (for example, Baldauf et al. 2015 comparing on-screen gamepad designs) [R; the numbers were not retrieved].
- GAG: "Ensure interactive elements / virtual controls are large and well spaced, particularly on small or touch screens" [R title]. Advanced guidelines ask to allow interfaces to be rearranged or resized [R].

**Algorithm**
1. Get control boxes in pixels from the UI tree or vision. Convert to millimetres: `mm = px / ppi × 25.4`. Flag controls below 7 mm and, for thumb-primary controls, below 9.2–9.6 mm.
2. Measure the gap between adjacent controls in millimetres. Run a touch-error simulation: inject taps with Gaussian offset, with the SD calibrated from the persona's thumb precision [R/unknown]. Estimate the rate of mis-taps onto neighbouring controls.
3. **Reach:** model each thumb as an arc anchored at the grip point, with the radius set from the persona's thumb length and the grip offset from the device edge (a persona parameter). Flag controls that need a grip change. **Unvalidated geometry: calibrate it with Korean users on common devices.**
4. **Occlusion:** while the virtual stick is held, project a thumb and hand polygon from the contact point toward the bottom and side edge. Flag critical HUD (health, minimap, cooldowns, subtitles) under the polygon.
5. **Customisation:** check that a layout editor exists and that resized or moved controls persist.

**Severity**

| Condition | Severity |
|---|---|
| Critical control (attack, jump, confirm) below 7 mm, or with a mis-tap rate above about 5% (not sourced) | P1 |
| Critical HUD occluded during core play | P1 |
| No layout customisation | P2 |

**Not automatable:** grip comfort, hand fatigue, and phone heat or throttling. The last one can be partly measured through the frame rate.

### 2.13 Controller ergonomics and cumulative input load

**Sources**
- Case reports of video-game tendinopathies ("Nintendinitis", Brasington 1990, NEJM) [R].
- An esports health survey reporting eye fatigue, neck and back pain, and wrist and hand pain (DiFrancisco-Donoghue et al. 2019, BMJ Open SEM) [R; the percentages are not retrieved].
- XAG 107 on duration and complexity [V2].
- **No validated game-specific RSI threshold was found.**

**Algorithm**
1. From the injected and recorded input logs of a representative play session, compute:
   - presses per minute per button;
   - total trigger-held time and the longest continuous hold;
   - stick deflection time;
   - chord frequency;
   - the longest period without a natural pause, used as a "rest opportunity" measure.
2. Compare with the persona's endurance parameters and with other games in the portfolio (relative ranking).

**Severity:** P2 or P3 advisory only, unless it combines with 2.8 failures.

**Not automatable:** pain, and differences in hand anthropometry across controllers. Physical reach needs hand models or human testing.

### 2.14 Difficulty, failure and flow

**Sources**
- Flow theory: Csikszentmihalyi; Chen 2007, "Flow in games" [R].
- Hodent's "game flow" pillar [R].
- DDA precedent: Hunicke 2005 [R].
- Industry AI playtesting for difficulty:
  - King: Gudmundsson et al. 2018, human-like playtesting in Candy Crush, predicting level pass rates [R].
  - Rovio and Aalto: Roohi et al. 2021, predicting engagement and difficulty with AI players [R].
- XAG and GAG recommend difficulty options and practice without failure [R].

**Algorithm**
1. Run a swarm of agent personas with parameterised skill: RT distribution, aim noise, planning depth. Each attempts every segment.
2. Log for each segment: attempts to clear, pass rate, time to clear, and time lost per failure (the distance back to the checkpoint).
3. Flag spikes: a segment whose pass rate is below k× its neighbours. k is design-tuned and not sourced.
4. Flag checkpoint gaps where the time lost per failure exceeds the persona's tolerance.
5. Verify that assist and difficulty options change the measured pass rate.

**Severity**

| Condition | Severity |
|---|---|
| A segment that cannot be completed (bug, soft-lock) | P0 |
| A critical-path difficulty wall for the target persona with no assist option | P1 |
| A spike with assist available | P2 |

**Not automatable:** whether difficulty is intended (Souls-likes), fun, sense of mastery, and frustration against challenge. Agent skill does not map directly onto human skill, so calibrate against human telemetry.

### 2.15 Onboarding, tutorials and learnability (Hodent framework)

**Sources**
- Hodent, *The Gamer's Brain* (2017) [R]. Usability pillars:
  1. Signs and feedback
  2. Clarity
  3. Form follows function
  4. Consistency
  5. Minimum workload
  6. Error prevention and recovery
  7. Flexibility

  Engage-ability pillars: motivation, emotion and game flow. These rest on the limits of perception, attention and memory, and on "learning by doing".
- Andersen et al. 2012, CHI [R]. About 45,000 players across 3 games. Tutorials paid off only in the most complex game (up to about 29% more play time), not in simpler ones. Just-in-time, context-sensitive help worked better than front-loaded help.
- Pinelle et al. 2008 game usability heuristics [R].
- GAG basic guidelines on including tutorials and starting the game without navigating multiple menus [R titles].

**Automatable metrics**
- Inputs and time from boot to first control of the character (count unskippable logos).
- Number and length of text screens shown before the first interaction.
- Whether accessibility settings (subtitles, text size, CVD options) appear before first gameplay.
- Whether tutorial prompts show the correct glyph set for the active device, and whether they follow remapping.
- Whether tutorials can be skipped and replayed, and whether a control reference is available from pause.
- Whether a tutorial prompt blocks play until the correct action is performed (learning by doing), compared with text-only prompts.
- How often the same prompt re-appears. Repeated appearance is an inferred proxy for failure to learn.

**Severity**

| Condition | Severity |
|---|---|
| A required mechanic never taught, and never shown in the control reference | P1 |
| Glyph mismatch (for example, Xbox glyphs on a PlayStation pad) | P2 |
| A text wall before first control | P3 |

**Not automatable:** comprehension. Use LLM-persona "think-aloud" only as a hypothesis generator, then confirm with human playtests.

### 2.16 Pause and save anytime, time limits, game speed, menu navigation and narration

**Sources**
- XAG 112, UI navigation [V2 title].
- XAG screen narration (106) [R number].
- XAG 107 on game speed [V2].
- GAG guidance on time limits and pause [R].

**Automatable checks**
- Inject Pause at random times, including in cutscenes and QTEs. Verify the gameplay region freezes: frame difference ≈ 0 outside menu overlays.
- OCR countdown timers, and check for options to extend or disable them.
- Check that every menu is reachable with a single input method: D-pad only, keyboard only, and touch only.
- Check that the focus indicator is visible, with contrast ≥ 3:1 against its surroundings (mirrors XAG 102).
- Check that menu narration (TTS) fires on focus change. Detect speech in the audio within about 500 ms of the focus change and compare the ASR text with the focused label.

**Severity**

| Condition | Severity |
|---|---|
| Cannot pause during mandatory timed sequences | P1 |
| No narration on menus, where the platform expects it | P2 |
| Focus indicator invisible | P1 in menus that gate play |

### 2.17 Automated playtesting agents: what they can and cannot do

**Evidence**
- **VideoGameBench** (Zhang et al., May 2025) [V1 structure]:
  - 7 test and 13 dev games on Game Boy, MS-DOS and browser.
  - Perception is "exclusively through screenshots".
  - Model calls run asynchronously in real time. The "Lite" mode pauses the game while the model thinks.
  - Result: the best model completed about 0.48%, and 1.6% in Lite [R; from the paper abstract]. Inference latency was named a major limitation.
- **BALROG** (Paglieri et al., 2024; ICLR 2025): long-horizon RL environments including NetHack [V1]. Reported that vision input often did not help, or hurt, compared with text-only observations [R].
- **LMGame-Bench / GamingAgent** (ICLR 2026) [V1]:
  - Games: Sokoban, Tetris, 2048, Candy Crush, Pokémon Red, Super Mario Bros and Ace Attorney.
  - Evaluated both with and without an agentic "gaming harness". Harnesses change the results materially [R].
- **Orak**, from KRAFTON (Korea), 2025 [V1]:
  - 12 games across 6 genres: Street Fighter III, Super Mario, Ace Attorney, Her Story, Pokémon Red, Darkest Dungeon, Minecraft, Stardew Valley, StarCraft II, Slay the Spire, Baba Is You and 2048.
  - Observations are text and screenshots. The interface is MCP-based.
- **Industry reinforcement-learning agents** [R]:
  - EA SEED: Bergdahl et al. 2020, augmenting automated testing with deep RL; Gordillo et al. 2021, curiosity-driven coverage.
  - Ubisoft La Forge: RL navigation in AAA games.
  - King: human-like playtesting.
  - DeepMind SIMA (2024) and SIMA 2 (2025): instructable pixel-to-keyboard/mouse agents.
- **Glitch detection by vision-language models:** GlitchBench (CVPR 2024) and VideoGameQA-Bench (2025) report weak detection [R].
- **Industry adoption:** Politowski et al. 2022 found automated game testing still "a long way to go" [R].

**Design rules for this repository's persona swarm**
1. **Split roles.**
   - The LLM/VLM persona agent sets goals, navigates, decides what to try next and writes hypotheses in the persona's voice.
   - Deterministic analysers produce every measured number: PSE, size, contrast, timing windows, latency and safe area.
   - The injection engine executes the sweeps.
2. **Pause when possible.** Real-time play by LLMs fails mainly on latency [R]. Use engine pause or step, emulator frame-stepping, or checkpoint reloads, and measure timing with scripts, not with the agent.
3. **Evidence-first findings.** Every finding cites frame indices and a clip, the injected input log, the analyser version and the thresholds used. A VLM claim without an analyser measurement is `inferred`, never `observed`.
4. **Human gate.** P0 and P1 findings need human confirmation, except PSE analyser FAIL, which is released as P0 immediately with the clip attached.
5. **Coverage accounting.** Report which states were reached (levels, menus, effects) and which were not, as `unknown`.

---

## 3. Persona dimensions: the ergonomic profile schema

Each dimension lists its unit, how to set a default, and which checks use it. Default distributions marked "calibrate" have no verified numbers in this brief.

| Group | Dimension | Unit and values | Default or prior (tag) | Used by |
|---|---|---|---|---|
| Demographic | age_band | 10s, 20s, … 70+ | Korean market mix: calibrate from telemetry | RT priors, reading speed |
| Reaction | srt_exgauss | μ, σ, τ in ms | Age-banded from Der & Deary 2006 tables [R, extract]. Young adults are roughly 190–250 ms mean [R] | 2.9 |
| Reaction | crt_slope | ms per bit (Hick–Hyman) | Calibrate; CRT slows linearly with age [R] | 2.9 multi-button QTE |
| Reaction | rt_variability | intra-individual SD | Increases with age [R] | 2.9 |
| Motor | tap_rate_sustained(T) | Hz as a function of duration | About 5 Hz for a young adult's index finger [R, verify]; thumb on a pad unknown | 2.8 mash |
| Motor | hold_max | s | Unknown; XAG's 3 s example is illustrative | 2.8 hold |
| Motor | chord_capacity | Max simultaneous inputs | 1–4 | 2.8 |
| Motor | hands_available / one_handed | enum | — | 2.8, 2.12 |
| Motor | tremor / aim_noise | px or deg SD | Calibrate | 2.12 touch error, 2.14 agent skill |
| Motor | thumb_length, hand_span | mm | Anthropometric tables [R/unknown for Korean data] | 2.12 reach, 2.13 |
| Motor | input_device | gamepad, keyboard and mouse, touch, adaptive, switch access | — | Remap and navigation checks |
| Motor | pain_or_fatigue_condition | bool plus notes | — | 2.13 |
| Vision | acuity_logMAR | logMAR | 0.0 normal; low-vision personas at 0.5 or more | 2.2 θ_min scaling [R heuristic] |
| Vision | cvd_type, cvd_severity | protan, deutan or tritan; 0–1 | Male prevalence about 8% (European) and lower in East Asia [R] | 2.6 |
| Vision | contrast_sensitivity | logCS | Calibrate | 2.3 (raise the contrast bar) |
| Vision | photosensitive | bool | Treat all builds as needing a pass; the persona flag only adds narrative | 2.1 (P0 regardless) |
| Vision | screen_reader_or_narration_needed | bool | — | 2.16 |
| Hearing | hearing_level | none, HoH, Deaf, single-sided | — | 2.4, 2.7 (mono audio) |
| Hearing | sound_off_context | bool (for example, subway commute) | Common in Korean mobile play: context assumption, unverified | 2.4, 2.7 |
| Cognitive | reading_speed | characters per second (Korean) or wpm (English) | English 160–180 wpm broadcast norm [V2 secondary]; **Korean unknown, calibrate** | 2.4, 2.15 |
| Cognitive | genre_literacy, controller_literacy | novice, casual or expert | — | 2.14 agent skill, 2.15 |
| Cognitive | working_memory_load_tolerance | low, medium or high | — | Hodent minimum-workload checks |
| Vestibular | mssq_percentile | 0–100 | From the MSSQ norms [R] | 2.11 interpretation |
| Context | device_class, screen_diag, resolution, viewing_distance | in, px, m | Console on a 55" TV at 2.5 m, PC on a 24" monitor at 0.6 m, phone at 0.35 m. These are illustrative defaults, not sourced norms | 2.1 area, 2.2 angle, 2.12 mm |
| Context | display_lag_ms, hdr_on, peak_nits | ms, bool, cd/m² | Calibrate | 2.1, 2.9, 2.10 |
| Context | network_profile | RTT and jitter | — | 2.10 cloud and online play |
| Context | session_length, posture | minutes; couch, desk or commute | — | 2.11, 2.13 |
| Motivation | goal_orientation | story, challenge or social | Hodent's engage-ability pillars [R] | 2.14 tolerance |
| Motivation | failure_tolerance | Retries before quitting | Calibrate from telemetry | 2.14 |

Rules for personas:
- Any number a persona contributes to a finding must be recorded under `inferred` with its tag.
- Only the analyser's measurements go under `observed`.

---

## 4. Non-automatable judgments (human or expert review needed)

1. **Photosensitivity certification** and HDR on real displays. IRIS disclaims certification [V1].
2. **Whether information is essential**: colour-coded, audio-only or subtitle-relevant. The analyser finds candidates and designers decide.
3. **Actual motion sickness, pain and fatigue.** Use the SSQ and self-report in human sessions [V1/R].
4. **Fun, flow and fairness.** This includes intended difficulty (genre conventions) and whether mashing or a QTE is "the point" of a moment. Hodent's engage-ability pillars can only be measured by proxy [R].
5. **Comprehension of tutorials and objectives.** LLM personas generate hypotheses; humans confirm them.
6. **Subtitle and caption quality**: translation fidelity, the meaning of sound captions, and correct speaker identification.
7. **Legibility of stylised fonts and of Hangul at small sizes.** No game-specific Korean norm was found.
8. **Cultural and age appropriateness of feedback** (emotion) and the sense of "game feel".
9. **Physical reach and grip on real devices and controllers.** Anthropometry can only be approximated.
10. **Whether a VLM agent's perception is correct.** It must be cross-checked against analyser outputs or UI-tree data. VLMs hallucinate game states [R].

---

## 5. Contradictions and tensions, with guidance on resolving them

1. **Subtitle size: 46 px, about 72 px, or 26 px?**
   - Channel 4's 46 px in HD [V2] is a broadcast glyph-size convention.
   - BBC's fontSize is about 6.667% of the height, which is about 72 px em at 1080p, with a line height of about 86 px ("8%") [V1].
   - XAG 104 only requires the XAG 101 minimum (26 px at 1080p on console, measured ascender to descender) plus 200% scaling [V2].

   These are different metrics (em, line height, glyph extent) applied to different contexts (broadcast and games). **Resolution:** measure glyph extent in pixels, convert it to arcmin for the persona's setup, and report against every reference.
2. **Minimum text: 26 px (console XAG), 28 px (Amazon TV) or 18 px (PC XAG).** All three hold under their own viewing assumptions. The visual-angle table in 2.2 reconciles them [D].
3. **Flash thresholds: relative against absolute.** WCAG's 10% and < 0.8 match ITU/Ofcom's 20 cd/m² and < 160 cd/m² **only at a 200 cd/m² reference** [V1 Trace]. HDR displays much brighter than that break the equivalence. Trace proposes keeping 200 cd/m² as the reference for HDR [V1].
4. **Area: 25% of the screen or 25% of a 10° field.** At a 55" TV and 2.5 m, the WCAG-style area is about 5.5× smaller than the broadcast area [D], so WCAG is stricter up close. Handhelds and phones are viewed close, so this matters for them. Use the stricter rule and report both.
5. **"Extended flashing" exists only in some tools.** IRIS flags 2–3 flashes/s over 5 s [V1]. WCAG has no such rule. A community Python port of IRIS uses `extended_fail_seconds` = 4 and `max_transitions` = 4 [V1]. These differ from the IRIS README. Pin one analyser version, record its configuration in every finding, and do not mix outputs.
6. **Red-flash definitions:** WCAG 2.2 uses u′v′ ≥ 0.2 [V2]; IRIS uses "±20", which looks like the older (R−G−B)×320 formulation [V1/R]. Different tools can disagree on saturated-red content.
7. **Subtitle usage statistics disagree:** more than 60% "activated" subtitles (AC Origins) against 95–97% "kept on" (Odyssey, Far Cry New Dawn) [V2 secondary]. The likely cause is default-on against opt-in, and "kept on" includes passive defaults. **Implication:** test and report the first-launch default state.
8. **Accessibility against design intent.** XAG and GAG advise against mashing, QTEs and hard timing [V2]. Genres such as fighting and rhythm games treat these as core mechanics. **Resolution:** severity depends on whether the element is on the critical path and whether an option exists, not on the mechanic itself.
9. **Tutorials.** Andersen et al. found tutorials helped only in complex games [R], while guidelines advise including tutorials [R]. **Resolution:** measure whether players can learn the game (2.15 metrics). Do not count tutorial screens.
10. **Latency thresholds.** Genre-level tolerances of 100 to 1000 ms [R] conflict with competitive-aiming studies that show effects at tens of milliseconds [R]. **Resolution:** use persona-by-genre thresholds, stricter for competitive personas.
11. **Agent capability claims.** Real-time screenshot agents barely progress (VideoGameBench, about 0.5%) [R], while harnessed agents finish long RPGs [R]. The harness, not the model alone, drives capability. Do not generalise from demos.
12. **CVD simulation algorithms disagree.** Machado fails for tritan [V1]. Use the per-type choice described in 2.6.
13. **TV overscan.** Many modern TVs have no overscan in game mode [R], yet safe-area guidance persists. Keep the 90% rule for critical HUD. It costs little and players' settings vary.

---

## 6. Sources

Access status: "fetched" means the full text was read at the time of writing; "snippet" means only search-result text was seen; "not accessed" means it is cited from prior knowledge [R].

**Guidelines and standards**
1. Microsoft, Xbox Accessibility Guideline 101: Text display. Snippet [V2] (console 26→52 px at 1080p). https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/101
2. anevins12, *XAG V3.2 testing methodology* (PC scope), 101-Text-Display.md. Fetched [V1-3p]: 18 px at 1080p or 36 px at 4K, ascender to descender, 200%, spacing. https://github.com/anevins12/xag-methodology
3. Microsoft, XAG 102: Contrast. Snippet [V2]. https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/102
4. Microsoft, XAG 103: Additional channels for visual and audio cues. Title only [V2]. https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/103
5. Microsoft, XAG 104: Subtitles and captions. Snippet [V2]. https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/104
6. Microsoft, XAG 107: Input. Snippet [V2]. https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/107
7. Microsoft, XAG 112: UI navigation. Title only [V2]. https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/112
8. Microsoft, XAG version history, and accessibility feature tags. Not accessed. https://learn.microsoft.com/en-us/gaming/accessibility/xag-version-history ; https://learn.microsoft.com/en-us/xbox/accessibility/accessibility-feature-tags
9. Game Accessibility Guidelines (Basic/Intermediate/Advanced). Page titles seen via snippet [V2]; the site could not be fetched and the levels of the individual guidelines are [R]. https://gameaccessibilityguidelines.com/use-an-easily-readable-default-font-size/ ; https://gameaccessibilityguidelines.com/if-any-subtitles-captions-are-used-present-them-in-a-clear-easy-to-read-way/ ; https://gameaccessibilityguidelines.com/avoid-repeated-inputs-button-mashing-quick-time-events/
10. W3C, Understanding SC 2.3.1 Three Flashes or Below Threshold (WCAG 2.2). Snippet [V2]. https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html
11. ITU-R BT.1702 (-2 10/2019, -3 11/2023): Guidance for the reduction of photosensitive epileptic seizures caused by television. Snippet [V2]. https://www.itu.int/rec/R-REC-BT.1702/
12. Ofcom/ITC, Guidance Note for Licensees on Flashing Images and Regular Patterns. Existence confirmed by snippet; details not accessed [R]. https://www.ofcom.org.uk/__data/assets/pdf_file/0021/16248/gn_flash.pdf
13. Jordan, J. B. & Vanderheiden, G. C. (2024). International Guidelines for Photosensitive Epilepsy: Gap Analysis and Recommendations. *ACM TACCESS* 17(3). Snippet [V2] (16 Hz peak, 65 Hz, 0.006 sr). https://dl.acm.org/doi/10.1145/3694790
14. Trace RERC, *pseGuidelines* (guidelinesFromPaper.md, pseGuidelines.md). Fetched [V1]. https://github.com/traceRERC/pseGuidelines
15. Fisher, R. S. et al. (2026). Visually-provoked seizures: Consensus of the Epilepsy Foundation Working Group. *Epilepsia* 67:565–581. Snippet [V2]; thresholds not accessed. https://onlinelibrary.wiley.com/doi/10.1111/epi.18702
16. Fisher, R. S. et al. (2005). Photic- and pattern-induced seizures: review for the EFA Working Group. Title snippet [V2]. https://pubmed.ncbi.nlm.nih.gov/16146439/
17. BBC, *ttml-validator* discussion #10, "BBC Subtitle Guidelines technical requirements for EBU-TT-D". Fetched [V1]. https://github.com/bbc/ttml-validator/discussions/10
18. BBC R&D, "How big should subtitles be?" Not accessed. https://bbc.github.io/csun/how_big_should_subtitles_be/index.html
19. Hamilton, I., "How to do subtitles well – basics and good practices". Snippet [V2] (Channel 4 46 px HD / 26 px SD; about 38 characters per line). https://ian-hamilton.com/how-to-do-subtitles-well-basics-and-good-practices/
20. 80.lv, "10 Golden Rules on Subtitles for Games". Snippet [V2, secondary] (Ubisoft 95% / 97% kept on). https://80.lv/articles/10-golden-rules-on-subtitles-for-games
21. Secondary summaries of BBC guidance (37 characters per line, 160–180 wpm). Snippet [V2, secondary]. https://www.clevercast.com/bbc-subtitling-guidelines/
22. SMPTE RP 2046-1, safe areas. Not accessed [R].
23. ITU-R BT.1359, relative timing of sound and vision. Not accessed [R].
24. KWCAG 2.1/2.2, Korean Web Content Accessibility Guidelines, flashing item. Not accessed [R].
25. Accessible Games Initiative (ESA and platform holders, 2025), accessibility tags. Not accessed [R]. The pixel criteria are unknown.
26. AbleGamers, Accessible Player Experiences (APX) design patterns. Not accessed [R]. Pattern names should be taken from accessible.games before use.

**Tools**

27. Electronic Arts, *IRIS*, README. Fetched [V1]. https://github.com/electronicarts/IRIS ; Unreal Engine plugin (snippet [V2]): https://github.com/electronicarts/IRIS-Unreal-Plugin ; open-source announcement (snippet): https://caniplaythat.com/2023/12/04/ea-open-sources-photosensitivity-tool-and-adds-more-patents-to-pledge/
28. tokoroten, *iris-pse-detection* (Python port), USAGE.md. Fetched [V1]. https://github.com/tokoroten/iris-pse-detection
29. DaltonLens-Python, `simulate.py`. Fetched [V1]. https://github.com/DaltonLens/DaltonLens-Python
30. jgxuann, *Simulator-Sickness-Questionnaire*, `calculate_SSQ.py`. Fetched [V1] (implements Kennedy et al. 1993). https://github.com/jgxuann/Simulator-Sickness-Questionnaire
31. NetEase, *Airtest* and *Poco*. Fetched [V1]. https://github.com/AirtestProject/Airtest
32. NVIDIA, *FPSci* (latency and FPS user-study tool). Fetched [V1]. https://github.com/NVlabs/FPSci

**Game-agent benchmarks and research**

33. Zhang, A. et al. (2025). VideoGameBench. Repository fetched [V1]; headline results [R] (arXiv 2505.18134). https://github.com/alexzhang13/VideoGameBench
34. Paglieri, D. et al. (2024). BALROG. Repository fetched [V1]; findings [R] (arXiv 2411.13543). https://github.com/balrog-ai/BALROG
35. LMGame-Bench / GamingAgent (ICLR 2026). Repository fetched [V1] (arXiv 2505.15146). https://github.com/lmgame-org/GamingAgent
36. KRAFTON, Orak (2025). Repository fetched [V1] (arXiv 2506.03610). https://github.com/krafton-ai/Orak
37. Not accessed [R]:
    - Bergdahl et al. 2020 (EA SEED, IEEE CoG); Gordillo et al. 2021 (EA SEED, IEEE CoG).
    - Ubisoft La Forge, RL navigation in AAA games (about 2020–2021).
    - Gudmundsson et al. 2018 (King, IEEE CIG).
    - Roohi et al. 2021 (CHI PLAY).
    - Politowski, Guéhéneuc & Petrillo 2022.
    - DeepMind SIMA 2024 and SIMA 2 2025.
    - Taesiri et al., GlitchBench (CVPR 2024) and VideoGameQA-Bench (2025).
38. Springer UAIS (2025), "The evolution of video game accessibility on Xbox consoles in the Far Cry game series". Title snippet only. https://link.springer.com/article/10.1007/s10209-025-01208-4

**Human factors literature (all [R]; not accessed at the time of writing; verify before use)**

39. Der, I. & Deary, I. J. (2006). Age and sex differences in reaction time in adulthood: Results from the United Kingdom Health and Lifestyle Survey. *Psychology and Aging* 21(1):62–73.
40. Woods, D. L. et al. (2015). Factors influencing the latency of simple reaction time. *Frontiers in Human Neuroscience*. Kosinski, R. J. (2008+). A literature review on reaction time (Clemson).
41. Claypool, M. & Claypool, K. (2006). Latency and player actions in online games. *Communications of the ACM* 49(11).
42. Spjut, J. et al. (2019). Latency of 30 ms benefits first person targeting tasks more than refresh rate above 60 Hz. *SIGGRAPH Asia Technical Briefs*. Ivkovic, Z. et al. (2015). Quantifying and mitigating the negative effects of local latencies on aiming in 3D shooter games. *CHI*.
43. Ng, A. et al. (2012). Designing for low-latency direct-touch input. *UIST*. Jota, R. et al. (2013). How fast is fast enough? *CHI*.
44. Kennedy, R. S. et al. (1993). Simulator Sickness Questionnaire. *International Journal of Aviation Psychology* 3(3). Golding, J. F. (2006). MSSQ-short. Stoffregen, T. A. et al. (2008). Motion sickness and postural sway in console video games. *Human Factors* 50(2).
45. Hodent, C. (2017). *The Gamer's Brain: How Neuroscience and UX Can Impact Video Game Design*. CRC Press.
46. Andersen, E. et al. (2012). The impact of tutorials on games of varying complexity. *CHI*. Pinelle, D., Wong, N. & Stach, T. (2008). Heuristic evaluation for games. *CHI*.
47. Csikszentmihalyi, M. (1990). *Flow*. Chen, J. (2007). Flow in games. *CACM*. Hunicke, R. (2005). The case for dynamic difficulty adjustment in games. *ACE*.
48. Parhi, P., Karlson, A. & Bederson, B. (2006). Target size study for one-handed thumb use on small touchscreen devices. *MobileHCI*. Hoober, S. (2013). How do users really hold mobile devices? *UXmatters*. Apple Human Interface Guidelines; Material Design.
49. Birch, J. (2012). Worldwide prevalence of red-green color deficiency. *JOSA A*. Brettel, Viénot & Mollon (1997); Viénot, Brettel & Mollon (1999); Machado, Oliveira & Fernandes (2009).
50. Brasington, R. (1990). Nintendinitis. *NEJM*. DiFrancisco-Donoghue, J. et al. (2019). Managing the health of the eSport athlete. *BMJ Open Sport & Exercise Medicine*.

**Verification to-do, in priority order before encoding hard gates**
1. The official XAG 101, 104 and 107 pages: exact console, PC and mobile pixel tables, and XAG numbering for motion (117?) and photosensitivity (118?).
2. Ofcom GN pattern rules: stripe-pair count, area and luminance.
3. Der & Deary 2006: SRT and CRT means and SDs by age band.
4. Claypool 2006 thresholds, and BT.1359 A/V values.
5. SMPTE safe-area percentages.
6. Korean CVD prevalence and the KWCAG flash item wording.
7. VideoGameBench and BALROG headline numbers.
8. Accessible Games Initiative tag criteria.
