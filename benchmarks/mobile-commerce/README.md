# Benchmark suite: `mobile-commerce`

Blind validation fixtures for the ergonomic persona swarm QA tool (spec §12).
The suite was written without access to `ergoqa/`, `drivers/` or `scripts/`.
It contains Korean-language mobile-web flows. Each flow has a variant with
seeded human-factors problems and a clean control of the same flow. The only
list of the seeded problems and decoys is `answer_key.json`. Implementers of
the detector must not read it (or this suite) until scoring.

## Layout

```
benchmarks/mobile-commerce/
  site/                 static pages (no network, system fonts, inline CSS/JS)
    checkout.html       checkout-clean.html     쇼핑 장바구니 → 결제
    transfer.html       transfer-clean.html     송금/이체 (confirmation sheet + limit error)
    settings.html       settings-clean.html     설정 (notification toggles, logout/회원탈퇴)
    booking.html        booking-clean.html      미용실 예약 폼 (2 steps, validation, toast)
  scenarios/            ergo-scenario.v1, one per page
  answer_key.json       seeded defects, decoys, clean controls
```

| Flow | Scenario id (variant / clean) | Task goal (`task_goal_ko`) |
|---|---|---|
| Checkout | `SC-checkout-01` / `SC-checkout-01-clean` | 쿠폰 안내 배너를 닫고 토스페이로 결제 |
| Transfer | `SC-transfer-01` / `SC-transfer-01-clean` | 홍길동님에게 송금, 한도 초과 안내 후 50,000원으로 다시 송금 |
| Settings | `SC-settings-01` / `SC-settings-01-clean` | 혜택·이벤트(마케팅) 알림을 끄고 저장 |
| Booking | `SC-booking-01` / `SC-booking-01-clean` | 9월 30일(수) 15:30 1명 예약 (처음엔 휴대폰 번호 누락) |

A variant page and its clean page share the same element ids for the
elements the scenario touches and for the declared targets. Only placement,
size, colour, timing and feedback differ between them.

## Serving

Serve the `benchmarks/` directory (not the suite directory), because scenario
URLs are `{BASE}/mobile-commerce/site/<page>.html`:

```bash
cd benchmarks && python3 -m http.server 8765 --bind 127.0.0.1
# {BASE} = http://127.0.0.1:8765
```

The pages make no network requests beyond their own HTML. They use only
system fonts and no CDNs.

## Devices

The pages target portrait phones from 360 to 393 CSS px wide. Scenarios list
`galaxy-s24` (360x780 CSS px, dpr 3, touch). All eight scripted scenarios were
checked end to end with Playwright/Chromium on:

- Galaxy S24 (360x780, touch)
- iPhone 15 (393x852 and Playwright's 393x659 viewport, touch)
- a 1920x1080 mouse viewport, where the layout is a centred 480 px column and
  `tap` is replaced by `click`

Fixed bottom bars, sheets, toasts and overlays use `position: fixed`, so their
geometry does not depend on scroll position.

## Scenario conventions

- Roles are declared only in each scenario's `targets` (`primary`,
  `destructive`, `critical_message`, `error_message`, `status`, `timed`,
  `ad_like`). The pages carry no `data-ergo-role` attributes.
- `type` steps use `{"action":"type","target":"<selector>","text":"..."}`.
  They always follow a `tap` on the same field and only type into empty fields,
  so fill and keystroke typing give the same result.
- Grouped controls are addressed through a stable container id plus a data
  attribute, for example `#amount-chips [data-add="50000"]` and
  `#time-slots [data-time="15:30"]`.
- Explicit `snapshot` steps mark the moments of interest: the initial state,
  just after a tap whose feedback matters, and after an error or toast appears.
- `timing_windows` measure `visible_duration` of toasts (`#toast`, `#save-toast`).
- `success.selector_visible` names an element that appears only when the task
  is completed.

## Answer key notes

- Format follows spec §12. `element_selector` is always a single id. For a
  group-level issue it is the group container, and step targets inside that
  group start with the container id.
- `profile_condition` is a subset of the `ergo-profile.v1` `attributes`
  object. Nested objects match recursively; for example,
  `{"vision":{"cvd":"deutan"}}` or `{"context":{"mobility":"walking"}}`.
  `{}` means any profile. A condition names the profile where the problem is
  specific or worst. It does not claim that other profiles are unaffected.
- `severity_min` uses P1 (most severe) to P4. Keys are set conservatively at
  P2 or P3.
- Decoys look suspicious but are acceptable under the cited standard: a
  disabled control, an inline link, a small icon with enough spacing, colour
  that is also carried by text, latency shown with immediate feedback, a short
  redundant toast, and similar cases. They are present in both the variant and
  the clean page. A finding on a decoy or on a clean control is a
  false-positive candidate and needs manual adjudication, because a detector
  may find a real problem that was not seeded.
- The answer key uses Galaxy S24 physical scale (~0.183 mm per CSS px,
  ~66x143 mm screen) to convert measured geometry to millimetres.
