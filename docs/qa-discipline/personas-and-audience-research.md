# Personas grounded in audience research, and how to compose a persona set

Date: 2026-09-28. Research brief for `skills/ergonomic-persona-swarm-qa`. It covers:

- persona foundations and their critiques;
- data-driven, automatic and LLM-generated personas;
- inclusive design, extreme users and lead users;
- context of use (ISO 9241-11, ISO 9241-210, ISO/IEC 25063) and jobs to be done;
- audience evidence sources, including Korean public statistics;
- methods for composing a persona set.

Section 3 applies these to the `ergo-audience.v1` contract (`docs/ergonomic-swarm-spec.md` §13) and to `ergoqa/audience.py`. This is research only. No code, benchmark, answer key or validation record was changed.

**Evidence tags.**

- [standard]: normative text.
- [paper]: peer-reviewed.
- [industry]: vendor or company documentation, or a practitioner book.
- [report]: survey or government statistics.
- [snippet]: seen only in a search-result excerpt, not checked in the source.
- [derived]: my own computation, from cited numbers or from this repository's files.
- [opinion]: practitioner opinion (mine unless attributed).

I could not open any primary source (see below), so every literature claim is tagged [snippet], followed by the source type. For example, [snippet · paper] means a peer-reviewed paper I saw only through a search excerpt.

**Read this first.**

1. **No primary source was opened.** WebFetch returned `EGRESS_BLOCKED` for every host I tried: csrc.nist.gov, quantuxbook.com, cnchapman.wordpress.com, cdn.standards.iteh.ai and inclusive.microsoft.design. All literature claims and all statistics below come from search excerpts. Check every number in its source before it becomes a threshold, a default or a sentence in a report.
2. **The most useful numbers come from this repository, not from the literature.** In the frozen held-out run (`8c1de02`), 111 of 225 swarm findings (49 %) exist only because of which profiles were in the swarm. Only 5 of those 111 name the condition that triggered them [derived, §2.9]. Composition decides almost half of what the swarm reports, but the report rarely says why. Commit `782a15c`, made today, fixes part of this. Checks that only ever evaluate one kind of profile (PC-03, PC-05) still name no condition (R12, AP-05).
3. **The spec already follows most of what the literature recommends.** It has evidence-linked segments, a base profile plus one-facet variations, inclusive floors, and coverage instead of prevalence. Most rows in §3 therefore tighten, prune or instrument the spec rather than replace it.
4. **Two sibling briefs overlap with this one.** `software-testing-foundations.md` §2.4 (combinatorial coverage) and `usability-evaluation-methods.md` (UEM-01 coverage denominators) cover related ground. I cross-reference them instead of repeating them.

---

## 1. Scope and sources searched

**Local context read (nothing modified)**

- `skills/ergonomic-persona-swarm-qa/SKILL.md`.
- In the same skill's `references/`:
  - `human-factors-checks.md`. I read it at the start and re-checked the check IDs after commit `ab7dea4`, which marked PC-05, GZ-01 and GZ-04 as "hypothesis" checks.
  - `persona-agent-protocol.md`.
  - `audience-research.md`.
- `docs/ergonomic-swarm-spec.md`:
  - §0, §2 (profile), §6 (observation), §7 (finding), §12 and §12.1 (benchmark);
  - §13 (audience), re-read after it changed on disk.
- `docs/validation/heldout-mixed-frozen-8c1de02.json`, top-level summary only.

**Repository data analysed.** These are tool outputs and code, not answer keys.

- Ablation results:
  - `docs/validation/experiments/ablation-dev-8707b70.json`.
- Frozen held-out outputs:
  - `.ergo-bench/heldout-frozen/findings-swarm.json`;
  - `.ergo-bench/heldout-frozen/profiles.json`.
- Code:
  - `ergoqa/audience.py`: constants, function list, the `compose` docstring;
  - `ergoqa/checks.py`: `applicable()` and which profile attributes the checks read;
  - `ergoqa/profiles.py`: strata and label code;
  - `ergoqa/swarm.py`: `_differential`, `aggregate`, and commit `782a15c`;
  - `ergoqa/params.py`: `AGE_BAND_SHARE_KR` and the CVD shares.
- `docs/human-factors/korean-population-context.md`: the items marked NOT RETRIEVED.
- The sibling briefs `docs/qa-discipline/usability-evaluation-methods.md` (header) and `software-testing-foundations.md` (§2.4).

**Not opened**

- Any `benchmarks/*/answer_key.json` or `benchmarks/*/README.md`.
- `.ergo-bench/*/score-*.json`, because these repeat answer-key content.
- Anything inside `benchmarks/heldout-2/` beyond its directory names. Its product briefs are Stage-0 inputs for the blind test.

**Web.** I ran 32 WebSearch queries. The target was 30 or fewer; the last two covered Cooper's persona types and IDEO's extremes, which the brief asked for by name. All 5 WebFetch attempts were blocked.

Persona foundations and critiques
- Cooper, About Face persona types (secondary summaries): https://www.sciencedirect.com/topics/computer-science/primary-persona ; https://flylib.com/books/en/2.153.1.34/1/
- Pruitt & Grudin 2003, DUX: https://www.microsoft.com/en-us/research/publication/personas-practice-theory/ ; https://www.microsoft.com/en-us/research/wp-content/uploads/2017/03/pruitt-grudinold.pdf
- Pruitt & Adlin 2006, *The Persona Lifecycle*: https://www.sciencedirect.com/book/9780125662512/the-persona-lifecycle ; https://booksite.elsevier.com/samplechapters/9780123814180/01~Front_Matter.pdf
- Chapman & Milham 2006, HFES 50:634–636: https://journals.sagepub.com/doi/10.1177/154193120605000503
- Chapman, Love, Milham, ElRif & Alford 2008, HFES 52(16):1107–1111: https://journals.sagepub.com/doi/abs/10.1177/154193120805201602
- Matthews, Judge & Whittaker 2012, CHI, 1219–1228: https://dl.acm.org/doi/10.1145/2207676.2208573
- Friess 2012, CHI: https://dl.acm.org/doi/10.1145/2207676.2208572

Data-driven, automatic and LLM-generated personas
- McGinn & Kotamraju 2008, CHI: https://dl.acm.org/doi/10.1145/1357054.1357292
- Salminen, Guan, Jung & Jansen 2021, IJHCI 37(18):1685–1708: https://www.tandfonline.com/doi/full/10.1080/10447318.2021.1908670
- Salminen, Chhirang, Jung, Thirumuruganathan, Guan & Jansen 2022, *Big Data* 10(4):313–336: https://doi.org/10.1089/big.2021.0177 ; https://persona.qcri.org/blog/big-data-small-personas-how-algorithms-shape-the-demographic-representation-of-data-driven-user-segments/
- Automatic Persona Generation (APG) research page: https://persona.qcri.org/persona-research
- Li et al. 2025, "LLM Generated Persona is a Promise with a Catch" (NeurIPS 2025 position track): https://arxiv.org/abs/2503.16527 ; https://neurips.cc/virtual/2025/poster/121924

Inclusive design, extremes, lead users
- Microsoft Inclusive Design, persona spectrum: https://inclusive.microsoft.design/articles/inclusive-101-guidebook
- IDEO.org, Extremes and Mainstreams: https://designthinking.ideo.com/resources/extremes-and-mainstreams-design-toolkit-by-ideo-org
- von Hippel 1986, *Management Science* 32(7):791–805: https://pubsonline.informs.org/doi/abs/10.1287/mnsc.32.7.791
- Lilien, Morrison, Searls, Sonnack & von Hippel 2002, *Management Science* 48(8):1042–1059: https://pubsonline.informs.org/doi/abs/10.1287/mnsc.48.8.1042.171

Context of use and jobs
- ISO 9241-11:2018 (preview and summary): https://webstore.ansi.org/preview-pages/ISO/preview_ISO+9241-11-2018.pdf ; https://www.dialogdesign.dk/usability-user-experience-ux/
- ISO/IEC 25063:2014: https://www.iso.org/standard/35789.html
- ODI opportunity algorithm (secondary): https://en.wikipedia.org/wiki/Outcome-Driven_Innovation ; https://www.productplan.com/glossary/opportunity-scoring

Segmentation and group sizes
- Nielsen 2000, NN/g: https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/

Evidence sources and review mining
- Khalid, Shihab, Nagappan & Hassan 2015, *IEEE Software* 32(3):70–77: https://dl.acm.org/doi/10.1109/ms.2014.50
- Maalej & Nabil 2015, RE: https://www.researchgate.net/publication/301442885_Bug_report_feature_request_or_simply_praise_On_automatically_classifying_app_reviews ; journal extension: https://link.springer.com/article/10.1007/s00766-016-0251-9
- Guzman & Maalej 2014, RE, 153–162: https://research.vu.nl/en/publications/how-do-users-like-this-feature-a-fine-grained-sentiment-analysis-
- Eler, Orlandin & Oliveira 2019, IHC: https://dl.acm.org/doi/10.1145/3357155.3358477
- AlOmar et al. 2021, CHI: https://arxiv.org/pdf/2210.09947
- "Why Are Accessibility App Reviews Rare?" (2025): https://link.springer.com/chapter/10.1007/978-3-032-04999-5_11
- Appt accessibility-settings statistics: https://appt.org/en/stats ; https://andycarter.dev/blog/more-than-half-of-smartphone-users-use-accessibility-settings

Korean public data
- 행정안전부, 65+ share reaches 20 % (2024-12-24): https://www.mois.go.kr/frt/bbs/type010/commonSelectBoardArticle.do?bbsId=BBSMSTR_000000000008&nttId=114622 ; data: https://jumin.mois.go.kr/
- 2024 방송매체 이용행태조사 (released 2024-12-30): https://www.kmcc.go.kr/user.do?boardId=1113&page=A05030000&dc=K00000200&boardSeq=64951&mode=view ; https://www.gov.kr/portal/ntnadmNews/4125633
- 한국갤럽 스마트폰 사용률·브랜드 2025: https://x.com/GallupKoreaNews/status/1942144620974207458 ; https://www.datanews.co.kr/news/article.html?no=139581 ; https://www.gallup.co.kr/gallupdb/reportContent.asp?seqNo=1566
- NIA 2024 디지털정보격차 실태조사: https://www.nia.or.kr/site/nia_kor/ex/bbs/View.do?cbIdx=81623&bcIdx=27832&parentSeq=27832 ; https://www.etnews.com/20250327000412 ; https://theindigo.co.kr/archives/61549
- 보건복지부 2024년 등록장애인 현황 (2025-04-17): https://www.mohw.go.kr/board.es?mid=a10503010100&bid=0027&act=view&list_no=1485363
- WiseApp·Retail: https://www.wiseapp.co.kr/ ; https://www.wiseapp.co.kr/report/

Composition methods
- Kuhn, Wallace & Gallo 2004, *IEEE TSE* 30(6):418–421: https://dl.acm.org/doi/10.1109/TSE.2004.24 ; preprint: https://csrc.nist.gov/CSRC/media/Projects/automated-combinatorial-testing-for-software/documents/kuhn-wallace-gallo-tse-preprint.pdf
- Base choice (Ammann & Offutt, described in Grindal, Offutt & Andler): https://csrc.nist.gov/CSRC/media/Presentations/Combination-Testing-Strategies-A-Survery-July-20/images-media/grindal-offutt-andler.pdf ; http://cc.ee.ntu.edu.tw/~farn/courses/ST/slides/Ch4-ISP.pdf
- Apportionment methods: https://en.wikipedia.org/wiki/D%27Hondt_method ; https://www.sciencedirect.com/science/article/abs/pii/S0261379402000276 ; https://en.wikipedia.org/wiki/Huntington%E2%80%93Hill_method

---

## 2. Key knowledge

### 2.1 What a persona is for, and why personas are criticised

- **Persona types (Cooper).**
  - *About Face* names six persona types: primary, secondary, supplemental, customer, served and negative [snippet · industry].
  - Its axiom is "design each interface for a single, primary persona" [snippet · industry].
  - Customer personas buy the product but do not use it. Served personas are affected by the product but do not operate it. Negative personas are people the product is not designed for [snippet · industry].
  - Cooper's 1999 book *The Inmates Are Running the Asylum* is usually credited as the origin of the method. I did not search it [opinion].
- **Personas as a way to carry data (Pruitt & Grudin 2003).**
  - They extended Cooper's technique over three years of use at Microsoft. The smaller of their two projects was the first version of MSN Explorer [snippet · paper].
  - They argue that personas "provide a conduit for conveying a broad range of qualitative and quantitative data" and engage teams more than scenarios alone [snippet · paper].
  - I remember that they tied persona statements to per-persona source documents. I could not check this.
- **Weighting personas (Pruitt & Adlin 2006).** *The Persona Lifecycle* contains a "persona-weighted feature matrix" in its G4K case study. Each feature is scored per persona, and each persona carries a weight [snippet · industry]. I did not see how the weights are computed.
- **Critique 1: unknown representation, no falsifiability (Chapman & Milham 2006)** [snippet · paper]:
  - it is hard to tell how many users, if any, a persona represents;
  - personas cannot be verified or falsified;
  - they invite political conflict;
  - until these problems are solved, personas should not be treated as a way to communicate data.
- **Critique 2: combinations of attributes describe almost nobody (Chapman et al. 2008).**
  - The authors used six survey datasets (N = 268 to 10,307) and two simulated datasets. For each, they measured the prevalence of 10,000 random persona-like descriptions. Prevalence "decreases rapidly as attributes are added" [snippet · paper]. I did not see the exact curve.
  - Illustration: suppose attributes were independent and each matched half the users. Then a 4-attribute profile would match 6.25 % of users and an 8-attribute profile 0.39 % [derived].
- **Critique 3: how practitioners actually use personas.**
  - Practitioners used personas mainly to communicate within the team. They saw a risk that irrelevant persona attributes would mislead or distract decision makers (Matthews, Judge & Whittaker 2012) [snippet · paper].
  - In an ethnographic study of a design team, designers rarely mentioned personas during decision-making (Friess 2012) [snippet · paper]. I did not see the exact percentage.

**What this means for the skill.** A composed profile is a *test condition* whose attributes can be traced to sources. It is not a person, and it is not a share of users. Chapman's finding about attribute combinations also applies to the spec's "typical member", which combines the most common age band, top device, dominant grip, most common context and majority conditions. It is a base for variation, not a representative user [derived].

### 2.2 Data-driven, automatic and LLM-generated personas

- **McGinn & Kotamraju (CHI 2008, Sun Microsystems)** described a fast, low-cost method to create and validate personas by statistical analysis of survey data. It targets personas that are "not based on real customer data" or are based on samples too small to generalise from [snippet · paper]. I did not see the sample size.
- **Salminen, Guan, Jung & Jansen (IJHCI 2021)** reviewed 77 data-driven persona articles from 2005–2020. They describe periods starting with "Quantification" (2005–2008: clustering, principal component analysis, factor analysis), followed by "Diversification" [snippet · paper].
- **Salminen et al. (*Big Data* 2022)** built personas from 363 million video views, using several algorithms [snippet · paper]:
  - they scored each algorithm on fairness (over- or under-representation), diversity, and consistency across hyperparameters;
  - algorithms that ranked high on diversity ranked low on fairness (Spearman −0.83);
  - spectral embedding balanced the three criteria best;
  - in short, the choice of algorithm and settings changes *who is represented*.
- **Automatic Persona Generation (APG)** by the QCRI group builds personas from online analytics [snippet · industry]. I saw only the page title, not details.
- **LLM-generated personas (Li et al. 2025)** [snippet · paper]:
  - The more LLM-generated content a persona contains, the further simulation results drift from reality.
  - In a US presidential-election simulation, the simulated electorate moved left until every state voted Democratic.
  - LLM-generated personas also favoured environmentally conscious choices, liberal-arts education and artistic films.
  - Personas built from real metadata ("Meta Personas") came closest to real outcomes.

**What this means for the skill.**

- Inclusive floors must not depend on data-driven segment weights, because segmentation algorithms can drop small groups.
- No number in an audience file may come from an LLM without a quoted source. The skill already bans synthetic personas as audience sources.
- Synthetic narrative records such as Nemotron-Personas-Korea are fine as test data for form fields. They should not supply a persona's voice or opinions.

### 2.3 Inclusive design: persona spectrum, extremes, lead users

- **Persona spectrum (Microsoft).** It pairs the permanent, temporary and situational forms of one limitation. In the US [snippet · industry]:
  - permanent: about 26,000 people have lost an upper limb;
  - temporary: about 13 million have an arm injury;
  - situational: about 8 million are new parents holding a baby;
  - so a one-handed design serves about 21 million people.
- **Extremes and Mainstreams (IDEO.org).** Research people in the middle of the audience and people at its extremes, on several dimensions [snippet · industry]. IDEO claims that "an idea that suits an extreme user will nearly certainly work for the majority" [snippet · industry]. The claim itself is untested opinion.
- **Lead users (von Hippel 1986).** Lead users face a need months or years before most of the market does, and they gain a lot from solving it [snippet · paper].
  - At 3M, lead-user projects produced more novel ideas than parallel conventional projects. Their forecast sales in year 5 were eight times higher (Lilien et al. 2002) [snippet · paper].

**What this means for the skill.**

- The cause of a limitation (permanent, temporary or situational) changes *how many* people share it, not *what the models compute*. One one-handed profile exercises the same reach model whatever the cause [derived].
- The one-facet variations already supply the extremes.
- Lead-user research is an innovation method. It adds little to ergonomic QA beyond the existing `expert` familiarity value [opinion].

### 2.4 Context of use and key tasks

- **ISO 9241-11:2018.** Usability is defined for specified users, goals and context of use [snippet · standard]. The context of use comprises users, goals and tasks, resources, and the environment [snippet · standard].
  - The excerpt names the technical, physical and social environments.
  - I recall that the standard also names cultural and organisational environments. I could not verify this.
- **ISO 9241-210:2019.** Its first principle is that design is based on an explicit understanding of users, tasks and environments. This is already recorded, with its tags, in `docs/human-factors/ux-design-discipline.md` [derived].
- **ISO/IEC 25063:2014** (Common Industry Format for a context-of-use description) [snippet · standard]:
  - it specifies the content of high-level and detailed descriptions, for an intended, existing, implemented or deployed system;
  - the content covers users and other stakeholder groups, the characteristics of each user group, goals, tasks, and the environments of use.
- **Fit with the audience file.** An `ergo-audience.v1` file is in effect a 25063 description. It is missing *resources* and the *technical environment*: text size, dark mode, assistive technology, network [derived].
- **Jobs to be done and Outcome-Driven Innovation (Ulwick)** [snippet · industry]:
  - opportunity score = importance + max(importance − satisfaction, 0);
  - importance and satisfaction are each the share of high ratings, on a 0–10 scale;
  - a score of 15 or more is highly attractive, 10–15 is attractive, and below 10 means the outcome is already over-served.
- **Christensen's JTBD writing** was not searched. The spec's "When …, I want to …, so I can …" job-story format is a practitioner convention [opinion].

### 2.5 Segmentation practice and how many people per group

- **Nielsen (NN/g, 2000)** [snippet · industry]:
  - the five-user rule holds only for users who are comparable;
  - with two highly distinct groups, test 3–4 users per group;
  - with three or more groups, test 3 per group, because problems overlap across groups.
- **That rule is about variation between people.** The swarm's measured and model checks are deterministic on a recorded run. A second profile with the same model inputs adds nothing. Variation exists only in the LLM judgment layer, which the protocol already treats as one correlated rater per model (`persona-agent-protocol.md` §5) [derived].
- **Segment by behaviour and context, not demographics alone.** Demographics are a poor proxy for what the models read: grip, vision and context [opinion]. This matches Cooper's practice of segmenting by behaviour, which I did not verify here.

### 2.6 Audience evidence sources and how to mine them

- **App-store reviews.**
  - Khalid et al. (2015) coded 6,390 low-rated reviews of 20 free iOS apps into 12 complaint types [snippet · paper]:
    - the most frequent were functional errors, feature requests and crashes;
    - privacy and ethical issues, and hidden costs, hurt ratings the most;
    - 11 % of the reviews blamed a recent update.
  - Maalej & Nabil (RE 2015) classified reviews into four types: bug reports, feature requests, user experiences and ratings [snippet · paper]. They used Naive Bayes and decision trees over keywords, bag of words, sentiment, star rating and length. I did not see the accuracy.
  - Guzman & Maalej (RE 2014) extracted opinions about individual features from reviews of 7 apps. Against a manual analysis by peers, they reached precision 0.59 and recall 0.51 [snippet · paper].
- **Disabled users are largely silent in reviews.**
  - Eler et al. (2019) found that users generally do not mention accessibility in Google Play reviews [snippet · paper].
  - AlOmar et al. (CHI 2021) titled their detector "Finding the needle in a haystack" [snippet · paper].
  - A 2025 study asks "Why are accessibility app reviews rare?" [snippet · paper, title only].
  - So a lack of accessibility complaints does not show a lack of affected users.
- **Telemetry of device settings (Appt).** Q42's open-source library collects these figures from about 5 million users of Dutch apps [snippet · industry]:
  - about half of iOS users, and almost three quarters of Android users, have at least one accessibility setting on;
  - more than a third change the font size (one source says 26 % use a larger text size);
  - more than a third of iOS users use dark mode.
  - A product's own analytics can measure these shares directly. In ISO terms they belong to the technical environment.
- **Competitor and panel data.** WiseApp·Retail describes its figures as statistical estimates from a panel sample of Korean smartphone users [snippet · industry]. I found neither the panel size nor the iOS/Android split. I did not retrieve Mobile Index's methodology.

### 2.7 Korean public data for composing audiences

| Source (publisher, date) | Latest figures found | Use in `ergo-audience.v1` | Caveat | Tag |
| --- | --- | --- | --- | --- |
| 주민등록 인구통계, 행정안전부 (press release 2024-12-24; monthly data at jumin.mois.go.kr; mirrored on KOSIS) | 51,221,286 residents on 2024-12-23. Aged 65+: 10,244,550 (20.00 %). Share aged 65+ is 17.83 % among men (4,546,287) and 22.15 % among women (5,698,263). | Population bounds for `age_bands` and `sex_mix`. Replace the placeholder `AGE_BAND_SHARE_KR` in `ergoqa/params.py` with dated values. | Describes the population, not the product's users. | [snippet · report] |
| 2024 방송매체 이용행태조사, 방송통신위원회 (released 2024-12-30; now hosted by 방송미디어통신위원회) | 8,316 people aged 13+ in 5,645 households, interviewed face to face. Smartphone ownership 95.3 % (2023: 94.8 %). Among 70+: 73.0 % (+6.5 pp); 64.4 % use a smartphone at least 5 days a week. | Upper bound on smartphone access for segments aged 70+. Record `mode: probability_face_to_face`. | Owning a smartphone is not using this product. | [snippet · report] |
| 한국갤럽 스마트폰 사용률·브랜드 (July 2025) | Adults' smartphone use 99 %; 70+: 91 %. Main brand: Samsung 72 %, Apple 24 %, other 2 %. By age: 18–29 Apple 60 %, Samsung 40 %; 30s Samsung 50 %, Apple 47 %; 40s Samsung 67 %; 60+ Samsung 92 %. | `devices` for segments defined by age. For example, 60+ gets Galaxy models; 20s get iPhone first. | Phone survey. Brand is not model or screen size. A July 2026 headline reports Samsung 81 % and Apple 19 %; the base is unclear and it is unverified. | [snippet · report] |
| 2024 디지털정보격차 실태조사, 과기정통부 and NIA (published 2025-03-27) | Digital level of the four vulnerable groups: 77.5 % of the general public (2023: 76.9 %). By group: older adults 71.4 %, farmers and fishers 80.0 %, disabled people 83.5 %, low-income 96.5 %. By component: access 96.5 %, competence 65.6 %, use 80.0 %. | The new `digital_competence` field for older and edge segments. It steers task choice (onboarding, error recovery) and interactive first-use runs. | A relative index (general public = 100). The age cut-off for "older adults" (55+ per repository notes) is not re-verified. | [snippet · report] |
| 2024년 등록장애인 현황, 보건복지부 (2025-04-17) | 2,631,356 registered disabled people (5.1 % of the population). By type: physical 43.0 %, hearing 16.8 %, visual 9.4 %, brain lesion 8.9 %, intellectual 8.9 %. Aged 65+: 55.3 % (1,455,782), up from 42.3 % in 2015. 60s 23.6 %, 70s 22.0 %, 80s 17.5 %. | Edge segments (visual → low vision; physical or brain lesion → motor). Hearing and intellectual disability become declared-but-not-simulated conditions and `exclusions[].test_instead`. | Registration is not the same as functional limitation. Under-registration is likely. | [snippet · report] |
| 2023 장애인실태조사, 보건복지부 / KIHASA (every three years) | Not retrieved | Functional limitations and assistive-technology use | — | — |
| WiseApp·Retail; Mobile Index (IGAWorks) | WiseApp publishes panel-based estimates of app users. Methodology not found. | `competitor` or `market_report` sources for the age and sex mix of comparable apps, with `basis: estimated`. | Panel make-up unknown. Only press-release detail is public. | [snippet · industry] |

**Cross-check.** For the 70+ age band, two sources give very different figures [derived]:

- KCC: 73.0 % *own* a smartphone (2024; face-to-face household sample of people aged 13+).
- Gallup: 91 % *use* one (2025; phone survey of adults).

A gap of 18 points comes from population, survey mode and definition. A share must therefore record all three.

### 2.8 Composition methods

- **Stratified and quota sampling.**
  - Stratified sampling allocates people by stratum size (or size × variability) to *estimate* population quantities.
  - Quota sampling fills fixed quotas without random selection.
  - The swarm's goal is different: to *detect* defects that affect a given condition [opinion].
- **Base choice (Ammann & Offutt)** [snippet · paper/textbook]:
  - build a base test from the most important value of every parameter (for example, the most common);
  - then vary one parameter at a time, so every value is used once with the base values of all other parameters;
  - the number of tests is 1 + Σ(kᵢ − 1), where kᵢ is the number of values of parameter i [derived];
  - with one base per segment ("multiple base choice"), this is exactly the spec's typical member plus one-facet variations.
- **t-way coverage (Kuhn, Wallace & Gallo 2004)** [snippet · paper]:
  - a single factor caused 9–67 % of failures, depending on the system;
  - testing all pairs plus all single values found 88 % of the correctness and convergence bugs in NASA's RAX software.
- **Size of a pairwise set.** It is at least the product of the two largest factor sizes [derived].
  - Grip (4 values) × vision state (4 values) needs at least 16 profiles per device.
  - Base choice over grip 4, vision 4, motor or mobility 3, hand size 3 and age 3 needs 1 + 3 + 3 + 2 + 2 + 2 = 13.
  - `software-testing-foundations.md` §2.4 computes 15–16 rows for full pair coverage over 8 touch factors.
- **Apportionment** (turning weights into whole numbers of profiles) [snippet · secondary]:
  - D'Hondt is known to favour larger parties;
  - Sainte-Laguë (odd divisors) is close to unbiased;
  - Huntington–Hill gives every state one seat before dividing.
- **Worked example** [derived]: weights 0.6, 0.3 and 0.1; one base profile each; 6 extra slots; ties go to the higher priority.
  - D'Hondt gives 5, 1 and 0 extra slots (totals 6/2/1).
  - Sainte-Laguë and Huntington–Hill both give 4, 2 and 0 (totals 5/3/1).
  - Exact proportions would be 5.4/2.7/0.9.
  - At swarm budgets the divisor moves at most one profile.
- **Priority weighting versus minimum coverage for small groups.**
  - Weighting (Cooper's primary persona; Pruitt & Adlin's weighted matrix) spends effort where most users are.
  - Minimum coverage (the persona spectrum; extreme users) guarantees small groups with high stakes a slot.
  - Data-driven weights under-represent small groups (§2.2), and reviews under-report disability (§2.6). The minimum must therefore be set independently of the weights [derived from the cited items].

### 2.9 What this repository's own runs say about composition

| # | Observation | Value | Source |
| --- | --- | --- | --- |
| R1 | Stratified, 14 profiles per touch device, versus a single default persona and measured-only checks (dev suites, 53 defects) | Strict recall 0.906 / 0.623 / 0.302. Clean-control findings 213 / 133 / 31. | `ablation-dev-8707b70.json`, `configs` |
| R2 | Discovery curve | Stratified: 0.868 at 8 per device, 0.906 at 14. Random: 0.789 at 8, 0.833 at 14; it reaches 0.908 only at 40. | `discovery_curve` |
| R3 | Defects that needed two conditions in one profile | None (`pool_defects_needing_combined_profiles: []`) | same file |
| R4 | Unique defects lost when one condition is removed from the swarm | Left one-hand grip 5, right one-hand grip 5, deutan 4, walking 2, age 50s 2, presbyopia at 60s 1, age 70s+ 1, age 20s 1, small hand 1 | `swarm_condition_leave_one_out` |
| R5 | Conditions whose removal changed neither recall nor the number of findings | Protan, tritan, mild tremor, moderate tremor, transit, dark, first use, large hand | same |
| R6 | Effect of removing bright sun | Recall unchanged. Findings 518 → 487. Clean-control findings 213 → 196 (−8.0 %). | same |
| R7 | Frozen held-out swarm (`8c1de02`), 225 findings | 114 were triggered by every profile on their device. The other 111 were triggered by only some of the device's profiles. Of those, 89 were reported as "k/k", because before `782a15c` the tested set held only the profiles that emitted an observation (PC-04 50, RH-01 17, PC-05 16, PC-03 5, PT-02 1). The remaining 22 were reported with a real denominator (RH-01 12, PT-04 9, GM-03 1). | `.ergo-bench/heldout-frozen/findings-swarm.json`, `profiles.json` |
| R8 | Findings that name a differential condition | 5 of 225: 4 for the left one-hand grip and 1 for the right. Scoped findings read, for example, "1/1 simulated profiles", with no condition named. | same |
| R9 | Volume by check | PC-04: 82 findings (36 %). PC-05: 16 (7 %). All P3. | same |
| R10 | Profile inventory | 49 profiles: 14 on each of 3 touch devices and 7 on the laptop. 13 of them (27 %) use R5 conditions: tremor (4), protan (3), first use (3), presbyopic 70s+ with a large hand (3). | `profiles.json` |
| R11 | Profile attributes the checks read | Checks read grip, handedness, thumb length and hand percentile, age band, vision (acuity, presbyopia, CVD and its severity, viewing distance), tremor, mobility, lighting, time pressure, reading rate, reaction time, device and orientation. No check reads familiarity, interruptions or free hands. Among lighting values, only `bright_sun` is read. `first_use` changes only the profile label. | `ergoqa/checks.py`, `ergoqa/profiles.py`; matches `software-testing-foundations.md` §2.4 |
| R12 | Denominator fix | Commit `782a15c` computes the tested profiles with `checks.applicable()`. That repairs coverage labels for checks that apply to everyone. `applicable()` limits PC-03 to profiles with a colour-vision deficiency and PC-05 to bright-sun profiles. So those findings still show "k/k" with an empty condition, because `_differential` returns `{}` when no tested profile stayed silent. | `ergoqa/swarm.py`, `ergoqa/checks.py` |
| R13 | Contamination | heldout-mixed is one of the three dev ablation suites (53 = 17 + 16 + 20 defects). It can no longer decide composition questions; heldout-2 must. | ablation JSON, `suites` |

All rows are [derived].

**How to read R7–R12.**

- About half of the swarm's output depends on composition.
- The noise that composition can remove is mostly environment strata without evidence (PC-05).
- The large-volume noise (PC-04, all P3) is a threshold question for the check briefs, not a composition question.

---

## 3. Implications for the skill

**Metrics used in the table**

- `R_s`: strict recall.
- `CC`: clean-control findings.
- `N`: number of findings.
- `PCov` (plan coverage): the share of seeded defects whose `profile_condition` is satisfied by at least one planned profile. The harness computes it after planning, blind.
- `R_rel`: recall within each `audience_relevance` stratum of the heldout-2 keys.
- `ATTR`: the share of persona-dependent findings that name a condition which holds for every triggered profile on the device and for none of the others.
- `STAB`: the mean pairwise Jaccard similarity of the planned model-input vectors across independent Stage-0 runs on the same brief.
- `UNSUP`: the count of numbers in an audience file with no supporting quote.

Recall comparisons use the exact McNemar test on the defects where the two variants disagree, as the ablation harness already does. "Frozen runs" means re-analysing existing recordings; no new recording is needed.

### 3.1 Candidates

| ID | Type | What exactly | Evidence | Expected effect on recall / noise / usefulness | Experiment that decides it (hypothesis, metric, pass rule, data) | Effort |
| --- | --- | --- | --- | --- | --- | --- |
| AP-01 | KEEP (rename) | Keep audience-first composition: one base profile per segment plus one-facet variations (spec §13, steps 1 and 4). Rename "typical member" to "base profile". Its reasons text should say "a base for variation, not an average user". Use the stratified generator only when no audience file exists. | Base choice: most common value as the base, one parameter varied at a time [snippet · paper]. Combinations of attributes describe few people (Chapman et al. 2008) [snippet · paper]. Dev (R2, R3): stratified 0.906 at 14 per device versus random 0.908 at 40; no defect needed combined conditions [derived]. | Recall: no change expected, since the structure is the same. Usefulness: fewer readers mistake a profile for a share of users. | No experiment needed to keep it. Guard: on heldout-2, PCov of the audience plan (14 per device) ≥ PCov of the stratified default at the same budget. If not, find which defect conditions the audience file missed. Data: blind audience files written from the heldout-2 briefs. | S |
| AP-02 | KEEP (state the rule) | Set inclusive floors independently of segment weights: a left-hand mirror per input kind, deutan, presbyopia, and walking on touch devices. Reserve at most ⌊remaining/3⌋ slots. Label floor profiles. Rule for adding a floor: removing the condition lost unique defects in ≥ 2 dev suites, or it is a legally protected group that `ergoqa` has a model for. | Swarm leave-one-out losses (R4): left one-hand 5, deutan 4, walking 2 [derived]. Walking and deutan each add 0–1 clean-control findings [derived]. Data-driven segmentation trades diversity against fairness (ρ = −0.83) [snippet · paper]. Reviews rarely mention accessibility [snippet · paper]. Situational one-handedness (8 M) dwarfs permanent (26 k) [snippet · industry]. | Protects recall on edge defects. Removing one floor cost 0.02–0.09 of strict recall on dev. Noise ≈ 0. | Hypothesis: removing floors from audience-composed swarms loses ≥ 1 heldout-2 defect whose `audience_relevance` is edge or secondary. Metrics: R_s, R_rel, CC with floors on and off. Keep floors if R_rel(edge) with floors ≥ without, and CC rises ≤ 5 %. Data: heldout-2 and the blind audience files. | S |
| AP-03 | CUT (require evidence) | Drop `bright_sun` (PC-05) and `dark` from the default strata. Add a lighting facet only when the audience file has a context with that lighting at share ≥ 0.15, or an outdoor task with high stakes. Environment conditions without evidence go to `untested` with the reason "no audience evidence". | Dev (R6): removing bright sun lost 0 defects; findings 518 → 487; CC 213 → 196 (−8.0 %) [derived]. Held-out (R9): PC-05 gave 16 of 225 findings, all P3 [derived]. PC-05 is now tagged "hypothesis" in the check reference [derived]. ISO 9241-11 treats the environment as part of the context to specify, not to assume [snippet · standard]. | Noise: 6–8 % fewer findings, with no measured recall loss. Risk for outdoor products; the evidence rule covers it. | Hypothesis: requiring evidence for lighting cuts CC by ≥ 5 % and loses no defect. Metrics: CC, N, R_s on frozen dev runs and on heldout-2. Pass: 0 defects lost on dev, and ≤ 1 lost on heldout-2 with `audience_relevance: none`. Data: frozen runs; no re-recording. | S |
| AP-04 | CUT (prune) | In the deterministic plan, skip facets that change no model input: `first_use`, `expert`, `interruptions`, `free_hands` alone, and `lighting: dark`. Also skip facets that their base dominates (§3.3, step 3), such as a younger age band. Merge profiles whose model inputs duplicate an existing profile, keeping both segment references. Drop protan, tritan, `large_hand` and `transit` from the default strata. Keep `tremor` only when the audience file gives evidence for it, and skip it when a profile on the same base already has an equal or larger effective σ multiplier, because tremor then adds nothing. Rank interactive persona-agent runs separately, with their own `--agent-budget`; there, `first_use`, `expert` and `digital_competence` come first. | Checks read no familiarity, interruptions or free hands (R11) [derived]. Removing any one of protan, tritan, mild or moderate tremor, transit, dark, first use or large hand changed neither recall nor the finding count (R5) [derived]. 13 of 49 held-out profiles (27 %) are of these kinds (R10) [derived]. `software-testing-foundations.md` reaches the same list [derived]. | Recall and noise unchanged, if removing them together behaves like removing them one by one. Frees up to 27 % of slots for facets backed by audience evidence. Shorter plan and report. | Hypothesis: at equal budget, the pruned plan keeps R_s and adds ≥ 1 distinct model-relevant facet per device. Metrics: R_s, CC, number of distinct model-input vectors. Pass: 0 defects lost (dev and heldout-2) and McNemar p ≥ 0.05. Data: frozen runs. | S |
| AP-05 | CHANGE | Name the condition for checks limited to a subset of profiles. Compute the differential condition over all profiles evaluated on the device, counting profiles outside `checks.applicable()` as not triggered. Add `condition_scope`: `context.lighting = bright_sun` for PC-05, `vision.cvd ≠ none` for PC-03, one-hand or two-thumb phone grips for RH-01. Coverage label: "1 of 14 profiles on galaxy-s24 (scope: bright sun)". Add `vision.acuity` and `cognition.time_pressure` to `DIFFERENTIAL_ATTRIBUTES`. | In the frozen run (R7, R8), 111 findings depended on composition, but 5 named a condition [derived]. Commit `782a15c` fixed the denominators, but by construction PC-03 and PC-05 stay "k/k" with an empty condition (R12) [derived]. Personas are useful to communicate who is affected (Matthews et al.; Friess) [snippet · paper]. | Usefulness: ATTR was about 5 % in the frozen run. `782a15c` should fix most of that. AP-05 closes the rest by construction: PC-03 and PC-05 account for 21 of the 111 findings (19 %). Target: ATTR ≥ 80 % overall. Recall and noise unchanged. | Hypothesis: after the change ATTR ≥ 0.8, with the same matched defects. Metrics: ATTR and the set of matched defects. Pass: ATTR ≥ 0.8 and no change in matches. Data: re-aggregated frozen held-out and dev runs. | S |
| AP-06 | ADD | Add `segments_at_risk` to every finding that depends on composition. Take the finding's minimal failure-causing schema (MFS) from the sweep proposed in `software-testing-foundations.md` §2.4. If no MFS is available, use the smallest rule that holds exactly over the device's profiles: one attribute with a threshold, or an OR of two conditions. List every audience segment whose distributions contain those values, with its priority and stakes. Never list shares. Keep `segments_affected` for the composed profiles. | 22 findings were triggered by only some of the profiles tested (RH-01 12, PT-04 9, GM-03 1); 5 had an AND-of-attributes differential condition (R7, R8) [derived]. Failures are usually triggered by 1–2 factors (Kuhn et al. 2004) [snippet · paper]. Chapman & Milham: say whom a persona represents [snippet · paper]. | Usefulness: findings map to audience groups beyond the composed profiles. No change to recall or noise. | Hypothesis: ≥ 80 % of composition-dependent findings get an exact rule with ≤ 2 conditions. Metrics: share of findings with a rule, and rule exactness. Pass: ≥ 0.8 with no exceptions over the device's profiles. Data: frozen runs and one blind audience file per heldout-2 product. | M |
| AP-07 | ADD | Record source quality and uncertainty in the audience file. New fields: `sources[].{publisher, population, n, mode, period, geography, tag}`, `share.{low, high, of}`, and `evidence[].quote`. The quote is required for statistic and official evidence and must contain the number. Confidence rule: high means product analytics or a survey of the product's users with n ≥ 100; medium means official statistics that bound the segment, or a named comparable product; low means inference or judgment. The validator rejects numbers without a quote, and rejects `basis: measured` from `expert_judgment`. | For 70+, KCC gives 73.0 % ownership (face to face, n = 8,316) and Gallup 91 % use (phone): an 18-point gap from mode and definition [snippet · report][derived]. LLM-generated persona content biases simulations [snippet · paper]. How many users a persona represents is otherwise unknowable [snippet · paper]. Panel figures such as WiseApp's are estimates [snippet · industry]. | Trust and auditability improve. Invented numbers are blocked. No change to recall. | Hypothesis: two independent Stage-0 agents per heldout-2 brief produce UNSUP > 0 without the validator and 0 with it. Metrics: UNSUP and validator rejections. Pass: UNSUP = 0 with the validator, and a human spot-check finds ≥ 19 of 20 quotes faithful. Data: heldout-2 briefs and public sources. | S |
| AP-08 | ADD | Ship a dated Korean audience prior (`references/audience-prior-kr.json`) covering: age × sex (행정안전부); smartphone ownership by age (방송매체 이용행태조사); brand by age (한국갤럽); digital competence of vulnerable groups (NIA); registered disability by type (보건복지부). Each value carries source, mode, date and tag, and is checked in the primary source first. Stage 0 starts from the prior and overrides it with product evidence. Replace the `AGE_BAND_SHARE_KR` placeholders. | Values in §2.7 [snippet · report]. `korean-population-context.md` §5, §6 and §10 list them as NOT RETRIEVED [derived]. Data-driven segments are unstable from run to run [snippet · paper]. | Stage 0 becomes more consistent: the same age mix gives the same devices. Fewer invented numbers. The recall effect is indirect, through device choice. | Hypothesis: with the prior, independent Stage-0 runs on the same brief agree more. Metrics: STAB over 3 runs per brief; PCov. Pass: STAB ≥ 0.8 with the prior and ≥ 0.15 higher than without; PCov not worse. Data: heldout-2 briefs and the verified prior. | M |
| AP-09 | ADD | Add technical-environment facets, following the ISO context of use: `contexts[].technical.{text_scale, dark_mode}`, with shares. The facet applies when a share is ≥ 0.15; text scale 1.3 is also a floor for segments aged 60+. For each facet, record and analyse an extra run: the web driver emulates `prefers-color-scheme: dark` or 130 %/200 % text scale (Android uses its font scale). Re-run the measured checks (PC-01/02/03 and the layout checks). | ISO 9241-11: the context includes resources and the technical environment [snippet · standard]. Appt: about half of iOS and three quarters of Android users have ≥ 1 accessibility setting on; > 1/3 change font size (26 % larger text in one source); > 1/3 of iOS users use dark mode [snippet · industry]. heldout-2 adds a `layout` category, which includes content lost at 200 % zoom (spec §12.1) [derived]. | Possible new recall on dark-theme contrast and text-scaling defects, which no current profile can reach. Moderate noise risk from new measured findings. | Hypothesis: the dark-mode and text-scale facets find ≥ 1 seeded defect that no other profile finds. Metrics: unique defects, CC. Pass: ≥ 1 unique defect and CC rises ≤ 10 %. Data: heldout-2, plus fixtures that support dark mode or text scaling (author them blind if none exist). | M |
| AP-10 | ADD | Add segment `role`: operator, customer or served; only operators get profiles. Add conditions that are declared but not simulated (`hearing_loss`, `deaf`, `screen_reader`, `switch_access`, `cognitive`). They always go to `untested` with a population reference. Add `exclusions[].test_instead`. | Cooper's persona types include customer, served and negative personas [snippet · industry]. Korean registered disability (2024): hearing 16.8 %, intellectual 8.9 %, brain lesion 8.9 % [snippet · report]. The skill does not simulate assistive technology (`audience-research.md`) [derived]. | Usefulness: the report names the groups it did not test, with their size. No change to recall. No profiles for people who do not operate the product. | Checklist test: for each heldout-2 product, the plan's `untested` names every declared-but-not-simulated group and every exclusion. Pass: 100 %. | S |
| AP-11 | ADD | Add `conditions[].cause`: permanent, temporary or situational. Composition merges profiles by model effect, so the three causes of one limitation share one profile. The cause is used only in the explanation card and to justify floors. | Persona spectrum: 26 k / 13 M / 8 M people; a one-handed design serves about 21 M in the US [snippet · industry]. Models read the limitation, not its cause [derived]. | Explanations improve. Plan size unchanged. | No experiment; this is documentation. Unit test: adding causes does not change the plan. | S |
| AP-12 | CHANGE (partial cut) | Use Nemotron-Personas-Korea rows only as concrete test data (names, regions and ages for form fields). Never use them as an agent's voice, opinions or audience evidence. | The more LLM-generated content in a persona, the larger the systematic bias [snippet · paper]. Irrelevant persona attributes mislead [snippet · paper]. The protocol already forbids giving agents a demographic voice [derived]. | Lower bias risk. Realistic Korean form data. No change to recall. | Spot check: 20 interactive agent runs with and without narrative persona text. Count notes that cite persona traits instead of the screen. Pass: 0 such notes after the change. | S |
| AP-13 | ADD | Add task priority and pain-point mapping. Task fields: `tasks[].importance` and `satisfaction` (0–10 share of top-2 ratings), and the derived `opportunity = importance + max(importance − satisfaction, 0)`. Scenario order: tasks whose criticality is safety, health, money, legal or access first; then opportunity ≥ 10; then frequency. Pain-point fields: `pain_points[].complaint_type` (the Khalid et al. types) and `maps_to` (a check family, `dark_pattern_audit` or `out_of_scope`). | The ODI opportunity score and its thresholds [snippet · industry]. Khalid et al.: complaint types; privacy and hidden-cost complaints hurt ratings most [snippet · paper]. Review mining is imprecise: precision 0.59, recall 0.51 for feature opinions [snippet · paper]. | Usefulness improves: tests go where users hurt. Recall on defects that matter to the audience may improve, but fixed benchmark scenarios cannot measure it. | Hypothesis: a blind task ranking from the brief puts the defects that matter to the audience on the top tasks. Metric: share of `audience_relevance: primary` defects on the two top-ranked tasks. Pass: ≥ 0.7. Data: heldout-2 keys, scored after ranking. | S |
| AP-14 | CHANGE | Vary one thing per facet, presbyopia included. An age facet never switches presbyopia on or off; presbyopia is its own facet (and a floor). A context facet may change several attributes only if no check reads more than one of them. For example, walking feeds PT-03/04 and bright sun feeds PC-05. | Base choice varies one parameter at a time [snippet · paper]. The stratified strata set 2–4 attributes at once, so age and presbyopia cannot be separated (`software-testing-foundations.md`) [derived]. Checks read ≤ 4 attributes each, mostly different ones [derived]. | Findings are easier to attribute. No change to recall. | Unit test on composed plans: every facet differs from its base in exactly one model-relevant attribute, or in a group of attributes that no single check reads together. Pass: 100 %. | S |
| AP-15 | CHANGE (low priority) | Fix the tie-break rules (§3.3). Run a sensitivity check with Sainte-Laguë divisors and with facet thresholds × 0.5 and × 1.5. Keep D'Hondt unless a variant changes PCov. | D'Hondt favours large parties; Sainte-Laguë is close to unbiased; Huntington–Hill guarantees one seat [snippet · secondary]. The worked example in §2.8 moves one profile [derived]. The current thresholds (0.15/0.2/0.25/0.3) are team policy without a source [derived]. | Negligible effect on recall. More reproducible. | Hypothesis: the allocation variants do not change PCov. Keep D'Hondt if PCov changes by less than 1 defect on heldout-2. Data: the heldout-2 audience files. | S |
| AP-16 | ADD (conditional) | When segments come from clustering analytics or survey data, record `method.segmentation` and a stability index: the adjusted Rand index across 3 seeds and k ± 1. If it is below 0.7, merge the unstable segments or set confidence to low. | The choice of algorithm and settings changes who is represented and how consistently (Salminen et al. 2022) [snippet · paper]. Statistical persona creation (McGinn & Kotamraju 2008) [snippet · paper]. | More robust for teams with rich data. No benchmark effect. | Synthetic test on a public dataset. Pass: the index is computed and reported. Real validation needs a product team's analytics. | M |
| AP-17 | ADD (conditional) | Use pairwise coverage only for expensive runs (device and orientation recordings, interactive agents), only for the primary segment, and only if heldout-2 shows defects that need two conditions together. | A single factor caused 9–67 % of failures; pairs plus single values found 88 % of RAX bugs [snippet · paper]. No dev defect needed combined conditions (R3) [derived]. `software-testing-foundations.md` §2.4 reaches the same conclusion [derived]. | Recall improves only if such defects exist. Costs 20–50 % more profiles and adds noise. | Hypothesis: ≥ 2 heldout-2 defects need a two-condition profile. Metric: `pool_defects_needing_combined_profiles`. Adopt if ≥ 2. Data: heldout-2 with a pairwise pool. | M |
| AP-18 | ADD | Give every planned profile a structured explanation card (fields in §3.3, step 7). It lists the base values with sources, the one facet varied with its share and confidence, the floor flag, the checks the profile can change, and the line "a test condition, not a share of users". | Personas carry data only if their statements trace back to data (Pruitt & Grudin 2003) [snippet · paper]. Chapman & Milham: personas cannot be falsified [snippet · paper]. Designers rarely cite personas when deciding (Friess 2012) [snippet · paper]. | Usefulness improves and review takes less time. | Hypothesis: a blind reviewer who sees only the plan can predict which profiles will trigger 20 sampled model findings. Metric: prediction accuracy with and without the cards. Pass: ≥ 20 points better with the cards. Data: frozen runs. | S |

### 3.2 Deliverable (a): proposed `ergo-audience.v1` field list

Key to the Req. column: R = required, O = optional, C = conditionally required.

- Every new field is optional, so existing v1 files stay valid.
- The validator enforces the "C" rules only when the related field is present.
- Fields marked "kept" already exist in spec §13.

| Field | Req. | Status | Values and meaning | Why (evidence) |
| --- | --- | --- | --- | --- |
| `schema_version`, `audience_id`, `researched_at` | R | kept | `"ergo-audience.v1"`; id; date | Provenance |
| `product.{name, category, surface, locale}`; `product.brief_ref` | R; O | kept | Surface is one of web, android, ios, desktop, game | ISO/IEC 25063 describes the context of a named system [snippet · standard] |
| `researcher` | O | new | `{kind: human or agent, model, time_box_min}` | LLM-written content biases persona work [snippet · paper] |
| `method.summary`, `method.limitations[]` | R | kept | At least one limitation | Chapman & Milham [snippet · paper] |
| `method.segmentation` | O | new | `judgment`, `quota_from_statistics`, `survey_factor_analysis`, `clustering` or `analytics_nmf` | McGinn & Kotamraju; Salminen et al. 2021 [snippet · paper] |
| `method.stability` | C | new | `{index: "ARI", value, runs}`. Required when `segmentation` is statistical. | Salminen et al. 2022 [snippet · paper] |
| `sources[].{source_id, type, title, accessed_at}` | R | kept | `type` uses the existing enum | — |
| `sources[].url` | C | kept | Required unless the source is internal (analytics, interviews, support tickets) | — |
| `sources[].tag` | R | new | `standard`, `paper`, `industry`, `report`, `snippet`, `derived` or `opinion` | Same tags as the research briefs |
| `sources[].{publisher, population, n, mode, period, geography}` | O (`mode` is R for statistics) | new | `mode` is one of: `census_admin`, `probability_face_to_face`, `probability_phone`, `online_panel`, `device_telemetry`, `product_analytics`, `review_corpus`, `community`, `interview`, `brief`, `expert` | The 18-point KCC–Gallup gap for 70+ [derived] |
| `segments[].{segment_id, name_ko, summary}` | R | kept | Name segments by behaviour and context | [opinion] |
| `segments[].role` | O | new | `operator` (default), `customer` or `served`. Only operators get profiles. | Cooper's persona types [snippet · industry] |
| `segments[].priority` | R | kept | `primary`, `secondary` or `edge` | Primary persona; extreme users [snippet · industry] |
| `segments[].share.{value, basis, source_ids}` | R | kept | `value` is null exactly when `basis` is `unknown` | — |
| `segments[].share.{low, high, of}` | O | new | An interval, plus the population it is a share of (for example "product MAU", "category users", "KR residents 13+") | Chapman & Milham; KCC–Gallup gap |
| `segments[].confidence` | R | kept (rule added) | High, medium or low, by the AP-07 rule | — |
| `segments[].evidence[].{source_id, claim, kind}` | R (≥ 1) | kept | `firsthand`, `statistic`, `official` or `inference` | Personas carry data (Pruitt & Grudin) [snippet · paper] |
| `segments[].evidence[].quote` | C | new | Required for `statistic` and `official`; must contain the number | AP-07 |
| `segments[].age_bands` | R | kept | Share per profile age band | 행정안전부 age data [snippet · report] |
| `segments[].sex_mix` | O | new | `{female, male}`. Used only to place CVD and hand-size facets where they are plausible. | CVD in Korea: men 5.9 %, women 0.44 % (`params.py`) [derived]; 65+ share: women 22.15 %, men 17.83 % [snippet · report] |
| `segments[].devices` (+ `device_source_ids`) | R (+ O) | kept (+ new) | Catalog ids with shares | Gallup brand by age [snippet · report] |
| `segments[].{orientation, grips, left_hand_share}` | O | kept | Defaults come from `params.py`. Floors ignore `left_hand_share`, so Stage 0 need not research it. | — |
| `segments[].familiarity` | O | kept (use changed) | Chooses interactive agent runs, not deterministic profiles (AP-04) | R11 [derived] |
| `segments[].digital_competence` | O | new | Shares of `{low, medium, high}`. Steers task choice (onboarding, error recovery) and interactive first-use runs. | NIA: competence 65.6 % versus access 96.5 % of the general public [snippet · report] |
| `segments[].conditions[].{condition, share, stakes, source_ids, why}` | R when a condition is present | kept | The enum gains declared-but-not-simulated values (AP-10) | — |
| `segments[].conditions[].cause` | O | new | `permanent`, `temporary` or `situational` | Persona spectrum [snippet · industry] |
| `segments[].contexts[].{context_id, mobility, lighting, one_handed, interruptions, time_pressure, share, source_ids}` | O | kept | Evidence is required before a lighting facet is used (AP-03) | ISO 9241-11 environment [snippet · standard] |
| `segments[].contexts[].technical` | O | new | `{text_scale: 1.0, 1.3 or 2.0; dark_mode: bool; network: fast, slow or offline; assistive: none, screen_reader, switch or magnifier}` | ISO 9241-11 resources and technical environment; Appt settings shares [snippet] |
| `segments[].contexts[].viewing_distance_mm` | O | new | Overrides the device default, with a source (for example, a tablet on a desk versus held in the hand) | PC-04 volume on tablets (R9) [derived] |
| `segments[].tasks[].{task_id, goal_ko, jtbd, frequency, criticality, concrete_data, success_ko, source_ids}` | R (≥ 1 per operator segment) | kept | `concrete_data` is mandatory | ISO 9241-11 goals and tasks [snippet · standard] |
| `segments[].tasks[].{importance, satisfaction, outcome_statements, success_criteria}` | O | new | `importance` and `satisfaction` on 0–10. `success_criteria` is `{max_steps, max_time_s, must_see}`, used for the agent's stop rule and for judging effectiveness. | ODI [snippet · industry]; ISO effectiveness and efficiency [snippet · standard] |
| `segments[].pain_points[].{text, source_ids, kind}` | O | kept | — | — |
| `segments[].pain_points[].{complaint_type, maps_to}` | O | new | Khalid et al. complaint type. `maps_to` is a check family, `dark_pattern_audit` or `out_of_scope`. | [snippet · paper] |
| `exclusions[].{group, why}` | O | kept | Cooper's negative persona, or a group outside the models | [snippet · industry] |
| `exclusions[].test_instead` | O | new | For example, "screen-reader walkthrough with 2 blind users" | — |
| `floors` | O | kept | Overrides the default floors; `[]` disables them | AP-02 |

**Personal data.** An audience file holds aggregate public statistics and aggregated product analytics only. It never holds personal records, and never holds disability data about identifiable people [opinion].

### 3.3 Deliverable (b): composition algorithm (`compose` v1.1)

**Inputs**

- An audience file `A`.
- A budget `B`: the number of deterministic profiles. It bounds analysis and review load; analysing more profiles costs only CPU (R11 and the software-testing brief).
- A separate `B_agent` for interactive persona-agent runs.
- Floors `F`. Default: `left_hand`, `cvd_deutan`, `presbyopia`, `walking`.
- The device catalog.
- The exercise map `E`, below.

**Exercise map `E`: which checks read which profile attribute.**

| Profile attribute | Checks that read it |
| --- | --- |
| `grip`, `handedness` | RH-01, RH-02, GM-02, PT-02, PT-03/04 (σ), GZ-02 (occlusion) |
| `thumb_length_mm`, `hand_percentile` | RH-01, RH-02 |
| `device_id`, `orientation` | All geometry-based checks |
| `age_band` | PT-03/04 (σ × 1.15 at 60s, × 1.3 at 70s+), CG-02 (reading rate per decade: 587/560/500/410/380 syllables per minute for 30s/40s/50s/60s/70s+), GM-03 (choice reaction time per decade: 440–580 ms), GZ-02 (bands × 0.7 at 70+), PC-04 (60s+ threshold) |
| `vision.presbyopia`, `vision.acuity`, viewing distance | PC-04, GM-01, GZ-02 (low vision) |
| `vision.cvd`, `cvd_severity` | PC-03 |
| `motor.tremor`, `context.mobility` | PT-03, PT-04 (σ) |
| `context.lighting = bright_sun` | PC-05 |
| `cognition.time_pressure = high` | GZ-02 |
| `reaction_time_ms` | GM-03 |
| `cognition.familiarity`, `context.interruptions`, `context.free_hands`, `lighting = dark` | None (label only, or unused) |

Sources: `ergoqa/checks.py`, `ergoqa/profiles.py` and `human-factors-checks.md`; it matches `software-testing-foundations.md` §2.4 [derived]. Keep the map as data next to `checks.applicable()` so that it cannot drift from the code.

**Definitions**

- `S`: the operator segments.
- Segment weight `w_s`: `share.value`, normalised over `S`. When the basis is unknown, use the priority default (0.5 / 0.3 / 0.2) scaled into the share not yet claimed (unchanged from the spec).
- `m(p)`: the model-input vector of profile `p`, meaning the values of every attribute in `E` that some check reads.
- Two profiles are *model-equivalent* when their `m(p)` are equal.
- A *facet* changes one model-relevant attribute of a base. It may instead change a group of context attributes, but only if no single check reads two of them (AP-14).

**Steps**

1. **Base profiles (multiple base choice).** For each segment `s`, build base `b_s`:
   - the most common age band, top device, dominant grip (right hand) and most common context;
   - every condition with share ≥ 0.5;
   - presbyopia when the age band is ≥ 50s, unless the segment states otherwise.

   Resolve ties in this order (T1): higher share; then the value that more checks read in `E` (older band, one-hand grip, walking); then catalog or alphabetical order. Merge model-equivalent bases into one profile with several `segment_refs`. If `B < |S|`, take segments in this order (T2): priority rank, then `w_s`, then whether the segment has a high-stakes condition, then `segment_id`.

   *Rationale:* base choice [snippet · paper] with one base per segment (Cooper's primary persona per interface [snippet · industry]). Merging follows from determinism: a duplicate model vector adds no information (§2.5) [derived].
2. **Reserve slots for floors.** The requirements are:
   - `(left_hand, k)` for each input kind `k` present;
   - `(walking, touch)` if any device is touch;
   - each other floor in `F` once.

   Let `Q'` be the requirements not met after step 1. Reserve `r = min(|Q'|, ⌊(B − |bases|)/3⌋)` slots. This is unchanged from the spec. *Evidence:* R4 [derived] and §2.2 and §2.6 [snippet · paper].
3. **Candidate facets per segment**, in this order:
   1. minority conditions with high stakes;
   2. the left-hand mirror;
   3. other devices with share ≥ 0.30;
   4. contexts with share ≥ 0.15, including `technical` text-scale and dark-mode facets (AP-09);
   5. other conditions with share ≥ 0.05;
   6. other age bands with share ≥ 0.20, never switching presbyopia;
   7. other grips with share ≥ 0.25.

   Then filter:
   - Drop a facet `c` if `m(c) = m(b_s)`. This removes facets that change no model input. Route them to the agent ranking.
   - If `m(c)` equals an already planned profile, merge: add `s` to that profile's `segment_refs`.
   - Drop a facet whose base dominates it. That is the case when every input the facet changes is equal or less demanding on every check that reads it. Example: a younger age band, since it reads faster, reacts faster and has the same or a smaller σ. Such a facet can only trigger a subset of its base's findings [opinion; tested inside AP-04].
   - Drop a facet that has no share with a source, unless its stakes are high.

   Resolve ties within one class (T4): larger share, then more checks exercised in `E`, then alphabetical order.
4. **Allocation (D'Hondt, kept).** Repeat until `B − r` profiles are used:
   - Pick the segment `s* = argmax_{s : C_s ≠ ∅} w_s / (n_s + 1)`, where `n_s` counts the profiles already attributed to `s`, base included.
   - Take its next facet.

   Resolve ties (T3): priority rank, then a segment with an untried high-stakes facet, then larger `w_s`, then `segment_id`. *Evidence:* apportionment bias is small at these budgets (§2.8) [derived]. AP-15 tests Sainte-Laguë as a sensitivity check.
5. **Place the floors.** For each unmet requirement, attach it to the segment with the highest plausibility score:

   | Floor | Plausibility score |
   | --- | --- |
   | `presbyopia` | Σ of age-band shares ≥ 50s |
   | `cvd_deutan` | `w_s` × male share (0.5 if `sex_mix` is absent); CVD is about 13 times more common in Korean men (5.9 % versus 0.44 %) [derived from `params.py`] |
   | `left_hand(k)` | `w_s` among segments whose top device has input kind `k` |
   | `walking` | `w_s` × share of contexts whose mobility is walking or transit; if all are zero, use the touch segment with the highest `w_s` |

   Resolve ties (T5): larger score, then larger `w_s`, then `segment_id`.
   - If the segment's own evidence supports the facet (its share reaches the step-3 threshold), label the profile `floor_met_by_segment_evidence`.
   - Otherwise, label it `inclusive floor (coverage guarantee, not segment evidence)`.
   - Unused reserve slots go back to step 4.
6. **Left-hand mirror.**
   - A mirror is the base with `one_hand_right→one_hand_left`, `cradle_right→cradle_left`, `mouse_right→mouse_left` and `handedness right→left`. Everything else stays the same, so the differential condition is handedness alone.
   - One mirror per input kind is a floor. It goes on the base of the highest-weight segment whose top device has that input kind.
   - Further mirrors come only through facet class 2, and only on a base whose device differs from every base already mirrored: a different form factor, or a body width at least 5 mm different. Otherwise the mirror is a near-duplicate [opinion; test inside AP-04].

   *Evidence:* Korea's left-handed share is small (5–7 %, `human-factors-checks.md`), but about a third of one-handed phone use is left-thumb (repository handedness research). The left one-hand grip was the costliest removal on dev: 5 defects (R4) [derived].
7. **Explanation card and untested list.** Every profile gets a `why` object:

   ```json
   {"profile_id": "EP-04", "why": {
     "kind": "facet",
     "segment": {"id": "SEG-drivers", "priority": "primary", "weight": 0.55, "weight_basis": "estimated", "confidence": "medium"},
     "base_profile": "EP-01",
     "varies": {"attribute": "grip", "from": "one_hand_right", "to": "one_hand_left", "facet": "left_hand_mirror"},
     "evidence": [{"source_id": "SRC-03", "claim": "...", "quote": "...", "tag": "report"}],
     "floor": "left_hand", "floor_met_by_segment_evidence": false,
     "exercises_checks": ["RH-01", "RH-02", "GZ-02"],
     "not_a_claim": "test condition; says nothing about how many users hold the phone this way"
   }}
   ```

   The plan's `untested` list includes:
   - facets the budget did not reach, ordered by `w_s` × facet share (an ordering key, never printed as a share of users);
   - facets that change no model input, routed to agent runs;
   - declared-but-not-simulated conditions;
   - exclusions, with `test_instead`.

   The report copies `untested` verbatim (AP-18, AP-10).
8. **Agent ranking (`B_agent`).** Use the same steps, but without the no-model-input filter. Facet class 2 becomes "unfamiliar user" (`first_use`, or low `digital_competence`). Each agent run records its model, because agents of one model count as one rater (protocol §5).

All tie-breaks are deterministic. No random seed is used.

**Worked example.** An illustrative street-parking payment app; the numbers are made up, not evidence. Touch only, budget `B = 10`.

The segments:

- **SEG-drivers** (primary, `w` = 0.55, estimated):
  - ages: 30s 0.35, 40s 0.40, 50s 0.25; male share 0.6;
  - devices: galaxy-s24 0.65, iphone-15 0.35;
  - grips: one-hand 0.6, cradle 0.3;
  - contexts: CTX-car (seated, indoor light) 0.55; CTX-kerb (walking, bright sun, one-handed) 0.45.
- **SEG-older** (secondary, 0.30):
  - ages: 60s 0.6, 70s+ 0.4;
  - devices: galaxy-a55 0.7, galaxy-s24 0.3; this follows the Gallup figure of 92 % Samsung at 60+ [snippet · report];
  - conditions: presbyopia 0.9, reduced acuity 0.25; `digital_competence` low 0.5;
  - contexts: CTX-car 0.6, CTX-kerb 0.4.
- **SEG-tremor** (edge; share unknown, default scaled to 0.15; high stakes because money is involved):
  - age 70s+, galaxy-a55, mild tremor 1.0, CTX-car.

Composition runs as follows:

- The segments form 3 bases. The presbyopia floor is met by SEG-older's own evidence.
- Three floors remain unmet: left hand, walking and deutan. So the reserve is `r = min(3, ⌊7/3⌋) = 2`.
- D'Hondt fills 5 slots. The quotients start at 0.275, 0.15 and 0.075.
- The remaining reserve slot returns to D'Hondt after the deutan floor.

| # | Profile | Segment | Kind | What varies | Evidence or floor | Checks it can change |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 40s, galaxy-s24, one-hand right, CTX-car | drivers | base | — | Most common value of each attribute | RH-01/02, PT-02/03/04, GZ-02, plus every check that reads no attribute |
| 2 | 60s, galaxy-a55, one-hand right, presbyopia, CTX-car | older | base | — | Presbyopia 0.9 (floor met by evidence) | PC-04, CG-02, PT-03/04 (× 1.15), GZ-02 |
| 3 | 70s+, galaxy-a55, presbyopia, mild tremor, CTX-car | tremor | base | — | Tremor 1.0; high stakes | PT-03/04 (× 1.3 × 1.5), GZ-02 (× 0.7), PC-04, CG-02 |
| 4 | #1 mirrored | drivers | facet 2 | grip → one-hand left | Left-hand floor | RH-01/02, GZ-02 occlusion side |
| 5 | #1 on iphone-15 | drivers | facet 3 | device | 0.35 ≥ 0.30 | Every geometry check |
| 6 | #2 mirrored | older | facet 2 | grip → one-hand left | Different device from #4 | RH-01/02 on the A55 |
| 7 | #1 in CTX-kerb | drivers | facet 4 | mobility walking + bright sun (checks read them separately) | 0.45; meets the walking floor by evidence | PT-03/04 (× 1.4), PC-05 |
| 8 | #1 at 50s | drivers | facet 6 | age → 50s; presbyopia stays at the base value (AP-14) | 0.25 ≥ 0.20. The 30s facet (0.35) was skipped because the base dominates it. | CG-02 (500 vs 560 syllables/min); GM-03 wherever timed inputs exist |
| 9 | #1 with deutan | drivers | floor | CVD deutan | Inclusive floor, not segment evidence (score 0.6 × 0.55) | PC-03 |
| 10 | #2 on galaxy-s24 | older | facet 3 | device | 0.30 ≥ 0.30 | Geometry checks with presbyopia |

The plan's `untested` list for this example:

- SEG-drivers: cradle grip (0.30).
- SEG-older: CTX-kerb (0.40), reduced acuity (0.25), 70s+ (0.40).
- Every SEG-tremor facet.
- Facets that change no model input: SEG-older with low `digital_competence` (0.5), moved to the agent ranking.
- Facets dominated by their base: age 30s for SEG-drivers.

The dev ablation's `age_50s` stratum lost 2 defects (R4). That stratum sets age 50s *and* presbyopia together (`scripts/ergo_experiments.py`), so the loss cannot be attributed to either one. AP-14 separates them so that the next ablation can tell them apart.

### 3.4 Order of work

1. **Frozen runs, no recording** (hours): AP-05, AP-03, AP-04, AP-18.
2. **Blind Stage 0 on the heldout-2 briefs.** At the time of writing there are two product directories. Run AP-07 and AP-08 (with STAB), the AP-01 guard (PCov), AP-02 (floors on and off), AP-13 and AP-15. Freeze the pass rules before anyone looks at scores.
3. **Driver work:** AP-09 (dark mode and text scale).
4. **Only if triggered:** AP-16 needs product analytics; AP-17 needs defects that require two conditions.

---

## 4. Risks, open questions and what could not be verified

**Could not be verified** (every item below was seen only in excerpts, or not at all):

- Chapman et al. 2008: the exact prevalence curve.
- Matthews et al. 2012: sample size.
- Friess 2012: the share of decisions in which personas were cited.
- McGinn & Kotamraju 2008: sample size.
- Pruitt & Grudin: the per-persona source documents (from memory).
- Pruitt & Adlin: how the weighted matrix computes its weights.
- ISO/IEC 25063: the clause list. ISO 9241-11: the full list of environments.
- Christensen's JTBD articles.
- Appt: its "more than a third" and "26 %" font-size figures disagree, and the sample is Dutch.
- The Gallup 2026 headline (Samsung 81 %).
- NIA: the "older adults" age cut-off.
- The executing agency of the KCC survey.
- WiseApp and Mobile Index methodology.
- The 2023 장애인실태조사.
- The age of presbyopia onset that justifies the spec's rule "ages 50s+ are presbyopic".

Verify these before any of them becomes a default, a threshold or report text.

**Limits of the benchmark.**

- Seeded defects are mostly single-condition by construction; the answer-key examples use one attribute. So the current suites cannot refute base choice, and cannot show the value of pairwise coverage (R3; the software-testing brief makes the same point).
- heldout-mixed was used in the dev ablation (R13), so only heldout-2 can decide composition questions.
- heldout-2 has only a few products so far. Experiments will have low power: use exact McNemar tests and Wilson intervals, and fix the pass rules in advance.

**Requiring evidence can hide real risks.** If Stage 0 is shallow, requiring evidence for a condition (AP-03) drops conditions that do matter, such as glare for couriers or parking. Mitigations:

- the floors stay;
- gated conditions are listed in `untested`;
- a mobile product whose audience file has no context evidence keeps the walking floor, and the report says the environment was not researched.

**Prevalence creep.** Segment weights printed next to findings invite readings such as "affects 55 % of users", the exact failure Chapman & Milham warn about. Keep weights out of finding text. `segments_at_risk` lists names and priorities only.

**LLM Stage-0 risks.**

- Numbers may be invented or taken from the wrong population.
- Ownership may be mixed up with use (§2.7), or 55+ with 65+.
- Korean table labels may be mistranslated.
- Two runs on the same brief may disagree.

AP-07 and AP-08 are the controls. A human should still spot-check quotes on high-stakes products.

**Low digital competence cannot be simulated by the deterministic models.** It is the largest gap in the NIA survey: competence 65.6 % versus access 96.5 %. It reaches the swarm only through task choice and interactive agents, whose validity is limited (`persona-agent-protocol.md`). The report must say so, and recommend testing with real older users.

**Sensitive attributes.** Disability data and sex are needed only in aggregate, to decide where facets are plausible. Never collect them per person, and never let them drive an agent's voice.

**Institutional drift.**

- 방송통신위원회 has been reorganised as 방송미디어통신위원회.
- The digital-divide survey now falls under 디지털포용법 (see `korean-population-context.md`).
- Survey names and URLs change; each prior value keeps its date and source.

**Open questions.**

1. Which tablet viewing distance should PC-04 use? PC-04 produced 36 % of held-out findings, most of them on the tablet at the catalog default of 400 mm. `contexts[].viewing_distance_mm` makes this an audience question, but no evidence was gathered here.
2. Should text scale 1.3 be a floor for segments aged 60+? There is no Korean telemetry. Appt's Dutch figures are the only lead.
3. When audience facets disagree with the ablation (for example, a product whose audience evidence strongly supports tremor, which never produced a unique defect on dev), evidence should win for inclusion. The finding should then be reported with its hypothesis tier. This needs a team decision.
