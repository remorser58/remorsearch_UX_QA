# UX design discipline as screen-level QA checks

Brief for the persona-swarm QA ("look at the screen and operate it"). Scope: the canon a UX/interaction-design major learns, rewritten as checks an LLM persona agent can run against a live screenshot and action trace, plus the Korean regulatory and convention layer.

- Prepared: 2026-09-28.
- Audience: engineers building `ergoqa`/`uxloop` checks, and the prompt authors for persona agents.
- Severity vocabulary: the repo's own P0–P3 (`skills/persona-driven-ux-qa/references/evidence-and-severity.md`).

## Retrieval note and evidence tags

Most web hosts were blocked by the egress proxy: nngroup.com, baymard.com, w3.org, iso.org mirrors, arxiv.org, deceptive.design, ftc.go.kr, korea.kr and law.go.kr all failed. The web-search budget also ran out mid-session. Primary text was therefore read from sources that were reachable:

- Korean statutes, as current consolidated text: `legalize-kr/legalize-kr` on GitHub, a git mirror of law.go.kr.
- KWCAG 2.2: an HTML copy of KS X OT0003:2022, read from the a11ykr/kwcag22 HTML edition.
- WCAG 2.2 success-criterion text: `w3c/wcag` on GitHub.
- Apple HIG: developer.apple.com JSON.
- GOV.UK Design System guidance: `alphagov/govuk-design-system` on GitHub.
- The Mathur et al. 2019 released dataset: `aruneshmathur/dark-patterns` on GitHub.
- The KRDS component kit: `KRDS-uiux/krds-uiux` on GitHub.

Every claim carries a tag:

| Tag | Meaning |
|---|---|
| **[P]** | Primary text read at the time of writing. |
| **[S]** | Search-engine snippet. The page was not opened. Snippets from secondary sites are marked **[S2]**. |
| **[B]** | Background disciplinary knowledge, not re-verified at the time of writing. No numbers are given under [B]. |
| **[D]** | Derived by me from [P]/[S] material. |
| **UNCONFIRMED** | A number or fact I could not confirm. Do not hard-code it as a gate. |

---

## 1. Summary

1. **Use one crosswalked check catalogue, not six heuristic lists.** Nielsen's 10 heuristics, Norman's principles, Shneiderman's 8 golden rules, ISO 9241-110:2020 (7 interaction principles) and ISO 9241-112 (6 presentation principles) overlap heavily. Section 3 merges them into 24 check units (`UXD-01`…`UXD-24`). Each unit keeps its source tags, so a finding can cite, for example, "N1 / Norman-feedback / S3 / ISO110-self-descriptiveness".
2. **Every check splits into a deterministic part and a judgment part.** Deterministic parts are computed from DOM, accessibility tree, geometry, timing or cross-screen diffs. Judgment parts are for the vision-LLM persona: is the label meaningful, does the icon read as tappable, is the tone blaming. Deterministic results are `observed`. LLM judgments are `inferred` and need a screenshot crop plus a rationale.
3. **Timing checks are the cheapest high-value automation.** The response-time limits of 0.1 s, 1 s and 10 s (Nielsen 1993, after Miller 1968) [S] give thresholds for feedback latency, busy indicators and progress/cancel requirements. Blank-screen detection and duplicate-submit detection follow from them.
4. **Form and checkout checks have public quantitative anchors (Baymard)** [S/S2]. All are secondary-snippet level; re-verify before using them as gates.
   - Documented average cart abandonment: 70.19% across 49 studies.
   - Leading fixable abandonment reason: extra costs, 39% (2024 US survey, n = 4,329).
   - Average checkout: 11.3 form fields (2024) vs. about 8 needed.
   - Checkout-design conversion upside: up to 35.26%.
5. **Dark patterns now have hard legal edges in Korea.** The 2024 amendment of 전자상거래법 took effect 2025-02-14 [P].
   - Art. 21-2 prohibits five interface behaviours: 순차공개 가격책정, 특정옵션 사전선택, 잘못된 계층구조, 취소·탈퇴 방해, 반복간섭.
   - Art. 13(6) adds the 숨은 갱신 duty: consent within the 30 days before a subscription price increase or free-to-paid conversion.
   - 반복간섭 has a 7-day safe harbour [P].
   - Since 2026-07-21 the fine ceiling for Art. 21-2 violations is ₩10,000,000 [P]. Secondary sources say it was ₩5,000,000 before [S2].
   - Many of these checks are measurable: pre-checked boxes, prominence ratios between choices, step counts for sign-up vs. cancel, price on the first screen vs. the final total, and re-prompt intervals.
6. **Academic taxonomies are broader than the law.** They cover Brignull/deceptive.design, Mathur et al. 2019 (15 types in 7 categories, 1,818 instances), Gray et al. 2018 (5 strategies), EU DSA Art. 25, and the Korean FTC 2023 guideline (4 categories, 19 types). A screen can be a dark pattern (P1/P2 trust finding) without being illegal. Report the legal hook separately from severity.
7. **Korean-specific flows are major sources of P0/P1.** These include 본인확인 (identity verification, often popup or app-switch), 간편결제 hand-offs, and 약관/개인정보 동의 screens. Several rules are statutory and screen-checkable:
   - PIPA Art. 22: separate consents; no refusal of service for declining optional items.
   - PIPA Art. 24-2(3): sign-up must be possible without a 주민등록번호.
   - 정보통신망법 Art. 22-2: app permission notices split into necessary and optional.
   - 정보통신망법 Art. 50: explicit ad consent, a separate night-time (21:00–08:00) consent, and reconfirmation every 2 years.
   - 게임산업법 Art. 33(2): 확률형 아이템 probability disclosure.
8. **KWCAG 2.2 (KS X OT0003:2022) is not WCAG 2.2** [P].
   - Structure: 4 principles, 14 guidelines, 33 items. It was built on WCAG 2.1 and centred on level A, but adds:
     - 4.5:1 contrast;
     - three WCAG 2.2-like items: consistent help, accessible authentication, redundant entry;
     - Korea-only items: 5.4.4 content separation, and 6.1.3 control size (≥ 6.0 mm diagonal, "desirable").
   - It keeps markup-parsing validity (8.1.1), which WCAG 2.2 made obsolete.
   - Mobile apps are covered by statute: 장애인차별금지법 Art. 21(2) and Enforcement Decree Art. 14(4)–(6) [P], plus 디지털포용법 (in force 2026-01-22) [P]. The technical baseline is KS X 3253 (Mobile App Accessibility Guideline 2.0) [S via sibling brief].
9. **Persona agents can be manipulated by the patterns they are meant to detect.** Research on computer-use agents shows susceptibility to dark patterns (SusBench, DECEPTICON; titles only [S]). Dark-pattern detection must therefore rest on deterministic probes plus a separate "auditor" pass, not on whether a persona "fell for it".
10. **Some things stay human or LLM judgments:** conceptual-model fit, tone, cultural appropriateness, "현저한 차이" (legally significant prominence), whether urgency or scarcity claims are true, and whether game difficulty is intended. Record these as `inferred` with confidence, never as `observed`.

---

## 2. Foundations to cite in findings

### 2.1 Definitions and standards

| Framework | Content | Tag |
|---|---|---|
| **ISO 9241-11:2018 usability** | "extent to which a system, product or service can be used by specified users to achieve specified goals with effectiveness, efficiency and satisfaction in a specified context of use." The standard also relates usability to accessibility, UX and avoidance of harm. | [S] |
| **ISO 9241-210:2019 HCD principles** | (a) design based on explicit understanding of users, tasks and environments; (b) users involved throughout design and development; (c) design driven and refined by user-centred evaluation; (d) iterative process; (e) design addresses the whole user experience; (f) multidisciplinary skills and perspectives. These are process principles. QA uses them only to justify evidence practice (context-of-use recording, iteration), not as screen checks. | [S] for (a)–(d) and the gist of (e)–(f); exact wording of (e)–(f) [B] |
| **ISO 9241-110:2020 interaction principles (7)** | 1. Suitability for the user's tasks. 2. Self-descriptiveness. 3. Conformity with user expectations. 4. Learnability. 5. Controllability. 6. Use error robustness. 7. User engagement (new in 2020). | [S] |
| ISO 9241-110 mapping from the 2006 "dialogue principles" | Error tolerance → use error robustness; suitability for learning → learnability; suitability for individualization was dropped as a separate principle. | [B] |
| **ISO 9241-112:2017 presentation principles (6)** | Detectability, freedom from distraction, discriminability, unambiguous interpretability, conciseness, consistency (internal/external). An ISO 9241-112:2025 edition exists; its principle list was not verified. The 1998 predecessor ISO 9241-12 used clarity, discriminability, conciseness, consistency, detectability, legibility, comprehensibility. | [S] |

### 2.2 Heuristic and principle sets

| Framework | Content | Tag |
|---|---|---|
| **Nielsen's 10 heuristics** | N1 visibility of system status; N2 match between system and real world; N3 user control and freedom; N4 consistency and standards; N5 error prevention; N6 recognition rather than recall; N7 flexibility and efficiency of use; N8 aesthetic and minimalist design; N9 help users recognize, diagnose and recover from errors; N10 help and documentation. | N1–N3 wording [S]; list [B]; source page nngroup.com/articles/ten-usability-heuristics (blocked) |
| **Nielsen severity scale** | 0 not a problem; 1 cosmetic; 2 minor; 3 major; 4 usability catastrophe. Components: frequency, impact, persistence (plus market impact). A single evaluator's ratings are unreliable; average several evaluators. | [S] (NN/g page title plus a secondary summary) |
| **Norman (DOET, revised ed.)** | Discoverability; affordances; signifiers; constraints (incl. forcing functions); mappings; feedback; conceptual model. Seven stages of action: goal, plan, specify, perform (gulf of execution), perceive, interpret, compare (gulf of evaluation). | [S] |
| **Shneiderman's 8 golden rules** (DTUI 6th ed., 2016, §3.3.4) | S1 strive for consistency; S2 seek universal usability; S3 offer informative feedback; S4 design dialogs to yield closure; S5 prevent errors; S6 permit easy reversal of actions; S7 keep users in control; S8 reduce short-term memory load. Earlier editions had "enable frequent users to use shortcuts" where S2 now stands. | List [S]; the replacement [B] |
| **Information foraging** (Pirolli & Card 1999, *Psychological Review*) | Users follow **information scent**: proximal cues (link text, labels, snippets) predict the value of distal content. Users stay in a "patch" or leave it by a cost–benefit logic. | [S] |
| **Response-time limits** (Nielsen 1993 after Miller 1968) | 0.1 s feels instantaneous; 1.0 s keeps the flow of thought; 10 s is the limit for keeping attention on the dialogue. | [S] |

### 2.3 Mapping to the repo's severity scale

Nielsen's scale and P0–P3 are not the same axis. Nielsen rates usability harm. The repo's scale adds safety, privacy and misleading high-stakes actions. Use this mapping:

- Nielsen 4 ⇒ P0 if the critical task is blocked, or if money, privacy or legal consequences are misled. Otherwise P1.
- Nielsen 3 ⇒ P1.
- Nielsen 2 ⇒ P2.
- Nielsen 1 ⇒ P3.
- Always raise one level when:
  - the issue sits on the critical path of a high-stakes flow (payment, consent, identity, cancellation, deletion); or
  - it violates a statutory rule (Section 4). The legal hook goes in a separate `legal_refs` field.
- **Persistence** (repeat exposure) should raise severity. A small cost on a screen seen many times per session is not "minor" [S2].

---

## 3. Check catalogue (`UXD-xx`)

### How to read a check

Each unit has:

- **Statement:** the principle.
- **Sources:** framework IDs and tags.
- **Screen check:** what the persona agent does or inspects.
- **Evidence:** what must be recorded. The minimum is `screen_id`, `step_index`, `element` (selector/role/name + bbox in CSS px + screenshot crop), `action` and `timestamp`, `expected` vs. `observed`, and `epistemic_status`.
- **Deterministic:** what can be computed without an LLM.
- **Severity:** P0–P3 rules.
- **Surfaces:** notes for web, app, game or TV where they differ.

**Standing rule for persona agents.** Before every action, the agent writes an **expectation**: what it thinks will happen and where it will land. After the action it records the outcome. The expectation–outcome gap is the operational measure of both of Norman's gulfs:

- Gulf of execution: "I couldn't find how to do X."
- Gulf of evaluation: "I did something but can't tell what happened."

This logging is cheap, universal and auditable [D].

---

### UXD-01 Feedback and visibility of system status

- **Statement.** Every user action gets perceptible feedback within a reasonable time. Current state (selected, loading, saved, offline, logged in, cart count) stays visible.
- **Sources.** N1; Norman *feedback*; S3; ISO 9241-110 self-descriptiveness; ISO 9241-112 detectability; response-time limits [S].
  - Apple HIG Feedback [P]: match the delivery to significance; show status near the items it describes; "Show people when a command can't be carried out and help them understand why."
  - WCAG 4.1.3 Status Messages (AA) [P]: status messages must be programmatically exposed without taking focus.
- **Screen check.** After each tap, click or key, the persona asks: did anything change? Did the thing I touched change state? Can I tell whether it worked? For toggles, filters and add-to-cart, look for a state change on the control and a global indicator (badge, toast).
- **Evidence.**
  - Action timestamp.
  - Screenshots at +100 ms, +1 s and +3 s, plus one when the page settles.
  - Crop of the target and of any toast or badge.
  - The DOM or accessibility-tree status node, if any.
- **Deterministic.**
  - `t_first_feedback`: time from input event to the first pixel change inside or near the target bbox (screenshot diff above a noise threshold), or a DOM mutation on the target or an `aria-live` region.
  - Thresholds [S]:
    - > 0.1 s with no visual response on the pressed control ⇒ note.
    - > 1 s with no busy indicator ⇒ violation.
    - > 10 s with no progress indication or cancel ⇒ violation.
  - Status messages: the element has `role=status|alert|log|progressbar` or `aria-live` (WCAG 4.1.3) [P].
  - Duplicate-submission probe: a second click within 1 s on a submit or pay button. Check whether it is disabled or deduplicated (network log shows one request) [D].
- **Severity.**
  - P0: no feedback on payment or submit, and a repeat action creates a duplicate order or charge (observed in the network log or order list).
  - P1: action silently fails; the user cannot tell whether a save, send or cancel took effect.
  - P2: feedback later than 1 s with no busy indicator on a frequent action.
  - P3: feedback present but only off-target, such as a distant toast.
- **Surfaces.**
  - Games: input-to-response latency on player controls is a core quality attribute. Use the 0.1 s limit as the ceiling for "direct manipulation" feel [S]. Game-specific frame-latency norms were not researched here.
  - TV: focus state is the status. Always record which element has focus.

### UXD-02 Loading, waiting and progress states

- **Statement.** Waiting is visible, estimated when possible, cancellable when long, and never a blank screen.
- **Sources.** N1; Apple HIG Loading [P]: "Show something as soon as possible… consider showing placeholder text, graphics, or animations"; use determinate indicators when duration is known and indeterminate when it isn't; for long loads, give people something to do. Response-time limits [S].
- **Screen check.** On navigation or data fetch, capture the frames. Is there a skeleton or spinner? Does the layout jump when content arrives? Is there a percentage or time estimate for long operations? Is there a cancel?
- **Evidence.** Frame sequence with timestamps; the time the first contentful frame appears; the type of indicator; any layout shift.
- **Deterministic.**
  - Blank-frame detection: more than about 95% of viewport pixels uniform, or no text nodes in the viewport, at t ≥ 1 s. (The 95% is my heuristic threshold [D]. Calibrate it.)
  - Indicator presence: `aria-busy=true`, `role=progressbar` or a known skeleton or spinner class.
  - Determinate indicator: `aria-valuenow` present.
  - Layout-shift sum from the browser's LayoutShift API [B].
  - Operations over 10 s without determinate progress or cancel ⇒ flag [S].
- **Severity.**
  - P1: blank screen longer than 10 s, or an indefinite spinner with no error or timeout path (user stuck).
  - P2: blank screen of 1–10 s; content jump that causes a mis-tap (observed).
  - P3: indeterminate indicator where progress is knowable.
- **Surfaces.** Games: Apple HIG endorses custom loading views with tips [P]. Watch for loading screens that hide the chance to cancel matchmaking.

### UXD-03 Match with the real world: language, conventions, order

- **Statement.** Use the user's words, units, formats and sequencing. Don't use internal jargon or system codes.
- **Sources.** N2; Norman *conceptual model*; ISO 9241-110 conformity with user expectations; ISO 9241-112 unambiguous interpretability [S].
  - Apple HIG Writing [P]: "Choose simple, plain language… avoiding jargon"; "Avoid using we"; describe gestures correctly (not "click" on touch).
  - KWCAG 7.1.1 default language [P].
- **Screen check.** The persona reads each screen as its own profile (age, domain literacy, region) and lists every term it would not understand or would misread. It checks formats: dates (YYYY.MM.DD is common in Korea [B]), ₩/원 amounts with thousands separators, phone numbers `010-XXXX-XXXX` [B], and 도로명 vs. 지번 addresses [B].
- **Evidence.** Quoted string, its location, and the persona's paraphrase of what it thinks the string means (expected meaning vs. actual function).
- **Deterministic.**
  - Error codes or English system strings visible in Korean UI: regex for `Error \d+`, `null`, `undefined`, `NaN`, `[object Object]`, stack traces.
  - Mixed honorific registers across one flow (합니다 vs. 해요 endings): regex on sentence endings [D]. Mixed registers are a consistency smell, not always a defect.
  - `<html lang>` present and correct (KWCAG 7.1.1) [P].
- **Severity.**
  - P0: terms in legal, financial or medical actions whose misreading changes the commitment (e.g., "해지" vs. "일시정지" ambiguity on a subscription screen).
  - P1: raw error codes or system strings on a critical path.
  - P2: jargon that forces a lookup.
  - P3: register or format inconsistency.

### UXD-04 Affordances and signifiers (clickability and discoverability)

- **Statement.** Interactive things look interactive, non-interactive things don't, and hidden gestures have signifiers.
- **Sources.** Norman *affordances*, *signifiers*, *discoverability* [S]; N4, N6; ISO 9241-112 discriminability [S]; KWCAG 6.1.3 control size (≥ 6.0 mm diagonal, desirable) [P]; WCAG 2.5.8 Target Size (Minimum), ≥ 24×24 CSS px with spacing exception [P]. Target-size maths is in the sibling brief `motor-pointing.md`.
- **Screen check.**
  - The persona lists, from the screenshot alone, what it believes is tappable. It then probes: taps each candidate it would plausibly try, plus one false-affordance candidate per screen.
  - It records "looked tappable, wasn't" (false affordance) and "didn't look tappable, was the only way" (hidden affordance).
- **Evidence.** Candidate list with bboxes; probe results; for hidden gestures (swipe or long-press only), the missing signifier.
- **Deterministic.**
  - Interactive set = elements with native interactive roles, `onclick` or pointer listeners (via CDP `DOMDebugger.getEventListeners`), or `cursor:pointer`.
  - Compare with the LLM's "looks tappable" set: false positives are false affordances; false negatives are hidden affordances.
  - Link-in-text distinguishability: underline or ≥ 3:1 contrast against surrounding text [B, WCAG technique G183].
  - Target sizes per WCAG 2.5.8 and KWCAG 6.1.3.
- **Severity.**
  - P1: the only path to a critical task is a hidden gesture or unsignified element (discovered by fewer than half of the swarm's profiles; report as coverage, not prevalence).
  - P2: false affordance that costs a tap and a back navigation.
  - P3: weak signifier on a secondary action.
- **Surfaces.** Games: diegetic UI may deliberately hide affordances, so judge against the game's teaching (UXD-20). TV: every focusable item needs a visible focus state (KWCAG 6.1.2) [P].

### UXD-05 Mapping (control ↔ effect correspondence)

- **Statement.** The layout and direction of controls correspond to their effects: +/−, sliders, steppers, left/right, map pan, game directional input.
- **Sources.** Norman *mapping* [S]; ISO 9241-110 conformity with user expectations [S].
- **Screen check.** Operate each paired control once. Record whether the direction, target and magnitude of the effect matched the expectation.
- **Evidence.** Control bbox, the affected-region bbox, and before/after values.
- **Deterministic.**
  - Distance between a control and the region it changes (bbox centroid distance). Flag when the changed region is outside the viewport or more than half a viewport away [D, heuristic].
  - Direction consistency: increment control raises the value; swipe-left advances in carousels whose indicator moves left→right [D].
- **Severity.** P1 if the mapping inverts a high-stakes value (quantity, amount, date range); P2 if it causes repeated correction; P3 otherwise.

### UXD-06 Error prevention and constraints

- **Statement.** Prevent slips and mistakes: constrain inputs, use good defaults, confirm destructive or irreversible actions, and let people review high-stakes submissions.
- **Sources.** N5; S5; Norman *constraints / forcing functions* [S]; ISO 9241-110 use error robustness [S].
  - WCAG 3.3.4 Error Prevention (Legal, Financial, Data) (AA) [P]: submissions that cause legal commitments, financial transactions or data changes must be reversible, checked, or confirmed.
  - Apple HIG Alerts [P]: warn for uncommon, irreversible destructive actions; don't alert for common undoable ones; always include "Cancel" with destructive actions.
- **Screen check.**
  - Try likely slips: invalid date, past date for a future booking, letters in a numeric field, double-tap on pay, back during payment, delete without confirm.
  - Check that a final review screen exists before payment or contract.
- **Evidence.** The attempted invalid input, the system response, and whether the irreversible action executed.
- **Deterministic.**
  - Input `type`/`inputmode`/`pattern`/`min`/`max` presence on typed fields.
  - Date pickers disable impossible dates (check `disabled` on past cells).
  - Irreversible-action inventory: buttons whose label matches the delete/withdraw/pay/cancel lexicon: 삭제, 탈퇴, 결제, 해지, 송금, 구매 확정 [D]. Verify a confirm or undo step via action trace.
  - WCAG 3.3.4: a review or confirm step exists before a financial submission [P].
- **Severity.**
  - P0: an irreversible financial, legal or data-deleting action executes with no review, confirmation or undo.
  - P1: a common slip leads to lost work.
  - P2: a missing constraint lets invalid data through to a later error.
  - P3: over-confirmation of trivial undoable actions (friction; Apple guidance) [P].

### UXD-07 User control and freedom: undo, cancel, back, exit

- **Statement.** Users can back out, cancel, undo and exit without penalty. Browser or system back works and preserves state.
- **Sources.** N3; S6; S7; ISO 9241-110 controllability [S].
  - GOV.UK question pages [P]: always include a Back link; "do not break the browser back button… take users to the previous page they were on, in the state they last saw it"; after one-time actions (payment), back should show a sensible message rather than repeat the action.
  - KWCAG 7.2.1: no unintended new windows or context change on focus or input [P].
- **Screen check.** At every step of the scenario, press system back (Android back gesture, iOS edge swipe, browser back, Esc for modals, B button in games). Record where you land and whether entered data survived. Try closing every modal via X, backdrop and Esc.
- **Evidence.** State before and after back (URL/route, form values); modal dismiss methods tried and results.
- **Deterministic.**
  - Form-value persistence after back and forward (compare field values).
  - Modal has a focusable close control with an accessible name.
  - Esc closes it (keyboard) [D].
  - A route change occurs on back, not an app exit, when history exists.
  - `target=_blank` or `window.open` without warning (KWCAG 7.2.1) [P].
- **Severity.**
  - P0: back or cancel during payment or identity verification leaves an ambiguous charge or verification state (unknown whether paid or verified).
  - P1: back exits the app or loses the multi-field form; a modal can't be closed (trap).
  - P2: back skips to an unexpected step.
  - P3: missing in-page back link where system back works.

### UXD-08 Consistency and standards

- **Statement.** The same function has the same name, look and place. Platform conventions are followed.
- **Sources.** N4; S1; ISO 9241-110 conformity with user expectations; ISO 9241-112 consistency [S]; WCAG 3.2.3 Consistent Navigation (AA) and 3.2.4 Consistent Identification (AA) [P]; KWCAG 7.2.2 (help in the same relative order) [P]; Apple HIG Writing: "Build language patterns… use consistent language throughout processes" [P].
- **Screen check.** Across screens in the run, the persona notes when the same action is labelled differently, or looks or behaves differently (e.g., "다음" / "계속" / "확인" for the same step-advance action; primary buttons in different colours).
- **Evidence.** Pairs of (screen, element, label, style tokens) that should match.
- **Deterministic.**
  - Cluster elements by destination (href/route) or by handler, and diff their accessible names. Different names for the same destination ⇒ inconsistency (WCAG 3.2.4) [P+D].
  - Nav order: compare the ordered list of nav items across pages (WCAG 3.2.3) [P].
  - Style drift: cluster buttons by role (primary/secondary) using computed background, colour, radius and height. Within-role variance above a threshold ⇒ flag [D].
  - Help-mechanism position order across pages (KWCAG 7.2.2) [P].
- **Severity.** P1 if the inconsistency flips meaning (the same colour or position means "confirm" on one screen and "delete" on another); P2 for label or position drift on the critical path; P3 for cosmetic drift.

### UXD-09 Recognition rather than recall (memory load)

- **Statement.** Keep needed information visible or retrievable. Don't make users remember things across screens or re-enter data.
- **Sources.** N6; S8 [S]; WCAG 3.3.7 Redundant Entry (A) [P]; KWCAG 7.3.4 반복 입력 정보 [P] (e.g., copy the orderer's address to the recipient's); WCAG 1.3.5 Identify Input Purpose (AA, `autocomplete` tokens) [B]; GOV.UK: "only ask for a piece of information once within a single journey" [P]; Apple HIG Entering Data: "Get information from the system whenever possible" [P].
- **Screen check.** Look for moments where the persona must remember a code, a price, an option chosen earlier, or instructions shown on a previous screen. Look for repeated entry of the same data.
- **Evidence.** The datum, where it was first shown or entered, and where it is needed again.
- **Deterministic.**
  - Redundant-entry detector: within a flow, find fields with the same `autocomplete` token or the same normalized label (이름, 휴대폰, 주소) on later steps that are not prefilled and offer no "same as above" option [D].
  - `autocomplete` coverage on personal-data inputs [B].
  - Instructions only visible on a prior screen (text diff), e.g., a verification code shown then hidden [D].
- **Severity.** P1 if recall failure blocks completion (e.g., a code needed after the screen that showed it); P2 for redundant entry of multi-field data; P3 for minor.

### UXD-10 Flexibility and efficiency; universal usability

- **Statement.** Accelerators for experienced users (shortcuts, saved info, 간편결제, recent items), without penalizing novices. Diverse users (age, disability, device, network) are served.
- **Sources.** N7; S2 [S]; ISO 9241-110 suitability for the user's tasks [S]; KWCAG 6.1.1 keyboard, 6.1.4 character-key shortcuts [P]; KWCAG 7.3.3 / WCAG 3.3.8 accessible authentication [P].
- **Screen check.** Measure the path length for the main task. Check that a returning user's saved info is offered, and that at least one non-memory login or verification method exists.
- **Evidence.** Step, tap and keystroke counts per scenario; list of accelerators available.
- **Deterministic.**
  - Counts from the action trace: taps, keystrokes, screens, scroll distance [D].
  - Keyboard-only completion (web): tab through and complete the task. Report the first unreachable control (KWCAG 6.1.1) [P].
  - Single-character shortcuts must be disableable, remappable or focus-scoped (KWCAG 6.1.4) [P].
- **Severity.** P1 if the task is impossible with keyboard or assistive tech, or authentication relies only on a cognitive test (KWCAG 7.3.3) [P]; P2 for an unusually long path relative to a comparable baseline; P3 for a missing accelerator.

### UXD-11 Visual hierarchy, minimalism, detectability, freedom from distraction

- **Statement.** The primary task and its CTA are the most salient things on the screen. Irrelevant content doesn't compete. Adjacent content is distinguishable.
- **Sources.** N8 [B]; ISO 9241-112 detectability, discriminability, conciseness, freedom from distraction [S]; KWCAG 5.4.4 content separation (borders, dividers, spacing) [P]; KWCAG 5.4.1 no colour-only meaning and 5.4.3 contrast ≥ 4.5:1 (3:1 for ≥ 18 pt or ≥ 14 pt bold) [P]; WCAG 1.4.1 [P].
- **Screen check.** From the screenshot, the persona states in one line what the screen is for and what the next action is, within the first glance and before scrolling. It lists competing elements (banners, promos, popups) between it and the task.
- **Evidence.** Persona's stated purpose and next action vs. the scenario's intended ones; the salient elements the persona named first.
- **Deterministic.**
  - Primary CTA above the fold at the device viewport (bbox y < viewport height).
  - Prominence metrics: area, contrast against the background, and font weight of the primary CTA vs. every other button [D].
  - Count of animated or auto-rotating regions. Each needs pause controls (KWCAG 6.2.2) [P].
  - Colour-only states: error or selection indicated only by hue change (compare greyscale screenshots) [D].
  - Text contrast via the WCAG formula.
- **Severity.** P1 if the persona cannot identify the next step on a critical screen (gulf of execution), or a colour-only critical state fails; P2 for competing promos that delay the task; P3 for clutter.

### UXD-12 Error messages and recovery

- **Statement.** Errors are visible, near the problem, in plain language, and say what happened and how to fix it. User input is preserved. The message doesn't blame.
- **Sources.** N9.
  - NN/g error-message guidelines [S]: visibility (close to the source; noticeable, redundant, accessible indicators; not premature), communication (human-readable, concise, precise, constructive, no blame), efficiency (safeguard likely mistakes, **preserve input**, reduce correction effort). NN/g also publishes a scoring rubric.
  - Apple HIG Writing and Alerts [P]: "display it as close to the problem as possible, avoid blame"; avoid "Error"/"Error 329347 occurred" titles; avoid "oops".
  - GOV.UK Error message and Error summary [P]: message next to the field *and* a summary at the top; move focus to the summary; "Do not clear any form fields"; reuse the question's wording in the message.
  - WCAG 3.3.1 Error Identification (A), 3.3.3 Error Suggestion (AA) [P]; KWCAG 7.3.1 (tell the location *and* the reason) [P].
- **Screen check.**
  - Submit with the scenario's intended mistakes (empty required field, bad format, expired card, server failure via network throttling or offline).
  - For each error, the persona answers: What went wrong? Where? What do I do now? Did I lose anything?
- **Evidence.** Error text verbatim, message bbox vs. field bbox, field values before and after, focus location after submit.
- **Deterministic.**
  - `aria-invalid=true` on failing fields.
  - Message linked by `aria-describedby`, or inside the label.
  - Message-to-field distance (bbox gap in px). Flag if the message is outside the viewport when the error appears.
  - Input preserved (values equal before and after, excluding password fields).
  - Focus moved to the error summary or first invalid field.
  - Error text not only coloured red (greyscale diff).
  - Generic-text lint: "오류가 발생했습니다" with no cause or action, raw codes, English exception text [D].
  - Premature validation: an error shown while the field still has focus and fewer characters than a valid minimum have been typed [D; NN/g "avoid displaying prematurely" [S]].
- **Severity.**
  - P0: the error hides that a payment or consent state is unknown ("결제 중 오류" with no indication whether money moved).
  - P1: error with no location or no fix path on a critical form; input wiped; error not announced (inaccessible).
  - P2: vague but recoverable message.
  - P3: tone ("oops", blame) only.

### UXD-13 Help, documentation and contextual guidance

- **Statement.** Help is available in context and in a consistent place, with a human or channel contact for critical flows.
- **Sources.** N10 [B]; ISO 9241-110 learnability [S]; KWCAG 7.2.2 / WCAG 3.2.6 Consistent Help [P] (contact details, contact mechanism, self-help, chatbot in the same relative order across pages); KRDS offers contextual-help, help-panel, tutorial-panel and coach-mark components [P, component list only].
- **Screen check.** From any stuck point, can the persona reach help within two actions? Is help in the same place on every page of the flow?
- **Evidence.** Path to help from the stuck point; help locations per page.
- **Deterministic.** Presence and DOM-order index of help links or buttons across pages (KWCAG 7.2.2) [P]; tap count to help [D].
- **Severity.** P1 if stuck in a critical flow (payment, identity) with no help or contact; P2 if help exists but is inconsistent or buried; P3 otherwise.

### UXD-14 Closure and success states

- **Statement.** Task sequences end with a clear completion state: what was done, reference number, what happens next, where to go.
- **Sources.** S4 [S]; Apple HIG Feedback [P]: confirm significant completed actions ("confirms a successful Apple Pay transaction"), but reserve confirmations for important ones; Apple HIG Writing: make completion clear ("Done") [P].
- **Screen check.** At the end of each scenario, the persona states: Did it work? What is my reference (order or application number)? What happens next, and when?
- **Evidence.** Completion screen capture; presence of reference ID, amount, schedule and next step.
- **Deterministic.** On completion routes: the page contains an ID-like token (regex), the amount matches the pre-submit total (diff), and there is a heading and a next-step link [D].
- **Severity.** P1 if completion is ambiguous for payment, application or cancellation (users retry or call support); P2 if the reference or next step is missing; P3 for tone.

### UXD-15 Empty states (and zero-result search)

- **Statement.** Empty lists, zero results, first-use screens and "all done" states explain the state and give a next action.
- **Sources.** Apple HIG Writing [P]: "Provide clear next steps on any blank screens… guide people on actions they can take, and give them a button or link"; "empty states are usually temporary, so don't show crucial information". N1/N10 [B].
- **Screen check.** Force empty states: a new account, a search for a nonsense string, filters that exclude everything, an empty cart. Can the persona tell *why* it is empty (no data vs. error vs. filter) and what to do next?
- **Evidence.** Screen capture, trigger action, available next actions.
- **Deterministic.**
  - A list container with zero items has an explanatory text node plus at least one actionable element [D].
  - Zero-result search shows the query echo and a filter reset [D].
  - Distinguish error from empty: HTTP status or console error during an "empty" render ⇒ mislabelled error [D].
- **Severity.** P1 if an error is shown as "empty" (e.g., "주문 내역이 없습니다" when the fetch failed), which can cause duplicate orders or false reassurance; P2 for a dead-end empty state on a key screen; P3 for copy.

### UXD-16 Information architecture and wayfinding

- **Statement.** Users know where they are, where they can go, and how to get back. Labels and grouping follow users' mental models.
- **Sources.** N6 and Norman conceptual model [B]; KWCAG 6.4.2 titles for page, frame and block, 6.4.1 skip repeated areas, 6.4.3 meaningful link text [P]; KRDS breadcrumb, side-navigation, in-page-navigation and step-indicator components [P, component list].
- **Screen check.** On arrival at each screen, the persona answers: Where am I (section and page)? How did I get here? How do I go up one level or back to the start? It also predicts which menu holds the scenario's target *before* opening menus (a tree-test-like probe) [D].
- **Evidence.** The persona's location statement vs. the actual route; the menu-prediction hit or miss.
- **Deterministic.**
  - Unique, descriptive `<title>` per route (KWCAG 6.4.2) [P].
  - One `h1`.
  - `aria-current` on active nav.
  - Breadcrumb or step-indicator presence in deep or multistep flows.
  - Skip link as the first focusable element (KWCAG 6.4.1) [P].
  - Nav depth: taps from home to the target [D].
- **Severity.** P1 if the target is unreachable by navigation (search only) or the persona is lost in a critical flow; P2 for wrong-section predictions by several profiles (coverage) or missing location cues in multistep flows; P3 for titles and labels.

### UXD-17 Information scent (link and label predictiveness)

- **Statement.** Link and label text predicts the destination, so users choose correctly and don't pogo-stick.
- **Sources.** Pirolli & Card 1999, information foraging and scent [S]; KWCAG 6.4.3 and WCAG 2.4.4 link purpose [P]; Apple HIG Writing: avoid "Click here" [P].
- **Screen check.**
  - Before each navigation click, the persona writes the expected destination content in one sentence and a confidence of 1–5.
  - After landing, it scores match or mismatch.
  - Generic labels are flagged: 더보기, 바로가기, 클릭, 여기, 자세히 — acceptable only with context.
- **Evidence.** (link text, surrounding context, predicted content, actual `h1`/`title`, match score).
- **Deterministic.**
  - **Scent-mismatch rate:** share of navigations where a text-similarity score between the prediction and the landing `h1`/`title`/first paragraph falls below a threshold [D]. The LLM does the prediction; the comparison can be embedding-based. Calibrate the threshold.
  - **Pogo-stick count:** return to the previous route within N seconds without interaction [D].
  - Duplicate link texts pointing to different destinations on one page [D].
- **Severity.** P1 when mis-scent sends users to a wrong high-stakes action (e.g., "해지" link leads to a retention offer page with no cancel path; see DP checks); P2 for repeated pogo-sticking on the main task; P3 for generic labels with sufficient context.

### UXD-18 Form design

- **Statement.** Ask only what's needed, one clear question at a time. Use persistent visible labels, the right input types and keyboards, clear required/optional marking, and well-timed validation.
- **Sources.**
  - Wroblewski, *Web Form Design* (2008). Penzo's 2006 eye-tracking [S] reported that top-aligned labels allowed label and field to be captured together, with the fastest completion. The same snippet says right-aligned labels roughly halved fixations and completion time, apparently relative to left-aligned labels; the comparison baseline is UNCONFIRMED.
  - Baymard checkout benchmark [S]: average checkout 11.3 form fields in 2024 (11.8 in 2021, 12.7 in 2019). Most sites need about 8 fields, or about 12–14 form elements. An older benchmark figure of 23.48 form elements / 14.88 fields has an unconfirmed year.
  - GOV.UK Question pages [P]: "Never mark mandatory fields with asterisks"; add "(optional)" to optional fields; one question per page to start; allow "I do not know" when valid.
  - Apple HIG Entering Data [P]: pre-gather data, offer choices instead of typing, validate dynamically, never prefill passwords, make clear that required data blocks progress.
  - KWCAG 7.3.2 labels associated with inputs [P]; WCAG 3.3.2 [P].
- **Screen check.** Fill the form as the persona would, on the persona's device, including autofill. Note:
  - every field whose purpose is unclear;
  - every label that disappears (placeholder-only);
  - wrong keyboards (numeric fields opening a text keyboard);
  - confusing required/optional markers;
  - validation that fires while typing.
- **Evidence.** Field inventory: label, type, required flag, autocomplete, keyboard shown, validation behaviour.
- **Deterministic.**
  - Field count per flow; compare with the flow's minimum necessary set (a scenario-defined list) [D]. Baymard's 8 applies to checkout only [S].
  - Placeholder-only labelling: input with no `<label>`/`aria-label`/`aria-labelledby` but with `placeholder` [D].
  - `type`/`inputmode` for tel, email and numeric data.
  - `autocomplete` tokens.
  - Required marker consistency: `required`/`aria-required` vs. visual marker [D].
  - Multi-column layouts on mobile: fields side by side at < 400 CSS px width [D, heuristic].
  - Validation timing (see UXD-12).
- **Severity.** P1 if a required field is unlabelled for assistive tech or the persona cannot determine what to enter on a critical form; P2 for excess fields, wrong keyboards or placeholder-only labels; P3 for marker style.
- **Korea.**
  - Address entry normally uses a postcode search popup or layer [B]. Test it on mobile (popup blockers, iframe scroll traps, return of values).
  - Name fields: accommodate foreign names and spacing [B].
  - Phone: carrier-verified numbers often come from 본인확인 (Section 4.2), which removes the need to type them again (UXD-09).

### UXD-19 Price and total-cost transparency (checkout)

- **Statement.** The price a user decides on is the price they pay. Mandatory costs are visible early. The total is visible before commitment.
- **Sources.**
  - Baymard [S2]: extra costs too high is the #1 fixable abandonment reason (39%, 2024 US survey of 4,329 adults, excluding "just browsing"). Other reasons: "couldn't see / calculate total order cost up-front" (21%, UNCONFIRMED year), "didn't trust the site with my credit card" (19%), "checkout too long/complicated" (18% in 2024; 17% in a 2025 secondary summary), required account creation (19% in 2024; another secondary summary cites about 26% of "preventable" abandonments, basis unclear, UNCONFIRMED), slow delivery (23%, UNCONFIRMED). Average documented cart abandonment 70.19% across 49 studies [S]; a 2026 secondary site cites 70.22% (UNCONFIRMED).
  - Better checkout design: up to 35.26% conversion increase, "$260 billion" recoverable across $738 billion of US+EU e-commerce; the average of 60 benchmarked sites had 39 improvement areas [S].
  - **Korea: 전자상거래법 Art. 21-2(1)1** [P]. On the **first screen** of a price display or advertisement, showing only part of the **총금액** (price plus costs necessarily incurred to receive the goods or service) to lure consumers is prohibited. The exception requires a legitimate reason, disclosed per 시행규칙 Art. 11-4 [P]: disclose the excluded items and the reason on the first screen; if space is short, the reason may be on a directly linked screen.
- **Screen check.** Record the price at: the listing card, the product detail first view, the cart, the checkout, and the final pay screen. The persona notes every new mandatory charge and where it first appeared.
- **Evidence.** Price ledger per stage with screenshots and element selectors.
- **Deterministic.**
  - Parse currency amounts per stage and compute Δ = final payable − first-shown price.
  - Attribute Δ to line items: shipping, service fee, mandatory option, tax.
  - Any mandatory line item not disclosed on the first screen, with no exclusion notice ⇒ candidate Art. 21-2(1)1 issue.
  - Whether shipping counts as "necessarily incurred" in a given model is a legal judgment. Record it, don't decide it.
  - Coupon or card-discount "최대 할인가" shown larger than the payable price: prominence ratio [D]. Links to the FTC 거짓 할인 type [S] if conditions are hidden.
- **Severity.**
  - P0: the final charged amount differs from the confirmed total, or a fee appears after the final confirm.
  - P1: a mandatory fee first appears at checkout and was not on the first screen (plus legal ref).
  - P2: total visible only after login or address entry.
  - P3: formatting.

### UXD-20 Onboarding, first-run and permission requests

- **Statement.** First use is brief, optional where possible, and teaches by doing in context. Permissions are requested when needed, with reasons.
- **Sources.**
  - Apple HIG Onboarding [P]: teach through interactivity; prefer context-specific tips; if a tutorial exists, make it optional and don't show it again after skipping, but keep it findable; postpone nonessential setup; avoid licensing text in onboarding; ask for ratings or purchases only after engagement.
  - Apple HIG Alerts: avoid alerts at app start [P].
  - **Korea: 정보통신망법 Art. 22-2** [P]. For app access permissions, tell users for each permission whether it is necessary. For necessary ones: the item and reason. For optional ones: the item, the reason, and that the user may refuse. Service cannot be refused for declining optional permissions (Art. 22-2(2)).
- **Screen check.**
  - Cold-start the app. Count screens before the first value moment.
  - Check whether tutorial and marketing screens are skippable.
  - Check whether each permission prompt says what and why, and whether the app still works after "허용 안 함" for optional permissions.
- **Evidence.** First-run screen sequence; permission prompts with text; post-denial behaviour.
- **Deterministic.**
  - Screens and taps to first task start [D].
  - A skip control exists (text match 건너뛰기/skip) [D].
  - The permission notice screen lists each permission with a 필수/선택 marking [D].
  - Post-denial probe: deny an optional permission, then attempt the main task. Blocked ⇒ violation of Art. 22-2(2) [P].
- **Severity.** P0 if denying an optional permission blocks the core service (legal and privacy); P1 for an unskippable long tutorial blocking the critical task, or a permission request with no reason; P2 for onboarding that front-loads setup; P3 for tone.
- **Surfaces.** Games: forced tutorials are common. Judge by Apple's "fast, fun, optional" and by whether the tutorial can be replayed [P].

### UXD-21 Microcopy and button labels

- **Statement.** Labels say what will happen (verb plus object). Destructive and cancel options are unambiguous. Voice and tone are consistent and non-manipulative.
- **Sources.** Apple HIG Alerts and Writing [P]: prefer specific verbs ("Erase", "Delete") over "OK"; always "Cancel" for cancel; place the default button trailing; "Avoid using we"; avoid cute labels ("Send" > "Let's do it!"). KWCAG 6.5.3 (visible label text included in the accessible name) [P]; KWCAG 6.4.3 [P].
- **Screen check.** For each dialog, the persona predicts the result of each button from its label alone, then verifies. It flags "확인/취소" pairs where "취소" is ambiguous (cancel the dialog vs. cancel the order) [B, a common Korean ambiguity].
- **Evidence.** Dialog text, button labels, predicted vs. actual effect.
- **Deterministic.**
  - Label lexicon lint: generic labels (확인, OK, 예/아니오) on destructive or financial dialogs [D].
  - Visible text ⊂ accessible name (KWCAG 6.5.3) [P].
  - Same label for opposite effects across screens (UXD-08).
- **Severity.** P0 if a button label misstates a financial or legal effect (e.g., "무료 체험 시작" starts a paid subscription without disclosure; see DP checks); P1 if an ambiguous "취소" causes the wrong cancellation; P2 for vague labels; P3 for tone.

### UXD-22 Interruptions: modals, popups, alerts, notifications

- **Statement.** Interrupt only for critical, actionable information. Never re-ask a decision the user just made. Let users dismiss easily.
- **Sources.**
  - Apple HIG Alerts [P]: use sparingly; not merely to inform; not at app start; not for common undoable actions.
  - Shneiderman S7 [S]; KWCAG 7.2.1 no popups the user didn't initiate [P].
  - EU DSA Art. 25(3)(b): "repeatedly requesting… a choice… already made, especially by presenting pop-ups" [S].
  - **Korea: 전자상거래법 Art. 21-2(1)5 (반복간섭)** [P]. Repeatedly asking via popups to change a choice already made is prohibited. The exception applies if, when asking, the user can opt not to be asked again for ≥ **7 days** (시행령 Art. 27-2) [P].
- **Screen check.** Count interruptions per scenario. After declining an offer, app review prompt or notification opt-in, continue the scenario and later restart the session. Record whether and when the same ask reappears, and whether a "7일간 보지 않기" option was offered.
- **Evidence.** Interruption log: time, trigger, content, dismiss options, recurrence.
- **Deterministic.**
  - Modal detection (`role=dialog`, overlay covering ≥ X% of the viewport).
  - Interrupts per minute of task time [D].
  - Re-ask interval after decline, measured within the session and across sessions with a clock shift if the harness allows.
  - Opt-out option present with ≥ 7-day scope ⇒ exception satisfied [P].
  - Modal on cold start before any user action ⇒ note (Apple) [P].
- **Severity.** P1 if a re-ask of a declined commercial choice happens without the 7-day option (legal ref plus trust), or a modal blocks a critical task with no dismiss; P2 for interruption density on the main path; P3 otherwise.

### UXD-23 Time limits

- **Statement.** Time limits are avoided or adjustable, with warnings and extension.
- **Sources.** WCAG 2.2.1 Timing Adjustable (A) [P]: turn off, adjust to at least 10×, or warn and give ≥ 20 s to extend with a simple action (extendable ≥ 10 times); real-time and > 20 h exceptions. KWCAG 6.2.1 [P]: avoid time limits; if required, allow release or extension, announced ≥ 20 s in advance; auctions and real-time games are exempt but must announce the limit and its end; sessions ≥ 20 h are exempt.
- **Screen check.** Detect countdowns (session expiry, 인증번호 입력 시간, seat hold, payment window). Wait to near expiry. Check the warning and extend option, and what happens to entered data at expiry.
- **Evidence.** Timer text, start time, warning time, extend control, post-expiry state.
- **Deterministic.**
  - Countdown regex (`\d{1,2}:\d{2}`, `남은 시간`) plus DOM mutation cadence.
  - Measure warning lead time (≥ 20 s) and the extend control [P].
  - Data retention after expiry (diff) [D].
  - Typical SMS verification timers are UNCONFIRMED here. Measure, don't assume.
- **Severity.** P0 if expiry during payment or identity verification leaves an unknown charge or verification state; P1 if expiry without warning loses entered data; P2 for a short but extendable limit; P3 for no countdown visibility.
- **Surfaces.** Games: real-time challenge timers are exempt (essential), but menus, purchases and consent screens are not [P+D].

### UXD-24 Deceptive and manipulative design

Detection rules are in Section 4.4, which crosswalks the taxonomies and Korean law. Severity baseline:

- P0: the pattern causes an unconsented payment, subscription, data disclosure, or an irreversible commitment.
- P1: the pattern steers a material choice or blocks cancellation or withdrawal (trust damage), or matches a statutory prohibition.
- P2: pressure cues with no verified falsity (timers or stock claims that can't be verified).
- P3: mild nudges.

---

## 4. Dark patterns: taxonomies, law and checks

### 4.1 Taxonomies

**Brignull / deceptive.design.**

- Original list [S2]: trick questions, sneak into basket, roach motel, privacy zuckering, price comparison prevention, misdirection, hidden costs, bait and switch, confirmshaming, disguised ads, forced continuity, friend spam.
- Current site types seen in snippets [S]: comparison prevention, confirmshaming, disguised ads, fake scarcity, fake social proof, fake urgency, forced action, hard to cancel, hidden costs, hidden subscription, nagging, obstruction, preselection, sneaking, trick wording, visual interference. The exact current list is UNCONFIRMED; the page was not fetched. Six of these were confirmed by definition snippets: comparison prevention, fake social proof, hidden subscription, visual interference, trick wording, hard to cancel.

**Gray, Kou, Battles, Hoggatt & Toombs, CHI 2018** [S]. Five strategies: nagging, obstruction, sneaking, interface interference, forced action.

**Mathur et al., CSCW 2019, "Dark Patterns at Scale"** [S for the paper; P for the released data].

- Paper figures: about 53K product pages from about 11K shopping sites; 1,818 instances; 15 types in 7 categories; 183 websites with deceptive instances; 22 third-party entities offering dark patterns as turnkey solutions.
- Released CSV (`data/final-dark-patterns/dark-patterns.csv`): 1,818 rows. The `Deceptive?` column holds Yes 208 / Depends 26 / No 1,584. Distinct hostnames by my parse: 1,263. The paper's site count was not verified.

| Category | Type | Instances (CSV) [P] |
|---|---|---|
| Sneaking | Sneak into Basket | 7 |
| Sneaking | Hidden Costs | 5 |
| Sneaking | Hidden Subscription | 14 |
| Urgency | Countdown Timer | 393 |
| Urgency | Limited-time Message | 88 |
| Misdirection | Confirmshaming | 169 |
| Misdirection | Visual Interference | 25 |
| Misdirection | Trick Questions | 9 |
| Misdirection | Pressured Selling | 67 |
| Social Proof | Activity Notification | 313 |
| Social Proof | Testimonials of Uncertain Origin | 12 |
| Scarcity | Low-stock Message | 632 |
| Scarcity | High-demand Message | 47 |
| Obstruction | Hard to Cancel | 31 |
| Forced Action | Forced Enrollment | 6 |

The three most frequent types (low-stock, countdown, activity notifications) are visually obvious but their truthfulness is hard to verify. Those are exactly the checks that need cross-session probes, not screenshots.

**EU DSA Art. 25** (applicable 17 Feb 2024) [S].

- Art. 25(1): online platform providers "shall not design, organise or operate their online interfaces in a way that deceives or manipulates… or… materially distorts or impairs" free and informed decisions.
- Art. 25(2): excludes practices covered by the UCPD or GDPR.
- Art. 25(3): Commission guidelines may address (a) giving more prominence to certain choices, (b) repeatedly requesting a choice already made, especially via pop-ups, and (c) making termination harder than subscribing.
- Recital 67 names "dark patterns".
- A BEUC Dec 2025 position paper, "Towards the Digital Fairness Act", signals further EU rules [S].

**Korean FTC 온라인 다크패턴 자율관리 가이드라인** (2023-07-31) [S]: 4 categories and 19 types. It is non-binding; the guideline itself is not the legal violation standard.

| Category | Definition [S] | Types | Membership tag |
|---|---|---|---|
| 편취형 | Small interface manipulations that induce irrational or unexpected spending | 숨은 갱신, 순차공개 가격책정, 몰래 장바구니 추가 | [S] |
| 오도형 | False information, or screens and sentences built against normal expectations to induce mistakes | 거짓 할인, 거짓 추천, 유인 판매, 위장 광고, 속임수 질문, 잘못된 계층구조, 특정옵션 사전선택 | [B], UNCONFIRMED membership |
| 방해형 | Making the user's intended action hard (snippet example: a hard-to-find ad close button) | 취소·탈퇴 등의 방해, 숨겨진 정보, 가격비교 방해, 클릭 피로감 유발 | [B], UNCONFIRMED |
| 압박형 | Repeated interference, time limits, low stock, other consumers' activity | 반복 간섭, 감정적 언어사용, 시간제한 알림, 낮은 재고 알림, 다른 소비자의 활동 알림 | [S] for 반복간섭, time limit, low stock, social activity; 감정적 언어사용 [B] |

The per-category counts (3 + 7 + 4 + 5 = 19) are consistent with the confirmed total. The FTC reportedly selected 13 of the 19 as needing regulation. Six not covered by the existing law were written into the 2024 amendment [S2].

### 4.2 Korean statute: 전자상거래법 as of 2026-07-21 [P]

**Amendment history.**

- Law No. 20302, promulgated 2024-02-13, in force one year later (2025-02-14) [P for the addendum; the date is [S]].
- 순차공개 가격책정 had a 6-month guidance period, ending 2025-08-13 [S].
- Law No. 21312, promulgated 2026-01-20, in force six months later (2026-07-21) [P]. It raised the fine ceiling for Art. 21-2 violations.

**Duties and prohibitions.**

| # | Provision | Legal text (paraphrase) [P] | Screen check |
|---|---|---|---|
| 1 | **숨은 갱신**, Art. 13(6); Decree Art. 20-2 | Before a subscription price increase or a free-to-paid conversion, the seller must obtain consent within the **30 days** before it takes effect, covering date, before/after price and payment method. It must also notify the conditions, method and effect of cancelling. | In free-trial sign-up: is the conversion date, price and cancel method shown at sign-up? The actual 30-day consent message is outside a single session (mark `unknown` unless the scenario spans it). |
| 2 | **순차공개 가격책정**, Art. 21-2(1)1; Rule Art. 11-4 | See UXD-19. | Price ledger. |
| 3 | **특정옵션 사전선택**, Art. 21-2(1)2 | During a purchase, sign-up or contract, offering a choice about *another* purchase, sign-up or contract with the "yes" option pre-marked before the consumer chooses. | DOM: any checkbox or radio for an add-on, insurance, membership or subscription that is `checked` on first render with no user action ⇒ violation candidate (deterministic). |
| 4 | **잘못된 계층구조**, Art. 21-2(1)3 | Among choices about purchase, sign-up, contract, cancellation, withdrawal or termination, showing visually **remarkable differences** in size, shape or colour that mislead the consumer: (가) that only a particular item can be chosen, or (나) that a particular item must be chosen as a condition. | Prominence metrics per decision group (area ratio, contrast ratio, fill vs. text-only, font size and weight). The legal threshold "현저한 차이" is undefined, so report metrics and let the judgment pass decide (Section 5). |
| 5 | **취소·탈퇴 등의 방해**, Art. 21-2(1)4 | Without legitimate reason: (가) a cancellation, withdrawal or termination procedure more complex than the purchase, sign-up or contract procedure; (나) cancellation only possible by a different method than sign-up (e.g., sign up in-app, cancel only by phone). | Run both scenarios. Compare screens, taps, required fields, and channel. Secondary sources say repeated "are you sure?" confirmation in two or more stages is a clear violation [S2]. |
| 6 | **반복간섭**, Art. 21-2(1)5; Decree Art. 27-2 | Repeated popup demands to change a choice already made; exception when the user can opt out for ≥ **7 days**. | UXD-22. |

**Related provisions.**

- **Reviews transparency**, Art. 21-4; Decree Art. 27-3, in force 2026-07-21 [P]. Sites posting user reviews must show, on the first review screen or one directly linked, who may write reviews, how long they are posted, the rating criteria and their effects, and the deletion criteria and objection procedure. Screen check: find that disclosure. Relates to FTC 거짓 추천 and Mathur "testimonials of uncertain origin".
- **Operator identity**, Art. 10(1) [P]. A cybermall must show the trade name and representative, address, phone and email, and further items. This is the common Korean footer block. Absence is a trust signal (UXD-13 and trust).
- **Sanctions.**
  - Art. 45(4)7 and 5-2: fine up to ₩10,000,000 for Art. 21-2 and 13(6) violations (amended 2026-01-20) [P].
  - Secondary sources report earlier per-violation amounts of ₩1M/₂M/₅M and business suspension of 3/6/12 months for repeat violations [S2, UNCONFIRMED; the annex tables were not readable].
  - First reported enforcement: in Oct 2025, four companies (Coupang, Wavve, NHN Bugs, Spotify) received corrective orders and ₩10.5M in total fines [S2, UNCONFIRMED]; ZDNet (2025-09-30) reports 45 dark-pattern cases corrected across OTT, music and commerce platforms [S].

### 4.3 Other Korean statutory screen rules touching manipulation or consent [P]

**PIPA (개인정보 보호법) Art. 22.**

- (1) Each consent item must be separated and clearly notified.
- (5) Service cannot be refused because the user declined optional items or marketing or third-party consents.
- (3) Data processed without consent must be disclosed separately from consented data.
- Decree Art. 17(1): consent must be free, specific and clear, in easy wording, with a clear way to indicate yes or no.
- Decree Art. 17(3): items to highlight — marketing contact, sensitive data or passport/licence/alien registration numbers, retention period, recipients and their purposes.
- Decree Art. 17(4): make clear that the user may choose.

**정보통신망법 Art. 50.**

- Explicit prior consent is required for commercial ads.
- Ads between 21:00 and 08:00 need a *separate* prior consent.
- Every ad must include sender identity and an easy opt-out.
- Decree: reconfirm consent every 2 years.

**게임산업법 Art. 33(2)** (new 2023-03-21). Games must display 확률형 아이템 types and per-type probabilities in the game, on the website and in advertising. Art. 33-2 allows damages up to 3× for intentional violations. The gacha purchase screen is directly checkable.

### 4.4 Detection matrix (what the swarm does)

| Pattern (taxonomy → KR law/FTC) | Deterministic probe | Judgment part | Default severity |
|---|---|---|---|
| Preselection / sneak into basket (Mathur Sneaking; Brignull; KR 21-2(1)2; FTC 몰래 장바구니 추가) | Initial-render state of all checkboxes, radios and toggles in commerce and consent flows. Cart diff between items explicitly added and items present at checkout. | Whether an item is "another" purchase or contract vs. part of the same one. | P1; P0 if it results in a charge. |
| Hidden costs / drip pricing (Mathur; KR 21-2(1)1) | Price ledger Δ (UXD-19). | Whether a cost is "necessarily incurred". | P1; P0 if post-confirm. |
| Hidden subscription / forced continuity (Mathur; KR 13(6)) | Text on the trial CTA and sign-up screen: conversion date, price, cancel method present? Payment method required for a "free" trial? | Clarity and prominence. | P0 if a paid subscription starts with no clear disclosure; P1 if disclosure is present but buried. |
| False hierarchy / visual interference (Gray interface interference; Mathur visual interference; KR 21-2(1)3; DSA 25(3)(a)) | For each binary choice group: area ratio, contrast ratio, filled vs. ghost, text size. Flag when the "decline/cancel" option is below 3:1 text contrast (WCAG text threshold as a floor) or much smaller [D]. | Is the difference "현저" and does it mislead? | P1 on consent, cancellation or purchase choices. |
| Hard to cancel / obstruction / roach motel (Mathur; Brignull; KR 21-2(1)4; DSA 25(3)(c)) | Sign-up vs. cancel path: screens, taps, fields, channel, number of retention interstitials. | Legitimacy of extra steps (e.g., identity check for a financial account). | P1; P0 if cancellation is impossible in-product while sign-up was in-product. |
| Nagging (Gray; KR 21-2(1)5; DSA 25(3)(b)) | Re-ask log after decline; presence of a ≥ 7-day opt-out. | — | P1 if no opt-out on a commercial re-ask. |
| Countdown timers / limited-time (Mathur Urgency; FTC 시간제한 알림) | Reload and fresh-session probe: does the timer reset or does the deadline move? Compare the deadline across sessions. | Whether urgency is real. | P2; P1 if the timer is demonstrably fake. |
| Low-stock / high-demand / activity notifications (Mathur Scarcity & Social Proof; FTC 낮은 재고, 다른 소비자 활동) | Cross-session and cross-account consistency of the stock count or "N명이 보는 중"; stock message persists after the purchase quantity exceeds the claimed stock. | Truthfulness is often `unknown`. | P2 (`unknown` truth) → P1 if demonstrably false. |
| Confirmshaming / emotional language (Mathur Misdirection; FTC 감정적 언어사용) | Decline-option text lexicon (e.g., "혜택을 포기할게요", "괜찮아요, 비싸게 살래요") [D]. | Guilt or shame tone. | P2; P1 on cancellation flows. |
| Trick questions / trick wording (Brignull; Mathur; FTC 속임수 질문) | Double negatives and opt-in/opt-out polarity mixed in one consent group (regex for 않/안/거부 within checkbox labels) [D]. | Comprehension check: the persona paraphrases what checking means. | P1 on consent. |
| Disguised ads (Brignull; FTC 위장 광고) | Ad-network iframes or known ad selectors without a visible "광고/AD" label nearby [D]. | Whether the content reads as editorial or search result. | P2; P1 in search results. |
| Forced action / forced enrollment (Gray; Mathur) | Task blocked until an unrelated action (account creation, app install, marketing consent). Probe by attempting to skip. | — | P1; P0 if the forced item is a privacy consent contrary to PIPA 22(5). |
| Comparison prevention (Brignull; FTC 가격비교 방해) | Unit price missing where quantities differ; plan comparison table missing fields [D]. | — | P2. |
| Click fatigue / 클릭 피로감 유발 (FTC) | Taps required to decline vs. accept. | — | P2. |
| Gacha probability disclosure (KR game law 33(2)) | Probability table reachable from the purchase screen of a random item [D]. | Completeness. | P1 if absent (legal); P0 if a paid random item has no disclosure and the purchase is one tap. |

**Agent-susceptibility safeguard.** Detection must not depend on the persona agent "noticing". Research on web and computer-use agents reports they can be steered by dark patterns (SusBench, arXiv 2510.11035; DECEPTICON, arXiv 2512.22894; titles only [S]). Run a separate auditor pass with the deterministic probes above. Log when a persona agent *accepted* a preselected or steered option as a coverage signal, not as proof.

---

## 5. Korean-specific conventions and regulations

### 5.1 Identity verification (본인확인 / 본인인증)

**Legal frame [P].**

- 정보통신망법 Art. 23-2: providers may not collect 주민등록번호 unless designated as 본인확인기관 (Art. 23-3, designated by the 방송미디어통신위원회 after amendment 2025-10-1), or the MVNO case. Even then they must offer a non-RRN alternative (대체수단).
- PIPA Art. 24-2(1): RRN processing only with specific legal basis. **Art. 24-2(3):** even then, web sign-up must be possible *without* an RRN.
- PIPA Art. 22-2 and Decree Art. 17-2: under-14 users need legal-guardian consent, verified by methods including the guardian's mobile 본인인증, card information, or SMS confirmation.

**Common flow forms [B].**

- Mobile-carrier verification (통신사 selection including MVNO/알뜰폰, name, birthdate plus the RRN gender digit, phone, then SMS code or carrier app).
- Carrier "PASS"-type app verification.
- 공동인증서 / 금융인증서.
- Private certificates (e.g., Kakao, Naver, Toss).
- i-PIN (legacy).

**Screen checks.**

1. **Context change.** Verification opens in a popup, new window or app switch. KWCAG 7.2.1 requires no unintended new windows [P]. Check return-to-origin with state preserved (UXD-07). Test with popup blockers and in in-app browsers (KakaoTalk or Naver in-app webviews are common entry points [B]).
2. **Timers.** Measure the SMS code window and extension (UXD-23).
3. **Carrier list.** Includes MVNO. Foreigners and non-Korean-phone users have a documented alternative or a clear dead-end message (universal usability, S2).
4. **Data minimization.** Fields requested vs. needed. If the verification result supplies name, birthdate and phone, they should not be re-entered (UXD-09).
5. **Accessible authentication.** At least one method must not rely only on a cognitive test (KWCAG 7.3.3) [P]. KWCAG lists "finding images containing a specific object" as a cognitive test, which is stricter than WCAG 3.3.8 AA; WCAG allows object recognition there and only AAA 3.3.9 removes it [P, D]. CAPTCHA-only gates on sign-up ⇒ flag.
6. **Result ambiguity.** After verification, the originating screen shows a verified state (name or number masked) (UXD-01).

**Severity.** P0 if a verification failure or timeout during payment or account recovery leaves the user locked out with no alternative, or if RRN is required at sign-up with no alternative (privacy and legal). P1 if the popup is blocked in common in-app browsers or state is lost on return. P2 for re-entry of verified data.

### 5.2 Digital signatures (공동인증서) [P]

The 전자서명법 full revision (Law No. 17354, promulgated 2020-06-09, in force six months later) removed the special legal status of 공인인증서. The old certificates became 공동인증서 in common usage [B].

- **Art. 6(2):** the state must not restrict use to a specific e-signature means unless a statute specifies one.
- **Art. 6(1):** the state must promote diverse means such as biometrics and blockchain.

QA implications:

- A public-sector flow that offers only one certificate type, where no law mandates it, is a finding to raise, with a legal-hook note.
- Legacy pain points (plug-in or security-program installs, keyboard-security modules) remain possible [B]. Check whether any install is required before the task. Record whether install prompts are OS-native or deceptive-looking.

### 5.3 Simple payments (간편결제) and PG hand-offs [B]

**Screen checks.**

- The total amount is consistent across merchant → PG or wallet → return (UXD-19).
- App-switch round trip returns to the right screen with the order state.
- Back or cancel inside the wallet produces a clear "not paid" state (UXD-07, UXD-14).
- Default wallet preselection is neutral. Preselecting a payment *method* is not the Art. 21-2(1)2 pattern, which concerns *other* purchases or contracts. But a preselected paid add-on (e.g., 결제 보험, membership trial) inside payment is.
- The confirmation screen shows the amount and merchant (UXD-14).

### 5.4 Terms and consent UI (약관 동의)

**Korean convention [B].** An "전체 동의" master checkbox, with individual items labelled [필수] / [선택] and expandable full text.

**Statutory checks [P].**

- Separate consent per legally distinct item (PIPA Art. 22(1)).
- Optional items clearly marked as choosable (Decree Art. 17(4)).
- Important items emphasized (Decree Art. 17(3)).
- Declining optional or marketing items does not block sign-up (Art. 22(5)).
- Marketing SMS or push consent separate, plus a separate night-time consent (정보통신망법 Art. 50(1),(3)).
- App permission notice split into 필수/선택 (Art. 22-2).

**Deterministic probes.**

1. Count checkboxes, and check whether [선택] items are unchecked on first render.
2. Uncheck every [선택] item and try to proceed. Blocked ⇒ violation candidate.
3. The master "전체 동의" toggles all items, and individual toggles remain operable afterwards [D].
4. The full text is expandable and readable: font size and contrast per KWCAG 5.4.3 [P].
5. The marketing item is not bundled into a [필수] item's text (text search for 광고, 마케팅, 이벤트 inside [필수] item bodies) [D].

**Severity.** P0 if optional or marketing consent is required to proceed, or a [선택] item is pre-checked and bundled (privacy). P1 if consents are bundled into one checkbox. P2 for unreadable full text. P3 for layout.

### 5.5 Korean e-commerce patterns and pain points (screen checks) [B, no prevalence numbers]

- **Long image-based detail pages (상세페이지).** Text rendered in images fails KWCAG 5.1.1 (alt text) and 1.4.3 (contrast) [P]. It also defeats zoom and search. Deterministic: ratio of text-in-image area to real text (OCR on images vs. DOM text).
- **Price stacks.** "정가 → 할인가 → 쿠폰가 → 카드 즉시할인 → 최대 혜택가" with the largest emphasis on a conditional price. Check the prominence of the payable-without-conditions price (UXD-19; FTC 거짓 할인).
- **Free-shipping thresholds and bundles.** Verify that the shipping-fee rule is visible on the first price screen (Art. 21-2(1)1).
- **Review areas.** Review policy disclosure (Art. 21-4) [P]; "구매자 리뷰" vs. "체험단" labelling (disguised ads / 거짓 추천).
- **Membership upsells** during checkout (preselection, nagging).
- **Business info footer** (Art. 10) [P].
- **Government sites.** KRDS masthead text "이 누리집은 대한민국 공식 전자정부 누리집입니다" [P]. This is an authenticity cue; its absence on a claimed-government page is a trust or phishing signal.

### 5.6 Accessibility: KWCAG 2.2 (KS X OT0003:2022) [P]

**Structure.** 4 principles (인식의 용이성, 운용의 용이성, 이해의 용이성, 견고성), 14 guidelines, 33 items. It went from 24 to 33 items: 9 new, 2 guidelines added and 1 removed. Revised 2022-12-28. The foreword says it is based on WCAG 2.1 (2018), centred on level-A criteria and domestic conditions.

**The 33 items.**

| Principle | Items |
|---|---|
| 인식의 용이성 | 5.1.1 alt text; 5.2.1 captions, transcript or sign language; 5.3.1 tables; 5.3.2 linear order; 5.3.3 instructions not dependent on shape, size, position, direction, colour or sound; 5.4.1 no colour-only; 5.4.2 no autoplay sound (< 3 s allowed; otherwise a control); 5.4.3 contrast 4.5:1 (3:1 for ≥ 18 pt or 14 pt bold, or zoomable content); 5.4.4 separation of adjacent content |
| 운용의 용이성 | 6.1.1 keyboard; 6.1.2 focus order and visibility; 6.1.3 operable controls (diagonal ≥ 6.0 mm desirable, ≥ 1 px inner non-reactive margin desirable); 6.1.4 character-key shortcuts; 6.2.1 adjustable time limits (≥ 20 s notice; 20 h exception); 6.2.2 pause moving content; 6.3.1 no flashing at 3–50 Hz; 6.4.1 skip repeated areas; 6.4.2 titles; 6.4.3 link text; 6.4.4 fixed reference location (e-publications); 6.5.1 single-pointer alternative; 6.5.2 pointer cancellation; 6.5.3 label in name; 6.5.4 motion actuation |
| 이해의 용이성 | 7.1.1 language; 7.2.1 execution on user request (no unexpected new windows or context change); 7.2.2 consistent help; 7.3.1 error correction; 7.3.2 labels; 7.3.3 accessible authentication; 7.3.4 redundant entry |
| 견고성 | 8.1.1 markup validity; 8.2.1 web-application accessibility |

**Differences from WCAG 2.1 / 2.2** [P for text, D for comparisons].

- **Scope.** KWCAG is a subset centred on level A. It *adds* AA contrast (1.4.3) as mandatory. Most AA and all AAA criteria are absent: reflow, resize text, non-text contrast, focus not obscured, target size (24 px), dragging movements.
- **New in 2022 (9).** 6.1.4, 6.5.1–6.5.4 (WCAG 2.1 A items), 6.4.4, 7.2.2, 7.3.3, 7.3.4. Of these:
  - 7.2.2 ≈ WCAG 2.2 3.2.6 Consistent Help (A).
  - 7.3.4 ≈ WCAG 2.2 3.3.7 Redundant Entry (A).
  - 7.3.3 ≈ WCAG 2.2 3.3.8/3.3.9. KWCAG's example treats object-image recognition as a cognitive test (closer to AAA 3.3.9).
  - 6.4.4 (page-break or reference locators for e-publications) has no WCAG 2.2 counterpart I could confirm.
- **Kept, but obsolete in WCAG 2.2.** 8.1.1 markup parsing. WCAG 2.2 removed 4.1.1 Parsing (marked obsolete 2023-01-25) [P].
- **Korea-only or stricter items.**
  - 5.4.4 content separation.
  - 6.1.3 control size in mm (≈ 4.24 mm square side [D]; WCAG uses 24 CSS px).
  - 5.4.2 frames autoplay as prohibited, with a 3 s tolerance.
- **WCAG 2.2 for comparison.** The `w3c/wcag` main branch includes 87 SC entries: 61 from 2.0, 17 from 2.1, 9 from 2.2, with 4.1.1 obsolete, so 86 active [P, D].

**Mobile apps and other surfaces.**

- **장애인차별금지법 Art. 21(2)** (new 2021-07-27) [P]: reasonable accommodation for mobile applications. **Decree Art. 14(4)–(6)** (new 2023-03-30; amended 2025-12-31) [P] covers smartphone apps and requires:
  1. compliance with the verification criteria set under 디지털포용법 시행령 Art. 24(2) (MSIT notice);
  2. an indication, before purchase or install, of whether the criteria are met;
  3. information needed for install and use by disability type.
- The Art. 24(2) criteria must consider functions that supplement hand or arm movement, reaction time, vision, colour discrimination, hearing and more [P].
- **디지털포용법** (Law No. 20672, promulgated 2025-01-21, in force 2026-01-22 per decree metadata) [P]. Art. 19 requires 국가기관등 to ensure accessibility of websites, mobile apps, **kiosks** and e-publications. Art. 20 covers kiosk assistance duties. Art. 21 creates an accessibility quality certification.
- **Technical baselines.**
  - KS X 3253:2016 (모바일 애플리케이션 콘텐츠 접근성 지침 2.0). The sibling brief reports controls ≥ 9 mm × 9 mm [S, UNCONFIRMED here].
  - KS X 9211:2022 kiosk accessibility: button gaps ≥ 2.5 mm [S, UNCONFIRMED].

**Automatable KWCAG checks**, via axe-style tooling plus custom rules:

- 5.1.1 alt presence (quality is judgment).
- 5.4.2 autoplay audio > 3 s (media element state).
- 5.4.3 contrast.
- 6.1.1 and 6.1.2 keyboard reachability and focus visibility (screenshot diff on focus).
- 6.1.3 control size in mm from device PPI.
- 6.2.1 timers.
- 6.3.1 flashing (frame analysis, 3–50 Hz).
- 6.4.1 skip link; 6.4.2 titles; 6.4.3 generic link text.
- 6.5.1 path gestures (sibling brief).
- 6.5.3 label-in-name; 7.1.1 lang.
- 7.2.1 new windows or context change on focus or input.
- 7.2.2 help order; 7.3.2 labels; 7.3.4 redundant entry; 8.1.1 duplicate IDs and nesting.

---

## 6. Non-automatable judgments

These must be recorded as `inferred` with an LLM rationale and screenshot crop, and preferably confirmed by a human for P0/P1.

1. **Conceptual-model fit** (Norman). Does the product's model (e.g., "wallet vs. points vs. coupons") match the persona's? Detectable only through expectation–outcome gaps and paraphrase tests.
2. **Language quality.** Plainness, tone, blame, register appropriateness for the persona (age, literacy, dialect), cultural fit, honorific choice. Lints only surface candidates.
3. **Meaning of icons and signifiers.** Whether a glyph reads as tappable or as intended (UXD-04). Deterministic checks find interactivity, not interpretability.
4. **"현저한 차이" and "misleading" in Art. 21-2(1)3.** Metrics can rank prominence gaps, but the statute has no numeric threshold. Legality is not decided by the tool.
5. **Legitimacy of friction.** Whether an extra cancellation step is a "정당한 사유" (e.g., fraud prevention); whether a cost is "necessarily incurred".
6. **Truthfulness of urgency, scarcity and social-proof claims.** Often `unknown`, even with cross-session probes. Server-side truth is invisible.
7. **Information-scent adequacy** for a specific persona's vocabulary. The prediction is the LLM's; only the comparison is computed.
8. **Aesthetic and minimalist design.** Clutter judgments beyond simple counts.
9. **Game-specific intent.** Whether difficulty, hidden affordances, timers or "forced" tutorials are intended challenge or a usability defect. Nielsen's heuristics must be reinterpreted for play (challenge is the product). Game-specific heuristic sets (e.g., Desurvire's HEP or PLAY, Pinelle et al.) exist in the literature [B] but were not researched here.
10. **Consent comprehension.** Whether a reasonable user would understand what they agreed to (persona paraphrase vs. legal text).
11. **Severity calibration across personas.** k-of-n profile coverage is not prevalence (repo rule). Final severity needs human review for P0/P1.
12. **Help and alternative adequacy for excluded groups** (foreigners without Korean phones, MVNO users, under-14s). The tool can find dead ends; whether an offline alternative is adequate is judgment.

---

## 7. Contradictions and tensions

| Topic | Position A | Position B | Resolution for QA |
|---|---|---|---|
| Inline validation timing | Apple HIG: "validate field values… as soon as people enter them" [P] | NN/g: avoid displaying errors prematurely [S] | Validate on blur or after a plausible complete entry, not per keystroke. Flag only premature (mid-typing) errors. |
| Required-field marking | GOV.UK: "Never mark mandatory fields with asterisks"; mark optional [P] | Korean and common practice: `*` = 필수 [B]; Baymard reportedly recommends marking both (UNCONFIRMED) | Don't flag asterisks per se. Flag *inconsistency* between visual marker and `required`, and unmarked optional fields. |
| Placeholder / hint text | Apple HIG: use hint or placeholder text for format [P] | Placeholder-as-label is harmful [B, widely cited NN/g and W3C techniques] | Placeholder allowed *in addition to* a persistent label. Placeholder-only ⇒ flag. |
| Confirmation dialogs | Shneiderman S5 and NN/g: prevent errors; confirm | Apple: don't confirm common undoable actions [P]. Korean law: repeated "are you sure" steps in cancellation can be obstruction [S2] | Confirm only irreversible or high-stakes actions. For cancellation, one confirmation is fine; stacked retention prompts are an obstruction candidate. |
| Label alignment | Penzo 2006: top-aligned fastest [S] | Same snippet: right-aligned reduced fixations vs. left (baseline unclear) [S] | Mobile: top-aligned by default. Don't score alignment as a defect unless the persona mis-associates labels. |
| Baymard figures drift | Account creation 19% (2024) [S2] | About 26% in another secondary summary (basis unclear) [S2]; abandonment 70.19% vs. 70.22% [S/S2] | Always cite year and survey. Treat as context, not gates. |
| ISO 9241-112 version | 2017 six principles [S] | 2025 edition exists; list not verified [S] | Cite "ISO 9241-112:2017" explicitly until the 2025 text is checked. |
| KWCAG "2.2" naming | Name suggests WCAG 2.2 | Text says based on WCAG 2.1; adds some 2.2-equivalent items and keeps obsolete Parsing [P] | Never treat KWCAG conformance as WCAG 2.2 AA. Run both rule sets and report separately. |
| Control-size floors | KWCAG 6.0 mm diagonal (desirable) [P] | WCAG 2.5.8: 24 CSS px; KS X 3253: 9 mm [S]; platform 44 pt / 48 dp (sibling brief) | Choose per surface (web vs. app vs. kiosk). See `motor-pointing.md`. |
| Dark-pattern definitions | Academic taxonomies (15–19+ types) | KR law: 5 prohibited behaviours + 1 subscription duty; DSA Art. 25 limited to online platforms and carved out for UCPD/GDPR | Severity is from user harm; `legal_refs` is separate. Never label a finding "illegal"; say "matches statutory element X; legal assessment required". |
| Severity scales | Nielsen 0–4 (usability harm) [S] | Repo P0–P3 (includes safety, privacy, misleading high-stakes) | Use the mapping in §2.3. Persistence raises severity. |
| Response-time limits | 0.1 / 1 / 10 s from 1968–1993 research [S] | Modern expectations may be stricter (no source found) | Use them as upper bounds for "must show feedback", not as quality targets. |
| FTC 19-type category membership | 편취형 and 압박형 members confirmed [S] | 오도형 and 방해형 membership from background [B] | Verify against the FTC PDF before publishing a Korean-language taxonomy table. |

---

## 8. Sources

### Primary, read at the time of writing [P]

- 전자상거래 등에서의 소비자보호에 관한 법률, 시행령, 시행규칙 (current: law as amended 2026-01-20, in force 2026-07-21). Via legalize-kr mirror of law.go.kr — https://github.com/legalize-kr/legalize-kr (kr/전자상거래등에서의소비자보호에관한법률/); canonical https://www.law.go.kr/법령/전자상거래등에서의소비자보호에관한법률
- 개인정보 보호법 and 시행령 (current text; Art. 22, 22-2, 24-2; Decree Art. 17, 17-2) — legalize-kr kr/개인정보보호법/
- 정보통신망 이용촉진 및 정보보호 등에 관한 법률 and 시행령 (Art. 22-2, 23-2, 23-3, 50) — legalize-kr kr/정보통신망이용촉진및정보보호등에관한법률/
- 전자서명법 (full revision Law No. 17354, 2020-06-09; Art. 6) — legalize-kr kr/전자서명법/
- 장애인차별금지 및 권리구제 등에 관한 법률 and 시행령 (Art. 21; Decree Art. 14) — legalize-kr
- 디지털포용법 and 시행령 (Law No. 20672, 2025-01-21) — legalize-kr kr/디지털포용법/
- 게임산업진흥에 관한 법률 (Art. 33, 33-2) — legalize-kr kr/게임산업진흥에관한법률/
- KS X OT0003:2022 한국형 웹 콘텐츠 접근성 지침 2.2 (HTML edition, a11ykr) — https://a11ykr.github.io/kwcag22/
- W3C WCAG 2.2 source: guidelines/index.html and sc/20, 21, 22 criterion files (target-size-minimum, consistent-help, redundant-entry, accessible-authentication-minimum/enhanced, error-identification, error-suggestion, error-prevention-legal-financial-data, status-messages, timing-adjustable, consistent-navigation, consistent-identification, labels-or-instructions, use-of-color, on-input) — https://github.com/w3c/wcag ; published at https://www.w3.org/TR/WCAG22/
- Apple Human Interface Guidelines: Onboarding, Loading, Feedback, Alerts, Entering data, Writing, Progress indicators — https://developer.apple.com/design/human-interface-guidelines/ (JSON endpoints)
- GOV.UK Design System: Error message, Error summary, Question pages — https://github.com/alphagov/govuk-design-system ; https://design-system.service.gov.uk/
- Mathur et al. dark-patterns dataset — https://github.com/aruneshmathur/dark-patterns (data/final-dark-patterns/dark-patterns.csv)
- KRDS HTML component kit (masthead, identifier, help components) — https://github.com/KRDS-uiux/krds-uiux ; https://www.krds.go.kr

### Search-snippet sources [S] (pages not opened)

- Nielsen, "10 Usability Heuristics for User Interface Design", NN/g (1994, updated) — https://www.nngroup.com/articles/ten-usability-heuristics/
- NN/g, "Visibility of System Status" — https://www.nngroup.com/articles/visibility-system-status/
- Nielsen, "Severity Ratings for Usability Problems", NN/g — https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/
- Nielsen, "Response Time Limits" (1993) — https://www.nngroup.com/articles/response-times-3-important-limits/
- NN/g, "Error-Message Guidelines" — https://www.nngroup.com/articles/error-message-guidelines/ ; "An Error Messages Scoring Rubric" — https://www.nngroup.com/articles/error-messages-scoring-rubric/
- NN/g, "Information Foraging" — https://www.nngroup.com/articles/information-foraging/ ; Pirolli & Card, "Information Foraging", Psychological Review, 1999 — https://philpapers.org/rec/PIRIF
- ISO 9241-110:2020 (preview) — https://webstore.ansi.org/preview-pages/ISO/preview_ISO+9241-110-2020.pdf ; summaries: https://www.dialogdesign.dk/isos-dialogue-principles-2019/
- ISO 9241-11:2018 — https://webstore.ansi.org/preview-pages/ISO/preview_ISO+9241-11-2018.pdf ; MeasuringU — https://measuringu.com/iso-9241/
- ISO 9241-210:2019 — https://www.iso.org/standard/77520.html
- ISO 9241-112:2017 — https://www.iso.org/standard/64840.html ; AHFE 2025 paper listing the six principles — https://openaccess-api.cms-conferences.org/articles/download/978-1-964867-75-5_220
- Norman, *The Design of Everyday Things*, revised ed. (2013) — summaries via https://uxmag.com/articles/understanding-don-normans-principles-of-interaction
- Shneiderman et al., *Designing the User Interface*, 6th ed. (2016) — https://www.cs.umd.edu/~ben/goldenrules.html ; https://www.hcil.umd.edu/posts/dtui-6th-edition/
- Baymard Institute, cart abandonment statistics — https://baymard.com/lists/cart-abandonment-rate ; checkout form fields — https://baymard.com/blog/checkout-optimization-from-16-fields-to-8 ; checkout UX guide — https://baymard.com/blog/checkout-flow-ux-optimization
- Penzo (2006) label placement; Wroblewski, *Web Form Design* (2008) — https://www.lukew.com/resources/web_form_design.asp ; Das, McEwan & Douglas (2008) NordiCHI — https://dl.acm.org/doi/10.1145/1463160.1463217
- Mathur et al., "Dark Patterns at Scale", PACM HCI CSCW 2019 — https://arxiv.org/abs/1907.07032 ; https://dl.acm.org/doi/10.1145/3359183
- Gray et al., "The Dark (Patterns) Side of UX Design", CHI 2018 — https://dl.acm.org/doi/10.1145/3173574.3174108
- Brignull, Deceptive Patterns — https://deceptive.design/
- EU Digital Services Act Art. 25 — https://www.eu-digital-services-act.com/Digital_Services_Act_Article_25.html ; EPRS 2025 briefing — https://www.europarl.europa.eu/RegData/etudes/ATAG/2025/767191/EPRS_ATA(2025)767191_EN.pdf ; BEUC Dec 2025 — https://www.beuc.eu/sites/default/files/publications/BEUC-X-2025-110_Towards_the_Digital_Fairness_Act.pdf
- 공정거래위원회, 온라인 다크패턴 자율관리 가이드라인 (2023-07-31) — https://www.korea.kr/briefing/pressReleaseView.do?newsId=156583129 ; https://www.ftc.go.kr/www/selectReportUserView.do?key=10&rpttype=1&report_data_no=10140
- 공정위 6개 유형 다크패턴 문답서 — https://news.seoul.go.kr/economy/archives/566114 ; 정책브리핑 정기결제 30일 — https://www.korea.kr/news/policyNewsView.do?newsId=148939436
- Law-firm and press summaries [S2]: 법률신문 — https://www.lawtimes.co.kr/LawFirm-NewsLetter/209791 , https://www.lawtimes.co.kr/LawFirm-NewsLetter/210196 ; 김·장 — https://www.kimchang.com/ko/insights/detail.kc?sch_section=4&idx=31411 ; ZDNet Korea 2025-09-30 — https://zdnet.co.kr/view/?no=20250930112519 ; imweb blog (fine increase, first enforcement) — https://imweb.me/blog?idx=496
- Agent susceptibility: SusBench — https://arxiv.org/pdf/2510.11035 ; DECEPTICON — https://arxiv.org/pdf/2512.22894 (titles only)
- LLM-based usability evaluation (related work, titles only): https://arxiv.org/pdf/2512.04262 ; https://arxiv.org/pdf/2604.25420

### Sibling brief

- `docs/human-factors/motor-pointing.md`: target size, KS X 3253 and KS X 9211 values, platform minimums.
