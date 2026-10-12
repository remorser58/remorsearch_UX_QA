# Platform Drivers

Every finding must come from the real surface. Drivers measure; they never score
ergonomics or role-play a user. All of them emit `ergo-snapshot.v1` /
`ergo-run.v1` (`docs/ergonomic-swarm-spec.md`), so `scripts/ergo_qa.py` analyses
them the same way.
These are repository documents, not installed with the skill.

| Surface | Path | What is real | What is not exercised here |
| --- | --- | --- | --- |
| Web, mobile web, browser games (canvas/WebGL) | `drivers/web/ergo_drive.mjs` (Node 22 + Playwright/Chromium) | Real touch/mouse/keyboard input (CDP), device-emulated viewport/DPR/touch, screenshots, DOM geometry and composited colours, feedback latency, 16 ms timing-window polling, flash sampling, off-origin network blocking | WebKit/Safari, real phones, on-screen keyboards, browser chrome, iframes/closed shadow roots |
| Android apps | `adb exec-out uiautomator dump` + `adb exec-out screencap -p` → `scripts/ergo_qa.py android-snapshot`; inputs via `ergoqa/drivers/android.py` argv builders | Real device geometry (bounds in px → dp) and screenshots when run against a device/emulator | Live device execution is not exercised in this repository (fixture-tested only) |
| iOS apps | Exported XCUITest attachments + typed `xcuitest-capture.v1` JSON → `scripts/ergo_qa.py ios-import` | Actual XCUIElement point frames, label/identifier/value/enabled, PNG dimensions/hash, xcresult attachment/test summary join, built app bundle identity | VoiceOver/accessibility order, fonts, colours, intent, action/task outcome, and independent screenshot authenticity; device geometries absent from `ergoqa/devices.py` are rejected rather than nearest-mapped |
| Desktop apps, engine-rendered games | Platform screenshot + vision/human annotation → `ergoqa/drivers/annotation.py` | Screenshots from the real device | Geometry is estimated (`source: vision`), so every geometry-based observation is `inferred` |

## Web driver quick reference

```sh
# Scripted scenario
node drivers/web/ergo_drive.mjs run --scenario sc.json --profile ep.json --out runs/ \
  --base http://127.0.0.1:8765 [--flash-sample-ms 1500]

# Interactive session for a persona agent (127.0.0.1 only)
node drivers/web/ergo_drive.mjs serve --scenario sc.json --profile ep.json --agent-json agent.json --out runs/ --port 9477
curl -s localhost:9477/snapshot
curl -s -X POST localhost:9477/act  -d '{"action":"tap","target":"#pay"}'
curl -s -X POST localhost:9477/note -d '{"step_index":1,"intent":"…","expected":"…","observed":"…","confusion":false,"failure_class":"ux_issue"}'
curl -s -X POST localhost:9477/finish -d '{"success":true}'

# Self-test (~1 minute)
node drivers/web/selftest.mjs
```

Scenario notes:

- `surface.kind` is `web` or `game` (browser game). Canvas controls are exposed
  with `scenario.hotspots` or `window.__ergoqa__.hotspots()`; roles such as
  `game_control`, `hud`, `timed` come from the scenario, never guessed.
- Declare `timing_windows` with `kind: "transient_text"` (toasts) or
  `kind: "qte"` (timed inputs). Undeclared kinds are inferred: a window the run
  acted on, or a short interactive/timed game prompt, is a timed input; a window
  with a readable message is transient text; others are decorative. Windows
  that toggle repeatedly are screened as flash sources (WCAG 2.3.1) from the
  16 ms DOM poll, because frame sampling (~30 fps) aliases fast flashes.
- Each snapshot also stores a CSS-scale copy of the screenshot
  (`screenshot.css`) for fast analysis, and each element lists up to three
  ancestor ids (`ancestor_ids`) so grouped controls (toolbars, chip rows) can be
  reported by their container.

Full option list, measured fields and limitations: `drivers/web/README.md`.

## Real devices and games

iOS import consumes an already exported native-evidence directory; it is not a test runner. The directory must
contain the actual xcresult attachment manifest/export files, test summary/results, built target app
`Info.plist`, fixture origin and run metadata. The caller explicitly binds the supported catalog device,
one exact capture UUID, scenario/profile, route and fixture identity; the importer cross-checks app/build
identity, device model, point/pixel geometry, capture intervals and UUID-named attachments. The source
XCTest result is provenance only: the selected capture is a separate completed observation with unknown UX
task success. An optional producer image_source value of device_screen marks an actual XCUIScreen PNG;
omitting it keeps the historical application-screenshot meaning, and pixels are never rescaled. Product
validation fixtures use --fixture-kind synthetic_app_data even when execution is real. XCUI cells remain
non-actionable rows, visual visibility is unsupported, and accessibility, fonts, colours and intent remain
unknown unless separately measured.

Required evidence layout:

```text
EVIDENCE/
  screenshots/manifest.json
  screenshots/<exported rq-native JSON and PNG attachments>
  test-summary.json
  test-results.json
  metadata.txt                 # one xcode_version= entry
  fixture-origin.txt
  <result>.xcresult/Info.plist
  built-app/<Bundle>.app/Info.plist
  artifact-sha256.txt          # binds every consumed file above
```

There must be exactly one actual built application Info.plist matching the selected capture's application_id;
the bundle identity must match application_id. Package the actual build Info.plist even when
DerivedData is reused; a source path or historical build directory does not satisfy the importer. Preserve the
frozen native evidence unchanged and always write imports to a fresh output directory.

Portable one-capture import template:

```sh
RQ_EVIDENCE="/path/to/completed-xcresult-evidence"
RQ_OUT="/path/to/new-empty-import-output"
RQ_CAPTURE_ID="actual-producer-capture-uuid"

python3 skills/remorsearch-ux-qa/scripts/ergo_qa.py ios-import \
  --evidence "$RQ_EVIDENCE" \
  --out "$RQ_OUT" \
  --device iphone-15-pro-max \
  --capture-id "$RQ_CAPTURE_ID" \
  --scenario-id SC-release-surface-customization \
  --profile-id EP-01 \
  --route /settings/customization \
  --fixture-id owned-native-qa-fixture \
  --fixture-kind synthetic_app_data
```

The route, scenario, profile and fixture labels are caller bindings. They do not independently prove
navigation, intent or task success. The importer always leaves the imported run's success value null; task
evidence is assessed separately and this command does not mutate that result.

- Timing-critical game checks need frame-accurate capture: a capture card or
  engine-side capture (EA IRIS UE5 plugin), and hardware input injection when
  end-to-end latency matters; software injection under-reports latency.
- Run LLM persona agents paused or frame-stepped for games; timing windows are
  judged from measurements, never from the agent failing in real time.
- Physical device size and pixel pitch always come from `ergoqa/devices.py`;
  add a device there (with its source) before testing it.
