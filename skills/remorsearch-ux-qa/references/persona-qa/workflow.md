<!-- Mode: persona-qa. Entry point: `SKILL.md`. -->
# Persona QA mode

Test completion, input preservation and rendered design. Scenarios define conditions; traces establish failures. Improvement adds task-linked research; standalone QA is read-only.

## Fast path for UI QA

For a page UI check naming no persona, audience or condition matrix. It replaces the run path; numbered sections stay lookups.

1. Start `python3 scripts/ergo_qa.py scan --url URL --out work/scan` (one `--url` per page) first: it records each page top to end on a phone and a laptop. `scan.md` lists layout candidates (cut, covered or overlapping text, alignment, spacing, icon centring, field sizes, touching labels, bar overflow, page width) with outlined crops, then the other checks by cause, and fills in as pages finish. A driver failure is a coverage gap.
2. Open every layout crop and the top, middle and end screenshots in `runs/SCAN-*/*.css.png`; capture more only for what they miss. Confirm a candidate only when the pixels show it; list dismissals with reasons. Report LY-08 once for all text it cuts and each grouped cause once. Then check what measurement misses with `references/persona-qa/ui-quality.md` by section: hierarchy, wrong or broken content, inconsistent components, and differences from Figma or a spec.
3. Exercise only named tasks, or the primary form: happy path, one required omission, validation and recovery.
4. Report with the template's Decision and Findings sections: each finding cites its crop, measurement and fix. Name what stayed untested (Safari/WebKit, real devices, unreached states).

## Phase 0 recap

Use `SKILL.md` Phase 0. Every product UI QA uses `references/persona-qa/ui-quality.md` by section; pure research skips it.

Chromium emulation leaves Safari/WebKit, real devices, safe areas and screen readers untested. Korean product: `references/persona-qa/kwcag-card.md`; report language changes wording only. Outside-product pages: `references/shared/access-card.md` in operator/verifier prompts. Host browser first; preserve user state.

Follow the UI card's host visual procedure and `references/persona-qa/generated-ui-preflight.md` sections 1–4 before verdict and after fixes. Capturing is not viewing; record inspected regions.

## Run path

Compose before persona runs; observation may come first. Retain supplied audience/plan. `--budget` counts profiles, not runs. Research-origin audiences require supported `--run`, `--bundle`, `--gate` per `references/ergonomics/audience-research.md` by section; never replace missing research with standalone assumptions. Adjust budget to scope:

```sh
python3 scripts/ergo_qa.py audience-check audience.json
python3 scripts/ergo_qa.py personas --audience audience.json --budget 4 --plan work/persona-plan.md --out work/profiles.json
python3 scripts/ergo_qa.py scenario-stubs --audience audience.json --out scenarios/
```

Without an audience, use `profiles --count N --seed 7 --devices DEVICE --out work/profiles.json`; never overwrite audience-composed profiles. Cover two task-changing conditions when scope permits; a single-condition request is valid with the gap recorded. Base-rate profiles are baselines; only an actual clean twin is a clean control. Attribution needs a matched pair differing in one facet; failure under both proves neither prevalence nor a facet effect.

Complete the chosen stub as `sc.json` with real URL/build, safe task data, target roles and success checks (section 1). Save a selected profile object unchanged as `work/profile.json`; use its actual ID, including composed AP IDs. Set `RUN_ID` uniquely per profile/task and `PRODUCT_BUILD_ID` to the tested build. Record the actual operator/model/input_channel in `agent.json`. Use existing Node.js 22 dependencies:

```sh
node drivers/web/ergo_drive.mjs serve --scenario sc.json --profile work/profile.json \
  --build-id "$PRODUCT_BUILD_ID" --agent-json agent.json --out runs/scenario-1/ --run-id "$RUN_ID" --port 9477 --analyze
# Operate via drive_client.mjs observe/act/note/finish; finish with the actual outcome.
python3 scripts/ergo_qa.py swarm --runs runs/scenario-1/ --profiles work/profiles.json --scenario sc.json --out report/
```

`--analyze` screens the recording at finish and returns report paths and counts, never a pass verdict (exit 4 with a reason when analysis fails; `--python PATH` if needed). Repeat each selected profile on the same task with baseline and clean controls, one run directory per scenario/build/device/orientation, analysed with the profiles used to record (all matching `--scenario` files). `--cross-profile` compares shared recordings; it is not another persona execution. Label evidence measured/model/judgment; hypotheses need reproduction before promotion. Attach bound runs in section 5. Driver mechanics: `drivers/web/README.md`, Commands section.

## 1. Build the priority-task matrix

For each priority task and scoped device:

| Path | Required checks |
| --- | --- |
| Rendered design | Mobile/desktop, short height, open overlays and error/selected states; readable text, alignment and unobscured controls |
| Happy path | Enter all choices/values; compare with final state/payload |
| Required omissions | Leave each required choice or field out separately |
| Validation | Exercise each validation error with safe test data |
| Recovery | Back, return, rerender and each coupon/address/error transition |
| Keyboard only | Whole primary task, including intermediate choices and recovery |
| Reading order | Each intermediate screen's meaningful sequence and focus order |

List reached/missing screens, states and devices. Check Korean clipping/IME where relevant; verify retained values after every step. Author `success.task_checks` for material fields after error/coupon/address/recovery transitions and at completion (`drivers/web/README.md`). Failed submit: record the actual focus, invalid state and error association. Automatic first-invalid focus and errors clearing while typing become findings only with blocked navigation or completion, broken error association, an incorrect submission, or explicit spec/standard support; otherwise they stay observations. Success requires final options/quantities/amounts/notes to match. Each row: pass/partial/fail/untested with reason.

Record the UI card's component/screen matrices for every product UI QA.

Scenario: ID/task/goal, safe data, condition, device/input/start, expected result/integrity/risk, claim IDs and omissions. Audience rows cite audience_id/segment_id/task_id/facet and gate-supported motivations. Without an audience, choose task-changing strata: new/returning, touch/keyboard, interruption, delay, empty/stale/edge data. Do not add demographic decoration or stereotypes.

Optional dataset: record source/revision/schema, bounded sample/seed/config, IDs/strata and stop; separate attributes from assumptions. Scenario detail: `references/persona-qa/persona-scenario-design.md` by section.

## 2. Exercise and capture

Exercise actual product/input/start state; capture decisions/recovery, console/network/runtime errors, keyboard/focus/semantics and feedback. Screenshots support the trace; available interactions require flow evidence.

Blind touch uses screenshots before DOM/source/run data. A separate a11y or screenshot+a11y auditor reproduces transitions with provenance; `drive_client.mjs --port 9477 inspect` after each step/failed submit records values, choices, invalid/error association, focus and reading order. Screenshot-only sessions refuse inspect; never leak DOM knowledge into the blind pass. Programmatic evidence cannot stand for assistive-tech speech. Scripted replay uses `ergo_drive.mjs run` with the same scenario/profile/build and authored steps/integrity criteria. Driver success cannot override data loss.

Budget a bounded task matrix. Stop at missing access or unsafe actions; posting, purchase, signup, account and data changes need separate authorization. Production identity/SMS/CAPTCHA/security-keypad/certificate/payment gates stop; only approved staging mocks or test payment complete. No real government/contact/payment/account inputs. Team-approved origins govern widgets; unavailable iframe/popup/app-switch evidence is untested. Lookup `drivers/web/README.md` options/sandbox by section; no installation to pass blocks.

Write a receipt beside each capture during the run:

```text
{artifact_path, sha256, captured_at, surface_url, build_id, device, quoted_ui_text}
```

Build ID: commit/version/deploy ID/page-source hash via `--build-id` or `scenario.surface.build_id`. PNG hashes prove capture integrity only; an unknown build cannot support same-build reproduction. Redact personal data and quote exact UI text.

## 3. Conditional evidence and intended experience

Task-linked research during improvement, or separately requested research, enters `references/research/workflow.md` with access/evidence cards. Use `references/persona-qa/community-to-test.md` by section; supported_high/medium may motivate P0/P1, single_voice/lead_only stay exploratory. Missing gate leaves community motivation unverified; reproduced product harm keeps impact-based severity. Personas receive scrubbed summaries only.

Inspect Figma/spec entry/journey/hierarchy/content/units/variants/tokens/critical states/responsive/input. Bind file/branch/version/nodes/readback to the actual build; view both images using the UI card's procedure. Separate implementation_defect/design_defect/spec_conflict/approved_deviation; unresolved conflict blocks code acceptance, missing source limits fidelity. Differences need task or verified design-rule impact. Proposals follow the project's own design rules.

## 4. Grade, trace and second-pass

Severity: `references/persona-qa/evidence-and-severity.md` by section, impact-based. Reproduced input loss/inaccessible required control can be P0/P1 for blocked/corrupted task. Synthetic confusion stays P2/P3 under caps; preference stays hypothesis. No audience/gate downgrade of observed harm.

Finding: ID/severity/rationale; build/screen/device/viewport/input; persona or scenario/task; steps from start URL; expected and observed with visible UI quotes; capture receipt; user/product impact; verified/inferred cause; fix layer/change/trade-off; standards for accessibility only; second pass; confidence. Consult `references/shared/causal-chain.md` for every P0/P1; unknown organizational constraints remain unknown.

Every P0/P1 requires a second pass over only its capture and text dump, without the draft (at most three priority scenarios):

```text
{finding_id, reviewer: subagent|self, task_completed, control_name,
 omitted, severity: agree|disagree, inconclusive}
```

Without subagents, run a labelled self-pass; it is not independent review. Resolve every disagreement in writing before finalization. Unreadable artifacts require recapture or inconclusive status. Korean accessibility findings have separate KWCAG 2.2 and WCAG 2.2 item/status/coverage; lookup mappings in `references/persona-qa/kwcag-2.2.md` by ID.

## 5. Remediate, replay and report

Fix the reproduced cause with a minimal intent-compatible change. State expected behavior, trade-off and validation; benefit claims need measurements. Reuse the improvement request's scoped grants; standalone review remains read-only. When the project keeps design in Figma, change it there first with actual nodes/version/readback; missing access blocks only that change. Replay the original scenario/data/build scope/device/input, primary task, recovery, adjacent states, Figma and accessibility. Explicitly recheck preserved decisions; retain baseline/change/replay evidence. Acceptance requires passing replay, regression and intent checks.

Use `references/persona-qa/qa-report-template.md` by section: Decision first (verdict rules, at most three actions, one untested line), then findings.

Then matrix/basis, ranked cards, P0/P1 causes, recommendations, Figma/artifacts/replay/unverified/next evidence. Community/access annex only if run; omit zero stops. Emulation/AT/identity/payment limits explicit; language adds no research administration. Reusable artifacts: `references/research/evidence-bundle-contract.md` by section (persona copy exists); verified findings link observed observations/completed runs/scenarios. Record separate read/write/blocked reasons.

Validate reusable bundles with `scripts/validate_bundle.py`. To attach a recorded profile run, set `PROFILE_ID` to its actual ID and bind the matching bundle scenario. Preserve device/orientation/capture times and successful runs. Output and receipt copies use new paths outside inputs/run folders:

```sh
python3 scripts/ergo_qa.py attach --bundle bundle.json --runs "runs/scenario-1/$RUN_ID" --profiles work/profiles.json \
  --scenario sc.json --bind "scenario-1=$PROFILE_ID" --receipts-dir receipts/ --out bundle.ergo.json
python3 scripts/validate_bundle.py bundle.ergo.json --artifacts-root receipts/
```

For P0/P1 supply `--second-pass` records for the exact `finding_id` and capture/text. Link completed value mismatches to `TI-01`/captures, preserving `task_success:false`. Missing/unreached checks stay unknown. Preserve existing evidence; never duplicate anonymous review records or bind device-only recordings as persona executions.

## Failure ladder

| Missing/failing | Next step; ask boundary |
| --- | --- |
| Browser/build | Highest available fallback; if denied/unavailable, named blocker and inconclusive. Ask only for access needed to exercise the task. |
| Dataset/audience | Brief-derived synthetic conditions; continue QA, no invented participants. |
| Community source/key | When research is active: obey final stops, continue eligible sources and QA; ask for an environment key only if material and not declined. |
| Figma/verifier | Conditional comparison; labelled self-pass. Ask for missing required design decision or independent/human verification. |
| Coverage/time | Finish bounded rows, list untested ones; minimum unmet means inconclusive. |

## Done when

Scoped coverage or exact gaps reported; findings graded and reviewed under section 4; reusable bundle validates; report names build, limits and replay outcome. No unauthorized side effect occurred.
