# Perception & cognition: research brief (`perception-cognition`)

최신 출처 검토는 [2026-10-02 갱신 기록](2026-10-02-research-update.md)에 있습니다.
이 문서에는 당시의 접근 제한과 잠정 주장을 보존합니다.

Prepared 2026-09-28 for the ergonomic persona-swarm QA (`ergoqa`).

**Scope.** This brief covers:
- colour and contrast: WCAG 2.x 1.4.3, 1.4.6 and 1.4.11, KWCAG, and the status of APCA/WCAG 3;
- colour vision deficiency (CVD): prevalence (global and Korean), Machado 2009 simulation, and ΔE00 distinguishability;
- colour-only information (1.4.1);
- text size and legibility: visual angle, critical print size, Hangul, KRDS;
- text spacing and line length (1.4.8, 1.4.12);
- presbyopia;
- glare and ambient light;
- reading time for transient messages (2.2.1, 2.2.2);
- response-time limits and required feedback;
- Hick–Hyman, working memory, and recognition vs recall;
- Gestalt grouping;
- human-error taxonomy;
- flashing (2.3.1) and motion (2.3.3);
- self-report instruments (NASA-TLX, SUS, SEQ, UMUX-Lite) and why LLM personas must not fill them in.

## How to read this brief

### Evidence tags

Each number carries one of the tags below. These match the sibling `motor-pointing.md`, plus one extra tag, `[recalled]`.

- `[primary]`: I read the primary text or data myself at the time of writing. Examples: the WCAG 2.0 SC text in the `wcag-as-json` package, the axe-core 4.13.0 source, the apca-w3 0.1.9 docs, and the colour-science 0.4.6 Machado tables.
- `[snippet]`: the value comes from search-engine excerpts of the named source. I could not open the full text. Verify before hard-coding.
- `[derived]`: I computed the value here from a cited model. It is a model output, not an observation.
- `[recalled]`: a well-known value from the cited primary source. It is **not re-verified at the time of writing** because of the access problems below. Treat it as provisional until someone checks the source. It is never a threshold on its own authority.
- `unconfirmed`: I could not trace the value to a source. Do not use it as a threshold.

### Retrieval limits when this was written (October 2026)

- **WebFetch was blocked** by the egress proxy for every host I tried: w3.org, pubmed, nngroup.com, arxiv.org, inf.ufrgs.br, adrianroselli.com and readthedocs.io.
- **Web search** was rate-limited after about 25 queries.
- **Package registries (PyPI, npm) were reachable.** I used them to read these primary data and texts:
  - Machado matrices, from the `colour-science` dataset;
  - APCA level definitions, from `apca-w3`;
  - WCAG 1.4.12 spacing values and the large-text definitions, from `axe-core`;
  - WCAG 2.0 SC wording, from `wcag-as-json`.
- All worked examples were computed locally with colour-science 0.4.x and small scripts (not shipped); `[derived: …]` tags name the script that produced each value.

### Epistemic mapping to the repository's evidence bundle (same as `motor-pointing.md`)

| What | `basis` | `epistemic_status` |
|---|---|---|
| Measured geometry, colours, font sizes and timestamps from DOM, UIAutomator or frames | `measured` | `observed` |
| Model outputs: CVD simulation, visual angle vs CPS, Hick, reading time, ambient contrast | `model` | `inferred` |
| Vision-LLM or human judgement (meaning, grouping intent, whether an icon is recognisable) | `judgment` | `inferred` |
| Anything a synthetic persona "feels" or "rates" | — | **never** `observed`, and never counted as evidence that real users are affected at any rate |

### Severity policy used throughout

The rules are team-tunable policy, consistent with `motor-pointing.md`:

- **P0** needs one of:
  - an observed blocking failure on a critical path;
  - a structural path to irreversible harm;
  - a **measured safety hazard**, such as a WCAG 2.3.1 flash failure. This is a measured property of the content, not a persona prediction.
- **A model prediction alone reaches P1 at most.** This includes the CVD-simulated confusion, text below the critical print size at the persona's distance, and reading time longer than the toast duration.
- Normative failures that make content inaccessible, such as 1.4.3, 1.4.11 or 1.4.1 on a critical path, are **P1**. On non-critical content they are **P2**.
- AAA-only gaps and "margin" findings are **P3**. Situational findings (glare) are **capped at P2**.

---

## 1. Summary

1. **Contrast: WCAG 2.x is still the only normative rule in 2026.**
   - The thresholds:
     - 4.5:1 for body text; 3:1 for large text (≥18 pt, or ≥14 pt bold, i.e. 24 px or 18.66 px);
     - 7:1 / 4.5:1 for AAA;
     - 3:1 for non-text UI parts and states (1.4.11).
     - All `[snippet]` from W3C Understanding. `axe-core` encodes 18 pt / 14 pt bold and 4.5 `[primary]`.
   - KWCAG 2.2 uses the same 4.5:1 and 3:1. It also allows 3:1 for **zoomable** content `[snippet]`, which is a Korea-specific relaxation.
   - The WCAG 3 draft says the contrast algorithm is "to be determined". APCA is exploratory and non-normative (visual-contrast section removed July 2023) `[snippet]`.
   - Use APCA only as an advisory second opinion. Its levels:
     - Lc 75 minimum for body text; Lc 90 preferred;
     - Lc 60 for other content text; Lc 45 for headlines;
     - Lc 30 for spot text; Lc 15 for discernible non-text.
     - All from `apca-w3` 0.1.9 docs `[primary]`.
   - The two methods disagree sharply on dark colours. Example: #8A8A8A text on black passes WCAG at 6.08:1 but is only Lc −39.6 in APCA `[derived]`.
2. **CVD base rates for Korea.**
   - Males: 5.90% and females 0.44%, using HRR plates (J Korean Med Sci 1989) `[snippet]`.
   - Males: 6.5% and females 1.1%, with a weighted overall 3.9%, in KNHANES 2013. The sample was 2,686 adults aged 19–49 (Kim et al. 2019, Optom Vis Sci) `[snippet]`.
   - Deutan is far more common than protan: 2.5% vs 0.4% of all participants (≈6:1) `[snippet]`.
   - For comparison, Northern Europeans are ≈8% male / 0.5% female. Chinese and Japanese men are 4–6.5% (Birch 2012) `[snippet]`.
3. **CVD simulation.**
   - Use Machado et al. (2009) matrices on **linearised** sRGB. Take the per-severity matrices from the published 0.1-step tables `[primary: colour-science]`.
   - ergoqa currently interpolates between identity and the severity-1.0 matrix. That approximation errs by a median ΔE00 ≈ 2–3.6 and a p95 of up to ≈6.8 vs the tabulated matrices `[derived]`. The error is too large when the pass line is ΔE00 10.
4. **When are two state colours "distinguishable"?**
   - No standard exists.
   - Defensible anchors:
     - ΔE00 ≈ 1 is a JND for large side-by-side patches `[snippet]`;
     - Palettailor requires a minimum pairwise ΔE00 of **10** for categorical palettes `[snippet]`;
     - discriminability falls with mark size (Szafir 2018) `[snippet]`.
   - Recommendation:
     - after CVD simulation, ΔE00 ≥ 10 is "distinct"; 5–10 is "marginal"; < 5 is "confusable" `[policy]`;
     - **and** require a non-colour cue, or ≥ 3:1 luminance contrast between states (WCAG technique G183) `[recalled]`.
   - Example: error-red #D32F2F vs success-green #388E3C has ΔE00 66 for normal vision. Under deuteranopia it drops to **5.2**, and the contrast ratio between the two is only 1.21:1 `[derived]`.
5. **Text size should be judged as visual angle, not px.**
   - Critical print size (CPS) for normal vision is **0.2° x-height**, within a 0.15–0.3° range (Legge & Bigelow 2011) `[snippet]`.
   - Hangul CPS is larger than English CPS (He, Baek & Legge 2018) `[snippet]`. A Korean on-screen study measured **0.41° (young) vs 0.52° (older adults)** (Korean J Cognitive Psychology 2015) `[snippet]`.
   - Default 16 CSS px at the CSS reference distance is ≈24′ em ≈ 12′ x-height. That sits *exactly at* CPS, with no acuity reserve `[derived]`.
   - KRDS (the Korean government design system) sets body text ≥16 px, with 17 px as the default in its standard style `[snippet]`.
   - **ergoqa bug risk:** `TEXT_MIN_ARCMIN = 12` is compared with the **font size (em)**. But 12′ (0.2°) is an **x-height** criterion. For Latin text it should be ≈24′ em; for Hangul ≈25–31′ `[derived]`.
6. **Presbyopia moves the phone away and shrinks the text.**
   - Minimum accommodation amplitude ≈ 15 − 0.25 × age dioptres (Hofstetter) `[recalled]`. That gives a near point of ≈40 cm at 50 and ≈80 cm at 55 without correction `[derived]`.
   - At 50 cm, 16 px phone text subtends only 18′ `[derived]`.
7. **Reading time for toasts.**
   - Korean adult silent reading is ≈202 ± 88 "WPM" (about 9.8 syllables/s mean and 5.5/s at −1 SD) `[snippet → derived]`.
   - Older adults read ≈30% slower (208 vs 296 wpm) `[snippet]`.
   - Android Toast is 2 s / 3.5 s `[snippet]`. Material snackbar guidance is 4–10 s `[snippet]`.
   - A 13-syllable Korean toast needs ≈4.8 s for a slow older reader (with ergoqa's 1.5× safety factor) `[derived]`. So a 2 s toast fails that persona.
8. **Response-time limits and feedback.**
   - 0.1 s gives a sense of direct manipulation. 1 s keeps the flow of thought. At 10 s attention is lost: show percent-done and cancel (Miller 1968; Card et al. 1991; Nielsen 1993) `[recalled]`.
   - Productivity threshold ≈400 ms (Doherty & Thadani 1982) `[recalled]`.
   - These can be checked on action traces with frame-accurate timestamps.
9. **Cognition models (Hick–Hyman, working memory) compare designs; they do not give pass/fail limits.**
   - Hick–Hyman slope ≈150 ms/bit (Card, Moran & Newell 1983) `[recalled]`. It applies to practised, equiprobable choices; novices search menus roughly linearly.
   - Working-memory span is ~4 chunks (Cowan 2001), not 7 ± 2 `[recalled]`.
   - The robust, automatable check is **cross-screen recall**: information shown on one screen that must be reproduced on another without copy, paste or autofill (WCAG 2.2 3.3.7 / 3.3.8) `[recalled]`.
10. **Flashing (2.3.1) is fully computable and is P0.**
    - The WCAG area threshold, "0.006 sr = 25% of a 10° field", follows from geometry: a 10° field is 0.0239 sr `[derived]`.
    - On a phone at 30 cm, 10° spans ≈315 CSS px. So almost any full-width flash exceeds the area limit `[derived]`.
11. **Self-report instruments (SUS, SEQ, UMUX-Lite, NASA-TLX) measure a human's experience.** An LLM persona has none. Scores it produces are text predictions, influenced by known norms (SUS ≈68) and prone to flattened variance. They must never be reported as instrument scores.

---

## 2. Principles

Each principle gives: claim and sources, inputs, algorithm, threshold, severity, what cannot be automated, and validity limits. Check IDs `PC-xx` align with `ergoqa/checks.py` naming where a check already exists.

### PC-01 Text contrast (WCAG 1.4.3 AA, 1.4.6 AAA; KWCAG 5.4.3)

**Claim and sources.**
- **1.4.3 (AA).** Text needs ≥4.5:1. Large-scale text needs ≥3:1. Large means ≥18 pt, or ≥14 pt bold; 1 pt = 1.333 CSS px, so ≈24 px and ≈18.66 px `[snippet: W3C Understanding 1.4.3]`. axe-core 4.13.0 uses `largeTextPt: 18`, `boldTextPt: 14` and `contrastRatio.normal.expected: 4.5` `[primary]`.
- **1.4.6 (AAA).** 7:1, and 4.5:1 for large text `[recalled; W3C Understanding 1.4.6]`.
- **Rationale for 4.5:1.**
  - The ANSI standard sets 3:1 as the minimum for normal observers.
  - 20/40 acuity is associated with a contrast-sensitivity loss of about 1.5×, and 3 × 1.5 = 4.5.
  - 20/40 is "commonly reported as typical visual acuity of elders at roughly age 80".
  - All `[snippet: W3C Understanding 1.4.3]`. The 7:1 level targets roughly 20/80 `[recalled]`.
- **Formula.** Contrast = (L1 + 0.05)/(L2 + 0.05). Relative luminance L = 0.2126R + 0.7152G + 0.0722B on linearised sRGB. The linearisation threshold is 0.04045; it was 0.03928 before May 2021, with no practical effect `[snippet]`.
- **Exceptions:** incidental text, inactive components, pure decoration and logotypes `[recalled]`.
- **KWCAG 2.2.** Text contrast ≥4.5:1. 18 pt+ or 14 pt bold+ may drop to 3:1, and **text in content that can be zoomed may drop to 3:1** `[snippet: a11ykr/KWCAG 2.2 summaries]`. KWCAG 2.2 has 4 principles, 14 guidelines and 33 check items `[snippet]`. Item number 5.4.3 is `[recalled]`.

**Inputs.**
- Per text node: computed `color` and `background`, after compositing alpha and walking up to the first opaque ancestor.
- `font-size` in CSS px, and `font-weight`.
- For images, canvas or game HUD: an OCR text box (PaddleOCR and similar support Hangul) plus the pixels in the box.

**Algorithm.**
1. DOM path: composite the colours, then compute the WCAG ratio.
2. Pixel path (canvas, game, video, gradient or image backgrounds):
   - k-means with k = 2 on the box pixels, using the eroded glyph mask as foreground and a dilated ring as background;
   - report the **5th-percentile** ratio across background samples `[policy]`;
   - tag the result `basis: model`, because anti-aliasing lowers measured glyph contrast.
3. Apply the large-text rule using the *rendered* px after OS font scaling.

**Threshold.** Required ratio = 4.5 for normal text, 3.0 for large text. Use AAA values only for P3 "margin" reports.

**Severity.**

| Condition | Severity |
|---|---|
| Critical information below 3:1 (price, consent, error text, primary CTA label) | P1 |
| Body or critical text below AA | P1 |
| Other text below AA | P2 |
| AA passes but AAA fails, for personas with reduced acuity or age ≥ 65 | P3 |
| Placeholder or disabled text | Exempt from AA (inactive), but flag P3 if Lc < 30 |

**Cannot automate.**
- Whether text is "incidental" or "logotype".
- Whether a disabled control *should* be readable.
- Legibility of decorative or display fonts: weight and x-height vary by typeface.

**Validity limits.**
- WCAG 2 luminance contrast overstates contrast near black. Dark-mode pairs can pass 4.5:1 and still read poorly (see PC-03).
- The formula ignores font weight and size, except for the binary large-text rule.
- It assumes an sRGB display and nominal flare (the +0.05 term).
- Wide-gamut CSS colours (`color(display-p3 …)`) must be converted to sRGB first.

### PC-02 Non-text contrast and state visibility (WCAG 1.4.11 AA; 2.4.13 AAA)

**Claim and sources.**
- **1.4.11.** Visual information needed to identify UI components and their states, and meaningful graphical objects (icons, chart lines, pie wedges), needs ≥3:1 against adjacent colours. Inactive components are exempt `[snippet: W3C Understanding 1.4.11; WebAIM]`.
- **2.4.13 Focus Appearance (AAA, WCAG 2.2).**
  - The focus-indicator area is at least that of a 2 CSS px perimeter.
  - Focused vs unfocused states differ by ≥3:1 `[recalled]`.

**Inputs.**
- Component boxes and computed border, fill and outline colours, plus the adjacent background.
- Screenshots of each state (default, hover, focus, selected, error, disabled), taken by driving the state through the driver.

**Algorithm.**
- For each component, take the max over {border vs background, fill vs container} and require ≥3:1. ergoqa already does this.
- **State-pair check.** For selected vs unselected (tabs, toggles, chips, radio buttons), compute:
  - contrast between the state colours;
  - pixel-diff area between the two state screenshots;
  - presence of a non-colour cue: a check icon, weight change, underline or shape change, detected in the DOM or by image diff.
- Focus: compare focused and unfocused screenshots. Changed-pixel area must be ≥ perimeter × 2 px, and the changed pixels must have ≥3:1 contrast vs their prior colour.

**Threshold.** 3:1 (1.4.11). For state pairs: 3:1 between states **or** a non-colour cue (see PC-04).

**Severity.**
- Primary control boundary invisible (< 3:1 and no text label) on a critical path: **P1**.
- Focus indicator absent for keyboard, TV or controller navigation: **P1**. This also fails 2.4.7 AA `[recalled]`.
- Other failures: P2.

**Cannot automate.**
- Which graphical parts are "required to understand" the content.
- Whether a text label is sufficient without a boundary. Button-like text links are a design judgement.

**Validity limits.**
- "Adjacent colour" is ambiguous for gradients, shadows and translucent surfaces.
- Shadows are often the only boundary cue, and they are not measured well by a 2-colour ratio.

### PC-03 APCA and WCAG 3: status and advisory use

**Claim and sources.**
- **Status.**
  - WCAG 3.0 is a Working Draft. Its text outcome reads "The default visual presentation of text meets @@[contrast measure to be determined]".
  - A separate requirement "may be needed if red/green CVD is not accounted for" `[snippet: w3.org/TR/wcag-3.0 and WCAG 3 support material]`.
  - APCA's visual-contrast section was moved out of the Working Draft in July 2023 `[snippet: multiple secondary sources]`.
  - Adrian Roselli, "WCAG3 Contrast as of April 2026", covers this; fetch was blocked, so only the title and summary are `[snippet]`.
  - One vendor blog claims a September 2026 WD and a Recommendation around late 2029. That is **unconfirmed**.
- **APCA levels** (apca-w3 0.1.9 docs, algorithm 0.0.98G-4g) `[primary]`:
  - **Lc 90**: preferred for body text (≥18 px/300 or ≥14 px/400).
  - **Lc 75**: minimum for body text (≥24 px/300, 18 px/400, 16 px/500, 14 px/700).
  - **Lc 60**: minimum for other readable content text (≥24 px/400, 16 px/700).
  - **Lc 45**: large or heavy text (≥36 px/400 or 24 px/700) and fine pictograms.
  - **Lc 30**: absolute minimum for spot text (placeholder, disabled) and solid icons.
  - **Lc 15**: minimum for discernible non-text ≥6 px; treat anything below as invisible.
  - "AAA-equivalent": add Lc 15.
  - Font sizes assume an x-height ratio of 0.5 and Helvetica/Arial weights. "One reference px is defined as 1.278 arc minutes."

**Worked disagreements** (`[derived]`, computed with apca-w3 0.1.9 and the WCAG formula):

| Text on background | WCAG 2 | APCA Lc | Note |
|---|---|---|---|
| #767676 on #FFFFFF | 4.54 | 71.6 | Passes AA; just below APCA body minimum 75 |
| #FFFFFF on #767676 | 4.54 | −77.0 | Polarity matters in APCA |
| #FFFFFF on #F57C00 (orange) | 2.70 (fail) | −56.9 | APCA rates white-on-orange far better than WCAG does |
| #000000 on #F57C00 | 7.77 | 52.3 | WCAG prefers black; APCA rates it below Lc 60 |
| #8A8A8A on #000000 | 6.08 (pass) | −39.6 | Dark mode: passes WCAG, fails APCA for body text |

**Operationalisation.**
- Compute both. Keep WCAG 2 as the pass/fail driver.
- Emit an **advisory** P3 when WCAG passes but |Lc| < 60 for body text, or < 45 for large text. The same applies to dark themes.
- Never raise severity from APCA alone.

**Validity limits.**
- APCA was developed by a single team and is still in public beta.
- It has not been adopted by any law, including KWCAG or the EU EN 301 549.

### PC-04 Colour-only information (1.4.1) and CVD distinguishability

**Claim and sources.**
- **1.4.1 (A).** "Color is not used as the only visual means of conveying information, indicating an action, prompting a response, or distinguishing a visual element" `[primary: WCAG 2.0 text]`. KWCAG equivalent: 5.4.1 "색에 무관한 콘텐츠 인식" (content recognisable regardless of colour) `[recalled]`.
- **Technique G183.** A link or control distinguished only by colour needs ≥3:1 luminance contrast with surrounding text, **plus** a non-colour cue on hover and focus `[recalled]`.
- **Simulation.** Machado, Oliveira & Fernandes (2009), IEEE TVCG 15(6):1291–1298. The model is physiologically based and handles anomalous trichromacy and dichromacy in one framework. Matrices are published in severity steps of 0.1 `[snippet]`.
  - DaltonLens's review: Machado is reasonable for protan and deutan. For tritan, Brettel 1997 is the better-validated choice `[snippet]`.
  - Severity-1.0 matrices, identical to the ergoqa constants `[primary: colour-science 0.4.6 `CVD_MATRICES_MACHADO2010`]`:
    - protan `[[0.152286,1.052583,−0.204868],[0.114503,0.786281,0.099216],[−0.003882,−0.048116,1.051998]]`
    - deutan `[[0.367322,0.860646,−0.227968],[0.280085,0.672501,0.047413],[−0.011820,0.042940,0.968881]]`
    - tritan `[[1.255528,−0.076749,−0.178779],[−0.078411,0.930809,0.147602],[0.004733,0.691367,0.303900]]`
  - Apply the matrices to linear RGB. That is DaltonLens's convention `[recalled]` and ergoqa's current choice.
- **ΔE00 anchors.**
  - JND ≈ 1 `[snippet: arXiv 2404.03787]`.
  - Palettailor (Lu et al. 2021) requires a minimum pairwise ΔE00 of **10** in categorical palettes "so colours can be distinguished even for large spatial distances" `[snippet]`.
  - Szafir 2018, "Modeling color difference for visualization design" (TVCG 24(1):392–401): the discriminable difference grows as mark size shrinks `[snippet; exact size-dependent values not captured, so unconfirmed]`.
  - A generic rule of thumb ("<1 imperceptible, 2–3 perceptible on close look, >5 clearly visible") appears in secondary sources only. It is `unconfirmed` and applies to large side-by-side patches, not to small UI marks recognised in isolation.

**Inputs.**
- Colour pairs that encode meaning: state colours, series colours, status badges, error borders, game team colours, map legends.
- Persona `vision.cvd` ∈ {none, protan, deutan, tritan} and severity 0.1–1.0.

**Algorithm.**
1. Find colour-coded pairs: elements with the same role or shape that differ only in colour, legend entries, and states of one component.
2. For each pair, compute:
   - (a) ΔE00 for normal vision;
   - (b) ΔE00 after Machado simulation at the persona's severity. Use the **tabulated** matrix for that severity, not interpolation. Interpolation error: median 1.8–3.6 and p95 3.2–6.8 ΔE00 vs the tables `[derived: interp.py, 400 random colours]`;
   - (c) the WCAG ratio between the two colours;
   - (d) whether a non-colour cue exists: text, icon, pattern, shape, position or underline.
3. Decide:

| Result | Verdict |
|---|---|
| (d) present | Pass |
| (d) absent and (c) ≥ 3:1 | Pass for 1.4.1 (G183 analogue); still report (b) |
| (d) absent, (c) < 3:1, and (b) < 10 | Colour-only failure for that persona |
| (b) < 5 | "Confusable" |

**Worked example** (`[derived: calc.py]`):

| Pair | CR between | ΔE00 normal | Protanopia | Deuteranopia | Tritanopia | Deutan 0.6 |
|---|---|---|---|---|---|---|
| #D32F2F error vs #388E3C success | 1.21 | 66.0 | 17.0 | **5.2** | 61.3 | 18.1 |
| #E53935 vs #43A047 | 1.28 | 68.1 | 19.5 | **5.2** | 64.0 | 18.8 |
| #F57C00 orange vs #7CB342 green | 1.08 | 46.1 | **8.4** | **6.9** | 50.7 | 13.0 |
| #1E88E5 blue vs #8E24AA purple | 1.91 | 38.2 | 23.1 | 13.7 | 56.9 | 19.5 |

**Threshold** `[policy]`:
- Distinct: ΔE00 ≥ 10 after simulation.
- Marginal: 5–10.
- Confusable: < 5.
- Between-state luminance: ≥ 3:1 (G183).

**Severity.**

| Condition | Severity |
|---|---|
| 1.4.1 failure (no cue, < 3:1 between states) on a critical state: error vs valid, destructive vs safe, game ally vs enemy, required-field marker | P1 (normative failure for every user) |
| Same failure on a non-critical state | P2 |
| CVD-simulated confusable (< 5) only for a persona, with a cue present | No finding |
| CVD marginal (5–10) with no cue | P3 |

**Cannot automate.**
- Whether a colour difference *carries meaning*, as opposed to being decorative.
- Whether the non-colour cue is itself understandable. A tiny icon can technically exist and still not work.
- Real CVD appearance varies by individual. The simulation is not a percept.

**Validity limits.**
- Machado is less validated for tritan.
- ΔE00 was fitted on large patches under controlled viewing. Small marks need larger differences.
- Display gamut and brightness change the simulated result.

### PC-05 Text size and legibility as visual angle (Latin and Hangul)

**Claim and sources.**
- **Legge & Bigelow (2011), JOV "Does print size matter for reading?"** `[snippet]`:
  - critical print size (CPS) for normal vision has a consensus value of **0.2° x-height**, ranging 0.15–0.3° by individual and font;
  - the fluent range spans 0.2–2°;
  - CPS is at least 2× acuity size.
- **MNREAD** measures reading acuity, maximum reading speed and CPS, with 0.1 log-unit steps `[snippet]`.
- **Hangul.**
  - He, Baek & Legge (2018), Vision Research 150:8–14: **CPS is larger for Korean than for English** at every eccentricity. Maximum RSVP reading speed is similar at the fovea (713 vs 787 wpm). From 0° to 10°, max reading speed falls 6.5× for Korean vs 2.8× for English. The explanation offered is within-character crowding `[snippet]`.
  - Korean J Cognitive Psychology 27(3):367–384 (2015), on-screen Hangul: **CPS 0.41° (young) vs 0.52° (older adults)**. Max reading speed was 296 vs 208 wpm `[snippet; authors not captured; KCI ART002014698]`. Whether the angle is character height or font size is **unconfirmed**.
  - Korean MNREAD (Kim, Kim & Kim 2024, Sci Rep 14:7429), 20–35-year-olds: every subject's CPS was ≤0.2 logMAR. Max reading speed 174 ± 29 wpm `[snippet]`.
- **Guidance.**
  - KRDS: body text **≥16 px**. The standard style uses **17 px** as the default because Pretendard GOV renders relatively small `[snippet: krds.go.kr]`.
  - Apple HIG: default body 17 pt, minimum 11 pt `[recalled]`.
  - Material 3: Body Large 16 sp, Body Medium 14 sp, Body Small 12 sp `[recalled]`.
  - WCAG 1.4.4: text resizable to 200% without loss `[primary: WCAG 2.0 text]`.

**Unit bridge** (`[derived]`):
- The CSS reference px is 1/96 in at 28 in, i.e. 0.0213° = **1.28′**. apca-w3 states 1.278′ `[primary]`.
- 16 px at the reference geometry = 24.3′ em. With a Latin x-height ratio of ≈0.5, that is ≈12′ x-height = **exactly the 0.2° CPS**, with no reserve.
- Phone at ≈153 CSS px/in (≈460 ppi at 3×): 16 px = 36.5′ at 25 cm, 30.4′ at 30 cm, 22.8′ at 40 cm, **18.3′ at 50 cm**, 15.2′ at 60 cm.
- Desktop at 96 CSS px/in and 60 cm: 16 px = 24.3′.
- A 55″ 1080p TV at 2.7 m: 24 px = 19.4′. TV UI needs much larger type.

**Inputs.**
- Rendered font size in CSS px, after OS scaling.
- The font's x-height ratio and cap/Hangul glyph height, from font metrics (`OS/2` sxHeight and capHeight) or measured from the glyph raster.
- Device physical CSS-px density from the device catalog.
- The persona's viewing distance.

**Algorithm.**
1. Physical size: size_mm = px × 25.4 / css_ppi.
2. Visual angle: angle′ = 2·atan(size_mm / 2d) × 60.
3. Compare on the **same metric as the criterion**:
   - Latin text: x-height angle vs 12′ (0.2°);
   - Hangul text: glyph-height or font-size angle vs 24.6′ (young, 0.41°) or 31.2′ (older, 0.52°), with the metric caveat above.
4. Report the **acuity reserve** = angle / CPS. Legge's "≥2× acuity" argument means a reserve below 1 predicts slowed reading. For low-vision personas, require reserve ≥ 1 at *their* CPS.

Text size (CSS px on a 153-px/in phone) that reaches each CPS `[derived]`:

| Distance | 24′ em (Latin 0.2° x-height at 0.5 ratio) | 24.6′ (Hangul young) | 31.2′ (Hangul older) |
|---|---|---|---|
| 30 cm | 12.6 px | 12.9 px | 16.4 px |
| 40 cm | 16.8 px | 17.2 px | 21.9 px |
| 50 cm | 21.0 px | 21.6 px | 27.3 px |

**Threshold** `[policy]`. Body text below the persona's CPS (reserve < 1) is a finding. For reference, KRDS says 16 px minimum (Korean public-sector norm).

**Severity.**

| Condition | Severity |
|---|---|
| Critical information below CPS for the persona (price, dose, legal consent, error text, OTP) | P1 |
| Body text below CPS | P2 |
| Below KRDS 16 px but above CPS | P3 |
| HUD or game text below CPS during time-pressured play | P2 (P1 if needed to proceed) |

**Cannot automate.**
- Font legibility beyond size: stroke contrast, counters, hinting, Hangul jamo design.
- Whether small text is intentionally "fine print" that is still necessary.
- Reading comprehension.

**Validity limits.**
- CPS values come from high-contrast continuous-text reading. Low contrast or thin weights raise CPS.
- Glanceable UI labels are not the same task as sentence reading.
- The Hangul CPS metric definition is unconfirmed. Treat the 0.41°/0.52° values as the metric-uncertain ranges shown in the table.

### PC-06 Text spacing, line length and reflow (1.4.12, 1.4.8, 1.4.10, 1.4.4)

**Claim and sources.**
- **1.4.12 (AA, WCAG 2.1).** No loss of content when the user sets:
  - line-height ≥1.5× font size;
  - paragraph spacing ≥2×;
  - letter spacing ≥0.12×;
  - word spacing ≥0.16×.
  - axe-core 4.13.0 encodes line-height 1.5, letter 0.12 and word 0.16 `[primary]`; the 2× paragraph value is `[recalled]`.
- **1.4.8 (AAA).** Per WCAG 2.0 text `[primary]`:
  - width ≤80 characters, **or 40 for CJK**;
  - not justified;
  - line spacing ≥1.5, and paragraph spacing ≥1.5× line spacing;
  - resize to 200% without horizontal scrolling.
- **1.4.10 Reflow (AA).** No two-dimensional scrolling at a 320 CSS px width `[recalled]`.
- **1.4.4 (AA).** 200% text resize `[primary]`.

**Inputs.** DOM, and the ability to inject CSS or set OS font scale (Android font scale 1.3 / 2.0; iOS Dynamic Type accessibility sizes).

**Algorithm.**
1. Inject the 1.4.12 bookmarklet CSS. Re-snapshot, and detect:
   - clipped text: `scrollWidth > clientWidth` with overflow hidden;
   - overlap between text boxes;
   - truncation ellipses that were not present before.
2. Set a 320 px viewport and detect horizontal scroll.
3. Set OS font scale to 200% on native apps, and look for truncated labels or buttons pushed off-screen.
4. Line length: characters per line (measure the line boxes). Flag Hangul > 40 or Latin > 80 per line for body text as P3 (AAA).

**Severity.**
- Content or controls lost at 1.4.12, 1.4.4 or 1.4.10: **P1** when critical, **P2** otherwise.
- Line length: P3.

**Cannot automate.**
- Whether truncated text is still understandable (e.g. "주문 확…" for "주문 확인", "confirm order").

**Validity limits.**
- Line-length evidence for screens is mixed. Longer lines can be read faster but are rated worse (Dyson 2004) `[recalled]`. The 40-CJK rule is a standards convention, not a Hangul-specific finding.

### PC-07 Presbyopia and near focus (persona-conditioned viewing distance)

**Claim and sources.**
- Accommodation amplitude declines linearly with age. Hofstetter (1950), from Duane's data `[recalled]`:
  - minimum A = 15 − 0.25 × age D;
  - average A = 18.5 − 0.3 × age D;
  - maximum A = 25 − 0.4 × age D.
- Comfortable sustained near work uses about half the amplitude `[recalled; clinical rule]`.
- Global presbyopia was ≈1.8 billion people in 2015 (Fricke et al. 2018, Ophthalmology) `[recalled]`.
- Korean presbyopia prevalence by age: **unconfirmed** (not found at the time of writing).
- The older retina receives much less light: ≈1/3 at 60 vs 20 (Weale) `[recalled]`. That reduces contrast sensitivity, so presbyopia interacts with PC-01 and PC-08.
- Korea became "super-aged" with ≥20% of residents 65+ in December 2024 `[snippet via sibling motor-pointing brief]`.

**Derived near points** (uncorrected, from minimum amplitude) `[derived]`:

| Age | Minimum amplitude | Near point | Comfortable (half amplitude) |
|---|---|---|---|
| 40 | 5.0 D | 20 cm | 40 cm |
| 45 | 3.75 D | 27 cm | 53 cm |
| 50 | 2.5 D | 40 cm | 80 cm |
| 55 | 1.25 D | 80 cm | — |
| ~60+ | ≈0 D | — | — |

- With **average** amplitude, age 50 gives a near point of 29 cm and a comfortable distance of 57 cm.

**Operationalisation.**
- Persona fields: `presbyopia: {age, correction: none|readers|progressive|multifocal_iol, correction_available_in_context: bool}`.
- If uncorrected in the scenario (e.g. outdoors without glasses), set viewing distance = min(max(comfortable_distance, 30 cm), arm-reach cap ≈ 50–60 cm `[assumption]`). Re-run PC-05 at that distance.
- Where the needed distance exceeds the arm-reach cap, the text is also optically blurred. Report "blur-limited", and require OS text scaling support (PC-06).
- Progressive-lens wearers read through the lower lens zone. Screen tilt and position matter, but this is **not quantifiable** here.

**Severity.** As PC-05 at the adjusted distance. A failure only under the "no glasses available" scenario is capped at P2 unless the content is critical *and* typically used on the go (e.g. a transit ticket or payment QR screen).

**Validity limits.**
- Hofstetter's lines are population norms with wide individual spread.
- Screen luminance and pupil size change depth of field.
- Many people over 45 are corrected. The persona must state correction status explicitly; never assume it.

### PC-08 Glare and sunlight (situational contrast)

**Claim and sources.**
- Reflected ambient light adds to both text and background luminance and compresses contrast.
- Physical model: L_reflected = ρ·E/π. This holds for a diffuse (Lambertian) reflectance ρ under illuminance E `[recalled; standard photometry]`.
- The WCAG +0.05 term already models a *nominal* flare `[recalled]`.
- Ambient levels: offices ≈300–500 lx; overcast daylight ≈10³–10⁴ lx; direct sun ≈3×10⁴–10⁵ lx `[recalled; typical photometric values]`.
- Phone peak luminance: device-specific, check the catalog. ρ for phone cover glass with AR coating: **unconfirmed** (2% used below as an assumption).

**Worked example** (`[derived: glare.py]`, ρ = 0.02 and black level 0.5 cd/m² `[assumption]`):

| Text on white | WCAG | 1000 nit display, 10 klx | 1000 nit, 50 klx | 2000 nit, 50 klx | 2000 nit, 100 klx |
|---|---|---|---|---|---|
| #767676 (AA) | 4.54 | 4.34 | 2.64 | 3.40 | 2.64 |
| #595959 (AAA) | 7.00 | 6.49 | 3.15 | 4.47 | 3.15 |
| #000000 | 21 | 16.6 | 4.14 | 7.27 | 4.14 |

- In direct sun, only very dark text on a bright display keeps ~3:1.
- To keep an ambient 4.5:1 at 50 klx on a 2000-nit display, you need text with WCAG ≈ 7:1 against white. The same target is impossible on a 1000-nit display at 50 klx `[derived]`.
- ergoqa's `CONTRAST_BRIGHT_LIGHT = 7.0` is therefore consistent with *one* assumption set. It is not a standard.

**Algorithm.**
- Persona or scenario `ambient_lux`, and device `peak_nits` and `rho`.
- Convert relative luminance to absolute: L = L_black + Y·(L_peak − L_black) + ρE/π.
- Compute ambient contrast. Compare with 3:1 (large or non-text) and 4.5:1 (text).

**Severity.** Capped at **P2**, because the device and environment dominate. Report it as a "margin" finding: P3 by default, P2 for critical outdoor-use screens (maps, transit, payment QR, camera shutter UI).

**Cannot automate.**
- Specular glare geometry, polarised sunglasses (which black out some LCDs at certain angles), and the user's shading behaviour.

**Validity limits.**
- The model ignores auto-brightness boosting and the eye's adaptation state. ρ is unmeasured.
- Use it only as relative stress-testing.

### PC-09 Reading time for transient messages (toasts, snackbars) and time limits (2.2.1, 2.2.2)

**Claim and sources.**
- **WCAG 2.2.1 (A).** For each time limit set by content, at least one must hold `[primary]`:
  - the user can turn it off;
  - the user can adjust it (≥10× default);
  - the user is warned and gets **≥20 s** to extend with a simple action, at least 10 times;
  - there is a real-time or essential exception;
  - the limit is >20 h.
- A W3C-sourced example says a toast that disappears after 5 s is *not* a time limit **if the same information is available elsewhere** (e.g. the inbox). The snippet did not show whether this comes from the Understanding 2.2.1 page or from the w3c/wcag issue #976 discussion. The text is `[snippet]`; its exact source page is `unconfirmed`.
- **2.2.2 (A).** Moving, blinking or scrolling content that starts automatically, lasts **>5 s** and runs in parallel with other content must be pausable, stoppable or hideable `[primary]`.
- **4.1.3 Status messages (AA).** Toasts must be announced to assistive technology without moving focus `[snippet]`.
- **Platform durations** `[snippet]`:
  - Android `Toast.LENGTH_SHORT` ≈2 s, `LENGTH_LONG` ≈3.5 s;
  - Material Components snackbar short 1.5 s, long 2.75 s;
  - Material guidance 4–10 s;
  - React Aria recommends a ≥5 s minimum and warns against auto-dismissing anything that needs reading.
  - Android 10+ exposes the user's "Time to take action" setting via `AccessibilityManager.getRecommendedTimeoutMillis` `[recalled]`.
- **Korean reading rates.** All "WPM" in Korean studies are **assumed to be 어절 (space-delimited word units) per minute**. The syllables-per-어절 figure of 2.91 comes from the JKOS 2016 sentence statistics (18.9 syllables / 6.5 어절) `[snippet → derived]`.

| Source | Measure | Syllables/min `[derived]` | Syllables/s `[derived]` |
|---|---|---|---|
| JKOS 2016 57(4):642–649, iPad at 40 cm, 10 pt, silent | 202.3 ± 88.4 WPM `[snippet]` | 587 (mean); 330 (−1 SD) | 9.8; 5.5 |
| KJCP 2015, young vs older, max rate | 296 vs 208 wpm `[snippet]` | older ≈ 0.70 × young | — |
| Korean MNREAD in elderly **patients** | ≈100 WPM `[snippet]` | ≈290 | 4.8 |
| English adult silent reading (Brysbaert 2019, 190 studies) | 238 wpm non-fiction, 260 fiction, 183 aloud `[snippet]` | — | — |

**Algorithm** (ergoqa already implements this form):

```
t_needed = t_orient + N_hangul_syllables / r_syl + N_latin_words / r_wpm
t_required = max(TOAST_FLOOR, t_needed × safety)
```

Read `t_shown` from the action trace, using the first and last frames containing the toast box.

**Worked example** (`[derived]`, t_orient 0.5 s `[assumption]`, safety 1.5 `[policy]`):
- "장바구니에 상품이 담겼습니다" ("Item added to cart", 13 syllables):
  - slow older reader at 290 syl/min: (0.5 + 2.7) × 1.5 = **4.8 s**;
  - mean adult at 587 syl/min: 2.7 s, which the 4 s floor overrides.
- A 40-syllable error toast for a slow reader needs ≈13 s. That exceeds Material's 10 s maximum, so it should not be a toast.

**Threshold.**
- t_shown ≥ t_required for the persona's **slow-reader percentile**, not the mean.
- Additionally, if the toast contains an **action** (Undo) or **information not available elsewhere**, it is a 2.2.1 time limit. It must persist until dismissed or honour the OS timeout setting.

**Severity.**

| Condition | Severity |
|---|---|
| Toast with a unique critical message (error cause, OTP, reservation number) or an Undo action that auto-dismisses, violating 2.2.1 | P1 |
| t_shown < t_required for a persona, informational message available elsewhere | P3 |
| Same, but the message is the only feedback for a completed action | P2 |
| Auto-moving carousel >5 s with no pause | P2 (2.2.2 A); P1 if it contains the primary CTA |

**Cannot automate.** Whether the information is "available elsewhere". That needs a flow model or human review.

**Validity limits.**
- Korean rates come from small samples and sentence-reading tasks, and the units are uncertain.
- Toasts appear in the periphery; noticing time (t_orient) is **unconfirmed**. See the gaze brief for UFOV.

### PC-10 Response time and required feedback

**Claim and sources** (all `[recalled]`; NN/g fetch was blocked):
- Miller (1968), "Response time in man-computer conversational transactions", AFIPS FJCC 33:267–277.
- Card, Robertson & Mackinlay (1991): about 0.1 s perceptual processing, 1 s immediate response, 10 s unit task.
- Nielsen (1993), *Usability Engineering*:
  - **0.1 s**: the system feels instantaneous; no feedback needed beyond showing the result;
  - **1 s**: the flow of thought stays uninterrupted, though the delay is noticed;
  - **10 s**: the limit for keeping attention. Longer delays need a percent-done indicator and a way to interrupt.
  - Between 2 and 10 s, show a busy indicator.
- Doherty & Thadani (1982), IBM: productivity rises sharply when system response is **< 400 ms**.
- Google Web Vitals, at the 75th percentile: INP ≤200 ms good, >500 ms poor; LCP ≤2.5 s good, >4 s poor; CLS ≤0.1 good, >0.25 poor.
- Nah (2004): users' tolerable waiting time for web pages ≈2 s.

**Inputs.** Action trace with timestamps for:
- `t_input` (pointer-up or key-down, from the driver);
- `t_ack`: the first frame whose pixels change inside the target or a feedback region (pressed state, ripple, spinner);
- `t_ready`: the frame at which the next state is stable and interactive, e.g. no layout shift for 500 ms `[policy]`.

Web targets also have the Event Timing API (INP) and PerformanceObserver. Native targets have Perfetto/systrace, or ≥60 fps screen recording.

**Algorithm.**
1. Latency_ack = t_ack − t_input. Latency_ready = t_ready − t_input.
2. Classify, and check that the required feedback exists:

| Latency_ready | Required feedback |
|---|---|
| ≤ 0.1 s | Pressed or immediate state change |
| ≤ 1 s | Acknowledgement within 0.1 s |
| 1–10 s | Indeterminate indicator within ≤ 1 s (spinner or skeleton) |
| > 10 s | Determinate progress, a cancel or background option, and a completion notice |

3. Also detect **double activation**: a second input on the same target before t_ready.

**Severity.**

| Condition | Severity |
|---|---|
| No acknowledgement within 1 s on a submit or payment, and a duplicate submission was **observed** | P1 |
| Same, and a duplicate charge or order is structurally possible (no idempotency visible) | P0 |
| No indicator for 1–10 s waits on the primary path | P2 |
| > 10 s with no progress or cancel | P1 |
| t_ack > 0.1 s on direct manipulation (drag, scroll, typing echo) | P2 |
| Latency above the 400 ms Doherty threshold | P3 (relative comparison) |

**Cannot automate.**
- Whether perceived waiting is acceptable in context (e.g. users expect payment to take time).
- Whether an animation masks latency acceptably.

**Validity limits.**
- The thresholds are rules of thumb synthesised from 1960s–1990s work, not psychophysical constants.
- Screenshot polling has too coarse a resolution. Frame-accurate capture (≤16.7 ms) is required for the 0.1 s class.

### PC-11 Choice complexity: Hick–Hyman law and choice overload

**Claim and sources** (`[recalled]`):
- Hick (1952, QJEP 4:11–26) and Hyman (1953, JEP 45:188–196): choice reaction time rises linearly with stimulus information, **RT = a + b·H**. For n equiprobable alternatives, H = log₂(n + 1) (Hick, which counts "no signal") or log₂ n (Hyman).
- Card, Moran & Newell (1983), Model Human Processor: I_c ≈ **150 ms/bit** (range 0–157).
- The intercept a is task-specific. ergoqa's 200 ms is a placeholder.
- Hick–Hyman applies to **practised, known, equiprobable mappings**. For unfamiliar menus, visual search is roughly linear in n. Cockburn, Gutwin & Greenberg (2007, CHI) model menus as a transition from novice linear search to expert Hick–Hyman decisions.
- Landauer & Nachbar (1985): selection time in broad menus follows a log relationship, which favours breadth over depth.
- "Choice overload": Iyengar & Lepper (2000) jam study (24 vs 6 options). But the Scheibehenne, Greifeneder & Todd (2010) meta-analysis found a **mean effect ≈0** with high moderator dependence.

**Inputs.**
- Interactive elements at a decision point, grouped by visual equivalence (same role, size and style). ergoqa's `check_choice_overload` does this.
- Persona expertise (novice or expert with the app).

**Algorithm.** Relative comparison only:
- Expert personas: T_decide = a + b·log₂(n + 1).
- Novice personas: T_search ≈ c·n/2 for self-terminating search. c per item is **unconfirmed**; calibrate from observed dwell.
- Compare flows A vs B, or before vs after.
- Flag when n is large **and** the items lack grouping or headings. Grouping reduces the effective n (see PC-13).

**Threshold.** No literature constant. ergoqa's `CHOICE_OVERLOAD_MAX = 9` is `[policy]`. It is borrowed from Miller's span, which does **not** apply to visible options (see §5).

**Severity.**
- Model alone: **P3**.
- P2 when observed persona traces show long dwell, back-and-forth, or wrong selection at that decision point.

**Cannot automate.**
- Whether options are meaningfully distinct, whether defaults are sensible, and information scent.

**Validity limits.** Parameters come from lab choice-reaction tasks and do not transfer directly to real menus. Use them for ranking designs only.

### PC-12 Working-memory load and recognition vs recall

**Claim and sources** (`[recalled]`):
- Miller (1956): span of absolute judgement and immediate memory ≈7 ± 2, with chunking.
- **Cowan (2001, BBS 24:87–185): a capacity of about 4 ± 1 chunks** when rehearsal and chunking are controlled.
- Peterson & Peterson (1959): recall of consonant trigrams with distraction falls to ≈10% after 18 s.
- Recognition is easier than recall. This is Nielsen's heuristic 6, "recognition rather than recall" (1994).
- Icons with text labels outperform icon-only controls for novices (Wiedenbeck 1999).
- Card, Moran & Newell (1983): working-memory capacity ≈3 chunks pure (7 with LTM support); decay half-life ≈7 s for 3 chunks.
- WCAG 2.2 adds `[recalled]`:
  - **3.3.7 Redundant Entry (A):** do not make users re-enter information they already gave in the same process;
  - **3.3.8 Accessible Authentication (Minimum) (AA):** no cognitive function test (memorising or transcribing) without an alternative or assist. Allowing paste and password managers counts as an assist.
- KWCAG 2.2 has corresponding new items, "접근 가능한 인증" (accessible authentication) and "반복 입력 정보" (repeated input information) `[recalled; the snippet confirms that 2.2 added items]`.

**Inputs.**
- Screen sequence text (OCR or DOM) and input fields.
- Clipboard and paste permission, and autofill attributes (`autocomplete="one-time-code"`, Android SMS Retriever).

**Algorithm.**
1. **Cross-screen carry.**
   - Find tokens shown on screen i (codes, amounts, addresses, reference numbers) that are required as input or comparison on screen j > i and are not visible on j.
   - Estimate chunks, e.g. digits grouped by display separators; an ungrouped 6-digit OTP ≈ 2–3 chunks `[assumption]`.
   - Measure the carry duration from trace timestamps.
2. **Paste blocked** on password or OTP fields: test by an actual paste action, then check 3.3.8.
3. **Re-entry.** The same datum is requested twice in a flow, with no prefill or selection (3.3.7).
4. **Recall-dependent navigation.**
   - Icon-only primary navigation without labels.
   - Gestures with no visible affordance.
   - Settings where the current state is not shown.

**Threshold** `[policy]`:
- More than 4 chunks carried: flag.
- Any carry across a screen change with a delay > 10–18 s (Peterson range) without re-display: flag.
- Any paste block on authentication fields: flag (normative).

**Severity.**

| Condition | Severity |
|---|---|
| Paste or autofill blocked on an authentication or OTP field (3.3.8) | P1 |
| Re-entry without prefill (3.3.7) | P2 |
| Cross-screen carry > 4 chunks | P2 |
| Carry ≤ 4 chunks with a long delay | P3 |
| Icon-only primary navigation | P3; P2 for novice or older personas when traces show misses |

**Cannot automate.**
- Whether an icon is recognisable (vision-LLM or human judgement, preferably tested with real users).
- Whether a datum "must" be remembered.

**Validity limits.**
- Chunk counts depend on familiarity. For example, a phone-number format is a single chunk to Koreans (010-XXXX-XXXX).

### PC-13 Gestalt grouping (proximity, common region, similarity)

**Claim and sources** (`[recalled]`):
- Wertheimer (1923) identified proximity, similarity, continuity, closure and common fate.
- Palmer (1992) added **common region**; Palmer & Rock (1994) added **uniform connectedness**.
- Grouping by proximity depends on the **ratio** of inter-element distances (Kubovy & Wagemans 1995; Kubovy & van den Berg 2008).
- Review: Wagemans et al. (2012), *Psychological Bulletin*.
- No UI-level numeric threshold is standardised.

**Inputs.** Element boxes, text boxes, container boxes (borders or background fills), and label associations: `<label for>`, `aria-labelledby`, Android `labelFor`.

**Algorithm.**
1. **Label–control ambiguity.** For each visible label ℓ and its programmatic control c, compute d_own = edge distance(ℓ, c) and d_other = min distance(ℓ, any other control). Ratio r = d_own / d_other.
2. **Group separation.** For clustered items, the between-group gap divided by the median within-group gap.
3. **Common region consistency.** Items of one radio or checkbox group should share a container. Items of different groups should not share one without a divider.
4. **Similarity conflicts.** Elements with the same visual signature (colour, shape, size) but different function, e.g. a link styled like body text, or a destructive button styled like the primary one.

**Threshold** `[policy — no literature constant]`:
- r ≥ 1: label is closer to another control, "ambiguous";
- 0.8 ≤ r < 1: "weak";
- between-group/within-group gap < 1.5: "weak separation".

**Severity.**
- Ambiguous label on a form field, or a similarity conflict on a destructive action: P2.
- Weak separation: P3.
- Structural mislabel where the programmatic label ≠ the visually nearest label: P1, because screen-reader users and sighted users get different answers.

**Cannot automate.**
- Whether the designer's grouping matches the user's mental model.
- Competing cues, for example alignment vs proximity, or when colour overrides spacing.
- A vision-LLM can propose groupings, but these are `judgment`.

**Validity limits.** Ratio effects are shown for dot lattices. Transfer to UI layouts is plausible but not quantified.

### PC-14 Human-error taxonomy and error-tolerant design

**Claim and sources** (`[recalled]`):
- Norman (1981, *Psychological Review* 88:1–15) and Norman (2013, *The Design of Everyday Things*):
  - **slips** are action-based: capture, description-similarity, mode errors;
  - **memory lapses**;
  - **mistakes**: rule-based, knowledge-based, and memory-lapse mistakes.
- Reason (1990, *Human Error*), GEMS: slips and lapses are skill-based. Rule- and knowledge-based mistakes are the others. **Violations** are deliberate.
- Rasmussen (1983) defines the skill/rule/knowledge (SRK) levels.
- Byrne & Bovair (1997): the **post-completion error** is forgetting a final step after the main goal is met, such as leaving a card in an ATM.
- Error-handling SCs `[primary: WCAG 2.0 text]`:
  - **3.3.1** errors are identified and described in text;
  - **3.3.4** legal, financial and data submissions are reversible, checked or confirmed;
  - 3.2.2: changing a setting does not change context unexpectedly.

**Inputs.**
- Action trace: target, timestamp, resulting screen, undo or back events.
- The persona's declared intended goal and plan (from the scenario).
- The DOM or state model: modes, toggles, destructive actions, confirmation dialogs.

**Algorithm** (trace-level classifiers, all `[policy]`):

| Class | Detection rule |
|---|---|
| **Slip (capture or description-similarity)** | Activation of element B ≠ intended A, where A and B are adjacent or visually similar (PC-13 signature), followed within ≤ 3 s `[policy]` by back, undo or cancel. Cross-reference `motor-pointing` MP-03/MP-14 to separate motor misfire from perceptual similarity. |
| **Mode error** | The same input yields different outcomes depending on hidden state, and the mode indicator fails PC-02 (< 3:1) or lies outside the gaze or UFOV region (see the gaze brief). |
| **Lapse or post-completion** | A required step comes after the goal state appears ("done"-looking screen, but "submit" or "save" still needed). Or the persona abandons the task without completing an explicit final step. |
| **Mistake (rule- or knowledge-based)** | Persistent wrong path, e.g. ≥ 2 wrong branches before the right one, driven by labels. Requires semantic judgement about why the path was chosen. |
| **Error-handling quality** | Error message present in text (3.3.1). Error adjacent to the field and announced (4.1.3). A suggestion given (3.3.3 AA `[recalled]`). Legal, financial or data actions reversible or confirmed (3.3.4 AA). |

**Severity.**

| Condition | Severity |
|---|---|
| Irreversible destructive, financial or legal action reachable by a single slip with no confirm or undo | P0 (structural path to harm) |
| Missing 3.3.1 error identification on a critical form | P1 |
| Mode error with an invisible mode indicator | P1 when the consequence is data loss, otherwise P2 |
| Post-completion trap on a critical flow | P2 |
| Mistakes | P2 when observed repeatedly across personas, otherwise P3 |

**Cannot automate.**
- Assigning intent. Slip vs mistake depends on what the user meant.
- LLM personas have *declared* intents. Real users' intents must be inferred.
- A persona's errors are hypotheses, not error rates.

**Validity limits.** Taxonomies are descriptive and categories overlap. Use them for design remedies, not for statistics.

### PC-15 Flashing and red flash (WCAG 2.3.1 A, 2.3.2 AAA; KWCAG 6.3.1; broadcast)

**Claim and sources.**
- **2.3.1 (A).** Content does not flash more than three times in any one-second period, or the flash is below the general-flash and red-flash thresholds `[primary: WCAG 2.0 text]`.
- **Glossary** `[recalled]`:
  - **General flash:** a pair of opposing changes in relative luminance of **≥10% of maximum (0.1)**, where the darker image's relative luminance is **< 0.80**.
  - **Area:** the combined area of concurrent flashes must not exceed **0.006 sr within any 10° visual field** (25% of any 10° field) at typical viewing distance.
  - **Legacy approximation:** a 341 × 256 px rectangle on a 1024 × 768 display, for a 15–17″ screen at 22–26″.
  - **Red flash:** a pair of opposing transitions involving a saturated red.
    - WCAG 2.0/2.1 working definition: R/(R+G+B) ≥ 0.8, and a change in (R−G−B)×320 > 20.
    - WCAG 2.2 note: one state has R/(R+G+B) ≥ 0.8, and the change is > 0.2 in the CIE 1976 UCS chromaticity diagram (ISO 9241-391).
- **2.3.2 (AAA):** no more than three flashes regardless of size `[recalled]`.
- **2.3.3 (AAA):** see PC-16.
- **KWCAG 6.3.1:** no content flashing at **3–50 Hz** `[recalled]`. Any area exception: **unconfirmed**.
- **Broadcast (ITU-R BT.1702 and Ofcom):** absolute luminance changes of ≥20 cd/m² where the darker state is < 160 cd/m². Area > 25% of the *screen*. Also spatial patterns (stripes) `[recalled]`.
- Photosensitive epilepsy is roughly 1 in 4,000 people `[recalled; order-of-magnitude only]`.

**Geometry** (`[derived: calc.py]`):
- A 10° circular field subtends 2π(1 − cos 5°) = **0.0239 sr**. 25% of that is **0.00598 ≈ 0.006 sr**, which is where the WCAG number comes from.
- Legacy check: 10° spans 290–388 px of 1024 across 15–17″ at 22–26″, consistent with 341 px. The area threshold within 341 × 256 ≈ 21,800 px².
- Modern devices: compute from physical density and distance. At the CSS reference px (1.28′), 10° = 469 px.

| Device (CSS px/in), distance | 10° span | 25% of 10° circle |
|---|---|---|
| Phone (153), 25 cm | 263 px | 13,600 px² |
| Phone (153), 30 cm | 315 px | 19,500 px² |
| Phone (153), 40 cm | 421 px | 34,700 px² |
| Desktop (96), 60 cm | 396 px | 30,800 px² |

- On a 390-px-wide phone at 30 cm, a single 140 × 140 px flashing tile reaches the limit.

**Inputs.**
- Screen recording at ≥60 fps. Flashes are counted per second, and brief frames must not be missed.
- Device physical density and persona viewing distance.

**Algorithm.**
1. Per frame, compute a relative-luminance map on a downsampled grid, e.g. 4 × 4 px cells.
2. Per cell, detect opposing transitions with |ΔY| ≥ 0.1 where min(Y) < 0.8. Separately detect red transitions using the 2.2 chromaticity rule, falling back to the 2.0 rule.
3. For each 1 s sliding window, count flash pairs per cell.
4. Take the union area of cells with more than 3 flashes/s that flash concurrently. Measure it within any 10° window: slide a circle of radius 5° converted to px.
5. **Fail** if the concurrent area is > 25% of any 10° field. Evaluate general and red flashes independently.

**Threshold.** More than 3 flashes/s **and** area > 25% of a 10° field. For AAA, or when the persona is photosensitive: more than 3 flashes/s at any size.

**Severity.**
- 2.3.1 failure: **P0**. It is a measured safety hazard, not a persona prediction.
- 2.3.2-only failure: P2.
- Broadcast-rule-only failure (e.g. a game trailer): P1 for video content.

**Cannot automate.**
- Whether the flash is part of essential content. There is no "essential" exception in 2.3.1.
- Harmful spatial patterns that do not flash (stripes, spirals) need BT.1702-type analysis, or human review.

**Validity limits.**
- Relative luminance ignores display peak luminance. The broadcast rule uses absolute cd/m².
- HDR content and variable refresh rates complicate frame analysis.
- Frame capture can miss sub-frame flicker (PWM dimming is out of scope).

### PC-16 Motion, animation and vestibular safety (2.3.3 AAA; 2.2.2 A)

**Claim and sources.**
- **2.3.3 (AAA):** motion animation triggered by interaction can be disabled, unless it is essential `[recalled]`.
- **2.2.2 (A):** auto-starting motion >5 s needs pause, stop or hide `[primary]`.
- Platform settings `[recalled]`: CSS `prefers-reduced-motion`, iOS Reduce Motion, and Android "Remove animations" (animator duration scale 0).
- Vestibular dysfunction is common in older adults. About 35% of US adults aged 40+ had evidence of vestibular dysfunction (Agrawal et al. 2009) `[recalled]`. There are **no validated numeric motion thresholds** for UI.

**Algorithm.**
1. Run each flow twice: with reduced motion off, then with it **on**. Use CDP `Emulation.setEmulatedMedia` with `prefers-reduced-motion: reduce`, or the platform setting.
2. Compute motion energy per interaction: optical-flow magnitude times area, from frames.
3. Flag if, with reduce **on**, large-area motion persists:
   - parallax, zoom or scale transitions covering > 1/3 of the viewport `[policy]`;
   - or auto-play loops > 5 s without a pause control.

**Severity.**

| Condition | Severity |
|---|---|
| 2.2.2 failure | P2 |
| 2.2.2 failure covering primary content | P1 |
| Reduce-motion ignored with large-area motion | P2 (AAA, but a health-relevant effect) |
| Small or decorative motion | P3 |

**Cannot automate.** Whether a motion is "essential", and individual susceptibility.

**Validity limits.** The 1/3-viewport rule is policy, not evidence.

### PC-17 Self-report instruments: NASA-TLX, SUS, SEQ, UMUX-Lite (policy: humans only)

**What they are** (`[recalled]`):
- **NASA-TLX** (Hart & Staveland 1988). Six subscales: mental, physical and temporal demand, performance, effort and frustration. Each is rated 0–100, and the weights come from 15 pairwise comparisons. **Raw TLX** drops the weighting (Hart 2006).
- **SUS** (Brooke 1996). Ten items on a 5-point scale, scored 0–100. The benchmark mean is ≈68 across ~500 studies (Sauro 2011). The adjective scale is from Bangor, Kortum & Miller (2009).
- **SEQ.** One 7-point item asked after each task (Sauro & Dumas 2009). The historical mean is ≈5.5 (Sauro).
- **UMUX-Lite** (Lewis, Utesch & Maher 2013). Two 7-point items. SUS-equivalent ≈ 0.65 × UMUX-Lite + 22.9.

**Why an LLM persona must not fill these in as measurements:**
1. **Construct validity.** Each instrument operationalises a *respondent's experienced* workload or satisfaction. An LLM persona has no experience, so its "rating" is a text continuation conditioned on the prompt and screen description. It is `basis: judgment`, `epistemic_status: inferred` at best.
2. **Norm leakage.** LLMs have read the SUS norms (68), the SEQ mean (5.5) and the adjective bands. Outputs may regress to published averages rather than track the design (a hypothesis; not measured here).
3. **Distortions documented in "silicon sample" research** `[recalled]`:
   - reduced variance, and sensitivity to prompt wording and model version (Bisbee et al. 2024, *Political Analysis*);
   - "hyper-accuracy" distortion (Aher, Arriaga & Kalai 2023, ICML);
   - misportrayal and flattening of identity groups (Wang, Morgenstern & Dickerson 2025, *Nature Machine Intelligence*).
   - Argyle et al. (2023, *Political Analysis*) report "algorithmic fidelity" for some aggregate attitudes, which shows the question is contested. It still does not validate per-respondent workload ratings.
4. **Statistics.** N personas are not N independent participants. Confidence intervals, benchmarks and significance tests on persona scores are meaningless, and mixing them with human data corrupts both.

**Policy for ergoqa.**
- Personas may output **structured friction predictions** tied to observed trace evidence (retries, dwell, backtracks, errors, unmet thresholds). They may label predicted friction with TLX *dimension names* (e.g. "temporal demand: toast shorter than reading time").
- Personas must not output 0–100 or 1–7 instrument scores. If a numeric summary is unavoidable, name it something else (e.g. `predicted_friction_index`) and tag it `basis: model`. Never aggregate it with human SUS, SEQ or TLX.
- Use the real instruments with real participants:
  - SEQ after each task;
  - SUS or UMUX-Lite after the session;
  - Raw TLX for time-pressured or game tasks.
- Korean-validated versions: **unconfirmed**. Check before using translations.

---

## 3. Persona dimensions (perception and cognition)

Base rates are for **plausible scenario mixes**, not claims about real-user prevalence in any product.

| Dimension | Values | Base rate (source, tag) | Test effect (checks parameterised) |
|---|---|---|---|
| `vision.cvd` | none / deutan / protan / tritan | **Korea, men:** 5.90% (HRR, JKMS 1989 `[snippet]`); 6.5% (KNHANES 2013, age 19–49, Kim et al. 2019 `[snippet]`). **Korea, women:** 0.44% / 1.1%. The 2019 figure includes "unclassified" types. **Type split, all KNHANES participants:** deutan 2.5% vs protan 0.4% (≈6:1); deutan was 64.2% of male failures `[snippet]`. **Global:** ≈8% male / 0.5% female (N. Europe); Chinese/Japanese men 4–6.5% (Birch 2012 `[snippet]`); children and adolescents pooled 2.59%, boys 4.38% (Ophthalmology 2025 meta-analysis `[snippet]`). **Tritan:** very rare, figures range from 0.0001% to ~1/10,000 across secondary sources (`unconfirmed`); use as an edge scenario only | PC-04 (sim + ΔE00), PC-02 state pairs, game team colours |
| `vision.cvd_severity` | 0.1–1.0 (anomalous) or 1.0 (dichromat) | Caucasian men: deuteranomaly ≈5%, deuteranopia ≈1%, protanomaly ≈1%, protanopia ≈1% (Sharpe et al. 1999 `[snippet]`). So ≈25% of CVD men are dichromats (European data). Korean split `unconfirmed` | Choose the tabulated Machado matrix |
| `vision.acuity` | normal / reduced (≈20/40) / low vision | 20/40 is "typical visual acuity of elders at roughly age 80" (WCAG Understanding 1.4.3 `[snippet]`) | PC-01 (AAA margin), PC-05 CPS × factor |
| `vision.presbyopia` + `correction` + `correction_available` | age; none/readers/progressive; bool | Onset ~40s; Hofstetter amplitude lines `[recalled]`. Korea 65+ ≈20% of the population (Dec 2024) `[snippet via sibling brief]`. Korean presbyopia prevalence `unconfirmed` | PC-07 changes viewing distance, which feeds PC-05 and PC-15 geometry |
| `vision.viewing_distance_mm` | phone 250–400; desktop 500–700; TV 2,000–3,000 | Smartphone text ≈36 cm and web ≈32 cm mean (Bababekova et al. 2011 `[recalled]`). ergoqa defaults are `[assumption]` | All angle-based checks |
| `context.ambient_lux` | indoor 300–500; overcast 10k; sun 50–100k | Typical photometric values `[recalled]` | PC-08 |
| `cognition.reading_rate_syl_per_min` (Korean) | by age band; use the **slow** percentile for timing checks | Adults: mean ≈587, −1 SD ≈330 (JKOS 2016 → `[derived]`). Older adults ≈0.70 × young (KJCP 2015 `[snippet]`) → ≈410 mean. Clinical elderly ≈290 (MNREAD-K `[snippet → derived]`) | PC-09 |
| `cognition.expertise` | novice / intermediate / expert (with this app) | No base rate (scenario) | PC-11 (search vs Hick), PC-12 (icon recall) |
| `cognition.wm_capacity_chunks` | 4 (default), 3 (older or distracted `[assumption]`) | Cowan 2001 `[recalled]`. Age-related decline in processing speed and WM (Salthouse 1996 `[recalled]`). The magnitude for a persona is `[assumption]` | PC-12 |
| `cognition.language` | Korean L1 / Korean L2 / English | L2 reading slower, magnitude `unconfirmed` | PC-09, PC-11 |
| `sensitivity.motion` | reduce_motion on/off; vestibular yes/no | ≈35% of US 40+ with vestibular dysfunction evidence (Agrawal 2009 `[recalled]`). Korean share `unconfirmed` | PC-16 |
| `sensitivity.photosensitive` | yes/no | ≈1/4,000 `[recalled]` | PC-15 at AAA strictness (any 3+ flashes/s) |
| `attention.state` | focused / interrupted / dual-task (walking, transit) | Scenario | PC-09 t_orient ↑, PC-12 carry delay ↑, PC-14 lapse risk |

**Sampling guidance.**
- Sample CVD for male personas at ≈6% and female personas at ≈0.5–1%, with deutan:protan ≈6:1 (Korea).
- Always run one **deuteranopia** and one **protanopia** stress persona, whatever the sampled mix. Deutan and protan confusions differ: see orange/green above, where protan ΔE00 8.4 vs deutan 6.9.

---

## 4. Non-automatable judgments (need a human or vision-LLM; `basis: judgment`)

- **Meaning of colour.** Whether a colour difference encodes information, and whether a non-colour cue is understandable.
- **Essential exceptions.** Incidental or logo text (1.4.3), essential motion (2.3.3), essential timing (2.2.1), and "information available elsewhere" for toasts.
- **Typeface legibility beyond size.** Thin weights, condensed Hangul fonts, stylised game fonts, and text over busy art where OCR confidence is low.
- **Icon recognisability** and label clarity (recognition vs recall). This is best validated with real users of the target culture and age.
- **Grouping intent vs the user's mental model** (Gestalt). Also information scent and whether choices are meaningfully distinct.
- **Error intent.** Slip vs mistake.
- **Harm assessment.** Whether an action is "irreversible" in business terms, e.g. an order that can be cancelled within 10 minutes.
- **Subjective workload and satisfaction** (TLX, SUS, SEQ, UMUX-Lite): humans only.
- **Pattern-sensitive epilepsy risk** from static patterns, vestibular discomfort, and glare behaviour (shading, tilting).
- **Whether a presbyopic persona would realistically have glasses available** in the scenario. This is a scenario-authoring judgement.

---

## 5. Contradictions and uncertainties

1. **WCAG 2 vs APCA.** They disagree on dark and mid-tone pairs and on polarity (§PC-03 table). WCAG 2 remains the legal and compliance standard. APCA is advisory and not in the WCAG 3 WD. Vendor claims about WCAG 3 timing (Recommendation around 2029) are `unconfirmed`.
2. **KWCAG vs WCAG.** KWCAG 2.2 lets zoomable text drop to 3:1 `[snippet]`; WCAG has no such relaxation. KWCAG's flash rule (3–50 Hz) differs in form from WCAG's area-based thresholds `[recalled]`.
3. **Korean CVD female prevalence.** 0.44% (HRR, 1989) vs 1.1% (KNHANES, 2019). The latter includes unclassified and possibly acquired defects, and has a small female case count. The male estimate is consistent (5.9–6.5%).
4. **Tritan prevalence.** Secondary sources give values from 0.0001% to ~0.01%. All are `unconfirmed`.
5. **The ΔE00 "distinct" threshold is not standardised.**
   - JND ≈ 1 applies to large, side-by-side patches.
   - The categorical palette tool uses 10.
   - Size-dependence (Szafir) implies larger values for small marks.
   - The ergoqa values 10 (`CVD_CONFUSABLE_DE`) and 20 (`CVD_DISTINCT_NORMAL_DE`) are policy.
6. **Machado severity interpolation.** It is not equivalent to the published per-severity matrices. The errors (median ~3, p95 ~7 ΔE00) are big enough to flip a 10-ΔE00 decision `[derived]`.
7. **Critical print size metric.** Legge's 0.2° is **x-height** (Latin). The Korean 0.41°/0.52° values' metric is `unconfirmed`. ergoqa compares font size (em) with 12′, which is too lenient by about 2× for Latin text `[derived]`.
8. **Miller 7±2 vs Cowan 4.** The design folklore of "≤7 menu items" misapplies memory span to *visible* options (recognition). Cowan's 4 chunks applies to information held *in mind* (PC-12), not to menus.
9. **Choice overload.** The famous jam study vs a meta-analytic mean effect ≈0. Treat choice-count checks as P3 heuristics only.
10. **Response-time limits.** These are engineering conventions, not measured human constants. The 0.1/1/10 s and 400 ms figures originate in 1968–1993 contexts. Web Vitals thresholds are Google policy based on field data.
11. **Toasts and 2.2.1.** It is contested whether auto-dismissing toasts are "time limits" (w3c/wcag #976). The decisive factor is whether the content or action is available elsewhere.
12. **Korean reading-rate units.** "WPM" in Korean studies is presumably 어절/min. That assumption drives the syllable rates. The 2015 KJCP max rates may be RSVP or other paradigms (`unconfirmed`).
13. **Glare parameters.** ρ and actual outdoor peak luminance are unmeasured. The ambient model supports relative stress tests only.
14. **Flash area on modern displays.** The 341 × 256 px legacy approximation was built for 1024 × 768 CRT/LCD geometry. Computing from CSS-reference px (10° = 469 px) gives a different number. Use the device's physical density and the viewing distance.
15. **Source verification debt.** Everything tagged `[recalled]` must be checked against the primary source before hard-coding. This includes the WCAG glossary flash definitions, G183, Hofstetter, Card/Nielsen/Doherty, Cowan and the instrument norms. Every `[snippet]` value should get a full-text read.

### Recommended updates to `ergoqa/params.py` (from this brief)

| Param (current) | Recommendation | Tag |
|---|---|---|
| `CVD_MALE_SHARE_KR = 0.059` | Keep 0.059 (1989 HRR). Record the alternative 0.065 (KNHANES 2013, age 19–49). Add `CVD_FEMALE_SHARE_KR ≈ 0.0044–0.011` | `[snippet]` |
| `CVD_TYPE_SHARE = {deutan .75, protan .24, tritan .01}` | Korea: deutan ≈0.86, protan ≈0.14 (2.5 : 0.4). Treat tritan as a scenario, not a sampled share | `[snippet → derived]` |
| `simulate_cvd` interpolation | Use the tabulated Machado matrices (0.1 steps; BSD-licensed copy in colour-science) | `[derived]` error estimate |
| `CVD_CONFUSABLE_DE = 10.0` | Keep 10 as "distinct" pass. Add 5 as "confusable". Always pair with the 3:1-between-states or non-colour-cue rule | `[snippet]` Palettailor + `[policy]` |
| `TEXT_MIN_ARCMIN = 12.0` applied to font size | Either measure x-height and compare with 12′, or compare **font size** with ≈24′ (Latin) and ≈25′ (Hangul, young) | `[derived]` |
| `TEXT_MIN_ARCMIN_PRESBYOPIA = 16.0` | Replace with ≈31′ font-size-equivalent (Hangul older CPS 0.52°), metric caveat. Also move viewing distance via PC-07 | `[snippet → derived]` |
| `CONTRAST_BRIGHT_LIGHT = 7.0` | Keep as `[policy]`. It matches one ambient model (2000 nits, 50 klx, ρ 0.02 → WCAG ≈ 7.07). Cap severity at P2 | `[derived]` with `[assumption]` |
| `HICK_A_MS = 200`, `HICK_B_MS_PER_BIT = 150` | Keep b = 150 (CMN 1983, `[recalled]`). a is task-specific; use it only for relative comparison | `[recalled]` |
| `CHOICE_OVERLOAD_MAX = 9` | Keep as P3 policy only. Remove any Miller-based justification | `[policy]` |
| `READING_SYLLABLES_PER_MIN` (600 → 350) | Means are consistent with the derived ≈587 (adult) and ≈410 (older). Add slow percentiles: ≈330 (adult) and ≈290 (older) for timing checks | `[derived]` |
| `TOAST_FLOOR_MS = 4000` | Keep; it matches the Material 4 s lower bound. Add a rule: action or unique-info toasts must not auto-dismiss (2.2.1) | `[snippet]` |
| `LATENCY_*` | Add `LATENCY_DOHERTY_MS = 400` and `INP_GOOD_MS = 200` / `INP_POOR_MS = 500` for web | `[recalled]` |
| `FLASH_*` | Correct. Add the red-flash rule (2.2 chromaticity form) and compute the 10° field from the device's physical px density × distance | `[recalled]` / `[derived]` |

---

## 6. Sources

Access tag in brackets: how it was accessed at the time of writing.

**Standards and guidelines**
- W3C. *WCAG 2.2 Understanding SC 1.4.3 Contrast (Minimum)*: 4.5:1 rationale, 20/40 ≈ age 80, 18 pt/14 pt bold, relative-luminance note (0.04045 vs 0.03928). w3.org/WAI/WCAG22/Understanding/contrast-minimum [snippet]
- W3C. *Understanding SC 1.4.6 Contrast (Enhanced)*. [snippet/recalled]
- W3C. *Understanding SC 1.4.11 Non-text Contrast*; WebAIM, "Contrast and Color Accessibility". [snippet]
- W3C. *WCAG 2.0* SC texts for 1.4.1, 1.4.4, 1.4.8, 2.2.1, 2.2.2, 2.2.4, 2.3.1, 3.2.2, 3.3.1 and 3.3.4, via npm `wcag-as-json` 0.0.1. [primary]
- W3C. *WCAG 2.1/2.2*: 1.4.10, 1.4.12, 2.3.3, 2.4.13, 3.3.7, 3.3.8, the general/red flash glossary, and technique G183. [recalled]
- W3C. *WCAG 3.0 Working Draft*, w3.org/TR/wcag-3.0/, and WCAG 3 support material "Text contrast sufficient (minimum)". [snippet]
- w3c/wcag GitHub issue #976, "2.2.1 Timing Adjustable and notifications/toasts". [snippet]
- Deque axe-core 4.13.0 source (npm): `largeTextPt 18`, `boldTextPt 14`, contrast 4.5; text-spacing minima: line-height 1.5, letter 0.12, word 0.16. [primary]
- Myndex. `apca-w3` 0.1.9 README and docs/APCA_in_a_Nutshell.md (algorithm 0.0.98G-4g): Lc levels, the font-size table notes, and "1 reference px = 1.278 arcmin". [primary]
- 한국형 웹 콘텐츠 접근성 지침 (KWCAG) 2.2: a11ykr.github.io/kwcag22 and mulder21c.io summaries. 33 items; contrast 4.5:1; 3:1 for large or zoomable text. [snippet]
- KRDS, 디지털 정부서비스 UI/UX 가이드라인 (Korean government digital-service UI/UX guidelines), Typography: body ≥16 px; standard style 17 px (Pretendard GOV). krds.go.kr/html/site/style/style_03.html [snippet]
- Apple Human Interface Guidelines, Typography; Material Design 3 type scale. [recalled]
- Material Design snackbar guidelines (m3.material.io); Android Toast and Snackbar duration constants; React Aria Toast docs. Values via the kanso-labs/kanso-ui issue #1111 and search excerpts. [snippet]
- ITU-R BT.1702; Ofcom guidance on photosensitive epilepsy. [recalled]
- Google web.dev Core Web Vitals (INP, LCP, CLS thresholds). [recalled]

**Colour vision**
- Kim et al. (2019). "Prevalence of Color Vision Deficiency in an Adult Population in South Korea." *Optometry and Vision Science*. doi:10.1097/OPX.0000000000001441. [snippet]
- "The incidence of congenital color deficiency among Koreans" (1989). *J Korean Medical Science* 4(3):117. doi:10.3346/jkms.1989.4.3.117. [snippet]
- Birch, J. (2012). "Worldwide prevalence of red-green color deficiency." *JOSA A* 29(3):313–320. [snippet]
- "Global Prevalence of Congenital Color Vision Deficiency among Children and Adolescents, 1932–2022" (2025). *Ophthalmology*. doi:10.1016/j.ophtha.2025.07.031. [snippet]
- Sharpe, Stockman, Jägle & Nathans (1999). Chapter 1 (pp. 3–52) in Gegenfurtner & Sharpe (eds.), *Color Vision: From Genes to Perception*, Cambridge UP. The title is usually cited as "Opsin genes, cone photopigments, color vision, and color blindness"; the Springer snippet cites it as "Cone genes, cone pigments…". Accessed via Springer Encyclopedia entries on protanopia and deuteranopia. [snippet]
- Machado, Oliveira & Fernandes (2009). "A Physiologically-based Model for Simulation of Color Vision Deficiency." *IEEE TVCG* 15(6):1291–1298. doi:10.1109/TVCG.2009.113. Matrices from colour-science 0.4.6, `CVD_MATRICES_MACHADO2010` (Machado 2010 thesis). [primary for matrices; snippet for paper]
- DaltonLens. "Review of Open Source Color Blindness Simulations." daltonlens.org. [snippet]
- Szafir, D. A. (2018). "Modeling color difference for visualization design." *IEEE TVCG* 24(1):392–401. [snippet]
- Lu et al. (2021). "Palettailor: Discriminable Colorization for Categorical Data." *IEEE TVCG* (arXiv 2009.02969). [snippet]
- arXiv 2404.03787, "Revisiting Categorical Color Perception in Scatterplots…" (JND ≈ ΔE00 1). [snippet]
- Sharma, Wu & Dalal (2005). "The CIEDE2000 color-difference formula: implementation notes…" *Color Res Appl*. [recalled]

**Reading, legibility and ageing**
- Legge & Bigelow (2011). "Does print size matter for reading? A review of findings from vision science and typography." *Journal of Vision* 11(5):8. [snippet]
- He, Baek & Legge (2018). "Korean reading speed: Effects of print size and retinal eccentricity." *Vision Research* 150:8–14. [snippet]
- Kim, Kim & Kim (2024). "Korean version of the MNREAD acuity chart." *Scientific Reports* 14:7429. [snippet]
- "컴퓨터 환경에서 한글 글자 크기가 청년과 노인의 읽기 속도에 미치는 영향" ("Effect of Hangul letter size on reading speed of young and older adults on computers", 2015). 한국심리학회지: 인지 및 생물 27(3):367–384. KCI ART002014698. [snippet]
- 송지호·김재형·형성민 (2016). "한국어 읽기 속도 측정 애플리케이션의 유효성 및 정상인의 읽기 속도에 대한 사전 연구" ("Validity of a Korean reading-speed app and a pilot study of normal reading speed"). 대한안과학회지 57(4):642–649. [snippet]
- Brysbaert, M. (2019). "How many words do we read per minute? A review and meta-analysis of reading rate." *J Memory and Language* 109:104047. [snippet]
- Hofstetter, H. W. (1950). Useful age-amplitude formula. *Optometry World* 38:42–45 (from Duane 1922). [recalled]
- Fricke et al. (2018). "Global prevalence of presbyopia and vision impairment from uncorrected presbyopia." *Ophthalmology* 125(10):1492–1499. [recalled]
- Bababekova et al. (2011). "Font size and viewing distance of handheld smart phones." *Optom Vis Sci* 88(7):795–797. [recalled]
- Owsley, C. (2011). "Aging and vision." *Vision Research* 51:1610–1622; Weale (1961/1963) on senile miosis and lens transmission. [recalled]
- Dyson, M. C. (2004). "How physical text layout affects reading from screen." *Behaviour & IT* 23(6):377–393. [recalled]
- Agrawal et al. (2009). "Disorders of balance and vestibular function in US adults." *Arch Intern Med* 169(10):938–944. [recalled]

**Cognition, timing and error**
- Hick (1952), *QJEP* 4:11–26; Hyman (1953), *JEP* 45:188–196. [recalled]
- Card, Moran & Newell (1983). *The Psychology of Human-Computer Interaction*. Erlbaum. [recalled]
- Cockburn, Gutwin & Greenberg (2007). "A predictive model of menu performance." CHI. [recalled]
- Landauer & Nachbar (1985). "Selection from alphabetic and numeric menu trees using a touch screen." CHI. [recalled]
- Iyengar & Lepper (2000), *JPSP* 79(6):995–1006; Scheibehenne, Greifeneder & Todd (2010), *J Consumer Research* 37(3):409–425. [recalled]
- Miller, G. A. (1956), *Psychological Review* 63(2):81–97; Cowan, N. (2001), *BBS* 24(1):87–185; Peterson & Peterson (1959), *JEP* 58(3):193–198. [recalled]
- Nielsen, J. (1994). "10 Usability Heuristics"; Nielsen (1993), *Usability Engineering*, ch. 5; NN/g "Response Times: The 3 Important Limits". [recalled; fetch blocked]
- Miller, R. B. (1968). "Response time in man-computer conversational transactions." AFIPS FJCC 33:267–277. [recalled]
- Card, Robertson & Mackinlay (1991). "The Information Visualizer." CHI. [recalled]
- Doherty & Thadani (1982). "The economic value of rapid response time." IBM GE20-0752. [recalled]
- Nah, F. (2004). "A study on tolerable waiting time." *Behaviour & IT* 23(3):153–163. [recalled]
- Wertheimer (1923); Palmer (1992), *Cognitive Psychology* 24:436–447; Palmer & Rock (1994), *Psychonomic Bull Rev* 1:29–55; Kubovy & Wagemans (1995), *Psych Science* 6:225–234; Wagemans et al. (2012), *Psychological Bulletin* 138(6):1172–1217. [recalled]
- Wiedenbeck, S. (1999). "The use of icons and labels in an end user application program." *Behaviour & IT* 18(2):68–82. [recalled]
- Norman, D. A. (1981). "Categorization of action slips." *Psychological Review* 88(1):1–15; Norman (2013), *The Design of Everyday Things* (rev. ed.). [recalled]
- Reason, J. (1990). *Human Error*. Cambridge UP; Rasmussen (1983), *IEEE SMC* 13(3):257–266; Byrne & Bovair (1997), *Cognitive Science* 21(1):31–61. [recalled]
- Salthouse, T. A. (1996). "The processing-speed theory of adult age differences in cognition." *Psychological Review* 103(3):403–428. [recalled]

**Instruments and synthetic respondents**
- Hart & Staveland (1988). "Development of NASA-TLX." In *Human Mental Workload*; Hart (2006), "NASA-TLX: 20 years later," HFES. [recalled]
- Brooke (1996), SUS; Sauro (2011), *A Practical Guide to the SUS*; Bangor, Kortum & Miller (2009), *J Usability Studies* 4(3):114–123. [recalled]
- Sauro & Dumas (2009). "Comparison of three one-question, post-task usability questionnaires." CHI. [recalled]
- Lewis, Utesch & Maher (2013). "UMUX-LITE." CHI. [recalled]
- Argyle et al. (2023), *Political Analysis* 31(3):337–351; Bisbee et al. (2024), *Political Analysis*; Aher, Arriaga & Kalai (2023), ICML; Wang, Morgenstern & Dickerson (2025), *Nature Machine Intelligence*. [recalled]

**Status and commentary**
- Roselli, A. (2026-04). "WCAG3 Contrast as of April 2026." adrianroselli.com. [snippet — title/summary only; fetch blocked]
- Eggert, E. "WCAG 3 is not ready yet." yatil.net. [snippet]
