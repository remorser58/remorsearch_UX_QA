# LLM persona simulation: validity, MiroFish-style swarms, and design rules for an ergonomic persona swarm

Research brief, 2026-09-28. Scope: what a MiroFish-style "persona swarm" can and cannot tell us when it
looks at the screen and operates web, app and game UIs, and how to build human factors into it.

## How to read the evidence tags

Network note: when this was written (October 2026), page fetches could reach only `github.com` / `raw.githubusercontent.com`.
arXiv, Hugging Face, ACM DL, Nature, Semantic Scholar, ACL Anthology and project `*.github.io` pages were
blocked by the egress proxy. Web search was rate-limited partway through the work. So the tags below
matter:

| Tag | Meaning |
|---|---|
| **[V]** | Verified at the time of writing from a primary artifact: repo README, source code or leaderboard data file. |
| **[S]** | Seen only in search-result snippets of the primary page (abstract/ACM/arXiv listing). The wording is probably right, but I did not read the full text. |
| **[2nd]** | Secondary source (news, blog, third-party paper summary). |
| **[M]** | From prior knowledge; not re-verified at the time of writing. **Treat any number carrying [M] as unconfirmed** until someone checks the primary source. |

Vendor or self-reported benchmark numbers are marked "self-reported" no matter which tag they carry.

---

## 1. Summary

1. **MiroFish is a pipeline around CAMEL-AI's OASIS, not a validated forecaster.** Its five stages are
   seed material → GraphRAG knowledge graph in Zep → LLM persona generation → parallel OASIS simulation
   of X/Twitter and Reddit → ReACT ReportAgent, followed by chat with individual agents [V].
   - Its README gives demos only, with no accuracy benchmarks [V].
   - Third-party commentary notes that no predictions have been compared against real outcomes [S].
   - The ReportAgent prompt tells the model that the simulation "is not experimental data but a
     rehearsal of the future" and that agent behaviour *is* the prediction of how future crowds will
     behave [V: `report_agent.py`].
   - Simulated agent activity is written back into the same Zep knowledge graph as the seed facts.
     The episode text deliberately carries no "simulated" prefix; provenance survives only as episode
     metadata [V: `zep_graph_memory_updater.py`].
   - Demographics (age, gender, MBTI, country) and activity parameters are made up by the LLM [V].
   - **Takeaway:** these are the patterns our swarm must *not* copy.
2. **LLM usability-testing agents are good at exploring and generating hypotheses; they are weak
   models of human behaviour.**
   - UXAgent (CHI EA 2025) reads a simplified DOM. Its evaluation was a heuristic review by five UX
     researchers, not a comparison with real users [S].
   - On real shopping sessions, prompted frontier LLMs predicted the next human action with only
     about 11.7–11.9% accuracy; fine-tuning raised this to 17.26% [S].
   - Agent A/B (1,000 agents on Amazon) reproduced only the *direction* of a real A/B result
     (414 vs 403 purchases) [S].
3. **The critique literature is consistent.** LLM stand-ins:
   - misportray and flatten identity groups (Nature Machine Intelligence 2025) [M];
   - caricature some personas and topics (CoMPosT, EMNLP 2023) [V repo / M findings];
   - lean WEIRD and toward particular US subgroups [M];
   - show hyper-accuracy distortion (they know "too much") [V abstract];
   - herd more readily than humans (OASIS) [2nd];
   - match human starting points but not dynamics (SILICA, Aug 2026) [S];
   - produce plausible narratives that miss empirical regularities (urban mobility, Jun 2026) [S].

   They also have no body: no motor noise, no fatigue, no human perceptual limits, and no
   human-scale reaction time.
4. **Ergonomics can be simulated, but by deterministic or RL-trained human-performance models, not
   by role-play.**
   - Computational-rationality models reproduce human-like behaviour from explicit bounds:
     touchscreen typing (Jokinen et al. CHI 2021 [M]; CRTypist CHI 2024 [V]), muscle-actuated
     biomechanics (User-in-the-Box UIST 2022 [V]) and VR testing (SIM2VR UIST 2024 [V]).
   - They are heavy to train. CRTypist's supervisor policy trains for about 2×10^7 timesteps [V].
   - For a QA swarm, the practical route is to inject closed-form or parametric models (Fitts/FFitts,
     thumb functional area, KLM, Hick-Hyman, WCAG geometry) as tools the driver calls. The LLM picks
     *intent*; the model computes *consequence*. Heavy RL simulators serve as offline calibrators.
5. **GUI agents can now operate most UIs, but their failures are not user failures.**
   - ScreenSpot-Pro grounding went from 0.8% (GPT-4o) to 82.7% at the top of the leaderboard.
     Icons still trail text (70.4% vs 90.4% for the leader) [V].
   - OSWorld: self-reported scores are about 70–80% against a human baseline of about 72% [V].
     Some of those scores use best-of-N selection.
   - AndroidWorld: the best pure-vision agent scores 76.7% (Jan 2026, self-reported) [V].
   - Real-time games remain very hard for VLM agents, which need the game to pause while they think
     [V README; M numbers].
6. **Consequences for the swarm:**
   - Keep strict role separation between measured, model and judgment findings.
   - Report counts as coverage, never prevalence.
   - Treat N same-model agents as one correlated rater.
   - Quarantine and label any simulated social discourse.
   - Tag every failure as a UX issue, an agent limitation, or unknown before it becomes a finding.

---

## 2. MiroFish and OASIS architecture (plus related Chinese work)

### 2.1 MiroFish (github.com/666ghj/MiroFish)

**Identity**
- "A Simple and Universal Swarm Intelligence Engine, Predicting Anything" (简洁通用的群体智能引擎，预测万物) [V].
- License AGPL-3.0 [V].
- About 75.2k stars and 11.6k forks on 2026-09-28 [V: GitHub page fetch].
- "Strategic support and incubation from Shanda Group" [V].
- Built by Guo Hangjiang, a BUPT undergraduate who also wrote the earlier BettaFish public-opinion
  analyser [2nd: 36Kr, TMTPost, PANews].
- Reported as built in about 10 days and funded with 30 million RMB by Chen Tianqiao [2nd].
- Topped GitHub global trending on 2026-03-07 [2nd].
- A v0.1.0 date of December 2025 appears in one commentary [2nd, unconfirmed].

**Pipeline**

The README workflow [V]:
1. **Graph Building**: seed extraction, individual/collective memory injection, GraphRAG construction.
2. **Environment Setup**: entity-relationship extraction, persona generation, agent configuration injection.
3. **Simulation**: dual-platform parallel simulation, auto-parsing of prediction requirements, dynamic temporal memory updates.
4. **Report Generation**: a ReportAgent with a rich toolset.
5. **Deep Interaction**: chat with any agent in the simulated world, and with the ReportAgent.

Backend services, from the repo tree [V]: `ontology_generator.py`, `graph_builder.py`,
`zep_entity_reader.py`, `oasis_profile_generator.py`, `simulation_config_generator.py`,
`simulation_runner.py` / `simulation_manager.py` / `simulation_ipc.py`,
`zep_graph_memory_updater.py`, `zep_tools.py`, `report_agent.py`.

**Stack** [V]
- Python 3.11–3.12 backend, Node 18+ frontend.
- Any OpenAI-compatible LLM; the README recommends Alibaba `qwen-plus`.
- Zep Cloud for graph memory.
- The README warns of "high consumption, try simulations with fewer than 40 rounds first".

**Persona generation** (`oasis_profile_generator.py`) [V]
- Entity nodes from the Zep graph become OASIS profiles.
- The LLM generates a "very detailed persona" (非常详细的人设): a 2000-character persona text
  (详细人设描述（2000字的纯文本）), plus `age`, `gender`, `mbti`, `country`, `profession` and
  `interested_topics`.
- Institutional entities (universities, media outlets, NGOs) get placeholder demographics.
- Follower and status counts can come from `random.randint` fallbacks.
- **The demographics are not sampled from any population.** They are the LLM's guesses about an
  entity named in the seed text.

**Simulation configuration** (`simulation_config_generator.py`) [V]
- The LLM sets per-agent `activity_level`, `posts_per_hour`, `comments_per_hour`, `active_hours`,
  `response_delay`, `sentiment_bias` (−1..1), `stance`
  (`supportive|opposing|neutral|observer`) and `influence_weight`.
- Time defaults assume Chinese daily rhythms (Beijing time): `total_simulation_hours=72`,
  `minutes_per_round=60`, `peak_hours=[19,20,21,22]`, `off_peak_hours=[0..5]`.
- Platform recommender constants are fixed:

  | Platform | recency | popularity | viral_threshold | echo_chamber_strength |
  |---|---|---|---|---|
  | X/Twitter | 0.4 | 0.3 | 10 | 0.5 |
  | Reddit | 0.3 | 0.4 | 15 | 0.6 |

- A rule-based fallback applies when the LLM fails.
- **None of these parameters is calibrated to observed platform data in the repo.**

**Memory write-back** (`zep_graph_memory_updater.py`) [V]
- The updater tails the simulation action log and turns each action (`CREATE_POST`, `LIKE_POST`,
  `REPOST`, `FOLLOW`, …) into natural-language text such as `[t] [twitter round r] Name: 发布了一条帖子：「…」`.
- It then calls `graph.add` on the same graph that holds the seed facts.
- The docstring says the text deliberately omits any simulation prefix "to avoid misleading graph
  updates" (不添加模拟相关的前缀，避免误导图谱更新).
- Provenance is kept only in episode metadata (`source: "mirofish_simulation"`, `simulation_id`,
  rounds, agent ids).
- I did not verify whether this provenance reaches the entity/edge "facts" that the ReportAgent
  later retrieves. `zep_tools.py` labels retrieved content as 【当前有效事实】(模拟结果原文) ("currently
  valid facts (simulation-result original text)") [V].

**ReportAgent** (`report_agent.py`) [V]
- A ReACT loop per report section: `max_iterations = 5`, `min_tool_calls = 3`,
  `MAX_TOOL_CALLS_PER_SECTION = 5`, `MAX_REFLECTION_ROUNDS = 3`.
- Tools: `insight_forge` (decomposed deep retrieval), `panorama_search` (full event trajectory),
  `quick_search`, and `interview_agents` (live interviews of simulated agents on both platforms).
- Good constraints: 禁止捏造数据 (no fabricated names, quotes, statistics or interaction data), and a
  ban on using the model's own knowledge.
- **Framing:** it writes a 「未来预测报告」 (future-prediction report) from a 「上帝视角」 (god's-eye
  view). It is told:
  > 你正在观察的不是"实验数据"，而是"未来的预演"

  ("What you observe is not 'experimental data' but 'a rehearsal of the future'") and
  > Agent的行为和互动，就是对未来人群行为的预测

  (agents' behaviour and interactions *are* the prediction of future population behaviour).

**Published validation**
- None found. The README offers only demos: a Wuhan University public-opinion case and a "lost
  ending" of *Dream of the Red Chamber*. Financial and political prediction examples are listed as
  "coming soon" [V].
- Commentary (LinkedIn, blocmates) states that there are no benchmarks against historical outcomes
  and that the demos illustrate the approach without evidencing accuracy [S].
- I found no peer-reviewed or preprint evaluation of MiroFish forecasts. Given the network limits,
  that is "not found", not "does not exist".

**What is worth borrowing** (architecture, not epistemics):
- seed → knowledge graph → entity-grounded scenarios;
- parallel multi-surface runs (web, app, game instead of X and Reddit);
- a report agent restricted to tool retrieval and forbidden from fabricating;
- a post-run debrief of individual agents.

**What must not be borrowed:**
- prediction framing;
- LLM-invented demographics and MBTI;
- LLM-set behavioural parameters presented as realistic;
- writing simulated discourse into the evidence store without a text-level label.

### 2.2 OASIS (camel-ai/oasis; arXiv 2411.11581)

**Scale and actions** [V README]
- Supports "up to one million agents".
- The README lists 23 actions: follow, comment, repost, like/dislike, search, trend, refresh, mute,
  report, quote, group chat and others. A third-party summary of paper v4 counts 21 actions [2nd].
  The number grew over versions.
- Two recommender types, interest-based and hot-score-based. Platforms X and Reddit. Apache-2.0.
- Arxiv v1 is dated 2024-11-18; v5 is 2025-03-23 [S].

**Architecture** [2nd: cognitivetech summary of v4]
- Environment Server: a relational DB of users, posts, comments, relations, traces and recommendations.
- RecSys: X uses in-/out-of-network posts ranked with TwHIN-BERT; Reddit uses hot score.
- Agent Module, Time Engine and Scalable Inferencer.

**Reported validation** [2nd unless noted]
- Information-propagation replication against real X cascades had an "RMSE error margin around
  30%", and simulated cascade *depth* ran smaller than the real trend.
- Group polarization appeared, and opinion diversity grew with more agents.
- **Herd effect: "agents are more likely to exhibit herd effect than humans".** It became explicit
  when agents were scaled from 100 to 10,000 [2nd; also in search snippet S].
- A secondary summary cites 1M-agent runs needing tens of A100 GPUs and many hours per time step.
  That is unconfirmed [2nd].
- Stated limits: the recommender only approximates the real platforms, agents are abstracted
  individuals, and the environment is text-only.

### 2.3 Related Chinese work

**AgentSociety** (Tsinghua FIB Lab; arXiv 2502.08691; v2 is arXiv 2607.11895)
- More than 10k agents and about 5M interactions in urban, social and economic environments [S].
- Topics: polarization, spread of inflammatory messages, UBI, external shocks (hurricanes) and urban
  sustainability [S].
- Hurricane Dorian case: 1,000 virtual residents of Columbia, SC, and a figure comparing simulated
  vs real daily visits [2nd].
- AgentSociety 2 is an "LLM-native" platform with research skills (hypothesis generation, experiment
  design, paper writing) and replay [V README].
- An independent evaluation of AgentSociety and CitySim against Paris and Shanghai mobility data
  ("When Plausible Is Not Realistic", arXiv 2606.13835) found a "substantial gap between narrative
  plausibility and empirical mobility realism". Trip lengths, origin–destination flows, dwell times
  and transition dynamics were poorly reproduced [S].

**YuLan-OneSim** (RUC GSAI; arXiv 2505.07581; built on AgentScope) [V README]
- Code-free scenario construction, 50+ default scenarios across 8 domains, up to 100,000 agents, and
  feedback-driven fine-tuning of the backbone LLM.
- Validation:
  - an Axelrod cultural-dissemination replication (qualitative);
  - Brazilian housing-price distribution shape, underestimated in the 0.45–0.55 normalized band;
  - LLM-graded "AI Social Researcher" reports: scenario design 4.13/5; report Insightfulness 3.25
    and Practicality 3.00; one report scored 2.0 for practicality.
- Takeaway: the reports automate plumbing well but are weak on actionable insight.

**Persona Hub** (Tencent AI Lab; arXiv 2406.20094) [V README]
- 1 billion personas (about 13% of the world population) curated from web text. A 200k preview and
  370M "elite personas" were released 2025-02-18.
- Intended for synthetic data (math, instructions, NPCs, tools), not for population simulation.
- Disclaimer: "may contain inaccuracies, unsafe content, or biases".
- Contrast with Nemotron-Personas-Korea, which the repo uses because it is built to match Korean
  demographic distributions (per NVIDIA's dataset description; not re-verified at the time of writing [M]).
  Persona Hub is diverse in *perspective*, not calibrated to *population*.

**Microsoft TinyTroupe** (arXiv 2507.09788) [V README]
- `TinyPerson`, `TinyWorld` and `TinyPersonFactory`, plus a `SimulationExperimentEmpiricalValidator`
  that compares simulated and real survey data with t-tests and KS-tests.
- Positioned as "imagination enhancement".
- Disclaimer: "for research and simulation only… We advise using TinyTroupe's outputs for insight
  generation and not for direct decision-making."
- It is a useful precedent for *built-in empirical validation hooks*.

---

## 3. LLM agents for usability testing

| System | Perception / operation | What it produces | Evidence of agreement with real users |
|---|---|---|---|
| **UXAgent**: Lu, Yao, …, Wang (arXiv 2502.12561, CHI EA 2025; demo system arXiv 2504.09407) | "Universal Browser Connector": a custom DOM parser simplifies raw HTML and assigns stable semantic IDs, so the agent reads DOM, not pixels [S]. Playwright/Chromium [V]. Fast/slow dual-process loops linked by a memory stream [S]. | Thousands of personas from weighted demographic choices plus an example persona [V]. Action traces, screenshots, video, agent "interviews", post-task questionnaires such as SUS items [V/S]. | Heuristic evaluation with **five UX researchers**, who praised the approach but raised concerns [S]. No human-behaviour agreement metric in the CHI EA paper as far as the snippets show. The README's default demographics are uniform (for example male/female/non-binary 1:1:1, age "18-55") [V], so sampling weights are design choices, not population estimates. |
| **"Beyond Believability" / "Can LLM Agents Simulate Multi-Turn Human Behavior?"**: Lu et al. (arXiv 2503.20749) | Web shopping pages, real customer sessions | Next-action generation | Prompt-only DeepSeek-R1 **11.86%** and Claude 3.5 Sonnet v2 **11.69%** action accuracy. Fine-tuned Qwen2.5-7B reached **17.26%**, and 33.86% F1 on purchase prediction [S]. "Believable" ≠ accurate. |
| **Agent A/B**: arXiv 2504.09723; CHI EA 2026 (DOI 10.1145/3772363.3799039) | Persona LLM agents on live pages (search, filter, click, purchase) | Simulated between-subjects A/B tests | 1,000 agents on Amazon filter-panel variants: **414 vs 403** purchases, "reproducing directional outcomes" of a parallel human experiment [S]. Direction only, a small difference, one case. |
| **PerceptUI** (arXiv 2606.05697, Jun 2026) | Persona-conditioned prediction of answers to UI questions | Answers plus rationales, fine-tuned on human decisions | Claims "human-level realism" and population-level response distributions; positioned as complement not replacement [S]. Numbers not seen. |
| **uxCUA**: "Training Computer Use Agents to Assess the Usability of GUIs" (arXiv 2604.26020, Apr 2026, UW/Reinecke) | Computer-use agent executing flows | A learned numeric usability score | States that prior CUAs "still struggle to provide accurate usability assessments"; trains on UIs paired with usability labels and human preferences [S]. |
| **Avenir-UX** (arXiv 2604.09581) | Vision/GUI grounding | Automated UX evaluation | Title and abstract only [S]. |
| **TinyTroupe** | Text only (no GUI) | Focus groups, surveys | Validator hooks exist; the README gazpacho and story-device examples compare against real survey data [V]. |
| **Synthetic-user SaaS** (Synthetic Users and others) | Mostly chat or survey | Interview-like transcripts | No independent validation found at the time of writing. Nielsen Norman Group's 2024 "Synthetic Users" article warns that they are shallow, overly positive and cannot show behaviour [M]. |

### DOM vs vision operation: the trade-off that matters for ergonomics

**DOM or accessibility tree** (UXAgent; `uiautomator`/a11y on Android)
- Gives exact element identity, role and geometry, which is ideal for *measurement*.
- But it hands the agent information a human may not perceive: off-screen or low-contrast text,
  aria labels, hidden elements. That gives the agent super-human perception and hides
  discoverability and legibility problems.
- In the AndroidWorld comparisons published by UI-Venus, GPT-4o with an a11y tree scored 30.6%
  [V], so a structured tree does not by itself make an agent capable.

**Pure vision** (UI-TARS, OmniParser "pure vision based GUI agent", MAI-UI)
- Sees rendered pixels, including visual hierarchy, and is the only option for canvas/WebGL games.
- But it adds grounding error that can be mistaken for a UX problem. Icons are the weak spot
  (see §6).
- OmniParser v2 reported 39.5% on ScreenSpot-Pro in Jan 2025 [V README].

**Rule the literature implies:** the persona agent *decides* from what a human could see (a
viewport-only screenshot at device scale, optionally degraded for the profile's vision). The
deterministic layer *measures* from DOM, a11y or uiautomator data. Findings name which channel
produced them.

---

## 4. Validity evidence and critiques

### 4.1 Evidence of partial validity (aggregate or directional)

**Algorithmic fidelity**
- Argyle et al. 2023 (*Political Analysis*, "Out of One, Many"): GPT-3 conditioned on survey
  backstories reproduced several aggregate US political-attitude patterns [M].

**Individual-level simulation from interviews**
- Park et al. 2024 (arXiv 2411.10109): agents built from qualitative interviews with **1,052** people
  replicated GSS answers **85%** as accurately as the participants replicated themselves two weeks
  later [S].
- They beat demographic-only and persona-only agents and reduced accuracy gaps across racial and
  ideological groups [S].
- **Implication:** demographic persona prompts (our Nemotron case) are the *weaker* condition.

**Experiment-effect prediction**
- Hewitt, Ashokkumar, Ghezae and Willer 2024: GPT-4-predicted treatment effects correlated with
  observed effects (r ≈ 0.85 across about 70 US survey experiments) [M, number unconfirmed].
- This concerns aggregate attitude effects, not UI behaviour.

**Directional A/B replication:** Agent A/B, above [S].

**Macro regularities**
- AgentSociety's hurricane mobility dip [2nd].
- YuLan-OneSim's housing-price distribution shape [V README].
- Both are qualitative and figure-level, and both come from the developers themselves.

### 4.2 Critiques and failure modes

| Failure mode | Source | Relevance to a UX persona swarm |
|---|---|---|
| **Misportrayal and flattening of identity groups.** LLMs portray groups as out-groups imagine them and compress within-group diversity; identity prompts also essentialize. | Wang, Morgenstern & Dickerson, *Nature Machine Intelligence* 7 (2025), "Large language models that replace human participants can harmfully misportray and flatten identity groups" [M]. Reported design, unconfirmed: 4 LLMs, 3,200 human participants, 16 US identity groups. They suggest identity-coded names rather than explicit labels and caution that higher temperature does not fix flattening [M]. | Don't let agents "speak as" a demographic ("as a 60-year-old woman I find…"). Use demographics only to choose goals, context and device, and let deterministic models supply the capability differences. |
| **Caricature** (low individuation plus exaggeration) | Cheng, Piccardi & Yang, **CoMPosT**, EMNLP 2023 [V repo]. Political and marginalized-group personas and general topics were most caricatured [M]. Cheng, Durmus & Jurafsky, "Marked Personas", ACL 2023 [M]. | Persona-voiced comments drift toward stereotype. Score or suppress persona-voice text; never quote it as user voice. |
| **Whose opinions:** skew toward particular US groups, especially after RLHF | Santurkar et al. 2023, OpinionQA [V repo; findings M] | Korean personas simulated by US-tuned models inherit a foreign centre of gravity. |
| **WEIRD bias:** similarity to human responses falls with cultural distance from the US | Atari, Xue, Park, Blasi & Henrich 2023, "Which Humans?" [M] | Korean older adults and rural profiles are least likely to be simulated faithfully. |
| **Survey artefacts:** order and label biases dominate; after correction, responses trend toward uniform and track no subgroup | Dominguez-Olmedo, Hardt & Mendler-Dünner, NeurIPS 2024 [V repo; findings M] | Post-task Likert or SUS answers from agents are close to meaningless as scores. |
| **Synthetic survey data:** plausible means, too little variance, prompt-sensitive, drifts over model versions | Bisbee et al. 2024, *Political Analysis* [M] | Pin the model version, re-run across versions, and never report agent SUS means. |
| **Hyper-accuracy distortion:** models answer "too correctly" | Aher, Arriaga & Kalai, ICML 2023: the Wisdom-of-Crowds Turing Experiment revealed a "hyper-accuracy distortion" in ChatGPT and GPT-4 [V abstract] | Agents know UI conventions and famous apps. They find hidden features real novices miss, which produces false negatives. |
| **Diminished diversity of thought** (near-zero variance) | Park, Schoenegger & Zhu 2024, *Behavior Research Methods* [M] | Many agents from one model are not independent samples. |
| **Persona variables explain little** | Hu & Collier, ACL 2024, "Quantifying the Persona Effect" (<10% of annotation variance) [M] | The persona prompt is a weak lever on behaviour. |
| **Herding and faster polarization** | OASIS: agents herd more than humans, increasingly with scale [2nd/S] | Social or discourse simulations overstate bandwagon effects, and bigger swarms make it worse. |
| **Start points match, dynamics don't; memorised results** | SILICA (arXiv 2608.28182, 2026-08-28; OSF pre-registered 2026-08-15): first-round public-goods contributions fell inside the equivalence margin for 8 of 11 models, but **no model matched end-state contributions** [S]. It tests perturbations that re-render the same rules and payoffs that "point away from the memorised result" [S]. | Test stability under superficial re-rendering, and distrust agents on well-known products. |
| **Plausible ≠ realistic** | arXiv 2606.13835 (AgentSociety/CitySim vs Paris/Shanghai) [S] | Narrative "why I did this" is easy; temporal and sequence structure is hard. |
| **Believable ≠ accurate** at the action level | Lu et al. 2025: about 12% next-action accuracy [S] | Individual click paths are not predictions of human paths. |
| **Disembodiment, uniformity, atemporality** | Kozlowski & Evans 2025, "Simulating Subjects" [M]. Anthis et al., ICML 2025 position paper lists diversity, bias, sycophancy, alienness and generalization as open challenges [M]. Larooij & Törnberg 2025 review generative ABMs and find validation mostly absent or face-validity only [M]. | Motivates the deterministic ergonomics layer. |

### 4.3 Behaviours LLM personas simulate poorly, and what should replace role-play

| Human factor | Why LLM role-play fails | Replace with |
|---|---|---|
| **Motor error** (mis-taps, slips, tremor) | Agents click exact element centres or DOM handles; any "fat finger" they report is fiction. | Sample the tap point from a touch-error model (FFitts / Bi-Zhai 2013 σ, plus tremor and walking multipliers) inside the driver. Log the outcome as `basis: model`. |
| **Reach and grip** | No body | Thumb functional-area model (Bergstrom-Lehtovirta & Oulasvirta CHI 2014 [M]) with the device's physical mm size. The repo already has `REF-bergstrom2014` and `REF-hoober2013`. |
| **Movement time and effort** | No kinematics | Fitts/MacKenzie ID→MT, KLM operators for task-time estimates [M: classic KLM operator values], biomechanical sims offline (UitB/SIM2VR) for VR or gesture-heavy game design [V]. |
| **Perception** (acuity, contrast, CVD, glare, banner blindness, visual search) | DOM agents read everything; VLMs see full-resolution pixels without glare or CVD. | WCAG contrast and size geometry (2.5.8 minimum **24×24 CSS px**; 2.5.5 enhanced **44×44 CSS px** [V: w3c/wcag source]), CVD simulation (Machado 2009 [M]), saliency and visual-search models. Optionally feed the agent a *degraded* screenshot, but compute pass/fail deterministically. |
| **Reading and comprehension time** | LLM reads instantly | Reading-speed parameters by age band, with reading time computed not narrated. |
| **Reaction time and timing windows** (QTEs, toasts, auto-dismiss) | LLM steps take seconds; real-time games need pausing (VideoGameBench "lite" mode "pause enabled while model is thinking" [V]). | Measure the window's duration in the driver and compare with Hick-Hyman or simple RT distributions plus movement time. The agent never "decides it was too fast". |
| **Fatigue across a session** | LLM stamina is unlimited; "I'm tired" is theatre. | Accumulate model-based load proxies (far-reach taps, total movement time, repeated precision taps, gaze switches) and report them as load indicators. Treat the fatigue *threshold* as `unknown` unless there is a validated model. |
| **Impatience and abandonment** | Agents persist until the step cap; there is no inherent patience. | Explicit time/step budgets derived from model-predicted human time. AndroidWorld set step budgets to about 2× the human average completion time [V README]. Latency thresholds come from HCI norms (repo `REF-nielsen1993`). |
| **Learning, habit, memory across sessions** | Context window ≠ human memory; famous apps are pre-learned (hyper-accuracy). | Mark `familiarity` as a scenario assumption. Use unfamiliar or perturbed builds for first-use claims. |
| **Social influence** (reviews, community pressure) | Stronger herding than humans (OASIS) | Treat as a hypothesis generator only (see §7.4). |

---

## 5. Ergonomic user simulation that actually models the body and mind

**Computational rationality** (Oulasvirta, Jokinen & Howes, "Computational Rationality as a Theory of
Interaction", CHI 2022 [M])
- Users are modelled as bounded-optimal agents: behaviour is the policy that maximises expected
  utility given explicit perceptual, motor and cognitive bounds and the interface.
- It is solved with RL, so the bounds, not a narrative, generate behaviour. This is the principled
  opposite of persona role-play.

**Touchscreen typing**
- Jokinen, Acharya, Uzair, Jiang & Oulasvirta, "Touchscreen Typing As Optimal Supervisory Control",
  CHI 2021 [M]: a hierarchical model coordinating vision (keyboard vs text), finger and proofreading.
- **CRTypist** (Shi, Zhu, Jokinen, Acharya, Putkonen, Zhai & Oulasvirta, CHI 2024 Honorable Mention,
  DOI 10.1145/3613904.3642918) [V project page]:
  - reformulates typing as supervisory control over a working-memory representation;
  - "works directly from pixels, without requiring hand-crafted feature engineering for keyboards";
  - "aligns with human data in terms of movements and performance, covers individual differences,
    and can generalize to diverse keyboard designs";
  - but is "limited to skilled typists".
  - Training uses separate vision, finger and working-memory modules plus a supervisor policy trained
    for 2×10^7 timesteps, followed by parameter fitting [V repo README].

**User-in-the-Box** (Ikkala, Fischer, Klar, Bachinski, Fleig, Howes, Hämäläinen, Müller, Murray-Smith
& Oulasvirta, UIST 2022, DOI 10.1145/3526113.3545689) [V README]
- A muscle-actuated MoBL-ARMS biomechanical model in MuJoCo with egocentric vision and
  proprioception, trained with RL.
- Tasks: pointing, tracking, choice reaction, and driving an RC car with a joystick.
- Pluggable effort models ("WIP").
- The paper reports emergent Fitts'-law-like pointing [M].

**SIM2VR** (Fischer, Ikkala, Klar, Fleig, Bachinski, Murray-Smith, Hämäläinen, Oulasvirta & Müller,
UIST 2024, DOI 10.1145/3654777.3676452) [V README]
- Runs UitB simulated users inside the real Unity VR application, so real and simulated users
  "perceive and control exactly the same virtual environment".
- Purpose: to "predict and analyse differences in performance and ergonomics between specific
  design choices".
- Beat Saber-style example: effort-cost weights 0.001, 0.01 and 0.05 produced different strategies.
  The highest-effort user hit targets "relying mostly on wrist movements, suggesting that the game
  design could benefit from modifying the target trajectories".
- Current limits: visual and proprioceptive channels only, with no audio or haptics.
- **Lesson for the swarm:** an *effort-cost parameter*, not a persona adjective like "lazy", produced
  the ergonomic insight.

**How to inject simple parametric models into LLM agents** (engineering pattern; design proposal, not
an empirical result)

1. The agent outputs an **intent**, for example `tap(target="결제하기")` or `swipe(from, to)`, never
   coordinates it claims a human would hit.
2. The driver resolves the target geometry from DOM/a11y/vision and calls **model tools**:
   - `reach(profile, device, point)` → difficulty 0..1 (thumb functional area);
   - `pointing(profile, W, D)` → MT (Fitts/MacKenzie) and σ (FFitts);
   - `sample_touch(point, σ, seed)` → actual touch point;
   - `rt_window(profile, n_choices, D, W)` → required time vs the measured window;
   - `legibility(fg, bg, size_px, viewing_distance)` → contrast or angular size pass/fail.
3. The driver **executes the perturbed action** (a mis-tap can really hit the neighbouring control)
   and returns the *observed* outcome to the agent. The agent must then recover as a user would.
   The error's *occurrence* is modelled; its *consequence* on the real UI is measured.
4. Every such event is logged as an observation with `basis: model`, `model` id and version, seed and
   inputs. The LLM's notes on it are separate `basis: judgment` records.
5. Heavy simulators (UitB, SIM2VR, CRTypist) run **offline** on key screens or controllers to
   calibrate or sanity-check the parametric layer, for example to check that a keyboard or a VR
   gesture set is within effort bounds. They should not run per swarm step.

The repo's `docs/ergonomic-swarm-spec.md` already encodes points 1–4 in principle (hard rules 1–4)
and has model references (`REF-fitts1954`, `REF-mackenzie1992`, `REF-bi-zhai2013`,
`REF-bergstrom2014`, `REF-hick1952`, `REF-hyman1953`, `REF-machado2009`, WCAG refs). §7 adds rules for
the agent layer and aggregation.

---

## 6. GUI agent capability limits (2025–2026)

| Benchmark | Human reference | Best numbers seen (date, source, caveats) |
|---|---|---|
| **OSWorld** (369 tasks [V]; OSWorld-Verified released 2025-07-28 [V]) | about 72% ([V] Agent S README; 72.36% in the original paper [M]) | Agent S3: 69.9% (2025-10-02) → **72.60%** (2025-12-15), described as first above human. Single-run Agent S3 is **66%** at 100 steps; 72.6% needs *Behavior Best-of-N* rollouts [V]. Qwen-UI-Agent **79.5% OSWorld-Verified** (2026-07-30, self-reported) [V]. Earlier: UI-TARS-1.5 42.5, OpenAI CUA 36.4, Claude 3.7 28 (100 steps) [V]. |
| **OSWorld 2.0** (paper arXiv 2606.29537, 2026-06-26; releases 2026-06-24, 2026-08-08, v2.1 2026-09-16 [V]) | Tasks "take skilled humans more than an hour" [V Simular README] | Sai (Simular) **73%** (2026-08-28, self-reported); GPT-5.6 Sol **62.57%** "as reported by OpenAI" (quoted by Simular) [V]. Qwen-UI-Agent **40.0% (partial score)** [V]. **These are not comparable:** release versions and scoring differ. |
| **AndroidWorld** (116 tasks, 20 apps; step budget about 2× human time [V]) | 80.0% [M] | MAI-UI-235B **76.7%**, #1 pure-vision end-to-end (2026-01-15, self-reported) [V]. GUI-Owl-1.5-8B-Thinking 71.6% [V]. Agent S3 68.1% → 71.6% with 3 rollouts [V]. UI-Venus-Navi-72B 65.9%. GPT-4o with a11y tree 30.6% [V]. |
| **ScreenSpot-Pro** (professional high-res apps: CAD, creative, scientific, dev, office, OS [V]) | n/a | Leaderboard file (GUI-Agent/grounding-leaderboard, fetched 2026-09-28) [V]: top **82.7%** (Indeed-UI-32B zoom-in; icon 70.4 / text 90.4). Holo2-235B agentic 78.5. MAI-UI-32B 67.9% with no zoom (2026-01-13). Original baselines: GPT-4o **0.8%**, Claude Computer Use **17.1%**, OS-Atlas-7B 18.9%, UI-TARS-1.5 61.6%. Many entries are self-reported, zoom-in or ensemble pipelines. |
| **Games** | n/a | UI-TARS-1.5 reported 100% on 14 casual Poki web games (self-reported) [V]. VideoGameBench (arXiv 2505.18134) runs real-time Game Boy, DOS and browser games; a "lite" mode pauses the game while the model thinks [V]. The best frontier model completed well under 1% of the full benchmark (0.48% for Gemini 2.5 Pro [M]). |
| **Human-likeness** (not success) | n/a | Next-action accuracy of about 12% for prompted frontier LLMs on real shopping sessions [S]. |

**Implications for QA**
1. Operation is now good enough to *reach* most states of typical web and app flows. That is the
   swarm's real value: state-space coverage.
2. Agent success ≠ human success. Agents can beat humans on benchmarks while diverging in path,
   timing and perception.
3. Agent failure ≠ user failure. Grounding misses, especially icons and dense professional UIs, and
   step limits cause failures a human would not have.
4. Real-time games need step-locked or paused execution. Timing difficulty must be computed, not
   inferred from agent failure.
5. Leaderboard numbers are volatile, often self-reported, and inflated by best-of-N or zoom tricks.
   Pin the agent model and version per run and record it in `run.json`.

---

## 7. Design rules for the persona swarm

Rule IDs are proposals (SW-xx). They extend the repo's existing hard rules in
`docs/ergonomic-swarm-spec.md` §0.

### 7.1 What is LLM judgment vs deterministic model vs measurement

| Layer | Owns | Never does |
|---|---|---|
| **Driver / measured** (`basis: measured`, epistemic `observed`) | Geometry, colours, timing windows, feedback latency, state changes, success or failure of the real UI, console errors | Interpret intent |
| **Deterministic HF models** (`basis: model`, epistemic `inferred`, with model id/version, inputs and seed) | Reach, pointing time and error, touch-noise sampling, legibility and contrast, CVD simulation, reading time, reaction-window adequacy, load proxies, abandonment budgets | Use LLM output as a parameter |
| **LLM persona agent** (`basis: judgment`, epistemic `inferred`) | Task decomposition; choosing the next *intent* from the visible screen; expectation-vs-outcome notes; hypotheses about label or copy comprehension; recovering after (model-injected) errors | Emit ergonomic numbers, pain or fatigue claims, prevalence, "users like me…" group opinions, or severity |
| **Report agent** | Assemble findings from bundle IDs only | Introduce facts; use predictive framing; quote agents as users |

- **SW-01 Intent, not ergonomics.** The agent emits intents. The driver resolves geometry and applies
  model-sampled motor noise. Any ergonomic number in LLM text is discarded, and a lint check should
  flag it.
- **SW-02 Decide from the visible, measure from the structural.** The agent's decision input is the
  viewport-only screenshot at the device's CSS size, optionally degraded by the profile's vision
  model. DOM, a11y and uiautomator data feed only the measurement layer. If a DOM channel must be
  given to the agent for robustness, restrict it to in-viewport, visible, non-aria-hidden elements
  and record `perception_channel: dom|vision|hybrid` in the run.
- **SW-03 Demographics select scenarios, not voices.** Nemotron-Personas-Korea fields may choose
  goals, contexts, devices and familiarity, and the swarm may stratify on them. The agent must not
  narrate identity-based opinions ("as an older woman I…"), because of misportrayal, flattening and
  caricature. Never infer ergonomic attributes from demographics (already rule 4). Never generate
  MBTI or "personality" fields. MiroFish does both.
- **SW-04 Behavioural parameters are declared, not LLM-generated.** Patience budgets, activity
  levels, reading speed and time pressure come from a parameter table with references
  (`base_rate_refs`) or are listed in `assumption_fields`. They are never set by an LLM as
  "realistic", as MiroFish's `simulation_config_generator` does.

### 7.2 Separating agent limits from UX issues

- **SW-05 Failure triage before a finding exists.** Every failed step is classified as
  `ux_issue | agent_limit | environment | unknown`.
  - Classify as `agent_limit` if: grounding confidence is low, the target was an icon without a text
    label and a text or DOM re-try succeeds, the step cap was hit before the model-predicted human
    time, or the failure disappears when another agent model or another perception channel is used.
  - Only `ux_issue` failures, and `unknown` failures marked as such, become findings.
- **SW-06 Replicate across agent configurations.** A judgment-basis finding needs at least two
  agent-model or perception-channel configurations to reproduce it before it can exceed P3. Grounding
  gaps (icons 70.4% vs text 90.4% even at the top of ScreenSpot-Pro) mean that single-agent "could
  not find X" is weak evidence.
- **SW-07 Known-product contamination check.** For widely known apps and games, run a perturbed
  build (relabelled, re-ordered or re-skinned) or mark first-use findings `unknown`. Agents may
  already "know" the UI (hyper-accuracy; SILICA's memorisation concern).
- **SW-08 Real-time surfaces run step-locked.** Games and time-limited UIs run paused or
  frame-stepped for the agent. Timing adequacy comes only from measured window durations against RT
  and MT models. The agent's in-game failure is never evidence that a game is "too hard".

### 7.3 Aggregation without implying prevalence

- **SW-09 Coverage counts only** ("k/n simulated profiles triggered"; already rule 3).
  - Always print the tested strata and the **untested/unfilled strata** next to the count.
  - No percentages in titles or summaries.
  - No confidence intervals, significance tests or population weighting. Base rates may choose
    plausible profile combinations but must never be re-applied to outputs.
  - Korean label: 「시뮬레이션 프로필 k/n (실사용자 비율 아님)」.
- **SW-10 Conditional statements, not frequencies.** Express swarm results as *differential
  conditions*, for example "fails when handedness=left ∧ grip=one-hand on galaxy-s24-ultra" (the
  spec's `profile_specific`). This is a model-conditional prediction about a kind of user, not a
  claim about how many such users exist.
- **SW-11 Severity from consequence and basis, never from count.** One profile hitting a
  critical-path blocker can be P0 if measured. Fifty agents agreeing on a judgment remains a
  judgment. Agents from the same model are **one correlated rater**: swarm agreement ≠ inter-rater
  reliability (see diminished diversity and herding).
  - Proposed caps: judgment-only findings ≤ P2 until corroborated by a measured or model
    observation or by a human study. Model-only findings ≤ P1 unless the element is on a critical
    path and the model's inputs were measured.
- **SW-12 Report scale sensitivity.** If results change with swarm size, recommender settings or the
  agent model, report the sensitivity. OASIS shows that herding grows with N, so bigger is not
  "more representative".
- **SW-13 Calibration status per check.** Each judgment-based check carries
  `calibration: uncalibrated | study-calibrated(<study id>)`.
  - Calibration means comparison with the team's own real-user sessions on the same build: hit rate
    and false-alarm rate of swarm issues against human-found issues, reported as study-specific,
    never generalised.
  - This follows the TinyTroupe validator idea and Park et al.'s self-consistency benchmark.
- **SW-14 Perturbation stability.** Re-run judgment checks under meaning-preserving perturbations:
  copy paraphrase, element order, theme. Unstable judgments are downgraded to `unknown`. This is
  SILICA-style robustness.
- **SW-15 No agent Likert or SUS scores as metrics.** Post-task questionnaires answered by agents may
  be kept as qualitative prompts but are never averaged or compared. Order and label biases dominate,
  as do low variance and version drift.

### 7.4 Simulated social discourse (MiroFish/OASIS-style) and agent interviews

These rules apply if the swarm generates reviews, community posts, rating reactions, word-of-mouth
or "public opinion" around a feature.

- **SW-16 Quarantined store.** Simulated discourse lives in a separate namespace, never in the
  evidence bundle's observations or the research knowledge graph. MiroFish's pattern of writing sim
  activity into the seed graph with no in-text label is explicitly disallowed. Provenance must
  survive at the level of each item, fact or edge (`origin: simulated`, `sim_id`, `model`, `seed`,
  `round`), not just the batch.
- **SW-17 In-text labels on every item.** Each simulated post, review or interview answer starts with
  a visible tag, 「[시뮬레이션 · 합성 담론 · 실제 사용자 발화 아님]」 / "[SIMULATED — synthetic
  discourse, not user data]". Exports and screenshots keep the tag.
- **SW-18 No predictive framing.** Reports use "scenario exploration" or "hypothesis generation"
  language only. Banned phrasings (lint-able): "will happen", "users will", "the public will",
  "predicts", 「예측」 for outcomes, "rehearsal of the future", and any "god's-eye view" framing.
  This is the exact opposite of MiroFish's ReportAgent prompt.
- **SW-19 No numbers from discourse.** No sentiment percentages, share-of-voice, virality counts or
  "N% of agents opposed". The known distortions (herding stronger than humans, caricature, flattening,
  WEIRD skew) make such numbers misleading. Allowed outputs: a list of *argument types* and *risk
  hypotheses*, each with a proposed real-world verification method (survey item, interview probe,
  log metric).
- **SW-20 Agent interviews are simulated think-aloud.** Post-run "chat with the agent" answers are
  `basis: judgment` rationales that may be post-hoc confabulation. They may point to an existing
  observation but can never be the sole support of a finding. They must never be quoted as user
  quotes in personas, reports or slides.
- **SW-21 Report agent restricted to IDs.** Like MiroFish's no-fabrication rule, but stricter:
  - every sentence in a swarm report cites observation, finding or run IDs;
  - every sentence carries basis and epistemic tags;
  - the report agent may not add facts, may not use its own knowledge about "typical users", and
    must list what is `unknown` (untested strata, uncalibrated checks, agent-limit failures).

### 7.5 Minimal additions to the existing schemas (suggested)

- `run.json`: `agent: {model, version, perception_channel, grounding_model}`,
  `execution_mode: realtime|step_locked`, and `step_budget_basis`
  (for example "2× model-predicted human time").
- Observation: `failure_class: ux_issue|agent_limit|environment|unknown` and
  `calibration: uncalibrated|study-calibrated:<id>`.
- Aggregated finding: `replicated_by: [agent configs]`, `untested_strata: [...]`,
  `stability: stable|unstable|untested`.
- A separate `sim-discourse.v1` schema with a mandatory `label_ko`/`label_en` and item-level
  `origin: simulated`.

---

## 8. Sources

Tags as defined at the top. URLs are given even when the page itself was blocked for fetching.

**MiroFish / OASIS / Chinese simulation work**
- MiroFish repo and README: https://github.com/666ghj/MiroFish ; https://raw.githubusercontent.com/666ghj/MiroFish/main/README.md [V]
- MiroFish source files [V]:
  - https://raw.githubusercontent.com/666ghj/MiroFish/main/backend/app/services/report_agent.py
  - .../simulation_config_generator.py
  - .../oasis_profile_generator.py
  - .../zep_graph_memory_updater.py
  - .../zep_tools.py
- MiroFish news: https://eu.36kr.com/en/p/3715147673006213 ; https://en.tmtpost.com/post/7905996 ; https://www.panewslab.com/en/articles/019cf53a-ca7c-7159-9fbc-40859cdfa108 [2nd]
- MiroFish commentary on the lack of validation: https://www.linkedin.com/pulse/swarm-intelligence-comes-forecasting-how-mirofish-simulates-borish-lahve ; https://www.blocmates.com/articles/what-is-mirofish-the-agent-engine-that-can-predict-anything-and-everything [S]
- OASIS repo: https://github.com/camel-ai/oasis [V]; paper https://arxiv.org/abs/2411.11581 [S]; summary of v4 https://github.com/cognitivetech/llm-research-summaries/blob/main/interactive-agents/OASIS-Open-Agent-Social-Interaction-Simulations-with-One-Million-Agents_2411.11581v4.md [2nd]
- AgentSociety: https://arxiv.org/abs/2502.08691 [S]; https://github.com/tsinghua-fib-lab/AgentSociety (v2 arXiv 2607.11895) [V]; Dorian description https://medium.com/@Micheal-Lanham/building-virtual-societies-with-30-000-ai-agents-23369c2d6da8 [2nd]
- "When Plausible Is Not Realistic" (arXiv 2606.13835): https://arxiv.org/abs/2606.13835 [S]
- YuLan-OneSim: https://github.com/RUC-GSAI/YuLan-OneSim [V]; https://arxiv.org/abs/2505.07581 [S]
- Persona Hub: https://github.com/tencent-ailab/persona-hub [V]; https://arxiv.org/abs/2406.20094 [S]
- TinyTroupe: https://github.com/microsoft/TinyTroupe [V]; arXiv 2507.09788 [V link]

**LLM usability-testing agents**
- UXAgent: https://arxiv.org/abs/2502.12561 ; https://dl.acm.org/doi/10.1145/3706599.3719729 [S]; repo https://github.com/neuhai/UXAgent (system paper arXiv 2504.09407) [V]
- Lu et al., "Beyond Believability" / "Can LLM Agents Simulate Multi-Turn Human Behavior?": https://arxiv.org/abs/2503.20749 [S]
- Agent A/B: https://arxiv.org/abs/2504.09723 ; https://dl.acm.org/doi/10.1145/3772363.3799039 [S]
- PerceptUI: https://arxiv.org/abs/2606.05697 [S]
- uxCUA: https://arxiv.org/abs/2604.26020 [S]
- Avenir-UX: https://arxiv.org/abs/2604.09581 [S]
- OmniParser: https://github.com/microsoft/OmniParser [V]

**Validity and critique**
- Park et al. 2024, Generative Agent Simulations of 1,000 People: arXiv 2411.10109 [S]; https://github.com/joonspk-research/genagents [V]
- Aher, Arriaga & Kalai, ICML 2023 (hyper-accuracy distortion): https://github.com/GatiAher/Using-Large-Language-Models-to-Replicate-Human-Subject-Studies (abstract) [V]; arXiv 2208.10264
- Cheng, Piccardi & Yang, CoMPosT, EMNLP 2023: https://github.com/myracheng/lm_caricature [V repo; findings M]
- Santurkar et al. 2023, OpinionQA: https://github.com/tatsu-lab/opinions_qa [V repo; findings M]
- Dominguez-Olmedo, Hardt & Mendler-Dünner, NeurIPS 2024: https://github.com/socialfoundations/surveying-language-models [V repo; findings M]
- SILICA (Bin Tareaf, arXiv 2608.28182, 2026-08-28): https://arxiv.org/abs/2608.28182 [S]
- Not re-verified at the time of writing [M]:
  - Wang, Morgenstern & Dickerson 2025, *Nature Machine Intelligence* 7
  - Argyle et al. 2023, *Political Analysis*
  - Bisbee et al. 2024, *Political Analysis*
  - Atari et al. 2023, "Which Humans?"
  - Park, Schoenegger & Zhu 2024, *Behavior Research Methods*
  - Hu & Collier 2024, ACL
  - Hewitt et al. 2024
  - Kozlowski & Evans 2025
  - Anthis et al. 2025, ICML position paper
  - Larooij & Törnberg 2025
  - Cheng, Durmus & Jurafsky 2023, "Marked Personas"
  - NN/g "Synthetic Users" 2024

**Ergonomic and computational-rationality simulation**
- User-in-the-Box (UIST 2022, DOI 10.1145/3526113.3545689): https://github.com/aikkala/user-in-the-box [V]
- SIM2VR (UIST 2024, DOI 10.1145/3654777.3676452): https://github.com/fl0fischer/sim2vr [V]
- CRTypist (CHI 2024, DOI 10.1145/3613904.3642918): project page source https://raw.githubusercontent.com/crtypist/crtypist.github.io/main/index.html ; code https://github.com/kadensalem/crtypist [V]
- Not re-verified at the time of writing [M]:
  - Jokinen et al. CHI 2021, "Touchscreen Typing As Optimal Supervisory Control"
  - Oulasvirta, Jokinen & Howes CHI 2022, "Computational Rationality as a Theory of Interaction"
  - Bergstrom-Lehtovirta & Oulasvirta CHI 2014
  - Bi, Li & Zhai CHI 2013 (FFitts)
  - Card, Moran & Newell 1980 (KLM)
- WCAG 2.2 target size (24×24 minimum; 44×44 enhanced): https://raw.githubusercontent.com/w3c/wcag/main/understanding/22/target-size-minimum.html ; .../understanding/21/target-size-enhanced.html [V]

**GUI agent capability**
- OSWorld: https://github.com/xlang-ai/OSWorld [V]
- OSWorld 2.0: https://github.com/xlang-ai/OSWorld-V2 [V]
- Agent S / Simular: https://github.com/simular-ai/Agent-S (README) [V, self-reported]
- UI-TARS: https://github.com/bytedance/UI-TARS [V, self-reported]
- AndroidWorld: https://github.com/google-research/android_world [V]
- MAI-UI / Qwen-UI-Agent: https://github.com/Tongyi-MAI/MAI-UI [V, self-reported]
- GUI-Owl-1.5: https://github.com/X-PLUG/MobileAgent/tree/main/Mobile-Agent-v3.5 [V, self-reported]
- UI-Venus: https://github.com/inclusionAI/UI-Venus [V, self-reported]
- ScreenSpot-Pro: https://github.com/likaixin2000/ScreenSpot-Pro-GUI-Grounding [V]; leaderboard data https://raw.githubusercontent.com/GUI-Agent/grounding-leaderboard/main/results/screenspot_pro.json (fetched 2026-09-28) [V]
- VideoGameBench: https://github.com/alexzhang13/videogamebench (arXiv 2505.18134) [V README; result numbers M]
