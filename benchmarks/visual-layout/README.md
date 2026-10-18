# Benchmark suite: `visual-layout`

Blind validation fixtures for rendered visual-layout defects (spec §12). The
suite was written without access to the QA tool, `ergoqa/`, `drivers/` or any
detector code. It contains four Korean-language products. Each product has a page
with seeded defects and a clean control that shows the same content with the
same element ids. Every seeded defect is visible in a screenshot at the listed
device size; the only interaction is scrolling. The only list of the seeded
defects and decoys is `answer_key.json`. Implementers of the detector must not
read it (or this suite) until scoring.

The defects are of the kinds often found in hastily built or generated web UIs:

| # | Family | Category | Defects |
|---|---|---|---|
| 1 | Text cut by its own fixed-size box (fixed width, overflow hidden) | layout | D-01, D-17, D-25 |
| 2 | Text cut by a clipping ancestor narrower than the text | layout | D-10, D-18, D-24 |
| 3 | Content past the right edge of the phone screen, sideways scrolling disabled | layout | D-02, D-08, D-27 |
| 4 | Text permanently under a fixed bar (first content at scroll 0, last row at the end) | layout | D-03, D-15, D-16, D-23 |
| 5 | Overlap in normal layout (positioned badge, negative margin) | layout | D-04, D-09, D-19 |
| 6 | Wrapped heading lines overlapping (line-height 0.7-0.72) | layout | D-05, D-11, D-20 |
| 7 | Near-miss alignment (3-5 px off a shared left edge) | layout | D-12, D-21, D-28 |
| 8 | One odd gap in a repeated list | layout | D-06, D-14, D-22 |
| 9 | Text the user must read set below 11 px on a phone | perception | D-07, D-13, D-26 |

## Layout

```
benchmarks/visual-layout/
  site/                      static pages (inline CSS, system fonts, no scripts, no network)
    menu-options.html        menu-options-clean.html       메뉴 옵션 시트 (phone)
    case-study.html          case-study-clean.html         고객 사례 아티클 (phone)
    team-dashboard.html      team-dashboard-clean.html     팀 성과 대시보드 (laptop)
    checkout-summary.html    checkout-summary-clean.html   주문서와 결제 (phone)
  scenarios/                 ergo-scenario.v1, one per page (scroll and snapshot only)
  answer_key.json            28 seeded defects, 11 decoys, 4 clean controls
```

| Product | Scenario id (variant / clean) | Devices | Defects | Decoys |
|---|---|---|---|---|
| Menu option sheet: sticky header, size options, sauce chips, carousel, toppings, fixed cart bar | `SC-menu-options-01` / `SC-menu-options-01-clean` | galaxy-s24, iphone-15 | D-01..D-07 | N-01..N-03 |
| Case-study article: long headings, summary, stats, numbered steps, lessons, more cases, fixed CTA | `SC-case-study-01` / `SC-case-study-01-clean` | galaxy-s24, iphone-15 | D-08..D-15 | N-04, N-05 |
| Team dashboard: fixed top bar, tabs, KPI cards, campaign table, activity feed, side panels | `SC-team-dashboard-01` / `SC-team-dashboard-01-clean` | laptop-1440 | D-16..D-22 | N-06..N-08 |
| Checkout summary: fixed header, address, items, coupons, installment table, totals, fixed pay bar | `SC-checkout-summary-01` / `SC-checkout-summary-01-clean` | galaxy-s24, iphone-15 | D-23..D-28 | N-09..N-11 |

All companies, people, addresses and products are fictional.

## Serving

Serve the `benchmarks/` directory (not the suite directory), because scenario
URLs are `{BASE}/visual-layout/site/<page>.html`:

```bash
cd benchmarks && python3 -m http.server 8765 --bind 127.0.0.1
# {BASE} = http://127.0.0.1:8765
```

## Devices

- `galaxy-s24`: 360x780 CSS px, dpr 3, touch (phone scenarios)
- `iphone-15`: 393x852 CSS px, dpr 3, touch (phone scenarios)
- `laptop-1440`: 1440x900 CSS px (dashboard)

Every seeded defect was confirmed on each device listed in its scenario. The
phone pages were also checked at Playwright's 393x659 iPhone 15 viewport, where
all defects are present too. At that height the 600 px scroll steps are taller
than the strip between the fixed or sticky bars (for example 659 - 52 - 77 =
530 px on the menu page), so a few rows fall under a bar in every snapshot, on
clean pages as well. At the listed 780 and 852 px heights there is no such gap.

Horizontal overflow on the phone pages is clipped by the page wrapper
(`main` or `.app` with `overflow-x: hidden`), in addition to
`body { overflow-x: hidden }`. With body-level clipping alone, mobile Chromium
widened the layout viewport to the overflowing content (innerWidth 456 px) and
pushed the fixed cart bar below the screen, which would have added unseeded
defects.

## Scenario conventions

- Steps are `snapshot`, then `scroll` 600 / `wait` 250 / `snapshot` repeated
  until the end of the page plus one extra scroll: 4 scrolls on the phone pages
  (enough for 393x659) and 2 on the dashboard. The variant and clean scenario of
  a product use the same steps.
- `targets.primary` names the main action (`#btn-add-cart`, `#btn-consult`,
  `#btn-export`, `#btn-pay`); all other target lists are empty. Fixed bars are
  not declared in any target field. `success.selector_visible` is the primary
  action.

## Answer key notes

- Format follows spec §12 with the v2 fields `taxonomy_ref` and
  `detectable_by`. `profile_condition` is `{}` (any profile). There are no
  product briefs; this is a v1-style suite.
- `element_selector` is always a single id. When a defect involves two
  elements (a clipping card and its text, a badge and the label under it, a
  callout and the paragraph it covers, a stat row and its off-screen cell), the
  key names the containing element and the involved descendants carry ids that
  start with the key id (`#addr-box` and `#addr-box-line`,
  `#opt-size-large` and `#opt-size-large-ribbon`), so a finding on either
  element matches by containment. For family 8 the key is the list container.
  No key or decoy is nested inside another, and no other id contains a key id.
- Geometry in the descriptions is galaxy-s24 CSS px in document coordinates
  (laptop-1440 for the dashboard); iphone-15 values are added where they differ.
  The smallest clipped overflow is 16.8 px (D-25) and the smallest line overlap
  is 9.6 px (D-20), so the defects survive small font-metric differences.
  Measured on macOS system fonts (SF and Apple SD Gothic Neo).
- `severity_min` is P2 where text or a number is hidden, cut or overlapped,
  and P3 for alignment, spacing and small text. `detectable_by` is
  `measurement` for all 28 defects.
- Decoys look like defects but are acceptable: a sticky header with a correct
  offset, a scrollable carousel cut at the edge, screen-reader-only text, an
  overlapping decorative avatar stack, an intentionally indented sub-list, a
  table ellipsis whose full text is on the same screen, a single-line numeral
  with line-height 0.9, an unread dot over an icon, a pay-bar ellipsis, a
  grouped coupon list, and a 10 px legal footer. They are identical in the
  variant and the clean page. A finding on a decoy or on a clean control is a
  false-positive candidate that needs manual adjudication.
- The clean pages show no clipped, covered, off-screen or overlapping text and
  no other text below 11 px. Contrast is at least 4.5:1 and targets at least
  24 px; apart from the decoys, the only measured difference is a 1.4 px offset
  from the narrower digit "1" centred in the first case-study step circle.

## Authoring note

Written blind to the QA tool on 2026-10-18 by claude-opus-5-5 (a Claude Agent
SDK leaf worker), reading only the task brief, the spec excerpt and the example
suite. The geometry was checked by rendering every page in Playwright Chromium
(headless shell, `--single-process`) with mobile emulation at 360x780, 393x852
and 393x659 and at 1440x900 for the dashboard. The check measured per-character
boxes against clipping ancestors and the viewport, hit-tested every character
every 40 px of scroll to find text that is never visible, and compared line pitch
with glyph height, list gaps, left edges, font sizes, contrast and target sizes.
Screenshots of each scenario snapshot were reviewed by eye. Every number in
`answer_key.json` comes from these measurements; none was computed from the CSS
alone.
