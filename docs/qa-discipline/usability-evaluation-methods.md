# Usability evaluation science for the ergonomic persona swarm

Date: 2026-09-28. Topic: problem-discovery models, the evaluator effect, and
how to judge whether an evaluation method is any good. The brief then applies
these to `skills/ergonomic-persona-swarm-qa`. It is research only. No code,
benchmark, answer key or validation record was changed.

**Evidence tags.** [standard] normative text · [paper] peer-reviewed value
checked in the source · [industry] vendor or company documentation ·
[report] survey or government statistics · [snippet] seen only in a
search-result excerpt, not checked in the source · [derived] my own
computation, from cited numbers or from this repository's files ·
[opinion] practitioner opinion (mine unless attributed).

**Read this first.** The egress proxy blocked WebFetch for every domain I
tried, so I could not open any primary source. Every literature claim below
comes from search-result excerpts and is tagged [snippet], even when the
excerpt quoted an abstract. No claim is tagged [paper]. Check every number
against its source before it becomes a gate or a threshold in code. Where I
give a formula from memory, the text says so.

---

## 1. Scope and sources searched

**Local context read.** `skills/ergonomic-persona-swarm-qa/SKILL.md`;
`references/human-factors-checks.md`, `persona-agent-protocol.md` and
`validation-and-limits.md` (added at the time of writing);
`docs/ergonomic-swarm-spec.md` (§0, §2 profile, §6 observation, §7 finding,
§12 and the new §12.1); the top-level summary of
`docs/validation/heldout-mixed-frozen-8c1de02.json`;
`scripts/ergo_bench.py`; `scripts/ergo_experiments.py` (header and
structure); `ergoqa/bench.py`; `ergoqa/swarm.py`; the strata in
`ergoqa/profiles.py`; and the frozen held-out tool outputs
`.ergo-bench/heldout-frozen/findings-*.json` and `profiles.json`. I did not
open any `benchmarks/*/answer_key.json`, any `benchmarks/*/README.md`, or the
`score-*.json` files, because those repeat answer-key content.

**Web.** 31 WebSearch queries. WebFetch returned `EGRESS_BLOCKED` for
nngroup.com, measuringu.com, journals.sagepub.com, api.semanticscholar.org,
arxiv.org, en.wikipedia.org, mortenhertzum.dk, dl.acm.org, tandfonline.com,
cacm.acm.org and redalyc.org. The pages below were reached only through
search excerpts.

Problem-discovery models
- Nielsen & Landauer 1993, INTERCHI '93, 206–213: https://dl.acm.org/doi/10.1145/169059.169166 ; https://www.semanticscholar.org/paper/A-mathematical-model-of-the-finding-of-usability-Nielsen-Landauer/245061d94c228abdc9bda2d9a10679e897526465
- NN/g summary "Why you only need to test with 5 users" (blocked; seen through secondary excerpts): https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/ ; https://www.humanfactors.com/newsletters/how_many_test_participants.asp
- Virzi 1992, Human Factors 34(4): https://journals.sagepub.com/doi/10.1177/001872089203400407
- Lewis 1994 (title only): https://www.researchgate.net/publication/15128047_Sample_Sizes_for_Usability_Studies_Additional_Considerations
- Lewis 2001, IJHCI 13(4): https://www.researchgate.net/publication/220302535_Evaluation_of_Procedures_for_Adjusting_Problem-Discovery_Rates_Estimated_From_Small_Samples
- Faulkner 2003, BRMIC 35(3): https://link.springer.com/article/10.3758/BF03195514 ; https://pubmed.ncbi.nlm.nih.gov/14587545/
- Hwang & Salvendy 2010, CACM 53(5): https://dl.acm.org/doi/10.1145/1735223.1735255
- Schmettow 2012, CACM 55(4): https://dl.acm.org/doi/10.1145/2133806.2133824 ; https://cacm.acm.org/research/sample-size-in-usability-studies/
- Petersson, Thelin, Runeson & Wohlin 2004, JSS 72(2): https://www.sciencedirect.com/science/article/abs/pii/S0164121203000906 ; https://wohlin.eu/jss04-1.pdf
- Briand, El Emam, Freimut & Laitenberger 2000, IEEE TSE 26(6): https://www.researchgate.net/publication/3188084_A_Comprehensive_Evaluation_of_Capture-Recapture_Models_for_Estimating_Software_Defect_Content
- Wang et al., "Crowdtesting: when is the party over?": https://arxiv.org/abs/1805.03218
- Kuhn, Wallace & Gallo 2004, IEEE TSE: https://csrc.nist.gov/CSRC/media/Projects/automated-combinatorial-testing-for-software/documents/kuhn-wallace-gallo-tse-preprint.pdf ; https://csrc.nist.gov/Projects/automated-combinatorial-testing-for-software/combinatorial-methods-in-testing/interactions-involved-in-software-failures

The evaluator effect and reproducibility
- Hertzum & Jacobsen 2001/2003: https://mortenhertzum.dk/publ/IJHCI2003.pdf ; https://www.tandfonline.com/doi/abs/10.1207/S15327590IJHC1501_14
- CUE-2 (Molich et al. 2004, BIT 23(1)): http://molich.dk/cue-2/ ; https://www.tandfonline.com/doi/abs/10.1080/0144929032000173951
- CUE-4 (Molich & Dumas 2008, BIT 27(3)): https://www.tandfonline.com/doi/abs/10.1080/01449290600959062
- Molich, "Are usability evaluations reproducible?", interactions 2018: https://interactions.acm.org/archive/view/november-december-2018/are-usability-evaluations-reproducible
- CUE-9 (Hertzum, Molich & Jacobsen 2014, BIT 33(2)): https://mortenhertzum.dk/publ/BIT2014.pdf ; https://www.dialogdesign.dk/cue-9/
- Hornbæk & Frøkjær 2008, IwC 20(6): https://academic.oup.com/iwc/article-abstract/20/6/505/667956

Criteria for judging evaluation methods
- Hartson, Andre & Williges 2001, IJHCI 13(4): https://www.tandfonline.com/doi/abs/10.1207/S15327590IJHC1304_03
- Andre, Williges & Hartson 1999: https://doi.org/10.1177/154193129904302007 ; Andre, Hartson & Williges 2003: https://doi.org/10.1518/hfes.45.3.455.27255
- Gray & Salzman 1998, HCI 13(3): https://www.tandfonline.com/doi/abs/10.1207/s15327051hci1303_2 ; https://homepages.rpi.edu/~grayw/pubs/papers/1998/Gray&Salzman98_HCI.html
- Sears 1997, IJHCI 9(3): https://www.tandfonline.com/doi/abs/10.1207/s15327590ijhc0903_2
- Cockton & Woolrych 2001: https://link.springer.com/chapter/10.1007/978-1-4471-0353-0_11 ; Cockton et al. 2003 (title only): https://link.springer.com/chapter/10.1007/978-1-4471-3754-2_9
- Hornbæk 2010, "Dogmas…" (the excerpts about impact and persuasiveness came from here): https://www.kasperhornbaek.dk/papers/BIT2010_Dogmas.pdf
- Hertzum 2006, IJHCI 21(2): http://mortenhertzum.dk/publ/IJHCI2006.pdf

Inspection and walkthrough methods, including LLM evaluators
- Nielsen 1992, CHI '92: https://dl.acm.org/doi/10.1145/142750.142834 ; NN/g theory page (blocked): https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/theory-heuristic-evaluations/
- Wharton, Rieman, Lewis & Polson 1994: https://dl.acm.org/doi/10.5555/189200.189214 ; https://www.colorado.edu/ics/sites/default/files/attached-files/93-07.pdf
- Blackmon et al. CWW, CHI 2002: https://dl.acm.org/doi/10.1145/503376.503459 ; CHI 2005: https://www.researchgate.net/publication/221518807_Tool_for_accurately_predicting_website_navigation_problems_non-problems_problem_severity_and_effectiveness_of_repairs
- Synthetic heuristic evaluation (2025): https://arxiv.org/abs/2507.02306 ; GPT-4o heuristic evaluation: https://arxiv.org/pdf/2506.16345 , https://link.springer.com/chapter/10.1007/978-3-032-05005-2_20 ; "Synthetic Cognitive Walkthrough" (title only): https://arxiv.org/pdf/2512.03568

Severity ratings
- Nielsen 1992 poster, "Reliability of severity estimates…": https://dl.acm.org/doi/10.1145/1125021.1125117 ; NN/g severity article (blocked): https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/
- Sauro 2014, JUX 10(1): https://uxpajournal.org/the-relationship-between-problem-frequency-and-problem-severity-in-usability-evaluations/
- Herr et al. CHI 2016 (title only): https://cml.hci.uni-bamberg.de/~gross/publ/chi16_herr_et_al_severity_rating_scales__proceedings.pdf

Think-aloud and task metrics
- Fox, Ericsson & Best 2011, Psychological Bulletin 137(2): https://eric.ed.gov/?id=EJ933832
- Sauro & Lewis, adjusted-Wald completion rates and *Quantifying the User Experience*: https://measuringu.com/papers/sauro-lewisHFES.pdf ; https://www.educate.elsevier.com/book/details/9780128023082

---

## 2. Key knowledge

### 2.1 Problem-discovery models

- **Poisson/binomial model.** Nielsen & Landauer (INTERCHI '93, pp. 206–213)
  found that the number of problems detected, as a function of the number of
  test users or heuristic evaluators, is "well modeled as a Poisson process",
  which lets a team plan evaluation for a target thoroughness [snippet]. The
  usual form is Found(n) = N·(1 − (1 − λ)^n). λ averaged **0.31** over the
  projects studied, which gives about **85 %** of problems with 5 users.
  Secondary summaries of the NN/g article say about 15 users find nearly all
  problems [snippet; secondary excerpts, not the paper].
- [derived] At p = 0.31, 1 user finds 31 %, 3 users 67 %, 5 users 84.4 %,
  10 users 97.6 % and 15 users 99.6 %.
- **Virzi 1992** (Human Factors 34(4)) reported three experiments. About
  **80 %** of problems were found with **4–5** subjects, and further subjects
  were less and less likely to reveal new problems. The most severe problems
  tended to appear with the first few subjects. On average **5 subjects found
  80 % and 9 found 95 %** [snippet].
- **Lewis 1994** ("Sample sizes for usability studies: additional
  considerations"). I saw only the title. Its content, which is often cited as
  failing to replicate Virzi's link between severity and discovery order, is
  not verified here.
- **Lewis 2001** (IJHCI 13(4):445–479). Estimates of p from small samples
  have a "serious overestimation bias", which leads to underestimated sample
  sizes and overestimated proportions discovered. Monte Carlo simulations
  showed that the average of a normalization procedure and Good–Turing
  discounting gives highly accurate estimates from small samples [snippet].
  The algebra as I recall it is p_adj = ½·(p̂ − 1/n)(1 − 1/n) + ½·p̂/(1 + GT),
  where GT = (problems seen exactly once) / (distinct problems). This formula
  is from memory; verify it in Lewis 2001 or Sauro & Lewis before coding it.
- **Faulkner 2003** (BRMIC 35(3):379–383) tested 60 users and drew random
  subsets. Sets of 5 users found between **55 % and 99 %** of problems. The
  worst set of 10 found **80 %** and the worst set of 20 found **95 %**
  [snippet]. The spread of results, and not only the mean, is what argues
  against small samples.
- **Hwang & Salvendy 2010** (CACM 53(5):130–133) meta-analysed studies since
  1990 covering think-aloud, heuristic evaluation and cognitive walkthrough.
  They concluded that **10 ± 2** participants or evaluators find about 80 % of
  problems [snippet].
- **Schmettow 2012** (CACM 55(4):64–70). Magic numbers and the geometric
  series formula both "underestimate required sample size" because problems
  differ in how detectable they are (heterogeneity). He proposed an extended
  model, the zero-truncated logit-normal binomial (LNB), to estimate how many
  problems remain undiscovered and to keep adding participants until they are
  found [snippet].
- [derived] **Why heterogeneity matters for condition-specific problems.**
  Suppose a problem affects only users in a condition whose population share
  is s, and every such user hits it. In a random sample, the per-user
  discovery probability is then p ≈ s. The number of users needed for 80 %
  discovery, ln 0.2 / ln(1 − p), is 5 at p = 0.31, 16 at 0.10, 32 at 0.05,
  53 at 0.03 and 161 at 0.01. Averaging p over all problems, as the geometric
  model does, hides these rare-condition problems.
- **Capture–recapture and Good–Turing in software inspection.**
  - Petersson, Thelin, Runeson & Wohlin 2004 (JSS 72(2):249–264) reviewed ten
    years of work. Most software-engineering evaluations end by recommending
    Mh-JK, a heterogeneity model with a jackknife estimator. Mh-JK is
    "accurate when the number of reviewers is 4 or more" but is "non-robust in
    the case with two reviewers and produces underestimates" [snippet].
  - Briand et al. 2000 (IEEE TSE 26(6):518–540) is the comprehensive
    evaluation of capture–recapture models for defect content. I saw only the
    title and venue [snippet].
  - Wang et al. ("Crowdtesting: when is the party over?", arXiv 1805.03218)
    built 8 close-prediction methods, including a capture–recapture estimate
    of total bugs. Across 218 crowdtesting tasks, a median **91 %** of bugs
    were detected with **49 %** of the cost saved [snippet]. This is the
    closest published analogue to deciding when to stop adding agents.
- **Combinatorial testing** is relevant to choosing profile sets. Kuhn,
  Wallace & Gallo 2004 (IEEE TSE) found that the share of failures triggered
  by a single factor ranged from **9 % to 67 %** across the applications
  studied. One or two factors triggered **47 %–97 %**, and no failure needed
  more than six [snippet]. The excerpt came from NIST pages that may include
  later data sets.

### 2.2 The evaluator effect and reproducibility across teams

- **Hertzum & Jacobsen** (IJHCI, 2001; reprinted in 15(1), 2003) reviewed
  11 studies of cognitive walkthrough, heuristic evaluation and think-aloud
  testing. The average agreement between any two evaluators who used the same
  method on the same system ranged from **5 % to 65 %**. The effect held for
  novice and experienced evaluators, cosmetic and severe problems, problem
  detection and severity assessment, and simple and complex systems
  [snippet]. I compute any-two agreement as the mean, over evaluator pairs, of
  #(Pi ∩ Pj) / #(Pi ∪ Pj). That formula is from memory; the paper could not be
  opened.
- **CUE-2** (Molich et al. 2004, BIT 23(1)): 9 teams tested Hotmail and
  reported 310 different problems. **232 (75 %)** were reported by only one
  team, and only **2** were reported by six or more teams [snippet].
- **CUE-4** (Molich & Dumas 2008, BIT 27(3)): 17 professional teams evaluated
  the Hotel Pennsylvania website, 9 with usability tests and 8 with expert
  reviews. They reported **340** issues. **205 (60 %)** came from a single
  team, and only **9** were reported by more than half the teams. There was
  "no practical difference" between testing and expert review, and it was
  "not possible to prove the existence of either missed problems or false
  alarms in expert reviews" [snippet].
- **CUE-9** (Hertzum, Molich & Jacobsen 2014, BIT 33(2):143–161): 19
  experienced professionals analysed the same video-recorded sessions with 5
  users of the U-Haul site. Any-two agreement was **30 %** for unmoderated
  sessions and **31 %** for moderated ones. An evaluator in the moderated
  group reported on average **33 %** of all problems the nine reported, and
  **50 %** of the problems that someone rated critical or serious. Of the
  problems reported by several evaluators, **24 %** (moderated) and **30 %**
  (unmoderated) were rated critical by one evaluator and minor by another
  [snippet].
- **Hornbæk & Frøkjær 2008** (IwC 20(6):505–514). Matching problem
  descriptions decides the overlap figures in every method or evaluator
  comparison, and it "may be fundamentally unreliable". In the study, 52
  novice evaluators matched the same problem descriptions from three
  think-aloud studies [snippet].
- [opinion] Any overlap, agreement or "k raters agree" number is only as good
  as its matching key, so the key must be stated with the number.

### 2.3 How to judge an evaluation method

- **Hartson, Andre & Williges 2001** (IJHCI 13(4):373–410) argue that methods
  cannot be compared reliably without standard criteria. Their criteria
  include **thoroughness, validity, effectiveness and reliability**.
  Thoroughness = real problems found / real problems that exist [snippet].
  The same group scores a method's output against a reference method as hits,
  misses, false positives and false negatives (Andre et al. 1999; Hartson et
  al. 2003) [snippet]. Andre et al. (1999) call thoroughness, validity and
  reliability the core metrics [snippet]. The usual definitions are validity =
  real problems found / issues reported as problems and effectiveness =
  thoroughness × validity. The excerpts attribute these equations to Sears
  (1997) [snippet], but I did not see their exact wording. The brief I was
  given also lists downstream utility and cost-effectiveness; I did not verify
  those in excerpts.
- **Sears 1997** (IJHCI 9(3)) proposed ways to compare validity, thoroughness
  and reliability. The heuristic walkthrough, which is heuristic evaluation
  with task-based walkthrough structure, found more problems than a cognitive
  walkthrough and produced fewer false positives than heuristic evaluation
  [snippet].
- **Gray & Salzman 1998** (HCI 13(3)) reviewed five influential experiments
  that compared evaluation methods. They concluded that "small problems in the
  way these experiments were designed and conducted call into serious
  question what we thought we knew" about how well the methods work
  [snippet]. The validity typology often attributed to them (Cook & Campbell's
  statistical-conclusion, internal, construct and external validity, plus
  conclusion validity) is not verified here.
- **Cockton & Woolrych 2001.** 99 analysts, working in groups, applied
  heuristic evaluation to a drawing editor. Structured problem-report formats
  made it easier to merge predictions and to match them against problems
  extracted from user tests, which were designed to exercise every predicted
  problem. The work led to the DR-AR model of inspection effectiveness
  [snippet]. False positives were analysed, but I could not retrieve their
  share.
- **Downstream utility.** Sawyer, Flanders & Wixon 1996 (CHI '96, 376–382)
  define **impact ratio** = problems solved / problems found. John & Marks
  (1997) call this persuasive power, and Law (2006, IJHCI 21(2):147–172)
  studies downstream utility and the "developer effect" [snippet]. Hertzum
  (2006) finds that designers' response to evaluation results depends on
  factors that "may overshadow severity" [snippet].
- Hornbæk 2010, "Dogmas in the assessment of usability evaluation methods"
  (BIT): only the title and PDF location were seen.

### 2.4 Inspection and walkthrough methods, including LLM evaluators

- **Heuristic evaluation.** Averaged over six of Nielsen's projects, a single
  evaluator found **35 %** of problems. Three evaluators found about 75 % and
  five about 85 % [snippet; the 3- and 5-evaluator figures may come from
  secondary summaries]. [derived] With λ = 0.35, the model gives 72.5 % for 3
  evaluators and 88.4 % for 5. Nielsen (CHI '92) found that usability
  specialists outperformed non-specialists, and "double experts" (usability
  plus domain) did better still [snippet]. The often-quoted 22 %, 41 % and
  60 % figures were not retrieved.
- **Cognitive walkthrough** (Wharton, Rieman, Lewis & Polson 1994) asks four
  questions at each step [snippet]:
  1. Will the user try to achieve the right effect?
  2. Will the user notice that the correct action is available?
  3. Will the user associate the correct action with the effect they are
     trying to achieve?
  4. If the correct action is performed, will the user see that progress is
     being made?
- **CWW** (Blackmon et al., CHI 2002; Blackmon, Kitajima & Polson, CHI 2005,
  31–40) uses Latent Semantic Analysis to estimate "information scent": the
  semantic similarity between 100–200-word user goal statements and
  heading/link texts. It identifies three types of navigation problem
  [snippet]. The 2005 paper's title claims accurate prediction of problems,
  non-problems, problem severity and repair effectiveness. Its numbers were
  not retrieved.
- **LLM evaluators.**
  - A 2025 comparison (arXiv 2507.02306) had an LLM perform heuristic
    evaluation. It identified **73 % and 77 %** of issues in two apps, against
    **57 % and 63 %** for five experienced human evaluators. It did best on
    "aesthetic and minimalist design" (86 % and 74 %, against 38 % and 42 %),
    worst on "consistency and standards" (46 % and 40 %), and struggled with
    violations that span screens [snippet].
  - A GPT-4o study (arXiv 2506.16345; Springer 2025) reports false positives
    from hallucination and from "attempts to predict issues" [snippet].
  - [opinion] LLM evaluators look like high-recall, low-validity evaluators.
    That is the heuristic-evaluation failure mode, in an extreme form.

### 2.5 Severity-rating reliability

- **Nielsen 1992 poster** (CHI '92 posters): severity ratings from a single
  evaluator are "very unreliable". The mean rating of **four** evaluators
  came within **half a rating point** of the true severity **95 %** of the
  time, and 3–4 evaluators are "satisfactory for many practical purposes".
  Ratings correlated positively with the number of evaluators who found each
  problem [snippet].
- **What severity is made of.** Severity combines frequency, impact and
  persistence (NN/g) [snippet]. Hertzum (2006, IJHCI 21(2):125–146) reports
  that the correlations among these three are often modest, so raters who
  weigh different components disagree [snippet].
- **Sauro 2014** (JUX 10(1):17–25): across nine studies with several
  independent raters, the average correlation between problem frequency and
  severity was not different from zero, and only one study showed a positive
  correlation. His advice is to treat frequency and severity as independent
  [snippet].
- **Other disagreement data.** In CUE-9, 24–30 % of problems reported by
  several evaluators were rated critical by one and minor by another
  [snippet]. Hertzum & Jacobsen found the evaluator effect in severity
  assessment as well as in detection [snippet]. Herr et al. (CHI 2016)
  compared severity rating scales for heuristic evaluation; only the title was
  seen.

### 2.6 Think-aloud validity and task metrics

- **Fox, Ericsson & Best 2011** (Psychological Bulletin 137(2):316–344), a
  meta-analysis of about **3,500** participants. The effect of think-aloud on
  performance was **r = −0.03**, indistinguishable from zero. Instructions
  that asked for explanations or detailed descriptions were reactive, meaning
  they changed performance [snippet].
- **Sauro & Lewis** recommend the adjusted-Wald binomial interval for
  completion rates, because the plain Wald interval "grossly understates" the
  width at small n [snippet]. The SUS mean of about 68 and the SEQ norms are
  widely cited but were not verified at the time of writing;
  `docs/human-factors/perception-cognition.md` lists them as recalled.
- [opinion] An LLM agent's "think-aloud" is not a verbal protocol.
  `persona-agent-protocol.md` §7, which forbids agents from filling in SUS,
  SEQ or NASA-TLX, is consistent with this literature.

### 2.7 Audit of this repository's own numbers (no answer key read)

These figures come from `docs/validation/heldout-mixed-frozen-8c1de02.json`,
`.ergo-bench/heldout-frozen/{profiles.json, findings-*.json}` and the code
named below.

- **Swarm size.** 49 profiles: 14 each on galaxy-tab-s9, iphone-15 and
  galaxy-s24-ultra, and 7 on laptop-1440. `single_profile` uses one default
  persona per device, so 4 profiles. Three `first_use` profiles are included,
  but `cognition.familiarity` is read by no check in `ergoqa/checks.py`
  [derived].
- **Strict detections and uncertainty.** Measured-only found 3/20 defects
  (Wilson 95 % CI 0.05–0.36), single profile 7/20 (0.18–0.57) and the swarm
  16/20 (0.58–0.92). Swarm against single profile: 9 gained, 0 lost, exact
  McNemar p = 0.0039. Swarm against measured-only: 13 gained, 0 lost,
  p = 0.00024. Decoys flagged: 2/6 (0.10–0.70) [derived].
- **Where the noise comes from** [derived]:

  | Step | Defects gained | Clean-control findings added | Clean-control findings per defect gained | All findings added | Findings per defect gained | `precision_labeled` |
  | --- | --- | --- | --- | --- | --- | --- |
  | Turn on model checks for the default persona (measured-only → single profile) | +4 | +48 | 12.0 | +105 | 26.3 | 0.656 → 0.318 |
  | Add 45 stratified profiles (single profile → swarm) | +9 | +39 | 4.3 | +81 | 9.0 | 0.318 → 0.34 |

  On this suite, extra profiles bought recall at about a third of the noise
  cost of the model checks themselves. Precision did not fall.
- **Composition of the swarm's 225 findings** [derived]:
  - 149 (66 %) are model-basis P3.
  - PC-04 (text visual angle) alone produces 82 (36 %), all P3, with up to 28
    in one scenario. It also produces 32 findings for the default persona
    alone. Its P3 rule rests on a Hangul critical-print-size threshold that
    `human-factors-checks.md` marks "snippet-level, metric unconfirmed".
  - By consolidation key, the 225 findings are 202 units by (scenario,
    element, category), 153 by (scenario, element), 63 by (scenario, check,
    identical set of triggered profiles) and 52 by (scenario, check).
- **Coverage denominators are missing for most checks** [derived]. 203 of
  225 findings (90 %) have `tested_profiles == triggered_profiles`, and 220
  of 225 have an empty `profile_specific`. Examples:
  - PC-04 on `SC-hm-lesson-a` is labelled "7/7 simulated profiles". The seven
    triggered profiles are all presbyopic (50s–70s+). The seven
    non-presbyopic galaxy-tab-s9 profiles were evaluated but do not appear in
    `tested_profiles`. The label should read 7/14 with
    `vision.presbyopia = true`.
  - PC-05 ("1/1") and PC-03 ("1/1") have the same defect.

  The cause is that most checks emit only failing observations; spec §6 keeps
  `passed: true` observations "only in verbose mode". `swarm.aggregate` then
  builds `tested` from emitted observations only. Only RH-01, PT-04 and GM-03
  show k < n.
- **Scorer semantics** (`ergoqa/bench.py`) [derived]:
  - A finding counts toward "matched" (precision numerator) through a
    *lenient* match when no strict match exists.
  - Several findings matching one defect all count.
  - `severity_ok` is one-sided: at least as severe as `severity_min`. An
    over-rating tool therefore scores well.
  - A finding whose `element_key` starts with `viewport|` matches any
    selector, but it is excluded from decoy hits. The held-out suite had 0
    such findings, so its 0.80 is unaffected. The game suites may not be.

### 2.8 Mapping the literature onto the swarm's layers

| Layer | Is it a sampling process? | Discovery model that applies | Main validity threat |
| --- | --- | --- | --- |
| Measured checks (fixed standard on measured geometry, colour or timing) | No. The output is deterministic given the recording. | None. Stability across re-recordings is the reliability measure. | Construct: the standard is not the same as user harm. Flaky timing inputs. |
| Model checks × profiles | No. Each check is a pure function of (run, profile). | Combinatorial coverage of attribute values, not 1 − (1 − p)^n. | Thresholds with weak evidence (PC-04 P3); severity rising with the number of profiles through the max rule. |
| LLM persona agents (judgment, paths reached) | Yes. Different agents behave like different evaluators. | Discovery curves with heterogeneity (Schmettow); capture–recapture (Mh-JK with ≥ 4 raters); the crowdtesting stop rule. | Evaluator effect; correlated raters from one model; hallucinated false positives. |
| Recording of runs | Partly: timing, animation, network. | None. Measure any-two agreement across re-runs. | Flaky findings counted as real. |
| Benchmark scoring | Not applicable. | Not applicable. | Matching leniency (Hornbæk & Frøkjær); a one-rater "gold" severity; small n (Gray & Salzman). |

---

## 3. Implications for the skill

Rows are ordered by my estimate of expected value: benefit × confidence ÷
effort. Field names follow the spec. Thresholds marked "policy" are team
choices, not literature values.

| ID | Type | What exactly | Evidence | Expected effect on recall / noise / usefulness | Experiment that decides it (hypothesis, metric, pass rule, data needed) | Effort |
| --- | --- | --- | --- | --- | --- | --- |
| UEM-01 | CHANGE | **Record the denominator.** For each (scenario, check, element), every check records the profiles it evaluated (`evaluated_profiles`) and those for which it did not apply (`not_applicable_profiles`), even when all pass. `swarm.aggregate` sets `tested_profiles` to the evaluated set and computes `profile_specific` from evaluated-but-untriggered profiles. It restricts the differential to the attributes the check reads, through a new `CheckSpec.profile_inputs` (for example, PC-04 reads `age_band`, `vision.*` and viewing distance). | 203/225 held-out findings have tested == triggered, and 220/225 have an empty differential. PC-04 reads "7/7" when it should read 7/14, presbyopia [derived, §2.7]. Thoroughness-type measures need a denominator (Hartson et al. 2001) [snippet]. | Recall unchanged. Usefulness rises: the swarm's two distinctive outputs, the coverage label and the differential condition, become informative for about 90 % of findings. Prerequisite for UEM-02, 05 and 07. | H: every finding with 0 < k < n gets a non-empty differential. Metric: share of non-empty differentials where k < n; per-defect strict detection. Pass: identical per-defect detection on all suites and ≥ 90 % non-empty. Data: offline re-analysis of the existing `.ergo-bench` recordings. | S |
| UEM-02 | CHANGE | **Count problem units, not findings.** Unit key = (`scenario_id`, `check_id`, differential condition), with the elements listed as `instances`. A systemic problem, such as small body text on a whole page for presbyopic profiles, becomes one unit. The benchmark matches a defect when any instance matches its selector. `report.md` counts units; `findings.json` keeps per-element detail. | Merging instances into problems is a standard step before counting, and structured reports make it reliable (Cockton & Woolrych 2001; Hornbæk & Frøkjær 2008) [snippet]. 225 findings become 63 units by (scenario, check, trigger set); PC-04 alone is 82 findings [derived]. | Recall unchanged. The reported count falls by about 70–77 %. Triage time falls. | H: unit-level clean-control count ≤ 0.4 × the finding-level count, with identical strict recall. Metric: clean-control units, strict recall, reviewer minutes per real problem (2 reviewers, 1 suite). Pass: as stated. Data: existing runs. | S |
| UEM-03 | CUT | **The default report keeps only validated findings.** It keeps measured findings, model findings at P1–P2, and model P3 findings only when the element is on the task path *and* trace evidence corroborates them (the script or agent failed, retried or slowed at that element). Two groups move to `hypotheses[]`, grouped by condition: all other model P3 findings, and any finding whose threshold is tagged [snippet] or [assumption] in `ergoqa/params.py` (for example, PC-04's Hangul critical-print-size rule). | 149/225 findings (66 %) are model P3; PC-04 P3 = 82, including 32 for the default persona [derived]. Low-severity problems are the least reproducible: an evaluator reports 33 % of all problems but 50 % of critical ones (CUE-9); severity rises with the number of finders (Nielsen 1992) [snippet]. Inspection predictions need confirmation (Cockton & Woolrych 2001; Sears 1997) [snippet]. | Noise falls sharply (up to −66 % of findings, and likely more of the clean-control units). Recall falls only for defects whose best match is a model P3 finding. | H: demotion cuts clean-control units by ≥ 50 % and loses ≤ 1 of 20 held-out defects (strict). Metric: per-defect McNemar against the current output; clean units. Pass: recall loss ≤ 0.05 absolute on every suite. Data: offline re-scoring. | S |
| UEM-04 | CHANGE | **Replace the headline metrics with Hartson/Sears metrics at unit level** (§3.1): `thoroughness_strict` with a Wilson CI, `validity_lb`, `validity_adj`, `effectiveness` = T × V, `false_alarms_per_clean_scenario` by severity with the gate P0 + P1 = 0, and two-sided severity metrics (exact, within one level, over-rating rate, quadratic-weighted κ against a consensus). True positives come from strict matches only; lenient matches are diagnostic. No defect is counted twice. | Hartson et al. 2001; Sears 1997 [snippet]. `ergoqa/bench.py` counts lenient matches and duplicates as true positives, and its `severity_ok` (≥ `severity_min`) rewards over-rating [derived]. | Detection unchanged. Precision and severity become honest, and over-rating becomes visible. | H: unit-level `validity_lb` differs from `precision_labeled` by ≥ 0.05 in at least one suite. Metric: both, on all scored suites. Pass: adopt the new headline if any suite differs; keep the old numbers for one release. Data: existing scores. | S |
| UEM-05 | CHANGE | **Enumerate the deterministic layer; do not sample it.** Checks are pure functions of (recorded run, profile). Evaluate each run on the full grid of values the checks read: grip 4 × vision {none, deutan, protan, presbyopic} × tremor {none, mild, moderate} × context {seated, walking, bright sun} × hand percentile {5, 50, 95} × age {≤ 50s, 60s, 70s+}, which is 3,888 cells per device. The alternative is a t = 2 covering array (at least 16 rows per device) plus adaptive refinement around failing cells. Report each unit's minimal failure-inducing condition, and report `combinatorial_coverage` {t1, t2} over audience-relevant values instead of a profile count. Drop the attributes no check reads (`cognition.familiarity`, `context.interruptions`, `context.free_hands`) from deterministic profiles; keep them for agents. | Most failures need 1–2 factors, none more than 6 (Kuhn et al. 2004) [snippet]. Random samples of 5 users ranged 55–99 % (Faulkner 2003) [snippet], so sampling adds variance where enumeration is cheap. Recording is the expensive step (14–31 s per held-out run; 183 s for the whole suite) and analysis is offline [derived]. | Recall ≥ current, with no misses from sampling. Raw findings rise unless UEM-01, 02, 03 and 07 are in place. Usefulness rises: exact condition boundaries replace "k/n". | H1: t = 2 recall = full-grid recall on all suites. H2: full-grid recall ≥ the recall of the 14-profile stratified swarm. Metric: strict recall, clean units, analysis time. Pass: H1 and H2 hold, and grid + UEM-02/03 clean units ≤ the current clean-control findings. Data: existing recordings. | M |
| UEM-06 | ADD | **Estimate saturation and stop adding agents, without an answer key** (for the stochastic layer: LLM persona agents, judgment units, and distinct screens or states reached). Build an agent × unit incidence matrix. Compute an accumulation curve (mean of 200 random orders), Q1 and Q2, Chao2 and jackknife-1 totals, Good–Turing coverage, and a Lewis-adjusted p̂ for a geometric projection (§3.2). Start with 4 heterogeneous agents (2 model families × screenshot or accessibility-tree channel) and add them in pairs. Stop when the last 2 add no new corroborated unit and coverage ≥ 0.9 (policy), with a cap of m = 12. Report the estimates as lower bounds when agents share a model. | Small-sample p is overestimated; normalization plus Good–Turing corrects it (Lewis 2001) [snippet]. Heterogeneity makes the geometric model underestimate n; estimate what remains (Schmettow 2012) [snippet]. Mh-JK is accurate with ≥ 4 reviewers and underestimates with 2 (Petersson et al. 2004) [snippet]. 10 ± 2 for 80 % (Hwang & Salvendy 2010) [snippet]. A capture–recapture stop rule kept 91 % of bugs at 49 % of cost (Wang et al.) [snippet]. | The remainder of agent-detectable defects becomes measurable. Agent cost falls. Noise is neutral. | H: after m ≥ 4, the estimate is within ±30 % of the pooled total at m = 12 on ≥ 70 % of scenarios, and the stop rule reaches ≥ 80 % of the m = 12 corroborated units at ≤ 60 % of the agent cost. Data: 12 agent runs per heldout-2 scenario over ≥ 2 model families, using defects with `detectable_by: agent_judgment`. | M |
| UEM-07 | CHANGE | **Severity must not rise with swarm size.** Store `severity_by_condition`. The headline severity is the maximum over cells that `ergo-audience.v1` marks primary or secondary, plus `edge` cells only when the stakes rule applies. Report the worst-case cell separately. Coverage never feeds severity. Keep the +1 raise for critical-path primary and destructive elements. | Taking the maximum over triggered profiles is an order statistic: it never falls as profiles are added, and it saturates on a full grid [derived]. Frequency and severity are independent (Sauro 2014) [snippet]. A single rater's severity is unreliable (Nielsen 1992) [snippet]. | Fewer inflated P1/P2 findings on clean pages. `severity_min` recall for edge-condition defects may fall, which is intended. | H: gating cuts over-rating against the consensus by ≥ 30 % without lowering exact agreement. Metric: the UEM-04 severity metrics on heldout-2, which has `audience_relevance`. Pass: as stated. Data: heldout-2 plus the UEM-08 consensus. | S |
| UEM-08 | ADD | **Build severity ground truth from ≥ 3 independent raters** who do not see tool output. Humans are preferred; LLM judges count only if drawn from ≥ 2 model families. The consensus is the median, and inter-rater weighted κ is reported as the ceiling. A second author also reviews each seeded defect and records whether it is a real problem and at what severity. In the same study, score an LLM severity rater: keep rule-based severity if its κ is at least the LLM's. | The mean of 4 raters is within ±0.5 point 95 % of the time, and 3–4 raters are satisfactory (Nielsen 1992) [snippet]. The evaluator effect also covers severity (Hertzum & Jacobsen) [snippet]. 24–30 % critical-versus-minor splits (CUE-9) [snippet]. | Validates or refutes the P0–P3 rules. No direct effect on recall or noise. | H: tool-versus-consensus quadratic-weighted κ ≥ the lower 95 % bound of leave-one-rater-out κ. Pass: as stated; otherwise revise the failing rule family. Data: 3 raters × about 40 defects or units. | M |
| UEM-09 | ADD | **Measure reliability.** Re-record each suite 3 times at one commit and compute per-check any-two agreement over units. Checks below 0.8 (policy) are marked `unstable` and capped at P3 until fixed. For the agent layer, report any-two agreement across agents for each scenario. | Any-two agreement is the evaluator-effect metric, and reliability is a criterion for judging methods (Hertzum & Jacobsen; Hartson et al.; Sears) [snippet]. | Noise falls as flaky findings from timing and animation are removed. Recall stays stable. | H: timing-dependent checks (CG-03, GZ-02, frame-sampled GM-04) agree less than geometry checks. Pass: every check allowed at P1/P2 has any-two ≥ 0.8. Data: 3 re-recordings × 4 suites, about 0.5–1 h of recording [derived from 183 s per held-out suite]. | S |
| UEM-10 | CHANGE | **Tighten benchmark matching and pre-register.** (a) Viewport-level findings match only page-level keys, and decoy scoring treats them the same way. (b) True positives come from strict matches only (UEM-04). (c) A second, independent matcher checks a 25 % sample, and κ is reported. (d) Metrics and pass rules for heldout-2 are fixed in `docs/validation/experiments/` before scoring. | Matching determines overlap and may be unreliable (Hornbæk & Frøkjær 2008) [snippet]. Small design features of method-comparison experiments undermine their conclusions (Gray & Salzman 1998) [snippet]. The held-out suite had 0 viewport findings; the game suites may be affected [derived]. | Recall may fall slightly on game suites. Credibility rises. | H: exact matching changes recall by ≤ 0.05 on each suite. Metric: recall with and without the wildcard; matcher κ. Pass: report both, with exact matching as the headline; κ ≥ 0.8 (policy), otherwise fix the key selectors. Data: existing. | S |
| UEM-11 | KEEP (tighten) | **Agents from the same model count as one rater.** Judgment findings rise above P3 only after corroboration. Tighten the rule: the corroborator must differ in model family or input channel, not only in seed. Report any-two agreement among agents for each scenario. | Any-two agreement of 5–65 % over 11 studies (Hertzum & Jacobsen) [snippet]. 75 % and 60 % of problems came from a single team (CUE-2, CUE-4) [snippet]. LLM heuristic evaluation hallucinates problems (GPT-4o study) [snippet]. | Judgment noise falls, at a small recall cost. | H: P(real given corroborated) − P(real given not corroborated) ≥ 0.15 among adjudicated judgment units. Pass: as stated; otherwise corroboration adds cost without validity. Data: ≥ 60 adjudicated judgment units. | S |
| UEM-12 | KEEP | **Keep stratified coverage in preference to base-rate sampling.** | For problems confined to a condition, random sampling needs 53 users at p = 0.03 against 5 at p = 0.31 [derived, from the Nielsen & Landauer model, snippet]. On the held-out suite the swarm gained 9 defects over the default personas and lost none; McNemar p = 0.0039 [derived]. | Preserves the swarm's recall gain. | H: at equal n, stratified recall ≥ the mean recall of random sampling (harness experiment E4). Pass: holds on every suite. Data: existing. | S |
| UEM-13 | CHANGE | **Structure judgment notes as the cognitive-walkthrough questions** (§2.4) at each step: `cw.goal`, `cw.notice`, `cw.associate`, `cw.progress`, each yes/no/unsure with a snapshot ID. A judgment unit needs at least one "no" with evidence. This replaces free-text `confusion: true`. | The four cognitive-walkthrough questions (Wharton et al. 1994) [snippet]. The more structured heuristic walkthrough found more problems than a cognitive walkthrough and had fewer false positives than heuristic evaluation (Sears 1997) [snippet]. Structured reports ease merging (Cockton & Woolrych 2001) [snippet]. | Fewer judgment false alarms; better matching; learnability defects become traceable. | H: false alarms per clean scenario fall by ≥ 30 %, and recall of `agent_judgment` defects falls by no more than 1. Data: 2 arms × 6 agent runs per heldout-2 scenario. | S–M |
| UEM-14 | CHANGE | **Split validity in two.** `validity_conformance` asks whether the check applied its rule correctly; judges decide it from the rule text and the screenshot. `validity_predictive` asks whether users in that condition actually have the problem; only user observation decides it. The LLM-judge adjudication in `validation-and-limits.md` measures conformance only. Only predictive validity may support statements such as "users would …". Use ≥ 3 judges from ≥ 2 model families and report κ. | Definitions of a "real" problem (Hartson et al. 2001) [snippet]. Without user data, expert-review false alarms could be neither proven nor ruled out (CUE-4) [snippet]. The DR-AR model checks predictions against problems seen in user tests (Cockton & Woolrych 2001) [snippet]. | Prevents over-claiming. No effect on recall or noise. | The definition needs no experiment; UEM-17 measures predictive validity. | S |
| UEM-15 | ADD | **Measure downstream utility.** Add `disposition` to each unit in the bundle: `fixed`, `accepted`, `wont_fix`, `duplicate`, `not_a_problem` or `needs_research`. Impact ratio = (fixed + accepted) / reviewed, per check family and basis. A family below 0.2 after ≥ 30 reviewed units is demoted to hypotheses (policy). | Impact ratio (Sawyer, Flanders & Wixon 1996); persuasive power (John & Marks 1997); downstream utility and the developer effect (Law 2006); designers weigh more than severity (Hertzum 2006) [snippet]. | This is the only field measure of usefulness. Noise falls over time. | H: measured P1–P2 findings have an impact ratio ≥ 0.5 and model P3 findings < 0.2. Pass: demote families below 0.2. Data: 2 real products whose teams review ≥ 30 units each. | M |
| UEM-16 | CUT (conditional) | **Remove strata that never find anything unique.** Drop stratum s from the default swarm when harness experiments E3/E3b show 0 unique strict detections across all suites and removal lowers clean units. Never drop strata that the audience research marks primary. Make `first_use` agent-only, because no deterministic check reads it. | Marginal-gain logic of discovery curves (Nielsen & Landauer; Faulkner) [snippet]; code audit [derived]. | Noise falls modestly. Recall unchanged. | Pass rule: as stated, per suite. Data: existing harness output. | S |
| UEM-17 | ADD | **Run a predictive-validity study sized per condition cell.** Use non-directed think-aloud tests on 2 products. Recruit 5 users per audience-relevant cell (for example one-hand right or left × presbyopic or not, plus deutan). Extend a cell to 10 ± 2 users when the Lewis-adjusted p̂ < 0.25 (policy). Report completion with adjusted-Wald CIs. Match the problems users show to swarm units, per check family. | Nielsen & Landauer; Lewis 2001; Faulkner 2003; Hwang & Salvendy 2010; Schmettow 2012 [snippet]. Non-directed think-aloud is non-reactive (r = −0.03, about 3,500 participants), but prompts for explanation are reactive (Fox et al. 2011) [snippet]. Adjusted-Wald intervals for small n (Sauro & Lewis) [snippet]. | The first external estimate of thoroughness and validity. It may cut whole model families. | H: predictive validity ≥ 0.6 for measured families and ≥ 0.3 for model families (policy). Pass: families below 0.3 are demoted to hypotheses. Data: about 25–60 participants (5 cells × 5–12) [derived]. | L |
| UEM-18 | ADD | **Add an information-scent check in the style of CWW.** Compute Korean sentence-embedding similarity between the scenario goal text and the visible link and heading labels at each step. Flag the step when the correct target is not the highest-scent candidate, or when a competitor is within 0.05 cosine (policy). Basis `model`; at most P3 until calibrated. | CWW uses LSA scent between goal statements and link texts to predict navigation problems (Blackmon et al. 2002, 2005) [snippet]. `gaze-visual-attention.md` lists CWW as UNCONFIRMED. | Recall rises for navigation and label defects, which today only the judgment layer can find. Moderate noise risk. | H: flags ≥ 50 % of seeded navigation-label defects with ≤ 1 false alarm per clean scenario. Data: heldout-2 navigation defects (category `heuristic`). | M |
| UEM-19 | CUT | **Remove post-run agent interviews from the default workflow**; keep them opt-in. | Protocol §6 already bars interviews as evidence. Explanation-type reports are the reactive kind in human research (Fox et al. 2011) [snippet]. That LLM post-hoc rationales are not evidence of process is [opinion]. | Cost falls. Recall and noise unchanged. | H: interviews change no finding decision. Metric: decisions changed over the next 10 agent runs. Pass (cut): 0 changes. | S |
| UEM-20 | ADD (test) | **Test whether the pre-action note makes agents react.** Run agents with and without the `intent`/`expected` note before each action. | In humans, directed or explanatory verbalization is reactive and non-directed think-aloud is not (Fox et al. 2011) [snippet]. The LLM analogy is [opinion]. | Judgment recall could rise if the note makes agents unrealistically careful. | H: without the note, agents hit seeded confusion points more often (at least 1 more `agent_judgment` defect) with no rise in false alarms. Data: 2 arms × 6 runs per heldout-2 scenario. | S |

### 3.1 Metric card

**Benchmarks** (`docs/validation/*.json`, per mode):

- `units`: problem units after UEM-02. A defect is detected when a unit has
  the same category, an instance that matches the selector exactly (no
  wildcard), and a triggered cell that satisfies `profile_condition`.
- `thoroughness_strict` = detected / defects, with a Wilson 95 % CI.
  `thoroughness_weighted` uses weights P0 = 8, P1 = 4, P2 = 2, P3 = 1
  (policy).
- `validity_lb` = matched units / (matched + clean-control + decoy units).
  Unlabelled units are reported separately.
- `validity_adj` = (matched + r̂ × (unlabelled + clean)) / all units. r̂ is
  the adjudicated-real (conformance) rate from a stratified sample of ≥ 30
  units per basis, with a Wilson CI.
- `effectiveness` = thoroughness × validity, reported for both validity
  values.
- `false_alarms_per_clean_scenario` for each of P0–P3. Gate: P0 + P1 = 0.
- `decoy_false_alarm_rate`, with a Wilson CI. Held-out: 2/6, CI 0.10–0.70
  [derived].
- `severity`: exact agreement, within one level, over-rating rate and
  under-rating rate, each against the ≥ 3-rater consensus (UEM-08), plus
  quadratic-weighted κ.
- `reliability_any_two` = mean over run pairs of #(Ui ∩ Uj) / #(Ui ∪ Uj),
  over ≥ 3 re-recordings.
- `marginal`: for each check family and each stratum, from leave-one-out:
  Δ detected, Δ clean units, and clean units per unique detection. The
  held-out analogue of the last figure is 4.3 for the profile expansion and
  12.0 for the model checks (§2.7).
- `cost`: recording seconds, analysis seconds, agent tokens and reviewer
  minutes per valid unit.

**Product runs** (no answer key):

- Units by basis × severity; hypotheses counted separately.
- `combinatorial_coverage` {t1, t2} over audience-relevant values, with the
  untested cells listed.
- Agent layer: m, S_obs, Q1, Q2, Chao2, jackknife-1, Good–Turing coverage,
  any-two agreement, `stop_reason`.
- After review: dispositions and impact ratio.
- Never a "% of problems found" for the deterministic layer. For the agent
  layer, only "estimated completeness (lower bound)", with its assumptions
  stated. This extends "coverage, not prevalence" to "coverage, not
  completeness".

### 3.2 Swarm-size procedure

1. **Deterministic layer.** Enumerate the grid, or use a t = 2 covering array
   with adaptive refinement. From each failing cell, move one attribute at a
   time back to baseline. The smallest set of non-baseline values that still
   fails is the minimal failure-inducing condition, and it goes into
   `profile_specific`. "Swarm size" here is the number of cells, a
   computational cost, not a sample size.
2. **Agent layer.** Start with 4 heterogeneous agents, add them in pairs and
   stop as in UEM-06. The formulas below are from memory; verify them against
   Chao (1987), Burnham & Overton (1978) and Lewis (2001) before coding.
   - Chao2: Ŝ = S_obs + ((m − 1)/m)·Q1²/(2·Q2). When Q2 = 0, use
     S_obs + ((m − 1)/m)·Q1·(Q1 − 1)/2.
   - Jackknife-1 (incidence): Ŝ = S_obs + Q1·(m − 1)/m.
   - Good–Turing coverage: Ĉ ≈ 1 − Q1/U, where U is the total number of
     (agent, unit) detections.
   - Lewis adjustment: p_adj = ½·(p̂ − 1/m)(1 − 1/m) + ½·p̂/(1 + Q1/S_obs).
     Geometric total: N̂ = S_obs / (1 − (1 − p_adj)^m).
   - When agents share a model family, positive dependence biases every
     estimate downward. Label the results as lower bounds.
3. **Real-user validation.** Use 5 users per cell, estimate p̂, apply Lewis's
   adjustment, and extend while 1 − (1 − p_adj)^n < 0.85, up to 12 per cell
   (UEM-17).

### 3.3 Severity procedure

- Keep the rule-based severity per cell. It is perfectly repeatable, whereas
  single human or LLM raters are not (§2.5). Validate it against a ≥ 3-rater
  consensus (UEM-08).
- The headline severity comes from audience-relevant cells, and the worst
  case is reported separately (UEM-07). Coverage and frequency never raise
  severity, following Sauro 2014. The declared persistence rule for repeated
  exposure is a separate question, answered in `ux-design-discipline.md`
  §2.3.
- The benchmark's severity check becomes two-sided (UEM-04), so over-rating
  is visible and not rewarded.

---

## 4. Risks, open questions and what could not be verified

**Not verified** (all web evidence is excerpt-level):
- Exact wording and algebra of Lewis 2001's adjusted p, Hartson et al.'s
  validity and effectiveness formulas, the any-two agreement formula, and the
  Chao2, jackknife and Good–Turing estimators. All were written from memory.
- Lewis 1994's findings, Nielsen 1992's 22 %, 41 % and 60 % figures, Gray &
  Salzman's validity typology, and Hertzum & Jacobsen's specific
  recommendations.
- The SUS 68 and SEQ norms, and whether think-aloud lengthens task time.
- The 3- and 5-evaluator heuristic-evaluation percentages, which may come
  from secondary summaries.
- Kuhn et al.'s ranges, which may include later NIST data sets.
- CUE figures, which came through summaries (the 2018 interactions article,
  molich.dk).

**Conceptual risks.**
- Capture–recapture assumes a closed population and independent detectors.
  LLM agents from one model violate independence, which biases estimates
  down. Agents that follow different paths also violate the closed-population
  assumption, because they reach different screens. That is why UEM-06
  counts screens or states reached as a quantity to estimate, and not only
  problems.
- The deterministic layer is not a sampling process. Applying
  1 − (1 − p)^n or Chao2 to it would be a category error; use enumeration.
- A full grid (UEM-05) without UEM-01, 02, 03 and 07 would multiply findings
  and push the max-rule severity to the worst corner of the grid. Ship those
  first.
- Demotion (UEM-03) can hide real P3 defects. The pass rule limits the
  recall loss, but a product team may still want P3 hypotheses for some
  audiences, such as older-adult services. Keep `hypotheses[]` one click
  away.

**Validity of the current numbers** (Gray & Salzman-style threats, my
assessment [opinion]):
- 20 held-out defects give a recall CI of 0.58–0.92.
- Development suites were tuned post hoc, and blindness was breached, as
  disclosed in `validation-and-limits.md`.
- Seeded defects were written from the same literature as the checks
  (construct validity).
- The pages are synthetic (external validity).
- `precision_labeled` is not strictly a lower bound. Clean-control findings
  may be real, which makes it conservative, but lenient and duplicate matches
  counted as true positives inflate it (§2.7).

**Open questions.**
- What counts as a "real" problem for model-based ergonomic findings, such as
  small text for presbyopic profiles, before Korean calibration data exist?
  Conformance and predictive validity (UEM-14) may diverge a lot.
- Do LLM agents' detection probabilities behave like human evaluators'
  (heterogeneous p, low any-two agreement)? Does 10 ± 2 transfer? Only
  UEM-06's data can say.
- How should edge conditions with high stakes, for example tremor on a
  payment confirmation, be weighted against audience-relevance gating in
  UEM-07? This needs a policy decision, not literature.
- Does the unit key of UEM-02 merge problems that a team would fix
  separately? Check it with reviewers in UEM-02's experiment.

**Audit caveat.** The findings in §2.7 come from the frozen held-out outputs
at detector `8c1de02`. Later commits may already differ. UEM-01 is the only
item that looks like a defect in current behaviour, not a research proposal.
Confirm it on HEAD before fixing it.
