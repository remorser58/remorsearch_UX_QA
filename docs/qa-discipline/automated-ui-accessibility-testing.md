# 자동 UI·접근성 테스트: 규칙 엔진, 커버리지, 오탐 (Automated UI and accessibility testing)

작성: 2026-09-28. 후보 ID 접두사: `AUT-`. 사용자 지시에 따라 본문은 한국어로 쓰고, 표준 이름·규칙 ID·필드 이름·원문 인용은 영어 그대로 둡니다.

> 상태: 완료 (2026-09-28). 1–4절 모두 작성. 파일럿 스크립트는 스크래치패드에만 있고 저장소에는 넣지 않았습니다 (AUT-15에서 옮길 대상).

## 1. Scope and sources searched (범위와 검색한 자료)

### 1.1 질문

1. 규칙 엔진(axe-core, Lighthouse, Android ATF, XCTest 감사, W3C ACT Rules)은 무엇을 어떤 알고리즘으로 검사하고, 공개된 탐지율과 오탐률은 얼마인가?
2. Playwright 드라이버에서 결정적으로(deterministic) 검사할 수 있는 WCAG 성공 기준은 무엇이고, 정확한 알고리즘은 무엇인가? (4.1.2, 2.4.3, 2.4.7, 2.4.11/2.4.12, 1.4.10, 1.4.4, 1.4.12, 2.5.8, 1.3.1, 3.3.1/3.3.3, 글자 잘림)
3. 어느 검사가 프로필과 무관하고(한 번만 보고), 어느 검사가 프로필에 따라 달라지는가(저시력 확대, 노안 글자 크기)?
4. 이미 구현된 SM-01~SM-06, LY-01 가운데 무엇을 유지·축소·삭제하고, 무엇을 axe-core에 맡기며, 무엇을 새로 더해야 하는가? axe-core를 페이지 안에서 호출할 때 MPL-2.0은 무엇을 요구하는가?

### 1.2 검색 조건 (태그를 믿기 전에 읽을 것)

- 웹 검색 15회(검색 도구가 한 번에 여러 질의를 돌린 경우 포함), 원문 가져오기(WebFetch, raw GitHub, npm 레지스트리) 약 40회. 이 세션의 네트워크 정책이 `w3.org`, `deque.com`, `webaim.org`, `dl.acm.org`, `arxiv.org`, `semanticscholar.org`, `zenodo.org`, `*.github.io`, 대학 저장소(`eprints.whiterose.ac.uk`, `ro.ecu.edu.au`), `philmcminn.com`, `businesswire.com`을 막았습니다.
- 그래서 W3C 규범 문서는 W3C가 GitHub에 둔 **원본 소스**(`w3c/wcag`, `w3c/accname`, `w3c/wcag-act`, `act-rules/act-rules.github.io`)로 읽었습니다. 이 원본에서 읽은 문장은 [standard]로 태그합니다. 편집 중인 main 브랜치일 수 있으므로 인용문은 권고안(Recommendation)과 한 글자씩 대조하지는 않았습니다.
- 논문 대부분(Vigo 2013, Chiou 2021/2024, Althomali 2019, Groundhog 2022)은 초록이나 검색 발췌만 봤습니다. 이런 수치는 [snippet]입니다.
- 이 저장소의 `benchmarks/`, `.ergo-bench/`, `.claude/`는 읽지 않았습니다. 드라이버와 검사 코드(`drivers/web/*.mjs`, `ergoqa/checks.py`)는 읽기만 했습니다.

### 1.3 원문을 직접 읽은 자료

| 자료 | URL | 확인한 내용 |
| --- | --- | --- |
| axe-core README | https://github.com/dequelabs/axe-core | "on average 57% of WCAG issues automatically", "zero false positives (bugs notwithstanding)", `incomplete`, MPL-2.0 |
| axe-core 4.13 규칙 목록 | https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md | 규칙 105개(비권장 5개 포함), 절별 개수, Issue Type, ACT 대응 |
| axe-core LICENSE와 `axe.min.js` 4.13.0 머리말 | https://github.com/dequelabs/axe-core/blob/develop/LICENSE , https://registry.npmjs.org/axe-core/-/axe-core-4.13.0.tgz | MPL-2.0 §1.7, §3.1–3.4; 파일 크기 |
| npm 메타데이터 | https://registry.npmjs.org/ | axe-core 4.13.0 MPL-2.0, @axe-core/playwright 4.13.0 MPL-2.0, accessibility-checker 4.0.34 Apache-2.0, @siteimprove/alfa-rules 0.119.0 MIT, html_codesniffer 2.5.1 BSD-3-Clause |
| axe-core 이슈 검색 ("false positive" in title) | https://github.com/dequelabs/axe-core/issues?q=is%3Aissue+%22false+positive%22+in%3Atitle | 오탐 보고가 몰리는 규칙 |
| Lighthouse 설정과 점수 문서 | https://github.com/GoogleChrome/lighthouse/blob/main/core/config/default-config.js , https://github.com/GoogleChrome/lighthouse/blob/main/docs/scoring.md | 접근성 감사 가중치, 수동 감사 10개 |
| GOV.UK 접근성 도구 감사 | https://github.com/alphagov/accessibility-tool-audit (README, `tests.json`, gh-pages `index.html`) | 장벽 142개 × 도구 13개, 도구별 탐지율, 2018-04-13 갱신 |
| WCAG 2.2 성공 기준 원문과 Understanding | https://github.com/w3c/wcag (`guidelines/sc/**`, `understanding/**`) | 1.3.1, 1.4.4, 1.4.10, 1.4.12, 2.4.3, 2.4.7, 2.4.11–2.4.13, 2.5.3, 2.5.8, 3.3.1–3.3.3, 4.1.2 |
| ACT 규칙 원본 | https://github.com/act-rules/act-rules.github.io/tree/develop/_rules | 59br37, oj04fd, b4f0c3, 2ee8b8, 36b590, e086e5, 97a4e1, 24afc2 |
| ACT 구현 판정 규칙 | https://github.com/act-rules/act-rules.github.io/blob/develop/pages/implementations/mapping.md | 예제 유형별 허용 결과, correct/partial 구현 정의 |
| ACT 1.0 CR 구현 보고 (2019) | https://github.com/w3c/wcag-act/blob/main/act-implementations.html | 초기 규칙 11개와 구현 도구 |
| accname 1.2 편집자 초안 | https://github.com/w3c/accname (gh-pages `index.html`) | 계산 단계(Hidden Not Referenced ~ Tooltip), CSS 생성 콘텐츠, shadow DOM |
| Chrome DevTools Protocol `Accessibility` | https://github.com/ChromeDevTools/devtools-protocol/blob/master/pdl/domains/Accessibility.pdl | `getFullAXTree`, `queryAXTree`, 이름 출처 유형, 속성 이름, 무시 사유 |
| Playwright 문서 | https://github.com/microsoft/playwright/blob/main/docs/src/accessibility-testing-js.md , `aria-snapshots.md` | `@axe-core/playwright` 권장, 면책 문구, ARIA snapshot |
| Android ATF 소스 | https://github.com/google/Accessibility-Test-Framework-for-Android (`framework/checks/*.java`) | 검사 14개, 48 dp와 가장자리 32 dp, 대비 허용오차 0.01, TextSizeCheck 오탐 경고 |
| Apple `XCUIAccessibilityAuditType` | https://developer.apple.com/documentation/xcuiautomation/xcuiaccessibilityaudittype (JSON) | 감사 옵션 10개(`all` 포함), iOS 17 / macOS 14부터 |
| WWDC23 세션 10035 | https://developer.apple.com/videos/play/wwdc2023/10035/ | 이슈 핸들러로 오탐 무시, "audits shouldn't substitute real testing" |
| KWCAG 2.2 (KS X OT0003:2022) | https://github.com/a11ykr/kwcag22 | 33개 검사항목, 6.1.2, 6.1.3(대각선 6.0 mm 권장), 6.5.3, 7.3.1, 7.3.2 |
| VISER README | https://github.com/redecheck/viser | 반응형 레이아웃 실패를 "보이는 것/보이지 않는 것"으로 분류 |
| 라이선스 확인 | https://github.com/act-rules/act-rules.github.io/blob/develop/pages/license.md , https://github.com/alphagov/accessibility-tool-audit/blob/master/LICENSE | ACT: W3C Software and Document Notice. GOV.UK 감사: MIT |
| WCAG-EM 2.0 초안 | https://github.com/w3c/wai-wcag-em (`procedure.md`, `status.md`) | 무작위 표본 10 %, 완결 프로세스, Step 4.3 |

### 1.4 검색 발췌로만 본 자료 ([snippet])

- Deque, "Automated testing identifies 57 percent of digital accessibility issues" (2021): https://www.deque.com/blog/automated-testing-study-identifies-57-percent-of-digital-accessibility-issues/ , 보도자료 https://www.businesswire.com/news/home/20210310005156/en
- Vigo, Brown & Conway, "Benchmarking web accessibility evaluation tools: measuring the harm of sole reliance on automated tests", W4A 2013: https://dl.acm.org/doi/10.1145/2461121.2461124
- WebAIM Million 2026: https://webaim.org/projects/million/
- W3C ACT 구현 보고서(axe-core, Alfa, QualWeb, Equal Access): https://www.w3.org/WAI/standards-guidelines/act/implementations/
- Chiou, Winn, Alotaibi & Halfond, "Automatically Detecting Reflow Accessibility Issues in Responsive Web Pages", ICSE 2024: https://doi.org/10.1145/3597503.3639229
- Chiou, Alotaibi & Halfond, "Detecting and localizing keyboard accessibility failures in web applications" (KAFE), ESEC/FSE 2021: https://dx.doi.org/10.1145/3468264.3468581 ; 대화상자 키보드 실패, ICSE 2023: https://dl.acm.org/doi/abs/10.1109/ICSE48619.2023.00120
- Flow-A11y (2026): https://arxiv.org/abs/2607.03100 ; A11yLTLNav (2026): https://arxiv.org/pdf/2609.17959
- Althomali, Kapfhammer & McMinn, "Automatic visual verification of layout failures in responsively designed web pages", ICST 2019: https://www.gregorykapfhammer.com/research/papers/althomali2019/
- Salehnamadi, Mehralian & Malek, Groundhog, ASE 2022: https://dl.acm.org/doi/10.1145/3551349.3556905 ; TaskAudit (Groundhog 재평가): https://arxiv.org/html/2510.12972v1
- ScreenAudit, CHI 2025: https://doi.org/10.1145/3706598.3713797
- Adrian Roselli, "Honoring Mobile OS Text Size" (2026-02): http://adrianroselli.com/2026/02/honoring-mobile-os-text-size.html

### 1.5 읽은 저장소 맥락 (수정하지 않음)

`references/ergonomics/workflow.md`, `human-factors-checks.md`(SM-01~SM-06, LY-01 표), `persona-agent-protocol.md`, `validation-and-limits.md`, `docs/ergonomic-swarm-spec.md` §3·§5·§7·§12.1, `docs/validation/experiments/decisions.md`, `heldout-2-preregistration.md`(수정 1 포함), 기존 브리프 4개(UEM-, STF-, AP-, LAT- 후보), `drivers/web/page_scripts.mjs`(`accNameSrc`, `clippedOf`), `drivers/web/session.mjs`(`focusInfo`, `focusWalk`), `ergoqa/checks.py`(`check_semantics`, `check_focus_walks`).

**중요한 현황 차이.** 작업 지시문은 "semantics/layout 검사가 없다"고 적었지만, 저장소에는 이미 SM-01~SM-04와 LY-01(heldout-2 사전등록 수정 1), SM-05·SM-06(그 뒤 커밋 `962374f`, `50e05f7`)이 있습니다. 이 브리프는 새 검사를 제안하는 것과 함께 **이미 들어간 검사를 원문 기준으로 다시 검증**합니다. heldout-2는 아직 동결 전이고 기록되지 않았으므로, 동결 전에 바꿀 것과 동결 뒤 dev-2에서만 실험할 것을 3절에서 나눕니다.

## 2. Key knowledge (핵심 지식)

### 2.1 규칙 엔진과 규칙 집합

**axe-core (Deque, MPL-2.0).**

- README 원문: "With axe-core, you can find on average 57% of WCAG issues automatically. Additionally, axe-core will return elements as 'incomplete' where axe-core could not be certain, and manual review is needed." [industry]
- 설계 원칙(manifesto): "It returns zero false positives (bugs notwithstanding)." [industry] 즉 `violations`는 정밀도를 우선하고, 확신이 없는 경우는 `incomplete`(needs review)로 넘깁니다.
- 4.13 규칙 목록: 모두 105개입니다. WCAG 2.0 A/AA 60개, WCAG 2.1 A/AA 2개(`autocomplete-valid`, `avoid-inline-spacing`), WCAG 2.2 A/AA 1개(`target-size`), best practice 27개, AAA 3개, experimental 7개, deprecated 5개입니다. 56개가 ACT 규칙에 대응합니다. Issue Type은 failure만 42개, failure + needs review 52개, needs review만 11개입니다. [derived: `rule-descriptions.md` 표를 셈]
- 이 스킬과 겹치거나 인접한 규칙:
  - `button-name`(Critical), `link-name`(Serious), `label`(Critical), `select-name`, `input-button-name`, `aria-command-name`, `aria-input-field-name`, `aria-toggle-field-name`: 모두 4.1.2
  - `label-content-name-mismatch`: 2.5.3, **experimental**이라 기본으로 꺼져 있음 (axe 소스의 기본값 `tagExclude = ["experimental", "deprecated"]`)
  - `meta-viewport`: 1.4.4, Moderate, ACT b4f0c3
  - `avoid-inline-spacing`: 1.4.12, ACT 24afc2·9e45ec·78fd32
  - `target-size`: 2.5.8, "failure, needs review"
  - `scrollable-region-focusable`: 2.1.1·2.1.3
  - `aria-hidden-focus`, `nested-interactive`: 4.1.2
  - `tabindex`(양수 tabindex, best practice), `focus-order-semantics`(experimental)
  - `image-alt`, `role-img-alt`, `svg-img-alt`, `input-image-alt`, `area-alt`: 1.1.1
  - `document-title`, `html-has-lang`, `html-lang-valid`, `list`, `listitem`, `td-headers-attr`, `th-has-data-cells`, `duplicate-id-aria`, `aria-valid-attr-value`, `aria-required-attr` 등
  [industry]
- **axe-core에 없는 것:** 4.13 목록의 어떤 규칙도 ACT 59br37(200 % 확대 시 잘린 글자), oj04fd(보이는 초점), 36b590(오류 메시지가 잘못된 값을 설명)에 대응하지 않습니다. 2.4.11(초점 가림)과 1.4.10(리플로) 규칙도 없습니다. [derived: 규칙 표에서 ACT ID 검색] 이 스킬이 드라이버로 직접 측정해야 하는 영역이 바로 이것입니다.

**Lighthouse (Google).**

- 접근성 점수는 감사 항목의 가중 평균입니다 (`docs/scoring.md`). [industry]
- `default-config.js`(main)의 접근성 범주에는 가중치가 있는 감사 66개(가중치 10이 18개, 7이 31개, 3이 5개, 1이 4개, 0이 8개)와 가중치 0인 **수동** 감사 10개가 있습니다. [derived]
- 수동 감사 10개: `focusable-controls`, `interactive-element-affordance`, `logical-tab-order`, `visual-order-follows-dom`, `focus-traps`, `managed-focus`, `use-landmarks`, `offscreen-content-hidden`, `custom-controls-labels`, `custom-controls-roles`. 초점 순서, 초점 관리, 키보드 함정은 Lighthouse가 자동으로 판정하지 않는다는 뜻입니다.
- 주요 가중치: `button-name`·`image-alt`·`label`·`meta-viewport` 10, `link-name`·`color-contrast`·`target-size`·`tabindex`·`document-title` 7, `heading-order` 3, `label-content-name-mismatch` 0(숨김). [derived]
- 범주 설명 원문: "Automatic detection can only detect a subset of issues and does not guarantee the accessibility of your web app, so manual testing is also encouraged." [industry]

**Android Accessibility Test Framework (ATF, Google).**

- 검사 클래스 14개: `ClassNameCheck`, `ClickableSpanCheck`, `DuplicateClickableBoundsCheck`, `DuplicateSpeakableTextCheck`, `EditableContentDescCheck`, `ImageContrastCheck`, `LinkPurposeUnclearCheck`, `RedundantDescriptionCheck`, `SpeakableTextPresentCheck`, `TextContrastCheck`, `TextSizeCheck`, `TouchTargetSizeCheck`, `TraversalOrderCheck`, `UnexposedTextCheck`. [industry: 소스 디렉터리]
- `TouchTargetSizeCheck`: 기본 48 × 48 dp, 화면 가장자리나 IME 안에서는 32 × 32 dp. `TouchDelegate`, 클릭 가능한 조상, 스크롤 가장자리(이 경우 `NOT_RUN`), 조상에 의한 잘림을 고려합니다. [industry: 소스 상수와 주석]
- `TextContrastCheck`: `CONTRAST_TOLERANCE = 0.01`. 계산 대비가 기준보다 0.01까지 낮아도 통과시키는 보호 대역입니다. STF-15의 guard band와 같은 발상입니다. [industry]
- `TextSizeCheck`는 정적 휴리스틱입니다. sp가 아닌 단위, 그리고 고정 크기 뷰나 컨테이너 안의 sp 글자를 찾습니다. 소스 주석 원문: "This check is not perfect and can produce false positive (FP) results." [industry] 글자를 실제로 키워 보는 동적 검사가 정밀도에서 유리하다는 근거입니다 (2.3의 1.4.4).
- 나머지 검사의 소스 주석 [industry]:
  - `SpeakableTextPresentCheck`: "Does not check if the text makes sense."
  - `DuplicateClickableBoundsCheck`: 자식과 경계가 같은 클릭 가능 컨테이너.
  - `TraversalOrderCheck`: 개발자가 지정한 탐색 순서(traversalBefore/After)의 오류.
  - `UnexposedTextCheck`: OCR로 찾은 글자가 접근성 서비스에 노출되지 않음 (개발 중).
  - `ClickableSpanCheck`: Android O 이전 기기에서 `ClickableSpan` 사용. 상대 URI가 없는 `URLSpan`은 예외.
  - `RedundantDescriptionCheck`: 읽을 글자에 뷰 유형("button"), 상태("checked"), 동작이 중복으로 들어감. 스크린리더가 이미 알려 주기 때문입니다.
  - `LinkPurposeUnclearCheck`: 목적이 불분명한 링크.
  - `DuplicateSpeakableTextCheck`: 읽을 글자가 같은 뷰가 둘 있고 그중 하나 이상이 클릭 가능하면 경고.

**Apple XCTest `performAccessibilityAudit`.**

- `XCUIAccessibilityAuditType`: `action`, `all`, `contrast`, `dynamicType`, `elementDetection`, `hitRegion`, `parentChild`, `sufficientElementDescription`, `textClipped`, `trait`. 문서 메타데이터 기준 iOS 17.0, macOS 14.0부터입니다. 유형별 설명문은 공식 문서에 비어 있습니다. [industry]
- WWDC23 세션 10035 원문:
  - 감사 결과를 걸러 내는 클로저에 대해 "Perhaps the issue is a false positive or expected behavior. Accessibility audits makes it easy to ignore these kinds of issues."
  - "audits shouldn't substitute real testing with assistive technologies."
  - 데모에서 나온 이슈는 "Element has no description"과 "The label is not human-readable"(레이블이 `QUOTE_TEXTVIEW`)이었습니다.
  [industry]
- 스킬에 주는 시사점: 벤더도 오탐을 무시하는 경로를 API로 둡니다. 그리고 "사람이 읽을 수 없는 이름"(개발자 식별자)은 결정적으로 잡을 수 있는 이름 품질 결함입니다 (AUT-14).

**W3C ACT Rules.**

- 규칙은 적용 대상(Applicability), 기대(Expectation), 가정(Assumptions), 보조기술 지원(Accessibility Support), 그리고 사람이 쓴 예제(passed / failed / inapplicable)로 이루어집니다. [standard: ACT 규칙 원본]
- 구현이 맞는지는 예제로 판정합니다 (ACT CG "Mapping To Rule"):

  | 예제 유형 | 허용되는 결과 |
  | --- | --- |
  | Passed | `passed`, `cantTell`, `inapplicable` |
  | Failed | `failed`, `cantTell` |
  | Inapplicable | `inapplicable`, `cantTell`, `passed` |

  모든 예제에서 허용 결과를 내면 *correct implementation*입니다. passed·inapplicable은 모두 맞고 failed 일부만 잡으면 *partial implementation*입니다. [standard: W3C 커뮤니티 그룹 문서이며 W3C 권고안은 아님] 곧 **통과 예제를 하나라도 실패로 판정하면 일관된 구현이 아닙니다.** ACT의 판정 기준은 사실상 "예제에서 오탐 0"이라는 정밀도 계약입니다.
- 구현 보고서 수치 [snippet]:

  | 도구 (버전) | consistent WCAG 2 규칙 | consistent proposed 규칙 | partially consistent |
  | --- | --- | --- | --- |
  | axe-core 4.10.2 | 26 | 3 | WCAG 2 1개, proposed 11개 |
  | Alfa 0.108.2 | 29 | 4 | – |
  | QualWeb 3.0.0 | 29 | 7 | – |
  | Equal Access 3.1.42-rc.0 | 21 | 3 | – |

**WCAG-EM (평가 방법론).**

- 2.0 초안은 1.0을 바탕으로 합니다. [standard, draft]
- Step 3.2: 무작위 표본은 "**10% of the structured sample set**"입니다.
- Step 3.3: 완결된 프로세스(complete processes)를 포함합니다.
- Step 4.3: 무작위 표본에서 구조적 표본에 없던 *유형*의 콘텐츠나 결과가 나오면 안 됩니다. 나오면 구조적 표본이 대표성이 없다는 뜻입니다.
- Step 3의 고려 사항: "smaller sample sets may be required when evaluators have access to prior evaluation findings, including test results from manual and automated accessibility testing."
- 스킬에 대응시키면: 시나리오 실행은 "완결된 프로세스"이고, 페르소나 에이전트가 도달한 추가 화면은 "무작위 표본"의 역할을 할 수 있습니다 (AUT-17).

**KWCAG 2.2 (KS X OT0003:2022, 한국형 웹 콘텐츠 접근성 지침).**

- 검사항목은 33개입니다. 이 주제와 관련된 항목은 다음과 같습니다. [standard: a11ykr 공개본]
  - 5.4.3 텍스트 콘텐츠의 명도 대비: 4.5:1. 18pt 이상이나 14pt 굵은 글꼴은 3:1. "화면 확대가 가능한 콘텐츠"도 3:1까지 허용하는데, 이는 WCAG에 없는 예외입니다.
  - 6.1.2 초점 이동과 표시: "키보드에 의한 초점은 논리적으로 이동해야 하며, 시각적으로 구별할 수 있어야 한다." WCAG 2.4.3과 2.4.7을 한 항목에 묶었습니다.
  - 6.1.3 조작 가능: 대각선 길이 6.0 mm 이상을 권장("바람직하다")하고, 테두리 안쪽 1픽셀 여백을 권장합니다.
  - 6.5.3 레이블과 네임: WCAG 2.5.3에 해당합니다.
  - 7.3.1 오류 정정, 7.3.2 레이블 제공
- **KWCAG 2.2에는 WCAG 1.4.4(글자 크기 조절), 1.4.10(리플로), 1.4.12(글자 간격), 2.4.11(초점 가림)에 해당하는 검사항목이 없습니다.** [derived: 33개 항목 목록 대조] 따라서 한국 제품에서 이 검사들은 "품질인증 항목"이 아니라 "WCAG 2.2 AA 및 저시력 사용자 영향"으로 보고해야 합니다 (AUT-16).

### 2.2 커버리지, 오탐, 미탐에 관해 공개된 수치

**"자동 검사는 얼마나 찾는가"는 무엇을 세느냐에 따라 13 %에서 57 %까지 갈립니다.**

| 출처 | 분모 | 수치 | 태그 |
| --- | --- | --- | --- |
| Deque (2021) | 첫 감사 2,000건 이상, 13,000쪽 이상, 이슈 약 300,000건의 **이슈 건수** | axe로 57 %. 업계 통념은 20–30 %. Deque는 성공 기준 개수가 아니라 이슈 건수로 커버리지를 정의했습니다. | [snippet] |
| GOV.UK 도구 감사 (2018-04-13 갱신) | 일부러 넣은 **장벽 142개**, 도구 13개 | 온전히 탐지한 비율: 최고 40 %(SortSite), 최저 13 %(Nu Html Checker), aXe 29 %, Google ADT 17 %. 사람 확인 요청까지 넣으면 최고 50 %(FAE) | [industry] |
| 같은 감사 `tests.json` 재집계 | 장벽 142개 | 한 도구라도 오류·경고로 잡은 장벽 102개(72 %), 수동 확인 요청까지 124개(87 %), 어떤 도구도 표시하지 않은 장벽 18개 | [derived] |
| 같은 자료, 키보드·초점·확대·레이아웃·CSS 장벽 24개 | 24개 | 한 도구라도 8개. axe 1, Google ADT 1, WAVE 2, SortSite 2, Tenon 2, HTML_CodeSniffer 0 | [derived] |
| Vigo, Brown & Conway (W4A 2013) | 도구 6개, WCAG 2.0 | 성공 기준 커버리지 최대 50 %, 완전성(completeness) 14–38 %, 정확성(correctness)은 대체로 93 % 초과. 다만 완전성이 높은 도구는 66–71 %로 낮았습니다 (더 많이 잡으려다 오탐이 늘어남). | [snippet] |
| WebAIM Million 2026 | 홈페이지 100만 개, WAVE | 95.9 %가 자동 검출 가능한 WCAG 실패를 가짐(2025년 94.8 %). 쪽당 오류 56.1개(2025년 51개). 오류의 96 %가 여섯 범주: 낮은 대비 83.9 %, 대체 텍스트 없음 53.1 %, 입력 레이블 없음 51 %, 빈 링크 46.3 %, 빈 버튼 30.6 %, 문서 언어 없음 13.5 %. 낮은 대비는 쪽당 평균 34건 | [snippet] |

**GOV.UK 감사에서 13개 도구 중 어느 것도 잡지 못한 장벽.** 이 가운데 상당수가 이 스킬의 드라이버가 측정할 수 있는 것입니다. [derived: `tests.json`]

- "Focus not visible"
- "Focus order in wrong order"
- "Keyboard trap"
- "Wide page forces users to scroll horizontally"
- "Page zoom - boxes that don't expand with the text"
- "Inadequate line height used"
- "Error messages - no suggestion for corrections given"
- "Alert shows for a short time"
- 라이트박스 초점 문제 3개: 초점 이동 없음, 초점 유지 안 됨, ESC로 닫히지 않음

"Errors are not identified"는 1/13, "Keyboard focus is not indicated visually"는 3/13(axe는 못 잡음)이었습니다.

**정적 규칙 엔진의 오탐은 0이 아닙니다.**

- axe-core 이슈 가운데 제목에 "false positive"가 들어간 이슈가 적어도 11건입니다. [industry: GitHub 검색]
  - `scrollable-region-focusable` 여러 건
  - `aria-required-parent`
  - `label-content-name-mismatch`: "CJK / full-width punctuation is not removed". 한국어 UI에 직접 걸리는 문제입니다.
  - `p-as-heading`
  - `target-size`: 덮여 있는 input을 건너뛰지 않음
  - `link-in-text-block`
  - `color-contrast`: OKLCH 색
  - shadow DOM 목록
- 오탐은 휴리스틱 규칙(스크롤 영역, 구조, 실험 규칙)에 몰리고, 이름 규칙에는 드뭅니다. 2.4절 파일럿에서도 이름 규칙 오탐은 0이었습니다.

**모바일 스캐너와 상호작용 기반 도구** [snippet]:

- Groundhog(ASE 2022)는 보조기술로 앱을 조작하며 이슈를 찾습니다. Google Accessibility Scanner(ATF)와는 "no intersection between the type of issues each … detects"입니다.
- TaskAudit(2025)의 재평가에서 Groundhog는 기능 오류를 recall 25.6 %, precision 14.2 %로 찾았습니다. Locatability 표시의 73 %, Actionability 표시의 96 %가 오탐이었습니다.
- ScreenAudit(CHI 2025, LLM 기반)은 14개 화면에서 스크린리더 오류 커버리지 69.2 %를 보였고, 널리 쓰이는 검사기는 31.3 %였습니다 (전문가 6명 평가).
- 결론: 상호작용·판단 기반 탐지는 더 많이 찾지만 정밀도가 크게 떨어질 수 있습니다. 이 스킬이 에이전트 판단을 가설 등급에 두는 규칙(LAT-16, UEM-11)과 같은 방향입니다.

**한국어 사례 확인** (axe 4.13.0과 Chromium 1194, 직접 실행) [derived]:

- `<input placeholder="이름">`: axe 위반 없음, Chromium 이름 "이름"
- `title`만 있는 칸: axe `label-title-only`(best practice)
- `<button><span aria-hidden="true">×</span></button>`: axe `button-name` 위반, Chromium 이름 "". 현재 `accNameSrc`는 `innerText`로 "×"를 이름으로 잡으므로 SM-01이 **놓칩니다**.
- 보이는 글자 "장바구니 담기"와 이름 "상품을 장바구니에 담기": axe `label-content-name-mismatch`가 위반으로 판정합니다 (2.3(b)의 한국어 위험).

**레이아웃 실패 탐지의 오탐.**

- VISER README: 반응형 레이아웃 실패(요소 겹침, 컨테이너 넘침, 뷰포트 넘침)를 "visually observable / non-observable"로 분류하는 도구입니다. DOM 기하만으로 찾은 실패에는 **보이지 않는 실패**가 섞인다는 전제에서 출발합니다. [industry]
- 초록 발췌: ReDeCheck가 20쪽에서 보고한 117건을 VISER가 모두 자동 분류했고, 28건을 수동 분석과 다르게 분류했으며, 그중 3건은 오탐으로 올바르게 재분류했습니다. [snippet]
- 결론: 기하 기반 겹침·넘침 검사에는 **픽셀 확인 단계**가 필요합니다 (AUT-06, AUT-07).

**드라이버 기반 탐지 연구** [snippet, 수치는 확보하지 못함]:

- 키보드 접근성 실패 탐지 KAFE(FSE 2021): "high precision and recall"
- 대화상자 관련 키보드 탐색 실패(ICSE 2023)
- 반응형 리플로 접근성 이슈 자동 탐지(ICSE 2024): "among the most prevalent modern web accessibility issues"
- Flow-A11y(2026): 페이지 단위 스캐너는 대화상자 열림 시 초점 이동, 초점 가두기, 닫힘 시 초점 복귀를 검증할 수 없습니다. 시나리오를 실제 브라우저에서 실행하고 기준별 증거 묶음을 만듭니다.
- 이 스킬은 이미 실제 흐름을 실행하므로 같은 증거를 공짜에 가깝게 얻을 수 있습니다 (AUT-11).

### 2.3 Playwright 드라이버에서 결정적으로 검사할 수 있는 성공 기준과 알고리즘

아래 "필요한 데이터"는 드라이버가 이미 읽는 것(DOM, 계산된 스타일, 경계 상자, 스크린샷, 타이밍)과 새로 읽어야 하는 것(CDP 접근성 트리)을 구분합니다.

**(a) 4.1.2 Name, Role, Value: 접근 가능한 이름 계산.**

- 규범: "the name and role can be programmatically determined; states, properties, and values that can be set by the user can be programmatically set; and notification of changes to these items is available to user agents". [standard]
- accname 1.2의 계산 순서:
  1. Hidden Not Referenced: 숨은 노드라도 `aria-labelledby`로 직접 참조되면 포함
  2. LabelledBy
  3. Embedded Control: 레이블 안의 입력 칸은 그 값을 이름에 넣음
  4. AriaLabel
  5. Host Language Label: `label`, `alt`, SVG `title`. presentational이면 제외
  6. Name From Content: 이름을 내용에서 얻는 역할이나 참조된 노드일 때. CSS `::before`, `::after`, `::marker` 생성 글자와 shadow root·slot 자식을 포함
  7. Text Node
  8. Tooltip (`title`): "used only if nothing else, including subtree content, has provided results"
  [standard]
- 이 스킬의 `accNameSrc`는 이 순서를 단순화했습니다 (2.7). 구현 선택지는 넷입니다.
  1. **브라우저가 계산한 트리:** CDP `Accessibility.getFullAXTree`(experimental 도메인)
     - 노드마다 `role`, `name`, 이름 출처 `sources`를 줍니다. 출처 유형은 attribute, implicit, style, contents, placeholder, relatedElement이고, native 출처는 label, labelfor, labelwrapped, legend, figcaption, title, tablecaption 등입니다.
     - `ignored`와 그 사유(ariaHiddenElement, inertElement, notRendered, presentationalRole 등)를 줍니다.
     - 속성(focusable, focused, invalid, required, describedby, errormessage, labelledby, checked, expanded, pressed, modal 등)을 줍니다.
     - DOM 노드와는 `backendDOMNodeId`로 연결합니다.
     [industry: 프로토콜 정의]
  2. Playwright `locator.ariaSnapshot()`: 역할과 이름을 YAML로 줍니다. 편하지만 요소별 기하와 잇기 어렵습니다. [industry]
  3. axe-core 규칙 안의 이름 계산.
  4. 자체 JS(현재 방식).
- ACT 적용 범위: 이름 규칙(97a4e1 버튼, e086e5 입력 칸, c487ae 링크)은 **접근성 트리에 포함된** 요소에 적용하며, 화면에 보이는지를 따지지 않습니다. e086e5는 비활성 입력 칸에도 적용합니다 ("Several assistive technologies have a functionality to list all form fields on a page, including the `disabled` ones"). [standard: ACT CG]
- 정밀한 판정: 무시되지 않은(ignored가 아닌) AX 노드 가운데, 위젯 역할이거나 focusable인 노드의 이름이 공백을 제거하고 비어 있으면 실패입니다. 위젯 역할은 button, link, menuitem, tab, checkbox, radio, switch, textbox, searchbox, combobox, listbox, slider, spinbutton, treeitem입니다. 필요한 데이터: CDP AX 트리 + 기존 요소 상자.

**(b) 2.5.3 Label in Name.**

- 적용 대상: 이름을 내용에서 얻는 위젯 역할(button, checkbox, gridcell, link, menuitem, menuitemcheckbox, menuitemradio, option, radio, switch, tab, treeitem 등) 가운데 보이는 글자가 있고 `aria-label`/`aria-labelledby`를 가진 요소입니다. 약어나 철자 차이가 있으면 제외합니다. [standard: ACT 2ee8b8]
- 레이블 포함 판정 알고리즘:
  1. 괄호와 그 안의 글자를 지웁니다.
  2. 대소문자를 접고(case folding) NFKD로 정규화합니다.
  3. 글자(L)와 숫자(N)가 아닌 문자를 공백으로 바꿉니다.
  4. 그 언어의 단어 분리 규칙으로 나눕니다.
  5. 보이는 레이블의 토큰 목록이 이름 토큰 목록의 **연속 부분열**인지 봅니다.
  "보이는 내부 글자(visible inner text)"는 `innerText`와 다릅니다. 시각적으로 숨긴 글자는 빠집니다. [standard: ACT 용어 정의]
- 가정: 괄호 안은 무시해도 된다. 원문: "This assumption is almost always true in English… known to be often false in languages other than English". [standard]
- **한국어 위험** [derived]: 한국어는 조사가 붙은 어절 단위로 띄어 씁니다. 보이는 글자 "장바구니 담기"와 이름 "상품을 장바구니에 담기"는 토큰 "장바구니" ≠ "장바구니에"라서 ACT 알고리즘으로는 "포함되지 않음"입니다. 음성 제어가 실제로 실패하는지는 확인하지 못했습니다 (4절).

**(c) 1.3.1·3.3.2 레이블.**

- Chromium은 `label`이 없는 입력 칸에서 `title`이나 `placeholder`를 이름으로 씁니다. CDP 이름 출처 유형에도 `placeholder`가 있습니다 (`AXValueSourceType`). [industry: 프로토콜 정의와 직접 실행] HTML-AAM 원문의 순서는 이번에 확인하지 못했습니다.
- 따라서 placeholder만 있는 칸은 ACT e086e5를 **통과**합니다 ("non-empty accessible name"). 이는 레이블 품질 문제(axe `label-title-only` best practice)이지 WCAG 이름 실패가 아닙니다. [derived]
- 현재 SM-03은 placeholder·title만 있는 칸을 경로 위에서 P2로 올리므로, WCAG 실패로 읽히지 않게 이름을 붙여야 합니다 (AUT-03).

**(d) 3.3.1·3.3.3 오류 식별과 제안.**

- ACT 36b590의 세 기대 [standard: ACT CG]:
  1. 오류 표시(텍스트, 비텍스트, 표현)가 어느 칸의 오류인지 식별하게 해 준다.
  2. 원인이나 고치는 법을 **보이는** 텍스트로 설명한다.
  3. 그 텍스트가 접근성 트리에 있거나 그 칸의 이름·설명에 들어 있다.
- 드라이버가 읽을 수 있는 신호: `aria-invalid="true"`, `aria-errormessage`(`aria-invalid`가 참일 때만 유효), `aria-describedby`, `:user-invalid`, `role=alert`·라이브 영역. SM-04가 이미 `invalid`, `user_invalid`, `described_by`, `error_message`를 기록합니다.
- 3.3.3(제안)을 결정적으로 판정할 방법은 좁습니다. GOV.UK 감사의 "no suggestion for corrections" 장벽은 13개 도구 모두 못 잡았습니다 [derived]. 에이전트 판단(`error_unclear`)에 맡깁니다.

**(e) 2.4.3 초점 순서.**

- Understanding 원문: "Since there may be several possible logical reading orders for the content, the focus order may match any of them." [standard] 시각 순서와 DOM 순서의 불일치만으로는 실패를 판정할 수 없습니다. Lighthouse도 `logical-tab-order`, `visual-order-follows-dom`을 수동 감사로 둡니다. [derived]
- 드라이버가 정밀하게 잡을 수 있는 하위 실패:
  - 양수 `tabindex` (axe `tabindex`)
  - `aria-hidden` 안의 초점 가능 요소 (axe `aria-hidden-focus`)
  - 동작 뒤 초점이 `body`로 사라짐
  - 모달이 열렸는데 초점이 안으로 들어가지 않음
  - Tab이 모달 밖으로 빠져나감
  - 모달이 닫힌 뒤 초점이 트리거로 돌아오지 않음
  - 크기 0이거나 투명하거나 화면 밖에 있는 요소에 초점이 멈춤
  GOV.UK 감사의 라이트박스 초점 장벽 세 개는 13개 도구 중 0–1개만 잡았습니다. [derived] 필요한 데이터: 단계마다 `document.activeElement`, `dialog[open]`·`[aria-modal=true]`, 초점 걷기 결과(이미 있음).

**(f) 2.4.7 보이는 초점과 2.4.13 초점 모양.**

- ACT oj04fd의 기대: "there is at least one device pixel inside the scrolling area of the viewport whose HSL color value is different when the element is focused from when it is not." [standard: ACT CG]
- 같은 규칙의 배경 설명: 2.4.7에는 크기나 거리 요구가 없으므로 "barely perceptible changes at the other end of the page"도 통과합니다. [standard]
- 2.4.13(AAA) 원문: 초점 표시 영역이 "at least as large as the area of a 2 CSS pixel thick perimeter of the unfocused component"이고, "a contrast ratio of at least 3:1 between the same pixels in the focused and unfocused states"여야 합니다. [standard]
- 결론: **2.4.7 실패로 셀 수 있는 것은 "뷰포트 어디에도 변화가 없다"뿐입니다.** 요소 주변의 작은 변화는 2.4.13 성격의 약한 표시로 따로 다뤄야 합니다. 현재 SM-05는 요소 상자 + 4 px 안에서 24/255 이상 바뀐 픽셀이 4개 미만이면 실패로 봅니다. 표시가 요소 옆에 따로 그려지면 오탐이 납니다 (2.4절 파일럿).

**(g) 2.4.11·2.4.12 초점이 가려지지 않음.**

- 2.4.11 원문: "the component is not entirely hidden due to author-created content".
- 주석 두 개:
  - "Content opened by the user may obscure the component receiving focus."
  - "If the user can reveal the focused component without advancing the keyboard focus, the component with focus is not considered visually hidden."
- Understanding: 초점을 완전히 가리는 쿠키 배너는 실패입니다. 배너를 모달로 만들거나 `scroll-padding`을 쓰면 통과합니다. 사용자 조치가 필요 없는 알림은 초점을 잃을 때 닫히면 됩니다.
[standard]
- 현재 SM-06은 fixed·sticky 층이 9개 표본점을 모두 덮으면 P2, 일부만 덮으면 P3(2.4.12, AAA)로 봅니다. 사용자가 연 층과, 초점을 옮기지 않고 닫을 수 있는 층(Esc)을 빼지 않습니다 (AUT-13).

**(h) 1.4.10 리플로.**

- 규범: 세로 스크롤 콘텐츠는 폭 320 CSS px, 가로 스크롤 콘텐츠는 높이 256 CSS px에서 두 방향 스크롤 없이 정보와 기능을 잃지 않아야 합니다. 두 방향 배치가 필요한 부분(지도, 도표, 비디오, 게임, 프레젠테이션, 데이터 표, 조작 중 계속 보여야 하는 도구 모음)은 예외입니다. "320 CSS pixels is equivalent to a starting viewport width of 1280 CSS pixels wide at 400% zoom." [standard]
- Understanding [standard]:
  - "Neither adjusting or relocating content is considered a loss of information or functionality, so long as users are still able to access the content."
  - 줄여 보여 주더라도 전체를 볼 방법이 있으면 괜찮습니다.
  - 확대하면 고정·sticky 콘텐츠가 초점을 가리기 쉽습니다.
- 알고리즘 (AUT-06):
  - 폭 320 CSS px, 높이 256 CSS px, DPR 4로 에뮬레이트합니다 (데스크톱 1280 × 1024의 400 %).
  - RF-01: `document.scrollingElement.scrollWidth > clientWidth + 1`이면 오른쪽 끝이 뷰포트를 넘는 요소를 찾습니다. 예외 요소(`table`, `canvas`, `video`, `iframe`, `svg`, `pre`, 지도 역할), 그리고 자체 `overflow-x:auto|scroll` 컨테이너 안에 있는 요소는 제외합니다.
  - RF-02: 글자 잘림은 (l)의 ACT 방식으로 판정합니다.
  - RF-03: 인터랙티브 요소가 문서 스크롤 영역 밖에 있거나, fixed·sticky 층에 완전히 덮여 도달할 수 없음.
  - 겹침 후보는 VISER처럼 픽셀로 확인합니다. 겹친 상자 영역이 두 상태(겹침 해소 전후)에서 실제로 다르게 그려질 때만 셉니다.
  - 필요한 데이터: 추가 스냅숏 1장, 계산된 스타일, 경계 상자, 스크린샷.

**(i) 1.4.4 글자 크기 조절.**

- 규범: 캡션과 글자 이미지를 빼고 "text can be resized without assistive technology up to 200 percent without loss of content or functionality". [standard]
- Understanding: "Content satisfies the success criterion if it can be scaled up to 200% using at least one text scaling mechanism supported by user agents." [standard] 한 가지 메커니즘만 되면 됩니다.
- ACT 59br37 [standard: ACT CG]:
  - 640 × 512 뷰포트(1280 × 1024의 200 %)에서, `overflow: hidden|clip` 조상이 있는 보이는 텍스트 노드가 가로·세로로 잘리면 실패입니다.
  - 예외: 가로는 조상이 `white-space: nowrap`이고 `text-overflow`가 `clip`이 아니면(말줄임) 통과합니다. 세로는 조상의 line-height가 상자 높이 이상이면(한 줄 고정) 통과합니다.
  - 가정: 다른 크기 조절 수단이 있으면 실패가 SC 실패는 아닙니다.
- ACT b4f0c3(메타 뷰포트): `user-scalable=no`나 `maximum-scale` < 2는 실패입니다. 그러나 보조기술 지원 절 원문: "Desktop browsers ignore the viewport `meta` element, and most modern mobile browsers either ignore it by default or have an accessibility option which will allow zooming … Only users with older mobile browsers can experience issues tested by this rule." [standard: ACT CG] 확실하게 잡히지만 실제 영향은 제한적이므로 심각도는 낮게 둡니다 (AUT-08).
- 모바일 OS 글자 크기 (Roselli 2026) [industry·opinion]:
  - Android Firefox는 OS 글자 크기에 맞춰 웹 글자를 키웁니다.
  - Android Chrome은 OS 설정을 자동으로 따르지 않고 브라우저 안 설정을 써야 합니다.
  - Safari는 작성자가 `-apple-system-body` 같은 CSS를 쓰지 않으면 키우지 않습니다.
  - 앱 안 WebView는 "text inflation"으로 글자만 키우고 여백과 간격은 그대로 둡니다.
  따라서 모바일 프로필의 글자 확대는 "요소별 글자 크기 × s, 간격은 그대로"로 에뮬레이트하는 것이 WebView 동작에 가깝습니다. [derived]
- 정적 휴리스틱(ATF `TextSizeCheck`)은 오탐을 스스로 경고합니다. XCTest `dynamicType`은 실행 중에 검사합니다. [industry] 동적 방식이 낫습니다.

**(j) 1.4.12 글자 간격.**

- 규범 값 [standard]:
  - 줄 높이 ≥ 글자 크기의 1.5배
  - 문단 뒤 간격 ≥ 2배
  - 자간 ≥ 0.12배
  - 단어 간격 ≥ 0.16배
  이 속성을 쓰지 않는 언어·문자는 해당 속성만 빼고 적용합니다. Understanding에 따르면 일본어는 문단 뒤 간격을 쓰지 않습니다. 한국어는 띄어쓰기와 자간을 쓰므로 네 값이 모두 적용된다고 봅니다. [derived]
- Understanding: 글자가 겹치면 실패입니다. 말줄임표가 생겨도 전체 글자에 접근할 방법이 있으면 통과입니다. [standard]
- 정적 ACT 규칙(24afc2·78fd32·9e45ec)은 `style` 속성에 `!important`로 박힌 값이 기준보다 작은지만 봅니다. 사용자 스타일시트가 이길 수 없기 때문입니다. axe `avoid-inline-spacing`이 이를 구현합니다. [standard/industry]
- 동적 시험은 네 값을 주입한 뒤 잘림·겹침을 비교하는 방식입니다 (AUT-19). GOV.UK 감사의 "Inadequate line height used"는 13개 도구 모두 못 잡았습니다. [derived]

**(k) 2.5.8 대상 크기(최소).**

- 규범 [standard]: 24 × 24 CSS px 이상이어야 합니다. 예외는 다섯 가지입니다.
  - Spacing: "a 24 CSS pixel diameter circle is centered on the bounding box of each, the circles do not intersect another target or the circle for another undersized target"
  - Equivalent
  - Inline
  - User Agent Control
  - Essential
- 이 스킬의 PT-01이 이미 레이블까지 넓힌 대상과 원 예외를 구현합니다. axe `target-size`는 "failure, needs review"이고, "덮인 input을 건너뛰지 않는" 오탐 이슈가 있습니다. [industry] 새로 구현하지 않습니다 (AUT-18).

**(l) 글자 잘림과 말줄임.**

- ACT 용어집 정의(`pages/glossary/horizontally-clipped-by-overflow.md`, `vertically-clipped-by-overflow.md`): 노드의 flat-tree 조상 가운데 계산된 `overflow-x`(또는 `overflow-y`)가 `hidden|clip`인 것들을 모두 `visible`로 바꾸면 노드가 더 많이 보이게 되는 경우를 "Horizontally (Vertically) Clipped by Overflow"라고 합니다. [standard: ACT CG]
- 현재 LY-01은 **자기 상자**의 `scrollWidth > clientWidth + 1`만 봅니다. 조상에 잘리는 경우를 놓치고, ACT가 통과시키는 말줄임과 한 줄 고정을 잡습니다 (2.4절).
- XCTest에는 `textClipped` 감사 유형이 있습니다. [industry]
- "전체 내용에 접근할 수 있는지"(1.4.10·1.4.12의 Understanding)는 결정적으로 일부만 확인할 수 있습니다. 같은 글자가 `title`, `aria-label`, 연결된 상세 링크, 펼치기 버튼에 있는지 봅니다. 없으면 `truncated_without_alternative`로 기록합니다 (AUT-05).

### 2.4 파일럿: 사람이 쓴 ACT 예제로 현재 구현과 대안을 비교 [derived]

**목적.** 이 스킬의 벤치마크는 작성자·탐지기·심사관이 모두 Claude입니다 (`validation-and-limits.md`). W3C ACT 예제는 사람 커뮤니티가 쓴 외부 오라클입니다. SM/LY 검사가 ACT의 "통과 예제에서 오탐 0" 계약을 지키는지 확인했습니다.

**방법.**

- ACT 규칙 원본 8개와 c487ae에서 예제 169개를 추출했습니다.
- 브라우저: Playwright 1.56.1 + Chromium 1194 (`/opt/pw-browsers`). 예제 HTML과 ACT `test-assets`는 로컬 라우팅으로 제공하고, 외부 네트워크는 막았습니다.
- 비교 대상 네 가지:
  1. **스킬**: `page_scripts.mjs` 339–468행을 그대로 복사해 페이지에서 실행하고, `check_semantics`의 판정을 재현했습니다.
  2. **스킬 필터 + Chromium 이름**: 같은 가시성·활성 필터를 쓰되 이름만 CDP AX 트리에서 가져왔습니다.
  3. **Chromium AX 트리 그대로**
  4. **axe-core 4.13.0**: ACT에 대응하는 규칙만 실행했습니다.
- 스크립트와 결과는 스크래치패드에만 두었고, 저장소는 바꾸지 않았습니다.

**이름 규칙** (탐지 = 실패 예제 중 잡은 수, 오탐 = passed·inapplicable 예제 중 실패로 판정한 수):

| ACT 규칙 (실패 / 비실패 예제) | 스킬 (SM-01·SM-03) | 스킬 필터 + Chromium 이름 | Chromium AX 트리 | axe-core 4.13 |
| --- | --- | --- | --- | --- |
| 97a4e1 버튼 (5 / 12) | 3/5, 오탐 0/12 | 4/5, 0/12 | 5/5, 0/12 | 5/5, 0/12 |
| e086e5 입력 칸 (9 / 12) | 5/9, 0/12 (placeholder·title까지 세면 1/12) | 9/9, 0/12 (이 행만 가시성 필터 없이 계산) | 9/9, 0/12 | 9/9, 0/12 |
| c487ae 링크 (11 / 17) | 7/11, **3/17** | 7/11, 0/17 | 10/11, 0/17 | 11/11, 0/17 |
| **합계 (25 / 41)** | **15/25 (60 %), 오탐 3/41 (7.3 %)** | 20/25 (80 %), 0/41 | 24/25 (96 %), 0/41 | **25/25, 0/41** |

- **스킬이 놓친 원인:**
  - 크기가 0인 요소(빈 `<span role="button">`, 빈 `<a href>`, 공백만 있는 `role="none"` 링크)를 가시성 필터가 제외했습니다. 화면에는 안 보여도 접근성 트리에는 있어서 스크린리더 사용자는 만납니다.
  - `role="textbox"`인 `div` 3건은 요소 수집 선택자에 없습니다.
  - 비활성 입력 칸은 설계상 건너뜁니다.
  - `<area>`는 수집하지 않습니다.
  - `role="doc-biblioref"` 예제 하나는 파일럿에서 외부 이미지를 막은 탓이라 인공물일 수 있습니다.
- **스킬의 오탐 3건:** 링크 안 `img`의 `aria-label`, `title`, `aria-labelledby`로 생기는 이름을 계산하지 않았습니다. `accNameSrc`는 내용에서 `img[alt]`와 `svg title`만 봅니다.

**2.5.3 레이블 포함** (ACT 2ee8b8: 실패 16, 통과 16, 적용 외 6):

| 방식 | 탐지 | 통과 예제 오탐 | 적용 외 예제 오탐 |
| --- | --- | --- | --- |
| 현재 SM-02 (모든 비단어 문자 삭제 후 부분 문자열, 글자 2개 이상) | 7/16 | 3/16 | 0/6 |
| **ACT 알고리즘** (토큰화, 괄호 제거, NFKD, 연속 부분열), 보이는 내부 글자, 아이콘 글꼴 제외, 한글 조사 완화 | **16/16** | 1/16 ("X"를 닫기 기호로 쓴 경우) | 2/6 (약어 "Ave.", 하이픈 "non-standard") |
| axe `label-content-name-mismatch` (experimental) | 14/16 | 3/16 (아이콘 리거처, 공백 없는 span, 괄호) | 0/6 |

- 현재 SM-02가 놓친 9건 중 5건은 숫자만 있는 레이블("2021", 전화번호, "11×3=33")이라 글자 2개 이상 조건에 걸렸습니다. 나머지는 단어 경계를 지운 탓("Discover It" ⊂ "Discover Italy", "justice" = "just ice")입니다.
- **주의:** 아이콘 글꼴과 시각적으로 숨긴 글자 처리는 첫 실행의 오탐 두 건을 본 뒤 넣었습니다. 이 행은 이 예제에 맞춘 결과(fit)이지 보류 추정치가 아닙니다.

**잘림, 초점, 메타 뷰포트, 글자 간격:**

| ACT 규칙 (실패 / 통과 / 적용 외) | 방식 | 탐지 | 오탐 |
| --- | --- | --- | --- |
| 59br37 200 % 잘림 (5 / 4 / 5), 640 × 512, DPR 2 | 현재 LY-01 (자기 상자) | 5/5 (말줄임 제외 시 4/5) | 통과 2/4 (말줄임, 한 줄 고정), 적용 외 0/5 |
| 〃 | ACT식 조상 잘림 (축별, 스크롤 컨테이너에서 멈춤, 4 px 미만 상자 제외) | 5/5 | 0/4, 0/5 (**두 번 고친 뒤의 fit**) |
| oj04fd 보이는 초점 (1 / 4 / 2) | 현재 SM-05 (상자 + 4 px, 24/255 이상 픽셀 4개 미만이면 실패) | 1/1 | 통과 1/4 (표시가 요소 **옆**의 파란 사각형) |
| 〃 | ACT식 (뷰포트 전체에서 초점 전후 픽셀이 하나라도 다른가) | 1/1 | 0/4 |
| b4f0c3 메타 뷰포트 (7 / 5 / 4) | axe `meta-viewport` | 5/7 (`user-scalable=invalid`, `maximum-scale=invalid` 놓침) | 0/9 |
| 24afc2 `!important` 자간 (4 / 6 / 9) | axe `avoid-inline-spacing` | 4/4 | 2/15 (자기 글자가 없는 요소) |

**실행 비용.** 이름 파일럿 104개 예제가 브라우저 컨텍스트 생성, CDP 트리, axe 주입을 모두 합쳐 22.5초(예제당 약 0.2초)였습니다. 작은 페이지라 실제 제품 비용을 대표하지 않습니다.

**이 파일럿이 말하지 않는 것.** ACT 예제는 규칙당 5–38개이고 경계 사례 위주입니다. 실제 제품에서의 정밀도가 아닙니다. 다만 "현재 SM-01/SM-02/LY-01/SM-05가 사람이 쓴 통과 예제를 실패로 판정한다"는 것은 확인된 사실이고, 고치는 방법도 규칙 원문에 있습니다.

### 2.5 프로필과 무관한 검사와 프로필에 따라 달라지는 검사

| 검사 | WCAG / KWCAG 2.2 | 계산이 프로필에 따라 달라지나 | 보고 단위 | 누구에게 중요한가 (audience 조건) |
| --- | --- | --- | --- | --- |
| 이름·역할 (SM-01, SM-03, AX) | 4.1.2, 1.3.1, 3.3.2 / 7.3.2, 8.2.1 | 아니요 | `screen_key` × 기기 부류마다 한 번 | `screen_reader`, 음성 제어 (선언만 되고 시뮬레이션하지 않는 조건) |
| 레이블 포함 (SM-02) | 2.5.3 / 6.5.3 | 아니요 | 한 번 | 음성 제어 |
| 오류 연결 (SM-04) | 3.3.1 / 7.3.1 | 측정은 아니요. 알아차리는지는 예(GZ-02가 이미 다룸) | 한 번 | `screen_reader`, `cognitive`, 모두 |
| 보이는 초점, 초점 가림, 초점 관리 (SM-05, SM-06, AUT-11) | 2.4.7, 2.4.11, 2.4.3 / 6.1.2 | 계산은 아니요. 키보드가 있는 기기 부류에만 적용 | 키보드 기기마다 한 번. 프로필 속성 `grip=keyboard_only`와 연결 | `keyboard_only`, `switch_access`, 데스크톱 `screen_reader` |
| 약한 초점 표시 (AUT-10) | 2.4.13 AAA | **부분적으로 예**: 색 변화만으로 된 표시는 CVD 시뮬레이션과 시각(visual angle)에 따라 다르게 보임 | 시각 조건 프로필마다 (basis `model`) | `low_vision`, `cvd_*`, `presbyopia` |
| 320 CSS px 리플로 (AUT-06) | 1.4.10 / 없음 | 적합성 판정은 아니요 | 데스크톱 화면마다 한 번 | `low_vision`, `magnifier` (400 % 확대) |
| 200 % 확대 (AUT-07, 데스크톱) | 1.4.4 / 없음 | 아니요 | 한 번 | `presbyopia`, `low_vision` |
| OS 글자 크기 1.3·2.0배 (AUT-07, 모바일) | WCAG 밖 (플랫폼 설정) | **예**: `contexts[].technical.text_scale`(AP-09)에 따라 다름 | 그 프로필마다. 차등 조건 `technical.text_scale` | 60대·70대 이상 `presbyopia`, `low_vision` |
| 글자 간격 (AUT-19) | 1.4.12 / 없음 | 아니요 | 한 번 | 난독증, `low_vision` (선언만 됨) |
| 메타 뷰포트 확대 차단 (AUT-08) | 1.4.4 (ACT b4f0c3) | 아니요 | 모바일 화면마다 한 번 | 구형 모바일 브라우저의 `low_vision` |
| 대상 크기 (PT-01) | 2.5.8 / 6.1.3 권장 | 아니요 (이미 profile-invariant) | 한 번 | 운동 (PT-04 모델 검사는 프로필에 따라 다름) |

**원칙** [derived]:

1. 프로필과 무관한 검사는 페르소나 수만큼 곱하지 않습니다. 현재 `PROFILE_INVARIANT_CHECKS`(STF-08)와 같습니다.
2. 그렇다고 "누구와도 무관"하게 두지도 않습니다. `serves` 필드에 선언만 된 조건을 적고, audience 파일에 그 조건이 있는 세그먼트를 `segments_affected`로 연결합니다. 이렇게 해야 페르소나 구성과 이어집니다.
3. 글자 크기와 확대는 유일하게 **프로필 속성을 바꿔 다시 렌더링해야** 드러나는 레이아웃 결함입니다. 스웜 구조(프로필마다 다른 조건)가 정적 스캐너보다 확실히 나은 곳입니다.

### 2.6 axe-core를 페이지 안에서 호출해 결과를 매핑하는 방법과 MPL-2.0

- Playwright 공식 문서는 `@axe-core/playwright`를 권장합니다 (`AxeBuilder({ page }).analyze()`). 면책 문구는 "Automated accessibility tests can detect some common accessibility problems … But many accessibility problems can only be discovered through manual testing."입니다. [industry]
- 드라이버는 이미 Playwright를 쓰므로 `node_modules/axe-core/axe.min.js`를 `page.addScriptTag({ path })`로 넣고 `axe.run()`을 부르면 됩니다. 이렇게 하면 네트워크를 쓰지 않으므로 사양 §0의 "로컬 페이지 외 네트워크 금지"를 지킵니다. 4.13.0의 `axe.min.js`는 567 KB(gzip 152 KB)입니다. [derived]
- **MPL-2.0 원문의 요구** [standard: 라이선스 원문]:
  - §3.3: "You may create and distribute a Larger Work under terms of Your choice, provided that You also comply with the requirements of this License for the Covered Software."
  - §3.2: 실행 형태(Executable Form)로 배포하면 소스 형태도 제공해야 하고, 받는 사람에게 소스를 얻는 방법을 알려야 합니다.
  - §3.4: 라이선스 고지를 지우거나 바꿀 수 없습니다.
  - §1.10(b): "any new file in Source Code Form that contains any Covered Software"도 수정본(Modification)입니다.
  - `axe.min.js` 머리말: "This entire copyright notice must appear in every copy of this file you distribute or in any file that contains substantial portions of this source code." [industry]
- **정리** [derived, 법률 자문 아님]:
  1. npm **선택적 의존성**으로 두는 방식은 스킬이 axe를 재배포하지 않으므로 MIT인 스킬 코드에 아무 영향이 없습니다. 권장합니다.
  2. 오프라인 복사를 위해 동봉(vendoring)할 때는 수정하지 않은 `axe.min.js`와 머리말을 그대로 두고, `THIRD_PARTY_NOTICES.md`에 MPL-2.0 고지와 v4.13.0 소스 링크를 적습니다. 나머지 스킬 파일은 MIT로 남습니다 (Larger Work).
  3. axe의 **규칙 코드를 `checks.py`나 `page_scripts.mjs`에 옮겨 적으면 안 됩니다.** 그 파일이 MPL 수정본이 됩니다. 규칙은 ACT·accname 원문에서 다시 구현합니다.
- 허용적 라이선스 대안 [industry: npm 메타데이터]:
  - Siteimprove Alfa (MIT, ACT 중심). 구현 보고서의 consistent 규칙 수는 29로 axe(26)보다 많습니다 [snippet].
  - IBM Equal Access `accessibility-checker` (Apache-2.0)
  - HTML_CodeSniffer (BSD-3-Clause)

### 2.7 현재 SM/LY 구현 감사 (코드를 읽고 파일럿과 대조) [derived]

| 위치 | 관찰 | 영향 |
| --- | --- | --- |
| `page_scripts.mjs` `accNameSrc` (377–411행) | `aria-hidden` 하위, CSS 생성 글자, 하위 요소의 접근 가능한 이름(`img`의 `aria-label`·`title`·`labelledby`), 내장 컨트롤, 내용에서 이름을 얻을 수 없는 역할(`role=textbox`는 입력 글자가 이름이 됨), presentational 역할 충돌을 다루지 않음 | 파일럿 링크 오탐 3/17. `aria-hidden` 아이콘 글자(예: ×)가 이름으로 잡혀 이름 없는 버튼을 놓침 (2.2 한국어 사례) |
| `INTERACTIVE` 선택자 (520–522행) | textbox, searchbox, combobox, listbox, spinbutton, option, menuitemcheckbox, menuitemradio, treeitem, gridcell 역할이 없음 | 사용자 정의 입력 칸의 SM-03 미탐 (파일럿 3/9) |
| `checks.py` `_present` + 가시성 | 크기 0이거나 숨었지만 초점을 받는 요소를 건너뜀 | 스크린리더·키보드 사용자가 만나는 빈 링크와 빈 버튼을 놓침 |
| SM-02 (`checks.py` 1735–1743행) | 모든 비단어 문자를 지운 뒤 부분 문자열로 비교. 글자 2개 이상 조건. 괄호 규칙 없음. `innerText` 사용 | ACT 대비 미탐 9/16, 오탐 3/22 |
| SM-03 문서 | placeholder·title만 있는 칸을 1.3.1/3.3.2/4.1.2 실패처럼 서술 | ACT와 axe는 이름이 있다고 봄. best practice로 표기해야 함 |
| SM-04 | 48 CSS px 상수. 규범 출처 없음 (LAT-09 ER-01) | 글자 크기나 확대가 바뀌면 판정도 바뀜. DOM 그룹 근접성이 더 안정적임 |
| SM-05 (`session.mjs` 316–365행) | 상자 + 4 px, 채널 차이 24/255, 4 px. 초점 없는 상태를 Shift+Tab으로 만듦 | 표시가 떨어져 있으면 오탐 (파일럿 1/4). Shift+Tab은 이전 요소에 초점을 주므로, 이웃 요소의 표시가 잘라낸 영역에 들어오면 미탐 가능 |
| SM-06 (`focusInfo`) | 9개 표본점, fixed·sticky 조상만 셈. 사용자가 연 층이나 Esc로 닫히는 층을 빼지 않음. 일부 가림을 P3로 보고 | 2.4.11 주석과 어긋날 수 있음. AAA를 결함으로 셈 |
| LY-01 (`clippedOf`, 444–449행) | 자기 상자만 봄. 말줄임을 P3로 셈. 기본 뷰포트에서만 실행 | ACT가 통과시키는 말줄임·한 줄 고정에서 오탐. 조상이 자르는 경우 미탐. 확대 상태를 보지 않으므로 1.4.4 시험이 아님 |

**저장소 기록과의 대조.** exp5(`5b6e8fb`)에서 의미 검사를 더한 뒤에도 개발 스위트 53개 결함의 strict recall은 0.906으로 같았습니다. 발견은 193 → 200, 단위는 97 → 101, clean-control 단위는 26 → 27이었습니다 [derived: `decisions.md`]. 개발 스위트에는 의미 결함이 거의 없으므로, 이 수치는 소음의 규모를 알려 줄 뿐 정밀도나 재현율의 근거는 아닙니다. 위 표의 문제는 ACT 예제 같은 의미 전용 오라클에서만 드러납니다.

## 3. Implications for the skill (스킬에 주는 시사점)

### 3.0 요약

1. **새로 구현하기보다 브라우저와 axe에 맡길 것:**
   - 접근 가능한 이름은 Chromium이 계산한 트리를 씁니다 (AUT-01).
   - 1.1.1, 4.1.2, 1.3.1, 3.1.1 같은 정적 규칙은 axe-core의 WCAG 태그 규칙을 선택적 의존성으로 부릅니다 (AUT-02).
   - 자체 SM-01, SM-03(이름 없음)은 axe가 없을 때의 대체 수단으로만 남깁니다 (AUT-03).
2. **정적 스캐너가 못 하는 것에 집중할 것:**
   - 프로필이 글자를 키우거나 확대했을 때의 잘림과 리플로 (AUT-05, AUT-06, AUT-07)
   - 흐름 속 초점 관리 (AUT-11)
   - 보이는 초점과 초점 가림 (AUT-09, AUT-13)
   GOV.UK 감사에서 13개 도구가 거의 못 잡은 영역이고, axe 4.13에도 규칙이 없습니다.
3. **이미 있는 검사를 ACT 원문에 맞춰 고칠 것:** SM-02(AUT-04), LY-01(AUT-05), SM-05(AUT-09), SM-06(AUT-13), SM-04(AUT-22). 파일럿에서 네 검사 모두 사람이 쓴 통과 예제를 실패로 판정했습니다.
4. **외부 오라클을 들일 것:**
   - ACT 예제를 모든 SM/LY/AX 검사의 정밀도 관문으로 씁니다 (AUT-15).
   - GOV.UK 장벽 142개 페이지(MIT)를 외부 벤치마크로 씁니다 (AUT-02 실험).
   Claude만으로 만든 벤치마크의 한계(validation-and-limits)를 일부 메웁니다.
5. **빼거나 넣지 말 것:** 시각 순서 기반 초점 순서 휴리스틱(AUT-12), axe best-practice·experimental 규칙의 결함 집계, axe `color-contrast`·`target-size`(PC-01·PT-01과 중복, AUT-18), LY-01의 말줄임 P3, SM-06의 부분 가림(AAA) 결함 집계.

### 3.1 후보 표

노력(Effort): S ≤ 1일, M ≤ 1주, L > 1주. "dev-2"는 이 저장소의 semantics·layout 개발 스위트입니다 (이 브리프 작성자는 읽지 않았습니다). heldout-2는 사전등록대로 한 번만 채점하고 조정에 쓰지 않습니다.

| ID | Type | What exactly | Evidence | Expected effect on recall / noise / usefulness | Experiment that decides it (hypothesis, metric, pass rule, data needed) | Effort |
| --- | --- | --- | --- | --- | --- | --- |
| AUT-01 | CHANGE | **이름과 역할의 출처를 Chromium 접근성 트리로 바꿉니다.**<br>• `session.mjs`가 스냅숏마다 CDP `Accessibility.getFullAXTree`를 한 번 부르고, `DOM.describeNode`로 `backendDOMNodeId`를 요소에 잇습니다.<br>• 요소 필드 `a11y`에 `ax_name`, `ax_role`, `ax_name_sources`([type, nativeSource, attribute]), `ax_ignored`, `ax_ignored_reasons`, `ax_focusable`, `ax_invalid`, `ax_required`, `ax_describedby`, `ax_errormessage`를 더합니다.<br>• SM-01과 SM-03은 `ax_name`으로 판정하고, `name_source`는 `ax_name_sources`에서 유도합니다 (예: `placeholder`, `title`, `relatedElement:label`).<br>• `accNameSrc`는 CDP가 없을 때(비 Chromium)만 대체 수단으로 씁니다. | accname 1.2의 단계가 복잡합니다 (§2.3a) [standard]. 파일럿 이름 규칙: 스킬 15/25 탐지·오탐 3/41, Chromium 트리 24/25·0/41 [derived]. `aria-hidden` 아이콘 버튼을 현재 구현은 놓칩니다 [derived]. | **Recall:** SM-01/03이 ACT 실패 예제의 60 %만 잡던 것이 약 96 %로 오릅니다.<br>**Noise:** 하위 이미지 이름을 무시해 생기던 링크 오탐이 없어집니다.<br>**Usefulness:** 스크린리더가 실제로 들을 이름을 보고서에 적을 수 있습니다. | **H:** CDP 이름으로 바꾸면 ACT 이름 예제에서 오탐이 0이고, dev-2 semantics 재현율이 떨어지지 않습니다.<br>**Metric:** ACT 97a4e1·e086e5·c487ae·m6b1q3·59796f 예제의 결과, dev-2 semantics recall, clean-control SM 단위 수.<br>**Pass:** passed·inapplicable 예제에서 실패 판정 0; failed 예제 ≥ 95 % 탐지; dev-2 recall ≥ 현재; 스냅숏당 추가 시간 ≤ 300 ms (중앙값).<br>**Data:** ACT 규칙 저장소(커밋 고정), dev-2. | M |
| AUT-02 | ADD | **axe-core 적합성 층 `AX-*`.**<br>• `axe-core@4.13.x`를 `drivers/web/package.json`의 `optionalDependencies`로 둡니다. 동봉하지 않습니다.<br>• 드라이버는 기기 부류마다 새 `screen_key`가 처음 나올 때 한 번 `axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}, rules: {'color-contrast': {enabled: false}, 'target-size': {enabled: false}}, resultTypes: ['violations','incomplete'], selectors: true, iframes: true})`를 실행합니다.<br>• 결과는 스냅숏의 `axe: {version, duration_ms, violations[], incomplete[]}`에 넣습니다. 노드마다 `target`, `html`(200자), `failureSummary`, `box`를 둡니다.<br>• `check_axe`는 위반 노드를 관찰 `AX-<rule>`로 만듭니다: basis `measured`, model `axe-core@<ver>`, 범주는 태그로 매핑(§3.3). `incomplete`는 hypothesis 등급입니다.<br>• `AX-*`는 profile-invariant이고, 보고서에서 WCAG SC와 KWCAG 항목을 함께 적습니다. | axe README "57 %"와 "zero false positives" [industry]. ACT consistent 26 [snippet]. 파일럿 25/25·0/41 [derived]. GOV.UK 감사에서 axe 29 % [industry]. WebAIM 상위 여섯 범주 가운데 대체 텍스트 53.1 %, 문서 언어 13.5 %는 현재 스킬에 검사가 없습니다 [snippet]. Playwright 공식 권장 [industry]. MPL-2.0 §3.3 [standard]. | **Recall:** 1.1.1, 3.1.1, 2.4.2, ARIA 유효성, 표·목록 구조처럼 지금 0인 결함 유형이 새로 잡힙니다.<br>**Noise:** WCAG 태그의 violations만 세고, best-practice·experimental과 `incomplete`는 세지 않으므로 낮게 유지됩니다.<br>**Usefulness:** 업계 표준 도구와 같은 규칙 ID로 개발자에게 전달할 수 있습니다. | **H1 (외부):** GOV.UK 장벽 142개 페이지에서 AX + SM + 드라이버 검사가 2018년 최고 도구(40 %)보다 많이, 즉 ≥ 64개(45 %)를 잡고, 키보드·초점·확대 부분집합 24개 가운데 ≥ 8개를 잡습니다.<br>**H2 (정밀도):** 실제 제품 2개에서 무작위로 뽑은 AX 단위 ≥ 40개를 심사관 2명(가능하면 사람 1명 포함)이 판정했을 때 validity의 Wilson 하한 ≥ 0.85입니다.<br>**H3 (소음):** dev-2 clean control에서 AX 단위 P0–P2 ≤ 0.5개/시나리오.<br>**Pass:** H2와 H3를 모두 만족. H1은 보고만 합니다.<br>**Data:** GOV.UK `accessibility-tool-audit` 페이지(MIT, `tests.json`이 정답표), dev-2, 공개 사이트 2곳(읽기 전용). | M |
| AUT-03 | CUT (조건부) | **axe가 성공적으로 실행된 스냅숏에서는 SM-01과 SM-03(이름 없음)을 끄고 AX 결과만 셉니다.**<br>• SM-03의 placeholder·title 변형은 `SM-03b`로 이름을 바꿉니다: "best practice (레이블 품질)", 최대 P3, WCAG 실패라고 쓰지 않습니다.<br>• axe가 없으면 SM-01/03이 그대로 동작합니다 (AUT-01 적용). | 같은 요소에 SM-01과 `AX-button-name`이 동시에 뜨면 중복 단위가 됩니다 [derived]. placeholder만 있는 칸은 ACT e086e5와 axe `label`에서 통과합니다 (직접 확인) [derived]. | **Recall:** 0 변화 (H로 확인).<br>**Noise:** 중복 단위 ↓.<br>**Usefulness:** 유지할 코드가 줄고, WCAG 실패와 모범 사례가 구분됩니다. | **H:** ACT 예제와 dev-2에서 SM-01·SM-03(없음) 단위마다 같은 요소의 AX 단위가 있습니다.<br>**Metric:** SM만 있는 단위 수.<br>**Pass:** 0 (있으면 그 규칙 차이를 먼저 조사).<br>**Data:** 기존 기록. | S |
| AUT-04 | CHANGE (동결 전 가능) | **SM-02를 ACT 레이블 포함 알고리즘으로 바꿉니다.**<br>• 토큰화: 괄호와 그 안 제거 → NFKD·소문자 → L/N 이외는 공백 → 공백 분리 → **연속 부분열** 판정.<br>• 보이는 내부 글자에서 `display:none`, `visibility:hidden`, `clip`/`clip-path: inset(50%)`, 1 px 상자를 뺍니다.<br>• 아이콘 글꼴(`font-family`가 `/icon\|symbol\|glyph\|awesome\|material/i`) 글자는 비텍스트로 봅니다.<br>• 한 글자 기호(`×`, `X`, `+`, `<`, `>`, `☰`, `…`)는 비텍스트로 봅니다.<br>• 글자 2개 이상 조건을 없애고, L/N 토큰이 1개 이상이면 적용합니다.<br>• 적용 역할은 이름을 내용에서 얻는 위젯 역할입니다.<br>• 한국어 완화: 한글 레이블 토큰은 이름 토큰이 그 토큰으로 시작하면 일치로 봅니다 (조사). `.`으로 끝나는 약어 토큰도 접두 일치로 봅니다.<br>• 판정 결과에 `algorithm: "act-2ee8b8"`와 `relaxation`을 기록합니다. | ACT 2ee8b8과 레이블 포함 알고리즘 [standard]. 파일럿: 현재 7/16·오탐 3/22 → 새 방식 16/16·통과 오탐 1/16 [derived, 예제에 맞춘 결과]. axe 이슈 "CJK / full-width punctuation is not removed" [industry]. 한국어 사례에서 axe가 조사 차이를 위반으로 판정 [derived]. | **Recall:** 숫자 레이블과 단어 경계 오류가 새로 잡힙니다.<br>**Noise:** 괄호, 숨긴 글자, 아이콘 글꼴 오탐이 없어집니다.<br>**Usefulness:** 음성 제어 사용자 기준에 맞습니다. | **H:** 새 SM-02는 ACT 2ee8b8에서 실패 ≥ 15/16을 잡고 통과·적용 외 오탐이 0입니다. 한국어 쌍에서는 사람 판정과 ≥ 0.9 일치합니다.<br>**Metric:** ACT 결과; 한국어 쌍 일치율과 κ.<br>**Pass:** 두 조건 모두.<br>**Data:** ACT 예제 38개. **Claude가 아닌 한국어 사용자**가 쓴 한국어 레이블·이름 쌍 40–60개 (조사, "버튼" 접미사, 괄호, 숫자, 전각 문장부호). 가능하면 Android Voice Access(한국어)로 실제 명령이 통하는지도 확인합니다. | S |
| AUT-05 | CHANGE (동결 전 가능) | **LY-01을 ACT 59br37 방식의 조상 잘림 판정으로 바꿉니다.**<br>• 텍스트 노드마다 `Range.getClientRects()`의 합집합을 구합니다.<br>• 축(x, y)마다 조상을 올라가며 판정합니다: 그 축이 `auto\|scroll`인 조상에서 멈추고(스크롤로 닿을 수 있음), `hidden\|clip`이면 조상의 padding box와 비교합니다(허용오차 1 px).<br>• 예외: x축은 조상이 `nowrap`이고 `text-overflow` ≠ `clip`이면 통과. y축은 `line-height` ≥ 상자 높이이면 통과. 4 px 미만 상자는 스크린리더 전용이므로 제외. `aria-hidden` 하위도 제외.<br>• 통과한 말줄임은 결함이 아닙니다. 같은 글자가 `title`, `aria-label`, 펼치기 컨트롤이나 상세 링크 어디에도 없으면 `truncated_without_alternative`로 hypothesis에 둡니다.<br>• 기록 필드: `clipped: {axis, by (조상 selector), overflow_px, exception}`. | ACT 59br37 정의 [standard]. 파일럿: 현재 LY-01은 통과 예제 2/4를 실패로 판정. 새 방식은 5/5, 오탐 0/9 [derived, 예제에 맞춘 결과]. XCTest `textClipped` [industry]. 1.4.10과 1.4.12 Understanding의 말줄임 규칙 [standard]. | **Recall:** 조상이 자르는 경우가 새로 잡힙니다.<br>**Noise:** 말줄임과 한 줄 고정 오탐이 없어집니다.<br>**Usefulness:** AUT-06, AUT-07에서 그대로 재사용합니다. | **H:** 새 LY-01은 ACT 59br37 예제에서 오탐 0이고, dev-2 layout 재현율이 현재 이상이며, clean-control LY 단위가 현재 이하입니다.<br>**Pass:** 세 조건 모두.<br>**Data:** ACT 14개, dev-2. | S |
| AUT-06 | ADD | **리플로 패스 (1.4.10).**<br>• 데스크톱·노트북 기기에서 각 `screen_key`의 마지막 상태를 새 컨텍스트에서 다시 열거나, 같은 페이지의 뷰포트를 바꿔 320 × 256 CSS px, DPR 4로 스냅숏 1장을 찍습니다.<br>• **RF-01** (P2): `scrollingElement.scrollWidth > clientWidth + 1`. 범인 요소는 오른쪽 끝 > 320 + 1인 가장 바깥 요소입니다. 2차원 예외(`table` 안, `canvas`, `video`, `iframe`, 지도 역할, `svg` 도표, 코드 블록)와 자체 가로 스크롤 컨테이너 안은 제외합니다.<br>• **RF-02** (P2): AUT-05 잘림.<br>• **RF-03**: 과업 경로의 인터랙티브 요소가 스크롤 영역 밖에 있거나, fixed·sticky 층에 9개 점이 모두 덮여 닿을 수 없음. 경로면 P1, 아니면 P2.<br>• **RF-04** (hypothesis): fixed·sticky 층의 높이 합이 256 px의 50 % 이상 (정책값).<br>• 겹침 후보는 두 상자를 겹침 해소 전후로 그려 픽셀이 다를 때만 셉니다 (VISER 방식).<br>• profile-invariant. `serves: [low_vision, magnifier]`. | 1.4.10 원문과 Understanding [standard]. GOV.UK "Wide page forces users to scroll horizontally" 0/13 [derived]. ICSE 2024 리플로 탐지 연구 [snippet]. VISER의 보이지 않는 실패 [industry/snippet]. axe에는 해당 규칙이 없음 [derived]. | **Recall:** layout 범주에서 "320 px에서 잃는 콘텐츠"가 새로 잡힙니다 (heldout-2 사양 §12.1의 layout 정의).<br>**Noise:** 2차원 예외와 픽셀 확인이 없으면 큽니다 (VISER).<br>**Usefulness:** 저시력 확대 사용자에 대한 근거가 생깁니다. | **H:** RF 단위 validity의 Wilson 하한 ≥ 0.8이고, clean-control RF 단위 ≤ 0.3개/시나리오입니다.<br>**Metric:** 공개 사이트 2곳에서 심사한 RF 단위 ≥ 30개; dev-2 layout recall; GOV.UK 가로 스크롤 장벽 탐지.<br>**Pass:** H 만족, GOV.UK 장벽 탐지.<br>**Data:** 위 자료, 추가 스냅숏 비용 기록 (실행 시간 +10–20 % 예상 [opinion]). | M |
| AUT-07 | ADD | **글자 크기 패스 (1.4.4, 그리고 프로필에 따른 OS 글자 크기).**<br>• (a) 데스크톱: 640 × 512, DPR 2에서 한 장 찍습니다 (1280 × 1024의 200 %, ACT 59br37 조건). profile-invariant.<br>• (b) 터치 기기: 프로필에 `technical.text_scale` ∈ {1.3, 2.0}이 있으면(AP-09; 60대 이상과 노안 세그먼트) 요소마다 계산된 `font-size`와 px 단위 `line-height`에 s를 곱합니다. 여백과 간격은 그대로 둡니다 (WebView text inflation). 그리고 한 장 찍습니다.<br>• 이어서 AUT-05 잘림, 텍스트 상자 겹침(픽셀 확인), 컨트롤 밖으로 삐져나온 레이블, 인터랙티브 요소가 뷰포트 밖으로 밀림을 봅니다.<br>• (b)의 단위는 프로필에 따라 달라지고, 차등 조건은 `technical.text_scale`입니다.<br>• 이 검사가 이미 알고 있는 실패 예제의 조건을 이름으로 댈 수 있는지를 `recall_condition_attributed`로 봅니다. | 1.4.4 원문과 Understanding [standard]. ACT 59br37 [standard]. AP-09: 글자 크기를 바꾸는 사용자가 3분의 1 이상 [snippet, AP 브리프]. Roselli 2026 [industry]. ATF `TextSizeCheck`가 스스로 경고하는 정적 방식의 오탐 [industry]. XCTest `dynamicType` [industry]. KWCAG 2.2에는 해당 항목이 없음 [derived]. | **Recall:** 노안 프로필에서만 드러나는 잘림·겹침이 **조건이 식별된 채로** 잡힙니다. 스웜 구조가 정적 스캐너보다 확실히 나은 곳입니다.<br>**Noise:** 겹침 판정이 가장 큰 위험입니다. 픽셀 확인과 hypothesis 등급으로 제한합니다.<br>**Usefulness:** 60대 이상 세그먼트에 직접 연결됩니다. | **H:** (b)는 기본 크기 실행에서 없던 단위를 만들고, 그 단위의 validity ≥ 0.8입니다.<br>**Metric:** 조건이 식별된 layout 탐지 수; 확대 실행에서만 나온 단위 수; 심사 validity; clean-control 단위.<br>**Pass:** 스위트마다 조건이 식별된 고유 탐지 ≥ 1, validity ≥ 0.8, clean-control ≤ 0.5개/시나리오.<br>**Data:** dev-2 (글자 크기 조건 결함이 있으면), 공개 사이트 2곳, 심사관 2명. | M |
| AUT-08 | ADD | **메타 뷰포트 확대 차단 `LY-02`.**<br>• ACT b4f0c3 규칙을 그대로 따릅니다: `user-scalable`이 `no`이거나 −1 < 값 < 1, 또는 `maximum-scale` < 2이면 실패. 잘못된 값도 실패입니다 (axe는 이것을 놓침).<br>• 모바일 표면에서 P3. audience 기기에 앱 WebView나 구형 Android 브라우저가 있으면 P2. 데스크톱에서는 보고하지 않습니다.<br>• AUT-02가 켜져 있으면 axe `meta-viewport`와 합칩니다. | ACT b4f0c3와 그 보조기술 지원 절 [standard]. Lighthouse 가중치 10 [derived]. 파일럿에서 axe 5/7, 오탐 0/9 [derived]. | **Recall:** 작지만 확실합니다.<br>**Noise:** 약 0.<br>**Usefulness:** 고치기 쉬운 한 줄 수정입니다. | **H:** ACT 예제에서 오탐 0, 탐지 7/7.<br>**Pass:** 두 조건 모두.<br>**Data:** ACT 16개. | S |
| AUT-09 | CHANGE (동결 전 가능) | **SM-05를 ACT와 일관되게 바꿉니다.**<br>• 초점이 있을 때 뷰포트 전체를 찍고, `blur()` 뒤에 두 번 찍습니다. 두 번의 blur 사진 사이에서 바뀐 픽셀(애니메이션)은 가립니다.<br>• 가린 뒤 초점 전후로 다른 픽셀이 **하나도 없을 때만** 실패로 봅니다 (P2).<br>• 요소 주변의 변화량은 `indicator_local_px`, 뷰포트 전체의 변화량은 `indicator_any_px`로 남기고, AUT-10에 넘깁니다.<br>• Shift+Tab 대신 `blur()`를 씁니다. 이전 요소의 표시가 섞이지 않게 하기 위해서입니다. | ACT oj04fd의 기대와 배경 [standard]. 파일럿: 현재 SM-05 통과 예제 오탐 1/4, ACT식 0/4 [derived]. GOV.UK "Focus not visible" 0/13 [derived]. | **Recall:** 2.4.7 실패 탐지는 유지됩니다. 약한 표시는 AUT-10으로 옮깁니다.<br>**Noise:** 떨어져 그려진 표시 때문에 생기던 오탐이 없어집니다.<br>**Usefulness:** WCAG 판정과 일치합니다. | **H:** ACT oj04fd 오탐 0이고, GOV.UK의 초점 표시 장벽 두 개와 dev-2 초점 표시 결함을 잡습니다.<br>**Pass:** 세 조건 모두.<br>**Data:** ACT 7개, GOV.UK 페이지, dev-2. | S |
| AUT-10 | ADD (hypothesis 등급으로 시작) | **약한 초점 표시 `SM-07` (2.4.13 계열, 프로필에 따라 달라지는 모델).**<br>• 바뀐 픽셀 가운데 초점 전후 대비가 ≥ 3:1인 픽셀 수 `A`와, 요소 둘레 2 px 면적 `P = 2 × (2w + 2h)`를 비교합니다. `A < P`이면 약한 표시입니다.<br>• CVD 프로필에서는 초점 전후 색을 Machado로 시뮬레이션한 뒤 ΔE00 < 5이면 "이 프로필에게 보이지 않는 표시"로 봅니다. PC-03의 모델을 재사용합니다.<br>• 노안 프로필에서는 표시 두께의 시각이 1′ 미만인지를 봅니다 (정책값).<br>• 결과는 P3 hypothesis이고, 심사 뒤에 승격합니다. | 2.4.13 원문 [standard]. ACT oj04fd 배경: "barely perceptible" 표시도 2.4.7은 통과 [standard]. KWCAG 6.1.2 "시각적으로 구별할 수 있어야" [standard]. | **Recall:** 저시력·CVD 사용자에게 중요한 결함이 새로 잡힙니다.<br>**Noise:** 모르므로 hypothesis로 둡니다.<br>**Usefulness:** 스웜의 시각 모델과 연결됩니다. | **H:** 심사한 SM-07 단위 ≥ 30개의 validity ≥ 0.6이면 P3 결함으로 승격합니다.<br>**Metric:** validity, κ.<br>**Data:** 공개 사이트의 초점 표시 30개 이상. | M |
| AUT-11 | ADD | **흐름 속 초점 관리 `FM-01~05` (2.4.3, 2.4.7).** 키보드 기기와 `keyboard_only` 프로필 실행, 그리고 초점 걷기에서 단계마다 `activeElement`를 기록합니다.<br>• **FM-01:** 동작 뒤 초점이 `body`나 `documentElement`로 떨어지고, 그 전 초점 요소가 DOM에서 사라짐 (P2).<br>• **FM-02:** 모달(`dialog:modal`, `[aria-modal=true]`, 문서를 덮는 `role=dialog`)이 열렸는데 1 s 안에 초점이 그 안으로 들어가지 않음 (P2).<br>• **FM-03:** 모달이 열린 상태에서 마지막 초점 요소 뒤 Tab이 모달 밖으로 나감 (P2).<br>• **FM-04:** 모달이 닫힌 뒤 초점이 트리거나 그 다음 논리 요소로 돌아오지 않음 (P3).<br>• **FM-05:** 초점이 크기 0, 투명도 0, 뷰포트 밖(스크롤해도 안 보임)인 요소에 멈춤 (P2, 2.4.7).<br>• 모두 profile-invariant이고 `serves: [keyboard_only, switch_access, screen_reader]`입니다. | 2.4.3 Understanding [standard]. Flow-A11y의 대화상자 초점 이동·가두기·복귀 [snippet]. Lighthouse `managed-focus`·`focus-traps`는 수동 감사 [derived]. GOV.UK 라이트박스 장벽 0–1/13 [derived]. KWCAG 6.1.2 "논리적으로 이동" [standard]. | **Recall:** 페이지 스캐너가 구조적으로 못 보는 결함이 새로 잡힙니다.<br>**Noise:** FM-02/03은 낮고, FM-04는 중간입니다(P3).<br>**Usefulness:** 에이전트 메모 `dead_end` 등의 결정적 쌍이 됩니다 (LAT-09). | **H:** FM이 GOV.UK 라이트박스 장벽 3개 중 ≥ 2개와 dev-2 대화상자 결함을 잡고, clean-control FM 단위 ≤ 0.3개/시나리오입니다.<br>**Metric:** 위 수치와 심사 validity (≥ 30단위).<br>**Pass:** validity ≥ 0.8.<br>**Data:** GOV.UK 페이지, dev-2, 드라이버 단계 기록. | M |
| AUT-12 | CUT (계획에서 제외) | **시각 순서와 DOM 순서가 어긋나면 초점 순서 결함으로 세는 휴리스틱은 넣지 않습니다.** 넣더라도 hypothesis로만 둡니다. | "the focus order may match any of them" [standard]. Lighthouse `visual-order-follows-dom`은 수동 [derived]. 판정할 오라클이 없습니다. | **Noise:** 큰 소음원을 피합니다.<br>**Recall:** 약간 손해가 있으나, 명백한 경우는 AUT-11과 에이전트가 잡습니다. | 만든다면 hypothesis로 두고, 심사 validity ≥ 0.6(≥ 30단위)일 때만 승격합니다. | S |
| AUT-13 | CHANGE (동결 전 가능) | **SM-06을 2.4.11 주석에 맞춥니다.**<br>• 그 단계에서 사용자가 연 층(직전 동작의 대상이 연 메뉴·팝오버)은 제외합니다.<br>• 가린 층이 있으면 `Escape`를 눌러 봅니다. 층이 사라지고 초점이 그대로면 "초점을 옮기지 않고 드러낼 수 있음"이므로 통과입니다.<br>• 판정 대상 층에 `position:absolute`인 비모달 대화상자도 넣습니다.<br>• 일부 가림(2.4.12, AAA)은 결함이 아니라 hypothesis입니다. | 2.4.11 원문 주석과 Understanding(쿠키 배너, `scroll-padding`) [standard]. | **Noise:** 사용자가 연 메뉴에서 생기는 오탐 ↓, AAA 집계 ↓.<br>**Recall:** 2.4.11 실패는 유지됩니다. | **H:** dev-2 초점 가림 재현율은 그대로이고, clean-control SM-06 단위는 줄어듭니다.<br>**Pass:** 두 조건 모두.<br>**Data:** dev-2, `drivers/web/fixtures/focus.html`에 쿠키 배너 변형을 더한 픽스처. | S |
| AUT-14 | ADD | **이름 품질 `NQ-01~03`.**<br>• **NQ-01** (P2, measured): 이름이 개발자 식별자처럼 보임. 정규식 `^[A-Z0-9]+(_[A-Z0-9]+)+$`, `^[a-z]+([A-Z][a-z0-9]+)+$`, `\.(png\|jpe?g\|svg\|gif\|webp)$`, `^(ic\|btn\|img\|icon)[-_]`.<br>• **NQ-02a** (P3): 이름 끝에 역할 낱말이 중복됨 ("검색 버튼"이면 스크린리더는 "검색 버튼, 버튼"으로 읽음; "…button", "…링크", "…이미지"). ATF `RedundantDescriptionCheck`와 같습니다.<br>• **NQ-02b** (hypothesis): 이름이 일반어뿐임 ("button", "버튼", "image", "이미지", "icon", "아이콘", "link", "링크", "click here", "여기").<br>• **NQ-03** (hypothesis): 한 화면에서 목적지나 동작이 다른 링크·버튼이 같은 이름 (2.4.4, ATF `DuplicateSpeakableTextCheck`). | WWDC23 데모 "The label is not human-readable" (`QUOTE_TEXTVIEW`) [industry]. ATF `RedundantDescriptionCheck`, `LinkPurposeUnclearCheck`, `DuplicateSpeakableTextCheck` [industry]. ScreenAudit: LLM이 규칙 검사기보다 더 많이 찾음 (69.2 % 대 31.3 %) [snippet]. | **Recall:** 이름은 있지만 쓸모없는 경우가 새로 잡힙니다.<br>**Noise:** NQ-01과 NQ-02a는 낮고, NQ-02b와 NQ-03은 hypothesis입니다.<br>**Usefulness:** 스크린리더 경험을 직접 개선합니다. | **H:** NQ-01과 NQ-02a의 심사 precision ≥ 0.9 (각 ≥ 30단위).<br>**Pass:** 그렇지 않으면 hypothesis로 내립니다.<br>**Data:** 공개 사이트 2곳, dev-2. | S |
| AUT-15 | ADD | **ACT 예제를 모든 SM/LY/AX/FM 검사의 정밀도 관문으로 씁니다.**<br>• `scripts/ergo_act.py`(가칭)가 ACT 규칙 저장소를 고정된 커밋으로 받아, 구현한 규칙별 예제를 드라이버로 열고 해당 검사의 판정을 모읍니다.<br>• **실패 조건:** passed나 inapplicable 예제에서 실패 판정이 하나라도 나오면 CI가 실패합니다 (ACT "correct implementation" 정의).<br>• failed 예제의 탐지율은 보고만 합니다.<br>• 대상: 97a4e1, e086e5, c487ae, 2ee8b8, 59br37, oj04fd, b4f0c3, 36b590. 이 브리프의 파일럿 스크립트를 옮기면 됩니다. | ACT "Mapping To Rule" [standard]. 파일럿에서 현재 네 검사가 모두 통과 예제를 실패로 판정 [derived]. 벤치마크 작성자·탐지기·심사관이 모두 Claude라는 한계 [derived: validation-and-limits]. | **Noise:** 회귀를 막습니다.<br>**Usefulness:** 사람이 쓴 외부 오라클이 생깁니다. 저비용입니다. | **H:** 관문을 도입한 뒤 SM/LY 변경에서 통과 예제 오탐이 0으로 유지됩니다.<br>**Metric:** 규칙별 오탐과 탐지.<br>**Pass:** 오탐 0.<br>**Data:** ACT 저장소. W3C Software and Document Notice이므로 예제를 동봉하면 고지를 포함합니다 (4.1). | S |
| AUT-16 | CHANGE | **적합성 보고 형식.**<br>• profile-invariant 단위는 `screen_key` × 기기 부류마다 한 번만 적고, 규칙별로 묶습니다.<br>• 각 단위에 `wcag` (예: "2.4.7"), `kwcag` (예: "6.1.2", 없으면 null), `level` (A/AA/AAA/best-practice), `serves` ([screen_reader, keyboard_only, voice_control, low_vision, magnifier, cognitive])를 둡니다.<br>• `segments_affected`는 audience의 선언 조건과 `serves`의 교집합으로 계산합니다.<br>• 보고서에 "KWCAG 2.2에 없는 항목(1.4.4, 1.4.10, 1.4.12, 2.4.11)"을 표시합니다.<br>• best-practice와 AAA는 결함 수에 넣지 않습니다. | KWCAG 2.2 항목 목록 [standard/derived]. STF-08(profile-invariant), AP 브리프의 선언만 된 조건 [derived]. WCAG-EM 보고 요구 [standard, draft]. | **Usefulness:** 한국 조직이 인증 항목과 WCAG 추가 항목을 구분해 처리할 수 있습니다.<br>**Noise:** 보고 수 ↓.<br>**Recall:** 0 변화. | 정책입니다. 한국 실무자 2명이 보고서 10건을 보고 분류가 맞는지 확인합니다 (일치 ≥ 0.9). | S |
| AUT-17 | ADD | **화면 상태 커버리지 (WCAG-EM Step 3.3과 4.3).**<br>• 적합성 층(AX, SM, LY, FM)을 스크립트 실행과 에이전트 실행이 도달한 **모든** `screen_key`에서 한 번씩 실행합니다.<br>• 보고서에 `states_scanned`와 `rule_types_only_in_agent_states`를 둡니다.<br>• 에이전트 상태에서만 새 규칙 유형이 나오면 시나리오가 대표성이 없다는 신호로 표시합니다. | WCAG-EM 2.0 초안의 무작위 표본 10 %와 Step 4.3 [standard, draft]. Flow-A11y [snippet]. WebAIM은 홈페이지만 셈 [snippet]. | **Recall:** 흐름 뒤쪽 상태의 결함이 잡힙니다.<br>**Usefulness:** 에이전트 층이 "새 상태를 여는" 가치를 수치로 보여 줍니다.<br>**Noise:** 중복 제거가 필요합니다 (규칙과 선택자 기준). | **H:** 제품의 30 % 이상에서 에이전트 상태가 새 규칙 유형을 ≥ 1개 더합니다.<br>**Metric:** 제품별 새 유형 수.<br>**Data:** C6 실행 기록. | S–M |
| AUT-18 | KEEP | **PT-01(2.5.8)과 PC-01(1.4.3)은 자체 구현을 유지합니다.** axe `target-size`와 `color-contrast`는 끄고, 필요할 때만 진단용 교차 확인으로 씁니다. | PT-01은 레이블까지 넓힌 대상과 원 예외를 구현 [derived]. axe `target-size`는 needs review이고 덮인 대상 오탐 이슈가 있음 [industry]. | 중복 방지, 소음 ↓. | 교차 확인: dev 스위트에서 PT-01과 axe `target-size`가 다르게 판정한 요소를 표본 20개로 심사합니다. PT-01이 틀린 비율 < 10 %이면 유지합니다. | S |
| AUT-19 | ADD (낮은 우선순위) | **글자 간격 패스 (1.4.12).**<br>• 1.4.12의 네 값을 `!important` 스타일시트로 주입하고(`p`에는 `margin-bottom: 2em`), AUT-05 잘림과 픽셀 확인 겹침을 봅니다.<br>• inline `!important`로 막힌 요소는 ACT 24afc2·78fd32·9e45ec 방식의 정적 검사로 따로 표시합니다 (자기 글자가 있는 요소만; axe의 오탐 2/15를 피하기 위해).<br>• profile-invariant, `serves: [dyslexia, low_vision]`. | 1.4.12 원문과 Understanding [standard]. GOV.UK "Inadequate line height" 0/13 [derived]. 파일럿에서 axe `avoid-inline-spacing` 오탐 2/15 [derived]. | **Recall:** 작습니다.<br>**Noise:** 겹침 판정 위험이 있습니다.<br>**Usefulness:** 중간. | **H:** 심사 validity ≥ 0.8 (≥ 20단위).<br>**Data:** 공개 사이트, dev-2. | M |
| AUT-20 | CHANGE (동결 전 가능) | **의미 검사의 적용 범위를 접근성 트리 기준으로 바꿉니다.**<br>• 크기가 0이거나 화면 밖이어도, 초점을 받거나 위젯 역할이고 `ax_ignored`가 아니면 SM/AX 이름 규칙을 적용합니다.<br>• 그런 단위에는 `visible_to_sighted: false`를 달고 최대 P2로 둡니다.<br>• 비활성 입력 칸도 e086e5처럼 적용하되 P3으로 둡니다. | ACT 97a4e1·c487ae·e086e5의 적용 범위 [standard]. 파일럿에서 크기 0인 요소로 인한 미탐 [derived]. | **Recall:** ↑.<br>**Noise:** 약간 ↑ (P3 위주). | AUT-15의 ACT 관문과 dev-2 clean-control 단위로 판정합니다. 오탐 0이고 clean-control이 +0.2개/시나리오 이하이면 채택합니다. | S |
| AUT-21 | CHANGE (동결 전 가능) | **요소 수집 선택자 `INTERACTIVE`에 역할을 더합니다:** `[role=textbox]`, `searchbox`, `combobox`, `listbox`, `spinbutton`, `option`, `menuitemcheckbox`, `menuitemradio`, `treeitem`, `gridcell[tabindex]`. SM-03의 입력 칸 판정도 역할 기준으로 바꿉니다. | 파일럿: `div role=textbox` 3/9 미탐 [derived]. | **Recall:** ↑. 소음 거의 0. | ACT e086e5 관문 (AUT-15). | S |
| AUT-22 | CHANGE | **SM-04를 ACT 36b590 구조로 바꿉니다.**<br>• 대상: 오류 상태인 칸 (`ax_invalid`, `:user-invalid`, 선언된 오류 칸).<br>• **E1** (식별): `aria-describedby`/`aria-errormessage`로 연결된 오류 글자가 있거나, 같은 그룹 컨테이너(가장 가까운 `fieldset`, `[role=group]`, 레이블을 포함하는 조상) 안에 오류 글자가 있음. 48 px 상수를 대체합니다.<br>• **E2** (설명): 오류 글자가 보이고 글자로 되어 있음. 빨간 테두리나 아이콘뿐이면 실패이고, PC-03과 연결합니다.<br>• **E3** (노출): 그 글자가 접근성 트리에 있음 (`aria-hidden` 아님). 칸의 설명이나 라이브 영역에 들어 있음.<br>• E1·E3 실패는 P2, E2 실패는 P1(경로)입니다.<br>• 3.3.3(제안)은 에이전트 판단에 맡깁니다. | ACT 36b590 [standard]. GOV.UK "Errors are not identified" 1/13, "no suggestion" 0/13 [derived]. LAT-09 ER-01 [derived]. | **Recall:** 색만으로 표시한 오류와 스크린리더에 숨은 오류가 새로 잡힙니다.<br>**Noise:** 확대나 글자 크기에 영향받는 px 규칙이 없어져 줄어듭니다. | **H:** ACT 36b590 예제에서 오탐 0이고, dev-2 오류 결함의 재현율이 현재 이상입니다.<br>**Data:** ACT 9개, dev-2. | M |

### 3.2 최소한의 고정밀 추가 집합과 예상 정밀도

핵심 추가는 아래 여섯 가지입니다. AUT-08(AX 층이 켜지면 axe `meta-viewport`로 대체)과 AUT-14의 NQ-01·NQ-02a는 작은 추가입니다. AUT-10, NQ-02b·NQ-03, AUT-17, AUT-19는 hypothesis이거나 보고 기능입니다.

| 추가 | 판정 근거 | 예상 정밀도 | 근거 |
| --- | --- | --- | --- |
| AX 층 (AUT-02), WCAG 태그 violations만 | axe 규칙 | ≥ 0.9 | axe 설계 원칙 [industry]. 도구 정확성이 대체로 > 93 % (Vigo) [snippet]. 파일럿 0/41 [derived]. 오탐 이슈가 몰린 규칙(`scrollable-region-focusable`)은 hypothesis로 둡니다. |
| CDP 이름 기반 SM-01/SM-03 (AUT-01, AUT-20, AUT-21) | 브라우저 이름 계산 | ≥ 0.95 | 파일럿 0/41, 탐지 96 % [derived]. 남는 위험은 브라우저마다 이름이 다른 경우입니다 (Safari/VoiceOver 미검증). |
| 리플로 RF-01 (AUT-06) | 문서 가로 스크롤 + 2차원 예외 | ≥ 0.9 (RF-01), 약 0.8 (RF-02·03) | 문서 수준 넘침은 객관적인 측정입니다. 예외 목록 누락이 주된 위험입니다 [opinion]. |
| 확대·글자 크기 잘림 (AUT-05, AUT-07) | ACT 59br37 정의 | ≥ 0.9 (잘림), 약 0.8 (겹침, 픽셀 확인 뒤) | 파일럿 ACT 0/9 (fit) [derived]. VISER가 보여 준 보이지 않는 실패 [snippet]. |
| 보이는 초점 v2 (AUT-09) | 뷰포트 전체 무변화 | ≥ 0.95 | ACT 정의 자체가 가장 약한 조건입니다. 남는 위험은 캡처 타이밍 (80 ms settle) [derived]. |
| 초점 관리 FM-02·FM-03·FM-05 (AUT-11) | 모달 상태와 `activeElement` | 약 0.85–0.9 | 규칙이 결정적입니다. 사용자 정의 모달의 인식 누락은 미탐 쪽 위험입니다 [opinion]. FM-01은 약 0.8, FM-04는 약 0.7이라 P3에 둡니다. |

**axe에 맡기고 새로 구현하지 않을 것:**

- 1.1.1: `image-alt`, `role-img-alt`, `svg-img-alt`, `input-image-alt`, `area-alt`
- ARIA 유효성: `aria-allowed-attr`, `aria-required-attr`, `aria-required-children`, `aria-required-parent`, `aria-valid-attr`, `aria-valid-attr-value`, `aria-roles`, `aria-hidden-focus`, `nested-interactive`
- 문서: `document-title`, `html-has-lang`, `html-lang-valid`, `valid-lang`, `frame-title`
- 구조: `list`, `listitem`, `definition-list`, `td-headers-attr`, `th-has-data-cells`, `duplicate-id-aria`
- 기타: `autocomplete-valid`, `select-name`, `input-button-name`, `link-in-text-block`, `scrollable-region-focusable` (hypothesis 등급)

**자체 구현을 유지할 것:** 2.5.8(PT-01), 1.4.3·1.4.11(PC-01·PC-02), 그리고 axe에 없는 초점·확대·리플로·흐름 검사 전부.

### 3.3 axe 결과를 스킬 계약에 매핑하는 규칙 (AUT-02 세부)

- `check_id` = `"AX-" + rule.id`. `element_key` = axe `target`의 마지막 CSS 선택자 + `|` + AX 이름. 같은 선택자의 SM 요소가 있으면 `element_ids`로 연결합니다.
- **category** (axe `cat.*` 태그 기준):
  - `cat.color` → `perception`
  - `cat.sensory-and-visual-cues` → `meta-viewport`는 `layout`, 나머지는 `perception`
  - `cat.keyboard`, `cat.name-role-value`, `cat.aria`, `cat.forms`, `cat.text-alternatives`, `cat.language`, `cat.parsing`, `cat.semantics`, `cat.structure`, `cat.tables` → `semantics`
  - `cat.time-and-media` → `cognition`
- **severity:**
  - `impact` ∈ {critical, serious}이고 요소가 과업 경로나 primary이면 P1, 아니면 P2
  - `moderate`는 WCAG A이면 P2, 아니면 P3
  - `minor`는 P3
  - `incomplete`는 tier `hypothesis`
  - best-practice와 experimental 태그는 기본으로 실행하지 않습니다
- `measurement` = `{name: "axe_rule", value: rule.id, unit: "rule", impact, wcag: [...]}`, `refs` = `["REF-axe-core-4.13", "WCAG " + sc]`.
- **profile-invariant:** `PROFILE_INVARIANT_CHECKS`에 접두사 규칙 `AX-`를 더합니다.
- **benchmark:** heldout-2의 `taxonomy_ref`(WCAG SC)와 맞추려면 `wcag` 필드가 필요합니다. 사전등록된 C1–C6은 그대로 두고, AX 층을 켠 결과는 **추가 구성 C7**(C3 + AX)로 수정 2에 미리 선언한 뒤에만 보고합니다.
- **실행 시점:** 단계의 `after` 스냅숏을 찍은 뒤, 타이밍 창을 측정하는 동안이 아닐 때 실행합니다 (CG-03 지연 측정을 흐리지 않기 위해). 실패하면 `axe: {error}`만 남기고 실행을 계속합니다.

### 3.4 동결 전과 동결 후, 그리고 작업 순서

heldout-2는 아직 기록 전입니다 (사전등록 수정 1). 아래 1단계는 **heldout-2 내용과 무관한 외부 근거(ACT 원문과 예제)**로만 정한 수정입니다. 넣기로 하면 수정 2에 적고 동결합니다. 2단계 이후는 동결 뒤 dev-2와 외부 자료로만 개발하고, 다음 held-out에서 평가합니다.

1. **동결 전 (각 S):**
   - AUT-15 ACT 관문을 먼저 만듭니다. 이후 수정의 회귀 시험입니다.
   - AUT-04 (SM-02), AUT-05 (LY-01), AUT-09 (SM-05), AUT-13 (SM-06), AUT-21
   - AUT-20의 CDP 없는 형태: `a11y.focusable`이 참이면 크기·가시성과 무관하게 이름 규칙을 적용합니다. `ax_ignored` 기준은 AUT-01과 함께 넣습니다.
   - AUT-03의 SM-03b 이름 변경
   모두 ACT 예제에서 오탐 0을 확인한 뒤에만 넣습니다. 확인하지 못하면 넣지 않고 현 상태로 동결합니다.
2. **동결 뒤 1주차:** AUT-01 (CDP 이름), AUT-02 (AX 층, C7로 보고), AUT-08, AUT-16.
3. **2주차:** AUT-11 (초점 관리), AUT-06 (리플로), AUT-07 (글자 크기, AP-09의 `text_scale` 면과 함께), AUT-22.
4. **그 뒤:** AUT-14, AUT-17, AUT-10, AUT-19. AUT-12는 하지 않습니다.
5. **외부 평가:** GOV.UK 장벽 페이지와 공개 사이트 2곳에서 AUT-02의 H1–H3, AUT-06, AUT-07, AUT-11의 validity를 심사합니다. 심사는 LAT-14의 패널 규칙을 따르고, 가능하면 사람 심사관을 1명 포함합니다.

## 4. Risks, open questions and what could not be verified (위험, 열린 질문, 확인하지 못한 것)

### 4.1 확인하지 못했거나 일부만 확인한 것

- **Deque 57 %** [snippet]: deque.com과 보도자료 사이트가 막혀 발췌만 봤습니다. 이 수치는 이슈 건수 가중치입니다. 발생 빈도가 높은 유형(대비 등)이 차지하는 몫을 원문에서 확인하지 못했습니다. 성공 기준 개수 기준의 커버리지(Vigo: 최대 50 %)와 섞어 비교하면 안 됩니다.
- **Vigo et al. 2013, WebAIM Million 2026, ACT 구현 보고서 수치** [snippet]: w3.org, webaim.org, dl.acm.org가 막혔습니다. ACT 구현 수치는 axe-core 4.10.2 기준이라 4.13과 다를 수 있습니다.
- **논문 수치가 없는 것:** KAFE(FSE 2021), 대화상자 키보드 실패(ICSE 2023), 리플로 탐지(ICSE 2024), Flow-A11y(2026), A11yLTLNav(2026)의 정밀도·재현율은 확보하지 못했습니다. 존재와 주장만 인용했습니다.
- **VISER, Groundhog/TaskAudit, ScreenAudit의 수치** [snippet]: 초록이나 발췌 수준입니다.
- **W3C 규범 문장:** W3C GitHub의 main 브랜치 원본에서 읽었습니다. 권고안과 편집상 차이가 있을 수 있습니다. 인용한 성공 기준 문장은 WCAG 2.2 권고안의 문장과 일치한다고 봤지만, 한 글자씩 대조하지는 않았습니다. WCAG-EM은 **2.0 초안**입니다.
- **Apple 감사 유형의 의미:** 공식 문서의 설명문이 비어 있습니다. `hitRegion`, `parentChild`, `action`이 정확히 무엇을 검사하는지는 확인하지 못했습니다.
- **Lighthouse:** 가중치만 확인했습니다. 감사별 점수 방식(요소 하나만 실패해도 감사 전체가 실패하는지)은 확인하지 않았습니다.
- **KWCAG 2.2 목록:** a11ykr의 공개 HTML에서 읽었습니다. 국립전파연구원 표준 원문과는 대조하지 않았습니다.
- **Roselli 2026:** 모바일 브라우저가 OS 글자 크기를 따르는지에 관한 서술은 블로그 발췌이고, Chrome 버전에 따라 바뀔 수 있습니다.
- **라이선스 해석:** MPL-2.0 조항은 원문을 인용했지만, 동봉·선택적 의존성에 관한 결론은 법률 자문이 아닙니다.
- **재사용 조건:** ACT 예제를 동봉하려면 W3C Software and Document Notice를 포함해야 합니다 (`pages/license.md`, 확인함). GOV.UK 감사 저장소는 MIT(Crown Copyright, GDS)입니다 (확인함). 페이지 내용은 OGL v3입니다.
- **파일럿의 한계** [derived]:
  - 규칙당 예제 5–38개로 작고, 경계 사례 위주이며, 공개 자료라 blind가 아닙니다.
  - SM-02와 LY-01의 새 방식은 첫 실행 결과를 본 뒤 고쳤으므로 **예제에 맞춘 값(fit)**입니다.
  - Chromium 한 버전(1194)에서만 실행했습니다.
- **3.2의 예상 정밀도**는 측정값이 아니라 [opinion]/[derived] 추정입니다. AUT-02, AUT-06, AUT-07, AUT-11의 실험으로 대체해야 합니다.

### 4.2 권고안의 위험

- **소음 폭증 (AUT-02):**
  - 실제 사이트는 쪽당 오류가 평균 56.1개이고, 낮은 대비만 34건입니다 [snippet].
  - AX 결과를 요소마다 세면 보고서가 쓸 수 없게 됩니다. 문제 단위(UEM-02)를 (시나리오, 규칙, 조건)으로 묶고, 인스턴스는 목록으로만 보여 줘야 합니다.
  - `color-contrast`를 끄는 것도 같은 이유입니다. PC-01과 중복됩니다.
- **버전 흔들림:** axe와 Chromium 버전이 바뀌면 결과가 바뀝니다. 버전을 고정하고, 번들에 `axe.version`과 `browser.version`을 기록합니다.
- **CDP `Accessibility`는 experimental 도메인입니다.** 바뀌거나 빠질 수 있습니다. 대체 경로(`accNameSrc`, `ariaSnapshot`)와 selftest를 둡니다.
- **다른 플랫폼과의 차이:**
  - Chromium의 이름이 한국 스크린리더(센스리더, NVDA, TalkBack, VoiceOver)가 실제로 읽는 이름과 같다는 보장은 없습니다.
  - Android WebView와 Samsung Internet은 Chromium 계열이지만, iOS WKWebView는 WebKit입니다. iOS 사용자가 많은 audience라면 WebKit 확인이 필요합니다.
- **비용:**
  - 큰 페이지에서 전체 AX 트리와 axe 실행은 초 단위가 될 수 있습니다 [opinion]. 새 `screen_key`에서만 실행하고, 필요하면 `getPartialAXTree`로 줄입니다.
  - 리플로와 글자 크기 패스는 스냅숏을 늘립니다.
  - SPA에서는 상태를 다시 열기 어렵습니다. 같은 페이지에서 `setViewportSize`로 바꾸는 방식이 필요한데, 반응형 JS가 상태를 바꿀 수 있습니다.
- **글자 크기 에뮬레이션은 합성 조작입니다.** 요소마다 글자 크기를 곱하는 방식은 Chrome Android의 font scale이나 text autosizer와 같지 않습니다. 결과에는 `manipulation: "text_scale_emulated"`를 달고 최대 P2로 두어야 합니다.
- **ACT 관문의 과적합:** ACT 예제는 경계 사례에 치우쳐 있습니다. 예제만 통과하도록 검사를 맞추면 실제 제품에서의 정밀도는 보장되지 않습니다. dev-2와 실제 제품 심사를 함께 써야 합니다.
- **한국어 완화 규칙의 미탐:** 조사 완화(한글 토큰 접두 일치)가 진짜 불일치를 가릴 수 있습니다 (예: "삭제"와 "삭제하기"는 통과). 실제 음성 명령 시험 전까지는 두 판정(ACT 엄격, 한국어 완화)을 모두 기록해야 합니다.
- **heldout-2와의 관계:** 동결 전에 SM/LY를 바꾸면 사전등록 H1이 재는 대상이 바뀝니다. 수정 2에 적어야 합니다. AX 층은 C1–C6을 바꾸지 않도록 C7로 따로 보고해야 비교가 유지됩니다.
- **audience 연결의 공백:** audience 파일이 `screen_reader`, `keyboard_only`를 선언하지 않으면 적합성 단위의 `segments_affected`가 비게 됩니다. 법적 의무가 있는 적합성 실패가 우선순위에서 밀리지 않도록, 적합성 단위는 audience와 무관하게 항상 보고해야 합니다.

### 4.3 열린 질문

1. Android Voice Access 등 한국어 음성 제어는 "장바구니 담기"라고 말했을 때 이름이 "상품을 장바구니에 담기"인 링크를 실행하는가? 이 답에 따라 SM-02의 한국어 규칙이 정해집니다.
2. 한국 60대 이상 사용자가 실제로 쓰는 글자 크기 배율은 얼마인가 (One UI 글자 크기 단계, Chrome 텍스트 배율)? AP-09의 Appt 수치는 한국 자료가 아닙니다.
3. AAA(2.4.12, 2.4.13)와 best practice를 보고서에 아예 보이지 않게 할지, hypothesis 목록에만 둘지. 유용성과 소음의 균형을 실제 팀 반응(STF-02, UEM-15의 disposition)으로 정해야 합니다.
4. 적합성 층의 "커버리지"는 프로필 커버리지(k/n)와 다른 말로 표현해야 합니다. 예: "상태 n개, 규칙 m개 적용". 보고서 문구를 정해야 합니다.
5. 공개 사이트에서 axe violations의 규칙별 정밀도는 한국 사이트(정부·금융·쇼핑)에서도 비슷한가? 한국 사이트 표본으로 AUT-02의 H2를 따로 보고해야 합니다.
