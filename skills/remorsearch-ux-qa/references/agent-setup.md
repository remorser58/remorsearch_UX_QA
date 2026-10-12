# Subagent setup

This page governs permission, independent work and model settings for persona
operators, research readers and reviewers. The host dispatches agents; CLI
recording/analysis commands do not spawn them.

## 0. Current request takes precedence

Before spawning, ask once per skill run whether multi-agent research/persona QA
is allowed, unless the run already has an explicit answer. Example: "Allow
multi-agent research and persona QA? Parallel work can save time but uses more
model capacity." Record/reuse the answer for this run. Refusal or no answer means
single-agent serial execution; silence grants nothing. Model choice is separate:
use existing host role/config settings without a new mandatory selection.

Approval covers independent operators, readers and reviewers under one shared
cap: six active agents, or the smaller host/user cap. Start only independent work.
It grants no publishing, private-community access, external writes or resource
sharing; existing access and write grants still apply.

For approved live QA, dispatch independent persona operators using the product
in parallel under distinct task-relevant conditions derived from research.
Missing evidence stays task-based test assumptions, never invented audience
demographics. Each operator needs its own runID/profile, isolated browser context
and task-owned fixtures/state. Serialize any part whose state cannot be isolated.
Use the same build/scenario definitions; keep run/profile/capture IDs unique and linked. Decisions use the current
screenshot and allowed input channel, followed by real actions and before/after
evidence; preserve blind-pass limits. Aggregate observed traces, dedupe findings,
corroborate them and resolve disagreements. P0/P1 needs a fresh second pass
without the draft; with no approved reviewer, label the serial self-pass.
One scripted flow analyzed across profiles remains geometric screening, never
a substitute for approved live persona-agent QA. Measured/model/judgment and
live/synthetic distinctions remain unchanged.

Apply model, effort and role assignments explicitly supplied in the current
conversation before any saved choice or harness default. Mixed-provider teams
are allowed. Use the exact identifiers and effort options exposed by the host;
record requested and actual settings separately. Do not infer that `fast`,
`priority`, a subscription tier or a quota pool is active merely from the model
name. Apply such options only through a supported host control.

If the requested provider rejects the host's task envelope, retry through an
available documented plaintext task interface with the same model and scope.
Keep the same concurrency limit and never copy authentication data between
providers. Do not change global provider configuration to repair one task.
If the exact model, effort or quota route remains unavailable, report the actual
error and complete independent work. Never silently replace an explicitly
requested model. A model substitution requires an existing user-approved
fallback or a new user choice.

For task-local choices, keep settings in the run record. Write persistent model
preferences only when the user asks to save them. A session request to use
subagents does not require another model-selection question.

## 1. Saved choice

Read `${XDG_CONFIG_HOME:-~/.config}/remorsearch-ux-qa/config.json` if it exists:

```json
{
  "version": 1,
  "source": "harness | user",
  "host": "claude-code | codex | other",
  "roles": {
    "operator": {"model": "inherit | haiku | sonnet | opus | fable | <model id>", "effort": "inherit | low | medium | high | xhigh | max", "agent_type": "remorsearch-operator | null"},
    "judge": {"model": "...", "effort": "...", "agent_type": "remorsearch-judge | null"}
  },
  "decided_at": "2026-09-28T00:00:00Z"
}
```

- `operator`: persona agents that drive the real screen, research readers, and
  counter-searchers.
- `judge`: verification (including research verifiers that sample excerpts),
  matching findings to evidence, and severity review.

If the file is valid and the user did not ask to change it, use it and go to
step 4. If the user says something like "change the agent model" or "에이전트
모델 바꿔줘", start again at step 2.

## 2. Existing harness mapping comes first

Check read-only, without changing any setting:

- **Claude Code**: the `CLAUDE_CODE_SUBAGENT_MODEL` environment variable (and
  `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`), agent definitions with `model:` or
  `effort:` front matter in `.claude/agents/` or `~/.claude/agents/`, and agent
  types provided by plugins.
- **Codex**: per-agent or per-profile `model` and `model_reasoning_effort`
  settings in the user's Codex `config.toml`.
- **Other harnesses** (for example OMO-style plugins): their documented
  agent-to-model mapping.

If any mapping exists:

1. Do not pass a model or effort when starting subagents. In Claude Code a model
   given at call time wins over agent definitions and the environment default,
   so passing one would silently override the user's mapping.
2. If the harness defines role agents, route by role: research readers to its
   research agent, judges to its review or verification agent, persona operators
   to its general worker. The skill's own definitions from step 3,
   `remorsearch-operator` and `remorsearch-judge`, are role agents too.
3. Record `"source": "harness"` with `"model": "inherit"` for each role, tell the
   user in one line which mapping is being followed, and do not ask.

`CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` forces one model on every subagent. Any
choice made here then has no effect; say so instead of asking.

## 3. Ask once

Only when no saved choice and no harness mapping exist. Use the host's selection
prompt (in Claude Code, the `AskUserQuestion` tool); if the host has none, ask
with a numbered list. Before asking, explain the bounded independent work and
shared cap from section 0; profile count does not authorize that many agents.

**Model and effort for persona and research subagents.** One question with these
options; the host adds a free-text "Other".

| Option | Tell the user |
| --- | --- |
| Sonnet, max effort (Recommended) | Best reports in the benchmark: highest quality and fewest false alarms on fixed screens. The slowest, about 5 minutes per screen. |
| Opus, high effort | Found about as many defects, about 2.6 times faster, at a similar measured cost. Its reports scored lower (3.6 of 5 against 4.1). |
| Sonnet, high effort | Fastest. It reached every goal but raised the most false alarms on fixed screens, so keep the judge pass. |
| Same as this session | No extra configuration. |

Do not offer Haiku. In the benchmark it failed 5 of 11 tasks and found none of
the seeded defects. If the user types it under "Other", warn once, then accept
it.

Judges and verifiers use Opus at max effort, the setting of the benchmark's
judges. Ask about them only if the user raises cost.

In a research audience run, the brief questions (A0 in
`references/research/audience-pipeline.md`) may go in the same selection prompt,
so the user is asked once.

**Effort in Claude Code.** The Agent tool takes a model for each call but no
effort. A subagent runs at the `effort` in its agent definition, or else at the
session's effort level. So if the chosen effort differs from the session's, or
you cannot tell, ask one follow-up question in the same way: "Create two agent
definitions so the effort applies?", with the options "Create them
(Recommended)" and "No, use the session's effort". On yes, write
`~/.claude/agents/remorsearch-operator.md`:

```markdown
---
name: remorsearch-operator
description: Operator subagent of the Remorsearch UX QA skill (persona agents, research readers). Use only when that skill starts one.
model: sonnet
effort: max
---
Follow the task prompt you are given. It comes from the Remorsearch UX QA skill.
```

Use the chosen model and effort in it. Write
`~/.claude/agents/remorsearch-judge.md` the same way, with
`name: remorsearch-judge`, a judge description, `model: opus` and `effort: max`.
Never overwrite a file that already exists; if one differs, show it and ask.
Save each agent type in the config (`agent_type`).

Keep the answers with `"source": "user"` in the run record; save the config only
when requested. Create the folder if needed. Never
write secrets or tokens to this file.

## 4. Use the choice

- If a role has an `agent_type` and the host lists that agent type, start the
  role's subagents with it and pass no model, so the definition's model and
  effort apply. The host may list new definitions only from the next session.
- Otherwise pass the saved model for each call. Where the call also takes an
  effort, pass that too.
- Skip both when the source is `harness`.
- If a model is unavailable, use only a fallback the user has already allowed;
  otherwise record the blocked role and continue independent work.
- Record in every report the model and effort each role actually ran with,
  including an effort that could not be applied. Persona agents from one model
  count as one correlated rater
  (`references/ergonomics/persona-agent-protocol.md`, replication rule).

## 5. Research readers

These rules add to the steps above. They do not change how the model is chosen.

- Research readers and counter-searchers use the `operator` settings. Verifiers
  use the `judge` settings.
- Readers/reviewers require section 0's permission and share its cap with persona
  operators. Use 2-3 readers per batch, or 5-6 with a host-enforced return schema
  only when slots allow. The research ledger caps each host regardless of agent
  concurrency; never make parallel requests to one source host.
- Readers return `ux-reader-return.v1` (bundled schema) and never write their own
  fetch code. They read through `scripts/ux_research.py` and the browser tools in
  `references/research/public-page-access.md`.
- Harvest rule: the orchestrator does not finish until every reader has returned
  or has been recorded as a missing axis. A missing return is re-run in batch mode.
- Readers from one model share blind spots. When the user allows it, prefer a
  different model for verifiers than for readers, and record the choice.

## Evidence for the recommendation

The options come from a blind benchmark in this repository. Six model and effort
settings drove 11 Korean screens through the live web driver: 8 screens with 40
seeded defects, and 3 clean controls. Two blind judges scored every report
against the answer keys.

| Setting | Goals reached | Defects matched (of 40) | False alarms on clean controls | Quality (1–5) | Time per screen |
| --- | --- | --- | --- | --- | --- |
| Haiku 4.5 | 6/11 | 0 | 4.0 | 1.2 | 3.6 min |
| Sonnet 5.5, high | 11/11 | 20.5 | 6.0 | 2.9 | 1.3 min |
| Sonnet 5.5, max | 11/11 | 22.5 | 1.0 | 4.1 | 4.7 min |
| Opus 5.5, high | 11/11 | 21.5 | 4.0 | 3.6 | 1.8 min |
| Opus 5.5, max | 11/11 | 20.5 | 1.0 | 3.9 | 4.9 min |
| Fable 5.1, high | 11/11 | 12.5 | 5.0 | 2.8 | 2.1 min |

The method, costs, judge agreement and limits are in the repository document
`docs/validation/subagent-model-benchmark.md` (not installed with the skill).
