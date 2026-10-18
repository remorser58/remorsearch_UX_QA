# ergoqa — Ergonomic Persona Swarm QA: interface specification (v1)

Status: authoritative contract for all implementers. Do not change names or shapes
without updating this file. Python is standard-library only (3.10+). The live web
driver is Node.js + the globally installed `playwright` package (Chromium at
/opt/pw-browsers). Nothing reaches the network except the local page under test.

## 0. Principles that are hard rules

1. Deterministic human-factors models compute ergonomics (reach, pointing, gaze
   priority, contrast, colour-vision, reading time, reaction windows). LLM persona
   agents never role-play these numbers ("my thumb hurts"); they only look at the
   screen, choose actions toward the task goal, and record expectation vs. outcome.
2. Every observation carries `basis`:
   - `measured` — geometry, colour, timing read from the real surface (epistemic `observed`);
   - `model` — a published-model prediction applied to measured inputs (epistemic `inferred`, with `model` id and version);
   - `judgment` — an LLM/human qualitative judgment on a screenshot (epistemic `inferred`).
3. A swarm result reports "k of n simulated profiles triggered the check" as
   COVERAGE, never as prevalence/percent of real users.
4. Ergonomic attributes not present in the persona dataset (handedness, grip, hand
   size, vision, motor, device) are scenario assumptions and are listed in
   `assumption_fields` of the profile.
5. Stratified coverage sampling (guarantee left-handed, one-handed, CVD, presbyopia,
   tremor, walking, etc. appear) is the default. Base-rate sampling exists only to
   choose plausible combinations; it must not be reported as population estimates.
6. Research and QA stay read-only on real products. The driver only performs the
   declared scenario actions on the declared surface.

## 1. Device catalog (`ergoqa/devices.py`)

`Device` dataclass:
```
id: str                    # e.g. "galaxy-s24"
label: str
form_factor: "phone" | "tablet" | "foldable" | "desktop" | "laptop" | "tv" | "handheld_console"
viewport_css: (w, h)       # portrait CSS px (or landscape for desktop/tv)
dpr: float
physical_mm: (w, h)        # body width/height of the device (for grip/reach)
display_mm: (w, h)         # active display area width/height in mm
input: "touch" | "mouse" | "keyboard" | "gamepad" | "remote"
viewing_distance_mm: int   # typical
playwright_device: str|None   # name in playwright.devices, if any
source: str                # spec source note
```
Functions: `get_device(id)`, `list_devices()`, `css_px_to_mm(device, px, axis)`,
`mm_to_css_px(...)`, `rotate(device)` for landscape.
Catalog MUST include at least: galaxy-s24, galaxy-s24-ultra, galaxy-a55, galaxy-z-flip6,
galaxy-z-fold6-inner, iphone-15, iphone-15-pro-max, pixel-8, galaxy-tab-s9,
desktop-1920 (24" monitor), laptop-1440 (14"), tv-55-1080 (10-foot UI),
switch-handheld (handheld console, gamepad).

## 2. Ergonomic profile (`ergo-profile.v1`, `ergoqa/profiles.py`)

```json
{
  "schema_version": "ergo-profile.v1",
  "profile_id": "EP-01",
  "origin": "stratified_coverage | base_rate_sample | manual",
  "persona_ref": {"dataset": "nvidia/Nemotron-Personas-Korea", "revision": "...", "record_id": "..."} ,
  "label_ko": "왼손잡이 · 한 손 파지 · 이동 중",
  "attributes": {
    "age_band": "10s|20s|30s|40s|50s|60s|70s+",
    "handedness": "right|left|mixed",
    "grip": "one_hand_right|one_hand_left|cradle_right|cradle_left|two_thumbs|mouse_right|mouse_left|keyboard_only|gamepad|remote",
    "thumb_length_mm": 62.0,
    "hand_percentile": 50,
    "device_id": "galaxy-s24",
    "orientation": "portrait|landscape",
    "vision": {"acuity": "normal|reduced|low", "presbyopia": false, "cvd": "none|protan|deutan|tritan", "cvd_severity": 1.0, "viewing_distance_mm": 300},
    "motor": {"tremor": "none|mild|moderate", "touch_sigma_mm": 1.5},
    "context": {"mobility": "seated|walking|transit", "lighting": "indoor|bright_sun|dark", "free_hands": 1, "interruptions": false},
    "cognition": {"familiarity": "first_use|returning|expert", "time_pressure": "low|high", "reading_wpm_ko": 0},
    "reaction_time_ms": 250
  },
  "assumption_fields": ["handedness", "grip", "thumb_length_mm", "vision", "motor", "context", "device_id"],
  "base_rate_refs": {"handedness": "REF-..."}
}
```
Functions:
- `sample_profiles(count, seed, device_ids, strategy="stratified_coverage", persona_records=None) -> list[dict]`
  Deterministic for a seed. Stratified coverage fills these strata before anything
  else when count allows: right one-hand, left one-hand, two-thumbs, cradle,
  cvd≠none, presbyopia, tremor≠none, walking, bright_sun, first_use, 60s+.
- `validate_profile(p) -> list[str]` errors.
- `effective_touch_sigma_mm(p)` combines base σ, tremor, walking multipliers.
- `persona_to_profile(persona_record, ...)` keeps persona fields as `persona_ref`,
  never infers handedness/vision from demographics.

## 3. Snapshot (`ergo-snapshot.v1`) — produced by every driver

```json
{
  "schema_version": "ergo-snapshot.v1",
  "snapshot_id": "S-r1-003",
  "run_id": "R-...",
  "step_index": 3,
  "captured_at": "2026-09-28T12:00:00Z",
  "surface": {"kind": "web|android|ios|desktop|game", "url": "...", "title": "...", "app_id": null},
  "device": {"id": "galaxy-s24", "viewport_css": [360, 780], "dpr": 3.0, "orientation": "portrait"},
  "screenshot": {"path": "S-r1-003.png", "sha256": "...", "width_px": 1080, "height_px": 2340},
  "elements": [
    {
      "id": "el-12",
      "role": "button",
      "name": "결제하기",
      "text": "결제하기",
      "tag": "button",
      "selector": "#pay",
      "box": {"x": 16, "y": 700, "w": 328, "h": 48},
      "interactive": true, "visible": true, "enabled": true, "in_viewport": true,
      "font_size_px": 16, "font_weight": 700,
      "color_fg": "#ffffff", "color_bg": "#1a73e8",
      "border_color": null,
      "roles": ["primary"],
      "source": "dom|uiautomator|a11y|vision|manual"
    }
  ],
  "focus_point": {"x": 180, "y": 724},
  "console_errors": [],
  "notes": []
}
```
- `box` is in CSS px relative to the viewport's top-left (visible area).
- `roles` values: `primary`, `destructive`, `irreversible`, `critical_message`, `error_message`,
  `status`, `navigation`, `ad_like`, `hud`, `game_control`, `timed`.
  `irreversible` marks a destructive/payment action that cannot be undone and has no
  confirmation (declared by the scenario author after checking it in a sandbox).
  Roles come from the scenario's `targets` (selectors/text), from
  `data-ergo-role` attributes, or from an annotation; never guessed silently.
- `focus_point` = where the user's attention/finger was at the last action (for
  feedback-noticing checks); null on the first snapshot.
- Colours are hex; `color_bg` is the effective opaque background behind the element
  (driver walks ancestors; null if unknown/image). `container_bg` is the composited
  background of the layers below the element (what its boundary is seen against).
- Layer fields (web driver, additive): `occluded_fraction` (0–1, share of five sample
  points inside the visible box where another element — not the element, a
  descendant or an ancestor — is on top, e.g. a bottom sheet or scrim; null when
  off-screen), `occluded_by` (selector of the covering element), `inert_by_modal`
  (true when an open modal — `dialog:modal` or a visible `[aria-modal="true"]` — does
  not contain the element). Checks skip elements that are inert or ≥ 50 % covered in
  that snapshot; they are evaluated in the snapshots where they are usable.
- Text elements are listed only when they own a text node, so a `<li>` whose text is
  inside a child button does not report the child's text with its own font size.
- Semantics fields (web driver, additive): `dom_id`; for controls and form fields
  `a11y` = {`name_source` (aria-labelledby | aria-label | alt | value | label |
  placeholder | content | title | none), `invalid` (aria-invalid), `user_invalid`
  (`:user-invalid`), `described_by` (ids that exist), `error_message`, `required`,
  `focusable`, `tabindex`}; for text elements whose own box cuts their text,
  `clipped` = {`x`, `y`, `ellipsis`}.

## 4. Scenario (`ergo-scenario.v1`)

```json
{
  "schema_version": "ergo-scenario.v1",
  "scenario_id": "SC-checkout-01",
  "surface": {"kind": "web", "url": "http://127.0.0.1:8765/shop/index.html"},
  "task_goal_ko": "장바구니 상품을 결제한다",
  "device_ids": ["galaxy-s24"],
  "targets": {
    "primary": ["#pay"],
    "destructive": ["#delete-all"],
    "critical_message": ["#error"],
    "ad_like": [], "hud": [], "game_control": [], "timed": []
  },
  "steps": [
    {"action": "tap", "target": "#add"},
    {"action": "wait", "ms": 300},
    {"action": "tap", "target": "text=결제하기"}
  ],
  "timing_windows": [{"id": "qte-1", "selector": "#qte", "measure": "visible_duration", "kind": "qte"},
                     {"id": "toast-1", "selector": "#toast", "measure": "visible_duration", "kind": "transient_text"}],
  "success": {"selector_visible": "#done"},
  "hotspots": [{"id": "hs-jump", "name": "jump", "box": {"x": 300, "y": 600, "w": 64, "h": 64}, "roles": ["game_control"]}]
}
```
Actions: `tap`, `click`, `double_tap`, `long_press`, `swipe`, `drag`, `type`,
`press` (key), `scroll`, `wait`, `snapshot`, `gamepad` (web: keyboard mapping).
`target` is a Playwright selector or `hotspot:<id>` or `{x,y}`.

## 5. Run (`ergo-run.v1`) — directory layout

```
runs/<run_id>/run.json
runs/<run_id>/S-<run>-000.json + .png
...
```
`run.json`:
```json
{
  "schema_version": "ergo-run.v1",
  "run_id": "R-...",
  "scenario_id": "...",
  "profile_id": "EP-01",
  "driver": {"name": "playwright-web", "version": "1.56.1", "browser": "chromium"},
  "device": {...snapshot device...},
  "mode": "scripted|interactive",
  "started_at": "...", "ended_at": "...",
  "status": "completed|failed|blocked",
  "success": true,
  "steps": [
    {"step_index": 1, "action": {...}, "target_element_id": "el-12", "point": {"x": 180, "y": 724},
     "before": "S-...-000", "after": "S-...-001", "t_start_ms": 0, "t_end_ms": 120,
     "feedback_latency_ms": 80, "result": "ok|error|no_target", "error": null}
  ],
  "timing_windows": [{"id": "qte-1", "selector": "#qte", "kind": "qte", "visible_ms": 400,
                      "intervals_ms": [400], "text": "지금 누르세요!"}],
  "flash_samples": [{"t_ms": 0, "mean_luminance": 0.3}],
  "focus_walks": [{"phase": "load|end", "snapshot_id": "S-...-000", "ended": "cycle|left_document|max_stops|refocus_failed",
                   "stops": [{"selector": "#pay", "dom_id": "pay", "role": "button", "name": "결제하기",
                              "box": {"x": 0, "y": 0, "w": 0, "h": 0}, "in_viewport": true,
                              "indicator_px": 530, "clip_px": [120, 56], "obscured_fraction": 0, "obscured_by": null}]}],
  "persona_notes": [{"step_index": 1, "intent": "...", "expected": "...", "observed": "...", "confusion": false}]
}
```
`persona_notes` are written by the LLM persona agent in interactive mode (basis judgment).
`agent` (additive): from `--agent-json` `{model_family, input_channel
(screenshot|a11y|screenshot+a11y), model, model_version, effort, temperature, seed,
persona_arm, prompt_sha256, max_steps, description}`, or `{"description": ...}` from
`--agent`; `"unrecorded"` for interactive runs without either.
Persona notes (additive): `anchor` ("acted" | {point} | {box}), `anchor_snapshot_id`,
`anchor_element_ids`, `anchor_selectors`, `screen_key` (URL path + hash of visible
headings + "+modal"); `severity_claimed` and `corroborated_claimed` are stored but
never used. PJ-01 observations are keyed by the anchor selector; `swarm.aggregate`
marks a PJ-01 finding corroborated (P2, tier finding) only when notes at the same
anchor come from runs that differ in `model_family` or `input_channel`; otherwise it
is a P3 hypothesis.

## 6. Observation (`ergoqa/checks.py`, produced by `analyze`)

```json
{
  "id": "OB-...",
  "check_id": "RH-01",
  "category": "reach|pointing|gaze|perception|cognition|game|heuristic",
  "run_id": "R-...", "profile_id": "EP-01", "snapshot_id": "S-...", "step_index": 3,
  "element_ids": ["el-12"], "element_key": "#pay|결제하기",
  "basis": "measured|model|judgment",
  "epistemic_status": "observed|inferred",
  "model": "thumb-reach-v1",
  "measurement": {"name": "reach_difficulty", "value": 0.82, "unit": "0-1", "threshold": 0.66, "comparator": ">"},
  "passed": false,
  "severity": "P0|P1|P2|P3|null",
  "message_ko": "...", "message_en": "...",
  "refs": ["REF-bergstrom2014"]
}
```
`passed: true` observations are kept only in verbose mode (for coverage accounting).

## 7. Aggregated finding (swarm)

```json
{
  "id": "EF-001",
  "check_id": "RH-01",
  "element_key": "#pay|결제하기",
  "screen_key": "url-or-title + step",
  "severity": "P1",
  "basis": "model",
  "epistemic_status": "inferred",
  "triggered_profiles": ["EP-02", "EP-05"],
  "tested_profiles": ["EP-01", "EP-02", "EP-05", "EP-07"],
  "coverage_label": "2/4 simulated profiles (coverage, not prevalence)",
  "profile_specific": {"handedness": "left"},
  "observation_ids": ["OB-..."],
  "summary_ko": "...",
  "fix_layer": "interaction|visual|ia|content|accessibility|service",
  "recommendation_ko": "...",
  "refs": ["REF-..."]
}
```
`profile_specific` = attribute values shared by ALL triggered profiles and by NONE of
the evaluated-but-untriggered ones (the differential condition). Severity = max
observation severity; each check's own rule already accounts for the element's role
(primary, destructive, path), so there is no separate escalation step.

Additive fields and rules (2026-09-28):

- `tested_profiles` is every profile evaluated on the run's device and orientation
  for which `checks.applicable(check_id, profile, device)` is true (CVD checks: CVD
  profiles; touch checks: touch profiles; reach: phone one-hand/two-thumb grips),
  not only the profiles that emitted an observation. `profile_specific` is computed
  against those tested-but-untriggered profiles.
- Findings are grouped by (scenario, check, element selector); the element's text
  is display only (a countdown is one element, not one finding per value).
- `tier`: `finding` or `hypothesis`. Hypothesis checks (`checks.HYPOTHESIS_CHECKS`:
  GZ-01, GZ-04, PC-05) are listed for review and excluded from defect counts,
  benchmark scoring (`bench.score(..., include_hypotheses=False)`) and `--fail-on`.
- `segments_affected`: audience segments whose composed profiles triggered it.
- **Problem units** (`swarm.units`): findings with the same scenario, check and
  differential condition form one unit `{id: "EU-nnn", instances: [EF ids],
  elements, severity (worst), condition, tier}`. Reports and triage count units.

## 8. Evidence bundle export

`ergoqa/bundle.py:to_evidence_bundle(...)` emits `ux-evidence-bundle.v1` that passes
`scripts/validate_bundle.py` (import `validate_bundle` from it in tests):
- permissions: requested ["read_only"], granted ["read_only"], blocked [].
- personas: one per ergonomic profile, `basis: "synthetic"`, with ALL fields that the
  validator requires for synthetic personas (adapter_revision "ergoqa-profiles/1",
  schema_fingerprint = sha256 of sorted profile keys, seed, shard_or_config =
  strategy, max_scanned_rows/max_bytes_read/timeout_ms integers (0 when no dataset
  read), selected_record_ids (persona_ref record ids or []), filled_strata,
  unfilled_strata, stop_reason, original_attributes = persona_ref fields or {},
  scenario_assumptions = the ergonomic attributes listed in assumption_fields).
- scenarios: one per (scenario_id, profile_id) pair: id `"{scenario_id}@{profile_id}"`,
  `persona_id` = profile id record.
- runs: id = run_id, `scenario_id` = the pair id, `status` = run status.
- observations: failed checks only; `epistemic_status` from basis; `run_id`.
- findings: one bundle finding per (swarm finding × triggered pair): id
  `"{EF-id}@{profile_id}"`, `scenario_id` = pair id, `observation_ids` of that pair,
  `severity`, `swarm_finding_id`; `verification_status` "verified" ONLY when every
  linked observation is basis `measured` (observed) from a completed run of that same
  pair; otherwise "unverified" with epistemic `inferred`.
- proposals: one per swarm finding with a recommendation, `finding_ids` = its bundle findings.
- sources/evidence/claims/figma: empty arrays unless supplied.

## 9. CLI (`skills/remorsearch-ux-qa/scripts/ergo_qa.py` → `ergoqa/cli.py`)

```
ergo_qa.py devices [--json]
ergo_qa.py profiles --count N --seed S --devices galaxy-s24,iphone-15 [--strategy stratified_coverage] --out profiles.json
ergo_qa.py analyze --run runs/R-x [--profiles profiles.json] --out obs.json
ergo_qa.py swarm --runs runs/ --profiles profiles.json --out report_dir [--bundle]
      -> report_dir/findings.json, report_dir/report.md (Korean), report_dir/bundle.json
ergo_qa.py heatmap --snapshot runs/R-x/S-..json --profile EP-01 --kind reach|gaze|touch --out map.png
ergo_qa.py bench --key benchmarks/.../answer_key.json --findings report_dir/findings.json
ergo_qa.py android-snapshot --xml dump.xml --png screen.png --device galaxy-s24 --out snap.json
```
Exit codes: 0 ok, 1 findings at/above `--fail-on` severity, 2 usage/input error.

## 10. Web driver (`drivers/web/ergo_drive.mjs`)

```
node skills/remorsearch-ux-qa/drivers/web/ergo_drive.mjs run --scenario sc.json --profile p.json --out runs/ [--run-id R-x]
node skills/remorsearch-ux-qa/drivers/web/ergo_drive.mjs serve --scenario sc.json --profile p.json --agent-json agent.json --out runs/ --port 9477
   POST /act   {"action":"tap","target":"#pay"}  -> {"snapshot": ".../S-..json", "png": ".../S-..png", "result": "ok"}
   GET  /snapshot                               -> same, without acting
   POST /note  {"intent":..,"expected":..,"observed":..,"confusion":bool}
   POST /finish {"success": true}               -> writes run.json, exits
```
Resolves `playwright` via normal resolution, then NODE_PATH, then
`/opt/node22/lib/node_modules/playwright`. Emulates the profile's device (viewport,
dpr, hasTouch, isMobile, orientation) and uses real touch/mouse/keyboard events.
Element extraction: interactive elements (a, button, input, select, textarea,
[role=button|link|tab|checkbox|radio|switch|menuitem|slider], [onclick],
[tabindex>=0], canvas) + elements matched by scenario targets + `data-ergo-role`,
plus visible text blocks (p, h1-h6, li, label, span with direct text, [role=alert|status])
with `interactive:false`. For canvas games, hotspots from the scenario and
`window.__ergoqa__?.hotspots?.()` become elements with `source:"manual"`.
Timing windows: poll selector visibility every 16 ms. Flash sampling: optional
`--flash-sample-ms 1000` captures the viewport at ~25 fps via screenshots after
load and each input (N ms), during snapshot steps (N ms) and for the whole of
each wait step, with a random 0-15 ms pause between captures (breaks phase lock
with flicker). Additive sample fields: `block_lum` and `block_red` (base64, one
byte per block of `flash_sampling.block_grid`: round(255 x mean relative
luminance), round(255 x share of saturated-red pixels, linear R/(R+G+B) >= 0.8
and (R-G-B) x 320 > 20)), `block_moved` (bitmask of blocks whose change is
explained by content motion) and `motion_css`. Additive `flash_sampling`
fields: `during`, `jitter_ms`, `bursts`, `sampled_ms`, `mean_fps`,
`max_gap_ms`, `run_ms`, `truncated` (null, or where the 6 MB sample cap
stopped sampling), `caps`, `block_grid` (`cols`, `rows`, `block_css`,
`viewport_css`, `frame_px`). GM-04 tracks each block's transitions, counts
flashes per block in any 1 s (50 ms sampling tolerance) and sums the area of
concurrently flashing blocks within any 10 degree field (0.006 sr); a pass with
mean fps < 20, an unsampled wait or truncated sampling is `inconclusive`.
Runs without `block_grid` fall back to the whole-viewport mean.

## 11. Android and annotation drivers

- `ergoqa/drivers/android.py`: parse `uiautomator dump` XML (`bounds="[x1,y1][x2,y2]"`
  device px) → elements in CSS-equivalent dp using density; build snapshot; build
  `adb` argv lists for tap/swipe/text/keyevent (never via shell string). Unit-tested
  with fixture XML only; mark live execution as not exercised.
- `ergoqa/drivers/annotation.py`: convert a vision/human annotation JSON
  (screenshot + boxes + roles) into a snapshot with `source:"vision"`; every
  observation from such geometry gets epistemic `inferred`.

## 12. Benchmark (validation) — written blind by a separate agent

```
benchmarks/<suite>/site/...            fixture pages/games (defect and clean variants)
benchmarks/<suite>/scenarios/*.json    ergo-scenario.v1 (url may use "{BASE}" placeholder = http://127.0.0.1:<port>)
benchmarks/<suite>/answer_key.json
```
`answer_key.json`:
```json
{
  "suite": "mobile-commerce",
  "defects": [
    {"id": "D-01", "scenario_id": "SC-...", "category": "reach|pointing|gaze|perception|cognition|game",
     "element_selector": "#pay", "profile_condition": {"grip": "one_hand_left"},
     "severity_min": "P2", "description": "...", "human_factors_basis": "..."}
  ],
  "decoys": [
    {"id": "N-01", "scenario_id": "SC-...", "category": "pointing", "element_selector": "#icon",
     "description": "looks risky but is acceptable, e.g. 20px icon with >=24px spacing (WCAG 2.5.8 spacing exception)"}
  ],
  "clean_controls": [{"scenario_id": "SC-...-clean", "notes": "same flow with defects fixed"}]
}
```
Scoring matches by scenario_id + category + element (finding element_key or element
selector equals / contains the key's selector) + profile condition (at least one
triggered profile satisfies it). Check IDs are NOT part of the key, so the key does
not depend on detector internals. Findings on clean controls, on decoys, or unmatched
in defect variants are false-positive candidates that need manual adjudication (a
detector may find a real, unseeded issue).
Implementers of ergoqa MUST NOT read `benchmarks/` until the benchmark is scored.
Benchmark authors MUST NOT read `ergoqa/` or `drivers/`.

### 12.1 Suite format v2 (additive; used from `heldout-2`)

Each product in a v2 suite also ships a `benchmarks/<suite>/products/<product>/brief.md`:
what the product is, who it is sold to, the business context and the main tasks,
written like a real product brief. It never mentions seeded defects. Stage-0
audience research reads only the brief plus public sources about real users of
that product category.

Additional answer-key fields per defect (all optional for v1 suites):

| Field | Values | Meaning |
| --- | --- | --- |
| `product` | product slug | which brief the scenario belongs to |
| `detectable_by` | `measurement` \| `model` \| `agent_judgment` | the cheapest evidence that can reveal the defect: a fixed standard on measured geometry/colour/timing, a human-factors model, or an agent operating the task and noticing (dead end, unclear error, missing feedback) |
| `audience_relevance` | `primary` \| `secondary` \| `edge` \| `none` | how much the defect matters to the product's intended users according to the brief (`edge` = small group with high stakes) |
| `taxonomy_ref` | string | the published rule or defect taxonomy the defect instantiates (WCAG SC, Android ATF check, XCTest audit type, ODC/app-review complaint type, game accessibility guideline, human-factors paper) |

Additional categories: `semantics` (accessible name, role, state, focus order,
focus visibility, focus obscured) and `layout` (clipped or truncated text,
overlapping elements, content lost at 320 CSS px reflow or 200 % zoom). Task-flow
problems found by operating the task use the existing `heuristic` category.

Suite-level answer-key field `products`: `[{"product": "...", "brief": "products/<product>/brief.md", "scenarios": ["SC-..."]}]`.

## 13. Audience (`ergo-audience.v1`, `ergoqa/audience.py`) — Stage 0 target-user research

The swarm is composed from research on **who uses the product under test**, not
sampled at random. Stage 0 writes one `ergo-audience.v1` file; `ergo_qa.py
personas --audience` turns it into profiles, deterministically.

```json
{
  "schema_version": "ergo-audience.v1",
  "audience_id": "AU-<product>-<yyyymm>",
  "product": {"name": "...", "category": "...", "surface": "web|android|ios|desktop|game", "locale": "ko-KR", "brief_ref": "..."},
  "researched_at": "YYYY-MM-DD",
  "method": {"summary": "...", "limitations": ["..."]},
  "sources": [{"source_id": "SRC-01", "type": "official_statistics", "title": "...", "url": "...", "accessed_at": "YYYY-MM-DD"}],
  "segments": [{
    "segment_id": "SEG-...", "name_ko": "...", "summary": "...",
    "priority": "primary|secondary|edge",
    "share": {"value": 0.55, "basis": "measured|estimated|unknown", "source_ids": ["SRC-01"]},
    "confidence": "high|medium|low",
    "evidence": [{"source_id": "SRC-02", "claim": "...", "kind": "firsthand|statistic|official|inference"}],
    "age_bands": {"60s": 0.6, "70s+": 0.4},
    "devices": {"galaxy-a55": 0.7, "iphone-15": 0.3},
    "orientation": "portrait",
    "left_hand_share": null,
    "grips": {"one_hand": 0.5, "cradle": 0.35, "two_thumbs": 0.15},
    "familiarity": {"first_use": 0.3, "returning": 0.6, "expert": 0.1},
    "conditions": [{"condition": "presbyopia", "share": 0.9, "stakes": "normal", "source_ids": ["SRC-01"], "why": "..."}],
    "contexts": [{"context_id": "CTX-walk", "mobility": "seated|standing|walking|transit", "lighting": "indoor|bright_sun|dark",
                  "one_handed": true, "interruptions": false, "time_pressure": "low|high", "share": 0.5, "source_ids": ["SRC-02"]}],
    "tasks": [{"task_id": "T-...", "goal_ko": "...", "jtbd": "When ..., I want to ..., so I can ...",
               "frequency": "daily|weekly|monthly|rare|once", "criticality": "safety|health|money|legal|data|access|convenience",
               "concrete_data": {"amount": "20,000원"}, "success_ko": "...", "source_ids": ["SRC-03"]}],
    "pain_points": [{"text": "...", "source_ids": ["SRC-02"], "kind": "firsthand|inference"}]
  }],
  "exclusions": [{"group": "...", "why": "..."}],
  "floors": ["left_hand", "cvd_deutan", "presbyopia", "walking"]
}
```

Rules (validated by `audience-check`):

- `sources[].type` ∈ official_statistics, product_analytics, app_store_reviews,
  community, survey, interview, usability_test, support_tickets, official_docs,
  competitor, market_report, research_paper, product_brief, expert_judgment, news.
- `sources[].bundle_ref` (optional): the source's id in the `ux-evidence-bundle.v1`
  written by the research mode's public-page reader, so a quote can be traced to
  the page read (`references/research/public-page-access.md`).
- Community, app-store review and news sources support **existence** only: a
  share that rests only on them, or `statistic` evidence from them, is rejected
  (record such quotes as `firsthand`). Sizes need statistics, analytics or a
  survey.
- When the research mode wrote a gate (`ux-research-gate.v1`), Stage 0 cross-checks
  it before composition (planned: `audience-check --gate --bundle`).
- Every segment has at least one evidence item; every share, condition, context
  and task cites known `source_id`s. `share.value` is null exactly when
  `basis` is `unknown`.
- `age_bands` keys come from the profile's age bands; `devices` keys must exist in
  the device catalog (add a device with its source first).
- `conditions[].condition` ∈ presbyopia, low_vision, reduced_acuity, cvd_deutan,
  cvd_protan, cvd_tritan, tremor_mild, tremor_moderate, first_use, expert,
  time_pressure, small_hand, large_hand. `stakes: high` marks a small group
  whose failure is costly (it is tried before other minority conditions).
- Every task has `concrete_data`: the values an agent must type or pick. Goals
  without data leave branches untested (persona trial, 2026-09-28).
- `floors` (optional) overrides the inclusive floors; `[]` disables them.

Composition (`audience.compose(audience, budget, floors)`):

1. One **typical member** per segment: modal age band, top device, dominant grip,
   modal context, and every condition with share ≥ 0.5. Ages 50s+ are
   presbyopic unless the segment says otherwise. If the budget is smaller than
   the number of segments, segments are taken by priority, then weight.
2. Segment weight = `share.value`, or a priority default (primary 0.5, secondary
   0.3, edge 0.2) scaled into the share mass left unclaimed.
3. Up to a third of the remaining budget is reserved for unmet floors.
4. **D'Hondt:** the next profile goes to the segment with the highest
   weight / (profiles + 1) that still has an untried facet. Each extra profile
   varies **one facet** of the typical member, in this order: high-stakes
   minority conditions, the left-hand mirror, the typical member on another
   device with ≥ 30 % of the segment, contexts with share ≥ 0.15, other minority
   conditions, first use (≥ 20 %), other age bands (≥ 20 %), other grips
   (≥ 25 %). One facet at a time keeps the differential condition attributable.
5. **Floors** (default `left_hand`, `cvd_deutan`, `presbyopia`, `walking`: the
   conditions whose removal lost unique seeded defects in ≥ 2 of 3 development
   suites): a left-hand profile per input kind (touch, pointer), a walking profile
   on touch devices, and one profile per other floor condition across the swarm. A floor is met by the
   most plausible segment's own facet when it has one, otherwise by a profile
   labelled `inclusive floor (coverage guarantee, not segment evidence)`.
   Unused reserve returns to step 4.
6. Output `ergo-persona-plan.v1`: `profiles` (each with `origin:
   "audience_composed"` and `audience_ref` {audience_id, segment_id,
   segment_priority, context_id, task_ids, facet, floor, reasons, source_ids}),
   `segments` (weight, profiles), `floors_used`, and `untested` (facets and
   segments the budget did not reach — listed in the report). In the evidence
   bundle, each persona record keeps `basis: "synthetic"` and carries the
   profile's `audience_ref`; each finding record carries `segments_affected`.

Rules added after the personas-and-audience research brief (2026-09-28;
`docs/qa-discipline/personas-and-audience-research.md`):

- `evidence[].quote`: required. For `statistic` evidence it must contain the
  source's number; for `official` evidence it must be non-empty.
- `segments[].role`: `operator` (default), `customer` or `served`. Only operators
  get profiles; the others are listed as untested.
- `conditions[].condition` may also be a declared-but-not-simulated condition
  (`hearing_loss`, `deaf`, `screen_reader`, `switch_access`, `cognitive`,
  `magnifier`). These always appear in `untested`, never silently dropped.
  `conditions[].cause` (optional) is `permanent`, `temporary` or `situational`.
- `exclusions[].test_instead` (optional): how an excluded group should be tested.
- The first profile of a segment is its **base profile**, "a base for variation,
  not an average user".
- An age facet never switches presbyopia: presbyopia comes from the segment's
  conditions (the base profile of a 50+ segment is presbyopic unless the segment
  declares presbyopia explicitly), a facet or the floor.
- Differential conditions are computed over every profile evaluated on the device;
  profiles outside a check's scope count as not triggered, so a CVD-only finding
  names `vision.cvd`. The coverage label stays within the check's scope.

Findings gain `segments_affected` (segments whose composed profiles triggered
them). Segment weights steer allocation only; they are never reported as the
share of users affected by a finding.
