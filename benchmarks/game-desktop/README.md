# Benchmark suite: `game-desktop`

A blind validation suite for the ergonomic persona-swarm QA tool (`ergoqa`, see
`docs/ergonomic-swarm-spec.md` §12). It was written without reading `ergoqa/`,
`drivers/` or `scripts/`. It has two Korean-language surfaces. Each surface comes in
two variants: a **target** variant and a **clean control** variant. Both variants run
the same task flow.

The seeded issues, the decoys and the clean-control notes are listed only in
`answer_key.json`. This README describes the surfaces and conventions and does not
say what is wrong with them.

## Layout

```
benchmarks/game-desktop/
  site/game.html              (A) canvas runner game, target variant
  site/game-clean.html        (A) canvas runner game, clean control
  site/admin.html             (B) desktop admin dashboard, target variant
  site/admin-clean.html       (B) desktop admin dashboard, clean control
  scenarios/SC-game-run-01.json
  scenarios/SC-game-run-01-clean.json
  scenarios/SC-admin-members-01.json
  scenarios/SC-admin-members-01-clean.json
  answer_key.json
```

Every page is a single self-contained static HTML file with inline CSS and JS. The
pages make no network requests, load no external fonts and use system fonts only.
Serve the `benchmarks/` directory, for example
`python3 -m http.server 8765 --bind 127.0.0.1` from `benchmarks/`, and set
`{BASE}` = `http://127.0.0.1:8765`.

## Surface A: "별빛 러너" (mobile landscape runner game)

- It is designed for a phone held in landscape (Galaxy S24 landscape, 780×360 CSS px,
  dpr 3, touch). The scenarios declare `"device_ids": ["galaxy-s24"]` and a top-level
  `"orientation": "landscape"`. If the portrait viewport is used instead, the layout
  adapts and the flow still completes, but the static `hotspots` in the scenario only
  match the 780×360 landscape layout.
- The playfield and the virtual controls are drawn on a `<canvas>`. The page exposes
  the controls through
  `window.__ergoqa__.hotspots()`, which returns
  `[{id, name, box:{x,y,w,h}, roles:["game_control"]}]` in CSS px relative to the
  viewport. It returns only the controls currently on screen: none before start;
  `hs-stick` and `hs-pause` throughout play; `hs-jump` and `hs-attack` in stages
  1–3.
  The scenario files also carry the same boxes (measured at 780×360) under
  `hotspots` as a fallback. Scenario steps target them as `hotspot:<id>`.
- The HUD and prompts are DOM elements, so text size and colour can be measured:
  `#hud-stats` (score/HP), `#coin`, `#subtitle` (dialogue that tells the player what
  to do), `#pop` (score pop-up), `#flash` (hit feedback), `#qte` (timed prompt),
  `#mash` (escape prompt), `#radar`, `#radar-1` and `#radar-2` (supply-target
  picker), and `#clear` (stage clear). The sky behind the HUD is the CSS background
  of `#stage`, the ancestor of every HUD element. The canvas draws only the ground,
  hills, clouds, characters and controls.
- The task flow is event driven: tap to start → jump over the thorn bush → the guard
  hits you, then counter-attack → press the timed prompt → break free from the
  grab → give the supply to the ally → `#clear`.
- The `#qte` prompt stays visible for its whole response window, whether or not it
  was hit. Its `visible_duration` therefore equals the window length. A miss costs
  HP and the prompt reappears, up to 3 attempts. After that, the flow continues
  either way.
- Keyboard mapping, for `gamepad`/`press`: Space/↑ = jump, J = attack,
  E/Enter = timed prompt or escape prompt, ←/→ = move, Esc = pause.

## Surface B: "ORBIT Console" member management (desktop, 1920×1080, mouse)

- The scenarios declare `"device_ids": ["desktop-1920"]`, meaning a 1920×1080
  CSS px viewport, dpr 1, mouse. The benchmark author did not read the device
  catalog. This id was seen in another agent's smoke-test scenario. If the catalog
  names the 1920×1080 mouse device differently, map it before running.
- The task is to open the add-member form from the list toolbar, try to save with
  the email missing, see the error, fill in the email, save, and confirm that the new
  row `#saved-row` appears.
- The declared roles are:
  - primary: `#save`
  - destructive: `#delete-all`, `#row-remove`
  - critical_message: `#notice`
  - error_message: `#form-errors`
  - status/timed: `#toast`
  - ad_like: `#promo`

## Answer-key conventions

- `element_selector` is an element id selector. There are two exceptions:
  - Canvas hotspots use the bare hotspot id (for example `hs-<name>`), so it matches
    `hs-<name>`, `#hs-<name>` and `hotspot:hs-<name>`.
  - A key may name a container whose children share its id as a prefix. For example,
    a container `#foo` has the children `#foo-1` and `#foo-2`. The scorer's "finding
    selector contains key selector" rule then covers findings reported on any of the
    children.
- `profile_condition` uses the nested shape of `ergo-profile.v1` `attributes`, for
  example `{"grip": "two_thumbs"}` or `{"vision": {"cvd": "deutan"}}`. It is a subset
  match. `{}` means any profile.
- `severity_min` assumes P0 is the most severe and P3 the least severe.
- Decoys are present, unchanged, in both variants. Any finding on a clean-control
  scenario is a false-positive candidate. Under §12 it still needs manual
  adjudication.

## Verification performed by the author

The scenarios were checked with Node Playwright 1.56 and the bundled Chromium,
serving `benchmarks/` over `python3 -m http.server`:

- All four scenarios complete their scripted steps with no page errors. The success
  selectors (`#clear`, `#saved-row`) become visible.
- The game flow also completes in portrait (Galaxy S24, 360×780) for both variants.
- The selector-driven tap on `#qte` hit the prompt in 5 out of 5 runs of the target
  variant.
- Timing windows were measured with a MutationObserver on the `hidden` attribute.
  Element boxes, computed font sizes and colours were read from the DOM. The
  measured values relevant to scoring are recorded in the `answer_key.json`
  descriptions.
