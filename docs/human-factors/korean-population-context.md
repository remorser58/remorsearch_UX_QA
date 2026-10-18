# Korean population and platform context for ergonomic persona profiles

Brief for `ergoqa` (`docs/ergonomic-swarm-spec.md`, `ergo-profile.v1`). Prepared 2026-09-28.

**Purpose.** These base rates help the sampler choose *plausible combinations* of ergonomic attributes. They do not describe real-user prevalence for any product. A swarm result stays "k of n simulated profiles", never "x% of users" (spec rule 0.3).

## 0. How to read this brief (retrieval limits)

This brief was written in October 2026 under two retrieval limits. Read them before you reuse any number.

1. **Web search was rate-limited** after about a dozen searches; no further searches could run.
2. **WebFetch and curl were blocked** for almost every host by the egress proxy. Blocked hosts included huggingface.co, gallup.co.kr, kats.go.kr, sizekorea.kr, koreascience.kr, kosis.kr, law.go.kr, pubmed, pmc, mdpi, the NVIDIA blogs, namu.wiki and all Korean news sites. Only github.com, raw.githubusercontent.com, developer.android.com, developer.apple.com and microsoft.com could be reached.

Every value therefore carries an evidence tag:

| Tag | Meaning | Use for sampling? |
|---|---|---|
| **[P]** | Primary text read at the time of writing (law text, standard text, device descriptor file, vendor doc) | Yes |
| **[D]** | Computed by a third party from the full dataset. I read their output files at the time of writing. | Yes, but pin the dataset revision |
| **[S]** | Search-engine snippet only; fetching the page was blocked. The value is as the search engine summarised the named page. | Only as a provisional prior. Verify before release. |
| **[2]** | Secondary source (news, community) seen via a snippet | Provisional. Label the source as secondary. |
| **[X]** | Taken from a sibling brief (`research/handedness-grip-reach.md`). I did not re-verify it. | Provisional |
| **[R]** | UNCONFIRMED recall. I did **not** retrieve it at the time of writing. It is listed only so a person can verify it. | **No.** Do not sample from it until someone confirms it. |
| **NOT RETRIEVED** | No value was obtained | Use the stratified-coverage default only |

---

## 1. Summary table

| # | Parameter | Value | Population | Year | Source | Tag |
|---|---|---|---|---|---|---|
| 1 | Self-reported left-handed | **7%** overall. By age: 13–18: 13%, 19–29: 12%, 30s: 8%, 40s: 6%, 50s: 4%, 60+: 3% | Korea, aged 13+, n = 1,700 | Nov 2025 | Gallup Korea, reported by wbcb.co.kr https://www.wbcb.co.kr/news/articleView.html?idxno=99202 | [2][S] |
| 2 | Self-reported left-handed | **5%** (right-handed 93%, no answer 3%). By age: 20s 8%, 30s 6%, 40s 6%, 50s 3%, 60+ 2%. Eats with left hand 4%; **writes with left hand 1%**. | Korea, aged 19+, n = 1,217 | 28–31 Oct 2013 | Gallup Korea https://www.gallup.co.kr/gallupdb/reportContent.asp?seqNo=491 | [S] |
| 3 | Self-reported left-handed (trend) | 4% | Korea, aged 19+ (Gallup) | 2002 | Same Gallup 2013 report (seqNo=491) | [S] |
| 4 | Hand dominance, 3 categories | Right 86.3%, left **5.8%**, ambidextrous **7.9%** | Korea, n = 2,437 (Jung et al., Ergonomics 52(11)) | 2009 | https://www.khan.co.kr/article/20091115073301A ; https://pubmed.ncbi.nlm.nih.gov/19851904/ | [2][S] |
| 5 | Left / ambidextrous | 3.9% / 8.4% | KoGES cohort, aged 40–69, n = 8,806 | 2001–02 data, published 2023 | Song et al. 2023, Brain and Behavior https://onlinelibrary.wiley.com/doi/full/10.1002/brb3.3121 | [X] |
| 6 | Global left-handedness | Best estimate **10.6%**. Range 9.3% (strict) to 18.1% (non-right, lenient). | Meta-analysis, worldwide | 2020 | Papadatou-Pastou et al., Psychol Bull 146(6):481–524 https://research-information.bris.ac.uk/en/publications/human-handedness-a-meta-analysis/ | [S] |
| 7 | Hand length / breadth, mean (SD) | Men 185.95 (8.13) / 86.06 (4.10) mm. Women 172.40 (7.15) / 77.66 (4.00) mm. | Korean adults, n = 325, 58 hand dimensions (Kim & Kee 2012). Not a national survey. | 2012 | https://koreascience.kr/article/JAKO201215053142965.pdf | [S]; attribution to this paper is unconfirmed |
| 8 | Hand length / breadth, mean ± SD | 180.6 ± 10.7 / 80.8 ± 6.7 mm | 45 Korean smartphone users (28 men, 17 women), aged 20s–50s, recruited to match Korean hand-size distributions | 2020 | Choi et al., Applied Sciences 10(23):8374 https://www.mdpi.com/2076-3417/10/23/8374 | [S] |
| 9 | Hand length, 8th Size Korea survey | "about 18.5 cm, aged 20–39" (no sex split, no SD) | Korean adults 20–39 | Survey 2020–21 (KATS release Dec 2021) | Community repost of KATS results https://theqoo.net/square/3914759372 | [2], weak |
| 10 | Thumb length (Korea) | **NOT RETRIEVED** (Size Korea 8th-survey table not reachable) | — | — | https://sizekorea.kr/human-info/meas-report?measDegree=8 | — |
| 11 | Population share by 10-year band, whole population | 0–9: 5.79%, 10s: 9.05%, 20s: 11.12%, 30s: 13.06%, 40s: 14.83%, 50s: **16.89%**, 60s: 15.50%, 70+: 13.76% | Resident-registered population (주민등록인구), total 51,117,378 | 31 Dec 2025 | 행정안전부 (MOIS), reported by Money Today https://www.mt.co.kr/policy/2026/01/04/2026010216565058654 | [S] |
| 12 | Share by band, adults 20+ (derived from #11) | 20s 13.06, 30s 15.34, 40s 17.41, 50s 19.83, 60s 18.20, 70+ 16.16 (%) | Resident-registered, aged 20+ (85.16% of total) | 2025 | Computed here from #11 | derived |
| 13 | Nemotron-Personas-Korea age distribution | 19 only: 1.05, 20s 13.50, 30s 14.97, 40s 17.56, 50s 19.88, 60s 17.87, 70s 9.66, 80+ 5.51 (%). Mean 50.66, median 51, range 19–99. | 1,000,000 synthetic records | Released Apr 2026 | EDA of the full dataset https://github.com/SeanPresent/Nemotron-Personas-Korea-EDA (commit 28f59bc) | [D] |
| 14 | Nemotron-Personas-Korea schema | 1,000,000 rows × **26 columns**; 7 persona texts per record (7M total); 17 provinces, 252 districts, 2,120 occupations; CC BY 4.0; ages 19–99 | Synthetic Korean adults 19+ | Apr 2026 | EDA repo above; audit https://github.com/eopchang/nemotron-personas-korea-audit (commit 99b064b); field list https://github.com/Yenaaa/persona_survey | [D][P] |
| 15 | Samsung / Apple smartphone share | **NOT RETRIEVED** | — | — | To retrieve: Gallup Korea annual "스마트폰 사용률 & 브랜드" report (gallup.co.kr) | [R] lead in §5 |
| 16 | Foldable share | **NOT RETRIEVED** | — | — | — | — |
| 17 | CSS viewport widths, emulation profiles | Galaxy S24 360×780 @3; Galaxy S8 360×740 @3; Galaxy A55 480×1040 @2.25 (Playwright) vs 360×800 @2.25 (DevTools); Galaxy S20 Ultra 412×915 @3.5; Galaxy A51/71 412×914 @2.625; Z Fold 5 cover 344×882, inner 690×829; Z Fold 6 cover 412×968, inner 744×860; iPhone 15 393×852 screen; iPhone 15 Pro Max 430×932 screen | Emulation descriptors, not market data | 2025–26 | Playwright 1.56.1 `deviceDescriptorsSource.json`; Chrome DevTools `EmulatedDevices.ts` https://github.com/ChromeDevTools/devtools-frontend/blob/main/front_end/models/emulation/EmulatedDevices.ts (commit 2d671c5) | [P] |
| 18 | Window size classes | Compact width < 600 dp = 99.96% of phones in portrait. Medium 600–840 dp covers most unfolded inner displays in portrait. | Android device population (Google) | current | https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes | [P] |
| 19 | Older adults' digital-informatization level (NIA 디지털정보격차 실태조사) | **NOT RETRIEVED** | — | 2024/2025 | 한국지능정보사회진흥원 (NIA) report | — |
| 20 | Colour-vision deficiency (CVD) prevalence, Korea | **NOT RETRIEVED** | — | — | — | [R] lead in §8 |
| 21 | Presbyopia prevalence by age, Korea | **NOT RETRIEVED** | — | — | — | — |
| 22 | Registered disabled persons (visual, physical) | **NOT RETRIEVED** | — | — | 보건복지부 등록장애인 현황; 2023 장애인 실태조사 | [R] lead in §10 |
| 23 | Korean web accessibility standard | KWCAG 2.2 = **KS X OT0003:2022**, revised 2022-12-28. 4 principles, 14 guidelines, **33 check items**. Contrast ≥ 4.5:1 (3:1 for ≥ 18 pt or 14 pt bold). Control diagonal ≥ **6.0 mm** is *recommended*. Flashing 3–50 Hz is prohibited. | Standard | 2022 | Unofficial HTML conversion https://github.com/a11ykr/kwcag22 ; official text: 국립전파연구원 (rra.go.kr) | [P] |
| 24 | Anti-discrimination law: apps | 장애인차별금지법 Art. 21(2) (added 2021-07-27): providers must give "정당한 편의" for mobile-device apps. Enforcement decree Art. 14(4)–(6) (2023-03-30; amended 2025-12-31): smartphone apps; phased scope in 별표 3의2; content includes meeting MSIT verification criteria and supporting voice commands. Non-compliance with a confirmed corrective order: fine up to ₩30M (Art. 50). | Law | Act effective 2025-11-11 version; decree 2026-01-22 | legalize-kr mirror of law.go.kr https://github.com/legalize-kr/legalize-kr (`kr/장애인차별금지및권리구제등에관한법률/`) | [P] |
| 25 | Digital Inclusion Act (디지털포용법) | Act No. 20672, promulgated 2025-01-21, in force 2026-01-22. Replaces 지능정보화기본법 Arts. 46–49, which were deleted. Art. 19: public bodies must ensure accessibility of websites, mobile apps, kiosks and e-publications; private operators have a duty of effort. Art. 21: accessibility quality certification, valid 1 year (decree Art. 21). Art. 37: up to ₩30M for kiosk corrective-order non-compliance. | Law | 2026 | legalize-kr mirror (`kr/디지털포용법/`) | [P] |
| 26 | Game use by platform (KOCCA 게임이용자 실태조사) | **NOT RETRIEVED** | — | 2024/2025 | 한국콘텐츠진흥원 | — |
| 27 | Korean reading speed (syllables per minute) | **NOT RETRIEVED** | — | — | — | — |

---

## 2. Handedness (왼손잡이)

### Findings

- **Gallup Korea, 2013** [S]. Source: https://www.gallup.co.kr/gallupdb/reportContent.asp?seqNo=491 (page fetch blocked; snippet of the Gallup page).
  - Survey: 28–31 Oct 2013, nationwide, aged 19+, n = 1,217.
  - Results: left-handed 5%, right-handed 93%, no answer 3%.
  - By age: 20s 8%, 30s 6%, 40s 6%, 50s 3%, 60+ 2%.
  - By task: eats with the left hand 4%; writes with the left hand **1%**.
  - Earlier Gallup survey: 4% in 2002.
  - Note: a second-hand summary (gnnews.co.kr) phrases the 2013 result as "4% left, 1% ambidextrous, 95% right". The Gallup page snippet (5 / 93 / 3) is preferred.
- **Gallup Korea, Nov 2025** [2][S]. Source: news article https://www.wbcb.co.kr/news/articleView.html?idxno=99202.
  - Survey: aged 13+, n = 1,700. Left-handed **7%**.
  - By age: 13–18: 13%, 19–29: 12%, 30s: 8%, 40s: 6%, 50s: 4%, 60+: 3%.
  - The same snippet says about 6% eat and about 5% write with the left hand. It is **unconfirmed** whether these figures come from the 2025 survey. The jump from 1% (2013) to 5% in writing hand is large, so verify it against the Gallup release.
  - Attitudes (same article): 73% would leave their own child left-handed. By contrast, 59% of respondents aged 50+ wanted to correct left-handedness in 2002.
- **Jung et al. 2009, Ergonomics 52(11)** [2][S]. Survey of 2,437 Koreans. Sources: khan.co.kr and sciencetimes coverage; PubMed 19851904.
  - Results: 86.3% right, 5.8% left, 7.9% ambidextrous.
  - Age: 79% of left-handers were under 30.
  - Family: when the father was left-handed, 49.5% of children were left-handed (45 people). When both parents were right-handed, the rate was 3.3% (70 people).
  - 65% of left-handers reported everyday inconvenience.
- **KoGES cohort** [X]: 3.9% left, 8.4% ambidextrous (aged 40–69, n = 8,806; Song et al. 2023).
- **Global** [S]: 10.6% best estimate, range 9.3–18.1% depending on the criterion (Papadatou-Pastou et al. 2020).

### Interpretation

- Korean self-reported left-handedness (4–7%) sits below the global ~10.6%.
- It has a steep age gradient. Teens and people in their 20s are close to the global rate; people aged 60+ report 2–3%.
- This fits historical forced correction. The writing hand is the most-corrected task: only 1% wrote left-handed in 2013 while 5% self-identified as left-handed.
- An "ambidextrous" category (7.9–8.4%) appears only in surveys that offer it.

### Mapping to `attributes.handedness`

- **Stratified coverage.** Every run with count ≥ 3 includes at least one `left` and one `mixed` profile, whatever the base rate says.
- **Base-rate sampling.** Use the age-conditional left-handed rate from Gallup 2025 as P(left | age_band):
  - 20s: 0.12
  - 30s: 0.08
  - 40s: 0.06
  - 50s: 0.04
  - 60s and 70s+: 0.03 (Gallup reports only "60+")
  - For P(mixed), use 0.08 as a flat placeholder from Jung 2009 and KoGES. The age gradient for "mixed" is unknown, so this placeholder is UNCONFIRMED.
- **Keep handedness separate from the grip or operating hand.** The operating hand is a separate assumption (`grip`), and left-hand phone operation is much more common than left-handedness. See the sibling brief `handedness-grip-reach.md`: Hoober 2013 found 33% of one-handed use was left-thumb, and a self-selected Korean poll found 37% left-hand use [X].

---

## 3. Hand anthropometry (Size Korea / KATS)

### Findings

- **8th Korean anthropometric survey (제8차 한국인 인체치수조사)** [S]. Run by KATS (국가기술표준원).
  - Fieldwork: from Oct 2020, over two years (2020–21). The sizekorea.kr listing labels it "8차 인체치수조사(2020~23)".
  - Sample: planned about 6,400 adults aged 20–69. The sibling brief reports n = 6,839 [X].
  - Measurement items grew from 332 to 365, with more 3D measures.
  - Sources: KATS press release https://www.kats.go.kr/content.do?cmsid=240&searchField=title&y=0&x=0&mode=view&page=1&cid=23007 and KDI summary https://eiec.kdi.re.kr/policy/materialView.do?num=205689&pp=20 (both via snippet).
  - **Sex- and age-specific hand length, hand breadth and thumb length (mean and SD) were NOT RETRIEVED.** The tables are at https://sizekorea.kr/human-info/meas-report?measDegree=8 (blocked). A Scribd copy titled "(통계자료_1~2차년도) 제8차 한국인 인체치수 조사 측정 결과 자료" also exists.
- **Kim & Kee 2012** [S]. 대한안전경영과학회지 14(1). 325 subjects, 58 hand dimensions.
  - A search snippet attributes these values to the paper: men hand length 185.95 mm (SD 8.13), breadth 86.06 (4.10); women 172.40 (7.15), 77.66 (4.00).
  - It is **unconfirmed** that these numbers come from this paper and which Size Korea round they use.
- **Jee, Bahn & Yun 2015**, Forensic Sci Int [S].
  - Data: Size Korea hand data, n = 321 (167 men, 154 women), with even proportions across ages 20s–70s.
  - The most common hand type was "wide hand, short fingers" for men and "narrow hand, short fingers" for women.
  - Korean hands were wider with shorter fingers than those in 8 other national samples.
  - Numbers not retrieved.
- **Choi et al. 2020**, Applied Sciences 10(23):8374 [S].
  - Sample: 45 Korean users, aged 20s–50s, recruited across hand-length × hand-breadth terciles "considering Korean male and female hand-size distributions". Mean hand length 180.6 ± 10.7 mm; breadth 80.8 ± 6.7 mm.
  - Task: one-handed hard-key operation on 3.0–7.0″ mockups.
  - Dominant grips: L3-R1-K1 70.0%, L4-R1 13.3%, L3-R1-T1 12.0%.
- **Community repost of the 8th survey** [2]: "average hand length 18.5 cm, aged 20–39". No sex split, no SD. Weak.
- **Thumb length.** No Korean population value was retrieved.
  - The sibling brief notes that landmark definitions differ: Parhi 2006 used about 115 mm (US lab, tip-to-base), and Size Korea's "thumb length" is about 8.1 cm [X].
  - **Do not copy a thumb length across sources without matching the landmark.**

### Mapping to `thumb_length_mm` and `hand_percentile`

- Treat hand size as **percentile strata** (P5 / P50 / P95 per sex), not as prevalence.
- Until the Size Korea 8th-survey table is pulled, a provisional sex-specific normal model can use Kim & Kee's [S] means and SDs for hand length:
  - Men P5 ≈ 172.6, P95 ≈ 199.3 mm
  - Women P5 ≈ 160.6, P95 ≈ 184.2 mm
  - These are computed as mean ± 1.645 SD. Label them `hand_length_source: "Kim&Kee2012 [unverified]"`.
- Derive `thumb_length_mm` only through a declared landmark and a declared scaling rule. Keep it in `assumption_fields`.
- Size Korea's 8th survey covers ages 20–69 only. Hand sizes for profiles aged 70+ are extrapolations.

---

## 4. Korean adult age distribution (주민등록인구, 2025)

### Findings

- **Publisher.** Resident registration statistics (주민등록 인구통계) are published by **행정안전부 (MOIS)**, not 통계청. Official monthly tables: https://jumin.mois.go.kr/ageStatMonth.do (blocked). Open data: https://www.data.go.kr/data/3033304/fileData.do.
- **31 Dec 2025** [S], via Money Today, 2026-01-04:
  - Total 51,117,378. The population fell for the 6th year in a row, and "1 in 5 is aged 65+".
  - Shares: 50s 16.89%, 60s 15.50%, 40s 14.83%, 70+ 13.76%, 30s 13.06%, 20s 11.12%, 10s 9.05%, under 10 5.79%.
- **Context** [S]: at end-2023, the 70+ population exceeded people in their 20s for the first time (Newsis 2024-01-10, https://www.newsis.com/view/NISX20240110_0002587131).

### Comparison with Nemotron-Personas-Korea (adults 20+, renormalised)

| Band | MOIS 2025, 20+ (derived) | Nemotron 20+ (derived from [D]) |
|---|---|---|
| 20s | 13.06% | 13.64% |
| 30s | 15.34% | 15.12% |
| 40s | 17.41% | 17.75% |
| 50s | 19.83% | 20.09% |
| 60s | 18.20% | 18.06% |
| 70+ | 16.16% | 15.33% |

Nemotron's age marginal tracks the 2025 register within about 1 percentage point per band.

- The dataset contains **no one under 19**. The "10s" band holds only age 19 (1.05%).
- The 80+ band is 65% female, consistent with longevity.
- Nemotron's marginal is by design, so this closeness is **not** evidence about any product's users.

### Mapping to `age_band`

- `age_band` comes from the persona record's `age` field. It is a dataset attribute, not an assumption.
- A `10s` profile cannot be backed by a Nemotron record except at age 19. Treat any profile aged 13–18 as `origin: manual`, with age in `assumption_fields`.
- For stratified coverage, the spec's "60s+" stratum can draw from the 60s, 70s and 80+ records.

---

## 5. Smartphone market, device mix and viewports

### Findings

- **Brand share (Samsung vs Apple) and foldable share: NOT RETRIEVED.**
  - Where to get it: Gallup Korea's annual *스마트폰 사용률 & 브랜드* release (gallup.co.kr/gallupdb). It reports by age; young adults differ sharply from older adults.
  - Also: Counterpoint or StatCounter (gs.statcounter.com, Korea, mobile vendor).
  - **[R] lead, UNCONFIRMED:** recent Gallup releases put Samsung Galaxy at roughly two-thirds or more of Korean adult smartphone users and iPhone at roughly a quarter, with iPhone the majority among people in their 20s. Do not use this until verified.
- **Emulation viewports** [P]. These are *emulation descriptor values*, not measured Korean market data.

| Device | CSS viewport (portrait) | DPR | Source |
|---|---|---|---|
| Galaxy S24 | 360 × 780 | 3 | Playwright 1.56.1 |
| Galaxy S8 | 360 × 740 | 3 | Playwright 1.56.1 |
| Galaxy S8+ | 360 × 740 | 4 | DevTools |
| Galaxy S9+ | 320 × 658 | 4.5 | Playwright 1.56.1 |
| Galaxy A55 | **480 × 1040** | 2.25 | Playwright 1.56.1 |
| Galaxy A55 | **360 × 800** | 2.25 | DevTools |
| Galaxy S20 Ultra | 412 × 915 | 3.5 | DevTools |
| Galaxy A51/71 | 412 × 914 | 2.625 | DevTools |
| Galaxy Z Fold 5 | cover 344 × 882; inner 690 × 829 | 2.625 | DevTools |
| Galaxy Z Fold 6 | cover 412 × 968; inner 744 × 860 | 2.625 | DevTools |
| Galaxy Tab S9 | 640 × 1024 | 2.5 | Playwright |
| iPhone 15 / 15 Pro | viewport 393 × 659 (screen 393 × 852) | 3 | Playwright |
| iPhone 15 Pro Max | viewport 430 × 739 (screen 430 × 932) | 3 | Playwright |
| iPhone SE (3rd gen) | 375 × 667 | 2 | Playwright |
| Pixel 7 | 412 × 839 (screen 412 × 915) | 2.625 | Playwright |

- The Galaxy A55 entries disagree (480 vs 360 px wide). Samsung's effective CSS width also changes with the user's display-size or zoom setting. **Treat viewport width as a scenario parameter**; the 360–412 px band is not a single constant.
- Android window size classes [P]: compact width < 600 dp covers 99.96% of phones in portrait. Medium (600–840 dp) covers most large unfolded inner displays in portrait.

### Mapping to `device_id` and `viewport_css`

- The device is always an assumption.
- Stratify by width class:
  - ≤ 360 (Galaxy S / A default)
  - 390–430 (iPhone, Galaxy Ultra / Plus)
  - 600–840 (foldable inner, tablet portrait)
- Plus at least one foldable cover screen (344 px, narrower than any phone).
- Do not weight by brand share until #15 is verified.

---

## 6. Older adults' digital literacy (NIA 디지털정보격차 실태조사)

**NOT RETRIEVED.**

- NIA publishes the survey annually. It reports the "digital informatization level" of four vulnerable groups (disabled, low-income, farmers/fishers, older adults 55+) relative to the general public (= 100), split into access, capability and use.
- **Law context [P]:** under the Digital Inclusion Act, the survey now falls under 디지털포용법 Art. 11 (실태조사).
- **Mapping:** the Nemotron HF release has **no digital-skill field**. The Data Designer docs list `digital_skill` only for `ja_JP`. So `cognition.familiarity` (first_use / returning / expert) is always an assumption.
- Coverage should guarantee a `first_use` profile in the 60s+ stratum. That is a coverage choice, not a prevalence claim.

---

## 7. Presbyopia

**NOT RETRIEVED.** No Korean age-specific prevalence was obtained.

**Mapping:** `vision.presbyopia` is an assumption.

- In `base_rate_sample`, age may condition the draw to keep combinations plausible. The onset of presbyopia in the 40s is general physiology, but the Korean rates are unsourced here.
- The spec's `persona_to_profile` must still **not** infer it from the record.
- Coverage: at least one presbyopic profile in each run with a 40+ persona.

---

## 8. Colour-vision deficiency (CVD)

**NOT RETRIEVED.**

- **[R] lead, UNCONFIRMED:** Korean media often cite about 5.9% of men and about 0.4% of women. The original study was not identified.
- The protan/deutan split for Korea was not retrieved. The general textbook pattern is that deutan types outnumber protan types among red-green CVD. That is also unverified here.

**Mapping:** `vision.cvd` is an assumption.

- Sex-conditional sampling is plausible because CVD is X-linked, but the rates must be verified first.
- Coverage: always include one `deutan` and one `protan` profile.
- The legal hook is KWCAG 2.2 item 5.4.1 (색에 무관한 콘텐츠 인식) [P].

---

## 9. Korean reading speed

**NOT RETRIEVED.** No study was obtained that gives syllables per minute for Korean adults or seniors.

**Mapping:** leave `cognition.reading_wpm_ko` at 0 (unset), or give an explicit placeholder with `reading_rate_source: "assumption"`. Any reading-time check must report its rate as a model parameter, not a Korean norm.

---

## 10. Disability statistics relevant to digital access

**NOT RETRIEVED.**

- Sources to pull:
  - 보건복지부 annual 등록장애인 현황 (registered disabled persons by type and severity)
  - 2023 장애인 실태조사 (triennial survey, KIHASA)
- **[R] lead, UNCONFIRMED:** about 2.6 million registered disabled persons (about 5% of the population). Physical (지체) disability is the largest type, at a bit over 40%. Visual disability is below 10%. Verify all of these.

**Mapping:** `motor.tremor`, `vision.acuity = low`, and screen-reader use are assumptions.

- The Nemotron HF release has no disability field.
- The NGC / Data Designer `ko_KR` variant adds health indicators (blood pressure, blood sugar, BMI, waist, drinking, smoking) but still no disability, vision or handedness field [P].

---

## 11. KWCAG 2.2 and Korean accessibility law

### KWCAG 2.2 [P]

Source: https://github.com/a11ykr/kwcag22. This is an unofficial HTML conversion that states it did not change the content. The official text is at 국립전파연구원.

- **Identity:** KS X OT0003:2022. First enacted 2005-12-21; revised 2022-12-28 (replaces 2.1, KS X OT0003:2015). Structure: 4 principles, 14 guidelines, 33 check items.
- **Items directly usable as ergoqa checks:**

| Item | Name | Requirement |
|---|---|---|
| 5.4.1 | 색에 무관한 콘텐츠 인식 | Content must be perceivable without colour |
| 5.4.3 | 텍스트 콘텐츠의 명도 대비 | Contrast ≥ 4.5:1. It may drop to 3:1 for text ≥ 18 pt or 14 pt bold, or for zoomable text. |
| 6.1.3 | 조작 가능 | Each control's diagonal ≥ 6.0 mm and a ≥ 1 px non-reactive inner margin are **recommended** ("바람직하다"), not mandated |
| 6.2.1 | 응답시간 조절 | Time limits must be adjustable. Exceptions: real-time games, auctions, sessions ≥ 20 h. |
| 6.3.1 | 깜빡임과 번쩍임 사용 제한 | No flashing at 3–50 Hz |
| 6.5.1 | 단일 포인터 입력 지원 | Single-pointer input |
| 6.5.2 | 포인터 입력 취소 | Pointer cancellation |
| 6.5.4 | 동작기반 작동 | Motion actuation |

- The text also refers to **3:1 for non-text UI components** (links, buttons, input/check boxes).

### 장애인차별금지 및 권리구제 등에 관한 법률 [P]

Source: legalize-kr mirror of law.go.kr. The Act version is in force from 2025-11-11.

- **Art. 20:** bans discrimination in access to electronic and non-electronic information.
- **Art. 21(1):** providers must give the necessary means for equal access to electronic information.
- **Art. 21(2):** added 2021-07-27. Providers must give "정당한 편의" for apps on mobile devices.
- **Enforcement decree Art. 14** (decree in force 2026-01-22):
  - (2)1: an accessible website is a required means.
  - (4): the covered software is apps on smartphones and other mobile terminals.
  - (5): the phased scope of covered providers is in 별표 3의2. The table was not read.
  - (6): required content:
    1. Meet the verification criteria set by MSIT under 디지털포용법 시행령 Art. 24(2).
    2. Show whether the app meets them before purchase or installation.
    3. Give disability-specific install and use information.
    4. Give support channels in sign language, text and voice.
    5. Support **voice commands** when the app is hard to operate.
- **Decree Art. 24(2) criteria** must consider eight function types: hand/arm motion, reaction time, vision, colour discrimination, hearing, voice input, cognition and flashing. This lines up one-to-one with the profile's motor, reaction_time, vision, cvd and cognition fields.
- **Sanctions:** up to ₩30M fine for not complying with a confirmed corrective order (Art. 50). Malicious discrimination: up to 3 years' imprisonment or a ₩30M fine (Art. 49).

### 디지털포용법 (Digital Inclusion Act) [P]

Act No. 20672, promulgated 2025-01-21, in force 2026-01-22.

- It moved web accessibility out of **지능정보화 기본법**, where Arts. 46–49 are now "삭제 <2025.1.21>".
- **Art. 19(1):** national agencies and public bodies must ensure accessibility of:
  - websites
  - mobile apps
  - kiosks (무인정보단말기)
  - e-publications
- **Art. 19(2):** private operators (지능정보사업자) have a duty of effort.
- **Art. 20:** kiosk operators, manufacturers and lessors have obligations; a corrective order is possible.
- **Arts. 21–22 and decree Arts. 16, 21:** 접근성 품질인증.
  - This is the former 웹 접근성 품질인증 under 지능정보화기본법 Art. 47. Addenda Art. 2 carries over existing certificates.
  - The criteria are the four POUR-style principles.
  - Certification is valid for **1 year**.
- **Art. 37:** fines up to ₩30M for ignoring a kiosk corrective order, and up to ₩5M for false certification.
- **Caveat:** the mirror's header shows a later amendment (No. 21496, promulgated 2026-03-31, in force **2027-04-01**) that adds provisions such as Art. 25-2. Check the version in force on law.go.kr before citing article text in product documents.

### Not retrieved

- The MSIT notice (고시) that holds the app verification criteria.
- The current TTA mobile-app accessibility guideline (name and version UNCONFIRMED).

### Mapping

These laws and standards set severity context (for example, a KWCAG 5.4.3 failure on a public-sector site). They are not base rates. They justify guaranteeing CVD, low-vision, motor and voice-command profiles in coverage.

---

## 12. Korean gaming habits (KOCCA 게임이용자 실태조사)

**NOT RETRIEVED.**

- KOCCA publishes the survey annually. It reports game-use rate and platform-use rates (mobile, PC, console, arcade) by age for people aged 10–65.
- **Mapping:** for `surface.kind = game`, pick `grip` (gamepad / two_thumbs landscape) and `device_id` (switch-handheld, phone landscape, desktop) by coverage.
- Weight platforms only after the KOCCA table is retrieved.

---

## 13. Nemotron-Personas-Korea: what it contains and what it lacks

### Verified facts

- **Tags:** [D] = the third-party full-data EDA and audit repos. [P] = the Data Designer documentation in NVIDIA-NeMo/DataDesigner (commit 7044b5f, 2026-09-23).
- **Source:** `nvidia/Nemotron-Personas-Korea` on Hugging Face, released April 2026. The HF page itself was blocked.
- **License:** CC BY 4.0 [D].
- **Size:** 1,000,000 records, 26 columns, 0 missing values, 0 duplicate uuids, 9 Arrow shards [D]. Each record carries 7 persona narratives, so the "7M personas" headline counts narratives, not people [S][D].
- **Generation:**
  - A PGM samples demographics seeded on KOSIS, Supreme Court (names), NHIS (health), KREI (food) and NAVER Cloud [D][S].
  - Text comes from `google/gemma-4-31B-it`, about 1.7B tokens [D].
  - The OCEAN / Big-Five sampling stage, with T-scores μ = 50, σ = 10, clipped to 20–80, is documented for the collection pipeline [P].
- **Coverage:** Korean adults 19+ (observed range 19–99, mean 50.66). 17 provinces, 252 districts, 2,120 distinct occupations, `country` is always 대한민국 [D].

### Columns (26), verbatim

Source: [P] https://github.com/Yenaaa/persona_survey, matched by the [D] column profile.

- **Identifier:** `uuid`
- **Persona texts (7):** `persona`, `professional_persona`, `sports_persona`, `arts_persona`, `travel_persona`, `culinary_persona`, `family_persona`
- **Attributes (6):** `cultural_background`, `skills_and_expertise`, `skills_and_expertise_list`, `hobbies_and_interests`, `hobbies_and_interests_list`, `career_goals_and_ambitions`. The two `_list` fields are *string-encoded* lists.
- **Demographic and geographic (12):** `sex`, `age`, `marital_status`, `military_status`, `family_type`, `housing_type`, `education_level`, `bachelors_field`, `occupation`, `district`, `province`, `country`

### Two distributions

The NGC / Data Designer `ko_KR` PersonSampler asset documents *extra* Korea fields [P]:

- `economic_activity_status`, `housing_tenure`, `income_bracket`
- `drinking_status`, `smoking_status`
- `blood_pressure_status`, `blood_sugar_status`, `bmi_status`, `waist_status`
- core fields such as `first_name`, `birth_date`, `city`

`persona_ref.dataset` and `persona_ref.revision` must record which one was used.

### Known quality notes from the audit [D]

- `housing_type` is nearly independent of household attributes.
- `military_status` is almost a deterministic function of `occupation`. Also, 9.81% of `현역` records are female.
- `무직` (unemployed) is 36.7% of occupations.
- **Do not** use persona fields as proxies for ergonomic traits.

### Not in the dataset (must come from separate base rates and stay in `assumption_fields`)

- handedness
- grip or operating hand
- hand, thumb and finger size
- visual acuity, presbyopia, CVD
- hearing
- motor, tremor, disability status
- device, brand, OS, viewport, assistive technology
- digital skill or familiarity (Japan only has `digital_skill`)
- reading speed
- gaming habits
- situational context: mobility, lighting, free hands
- people under 19

---

## 14. Profile attribute mapping

| `ergo-profile.v1` field | From persona record? | Base rate in this brief | Status |
|---|---|---|---|
| `age_band` | **Yes** (`age`) | #11–13 (sanity check only) | Dataset attribute |
| `handedness` | No | #1–6, age-conditional | Assumption |
| `grip` | No | None for Korea (Choi 2020 grip postures are task-specific) | Assumption |
| `thumb_length_mm`, `hand_percentile` | No (sex may condition) | #7–10, provisional | Assumption |
| `device_id`, `orientation` | No | #17–18 (viewport); share not retrieved | Assumption |
| `vision.presbyopia` | No (age may condition in base-rate mode only) | Not retrieved | Assumption |
| `vision.cvd` | No (sex may condition) | Not retrieved; [R] lead | Assumption |
| `vision.acuity`, `motor.*` | No | Not retrieved; [R] lead | Assumption |
| `context.*` | No | None | Assumption |
| `cognition.familiarity` | No | NIA not retrieved | Assumption |
| `cognition.reading_wpm_ko` | No | Not retrieved | Assumption (unset) |
| `reaction_time_ms` | No | Not in scope | Assumption |

## 15. What must remain a scenario assumption

1. **Every ergonomic field** in the table above except `age_band`. This matches spec rule 0.4.
2. **Cross-attribute dependence.** No source gives joint distributions. Examples: left-handed × small hand, CVD × age, device × age. The sampler treats them as independent, and that independence is itself an assumption.
3. **Conditioning on persona demographics.** Age-conditional handedness or presbyopia, and sex-conditional CVD or hand size, may be used only in `base_rate_sample` mode to choose plausible combinations.
   - Record the condition and the `base_rate_refs` ID.
   - `persona_to_profile` never derives them.
4. **Any value tagged [S], [2], [X] or [R].** These are provisional until someone replaces them with the primary table.
5. **Viewport width for a named device.** Emulator descriptors disagree, for example Galaxy A55 at 480 vs 360 px, and user display-scaling changes it.
6. **Profiles under 19.** Nemotron has no such records.
7. **Outputs.** No output may state or imply Korean prevalence. Report coverage only ("k of n profiles").

## 16. Retrieval to-do (to close the gaps)

1. **Size Korea 8th-survey hand tables**, by sex and age: 손직선길이, 손너비, 엄지손가락길이, with mean, SD and percentiles. https://sizekorea.kr/human-info/meas-report?measDegree=8
2. **Gallup Korea smartphone brand release**, latest year, by age band.
3. **NIA 2024 and 2025 디지털정보격차 실태조사:** the older-adults index and its sub-indices.
4. **보건복지부 등록장애인 현황**, latest year: counts by type (지체, 시각, 청각, 뇌병변).
5. **A Korean CVD prevalence study** (original, peer-reviewed), with protan/deutan split by sex.
6. **A Korean presbyopia prevalence study** (for example, KNHANES-based), by age.
7. **KOCCA 2024 and 2025 게임이용자 실태조사:** platform use rates by age.
8. **A Korean reading-rate study** (syllables per minute, adults and seniors). For example, a Korean MNREAD adaptation, if one exists.
9. **The Nemotron HF dataset card:** pin the `revision` hash and confirm the age floor (19) on the card itself.

## Sources

**Primary: read at the time of writing**

- legalize-kr, Korean law mirror (law.go.kr source). https://github.com/legalize-kr/legalize-kr — `kr/장애인차별금지및권리구제등에관한법률/법률.md` (in force 2025-11-11), `시행령.md` (in force 2026-01-22), `kr/디지털포용법/법률.md`, `시행령.md`, `kr/지능정보화기본법/법률.md` (Arts. 46–49 deleted 2025-01-21). Commit 3969940.
- 한국형 웹 콘텐츠 접근성 지침 2.2 (KS X OT0003:2022), unofficial HTML conversion. https://github.com/a11ykr/kwcag22 (commit 63b3b36). Official source: 국립전파연구원 https://www.rra.go.kr
- NVIDIA NeMo Data Designer docs, `fern/versions/latest/pages/concepts/person_sampling.mdx` and `devnotes/posts/nemotron-personas.mdx`. https://github.com/NVIDIA-NeMo/DataDesigner (commit 7044b5f, 2026-09-23)
- Nemotron-Personas-Korea field list. https://github.com/Yenaaa/persona_survey
- Playwright 1.56.1 device descriptors (`playwright-core/lib/server/deviceDescriptorsSource.json`). https://github.com/microsoft/playwright
- Chrome DevTools `EmulatedDevices.ts`. https://github.com/ChromeDevTools/devtools-frontend (commit 2d671c5)
- Android Developers, "Use window size classes". https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes

**Third-party dataset analyses: read at the time of writing [D]**

- SeanPresent, Nemotron-Personas-Korea deep EDA (2026-04-28). https://github.com/SeanPresent/Nemotron-Personas-Korea-EDA (commit 28f59bc)
- eopchang, Nemotron-Personas-Korea joint-distribution audit (2026-05). https://github.com/eopchang/nemotron-personas-korea-audit (commit 99b064b)

**Search snippets only (page fetch blocked) [S] / [2]**

- Gallup Korea (2013), 왼손잡이 조사. https://www.gallup.co.kr/gallupdb/reportContent.asp?seqNo=491
- 복지TV부울경 (2025/26), 한국 10대 왼손잡이 13%. https://www.wbcb.co.kr/news/articleView.html?idxno=99202
- 경향신문 (2009), 한국인 5.8%가 왼손잡이. https://www.khan.co.kr/article/20091115073301A ; Jung et al. 2009, Ergonomics 52(11):1362–1371. https://pubmed.ncbi.nlm.nih.gov/19851904/
- Papadatou-Pastou et al. (2020), Human handedness: a meta-analysis, Psychol Bull 146(6):481–524. https://research-information.bris.ac.uk/en/publications/human-handedness-a-meta-analysis/
- 김상호·기도형 (2012), 손관련 인체측정자료를 이용한 한국인의 손모양 유형분류. https://koreascience.kr/article/JAKO201215053142965.pdf
- Jee, Bahn, Yun (2015), Determination of sex from various hand dimensions of Koreans, FSI. https://www.sciencedirect.com/science/article/abs/pii/S0379073815004387
- Choi et al. (2020), Effects of Smartphone Size and Hand Size on Grip Posture…, Appl Sci 10(23):8374. https://www.mdpi.com/2076-3417/10/23/8374
- KATS, 제8차 한국인 인체치수조사 press release. https://www.kats.go.kr/content.do?cmsid=240&searchField=title&y=0&x=0&mode=view&page=1&cid=23007 ; KDI summary https://eiec.kdi.re.kr/policy/materialView.do?num=205689&pp=20 ; Size Korea report index https://sizekorea.kr/human-info/meas-report?measDegree=8
- 더쿠 community repost, "사람 평균 손크기" (secondary, weak). https://theqoo.net/square/3914759372
- 머니투데이 (2026-01-04), 국민 5명 중 1명은 65세 이상…주민등록인구 6년째 줄었다. https://www.mt.co.kr/policy/2026/01/04/2026010216565058654
- 뉴시스 (2024-01-10), 70대 이상 인구 20대 첫 초월. https://www.newsis.com/view/NISX20240110_0002587131
- AI타임스 / NVIDIA Korea coverage of the Nemotron-Personas-Korea release (Apr 2026). https://www.aitimes.com/news/articleView.html?idxno=209762

**Sibling brief (not re-verified) [X]**

- `research/handedness-grip-reach.md`: KoGES handedness (Song et al. 2023, https://onlinelibrary.wiley.com/doi/full/10.1002/brb3.3121), Size Korea n = 6,839, thumb-landmark caveat, Hoober grip rates.
