# LLM agents as test users: what they can and cannot evidence

Date: 2026-09-28. Topic: LLM agents used as simulated users, usability-test
participants, GUI testers and judges, and what their output can legitimately
support in `skills/ergonomic-persona-swarm-qa`. This is research only. No code,
benchmark, answer key or validation record was changed. The only file written is
this one.

**Evidence tags.**
- [standard] normative text.
- [paper] peer-reviewed publication, with the claim read in the authors' own
  text (paper, abstract or repository README). A non-peer-reviewed preprint is
  marked "preprint" next to the tag.
- [industry] vendor or company documentation, engineering blog or leaderboard.
- [report] survey or government statistics.
- [snippet] seen only in a search-result excerpt, not checked in the source.
- [derived] my own computation, or a fact read in this repository's code or docs
  (file and line given).
- [opinion] practitioner opinion, mine unless attributed. Every threshold I
  propose is [opinion] until an experiment below sets it.

**Read this first.**

1. **Retrieval.** The egress proxy blocked WebFetch for arxiv.org,
   export.arxiv.org, aclanthology.org, openreview.net, proceedings.mlr.press,
   nngroup.com, baymard.com, research.fb.com, assets.amazon.science and
   static1.squarespace.com. Only GitHub pages could be read. Most literature
   numbers below are therefore [snippet]. Check each one against its source before
   it becomes a gate. I used 32 web searches, against a target of 30.
2. **Two repository facts matter more than any paper (§2.9, §3.0).** At commit
   `b913831`, re-checked at `a413015` after the Remorsearch restructure:
   - persona-agent notes (PJ-01) carry no element anchor, so the scorer can never
     match them to a seeded defect;
   - corroboration is a boolean that the agent posts itself, and runs do not
     record the agent's model family or input channel in machine-readable form.

   As the code stands, the heldout-2 pre-registration's H6 (persona agents find
   ≥ 30 % of `agent_judgment` defects) cannot pass, whatever the agents do. Fix
   both before the heldout-2 freeze.
3. **The current validation numbers come from scripted runs only.** Held-out
   strict recall 0.80 and the 98 clean-control findings say nothing yet about the
   LLM persona agents.

---

## 1. Scope and sources searched

### 1.1 Questions

- What can LLM stand-ins for people reproduce (aggregates, directions,
  individual actions), and where do they fail?
- Does persona conditioning change an LLM agent's behaviour enough to matter?
- What do LLM usability-test agents and LLM GUI testers find, and with what
  precision? How does that compare with human studies?
- How reliable are web and computer-use agents, and how do grounding failures
  show up?
- What do companies do in production?
- How reliable are LLM judges, and how should findings be adjudicated?
- What follows for this skill:
  - what persona agents may claim, and what stays with deterministic models;
  - required corroboration and grounding-failure mitigation;
  - the number and diversity of agents;
  - judge design.

### 1.2 Retrieval conditions

- **WebFetch.** Blocked for every paper host listed above. It worked only for
  `github.com` and `raw.githubusercontent.com`.
- **WebSearch.** 32 queries. Search results come with a machine summary of the
  excerpts. I only used statements that appeared in the excerpts and tagged them
  [snippet].
- **Sibling brief.** `docs/human-factors/llm-persona-simulation-validity.md`
  verified some leaderboard numbers (ScreenSpot-Pro, OSWorld) from primary data
  files. I cite them as "via sibling brief" and did not re-check them.

### 1.3 Read in the authors' own text (GitHub READMEs)

- Aher et al. (Turing Experiments): https://github.com/microsoft/turing-experiments
- Park et al. 2024 (agent bank access): https://github.com/joonspk-research/genagents
- UXAgent system: https://github.com/neuhai/UXAgent
- AUITestAgent: https://github.com/bz-lab/AUITestAgent
- SeeAct / Multimodal-Mind2Web: https://github.com/OSU-NLP-Group/SeeAct
- WebArena: https://raw.githubusercontent.com/web-arena-x/webarena/main/README.md
- OSWorld: https://github.com/xlang-ai/OSWorld
- Opened, but the READMEs carry no result numbers:
  - https://github.com/MobileLLM/AutoDroid
  - https://github.com/coinse/droidagent
  - https://github.com/allenai/persona-bias
  - https://github.com/McGill-NLP/agent-reward-bench
  - https://github.com/FondationUCA-Chair-LLM/NL-test-case-runner

### 1.4 Seen only in search excerpts (primary URLs)

**LLMs as simulated people**
- Park et al. 2023, UIST: https://dl.acm.org/doi/fullHtml/10.1145/3586183.3606763 · https://arxiv.org/abs/2304.03442
- Park et al. 2024 (preprint): https://arxiv.org/abs/2411.10109
- Argyle et al. 2023, *Political Analysis* 31(3): https://www.cambridge.org/core/journals/political-analysis/article/abs/out-of-one-many-using-language-models-to-simulate-human-samples/035D7C8A55B237942FB6DBAD7CAA4E49 · https://arxiv.org/abs/2209.06899
- Aher, Arriaga & Kalai 2023, ICML: https://proceedings.mlr.press/v202/aher23a.html
- Wang, Morgenstern & Dickerson 2025, *Nature Machine Intelligence* 7: https://www.nature.com/articles/s42256-025-00986-z · https://arxiv.org/abs/2402.01908
- Hu & Collier 2024, ACL: https://aclanthology.org/2024.acl-long.554/
- "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of LLMs", EMNLP Findings 2024 (authors not seen in excerpts; cited by title): https://aclanthology.org/2024.findings-emnlp.888/
- Gupta et al. 2024, ICLR ("Bias Runs Deep"): https://arxiv.org/abs/2311.04892
- Sharma et al. 2024, ICLR (sycophancy): https://arxiv.org/abs/2310.13548
- Rosala & Moran 2024, NN/g ("Synthetic Users"): https://www.nngroup.com/articles/synthetic-users/
- "Can LLM Agents Simulate Multi-Turn Human Behavior? Evidence from Real Online Customer Behavior Data" (preprint, 2025; authors not seen in excerpts; cited by title): https://arxiv.org/abs/2503.20749
- PerceptUI 2026 (preprint): https://arxiv.org/abs/2606.05697

**LLM agents for usability testing**
- UXAgent, CHI EA 2025: https://arxiv.org/abs/2502.12561 · https://dlnext.acm.org/doi/10.1145/3706599.3719729
- UXAgent system paper (preprint): https://arxiv.org/abs/2504.09407
- Agent A/B, CHI EA 2026: https://dl.acm.org/doi/10.1145/3772363.3799039 · https://arxiv.org/abs/2504.09723
- uxCUA (preprint, 2026): https://arxiv.org/abs/2604.26020
- Baymard Institute 2023: https://baymard.com/blog/gpt-ux-audit
- AXNav (Apple), CHI 2024: https://dl.acm.org/doi/10.1145/3613904.3642777 · https://machinelearning.apple.com/research/axnav

**LLM GUI testing**
- GPTDroid, ICSE 2024: https://arxiv.org/abs/2310.15780 · https://dl.acm.org/doi/abs/10.1145/3597503.3639180
- VisionDroid (preprint): https://arxiv.org/abs/2407.03037
- AUITestAgent (preprint): https://arxiv.org/abs/2407.09018
- AutoDroid, MobiCom 2024: https://dl.acm.org/doi/10.1145/3636534.3649379 · https://arxiv.org/abs/2308.15272
- DroidAgent, ICST 2024: https://arxiv.org/abs/2311.08649
- NL test cases executed by LLM agents (preprint; *Software Quality Journal* 2026 version): https://arxiv.org/abs/2509.19136 · https://link.springer.com/article/10.1007/s11219-026-09767-2

**Web and computer-use agents**
- WebArena, ICLR 2024: https://arxiv.org/abs/2307.13854
- SeeAct, ICML 2024: https://arxiv.org/abs/2401.01614
- OSWorld, NeurIPS 2024: https://arxiv.org/abs/2404.07972
- OSWorld-Verified aggregator, 2026: https://benchlm.ai/benchmarks/osworld-verified

**Industry**
- Meta WES/WW (Ahlgren et al. 2020): https://arxiv.org/abs/2004.05363 · https://research.facebook.com/publications/wes-agent-based-user-interaction-simulation-on-real-infrastructure/
- Meta TestGen-LLM, FSE 2024 Companion: https://arxiv.org/abs/2402.09171 · https://dl.acm.org/doi/10.1145/3663529.3663839

**LLM-as-judge**
- Zheng et al. 2023, NeurIPS Datasets & Benchmarks: https://arxiv.org/abs/2306.05685
- Verga et al. 2024 (preprint; PoLL): https://arxiv.org/abs/2404.18796
- AgentRewardBench (preprint): https://arxiv.org/abs/2504.08942
- Alternative annotator test (preprint; title only): https://arxiv.org/abs/2501.10970

### 1.5 Repository context read (not modified)

- **Skill docs.** `SKILL.md`, and in `references/`: `human-factors-checks.md`,
  `persona-agent-protocol.md` and `validation-and-limits.md`.
- **Spec.** `docs/ergonomic-swarm-spec.md` §0, §2, §5–§7, §10, §12 and §12.1.
- **Validation.** The top-level summary of
  `docs/validation/heldout-mixed-frozen-8c1de02.json`; the `configs` block of
  `ablation-dev-8707b70.json`; `experiments/heldout-2-preregistration.md` (commit
  `b913831`).
- **Sibling briefs, to avoid duplicating their candidates.**
  `docs/human-factors/llm-persona-simulation-validity.md` (summary),
  `docs/qa-discipline/usability-evaluation-methods.md` (UEM-xx) and
  `software-testing-foundations.md` (STF-xx).
- **Code, PJ-01 and agent paths only.** `ergoqa/checks.py`, `swarm.py`,
  `analyze.py`, `bench.py`; `drivers/web/serve.mjs`, `session.mjs`,
  `ergo_drive.mjs`; `scripts/ergo_bench.py`.
- **Not opened.** No `answer_key.json`, no benchmark README, and none of the
  heldout-2 `keys/`, `site/` or `scenarios/` content. I listed only the directory
  names.

---

## 2. Key knowledge

### 2.1 LLMs as stand-ins for people: what is reproduced

**Generative agents (Park et al. 2023, UIST).** 25 agents in a sandbox town.
Believability was judged by 100 evaluators who ranked five conditions [snippet]:
- TrueSkill μ = 29.89 (σ 0.72) for the full architecture;
- 26.88 without reflection;
- 22.95 for human crowdworkers role-playing the agents;
- a party invitation spread from 1 to 13 of 25 agents in two simulated days.

The study measures how believable the behaviour is to observers. It does not
measure accuracy against what particular people do.
→ Agent narratives are more convincing than human role-play, so reviewers
are more likely to accept unfounded notes [opinion].

**Simulations of 1,000 people (Park et al. 2024, preprint).**
- 1,052 stratified US participants each gave a two-hour interview. The resulting
  agents reproduced participants' General Social Survey answers 85 % as
  accurately as the participants reproduced their own answers two weeks later
  [snippet].
- They performed comparably on personality and experimental replications. They
  reduced accuracy gaps across racial and ideological groups compared with agents
  given only demographic descriptions [snippet].
- The agent bank is not public because of participant privacy. Individual
  responses need restricted, reviewed access [paper, preprint, README].
- → The fidelity came from rich individual interviews. This skill's persona
  label is the weak "demographic description" condition [derived].

**Silicon sampling (Argyle et al. 2023, *Political Analysis* 31(3):337–351).**
- GPT-3 conditioned on thousands of real sociodemographic backstories from US
  surveys reproduced subgroup response distributions ("algorithmic fidelity"),
  judged by criteria including Forward Continuity and Pattern Correspondence
  [snippet].
- I could not obtain the correlation values.
- → The claim concerns aggregate survey-answer distributions, not interaction
  behaviour on a UI [opinion].

**Turing Experiments (Aher, Arriaga & Kalai 2023, ICML).**
- The study replicated the Ultimatum Game, garden-path sentences and the Milgram
  shock experiment. The Wisdom-of-Crowds experiment exposed a "hyper-accuracy
  distortion" in some models, including ChatGPT and GPT-4, which "could affect
  downstream applications in education and the arts" [paper, abstract read in
  README].
- → In plain terms, simulated participants were unrealistically accurate (my
  paraphrase). Capable agents make fewer of the errors novices make, so they
  under-detect novice confusion [opinion].

**Real shopping sessions ("Can LLM Agents Simulate Multi-Turn Human Behavior?", arXiv 2503.20749, preprint).**
- Data: 31,865 sessions and 230,965 actions.
- Prompted LLMs (DeepSeek-R1, Llama, Claude) generated the human's next action
  correctly 11.86 % of the time.
- A Qwen2.5-7B fine-tuned on click data plus synthesized reasoning reached
  17.26 %, and 33.86 % F1 for purchase prediction [snippet].
- → That is +5.40 percentage points [derived]. Agent paths are exploration, not
  predictions of human paths [opinion].

**PerceptUI (2026, preprint).** It trains a persona-conditioned UI evaluator on
human decisions (contrastive reflection fine-tuning plus prompt evolution) and
claims human-level realism and population-level distributions [snippet; details
not verified].
→ The route to realism in the 2026 literature is training on human response
data, not prompting [opinion].

**NN/g, "Synthetic Users" (Rosala & Moran, 21 June 2024).**
- NN/g reran three studies with ChatGPT and a synthetic-user product. Real
  learners often started courses and did not finish them; synthetic learners
  reported completing everything [snippet].
- The bots were sycophantic. The conclusion: a few use cases exist, but user
  research needs real users [snippet].

### 2.2 Persona conditioning: how much does it change model behaviour?

- **Persona effect (Hu & Collier 2024, ACL).**
  - Persona variables explain < 10 % of the variance in annotations across
    existing subjective NLP datasets [snippet].
  - Persona prompting gives "modest but statistically significant" gains, largest
    where annotators disagree only mildly [snippet].
  - The gain grows linearly with how strongly persona variables correlate with
    the human labels [snippet].
- **Personas in system prompts ("When 'A Helpful Assistant' Is Not Really Helpful", EMNLP Findings 2024).**
  - The study tested 162 roles.
  - The revised version finds that personas in system prompts do not improve
    objective-task performance over a no-persona control and can hurt it
    [snippet].
  - Picking the best role per question performed about like random selection
    [snippet].
  - The paper's conclusion flipped between versions, so cite the final one.
- **Persona-induced bias (Gupta et al. 2024, ICLR, "Bias Runs Deep").**
  - Scope: 19 personas from 5 socio-demographic groups, 24 reasoning datasets and
    4 LLMs.
  - With ChatGPT-3.5, 80 % of personas showed bias, and some datasets dropped
    by 70 %+ [snippet].
  - For the "physically-disabled" persona, 58 % of errors were abstentions
    [snippet].
  - → A label such as "70대 · 떨림 · 노안" (70s, tremor, presbyopia) can make an
    agent refuse or feign inability. That is role-played disability, which the
    protocol forbids, and it is invisible unless measured [opinion].
- **Misportrayal and flattening (Wang, Morgenstern & Dickerson 2025,
  *Nature Machine Intelligence* 7:400–411).** 3,200 participants across 16
  demographic identities and 4 LLMs. LLMs misportray and flatten groups, and the
  authors argue analytically that current training cannot capture positionality
  [snippet].
  → Diversity bought through demographic labels is largely illusory [opinion].
- **Gap.** I found no study measuring whether persona conditioning changes
  **GUI navigation** behaviour. §3.2 designs one.

### 2.3 Sycophancy, over-competence and plausibility

- **Sycophancy (Sharma et al. 2024, ICLR).** Five state-of-the-art assistants
  were consistently sycophantic across four free-form tasks. Humans and
  preference models preferred convincingly written sycophantic answers over
  correct ones "a non-negligible fraction of the time" [snippet].
  → Questions such as "was this confusing?" or "find usability problems" invite
  agreement. A judge shown a claim tends to accept it [opinion].
- **Over-competence.**
  - Hyper-accuracy distortion (§2.1) [paper].
  - On OSWorld, agents went from 12.24 % against a 72.36 % human baseline (2024)
    to about 85–86 % on OSWorld-Verified in 2026, per aggregators [snippet;
    industry, self-reported] (§2.6).
  - → Agent success is weak evidence that users succeed, and failure-free agent
    runs are weak evidence that a flow is easy [opinion].
- **Plausibility.** Agents out-scored human role-players on believability
  (§2.1) [snippet], while prompted LLMs predicted only 11.86 % of real next
  actions [snippet].

### 2.4 LLM agents as usability-test participants and UX evaluators

**UXAgent (Lu et al., CHI EA 2025; system paper, preprint).**
- It has a persona generator ("thousands of user personas"), a universal browser
  connector and a result viewer [snippet].
- Evaluation was a heuristic review by five UX researchers, who praised it and
  raised concerns about the future of UX studies [snippet].
- The system samples personas from demographic categories (age, gender, shopping
  frequency) by weighted random choice and reads DOM data through
  Playwright/Chromium. The example config runs 20 personas, 10 concurrently.
  Agents answer post-study questionnaires [paper, preprint, README].
- No comparison with real participants' problems was reported [snippet, README].

**Agent A/B (CHI EA 2026).**
- Claude 3.5 Sonnet generated 100k personas, and 1,000 were sampled into a
  between-subjects test of Amazon's filter panel. The reduced filter list gave
  more purchases (414 vs 403), matching the direction of a parallel large human
  experiment [snippet].
- If the arms had 500 agents each (my assumption):
  - that is 82.8 % vs 80.6 %, z = 0.90, p ≈ 0.37 [derived];
  - the minimum detectable difference at 80 % power is about 6.9 points
    [derived].
- → The simulation reproduced a direction that its own sample could not show as
  significant [derived].

**uxCUA (2026, preprint).**
- Computer-use agents were trained to assess usability. The trained model's AUC
  for agreement with designer preferences was 0.607, against 0.435 for EvoCUA
  [snippet].
- Human inter-rater agreement on a subset was Krippendorff's α = 0.308
  [snippet]. 17 participants with design backgrounds rated 30 site pairs
  [snippet].
- → Even a model trained for this purpose is only slightly above chance, and
  the humans themselves agree weakly [opinion].

**Baymard Institute (2023): GPT-4 "UX audits".** 12 pages, compared with 6 UX
professionals [snippet]:
- 80 % error rate, 20 % accuracy;
- 26 % of the issues visible in the screenshot found, and 14 % of the issues on
  the live page;
- per page, 2.9 correct findings, 18.5 missed (live page), 9.4 missed
  (screenshot), 1.3 harmful and 10.6 "waste of time" suggestions.

My recomputation from those averages: 2.9 / 14.8 = 19.6 % of suggestions
correct; coverage 2.9 / 21.4 = 13.6 % (live) and 2.9 / 12.3 = 23.6 % (screenshot)
[derived]. The reported 26 % is probably a per-page average [opinion].

**AXNav (Apple, CHI 2024).**
- A planner, an action agent and an evaluation agent, with pixel-based UI
  understanding, execute manual accessibility tests (for example with VoiceOver).
  The output is a chaptered video for QA testers [snippet].
- **Heuristics** flag issues, such as text not growing with Large Text or
  VoiceOver navigation loops [snippet].
- 10 accessibility QA professionals found it useful and said it tested the way
  they do [snippet].
- → The agent navigates, deterministic rules flag, and humans decide. That is the
  same split as this skill's protocol [opinion].

**Synthesis.** No 2024–2026 source I found validates LLM agents against human
usability tests at the level of individual issues. The evidence is of three
kinds:
- expert opinion that the tools are useful (UXAgent, AXNav);
- directional agreement (Agent A/B);
- weak preference agreement (uxCUA).

Open-ended LLM audits are mostly wrong (Baymard) [snippet; opinion].

### 2.5 LLM agents as GUI testers

| System | Venue | Numbers | Tag |
| --- | --- | --- | --- |
| GPTDroid | ICSE 2024 | 93 Google Play apps; +32 % activity coverage and +31 % bugs over the best baseline; 53 new bugs, 35 confirmed and fixed | [snippet]; 35/53 = 66 % [derived] |
| QTypist ("Fill in the Blank", LLM text-input generation) | ICSE 2023 | Numbers not verified at the time of writing; title and venue from memory | — |
| VisionDroid (retitled "Seeing is Believing: Vision-driven Non-crash Functional Bug Detection for Mobile Apps") | preprint | Aligns GUI text with screenshots; function-aware explorer; logic-aware bug detector over segmented history; 3 datasets, 10 baselines; 29 new bugs, 19 confirmed and fixed; precision and recall not obtained | [snippet]; 19/29 = 66 % [derived] |
| AUITestAgent | preprint (Meituan deployment) | Natural-language requirement → interactions + verification. Verification accuracy 94 % | [snippet] |
|  |  | Recall 90 % on injected GUI functional bugs at a 4.5 % false-positive rate | [paper, preprint, README] |
|  |  | 4 new functional bugs in 10 regression runs over two months at Meituan | [snippet] |
| AutoDroid | MobiCom 2024 | 158 tasks; 90.9 % action accuracy; 71.3 % task completion; +36.4 % and +39.7 % over GPT-4 baselines | [snippet] |
| DroidAgent | ICST 2024 | 15 Themis apps; 61 % activity coverage vs 51 %; 317 of 547 self-generated tasks realistic and relevant | [snippet]; 58 % [derived] |
| NL test cases run by LLM agents | preprint; *SQJ* 2026 | Unsound verdicts come from ambiguous steps and agents hallucinating steps; repeated runs of one test give inconsistent outcomes; 8 LLMs (3B–70B); Llama 3.1 70B "acceptable", with consistency above the 3-sigma level | [snippet] |

**Synthesis.**
- With an explicit oracle (a crash, a stated requirement), LLM testers reach
  deep states and verify well [snippet; opinion].
- Open-ended judgments need confirmation. In two academic studies, about two
  thirds of reported new bugs were confirmed and fixed. Authors report the
  bugs they submitted, so this is an upper-biased usefulness figure [derived;
  opinion].
- Agent-invented tasks are often unrealistic (42 % were not) [derived].

### 2.6 Web and computer-use agents: capability and grounding

- **WebArena (ICLR 2024).**
  - The best GPT-4 agent succeeded end to end on 14.41 % of tasks, against a
    human rate of 78.24 % [snippet].
  - A common error was abandoning solvable tasks as "unachievable" [snippet].
  - About 170 human trajectories are released [paper, README].
- **SeeAct (ICML 2024).**
  - GPT-4V completed 51.1 % of tasks on live websites **if its textual plans were
    grounded manually** [snippet].
  - The best automatic grounding, which combines HTML structure and visuals, still
    trailed oracle grounding by 20–25 % [snippet].
  - Set-of-Mark prompting was not effective for web agents [snippet].
  - Grounding modes in the code: `text_choice`, `text_choice_som` (the default),
    element attributes and image annotation [paper, README].
  - Multimodal-Mind2Web splits:

    | Split | Actions | Tasks |
    | --- | --- | --- |
    | Train | 7,775 | 1,009 |
    | Test-task | 1,339 | 177 |
    | Test-website | 1,019 | 142 |
    | Test-domain | 4,060 | 694 |

    [paper, README]
- **OSWorld (NeurIPS 2024).**
  - 369 tasks. Humans completed 72.36 % and the best model 12.24 %. Models
    struggled "primarily" with GUI grounding and operational knowledge [snippet].
  - 2026 aggregators list OSWorld-Verified leaders at about 85–86 % (86.1 % on
    2026-09-28), above the human baseline [snippet; industry, self-reported,
    some best-of-N].
- **ScreenSpot-Pro grounding.** Accuracy rose from 0.8 % for GPT-4o to 82.7 %
  for the leaderboard leader. Icons still trail text, 70.4 vs 90.4 for the leader
  [industry, via sibling brief, not re-checked].
- **→ Consequences** [opinion]:
  1. Agent failures are dominated by grounding and operational knowledge, not by
     human-like confusion.
  2. By 2026, agents beat benchmark humans on many tasks, so agent success says
     little about user success.
  3. Grounding still fails most on icon-only and unlabeled targets. Those are
     also real UX defects, so an agent failing on an icon is confounded (agent
     limitation or label defect) until a deterministic check (accessible name,
     label in name) decides.

### 2.7 Industry practice

- **Meta WES / WW (Ahlgren et al. 2020).** A research agenda for Web-Enabled
  Simulation. Facebook's WW simulates social-media interactions on the real
  platform infrastructure ("hundreds of millions of lines of code") for
  reliability, integrity and privacy work [snippet].
  - From memory, not verified: WW's bots are isolated from real users, and
    constraints are placed on bot actions. Treat this as unconfirmed.
  - → The value comes from exercising **real infrastructure** with simulated
    operators, not from realistic bots. This skill's "real surface, simulated
    human model" rule has the same shape [opinion].
- **Meta TestGen-LLM (FSE 2024 Companion).**
  - LLM-generated tests are surfaced only after filters guarantee an
    improvement: 75 % built, 57 % passed reliably, and 25 % raised coverage
    [snippet].
  - It improved 11.5 % of the classes it was applied to, and engineers accepted
    73 % of its recommendations [snippet].
  - → Filter before surfacing ("assured" LLM output) [opinion].
- **Meituan (AUITestAgent), Apple (AXNav), Amazon (UXAgent and Agent A/B
  co-authors)** [snippet]. Deployments pair agents with an explicit oracle or a
  heuristic flagger and human review. None uses agents as stand-ins for user
  opinions [opinion].
- **Practitioner evidence.** Baymard and NN/g (above) [snippet].

### 2.8 LLM-as-judge reliability

- **Zheng et al. 2023 (NeurIPS Datasets & Benchmarks).** Strong judges (GPT-4)
  agreed with human preferences over 80 % of the time, the same level as
  human–human agreement. They show **position**, **verbosity** and
  **self-enhancement** biases and limited reasoning [snippet]. I did not obtain
  the paper's position-consistency percentages.
- **PoLL (Verga et al. 2024, preprint).** A panel of three smaller models from
  different families (command-r, gpt-3.5-turbo, Haiku) correlated better with
  human judgments than a single GPT-4 judge across six datasets. It showed less
  intra-model bias, cost over 7× less, and had the highest Cohen's κ [snippet].
- **AgentRewardBench (preprint).**
  - 1,302 web-agent trajectories from 5 benchmarks and 4 agent LLMs. Experts
    annotated success, side effects and repetitiveness [snippet].
  - Of 12 LLM judges, **none excelled across all benchmarks**, and rule-based
    benchmark checks **under-report** agent success [snippet].
- **Alternative annotator test (arXiv 2501.10970, preprint).** A statistical
  test for when an LLM may replace human annotators [snippet, title only]. I
  could not read the procedure.
- **→ For this skill** [opinion]:
  - A judge must be calibrated against human labels.
  - Evidence should be shown before the claim, so the judge cannot simply agree
    with it (sycophancy, §2.3).
  - Verbosity and order should be controlled.
  - A heterogeneous panel beats one strong model.

### 2.9 What this repository's LLM layer evidences today

All points below are [derived] from the named files at commit `b913831`. I
re-checked them at `a413015`, after the Remorsearch restructure. The same code
now also lives under `skills/remorsearch-ux-qa/`, where PJ-01 is built at
`ergoqa/checks.py` L1385 and `tier()` sits at L1566. Every fact below still
holds there.

1. **The benchmark records scripted runs only.**
   - Source: the `scripts/ergo_bench.py` docstring, "records one scripted run",
     and validation-and-limits §Method 2.
   - Held-out strict recall 0.80 (lenient 0.90) and the 98 clean-control findings
     therefore contain **no** PJ-01 units.
   - Of the 225 swarm findings, 98 (43.6 %) were on clean controls, 153 (68.0 %)
     were P3, and labelled precision is a lower bound of 0.34.
2. **PJ-01 has no anchor.** It is built with `element_ids = []` and
   `element_key = "step-{i}|persona-note"` (`ergoqa/checks.py` L1359).
   - The scorer matches answer-key selectors against `selectors` plus the
     element-key prefix (`ergoqa/bench.py` L22–44). `step-3` never equals `#pay`,
     so no PJ-01 unit can strictly match a seeded defect.
   - Swarm groups PJ-01 by `(scenario, check, "step-i")` (`ergoqa/swarm.py` L69).
     Interactive agents take different paths, so step indices are not comparable
     across agents. Unrelated notes at the same index merge, and the same problem
     at different indices splits.
3. **Corroboration is self-declared.** `tier()` promotes PJ-01 from hypothesis
   to finding only when `measurement.corroborated` is true (`checks.py` ~L1531).
   That value is the note's own `corroborated` boolean, which `/note` accepts
   from the agent (`drivers/web/serve.mjs` L15, L93).
4. **Agent identity is free text.** `run.json.agent` is
   `{description: <free text, ≤ 200 chars>}`, or `"unrecorded"` in serve mode
   (`session.mjs` L1160; `ergo_drive.mjs` L41, L185). Model family and input
   channel are not machine-readable, so the protocol's "second model or second
   channel" rule cannot be computed.
5. **The screenshot-only channel is not enforced.** `GET /snapshot` returns the
   path to the snapshot JSON, which holds DOM-derived elements, selectors and
   roles (`serve.mjs` L97–107). Protocol §2's "no DOM, no accessibility tree" is
   a convention.
6. **Unused severity field.** `/note.severity` is accepted and validated
   (`serve.mjs` L15, L88) but never used by PJ-01.
7. **Body and sensory label.** The agent receives the profile label (age, grip,
   vision, context) and optionally a CVD or low-acuity view (protocol §2).
8. **heldout-2 H6 is structurally untestable.** The pre-registration
   (`heldout-2-preregistration.md`) scores C6 persona agents (Opus, budget 4 per
   product) by **strict selector match**, and counts only corroborated PJ-01
   units. Authors, detector and judges are all Claude. With the facts above, H6
   cannot pass:
   - item 2 alone forces recall to 0;
   - item 3 plus same-model agents forces every unit to stay a hypothesis unless
     the four runs span two input channels.

### 2.10 Synthesis: what persona agents may legitimately evidence

This table is my synthesis of §2.1–§2.9 [opinion]. Check IDs come from
`references/human-factors-checks.md` [derived]. NV-01, NV-02, ER-01, LN-01 and
PJ-02 are proposals (LAT-09, LAT-10).

| Claim type | Who can evidence it | What the agent contributes | Corroboration required | Highest severity via agents |
| --- | --- | --- | --- | --- |
| Missing or late feedback after an action | CG-03 (measured), GZ-02 (model) | reaching the state; noticing | the deterministic twin decides | set by CG-03 / GZ-02 |
| Dead end, loop, no forward path | proposed NV-01 (measured), NV-02 (model) | reaching the state | twin, or 2 channels/families at the same anchor | P2 via twin; P3 otherwise |
| Result differs from a declared expectation | proposed PJ-02, deterministic when machine-checkable | observed outcome | deterministic, or 2 channels/families + replay | P2 |
| Copy or label comprehension (ambiguous label, jargon, misleading wording) | agent judgment only; label-in-name twin for the name–label mismatch part | an interpretation | 2 channels/families + paraphrase invariance + judge panel; real-user check before any claim about users | P3 (P2 when corroborated) |
| Wrong path choice (information scent) | UEM-18 scent model + agents | path choice | model agrees with agents | P3 |
| Unclear error message | proposed ER-01 (association, measured) + agent comprehension | comprehension | as copy | P2 for the measured part; P3 for the rest |
| Motor (reach, touch accuracy), perception (contrast, CVD, acuity), timing (reading time, QTE), flashing | deterministic models only | nothing; agent statements are discarded | — | per check table |
| Emotion, satisfaction, trust, preference, willingness to pay, prevalence, learning over sessions | not evidenced by this skill | — | real users | not reportable |
| Dark patterns | separate auditor pass | agents can be manipulated by them | — | per auditor |

---

## 3. Implications for the skill

### 3.0 Time-critical: before the heldout-2 freeze

Either land LAT-01, LAT-02 and LAT-03 (S–M together) before the detector is
frozen, or amend the pre-registration now, stating that H6 is untestable at the
frozen commit. Otherwise:
- C6 will report 0 recall;
- that 0 will be read as "persona agents find nothing";
- in fact it is an instrument artefact [derived, §2.9 items 2, 3 and 8].

Under the Claude-only rule, give the C6 runs two input channels (for example 2
screenshot + 2 screenshot-plus-accessibility-tree runs per product). Without two
channels, even correct corroboration is impossible.

### 3.1 Candidate changes

Effort: S ≤ 1 day, M ≤ 1 week, L > 1 week. The "pilot" means interactive runs on
dev fixtures or a new pilot suite outside heldout-2, so held-out data are not
spent on tuning. Cross-references: UEM-xx (`usability-evaluation-methods.md`) and
STF-xx (`software-testing-foundations.md`).

| ID | Type | What exactly | Evidence | Expected effect on recall / noise / usefulness | Experiment that decides it (hypothesis, metric, pass rule, data needed) | Effort |
| --- | --- | --- | --- | --- | --- | --- |
| LAT-01 | CHANGE (pre-freeze) | **Anchor every persona note to an element and a screen.**<br>• `/note` takes `anchor`, one of three forms: `"acted"` (the default: `steps[i].target_element_id`); `{"point": {x, y}}`; or `{"box": {x, y, w, h}}`, in screenshot pixels.<br>• The driver resolves the anchor against the `after` snapshot (the `before` snapshot for expectation notes). It picks the smallest element containing the point, or the element with IoU ≥ 0.3 with the box. It stores `anchor_element_ids`, `anchor_selectors` and `screen_key` (URL path + hash of visible headings and landmarks + an open-dialog flag).<br>• PJ gets `element_ids` = anchor ids, so `selectors` is filled and `element_key` becomes `<selector>\|persona-note`.<br>• The swarm key becomes (scenario, `screen_key`, selector, `mismatch_type`). `mismatch_type` is one of: no_feedback, unexpected_result, dead_end, missing_info, label_mismatch, error_unclear, other.<br>• Unresolvable notes stay `hypothesis`.<br>• Screenshot-channel agents still never see element ids. This feeds STF-03 defect records. | PJ-01 has no anchor [derived: checks.py L1359]. The scorer cannot match `step-i` [derived: bench.py L22–44]. Step-index grouping mixes agents' paths [derived: swarm.py L69; opinion]. heldout-2 H6 uses strict selector matching [derived: pre-registration]. | **Recall:** the agent layer goes from structurally 0 to measurable. **Noise:** ↓, because duplicates merge across agents and unanchored notes leave the findings list. | **H:** anchored grouping matches ≥ 1 task-flow defect in the pilot where step keys match 0, and cuts PJ units per clean scenario by ≥ 30 % through merging. **Metric:** re-score the same pilot runs both ways. **Pass:** both hold. **Data:** ≥ 4 interactive runs on each of ≥ 5 pilot scenarios, plus a unit test (`anchor: "acted"` on `#pay` → `selectors: ["#pay"]`). | S–M |
| LAT-02 | CHANGE (pre-freeze) | **Record the operator in machine-readable fields and enforce the input channel.**<br>• `run.json.agent` = {`description`, `model`, `model_family`, `model_version`, `temperature`, `seed`, `input_channel`, `persona_arm`, `prompt_sha256`, `max_steps`}.<br>• `model_family` is the provider lineage: claude, gpt, gemini, qwen, …<br>• `input_channel` ∈ {screenshot, a11y, screenshot+a11y}.<br>• `persona_arm` ∈ {neutral, cognition, full, full+view}.<br>• `serve --agent-json <file>` replaces the free-text flag. `validate` rejects interactive runs without `model_family` and `input_channel`.<br>• With `input_channel = screenshot`, `/snapshot` and `/act` replies omit the snapshot-JSON path and element counts, and the JSON is written outside the agent's workspace. | Agent identity is free text [derived: session.mjs L1160]. The JSON path leaks the DOM [derived: serve.mjs L97–107]. Protocol §5 needs model and channel [derived]. Channels fail differently: HTML + visual grounding was the best strategy but still 20–25 % short of oracle grounding (SeeAct) [snippet]. | Enables LAT-03, LAT-05 and LAT-13, and closes a validity leak: agents reading the DOM while being scored as screenshot-only. Recall and noise are neutral on their own. | Instrument change. **Pass:** 100 % of interactive runs carry the fields, and a probe confirms that screenshot-channel replies contain no JSON path. | S |
| LAT-03 | CHANGE (pre-freeze) | **Compute corroboration; stop accepting it from the agent.**<br>• Drop `corroborated` from `/note` (or keep it as `corroborated_claimed` and ignore it).<br>• In `swarm.aggregate`, a PJ unit is corroborated when ≥ 2 runs with notes in the same anchor group differ in `model_family` or in `input_channel`. Several seeds, or several models of one family on one channel, count once.<br>• Store `corroboration_basis` ∈ {family, channel, same_family_models}. The last one alone never lifts the tier.<br>• Under the Claude-only rule, C6 therefore needs both channels. | Self-declared corroboration promotes the tier [derived: checks.py ~L1531, L1357]. "Ten identical agents agreeing is still one vote" [derived: protocol §5]. A disjoint-family panel had less intra-model bias and higher κ with humans than one large judge (PoLL) [snippet]. No single LLM judge was best on all 5 benchmarks (AgentRewardBench) [snippet]. The heldout-2 authors, detector and adjudicators are all Claude [derived]. | **Noise:** ↓ (no self-promotion). **Recall:** the finding tier may lose units, but only units that no independent rater saw. | **H** (with UEM-11): P(judged real \| computed-corroborated) − P(judged real \| not) ≥ 0.15, and same_family_models adds ≤ 0.05 over no corroboration. **Data:** ≥ 60 judged PJ units from pilot runs over ≥ 2 channels (and ≥ 2 families if allowed). | S |
| LAT-04 | ADD | **Score the agent layer on its own, against paired clean controls.** `ergo_bench.py --interactive <panel.json>` runs the agent panel on each defect variant and its clean control and writes a `judgment_layer` block:<br>• `pj_recall_strict` on `detectable_by: agent_judgment` defects;<br>• `pj_unique_recall`: defects matched only by PJ units;<br>• **paired anchor Δ** = P(unit at the defect's selector \| defect variant) − P(unit at the same selector \| clean control), falling back to `screen_key` when the element exists only in the defect variant;<br>• `pj_units_per_clean_scenario`, `agent_success_rate`, `grounding_errors_per_100_actions`, `agent_limitation_rate` and `tokens_per_matched_defect`, all by model and channel.<br>**Default-path decision:** interactive agents stay in the default workflow only if this passes. Otherwise default runs are scripted and agents become an opt-in exploration mode. | Validated numbers exist for scripted runs only [derived]. Open-ended LLM UX audits: ~80 % of suggestions wrong, 14–26 % of issues found (Baymard) [snippet]. A usability-trained CUA reached AUC 0.607 against designer preferences [snippet]. With explicit oracles: 90 % recall at 4.5 % FPR (AUITestAgent) [paper, preprint, README]. | **Usefulness:** ↑↑. This is the first measurement of the LLM layer, and it may show that agents should leave the default path, which saves cost and noise. **Measurement:** the paired Δ separates defect-caused confusion from agent limitations that appear on both variants. | **H:** agents detect task-flow defects that no deterministic check detects. **Pass (stay in the default path):** `pj_unique_recall` ≥ 0.30, paired Δ ≥ 0.3, corroborated-unit precision (LAT-15) ≥ 0.5, and ≤ 1 corroborated unit per clean scenario. These are the H6 thresholds plus Δ and uniqueness [opinion]. **Data:** the pilot first, then the heldout-2 C6 runs after the freeze. | M |
| LAT-05 | ADD (experiment) | **Persona-conditioning ablation (§3.2).** Four arms:<br>• **N:** goal and concrete data only;<br>• **C:** N plus familiarity, domain knowledge and time pressure;<br>• **F:** the current full label, adding age band, grip, vision, mobility and lighting;<br>• **F+V:** F plus the CVD or acuity profile view.<br>Model, temperature, step cap and goal text are identical across arms; only the persona block differs (its hash is recorded). | Persona variables explain < 10 % of annotation variance [snippet]. Personas in system prompts do not help objective tasks, and the best role was about random [snippet]. 80 % of personas showed bias, with drops of 70 %+ and 58 % of errors being abstentions for one persona [snippet]. Identity groups are flattened [snippet]. Demographic descriptions were beaten by interview-based agents [snippet]. No GUI-navigation study exists (§2.2). | If the literature transfers, N ≈ C ≈ F on defects found, and F adds role-played and stereotyped notes. Then cutting F loses no recall and lowers noise and tokens. | **Pass rules (§3.2):**<br>• keep F only if F − N ≥ +1 matched `agent_judgment` defect in both channels (or families), clean-control units rise ≤ 10 %, and leakage ≤ 1 % of notes;<br>• keep C over N only if C − N ≥ +1 matched defect, or ≥ 1 corroborated first-use unit is judged real;<br>• otherwise use N. | M |
| LAT-06 | CUT (conditional on LAT-05) | **Remove body, sensory and demographic facets from the operating agent's input.**<br>• Remove age band, grip, handedness, vision, tremor, mobility and lighting from the prompt.<br>• Stop giving the agent the CVD or low-acuity "profile view" as a source of findings. `ergo_qa.py view` stays as an illustration for human reviewers.<br>• Each run keeps its `profile_id`. Profiles still choose scenarios and devices, and every recorded run is still analysed under all profiles (`--cross-profile`) and scored against key conditions. | Ergonomic checks are computed per snapshot under every profile, whoever operated the run [derived: SKILL.md step 3]. The label can therefore only change path choice or produce role-play, which the protocol discards [derived: protocol §1]. Persona-induced abstention and bias [snippet]. A VLM viewing a Machado-simulated image is not a validated proxy for a CVD viewer [opinion]. PC-03 already computes CVD confusability [derived]. | **Recall:** 0 change expected; the ergonomic checks are unchanged. **Noise:** ↓ (no stereotyped notes). **Cost:** fewer prompt tokens. | Decided by LAT-05 (F vs C or N), plus a leakage audit: notes with body or ability claims per arm, found by a Korean/English regex and a classifier. **Pass (cut):** C or N has ≥ 50 % fewer leakage notes and no fewer matched defects. | S |
| LAT-07 | ADD | **Describe-then-ground, with grounding telemetry.**<br>• The agent names the target as it appears ("the blue '결제하기' button, bottom") plus a coarse region.<br>• The driver resolves the description against the current snapshot's visible elements and text blocks: visible-text similarity ≥ 0.8, then region, then icon-crop similarity.<br>• 1 candidate → act. 2–4 candidates within 0.05 → return their crops, with no role or clickability flags, for the agent to pick. 0 candidates → `no_visible_match`.<br>• Per step, `grounding` = {`method` ∈ {describe, coords, hotspot}, `candidates`, `resolved_element_id`, `match_score`, `hit_element_id` (elementFromPoint at the tap), `retries`}.<br>• Error classes: wrong_element, no_visible_match, offscreen, coordinate_miss, stale_screen, hallucinated_target.<br>• Icon-only targets get one re-query on a 2× crop. No Set-of-Mark overlay in the screenshot channel, because it reveals what is clickable. | SeeAct: 51.1 % with manual grounding, the best automatic grounding 20–25 % below oracle, and Set-of-Mark not effective [snippet]. OSWorld failures were mainly grounding and operational knowledge [snippet]. Icons trail text (70.4 vs 90.4) [industry, via sibling brief]. | **Noise:** ↓ (fewer agent-caused "dead ends" filed as UX issues). **Recall:** ↑ (deeper states reached). A `no_visible_match` for a target the scenario names becomes a label or affordance candidate when two channels agree; LAT-09's label-in-name twin checks it. | **H:** G1 (describe-then-ground) vs G0 (current coordinates or selectors): `agent_limitation` rate −50 %, success +15 points, clean-control PJ units no higher and matched defects no fewer. **Data:** 2 arms × 2 channels × 3 seeds on ≥ 8 pilot scenarios. | M |
| LAT-08 | CHANGE | **Assign `failure_class` from telemetry first; keep the agent's own class as a claim.** Rules, in order:<br>1. `environment`: a network error, HTTP ≥ 400, console exception or driver error at the step.<br>2. `agent_limitation`: `hit_element_id` ≠ `resolved_element_id`, the target was off-screen, or the same action repeated ≥ 3 times on an unchanged screen.<br>3. `ux_candidate`: the hit element is visible and interactive and CG-03 saw no DOM change within 3 s, or a LAT-09 twin fired.<br>4. Otherwise the agent's class, stored as `failure_class_claimed`.<br>This replaces "stop after three consecutive agent_limitation notes" with the computed class plus STF-12's `flatline`. | Agents abandon solvable tasks as unachievable (WebArena) [snippet]. Agents running NL tests hallucinate steps and give inconsistent verdicts across repeats [snippet]. The class is self-reported today [derived: protocol §3]. | **Noise:** ↓ (agent failures stop becoming UX units). **Recall:** ≈. | **H:** the computed class agrees with the adjudicated class (two humans, or the LAT-14 panel) at κ ≥ 0.6, and beats the agent's own class by ≥ 0.15 κ. **Data:** ≥ 100 `confusion: true` notes from the pilot. | M |
| LAT-09 | ADD | **Deterministic twins for what agents notice.** Each `mismatch_type` gets a check that can confirm it without an LLM:<br>• `no_feedback` → CG-03 at the same step. If CG-03 passed and the change was visible, the unit becomes `agent_misperception_candidate`.<br>• `dead_end` → **NV-01**: on a task-path screen, the only visible interactive elements are back, close or home, or there are none (P2, measured).<br>• loop → **NV-02**: ≥ 3 returns to one `screen_key` in a run without new state (model basis, P3, needs 2 channels).<br>• `error_unclear` → **ER-01**: an error text appears after submit, the invalid field has no `aria-invalid`, `aria-describedby` or `aria-errormessage` link, and the text is > 48 CSS px from the field (P2).<br>• `label_mismatch` → **LN-01**: the accessible name does not contain the visible label (P2).<br>A unit whose twin fires is reported under the twin. The rest stay judgment. | AXNav: agents navigate, heuristics flag (text not growing with Large Text, VoiceOver loops), humans review the video [snippet]. Explicit verification: 90 % recall at 4.5 % FPR [paper, preprint, README]; open-ended audits ~80 % wrong [snippet]. WCAG 2.5.3 Label in Name and 3.3.1 Error Identification [standard; text not re-read at the time of writing]. | **Recall:** ↑ for dead-end, feedback, error and label defects, also in scripted runs with no agent. **Noise:** ↓ relative to PJ. **Basis:** upgraded from judgment to measured. | **H:** ≥ 40 % of judged-real PJ units in the pilot have a twin, and twin precision on clean controls is ≥ 0.8. **Pass:** implement the twins and restrict PJ-01 to units without one. **Data:** pilot PJ units plus the dev suites. | M |
| LAT-10 | CHANGE | **Split declared expectations (PJ-02) from open-ended confusion (PJ-01).**<br>• Scenarios may declare `expect` per step or goal, e.g. `{"after_action": 3, "screen_contains": "주문 확인", "within_ms": 2000}`, `success_selector` or `success_text`.<br>• Machine-checkable expectations are checked by the driver (basis measured). The rest are compared against the operator's `observed` by the blind analyst of LAT-11.<br>• **PJ-02** (a violated declared expectation) reaches P2 when deterministic, and P2 when corroborated otherwise.<br>• **PJ-01** (an open-ended mismatch) is a hypothesis unless corroborated, and at most P3.<br>• Expectations come from briefs or specs, never from defect lists. This complements STF-11 (a named oracle). | Requirement-oriented verification: 94 % accuracy [snippet], 90 % recall at 4.5 % FPR [paper, preprint, README]. Open-ended audits found 14–26 % of issues with ~80 % wrong suggestions [snippet]. Only 58 % of agent-invented tasks were realistic (DroidAgent) [snippet; derived]. | **Noise:** ↓ (open-ended notes demoted). **Recall:** ↑ for flows covered by expectations. | **H:** judged precision is ≥ 0.7 for PJ-02 and ≤ 0.4 for PJ-01. **Pass:** keep the split; headline metrics count PJ-02 only. **Data:** pilot flows with expectations written from briefs by someone blind to the defects. | M |
| LAT-11 | CHANGE | **Neutral operator, blind analyst.**<br>• The operating agent gets a neutral user prompt: the goal, the data, and "before each action, state what you expect; after it, state what you see". No QA framing, no "find problems", no persona adjectives, no `confusion` flag.<br>• A separate analyst (another family or channel when allowed) reads, per step, only the (expected, observed) pair, the before/after screenshots and the anchor, and assigns a `mismatch_type` or none.<br>• Leading questions ("Was this confusing?") are banned. | Sycophancy is general, and convincing sycophantic answers are sometimes preferred over correct ones [snippet]. Synthetic users were sycophantic and over-reported success (NN/g) [snippet]. Judges show position, verbosity and self-enhancement bias [snippet]. | **Noise:** ↓ (priming-induced confusion disappears). **Recall:** ≈ or slightly ↓. | **H:** neutral operator + analyst cuts clean-control PJ units by ≥ 30 % and loses ≤ 1 matched defect against the current prompt. **Data:** 2 arms × 2 channels × 3 seeds on ≥ 8 pilot scenarios. Cross with UEM-20 (the pre-action note) as a 2 × 2 if the budget allows. | S–M |
| LAT-12 | CHANGE | **Replay and input perturbation instead of product rewording.**<br>• **(a) Replay.** Re-execute each PJ unit's action prefix twice in `run` mode on the same device. The unit survives if the anchor reappears (same `screen_key` and selector) both times; otherwise it is `flaky_or_environment`.<br>• **(b) Perturb the agent's inputs, not the product:** a goal paraphrase, a screenshot scaled 0.9× or 1.1×, a new seed. The verdict must hold in ≥ 2 of 3.<br>• On real surfaces, this replaces protocol §5's "reworded copy, reordered elements": you cannot reword the product under test, and rewording a label changes the thing being judged. Product-side variants stay for fixtures only. STF-14's persona-label swap is kept. | TestGen-LLM surfaced only filtered candidates: 75 % built, 57 % passed reliably, 25 % raised coverage, and 73 % were accepted [snippet]. Repeated runs of the same NL test were inconsistent [snippet]. | **Noise:** ↓. **Recall:** ≈, because stable issues survive. | **H:** ≥ 10 % of PJ units fail replay or perturbation, and ≥ 70 % of those are judged not real. **Pass:** survival becomes a gate for the finding tier. **Data:** pilot PJ units. | M |
| LAT-13 | CHANGE | **Spend the agent budget on model and channel diversity, not personas.**<br>• Default panel per scenario: 4 runs = 2 families × {screenshot, screenshot+a11y}.<br>• Under the Claude-only rule: {Opus, Sonnet} × both channels, labelled `panel_independence: low`.<br>• Add a first-use run only for onboarding flows, or when `familiarity` is a declared condition.<br>• Add runs in pairs, stop by UEM-06, cap at 12. | Identical agents are one vote [derived: protocol §5]. A cross-family 3-model panel beat one large judge at > 7× lower cost [snippet]. Persona effects are small [snippet]. Grounding differs by channel [snippet]. | **Recall per run:** ↑ (independent views). **Noise:** ↓ (corroboration becomes possible). **Cost:** unchanged. | **H:** at 8 runs per scenario, family × channel diversity matches at least as many `agent_judgment` defects as 8 personas on one model and channel, with no more clean-control units. **Metrics:** matched defects, corroborated units, accumulation curve. **Data:** pilot scenarios. | M |
| LAT-14 | ADD | **A calibrated judge panel for adjudication (§3.3).**<br>• 3 judges, ≥ 2 families when allowed, temperature 0.<br>• Judges are blind to source, detector, severity, agent narrative, model identity and other votes. They get an evidence card only.<br>• Two stages: an independent look, then a claim check. Pairwise severity comparisons run in both orders. A padding test checks verbosity.<br>• Deploy only after calibration passes. Verdicts demote, never delete; they never raise severity; measured standard violations stay. | GPT-4 judges agree with humans > 80 % of the time (the human–human level) but show position, verbosity and self-enhancement bias [snippet]. PoLL [snippet]. AgentRewardBench: 1,302 trajectories, 12 judges, none best everywhere, and rule-based checks under-report success [snippet]. Sycophancy [snippet]. Round 2 as pre-registered: 2 Opus judges who see screenshot, element and rule [derived]. | **Measurement:** precision becomes estimable; today it is a lower bound of 0.34. **Noise:** ↓ in the default report once `not_real` units move to the appendix. | **H:** the panel reaches κ ≥ 0.6 with human consensus (and ≥ human–human κ − 0.1); specificity ≥ 0.9 on decoy findings; sensitivity ≥ 0.8 on strictly matched seeded defects; order-swap consistency ≥ 0.9; verdict flips ≤ 5 % under padding. **Data:** a dev-suite calibration set (matched findings = positives, decoy flags = negatives) plus ≥ 100 human-labelled units. | M |
| LAT-15 | ADD | **Correct precision for judge error.** Report `precision_corrected = (p_obs + spec − 1) / (sens + spec − 1)` (the Rogan–Gladen estimator), clipped to [0, 1], with a bootstrap 95 % CI that resamples both the units and the calibration set. Stratify by basis and by tier. | A standard misclassification correction [derived; formula from memory, check before use]. The current labelled precision of 0.34 is a lower bound [derived]. | **Usefulness:** honest precision. Detection is unchanged. | Instrument change. **Pass:** CI half-width ≤ 0.1 with ≥ 150 judged units. | S |
| LAT-16 | KEEP (tighten) | **Judgment never reaches P1, and agent success is run health, not usability.**<br>• PJ ≤ P3. P2 only when computed-corroborated and replay-verified. P0 or P1 only through a measured twin.<br>• Agent success, grounding errors and step counts are reported per model as run health, never as "x % of users fail".<br>• STF-19's `fail_ux` needs a twin, or corroboration at the same anchor. | Aggregators list agents above the OSWorld human baseline (≈ 86 % vs 72.36 %; self-reported) [snippet; industry]. Next-action accuracy was 11.86 % [snippet]. Agent A/B reproduced a direction only (414 vs 403: z = 0.90, p ≈ 0.37 at an assumed 500 per arm) [snippet; derived]. | **Noise:** ↓. **Usefulness:** ↑ (no false quantitative claims). | Policy. A report linter rejects percentages next to agent outcomes. | S |
| LAT-17 | CUT (from the default path) | **Post-run interviews and the experience board.** Both become opt-in, for generating hypotheses only. Their output goes in an appendix labelled "simulated discourse", never in findings, counts or summaries. | Agents out-scored human role-players on believability (29.89 vs 22.95); plausibility is not fidelity [snippet]. Next-action accuracy was 11.86 % [snippet]. Synthetic users over-report success [snippet]. The protocol already bars interviews as sole support [derived]. | **Recall:** 0 change (by rule they cannot create findings). **Noise and cost:** ↓. | **H:** interview-only hypotheses lead to < 1 confirmed finding per 10 scenarios. **Metric:** trace each confirmed finding to its origin. **Pass:** stay default-off. | S |
| LAT-18 | CUT | **The `/note.severity` field.** Remove it, or ignore it and never display it. | It is accepted and validated but unused [derived: serve.mjs L15, L88; checks.py]. An agent's severity guess anchors reviewers [opinion]. | No effect on detection; less clutter. | None. Check that no consumer reads it. | S |
| LAT-19 | ADD | **Acceptance rate on real products.** Use STF-02 `disposition` and report acceptance (confirmed and fixed or scheduled) per basis, tier and corroboration status. | GPTDroid 35/53 and VisionDroid 19/29 new bugs confirmed and fixed (66 % each) [snippet; derived]. TestGen-LLM: 73 % accepted [snippet]. Meituan: 4 new bugs in 10 regression runs [snippet]. | **Usefulness:** a signal from outside synthetic suites. | **H:** corroborated PJ acceptance ≥ 0.5 and uncorroborated ≤ 0.25, over ≥ 30 adjudicated findings. **Pass:** PJ stays in the main report; otherwise it moves to the appendix. | S (after STF-02) |
| LAT-20 | KEEP | **Scenario-declared goals with concrete data; agents never invent tasks.** | Only 58 % of DroidAgent's self-generated tasks were realistic [snippet; derived]. The persona trial never reached a transfer-limit branch without concrete amounts [derived: validation-and-limits.md]. | **Recall:** ↑ (branches reached). | Covered by LAT-04: success by goal specificity. | — |
| LAT-21 | KEEP | **Ergonomics are computed; LLM ergonomic statements are discarded.** | LLMs have no motor noise, fatigue or perceptual limits [opinion]. Hyper-accuracy distortion [paper]. Persona bias [snippet]. LLM audits ~80 % wrong [snippet]. | Removing this rule would add noise with no validity. | The LAT-06 leakage audit doubles as a regression check. | — |
| LAT-22 | KEEP | **Real surface, simulated operator, read-only isolation.** | WW runs bots on Meta's real infrastructure for reliability, integrity and privacy work [snippet]. Its isolation details were not verified. | — | — | — |
| LAT-23 | KEEP | **Novelty control for well-known products.** Use relabelled or reshuffled builds for first-use claims; otherwise set `novelty: unknown`. | Hyper-accuracy distortion [paper]. Agents beat benchmark humans [snippet], so they know common products and conventions [opinion]. | **Noise:** ↓ for first-use claims. | **H:** flows of famous products produce fewer first-use units than relabelled clones. **Pass:** if they do not, drop the control. | S |
| LAT-24 | KEEP | **No agent questionnaires; coverage, not prevalence.** | Synthetic users claimed completing every course (NN/g) [snippet]. UXAgent collects agent questionnaires but was evaluated by 5 UX researchers, not against human answers [snippet; paper, preprint, README]. The 85 % normalized accuracy required a 2-hour interview per person [snippet]. | — | — | — |

### 3.2 Persona-conditioning ablation protocol (LAT-05)

**Design.**
- **Scenarios:** ≥ 8 pilot scenarios with task-flow defects and their clean
  controls. Heldout-2 is used only through a dated amendment.
- **Arms:** N, C, F and F+V as in LAT-05.
- **Replicates:** 3 seeds per arm × 2 families (under Claude-only, 2 channels) →
  24 runs per scenario variant, or 384 runs at ≤ 25 steps each. A cheaper
  variant drops F+V: 288 runs.
- **Controls:**
  - the same model version, temperature, step cap, goal wording and data;
  - a randomized run order;
  - the persona block is the only difference, and its `prompt_sha256` is
    recorded (LAT-02).

**Metrics.**
- **M1, behavioural divergence.**
  - Each action is a token (action type, resolved selector or `screen_key`).
  - The distance between two runs is d = Levenshtein(a, b) / max(|a|, |b|).
  - D_w is the within-arm distance between seeds; D_b is the between-arm
    distance.
  - Effect = median D_b(N, F) − median D_w.
  - Significance comes from a permutation test that shuffles arm labels within
    each scenario × family (10,000 permutations).
- **M2, outcome.** Success, steps to success and backtracks. A mixed logistic
  regression: success ~ arm + (1 | scenario) + (1 | family).
- **M3, detection.** Per `agent_judgment` defect, whether each arm detected it
  (any anchored unit at its selector on the defect variant). McNemar between
  arms, plus the paired anchor Δ of LAT-04 per arm.
- **M4, noise.** PJ units per clean-control run, and the judged-real share.
- **M5, leakage.**
  - The share of notes with body, ability or age claims.
  - Regex seeds:
    - Korean: "손이 떨", "눈이 잘 안", "글씨가 작아", "나이", "노안", "왼손이라",
      "걸으면서";
    - English: "my eyes", "my hands", "too small for me", "hard to reach",
      "as an older".
  - Each match is confirmed by a classifier. Abstentions and refusals are also
    counted.
- **M6, cost.** Tokens and wall time per run.

**Decision rules** [opinion]:
- **Behaviour.** Persona conditioning "changes behaviour" if the M1 effect is
  ≥ 0.10 with p < 0.05 in at least half of the scenarios.
- **Detection.** Keep an arm richer than N only if it also wins on M3 (≥ +1
  matched defect in both families or channels), stays within +10 % on M4, and
  keeps M5 ≤ 1 %.
- **Behaviour without detection.** If personas change paths but not detection,
  they buy path diversity that seeds or channels buy more cheaply. Compare
  D_b(N, F) with D_w across families.
- **Power.** With about 10–15 `agent_judgment` defects, McNemar detects only
  large differences. When evidence is absent, the rule defaults to the cheaper
  arm, N.

### 3.3 Judge design for adjudicating findings (LAT-14, LAT-15)

**Scope.** Round-2 precision estimation for all bases, and optional triage in
product reports. Judges demote; they never delete and never raise severity.

**Card shown to each judge.**
- The rule text and threshold (measured or model checks); the declared
  expectation (PJ-02); or the (expected, observed) pair only (PJ-01).
- The full screenshot with the anchor box, a 2× crop of the anchor, and the
  before/after pair for feedback and timing checks.
- The measured value, and the profile differential only when the rule depends on
  it.

**Never shown.** The detector's severity, the check name's wording, the agent's
narrative or rationale, model identities, other judges' votes, or the answer key.

**Procedure.**
1. **Independent look.** "Describe any problem a user doing <task> would have at
   the boxed element. Answer NONE if there is none."
2. **Claim check.** "Claim: <rule-based statement>. Verdict: real, not_real or
   cannot_tell. Cite the evidence ids."
3. **Framing check.** A unit judged NONE in stage 1 and real in stage 2 is
   `framing_sensitive`, and counts as cannot_tell unless its basis is measured
   [opinion, motivated by sycophancy §2.3].

**Panel.**
- Three judges from ≥ 2 families. The verdict is the majority of non-abstaining
  judges; a tie is cannot_tell.
- Under the Claude-only rule, use three different Claude models, or one model
  with three evidence framings (screenshot-only, DOM excerpt, rule-first), and
  record `panel_independence: low`.

**Bias controls.**
- Randomize the order of units.
- Run every pairwise severity comparison in both orders and keep only
  consistent results.
- On 10 % of cards, add 150–200 tokens of plausible but irrelevant text. Flips
  must stay ≤ 5 %.

**Calibration before deployment.**
- Positives: dev-suite findings strictly matched to seeded defects.
- Negatives: findings on decoy elements, plus human-labelled invalid units.
- Human labels: ≥ 100 units, 2 raters, with human–human κ reported as the
  ceiling.
- Deploy when κ(panel, human consensus) ≥ 0.6 and ≥ human–human κ − 0.1,
  specificity ≥ 0.9 and sensitivity ≥ 0.8. Otherwise judges only sort review
  queues [opinion].

**Estimation.** Rogan–Gladen-corrected precision (LAT-15), with a bootstrap CI.

### 3.4 What the model experiment on `claude/admiring-goldberg-llu3f5` should report

That session asked for task success per model, grounding failure types and the
`failure_class` distribution. To make those numbers usable here, report per model
× channel:

1. task success on **clean controls** (agent capability);
2. the **paired anchor Δ** on defect variants (defect sensitivity). This is the
   selection metric, not success;
3. grounding errors per 100 actions by target kind (text button, icon-only, form
   field, canvas hotspot) and by LAT-07 class;
4. a confusion matrix of the agent-claimed `failure_class` against the class
   computed by LAT-08 rules or adjudication;
5. PJ units per clean-control run, and the judged-real share;
6. leakage notes (body or ability claims) per 100 notes;
7. repeat consistency: the Jaccard overlap of anchored units across 3 seeds;
8. tokens, wall time per step, and cost per matched defect;
9. the LAT-02 `agent` block for every run.

**Selection rule** [opinion]: choose the cheapest model whose paired Δ is within
0.05 of the best and whose clean-control units are not higher. A model that
succeeds more often is not better for this purpose if its Δ is lower: success
measures the agent, and Δ measures the product.

### 3.5 Order of work

1. **Before the heldout-2 freeze:** LAT-01, LAT-02, LAT-03, and a two-channel C6
   panel. If they cannot land in time, amend the pre-registration instead.
2. **Pilot:** the LAT-04 harness with LAT-07 telemetry and LAT-08. Run LAT-05,
   LAT-11 and LAT-13 as one factorial where possible.
3. **Evidence upgrades:** LAT-09 twins and LAT-10 expectations.
4. **Judge work:** LAT-14 and LAT-15. These can start now on the existing
   deterministic findings.
5. **Remaining items:** LAT-12, LAT-17, LAT-18 and LAT-19.

---

## 4. Risks, open questions and what could not be verified

### 4.1 Unverified or partly verified

- **Every [snippet] number.** In particular:
  - Park et al. 2023: TrueSkill values and diffusion counts.
  - Park et al. 2024: the 85 % figure and the group-bias result.
  - Hu & Collier: "< 10 %".
  - Gupta et al.: 80 %, 70 %+ and 58 %.
  - The "helpful assistant" persona study: the conclusion flipped between versions.
  - NN/g: study details.
  - Baymard: my recomputation gives 13.6 % and 23.6 % coverage, against the
    reported 14–26 %.
  - Agent A/B: arm sizes. My significance test assumes 500 per arm.
  - uxCUA: all figures.
  - GPTDroid, VisionDroid, AutoDroid and DroidAgent: all figures.
  - AUITestAgent: the 94 % figure and the Meituan deployment. The 90 % and 4.5 %
    figures were read in the README.
  - WebArena: the early-stop characterisation.
  - SeeAct: 51.1 % and 20–25 %.
  - OSWorld: 72.36 % and 12.24 %.
  - OSWorld-Verified 2026: from an aggregator, self-reported, some best-of-N.
  - TestGen-LLM, Zheng et al. 2023 (> 80 %), PoLL, AgentRewardBench.
- **Not obtained at all.**
  - Argyle et al.'s correlation values.
  - QTypist's numbers (title and venue from memory).
  - VisionDroid's precision and recall.
  - Mind2Web accuracies.
  - Zheng et al. 2023's position-consistency rates.
  - WW's isolation mechanisms (from memory).
  - The alternative-annotator-test procedure.
- **From memory.** The Rogan–Gladen formula, and the WCAG 2.5.3 and 3.3.1 texts
  (not re-read at the time of writing).
- **Code facts** were read at `b913831` and re-checked at `a413015` (root and
  `skills/remorsearch-ux-qa/` copies). They can change. Line numbers are
  approximate after later edits.

### 4.2 Risks of the recommendations

- **Circularity.** Claude wrote the heldout-2 defects; the agents and judges are
  Claude too [derived: pre-registration]. Agent-detectable defects written by an
  LLM may be exactly those LLMs notice, which inflates PJ recall. Validate on
  human-authored or real regression defects.
- **Family independence is partial.** Models from different providers share web
  training data. PoLL's evidence is on text evaluation, not GUIs [opinion].
- **Identity.** Cutting persona conditioning can look like losing the "swarm".
  Persona facets still drive the deterministic swarm, which is where the
  validated recall comes from [derived; opinion].
- **Twin noise.** Twins bring their own false positives: decorative elements with
  click handlers, SPA updates outside the viewport. They need role filters and
  CG-03's visibility rule [opinion].
- **Affordance leaks.** Describe-then-ground crops can reveal what is clickable.
  Restrict them to visible regions and never label interactivity [opinion].
- **Model drift.** Agent behaviour changes across versions. Re-run LAT-04 on
  every model change, using LAT-02's `model_version` [opinion].
- **Rising competence.** As models improve, agent confusion at real defects may
  disappear (hyper-competence). The layer's value for finding novice confusion
  may then fall while its value for exploration rises [opinion].
- **Language and population.** Most of this literature is English-language, and
  several samples are from the US [snippet; opinion]. Korean copy-comprehension
  units need Korean-capable families, and eventually Korean users.
- **The paired design's assumption.** The paired clean-control design assumes
  the two variants differ only by the seeded defect [derived: spec §12].
- **Cost.** The §3.2 factorial is about 300–400 agent runs.

### 4.3 Open questions

- **Element-level validity.** Does agent confusion at an element predict human
  confusion at the same element? I found no element-level study. The closest
  evidence is site-level preference agreement (uxCUA, AUC 0.607) and directional
  A/B agreement (Agent A/B).
- **Persona effects on GUIs.** Does persona conditioning change GUI navigation
  at all? §3.2 is built to answer this.
- **Trained user models.** Would a small user model trained on real behaviour
  (Customer-R1 or PerceptUI style) beat prompting for Korean mobile commerce? It
  would need real click data, which this project does not have.
- **Screen-reader users.** Is the accessibility-tree channel a useful proxy for
  screen-reader users? AXNav shows agents can drive VoiceOver. "Are We There
  Yet? Assessing Computer-Use Agents for Blind Users' Accessible Interaction with
  Desktop Applications" (arXiv 2609.00524) was seen only as a title.
- **Titles seen but not read, possibly relevant to aggregate-level validity:**
  - "Large language models can predict the results of social science
    experiments" (*Nature*, 2026);
  - "This human study did not involve human subjects: Validating LLM simulations
    as behavioral evidence" (arXiv 2602.15785);
  - "Benchmarking LLM Judges for Mobile Agent Evaluation" (arXiv 2608.11434).
- **Judge calibration data.** What is the cheapest way to build a Korean
  human-labelled calibration set (≥ 100 units, 2 raters) for LAT-14?
