# Software testing foundations for persona-driven UX QA

Research brief for `skills/ergonomic-persona-swarm-qa`, written 2026-09-28 by a
research subagent (QA engineering, HCI, human factors). The only file written is
this one. No `benchmarks/*/answer_key.json` or `benchmarks/*/README.md` was
read. Repository numbers come from the files listed in §1.5.

**Tags.** **[standard]** normative text. **[standard†]** normative text that I
read only as quoted in a secondary source, which I read in full; it was not
checked against the purchased standard. **[paper]** peer-reviewed.
**[industry]** vendor or company docs, engineering book or blog. **[report]**
survey or government statistics. **[snippet]** seen only in a search excerpt,
not verified in the source. **[derived]** my computation, from repository files
or from cited numbers. **[opinion]** practitioner opinion; "my view" marks mine.

**In one paragraph.** In testing terms the swarm mixes three things. The
deterministic checks work as an executable checklist. The profiles are a
combinatorial test-input model. The persona agents are a crowd of exploratory
testers. Each of these has established controls, and the skill uses only some
of them:

- The checks have no false-positive budget. Findings are counted once per
  failure symptom, not once per defect.
- The profile plan is one-factor-at-a-time (base choice). For deterministic
  models it samples a space that could be enumerated exhaustively at CPU cost.
- The agents have goals and a step limit, but no charter, no named oracle and
  no stopping heuristics.
- Severity mixes impact, likelihood and confidence.

The fixes with the highest value are cheap:

- demote checks that have no unique recall but add noise;
- group findings into defect records;
- report a minimal triggering condition instead of "k/n profiles";
- split severity into impact, likelihood and confidence;
- charter the agent sessions.

---

## 1. Scope and sources searched

### 1.1 Questions

- How should persona-agent sessions be structured (charters, oracles, stopping rules)?
- How should profile conditions be covered (pairwise or t-way coverage vs stratified sampling)?
- How should findings be classified and prioritised?
- What do the skill's severity rules miss? What can be removed without losing anything?

### 1.2 Retrieval conditions (read before trusting the tags)

- I made 29 web searches.
- The session's egress proxy refused CONNECT (HTTP 403) to istqb.org,
  astqb.org, iso.org, ieee.org/ieeexplore, nist.gov (csrc, nvlpubs, tsapps),
  satisfice.com, developsense.com, arxiv.org, dl.acm.org, springer, researchgate,
  semanticscholar, wikipedia, bipm.org, govinfo.gov, IBM Cloud object storage,
  `*.github.io` and every university host I tried.
- Reachable hosts were `raw.githubusercontent.com`, `www.microsoft.com` and
  `developer.apple.com`. The ISTQB syllabi, ISO/IEEE standards and the
  practitioner blogs could therefore be seen only as search excerpts, which is
  why most claims are tagged [snippet].
- Eight sources were read in full (§1.3).

### 1.3 Read in full

- **S01** Barr, Harman, McMinn, Shahbaz, Yoo (2015). "The Oracle Problem in
  Software Testing: A Survey." *IEEE TSE* 41(5):507–525. Author-lab PDF:
  https://raw.githubusercontent.com/coinse/coinse-web-snapshot/main/publications/pdfs/Barr2015qd.pdf [paper]
- **S02** Lam, Godefroid, Nath, Santhiar, Thummalapenta (2019). "Root Causing
  Flaky Tests in a Large-Scale Industrial Setting." ISSTA '19.
  https://www.microsoft.com/en-us/research/wp-content/uploads/2019/11/LamETAL19RootFinder.pdf [paper]
- **S03** Winters, Manshreck, Wright (eds., 2020). *Software Engineering at
  Google*, ch. 20 "Static Analysis" (Tricorder). HTML source:
  https://raw.githubusercontent.com/abseil/abseil.github.io/master/resources/swe-book/html/ch20.html
  (published at https://abseil.io/resources/swe-book/html/ch20.html) [industry]
- **S04** Microsoft PICT documentation:
  https://raw.githubusercontent.com/microsoft/pict/main/doc/pict.md [industry]
- **S05** NIST combinatorial-testing-tools README:
  https://raw.githubusercontent.com/usnistgov/combinatorial-testing-tools/master/README.md [industry]
- **S06** arc42 Quality Model pages that quote ISO/IEC 25010:2023. Sources:
  https://raw.githubusercontent.com/arc42/quality.arc42.org-site/main/_articles/07-iso-25010-update-2023.md ,
  `.../_standards/iso/iso-25010.md` and `.../_qualities/{U,I,S,O,A,L,H}/*.md`
  (live site https://quality.arc42.org). [industry], quoting [standard†]
- **S07** Course notes that reproduce the ISO/IEC 25023 measure UEp-1-G:
  https://raw.githubusercontent.com/CristianoBerardo/Software_Design_and_Architecture/main/content/chapters/Software-Quality.tex [standard†]
- **S08** SAP fundamental-ngx wiki, "Exploratory Testing Tours" (descriptions of
  Whittaker's tours):
  https://raw.githubusercontent.com/wiki/SAP/fundamental-ngx/Exploratory-Testing-Tours.md [industry]

### 1.4 Seen only in search excerpts

- **S09** ISTQB CTFL v4.0 / v4.0.1 syllabus:
  https://istqb.org/istqb-releases-certified-tester-foundation-level-v4-0-ctfl/ ,
  https://astqb.org/assets/documents/ISTQB_CTFL_Syllabus_v4.0.1.pdf ,
  https://astqb.org/5-2-risk-management/
- **S10** ISTQB CTAL-TA v4.0 syllabus:
  https://istqb.org/wp-content/uploads/sdm-uploads/ISTQB-CTAL-TA-Syllabus-v4.0-EN-4.pdf ,
  https://trendig.com/en/blog/new-version-released-istqb-certified-tester-advanced-level-test-analyst-v4/
- **S11** ISTQB Glossary, "severity" and "priority":
  https://glossary.istqb.org/en_US/term/priority , https://istqb-glossary.page/severity/
- **S12** ISO/IEC 25023:2016 measure names and IDs:
  https://www.iso.org/standard/35747.html ; https://arxiv.org/pdf/2108.02921
- **S13** ISO/IEC/IEEE 29119-4:2021: https://www.iso.org/standard/79430.html ,
  https://ieeexplore.ieee.org/document/9591574
- **S14** Grindal, Offutt, Andler, "Combination testing strategies: a survey"
  (base choice):
  https://csrc.nist.gov/CSRC/media/Presentations/Combination-Testing-Strategies-A-Survery-July-20/images-media/grindal-offutt-andler.pdf
- **S15** Kuhn, Wallace, Gallo (2004), *IEEE TSE* 30(6), and NIST SP 800-142:
  https://csrc.nist.gov/pubs/journal/2004/06/software-fault-interactions-and-implications-for-s/final ,
  https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-142.pdf
- **S16** Nie & Leung (2011), "The minimal failure-causing schema of
  combinatorial testing," *ACM TOSEM* 20(4):15:1–15:38:
  https://dl.acm.org/doi/10.1145/2000799.2000801
- **S17** van Veenendaal, PRISMA:
  https://www.erikvanveenendaal.nl/NL/files/PRISMA%20white%20paper%201.4.pdf ,
  https://www.erikvanveenendaal.nl/site/wp-content/uploads/Risk-Based-Testing-for-Agile-projects.pdf
- **S18** IEEE Std 1044-2009, *Classification for Software Anomalies*:
  https://standards.ieee.org/ieee/1044/4607/
- **S19** Chillarege et al. (1992), "Orthogonal Defect Classification," *IEEE
  TSE* 18(11):943–956 (https://dl.acm.org/doi/10.1109/32.177364), and ODC v5.2
  (https://s3.us.cloud-object-storage.appdomain.cloud/res-files/70-ODC-5-2.pdf, blocked)
- **S20** Bolton, "FEW HICCUPPS" (2012):
  https://developsense.com/blog/2012/07/few-hiccupps
- **S21** Bolton, "When Do We Stop a Test?" (2009):
  https://developsense.com/blog/2009/09/when-do-we-stop-test
- **S22** J. Bach, "Session-Based Test Management" (2000):
  https://www.satisfice.com/download/session-based-test-management
- **S23** Hendrickson, *Explore It!* (2013), charter template; Hendrickson,
  Lyndsay & Emery, *Test Heuristics Cheat Sheet*:
  https://pragprog.com/titles/ehxta/explore-it/
- **S24** Whittaker, *Exploratory Software Testing* (2009), tours:
  https://www.informit.com/store/exploratory-software-testing-tips-tricks-tours-and-9780321636416
- **S25** Bach, Heuristic Test Strategy Model (SFDIPOT):
  https://www.developsense.com/resource/htsm.pdf
- **S26** Chen, Cheung, Yiu (1998), HKUST-CS98-01; Segura, Fraser, Sanchez,
  Ruiz-Cortés (2016), *IEEE TSE* 42(9):805–824:
  https://eprints.whiterose.ac.uk/id/eprint/110335/1/segura16-tse.pdf
- **S27** Itkonen, Mäntylä, Lassenius (2007), ESEM; Afzal et al. (2015), *EMSE*
  20:844–878: https://link.springer.com/article/10.1007/s10664-014-9301-4
- **S28** Andrews, Briand, Labiche (2005), ICSE, pp. 402–411; Just et al.
  (2014), FSE, pp. 654–665:
  https://homes.cs.washington.edu/~rjust/publ/mutants_real_faults_fse_2014.pdf
- **S29** Sadowski et al., Tricorder (ICSE 2015) and "Lessons from Building
  Static Analysis Tools at Google" (CACM 2018):
  https://research.google.com/pubs/archive/43322.pdf ; https://dl.acm.org/doi/10.1145/3188720
- **S30** JCGM 106:2012, *Evaluation of measurement data — The role of
  measurement uncertainty in conformity assessment*:
  https://www.bipm.org/documents/20126/2071204/JCGM_106_2012_E.pdf

### 1.5 Repository context read (not modified)

- `skills/ergonomic-persona-swarm-qa/SKILL.md`,
  `references/human-factors-checks.md`, `references/persona-agent-protocol.md`,
  `references/report-template.md`.
- `docs/ergonomic-swarm-spec.md` §0, §2, §4–§7, §12 and the new §13
  (`ergo-audience.v1`).
- `docs/validation/heldout-mixed-frozen-8c1de02.json`, top-level summary only.
- `docs/validation/experiments/ablation-dev-8707b70.json`, aggregated rows
  only: configs, per-check and per-category leave-one-out, model toggles, the
  discovery curve, and `severity_by_check` totals. Its 53 development defects
  include the former held-out suite. The file also has per-defect attribution
  rows derived from answer keys. Some were printed once while I inspected the
  file structure; none is used here.
- Code: `ergoqa/profiles.py` (`coverage_plan`), `ergoqa/swarm.py`
  (`aggregate`), `ergoqa/checks.py` (profile attributes each check reads),
  `ergoqa/bench.py` (`score`).
- `skills/persona-driven-ux-qa/references/evidence-and-severity.md` and
  `docs/human-factors/ux-design-discipline.md` §2.3 (severity mapping).
- A sibling brief, `docs/qa-discipline/usability-evaluation-methods.md`, covers
  evaluator effects and the reliability of severity ratings. This brief does not
  repeat them.

---

## 2. Key knowledge

### 2.1 ISTQB CTFL 4.0 and CTAL Test Analyst 4.0

**CTFL**

- CTFL v4.0 was released 2023-04-21, and v4.0.1 (errata) on 2024-09-15 [snippet S09].
- **Error guessing:** the tester creates "a list of possible errors, defects and
  failures" and designs tests to expose them. The lists come from "experience,
  defect and failure data, or from common knowledge about why software fails"
  [snippet S09].
- **Checklist-based testing:** "Checklist items are often phrased in the form of
  a question, and it should be possible to check each item separately and
  directly" [snippet S09].
- **Risk:** risk level is "determined by likelihood and impact" (learning
  objective FL-5.2.1). Product risk analysis focuses test effort so that
  residual risk is minimised (FL-5.2.3) [snippet S09].
- CTFL 4.0 names principles "Tests wear out" and "Absence-of-defects fallacy".
  I saw these names only in GitHub study notes that quote the syllabus
  [snippet].

**CTAL-TA**

- CTAL-TA v4.0 was released 2025-05-02, with 20.25 h of instruction [snippet S10].
- Black-box techniques are organised as data-based, behaviour-based and
  rule-based [snippet S10].
- Domain testing extends equivalence partitioning and boundary value analysis to
  multi-parameter domains, with ON, OFF, IN and OUT points (simplified vs
  reliable domain coverage) [snippet S10].
- Combinatorial testing covers base choice and pairwise coverage. Random testing
  may be guided or unguided [snippet S10].
- New in v4.0: metamorphic testing, crowd testing and CRUD testing. The syllabus
  also covers session-based testing and test charters [snippet S10].

**Glossary**

- Severity: "The degree of impact that a defect has on the development or
  operation of a component or system" [snippet S11].
- Priority: "The level of (business) importance assigned to an item, e.g.,
  defect" [snippet S11].

**My view [opinion]:**

- The deterministic checks are checklist-based testing with executable items.
- The LLM persona swarm is crowd testing plus exploratory testing.
- The benchmark's seeded defects are an error-guessing list.
- The profile model is a classification tree that feeds combinatorial selection.

### 2.2 ISO/IEC 25010:2023 and ISO/IEC 25023 measures

**What changed in 2023.** ISO's summary, as quoted by arc42:

> "Inclusivity and self-descriptiveness, resistance, and scalability have been
> added as subcharacteristics of interaction capability, security, and
> flexibility respectively. User interface aesthetics and maturity have been
> replaced with user engagement and faultlessness respectively. Accessibility
> has been split into inclusivity and user assistance." [standard† S06]

"Usability" was renamed "interaction capability", "portability" became
"flexibility", and **safety** was added as a ninth characteristic [standard† S06].

**Interaction capability** is "the degree to which a product or system can be
operated by specified users to achieve specified goals with effectiveness,
efficiency and satisfaction in a specified context of use." Its
sub-characteristics are appropriateness recognisability, learnability,
operability, user error protection, user engagement, inclusivity, user
assistance and self-descriptiveness [standard† S06].

**Sub-characteristic definitions** (2023 wording, "Capability of a product to …")
[standard† S06]:

- **User error protection:** "protect users against making operation errors".
- **Inclusivity:** "be utilised by people of various backgrounds". The long form
  lists "ages, abilities, cultures, ethnicities, languages, genders, economic
  situations, etc."
- **User assistance:** "be used by people with the widest range of
  characteristics and capabilities to achieve specified goals in a specified
  context of use".
- **Self-descriptiveness:** "present appropriate information, where needed by
  the user, to make its capabilities and use immediately obvious to the user
  without excessive interactions with a product or other resources".
- **Operability:** "have facilities and attributes that make it easy to operate
  and control".
- **Learnability:** "have specified users learn to use specified product
  functions within a specified amount of time".
- **Safety** has these sub-characteristics: operational constraint, risk
  identification, fail safe, hazard warning and safe integration. Hazard warning
  means "provide warnings of unacceptable risks … so that they can react in
  sufficient time".

**ISO/IEC 25023:2016 measures** [snippet S12]:

- User error protection: *Avoidance of user operation error* (UEp-1-G), *User
  entry error correction* (UEp-2-S), *User error recoverability* (UEp-3-S).
- Operability: *Message clarity* (UOp-2-G), *Undo capability* (UOp-6-S),
  *Appearance consistency* (UOp-8-S).
- UEp-1-G asks "What portion of user actions and inputs are protected against
  causing any system malfunction?" Measure X = A/B, where A = actions and inputs
  protected and B = actions and inputs that could be protected. 0 ≤ X ≤ 1, and
  closer to 1 is better [standard† S07].

**How the check families map onto 25010:2023** [derived from the check catalog; my mapping]:

| Check family | Primary sub-characteristic | Secondary |
| --- | --- | --- |
| RH, PT-01/02/04, GM-02/05 (reach, target size, touch accuracy) | Operability | Inclusivity / user assistance (left hand, tremor, older adults) |
| PT-03, PT-06 (misfire into destructive neighbour) | User error protection | Safety (only if the action is irreversible) |
| GZ-01/03/04 (hierarchy, banner blindness) | Appropriateness recognisability | Self-descriptiveness |
| GZ-02, CG-03 (feedback noticing, latency) | Self-descriptiveness / operability | Performance efficiency (time behaviour) |
| PC-01/02/05, PC-03, PC-04, GM-01 (contrast, CVD, text angle) | Inclusivity / user assistance | — |
| CG-01, CG-02 (choice load, transient text) | Learnability / self-descriptiveness | User error protection (toasts that carry an action) |
| GM-03, GM-06 (reaction windows, mashing) | Inclusivity | Operability |
| GM-04 (flashing) | **Safety — hazard** | — |

**Gaps** [derived]:

- **Learnability.** `cognition.familiarity` is not read by any check.
- **User error protection beyond misfire.** Confirmation, undo and entry
  correction are judgment-only.
- **Self-descriptiveness of labels and icons.** Judgment-only.
- **User engagement.** Out of scope.
- **Safety beyond GM-04.** Not covered.

### 2.3 ISO/IEC/IEEE 29119-4 test design techniques

- The 2015 edition lists specification-based techniques including equivalence
  partitioning, the classification tree method, boundary value analysis, syntax
  testing and combinatorial test design techniques [snippet S13].
- The 2021 edition contains "a specification-based test case design technique
  based on generating test cases on the basis of existing test cases and
  metamorphic relations" [snippet S13].
- I could not see the full 2021 list, its coverage-measure clauses, or whether
  requirements-based testing was added (§4).

How each technique maps onto the swarm [opinion; my mapping]:

| Technique | Swarm analogue | State today |
| --- | --- | --- |
| Equivalence partitioning | Element roles (primary, destructive, path, other); attribute classes | Roles declared manually; good |
| Boundary value / domain testing (ON/OFF points) | Every threshold: 24 px, 4.5:1 and 3:1, 3 flashes/s, 4 s toast floor, 400 ms / 1 s / 10 s, 4.4 / 7 / 9.2 mm | Decoys exist, but boundary pairs are not systematic |
| Classification tree | Profile factors (grip, age, vision, motor, context, cognition, hand size) | Implicit in `profiles.py` |
| Combinatorial (each choice, base choice, pairwise) | Profile selection | Base choice only (§2.4) |
| Decision table | **The severity rules themselves** | No full decision-table test of the rules |
| State transition | Screens and states, including back, cancel and rotate | Not measured |
| Scenario / use case | Scenario steps; persona goals | Present |
| Random | `base_rate_sample` filler | Present, low value (§2.4) |
| Metamorphic | Meaning-preserving re-runs for judgment | Judgment only (§2.9) |
| Error guessing, checklists | UXD-01…24, dark-pattern list, seeded-defect ideas | Present in the judgment layer |

### 2.4 Combinatorial coverage: interaction rule, base choice, covering arrays

**What the literature says**

- **Interaction rule:** "Most failures are induced by single factor faults or by
  the joint combinatorial effect (interaction) of two factors, with
  progressively fewer failures induced by interactions between three or more
  factors" [snippet S15].
  - Medical devices: 66 % of failures were triggered by one variable value, and
    97 % by one or two [snippet S15].
  - The single-factor share ranges from 9 % to 67 % across studies [snippet S15].
  - No failure involving more than 6 variables has been observed; the maximum
    was 4 to 6 in the six studies cited [snippet S15].
  - If all faults involve at most t variables, testing all t-way combinations is
    "pseudo-exhaustive" [snippet S15].
- **Base choice** (Ammann & Offutt 1994, as described by Grindal, Offutt and
  Andler) [snippet S14]:
  - Build a base test from the most frequent value of each parameter.
  - Vary each non-base value once while the rest stay at base values.
  - This satisfies 1-wise coverage but does not guarantee pairwise coverage.
- **Minimal failure-causing schema (MFS):** the smallest set of factor values
  that triggers a failure. An m-MFS involves m factors (Nie & Leung 2011)
  [snippet S16].
- **PICT** [industry S04]:
  - Defaults: order 2 by default; `/o:1` "merely covers all values".
  - Options: seeding rows (`/e`), constraints and sub-models.
  - Constraints: violating rows cannot simply be deleted afterwards, because "an
    offending test case may cover other, possibly valid, pairs". Disallowed
    combinations must be removed during generation.
  - Sub-models give a group of parameters its own order. Doc example: about 10
    hardware configurations instead of about 40, but about 140 tests instead of
    about 60 at `/o:3`.
  - Negative testing uses one out-of-range value per test, "to prevent input
    masking".
  - Suite size varies by 5–10 % with the seed.
- **NIST tools** [industry S05]: Combinatorial Coverage Measurement measures an
  existing test set. Sequence covering arrays serve "event driven systems
  including GUIs". A Fault Identification tool narrows fault-triggering
  combinations. ACTS supports constraints and variable-strength arrays.

**What the repository does** [derived]:

- **Stratum design.** `coverage_plan` first fills 4 core grip strata per touch
  device, then 10 condition strata, each applied alone, then random base-rate
  filler. Condition strata set 2–4 attributes at once. For example,
  `presbyopia_60s` sets age 60s, presbyopia and a one-hand grip, so age and
  presbyopia cannot be told apart by construction.
- **Pair coverage.** With one device, 16 profiles and seed 7, the profiles cover
  all 21 single values (100 % 1-way) but only **62 % of 2-way value pairs**
  (119/191). No profile has two or more non-default conditions. Doubling to 32
  profiles reaches 65 %: random filler adds 3 points.
- **Dropped strata.** The example in `SKILL.md` (`--count 16 --devices
  galaxy-s24,iphone-15`) needs 18 stratum slots. `small_hand` and `large_hand`
  are **silently dropped**.
- **Covering-array sizes.** For the same 8 touch factors (grip 4, age band 3,
  CVD 3, tremor 2, mobility 2, lighting 2, familiarity 2, hand percentile 3;
  1,728 combinations exhaustive), a greedy covering array needs **15–16 rows for
  100 % pairs** (lower bound 12) and 47–50 rows for 3-way (lower bound 36).
  Adding the constraint walking ⇒ one-hand grip gives 15–16 and 47–50.
- **Attributes each check reads** (from `checks.py`):
  - **13 of the 26 automated checks read no profile attribute:** PT-01, PT-05,
    PT-06, PC-01, PC-02, CG-01, CG-03, GZ-01, GZ-03, GZ-04, GM-04, GM-05, GM-06.
  - The others read at most four attributes each:
    - reach: grip, thumb length, orientation;
    - PT-02: grip;
    - PT-03/04: the σ multiplier from grip, tremor, mobility and age;
    - GZ-02: 70s+, acuity, time pressure, grip;
    - PC-03: CVD type and severity;
    - PC-04/GM-01: age, presbyopia or acuity, viewing distance;
    - PC-05: lighting;
    - CG-02: age;
    - GM-03: reaction time.
  - `context.free_hands`, `context.interruptions` and `cognition.familiarity`
    are read by no check.
- **Analysis cost.** Analysis runs after the recording (`--cross-profile`).
  Evaluating more profiles on a recorded run costs CPU only.
- **Dev ablation** (`ablation-dev-8707b70.json`, 53 defects):
  - The stratified pool reaches strict recall 0.906 at 14 profiles per device
    and then plateaus. A random pool needs 40 per device to reach 0.908.
  - `pool_defects_needing_combined_profiles` is empty. No dev defect was found
    to need a profile that combines conditions. The pool itself varies one
    facet at a time, and the answer-key contract's example conditions are
    single-attribute (spec §12). The suites as built therefore cannot show a
    benefit or a cost from t-way coverage.

**Consequence [opinion; my view].** For **deterministic** checks, sampling
profiles is the wrong technique. Each check depends on at most about four
attributes. Its causal sub-space (at most 48 combinations) can be enumerated
**pseudo-exhaustively** and the MFS reported. Sampling matters only where runs
are expensive and behaviour depends on the profile: interactive persona agents,
and device or orientation recordings. There, keep base choice for clean
attribution, as PICT's masking rule suggests, and add a small pairwise array to
cover interactions.

### 2.5 Risk-based testing (ISTQB, PRISMA)

- ISTQB: risk level is determined by likelihood × impact [snippet S09].
- PRISMA uses a product risk matrix [snippet S17]:
  - Impact on the horizontal axis and likelihood on the vertical, split into
    four quadrants I–IV.
  - Business (impact) factors: critical functionality, visible areas, most-used
    areas.
  - Technical (likelihood) factors: complexity, new development (re-use),
    interrelations (interfaces), size, technology and team (in)experience.
  - Component and integration testing focus on quadrants I and II;
    system and acceptance testing on I and IV.
  - I infer the numbering: I = high/high, II = high likelihood/low impact, IV =
    low likelihood/high impact. The excerpts did not state it explicitly.
- The new audience contract already has the inputs for such a matrix
  (spec §13) [derived]:
  - `tasks[].criticality` ∈ safety | health | money | legal | data | access |
    convenience;
  - `tasks[].frequency`;
  - segment `priority` and `share`;
  - condition `stakes: high`.

### 2.6 Severity vs priority; anomaly classification (IEEE 1044, ODC)

**Definitions and standards**

- **ISTQB** separates severity (impact) from priority (importance to fix)
  (§2.1) [snippet S11].
- **IEEE 1044-2009** [snippet S18]:
  - Purpose: a common vocabulary and "a common set of attributes" for defect and
    failure data. The data serve causal analysis, project management and process
    improvement.
  - Defect *Type* ∈ {Data, Interface, Logic, Description, Syntax, Standards,
    Other}.
  - Defect *Mode* ∈ {Wrong, Missing, Extra}.
  - I recall that the standard classifies defects and failures in separate
    attribute sets, each with its own severity, and adds priority and
    probability on the defect. I could not verify the full attribute list (§4).
- **ODC** (Chillarege et al. 1992, *IEEE TSE* 18(11):943–956) extracts process
  "signatures" from defect semantics using eight defect-type categories
  [snippet S19]. In ODC v5.2 [snippet S19]:
  - *Trigger* is "the environment or condition that had to exist to expose the
    defect".
  - *Qualifier* records a missing, wrong or irrelevant (extraneous)
    implementation.
  - *Impact* is the perceived or actual effect on the customer.
  - Activity, Trigger and Impact are recorded when a defect is opened; Target,
    Type, Qualifier, Age and Source when it is closed.

**What the repository does** [derived]:

- **Aggregation.** Findings are aggregated per (scenario, check, element), with
  severity = the worst observation (`swarm.aggregate`). One small button can
  therefore yield PT-01, PT-02 and PT-04 findings.
- **Unimplemented escalation.** Spec §7 raises severity one level (max P1) for
  primary or destructive elements on a critical path. `checks._escalate`
  implements this but **has no caller**.
- **Task outcome.** `run.success` appears only in the run table. A failed task
  is never a finding.
- **Severity capped by confidence.**
  `persona-driven-ux-qa/references/evidence-and-severity.md` says: "Severity
  describes user and product impact. Confidence describes how well the finding
  is supported. Do not use one as a substitute for the other." Yet the
  ergonomic skill caps severity by basis: a model alone is at most P2, reach
  alone at most P2, and unreplicated judgment at most P3.
- **Under-rating.** The dev ablation's `severity_by_check` table covers 56
  defect–check pairs. **5 of them were rated below the key's minimum
  severity**, one each from PC-04, RH-01, GZ-02, PC-03 and GZ-03, all
  model-basis checks.
- **One-sided scoring.** `bench.score` accepts any **over**-rating as
  "severity_ok". The answer-key contract has only `severity_min`.
- **Unused severity factors.** `ux-design-discipline.md` §2.3 says persistence
  and high-stakes paths should raise severity. Neither is implemented as a
  general rule; only some per-check rules use element roles.

### 2.7 Test oracles

From Barr et al. 2015 [paper S01]:

- **The oracle problem:** "Given an input for a system, the challenge of
  distinguishing the corresponding desired, correct behaviour from potentially
  incorrect behavior."
- **Four categories** of literature: specified oracles (317 papers), derived
  (245), implicit (76), and no automatable oracle (56).
- **Probabilistic oracle.** "A probabilistic test oracle … maps a test activity
  sequence into the interval [0, 1]" (Definition 2.5). Soundness and
  completeness are defined against a conceptual ground-truth oracle G.
- **Derived oracles** include:
  - pseudo-oracles and N-version programming ("agreement among independent
    implementations");
  - metamorphic relations;
  - regression suites, which rest "on the implicit assumption that the previous
    version can serve as an oracle";
  - inferred models.
- **Implicit oracles** "are not universal. Behaviours abnormal for one system in
  one context may be normal for that system in a different context."
- **Human oracle cost** can be cut *quantitatively* ("fewer/shorter tests for the
  same coverage") or *qualitatively* ("the extent to which test cases … may be
  easily understood").
- **Crowdsourcing the oracle** was shown feasible, with "problems in presenting
  the test problem to the crowd such that it could be easily understood"
  (Pastore et al. 2013).

**FEW HICCUPPS** (Bach and Bolton) [snippet S20][opinion]:

- The letters stand for Familiar problems, Explainability, World, History,
  Image, Comparable products, Claims, User expectations, Product, Purpose,
  Standards and Statutes.
- "All oracles are heuristics." The set is meant for when specifications are
  missing or thin.

**Mapping to the skill** [opinion; my view]:

- **`measured`** is a *specified* oracle. It is sound for the standard (WCAG,
  platform minimums) but not for the user outcome.
- **`model`** is a *probabilistic derived* oracle. Its soundness is unknown
  until calibrated.
- **`judgment`** is a *human or crowd* oracle. Agents from one model are
  N-version programming with a common-mode failure, which is why the protocol's
  "one model = one vote" rule is correct.
- The consistency oracles (**P**roduct, **H**istory, **C**omparable) can be
  **automated**:
  - same role, same appearance across screens (ISO 25023 UOp-8-S);
  - same element across devices;
  - same screen across builds (regression oracle).

### 2.8 Exploratory testing, SBTM, charters, tours, stopping heuristics

**Sessions and charters**

- **SBTM** (J. Bach 2000) [snippet S22]:
  - A session is an "uninterrupted block of reviewable, chartered test effort".
  - A *session sheet* is produced that a third party can examine.
  - Metrics: sessions per area, and time split among testing, bug investigation
    and setup.
  - Debriefs follow **PROOF** (Past, Results, Obstacles, Outlook, Feelings).
  - Sessions run from 45 minutes to several hours.
- **Charter template** (Hendrickson): "Explore <target> With <resources> To
  discover <information>". Resources may include constraints or a time-box
  [snippet S23].
- **Cheat-sheet heuristics** include Never & Always; Zero, One, Many; and Some,
  None, All [snippet S23].
- **SFDIPOT:** Structure, Function, Data, Interfaces, Platform, Operations,
  Time. These are the product elements of Bach's Heuristic Test Strategy Model
  [snippet S25].

**Tours**

Whittaker's tours are grouped into districts [snippet S24]:

- Business: Guidebook, Money, Landmark, Intellectual, FedEx, After-Hours,
  Garbage Collector's.
- Tourist: Collector's, Lonely Businessman, Supermodel, TOGOF, Scottish Pub.
- Seedy: Saboteur, Antisocial, Obsessive-Compulsive, and others.
- Historical: Bad-Neighborhood, Museum, Prior Version.
- Entertainment: Supporting Actor, Back Alley, All-Nighter.
- Hotel: Rained-Out, Couch Potato.

The SAP wiki describes them as follows [industry S08]:

- **Supermodel** "tests only the UI and not the logic behind it".
- **Couch Potato** tests with "as little work as possible … ensure that the
  default cases are getting tested".
- **Rained-Out:** "use the cancel button A LOT".
- **Obsessive-Compulsive:** "Repeat every step … twice".
- **Saboteur:** remove or restrict resources and change the environment.
- **Antisocial:** "Always do the opposite … Use invalid inputs".
- **Landmark:** the main features "in different orders".
- **Back-alley:** rarely used features, "for example … first time" screens.
- **Lonely Businessman:** "Choose long paths over short paths".
- **FedEx:** "follow specific pieces of data through" the product.

**Stopping heuristics** (Bolton 2009) [snippet S21][opinion]:

- The list: Time's Up, Piñata, Dead Horse, Mission Accomplished, Mission
  Revoked, I Feel Stuck, Pause That Refreshes, Flatline, Customary Conclusion,
  No More Interesting Questions, and Avoidance/Indifference.
- **Piñata:** stop "when we see the first sufficiently dramatic problem".
- **Dead Horse:** "the program is too buggy to make further testing worthwhile".
- **Flatline:** "no matter what we do, we're getting the same result".
- **Pause That Refreshes:** a new *type* of error prompts looking for the same
  type elsewhere.

**Evidence and current protocol**

- Two controlled comparisons of exploratory and test-case-based testing exist:
  Itkonen et al. 2007 (ESEM), and Afzal et al. 2015 (four experiments, 24
  practitioners and 46 students) [snippet S27]. **I could not verify their
  results.**
- The current persona protocol stops on success, on the step limit (default
  25), after three consecutive `agent_limitation` notes, or before a side
  effect [derived]. It has no charter, tour, oracle field, flatline rule or
  session sheet.

### 2.9 Metamorphic testing

- Metamorphic testing originates in Chen, Cheung and Yiu 1998 (HKUST-CS98-01).
  The main survey is Segura et al. 2016, *IEEE TSE* 42(9):805–824 [snippet S26].
- Metamorphic relations act as *partial* derived oracles "built from known
  relationships between desired behaviour" [paper S01].
- 29119-4:2021 [snippet S13] and CTAL-TA v4.0 [snippet S10] include metamorphic
  testing.
- The repository already applies metamorphic re-runs to **judgment**:
  reworded copy, reordered elements, theme change, and marking a flipped verdict
  `unknown` [derived]. The deterministic checks have no metamorphic relations.
  Their left-hand mirroring, monotonicity and attribute independence are
  asserted but not tested this way.

### 2.10 Noise and flakiness in automated QA

**Google's false-positive budget** [industry S03, corroborated by snippet S29]:

- Tricorder requires new checks to "Produce less than 10% effective false
  positives — Developers should feel the check is pointing out an actual issue
  at least 90% of the time".
- A finding is an *effective* false positive "if developers did not take some
  positive action after seeing the issue".
- Users click "Not useful" or "Please fix". The team "will disable analyzers if
  they don't work to address problems and improve the 'not useful' rate".
- The overall effective false-positive rate is "just below 5%" across more than
  100 analyzers.

**Flaky tests** [paper S02]:

- Google (as cited): 1.5 % of test runs are flaky, and "almost 16% of 4.2 million
  individual tests fail independently of changes in code or tests". About
  2–16 % of the testing budget goes to reruns.
- Microsoft: 4.6 % of individual tests were flaky over one month in five
  projects. 86 % of flaky tests were flaky only in CI. Up to 52 % of builds in
  one project had flaky failures.

**This repository** [derived]:

- On the held-out suite the swarm's `precision_labeled` is **0.34**. By my
  reconstruction it is 53/156 (95 % Wilson 0.27–0.42). This is a lower bound,
  because clean-control findings may be real issues that were not seeded.
- On the dev ablation (53 defects, 213 clean-control findings in the swarm
  configuration):
  - **PC-04 alone accounts for 79 clean-control findings (37 %)** while
    contributing 3 unique defect detections.
  - GZ-01, PC-05, PT-02, GZ-04 and RH-02 contribute **zero unique detections**
    (leave-one-out Δrecall = 0) but 17, 17, 11, 7 and 1 clean-control findings.
    That is 53 in total, 25 %.
  - Turning off the declared touch multipliers leaves recall at 0.906 and
    removes 11 clean-control findings.
  - Disabling the gaze conspicuity map changes nothing (recall 0.906, clean +3).
  - PT-05 does not appear in the leave-one-out table.

### 2.11 Validity of benchmarks with seeded defects

**Seeded faults vs real faults** [snippet S28]:

- Andrews, Briand and Labiche (2005): mutants from a well-chosen operator set
  behave like real faults, whereas **hand-seeded faults "seem to be harder to
  detect than real faults"**.
- Just et al. (2014): mutant detection correlates with real-fault detection for
  **73 %** of real faults. **17 %** of real faults are not coupled to any mutant,
  and 10 % need new operators.

**Statistics of the current results** [derived]:

- Wilson 95 % intervals:
  - swarm strict recall 16/20: 0.58–0.92;
  - swarm lenient recall 18/20: 0.70–0.97;
  - single-profile recall 7/20: 0.18–0.57;
  - measured-only recall 3/20: 0.05–0.36;
  - dev swarm 0.906: 0.80–0.96 (from the ablation file).
- Estimating recall ±0.05 at p = 0.8 needs about 246 defects; ±0.10 needs about
  61.
- Swarm vs single on the same defects needs a paired test. If the 9
  "swarm-only" defects are strict detections and single-profile found none that
  the swarm missed, an exact McNemar test gives p ≈ 0.004.
- The held-out matches work out as 225 − 98 clean − 74 unlabeled = 53 findings
  for 16–18 detected defects, i.e. **about 3 findings per detected defect**.
- Marginal noise per extra detected defect:
  - held-out: single → swarm +39 clean findings for +9 defects (4.3 each);
    measured → swarm +87 for +13 (6.7 each);
  - dev: single → swarm +80 for +15 (5.3 each); measured → swarm +182 for +32
    (5.7 each).

### 2.12 Measurement uncertainty and decision rules

**JCGM 106:2012** [snippet S30]:

- It gives two kinds of decision rule: "simple acceptance (shared risk)" (§8.2)
  and **guard bands** (§8.3), which move the acceptance limits inward by a
  multiple of the expanded uncertainty.
- It names two risks: false accept (the consumer's risk) and false reject (the
  producer's risk).
- "Because of uncertainty in measurement, there is always the risk of
  incorrectly deciding whether or not an item conforms."

**Applied here [opinion; my view]:**

- A finding is a "reject" of a product element, so noise is false rejects.
- Model checks run on declared-assumption parameters. Examples: touch-σ
  multipliers one-hand 1.3, walking 1.4, tremor 1.5/2.25, 60s 1.15, 70s+ 1.3; the
  CV 0.2 reaction-time assumption; PC-04 visual-angle limits. Guarded rejection
  is the standard remedy for these.
- Measured WCAG conformance should still use the raw thresholds.

---

## 3. Implications for the skill

### 3.0 Short answers to the four questions

1. **Sessions.** Give every interactive persona run the following [opinion;
   evidence S20–S24]:
   - a charter: explore *target* with *profile and resources* to discover
     *information*;
   - a UX-mapped tour;
   - a step time-box set by risk;
   - a named oracle on every note (FEW HICCUPPS);
   - machine-checkable stopping rules (flatline, Piñata → reproduce, Dead Horse,
     mission accomplished);
   - an SBTM-style session sheet.

   Keep LLM agents off the tours that deterministic code already does
   (Supermodel, Garbage Collector).
2. **Coverage.** Stop sampling for deterministic checks:
   - Enumerate each check's causal attributes and report the minimal triggering
     condition (MFS).
   - Keep base choice (one facet at a time) for agent runs and add a small
     pairwise array, with seeding rows, constraints and a device sub-model.
   - The current suites contain no defect that needs a combination of
     conditions, so the benefit is unproven until heldout-2 seeds some.
3. **Classification and prioritisation.**
   - Group failures into defect records, keyed by element or style token and by
     root-cause family.
   - Classify each record by mode (missing, wrong, extra), ISO 25010:2023
     sub-characteristic and ODC-style trigger.
   - Prioritise by impact × likelihood (PRISMA), with confidence as a separate
     axis.
   - Keep a per-check false-positive ledger with a Tricorder-style budget.
4. **What the severity rules miss:**
   - consequence of the failure (a null tap versus an irreversible commit);
   - likelihood and exposure (persistence);
   - workarounds (`free_hands`);
   - the user's ability to notice a misfire;
   - task-level failure;
   - the difference between severity and priority.

   They also use confidence as a severity cap: all 5 under-rated dev
   defect–check pairs come from model-basis checks. The critical-path
   escalation rule is unimplemented, and the scorer never penalises
   over-rating.

### 3.1 Candidate changes

Effort: S ≤ 1 day, M ≤ 1 week, L > 1 week. "Dev" = the three development suites
in `ablation-dev-8707b70.json`. "heldout-2" = the new blind suite being authored.

| ID | Type | What exactly | Evidence | Expected effect on recall / noise / usefulness | Experiment that decides it (hypothesis, metric, pass rule, data needed) | Effort |
| --- | --- | --- | --- | --- | --- | --- |
| STF-01 | CUT | Demote to `advisory` (hidden from counts and default report; kept in verbose output and the bundle) the checks with **no unique detection and ≥ 5 clean-control findings**: GZ-01, GZ-04, PC-05. Stop emitting PT-02 as its own finding; it becomes one failure inside the pointing defect record (STF-03). Drop the *profile-only* touch-σ multiplier findings (PT-03/PT-04 raised only by the declared 1.3/1.4/1.5/2.25 multipliers). RH-02 also has no unique detection, but only 1 clean finding, so leave it. | Dev leave-one-out: Δrecall 0 for GZ-01, GZ-04, PC-05 and PT-02; Δclean −17/−7/−17/−11; multipliers off keeps recall 0.906, clean −11 [derived]. Tricorder < 10 % effective-FP rule [industry S03]. | Recall: 0 on dev (confirm on heldout-2). Noise: clean-control findings −25 to −30 % (up to 63/213 if additive). Usefulness: ↑. | **H:** the joint demotion loses no held-out defect. **Metric:** strict recall and clean-control findings on heldout-2, joint demotion vs current. **Pass:** strict recall drops by ≤ 1 defect, and clean findings fall ≥ 20 %. **Data:** heldout-2 and its clean controls (not yet seen by anyone tuning). | S |
| STF-02 | ADD | **Effective-false-positive ledger.** Each defect record gets `disposition` ∈ {confirmed, false_positive, not_useful, duplicate, wont_fix, unknown}, set by a new `ergo_qa.py triage` command. Per check, `effective_fp_rate` = (false_positive + not_useful) / adjudicated, over the last N ≥ 20. Above 10 %, the check is auto-demoted to advisory until fixed. Global target ≤ 10 % (Google reports about 5 %). Benchmark clean-control findings count as candidates until adjudicated. | Tricorder policy and "Not useful" loop [industry S03; snippet S29]. Held-out precision 0.34 [derived]. | Recall: risk only when a check is demoted (STF-01 gates it). Noise: ↓, and keeps falling as data accrue. Usefulness: ↑ trust. | **H:** most of the 98 held-out clean-control findings are not useful. **Metric:** per-check effective FP from two blind adjudicators. **Pass:** after the policy, overall effective FP ≤ 20 % on the next held-out run with strict recall ≥ 0.75. **Data:** adjudication of about 170 held-out and 213 dev clean or unlabeled findings. | M |
| STF-03 | CHANGE | **Defect records instead of per-check findings** (IEEE 1044 separates defect and failure). Key = (scenario, `screen_key`, root-cause family, target). Target is `element_key`, or for PC-01/PC-04 the computed style signature (font size, weight, fg/bg), so one CSS token is one defect. Families: size {PT-01, PT-02, PT-04, GM-05}; misfire {PT-03, PT-06}; reach {RH-01, RH-02, GM-02}; contrast {PC-01, PC-02, PC-05}; colour-only {PC-03}; text size {PC-04, GM-01}; timing {CG-02, GM-03}; feedback {GZ-02, CG-03}; hierarchy {GZ-01, GZ-03, GZ-04}; choice {CG-01}. Each record lists its failures (check, profiles, measurement). | IEEE 1044 purpose and attributes [snippet S18]. Quantitative human-oracle cost [paper S01]. About 3 matched findings per detected held-out defect; PC-04 is 37 % of dev clean findings [derived]. | Recall: unchanged (the scorer matches by element + category, and families stay inside one category). Noise: items to review ↓ ≥ 40 % (most for PC-04). Usefulness: ↑ (one fix per token or element). | **H:** grouping keeps recall and cuts review items. **Metric:** number of records on clean controls and defect variants; recall with a record-level matcher. **Pass:** strict recall identical, and clean-control items ↓ ≥ 40 %. **Data:** existing runs; re-aggregation only. | S |
| STF-04 | CHANGE | **Severity model split.** `impact`, I1–I4:<br>• **I4:** irreversible money, data, legal, consent or identity commitment; health hazard; or a critical task (criticality ∈ safety, health, money, legal, data, access) blocked with no workaround under the trigger.<br>• **I3:** a critical task blocked but with a workaround, or a non-critical task blocked; an error likely missed; information unreadable.<br>• **I2:** extra effort or recovered confusion.<br>• **I1:** cosmetic.<br>`likelihood`, L1–L3: measured deterministic failure or model P ≥ 10 % → L3; a standard violated with no outcome evidence, or P 3–10 % → L2; otherwise L1. Add +1 band if the element is on ≥ 3 path steps, or the task is daily.<br>`confidence`, C0–C3: measured → C3; calibrated model → C2; declared-assumption model or corroborated judgment → C1; single-rater judgment → C0.<br>`priority`, from a published decision table: P0 = I4 ∧ L ≥ 2 ∧ C ≥ 2; P1 = I4 otherwise, or I3 ∧ L3 ∧ C ≥ 2; P2 = I3 otherwise, or I2 ∧ L ≥ 2; P3 = the rest. C0 items are listed as hypotheses.<br>Workaround: RH-01 with `free_hands = 2` → impact −1.<br>A misfire whose result goes unnoticed (GZ-02) → impact +1.<br>Basis caps move from severity to priority. Legacy `severity` = `priority`.<br>Unit-test the table with full decision-table coverage. | ISTQB severity/priority and risk = likelihood × impact [snippet S09, S11]. IEEE 1044 keeps severity, priority and probability separate (partly verified) [snippet S18]. The sister skill's rule not to substitute confidence for severity; 5/56 dev defect–check pairs under-rated, all model-basis; escalation unimplemented [derived]. | Recall: 0. Noise: fewer high-priority items on clean pages, because low-likelihood and low-confidence items drop. Usefulness: ↑ triage; severity agreement ↑. | **H:** the split reproduces the benchmark's minimum severities with fewer under-ratings and no more P0/P1 on clean controls. **Metric:** under-ratings on 53 dev and all heldout-2 defects; P0/P1 on clean controls; weighted κ against blind adjudication of 60 stratified findings. **Pass:** under-ratings ≤ 1, clean P0/P1 not higher, κw ≥ 0.6. **Data:** benchmarks plus a 60-item adjudication set; audience `tasks[].criticality`. | M |
| STF-05 | CHANGE | **Two-sided severity scoring.** Benchmark authors add `severity_max` (or an exact level) to new answer keys, starting with heldout-2. `bench.score` reports exact agreement, the under-rating rate and the over-rating rate. | `severity_ok` accepts any over-rating [derived from `bench.py`]. | Measurement validity; no product change. | Instrument change, no hypothesis. **Pass:** implemented in `bench.py` and used on heldout-2. Only the blind benchmark authors edit keys (spec §12). | S |
| STF-06 | ADD | **Pseudo-exhaustive sweeps and MFS triggers for deterministic checks.** Each check declares `causal_attributes`. Examples: PT-04 = grip × tremor × mobility × age band (48 combinations); PC-03 = CVD type × severity; PC-04 = age × presbyopia/acuity × viewing distance; RH-01 = grip × hand percentile × orientation; CG-02 = age; GM-03 = reaction-time band; PC-05 = lighting. The analysis enumerates these on the recorded snapshots (CPU only) and writes `trigger` = the minimal failing attribute-value sets, e.g. `{grip: one_hand_left}` or `{motor.tremor: mild, context.mobility: walking}`. Report `condition_space_fraction` (share of enumerated combinations that fail, labelled "not prevalence") in place of `coverage_label` k/n for these checks. Only MFS inside the audience scope (STF-24) are shown by default. | Interaction rule; pseudo-exhaustive [snippet S15]. MFS [snippet S16]. Checks read at most 4 attributes; analysis runs after recording; strata confound age with presbyopia and grip; `_differential` returns {} when two different single attributes each trigger [derived]. | Recall: ↑ for defects triggered by a combination of conditions, and no longer depends on which 16 profiles were drawn. Noise: risk ↑ from stacked extremes, mitigated by audience scope and STF-01/04. Usefulness: ↑ (exact, minimal differential condition). | **H:** MFS reporting keeps every current detection and finds seeded 2-way defects. **Metric:** strict recall on heldout-2 including ≥ 6 seeded interaction defects (e.g. a target that fails only for tremor × walking, or text that fails only for presbyopia × bright sun); clean findings; trigger matches the key's `profile_condition`. **Pass:** single-condition recall ≥ current; ≥ 5/6 interaction defects; clean findings ≤ +10 %; trigger matches ≥ 90 %. **Data:** interaction defects in heldout-2 (benchmark authors). | M |
| STF-07 | CHANGE | **Profile plan for expensive, behaviour-dependent runs** (interactive agents, device and orientation recordings). Keep the base-choice layer: the segment's typical member plus one-facet variations, as `audience.compose` does. Add a 2-way covering array: PICT-style seeding rows = the base-choice rows; constraints (walking ⇒ one-hand grip; keyboard-only ⇒ pointer device); a device × orientation sub-model at order 1–2 to cap the number of recordings. Drop random base-rate filler in stratified mode. Fix the silent truncation: warn and record `unfilled_strata` when the count is below the plan (the SKILL.md example drops `small_hand` and `large_hand`). | Base choice is 1-wise only [snippet S14]. PICT seeding, constraints, sub-models and masking [industry S04]. Dev discovery curve: stratified 0.906 at 14/device vs random 0.908 at 40 [derived]. The 16-profile plan covers 62 % of pairs; 15–16 rows reach 100 % [derived]. | Recall: ↑ for interaction defects visible in agent behaviour. Noise: neutral if MFS attribution (STF-06) is applied. Usefulness: explicit pair coverage; no silently missing strata. | **H:** ≤ 6 extra covering-array rows per device find seeded interaction defects that base choice misses. **Metric:** interaction-defect recall; agent sessions used. **Pass:** ≥ +3 interaction defects with ≤ 40 % more sessions. **Data:** heldout-2 interaction defects plus agent runs. | M |
| STF-08 | CUT | **"k/n profiles" on profile-invariant checks.** 13 of 26 automated checks read no profile attribute (PT-01, PT-05, PT-06, PC-01, PC-02, CG-01, CG-03, GZ-01, GZ-03, GZ-04, GM-04, GM-05, GM-06). Evaluate them once per (device, snapshot) and label `profile_dependence: none`. | Code inspection [derived]. | Recall: 0. Noise: count unchanged. Usefulness: ↑ (removes pseudo-coverage); compute ↓. | **H:** same findings. **Metric:** set equality of (scenario, check, element, severity) before and after. **Pass:** equal. **Data:** existing runs. | S |
| STF-09 | CHANGE | **Coverage reporting in 29119 style.** Rename the finding label to "triggered in k of n evaluated profiles". Add a run-level coverage section: (a) t-way condition coverage, measured CCM-style (pairs covered / total); (b) screen-state and transition coverage, including back and cancel; (c) declared roles exercised; (d) check applicability, i.e. checks that could not run (no timing windows, no flash sampling, no hotspots). | NIST CCM tool [industry S05]. 29119-4 coverage items [snippet S13; details unverified]. | Usefulness: ↑ ("what was not tested" becomes explicit). No effect on recall or noise. | **H:** reviewers find untested areas faster. **Metric:** untested areas correctly named by 5 reviewers from report A vs B. **Pass:** ≥ 30 % more. **Data:** two report versions of the same run. | S |
| STF-10 | ADD | **Charters and tours for persona sessions** (`ergo-session.v1`). Fields: `charter` {explore, with, to_discover}, generated from audience tasks × risk quadrant; `tour` ∈ {money, landmark, couch_potato, rained_out, obsessive_compulsive, saboteur, antisocial, back_alley, fedex, guidebook, lonely_businessman}; `timebox_steps` by quadrant (I 30, II/IV 20, III 10); a session sheet with `steps_used`, `stop_reason`, on-charter vs opportunity steps, setup (environment) vs investigation (reproduction) steps, findings vs issues, and states/transitions visited; a PROOF debrief. LLM agents never run the Supermodel or Garbage-Collector tours. | SBTM [snippet S22]. Charter template [snippet S23]. Tours [snippet S24; industry S08]. | Recall: ↑ for flow and state defects that element checks cannot see (cancel traps, double submit, preselected consent, lost input on back, error recovery). Noise: neutral, ↓ with STF-11. Usefulness: ↑ (reviewable sessions). | **H:** chartered, toured sessions find more confirmed flow defects per 100 steps than goal-only sessions. **Metric:** confirmed distinct defects per 100 steps; transition coverage; `agent_limitation` rate. **Pass:** ≥ +30 % confirmed defects per 100 steps, `agent_limitation` rate up ≤ 5 points. **Data:** heldout-2 flow defects; runs with 2 agent models. | M |
| STF-11 | CHANGE | **A named oracle on every judgment note.** Add to `/note`: `oracle` ∈ {claims, user_expectation, product_consistency, comparable_product, history, image, purpose, standard_or_statute, familiar_problem, explainability, world}, and `oracle_ref` (the claim text, convention or clause, or the earlier screen). A note with no named oracle and no observable inconsistency becomes an `issue`, not a PJ finding. Rewrite UXD-01…24 as yes/no questions that can each be checked separately. | FEW HICCUPPS [snippet S20][opinion]. Human- and crowd-oracle cost [paper S01]. CTFL checklist guidance [snippet S09]. | Recall: small risk. Noise: ↓ PJ noise. Usefulness: ↑ (auditable). | **H:** notes with a named oracle have higher adjudicated precision. **Metric:** blind-adjudicated precision of PJ findings. **Pass:** +20 points or more, with ≤ 10 % loss of confirmed PJ findings. **Data:** interactive heldout-2 runs plus adjudication. | S |
| STF-12 | CHANGE | **Machine-checkable stopping rules.** New `stop_reason` values:<br>• `flatline`: 3 consecutive actions with no DOM or perceptual-hash change;<br>• `mission_accomplished`: success selector visible, or the charter question answered;<br>• `time_up`: timebox reached;<br>• `dead_horse`: ≥ 2 blocking `ux_issue` on the critical path, or ≥ 2 environment failures;<br>• `pinata`: first P0/P1 candidate — stop exploring and replay the minimal steps with a second model;<br>• `mission_revoked`: the side-effect guard fired.<br>Keep `stuck` (3 × `agent_limitation`). "Pause That Refreshes" spawns a follow-up charter for the same failure type on other screens. | Bolton [snippet S21][opinion]. Current rules [derived]. | Recall: neutral, ↑ via Pause That Refreshes. Noise: ↓ (fewer spent-agent notes). Usefulness: faster replication of severe issues. | **H:** fewer steps per confirmed defect. **Metric:** steps per confirmed defect; flow-defect recall. **Pass:** ≥ 25 % fewer steps with no recall loss. **Data:** the same runs as STF-10. | S |
| STF-13 | ADD | **Metamorphic self-tests for the deterministic checks** (CI):<br>• MR1, mirror: flip the snapshot horizontally and swap handedness → RH-01 and GZ-02 occlusion verdicts mirror.<br>• MR2, monotone size: target × 1.25 → P(miss) does not rise and no new PT finding appears.<br>• MR3, non-causal invariance: changing any attribute outside `causal_attributes` never changes a verdict.<br>• MR4, colour swap: swapping fg and bg gives the same contrast ratio.<br>• MR5, DOM reorder with identical rendering → identical measured findings.<br>• MR6: equal physical size on two devices → same PT-02 verdict. | Metamorphic testing [snippet S26]. Relations as partial oracles [paper S01]. In 29119-4:2021 [snippet S13] and CTAL-TA v4.0 [snippet S10]. | Recall: 0. Noise: ↓ (detector bugs caught). Usefulness: ↑ (trust in models). | **H:** the checks satisfy MR1–MR6. **Metric:** violations on fixture snapshots and property-based variations. **Pass:** 0 violations; each violation is triaged as a detector bug. **Data:** existing fixtures. | S–M |
| STF-14 | KEEP / extend | **Keep the meaning-preserving re-runs for judgment** (reworded copy, reordered elements, theme). Make them mandatory for any PJ above P3. Add a *persona-label swap* relation: same view, different label must not flip the verdict unless the rationale cites a profile-relevant cue. | Protocol §5 [derived]. Metamorphic testing [snippet S26]. | Noise: ↓ (label-driven verdicts removed). | **Metric:** flip rate under the relations. **Pass:** ≥ 95 % of flipped verdicts end as `unknown`. **Data:** interactive runs. | S |
| STF-15 | ADD | **Guard-banded decision rules.** Measured checks: estimate the expanded uncertainty U from pixel-sampled colours on gradients or images, catalogue display mm, 16 ms polling and ~30 fps flash sampling. A value within ±U of the limit is `marginal`: priority ≤ P3 and advisory. Model checks: re-evaluate at the favourable end of each declared-assumption parameter (multiplier 1.0, lower coefficient bound). Mark `robust` only if the check still fails. Keep raw thresholds for WCAG conformance statements. First target: PC-04. | JCGM 106 [snippet S30]. PC-04 = 37 % of dev clean findings; multipliers are declared assumptions [derived]. | Recall: risk for true boundary defects. Noise: ↓ at thresholds. Usefulness: ↑ (honest about marginal cases). | **H:** guard bands cut false rejects near thresholds. **Metric:** false rejects on OFF points and recall on ON points of boundary pairs. **Pass:** OFF-point false rejects ↓ ≥ 50 % with ON-point recall loss ≤ 5 points. **Data:** boundary pairs from STF-17. | M |
| STF-16 | ADD | **Flakiness policy for timing checks.** CG-03 latency, CG-02 visible duration, GM-03 windows and GM-04 frame sampling are measured 3 times per step. A timing finding needs ≥ 2 of 3 reproductions and reports the median and range; otherwise it is `flaky_suspect` (advisory). | Flaky-test data from Google and Microsoft [paper S02]. | Recall: ≈ 0. Noise: ↓ for timing checks. Cost: × 3 on timing steps only. | **H:** single-run timing verdicts are unstable. **Metric:** verdict agreement over 5 reruns of the timing scenarios. **Pass:** ≥ 95 % agreement after the 2-of-3 rule, with no recall loss. **Data:** existing timing fixtures. | S |
| STF-17 | ADD | **Suites generated by mutation and boundary pairs.** Apply UI mutation operators to clean fixtures:<br>• shrink a target to 20, 23.9 or 24 px;<br>• set contrast to 4.49, 4.5 or 3.0;<br>• move the primary action into the top band or edge;<br>• strip the icon from a colour-only state;<br>• cut a toast to 0.5 × reading time;<br>• add a 4 Hz flash;<br>• shrink a QTE window by 20 %;<br>• place a destructive neighbour within 4 px;<br>• remove confirm or undo.<br>Add *equivalent mutants* (spacing exception, low-contrast disabled control) as decoys. Report the mutation score per family with Wilson intervals. Keep the hand-seeded blind suites for external validity. The generator author must not read `ergoqa/` (spec §12). | Andrews 2005; Just 2014 [snippet S28]. CTAL-TA ON/OFF points [snippet S10]. ±0.05 needs about 246 defects [derived]. | Recall and noise: measured with narrow intervals; per-check false positives measured on equivalent mutants. Usefulness: ↑ (decisions no longer ride on 20 defects). | **H:** per-family mutation scores agree with hand-seeded recall within their intervals. **Metric:** mutation score and equivalent-mutant false positives per family. **Pass:** interval half-width ≤ 0.08 per family, with hand-seeded recall inside it. **Data:** generator plus clean pages. | M–L |
| STF-18 | ADD | **Baseline-diff mode (regression oracle).** `swarm --baseline <findings.json>` labels each defect record new, persisting or fixed (key: `screen_key` + target + family). The default report shows new and fixed. Diagnostic: the diff between a defect variant and its clean control isolates findings attributable to seeding; findings present in both are systematic noise or real issues that were not seeded. | Regression suites as oracle, Barr §5.3 [paper S01]. | Recall: no loss for regressions. Noise: ↓ strongly in fix-and-replay loops. Usefulness: ↑ (fits workflow step 7). | **H:** the diff keeps every seeded defect and shows far fewer items. **Metric:** seeded defects shown as "new vs clean"; items shown. **Pass:** 100 % of detected seeded defects retained; items ↓ ≥ 60 %. **Data:** existing suites. | S |
| STF-19 | ADD | **Task outcome as a finding.** Each run × profile gets `task_outcome` ∈ {success, fail_ux, fail_agent, fail_env, blocked_side_effect}. `fail_ux` on a critical task becomes a finding with impact I3/I4, linked to the element defect records as candidate causes. | 25010:2023 definition of interaction capability (effectiveness, efficiency, satisfaction) [standard† S06]. `run.success` is not a finding today [derived]. | Recall: ↑ for blockers that no element check sees. Noise: risk of misclassified agent failures. Usefulness: ↑ (primary outcome visible). | **H:** seeded blockers (e.g. a disabled primary action with no explanation) surface as task failures. **Metric:** blocker recall; false task failures on clean runs. **Pass:** ≥ 80 % recall, ≤ 1 false failure per 10 clean runs. **Data:** heldout-2 plus agent runs. | S–M |
| STF-20 | ADD | **User-error-protection measures derived from ISO 25023**, measured in a sandbox:<br>• **UEP-01** protection ratio X = A/B. A = declared destructive or irreversible actions that show a confirmation, undo within 10 s, or a delayed commit; B = all declared destructive actions (after UEp-1-G).<br>• **UOP-06:** undo available after commit steps.<br>• **UOP-08:** appearance consistency — the same role has the same style signature across screens; outliers are flagged. Starts as advisory.<br>These fill the gap that is judgment-only today. | ISO 25023 IDs [snippet S12]. UEp-1-G formula [standard† S07]. 25010:2023 user error protection [standard† S06]. Product-consistency oracle [snippet S20]. | Recall: ↑ in an untested sub-characteristic. Noise: risk from UOP-08, hence advisory. Usefulness: ↑. | **H:** the add-one checks find missing-confirm, missing-undo and inconsistent-primary defects. **Metric:** recall on seeded defects; clean findings. **Pass:** ≥ 80 % recall, ≤ 1 clean finding per suite. **Data:** heldout-2 seeded defects. | M |
| STF-21 | ADD | **Classification fields:** `mode` ∈ {missing, wrong, extra}; `quality_characteristic` (a 25010:2023 sub-characteristic, e.g. `inclusivity`, `user_error_protection`, `self_descriptiveness`, `operability`, `safety.hazard_warning`); `trigger` (the MFS from STF-06, in the ODC sense); `effect` ∈ {usability, accessibility, safety, performance}. Keep `fix_layer`. Add `disposition` (STF-02). Enables ODC-style signatures across products, e.g. "inclusivity × wrong × text token". | IEEE 1044 Type and Mode [snippet S18]. ODC trigger, qualifier and impact [snippet S19]. 25010:2023 [standard† S06]. | Recall and noise: 0. Usefulness: ↑ (routing, trends). | **H:** the fields can be assigned reliably. **Metric:** κ between rule output and a human on 100 records. **Pass:** κ ≥ 0.6 for `mode` and `quality_characteristic` (pre-registered). **Data:** 100 records. | S |
| STF-22 | CUT | **PT-05 as a finding.** Fitts ID > 6 bits → P3 has no normative threshold (the skill's own table says "relative comparison only"), and PT-05 is absent from the dev leave-one-out table. Keep the ID as a run metric. | Oracle soundness needs ground truth [paper S01]. Repository facts [derived]. | Recall: 0. Noise: ↓ slightly. | **H:** no defect depends on PT-05. **Metric:** leave-one-out on heldout-2. **Pass:** no defect lost. | S |
| STF-23 | CUT | **Uncorroborated PJ-01 notes as findings.** List them as hypotheses or issues until a second model or input channel reproduces them (the protocol's own replication rule). | Protocol §5 [derived]. Crowd-oracle limits [paper S01]. | Noise: ↓. Recall: the heuristic category is not strictly scored. | **Metric:** uncorroborated PJ items among findings. **Pass:** 0. | S |
| STF-24 | ADD | **Risk-based allocation (PRISMA) from `ergo-audience.v1`.** Impact = task criticality (safety, health, money, legal, data or access → high; convenience → low) × element role. Likelihood = technical factors (new or changed screen, element density, measured values near thresholds) + segment `stakes` + condition present in the audience.<br>• Quadrant I: full sweeps, ≥ 2 agent models, tours {money, rained_out, obsessive_compulsive, saboteur}.<br>• Quadrants II and IV: sweeps plus 1 agent session.<br>• Quadrant III: deterministic sweep only; P3 advisory hidden.<br>Findings keep "coverage, not prevalence" wording. | ISTQB risk; PRISMA quadrants and factors [snippet S09, S17]. Spec §13 fields [derived]. | Recall: preserved in the full view. Noise: ↓ in the default view. Usefulness: effort goes where risk is. | **H:** almost all real defects fall in the displayed quadrants. **Metric:** displayed recall and displayed clean findings. **Pass:** displayed recall ≥ 0.9 × full recall; displayed clean findings ↓ ≥ 40 %. **Data:** audience files and product briefs for benchmark products (suite format v2). | M |
| STF-25 | CHANGE | **Reconcile spec §7 escalation with the code.** Either implement "+1 level (max P1) for primary or destructive on a critical path" once, at aggregation, or delete the rule because the per-check rules already use roles. Remove the dead `checks._escalate`. Superseded if STF-04 lands. | `_escalate` has no caller [derived]. | Consistency. | **H:** the chosen variant under-rates less. **Metric:** under-ratings vs clean-control P1 count. **Pass:** fewer under-ratings at an equal clean P1 count. **Data:** dev and heldout-2. | S |
| STF-26 | ADD (later) | **Sequence coverage for flows.** Generate event-order variants (back, rotate, background/resume, double tap, cancel) with sequence covering arrays for scripted runs; report transition coverage. | NIST sequence covering arrays for GUIs [industry S05]. Rained-Out and Obsessive-Compulsive tours [industry S08]. | Recall: ↑ for state defects. Cost: ↑. | **H:** ordered event variants find state defects. **Metric:** detection of seeded state defects. **Pass:** ≥ 70 % with ≤ 2 × runs. **Data:** heldout-2 state defects. | L |
| STF-27 | KEEP | These parts already follow testing practice; removing them would raise noise or invalidate validation:<br>• the `measured` / `model` / `judgment` basis (specified, probabilistic-derived and human oracles);<br>• "LLM ergonomic numbers are discarded";<br>• one model = one correlated rater;<br>• blind authoring, a frozen held-out suite, clean controls and decoys;<br>• read-only guardrails and the side-effect stop;<br>• the base-choice stratified layer (sample-efficient per the dev discovery curve; masking-safe per PICT). | [paper S01], [industry S04], dev ablation [derived]. | — | Keep them in the regression metrics of every experiment above. | — |

### 3.2 Order and schema sketch

**Order [opinion]:**

1. STF-08, STF-03, STF-01, STF-22, STF-23 and STF-18. These are re-aggregation
   and demotion only, need no new data, and can be scored on existing runs.
2. STF-05 and STF-17 (the instrument).
3. STF-04 and STF-06 (the model).
4. STF-10–STF-12 (agent sessions).
5. STF-02 and STF-24, once adjudication and audience data exist.

A minimal extension of the finding contract (`ergo-finding.v2`, sketch):

```json
{"id": "ED-012", "scenario_id": "SC-checkout-01", "screen_key": "checkout@3",
 "family": "size", "target": "#pay|결제하기",
 "failures": [{"check_id": "PT-01", "basis": "measured", "measurement": {"value": 20, "threshold": 24}},
              {"check_id": "PT-04", "basis": "model", "trigger": [{"motor.tremor": "mild"}], "robust": true}],
 "trigger": [{"motor.tremor": "mild"}, {"context.mobility": "walking", "grip": "one_hand_left"}],
 "condition_space_fraction": 0.19,
 "impact": "I3", "likelihood": "L3", "confidence": "C2", "priority": "P1",
 "mode": "wrong", "quality_characteristic": "operability", "effect": "usability",
 "fix_layer": "visual", "disposition": "unknown", "baseline_status": "new",
 "label": "condition-space fraction; not prevalence"}
```

Session contract sketch (`ergo-session.v1`):

```json
{"charter": {"explore": "결제 단계 S3–S5", "with": "EP-07 (70s+, one_hand_left, walking), screenshot-only, presbyopia view",
             "to_discover": "결제·오류 복구를 한 손으로 찾고 조작할 수 있는가"},
 "tour": "rained_out", "risk_quadrant": "I", "timebox_steps": 30,
 "stop_reason": "flatline", "steps": {"on_charter": 18, "opportunity": 4, "setup": 2, "investigation": 3},
 "notes": [{"step_index": 7, "oracle": "claims", "oracle_ref": "버튼 문구 '취소'", "failure_class": "ux_issue", "evidence": "S-R-7-007"}],
 "issues": ["S-R-7-011: agent could not ground icon-only back button"],
 "coverage": {"states": 9, "transitions": 14, "back_or_cancel_transitions": 5},
 "debrief": {"past": "...", "results": "...", "obstacles": "...", "outlook": "...", "confidence": "..."}}
```

---

## 4. Risks, open questions and what could not be verified

### Unverified or partly verified

- **Tagging.** Primary text of ISTQB CTFL 4.0.1 and CTAL-TA 4.0, ISO/IEC
  25010:2023, ISO/IEC 25023, ISO/IEC/IEEE 29119-4:2021, IEEE 1044-2009, ODC v5.2,
  NIST SP 800-142, JCGM 106 and the Bach, Bolton and Hendrickson texts was
  **blocked**. Their claims are [snippet], or [standard†] where a secondary
  source quoted them.
- **ISO/IEC 25010:2023 definitions.** Quoted via arc42. The "Capability of a
  product to …" wording differs from the "degree to which …" wording in some
  excerpts, so verify against the purchased text before citing in `params.py`.
- **ISO/IEC 25023.** Measure IDs come from an excerpt. The UEp-1-G formula comes
  from course notes. The revision status of 25023 after the 2023 model was not
  checked.
- **IEEE 1044-2009.** Only the purpose and the Type and Mode values were seen.
  Unverified: the full defect and failure attribute lists, the value sets for
  severity, probability and effect, and my recollection that defects and
  failures are classified separately.
- **ODC.** The names of the eight defect types, the trigger value lists and the
  v5.2 impact values (whether usability and accessibility are among them) were
  not verified.
- **29119-4:2021.** The full technique list, its coverage-measure formulas, and
  whether requirements-based testing was added are unverified.
- **CTFL.** The exact wording of 2-value and 3-value boundary value analysis,
  the state-transition coverage criteria and the defect-report contents in
  CTFL §5.5 were not seen. The principle names are from study notes.
- **Kuhn et al.** Only the medical-device (66 %, 97 %) and range (9–67 %)
  figures were seen. Browser, server and NASA columns were not.
- **PRISMA.** The quadrant numbering is inferred.
- **SBTM.** The session sheet's section names and the often-quoted 90-minute
  norm were not verified.
- **Exploratory-testing experiments.** The results of Itkonen 2007 and Afzal
  2015 were not verified, so no claim about exploratory testing's effectiveness
  is made.
- **Metamorphic testing.** The number of papers in the Segura 2016 survey was
  not verified.

### Risks of the recommendations

- **STF-06 and STF-07 (pseudo-exhaustive sweeps, pairwise arrays).**
  - Stacking extreme conditions multiplies the model penalties (e.g. 70s+ × tremor
    × walking). The number of findings could *rise* unless reporting is limited
    to MFS inside the audience scope and guard bands (STF-15) are in place.
  - The `condition_space_fraction` will be read as prevalence by someone. Keep
    the "not prevalence" label, and never weight it by real population shares in
    the default report.
- **Evidence behind STF-01.**
  - The demotions rest on dev-suite leave-one-out data. heldout-mixed has been
    used for development and tuning, so "tests wear out" applies. Only heldout-2
    can confirm.
  - Leave-one-out effects are not additive. Checks can be redundant with each
    other, e.g. PT-02 with PT-01 and PT-04 on the same element, so remove them
    jointly in the experiment.
- **STF-02 (FP ledger).** Clean-control findings are false-positive
  *candidates*: some may be real problems the benchmark authors did not seed
  (spec §12). A demotion based only on benchmark labels could hide true issues,
  so the ledger needs human or blind-judge adjudication.
- **STF-04 (severity split).** The thresholds (10 %, 3 %, ≥ 3 steps) are my
  proposal, not published values. The split could raise P0 and P1 counts, so it
  must pass the clean-control P0/P1 check.
- **STF-10–STF-12 (sessions).** Tours and charters may raise
  `agent_limitation` rates in weaker agent models. LLMs also "remember" popular
  products, so novelty findings still need relabelled builds.
- **STF-15 (guard bands).** Guard bands trade recall at the boundaries.
  Conformance statements (WCAG, KWCAG) must keep raw thresholds. Only
  priority and visibility use the band.
- **STF-17 (mutation suites).** Mutation operators encode our own idea of a
  defect. About 17 % of real faults are not coupled to any mutant (Just 2014).
  Hand-seeded blind suites stay necessary. Hand-seeded faults may be harder
  than real ones (Andrews 2005), so recall on them may be conservative.

### Open questions

- Would reporting the MFS change what designers fix, compared with the current
  differential condition? This needs a small reviewer study.
- What counts as "adjudicated not useful" for a UX finding when no developer
  acts on it inside the loop? Google's definition assumes an owner who can act.
- Should `interruptions` and `free_hands`, which are read by no check today,
  become causal attributes (e.g. `free_hands` for reach workarounds), or be
  removed from the profile to cut noise in `_differential`?
- Can the swarm's recall gain over one profile (on held-out, 9 defects at 4.3
  clean findings each) be kept while the demotions and grouping bring the
  labelled precision above 0.6? This is the single most useful number for the
  next held-out run.
