# 게임 QA, 게임 접근성, 플레이테스트 실무 (Game QA, game accessibility and playtesting practice)

작성: 2026-09-28. 후보 ID 접두사: `GQA-`. 사용자 지시에 따라 본문은 한국어로 쓰고, 표준 이름·가이드라인 번호·필드 이름·원문 인용은 영어 그대로 둡니다.

> 상태: 완료 (2026-09-28). 1–4절 모두 작성. 코드·벤치마크·검증 기록은 바꾸지 않았습니다.

**증거 태그.** [standard] 규범 문서 원문 · [paper] 동료 심사 논문, 원문 또는 저자가 공개한 논문 본문에서 확인 · [industry] 업체·기업 문서, 공개 소스 코드, 엔지니어링 블로그 · [report] 조사·정부 통계 · [snippet] 검색 발췌로만 봄(원문 미확인) · [derived] 내 계산 · [opinion] 실무자 의견(따로 밝히지 않으면 내 의견).

**이 문서와 기존 문서의 관계.** 게임 인체공학의 기초 자료는 이미 `docs/human-factors/game-ux-ergonomics.md`(이하 "게임 브리프")에 있습니다. 이 문서는 그것을 되풀이하지 않고, (1) 게임 브리프가 [R]·[V2]로 남긴 값 중 이번에 원문·소스 코드로 확인하거나 반박한 것, (2) 게임 QA 실무(인증, 플레이테스트, 자동 에이전트)에서 스킬 설계로 옮길 것, (3) GM-02~GM-06의 유지·삭제·변경·추가 판단과 그 실험 설계만 다룹니다. 다른 `qa-discipline` 문서의 후보(STF-, UEM-, AP-, LAT-, AUT-, SIT-)에 기대는 곳은 ID로 적습니다.

---

## 1. Scope and sources searched (범위와 검색한 자료)

### 1.1 질문

1. 게임 접근성 가이드라인(GAG, XAG 101–120, AbleGamers APX, The Last of Us Part II 옵션, Accessible Games Initiative 태그, CVAA)은 스킬이 브라우저 드라이버로 잴 수 있는 무엇을 요구하는가?
2. 광과민성: WCAG 2.3.1, ITU-R BT.1702, Ofcom, Trace 제안, EA IRIS는 무엇이 같고 무엇이 다른가? 화면 캡처 도구는 무엇을 잴 수 있고 무엇을 못 재는가?
3. 타이밍과 입력: QTE 수용 창, 연타 대안, 연령별 반응 시간, 입력 지연 예산, 리듬 게임 판정 창은 실제로 몇 ms인가?
4. HUD·글자·자막·안전 영역·모바일 터치 조작의 수치 기준은 무엇인가?
5. 게임 QA 실무(플랫폼 인증, 기능·규격·사용성 QA, RITE, 생체 신호, 텔레메트리, 자동 테스트 에이전트)는 결함을 얼마나 찾는가?
6. GM-02~GM-06을 각각 유지·삭제·변경·추가할 근거는 무엇이고, GM-06 연타 속도 스윕과 GM-03 수용 창 측정을 브라우저 드라이버로 어떻게 돌리는가?

### 1.2 검색 조건 (태그를 믿기 전에 읽을 것)

- 웹 검색은 30회 이하로 제한했습니다. 이 세션의 네트워크 정책이 `learn.microsoft.com`, `accessiblegames.com`, `supp.apa.org`, `frontiersin.org`, `ar5iv.labs.arxiv.org`, `jpattonassociates.com`, `static.mtv.co.uk`(Ofcom 문서 사본)을 막았습니다. 그래서 XAG 본문, Ofcom 패턴 규칙, Der & Deary 2006의 표, RITE 사례 수치는 검색 발췌([snippet])로만 봤습니다.
- GitHub 원본(raw)은 읽을 수 있었습니다. 그래서 **EA IRIS의 기본 설정 파일과 C++ 소스**, **W3C WCAG 저장소의 2.3.1 정의와 Understanding 원본**, **Trace Center의 PSE 제안 지침**, **Playwright Clock 문서 원본**, **Chrome DevTools Protocol 정의(pdl)**, **osu! 공식 위키 원본**, **StepMania 계열(OutFox) 설정 문서**는 원문으로 확인했습니다.
- W3C 문서는 `w3c/wcag`의 main 브랜치(편집 중 초안)에서 읽었으므로 권고안과 한 글자씩 대조하지는 않았습니다.

### 1.3 원문·소스로 직접 확인한 자료

- W3C, WCAG 2.x 용어 정의 "general flash and red flash thresholds" 원본. https://github.com/w3c/wcag/blob/main/guidelines/terms/20/general-flash-and-red-flash-thresholds.html [standard]
- W3C, Understanding SC 2.3.1 원본. https://github.com/w3c/wcag/blob/main/understanding/20/three-flashes-or-below-threshold.html [standard]
- Electronic Arts, IRIS 기본 설정 `config/appsettings.json`과 `src/TransitionTracker.cpp`, `src/Flash.cpp`, `src/FlashDetection.cpp`, `src/PatternDetection.cpp`. https://github.com/electronicarts/IRIS [industry]
- Trace RERC, `pseGuidelines.md`, `guidelinesFromPaper.md`(Jordan & Vanderheiden 2024, ACM TACCESS 논문의 지침 본문). https://github.com/traceRERC/pseGuidelines [paper]
- Microsoft Playwright, Clock 문서 원본 `docs/src/clock.md`. https://github.com/microsoft/playwright/blob/main/docs/src/clock.md [industry]
- Chrome DevTools Protocol, `HeadlessExperimental.pdl`(`beginFrame`). https://github.com/ChromeDevTools/devtools-protocol/blob/master/pdl/domains/HeadlessExperimental.pdl [industry]
- osu! 공식 위키 "Overall difficulty" 원본. https://github.com/ppy/osu-wiki/blob/master/wiki/Beatmap/Overall_difficulty/en.md [industry]
- Project OutFox(StepMania 계열) 설정 문서 `preferences.md`. https://github.com/TeamRizu/outfox-wiki [industry]
- Apple Human Interface Guidelines "Game controls"(2025-06-09 개정)와 "Designing for games"의 문서 데이터(JSON) 원본. https://developer.apple.com/design/human-interface-guidelines/game-controls ; https://developer.apple.com/design/human-interface-guidelines/designing-for-games [industry]
- 한국형 웹 콘텐츠 접근성 지침 2.2 게시본(비공식). https://github.com/a11ykr/kwcag22 [standard, 원문 대조 필요]

### 1.4 검색 발췌로만 본 자료 ([snippet])

- Microsoft, Xbox Accessibility Guidelines 101, 107, 116, 117, 118, 119, 120 페이지 발췌. https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/101 (나머지 번호는 같은 경로)
- Game Accessibility Guidelines: "Avoid repeated inputs (button-mashing/quick time events)", "Avoid flickering images and repetitive patterns", Intermediate 목록. https://gameaccessibilityguidelines.com/avoid-repeated-inputs-button-mashing-quick-time-events/ ; https://gameaccessibilityguidelines.com/avoid-flickering-images-and-repetitive-patterns/ ; https://gameaccessibilityguidelines.com/intermediate/
- Accessible Games Initiative 태그 페이지, Steam 태그 기사. https://accessiblegames.com/accessibility-tags/playable-without-rapid-button-presses/ ; https://access-ability.uk/2025/11/07/steam-devs-are-misusing-the-playable-without-timed-inputs-accessibility-tag-and-it-might-be-valves-fault/
- AbleGamers APX. https://accessible.games/accessible-player-experiences/design-patterns/
- The Last of Us Part II 접근성 기능. https://blog.playstation.com/2020/06/09/the-last-of-us-part-ii-accessibility-features-detailed/ ; https://www.playstation.com/en-us/games/the-last-of-us-part-ii/accessibility/
- Apple App Store Accessibility Nutrition Labels. https://developer.apple.com/videos/play/wwdc2025/224/ ; https://support.apple.com/en-us/123073
- CVAA 게임 면제 종료. https://www.gamedeveloper.com/game-platforms/cvaa-accessibility-rules-come-into-effect-for-games-as-fcc-waiver-expires
- Ofcom 섬광·패턴 지침과 Harding et al. 2005(Epilepsia). https://www.ofcom.org.uk/__data/assets/pdf_file/0021/16248/gn_flash.pdf ; https://onlinelibrary.wiley.com/doi/10.1111/j.1528-1167.2005.31305.x
- Der & Deary 2006(Psychology and Aging). https://pubmed.ncbi.nlm.nih.gov/16594792/
- Ruff & Parker 1993(Perceptual and Motor Skills). https://pubmed.ncbi.nlm.nih.gov/8337069/
- Human Benchmark 반응 시간 통계. https://humanbenchmark.com/tests/reactiontime/statistics
- Ng et al. 2012(UIST), Jota et al. 2013(CHI) 터치 지연. https://dl.acm.org/doi/10.1145/2380116.2380174
- Repp 2005 SMS 리뷰와 후속 연구. https://link.springer.com/article/10.3758/BF03206433
- Claypool & Claypool 2006(CACM). https://dl.acm.org/doi/10.1145/1167838.1167860 (원문 차단)
- Netflix Korean Timed Text Style Guide. https://partnerhelp.netflixstudios.com/hc/en-us/articles/216001127-Korean-Timed-Text-Style-Guide (원문 차단; 수치는 GitHub의 2차 요약 `MaurUppi/srt-subtitle-processor`에서 봄)
- Ubisoft 자막 사용 자료. https://news.ubisoft.com/en-us/article/1etr8zW1Vo6XCeh0UM5KJO/how-ubisoft-is-putting-the-spotlight-on-accessibility
- KOCCA 2024 게임이용자 실태조사 보도. https://zdnet.co.kr/view/?no=20250102104131 ; https://www.kocca.kr/kocca/bbs/view/B0000147/2007554.do?menuNo=204153
- Medlock et al. 2002 RITE. https://www.semanticscholar.org/paper/Using-the-RITE-method-to-improve-products;-a-and-a-Medlock-Wixon/5340ef8a91900840263a4036b0433a389b7097b2
- Mirza-Babaei et al. 2013(CHI). https://dl.acm.org/doi/10.1145/2470654.2466200
- Bergdahl et al. 2020(EA SEED), Zheng et al. 2019(Wuji), Pfau et al. 2017(ICARUS), Politowski et al. 2022. https://arxiv.org/abs/2103.15819 ; https://dl.acm.org/doi/10.1109/ASE.2019.00077 ; https://dl.acm.org/doi/10.1145/3130859.3131439 ; https://arxiv.org/abs/2202.12777
- TITAN(arXiv 2509.22170), GlitchBench(CVPR 2024), VideoGameQA-Bench(2025). https://arxiv.org/abs/2509.22170 ; https://arxiv.org/abs/2312.05291 ; https://arxiv.org/abs/2505.15952
- 게임 규격·인증 QA 업체 글(PlayStation 인증의 광과민성 평가 주장 포함). https://www.ixiegaming.com/blog/game-compliance-testing-navigating-guidelines-ratings-legal-minefields/

웹 검색은 29회 썼습니다.

### 1.5 읽은 저장소 맥락 (수정하지 않음)

`skills/remorsearch-ux-qa/references/ergonomics/`의 `workflow.md`, `human-factors-checks.md`, `persona-agent-protocol.md`, `validation-and-limits.md`; `docs/ergonomic-swarm-spec.md` §0–§7; `docs/validation/experiments/decisions.md`; `docs/human-factors/game-ux-ergonomics.md`; `docs/qa-discipline/`의 기존 브리프 6편(목차와 게임 관련 부분); 코드 `ergoqa/checks.py`(GM-02, GM-03, GM-04, GM-05, GM-06, `_mash_bursts`, `_frame_flash`), `ergoqa/params.py`(게임 상수), `ergoqa/hf/game.py`(반응 시간 분위수, 연장 섬광), `drivers/web/session.mjs`와 `page_scripts.mjs`(타이밍 창 폴링, 섬광 표본). `benchmarks/`, `.ergo-bench/`, `.claude/`는 열지 않았습니다.

---

## 2. Key knowledge (핵심 지식)

### 2.1 광과민성: 섬광과 패턴

#### 2.1.1 규범 정의 (WCAG 2.3.1)

- **일반 섬광과 적색 섬광 기준.** 다음 중 하나면 통과: 어느 1초 동안에도 일반 섬광과 적색 섬광이 각각 3회 이하, 또는 동시에 일어나는 섬광의 합친 면적이 전형적 시청 거리에서 어떤 10° 시야 안에서도 0.006 sr(10° 시야의 25%) 이하. 일반 섬광은 "최대 상대 휘도(1.0)의 10% 이상인 상반된 변화 한 쌍이고, 어두운 쪽 상대 휘도가 0.80 미만"인 것입니다. [standard]
- **예외.** 한 변이 0.1° 미만인 "미세하고 균형 잡힌 패턴"(백색 잡음, 교대 체커보드)의 깜빡임은 기준을 어기지 않습니다. [standard]
- **10° 시야의 픽셀 근사.** 1024 × 768로 볼 때 341 × 256 px 사각형이 15–17인치 화면을 22–26인치에서 보는 10° 시야를 근사한다고 정의 문서가 적습니다. [standard]
- **적색 섬광의 새 정의(WCAG 2.2).** 한쪽 상태의 R/(R+G+B) ≥ 0.8이고, 두 상태의 CIE 1976 UCS 색도 차 √((u′₁−u′₂)² + (v′₁−v′₂)²)가 0.2보다 큰 상반된 전이 한 쌍. Understanding은 sRGB → XYZ 행렬과 u′ = 4X/(X+15Y+3Z), v′ = 9Y/(X+15Y+3Z)를 그대로 적습니다. [standard]
- **HDR과 절대 휘도.** sRGB가 아닌 색 공간 콘텐츠는 가장 넓은 동적 범위 판으로 검사하고, 이때 일반 섬광은 "20 cd/m² 이상의 변화이며 어두운 쪽이 160 cd/m² 미만"(ITU-R BT.1702). 어두운 쪽이 160 cd/m² 이상이면 Michelson 대비 (L_high − L_low)/(L_high + L_low) ≥ 1/17. [standard]
- **분석 조건.** "사용자가 볼 수 있는 가장 큰 크기"로 분석합니다. 웹 페이지 안에서도, 전체 화면으로도 재생되는 동영상은 전체 화면에서 분석합니다. 반복 재생되는 짧은 클립(GIF)은 반복시키며 분석합니다. [standard]
- **CSS 픽셀 대체와 그 모호함.** Understanding 원본은 "원래의 픽셀 블록을 CSS 픽셀로 바꾸면 섬광의 합친 면적은 341 × 256 CSS px, 즉 87,296 CSS px²가 된다"고 적습니다. [standard] 그러나 정의는 "10° 시야의 25%"이므로 같은 사각형을 10° 시야로 보면 문턱은 25%인 21,824 CSS px²입니다. [derived] 두 해석은 4배 차이가 납니다. 스킬은 이 모호함을 피해 기기 픽셀 피치와 프로필 시청 거리로 0.006 sr을 직접 계산합니다(아래 2.1.5).
- **밝기와 시청 거리의 한계.** Understanding은 "명세는 사람이 실제로 고르는 시청 거리를 반영할 수 없다. 이상적인 거리보다 가까이 보는 사용자는 규범상 통과하는 섬광 면적에도 영향을 받는다. 확대·화면 돋보기 사용자도 같다"고 적습니다. [standard] 스킬의 프로필별 시청 거리 계산은 이 한계를 줄이는 방향입니다.

#### 2.1.2 방송 기준과 연구 제안 (ITU-R BT.1702, Ofcom, Harding 2005, Trace 2024)

- **Trace 제안 지침(Jordan & Vanderheiden 2024).** 어떤 1초 구간에도 기준을 넘는 휘도 전이 또는 적색 전이가 6회를 넘지 않아야 합니다(= 3회 섬광 초과 금지를 전이 수로 쓴 것). 전이는 66 ms 이내에 끝나야 하며, 66 ms보다 느린 변화는 섬광 전이가 아닙니다. 같은 방향 전이가 20 ms 이내면 같은 전이로 보고 면적을 더합니다(작업값). 앞선 가장자리가 15 ms 이하 간격인 65 Hz 이상의 섬광은 위험이 크게 줄어듭니다. [paper]
- **Trace의 면적 문턱 세 가지.** (a) 화면 크기와 시청 거리를 알 때: 10° 시야의 0.006 sr(25%). (b) 크기를 모르는 TV 전용 콘텐츠: 화면의 25%. (c) 종류·크기를 모르는 화면: 0.0213°짜리 CSS px 기준으로 어떤 416 × 416 px 부분 영역의 25%(= 43,264 CSS px²), 사용자 확대 없이 가장 큰 크기로 표시할 때. 기준 화면은 23인치 Full HD 모니터를 71.1 cm에서 보는 것입니다. Trace는 TV의 "화면 25%" 기준이 하위 호환 때문에 남았고, 현대 디스플레이와 선호 시청 거리에서는 위험이 더 크다고 적습니다. HDR은 200 cd/m²를 기준 백색으로 봅니다. [paper]
- **Ofcom과 Harding 2005(EFA 합의)의 패턴 규칙.** 뚜렷한 줄무늬가 어느 방향으로든 밝음–어둠 쌍 5개를 넘으면 잠재적으로 해로운 패턴입니다. 줄무늬 전체가 최소 예상 시청 거리에서 0.006 sr보다 큰 입체각을 차지하고, 가장 밝은 줄의 휘도가 50 cd/m²를 넘고, 0.5초 이상 보이면, 줄무늬가 방향을 바꾸거나 진동·섬광·대비 반전할 때 밝음–어둠 쌍은 5개 이하여야 합니다. Ofcom은 정지한 줄무늬가 화면의 40%를 넘거나, 방향 변화·진동·섬광·대비 반전하는 줄무늬가 화면의 25%를 차지하면 허용하지 않습니다. Ofcom은 또 개별 기준 아래여도 5초에 걸친 섬광 연쇄의 누적 효과를 경고합니다. [snippet]
- **ITU-R BT.1702의 절대 휘도형 정의**(20 cd/m², 어두운 쪽 160 cd/m² 미만)는 WCAG Understanding이 인용한 문장으로만 확인했습니다. [standard, WCAG를 통해 간접]

#### 2.1.3 EA IRIS가 실제로 하는 일 (기본 설정과 소스 코드) [industry]

게임 브리프는 IRIS를 README 수준으로만 요약했습니다. 소스를 읽으면 스킬의 "IRIS와 같다"는 표현 몇 곳이 맞지 않습니다.

| 항목 | IRIS 기본값·동작 (근거 파일) | 스킬(GM-04) 현재 동작 | 차이의 의미 |
| --- | --- | --- | --- |
| 휘도 전이 | 상대 휘도 변화 0.1, 어두운 쪽 0.8 미만 (`appsettings.json`: `RelativeLuminanceFlashThreshold` 0.1, `RelativeDarkLuminanceThreshold` 0.8) | 같은 값, 블록별 | 같음 |
| 적색 전이 | `RedSaturation.FlashThreshold` 20, `RedDarkThreshold` 321(적색에는 어두운 쪽 조건을 사실상 끔) | 선형 RGB에서 (R−G−B)×320 > 20인 블록 비율 10% 이동 | 정의 계열은 같음. WCAG 2.2의 u′v′ 0.2 정의와는 둘 다 다름 |
| 면적 | `FlashDetection.AreaProportion` 0.25 = **프레임 전체 픽셀의 25%**. `Flash::CheckSafeArea`가 "조금이라도 바뀐 픽셀" 수(`countNonZero`)를 세어 25%를 넘을 때만 프레임 평균 휘도 차를 봄 | 블록 격자, 10° 시야(0.006 sr) 안의 동시 섬광 면적 합 | IRIS 기본 설정은 방송식 "화면 25%" 규칙이고, 전체 프레임 평균을 쓰므로 국소 섬광과 역위상 섬광을 놓칩니다. 스킬 쪽이 더 엄격하고 민감합니다 |
| 전이 누적 | `Flash::CheckTransition`: 같은 부호 평균 변화를 최근 1초 안에서 누적해 절댓값이 0.1을 넘으면 전이 1회(단조 구간당 1회) | 블록별 상반 변화 | IRIS에는 Trace의 "66 ms 이내" 조건이 없습니다. 느린 페이드도 1초 안에서 누적되면 전이가 됩니다 |
| 실패 | 최근 1초 전이 수 > `MaxTransitions` 6 → `FlashFail` | 1초 창 전이 7회 이상 → P0 | 같음 |
| 연장 실패 | `TransitionTracker::EvaluateFrameMoment`: 최근 5초 창(`ExtendedFailWindow` 5) 안에서 "1초 전이 수가 4–6인 프레임" 수가 4초 분량(`ExtendedFailSeconds` 4 × fps) 이상이고, 현재 1초 전이 수가 4 이상 → `ExtendedFail` | 5초 창 안에서 전이 20회(섬광 10회) 이상, 면적 초과 → P1 | **다른 규칙입니다.** IRIS는 "5초 중 4초 이상 초당 2–3회"를 보고, 스킬은 "5초에 섬광 10회"를 봅니다. 초당 2회가 4초 이어지면(섬광 8회) IRIS는 연장 실패, 스킬은 통과. 초당 3회가 3.4초 이어지면 스킬은 실패, IRIS는 통과 |
| 경고 | 1초 전이 수 ≥ `WarningTransitions` 4(초당 섬광 2회) → `PassWithWarning` | 없음 | 경고 단계가 없음 |
| 패턴 | `PatternDetection`: 50% 축소 → FFT 파워 스펙트럼 피크 → 역변환 → 윤곽선. 면적 ≥ 프레임의 25%, 줄 수(`nComponents`) ≥ `MinStripes` 6, 밝은 쪽 평균 휘도 ≥ 0.25, `TimeThreshold` 0.5초(= fps × 0.5 프레임) 지속이면 실패. **기본 설정에서 `PatternDetectionEnabled`: false** | 없음 | 패턴 규칙은 스킬에 없고, IRIS도 기본으로는 꺼져 있습니다 |
| 면책 | README: "IRIS is not intended to guarantee, certify or otherwise validate visual content's compliance with legal, regulatory or other requirements." | 보고서 문구: "인증 도구(EA IRIS/Harding)로 재검사가 필요합니다" | IRIS는 인증 도구가 아닙니다. IRIS 기본 설정의 통과가 스킬의 10° 시야 실패를 뒤집는 근거가 될 수 없습니다 |

#### 2.1.4 화면 캡처 도구가 잴 수 있는 것과 없는 것

- **짧은 섬광을 놓칠 확률.** 한 프레임(16.7 ms)짜리 밝은 상태를 무작위 위상의 순간 캡처로 잡을 확률은 캡처 간격에 대한 비율입니다. 20 fps 0.33, 24 fps 0.40, 30 fps 0.50, 60 fps(모든 프레임) 1.0. [derived] 드라이버 주석은 CDP 캡처가 약 24 fps라고 적습니다. 그러면 초당 4회의 한 프레임 섬광은 평균 초당 1.6회로 관측되므로 대개 통과합니다(어느 1초 창에서 4회가 모두 잡힐 확률은 0.4⁴ ≈ 0.026). 두 프레임(33 ms) 섬광은 24 fps에서 0.8로 잡힙니다. [derived] 지터(`FLASH_JITTER_MS` 15)는 위상 고정을 깨지만 이 누락 확률은 줄이지 못합니다.
- **나이퀴스트 한계.** 표본 주파수 f_s로는 f_s/2 미만의 깜빡임만 주파수를 보존합니다. 24 fps에서 12 Hz 이상은 낮은 주파수로 접혀 들어옵니다. 스킬은 평균 20 fps 미만을 `inconclusive`로 처리합니다(`FLASH_MIN_FPS`). 이 규칙은 한 프레임 섬광의 누락은 다루지 못합니다. [derived]
- **결정적 전 프레임 캡처가 가능합니다.** CDP `HeadlessExperimental.beginFrame`은 "BeginFrame을 보내고 프레임이 완성되면 돌아오며, 결과 프레임의 스크린샷을 선택적으로 찍는다". `frameTimeTicks`와 `interval`(기본 16.666 ms)을 지정할 수 있습니다. 조건은 대상이 BeginFrameControl로 만들어지고 `--run-all-compositor-stages-before-draw`와 함께 쓰는 것입니다(헤드리스 전용 실험 도메인). [industry] 이 방식이면 기계 속도와 무관하게 60 Hz의 모든 프레임을 캡처할 수 있습니다. 실제 Playwright 번들 Chromium에서 되는지는 확인하지 않았습니다.
- **캔버스 게임은 페이지 안에서 매 프레임 읽을 수 있습니다.** WebGL/2D 캔버스 게임은 `requestAnimationFrame` 콜백이 끝난 직후 같은 작업 안에서 캔버스를 작은 2D 캔버스로 복사하면 게임 자신의 프레임률로 모든 프레임의 블록 휘도를 계산할 수 있습니다. [opinion, 파일럿 필요] `preserveDrawingBuffer: false`인 WebGL은 합성 뒤에는 버퍼가 비므로 같은 작업 안에서 읽어야 합니다. [opinion]
- **잴 수 없는 것.** 실제 디스플레이 휘도(cd/m²), HDR 톤 매핑, 사용자의 밝기 설정, 실제 시청 거리, 개인 감수성, 게임 안에서 우연히 겹치는 효과(멀티플레이 폭발 30개)의 완전한 도달. 절대 휘도 규칙(20 cd/m², 50 cd/m² 패턴 조건)은 기준 백색 200 cd/m² 가정으로만 환산할 수 있습니다. [derived, Trace의 200 cd/m² 가정 사용]

#### 2.1.5 스킬의 면적 문턱은 얼마인가 (휴대폰 예) [derived]

`ergoqa/devices.py`의 galaxy-s24(0.1833 mm/CSS px, 뷰포트 360 × 780)로 계산하면:

| 기준 | 문턱(CSS px²) | 뷰포트 대비 |
| --- | --- | --- |
| 0.006 sr, 시청 거리 250 mm | 11,160 | 4.0% |
| 0.006 sr, 300 mm (기기 기본값) | 16,071 | 5.7% |
| 0.006 sr, 400 mm | 28,571 | 10.2% |
| WCAG CSS 대체, 25% × 341 × 256 | 21,824 | 7.8% |
| WCAG Understanding 문장 그대로, 341 × 256 | 87,296 | 31.1% |
| Trace, 25% × 416 × 416 | 43,264 | 15.4% |
| IRIS 기본, 프레임의 25% | 70,200 | 25% |

휴대폰에서는 스킬의 기하 계산이 가장 엄격합니다. IRIS 기본 설정보다 약 4.4배 작은 면적에서 실패합니다. 따라서 "IRIS로 재확인"은 휴대폰에서 스킬의 P0를 거의 항상 뒤집는 쪽으로만 작동할 수 있고, 그것은 규범적으로 옳지 않습니다(WCAG는 10° 시야 기준). GQA-03에서 문구와 절차를 바꿉니다.

#### 2.1.6 한국 기준: KWCAG 2.2 검사항목 6.3.1 [standard]

`a11ykr/kwcag22` 저장소에 실린 KWCAG 2.2 본문에서 확인했습니다(비공식 게시본이므로 KS X OT0003 원문과 대조 필요).

- 6.3.1(깜빡임과 번쩍임 사용 제한): "초당 3~50회 주기로 깜빡이거나 번쩍이는 콘텐츠를 제공하지 않아야 한다."
- 해설의 세부 기준: "번쩍임이 초당 3~50회이며, 10인치 이상의 화면에 표시된 번쩍이는 콘텐츠가 차지하는 면적의 합이 화면 전체 면적의 10%를 넘지 않아야 한다." "초당 3~50회의 속도로 깜빡거리게 만든 콘텐츠는 그 깜빡임을 정지시킬 수 있어야 한다." 번쩍이는 시간을 3초 미만으로 제한하는 방법을 권합니다. 10인치 이상 화면(태블릿, PC 모니터, 무인 안내기)을 특히 주의하라고 적습니다.
- **WCAG와 다른 점 세 가지.** (1) 하한이 "초당 3회 초과"가 아니라 "초당 3~50회"라서 정확히 3 Hz인 깜빡임도 대상일 수 있습니다. 스킬은 50 ms 허용 오차로 3 Hz를 일부러 통과시킵니다(`FLASH_WINDOW_TOLERANCE_MS`). (2) 면적 기준이 "10인치 이상 화면의 10%"로, 10° 시야 기준과 다릅니다. 24인치 모니터를 60 cm에서 볼 때 화면 10%는 약 15,900 mm²이고 0.006 sr은 약 2,160 mm²라서 이 경우 WCAG 쪽이 약 7배 엄격합니다. [derived] (3) 면적과 무관하게 "깜빡임(blinking)은 정지할 수 있어야" 합니다. 이것은 광과민성보다 WCAG 2.2.2(Pause, Stop, Hide)에 가까운 요구입니다.
- 스킬 보고서는 한국어이고 한국 공공 누리집의 준수 기준은 KWCAG입니다. GQA-05에서 KWCAG 판정을 따로 보고하도록 제안합니다.

### 2.2 타이밍과 입력: QTE, 연타, 누르고 있기, 반응 시간, 지연, 판정 창

#### 2.2.1 가이드라인이 요구하는 것

- **XAG 107(Input).** 가이드라인이 드는 배제 사례는 "보스를 이기려면 두 버튼을 반복해서 연타", "문을 열려면 오른쪽 트리거를 3초 누르고 있기"입니다. 입력의 종류뿐 아니라 "입력을 작동시키는 데 필요한 타이밍과 속도"를 평가하라고 하고, 버튼을 빨리 누르거나 **2–3초 이상** 누르고 있어야 하는 곳을 짚으라고 합니다. 권고는 반복 입력을 요구하지 않거나 대안을 주는 것입니다(콤보의 빠른 입력 회피, 정밀한 타이밍 연쇄 회피, 빠른 반복 탭 회피). [snippet]
- **XAG 116(Time limits), 117(Visual distractions and motion settings), 118(Photosensitivity), 119(STT/TTS chat), 120(Communication experiences).** 번호와 제목만 발췌로 확인했습니다. 117은 스크롤·깜빡임·자동 갱신·움직임을 멈출 수 있게 하고 시야각·카메라 움직임을 조절하게 하라고 합니다. [snippet]
- **GAG.** "Avoid repeated inputs (button-mashing/quick time events)"는 Intermediate, "Avoid flickering images and repetitive patterns"는 Basic입니다. 후자의 완화책 설명에는 5초 넘는 섬광 연쇄, 화면 25% 이상에서 1초 3회 초과 섬광, 화면 25% 이상을 덮는 움직이는 반복 패턴이나 균일한 글자 블록을 피하라는 내용이 있습니다. [snippet]
- **Accessible Games Initiative(2025, ESA 주도).** 24개 태그 가운데 "Playable without Rapid Button Presses"(연타와 QTE 같은 반복 버튼 동작을 피할 수 있음), "Playable without Button Holds"가 있습니다. Steam에는 "Playable without Timed Inputs" 태그가 있고, 개발사들이 이 태그를 잘못 붙인다는 비판 기사가 있습니다(Access-Ability, 2025-11). [snippet]
- **The Last of Us Part II(Naughty Dog/Sony).** 60개 넘는 접근성 설정 가운데 "모든 누르고 있기를 토글로", "모든 빠른 연타를 누르고 있기로" 바꾸는 개별 옵션, 게임 속도 50% 슬로 모션, 퍼즐 건너뛰기가 있습니다. [snippet] 즉 산업 모범 사례는 "연타 금지"가 아니라 "대체 입력이 있고, 그것이 작동하는가"입니다.
- **Apple HIG(Game controls).** "여러 버튼을 동시에 또는 연속으로 눌러야 하는 게임 메커닉은 다시 설계하라", 길게 누르기·두 번 탭 같은 제스처로 한 조작에 변형을 넣으라고 합니다. [industry]
- **QTE 최소 창에 관한 공개 표준은 이번에도 찾지 못했습니다.** 가이드라인은 수치 대신 "대안을 주라"고 합니다(XAG 107, GAG, AGI). 그래서 스킬의 QTE 판정은 표준 문턱이 아니라 측정한 창과 인간 모형의 비교일 수밖에 없고, 그 모형의 입력(반응 시간, 지연)이 [assumption]이라는 점을 보고서에 드러내야 합니다(GQA-15). [derived]

#### 2.2.2 반응 시간 분포

- **Der & Deary 2006**(영국 Health and Lifestyle Survey, 18–94세 7,130명): 단순 반응 시간은 50세 무렵까지 거의 느려지지 않고, 4지 선택 반응 시간은 성인기 내내 느려집니다. 여성이 더 느리고 변동이 큽니다(특히 선택 반응 시간의 개인 내 표준편차). [snippet] 연령대별 평균과 표준편차 표는 이번에도 얻지 못했습니다(APA 부록과 출판사 사이트 차단). 한 2차 발췌는 "20–50세 연 0.5 ms, 50세 이후 연 1.5–2.0 ms 느려짐"이라고 적지만 출처를 확인하지 못했습니다. [snippet, 2차]
- **웹 단순 반응 시간의 실측 기준점.** Human Benchmark의 "초록색이 되면 클릭" 과제는 8,100만 회 넘는 클릭에서 중앙값 273 ms, 평균 284 ms입니다. 이 값에는 컴퓨터와 모니터 지연(대략 10–50 ms)이 들어 있습니다. [snippet] 연령 정보는 없고, 스스로 참여한 사람들입니다.
- **스킬의 현재 모형.** `CHOICE_RT_MS_BY_AGE`(20대 420 ms … 70대 이상 580 ms)는 [assumption]이고, 로그정규 CV 0.2, 동작 100 ms, 입력 지연(터치 80, 키보드 20 ms)을 더합니다. 이 모형으로 계산하면 [derived]:

| 연령대 | 평균 RT | 95백분위 RT | 터치에서 95% 성공에 필요한 창 | 키보드 |
| --- | --- | --- | --- | --- |
| 20대 | 420 | 570 | 750 ms | 690 ms |
| 30대 | 440 | 598 | 778 ms | 718 ms |
| 60대 | 530 | 720 | 900 ms | 840 ms |
| 70대 이상 | 580 | 788 | 968 ms | 908 ms |

  같은 모형에서 터치 700 ms 창의 성공 확률은 20대 0.88, 60대 0.50, 70대 이상 0.33입니다. 600 ms 창은 20대 0.54입니다. [derived] 즉 스킬의 P1 규칙("20대 평균도 놓침")은 터치에서 창 600 ms 미만일 때 켜집니다.
- **단순 반응과 선택 반응의 구분이 빠져 있습니다.** 버튼이 하나로 정해진 QTE("지금 A")는 단순 반응이고, 버튼이 무작위로 바뀌는 QTE는 선택 반응입니다(Hick–Hyman 법칙: 선택지 수의 log₂에 비례해 늘어남). 스킬은 모든 QTE에 선택 반응 값을 씁니다. [derived, 코드 확인]

#### 2.2.3 예측 가능한 타이밍(리듬·타이밍 바)은 반응 시간 문제가 아닙니다

- 박자에 맞춰 누르는 과제에서 사람은 자극보다 수십 ms 먼저 누르는 경향(negative mean asynchrony)이 있고, 비동기의 표준편차는 시각 박자 46.2 ms, 청각 박자 38.5 ms로 보고되었습니다(한 연구). 다른 실험실 측정은 약 65 ms입니다. 음악가는 비동기와 변동이 더 작습니다. [snippet, Repp 2005 리뷰와 후속 연구 발췌]
- **실제 게임의 판정 창.** [industry]
  - osu!(표준 모드): 300 = ±(80 − 6·OD) ms, 100 = ±(140 − 8·OD) ms, 50 = ±(200 − 10·OD) ms. OD 5에서 ±50/±100/±150 ms, OD 0에서 ±80/±140/±200 ms. 50 창 밖은 미스. Double Time(속도 +50%)은 창을 33% 줄이고 Half Time(−25%)은 33% 늘립니다. 스피너는 초당 3–7.5회전을 요구합니다(OD에 따라).
  - StepMania 계열 기본값: W1 ±22.5, W2 ±45, W3 ±90, W4 ±135, W5 ±180 ms.
- 정규 오차 N(μ = −20 ms, σ = 46 ms)로 계산한 적중 확률 [derived]: ±22.5 ms 0.34, ±45 ms 0.63, ±90 ms 0.93, ±135 ms 0.99, ±180 ms 1.00. μ = −30 ms, σ = 65 ms면 ±90 ms 0.79, ±150 ms 0.96. 즉 리듬 게임의 "Perfect" 창은 늘 맞히라고 만든 창이 아니라 점수 등급이고, **미스 경계(±135–200 ms)가 통과/실패 경계**입니다. 예측 가능한 타이밍 입력을 반응 시간 모형으로 판정하면 이런 창을 전부 "사람이 못 누름"으로 잘못 봅니다.
- 따라서 QTE는 최소 두 종류로 나눠 판정해야 합니다: **반응형**(프롬프트가 예고 없이 뜸 → 반응 시간 분포)과 **예측형**(다가오는 표식·박자·타이밍 바로 시점을 예고함 → 시간 정밀도 분포). GQA-01의 핵심입니다.

#### 2.2.4 입력·표시 지연

- 상용 터치 기기는 터치에서 화면 갱신까지 대개 50–200 ms입니다(Ng et al. 2012, UIST). 탭 지연의 지각 문턱은 20–100 ms 범위로 보고되었습니다(Jota et al. 2013, CHI). [snippet]
- 장르별 지연 허용치(1인칭 약 100 ms, 3인칭 약 500 ms, 전지적 시점 약 1,000 ms; Claypool & Claypool 2006, CACM)는 이번에도 원문을 열지 못했습니다(WPI 서버 차단). 게임 브리프의 [R] 상태가 그대로입니다.
- 브라우저 드라이버는 CDP로 입력을 주입하므로 하드웨어·OS 지연을 건너뜁니다. 따라서 드라이버가 재는 것은 **게임 시간 기준의 수용 창**이고, 사람 쪽 지연(표시 + 입력)은 모형 값으로 더해야 합니다. 이 분리가 GM-03 개정의 전제입니다.

#### 2.2.5 연타 능력의 인간 자료

- 손가락 두드리기 검사(Finger Tapping Test) 규준 연구(Ruff & Parker 1993, 16–70세 360명)는 여성이 특히 고령에서 더 느리고, 나이가 들수록 느려지며, 교육 수준이 높을수록 빠르다고 보고합니다. [snippet] 연령별 평균(10초당 횟수)은 얻지 못했습니다.
- 게임 패드 엄지 연타, 터치스크린 엄지 연타의 연령별 지속 속도에 관한 공개 규준은 찾지 못했습니다. 게임 브리프의 "젊은 성인 검지 약 5 Hz"도 여전히 [R]입니다.
- 결론: GM-06의 심각도를 프로필별 "연타 능력"으로 정하면 근거 없는 숫자를 만들게 됩니다. 규범 기반(XAG 107, GAG, AGI 태그: 대안 없는 필수 연타 = 결함)으로 판정하고, 측정한 **요구 속도(Hz)** 는 심각도 등급의 보조 정보로만 씁니다(GQA-02).

### 2.3 HUD, 글자, 자막, 안전 영역, 모바일 터치 조작

#### 2.3.1 글자 크기: 무엇을 재는가가 먼저입니다

- **XAG 101.** 콘솔 글자는 1080p에서 26 px부터 52 px까지 키울 수 있어야 합니다. 크기는 가장 낮은 디센더와 가장 높은 어센더가 들어간 단어에서 재며, "body height = 디센더 + x-height + 어센더 픽셀 수"입니다. [snippet] PC 18 px(1080p), 36 px(4K), 200% 확대는 게임 브리프가 제3자 테스트 문서로 확인한 값입니다([V1-3p]). **과업 지시문의 "XAG 101: 1080p 28 px"는 이번 검색에서 XAG 원문 발췌로 확인되지 않았습니다.** 28 px는 게임 브리프에 Amazon 10-foot UI 값으로만 남아 있습니다([V2]).
- **Apple HIG(Designing for games) 최소 글자 크기.** [industry]

| 플랫폼 | 기본 글자 | 최소 글자 | 기본 버튼 | 최소 버튼 |
| --- | --- | --- | --- | --- |
| iOS, iPadOS | 17 pt | 11 pt | 44 × 44 pt | 28 × 28 pt |
| macOS | 13 pt | 10 pt | 28 × 28 pt | 20 × 20 pt |
| tvOS | 29 pt | 23 pt | 66 × 66 pt | 56 × 56 pt |
| visionOS | 17 pt | 12 pt | 60 × 60 pt | 28 × 28 pt |
| watchOS | 16 pt | 12 pt | 44 × 44 pt | 28 × 28 pt |

  같은 문서는 글자 크기, 조작 매핑, 움직임 강도, 소리 균형을 플레이어가 조절하게 하라고 적습니다. [industry] 스킬의 `TEXT_PLATFORM_MIN_CSS_PX_MOBILE = 11`은 [recalled]로 표시되어 있는데, 이 원문으로 [industry]로 올릴 수 있습니다.
- **측정 단위의 불일치 (코드 확인).** GM-01은 계산된 CSS `font-size`(em 크기)를 XAG의 body height 문턱(26 px × 해상도 비 / DPR)과 비교합니다(`check_text_size`). em 크기와 어센더–디센더 잉크 높이는 글꼴마다 다릅니다. 그래서 같은 26 px `font-size`가 XAG 기준으로 통과일 수도 실패일 수도 있습니다. [derived, 코드 확인] 브라우저는 Canvas `measureText()`의 `actualBoundingBoxAscent + actualBoundingBoxDescent`로 요소의 계산된 글꼴과 실제 문자열(또는 "bdpq", 받침 있는 한글)의 잉크 높이를 바로 줄 수 있습니다(HTML Canvas 표준의 TextMetrics; 이번 세션에서 원문 확인 안 함). GQA-07.

#### 2.3.2 자막

- XAG 104는 자막 크기를 XAG 101 최소 이상, 200%까지 키울 수 있게 하라고 합니다(게임 브리프 [V2]). BBC는 글자 크기를 화면 높이의 약 6.667%, 줄 높이 120–125%, 가장자리에서 5% 안쪽으로 둡니다(게임 브리프 [V1]).
- **한국어 자막 기준.** Netflix 한국어 Timed Text Style Guide는 줄당 16자입니다. 2차 요약에 따르면 한글은 1자, 라틴 문자·공백·문장부호는 0.5자로 세고, 읽기 속도는 성인 최대 12자/초, 아동 9자/초입니다. [snippet, 2차 요약. Netflix 원문은 차단되어 대조 못 함]
- **기본값이 사용률을 정합니다.** Ubisoft 자료로는 자막이 기본으로 켜진 게임에서 90–95%가 자막을 켠 채 두고, 기본으로 꺼진 게임에서는 50–60%가 켭니다(Assassin's Creed Odyssey 95%, Far Cry New Dawn 97%). [snippet]
- **스킬과의 관계.** 자막을 `transient_text`로 선언하면 CG-02(토스트 규칙: 느린 독자 × 1.5, 최소 4초)가 대부분의 자막 큐를 실패로 봅니다. 12음절 대사는 CG-02로 4,023 ms가 필요하지만 Netflix 한국어 12자/초 기준으로는 약 1,167 ms면 되고, 19음절은 5,932 ms 대 1,875 ms입니다(약 3.2–3.4배). [derived, `cognition.min_display_ms`로 계산] 자막은 대사 길이에 맞춘 연속 흐름이므로 토스트 규칙이 아니라 자막 규칙(초당 글자 수, 줄당 글자 수, 줄 수)으로 판정해야 합니다. [derived] 웹 동영상·컷신은 `<track>`의 TextTrack 큐(`startTime`, `endTime`, `text`)를 DOM에서 바로 읽을 수 있습니다(WHATWG HTML 표준; 이번 세션에서 원문 확인 안 함). GQA-12.

#### 2.3.3 안전 영역과 HUD 배치

- Apple HIG(Game controls): 버튼이 홈 인디케이터나 Dynamic Island 같은 시스템 기능과 겹치지 않게 하고, 기기 경계와 안전 영역을 고려하라고 합니다. [industry]
- TV의 title-safe 90%, action-safe 93%(SMPTE)는 이번에도 원문을 확인하지 못했습니다(게임 브리프 [R]).
- Playwright 기기 에뮬레이션이 CSS `env(safe-area-inset-*)`를 실제 기기처럼 채우는지는 확인하지 못했습니다. 확인 전에는 안전 영역 검사가 기기 카탈로그에 기록한 인셋 값에 의존해야 합니다. [opinion]

#### 2.3.4 모바일 게임 터치 조작

Apple HIG(Game controls, 2025-06-09 개정) 원문에서 확인한 규칙입니다. [industry]

- "자주 쓰는 버튼은 플레이어 엄지 가까이, 이동과 카메라 입력을 기대하는 원형 영역은 피해서" 둡니다. "메뉴 같은 보조 조작은 화면 위쪽"에 둡니다. GM-02의 보조 조작 면제(일시정지·메뉴·설정)가 이 문장으로 [industry] 근거를 얻습니다.
- 크기: "자주 쓰는 조작은 최소 44 × 44 pt, 메뉴처럼 덜 중요한 조작은 최소 28 × 28 pt".
- "손가락이 조작을 덮고 있을 때도 보이는" 누름 상태(예: 빛남)를 넣고, 소리·햅틱과 함께 쓰라고 합니다.
- 이동은 화면 왼쪽, 카메라는 오른쪽이 일반적 기대이고, 이동은 "엄지가 닿는 곳에 가상 스틱을 띄우는" 방식을, 카메라는 가상 스틱 대신 직접 터치로 화면을 끌어 돌리는 방식을 권합니다.
- 여러 버튼을 동시에 또는 연속으로 눌러야 하는 메커닉은 다시 설계하라고 합니다.
- GAG Basic: "특히 작은 화면이나 터치 화면에서 상호작용 요소·가상 조작부를 크고 간격을 두어 배치하라". [snippet]
- 가로 두 엄지 파지의 엄지 휴지 위치(스킬의 25 × 22 mm 인셋)에 대한 공개 규준은 이번에도 찾지 못했습니다. `LANDSCAPE_REST_INSET_MM`은 계속 [assumption]입니다.

### 2.4 게임 접근성 규범, 인증, 스토어 표시

- **XAG 목록.** 101 Text display, 102 Contrast, 103 Additional channels for visual and audio cues, 104 Subtitles and captions, 107 Input, 112 UI navigation, 116 Time limits, 117 Visual distractions and motion settings, 118 Photosensitivity, 119 STT/TTS chat, 120 Communication experiences. 번호·제목은 발췌로 확인했습니다. [snippet] XAG 118은 약 4,000명 중 1명이 섬광·패턴 같은 시각 자극으로 발작을 겪을 수 있다고 적습니다. [snippet, 인용한 쪽이 업체 블로그]
- **GAG 수준.** 섬광·반복 패턴 회피 Basic, 가상 조작부 크기·간격 Basic, 반복 입력(연타·QTE) 회피 Intermediate. [snippet]
- **AbleGamers APX.** 22개 디자인 패턴("Clear Text", "Do More With Less" 등). 전체 이름 목록은 사이트 차단으로 확인하지 못했습니다. [snippet]
- **Accessible Games Initiative(2025).** GDC 2025에서 발표된 24개 스토어 태그와 기준. 발췌에 나온 창립 회원은 EA, Google, Microsoft, Nintendo of America, Ubisoft입니다(전체 목록은 확인 못 함). 전 세계 장애가 있는 플레이어를 4억 2,900만 명 이상으로 인용합니다. [snippet]
- **App Store Accessibility Nutrition Labels(2025).** VoiceOver, Voice Control, Larger Text, Dark Interface, Sufficient Contrast, Differentiate Without Color Alone, Reduced Motion, Captions, Audio Descriptions 9종. 2025년 9월부터 이 표시로 검색할 수 있고, 처음에는 자발적이지만 신규 앱과 업데이트 제출 때 정보를 요구할 예정이라고 합니다. 개발사가 앱의 "일반적인 작업(common tasks)"에서 기능을 평가하라는 WWDC25 세션이 있습니다. [snippet]
- **CVAA(미국).** 게임에 대한 FCC 면제는 2018-12-31로 끝났고, 2019-01-01 이후 출시되는 게임의 고급 통신 서비스(VoIP, 게임 내 채팅 같은 전자 메시지, 상호운용 영상회의)는 접근 가능해야 합니다("achievable" 기준). [snippet]
- **플랫폼 인증.** Xbox Requirements(XR), PlayStation TRC, Nintendo Lotcheck은 안정성·시스템 API·오류 처리·등급·현지화·데이터 처리를 보는 규격 검사이고, 기능 QA("작동하는가")·사용성 테스트("재미있는가")와 구분됩니다. [snippet, QA 업체 블로그] 한 업체 글은 PlayStation 인증에 광과민성 평가가 들어 있다고 쓰지만 1차 자료로 확인하지 못했습니다. TRC와 Lotcheck 본문은 비공개(NDA)라 확인 불가입니다. [opinion]
- **시사점.** 게임 접근성의 규범 요구 대부분은 "기능이 있는가, 그리고 작동하는가"입니다(자막 기본값, 200% 확대, 누르기 → 토글, 연타 → 누르고 있기, 섬광 줄이기). 스토어 태그·라벨은 그 "있다"는 주장을 공개적으로 만든 것입니다. 드라이버가 옵션을 켜고 같은 측정을 다시 하면(A/B) 주장을 검증할 수 있습니다. GQA-11, GQA-17.

### 2.5 게임 QA 실무: 플레이테스트와 자동 테스트 에이전트

#### 2.5.1 플레이테스트 방법

- **RITE(Medlock, Wixon, Terrano, Romero, Fulton 2002, UPA).** Age of Empires II 튜토리얼 사례에서 원인이 분명한 문제는 참가자 한 명 뒤에도 고치며 반복했고, 참가자 10명 이후 설계가 안정되어 다음 6명 동안 변경이 필요 없었습니다(총 16명). 문제 발견과 수정 모두에 매우 효과적이었다고 보고합니다. [snippet]
- **생체 신호(Biometric Storyboards, Mirza-Babaei et al. 2013, CHI).** BioSt 기반 사용자 테스트는 사용자 테스트 없이 설계할 때보다 시각, 재미, 게임플레이 품질이 유의하게 좋은 결과를 냈고, 고전적 사용자 테스트는 같은 유의한 이점을 보이지 못했습니다. [snippet] 발견한 문제 수 비교는 얻지 못했습니다.
- **소리 내어 생각하기(think-aloud).** 게임 사용자 연구의 기본 방법이지만 이번에 게임 특화 수치를 찾지 못했습니다. 스킬의 사후 인터뷰는 시뮬레이션된 think-aloud일 뿐이고 사람의 발화를 대신하지 못합니다(persona-agent-protocol §6, LAT-17). [opinion]
- **텔레메트리.** 산업 사례(사망 히트맵 등)는 이번에 원문으로 확인하지 못했습니다. 게임 브리프의 King(Gudmundsson et al. 2018)과 Rovio(Roohi et al. 2021) 사례도 [R]입니다.
- **스킬과의 대응.** RITE의 "고치고 곧바로 다시 돌리기"는 스킬 7단계(수정 후 같은 시나리오·기기·프로필로 재생)와 같고, STF-18(기준선 비교 모드)이 그 비교를 자동화합니다. 생체 신호·텔레메트리는 실제 사람의 자료라서 스킬의 시뮬레이션이 대신할 수 없습니다. 스킬은 그 자료가 있을 때 Stage 0의 근거로만 씁니다. [opinion]

#### 2.5.2 자동 테스트 에이전트의 보고된 성과

| 시스템 | 방식 | 보고된 성과 | 태그 |
| --- | --- | --- | --- |
| EA SEED(Bergdahl et al. 2020, IEEE CoG) | 심층 강화학습 | 테스트 커버리지 증가, 의도치 않은 메커닉·익스플로잇·버그 발견, 맵 난이도 시험. 수치는 발췌에 없음 | [snippet] |
| Wuji(Zheng et al. 2019, ASE, NetEase) | 진화 알고리즘 + 심층 강화학습 + 다목적 최적화 | 상용 게임에서 개발사가 확인한 미지의 버그 3건 | [snippet] |
| ICARUS(Pfau et al. 2017, CHI PLAY, Daedalic) | 강화학습 + 휴리스틱 | Visionaire 엔진 어드벤처 게임의 전체 플레이를 전문 테스터의 스피드런과 비슷한 시간에 완주. 일일 빌드·하드웨어 호환성·성능 시험에 사용 | [snippet] |
| TITAN(arXiv 2509.22170, 2025) | LLM 에이전트, 상용 MMORPG 2종 | 과업 완료 95%, 심은 버그 82% 탐지(같은 시간 제한에서 전문 테스터 18%), 미지의 버그 4건, 상용 QA 파이프라인 8곳 배치 | [snippet] 저자 소속 회사의 자체 평가이고 버그는 저자가 심음 |
| GlitchBench(CVPR 2024) | 멀티모달 모델의 글리치 인식 | 최고 GPT-4V 평균 43.4%(Q1 57.2%, Q2 29.5%) | [snippet] |
| VideoGameQA-Bench(2025, NeurIPS D&B, Sony Interactive Entertainment 연구) | VLM 평가: 시각 단위 테스트, 회귀, 글리치 탐지, 버그 보고 등 9개 과제, 800개 이상 게임에서 4,786문항, 16개 모델 | 이미지 글리치 탐지에서 GPT-4o 정확도 82.9%, F1 0.83(다른 논문의 인용) | [snippet] |
| 업계 설문(Politowski, Petrillo, Guéhéneuc 2022) | 문헌 검토 + 개발자 설문 | 게임 개발자는 거의 전적으로 수동 플레이테스트와 테스터의 암묵지에 의존하고, 자동 에이전트 테스트에 회의적 | [snippet] |

- **읽는 법.** 성과가 큰 시스템(ICARUS, Wuji, TITAN)은 모두 게임 상태에 직접 접근하거나, 게임별로 만든 행동 공간·휴리스틱을 씁니다. 화면만 보는 범용 에이전트는 실시간 게임 진행이 매우 약합니다(VideoGameBench, 게임 브리프 [R]). 글리치 "인식"은 과제 정의에 따라 43%에서 83%까지 흔들립니다. [derived] 스킬의 설계 원칙("측정은 결정적 모형, 에이전트는 상태 도달과 판단 가설")은 이 자료와 맞습니다. 에이전트에게 게임을 "잘 하게" 할 것이 아니라, 옵션 메뉴·QTE·섬광 효과가 나오는 상태에 도달하게 하고, 측정은 드라이버가 하게 해야 합니다. GQA-17.

### 2.6 브라우저 드라이버가 게임에서 잴 수 있는 것

| 필요한 측정 | 방법 | 확인 상태 |
| --- | --- | --- |
| 게임 시간 통제(QTE 수용 창, 연타 속도) | Playwright `page.clock`: `install` 후 `pauseAt`, `runFor`, `fastForward`. 통제 대상: `Date`, `Temporal.Now`, `setTimeout`/`clearTimeout`, `setInterval`/`clearInterval`, `requestAnimationFrame`/`cancelAnimationFrame`, `requestIdleCallback`/`cancelIdleCallback`, `performance`, `Event.timeStamp`. `install`은 다른 시계 관련 호출보다 먼저 해야 함 | [industry] Playwright 문서 원본 |
| CSS 애니메이션으로 만든 QTE 링 | CDP `Animation.setPaused`, `seekAnimations`, `setPlaybackRate`, `getPlaybackRate`; Web Animations API `document.getAnimations()`로 지속 시간을 직접 읽기 | CDP 명령 존재는 [industry] pdl 원본. WAAPI는 이번 세션에서 원문 확인 안 함 |
| 모든 프레임 캡처(섬광) | CDP `HeadlessExperimental.beginFrame`(BeginFrameControl 필요, 헤드리스 전용 실험 도메인) | [industry] pdl 원본. Playwright 번들 Chromium에서의 동작은 미확인 |
| 가상 시간 전체 | CDP `Emulation.setVirtualTimePolicy`(`advance`, `pause`, `pauseIfNetworkFetchesPending`; 실험적) "모든 프레임에 대해 실시간을 합성 시간 소스로 대체" | [industry] pdl 원본 |
| 줄인 움직임 설정 A/B | CDP `Emulation.setEmulatedMedia`(미디어 기능 에뮬레이션)로 `prefers-reduced-motion: reduce` | [industry] pdl 원본 |
| 글자 잉크 높이 | Canvas `measureText()`의 실제 경계 상자 | 미확인(표준 지식) |
| 자막 큐 시각 | `HTMLMediaElement.textTracks[i].cues` | 미확인(표준 지식) |

**Playwright 시계가 못 다루는 것.** Web Audio의 `AudioContext.currentTime`(리듬 게임의 박자 기준), Web Worker 안의 타이머, CSS 애니메이션·트랜지션의 문서 타임라인은 위 목록에 없습니다. [derived, 목록과 대조] 이런 게임은 실시간 스윕(반복 3회, STF-16)과 루프백 지연 보정으로 떨어집니다. 또 드라이버 자신의 16 ms 타이밍 창 폴러(`pageInit`의 `setInterval`)도 페이지 안에서 돌기 때문에 시계를 설치하면 함께 멈춥니다. 시계 모드에서는 폴러를 `runFor` 단계마다 직접 호출해야 합니다. [derived, 코드 확인]

### 2.7 현재 GM 검사 감사 (코드와 근거 대조) [derived]

| 검사 | 지금 하는 일 | 근거와 맞는 점 | 맞지 않는 점 |
| --- | --- | --- | --- |
| GM-02 가로 도달 | 가로·두 엄지·게임 조작만; 아래 모서리에서 25 × 22 mm 인셋한 엄지 휴지점에서 이동 거리 > 35 mm → P3, 상단 띠 → P2; 보조 조작 이름 면제 | 상단 띠 = 보조 조작 자리, 자주 쓰는 조작은 엄지 근처(Apple HIG 원문으로 확인). dev 고유 탐지 2건 | 휴지점·35 mm는 [assumption]/[policy]. "엄지가 닿는 곳에 뜨는" 가상 스틱은 고정 위치가 아니라서 도달 판정 대상이 아님. 이동·카메라 원형 영역과 버튼의 겹침은 보지 않음 |
| GM-03 QTE | 창 = 프롬프트가 **보인 시간**의 최솟값; 선택 반응 시간 로그정규(CV 0.2) 95백분위 + 100 ms + 기기 지연; 20대 평균도 놓치면 P1 | 창은 측정, 반응은 모형이라는 분리 | 보인 시간 ≠ 수용 창(늦게 열림, 숨은 뒤 유예, 일부 구간만 인정). 단순/선택 반응 구분 없음. 예측형 타이밍(리듬, 타이밍 바)을 반응 시간으로 판정. 연쇄 QTE의 누적 확률 없음. 옵션(느리게, 자동 완료)의 존재·작동을 보지 않음 |
| GM-04 섬광 | 블록 격자, 10° 시야 0.006 sr, 적색, 5초 창 연장 규칙, 표본 부족 시 `inconclusive`, DOM 16 ms 폴링 경로 | WCAG 정의, Trace 제안과 방향이 같고 IRIS 기본 설정보다 엄격. 라이브 점검 30/30 | 한 프레임 섬광을 놓칠 확률 50–67%(20–30 fps). "IRIS extended"라는 이름과 실제 규칙이 다름. 보고 문구가 IRIS를 인증 도구처럼 씀. 패턴(줄무늬) 규칙 없음. KWCAG 6.3.1 판정 없음 |
| GM-05 게임 조작 크기 | < 7 mm P2, 연속 탭 조작 < 9.6 mm P3, 가장자리 2 mm 미만 P3 | 자주 쓰는 조작의 7 mm는 Apple HIG 44 pt와 맞음(원문). 정규 기준, 소음 낮음(clean 단위 1) | 일시정지·메뉴도 7 mm 미만이면 P2라서 Apple의 메뉴 최소 28 pt(약 4.4 mm)보다 엄격함. 가장자리 2 mm는 [policy]이고 실제 기기의 홈 인디케이터·노치 인셋과 무관 |
| GM-06 연타 | 스크립트가 같은 대상을 8회 이상 연속으로 누르면 P2(현재 hypothesis) | XAG 107·GAG·AGI 방향 | 게임이 요구한 속도가 아니라 스크립트가 누른 횟수를 셈(dev 탐지 1건이 스크립트 산물). 누르고 있기(2–3초 이상) 요구를 보지 않음. 대안(누르고 있기·토글·자동)의 작동을 보지 않음 |
| GM-01 HUD 글자 | CSS `font-size`를 XAG body height 문턱과 비교; 시각 16′ | 26/18 px 값은 XAG 발췌와 일치 | 측정 단위 불일치(em 대 잉크 높이). iOS 11 pt 최소는 `TEXT_PLATFORM_MIN_CSS_PX_MOBILE`로 이미 들어 있으나 근거 태그가 [recalled]. tvOS 23 pt는 XAG 26 px보다 느슨해 더할 필요 없음 |

### 2.8 게임 제품의 Stage 0: 누가 플레이하는가 (한국)

- **KOCCA 2024 게임이용자 실태조사.** 만 10–69세 1만 명(비이용자 포함; 이용자 8,000명) 조사에서 최근 1년 게임 이용률 59.9%(전년 대비 −3%p). 게임 이용자 중 플랫폼별 이용률은 모바일 91.7%, PC 53.8%, 콘솔 26.7%, 아케이드 15.1%. 50대의 확률형 아이템 구매 의향이 다른 연령대보다 높게 나타났습니다. [report, snippet] 공공데이터포털에 표본 원자료(2020년판)가 있습니다. [snippet]
- **장애와 옵션 사용.** 장애가 있는 플레이어 4억 2,900만 명 이상(AGI 인용), 전체 플레이어의 20–30%(정의에 따라)라는 추정이 인용됩니다. [snippet] 이 숫자는 스킬 규칙상 "비율"로 보고하면 안 되고, 조건 facet을 넣을 근거로만 씁니다(AP-10의 "선언했지만 시뮬레이션하지 않는 조건"과 같은 방식).
- **스킬에 주는 의미.** 게임 surface의 `ergo-audience.v1`은 연령 × 플랫폼 × 입력 장치(터치, 게임패드, 키보드·마우스) 세그먼트로 만들고, 조건 facet에 청각(자막 의존), 운동(연타·누르고 있기 불가), 광과민성(모든 빌드가 검사 대상이므로 facet은 서술용)을 둡니다. AP-08(한국 사전 분포)에 게임 표를 더하는 형태가 맞습니다. GQA-16.

---

## 3. Implications for the skill (스킬에 주는 시사점)

### 3.0 요약

- **GM-03과 GM-06은 "무엇을 재는가"부터 틀렸습니다.** GM-03은 프롬프트가 보인 시간을, GM-06은 스크립트가 누른 횟수를 잽니다. 둘 다 게임이 실제로 요구하는 것(수용 창, 요구 속도)이 아닙니다. 브라우저 드라이버는 Playwright 시계로 게임 시간을 멈추고 한 단계씩 진행할 수 있으므로, 둘 다 **탐침(probe) 스윕**으로 바꿀 수 있습니다(GQA-01, GQA-02). 그 전까지 GM-06 현재 규칙은 가설 목록에서도 뺍니다(GQA-13).
- **GM-04의 핵심은 유지합니다.** 10° 시야 블록 격자는 WCAG 정의와 Trace 제안에 맞고, IRIS 기본 설정보다 엄격합니다(GQA-19). 고칠 것은 (a) 한 프레임 섬광을 놓치는 캡처(GQA-04), (b) IRIS를 인증 도구처럼 쓰는 문구와 IRIS와 다른 "extended" 규칙(GQA-03), (c) 한국 기준 KWCAG 6.3.1 판정 부재(GQA-05), (d) 움직이는 줄무늬 패턴 규칙 부재(GQA-06)입니다.
- **HUD 글자는 단위부터 맞춥니다.** XAG 101은 어센더–디센더 잉크 높이를 재는데 스킬은 CSS em을 잽니다(GQA-07).
- **게임 접근성의 규범은 대부분 "옵션이 있고 작동하는가"입니다.** 드라이버가 옵션을 켜고 같은 측정을 다시 하는 A/B로 확인하고(GQA-17), 스토어 태그·라벨 주장을 검증합니다(GQA-11).
- **heldout-2와의 관계.** heldout-2는 동결 뒤 기록 전까지 검출기 변경을 금지합니다. 아래에서 "동결 전 가능"으로 표시한 것은 보고 문구만 바꾸거나 채점에서 빠지는 가설 층만 건드리는 것입니다. 나머지는 dev-2(또는 새 게임 개발 스위트)에서 만들고, 다음 held-out 스위트에서 범주별로 평가합니다. 드라이버 탐침은 시나리오에 탐침 필드가 없으면 지금 동작으로 되돌아가므로(아래 3.2, 3.3) heldout-2 결과를 해치지 않습니다.

### 3.1 후보 표

| ID | Type | What exactly | Evidence | Expected effect on recall / noise / usefulness | Experiment that decides it (hypothesis, metric, pass rule, data needed) | Effort |
| --- | --- | --- | --- | --- | --- | --- |
| GQA-01 | CHANGE | **GM-03을 "보인 시간" 대신 "탐침으로 잰 수용 창"으로 판정하고, 반응형/예측형을 나눈다.** 시나리오 `timing_windows[]`(kind `qte`)에 선택 필드 `probe` {`success` 오라클, `setup`(새로고침 + 앞 단계 재생), `input`, `onset: unpredictable\|cued`, `choices`(가능한 버튼 수), `chain_id`}를 더한다. 드라이버는 3.3의 절차로 `acceptance_ms: [lo, hi]`, `window_source: probe\|visible`, `clock: virtual\|real`, `resolution_ms`, `trials`를 run.json에 쓴다. 판정: (a) 반응형은 P(성공) = F_RT(hi − L) − F_RT(lo − L), F_RT는 단순 반응(choices = 1, 버튼 고정) 또는 선택 반응 분포, L = 표시 + 입력 지연(기기별). (b) 예측형은 시간 오차 N(μ, σ)로 P(성공) = Φ((hi − c − μ)/σ) − Φ((lo − c − μ)/σ), c는 목표 시점. (c) 연쇄는 곱. 심각도 매핑은 지금과 같게 둔다: 프로필 P(성공) < 0.95 → P2, 20대 기준 P(성공) < 0.5 → P1. 작동하는 보조 옵션(느리게, 자동 완료, 누르고 있기 대체)이 있으면 한 단계 내린다. 탐침 필드가 없으면 지금처럼 보인 시간을 쓰고 `window_source: visible`(신뢰도 낮음)로 표시한다. | 수용 창과 보인 시간은 다를 수 있음(설계상 자명; 리듬 게임은 표시 없이 ±ms 창으로 판정: osu!, StepMania 원문) [industry]. 예측형 오차 SD 38.5–65 ms [snippet]. XAG 107 "필요한 타이밍과 속도 평가" [snippet]. Playwright 시계가 `performance`, rAF, 타이머, `Event.timeStamp`를 통제 [industry]. 현재 규칙이 예측형 창을 반응 시간으로 판정함(코드 확인) [derived] | 재현율: 보인 시간과 수용 창이 다른 QTE(늦게 열림, 짧은 인정 구간)에서 ↑. 소음: 예측형 입력(리듬, 타이밍 바)의 오탐 ↓. 유용성: "20대 0.88, 70대 0.33" 같은 연령별 성공 확률을 보고 | **H1:** 가상 시계 탐침은 수용 창 경계를 ±10 ms 안에서 복원한다. **지표:** 경계 절대 오차. **통과:** 가상 시계 픽스처의 ≥ 95 %에서 ≤ 10 ms, 실시간 폴백은 ≤ 30 ms(3회 반복, STF-16). **H2:** 판정이 바뀐 사례만 결함 목록을 바꾼다. **지표:** dev 3종 + dev-2의 GM-03 strict recall과 clean-control GM-03 단위 수. **통과:** recall 하락 0, clean-control 단위 증가 0. **데이터:** 새 게임 픽스처 12개(반응형 4: 짧은 창, 늦게 열림, 숨은 뒤 유예, 부분 인정; 예측형 4: 타이밍 바, 리듬 ±50/±150 ms; 연쇄 2; CSS 애니메이션 링 2), 각 픽스처에 저자가 선언한 참값 창 | M |
| GQA-02 | CHANGE | **GM-06을 연타 속도·누르고 있기 스윕으로 바꾼다.** 시나리오 `probes[]`(kind `mash` 또는 `hold`) {`target`(selector, `hotspot:`, `{key}`), `success`, `setup`, `rates_hz` 기본 [2, 3, 4, 5, 6, 8, 10, 12], `max_ms` 15000, `hold_ms` 기본 [500, 1000, 2000, 3000, 5000], `alternatives[]`(설정 경로가 선언된 누르고 있기·토글·자동)}. 출력: `r_min_hz`(max_ms 안에 성공한 최저 속도), `presses_at_r_min`, `duration_at_r_min_ms`, `rate_independent`(2 Hz로도 성공), `hold_required_ms`, `alternatives[].works`. 판정(측정 기반, 프로필 무관): r_min > 2 Hz이고 작동하는 대안 없음 → P2; r_min > 5 Hz이고 대안 없음이며 과업 경로 → P1; 12 Hz로도 실패 → P1과 "사람에게 사실상 불가" 문구; 누르고 있기 ≥ 3,000 ms이고 토글 없음 → P2. 2 Hz·5 Hz·3 s는 [policy]로 표시한다. | XAG 107: 연타·3초 누르기가 배제 사례, "2–3초 이상" 누르기 [snippet]. GAG Intermediate [snippet]. AGI "Playable without Rapid Button Presses", "…Button Holds" [snippet]. TLOU2: 연타 → 누르고 있기, 누르고 있기 → 토글 [snippet]. osu! 스피너 초당 3–7.5회전 [industry]. 연령별 연타 규준은 확인 못 함(2.2.5) | 재현율: 실제 연타 관문 탐지 가능(지금은 스크립트 산물 1건). 소음: 스크립트가 여러 번 누른 것만으로 생기던 발견 제거. 유용성: "초당 6회 이상, 대안 없음"처럼 고칠 수 있는 수치 | **H:** 스윕이 픽스처의 r_min을 ±0.5 Hz 안에서 찾고, 대안의 작동 여부를 맞게 판정한다. **지표:** r_min 오차, 분류 정확도. **통과:** 픽스처 8개 모두 정확(연타 관문 r_min 3/5/8 Hz, 누르고 있기 대안이 있는 관문 1, 속도 무관 "많이 누르기" 2, 3초 누르기 2), clean-control GM-06 단위 0. **데이터:** 감쇠·이득을 아는 게이지 픽스처(dev-2 또는 새 게임 개발 스위트) | M |
| GQA-03 | CHANGE (동결 전 가능: 문구) | **IRIS와의 관계를 바로잡는다.** (a) 보고 문구 "인증 도구(EA IRIS/Harding)로 재검사"를 "IRIS는 인증 도구가 아니다(README 면책). IRIS 기본 설정은 프레임 전체 25%·전체 평균 휘도를 쓰므로 국소 섬광은 통과할 수 있다. IRIS 통과가 이 P0를 뒤집지 않는다. 방송·인증 목적이면 Harding FPA 등 인증 절차를 따로 밟는다"로 바꾼다. (b) `extended_failure`를 두 필드로 나눈다: `sustained_5s`(지금 규칙: 5초에 섬광 10회 이상)와 `iris_extended`(IRIS 규칙: 최근 5초 중 "1초 전이 수 4–6"인 시간이 4초 이상이고 현재 1초 전이 수 ≥ 4). 둘 중 하나면 P1. (c) `iris_warning`(1초 전이 ≥ 4)은 측정값으로만 기록하고 발견을 만들지 않는다. | IRIS `appsettings.json`, `TransitionTracker.cpp`, `Flash.cpp` [industry]. 2.1.3 표 | 재현율: 초당 2회가 4초 이어지는 연쇄를 P1로 잡음(지금은 통과). 소음: 거의 0. 유용성: 잘못된 인증 안내 제거 | **H:** 두 규칙은 경계에서만 다르다. **지표:** 합성 휘도 추적(초당 2회 × 4초, 3회 × 3.4초, 2.5회 × 5초, 2회 × 3초)에서의 판정표. **통과:** `iris_extended`가 IRIS 코드 논리를 옮긴 참조 구현과 100 % 일치. 가능하면 픽스처 녹화를 IRIS CLI로 돌려 대조. **데이터:** 단위 테스트용 합성 표본 | S |
| GQA-04 | ADD | **한 프레임 섬광을 놓치지 않는 캡처.** 단계 1(S): 실행마다 `min_detectable_flash_ms`(표본 간격의 95백분위)를 기록하고, 표본 간격보다 짧은 화면 변화가 있었다는 증거(DOM 경로의 16 ms 폴링 토글, 또는 캔버스 게임의 rAF 호출 수 대비 캡처 수)가 있으면 통과를 `inconclusive`로 바꾼다. 단계 2(M–L): 파일럿으로 캡처 방식을 고른다: (i) 지금의 CDP 스크린샷, (ii) `Page.startScreencast`, (iii) 캔버스 게임의 rAF 후크(각 프레임을 160 px 폭 2D 캔버스로 복사해 블록 휘도를 페이지 안에서 계산), (iv) `HeadlessExperimental.beginFrame` 60 Hz 결정적 캡처. | 무작위 위상 캡처가 16.7 ms 상태를 잡을 확률 20 fps 0.33, 24 fps 0.40, 30 fps 0.50 [derived]. Trace: 전이는 66 ms 이내 [paper]. `beginFrame` 정의 [industry] | 재현율: 짧은 섬광(1–2프레임)에서 ↑. 소음: 변화 없음(단계 1은 통과를 판정 불가로 바꿀 뿐). 유용성: 안전 P0의 누락 위험을 수치로 공개 | **H:** 방식 (iii) 또는 (iv)는 2프레임 이상 섬광을 ≥ 95 % 잡고 (i)은 못 잡는다. **지표:** 탐지율, 면적 기준 아래 섬광의 거짓 P0. **통과:** ≥ 95 % 탐지, 거짓 P0 0, 실행 시간 증가 ≤ 2배. **데이터:** 1·2·3프레임 섬광 × 4·5·8 Hz × 문턱 위/아래 면적 × DOM/캔버스 = 36개 픽스처 | S (1), M–L (2) |
| GQA-05 | ADD | **KWCAG 2.2 6.3.1 판정을 따로 낸다(한국어 보고서).** (a) 번쩍임: 초당 3–50회(경계 3.0 Hz 포함), 10인치 이상 화면에서 번쩍이는 면적 합 > 화면의 10% → `kwcag_6_3_1: fail`, 심각도 P1(WCAG 2.3.1도 실패면 P0 유지). (b) 깜빡임: 초당 3–50회 깜빡이는 요소에 정지 수단이 없음(선언된 정지 조작 없음, 판단 확인) → P2. 10인치 미만 화면에서는 면적 조건 대신 (b)만. 기기 대각선은 카탈로그 `diagonal_in`에서 읽는다. | KWCAG 2.2 6.3.1 본문과 해설 [standard] | 재현율: 한국 공공 기준 위반(3 Hz 경계, 정지 불가 깜빡임) 탐지. 소음: 3 Hz 깜빡이는 배지·커서가 있으면 약간 ↑. 유용성: 한국 준수 보고에 바로 쓰임 | **H:** 새 판정은 설계한 경계에서만 켜진다. **지표:** 경계 쌍 픽스처(2.9/3.0/3.1 Hz; 9 %/11 % 면적; 9.7인치/10.1인치; 정지 버튼 유무)의 판정, dev 스위트 clean-control 단위 증가. **통과:** 경계 쌍 모두 설계대로, clean-control 단위 증가 ≤ 1(증가분은 판정자 검토). **데이터:** STF-17 방식의 경계 쌍 픽스처 8개 | S |
| GQA-06 | ADD (가설 층부터) | **움직이는 줄무늬 패턴 선별(새 GM-07).** 블록 휘도 표본을 10° 시야 창과 화면 전체에서 2D FFT로 보고, 우세한 공간 주파수의 줄 수 ≥ 6(밝음–어둠 쌍 5 초과), 밝은 줄 상대 휘도 ≥ 0.25(200 cd/m² 기준에서 50 cd/m²), 0.5초 이상 지속, 연속 프레임에서 위상 이동·대비 반전이 있으면(움직임·진동·섬광) 면적이 화면 25% 이상 또는 0.006 sr 초과일 때 발견. 정지 패턴과 글자 블록은 제외한다(웹 문서의 긴 글에서 오탐이 나므로). 첫 단계는 가설 층, 검증 뒤 P1. | Harding 2005, Ofcom(정지 40 %, 움직임 25 %) [snippet]. IRIS `PatternDetection` 기본값(줄 6, 면적 25 %, 밝기 0.25, 0.5초; 기본 꺼짐) [industry]. GAG Basic의 "움직이는 반복 패턴이나 균일한 글자 25 % 이상" [snippet] | 재현율: 지금 없는 결함 범주(패턴 유발 발작 위험). 소음: 줄무늬 배경·체크 무늬에서 오탐 위험 → 가설 층으로 시작 | **H:** 움직이는 고대비 줄무늬를 잡고 정적 UI에서는 거의 안 켜진다. **지표:** 픽스처 탐지율, 실제 UI 스크린샷 30장과 dev clean-control의 오탐 단위. **통과:** 움직이는 6쌍 이상·25 % 이상 픽스처 100 %, 오탐 단위 ≤ 1. **데이터:** 줄 4/6/10쌍 × 정지/이동 × 면적 20/30/45 % 픽스처 12개, 공개 UI 스크린샷 30장 | M |
| GQA-07 | CHANGE | **GM-01을 XAG 101의 단위(어센더–디센더 잉크 높이)로 잰다.** 드라이버가 HUD·게임 surface 글자 요소마다 계산된 `font`로 Canvas `measureText(text)`의 `actualBoundingBoxAscent + actualBoundingBoxDescent`를 재서 `glyph_body_px`로 저장한다(한글만 있는 문자열은 그대로, 라틴 포함 문자열은 "bdpq"와 비교해 큰 값). GM-01은 `glyph_body_px`를 26 px(콘솔·TV·휴대 콘솔) / 18 px(PC) × (세로 해상도/1080) / DPR과 비교한다. iOS 11 pt 최소는 이미 코드에 있으므로 근거 태그만 [industry]로 올린다(tvOS 23 pt는 XAG 26 px보다 느슨해 추가하지 않음). 시각 16′ 판정은 그대로 둔다. | XAG 101 측정 정의 [snippet]. Apple HIG 게임 글자 표 [industry]. 현재 코드가 em을 비교함 [derived] | 재현율: 잉크가 작은 글꼴의 HUD 글자에서 ↑. 소음: 잉크가 큰 글꼴의 오탐 ↓. 유용성: 기준과 같은 단위라 반박하기 어려움 | **H:** `glyph_body_px`는 렌더링된 잉크 경계와 ±1 px 안에서 일치한다. **지표:** 픽스처 3개 글꼴(라틴 산세리프, 한글 고딕, 장식체) × 24–30 px의 오차, dev 게임 스위트의 GM-01 발견 변화. **통과:** 오차 ≤ 1 px, 판정이 바뀐 발견은 전부 판정자 검토에서 "기준에 맞는 변경". **데이터:** 픽스처 9개 + game-desktop v3 재분석 | S |
| GQA-08 | CHANGE | **GM-05 크기 규칙을 Apple HIG 게임 규칙에 맞추고, 가장자리 규칙을 기기 인셋으로 바꾼다.** (a) 자주 쓰는 게임 조작: < 7 mm(44 pt 상당) → P2, 연속 탭 조작 < 9.6 mm → P3(지금과 같음). (b) 보조 게임 조작(일시정지·메뉴·설정): < 4.4 mm(28 pt 상당) → P2, 4.4–7 mm는 통과(지금은 < 7 mm이면 P2). (c) `GAME_CONTROL_EDGE_MIN_MM` 2 mm 대신 기기 카탈로그에 `system_insets_mm`(홈 인디케이터 띠, 노치·Dynamic Island)를 방향별로 넣고 겹치면 P3. 인셋 값의 출처가 확보될 때까지 2 mm 규칙을 유지하고, 인셋 도입 뒤 2 mm 규칙은 ablation에서 고유 탐지가 0이면 뺀다. | Apple HIG: 자주 쓰는 조작 44 × 44 pt, 메뉴 28 × 28 pt, 홈 인디케이터·Dynamic Island와 겹치지 말 것 [industry]. Parhi 9.6 mm [paper, 기존] | 재현율: 변화 거의 없음(GM-05 고유 탐지 0, exp4). 소음: 4.4–7 mm 보조 조작 오탐 ↓. 유용성: 플랫폼 문서와 같은 문장으로 보고 | **H:** (b)는 clean-control 단위를 줄이고 결함을 잃지 않는다. **지표:** dev 3종 + dev-2의 GM-05 단위(결함/clean). **통과:** 결함 손실 0, clean 단위 비증가. **데이터:** 기존 녹화 재분석, 인셋 값 출처(Apple 문서) | S |
| GQA-09 | CHANGE | **GM-02를 "고정 버튼"에만 적용하고, 이동·카메라 영역과의 겹침을 본다.** (a) 시나리오 hotspot에 `floating: true`(엄지가 닿는 곳에 뜨는 가상 스틱)면 도달·이동 거리 판정을 건너뛴다. (b) `zones[]` {`kind: move\|camera`, `center`, `radius_mm`}를 선언하면 자주 쓰는 버튼 상자가 그 원과 겹칠 때 P3. (c) ablation에서 GM-02를 `top_band`와 `travel`로 나눠 보고, `travel > 35 mm`(휴지점이 [assumption])가 고유 탐지 0이고 clean-control 단위 ≥ 1이면 뺀다(CUT, 조건부). | Apple HIG: 자주 쓰는 버튼은 엄지 근처, 이동·카메라 원형 영역은 피하고, 이동 스틱은 엄지가 닿는 곳에 띄우기 권장, 보조 조작은 위쪽 [industry]. 휴지점 규준 없음(2.3.4) | 재현율: (b)로 새 P3. 소음: 떠 있는 스틱의 오탐 ↓, (c)로 추가 ↓ 가능. 유용성: 가정이 적은 규칙만 남김 | **H:** `travel` 규칙은 고유 탐지가 없다. **지표:** 규칙별 고유 탐지와 clean 단위(exp 재분석). **통과:** 기준대로 유지·삭제 결정, 결정은 decisions.md에 기록. **데이터:** 기존 녹화 + 떠 있는 스틱·겹침 픽스처 4개 | S |
| GQA-10 | ADD | **누름 상태가 엄지 밖에서 보이는가.** 드라이버 동작 `press_capture`: touchStart → 1–2프레임 진행 → 스크린샷 → touchEnd. 누르기 전과의 차이 중 터치점에서 반지름 r 밖의 변화 픽셀이 없으면(누름 효과가 전부 엄지 밑) 자주 쓰는 게임 조작에 P3. r은 7 mm [assumption]로 시작한다. | Apple HIG: "손가락이 조작을 덮고 있을 때도 보이는" 누름 상태 [industry] | 재현율: 새 P3 범주(현재 키 없음). 소음: 낮음(측정). 유용성: 터치 게임에서 흔한 "눌렸는지 모름"을 수치로 보임 | **H:** 빛남·확대 효과가 있는 버튼은 통과, 색만 바뀌는 작은 버튼은 실패. **지표:** 픽스처 분류 정확도. **통과:** 8개 모두 정확, dev clean 단위 증가 0. **데이터:** 누름 효과 4종 × 크기 2종 | M |
| GQA-11 | ADD | **접근성 주장 검증 모드.** 시나리오 `claims[]`에 스토어 태그·라벨을 적는다(AGI "Playable without Rapid Button Presses", "…Button Holds", Steam "Playable without Timed Inputs", App Store "Larger Text", "Sufficient Contrast", "Differentiate Without Color Alone", "Reduced Motion", "Captions"). 각 주장을 검사에 연결한다: 연타 → GQA-02(모든 연타 관문에 작동하는 대안), 누르고 있기 → GQA-02 hold, 시간 입력 → GQA-01(보조 없이 반응형 창 없음), 대비 → PC-01/PC-02, 색 → PC-03, 큰 글자 → SIT-06(큰 글자 재렌더) + LY-01, 움직임 → `prefers-reduced-motion: reduce` A/B, 자막 → GQA-12. 주장이 "일반적인 작업(common tasks)"에서 깨지면 `claim_mismatch` 발견: 과업 경로를 막으면 P1, 아니면 P2 [policy]. | AGI 24개 태그 [snippet]. Steam 태그 오용 비판 [snippet]. App Store 라벨 9종과 "common tasks" 평가 안내 [snippet] | 재현율: 벤치마크 키와 무관(새 범주). 소음: 낮음(각 검사가 이미 측정). 유용성: 출시 전 스토어 표시 점검이라는 분명한 쓰임 | **H:** 참/거짓 주장을 모두 맞게 가른다. **지표:** 주장 불일치 탐지율, 거짓 불일치. **통과:** 탐지 100 %, 거짓 0. **데이터:** 주장이 참인 픽스처 5, 거짓인 픽스처 5 | M |
| GQA-12 | CHANGE + ADD | **자막을 토스트 규칙에서 떼고 자막 규칙으로 판정한다.** 새 타이밍 창 kind `subtitle`과 `<track>` TextTrack 큐 자동 수집. 규칙: 한국어 초당 글자 수 = 글자 수(한글 1, 라틴·공백·부호 0.5) / 표시 시간 > 12(성인)·9(아동 대상) → P2(과업에 필요한 대사) 또는 P3; 줄당 16자 초과 또는 3줄 이상 → P3; 크기는 GM-01(XAG 104: XAG 101 최소 이상). `subtitle`은 CG-02에서 제외한다. | Netflix 한국어 기준(16자, 12/9 cps, 계산 규칙) [snippet, 2차 요약]. XAG 104 [V2, 게임 브리프]. CG-02가 자막에 토스트 기준을 적용하면 오탐(2.3.2) [derived] | 재현율: 청각 조건(AP-10의 선언만 된 조건)에 첫 측정 검사. 소음: 자막을 `transient_text`로 선언한 시나리오의 CG-02 오탐 ↓. 유용성: 컷신·동영상 QA | **H:** 규칙이 픽스처의 과속·과길이 큐만 잡는다. **지표:** 큐 단위 정확도, CG-02 clean 단위 변화. **통과:** 정확도 100 %, CG-02 오탐 0. **데이터:** WebVTT 트랙 4개(정상, 과속, 줄 초과, 3줄) | S |
| GQA-13 | CUT (동결 전 가능) | **GM-06 현재 규칙(스크립트 연속 8회)을 가설 목록에서도 뺀다.** GQA-02가 들어올 때까지 GM-06은 발견을 만들지 않는다. | dev 탐지 1건이 스크립트 산물이고, 스크립트가 누른 횟수를 셈(decisions.md, 게임 검토) | 재현율: 채점 변화 0(가설은 채점 제외). 소음: 가설 목록 ↓. 유용성: 검토자 시간 절약 | **H:** 채점 지표가 바뀌지 않는다. **지표:** dev 스위트 bench 결과 전후 비교. **통과:** 모든 채점 지표 동일. **데이터:** 기존 녹화 | S |
| GQA-14 | CHANGE | **QTE 모형의 동작 시간 이중 계산을 없앤다.** 반응 시간 과제는 자극에서 버튼 누름까지를 재므로 누르는 동작이 이미 들어 있다. 키보드·게임패드 버튼, 엄지가 이미 올라가 있는 터치 조작(GM-02 이동 거리 ≤ 10 mm [policy])은 `QTE_MOTOR_MS` = 0. 엄지가 이동해야 하는 터치 조작만 이동 시간을 더한다(지금 값 100 ms를 [assumption]으로 유지하거나 이동 거리 기반 Fitts 식). | Der & Deary의 단순·4지 선택 반응 시간은 버튼 응답 과제 [snippet]. Human Benchmark의 273 ms도 클릭까지 포함 [snippet]. 현재 식 `window − (RT + 100 + latency)` [derived, 코드] | 재현율: 영향 작음. 소음: 키보드·게임패드 QTE 오탐 ↓(100 ms 여유). 유용성: 모형 설명이 정확해짐 | **H:** 판정이 바뀌는 것은 키보드·게임패드 창뿐이다. **지표:** dev 스위트 GM-03 판정 변화 목록. **통과:** 결함 손실 0, 바뀐 판정은 전부 키보드·게임패드 창. **데이터:** 기존 녹화 | S |
| GQA-15 | CHANGE | **모형 기반 타이밍 판정에 민감도 띠를 붙인다.** GM-03(과 CG-02)의 판정을 반응 시간 ×0.8/×1.2, 지연(터치 50/200 ms, 데스크톱 10/50 ms), 예측형 σ 38/65 ms로 다시 계산해 `robust: true\|false`를 기록한다. 실패가 일부 조합에서만 나오면 `fragile`로 표시하고 P3로 제한한다. | 반응 시간 표·장르별 지연 원문 미확인(2.2.2, 2.2.4), 터치 지연 50–200 ms 범위 [snippet]. SIT-11(출처 정리), STF-15(보호 띠) | 재현율: 전 심각도 기준 변화 0, P0–P2 운영점에서 일부 ↓ 가능. 소음: 근거 약한 P2 ↓. 유용성: "가정에 민감한 결과"를 숨기지 않음 | **H:** GM-03 발견의 일부는 가정에 민감하다. **지표:** dev의 fragile 비율. **통과:** 게이트 없음(보고). fragile 비율 > 50 %면 반응 시간 보정 연구(UEM-17 방식)를 우선한다. **데이터:** 기존 녹화 | S |
| GQA-16 | ADD | **게임 제품용 Stage 0 사전 분포.** AP-08(한국 사전 분포)에 KOCCA 게임이용자 실태조사 표를 더한다: 연령 × 플랫폼(모바일·PC·콘솔·아케이드) 이용률, 공공데이터포털 원자료로 연령별 교차표. 게임 세그먼트 템플릿: 연령 × 플랫폼 × 입력 장치. 조건 facet: 청각(자막 의존, GQA-12), 운동(연타·누르고 있기 불가, GQA-02), 소리 끈 이동 중 맥락. 비율은 세그먼트 가중치에만 쓰고 보고하지 않는다. | KOCCA 2024: 이용률 59.9 %, 이용자 중 모바일 91.7 %, PC 53.8 %, 콘솔 26.7 %, 아케이드 15.1 % [report, snippet]. 장애 플레이어 추정 [snippet]. AP-08, AP-10 | 재현율: 시딩 스위트에서는 설계상 변화 없음. 유용성: 게임 surface의 `segments_affected`가 의미를 가짐 | **H:** 게임 브리프 2개에서 Stage 0가 근거를 추적할 수 있는 세그먼트를 만든다. **지표:** `audience-check` 통과, facet마다 출처, 예산이 닿지 않은 facet 목록. **통과:** 모든 facet에 출처, 검증 통과. **데이터:** 공개 게임 2종의 공개 자료 | S |
| GQA-17 | ADD | **게임 접근성 설정 투어(STF-10의 charter 형식).** 에이전트 과업: 첫 화면에서 설정을 찾아 각 옵션을 켠다. 드라이버가 다시 잰다: 글자 200 %(GM-01 재측정: HUD와 자막까지 커지는가), 자막 첫 실행 기본값, 누르기 → 토글·연타 → 누르고 있기(GQA-02 대안), QTE 보조(GQA-01), 섬광 줄이기(GM-04 A/B), 움직임 줄이기(`prefers-reduced-motion` 에뮬레이션과 게임 내 토글, 프레임 차이 에너지 비교). 옵션이 있는데 측정 효과가 없으면 P2(측정), 옵션이 없으면 P3(판단, XAG·GAG 권고). 설정까지 걸린 단계 수를 기록한다. | XAG 101/104 200 %, XAG 117 [snippet]. TLOU2 옵션 [snippet]. 기본값이 사용률을 정함(90–95 % 대 50–60 %) [snippet]. Apple HIG: 글자 크기·매핑·움직임 강도 조절 [industry]. 에이전트는 상태 도달에 쓰고 측정은 드라이버가(2.5.2) | 재현율: 새 범주("작동하지 않는 옵션"). 소음: 낮음(A/B 측정). 유용성: 게임 인증·스토어 태그 준비에 바로 쓰임 | **H:** 옵션 A/B가 고장 난 옵션만 잡는다. **지표:** 픽스처 분류 정확도, 에이전트의 설정 도달률. **통과:** 고장 탐지 100 %, 거짓 고장 0, 도달률 ≥ 90 %(실패는 `agent_limitation`으로 분리). **데이터:** 옵션이 작동/고장인 픽스처 게임 6개 | M |
| GQA-18 | KEEP | **수정 후 같은 시나리오·기기·프로필로 재생하는 7단계를 유지하고, 페르소나 수를 늘리는 대신 수정–재생 주기를 돌린다.** 포화 판단은 UEM-06을 따른다. | RITE: 원인이 분명하면 한 명 뒤에도 고치고 반복, 10명 뒤 안정, 이후 6명 무변경 [snippet] | 유용성: 발견 → 수정 → 확인이 한 주기 안에 끝남 | 해당 없음(과정 유지). STF-18 기준선 비교로 회귀를 잰다 | – |
| GQA-19 | KEEP | **GM-04의 10° 시야 블록 격자, DOM 16 ms 경로, `inconclusive` 정책을 유지한다.** IRIS 기본 설정으로 바꾸지 않는다. | WCAG 2.3.1 정의 [standard], Trace 면적 규칙 [paper], IRIS 기본은 화면 25%·전체 평균(2.1.3) [industry]. 휴대폰에서 IRIS 기본 문턱이 스킬의 약 4.4배(2.1.5) [derived]. 라이브 점검 30/30 | 재현율 유지. 안전 검사를 느슨하게 만드는 변경을 막음 | GQA-03, GQA-04 실험에 포함 | – |
| GQA-20 | KEEP | **타이밍은 측정으로 정하고, 에이전트가 실시간에서 실패한 것으로 정하지 않는다. 게임은 멈추거나 프레임 단위로 진행한다.** 에이전트는 상태 도달과 판단 가설만 맡는다. | 범용 화면 에이전트의 실시간 게임 진행이 매우 약함(VideoGameBench, 게임 브리프 [R]), 글리치 인식 43–83 %로 과제에 따라 흔들림 [snippet]. 성과가 큰 자동 테스트 시스템은 게임 상태 접근·전용 행동 공간을 씀(2.5.2) | 소음 ↓(에이전트 조작 실패를 결함으로 세지 않음) | 해당 없음(원칙 유지). LAT-16과 같음 | – |
| GQA-21 | ADD (가설 층) | **가로 두 엄지 파지에서 엄지가 핵심 HUD를 가리는가.** 휴지점(25 × 22 mm 인셋)에서 화면 안쪽으로 엄지·손 가림 다각형을 투영해 `hud`·`critical_message`와 겹치면 가설 P3. 기하는 [assumption]이라 보정 전까지 가설 층. | Apple 발표 자료: "엄지가 동작을 가리지 않고 중요한 버튼이 보이게" [snippet]. GZ-02의 한 손 가림 쐐기와 같은 발상. 가로 파지 가림 규준 없음 | 재현율: 새 가설. 소음: 가설 층이라 채점 영향 없음 | **H:** 판정자가 가설의 절반 이상을 타당하다고 본다. **지표:** 판정자 타당 비율(LAT-14 방식). **통과:** ≥ 0.5면 P3 발견으로 승격, 아니면 삭제. **데이터:** 가로 게임 픽스처 6개 | M |
| GQA-22 | ADD (가설 층) | **게임 조작 누름 피드백 지연 띠.** `game_control` 탭에 한해 CG-03을 게임 기준으로: 첫 화면 변화 > 100 ms → 가설 P3. DOM이 바뀌지 않는 캔버스 게임은 화면 차이로 잰다. | 탭 지연 지각 문턱 20–100 ms(Jota 2013) [snippet]. 장르별 허용치 원문 미확인 | 재현율: 새 가설. 소음: 가설 층 | **H:** 판정자 타당 비율 ≥ 0.5. **데이터:** 지연 50/100/150/300 ms 버튼 픽스처 | S |
| GQA-23 | ADD | **시간 입력이 있는 게임 시나리오에 연령 floor를 둔다.** 시나리오에 kind `qte` 창이나 `mash`·`hold` 탐침이 있으면, `audience.compose`가 audience의 최고령 운영자 세그먼트(없으면 60대)의 기본 프로필을 반드시 넣는다. 게임패드·키보드 입력 facet이 audience에 있으면 그 입력 장치 프로필도 하나 넣는다. | GM-03 판정이 연령에 크게 좌우됨: 터치 700 ms 창 성공 확률 20대 0.88, 60대 0.50, 70대 이상 0.33 [derived]. KOCCA: 50대가 두드러진 이용자층 [snippet]. 인클루시브 floor 규칙(AP-02) | 재현율: 연령 조건 QTE 결함이 예산 부족으로 빠지는 일을 막음. 소음: 프로필 1개 추가만큼. 유용성: 조건 귀속(`recall_condition_attributed`) 개선 | **H:** floor 없이 구성하면 일부 예산에서 연령 조건 GM-03 결함을 놓친다. **지표:** 예산 6/10/14에서 연령 조건 결함의 조건 귀속 재현율, floor 전후. **통과:** floor 후 모든 예산에서 누락 0, clean 단위 증가 ≤ 1. **데이터:** dev 게임 스위트 + GQA-01 픽스처 | S |
### 3.2 GM-06 연타 속도 스윕 설계 (GQA-02)

**공용 기반: 탐침 실행기(probe runner).** GQA-01, GQA-02, GQA-11, GQA-17이 같은 기반을 씁니다. 한 번 만들면 네 후보가 함께 움직입니다.

1. 시도마다 새 브라우저 컨텍스트를 엽니다. `addInitScript`로 `Math.random`을 시드 고정 PRNG로 바꿉니다(재생 결정성).
2. `clock: "auto"`면 이동 전에 `page.clock.install()`을 부릅니다. 같은 초기화 스크립트가 `AudioContext`와 `Worker` 생성자를 감싸 사용 여부를 표시합니다. 둘 중 하나가 쓰이면 시계가 게임 시간을 다 통제하지 못하므로 실시간 모드로 바꾸고 `clock: "real"`로 기록합니다(2.6).
3. `setup`(새로고침 + 시나리오 앞 n단계 재생)으로 관문 앞까지 갑니다.
4. 오라클은 `success`(보이는 selector, 속성 값 조건, 글자 정규식)와 선택적 `fail`입니다. 가상 시계 모드에서는 드라이버의 타이밍 창 폴러를 `runFor` 단계마다 직접 부릅니다(시계가 폴러의 `setInterval`도 멈추므로).
5. 읽기 전용 규칙은 그대로입니다. 탐침은 픽스처·테스트 빌드에서만 돌리고, 결제·게시·계정 변경이 있는 흐름에서는 돌리지 않습니다.

**시나리오 필드(추가형).**

```json
"probes": [
  {"id": "mash-gate-1", "kind": "mash",
   "target": "hotspot:hs-attack",
   "setup": {"reload": true, "steps": 4},
   "success": {"attr": {"selector": "#gauge", "name": "aria-valuenow", "gte": 100}},
   "fail": {"selector_visible": "#gate-failed"},
   "rates_hz": [2, 3, 4, 5, 6, 8, 10, 12],
   "max_ms": 15000,
   "hold_ms": [500, 1000, 2000, 3000, 5000],
   "alternatives": [{"id": "rapid-to-hold", "settings_steps": [{"action": "tap", "target": "#opt-rapid-hold"}], "input": "hold"}],
   "critical_path": true,
   "clock": "auto"}
]
```

`target`는 selector, `hotspot:<id>`, `{"key": "Space"}` 또는 두 버튼 번갈아 누르기용 목록(XAG 107의 "두 버튼 연타")입니다.

**절차.**

1. 각 속도 r에 대해 새 시도를 엽니다. 누르기 간격 Δ = 1000/r ms. 한 번 누르기는 터치면 touchStart → 30 ms → touchEnd, 키면 keydown → 30 ms → keyup입니다(12 Hz의 83 ms 간격에도 들어감). 누른 뒤 가상 시계는 `runFor(Δ − 30)`, 실시간은 Node의 표류 보정 스케줄러로 기다립니다. 매번 오라클을 읽고, 성공하거나 `max_ms`를 넘으면 멈춥니다.
2. 비단조 반응(너무 빨리 누르면 벌점)이 있을 수 있으므로 목록의 모든 속도를 돌립니다. 가상 시계에서는 15초 시도도 몇 초 안에 끝납니다. 실시간 모드는 속도마다 3회(STF-16의 3회 중 2회 규칙)이고, CDP 전송 시각에서 실제 달성 속도를 기록합니다.
3. `hold` 탐침: `hold_ms`를 오름차순으로 눌렀다 뗍니다. 성공한 가장 짧은 시간이 `hold_required_ms`입니다.
4. 대안: 선언된 설정 단계를 새 시도에서 실행한 뒤 대안 입력(누르고 있기, 한 번 누르기)으로 같은 관문을 시도합니다. 성공하면 `works: true`.
5. 게이지 속성이 있으면 누른 횟수 n(t)와 값 v(t)로 v = g·n − d·t를 최소제곱으로 맞춰 이론 최소 속도 r* = d/g를 교차 확인값으로 남깁니다.

**run.json 출력.** `probes[] = {id, kind, clock, trials[{rate_hz, achieved_hz, success, t_ms, presses}], r_min_hz, presses_at_r_min, duration_at_r_min_ms, rate_independent, hold_required_ms, alternatives[{id, works}], decay_fit{g, d, r_star_hz}, nondeterministic}`.

**판정(GM-06 v2, basis `measured`, 프로필 무관 목록 `PROFILE_INVARIANT_CHECKS`에 둠).**

| 조건 | 심각도 |
| --- | --- |
| 2 Hz로도 성공(`rate_independent`) | 연타 아님. 누른 횟수 > 30이면 정보 기록만 |
| r_min > 2 Hz, 작동하는 대안 없음 | P2 |
| r_min > 5 Hz, 작동하는 대안 없음, `critical_path` | P1 |
| 12 Hz로도 실패 | P1, "사람에게 사실상 불가" 문구 |
| `hold_required_ms` ≥ 3,000, 토글 없음 | P2 |
| 대안이 선언됐는데 작동하지 않음 | P2 ("옵션이 작동하지 않음", GQA-17과 같은 범주) |

2 Hz, 5 Hz, 3,000 ms, 30회는 [policy]입니다. XAG 107의 "2–3초 이상 누르기"와 연타 배제 사례, osu! 스피너의 초당 3–7.5회전이 크기를 정하는 참고점입니다. 연령별 인간 능력으로 심각도를 올리는 규칙은 규준을 확보할 때까지 두지 않습니다(2.2.5).

### 3.3 GM-03 수용 창 측정 설계 (GQA-01)

**시나리오 필드(추가형, `timing_windows[]`의 kind `qte`).**

```json
{"id": "qte-1", "selector": "#qte", "kind": "qte", "measure": "visible_duration",
 "probe": {"setup": {"reload": true, "steps": 6},
           "input": {"tap": "hotspot:hs-qte"},
           "success": {"selector_visible": "#qte-ok"}, "fail": {"selector_visible": "#qte-fail"},
           "onset": "unpredictable", "cue_target_ms": null, "cue_modality": "visual",
           "choices": 1, "chain_id": "boss-1", "chain_index": 0, "restart_on_fail": true,
           "resolution_ms": 5, "max_delay_ms": 3000,
           "assist": [{"id": "qte-auto", "settings_steps": [{"action": "tap", "target": "#opt-qte-assist"}]}]}}
```

`onset: "cued"`는 다가오는 표식·타이밍 바·박자로 목표 시점을 예고하는 입력이고, `cue_target_ms`는 시작 뒤 목표 시점입니다.

**절차(가상 시계).**

1. 새 시도, 시드 고정, 시계 설치, `setup` 재생.
2. 시작 시점 t0: 시계를 4 ms씩 진행(`runFor(4)`)하며 매번 selector의 표시 여부를 읽습니다. 처음 보인 시점이 t0이고 분해능은 4 ms입니다. 캔버스 게임처럼 DOM 표시가 없으면 스크린샷 차이나 게임이 노출한 상태 selector로 대신합니다.
3. 초기 추정: 보인 시간 `visible_ms`의 중간 δ = visible_ms/2에서 성공을 확인합니다. 실패하면 0부터 `max_delay_ms`까지 100 ms 간격으로 훑습니다.
4. 경계 정밀화: 성공 δ와 실패 δ 사이를 이분 탐색해 `resolution_ms`(5 ms)까지 좁힙니다. 아래 경계(늦게 열리는 창)와 위 경계(숨은 뒤 유예 포함)를 모두 찾습니다. 성공 구간이 여럿이면(부분 인정, Perfect/Good) 모두 기록합니다. 경계마다 약 6–10회, QTE당 12–20회 재생입니다. [derived]
5. 결정성 확인: 두 경계 δ를 3번씩 다시 돌려 결과가 다르면 `nondeterministic: true`로 표시하고 실시간 모드로 넘어갑니다.
6. 실시간 폴백: 시작 시점은 지금의 16 ms 폴러, 입력은 Node 시각 t0 + δ에 보냅니다. 실행 시작 때 루프백 지연(주입한 키가 격리된 리스너의 DOM 변경을 일으키기까지)을 20회 재서 중앙값을 뺍니다. δ마다 3회, 다수결.
7. 보조 옵션: `assist`마다 설정을 켠 새 시도에서 경계를 다시 찾습니다.

**run.json 출력.** `timing_windows[].probe_result = {acceptance_ms: [[lo, hi], …], onset_resolution_ms, window_source: "probe" | "visible", clock, trials, nondeterministic, assist[{id, acceptance_ms}]}`.

**판정(GM-03 v2).**

- 반응형(`onset: unpredictable`): P(성공) = Σ [F(hi − L − M) − F(lo − L − M)]. F는 로그정규 반응 시간 분포(CV 0.2)로, `choices` = 1이고 버튼이 고정이면 단순 반응, 아니면 선택 반응 값을 씁니다. L은 기기 지연(`INPUT_LATENCY_MS`), M은 GQA-14의 이동 시간입니다. 연령별 값은 SIT-11이 원표를 확보할 때까지 [assumption]입니다.
- 예측형(`onset: cued`): P(성공) = Σ [Φ((hi − c − μ)/σ) − Φ((lo − c − μ)/σ)], c = `cue_target_ms`, μ = −20 ms [assumption], σ = 46 ms(시각)·38.5 ms(청각) [snippet].
- 연쇄: P_chain = Π P_i. `restart_on_fail`이면 기대 시도 횟수 1/P_chain을 함께 적습니다.
- 심각도: 지금 규칙을 확률로 거의 그대로 옮깁니다(지금의 P1 조건은 20대 평균 RT로 여유가 음수인 것이고, 로그정규에서 평균은 중앙값보다 약간 커서 P(성공) ≈ 0.5 근처와 같음). 프로필 P(성공) < 0.95 → P2. 20대 기준 P(성공) < 0.5 → P1. 작동하는 `assist`가 있고 그 상태에서 프로필 P(성공) ≥ 0.95면 한 단계 내립니다. GQA-15의 민감도 띠에서 `fragile`이면 P3로 제한합니다.
- 보고: 연령대별 P(성공) 표(20대 … 70대 이상)와 연쇄 확률.
- `probe`가 없으면 지금처럼 보인 시간으로 계산하고 `window_source: "visible"`, 신뢰도 낮음으로 표시합니다. 이 경로 덕분에 탐침 필드가 없는 기존·held-out 스위트에서는 판정이 바뀌지 않습니다.

### 3.4 순서와 동결

1. **지금(heldout-2 동결 전에도 채점 영향 없음):** GQA-13(GM-06 현재 규칙 삭제), GQA-03(a)(IRIS 문구). GQA-03(b)는 판정을 바꾸므로 동결 전에 넣으려면 사전 등록 문서에 개정 항목으로 적고, 아니면 채점 뒤에 넣습니다.
2. **heldout-2 채점 뒤, dev-2에서:** S 크기 변경 GQA-07, GQA-14, GQA-15, GQA-08, GQA-09, GQA-05, GQA-12, GQA-16, GQA-23. 각 변경의 전후를 decisions.md에 기록합니다.
3. **탐침 실행기(3.2 공용 기반) 구현 후:** GQA-01, GQA-02, GQA-17, GQA-11. 그다음 GQA-04 단계 1과 캡처 파일럿, GQA-06·GQA-10·GQA-21·GQA-22(가설 층).
4. **평가:** 탐침 필드를 포함하는 새 blind 게임 스위트를 다른 에이전트가 쓰게 하고, 3.1 표의 통과 규칙을 채점 전에 사전 등록합니다. 저자에게 검사 ID는 알리지 않습니다(validation-and-limits.md의 기존 원칙).

---

## 4. Risks, open questions and what could not be verified (위험, 열린 질문, 확인하지 못한 것)

### 4.1 확인하지 못했거나 일부만 확인한 것

- **XAG 본문.** 101(26 → 52 px, body height 정의), 107(2–3초 이상 누르기, 연타 사례), 116–120 제목은 검색 발췌뿐입니다(learn.microsoft.com 차단). 과업 지시문의 "XAG 101: 1080p 28 px"는 XAG 발췌에서 찾지 못했습니다. 26 px로 둔 스킬 값이 발췌와 일치합니다. PC 18 px는 게임 브리프의 제3자 문서 확인([V1-3p])에 기댑니다.
- **Ofcom·Harding 2005 패턴 규칙**(쌍 5개 초과, 정지 40 %, 움직임 25 %, 50 cd/m², 0.5초)은 발췌뿐입니다. ITU-R BT.1702는 WCAG Understanding의 인용으로만 봤습니다.
- **인간 자료.** Der & Deary 2006의 연령대별 평균·표준편차, Ruff & Parker 1993의 연령별 두드리기 횟수, Claypool 2006의 장르별 지연, SMPTE 안전 영역 비율을 얻지 못했습니다. 예측형 오차 SD(38.5, 46.2, 65 ms)는 개별 연구의 발췌이고 연령 효과를 모릅니다.
- **Netflix 한국어 기준**의 12/9 cps와 글자 세기 규칙은 GitHub의 2차 요약에서 봤습니다(원문 차단). 검색 요약 하나는 17 cps라고 했는데, 영어 기준과 섞인 것으로 보입니다. 원문 대조 전에는 [policy] 값으로만 씁니다.
- **KWCAG 6.3.1**은 `a11ykr/kwcag22`의 비공식 게시본에서 읽었습니다. KS X OT0003 원문과 대조해야 합니다.
- **IRIS**는 2026-09-28의 main 브랜치 코드와 설정을 읽었습니다. 배포판·Unreal 플러그인의 기본값이 다를 수 있습니다. "IRIS에 66 ms 조건이 없다"는 것은 `Flash::CheckTransition`을 읽은 제 해석입니다.
- **브라우저 기능.** Playwright 시계의 통제 목록은 문서 원문으로 확인했지만 실제 게임(캔버스 + rAF)에서의 동작은 돌려 보지 않았습니다. `beginFrame`이 Playwright 번들 Chromium에서 되는지, `setEmulatedMedia`로 `prefers-reduced-motion`을 바꾸는 정확한 매개변수, Canvas `measureText`의 잉크 상자, TextTrack 큐는 이번 세션에서 원문을 열지 않았습니다.
- **자동 테스트 성과.** TITAN(82 % 대 18 %)은 저자 소속 회사의 자체 평가, 저자가 심은 버그, 시간 제한 조건입니다. VideoGameQA-Bench의 82.9 %는 다른 논문의 인용입니다. EA SEED와 ICARUS의 수치는 얻지 못했습니다.
- **스토어·규제.** AGI 태그의 판정 기준 원문(사이트 차단), App Store 라벨의 기준 원문, CVAA의 "achievable" 세부, PlayStation TRC·Nintendo Lotcheck의 광과민성 요구(비공개)를 확인하지 못했습니다.
- **KOCCA 2024** 수치는 보도 발췌입니다. 보고서 원문과 원자료는 열지 않았습니다.
- **찾지 못한 것.** 모바일 가상 조이스틱의 크기·위치에 관한 실험 연구 수치, Ubisoft La Forge의 AAA 게임 강화학습 내비게이션 결과, 게임 텔레메트리 히트맵의 결함 발견 수치, 게임 특화 think-aloud 비교 연구는 이번 검색 예산 안에서 확인하지 못했습니다.

### 4.2 권고안의 위험

- **탐침 실행기의 결정성.** 시드 고정은 `Math.random`만 다룹니다. `crypto.getRandomValues`, 네트워크 응답, Web Audio 시계, Worker 타이머, CSS 애니메이션 타임라인은 남습니다. 재생이 흔들리면 경계가 틀립니다. 결정성 확인(3.3의 5단계)과 3회 중 2회 규칙(STF-16), 실패 시 보인 시간으로 되돌리기로 막습니다.
- **가상 시계가 게임을 바꿀 수 있습니다.** 프레임 시간으로 난이도나 물리를 조정하는 게임은 가상 시계에서 다르게 움직일 수 있습니다. 픽스처에서 가상·실시간 탐침을 비교해 30 ms 넘게 다르면 둘 다 보고합니다.
- **비용.** QTE 하나에 12–20회, 연타 관문 하나에 속도 8개(실시간이면 × 3) 재생입니다. 실시간 모드는 관문당 최대 약 2분입니다. 탐침은 시나리오가 선언한 곳에서만 돕니다.
- **정책 문턱의 과적합.** 2 Hz, 5 Hz, 3초, 12 cps, 7 mm 반지름은 [policy]입니다. 개발 픽스처에서 조정하면 개발 스위트에만 맞춰집니다. 3.4의 사전 등록과 blind 평가로 막습니다.
- **판정의 중복.** KWCAG 판정(GQA-05)과 WCAG 판정(GM-04)이 같은 섬광에서 함께 나올 수 있습니다. 문제 단위로 묶고 보고서에서 한 항목 아래 두 기준으로 보여야 합니다.
- **패턴 검사의 오탐.** 줄무늬 디자인, 체크 무늬, 긴 글 블록에서 켜질 수 있습니다. 가설 층으로 시작하고 정지 패턴은 제외합니다(GQA-06).
- **주장 검증 문구의 무게.** "주장 불일치"는 법적 판정처럼 읽힐 수 있습니다. "측정한 조건과 과업에서 주장과 다른 결과"로 쓰고, 조건(기기, 설정, 과업)을 함께 적습니다.
- **같은 모델 계열의 벤치마크.** 새 게임 스위트도 Claude 계열 저자가 쓰면 validation-and-limits.md의 한계가 그대로 남습니다. 탐침 필드 형식은 공개하되 검사 ID와 문턱은 저자에게 알리지 않습니다.

### 4.3 열린 질문

1. 휴대폰 터치 QTE의 인간 모형은 "반응 시간 + 엄지 이동"이 맞는가? 한국 성인 약 20명 × 연령대 3개, 반응형·예측형 창, 휴대폰 2종으로 RT 분포와 σ를 맞추는 파일럿이 필요합니다(validation-and-limits.md의 보정 프로토콜에 항목 추가).
2. 연령별 엄지 연타 지속 속도(터치, 게임패드)의 규준을 어떻게 얻는가? 규준이 생기면 GM-06에 프로필 의존 심각도를 더할지 다시 판단합니다.
3. Web Audio 시계에 맞춘 리듬 게임의 판정 창을 브라우저에서 결정적으로 잴 방법이 있는가? `AudioContext`를 감싸 가상 시계에 묶을 수 있는지 시험이 필요합니다.
4. WCAG Understanding의 "341 × 256 CSS px, 즉 87,296 CSS px²" 문장은 문턱을 사각형 전체로 보는가, 25%로 보는가? 스킬의 기하 미상 폴백은 25% 해석(약 21,824 CSS px²)을 씁니다. W3C 이슈 확인이 필요합니다.
5. KWCAG의 "10인치 이상의 화면"은 기기 화면 대각선인가, 콘텐츠 표시 영역인가? 지금은 기기 대각선으로 해석했습니다.
6. 게임 설정 투어(GQA-17)에서 "옵션이 없음"을 판단이 아닌 측정으로 만들 수 있는가? 설정 화면의 접근성 트리 이름과 표준 옵션 사전(한국어·영어)을 맞춰 보는 방법을 시험할 수 있습니다.

