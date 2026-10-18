# 상황·연령 요인이 터치 입력, 읽기, 도달에 미치는 영향 (Situational and age effects on touch input, reading and reach)

작성일: 2026-09-28. `skills/remorsearch-ux-qa`(에르고노믹 페르소나 스웜 QA, 예전 이름
`ergonomic-persona-swarm-qa`)를 위한 연구 브리프다. 후보 ID 접두사는 `SIT-`이다.
연구만 했다. 코드, 벤치마크, 정답 키, 검증 기록은 바꾸지 않았고, 저장소에는 이 파일
하나만 썼다. 계산 스크립트는 세션 scratchpad(`sit/`)에만 두었다.
사용자 지시("한글로 해라")에 따라 본문은 한국어로 쓰고, 필드 이름·ID·논문 제목·단위는
원문 그대로 둔다. 결정 로그(`docs/validation/experiments/decisions.md`) Round 5가 이 브리프를
기다리고 있다: "Touch σ multipliers … Pending `situational-and-age-effects-on-touch.md`
(calibrate, cap or cut)". 답은 §3의 SIT-01~SIT-04다.

**증거 태그.**
- [standard]: 규범 문서 원문.
- [paper]: 동료 심사 논문을 원문(본문 텍스트)으로 확인한 값.
- [industry]: 벤더·기업 문서, 엔지니어링 블로그, 업계 통계.
- [report]: 설문·정부 통계.
- [snippet]: 검색 결과 요약·발췌로만 본 값. 원문 확인 전이다. `[snippet · paper]`처럼
  출처 종류를 함께 적는다.
- [derived]: 내가 계산한 값. 인용한 수치, 이 저장소의 코드(`ergoqa`), 또는 공개 원자료에서
  계산했다. 스크립트 이름을 적는다.
- [opinion]: 실무자 의견. 따로 적지 않으면 내 의견이다. 내가 제안하는 모든 임계값은 아래
  실험이 정하기 전까지 [opinion]이다.

**먼저 읽을 것.**

1. **원문 접근.** WebFetch가 시도한 모든 논문 호스트에서 `EGRESS_BLOCKED`를 돌려줬다
   (faculty.washington.edu, makeabilitylab.cs.washington.edu, eprints.gla.ac.uk,
   arxiv.org, link.springer.com, pmc.ncbi.nlm.nih.gov, www.ebi.ac.uk, api.openalex.org,
   api.semanticscholar.org, www.irit.fr, www.netlab.tkk.fi, 3dvar.com, mynkgoel.github.io).
   그래서 문헌 수치는 대부분 [snippet]이다. 게이트나 코드 상수로 쓰기 전에 원문으로 확인해야
   한다. 웹 검색은 30회 썼다.
2. **예외 두 가지.**
   - Parhi, Karlson & Bederson 2006은 이전 세션이 microsoft.com PDF에서 뽑은 본문
     텍스트(scratchpad `parhi.txt`)로 직접 읽었다 → [paper].
   - Findlater & Zhang 2020(ASSETS 최우수 논문)의 **공개 원자료**(github.com/leahkf/
     mouseandtouchinput, CC BY 4.0, 735명)를 받아 연령·떨림별 터치 오류를 직접 계산했다
     → [derived]. 이 브리프에서 원자료로 검증한 유일한 연령·떨림 수치다.
3. **결론 먼저.**
   - 현재 σ 배수의 **값**은 대체로 문헌 범위 안에 있다(보행 1.3–1.7, 60대 1.1–1.2).
     떨림 값은 조금 높고, 70대+와 대중교통은 근거가 없다.
   - 문제는 값보다 **구조와 심각도 정책**이다.
     - (a) 배수를 곱으로 쌓는다(엄지 1.3 × 보행 1.4 = 1.82).
     - (b) 배수를 Bi & Zhai 모델의 폭 비례 항(α·W²)까지 곱한다.
     - (c) 플랫폼 권장 크기(44 pt/48 dp ≈ 7–8 mm)를 지키는 타깃에도 프로필만으로 P2를 준다.
   - 그 결과 현재 모델은 "엄지 + 걷기"에서 18.2 mm, "엄지 + 경미한 떨림"에서 23.5 mm가
     있어야 Parhi의 9.2 mm 한 손 기준과 같은 오터치율이 나온다고 예측한다. 문헌 권고는
     걷기 11–14 mm, 고령자 8–11.4 mm다. 모델이 과하게 예측하는 것이다.
   - 권고는 "심각도 상한(SIT-01) + 분산 가산 구조(SIT-02) + 값·출처 보정(SIT-03)"이다.
     heldout-2에서도 조건 귀속 탐지가 0이면 조건부로 삭제한다(SIT-04).
   - 새로 더할 가치가 큰 것은 두 가지다. 노안·고령 프로필의 **큰 글자 렌더링 검사(SIT-06)**와
     **다크 테마 변형의 측정 검사(SIT-07)**다. 둘 다 사람들이 실제로 하는 보상 행동과 설정을
     따라간다.

---

## 1. 범위와 검색한 출처 (Scope and sources searched)

### 1.1 질문

- 걷기·대중교통·짐 든 한 손 사용이 터치 정확도와 읽기에 주는 효과의 크기는? 같은 오류율을
  내려면 타깃이 얼마나 커야 하나?
- 연령(고령자 터치 정확도, 떨림, 노안, 연령별 읽기 속도와 반응 시간)의 효과 크기는?
- 손 크기와 파지(엄지 기능 영역, 폰 크기, 왼손 비율, 태블릿 파지)는?
- 조명(햇빛 가독성, 반사, 다크 모드·야간)은?
- `ergoqa/params.py`의 각 상수가 문헌으로 지지되는가? 터치 σ 배수는 보정·상한·삭제 중 무엇을
  해야 하나?

### 1.2 읽은 저장소 맥락 (수정하지 않음)

- `skills/remorsearch-ux-qa/references/ergonomics/`: `workflow.md`, `human-factors-checks.md`,
  `persona-agent-protocol.md`, `validation-and-limits.md`.
- `docs/ergonomic-swarm-spec.md` §0, §2(profile), §6–7(observation, finding).
- `docs/validation/experiments/decisions.md`(Round 5 포함).
- `ergoqa/params.py`(상수와 태그), `ergoqa/profiles.py` 206–228행(σ 배수 계산),
  `ergoqa/checks.py` 600–665행(PT-04/PT-03), `ergoqa/hf/pointing.py` 47–76행(이중 가우시안).
- 형제 브리프: `docs/qa-discipline/` 4편(UEM-, STF-, AP-, LAT-)과 작성 중인
  `automated-ui-accessibility-testing.md`(AUT-). 기반 브리프: `docs/human-factors/`
  `motor-pointing.md`(MP-02, MP-11, MP-12), `handedness-grip-reach.md`(HGR-2, HGR-4, HGR-9),
  `perception-cognition.md`(PC-07, PC-08).
- 금지 경로(`benchmarks/`, `.ergo-bench/`, `.claude/`)는 열지 않았다.

### 1.3 원문·원자료로 확인한 것

- Parhi, Karlson & Bederson 2006, MobileHCI, "Target size study for one-handed thumb use on
  small touchscreen devices": https://www.microsoft.com/en-us/research/wp-content/uploads/2006/01/parhi-mobileHCI06.pdf
  (scratchpad `parhi.txt`로 읽음).
- Findlater & Zhang 2020, ASSETS, "Input Accessibility: A Large Dataset and Summary Analysis of
  Age, Motor Ability and Input Performance": https://dl.acm.org/doi/10.1145/3373625.3417031
  / 원자료 https://github.com/leahkf/mouseandtouchinput (`SummaryDataPerTrial N=735.csv`,
  `Data description.xlsx`).

### 1.4 검색 발췌로만 본 것 ([snippet])

걷기·짐·읽기
- Bergstrom-Lehtovirta, Oulasvirta & Brewster 2011, MobileHCI: https://dl.acm.org/doi/10.1145/2037373.2037396
- Ng, Brewster & Williamson 2014, CHI: https://www.researchgate.net/publication/266655673_Investigating_the_effects_of_encumbrance_on_one-_and_two-_handed_interactions_with_mobile_devices (원문 PDF https://eprints.gla.ac.uk/117068/1/117068.pdf 는 차단)
- Ng, Brewster & Williamson 2013, INTERACT, "The impact of encumbrance on mobile interactions": https://link.springer.com/chapter/10.1007/978-3-642-40477-1_6
- Musić & Murray-Smith 2016, *Human–Computer Interaction* 31(5): https://www.dcs.gla.ac.uk/~rod/publications/MusMur16.pdf
- Conradi, Busch & Alexander 2015, *Procedia Manufacturing*: https://www.sciencedirect.com/science/article/pii/S2351978915001833
- Perry & Hourcade 2008, Graphics Interface: https://graphicsinterface.org/proceedings/gi2008/gi2008-8/
- Nicolau & Jorge 2012, "Touch typing using thumbs": https://www.researchgate.net/publication/254005145_Touch_typing_using_thumbs_Understanding_the_effect_of_mobility_and_hand_posture
- Goel, Findlater & Wobbrock 2012, WalkType, CHI: https://dl.acm.org/doi/10.1145/2207676.2208662
- Kane, Wobbrock & Smith 2008, MobileHCI: https://dl.acm.org/doi/10.1145/1409240.1409253
- Schildbach & Rukzio 2010, MobileHCI: https://dl.acm.org/doi/10.1145/1851600.1851619
- Lin, Goldman, Price, Sears & Jacko 2007, *IJHCS* 65(9):759–769 (URL 미확보)
- Mustonen, Olkkonen & Häkkinen 2004, CHI EA: https://dl.acm.org/doi/10.1145/985921.986034

연령·떨림·크기
- Findlater et al. 2013, CHI: https://dl.acm.org/doi/10.1145/2470654.2470703
- Sultana & Moffatt 2019, *ACM TACCESS* 12(1): https://dl.acm.org/doi/10.1145/3300178
- Jin, Plocher & Kiff 2007, UAHCI: https://link.springer.com/chapter/10.1007/978-3-540-73279-2_104
- Kobayashi et al. 2011, INTERACT: https://opendl.ifip-tc6.org/db/conf/interact/interact2011-1/KobayashiHMAHI11.pdf
- Hwangbo, Yoon, Jin, Han & Ji 2013, *IJHCI* 29(9): https://www.tandfonline.com/doi/full/10.1080/10447318.2012.729996
- Park & Han 2010, *Int. J. Industrial Ergonomics*: https://www.sciencedirect.com/science/article/abs/pii/S0169814109001036 , https://www.sciencedirect.com/science/article/abs/pii/S0169814110000806
- 본태성 떨림 진폭(PubMed 11921117, "Is essential tremor predominantly a kinetic or a postural tremor?"): https://pubmed.ncbi.nlm.nih.gov/11921117/
- Azenkot & Zhai 2012, MobileHCI(자세별 터치 분포; 수치 못 얻음): https://dl.acm.org/doi/10.1145/2371574.2371612

노안·읽기·반응 시간
- Hamasaki, Ong & Marg 1956 인용 발췌, "Static aspects of accommodation: age and presbyopia": https://www.sciencedirect.com/science/article/pii/S0042698997003362
- Boccardo, Gurioli & Grasso 2023, *PLOS ONE*: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0282947
- Calabrèse et al. 2016, *IOVS* 57(8):3836–3843: https://iovs.arvojournals.org/article.aspx?articleid=2537421
- Der & Deary 2006, *Psychology and Aging* 21(1):62–73: https://pubmed.ncbi.nlm.nih.gov/16594792/

손·파지·도달
- Bergstrom-Lehtovirta & Oulasvirta 2014, CHI: https://dl.acm.org/doi/10.1145/2556288.2557354
- Hoober 2013, UXmatters: https://www.uxmatters.com/mt/archives/2013/02/how-do-users-really-hold-mobile-devices.php
- Clark, "How We Hold Our Gadgets", A List Apart: https://alistapart.com/article/how-we-hold-our-gadgets/
- Papadatou-Pastou et al. 2020, *Psychological Bulletin*: https://www.researchgate.net/publication/340407298_Human_handedness_A_meta-analysis
- 한국인 2,437명 손잡이 조사, *Ergonomics* 2009: https://pubmed.ncbi.nlm.nih.gov/19851904/
- 선호 손별 QWERTY 입력 비교(한국): https://www.sciencedirect.com/science/article/abs/pii/S0169814113000784

조명·글자 크기 설정
- DisplayMate 결과 보도(NotebookCheck): https://www.notebookcheck.net/DisplayMate-awards-the-Best-Smartphone-Display-title-to-the-iPhone-14-Pro-Max.658334.0.html ; DisplayMate 밝은 환경 비교: https://www.displaymate.com/Smartphone_Brightness_ShootOut_1.htm
- Piepenbrock, Mayr & Buchner 2013, *Ergonomics* 56(7):1116–1124: https://pubmed.ncbi.nlm.nih.gov/23654206/ ; 2014, *Human Factors*: https://journals.sagepub.com/doi/abs/10.1177/0018720813515509
- Dobres, Chahine & Reimer 2017, *Applied Ergonomics* 60:68–73: https://pubmed.ncbi.nlm.nih.gov/28166901/
- Appt 글자 크기 통계: https://appt.org/en/stats/font-size ; "1 out of 5 iPhone users prefers large text": https://finance.yahoo.com/news/1-5-iphone-users-prefers-133000992.html

---

## 2. 핵심 지식 (Key knowledge)

### 2.1 걷기·이동 중 터치 (walking and transit)

- **걷는 속도와 정확도.** Bergstrom-Lehtovirta, Oulasvirta & Brewster 2011(MobileHCI):
  선호 보행 속도(PWS)에서 정확도를 유지하려면 속도를 26 % 줄여야 했다. 수행은 PWS의
  40–80 %에서 평탄했고, 속도가 오르면 조작 시간과 오류율이 나빠졌다 [snippet · paper].
- **스스로 늦춘다.** Musić & Murray-Smith 2016(*HCI* 31(5):420–471, 20명, 걸으며 게임):
  걷는 동안 터치점 정확도가 떨어졌다. 사람들은 폰을 쓰며 PWS의 약 75 %로 저절로 늦췄다.
  보행 위상에 맞춘 오프셋 모델이 오류를 14–30 % 줄였고, 정적 모델은 6–17 %였다
  [snippet · paper]. Ng et al. 2014에서도 조작 중 PWS가 16.3 % 떨어졌다 [snippet · paper].
- **버튼 크기 권고.** Conradi, Busch & Alexander 2015(*Procedia Manufacturing*, AHFE):
  5·8·11·14 mm 버튼, 서기 대 걷기.
  - 걷기는 크기 효과를 키웠다. 5 mm는 다른 모든 크기와 크게 달랐다.
  - 걷는 중에는 14 mm를 권했고, 11 mm도 오류가 적었으며, "다소 높은 오류를 감수할 수
    있으면" 8 mm도 된다고 했다 [snippet · paper].
  - 기반 브리프 MP-11은 오류 횟수를 서기 M = 18(SD 21), 걷기 M = 47(SD 56)로 적었다
    [snippet].
- **효과가 없던 연구.** Perry & Hourcade 2008(Graphics Interface): 한 손 엄지 탭에서
  걷기와 서기의 수행 차이를 찾지 못했다. 가장자리 타깃의 정확도가 가장 높았다
  [snippet · paper]. 걷기 효과는 과제·속도·경로에 따라 0부터 크게까지 흩어진다.
- **보상 기법.** WalkType(Goel, Findlater & Wobbrock 2012, CHI)은 가속도계로 보정해
  걷는 중 미수정 오류를 45.2 % 줄이고 속도를 12.9 % 올렸다(16명 데이터로 모델 구축)
  [snippet · paper]. 걷기 오류의 상당 부분이 무작위 확산이 아니라 보행 위상에 묶인
  **체계적** 오프셋이라는 뜻이다. 확산(σ)만 키우는 모델은 이 부분을 잘못 표현한다
  [opinion].
- **입력 품질.** Nicolau & Jorge 2012(22명; 앉기·느린 걷기·보통 걷기 × 한 손/양손 세로/
  양손 가로): 이동은 입력 품질을 떨어뜨리고 특정 오류 패턴을 만들었다 [snippet · paper].
- **대중교통.** 차량 진동에서의 터치 정확도 수치는 찾지 못했다. 현재
  `mobility_transit = 1.4`는 "걷기와 같다"는 가정일 뿐이다 [derived: params.py 49행].

**걷기 배수 1.4를 문헌에 대 본 결과.**
- `params.py`의 주석 "Ng, Brewster & Williamson 2014: +40 % thumb error walking"은
  **귀속이 틀렸다.**
  - Ng 2014의 +40 %는 **짐을 든 경우 대 빈손**의 선호 엄지 조준 오차(4.2 mm)다. 걷기 대
    서기가 아니다.
  - 걷기와 관련된 Ng의 수치는 따로 있다. 지배 손에 가방을 들고 PWS로 걸을 때 서 있을
    때보다 조준 오차가 최대 +112 %였다 [snippet · paper].
- Ng의 "조준 오차"는 타깃 중심에서 터치다운까지의 평균 거리(mm)다 [snippet · paper].
  체계적 오프셋이 섞인 지표라서 σ 비율로 바로 옮길 수 없다.
- Conradi의 서기/걷기 오류 비 47/18 = 2.61을 Bi & Zhai 모델에 맞춰 역산했다(크기별 시행
  수가 같다고 가정) [derived: `sit/conradi_modeC.py`, `sit_derive.py` E].

  | 모델 구조 | 서기 기준 | 역산한 걷기 배수 | 8 mm 걷기 오터치 |
  | --- | --- | --- | --- |
  | 현재(σ 전체에 곱) | 검지(k = 1) | 1.27 | 5.7 % |
  | 현재(σ 전체에 곱) | 엄지(k = 1.3) | 1.40 | 24.0 % |
  | 분산 가산(절대 항만) | 검지 | 1.33 | 5.3 % |
  | 분산 가산(절대 항만) | 엄지 | 1.74 | 20.3 % |

  서기 오류의 75–90 %가 5 mm 조건에서 나오므로, 이 역산은 사실상 5 mm 한 조건이 정한다.
- 정리: 걷기 단독 배수 1.3–1.7은 문헌 범위 안이다. 원자료로 맞춘 값은 아니다. 연구 사이
  편차가 0(Perry & Hourcade)부터 +112 %(가방 + 걷기)까지 크다. 기준 자세를 무엇으로
  두느냐에 따라 8 mm 걷기 오터치 예측이 5 %에서 24 %까지 바뀐다. 이 불확실성 폭이
  P2를 줄 근거로는 너무 넓다 [opinion].

### 2.2 짐을 든 한 손 사용 (encumbrance)

- Ng, Brewster & Williamson 2014(CHI): 쇼핑백·상자를 들고 목표 획득. 자세는 양손 검지,
  한 손 선호 엄지, 양손 엄지 세 가지. 짐을 들면 검지 정확도가 48.1 %로 떨어졌고, 선호
  엄지 조준 오차는 4.2 mm로 빈손보다 40 % 컸다. 지배 손이 비지배 손보다 더 영향을
  받았다 [snippet · paper].
- 짐은 파지를 바꾼다. 지배 손으로 짐을 들면 남은 손으로 한 손 조작을 해야 한다. 오른손잡이가
  왼손 한 손 파지를 쓰는 대표적 경로다 [opinion]. 한국 자료도 이를 지지한다. 2,437명
  조사에서 오른손잡이의 8.7 %가 버튼 누르기에 왼손을 선호했고, 다른 조사에서 오른손잡이
  107명 중 10 %가 한 손 문자 입력에 왼손을 선호했다 [snippet · paper].
- `ergo-profile.v1`에는 `context.free_hands`가 있지만 어떤 검사도 읽지 않는다. 형제
  브리프 AP-04는 이를 "모델 입력을 바꾸지 않는 facet"으로 분류했다
  [derived: profiles.py 206–223행].

### 2.3 연령과 터치 정확도·타깃 크기 (age)

**문헌.**
- Findlater et al. 2013(CHI): 고령자는 전반적으로 느렸지만, 터치스크린이 마우스보다 연령
  격차를 줄였다 [snippet · paper]. 기반 브리프 MP-12는 "터치가 이동 시간을 고령자 35 %,
  젊은 층 16 % 줄였다"고 적었다 [snippet].
- Sultana & Moffatt 2019(*ACM TACCESS* 12(1)): 작은 타깃에서 고령자가 더 느리고 오류가
  많았다. 고령자 오류는 **미스**(착지와 이탈이 모두 타깃 밖)가 **슬립**(착지 후 밀려
  나감)보다 흔했다 [snippet · paper]. 미스가 주 원인이면 확산(σ) 모델이 고령자 오류의 큰
  부분을 설명할 수 있다.
- Hwangbo et al. 2013(*IJHCI* 29(9), 한국 고령자, 5·8·12 mm × 간격 1·3 mm): 크기·간격·위치가
  모두 수행에 영향을 줬다. 오류는 5 → 8 mm에서 가파르게 줄고 8 → 12 mm에서는 훨씬 덜
  줄었다. 청각 + 촉각 피드백에서 수행이 가장 좋았다 [snippet · paper].
- Jin, Plocher & Kiff 2007(UAHCI): 고령자용 최소 버튼 11.43 mm, 간격 3.17–12.7 mm
  [snippet · paper]. (16.51–19.05 mm 권고라는 기억이 있지만 검색 요약에서는 확인하지
  못했다.)
- Kobayashi et al. 2011(INTERACT): 고령자에게 8 mm 이상 타깃을 권했다. 의도 위치와 실제
  터치 위치의 차이를 보정하고, 드래그·회전 제스처를 조심하라고 했다 [snippet · paper].
- Park & Han 2010(*IJIE*, 한국, 40명, 4·7·10 mm × 25 위치, 한 손 엄지): 시간 지표는 7 mm와
  10 mm가, 오류와 만족도는 10 mm만 가장 좋았다. 한 손 엄지용으로 10 mm를 권했다
  [snippet · paper].
- Parhi, Karlson & Bederson 2006 [paper: parhi.txt]:
  - 참가자 20명(남 17), 오른손잡이, 19–42세(평균 25.7). **서서**, 오른손 엄지로만 수행했다.
  - 엄지 길이 99–125 mm(μ 115, σ 5.75), 손 너비 75–97 mm(μ 88).
  - 3.8·5.8·7.7·9.6·11.5 mm 중 9.6 mm와 11.5 mm의 오류율 차이는 유의하지 않았다.
  - 9.6 mm에서 모든 위치의 2-SD 상자 최대치는 9.1 × 8.9 mm였다. 단일 탭 9.2 mm,
    연속 탭 9.6 mm를 권했다.
  - 저자들은 "이동 중 한 손 엄지 크기는 따로 연구해야 한다"고 적었다.

**공개 원자료로 직접 계산한 연령 효과** [derived: `sit/age_tremor.py`, `sit/age_decades.py`].
- 자료: Findlater & Zhang 2020의 터치(iPad) 포인팅 20,315시행. 공간 이상치 12건을 빼고,
  자기보고 운동장애가 없는 사람만 연령대로 나눴다.
- 폭 W는 32/64/96 pt다. iPad(132 ppi)에서 1 pt ≈ 0.19 mm, mini(163 ppi)에서 ≈ 0.16 mm이므로
  32 pt ≈ 5–6 mm다.
- 암묵 σ는 "중심에 맞춘 등방 가우시안 + 지름 W 원형 타깃"을 가정해 첫 시도 성공률에서
  역산했다: σ = (W/2) / √(−2 ln p_miss). 정사각형을 가정해도 비율은 같았다. CI는 참가자 단위
  부트스트랩(2,000회)이다. 스크립트는 세션 scratchpad에만 있으므로, 재현하려면 공개 CSV
  (`SummaryDataPerTrial N=735.csv`)에서 `DeviceType = TOUCH`, `TaskName = Pointing`,
  `IsSpatialOutlier = FALSE`, `Trial_W_Nominal ∈ {32, 64, 96}`로 거른 뒤 같은 식을 쓰면 된다.

| 집단 | 인원 | W32 미스 | W64 미스 | W96 미스 | σ 비율(W32, 18–39 대비) | 95 % 부트스트랩 CI | 중앙 이동시간 W32 / W64 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 18–39 | 266 | 17.2 % | 1.7 % | 0.2 % | 1.00 | 0.96–1.04 | 570–601 / 483–517 ms (20대–30대) |
| 40–49 | 37 | 13.5 % | 0.6 % | 0.0 % | 0.94 | 0.87–1.01 | 681 / 601 ms |
| 50–59 | 21 | 15.4 % | 1.1 % | 0.4 % | 0.97 | 0.87–1.08 | 685 / 600 ms |
| 60–70 | 11 | 23.1 % | 2.1 % | 0.0 % | 1.10 | 0.99–1.21 | 698 / 652 ms |
| 운동장애(떨림 제외) | 23 | 33.5 % | 6.6 % | 2.3 % | 1.27 (W64 1.23, W96 1.26) | 1.10–1.48 | – |
| 떨림 자기보고 | 9 | 21.7 % | 4.5 % | 0.0 % | 1.07 (W64 1.15) | 0.92–1.24 | – |

- 읽는 법: 60–70세는 젊은 층보다 약 20 %(W32)–30 %(W64) **느리게** 움직였고, σ는 약 10 %
  컸다. 속도를 희생해 정확도를 지키는 모습이다. 70세 이상은 1명뿐이어서
  `age_70s+ = 1.3`은 이 자료로 검증할 수 없다.
- 한계:
  - 참가자 대부분(314/368)이 온라인 크라우드 모집이다(자기 선택, 기기 제각각). 젊은 층 W32
    미스는 크라우드 18.2 %, 현장 11.3 %였다. 절대값보다 비율을 믿어야 한다.
  - 한 손 엄지나 걷기 자료가 아니다.
  - 떨림은 자기보고라서 심한 정도를 모른다.
- 결론: `age_60s = 1.15`는 CI 상단(1.21) 안이다. 1.10으로 낮춰도 된다. `age_70s+ = 1.3`은
  근거 없는 가정으로 남는다.

### 2.4 떨림 (tremor: essential tremor, Parkinson)

- **진폭.** 본태성 떨림(ET)을 가속도계로 재면 자세 떨림 평균 0.51 mm(SD 0.66), 운동
  (kinetic) 떨림 평균 2.91 mm(SD 2.11)였다. ET의 자세 떨림 주파수는 4–12 Hz다.
  파킨슨병은 안정 시 떨림이 특징이라 움직이는 동안 줄 수 있다 [snippet · paper:
  PubMed 11921117]. 진폭이 0-정점인지 정점-정점인지는 확인하지 못했다.
- **유병률.** 65세 이상 ET 4.6 %(전 연령 0.9 %, 연구별 0.8–20.5 %), Louis & Ferreira 2010
  [snippet, 기반 브리프 MP-12].
- **떨림을 더해지는 잡음으로 보면** [derived: `sit_derive.py` F와 같은 계산].
  - 사인파 변위의 무작위 위상 SD는 진폭이 0-정점이면 A/√2, 정점-정점이면 A/(2√2)다.
  - 평균 ET 운동 떨림 2.91 mm를 8.1 mm 타깃의 엄지 σ(≈ 1.9 mm)에 분산으로 더하면 등가
    배수는 1.14(정점-정점 해석)–1.47(0-정점 해석)이다.
  - 평균 + 1 SD(≈ 5 mm)는 1.36–2.10이다.
  - 한 손 사용에서는 폰과 엄지가 같은 손으로 함께 흔들려 상대 변위가 더 작을 수 있다
    [opinion].
- **원자료.** 떨림 자기보고 9명의 σ 비율은 1.07–1.15(CI 0.92–1.24)였다 [derived, §2.3 표].
- **결론.**
  - `tremor_mild = 1.5`는 평균 ET 운동 떨림을 0-정점으로 읽을 때의 상한과 비슷하고, 자기보고
    표본보다 크다. 1.3이 두 근거의 가운데다.
  - `tremor_moderate = 2.25`는 중등도–중증 ET와 맞을 수 있지만 범위의 끝이다. 1.8이
    가운데다.
  - 둘 다 **직접 측정한 터치 σ 배수가 아니다.** 떨림은 탭 정확도보다 드래그, 길게 누르기,
    이중 탭, 시간 제한에서 더 문제가 된다(MP-12). 결정적 검사로 옮기기도 이쪽이 쉽다.

### 2.5 노안과 시거리 (presbyopia, near point, viewing distance)

- **조절력 감소.** 객관적으로 잰 조절력은 연간 약 0.3 D씩 거의 직선으로 줄어 50세 무렵
  0에 가깝다(Hamasaki, Ong & Marg 1956 인용). 근거리 시력이 눈에 띄게 불편해지는 시점은
  40–45세다 [snippet · paper]. 3세부터 잰 연구는 감소가 S자형이라고 보고했다(Anderson
  et al., *IOVS*; 제목만 확인) [snippet].
- **폰 거리로 옮기면** [derived: `sit_derive.py` H].
  - 30 cm를 보려면 3.33 D가 필요하다. 오래 편히 보려면 조절력의 절반 이하만 쓴다고 보면
    6.67 D가 있어야 한다.
  - Hofstetter 평균식(18.5 − 0.3 × 나이)으로는 6.67 D 아래로 떨어지는 나이가 약 39세,
    3.33 D 아래가 약 51세다. 최소식(15 − 0.25 × 나이)으로는 각각 약 33세, 47세다.
  - 따라서 교정하지 않으면 폰 거리에서 40대부터 불편하고, 50대 초에는 30 cm에 초점이 맞지
    않는다.
- **사람들은 보상한다.** Boccardo, Gurioli & Grasso 2023(*PLOS ONE*): 비노안(40세 미만)
  157명과 노안(40세 초과) 60명이 스마트폰 문자를 읽을 때, 노안군이 **더 먼 거리와 더 큰
  글자**를 썼다. 글자의 가장 작은 세부가 만드는 **각크기는 두 집단이 같았다**
  [snippet · paper]. 45–55세의 약 80 %가 노안이라는 발췌도 있다 [snippet].
- **스킬에 주는 뜻.**
  - PC-04가 "고령 임계 글자 크기(CPS)를 정상 시거리에 적용하되 더 먼 시거리와 겹치지 않는다"고
    정한 것은 이 보상 행동과 맞다. 거리와 CPS를 둘 다 불리하게 잡으면 이중 계산이다.
  - 실제 사용에서 노안의 결과는 "흐림"보다 **"사용자가 글자를 키운다"**다. 그러니 제품이
    큰 글자에서 깨지지 않는지를 검사해야 한다(§2.13, SIT-06).
  - 한국 노안 유병률(연령별)은 이번에도 찾지 못했다.

### 2.6 연령별 읽기 속도와 임계 글자 크기 (reading speed and critical print size)

- Calabrèse et al. 2016(*IOVS* 57(8):3836–3843, MNREAD, 정상 시력, 8–81세)
  [snippet · paper]:
  - 최대 읽기 속도(MRS): 8–16세에 140 → 200 wpm으로 오르고, 16–40세에 200 ± 25 wpm으로
    안정되며, 81세까지 175 wpm으로 떨어진다(−12.5 %).
  - 임계 글자 크기(CPS): 8–23세 0.08 logMAR로 일정, 68세까지 0.21로 천천히, 81세까지 0.34로
    빠르게 커진다.
  - 읽기 시력(RA): 16세 −0.18에서 81세 −0.05로 나빠진다.
- **CPS 비율** [derived: `sit_derive.py` J]: 10^(0.21 − 0.08) = 1.35(68세),
  10^(0.34 − 0.08) = 1.82(81세). 스킬의 한글 CPS 비율은 0.52°/0.41° = 1.27(KJCP 2015,
  snippet)이다. 현재 `TEXT_MIN_ARCMIN_PRESBYOPIA = 31.2′`는 24.6′ × 1.27이다. MNREAD의
  68세 비율을 쓰면 33.2′, 81세 비율이면 44.8′다.
- **44.8′를 기기로 옮기면** [derived]. 300 mm 시거리에서 44.8′는 글자 크기 약 3.9 mm, Galaxy
  S24(0.1833 mm/CSS px)에서 약 21 CSS px다. 31.2′는 약 14.9 px다. KRDS 본문 기본값은
  17 px다(`human-factors-checks.md`). 즉 70대+ 층을 따로 두면 거의 모든 화면의 본문을
  표시하게 된다.
- **읽기 속도.** 스킬의 고령 값(60대 410, 70대+ 380 음절/분; 성인 587 대비 −30 %/−35 %)은
  한국어 화면 연구 하나(KJCP 2015: 296 → 208 wpm)에서 왔다. MNREAD는 최적 글자 크기와 평소
  교정에서 81세까지 −12.5 %만 보였다. 두 출처가 상충한다. 타이밍 검사(CG-02)는 이미 −1 SD
  독자 값(성인 330, 고령 290)을 쓰므로 판정에 주는 영향은 작다.

### 2.7 연령별 반응 시간 (reaction time)

- Der & Deary 2006(*Psychology and Aging* 21(1):62–73; 영국 Health and Lifestyle Survey
  7,130명 재분석): 단순 반응 시간(SRT)은 50세 무렵까지 거의 느려지지 않았고, 선택 반응
  시간(CRT)은 성인기 내내(20세부터) 느려졌다. 남성이 일관되게 빨랐고, 여성의 RT가 더 느리고
  변동이 컸다 [snippet · paper].
- 연령대별 평균값(ms)은 찾지 못했다. `CHOICE_RT_MS_BY_AGE`(20대 420 → 70대+ 580 ms,
  비율 1.38)의 **모양**(20세부터 단조 증가)은 지지되지만 **크기**는 확인되지 않은
  [assumption]이다. 이 값은 GM-03에서만 쓰이고, GM-03의 P1은 "젊은 성인 중앙값도 창을
  놓칠 때"로 제한되어 있다.

### 2.8 손 크기, 파지, 엄지 도달, 폰 크기 (hand size, grip and reach)

- **엄지 기능 영역 모델.** Bergstrom-Lehtovirta & Oulasvirta 2014(CHI): 손에 쥔 엄지가 닿는
  화면 영역을 (1) 화면 크기, (2) 손 크기, (3) 뒷면 검지 위치로 예측하는 2차식 모델이다.
  20명의 엄지 궤적에서 적합도가 높았다. 레이아웃에서 거꾸로 파지를 추정하는 데도 쓸 수 있다
  [snippet · paper]. 계수는 이번에도 얻지 못했다(원문 호스트 차단). RH-01의
  `thumb-reach-v3-uncalibrated`는 이 모델이 아니라 극좌표 휴리스틱이다.
- **파지 비율.** Hoober 2013(UXmatters; 거리·공항·정류장·카페·기차·버스에서 1,333회 관찰):
  한 손 49 %, 한 손으로 받치고 다른 손으로 누르기(cradle) 36 %, 양손 엄지 15 %. 한 손
  사용의 67 %가 오른 엄지, 33 %가 왼 엄지였다 [snippet · industry].
  `MOBILE_GRIP_SHARE`와 같다.
- **공공장소 편향.** 같은 계열 자료(Clark, A List Apart)는 폰 사용의 19 %만 앉아서였다고
  적었다 [snippet · industry]. 공공장소 관찰이라 걷기·서기가 많이 잡힌 표본이다. 가정 내
  사용 비율은 아니다.
- **폰 크기.** 기반 브리프 HGR-4가 정리했다: 6.1–6.9″ 폰에서 위쪽 띠는 전형적 손으로 파지를
  바꾸지 않으면 닿지 않는다. 폭 90 mm 대 60 mm에서 불편이 12.3 % 높았다(Lee et al. 2016,
  뒷면 검지) [기반 브리프 인용]. 이번에 새 수치는 더하지 않았다.

### 2.9 왼손잡이와 왼손 파지 (left-handedness)

- 세계: Papadatou-Pastou et al. 2020(*Psychological Bulletin* 메타분석): 가장 엄격한 기준
  9.3 %부터 가장 느슨한 기준(비오른손잡이) 18.1 %까지이고, 최선 추정은 10.6 %다
  [snippet · paper].
- 한국: 2,437명 조사(*Ergonomics* 2009)에서 왼손잡이 5.8 %, 양손잡이 7.9 %였다. 10대–30대가
  40대 이상보다 왼손잡이 비율이 높았고, 30대가 가장 높았다(7.3–7.6 %). 오른손잡이의 8.7 %가
  버튼 누르기에 왼손을 선호했다 [snippet · paper]. `HANDEDNESS_SHARE_KR`와 일치한다.
- 스킬에 주는 뜻: 왼손 한 손 파지는 손잡이만으로 정해지지 않는다(Hoober 33 %, 짐, 오른손잡이의
  왼손 선호). 왼손 floor(AP-02, HGR-2)는 dev에서 고유 결함 3–5개를 잡았으므로 유지한다.

### 2.10 태블릿 파지 (tablets)

- 태블릿 사용의 88 %는 앉아서였다(폰은 19 %). 탁자에서는 한 손으로 아래 1/3을 받치고 다른
  손으로 누르는 경우가 많았다 [snippet · industry: Clark/Hoober].
- 기반 브리프 HGR-9: 손에 든 태블릿은 양손 옆 파지, 엄지는 옆 띠에만 닿고 가운데는 닿지
  않는다. 그렇지 않으면 내려놓고 검지를 쓴다(Wagner, Huot & Mackay 2012) [기반 브리프 인용].
- 스킬은 이미 태블릿에 한 손 모델을 쓰지 않는다(결정 로그 RH-01 수정). 태블릿의 기본 파지를
  "내려놓거나 받치고 검지"로 두고, 양손 엄지는 문맥 근거가 있을 때만 facet으로 쓰는 편이
  위 관찰과 맞다 [opinion].

### 2.11 조명: 햇빛, 반사 (sunlight readability)

- **실측 반사율.** DisplayMate가 잰 스마트폰 화면 반사율 중 가장 낮은 값은 iPhone 14 Pro Max의
  4.5 %였다. 이 기기의 피크 밝기는 2,300 nit를 넘었고, 주변광 대비 등급은 100 % APL에서 228,
  피크에서 513이었다 [snippet · industry]. DisplayMate의 밝은 환경 비교 사진은 적분 반구 안에서
  6,500 K 확산광으로 찍었다 [snippet · industry]. 반사율 측정도 같은 조건인지는 확인하지 못했다.
- **현재 가정.** PC-05(가설 등급)는 2,000 nit, 50 klx, 반사율 ρ = 0.02로 WCAG ≈ 7.07을
  외부 여유로 삼는다(`params.py` 120행, `human-factors-checks.md`).
- **대비 계산** [derived: `sit_derive.py` I; L = Y·L_peak + ρE/π, 검정 수준 0].

  | 텍스트(흰 배경) | WCAG 대비 | 2,000 nit, ρ 0.02, 50 klx | 2,000 nit, ρ 0.044, 50 klx | 1,000 nit, ρ 0.02, 50 klx |
  | --- | --- | --- | --- | --- |
  | #000000 | 21 : 1 | 7.28 | 3.86 | 4.14 |
  | #595959 | 7.0 : 1 | 4.47 | 3.00 | 3.15 |
  | #767676 | 4.54 : 1 | 3.41 | 2.54 | 2.64 |

- **해석.**
  - ρ = 0.02는 실측 최저값(4.5 %)보다 낙관적이다. 다만 DisplayMate 값은 확산광 조건의 측정으로
    보인다(측정 조건은 확인하지 못함).
    직사광에서는 사용자가 기울여 정반사를 피하므로 실효 반사율이 더 낮을 수 있다. 어느 쪽도
    측정되지 않았다.
  - 어떤 가정이든 햇빛은 **모든** 텍스트의 대비를 함께 무너뜨린다. WCAG 비율의 순서는
    유지된다. 따라서 "7 : 1 미만" 규칙은 순위를 매길 뿐, 읽히는 텍스트와 안 읽히는 텍스트를
    가르지 못한다.
  - 결정 로그: PC-05는 고유 탐지 0, 깨끗한 대조 페이지 P3 17건, bright-sun 층이 결함 없이
    31건을 더했다. 판정자 의견도 갈렸다.
- ISO 9241-303, IEC 62679, ICDM IDMS의 주변광 대비 규정 원문은 확인하지 못했다(§4).

### 2.12 다크 모드와 야간 (dark mode and night use)

- Piepenbrock, Mayr & Buchner 2013(*Ergonomics* 56(7):1116–1124): 양극성(밝은 배경의 어두운
  글자)이 젊은 층과 고령층 모두에서 시력과 교정(proofreading) 수행에 유리했다. 고령 망막의
  조도 감소를 밝은 화면이 보상한다는 설명이다 [snippet · paper]. 2014년 후속(*Human
  Factors*)은 이 이점이 **작은 글자에서 특히 크다**고 했다 [snippet · paper].
- Dobres, Chahine & Reimer 2017(*Applied Ergonomics* 60:68–73, 짧게 보고 읽기): 양극성 이점이
  있었고, 단어를 정확히 읽는 데 필요한 시간은 **어두운 주변광에서의 음극성(검정 배경 흰
  글자)**이 가장 길었다 [snippet · paper].
- 뜻: 다크 모드는 야간에도 작은 글자의 가독성에서 불리할 수 있다. 그러나 WCAG 대비 공식은
  극성에 대칭이라 이 차이를 잡지 못한다. 수치 보정 근거(몇 % 더 커야 하나)는 없다. 반면 다크
  테마는 별도 색 토큰 세트라서 **대비 결함이 따로 생긴다**. 이것은 측정 가능하다(SIT-07)
  [opinion].
- 현재 `lighting: dark`는 어떤 검사도 읽지 않아 AP-04가 가지치기 대상으로 분류했다.

### 2.13 사람들이 실제로 하는 보상: 글자 크기 설정 (user text-size settings)

- Appt(2026년 2월): Android와 iOS 사용자의 26 %가 기본 글자 크기를 키운다
  [snippet · industry].
- Q42(iOS 사용자 150만 명): 33 %가 글자 크기를 바꿨다(20 % 키움, 13 % 줄임). 다른 표본에서는
  iPhone 사용자의 20 %가 큰 글자를 썼다(기본 73 %, 작게 7 %) [snippet · industry; Q42 원문
  URL은 확보하지 못함].
- Boccardo 2023: 노안군은 더 큰 글자를 쓰고, 근거리 불편을 더 많이 보고할수록 그 경향이
  컸다 [snippet · paper].
- 뜻: 한국 고령 사용자가 많은 제품에서 "기본 글자 크기로 렌더링한 화면"은 고령 사용자가
  실제로 보는 화면이 아니다. 노안·고령 프로필의 가장 현실적인 모델은 **큰 글자로 다시 그린
  화면**이다. 거기서 잘림, 겹침, 가로 스크롤, 작아진 터치 영역을 측정할 수 있다. 작성 중인
  AUT 브리프가 reflow와 OS 글자 크기 존중(Roselli 2026)을 다룬다. SIT-06은 그것을 어떤
  프로필이 켜는지와 그 근거를 맡는다.

### 2.14 σ 모델 구조 분석 (why the multipliers are noisy) [derived]

스크립트: `sit/structure.py`, `sit/final_set.py`, `sit_derive.py` A–C. 기기 변환은
`ergoqa.devices`를 그대로 썼다.

**44 × 44 CSS px의 실제 크기.** Galaxy S24 8.07 mm, Galaxy A55 7.51 mm, iPhone 15 7.27 mm,
Pixel 8 6.91 mm, Galaxy Z Flip6 6.89 mm다. 같은 CSS 크기도 기기에 따라 7 mm 기준을 넘기도
하고 못 넘기도 한다.

**현재 구조.** `profiles.touch_sigma_multiplier`는 자세·떨림·이동·연령 배수를 **곱한다**.
`pointing.dual_gaussian_sigma_mm`는 그 곱을 σ **전체**에 곱한다: σ = √(αW² + σa²) × Πk.
- FFitts/이중 가우시안에서 αW²는 타깃 폭에 비례하는 속도-정확도 항이고, σa²는 손가락의
  절대 정밀도 항이다(Bi, Li & Zhai 2013; 기반 브리프 MP-02, 저장소 `pointing.py` 26–58행)
  [snippet · paper + derived].
- 걷기·떨림·짐은 손과 기기의 추가 흔들림이다. 서로 독립인 잡음원은 **분산으로 더해진다**.
  그래서 절대 항에 더하는 편이 물리적으로 맞다 [opinion].
- 대안 구조 C: σ² = αW² + σa² × (1 + Σᵢ(kᵢ² − 1)). 조건 하나일 때 작은 타깃에서는 현재와
  같고, 큰 타깃과 조건을 겹칠 때만 덜 부풀린다.

**8.07 mm(S24의 44 CSS px) 주요 버튼의 예측 오터치율**

| 프로필 | 현재 값·현재 구조 | 현재 값·구조 C | 권고 값(SIT-03)·구조 C |
| --- | --- | --- | --- |
| 검지, 앉음(기준) | 1.1 % | 1.1 % | 1.1 % |
| 엄지 | 6.4 % | 4.5 % | 4.5 % |
| 받치기 + 걷기 | 9.1 % | 6.4 % | 6.4 % |
| 엄지 + 걷기 | 23.6 % | 11.6 % | 11.6 % |
| 받치기 + 경미한 떨림 | 12.3 % | 8.5 % | 4.5 % |
| 엄지 + 경미한 떨림 | 28.3 % | 13.9 % | 9.5 % |
| 엄지 + 중등도 떨림 | 56.6 % | 33.5 % | 21.5 % |
| 엄지 + 60대 | 12.1 % | 6.7 % | 5.9 % |
| 엄지 + 70대+ | 18.9 % | 9.5 % | 9.5 % |
| 엄지 + 70대+ + 경미한 떨림 + 걷기 | 67.8 % | 26.1 % | 22.2 % |

**같은 오류율에 필요한 정사각형 크기(mm).** 기준은 Parhi의 9.2 mm 한 손 엄지 타깃(현재
모델에서 오터치 3.78 %)이다.

| 프로필 | 현재 값·현재 구조 | 현재 값·구조 C | 권고 값·구조 C | 문헌 권고 |
| --- | --- | --- | --- | --- |
| 받치기 + 걷기 | 10.3 | 9.0 | 9.0 | 걷기 11–14 mm, 8 mm는 "오류 감수 시"(Conradi) |
| 엄지 + 걷기 | 18.2 | 10.5 | 10.5 | 〃 |
| 엄지 + 경미한 떨림 | 23.5 | 11.0 | 9.9 | 운동장애 18 mm(Findlater 2017, snippet) |
| 엄지 + 중등도 떨림 | > 60 | 15.4 | 12.8 | 〃 |
| 엄지 + 60대 | 11.6 | 9.1 | 8.9 | 고령 8–11.4 mm(Hwangbo, Kobayashi, Jin) |
| 엄지 + 70대+ | 14.9 | 9.9 | 9.9 | 〃, 한 손 엄지 10 mm(Park & Han) |
| 네 조건 겹침 | > 60 | 13.8 | 12.9 | – |

읽는 법:
- 현재 구조는 조건을 겹칠 때 문헌 권고를 크게 넘는다. 구조 C는 걷기·고령에서 문헌 범위 안에
  들어온다.
- 구조 C만으로는 결정 로그의 소음이 사라지지 않는다. "받치기 + 걷기"는 8.07 mm에서 여전히
  6.4 %(P2 기준 5 % 초과)다. 그래서 심각도 상한(SIT-01)이 따로 필요하다.
- Hwangbo(한국 고령자)의 "5 → 8 mm 개선이 8 → 12 mm보다 훨씬 크다"는 관찰과 비교했다. 8 →
  12 mm 개선폭 / 5 → 8 mm 개선폭은 현재 구조의 엄지 + 70대+에서 0.48, 구조 C에서 0.32, 검지
  + 70대+(구조 C)에서 0.21이다. 약한 근거지만 구조 C 쪽이 더 맞다.

### 2.15 `params.py` 상수별 판정 (verdict per constant)

| 상수(현재 값, 태그) | 문헌·원자료 | 판정 | 권고 |
| --- | --- | --- | --- |
| `one_hand_thumb` 1.3 [derived → assumption] | Parhi 원문 2-SD 상자 ÷ 4를 검지 모델과 비교하면 크기·축별 1.15–1.65(9.6 mm에서 1.46–1.48) [paper → derived] | 범위 안 | 유지 |
| `mobility_walking` 1.4 ["Ng 2014 +40 % walking"] | Ng의 +40 %는 **짐** 효과다. Conradi 역산 1.27–1.74, Perry & Hourcade는 효과 없음, 가방 + 걷기는 최대 +112 % | 값은 범위 안, **인용 오류** | 값 유지, 출처를 Conradi 역산과 MP-11로 교체, 구조 C, P3 상한(SIT-01~03) |
| `mobility_transit` 1.4 [assumption] | 자료 없음. 형제 브리프 R5: transit은 재현율·발견 수 모두 불변 | 근거 없음 | 걷기의 별칭으로 합치거나 층에서 제거 |
| `tremor_mild` 1.5 [assumption] | ET 운동 떨림 평균 → 1.14–1.47. 원자료 자기보고 1.07–1.15(CI ≤ 1.24) | 조금 높음 | 1.3 |
| `tremor_moderate` 2.25 [assumption] | ET 평균 + 1 SD → 1.36–2.10. 운동장애 집단 1.27(CI ≤ 1.48) | 범위 끝 | 1.8 |
| `age_60s` 1.15 [assumption] | 원자료 60–70세 1.10(CI 0.99–1.21) | 지지(조금 높음) | 1.10 [derived] |
| `age_70s+` 1.3 [assumption] | 원자료 70+ 1명. Hwangbo: 8 mm 이후 개선 작음 | 근거 없음 | 가정으로 유지, 보정 실험(SIT-14)에 70+ 포함 |
| `TOUCH_SIGMA_BASE_MM` 1.30 | √1.68(Bi & Zhai x 절대 항) | 계산 맞음 | 유지 |
| `TOUCH_TARGET_ONE_HAND_MM` 9.2, `TOUCH_TARGET_SERIAL_MM` 9.6 | Parhi 원문 확인 | 지지 [paper] | 유지 |
| `THUMB_LENGTH_MM` | Parhi 원문: 99–125 mm, μ 115, σ 5.75(20명 중 남 17). 한국 값은 손 길이 비례 가정 | Parhi 부분 확인 | 유지(한국 값은 가정) |
| `TOUCH_TARGET_MOTOR_IMPAIRED_MM` 18 | Findlater 2017 [snippet, 이번에 재확인 못 함] | 미확인 | 유지 |
| `MOBILE_GRIP_SHARE` 49/36/15 | Hoober 2013 [snippet · industry] | 확인 | 유지. 공공장소 관찰임을 주석에 |
| `HANDEDNESS_SHARE_KR` 86.3/5.8/7.9 | 2009 조사 5.8 %, 7.9 % [snippet · paper] | 확인 | 유지 |
| `LEFT_SHARE_BY_AGE_KR` | 2009 조사: 젊을수록 높음(30대 최고 7.3–7.6 %). Gallup 2025 값은 미확인 | 방향 일치 | 유지 |
| `DEFAULT_VIEWING_DISTANCE_MM` 폰 300 | Boccardo 2023: 노안군이 더 멀리, 더 큰 글자, 각크기는 같음 | 부분 지지 | 유지. 노안은 거리 대신 글자 확대로 모델링(SIT-06) |
| `TEXT_MIN_ARCMIN` 24.6, `TEXT_MIN_ARCMIN_PRESBYOPIA` 31.2 | MNREAD CPS 비율 1.35(68세) → 33.2′, 1.82(81세) → 44.8′ | 60대 지지 | 유지. 70대+ 층은 추가하지 않음(SIT-10) |
| Hofstetter 주석(15 − 0.25 × 나이) | Hamasaki: 연 0.3 D, 50세 무렵 ≈ 0 [snippet] | 지지 | 노안 적격 나이를 40대부터(SIT-09) |
| `READING_SYLLABLES_PER_MIN` 60대 410, 70대+ 380 | KJCP 2015 −30 % 대 MNREAD −12.5 %(81세) | 출처 상충 | 유지(보수적), 두 값을 모두 기록(SIT-11) |
| `CHOICE_RT_MS_BY_AGE` | Der & Deary 2006: CRT는 20세부터 계속 느려짐, SRT는 50세까지 평탄 | 모양 지지, 크기 미확인 | [assumption] 유지, 원표 확보(SIT-11) |
| `CONTRAST_BRIGHT_LIGHT` 7.0(2,000 nit, 50 klx, ρ 0.02) | DisplayMate 최저 실측 반사율 4.5 %(측정 조건 미확인), 피크 > 2,300 nit | ρ는 측정 안 된 가정이고, 규칙이 가독/비가독을 가르지 못함 | PC-05 계산 중단(SIT-08) |

---

## 3. 스킬에 대한 함의 (Implications for the skill)

결정 로그의 규칙(KEEP: 고유 탐지 또는 측정 기반 규범 검사; CUT: 고유 탐지 0이고 타당도
≤ 1/6 또는 깨끗한 대조 소음 ≥ 5; CHANGE: 판정자가 구체 원인을 지목; ADD: 연구 순위가 높고
드라이버로 측정 가능)을 따른다. 모든 ADD는 heldout-2에서 범주별로 평가하고 거기에 맞춰
조정하지 않는다. 표의 dev 수치는 exp4(`ablation-dev-def157e.json`) 기준이다.

| ID | Type | What exactly | Evidence | Expected effect on recall / noise / usefulness | Experiment that decides it (hypothesis, metric, pass rule, data needed) | Effort |
| --- | --- | --- | --- | --- | --- | --- |
| SIT-01 | CHANGE | **플랫폼 크기를 지키는 타깃의 프로필 전용 터치 발견은 P3까지.** `check_touch_accuracy`에서 기준 모델(k = 1)의 심각도가 없고, 라벨 포함 타깃의 짧은 변이 `TOUCH_TARGET_MIN_MM`(7.0 mm, 44 pt/48 dp의 물리 크기) 이상이면 PT-04와 PT-03(이웃이 `irreversible`이 아닐 때)의 프로필 전용 심각도를 P3로 제한한다. `measurement.sensitivity = true`와 조건(예: `context.mobility=walking`)을 기록한다. 예외로, `ergo-audience.v1`에서 촉발 프로필의 세그먼트가 그 조건의 문맥을 인용 근거와 함께 share ≥ 0.30으로 가지고 있고, 요소가 primary이거나 경로 위이면 P2를 허용한다("근거 연동 P2"). 7 mm 미만은 지금처럼 둔다(PT-02가 이미 P2). 데이터: DOM 박스, 기기 카탈로그, audience 파일(모두 이미 있음). | Conradi 2015(걷기 중 8 mm는 "오류 감수 시" 가능, 5 mm만 모두와 다름); Hwangbo 2013(한국 고령자: 8 → 12 mm 개선 작음); Kobayashi 2011(≥ 8 mm); Parhi 2006 [paper]; 결정 로그 Round 5(깨끗한 대조 P2 단위 7개 중 4개가 걷기·떨림 전용 44 × 44 CSS px); §2.14 | 재현율: dev 변화 없음 예상(배수를 꺼도 0 손실). 소음: 깨끗한 대조 P2 단위 7 → 3 예상(발견 수는 그대로, P3로 이동). 유용성: P0–P2 목록이 7 mm 미만이나 근거 있는 문맥만 남는다. | H: 상한이 걷기·떨림 전용 깨끗한 대조 P2 단위 4개 중 3개 이상을 없애고 어떤 운영점에서도 dev 결함을 잃지 않는다. 지표: 깨끗한 대조 P2 단위, `recall_strict`, `recall_strict_by_operating_point`(P0–P2), `recall_condition_attributed`. 통과: dev 엄격 재현율 0.906과 P0–P2 재현율 불변, 깨끗한 대조 P2 단위 ≤ 3. 데이터: exp4 녹화 재분석만. 이후 heldout-2에서 한 번. | S |
| SIT-02 | CHANGE | **σ 부풀림을 곱에서 분산 가산으로 바꾼다.** `dual_gaussian_sigma_mm(width, axis, ks)`: σ² = α·W² + σa²·(1 + Σᵢ(kᵢ² − 1)), i ∈ {자세, 이동, 떨림, 연령, 짐}. `profiles.touch_sigma_multiplier`는 목록을 돌려주고, 표시용으로 등가 배수 √(1 + Σ(kᵢ² − 1))를 기록한다. 기준(k = 1) 경로는 그대로다. 데이터: 없음(코드만). | FFitts/이중 가우시안의 두 항 구분(MP-02; `pointing.py`); 독립 잡음은 분산으로 더해짐; §2.14: 현재 구조의 같은 오류율 크기 18.2 mm(엄지 + 걷기), 23.5 mm(엄지 + 경미한 떨림)는 문헌 권고(걷기 11–14, 고령 8–11.4)를 넘고, 구조 C는 10.5, 11.0 mm; STF 브리프의 "조건을 겹치면 모델 벌점이 곱해진다" 위험 | 재현율: 영향 없음 예상. 소음: 8–11 mm 타깃의 프로필 전용 PT-04가 준다(엄지 + 걷기 8.07 mm 23.6 → 11.6 %, 11 mm 11.9 → 3.0 %). 네 조건 겹침 11 mm 56.1 → 10.2 %. 유용성: 극단 프로필이 모든 버튼을 표시하는 일이 없어진다. | H: 구조 C가 PT-04 프로필 전용 발견을 30 % 이상 줄이고 dev 결함을 잃지 않는다. 지표: PT-04 발견 수, 깨끗한 대조 단위, 고유 탐지, 요소 순위의 Kendall τ(A 대 C). 통과: dev 결함 손실 0, τ ≥ 0.9(순위 보존), 발견 −30 % 이상. 데이터: exp4 재분석. | S |
| SIT-03 | CHANGE | **`TOUCH_SIGMA_MULT` 값과 출처를 고친다.** `mobility_walking` 1.4 유지, 주석을 "[derived] Conradi 2015 역산 1.27–1.74(기준 자세·구조에 따라); MP-11"로 교체(Ng +40 %는 짐 효과). `encumbered` 1.4 [snippet · paper: Ng 2014, 엄지]를 새로 두고 SIT-12에서만 쓴다. `mobility_transit`는 걷기 별칭으로 합치거나 층에서 뺀다. `tremor_mild` 1.5 → 1.3, `tremor_moderate` 2.25 → 1.8 [derived: ET 진폭 + 원자료]. `age_60s` 1.15 → 1.10 [derived: 원자료 CI 0.99–1.21]. `age_70s+` 1.3 유지 [assumption, 근거 없음 명시]. `one_hand_thumb` 1.3 유지 [paper → derived]. | §2.1, §2.3, §2.4, §2.15; Findlater & Zhang 원자료 | 재현율: 영향 없음 예상. 소음: 떨림 발견 감소(받치기 + 경미한 떨림 8.07 mm 8.5 → 4.5 %). 유용성: 근거 추적이 정확해진다(감사 가능). | H: 어떤 dev 결함도 배수의 정확한 값에 의존하지 않는다. 지표: 값 집합 {현재, 권고, 각 ±0.1}별 프로필 전용 발견 수와 결함 탐지. 통과: 모든 집합에서 탐지 결함이 같다(그러면 값은 문서 문제일 뿐이다). 데이터: exp4 재분석. | S |
| SIT-04 | CUT (조건부) | **heldout-2에서도 조건 귀속 탐지가 없으면 조건 배수를 발견에서 뺀다.** SIT-01~03 뒤, heldout-2 채점(한 번)에서 PT-04/PT-03을 통한 걷기·떨림·60+ 조건의 `recall_condition_attributed`가 0이고, 이 배수들이 여전히 깨끗한 대조 단위 3개 이상을 만들면: 프로필 전용 PT-04를 가설 등급(`HYPOTHESIS_CHECKS`)으로 내리고 SIT-05의 크기 줄로 대체한다. `one_hand_thumb`는 남긴다(자세는 손가락 위치를 바꾸고 floor다). 같은 결과가 나오면 걷기 floor도 AP-03처럼 audience 근거 연동으로 바꾼다. 결정 로그 R5가 이미 "걷기 floor의 dev 근거는 모델링이 아니라 조건의 존재"라고 적었다. | 결정 로그(고유 0, 발견 19, 깨끗한 대조 단위 6, 걷기 조건 존재만); Perry & Hourcade 2008(걷기 효과 없음); 연구 간 편차(§2.1) | 재현율: dev 0 손실(배수 끄기 실험). 소음: 깨끗한 대조 단위 최대 −6. 위험: 실제 걷기 전용 문제의 조건 식별을 놓칠 수 있다. | 사전 등록 규칙: heldout-2 채점 전에 이 행을 결정 로그에 적는다. 지표: 조건별 `recall_condition_attributed`, 깨끗한 대조 단위. 통과(= 삭제): 걷기·떨림·60+ 조건 귀속 탐지 0 AND 해당 배수의 깨끗한 대조 단위 ≥ 3. 데이터: heldout-2 채점 결과. | S |
| SIT-05 | ADD | **보고서에 "같은 오류율 크기" 한 줄.** 7–9.2 mm의 primary·경로 타깃마다, 프로필 집합에 있는 조건별로 Parhi 9.2 mm 기준과 같은 오터치율을 내는 최소 정사각형 크기를 모델로 계산해 한 줄로 쓴다. 예: "권장 크기(모델·가정): 걷기 10.5 mm, 70대 9.9 mm, 경미한 떨림 9.9 mm — 문헌: 걷기 11–14 mm(Conradi), 고령 8–11.4 mm, 운동장애 18 mm". 프로필별 발견 여러 개를 설계 숫자 하나로 바꾼다. 데이터: 이미 있음. | §2.14 표; Conradi, Hwangbo, Jin, Park & Han, Findlater 2017 | 재현율: 중립. 소음: 감소(k개 발견 → 1줄). 유용성: 디자이너가 바로 쓸 숫자가 된다. | H: 판정자가 이 줄을 기존 프로필 전용 발견보다 실행 가능하다고 본다. 지표: 2차 판정에서 무작위 10개 타깃에 대해 A(현재 발견)와 B(크기 줄)의 "타당 + 실행 가능" 비율. 통과: B ≥ 4/6 타당, B가 A보다 높음. 데이터: 2차 판정 표본(이미 계획됨). | S |
| SIT-06 | ADD | **노안·고령 프로필은 큰 글자로 다시 그린 화면에서 측정한다.** `vision.presbyopia = true`이거나 연령 60대+인 프로필이 있으면 드라이버가 같은 화면을 큰 글자로 다시 렌더링한다. Android: `adb shell settings put system font_scale 1.3`(지원 기기에서 2.0도). iOS 시뮬레이터: `xcrun simctl ui booted content_size` 큰 값. 웹: (a) 320 CSS px 폭 = 200 % 확대 상당(WCAG 1.4.10), (b) 브라우저 기본 글자 크기를 키운 렌더링(Chromium 환경설정 또는 `:root` 글자 크기 주입; 방법은 검증 필요). 큰 글자 화면에서 LY-01(잘림), 텍스트 상자 겹침, 가로 스크롤(`scrollWidth > clientWidth`), 겹치거나 작아진 터치 영역(PT-01)을 재고, 사용자 글자 크기를 키워도 본문 계산 글자 크기가 그대로인 경우("글자 크기 무시")를 표시한다. 발견은 `variant: text_scale_1.3`처럼 변형을 기록하고 프로필과 무관하게 한 번만 센다. AUT 브리프의 reflow·OS 글자 크기 규칙과 규칙을 공유한다. 데이터: 재렌더링, 계산 스타일, 박스, 스크린샷. | Appt 26 %, Q42 33 %(키움 20 %), iPhone 20 % [snippet · industry]; Boccardo 2023(노안군은 큰 글자를 씀, 각크기 유지) [snippet · paper]; Calabrèse 2016(CPS 81세 1.82배); 45–55세 약 80 % 노안 [snippet]; 한국 70대+ 연령대 비중 14.6 %(`AGE_BAND_SHARE_KR`) | 재현율: 현재 스웜이 원리적으로 못 찾는 결함 부류를 연다(노안은 지금 기본 크기의 CPS 층으로만 모델링됨). 소음: 중간(의도된 말줄임 제외 규칙 필요). 유용성: 고령 사용자가 많은 한국 제품에서 높음. | H: 큰 글자 렌더링이 공개 앱·사이트 5개에서 앱마다 실제 레이아웃 결함을 1개 이상 찾고, 판정 타당도가 높다. 지표: 새 단위 수, 판정 타당도, 큰 글자 깨끗한 대조 단위. 통과: 타당도 ≥ 0.6, 스위트당 깨끗한 대조 단위 ≤ 2. 데이터: 드라이버의 재렌더링 지원, 큰 글자 결함을 심은 dev-2 스위트(별도 에이전트가 블라인드로 작성). | M |
| SIT-07 | ADD | **다크 테마 변형에서 측정 색 검사를 다시 돌린다.** 페이지가 `prefers-color-scheme: dark`에서 색을 바꾸면(Playwright `colorScheme: 'dark'`로 두 번 렌더링해 `body`·주요 텍스트의 계산 색을 비교해 판정), 다크 렌더링에서 PC-01/PC-02/PC-03을 다시 잰다. Android `adb shell cmd uimode night yes`, iOS `xcrun simctl ui booted appearance dark`. `lighting: dark` 프로필이 이 변형을 선택하게 해서, 지금은 아무것도 읽지 않는 facet(AP-04)에 실제 효과를 준다. 발견은 `variant: dark`로 기록한다. 데이터: 에뮬레이션, 계산 스타일, 스크린샷. | Piepenbrock 2013/2014(양극성 유리, 작은 글자에서 특히); Dobres 2017(어두운 주변광의 음극성이 가장 느림) [snippet · paper]; 다크 테마는 별도 토큰 세트라 덜 검증된다 [opinion] | 재현율: 다크 테마 대비 결함(측정, 규범) 추가. 소음: 낮음(같은 측정 규칙). 유용성: 다크 모드가 있는 제품에서 높음. | H: 다크 테마가 있는 실제 사이트·앱 10개 중 3개 이상에서, 라이트 모드에는 없는 대비 실패를 다크 변형이 찾는다. 지표: 변형 고유 측정 발견, 판정 타당도. 통과: ≥ 3/10, 타당도 ≥ 0.8. 데이터: 대상 목록, 에뮬레이션. | S |
| SIT-08 | CUT | **PC-05(햇빛 대비) 계산을 기본에서 끈다.** 코드는 플래그 뒤에 남긴다. 실외 문맥 근거가 있는 audience에는 보고서에 권고 문장만 넣는다: "핵심 텍스트는 7 : 1 이상, 가는 글꼴 피하기, 실기기 실외 확인". 주변광 모델의 ρ = 0.02는 "측정 안 된 가정"으로 태그를 바꾸고 DisplayMate 4.5 %(측정 조건 미확인)를 병기한다. | 결정 로그(고유 0, 깨끗한 대조 P3 17, bright-sun 층 +31 발견, 판정 갈림); §2.11(ρ 4.4 %면 21 : 1도 50 klx·2,000 nit에서 3.9 : 1; 규칙이 순위만 매김); AP-03 | 재현율: 변화 없음(고유 0). 소음: dev 실행당 가설 항목 −17. 유용성: 가설 목록이 짧아진다. 실행 시간 조금 감소. | 추가 실험 불필요. 결정 로그에 "고유 0, 판정 갈림, 물리 모델상 변별 불가"를 근거로 기록한다. 되살리는 조건: 실외 실측(조도계 + 휘도계 + 사람 판독) 자료가 생길 때. | S |
| SIT-09 | CHANGE | **노안 facet: 적격 나이를 40대부터로, 효과는 글자 확대로.** audience 구성에서 노안 기본값(50대+)은 두고, 40대 세그먼트도 노안 facet의 적격 대상으로 만든다(기본 켜짐은 아님). 노안 facet의 모델 효과를 (1) PC-04 고령 CPS 층(유지)과 (2) SIT-06 큰 글자 렌더링으로 정의한다. PC-04에서 고령 CPS와 먼 시거리를 겹치지 않는 현재 규칙은 유지한다. | Hamasaki(연 0.3 D, 50세 무렵 ≈ 0), 증상 40–45세 [snippet]; §2.5: 30 cm를 편히 보려면 6.67 D, 평균 조절력이 약 39세에 그 아래로 [derived]; Boccardo 2023(각크기 유지 보상) | 재현율: 40대 세그먼트에서 조금 증가 가능. 소음: 작음. 유용성: 40대 중심 제품의 타당성 향상. | H: 40대 노안 facet이 추가 발견을 만들 때 그 발견이 판정에서 타당하다. 지표: 40대 노안 프로필 전용 단위의 판정 타당도. 통과: ≥ 4/6 타당. 데이터: 40대 세그먼트가 있는 audience 파일 하나(heldout-2 또는 dev). | S |
| SIT-10 | KEEP | **PC-04 CPS 층 값은 유지하고, 70대+ 층은 만들지 않는다.** 24.6′/31.2′ 유지. MNREAD 81세 비율 1.82를 쓴 44.8′ 층은 S24·300 mm에서 약 21 CSS px라서 KRDS 기본 17 px 본문을 거의 모든 화면에서 표시하게 된다. 70대+는 SIT-06으로 보낸다. PC-04의 CPS 층은 dev 고유 결함 3개를 잡았으므로 유지한다(결정 로그). | Calabrèse 2016; §2.6 [derived]; KRDS; 결정 로그 PC-04 | 재현율: 유지. 소음: 새 소음원을 막는다. | 실험 불필요(추가하지 않는 결정). 70대+ 층을 다시 제안하려면 한국 70대 화면 읽기 CPS 실측이 필요하다. | S |
| SIT-11 | CHANGE | **읽기 속도·반응 시간의 출처 정리.** `READING_SYLLABLES_PER_MIN`의 고령 값(−30/−35 %)에 "한국어 화면 연구 1편, MNREAD −12.5 %(81세, 최적 크기)와 상충"을 주석으로 단다. CG-02는 −1 SD 값을 계속 쓴다. `CHOICE_RT_MS_BY_AGE`는 "모양은 Der & Deary 2006이 지지, 크기는 미확인"으로 태그하고, Der & Deary 원표(연령대별 평균 CRT)를 확보해 교체한다. | §2.6, §2.7 | 판정 변화 없음. 감사 가능성 향상. | 원표 확보 후: GM-03 판정이 바뀌는 dev 사례 수를 센다. 통과 조건 없음(문서화). | S |
| SIT-12 | ADD | **짐 든 상황을 파지로 모델링한다.** `context.free_hands == 1`(짐)이면 한 손 파지를 강제하고, 오른손잡이도 비지배(왼손) 한 손 파지를 짐 facet으로 허용한다. σ에는 SIT-02 방식으로 `encumbered` 1.4를 더한다. 가지치기 대상이던 `free_hands`(AP-04)에 모델 효과가 생기고, 오른손잡이의 왼손 사용이라는 왼손 floor의 기제가 명시된다. | Ng 2014(짐: 엄지 오차 +40 %, 지배 손 영향이 더 큼); 한국 오른손잡이 8.7 %(버튼)·10 %(한 손 입력)가 왼손 선호 [snippet]; Hoober 왼 엄지 33 % | 재현율: 걷기·운반 문맥의 왼손 도달 발견이 조금 늘 수 있음. 소음: 작음(RH-01 규칙 그대로). | H: 짐 facet이 왼손 floor와 다른 고유 결함을 찾지 못하면 효과가 없다. 지표: 짐 facet 프로필의 고유 단위. 통과: heldout-2에서 고유 단위 ≥ 1 또는 audience 근거가 있는 제품에서 판정 타당 ≥ 4/6. 데이터: 운반 문맥이 있는 audience 파일. | S |
| SIT-13 | KEEP | **왼손 floor와 Hoober 파지 비율 유지, 참고문헌 보강.** Papadatou-Pastou 2020(세계 10.6 %; 9.3–18.1 %), 한국 5.8 % + 7.9 %(2009), 오른손잡이의 왼손 사용을 `BASE_RATE_REFS`에 더한다. `MOBILE_GRIP_SHARE`에는 "북미 공공장소 관찰"을 주석으로 단다. | §2.8, §2.9; 결정 로그(왼손 한 손 고유 결함 3–5) | 재현율 유지. | 실험 불필요. | S |
| SIT-14 | ADD | **터치 σ 보정: 공개 원자료 먼저, 한국 파일럿은 다음.** (1) 지금: Findlater & Zhang의 `/alldata` 이동 궤적(터치 좌표 포함)으로 연령·떨림 집단별 σa를 성공률 역산이 아니라 **착지점 분포**에서 직접 적합하고 CI를 붙인다. (2) 다음: 한국 파일럿. 연령 3구간(20–39, 60–69, 70+) × {받치고 검지, 한 손 엄지} × {앉기, 실내 자기 속도 걷기} × 크기 {5, 7, 9, 11 mm}, 구간당 12명(총 36명), 1인 30분. 조건별 이중 가우시안 σa를 적합해 `TOUCH_SIGMA_MULT`를 CI와 함께 교체한다. | `validation-and-limits.md` 보정 프로토콜(그립당 약 20명 제안); §2.3 원자료 분석 | 가정을 측정값으로 바꾼다. 이후 SIT-03 값은 폐기된다. | H: 원자료 적합 σ 비율이 §2.3 역산 비율과 ±0.1 안에서 일치한다. 지표: 집단별 σa와 CI. 통과: 일치하면 SIT-03 값 확정, 불일치하면 원자료 값 채택. 데이터: (1) 공개 저장소 전체 클론(궤적 JSON 포함 1 GB 이상; `blob:none` 부분 클론에서 `git ls-tree -l`을 쓰면 모든 blob을 받으려 하니 주의), (2) 참가자 모집·기기·IRB 수준 동의 절차. | M(1) / L(2) |
| SIT-15 | CHANGE | **태블릿 기본 파지를 "받치거나 내려놓고 검지"로.** 태블릿 프로필의 기본 파지를 cradle(검지)로 두고, 양손 엄지 옆 파지는 audience 문맥(서서, 손에 들고)이 있을 때만 facet으로 쓴다. RH-01의 태블릿 도달 발견은 양손 엄지 프로필에서만 나온다. | 태블릿 사용의 88 %가 앉아서, 받치고 누르기 흔함 [snippet · industry]; HGR-9 | 재현율: 영향 작음(태블릿 도달 결함은 양손 엄지 facet이 계속 잡음). 소음: 태블릿 도달 발견 감소. | H: 기본 파지 변경이 dev 결함을 잃지 않고 태블릿 깨끗한 대조 단위를 줄인다. 지표: 태블릿 RH-01 단위, dev 재현율. 통과: 손실 0. 데이터: exp4 재분석. | S |

**순서와 의존성.**
1. SIT-01, SIT-02, SIT-03은 한 번의 dev 재분석으로 함께 평가할 수 있다. 셋 다 녹화를 다시
   할 필요가 없다.
2. SIT-04는 heldout-2 채점 **전에** 결정 로그에 규칙을 사전 등록해야 한다. 채점 후에 정하면
   사후 조정이다.
3. SIT-06과 SIT-07은 드라이버 변경이 필요하다. AUT 브리프의 reflow·글자 크기 규칙과 한 번에
   설계하는 것이 좋다.
4. SIT-14(1)은 다른 모든 값의 근거를 바꿀 수 있으므로, 여력이 있으면 SIT-03보다 먼저 한다.

**빼도 되는 것(요약).** PC-05 계산(SIT-08), `mobility_transit`의 독립 값(SIT-03), 조건
배수의 P2 권한(SIT-01), 조건부로 조건 배수 전체(SIT-04). **살을 붙일 것.** 큰 글자
렌더링(SIT-06), 다크 변형(SIT-07), 같은 오류율 크기 줄(SIT-05), 원자료 보정(SIT-14).

---

## 4. 위험, 열린 질문, 검증하지 못한 것 (Risks, open questions and what could not be verified)

**검증하지 못한 것.**
- 원문을 못 연 핵심 수치: Ng 2014의 조건별 표(서기·걷기·짐 × 자세), Conradi 2015의 크기별
  시행 수와 오류율, Bergstrom-Lehtovirta & Oulasvirta 2014 모델 계수, Jin 2007의 권고 크기
  (11.43 mm인지 16.51–19.05 mm인지), Kobayashi 2011의 실험 크기, Findlater 2013의 오류율,
  Der & Deary 2006의 연령대별 평균, Bababekova 2011의 시거리 값(검색에서 수치를 못 얻어
  인용하지 않음), 떨림 진폭 논문의 저자와 진폭 정의(0-정점 대 정점-정점).
- ISO 9241-303, IEC 62679, ICDM IDMS의 주변광 대비 규정 원문. 인용하지 않았다.
- 한국 연령별 노안 유병률, 한국 고령자 화면 읽기 속도의 두 번째 출처, 한국 태블릿·폰 파지
  비율, 대중교통 진동의 터치 정확도. 찾지 못했다.
- Q42 연구의 원문 URL.

**계산의 위험.**
- Conradi 역산은 크기별 시행 수가 같다는 가정과 오류 합의 비율 하나(2.61)에 기대며, 사실상
  5 mm 조건이 결정한다. 기준 자세 가정에 따라 1.27–1.74로 흔들린다.
- 원자료 분석은 첫 시도 성공률에서 σ를 역산했다. 슬립, 실수 터치, 시간 초과도 실패로 셌다.
  크라우드 표본이라 기기와 자세가 통제되지 않았다. 60–70세는 11명뿐이고 70세 이상은
  없다.
- 떨림 등가 배수는 진폭 정의와 "폰과 손가락이 함께 흔들린다"는 기하에 크게 좌우된다.
- 구조 C(분산 가산)도 가정이다. 걷기 오류의 상당 부분이 보행 위상에 묶인 체계적
  오프셋이라는 WalkType·Musić 결과는 어느 구조의 등방 확산 모델로도 표현되지 않는다.

**스킬 차원의 위험.**
- SIT-01의 "근거 연동 P2"는 audience 파일의 share에 기대므로, Stage 0 조사가 부실하면 P2가
  사라지거나 남용된다. share가 `unknown`이면 P3로 둔다.
- SIT-04로 조건 배수를 빼면 걷기 floor의 모델 효과가 거의 남지 않는다. 그러면 걷기는
  "보고서에 문맥을 이름 붙이는" 역할만 남는다. heldout-2가 이것을 판정하게 해야 한다.
  재설계는 그 다음이다.
- SIT-06은 드라이버와 플랫폼별 재렌더링 방법에 의존한다. 웹에서 "텍스트만 확대"를 신뢰성
  있게 재현하는 방법은 검증이 필요하다. 의도된 말줄임(전체 텍스트 접근 가능)을 결함으로 세지
  않는 규칙도 필요하다.
- SIT-07은 페이지가 다크 스킴을 지원할 때만 의미가 있다. 삼성 인터넷의 강제 다크 모드처럼
  페이지가 아니라 브라우저가 색을 바꾸는 경우는 다루지 않는다(사용률 미확인).
- 이 브리프의 벤치마크 효과 예측은 dev(학습용) 스위트 기준이다. 결정 로그의 규칙대로 모든
  ADD는 heldout-2에서 범주별로만 평가해야 한다.
- 같은 모델 계열 문제: 벤치마크 작성자, 탐지기 작성자, 판정자가 모두 Claude다
  (`validation-and-limits.md`). SIT-05·SIT-09·SIT-12의 판정 기반 통과 조건은 이 한계를
  그대로 물려받는다.

**열린 질문.**
- 걷기 문맥의 기본 share를 무엇으로 둘까? Hoober/Clark의 "폰 사용의 19 %만 앉아서"는
  공공장소 관찰이라 기본값으로 쓰기 어렵다.
- 한국 고령자의 실제 파지(한 손 엄지 대 받치고 검지) 비율은? 고령 프로필의 기본 파지를
  엄지로 두는 것이 맞는지 모른다. 원자료(Findlater & Zhang)도 파지를 기록하지 않았다.
- 떨림 프로필을 탭 정확도가 아니라 드래그·길게 누르기·시간 제한 쪽 결정적 검사로 옮기는
  것이 더 유용한가(MP-10, MP-12)? 이번 범위에서는 후보로 만들지 않았다.
