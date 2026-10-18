# Improve an existing product

Improve a product from a URL or repository; no prepared packet or persona. Keep narrow requests scoped.

## Stages

1. Runtime: use `python3` if it is 3.10+; otherwise run `python3 scripts/find_runtime.py` and reuse the paths it prints. Missing Node 22 gaps only the bundled driver; host-browser QA continues.
2. Product and intent discovery.
3. Baseline: scoped real-product QA before packets or research. After first observation, use `references/persona-qa/generated-ui-preflight.md` sections 1–4; replay affected checks after fixes.
4. Task-linked research, only from questions the assessment raised.
5. A warranted reversible fix, then fill, strict improve and replay.

Access gaps or exhausted limits can leave partial work; continue every feasible step of an improvement request.

## Start from the product and preserve intent

Open the URL, or inspect the repository's start command and build; confirm a local endpoint is the tested build. Identify tasks, screens, tools, safe fixtures and grants. State scope and finite limits; reuse supplied limits. Otherwise begin with up to three primary tasks and two improvement rounds. Do not require a problem list.

Read relevant `AGENTS.md`, README, PRD, decision records, accessible Claude/Codex sessions and intent memory, commits and Figma history. Search by this product, task and decision; skip unrelated personal records. Candidate documents stay candidates until actually read. Record each preserved decision's source, authored/checked dates, version, affected task/screen and reason, and state honestly which memory searches ran. Mark missing or stale material. Implementation shows behavior, not why it was chosen.

Apply the latest explicit user instruction, currently confirmed project decisions, then older memory; a newer commit alone does not revoke a decision. Preserve intentional confirmation, business rules, access, feature order, terminology and brand experience. Missing memory permits neither arbitrary changes nor a blanket stop. Ask about unresolved material conflicts only for affected changes. Save intent in task artifacts, not global memory.

## Assess first, then ask research questions

Enter persona-qa with `references/persona-qa/workflow.md`. Establish the baseline before research. Derive scenarios from actual tasks: completion, input retention after back/errors/return, failure and recovery, empty/loading/stale states, keyboard/focus/reading order, relevant screen sizes, interruption. Where relevant, test Korean text clipping, IME composition, and input retention and recovery. Enumerate the screens, states and devices actually reached, and name what was not. Keep build, start state, safe data, device and input in each trace. Preserve tabs, accounts and real records; writes use owned synthetic fixtures.

Ask where the task stopped and what workaround existed. Separate unknown causes from reproduced behavior. Synthetic conditions claim no real participants or population estimates; emulation cannot establish real-device, assistive-technology or human accuracy.

Load `references/research/workflow.md` and its access/evidence cards only when research starts, with questions from the assessment, not a generic sweep. Choose candidates for task context; scraping all six is not required:

| Candidate | Context to seek |
| --- | --- |
| 당근 (Karrot) | Local, transaction or service task; post and comments |
| 디시인사이드 (DC Inside) | Gallery, conditions, replies, alternatives tried |
| 유튜브 댓글 (YouTube comments) | Video topic/time, feature, replies |
| X | Post, conversation, reply target |
| 인스타그램 (Instagram) | Caption, comments, problem context |
| Threads(쓰레드) | Post, connected replies, follow-up |

Add Naver Cafes, reviews, Reddit or official sources as relevant. Selection implies no access. Discover URLs, then invoke bundled insane-search under the research card's access/privacy rules. Unsupported output stays a lead; unread content stays a gap. Retain calls, source URL, dates, version, summary, read scope, firsthand/promotion/inference labels, counters and duplicates. A missing optional source or key does not stop other research or reproduced product QA; report it separately from missing required QA. Never invent callback receipts.

Turn scrubbed research into hypotheses and rerun related tasks. Unreproduced complaints stay hypotheses; sparse community evidence does not block reproduced defects. Never fabricate statuses.

## Fix and verify in the same scope

The improvement request, actor and scope authorize ordinary reversible fixes; do not ask again at a CLI permission stop. Review paths and concurrent edits, then make a minimal fix. Unresolved intent conflicts, scope expansion, deployment, publication and real account changes need their own authority.

When design lives in Figma (`policy.figma_first: true`), change screen composition and UX in editable Figma first, preserving existing design and recording file URL, nodes, version and readback. A missing Figma connection blocks only that change (a screenshot or local plan does not substitute); continue discovery and QA. A code-first project (`figma_first: false`) changes code directly with before/after captures. Follow the project's own design rules.

Use `references/loop/workflow.md` for patch/replay records and look up `references/loop/provider-contract.md` by section for packet fields. Host browser and Figma tools act; the CLI validates imported evidence and applies authorized local text patches. When it stops for missing receipts, continue feasible collection and resume with appended evidence.

Rebuild with project tools; replay the current build with matching start state, fixture, viewport and input: task completion, values, recovery, accessibility, adjacent regressions, Figma and each preserved decision. Failed/missing/stale checks prevent completion; correct within the remaining rounds and keep prior evidence. Do not restart budgets.

## Example request and checklist

`우리 앱 UX 개선해줘. URL: https://app.example.test 또는 저장소: /path/to/product`

1. Inspect the target and intent sources; save build identity, task scope, preserved decisions and unknowns. Run baseline QA and keep actual traces. Deliver that assessment even if later stages stop.
2. When questions warrant research, author `brief.json` and `plan.draft.json`. From the skill folder run `python3 scripts/ux_research.py start --brief brief.json`, then `python3 scripts/ux_research.py plan --run RUN --manifest plan.draft.json`. Capture, merge and gate as the research card specifies; retain gaps.
3. Collect real QA evidence for related scenarios and run `python3 scripts/validate_bundle.py QA_BUNDLE.json`. Prioritize reproduced task harm and intent-compatible fixes.
4. Author `DRAFT.json` from observed facts only: `goal.product_context_artifact_id` bound to the inspected context (provider-contract section 6) and real capture-time revisions. Mark mechanical hashes, digests, IDs and revisions `@auto`, then run `python3 scripts/ux_loop.py fill DRAFT.json --evidence-root EVIDENCE [--workspace PRODUCT] --out packet.json`. Fill never invents context, intent, grants, outcomes, severity or observations; exit 2 writes nothing, exit 1 is invalid, neither is acceptance (`references/loop/cli.md`).
5. Run `python3 scripts/ux_loop.py validate packet.json --evidence-root EVIDENCE`, then `python3 scripts/ux_loop.py improve packet.json --workspace PRODUCT --evidence-root EVIDENCE --checkpoint CHECKPOINT --grant code_write --actor OPERATOR --reason 'Existing UX improvement request; reviewed reversible scope'`. Only changed/conflicting intent needs specific `--intent-decisions`; preserved acknowledgements need none. `resume --input` appends missing evidence. Examples are not observations.
6. Link each replay to `intent_review_artifact_id`, covering every scoped constraint including unchanged ones (`fix_id: null`). `intent_verified` must be true for acceptance. Deliver changed locations, before/after evidence, intent results, regressions and gaps.

Complete only after original failures, adjacent regressions, preserved intent and required design checks pass on the current scoped build, with no known material in-scope issue or required evidence gap. An exhausted limit is partial. If scoped QA finds nothing reproducible to change, report the completed inspection with no changes, its evidence and coverage; do not manufacture a fix. A passed task proves that task only, never measured satisfaction, conversion, time savings, human accuracy or whole-product readiness.
