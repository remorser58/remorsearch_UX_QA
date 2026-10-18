# heldout-mixed

This suite is a held-out benchmark for `ergoqa`. It was written blind, from the spec only (`docs/ergonomic-swarm-spec.md` §0, §2–§4, §12), and it is meant to be scored **once**.

- Do not tune detectors, thresholds or prompts against this suite.
- Implementers must not open `answer_key.json` or read the page sources before scoring.

## Layout

```
benchmarks/heldout-mixed/
  site/              self-contained static pages (inline CSS/JS, no network, system fonts)
  scenarios/*.json   ergo-scenario.v1, url = "{BASE}/heldout-mixed/site/<page>.html"
  answer_key.json    spec §12 format (plus conventions / measured fields)
```

There are four surfaces. Each one comes in two variants of the same flow: `-a` and `-b`, which have the same task, steps and element ids. `answer_key.json` says which variant is the clean control.

| Scenario files | Pages | Device (`device_ids`) | Task (`task_goal_ko`) |
|---|---|---|---|
| `transfer-a.json`, `transfer-b.json` | `transfer-a.html`, `transfer-b.html` | `galaxy-s24-ultra` (384×824, dpr 3.75, touch, portrait) | Pick 김민지 from the recent list → +10만 ×3 → 다음 → confirm (voice-phishing check) → 이체하기 → 6-digit PIN → `#done` |
| `lesson-a.json`, `lesson-b.json` | `lesson-a.html`, `lesson-b.html` | `galaxy-tab-s9` (800×1280, dpr 2, touch, portrait) | Lecture list → 3-2 → play the 6 s clip → 확인 퀴즈 → answer 2 questions (one right, one wrong) → 제출 → `#quiz-result` |
| `starlight-a.json`, `starlight-b.json` | `starlight-a.html`, `starlight-b.html` | `iphone-15` (393×852, dpr 3, touch, portrait) | Canvas tap-timing game: start, tap to the beat, hit the boost when the prompt appears, wait for the 15 s round to end → `#result` |
| `signup-a.json`, `signup-b.json` | `signup-a.html`, `signup-b.html` | `laptop-1440` (1440×900, dpr 2, mouse) | Email signup: submit once with a mistyped password confirmation, read the validation feedback, fix it, submit → `#done` |

## Running

Start a static server rooted at `benchmarks/`, then replace `{BASE}` with `http://127.0.0.1:<port>`:

```
python3 -m http.server <port> --bind 127.0.0.1 --directory benchmarks
```

Things a driver needs to know:

- **Hotspots.** The canvas game exposes `window.__ergoqa__.hotspots()`. It returns `[{id, name, box:{x,y,w,h} (CSS px, viewport), roles:["game_control"]}]` for the visible canvas controls, and `[]` once the result overlay is shown. The same static boxes are also listed in the scenario `hotspots`. Steps address them as `hotspot:<id>`.
- **Game text.** The HUD, the score and the timed prompt (`#prompt`) are DOM text on top of the canvas.
- **Timing windows.** `timing_windows` entries carry `kind` (`transient_text` or `qte`) and the displayed `text`. The lesson window also carries `texts`, because each question shows different text.
- **Typing.** `type` steps use the field `text`. The pages accept either fill or key-by-key typing. After a failed submit, the signup page clears the password-confirmation field, so appending works.
- **Step timing.** Wait steps are sized so that the task still completes on a slow driver. The game round ends by itself about 15 s after the first tap.
- **Roles.** Targets and roles are declared in each scenario (`targets`). The pages carry no `data-ergo-role` attributes.

## Key conventions

These are also written into `answer_key.json` → `conventions`.

- **`element_selector`** is an id selector, or an id prefix that covers a repeated group by substring containment. Examples: `#pk-` matches `#pk-1` … `#pk-back`. For canvas controls it is the bare hotspot id (e.g. `hs-boost`), which is contained in `hotspot:hs-boost`.
- **`profile_condition` keys** are dotted paths into ergo-profile.v1 `attributes`, for example `grip`, `age_band`, `vision.cvd`, `vision.presbyopia`, `motor.tremor` and `context.mobility`.
- **`profile_condition` values.** A scalar must equal the attribute. A list means any-of. `{}` means the issue applies to every profile.
- **`measured`** fields record geometry, colours and durations measured in Chromium (Playwright) with each device's settings. Physical mm assume these densities: S24 Ultra ≈505 ppi, iPhone 15 460 ppi, Tab S9 274 ppi.

## Provenance

- All eight scenarios were run end to end in Playwright Chromium with the device settings above, and each reached its `success.selector_visible`.
- Page geometry depends slightly on the fallback font. Korean text was measured with the container's system CJK font (WenQuanYi Zen Hei). Fixed-position controls and hotspots do not depend on the font.
