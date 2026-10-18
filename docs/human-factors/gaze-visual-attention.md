# Gaze and visual attention: research brief for the persona-swarm ergonomic QA

최신 출처 검토는 [2026-10-02 갱신 기록](2026-10-02-research-update.md)에 있습니다.
이 문서에는 당시의 접근 제한과 잠정 주장을 보존합니다.

Domain: where people look first, what they miss, and whether they notice feedback on a live screen (web, mobile, desktop apps, games, TV).
Date: 2026-09-28. Written for engineers turning findings into (a) automated checks on a live screen and (b) persona ergonomic profile dimensions. Target code: `ergoqa/hf/gaze.py`, `ergoqa/checks.py` (GZ-01..GZ-04) and the gaze block in `ergoqa/params.py`.

## 0. Read this first: access limits and evidence tags

**Access limits at the time of writing.** The egress proxy blocked full-text fetches from dl.acm.org, arxiv.org, nngroup.com, aalto.fi, mit.edu, harvard.edu, stanford.edu, PMC, Wikipedia, huggingface.co and GitHub Pages. Only github.com and raw.githubusercontent.com could be fetched. Web search was rate-limited partway through this work. Every claim below therefore comes from one of three places: search-engine result text attributed to the source, source code or READMEs fetched from GitHub, or the author's recall of well-known papers. The tags below say which. Before any number is hard-coded as `[paper]`, someone should open the primary source and check it.

Tags (they match the `ergoqa/params.py` scheme):

| Tag | Meaning |
|---|---|
| `[paper]` / `[standard]` | Empirical value or normative text from the cited source |
| `[derived]` | Computed in this brief from cited values; the computation is shown |
| `[policy]` | A team-tunable threshold or weight. It is anchored on the cited literature but is **not** itself an empirical finding |
| `[assumption]` | A declared modelling assumption with no direct source. Use it only for sensitivity runs |

How well each item was verified:

| Mark | Meaning |
|---|---|
| **V1** | Read from a primary artifact at the time of writing (source code or README on GitHub) |
| **V2** | Appeared in search-result text attributed to the named source. The full text was not opened |
| **UNCONFIRMED** | Recalled from the cited source by the author and not checked at the time of writing. Treat as provisional |
| **UNKNOWN** | No source found |

Epistemic rule for the repo: every result produced by the gaze simulation is `inferred` (basis `model`). It never counts as `observed` evidence of real-user behaviour, and it never says how common a behaviour is among real users. Only geometry facts measured on the screen are `observed`, for example "the error message is outside the viewport" or "the element is 41° from the touch point".

---

## 1. Summary

1. **UIs are not natural scenes.** In GUI eye-tracking, early fixations cluster in the **upper-left**, not at the centre. This holds across UI types in UEyes (CHI 2023: 62 participants, 1,980 UIs) and on mobile UIs in Leiva et al. (MobileHCI 2020: 30 participants, 193 UIs), both V2. The pattern differs by type:
   - Mobile: the upper-left is the most salient area.
   - Web: saliency is spread more sparsely in the upper-left.
   - Desktop apps: two bands, one just above centre and one near the upper-left corner.
   - Posters: just above centre.

   Centre bias (Tatler 2007, V2) is the right prior for posters, key art and images, and probably for 3D game scenes. It is the wrong prior for structured UIs. On desktop web, NN/g measured 69% (2010) to 80% (2017) of viewing time on the left half of the page, and 57% of viewing time above the fold, with 74% in the first two screenfuls (2018) (all V2).
2. **Bottom-up saliency is a weak predictor on UIs.** Classic parameter-free models such as Itti-Koch and spectral residual fit mobile-UI fixations poorly. Position, text and images explain more than colour or size (Leiva 2020, V2). Keep the bottom-up term, but give it less weight than position and element-type cues, especially on mobile.
3. **Top-down task guidance dominates once users have a goal.** Guided Search 6.0 combines five sources of guidance into one priority map: top-down features, bottom-up features, selection history, reward, and scene syntax/semantics (Wolfe 2021, V2). The task also changes the gaze distribution: during information foraging, first-second fixations go to the centre and centre-left; during page recognition they go to the top-left and top-centre (Buscher et al. 2009, V2). Banner blindness is top-down suppression: users on a goal overlook ad-like elements even when those elements hold the answer (Benway 1998; NN/g 2018, V2).
4. **Visual angle is the unit that matters.** Fovea ≈ central 2°, parafovea to about 5° (Rayner 1998, UNCONFIRMED). The reading perceptual span is 3–4 letters left and 14–15 letters right of fixation (V2). For Korean it is about 1 character left and 6–7 characters right (Choi & Koh 2009, V2 snippet, single study). At typical phone text sizes, both work out to roughly 3–5° [derived]. Labels outside the parafovea, or crowded by neighbours spaced closer than about 0.5 × eccentricity (Bouma's rule, UNCONFIRMED), have to be fixated before they can be read.
5. **Feedback-noticing rule (recommended; it replaces the current single threshold).** Measure the eccentricity θ between the point the user just acted on and the new feedback, then classify the change:
   - **Non-salient change** (in-place text or value change, colour-only change, small icon swap, or any change hidden by a screen-wide transition): likely noticed at θ ≤ 2°, uncertain at 2–5°, likely missed at θ > 5°.
   - **Salient change** (new-object onset or motion, ≥ 3:1 contrast with its surround, ≥ about 1°, and the only transient on screen): likely noticed at θ ≤ 10°, uncertain at 10–20°, likely missed at θ > 20°.

   Scale both bands by k ≈ 0.7 for high-load, 70+ or low-vision personas. All of these values are `[policy]`. The anchors are the fovea/parafovea limits, the 10/20/30° target eccentricities of the UFOV test (Ball et al. 1988, V2), and the shrinking of the useful field under load or visual noise (Mackworth 1965; Williams 1985, V2).

   What this means on real screens:
   - Phone (300 mm viewing distance, iPhone-14 geometry): 1° ≈ 32 CSS px. A top-of-screen error after tapping a bottom CTA is about 22° away, so it is likely missed even if it is salient.
   - 24-inch 1080p desktop at 600 mm: 1° ≈ 38 px. A bottom-right toast after a top-left click is about 42° away.
6. **The simulation should be stochastic.** Use Monte Carlo sampling (priority^γ × distance decay in degrees × inhibition of return × a rightward/downward bias) and report *P(element fixated within the first k fixations)*, not one greedy rank. Use the UEyes horizons of 1 s, 3 s and 7 s, which correspond to roughly 3–4, 9–12 and 21–28 fixations (derived from UNCONFIRMED fixation durations).
7. **Honest validity.** Every dataset here is free viewing of static screenshots on a lab monitor, with small and mostly non-Korean samples. Even the mobile datasets were almost certainly viewed on a desktop monitor with a remote tracker (inferred from the tracker types). The outputs are population-average risk indicators. They are not predictions for individuals, and they are not evidence of how common a behaviour is among real users. Calibrate against a small Korean eye-tracking pilot before treating any threshold as more than a policy choice.
8. **Problems found in the current repo** (details in section 9):
   - The phone prior is centred (x = 0.5), which contradicts the mobile top-left evidence.
   - `check_gaze` computes `start` from `focus_point` but passes `start=None` to `predicted_scanpath`.
   - The distance discount is normalised by the viewport diagonal instead of using degrees.
   - GZ-02 treats "priority ≥ 0.7" as salient. Salience of a *change* should come from onset, motion, contrast and whether it is the only transient on screen, not from static priority.

---

## 2. Geometry primitives (needed by every check)

**Inputs:** CSS viewport (w, h), `devicePixelRatio` (DPR), physical pixel density (PPI) or physical screen width in mm, and viewing distance D (mm) from the persona or device default.

```
mm_per_css_px = 25.4 * DPR / PPI                        # e.g. iPhone 14: 25.4*3/460 = 0.1657 mm/CSS px [derived; device spec UNCONFIRMED]
theta_deg(p,q) = degrees(atan(|p - q|_px * mm_per_css_px / D))   # eye on the screen normal; fine for < ~30 deg
size_deg(s_px) = 2*degrees(atan(s_px * mm_per_css_px / (2*D)))
mm_per_deg(D)  = D * tan(1 deg)   # 300 mm -> 5.24 mm; 600 mm -> 10.47 mm; 2700 mm -> 47.1 mm [derived]
```

Viewing distances already in `params.DEFAULT_VIEWING_DISTANCE_MM` are `[assumption]`: phone 300, desktop 600, TV 2700 mm. Bababekova et al. 2011 reported mean smartphone distances of about 36 cm for text messages and about 32 cm for web pages (UNCONFIRMED). Run sensitivity at phone D ∈ {200, 300, 400} mm `[assumption]`.

Worked conversions `[derived]`, computed with the stdlib script this brief was built from:

| Device (assumed geometry) | D | px per 1° | 2° | 5° | 10° | 20° | Whole screen |
|---|---|---|---|---|---|---|---|
| Phone 390×844 CSS, DPR 3, 460 ppi | 300 mm | 31.6 CSS px | 63 | 158 | 319 | 659 | 12.3° × 26.2° |
| Same phone | 330 mm | 34.8 | 70 | 174 | 351 | 725 | — |
| 24" 16:9 1920×1080 monitor (0.277 mm/px) | 600 mm | 37.8 px | 76 | 190 | 382 | 789 | 47.8° × 28.0° |
| 14" laptop at 1280×720 CSS | 500 mm | 36.0 CSS px | — | — | — | — | 34.4° wide |
| 55" TV, 1920-wide layout | 2700 mm | 74.3 layout px | — | — | — | — | 25.4° × 14.5°; centre to corner 14.5° |

Consequences:
- A phone screen spans only about 12° horizontally. Almost any salient onset on the *same row band* falls within 10°, but the vertical extent (about 26°) is what defeats feedback.
- On desktop, feedback in the opposite corner is more than 40° away.
- On TV, the whole screen fits inside the UFOV test's 30° ring, but the corners are about 14.5° from the centre.

---

## 3. Principles

Each principle is laid out as: statement, parameters with sources, operationalization, applicability, and validity limits. Check IDs refer to section 5.

### GZ-P1. Position priors: upper-left in GUIs, centre in pictures, steep decay below the fold and to the right

**Statement.** Before content is processed, attention in structured GUIs starts at the upper-left for left-to-right (LTR) readers and moves right and down. Pictures, posters and full-bleed scenes instead show a centre (slightly above-centre) bias. On long web pages, attention decays sharply per screenful.

**Parameters and sources**

| Value | Context | Source | Status |
|---|---|---|---|
| Upper-left quadrant draws more fixations than other quadrants for **all** UI types; "in contrast against the centre bias of natural images, fixations in UI settings are mostly in the upper left" | 62 participants, 1,980 screenshots (495 each of web, desktop, mobile, poster); maps at 1/3/7 s; free viewing | Jiang et al., UEyes, CHI 2023 | V2 |
| Mobile: most salient area upper-left. Web: salient areas spread more sparsely in the upper-left. Desktop: two bands, just above centre and near the upper-left corner. Poster: just above centre | same | UEyes | V2 |
| Saccades tend toward the right or bottom; rightward saccades cover larger distances than downward ones | same | UEyes | V2 |
| Raw gaze logs are in Gazepoint API v2.0 format (so a Gazepoint tracker; model and sampling rate UNCONFIRMED); durations 1 s, 3 s, 7 s | dataset README | UEyes GitHub | V1 |
| Strong bias toward the top-left corner, text and images; colour and size affected saliency less; classic parameter-free models fit weakly; models trained on the data fit much better | 30 participants, 193 mobile UIs, SMI RED250 (250 Hz, 0.4° accuracy), 3.5 s per UI + 1.5 s blank | Leiva et al., MobileHCI 2020 | V2 |
| Information foraging: fixations concentrate centre-left and top-left. Page recognition: top-left and top-centre. Elements near the lower screen border are less likely to be fixated | 20 users, 361 web pages, desktop | Buscher, Cutrell & Morris, CHI 2009 | V2 |
| No fixation on the right third of the page in the first second | same (secondary citation) | Buscher 2009 via secondary source | V2, verify |
| 69% of viewing time on the left half, 30% on the right half | desktop web, 2010 | NN/g "Horizontal Attention Leans Left" | V2 |
| 80% left half, 20% right half | desktop web, 2017 update | NN/g | V2 |
| 57% of viewing time above the fold; 74% in the first two screenfuls (≤ 2160 px); 130,000 fixations, 120 people | desktop web, 2018 | NN/g "Scrolling and Attention" | V2 |
| 80% of viewing time above the fold | desktop web, 2010 | NN/g (original study) | V2 |
| Centre bias in scene viewing on monitors, independent of how image features are distributed | natural scenes, lab | Tatler 2007, JoV 7(14):4 | V2 |

**Operationalization**

- *Inputs:* element boxes (CSS px), viewport, device class, UI type (web page, native mobile, desktop app, poster/splash/key art, game in-play, TV 10-foot), scroll offset, and page height.
- *Prior* over the unit square of the current viewport: a mixture of anisotropic Gaussians `Σ w·exp(-((x-μx)²/2σx² + (y-μy)²/2σy²))`.

Recommended starting values. All are `[policy]` unless derived; replace them with fitted values as soon as possible.

| UI type | Components (w, μx, μy, σx, σy) | Basis |
|---|---|---|
| Web page (desktop) | (1.0, **0.26–0.36**, 0.30, 0.25, 0.35) | μx `[derived]`: with a normal truncated to [0,1] and σx = 0.25, μx = 0.264 gives an 80% left-half share (NN/g 2017) and μx = 0.362 gives 69% (NN/g 2010). With σx = 0.30 the range is 0.19–0.32. Default 0.30. |
| Native mobile | (1.0, 0.35, 0.25, 0.30, 0.30) | Qualitative top-left finding (Leiva 2020; UEyes). The current repo uses centre_x 0.5, which contradicts the evidence. |
| Desktop app | (0.6, 0.50, 0.40, 0.25, 0.15) + (0.4, 0.15, 0.12, 0.12, 0.10) | The two bands in UEyes |
| Poster / splash / key art / game menu art | (1.0, 0.50, 0.42, 0.25, 0.25) | UEyes posters; Tatler 2007 |
| Game in-play (3D, crosshair) | (1.0, 0.50, 0.50, 0.15, 0.15) | `[assumption]`: centre-locked camera. No UI eye-tracking dataset was found for this. |
| TV 10-foot | focus-highlighted element + (1.0, 0.50, 0.45, 0.30, 0.30) | `[assumption]`: no dataset found. With D-pad navigation the focus ring is the strongest cue. |

- *Long pages:* multiply the prior by the share for screenful k: s1 = 0.57, s2 = 0.17, and for k ≥ 3, `s_k = 0.17·r^(k-2)` with r = 0.26/(0.17+0.26) = 0.605. That gives 0.103, 0.062, 0.038, … `[derived]`. The geometric tail is an `[assumption]` and depends on page length. Screenful height is the device's viewport height (NN/g used about 1080 px screens).
- *RTL scripts:* mirror x. Korean horizontal Hangul UIs are LTR, so the LTR prior applies `[assumption: not tested on Korean users]`.
- *Fitting procedure (do this before trusting the priors):* download UEyes (Zenodo record 8010312; check the licence first). For each UI type, average the 1 s and 3 s fixation maps on a 100×100 grid, then fit a 1–2 component Gaussian mixture model. The "mean fixation map" is the standard centre-bias baseline in saliency benchmarking, so the fitted prior can be scored on held-out UIs with NSS and AUC. Keep separate 1 s priors for first-glance checks.

**Checks it drives.** GZ-01 (primary action early), GZ-05 (task-critical content in a low-prior zone). Suggested GZ-05 thresholds, all `[policy]`:
- Task-critical info (total price, consent terms, error summary, deadline) placed *only* in screenful ≥ 3, or with expected attention share < 0.10: **P2**.
- The same for informational content: **P3**.
- On desktop, task-critical info only in the right third with nothing pointing to it: P3. Raise to P2 if it is outcome-critical.

**Applicability.** Web desktop: strong evidence. Mobile: moderate (lab monitor viewing). Desktop apps: UEyes only. Posters, games and TV: weak or none (see the table).

**Validity limits.**
- Free viewing of static screenshots for 1–7 s. Real tasks change the distribution (Buscher).
- Samples are small (20–120 participants) and not Korean.
- These are averaged maps. Individual scanpaths vary widely, and UEyes itself discusses individual viewing strategies.
- NN/g numbers are proprietary studies with limited method detail.

### GZ-P2. Text scanning patterns (F-pattern and its siblings); Z-pattern and Gutenberg diagram

**Statement.** On text-heavy pages people scan rather than read. The pattern depends on formatting, motivation and task. The F-pattern is a *symptom* of unformatted text. It is not a layout to design for.

**Parameters and sources**

- NN/g 2006: eye-tracking of 232 users on thousands of pages. The dominant pattern was a horizontal sweep at the top, a shorter second sweep, then a vertical scan down the left side (V2).
- NN/g 2017 (Pernice, 12 Nov 2017, "F-Shaped Pattern of Reading on the Web: Misunderstood, But Still Relevant (Even on Mobile)"): the F-pattern still appears on desktop and on mobile (V2). Other patterns (V2 unless marked):
  - *Layer-cake:* eyes scan headings and subheadings and skip the body text.
  - *Spotted:* skipping large chunks while hunting for something specific, such as a link, digits, a word, or a distinctively shaped item like an address.
  - *Bypassing:* deliberately skipping the first words of lines when list items start with the same words.
  - *Commitment:* fixating almost everything.
  - *Marking:* eyes stay in one place while the finger or mouse scrolls; described as common on mobile (UNCONFIRMED wording; NN/g "Text Scanning Patterns: Eyetracking Evidence").
- Conditions for the F-pattern (paraphrase, UNCONFIRMED): (1) text with little or no formatting, (2) a user trying to be efficient, (3) a user not committed enough to read every word.
- **Gutenberg diagram / Z-pattern.** These are design-practice heuristics about "reading gravity" on homogeneous text. The claim that they improve reading has "little empirical evidence", and the Gutenberg diagram "no longer applies" once there is visual hierarchy (V2, secondary design literature: Vanseo Design). Djamasbi, Siegel & Tullis (HCII 2011) eye-tracked visual hierarchy on web pages; their results were not retrievable (UNKNOWN). No eye-tracking evidence was found for a bottom-right "terminal area" advantage, and UEyes posters show an above-centre concentration instead. **Recommendation: do not encode Gutenberg or Z as priors.** Keep only the evidence-backed parts: a top-left start and a tendency to saccade right and down (UEyes).
- Base rates of each pattern among users: UNKNOWN. NN/g reports them qualitatively.

**Operationalization (text-block model)**

- *Inputs:* text nodes with boxes, font size and weight, heading level, list structure, link and number tokens.
- *Within an unformatted paragraph* (no headings, bold, bullets or links for ≥ N lines; N = 5 `[policy]`), weight line i by `exp(-i/τ)` with τ = 2 lines `[policy]`. Within a line, weight the first about 6–7 Korean characters or about 15 Latin characters (P7) higher, with a left-edge ramp.
- *Spotted boosts:* numbers, currency ("원", "₩", "%"), dates, links, bold runs. *Layer-cake:* headings get full weight and body text a lower weight. *Bypassing:* when ≥ 3 consecutive lines share a prefix, move the line-start weight to the first differing token.
- **Check GZ-06, "key information buried in unformatted text".**
  - Trigger: a task-critical token (from the scenario definition) appears only in line ≥ 3 of an unformatted paragraph, or after character 20 of a line, with no emphasis.
  - Severity: **P3**. Raise to **P2** when the token is required to finish the task (for example a cancellation deadline or fee) and appears nowhere else.
  - Status: inferred.
- **F-risk flag.** A page region with more than 150 Korean characters `[policy]` and no subheadings or bullets gets P3 ("layer-cake impossible"), with the fix "add headings or bullets and front-load key terms".

**Applicability.** Web and mobile content pages, help and terms screens, settings descriptions. Rarely relevant to games (except codex or tutorial text) or to TV (little text).

**Validity.** Qualitative patterns with no published prevalence. Persona "scanning strategy" should be sampled for sensitivity (section 6). It must not be reported as a population share.

### GZ-P3. Bottom-up saliency (Itti-Koch; spectral residual) and its limits on UIs

**Statement.** Local feature contrast (intensity, colour opponency, orientation, and motion in dynamic scenes) draws early attention in free viewing. On structured UIs it is only a weak predictor.

**Parameters and sources**

- Itti, Koch & Niebur 1998 (IEEE TPAMI 20(11)). Multiscale features are combined into one saliency map, and a winner-take-all network with inhibition of return picks locations in order of decreasing saliency (V2). Canonical parameters (UNCONFIRMED; from the paper):
  - 9-level dyadic Gaussian pyramid; centre scales c ∈ {2,3,4}; surround s = c + δ with δ ∈ {3,4}.
  - 42 feature maps: 6 intensity, 12 colour (R-G, B-Y), 24 orientation (0/45/90/135°).
  - Normalisation operator N(·) scales each map to [0, M] and multiplies by (M − m̄)², where m̄ is the mean of the other local maxima.
  - Maps are summed at scale 4.
- Hou & Zhang 2007 (CVPR) spectral residual (SR):
  - Log amplitude spectrum minus its local 3×3 average, inverted with the original phase, squared, then Gaussian-smoothed.
  - The input is downsampled to about 64 px (V2 for 64×64).
  - In the uoip C++/Python port: 3×3 box filter on the log magnitude, and a 9×9 Gaussian with σ = 3 at a working width of 128 px ("has a great influence on the result") (V1, code).
- On mobile UIs, classic parameter-free models showed a weak fit (Leiva 2020, V2). UEyes released improved data-driven models UMSI++, DeepGaze++ and PathGAN++ (V1 README).
- **Sanity test at the time of writing** (our observation, not literature): a pure-Python SR on a *perfectly flat* synthetic background with one dark button came out degenerate (the peak was at the image border and the button averaged 0.02). Adding ±0.25% luminance dither made the button edges the peak (mean 0.37 against 0.03 elsewhere). Flat-design screenshots have large uniform areas, so **add tiny dither before SR** and expect SR to highlight edges and corners rather than whole objects.

**Operationalization**

- *Inputs:* the screenshot (device px), downsampled to 64–128 px wide, grayscale for SR or RGB for an Itti-lite model.
- *Pixel map:* use either SR (stdlib reference in section 4, about 0.3 s for 64×128 in pure Python) or the existing centre-surround box-blur Itti-lite in `gaze.conspicuity_map`. Normalise to [0,1].
- *Element score:* the mean of the top 25% of cells inside the box plus a 1-cell margin, so that SR edge responses are captured.
- *Element pop-out features* (more robust than pixel maps on UIs):
  - (a) luminance contrast of the element's fill or text against its surround (WCAG contrast formula);
  - (b) hue uniqueness: the minimum CIELAB ΔE to other interactive elements' fills;
  - (c) size rank in visual angle;
  - (d) font-size and weight rank.

  A feature counts as "unique" when the element differs from every competitor on it (GZ-P6).
- *CVD personas:* compute saliency and pop-out on a CVD-simulated screenshot (Machado, Oliveira & Fernandes 2009 matrices, UNCONFIRMED). Hue-only pop-out can disappear.
- *Weighting:* on mobile, give bottom-up ≤ 0.3 of the combined priority, below position and element-type cues (Leiva 2020). The current repo uses 0.4 everywhere `[policy]`.

**Applicability.** All platforms. For games and animated UIs, add a temporal channel: the frame-difference magnitude over the last 100–200 ms `[policy]`. Motion and onsets are the strongest peripheral attractors (GZ-P8).

**Validity.** It predicts free-viewing fixation density, not goal-directed behaviour. SR responds to edges and texture, which exaggerates busy photos and underweights clean, large CTAs.

### GZ-P4. Element-type attractors and "visual importance"

**Statement.** Text (especially headings), images and faces draw fixations regardless of low-level contrast. Designers' intended importance can be learned from human data.

**Sources**
- Leiva 2020: text and images attract attention; colour and size less (V2).
- Bylinskii et al., UIST 2017: neural models trained on human importance data, from BubbleView clicks and graphic-design annotations, predict the relative importance of elements in designs and visualisations; they were used for retargeting and thumbnails (V2). Fosco et al., UIST 2020 (UMSI): importance prediction across graphic-design types (V2 existence).
- The pull of faces is a general scene-viewing finding: UNCONFIRMED at the time of writing. It is not parameterised here.

**Operationalization.** Element-type cue weights `[policy]`: heading text 1.0; image/illustration 0.8; face in image 1.0 (if a detector exists); body text 0.5; icon-only button 0.4; plain container 0.1. Combine with size and contrast as the existing `element_cue` already does. An optional heavier path is to run UMSI++ or DeepGaze++ from the UEyes repo offline. That breaks the no-dependency rule, so keep it as a benchmark mode.

**Validity.** Importance labels come from crowd annotation or clicks, not eye movements. Weights are unvalidated for Korean UIs.

### GZ-P5. Top-down guidance: task relevance, expectations and learned layouts

**Statement.** Once the user has a goal, attention is guided by what the target looks like and where it is expected to be, more than by raw saliency.

**Sources**
- Guided Search 6.0 (Wolfe 2021, Psychon Bull Rev 28:1060–1092). There are five guidance sources (top-down features, bottom-up features, prior history, reward, scene syntax/semantics) combined into a spatial priority map. Items enter processing every 50–60 ms. Recognition is an asynchronous diffusion taking more than 150 ms per item. There are three functional visual fields: resolution, exploratory eye movements, and covert attention. Items near fixation are found faster (all V2).
- Buscher 2009: task type shifts the gaze distribution (V2).
- Information scent: the semantic similarity between the user's goal and a link label predicts selection (Pirolli & Card 1999, *Information foraging*; Blackmon et al., CHI 2002, *Cognitive Walkthrough for the Web*). Details UNCONFIRMED.

**Operationalization**
- *Task relevance* T(e) ∈ [0,1] is the similarity between the persona's current sub-goal (Korean text from the scenario) and the element's accessible name or visible text. Use lexical overlap with Korean morpheme normalisation (stdlib: character bigram Jaccard) `[policy]`, or an LLM judgment (see section 7).
- *Expectation prior* E(e): a curated table of conventional locations per platform, for example the logo top-left, search at the top, cart or profile top-right, back top-left, modal close top-right, and the primary checkout CTA as a bottom sticky bar on Korean commerce apps. Treat it as `[assumption]` and curate it per product with a human. When the expected location is empty and the target sits elsewhere, flag GZ-07 ("target outside its conventional location"): P3, or P2 on a critical path.
- *Crowding gate* (P7): T(e) can guide a saccade only if the label is readable from the current fixation, that is, within about 5° and not crowded. Otherwise guidance falls back to coarse features (colour, size, shape). This is the core idea of active-vision search models (Kieras & Hornof, CHI 2014, UNCONFIRMED).
- *Mode weights* for combining the priority (all `[policy]`):

| Mode | bottom-up | position | text/type cue | task T | expectation E | ad-likeness penalty A |
|---|---|---|---|---|---|---|
| Free view / first glance | 0.30 | 0.35 | 0.25 | 0.00 | 0.10 | 0.0 |
| Goal-directed | 0.15 | 0.20 | 0.15 | 0.35 | 0.15 | 0.3 (subtracted) |

**Validity.** No calibrated weights exist for GUIs. Treat them as sensitivity parameters.

### GZ-P6. Visual search: pop-out versus conjunction, set-size cost, competing CTAs

**Statement.** A target that differs from every distractor in one guiding feature pops out, and its search time barely depends on how many items there are. A target defined by a combination of features, or one that looks like its neighbours, needs roughly serial inspection, so time grows with the number of similar items.

**Parameters and sources**

| Value | Context | Source | Status |
|---|---|---|---|
| Flat reaction-time slope for a unique-feature target; linear increase for conjunctions | lab displays | Treisman & Gelade 1980 | V2 |
| Slopes form a continuum; 15 ms/item is unlikely for a feature search and 5 ms/item is unlikely for a spatial-configuration search, but the distributions overlap; the simple serial model predicts target-absent ≈ 2 × target-present | about 1 million trials, 2,500 sessions | Wolfe 1998, Psych Sci 9(1) | V2 |
| Inefficient search: target-present slopes of 20–40 ms/item for stimuli large enough not to need eye movements; target-absent slopes a bit more than twice as steep; efficient ≈ 0; inefficient > 25–30 ms/item | lab, covert attention | Wolfe (Scholarpedia "Visual search"; Wolfe & Horowitz reviews) | V2 |

**Operationalization**
- **GZ-04 (upgrade): pop-out test for the primary action.** Candidates are the visible interactive elements. The primary action "pops out" if it is unique in at least one guiding feature against *all* competitors:
  - hue: ΔE76 ≥ 20 against every other filled control. This reuses `CVD_DISTINCT_NORMAL_DE`, `[policy]`; also evaluate it under CVD simulation.
  - luminance contrast of the fill against the page ≥ 3:1 while competitors are below 3:1 (WCAG 1.4.11 proxy).
  - area ≥ 1.5 × the next largest control `[policy]`.

  With no unique feature, or with ≥ 2 elements styled "primary" (competing CTAs), record **P3**. Raise to **P2** when the competing element is destructive or off-path (for example "구독 해지" styled like "계속").
- **GZ-08: set-size cost.**
  - n_eff is the number of elements that share the target's coarse guiding features (same component style) in the region to be searched.
  - Covert estimate: `T ≈ n_eff × 20–40 ms` (target present), doubled when the persona must conclude "not here" (Wolfe 1998 ratio).
  - GUIs need eye movements, so also estimate fixations: `n_fix ≈ n_eff / items_per_fixation`, where items_per_fixation is the number of uncrowded, readable items within about 5° of a fixation (from P7), and multiply by about 0.25–0.3 s per fixation (UNCONFIRMED; P12).
  - Flag **P3** when the estimated target-present search is > 2 s or n_eff ≥ 20 `[policy]`. Raise to **P2** when the item is on a critical path and nothing (search box, filter, grouping) reduces n_eff.
  - Report these as *relative* costs for comparing variants. They are not predicted task times.

**Applicability.** Menus, product grids (dense Korean commerce lists), settings lists, game inventories and skill bars, TV content rows. For TV, D-pad traversal cost (P12) usually dominates visual search.

**Validity.** Lab slopes come from simple symbols with covert search. GUI search involves reading, semantics and learning (expert users jump to remembered locations). Novice GUI search is closer to serial; experts are closer to Hick-Hyman decision time (UNCONFIRMED; for example Cockburn, Gutwin & Greenberg, CHI 2007).

### GZ-P7. Acuity limits, crowding and perceptual span (including Korean)

**Statement.** Detail is only available near the point of gaze. Labels outside the parafovea, or crowded by neighbours, cannot be identified without a fixation. The reading span in Korean is about 6–7 characters to the right.

**Parameters and sources**

| Value | Context | Source | Status |
|---|---|---|---|
| Foveal region ≈ central 2°; parafovea out to about 5° either side; periphery beyond | reading | Rayner 1998, Psych Bull 124(3) | UNCONFIRMED (standard definition) |
| Perceptual span 3–4 letters left, 14–15 letter spaces right of fixation | skilled readers of alphabetic LTR scripts | Rayner 1998; McConkie & Rayner 1975 | V2 |
| About 3–4 letters per degree at normal reading distance, so 15 letters ≈ 3.8–5.0° | reading | Rayner 1998 | UNCONFIRMED; arithmetic `[derived]` |
| Korean perceptual span ≈ 6–7 characters right, 1 left | Korean sentence reading, moving-window paradigm | Choi & Koh 2009, Korean J Cognitive Science 20(4):573–601 | V2 (snippet; single study) |
| Parafoveal processing occurs in Korean reading (boundary paradigm) | 24 native readers | Kim, Radach & Vorstius 2012, Reading and Writing | V2 (existence) |
| Removing spaces hinders Korean reading, but less than in English; postpositional particles help segmentation | eye-tracking, sentences | Baek, Choi & Gordon 2023, QJEP | V2 |
| Crowding: critical spacing ≈ 0.5 × eccentricity (Bouma's rule) | peripheral letter identification | Bouma 1970, Nature 226; Pelli & Tillman 2008 | UNCONFIRMED |

Derived Korean and Latin spans at phone text sizes `[derived]`: 300 mm, 0.1657 mm/CSS px, Hangul advance about 1 em, Latin average letter about 0.5 em (both `[assumption]`).

| Font size | Hangul chars per degree | 6–7 Hangul chars | Latin letters per degree | 15 Latin letters |
|---|---|---|---|---|
| 14 px | 2.26 | 2.7–3.1° | 4.5 | 3.3° |
| 16 px | 1.98 | 3.0–3.5° | 4.0 | 3.8° |
| 20 px | 1.58 | 3.8–4.4° | 3.2 | 4.7° |

The angular spans come out similar, about 3–5°, so a **5° "readable-without-fixation" radius** is a reasonable policy boundary for both scripts `[policy]`.

**Operationalization**
- **Readability gate.** A label is "read" by the simulation only if a predicted fixation lands within 1° of its first characters, or the label lies to the right of a fixation within the span: 6–7 Hangul characters or 15 Latin letters, capped at 5° `[policy]`.
- **Crowding check** (used by P5 and P6). For element e at eccentricity φ from the current simulated fixation, if the nearest-neighbour centre spacing is < 0.5·φ (UNCONFIRMED), then e must be fixated to be identified.
- **GZ-09, front-loading (Korean).** A critical keyword beyond the 7th character of a label or first line, where a prefix repeats across items (bypassing), gets **P3**.
- **Text size** is already covered by `TEXT_MIN_ARCMIN` (perception brief). Link to it and do not duplicate.

**Applicability.** All platforms. TV and games (HUD) need arcmin checks at their viewing distances.

**Validity.** Reading-span studies use sentences on lab displays. UI labels are short and read in isolation. The Korean span comes from one study that was not verified in full text.

### GZ-P8. Useful field of view and peripheral detection, the basis for feedback noticing

**Statement.** What can be detected without moving the eyes shrinks with eccentricity, age, central task load and visual clutter. Abrupt onsets and motion are detected much further into the periphery than static colour or text changes.

**Parameters and sources**

| Value | Context | Source | Status |
|---|---|---|---|
| UFOV = the visual area from which information can be acquired within one fixation; it shrinks with age and partly recovers with practice | lab | Ball, Beard, Roenker, Miller & Griggs 1988, JOSA A 5:2210 | V2 |
| UFOV test: central target plus a peripheral target on 8 radial spokes at **10°, 20°, 30°**; exposure 16.7–500 ms with a staircase to 75% correct; subtest 3 adds distractors | test protocol | UFOV descriptions (PC version in Edwards et al. 2005/2006) | V2 |
| UFOV "40% reduction" cutoff predicts crash involvement: sensitivity 86.3%, specificity 84.3% | older drivers | Goode et al. 1998, J Clin Psychol Med Settings | V2 |
| UFOV size predicts crash history: sensitivity 89%, specificity 81% | older drivers | Ball et al. 1993, IOVS 34:3110 | V2 |
| Adding visual noise (extra letters) seriously impairs peripheral comparison ("tunnel vision") | lab | Mackworth 1965, Psychonomic Science 3:67 | V2 |
| Foveal load narrows the functional field | lab | Williams 1985, Human Factors 27(2) | V2 (existence) |
| Abrupt visual onsets capture attention | lab search | Yantis & Jonides 1984, JEP:HPP 10:601 | UNCONFIRMED |
| Motion cues are detected better than colour or shape changes in the periphery | large-display notification study | Bartram, Ware & Calvert 2003, IJHCS 58 ("Moticons") | UNCONFIRMED (no numbers retrieved) |
| Detection-response task remote stimulus placed about 11–23° left and 2–4° above the forward line of sight | in-vehicle cognitive load measurement | ISO 17488:2016 | UNCONFIRMED |
| "Avoid placing essential temporary information outside the player's eye-line" | game accessibility guideline | gameaccessibilityguidelines.com | UNCONFIRMED wording |

**Where the thresholds come from.** No study gives a "UI feedback is noticed if within X°" value. The bands below are `[policy]`, built from four anchors:
- (a) Non-salient content (text or value changes) must fall inside the region that can be *resolved or read* within the current fixation: fovea ≈ 2°, readable parafovea ≈ 5° (P7).
- (b) Salient onsets are tested and detectable out to the UFOV test's 10–30° rings, but accuracy drops at larger eccentricities, with age and with central load or distractors (Ball 1988; Mackworth 1965; Williams 1985).
- (c) Driving research measures load by detection at about 11–23° (ISO 17488, UNCONFIRMED). Detection there is measurable but misses rise under load.
- (d) The UFOV exposures are brief (≤ 500 ms), and so are transient toasts and snackbars, which makes the analogy reasonable for "noticed at the moment of change". Persistent messages get a second chance through the scanpath (step 7 below).

**Operationalization: feedback-noticing check (GZ-02 v2)**

*Inputs:* before and after screenshots with timestamps (or a short frame sequence), the action event (type, point in CSS px, t_action), element boxes and roles (`alert`, `status`, error, toast), device mm/px, D, and persona modifiers.

1. **Find the change.** Take the pixel difference on a 64–128 px grid, marking cells where |ΔL| > 0.1 relative luminance `[policy]`, together with new or changed accessibility nodes. Group the changed cells into regions.
2. **Transient uniqueness.** U = area of the feedback region / area of all changed pixels between t_action and t_action + 1 s. If U < 0.5 `[policy]`, as with a route transition, full re-render, auto-scroll or keyboard opening, the feedback's own onset is masked. Treat it as **non-salient** (change blindness: Rensink, O'Regan & Clark 1997, UNCONFIRMED).
3. **Salience of the change.** The change is salient if all of the following hold. Otherwise it is non-salient.
   - (i) It is the onset of a new object, or it includes motion or animation.
   - (ii) The new region's contrast with its immediate surround is ≥ 3:1 (WCAG 1.4.11 used as the proxy `[policy]`).
   - (iii) Its extent is ≥ 1° × 1° `[policy]`.
   - (iv) U ≥ 0.5.

   An in-place text or number change, a colour-only change (for example a border turning red), or a small icon swap is always **non-salient**.
4. **Gaze estimate at the time of change.** If the change starts within about 1 s of a touch or click, use the action point. The eyes typically lead the hand to the target (Johansson et al. 2001, UNCONFIRMED), and this is the current `focus_point` convention. Otherwise use the last simulated fixation.
5. **Eccentricity** θ from the gaze estimate to the *nearest point* of the feedback region, and also to its centroid; report both.
6. **Bands** `[policy]`, scaled by the persona factor k:

| Change class | Likely noticed | Uncertain | Likely missed |
|---|---|---|---|
| Non-salient | θ ≤ 2°·k | 2–5°·k | > 5°·k |
| Salient | θ ≤ 10°·k | 10–20°·k | > 20°·k |

   k = 1.0 by default. Use k = 0.7 for personas aged 70+, under high load (walking, transit, in-game combat, multitasking), with low vision, or when the screen is visually dense `[assumption]`. The direction is supported by Ball 1988 and Mackworth 1965; the magnitude has no source.
7. **Recovery by scanning.** If the message persists (it is not a toast, or it is visible for ≥ 4 s; compare `TOAST_FLOOR_MS`), run the Monte Carlo scanpath (P12) from the gaze estimate with the feedback element's post-change priority. If P(fixated within 3 s) ≥ 0.8 `[policy]`, raise the band by one step.
8. **Occlusion** (P11). If the feedback region is inside the hand-occlusion zone while the finger is down, it is not visible until the finger lifts. A feedback shorter than the press is "likely missed".
9. **Redundant channels.** Record, as mitigations, programmatic exposure (`role=alert`/`status`, `aria-live`; WCAG 2.2 SC 4.1.3), a focus move to the message, haptic or sound cues, and persistent inline state at the control (for example an error border plus text under the field). For screen-reader personas the visual bands do not apply; check programmatic exposure instead.

*Severity mapping* (the model output is `inferred`):

| Situation | Severity |
|---|---|
| Outcome-critical feedback (submit or payment failure, destructive-action result, safety warning) in "likely missed", with no redundant persistent cue | **P1** (inferred risk). P0 only if *observed*: the persona run proceeds as if it succeeded and a critical task fails, or there is a safety or financial loss with no recovery |
| Outcome-critical feedback in "uncertain" | **P2** |
| Non-critical status ("저장됨", "장바구니에 담김") in "likely missed" | **P2** if the user is likely to repeat the action (double submit or duplicate add), otherwise **P3** |
| Feedback not in the viewport at all after the action (observed geometry) and the action failed | **P1 observed**; P0 as above |

*Worked examples* `[derived]`:
- Phone, 300 mm: tapping a bottom CTA at y = 780 while an error banner appears at y = 60 (720 CSS px apart) gives θ ≈ 21.7°. That is likely missed even when salient. The fix is an inline error at the field plus scroll or focus to the first error.
- Desktop, 600 mm: a click at the top-left and a toast at the bottom-right give θ ≈ 41.6°.
- TV at 2.7 m: from the centre to a corner toast is about 14.5°, which is uncertain for a salient toast. Add sound, or place notifications near the focused row.

**Applicability.**
- Mobile: most important, because vertical travel is about 26°.
- Desktop web and apps: toasts in corners are a common failure.
- Games: HUD warnings during combat, with a centre-locked gaze and high load, so use k = 0.7.
- TV: 10-foot viewing and corner notifications.

**Validity.** The UFOV was measured with brief, lab-controlled stimuli. UI changes persist and are embedded in tasks. The bands are policy anchors, not measured detection probabilities. Real noticing also depends on expectation, since users look where they expect feedback. That judgment is left to a human or LLM (section 7).

### GZ-P9. Change blindness and inattentional blindness in UIs

**Statement.** People fail to notice large changes when the change's own transient is masked (by a blink, a saccade, a screen flash or a transition) or when attention is engaged elsewhere. Seeing something is not the same as noticing it.

**Sources**
- Rensink, O'Regan & Clark 1997, Psych Sci 8(5): the flicker paradigm. Changes are hard to see without focused attention (UNCONFIRMED details).
- Simons & Levin 1998: about half of people failed to notice a person swap in a real-world interaction (UNCONFIRMED).
- Simons & Chabris 1999, "Gorillas in our midst": roughly half missed an unexpected gorilla while counting passes (UNCONFIRMED).
- Drew, Võ & Wolfe 2013: most radiologists (reported 20/24) missed a gorilla inserted in a CT scan (UNCONFIRMED).
- HCI implications: Varakin, Levin & Fidler 2004 (HCI 19(4)); Durlach 2004 (HCI 19(4)) (UNCONFIRMED details).
- Perceptual load raises inattentional blindness (Lavie's load theory; Cartwright-Finch & Lavie 2007) (UNCONFIRMED).

**Operationalization.** Covered by GZ-02 v2 steps 2–3 (transient uniqueness, masking by transitions). Additional detectors:
- **GZ-10, silent state change.** A value changes in place, such as a cart badge count, a price after an option change, or a stock or seat status, with no animation, highlight or announcement, and the persona's gaze estimate is more than 2° away. Record **P3**. Raise to **P2** when the change alters the price or outcome the user is committing to.
- **Changes during transitions.** If a critical element changes in the same frame window as a page transition, loading spinner removal or scroll, flag it as masked.

**Applicability.** All platforms. Games in particular: during combat, peripheral HUD changes are prone to inattentional blindness.

**Validity.** The classic demonstrations are dramatic single-shot events, and rates vary widely with the situation. Do not quote the percentages as UI miss rates.

### GZ-P10. Banner blindness (ad-likeness suppression)

**Statement.** Users on a goal learn to skip regions and styles that look like advertising. Making such an element *more* eye-catching can make it *less* likely to be found.

**Sources**
- Benway 1998, HFES 42nd Annual Meeting: users looking for specific items overlooked distinctive banners, and increasing a banner's visibility did not help and could hurt (V2).
- Benway & Lane 1998 (Rice University): experimental banners were found about 58% of the time against about 94% for control items. Banners higher on the page, further from other links, were missed more. In a pilot, 42% missed prominent red banners holding task-critical information (V2 snippet; verify before quoting).
- Pagendarm & Schaumburg 2001, JoDI, "Why are users banner-blind?": goal-directed search against browsing (UNCONFIRMED finding).
- Owens, Chaparro & Palmer 2011, JUS: text-ad blindness (V2 existence).
- NN/g 2018, "Banner Blindness Revisited": it persists on mobile and desktop, and *legitimate content with ad-like characteristics is ignored too* (V2).
- Native ads draw more attention than banner ads (Electronic Commerce Research 2021 eye-tracking experiment, V2).

**Operationalization.** Ad-likeness score A(e) = number of these features present:
1. Position: a full-width top banner band (`AD_BANNER_Y_FRAC` 0.15, height ≤ 120 CSS px) or the right rail (`AD_RAIL_X_FRAC` 0.78) on desktop; an in-feed card or auto-rotating carousel near the top on mobile.
2. Standard ad-unit size within ±10%: 728×90, 300×250, 160×600, 320×50, 320×100 (IAB conventions, UNCONFIRMED list).
3. A label such as "광고", "AD", "Sponsored", "스폰서", "제휴", "프로모션".
4. Image-dominant with little text, strongly saturated, or animated.
5. Styling that departs from the page's content style (different font or palette).

For elements whose role is critical (errors, deadlines, required notices, coupon conditions needed for the task):
- A(e) ≥ 2: **GZ-03**, severity **P2** (the current code uses P3; raise it for task-critical content).
- A(e) = 1: **P3**.
- If the persona run then fails to use that information, the finding becomes **P1 observed** (repeated failure).

In goal-directed mode, subtract w_A·A(e)/5 from the element's priority (w_A = 0.3 `[policy]`).

**Applicability.** Web and mobile, including Korean commerce and portal promo carousels (whether Korean users are more carousel-blind is an unverified hypothesis). Games: store and promo panels in lobbies. TV: promoted rows on the home screen.

**Validity.** Effect sizes depend on the era and the site. Ad-likeness is ultimately a *perceptual judgment*, and a vision-LLM or human should confirm borderline cases (section 7).

### GZ-P11. Hand occlusion and handedness (the gaze side of grip)

**Statement.** On touchscreens the finger and hand hide the content under and behind the contact point. Feedback drawn there during the press, or feedback that lives under the thumb's arc, is not seen.

**Sources.** Touch occlusion of small targets under the fingertip: Vogel & Baudisch 2007, CHI ("Shift"). Occlusion shape models for direct input: Vogel et al., CHI 2009 (pen) (both UNCONFIRMED details). Korean handedness base rates are in `params.HANDEDNESS_SHARE_KR` (REF-kr-handedness-2009; not re-verified here).

**Operationalization.**
- The occlusion zone is a wedge from the contact point toward the hand. For the right thumb in one-handed use and the right index finger in cradle use, the wedge extends down and to the right; for left-handers it is mirrored. Width is about one finger breadth (≈ 16–20 mm `[assumption]`), extending to the screen edge on the hand's side.
- Feedback shown only during contact (press state, magnifier, slider value, tooltip) that falls inside the zone: **P3**. Raise to **P2** if the feedback is needed to complete the action (for example a slider value when setting an amount).
- Also feed the zone into GZ-02 step 8.

**Applicability.** Phones, tablets, touch kiosks, and touch games (virtual joystick thumbs cover the bottom corners, so HUD elements there are hidden).

**Validity.** The geometry is approximate. Hand size varies with the persona; reuse the reach model's thumb length.

### GZ-P12. Scanpath timing and prediction models

**Statement.** Scanpaths can be approximated by repeated selection on a priority map with inhibition of return and a cost for saccade distance. Time horizons follow from typical fixation durations.

**Parameters and sources**

| Value | Context | Source | Status |
|---|---|---|---|
| Mean fixation ≈ 225–250 ms and saccade ≈ 7–9 letter spaces in silent reading; ≈ 260–330 ms and 4–5° in scene perception; ≈ 180–275 ms and ≈ 3° in visual search | lab, typical adults | Rayner 2009, QJEP 62(8) (Table 1) | UNCONFIRMED |
| Covert selection every 50–60 ms; recognition > 150 ms per item | model | GS6 (Wolfe 2021) | V2 |
| Heatmaps at 1 s, 3 s, 7 s; improved scanpath model PathGAN++ | UIs | UEyes README | V1 |
| EyeFormer: transformer plus reinforcement learning, predicts scanpaths (including personalised ones) on UIs; evaluated with DTW, TDE and MultiMatch | UIST 2024 | EyeFormer GitHub README; arXiv 2404.10163 | V1 |
| Design choices in scanpath modelling strongly affect evaluation | ETRA 2024 (UNCONFIRMED venue) | Emami, Jiang, Guo & Leiva, arXiv 2405.08981 | V2 (existence) |

Fixation budget `[derived from UNCONFIRMED durations]`: 1 s ≈ 3–4 fixations, 3 s ≈ 9–12, 7 s ≈ 21–28.

**Operationalization (see section 4 for code).** Stochastic sampler with these `[policy]` parameters:
- N = 300 runs and 10–12 fixations (a 3 s horizon).
- Selection weight = priority^γ (γ = 2) × exp(−θ/λ), with λ = 5° (anchored on the 4–5° scene saccade), times the IOR factor (0.1 for already-visited elements), times (1 + β) for rightward or downward targets (β = 0.3, from the UEyes direction finding).
- The start point is the action point (`focus_point`) if one exists, otherwise the mode of the prior.

Outputs: for each element, P(fixated within the first k) for k = 1…n, the expected rank, and TTFF ≈ rank × 0.25–0.3 s. **GZ-01 v2** thresholds for the primary action `[policy]`:

| P(fixated within 3 s ≈ 10 fixations) | Result |
|---|---|
| ≥ 0.8 | pass |
| 0.5–0.8 | **P3** |
| < 0.5 | **P2** (inferred) |

Raise to **P1** only with observed failure, meaning the persona agent did not find the CTA or took a wrong path repeatedly. For critical status or error messages, use P(within 1 s ≈ 3 fixations) with the same cut-offs, together with GZ-02.

**Applicability.** All platforms. TV: replace saccade sampling with focus traversal. Visual attention follows the focus ring, so the cost is D-pad steps `[assumption]`. Games: add a motion channel and a centre-locked prior.

**Validity.** Scanpath models reproduce average statistics at best. Individual paths are highly variable; EyeFormer exists precisely because of personalisation. Report distributions only.

### GZ-P13. Eye-tracking metrics, for real data or for calibrating the simulation

**Definitions** (standard terms; Holmqvist et al. 2011, *Eye Tracking: A Comprehensive Guide to Methods and Measures*, UNCONFIRMED specifics):
- TTFF: time from stimulus onset to the first fixation in an area of interest (AOI).
- First fixation duration.
- Fixation count in an AOI.
- Dwell time, or total visit duration: the sum of fixation durations in the AOI, including revisits.
- Visit count or revisits.
- Entry order.
- AOI hit ratio: the share of participants who fixated the AOI at least once.

**Event detection** (UNCONFIRMED defaults): I-VT (velocity threshold, commonly 30°/s) or I-DT (dispersion about 1° with a minimum duration of about 100 ms) (Salvucci & Goldberg 2000, ETRA). Add a margin to AOIs of about the tracker's accuracy; Leiva's tracker had 0.4° accuracy (V2). Webcam trackers have errors of several degrees (UNCONFIRMED), which only suits large AOIs.

**Model validation metrics.**
- Saliency: AUC-Judd, shuffled AUC, NSS, CC, KLD, SIM (Bylinskii et al. 2019, TPAMI, "What do different evaluation metrics tell us about saliency models?", UNCONFIRMED specifics).
- Scanpaths: DTW, TDE, MultiMatch (V1, EyeFormer README) and ScanMatch.

**Calibration plan** `[policy]`. Run a Korean pilot with about 20 participants × 30 screens across phone, web and app, with one free-view block and one task block. Compute NSS and CC of the prior-only model, the bottom-up-only model and the full priority model, plus AOI hit ratios for primary CTAs and error messages. Tune the weights and the k factor. Until then, keep every gaze output `inferred` with basis `model`.

### GZ-P14. Korean text and layout specifics

- **Script and reading direction.** Korean UIs are horizontal LTR, so the LTR priors apply `[assumption]`. Vertical text is rare in UI.
- **Span and front-loading.** About 6–7 characters to the right per fixation (Choi & Koh 2009, V2 snippet). Put the discriminating word first in labels, list items and error messages ("결제 실패: 카드 한도 초과", not "고객님의 요청하신 결제가 … 실패하였습니다").
- **Spacing.** Korean readers rely less on spaces than English readers (Baek et al. 2023, V2). Whether CSS `word-break: keep-all` or line-breaking choices affect UI scanning is UNKNOWN; do not flag it.
- **Emphasis.** Italic is rarely used in Hangul typography, so emphasis relies on weight and colour. Colour-only emphasis fails for CVD personas (WCAG 1.4.1).
- **Density.** Korean portal and commerce screens are often information-dense. This is an unverified observation, not a sourced fact. Density reduces the useful field (Mackworth 1965) and increases crowding, so treat high edge density or element count in the viewport as a k-reducing context `[assumption]`.
- **Culture.** East Asian (Chinese) participants made more fixations on scene backgrounds than Americans did (Chua, Boland & Nisbett 2005, PNAS, UNCONFIRMED specifics). There is no evidence for Korean UI viewing, so **do not parameterise it**.
- **Standards.** KWCAG 2.2 (Korean national standard, based on WCAG) has items for contrast (4.5:1), colour-independent recognition, control of auto-changing content, flash limits and error correction (item numbering UNCONFIRMED). The WCAG 2.2 equivalents are SC 1.4.1, 1.4.3, 1.4.11, 2.2.2, 2.3.1, 2.4.11, 3.3.1 and 4.1.3 `[standard]`.

---

## 4. Reference gaze simulation (dependency-light, stdlib only)

The research sketch was ported to `ergoqa/hf/gaze.py` (Monte Carlo scanpath, position-prior mixtures, notice bands). Spectral residual ran in about 0.3 s on 64×128 in pure Python in the sketch; the repository keeps the cheaper centre-surround conspicuity. The pipeline:

```
INPUT  screenshot (RGB), elements [{id, box(css px), role, text, fg/bg colours, font, interactive, roles{primary,error_message,status,ad_like...}}],
       viewport, DPR, PPI (or mm/px), UI type, scroll offset/page height, action trace [{t, type, x, y}],
       persona {D_mm, age_band, load, cvd, low_vision, task_mode, goal_text, handedness, grip, scanning_strategy}
1  geometry: mm_per_px, theta() in degrees                                  (section 2)
2  image: if persona.cvd: simulate CVD; downsample to 64-128 px wide; add ±0.25% dither
3  S_bu  = spectral_residual(gray) or Itti-lite conspicuity; per element: mean(top 25% cells in box+1 cell)
4  F_pop = pop-out features per element (contrast vs surround, min ΔE to other controls, size rank, font rank)
5  P_pos = mixture prior(UI type) × screenful attenuation (web long pages)   (GZ-P1)
6  C_txt = element-type cue (heading/image/face/body/icon) + text-block model (F/layer-cake/spotted/bypass) (GZ-P2, P4)
7  T     = task relevance (goal_text vs label), gated by readability/crowding at the current fixation (GZ-P5, P7)
8  E     = expectation prior (curated conventional locations)               (GZ-P5)
9  A     = ad-likeness (0..5)                                               (GZ-P10)
10 priority(e) = Σ w_mode·[S_bu, P_pos, C_txt(+F_pop), T, E] − w_A·A/5 ; normalise to [0,1]
11 Monte Carlo scanpaths from start = action point or prior mode:
       w(e) = priority(e)^γ · exp(−θ(pos,e)/λ) · (IOR if visited) · (1+β if right/down)
       N=300 runs × n=10..12 fixations → P(first fixation ≤ k), expected rank, TTFF≈rank×0.25-0.3 s
12 checks GZ-01..GZ-10 (section 5); every result epistemic=inferred, basis=model, plus observed geometry facts
```

Key stdlib pieces (excerpt of the tested code):

```python
def spectral_residual(gray, blur_sigma=2.5):          # Hou & Zhang 2007; gray ~64 px wide, values 0..1
    F = _dft2([[complex(v) for v in row] for row in gray])
    L = [[math.log(abs(c) + 1e-12) for c in row] for row in F]
    P = [[cmath.phase(c) for c in row] for row in F]
    A = _box3(L)                                         # 3x3 mean, replicate border
    G = [[cmath.exp(complex(L[y][x] - A[y][x], P[y][x])) for x in range(len(L[0]))] for y in range(len(L))]
    S = [[abs(c) ** 2 for c in row] for row in _dft2(G, inverse=True)]
    S = _gauss_blur(S, blur_sigma)                       # port uses 9x9, sigma 3 at 128 px width
    lo, hi = min(map(min, S)), max(map(max, S))
    return [[(v - lo) / (hi - lo + 1e-12) for v in row] for row in S]

def simulate(elements, prio, start, mm_px, dist_mm, n_runs=300, n_fix=10, gamma=2.0,
             lam_deg=5.0, ior=0.1, dir_bias=0.3, seed=1):
    rng = random.Random(seed); ids = list(elements); hits = {i: [0]*n_fix for i in ids}
    for _ in range(n_runs):
        pos, seen = start, set()
        for k in range(n_fix):
            ws = []
            for i in ids:
                c = elements[i]
                w = (prio[i] ** gamma) * math.exp(-ecc_deg(pos, c, mm_px, dist_mm) / lam_deg)
                if i in seen: w *= ior
                if c[0] > pos[0] or c[1] > pos[1]: w *= (1 + dir_bias)
                ws.append(w)
            r = rng.random() * sum(ws); acc = 0.0
            for i, w in zip(ids, ws):
                acc += w
                if acc >= r: break
            if i not in seen:
                for kk in range(k, n_fix): hits[i][kk] += 1
            seen.add(i); pos = elements[i]
    return {i: [h / n_runs for h in hits[i]] for i in ids}
```

Sanity output from the test (synthetic phone screen, start at mid-screen): the title had P(≤3) = 0.79, and the bottom CTA with priority 0.7 had P(≤3) = 0.21 and P(≤10) = 0.60. Under the rule in P12 that would be GZ-01 **P2** (inferred). The web prior with μx = 0.26 and σx = 0.25 put 79.9% of its mass in the left half, matching NN/g 2017 by construction.

Seeds should be fixed per run for reproducibility, and results aggregated across personas in the swarm. Report the spread across personas; never report a single "the user will look here".

---

## 5. Check catalogue (proposed IDs; GZ-01..04 already exist in `ergoqa/checks.py`)

| ID | Check | Measure | Threshold `[policy]` | Severity (model = inferred) | Platforms |
|---|---|---|---|---|---|
| GZ-01 v2 | Primary action in early gaze | P(fixated ≤ 10 fixations ≈ 3 s) | ≥ 0.8 pass; 0.5–0.8; < 0.5 | P3; P2; P1 only if the persona run shows repeated failure | all |
| GZ-02 v2 | Feedback or error noticing after an action | θ from the action point, change salience, transient uniqueness U, persona k, occlusion | bands in GZ-P8 | critical: likely missed → P1, uncertain → P2; non-critical → P2 or P3; not in viewport and action failed → P1 observed | all (critical on phone, desktop toasts, TV, game HUD) |
| GZ-03 v2 | Critical info looks like an ad | A(e) feature count | ≥ 2; = 1 | P2; P3; P1 observed if the run misses it | web, mobile, TV home, game lobby |
| GZ-04 v2 | No pop-out, or competing primary styles | unique guiding feature (ΔE ≥ 20, contrast, 1.5× size); count of primary-styled controls | no unique feature, or ≥ 2 primaries | P3; P2 if the competitor is destructive or off-path | all |
| GZ-05 | Task-critical content in a low-attention zone | screenful index, expected attention share, right-third position (desktop) | screenful ≥ 3 or share < 0.10 | P2 critical / P3 informational | web, long mobile pages |
| GZ-06 | Key info buried in unformatted text | line index and character offset of the critical token; formatting present | line ≥ 3 or character > 20 without emphasis | P3; P2 if needed to finish the task | web, mobile |
| GZ-07 | Target outside its conventional location | expectation-table mismatch | mismatch on a critical path | P3; P2 critical | all (human-curated table) |
| GZ-08 | Search set-size cost | n_eff, estimated fixations and time | > 2 s or n_eff ≥ 20 | P3; P2 critical path with no filter or search | lists, grids, menus, inventories |
| GZ-09 | Front-loading (Korean label span) | character index of the discriminating keyword; repeated prefixes | beyond character 7, or ≥ 3 lines with the same prefix | P3 | all |
| GZ-10 | Silent in-place state change | value change with no highlight, motion or announcement, θ > 2° | as stated | P3; P2 if price or outcome changes | all |
| GZ-11 | Touch occlusion of contact-time feedback | feedback box ∩ occlusion wedge while pressed | any intersection | P3; P2 if essential | touch |

Every model-based observation stores its inputs (θ, D, mm/px, k, U, salience flags, priority, P(≤k)) so that reviewers can re-run it and see how sensitive it is.

---

## 6. Persona dimensions (gaze and attention)

| Dimension | Values | Base rate (source) | Effect in the simulation |
|---|---|---|---|
| `viewing_distance_mm` | phone 200/300/400; desktop 500/600/700; TV 2000/2700/3500 | Phone about 32–36 cm (Bababekova et al. 2011, UNCONFIRMED); repo defaults `[assumption]` | Every degree-based threshold (GZ-02, P7). Always run sensitivity |
| `age_band` | 10s … 70s+ | Korean shares placeholder in `AGE_BAND_SHARE_KR` `[assumption]`. Korea's 65+ share reached about 20% in Dec 2024 (UNCONFIRMED; verify with 행정안전부/KOSIS) | UFOV shrinks with age (Ball 1988, V2): k = 0.85 for 60s and 0.7 for 70s+ `[assumption]`; fixation durations +10–20% `[assumption]`; lower reading rate (existing param) |
| `attentional_load` | low (seated, single task), medium, high (walking, transit, combat, multitasking) | UNKNOWN for Korea | k = 1.0 / 0.85 / 0.7 `[assumption]` (Mackworth 1965; Williams 1985: direction only) |
| `task_mode` | free view (first impression), goal-directed, browsing | scenario-defined, not a population rate | Weight table (GZ-P5); ad-likeness suppression on in goal-directed mode (Benway 1998; NN/g 2018) |
| `scanning_strategy` | F, layer-cake, spotted, commitment, marking (mobile) | UNKNOWN (NN/g qualitative) | Text-block weights: commitment = upper bound (reads all), F = lower bound. Sample all for sensitivity, never report shares |
| `colour_vision` | normal, deutan, protan, tritan | Repo placeholder `CVD_MALE_SHARE_KR` 0.059 and type shares (perception brief; UNCONFIRMED here) | Saliency and pop-out computed on the CVD-simulated image; hue-only pop-out may vanish (GZ-04) |
| `low_vision` / `presbyopia` | none, presbyopic (no correction at near), low vision | UNKNOWN in this brief (see perception brief) | Readable span smaller: 5° gate → 3° `[assumption]`; k = 0.7; text-size checks from the perception brief |
| `handedness` × `grip` | right/left/mixed × one-hand thumb, cradle, two thumbs | Korea: right 86.3%, left 5.8%, mixed 7.9% (repo REF-kr-handedness-2009, N = 2,437; not re-verified here). Grip: Hoober 2013 (repo) | Side of the occlusion wedge (GZ-11, GZ-02 step 8) |
| `app_familiarity` | novice, returning, expert | UNKNOWN | Weight of the expectation prior E: 0.05 / 0.15 / 0.30 `[assumption]`; novices rely more on saliency (GS6 history guidance) |
| `screen_reader` | yes/no | UNKNOWN | Visual gaze model not applied; check programmatic exposure (WCAG 4.1.3) and focus management instead |
| `ad_avoidance` | low / typical / high | UNKNOWN (NN/g qualitative) | w_A = 0.15 / 0.3 / 0.45 `[assumption]` |

Base rates in the table exist only to generate plausible persona combinations for the swarm, which is already the stated purpose of that params block. They are never reported as prevalence estimates.

---

## 7. Judgments that cannot be automated (human or vision-LLM)

1. **Semantic noticing and comprehension.** A message being fixated does not mean it was understood. Whether the wording, tone and Korean honorifics convey the state (for example "처리 중" versus failure) is a human or LLM judgment.
2. **Task relevance of labels.** Ambiguous icons, brand-specific terms and Konglish or English labels. Similarity metrics are crude, and an LLM judge must mark itself as `inferred`.
3. **Ad-likeness perception.** Whether promo or native content *looks like* an ad to Korean users (carousel conventions, "이벤트" banners). A vision-LLM can pre-screen; a human confirms P2 or higher.
4. **Expectation priors.** Where users of a particular Korean app category expect things (Naver, Kakao, Coupang, banking conventions). This needs curation and domain knowledge, ideally real-user data.
5. **Intentional hierarchy.** Whether an element *should* be primary; the model cannot know the business intent.
6. **Emotional or social content.** Faces, gaze direction of people in images, and humour or shock imagery affect attention in ways not captured here.
7. **Motion design quality.** Whether an animation reads as feedback or as decoration. Frame-difference magnitude is automatable; meaning is not.
8. **Game context.** Whether a HUD warning competes with a boss telegraph, and how immersion and flow shape attention. These need playtest observation.
9. **Real prevalence.** Any statement like "most users will miss X" requires real eye-tracking or behavioural data. Synthetic personas never supply it.

---

## 8. Contradictions and uncertainties

| Topic | Disagreement | How to handle it |
|---|---|---|
| Left-half share (desktop web) | 69% (NN/g 2010) against 80% (NN/g 2017) | Use the range: μx 0.26–0.36 (σx 0.25). Default 0.30 |
| Above-the-fold share | 80% (NN/g 2010) against 57% (NN/g 2018) | Use 2018 as the default; run 2010 as a sensitivity case |
| Centre against top-left | Centre bias in scenes (Tatler 2007) and above-centre posters (UEyes) against top-left for UIs (UEyes, Leiva, Buscher). Buscher: foraging produces centre-left and centre fixations in the first second | Choose the prior by UI type *and* task mode. Do not use a single prior |
| Salient but ignored | Feature integration and pop-out predict that salient items capture attention, while banner blindness shows *more* visible ad-like items can be missed | Model top-down suppression explicitly (A(e)) only in goal-directed mode |
| Bottom-up models | Standard in saliency literature, but a weak fit on mobile UIs (Leiva) | Low weight; benchmark optional ML models offline |
| Z-pattern / Gutenberg | Common in design practice; no eye-tracking support found | Do not encode |
| Current repo feedback thresholds | 10° (non-salient) and 20° (salient) treated as pass limits, tagged `[paper]` | These are not paper values. Recommend 2/5° and 10/20° bands tagged `[policy]` |
| "Mobile" saliency data | Collected by showing mobile screenshots on a lab monitor with remote trackers (SMI RED250, Gazepoint), not handheld | This is an inference from the tracker types; verify in the papers. Handheld viewing adds scrolling, hand occlusion and a closer D |
| Korean span | One study (Choi & Koh 2009), snippet-level | Keep the 5° angular policy gate (robust to the exact character count) |
| Absolute search times | Lab slopes (20–40 ms/item, covert) against GUI search with eye movements and reading | Use only for relative comparisons |
| Age and load factor k | Direction supported (Ball 1988; Mackworth 1965; Williams 1985); magnitude has no UI source | `[assumption]`, sensitivity only |
| TV and in-play games | No GUI eye-tracking dataset found for either | Priors are `[assumption]`. Collect pilot data before relying on them |

---

## 9. Recommended changes to the current repo (gaze block)

1. `params.GAZE_POSITION_PRIOR["phone"]`: change `centre_x` from 0.5 to about 0.35, `centre_y` to about 0.25 (Leiva 2020; UEyes). Keep it `[policy]` until fitted on UEyes.
2. Desktop web: keep `centre_x` 0.35. Document the derived range 0.26–0.36 (NN/g 69–80%). Add separate `desktop_app` (two-band) and `poster` (centre-above) priors. Mark `tv` and game in-play as `[assumption]` with "no dataset".
3. Add screenful attenuation (0.57, 0.17, geometric tail with r = 0.605) for long pages `[derived]`.
4. `check_gaze`: pass `start=(focus.x, focus.y)` to `predicted_scanpath`. The code currently computes `start` and then passes `start=None`.
5. `predicted_scanpath`: use a distance discount in **degrees** (exp(−θ/λ), λ = 5°) instead of viewport-diagonal fractions. Otherwise phone and desktop behave inconsistently. Make it stochastic and report P(≤ k).
6. Replace `FEEDBACK_ECCENTRICITY_DEG = 10` and `..._SALIENT = 20` with the band tables in GZ-P8, and retag them `[policy]` (anchors: Rayner; Ball 1988; Mackworth 1965). Derive change salience from the before/after difference (onset or motion, ≥ 3:1, ≥ 1°, U ≥ 0.5), not from static priority ≥ 0.7.
7. Raise GZ-03 to P2 for task-critical content with A(e) ≥ 2. Add the IAB-size and label features and a mobile carousel case.
8. Lower `GAZE_COMBINE_WEIGHTS["bottom_up"]` for phone to ≤ 0.3 (Leiva: colour and size mattered less than position, text and images).
9. Add the SR stdlib implementation, with dither, as an alternative conspicuity map, and keep the existing Itti-lite. Record which one was used in the observation's `model_id`.

---

## 10. Sources

V1 = read at the time of writing on GitHub; V2 = search-result text; U = recalled, not opened at the time of writing.

**UI saliency, eye-tracking datasets and models**
- Jiang, Leiva, Rezazadegan Tavakoli, Houssel, Kylmälä, Oulasvirta. *UEyes: Understanding Visual Saliency across User Interface Types.* CHI 2023. https://dl.acm.org/doi/10.1145/3544548.3581096 (V2); dataset and code README https://github.com/YueJiang-nj/UEyes-CHI2023 (V1); extended dataset paper https://arxiv.org/abs/2402.05202 (V2)
- Leiva, Xue, Bansal, Tavakoli, Köroğlu, Du, Dayama, Oulasvirta. *Understanding Visual Saliency in Mobile User Interfaces.* MobileHCI 2020. https://dl.acm.org/doi/10.1145/3379503.3403557 ; PDF https://userinterfaces.aalto.fi/mobile-saliency/resources/mobile-saliency.pdf (V2)
- Bylinskii, Kim, O'Donovan, Alsheikh, Madan, Pfister, Durand, Russell, Hertzmann. *Learning Visual Importance for Graphic Designs and Data Visualizations.* UIST 2017. https://dx.doi.org/10.1145/3126594.3126653 ; code https://github.com/cvzoya/visimportance (V2)
- Kim, Bylinskii, Borkin, Gajos, Oliva, Durand, Pfister. *BubbleView.* ACM TOCHI 24(5), 2017. https://dl.acm.org/doi/10.1145/3131275 (V2)
- Fosco et al. *Predicting Visual Importance Across Graphic Design Types.* UIST 2020. https://dl.acm.org/doi/10.1145/3379337.3415825 (V2)
- Jiang et al. *EyeFormer: Predicting Personalized Scanpaths with Transformer-Guided Reinforcement Learning.* UIST 2024. https://arxiv.org/abs/2404.10163 ; https://github.com/YueJiang-nj/EyeFormer-UIST2024 (V1)
- Emami, Jiang, Guo, Leiva. *Impact of Design Decisions in Scanpath Modeling.* 2024. https://arxiv.org/abs/2405.08981 (V2)
- Buscher, Cutrell, Morris. *What Do You See When You're Surfing? Using Eye Tracking to Predict Salient Regions of Web Pages.* CHI 2009. https://www.microsoft.com/en-us/research/publication/what-do-you-see-when-youre-surfing-using-eye-tracking-to-predict-salient-regions-of-web-pages/ (V2)
- Djamasbi, Siegel, Tullis. *Visual Hierarchy and Viewing Behavior: An Eye Tracking Study.* HCII 2011, LNCS 6761. https://link.springer.com/chapter/10.1007/978-3-642-21602-2_36 (V2 existence)

**NN/g (practitioner eye-tracking studies)**
- *F-Shaped Pattern for Reading Web Content* (2006). https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content-discovered/ (V2)
- *F-Shaped Pattern of Reading on the Web: Misunderstood, But Still Relevant (Even on Mobile)* (2017). https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/ (V2)
- *Text Scanning Patterns: Eyetracking Evidence.* https://www.nngroup.com/articles/text-scanning-patterns-eyetracking/ (V2)
- *The Layer-Cake Pattern of Scanning Content on the Web.* https://www.nngroup.com/articles/layer-cake-pattern-scanning/ (V2)
- *Horizontal Attention Leans Left* (2010; 2017 update). https://www.nngroup.com/articles/horizontal-attention-leans-left/ ; https://www.nngroup.com/articles/horizontal-attention-original-research/ (V2)
- *Scrolling and Attention* (2018; 2010 original). https://www.nngroup.com/articles/scrolling-and-attention/ ; https://www.nngroup.com/articles/scrolling-and-attention-original-research/ (V2)
- *Banner Blindness Revisited: Users Dodge Ads on Mobile and Desktop* (2018). https://www.nngroup.com/articles/banner-blindness-old-and-new-findings/ (V2)
- Vanseo Design. *3 Design Layouts: Gutenberg Diagram, Z-Pattern, and F-Pattern.* https://vanseodesign.com/web-design/3-design-layouts/ (V2; secondary, used only for the "little empirical evidence" point)

**Banner blindness**
- Benway. *Banner Blindness: The Irony of Attention Grabbing on the World Wide Web.* Proc. HFES 42nd Annual Meeting, 1998. https://journals.sagepub.com/doi/10.1177/154193129804200504 (V2)
- Benway & Lane. *Banner Blindness: Web Searchers Often Miss "Obvious" Links.* 1998. https://www.ruf.rice.edu/~lane/papers/banner_blindness.pdf (V2)
- Pagendarm & Schaumburg. *Why Are Users Banner-Blind?* JoDI, 2001. https://jodi-ojs-tdl.tdl.org/jodi/article/view/jodi-37/38 (V2 existence; finding U)
- Owens, Chaparro, Palmer. *Text Advertising Blindness: The New Banner Blindness?* JUS 6(3), 2011. http://uxpajournal.org/wp-content/uploads/sites/7/pdf/JUS_Owens_May_2011.pdf (V2 existence)
- *The processing of native advertising compared to banner advertising: an eye-tracking experiment.* Electronic Commerce Research, 2021. https://link.springer.com/article/10.1007/s10660-021-09523-7 (V2)

**Visual search and attention theory**
- Treisman & Gelade. *A Feature-Integration Theory of Attention.* Cognitive Psychology 12:97–136, 1980. https://www.sciencedirect.com/science/article/abs/pii/0010028580900055 (V2)
- Wolfe. *What Can 1 Million Trials Tell Us About Visual Search?* Psych Sci 9(1), 1998. https://journals.sagepub.com/doi/10.1111/1467-9280.00006 (V2)
- Wolfe. *Guided Search 6.0: An Updated Model of Visual Search.* Psychon Bull Rev 28:1060–1092, 2021. https://link.springer.com/article/10.3758/s13423-020-01859-9 (V2)
- Wolfe. *Visual search.* Scholarpedia. http://www.scholarpedia.org/article/Visual_search (V2)
- Itti, Koch, Niebur. *A Model of Saliency-Based Visual Attention for Rapid Scene Analysis.* IEEE TPAMI 20(11), 1998. https://www.cse.psu.edu/~rtc12/CSE597E/papers/Itti_etal98pami.pdf (V2 overview; parameters U)
- Hou & Zhang. *Saliency Detection: A Spectral Residual Approach.* CVPR 2007. http://vigir.missouri.edu/~gdesouza/Research/Conference_CDs/IEEE_CVPR_2007/data/papers/0299.pdf (V2); port https://github.com/uoip/SpectralResidualSaliency (V1 code)
- Tatler. *The central fixation bias in scene viewing.* JoV 7(14):4, 2007. https://doi.org/10.1167/7.14.4 (V2)
- Yantis & Jonides. *Abrupt visual onsets and selective attention.* JEP:HPP 10(5):601–621, 1984. https://doi.org/10.1037/0096-1523.10.5.601 (U)
- Kieras & Hornof. *Towards accurate and practical predictive models of active-vision-based visual search.* CHI 2014. (U)
- Pirolli & Card. *Information foraging.* Psychological Review 106(4), 1999. https://doi.org/10.1037/0033-295X.106.4.643 (U)
- Blackmon, Polson, Kitajima, Lewis. *Cognitive Walkthrough for the Web.* CHI 2002. (U)
- Cockburn, Gutwin, Greenberg. *A Predictive Model of Menu Performance.* CHI 2007. (U)

**Peripheral vision, UFOV and load**
- Ball, Beard, Roenker, Miller, Griggs. *Age and visual search: expanding the useful field of view.* JOSA A 5(12):2210–2219, 1988. https://opg.optica.org/josaa/abstract.cfm?uri=josaa-5-12-2210 (V2)
- Ball, Owsley, Sloane, Roenker, Bruni. *Visual attention problems as a predictor of vehicle crashes in older drivers.* IOVS 34:3110, 1993. https://iovs.arvojournals.org/arvo/content_public/journal/iovs/933170/3110.pdf (V2)
- Goode et al. *Useful Field of View and Other Neurocognitive Indicators of Crash Risk in Older Adults.* J Clin Psychol Med Settings, 1998. https://link.springer.com/article/10.1023/A:1026206927686 (V2)
- Edwards et al. *The useful field of view test: Normative data for older adults.* Arch Clin Neuropsychol, 2006. https://www.sciencedirect.com/science/article/pii/S0887617706000382 (V2 existence)
- Mackworth. *Visual noise causes tunnel vision.* Psychonomic Science 3:67–68, 1965. https://link.springer.com/article/10.3758/BF03343023 (V2)
- Williams. *Tunnel Vision Induced by a Foveal Load Manipulation.* Human Factors 27(2), 1985. https://doi.org/10.1177/001872088502700209 (V2 existence)
- Wu & Wolfe. *The Functional Visual Field(s) in simple visual search.* https://search.bwh.harvard.edu/new/pubs/UFOV_WU&Wolfe.pdf (V2 existence)
- Bartram, Ware, Calvert. *Moticons: detection, distraction and task.* IJHCS 58(5), 2003. (U)
- ISO 17488:2016. *Road vehicles — Transport information and control systems — Detection-response task (DRT) for assessing attentional effects of cognitive load in driving.* iso.org (U)
- Game Accessibility Guidelines. https://gameaccessibilityguidelines.com/ (U)

**Change blindness and inattentional blindness**
- Rensink, O'Regan, Clark. *To see or not to see: The need for attention to perceive changes in scenes.* Psych Sci 8(5), 1997. https://doi.org/10.1111/j.1467-9280.1997.tb00427.x (U)
- Simons & Levin. *Failure to detect changes to people during a real-world interaction.* Psychon Bull Rev 5, 1998. (U)
- Simons & Chabris. *Gorillas in our midst.* Perception 28:1059–1074, 1999. https://doi.org/10.1068/p281059 (U)
- Drew, Võ, Wolfe. *The invisible gorilla strikes again.* Psych Sci, 2013. (U)
- Varakin, Levin, Fidler. *Unseen and unaware: implications of recent research on failures of visual awareness for human-computer interface design.* HCI 19(4), 2004. (U)
- Durlach. *Change blindness and its implications for complex monitoring and control systems design and operator training.* HCI 19(4), 2004. (U)

**Reading, acuity and Korean**
- Rayner. *Eye movements in reading and information processing: 20 years of research.* Psych Bull 124(3):372–422, 1998. http://andrewd.ces.clemson.edu/courses/cpsc881/papers/reading/Ray98_readingSurvey.pdf (V2 span; other values U)
- Rayner. *Eye movements and attention in reading, scene perception, and visual search.* QJEP 62(8), 2009. https://doi.org/10.1080/17470210902816461 (U)
- Choi & Koh. *The perceptual span during reading Korean sentences.* Korean Journal of Cognitive Science 20(4):573–601, 2009. (V2 snippet)
- Kim, Radach, Vorstius. *Eye movements and parafoveal processing during reading in Korean.* Reading and Writing, 2012. https://link.springer.com/article/10.1007/s11145-011-9349-0 (V2)
- Baek, Choi, Gordon. *Reading spaced and unspaced Korean text: Evidence from eye-tracking during reading.* QJEP, 2023. https://journals.sagepub.com/doi/abs/10.1177/17470218221104736 (V2)
- *Peeking into Hangul's Window.* In Handbook on the Korean Language and Literacy (Springer, 2025). https://link.springer.com/chapter/10.1007/978-3-031-88087-2_28 (V2 existence)
- Bouma. *Interaction effects in parafoveal letter recognition.* Nature 226:177–178, 1970. (U)
- Pelli & Tillman. *The uncrowded window of object recognition.* Nat Neurosci 11:1129–1135, 2008. (U)
- Chua, Boland, Nisbett. *Cultural variation in eye movements during scene perception.* PNAS 102(35), 2005. (U)

**Methods, standards and other**
- Holmqvist et al. *Eye Tracking: A Comprehensive Guide to Methods and Measures.* Oxford University Press, 2011. (U)
- Salvucci & Goldberg. *Identifying fixations and saccades in eye-tracking protocols.* ETRA 2000. (U)
- Bylinskii, Judd, Oliva, Torralba, Durand. *What do different evaluation metrics tell us about saliency models?* IEEE TPAMI, 2019. (U)
- Machado, Oliveira, Fernandes. *A physiologically-based model for simulation of color vision deficiency.* IEEE TVCG 15(6), 2009. (U)
- Johansson, Westling, Bäckström, Flanagan. *Eye–hand coordination in object manipulation.* J Neurosci 21(17), 2001. (U)
- Vogel & Baudisch. *Shift: A technique for operating pen-based interfaces using touch.* CHI 2007. (U)
- Bababekova, Rosenfield, Hue, Huang. *Font size and viewing distance of handheld smart phones.* Optom Vis Sci 88(7), 2011. (U)
- W3C. *Web Content Accessibility Guidelines (WCAG) 2.2.* https://www.w3.org/TR/WCAG22/ (standard; SC numbers cited from memory, U)
- KWCAG 2.2 (한국형 웹 콘텐츠 접근성 지침 2.2). (U; item numbering unverified)
