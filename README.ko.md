# Remorsearch UX QA

[English](README.md) | 한국어

Remorsearch(리모서치) UX QA는 이미 만든 제품의 UI와 UX를 점검하고 고치는 Claude Code·Codex 스킬입니다. URL이나 저장소를 주면 휴대폰과 노트북 화면에서 페이지를 끝까지 훑어 의심 지점마다 테두리를 그린 화면 조각을 보여 줍니다. 요청한 과업을 직접 수행해 보고, 원하면 관련 사용자 경험을 조사하며, 작은 수정을 적용한 뒤 같은 과업을 다시 실행할 수 있습니다.

## 하는 일

| 구성 요소 | 하는 일 | 필요한 것 |
| --- | --- | --- |
| **persona-qa** | 화면 UI QA. 명령 하나로 페이지를 휴대폰과 노트북에서 위부터 끝까지 기록하고, 잘린 글자, 고정 바에 계속 가려지는 글자, 겹친 글자, 몇 px 어긋난 정렬, 고르지 않은 목록 간격, 명도 대비, 터치 크기, 리플로를 측정합니다. 에이전트는 후보마다 화면 픽셀로 확인한 뒤 과업, 입력 양식, 키보드 사용과 접근성(KWCAG 2.2, WCAG 2.2)을 점검합니다. | 접속할 수 있는 URL, Node.js 22, 번들 Playwright 드라이버 |
| **research** | 커뮤니티, 댓글, 리뷰, 공식 자료에서 과업과 관련된 경험, 우회 방법, 반대 사례를 찾고 원문 맥락과 조사 공백을 남깁니다. | 읽어도 되는 출처. 유튜브 댓글은 본인의 YouTube Data API 키(`REMORSEARCH_YOUTUBE_API_KEY`)를 씁니다. |
| **ergonomics**(실험적) | 시뮬레이션한 프로필로 도달, 터치, 지각, 시간을 선별 점검합니다. | 관련 시나리오. 모델 결과는 실제 기기 근거와 따로 기록합니다. |
| **loop** | 범위를 정한 수정, 현재 빌드 재실행, 회귀와 의도 보존 점검을 기록합니다. | 사용하는 브라우저와 디자인 도구. Figma로 먼저 설계하는 프로젝트와 코드로 바로 고치는 프로젝트 모두에 맞춥니다. |

구성 요소는 고르지 않아도 됩니다. UI 점검, UX 개선, 조사, 접근성 검토 가운데 원하는 일을 말하면 그 요청에 필요한 부분만 불러옵니다.

탐지기 코드를 보지 않고 만든 렌더링 결함 28개, 미끼 11개, 결함 없는 쌍 페이지 4개의 벤치마크([`visual-layout-20261018.md`](docs/validation/visual-layout-20261018.md))에서 스캔의 측정 검사는 처음 실행에 19개를 찾았습니다. 이 검사들을 넣기 전에는 3개였고, 미끼와 결함 없는 페이지에는 새 발견이 없었습니다. 그 뒤 놓친 결함을 보고 탐지기를 고쳐 같은 페이지에서는 25개를 찾습니다. 25개는 그 페이지에 맞춘 값이고, 처음 보는 페이지에서 잰 값은 19개입니다. 문서대로 설치한 Ubuntu 24.04에서도 같은 재현율이 나왔습니다.

스킬을 쓰면 에이전트가 QA를 더 잘하는지는 아직 보여 주지 못했습니다. 오픈소스 관리자가 실제로 보고받고 고친 레이아웃 버그 12개([`real-layout-bugs`](docs/validation/real-layout-bugs/README.md))로 비교했을 때 1.0.0은 두 모델 어느 쪽도 개선하지 못했습니다. 모델마다 세 번씩 돌린 결과, GPT-6.1 Sol은 알려진 결함 34개 중 스킬을 쓰고 13개, 쓰지 않고 18개를 찾았고 DeepSeek 4.1 Flash는 15개와 14개를 찾았습니다. 휴대폰 화면이 옆으로 밀리는 사례 4개는 양쪽 모두 나올 때마다 찾았고, 버튼보다 3.6px 낮은 검색창 같은 미세한 사례 5개는 양쪽 모두 놓쳤습니다. 위 벤치마크 페이지로 한 [에이전트 비교](docs/validation/agent-comparison-20261018/README.md)에서는 스킬을 쓴 쪽이 28개 중 28, 28, 24개, 쓰지 않은 쪽이 28, 27, 22개를 찾았습니다. 탐지기를 그 페이지에 맞춰 고친 뒤라 스킬 쪽에 유리한 비교입니다.

## 설치

```sh
git clone https://github.com/remorser58/remorsearch_UX_QA.git
cd remorsearch_UX_QA
python3 scripts/install.py --target codex
```

`--target claude`는 `~/.claude/skills/remorsearch-ux-qa`에, 기본값 `codex`는 `~/.codex/skills/remorsearch-ux-qa`에 설치합니다. 원하는 폴더에 넣으려면 `--destination /path/to/folder`를 쓰세요.

설치 스크립트는 macOS, Linux, WSL에서 Python 3.10 이상, Node.js 22(>=22 <23), npm이 있는지 먼저 확인하고 나서 파일을 씁니다. 고정 버전 Playwright 드라이버와 Chromium을 임시 복사본에서 준비하고 Chromium을 한 번 실행해 본 다음에야 설치 폴더로 옮깁니다. 내려받기가 실패하면 기존 설치는 그대로 남고, 갱신할 때는 이전 폴더를 `remorsearch-ux-qa.backup-<timestamp>.tar.gz`로 먼저 보관합니다. 고정 버전인 Playwright 1.56.1의 브라우저 내려받기가 Node.js 24.16 이상에서 멈추기 때문에 Node.js 22가 필요합니다([microsoft/playwright#40724](https://github.com/microsoft/playwright/issues/40724)). 기본 `python3`가 3.10보다 낮으면 스킬 폴더에서 `python3 scripts/find_runtime.py`를 실행하세요. 쓸 수 있는 Python과 Node.js 경로를 알려 주며 아무것도 설치하지 않습니다. Linux에서는 Chromium에 시스템 라이브러리가 더 필요합니다. 실행 확인이 실패하면 `npx -y playwright@1.56.1 install-deps chromium`을 한 번 실행하고(Debian, Ubuntu 기준이며 sudo 암호를 묻습니다) 설치 스크립트를 다시 실행하세요.

Claude Code에서는 이 저장소를 플러그인 마켓플레이스로 추가해 설치할 수도 있습니다. `/plugin marketplace add remorser58/remorsearch_UX_QA` 다음 `/plugin install remorsearch-ux-qa@remorsearch`를 실행하세요. 플러그인으로 설치하면 설치 스크립트의 브라우저 준비 단계를 거치지 않아서, 첫 스캔이 멈추면서 한 번만 실행하면 되는 준비 명령(플러그인 안 `drivers/web`에서 `npm ci`와 `npx playwright install chromium`)을 알려 줍니다.

계정은 사용자가 준비합니다. 유튜브 댓글에는 YouTube Data API 키가, Figma 비교에는 Figma 접근 권한이 필요합니다. 유지보수용 패키징과 무결성 검사는 [빌드와 배포 전 검사](docs/release.md)에 있습니다.

## 사용법

평소 말투로 요청하거나 스킬 이름을 부르면 됩니다(Claude Code는 `/remorsearch-ux-qa`, Codex는 `$remorsearch-ux-qa`).

```text
/remorsearch-ux-qa Check the UI of https://app.example.test on a phone and a laptop.
/remorsearch-ux-qa 이 화면 UI QA해줘: https://app.example.test/checkout
/remorsearch-ux-qa Improve our app UX. Repository: /path/to/product
/remorsearch-ux-qa Find out why people abandon our checkout, from reviews and community posts.
/remorsearch-ux-qa 간편결제 실패 경험을 한국어 커뮤니티와 앱 리뷰에서 근거 붙여서 정리해 줘.
```

UI 점검은 측정 스캔 한 번으로 시작합니다. 직접 실행해도 됩니다.

```sh
python3 ~/.codex/skills/remorsearch-ux-qa/scripts/ergo_qa.py scan --url https://app.example.test --out scan-out
```

기본으로 `galaxy-s24`(360×780)와 `laptop-1440`(1440×900)에서 페이지를 기록하고(`--device ID`로 바꿀 수 있습니다), 후보마다 한 줄씩 적은 `scan-out/scan.md`, `scan.json`, 의심 영역에 테두리를 그린 `crops/`를 만듭니다. 후보는 측정값입니다. 에이전트는 화면 조각과 전체 스크린샷을 직접 열어 본 뒤에 보고하고, 제외한 후보도 이유와 함께 적습니다. 페이지를 열지 못했으면 깨끗한 결과로 처리하지 않고 점검하지 못한 범위로 남깁니다.

그다음 요청한 과업(정상 흐름, 필수 항목 누락, 검증 오류, 복구, 키보드)을 수행하고, 요청이 있을 때만 조사를 더합니다. 보고서는 판정과 최대 세 가지 조치, 근거와 수정안을 붙인 발견, 점검하지 못한 범위로 이루어집니다.

## 근거 규칙

- 모든 진술은 관찰, 추론, 미확인 가운데 하나로 표시합니다. 검증된 발견은 같은 빌드에서 끝까지 실행한 기록과 연결합니다.
- 스캔 후보는 화면 픽셀로 확인한 뒤에만 발견으로 셉니다. 캡처를 저장했다고 검토한 것으로 보지 않습니다.
- 합성 페르소나와 시뮬레이션 프로필은 테스트 조건을 만듭니다. 실제 사용자의 선호, 비율, 불편을 보여 주지 않습니다.
- 커뮤니티 글은 그런 상황이 있다는 사실만 보여 주고, 얼마나 자주 일어나는지는 알려 주지 않습니다.
- 조사와 리뷰 요청은 읽기만 합니다. 개선 요청은 그 범위 안의 되돌릴 수 있는 일반 수정을 허용하고, 배포·게시·계정 변경은 따로 허락을 받습니다.
- 스킬은 프로젝트의 디자인 기준과 규칙을 따르고 자체 스타일 규칙을 더하지 않습니다. 디자인을 Figma에서 관리하면 Figma부터 고치고, 코드로 바로 고치는 프로젝트는 수정 전후 캡처를 남깁니다.

## 공개 페이지 읽기

조사는 계정 없이 누구나 읽을 수 있는 내용만 읽습니다.

- **도구.** 에이전트 호스트가 가진 가장 좋은 브라우저 도구(에이전트형 브라우저, 그다음 Playwright MCP나 번들 페이지 리더 `read_page.mjs` 같은 자동화 브라우저)를 쓰고, 그다음 자체 리더, 마지막으로 일반 검색과 가져오기를 씁니다. 마지막 단계의 결과는 단서로만 씁니다. 출처마다 어떤 도구로 읽었는지 기록합니다.
- **리더**(`scripts/ux_research.py`)는 필요한 만큼만 단계를 올라갑니다. 공식 피드나 API, 신원을 밝힌 요청 한 번, 사이트의 모바일이나 피드 버전, 실제 브라우저 렌더링 순서입니다.
- **멈춤.** 로그인, 유료 구독, 회원 전용 게시판, 연령 확인, CAPTCHA 같은 사람 확인, 봇 차단, robots.txt와 AI·TDM 거부 표시, 요청 제한, 삭제된 글에서 멈추고 각각을 조사 공백으로 보고합니다. 멈춘 사이트는 그 실행에서 다시 읽지 않습니다. 플랫폼 약관이 자동 수집을 제한하는 곳에서도 멈춥니다(`terms_restricted`). 신원을 숨기지 않고, 검색 결과 페이지를 읽지 않으며, 같은 호스트에는 기본 8초 이상 간격을 두고 한 번에 한 페이지만 요청합니다.
- **개인정보.** 인용은 짧게 줄이고, 작성자는 솔트를 넣은 키로 바꾸며, 임시 페이지 원문은 프로젝트 밖에 두었다가 실행을 마칠 때 지웁니다. 전화번호, 이메일 주소, 신분증·카드·계좌 번호, IP 주소는 에이전트가 읽기 전에 지웁니다.

자세한 내용: [`public-page-access.md`](skills/remorsearch-ux-qa/references/research/public-page-access.md)

## 한국어 리서치

한국 제품, 한국어 사용자, 한국어 보고서에는 [`overview.md`](skills/remorsearch-ux-qa/references/research/korea/overview.md)에서 시작하는 한국어 팩을 함께 씁니다. 페르소나 QA에는 [`kwcag-2.2.md`](skills/remorsearch-ux-qa/references/persona-qa/kwcag-2.2.md)의 접근성 메모를 더합니다. 팩에는 접근 경로와 약관 상태를 정리한 한국 채널 27곳의 지도, 한국어 검색어 작성법, 광고·리뷰 보상 표시, 한국 통계의 출처 카드, 법률 점검표(법률 자문은 아닙니다), 한국어 보고서 양식이 들어 있습니다.

한국 플랫폼은 자동 수집을 제한하는 곳이 많습니다. 디시인사이드, 네이버, 쿠팡, X, 당근, Reddit은 사용자가 현재 약관을 확인하고 서면 허락을 받아야 리더가 페이지를 읽습니다. 유튜브는 본인 키로 Data API를 통해서만 읽고 YouTube API 약관을 따릅니다(저장한 항목은 가져온 지 30일 뒤 만료됩니다). [항목과 확인 절차](skills/remorsearch-ux-qa/references/research/public-page-access.md#171-entries)를 참고하세요.

## 저장소 구성

```text
skills/remorsearch-ux-qa/      the installable skill (installed by scripts/install.py)
  SKILL.md                     entry point
  references/                  mode workflows and reference cards, loaded per task
  scripts/                     CLIs: ergo_qa (scan and analysis), ux_research, ux_loop, validate_bundle
  drivers/web/                 Playwright driver (Node.js 22)
  ergoqa/ uxloop/ uxresearch/  Python packages behind the CLIs
scripts/                       installer and release checks
benchmarks/                    benchmark suites with answer keys
tests/                         unit tests and fixtures (offline)
docs/                          design notes, research notes and validation records
```

## 개발

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
python3 skills/remorsearch-ux-qa/scripts/smoke_loop.py
(cd skills/remorsearch-ux-qa/drivers/web && npm ci && npx playwright install chromium && node selftest.mjs)
python3 skills/remorsearch-ux-qa/scripts/ergo_bench.py --suite benchmarks/mobile-commerce --out .ergo-bench/mobile
python3 scripts/check_release.py --output dist/release-check
```

테스트는 네트워크에 접속하지 않고, 리더 테스트는 127.0.0.1의 로컬 서버를 씁니다. loop CLI 설명은 [`references/loop/cli.md`](skills/remorsearch-ux-qa/references/loop/cli.md)에 있습니다. 공개한 수치를 어떻게 만들었고 어떻게 다시 재는지는 [검증 기록](docs/validation/README.md)에 정리했습니다.

## 한계

- 스캔은 Chromium에서 기기를 흉내 냅니다. Safari/WebKit과 실제 기기는 따로 실행해야 합니다. 모바일 Safari는 문서화한 호스트 경로(iOS 시뮬레이터와 safaridriver)로, 네이티브 iOS 앱은 XCUITest 근거를 가져와 확인합니다.
- 스캔은 `--allow-origin`으로 더 지정하지 않으면 페이지와 같은 출처의 자원만 불러옵니다(글꼴·이미지 CDN 등). 막힌 요청과 기록하지 못한 페이지 구간은 결과에 따로 적습니다.
- 측정 후보는 위치와 크기, 명도 대비, 터치 크기, 이름을 다룹니다. 위계, 문구, 브랜드 적합성, Figma 일치는 에이전트가 화면 픽셀과 기준 디자인을 보고 판단합니다.
- 정렬과 간격 검사는 같은 종류의 형제 블록끼리 비교해 P3 후보로 보고합니다. 의도한 어긋남도 후보로 나올 수 있고, 화면을 확인한 뒤 제외합니다.
- `file://` 페이지에서 스캔은 그 페이지가 있는 폴더와 하위 폴더의 파일만 불러옵니다. 그래서 상위 폴더의 스타일시트(`../css/app.css`)는 막히고, 페이지는 그 스타일 없이 측정됩니다. 막힌 요청은 `scan.md`에 적힙니다. 리플로·텍스트 간격·짧은 창 검사(RF-01~RF-03)는 페이지를 http(s)로 열고 Chromium을 보통 방식으로 띄워야 제대로 동작합니다. `file://` 페이지에서는 이 검사들이 쓰는 복제 화면에 페이지 스타일이 빠지고, `REMORSEARCH_CHROMIUM_ARGS=--single-process`를 쓰면 검사 단계가 실패하는데 `scan.md`에는 아무 표시가 없습니다(실패 기록은 `runs/*/run.json`에만 남습니다). 로컬 파일은 `python3 -m http.server`로 띄우고, 샌드박스가 허용하면 Chromium을 보통 방식으로 실행하세요.
- RF-01은 WCAG 1.4.10과 같이 표 같은 2차원 콘텐츠를 예외로 둡니다. 그래서 표 때문에 휴대폰 화면이 옆으로 밀려도 보고하지 않습니다. 실제 버그 페이지에서 스캔은 버튼보다 3.6px 낮은 입력창, 버튼 중앙보다 2px 내려간 확대 기호, 중앙에서 4px 비켜난 로고 같은 작은 어긋남도 잡지 못했습니다.
- 인간공학 모델은 보정하지 않았고 벤치마크도 작으며 에이전트가 만들었습니다. 결과는 선별 점검으로만 쓰세요.
- 리더는 robots.txt와 AI·TDM 거부 표시를 지키고 봇 확인에서 멈추므로, 일부 사이트는 조사 공백으로 남습니다.

## 라이선스

MIT입니다. [`LICENSE`](LICENSE)를 참고하세요. 외부 자료와 참고 출처는 [`THIRD_PARTY_NOTICES.md`](skills/remorsearch-ux-qa/THIRD_PARTY_NOTICES.md)에 정리했습니다.

도움받은 프로젝트: 공개 페이지 리더와 조사 게이트는 fivetaku의 [insane-search](https://github.com/fivetaku/insane-search)와 [insane-research](https://github.com/fivetaku/insane-research)(둘 다 MIT)를 살펴본 뒤 설계했습니다. insane-search 원본 도구는 출처 기록과 원 라이선스를 그대로 둔 채 참고 자료로 함께 들어 있습니다. 한국어 팩과 이 README의 두 언어 구성은 [K-skill](https://github.com/NomaDamas/k-skill)(MIT), DaleSeo의 [korean-skills](https://github.com/DaleSeo/korean-skills)(MIT), [SoDam-Persona-Codex](https://github.com/sodam-ai/SoDam-Persona-Codex)(Apache-2.0), fivetaku의 [gptaku_plugins](https://github.com/fivetaku/gptaku_plugins)(MIT)에서 아이디어만 얻었습니다. 플랫폼 이름은 설명을 위해 썼을 뿐이며 어느 곳과도 제휴 관계가 없습니다.
