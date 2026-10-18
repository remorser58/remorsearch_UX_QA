# 결함 탐지기 평가: 벤치마크, 지표, 판정, 과적합 (Evaluating defect detectors: benchmarks, metrics, adjudication and overfitting)

작성: 2026-09-28. 후보 ID 접두사: `EVD-`. 사용자 지시에 따라 본문은 한국어로 쓰고, 논문·표준 이름, 필드 이름, 지표 이름, 원문 인용은 영어 그대로 둡니다.

> 상태: 완료 (2026-09-28). 1–4절 모두 작성. 모의실험 스크립트(`ci.py`, `prereg_sim.py`, `prereg_sim2.py`, `adj.py`, `fp.py`)는 스크래치패드에만 있고 저장소에는 넣지 않았습니다. EVD-03을 구현할 때 옮길 대상입니다.

**증거 태그.** [standard] 규범 문서 원문 · [paper] 동료 심사 논문, 원문 또는 공식 초록에서 확인 · [industry] 업체·기업 문서, 엔지니어링 블로그 · [report] 조사·정부 통계 · [snippet] 검색 발췌로만 봄(원문 미확인) · [derived] 내 계산 또는 이 저장소 파일에서 도출 · [opinion] 실무자 의견(따로 밝히지 않으면 내 의견).

## 1. Scope and sources searched (범위와 검색한 자료)

### 1.1 질문

1. 탐지 도구 벤치마크(심은 결함, 변이 분석, 정적 분석 벤치마크, Defects4J, 접근성 도구 벤치마크, 사용성 평가법 비교 연구)는 정답(ground truth), 매칭, 이중 계산을 각각 어떻게 다루는가?
2. 재현율·정밀도의 신뢰구간(Wilson, 군집 부트스트랩), 운영점, 비용 가중 지표, 범주별 보고, 심각도 일치, 문제 단위 매칭은 어떻게 해야 하는가?
3. 사람·LLM 판정: 일치도 지표(κ, α), 판정자 수, LLM 판정자의 편향(위치, 자기 선호), 눈가림은 어떻게 설계하는가?
4. 벤치마크 과적합: 홀드아웃·사전등록, 오염, Goodhart, 40–50개 결함에서 신뢰구간 폭, 다중 비교 통제.
5. 오탐 비용: 개발자가 참는 오탐 비율, 경보 피로, 그리고 깨끗한 대조 페이지(clean control)의 잡음 허용치.
6. 이 저장소의 검증 계획(`heldout-2-preregistration.md`, `decisions.md`, `ergoqa/bench.py`, 실행기 `scripts/ergo_eval.py`)이 위 문헌 기준으로 어디가 약한가? H1–H7 통과 규칙과 표본 크기는 충분한가? 유용성 주장을 믿을 만하게 하려면 무엇을 보고해야 하는가?

### 1.2 검색 조건 (태그를 믿기 전에 읽을 것)

- WebSearch 30회. WebFetch는 38회 시도했습니다.
- 이 세션의 네트워크 정책이 다음 도메인을 막았습니다: `owasp.org`, `arxiv.org`, `ar5iv.org`, `proceedings.neurips.cc`, `proceedings.mlr.press`, `aclanthology.org`, `openreview.net`, `huggingface.co`, `api.openalex.org`, `ui.adsabs.harvard.edu`, `samate.nist.gov`, `www.fda.gov`, `sv-comp.sosy-lab.org`, `pmc.ncbi.nlm.nih.gov`, `people.csail.mit.edu`, `discovery.ucl.ac.uk`, `coinse.github.io`, `www.kasperhornbaek.dk`, `www.markelvigo.info`, `www.alignmentforum.org`, `www.asc.upenn.edu`, `cameron.econ.ucdavis.edu`, `dmg5c1valy4me.cloudfront.net`. `homepages.rpi.edu`는 DNS 조회가 실패했고, `api.github.com`은 403을 돌려줬습니다.
- 그래서 논문 대부분은 검색 발췌로만 봤고 [snippet]으로 태그했습니다. 원문을 연 자료는 1.3에 따로 적었습니다. 발췌에 없는 수치를 기억으로 떠올린 경우에는 "기억, 미확인"이라고 적고 판단 근거로 쓰지 않았습니다.
- 이 저장소의 `benchmarks/`, `.ergo-bench/`, `.claude/`는 읽지 않았습니다. `docs/validation/*.json`과 `docs/validation/experiments/ablation-dev-*.json`(개발 스위트 결과, 답안 키 아님)은 읽었습니다.

### 1.3 원문을 직접 읽은 자료

| 자료 | URL | 확인한 내용 |
| --- | --- | --- |
| OWASP Benchmark 점수 규칙 (프로젝트 사이트 원본, GitHub) | https://github.com/OWASP/www-project-benchmark (`tab_scoring.md`) | 점수 = Youden index = TPR − FPR, 대각선 = "random guessing", 모두 보고하는 도구는 FPR 100 %, 범주별 행과 "Average TPR/FPR/Score", `expectedresults-1.2.csv`의 테스트마다 "single intentional CWE that is either a True or False Positive" |
| OWASP Benchmark Java v1.2 테스트 구성 | 같은 저장소 `tab_java_test_cases.md` | 테스트 2,740개, 범주 11개(XPath 35개 ~ SQLi 504개), 1.1부터 "both true positives and false positives in every vulnerability area" |
| Defects4J README | https://github.com/rjust/defects4j | 활성 버그 854개 + 폐기 10개, 프로젝트 17개. 버그 기준: 이슈 트래커 연결, 단일 커밋 수정, 무관한 변경을 손으로 걷어낸 최소화, 수정 전 실패·수정 후 통과하는 트리거 테스트(무작위·순서 의존 아님). `<id>b`/`<id>f` 버전 쌍 |
| Christakis & Bird, "What developers want and need from program analysis", ASE 2016 (Microsoft Research PDF) | https://www.microsoft.com/en-us/research/wp-content/uploads/2016/07/What-Developers-Want-and-Need-from-Program-Analysis-An-Empirical-Study.pdf | 응답 375건(응답률 19 %). 오탐률 허용: 5 %까지 90 %, 15 %까지 47 %, 20 %까지 24 %. "aim for a false positive rate no higher than 15–20%". Coverity도 안정 검사기에 20 % 미만을 목표로 함. 오탐 줄이기 49.3 % 대 더 많이 찾기 50.7 %. 오탐을 쉽게 걸러낼 수 있을 때 받겠다는 응답 55 % |
| Anthropic, "A statistical approach to model evaluations" (Miller 2024 요약) | https://www.anthropic.com/research/statistical-approach-to-model-evals | 권고 5개: 표준오차 보고, 문항이 묶여 있으면 군집 표준오차("over three times as large as naive"), 문항 내 분산 줄이기, 짝지은 차이(paired differences, 문항 점수 상관 0.3–0.7), 검정력 분석 |
| Alt-test 저자 README (Calderon, Reichart & Dror, ACL 2025) | https://github.com/nitaytech/AltTest | 사람 주석자 최소 2명(3명 이상 권장), 50–100개 항목(최소 30), ε: 전문가 0.2 · 숙련자 0.15 · 크라우드 0.1, leave-one-out 비교, 승률(winning rate)과 평균 우위 확률, Benjamini–Yekutieli FDR |
| BIG-bench README | https://github.com/google/BIG-bench | 모든 과제 파일의 canary 문자열: "prevent BIG-bench tasks from leaking into web-scraped training data", 편집 금지 |
| Bowyer et al. 코드 README | https://github.com/sambowyer/no_clt_paper | 논문이 IID, 군집, 짝지은 비교, 독립 모형 비교 설정을 다룬다는 것과 `bayes_evals` 패키지. 주장 자체는 발췌로만 봄 |

### 1.4 검색 발췌로만 본 자료 ([snippet])

벤치마크 설계
- NIST SARD Juliet C/C++ 1.3 (CWE 118개, 테스트 64,099개, good/bad 함수, flow variant): https://samate.nist.gov/SARD/test-suites/112 ; https://zenodo.org/records/4701387
- Papadakis, Shin, Yoo & Bae, "Are mutation scores correlated with real fault detection?", ICSE 2018: https://dl.acm.org/doi/10.1145/3180155.3180183
- Vigo, Brown & Conway, W4A 2013: https://dl.acm.org/doi/10.1145/2461121.2461124 (자매 브리프 `automated-ui-accessibility-testing.md` §2.2에 수치가 이미 있음)
- Law & Hvannberg, "Consolidating usability problems with novice evaluators", NordiCHI 2008: https://dl.acm.org/doi/10.1145/1463160.1463228
- Hornbæk, "Dogmas in the assessment of usability evaluation methods", BIT 29(1) 2010: https://www.tandfonline.com/doi/abs/10.1080/01449290801939400
- Gray & Salzman, "Damaged merchandise?", HCI 13(3) 1998: https://www.tandfonline.com/doi/abs/10.1207/s15327051hci1303_2
- Everingham et al., PASCAL VOC, IJCV 88(2) 2010 (중복 탐지 규칙): https://www.research.ed.ac.uk/en/publications/the-pascal-visual-object-classes-voc-challenge/
- FROC(Chakraborty 계열)와 보행자 탐지의 miss rate 대 FPPI(Dollár 등): https://pubmed.ncbi.nlm.nih.gov/18479482/ ; https://pdollar.github.io/files/papers/DollarCVPR09peds.pdf
- SV-COMP 점수 체계: https://www.sosy-lab.org/research/pub/2025-TACAS.Improvements_in_Software_Verification_and_Witness_Validation_SV-COMP_2025.pdf
- Zhu et al., "Establishing best practices for building rigorous agentic benchmarks" (ABC), NeurIPS 2025 D&B: https://arxiv.org/abs/2507.02825
- Lijmer et al., "Empirical evidence of design-related bias in studies of diagnostic tests", JAMA 282(11) 1999: https://scholar.google.com/scholar_lookup?doi=10.1001/jama.282.11.1061

지표와 통계
- Bowyer, Aitchison & Ivanova, "Position: Don't use the CLT in LLM evals with fewer than a few hundred datapoints", ICML 2025: https://arxiv.org/abs/2503.01747
- Cameron & Miller, "A practitioner's guide to cluster-robust inference", J. Human Resources 50(2) 2015: https://jhr.uwpress.org/content/50/2/317
- FDA, "Multiple Endpoints in Clinical Trials", Guidance for Industry, 2022: https://www.fda.gov/media/162416/download

판정
- Zheng et al., "Judging LLM-as-a-judge with MT-Bench and Chatbot Arena", NeurIPS 2023 D&B: https://arxiv.org/abs/2306.05685
- Panickssery, Bowman & Feng, "LLM evaluators recognize and favor their own generations", NeurIPS 2024: https://arxiv.org/abs/2404.13076 (Wataoka 등의 perplexity 설명은 같은 검색 발췌)
- Thakur et al., "Judging the judges: evaluating alignment and vulnerabilities in LLMs-as-judges" (GEM 2025): https://arxiv.org/abs/2406.12624
- Szymanski et al., "Limitations of the LLM-as-a-judge approach … in expert knowledge tasks", IUI 2025: https://dl.acm.org/doi/10.1145/3708359.3712091
- Yuan et al., "Silencer: from discovery to mitigation of self-bias in LLM-as-benchmark-generator", NeurIPS 2025: https://mlanthology.org/neurips/2025/yuan2025neurips-silencer/ ; Xu et al., "When LLMs benchmark themselves": https://arxiv.org/abs/2509.26600
- Hayes & Krippendorff 2007, "Answering the call for a standard reliability measure for coding data" (α 기준값): https://www.k-alpha.org/methodological-notes

과적합과 오염
- Dwork et al., "The reusable holdout", Science 349(6248) 2015: https://www.science.org/doi/10.1126/science.aaa9375
- Recht, Roelofs, Schmidt & Shankar, "Do ImageNet classifiers generalize to ImageNet?", ICML 2019: https://proceedings.mlr.press/v97/recht19a.html
- Kapoor et al., "AI agents that matter" (2024): https://arxiv.org/abs/2407.01502
- Simmons, Nelson & Simonsohn, "False-positive psychology", Psychological Science 22(11) 2011: https://journals.sagepub.com/doi/10.1177/0956797611417632

오탐 비용
- Johnson, Song, Murphy-Hill & Bowdidge, ICSE 2013: https://research.google/pubs/why-dont-software-developers-use-static-analysis-tools-to-find-bugs/
- Distefano, Fähndrich, Logozzo & O'Hearn, "Scaling static analyses at Facebook", CACM 62(8) 2019: https://cacm.acm.org/research/scaling-static-analyses-at-facebook/
- van der Sijs, Aarts, Vulto & Berg, "Overriding of drug safety alerts in CPOE", JAMIA 13(2) 2006: https://academic.oup.com/jamia/article-abstract/13/2/138/729701

### 1.5 읽은 저장소 맥락 (수정하지 않음)

`skills/remorsearch-ux-qa/references/ergonomics/`의 `workflow.md`, `human-factors-checks.md`, `persona-agent-protocol.md`, `validation-and-limits.md`; `docs/ergonomic-swarm-spec.md` §0–2, §6–7, §12–12.1; `docs/validation/experiments/decisions.md`, `heldout-2-preregistration.md`(수정 1 포함), `ablation-dev-5b6e8fb.json`; `docs/validation/{heldout-mixed-frozen-8c1de02, mobile-commerce-v2, game-desktop-v3}.json`의 실행 목록과 요약; `ergoqa/bench.py`(전체), `ergoqa/swarm.py`(`units`, 교차 확인 부분), `ergoqa/checks.py`(PJ-01 고정 부분), `scripts/ergo_eval.py`(구성, 점수, 가설 판정 부분).

### 1.6 기존 브리프와 겹치는 부분 (반복하지 않음)

- `usability-evaluation-methods.md`: Hartson·Sears의 thoroughness, validity, effectiveness(UEM-04), 평가자 효과(Hertzum & Jacobsen, CUE), 매칭 관대함과 viewport 와일드카드(UEM-10), 3인 이상 심각도 합의(UEM-08), 재기록 신뢰도(UEM-09), 예측 타당도 연구(UEM-17).
- `software-testing-foundations.md`: Tricorder의 "effective false positive < 10 %"와 오탐 장부(STF-02), 변이·경계쌍 스위트(STF-17), Andrews 2005·Just 2014, Wilson 구간과 ±0.05에 약 246개가 필요하다는 계산, McNemar.
- `llm-agents-as-test-users.md`: 판정 패널 설계(LAT-14), Rogan–Gladen 보정(LAT-15), PoLL, AgentRewardBench, Zheng 2023의 정성적 결론.
- `automated-ui-accessibility-testing.md`: Vigo 2013, GOV.UK 감사, Deque 57 %, axe-core 층(AUT-02).
- 이 브리프는 위 내용을 전제로, 평가 설계·통계·판정·과적합·오탐 허용치를 다루고 저장소의 검증 계획을 감사합니다. 겹치는 곳에서는 후보 ID를 인용합니다.

## 2. Key knowledge (핵심 지식)

### 2.1 탐지 도구 벤치마크 설계: 정답, 음성, 매칭, 이중 계산

| 벤치마크 | 정답(ground truth) | 음성(오탐을 세는 곳) | 매칭 단위 | 이중 계산 | 요약 지표 | 태그 |
| --- | --- | --- | --- | --- | --- | --- |
| OWASP Benchmark Java v1.2 | 테스트마다 의도한 CWE 1개가 참 또는 거짓 양성이라고 `expectedresults-1.2.csv`에 적혀 있음. 테스트 2,740개, 범주 11개 | 모든 범주에 거짓 양성 테스트(안전한 변형)가 있음 | 테스트 × CWE | 테스트마다 판정 하나 | 범주별 TPR − FPR(Youden J)과 범주 평균. 대각선은 "random guessing": 전부 보고하면 TPR 100 %, FPR 100 %, 점수 0 | [industry] |
| NIST SARD Juliet C/C++ 1.3 | 합성 테스트 64,099개, CWE 118개 | 같은 테스트 안의 good 함수(결함 없는 짝) | 함수 × CWE, 제어·데이터 흐름 변형(flow variant) | 테스트 안의 bad/good 짝 | 도구별 적중·오탐 | [snippet] |
| Defects4J | 실제 버그 854개(프로젝트 17개). 이슈 연결, 단일 커밋 수정, 최소화, 수정 전 실패·수정 후 통과하는 트리거 테스트 | 수정 버전 `<id>f` | 버그 × 트리거 테스트 | 버그마다 하나 | 연구마다 다름 | [industry] |
| 변이 분석 | 연산자로 만든 변이체 | 동치 변이체 | 변이체 | – | mutation score | Andrews 2005, Just 2014는 STF-17 참고 [snippet]. Papadakis 2018은 테스트 스위트 크기를 통제한 설계만 확인 [snippet] |
| 접근성 도구 벤치마크 (Vigo 2013; GOV.UK 2017–18) | 전문가 평가(Vigo); 일부러 심은 장벽 142개(GOV.UK) | Vigo의 correctness(오탐 반영) | 성공 기준 또는 장벽 | – | coverage, completeness, correctness; 도구별 탐지율 | AUT 브리프 §2.2 참고 [snippet]/[industry] |
| 사용성 평가법 비교 (Hartson 등; Gray & Salzman; Hornbæk) | 여러 방법이 찾은 문제의 합집합, 또는 사용자 시험 | 사용자 시험에서 확인되지 않은 예측 | 분석가가 맞춘 "문제" | 통합(consolidation) 단계에서 중복 제거 | thoroughness, validity, effectiveness | UEM 브리프 참고 |
| PASCAL VOC 물체 탐지 | 사람이 그린 상자 | 배경 | IoU ≥ 0.5 | 한 정답에 탐지 하나만 인정, 나머지 중복은 오탐 | AP | [snippet] |
| 의료 영상 CAD의 FROC; 보행자 탐지 | 병변 위치; 보행자 상자 | 병변 없는 영상; 영상당 오탐 | 허용 거리 안의 표시 | 병변당 하나 | LLF 대 영상당 NLF 곡선; 영상당 오탐(FPPI) 10⁻²–10⁰ 구간의 log-average miss rate | [snippet] |
| SV-COMP | 검증 과제의 기대 판정 | 오류 없는 프로그램 | 과제 | 과제마다 하나 | 비대칭 점수: 맞는 TRUE +2, 맞는 FALSE +1, 틀린 FALSE −16, 틀린 TRUE −32, UNKNOWN 0 | [snippet] |
| 에이전트 벤치마크 점검표 ABC | 과제 타당도(task validity)와 결과 타당도(outcome validity) | – | – | – | 결함이 성능을 상대적으로 최대 100 % 과대·과소 추정. SWE-Lancer는 과제를 하나도 풀지 않고 100 %를 받을 수 있었고, KernelBench는 절대 31 %p 과대 추정 | [snippet] |

**이 스킬에 옮길 교훈.**

1. **음성은 범주마다 설계해 넣습니다.** OWASP는 1.1부터 "both true positives and false positives in every vulnerability area"를 넣었고 [industry], Juliet은 같은 테스트 안에 결함 없는 good 짝을 둡니다 [snippet]. 이 스킬도 clean control과 decoy를 갖고 있습니다(KEEP). 그러나 `bench.py`는 두 가지를 하지 않습니다 [derived]:
   - 결함 요소와 **그 요소의 clean 짝**을 짝지어 보지 않습니다. 결함 변형에서 잡힌 요소가 clean 변형에서도 같은 범주로 잡히면, 그 탐지는 심은 결함 때문이 아닐 수 있습니다.
   - 범주별 음성 분모가 없습니다. decoy는 `decoys_flagged` 개수로만, clean control은 시나리오당 단위 수로만 나옵니다. 그래서 범주별 FPR을 계산할 수 없습니다.
2. **전부 보고하는 탐지기는 0점이어야 합니다.** OWASP 점수는 그렇게 설계되었습니다 [industry]. `recall_strict`는 모든 요소를 모든 범주로 모든 프로필에 대해 보고하는 탐지기에게 최고 점수를 줍니다. 벌점은 따로 떨어진 잡음 지표에만 있습니다 [derived]. ABC가 권하는 "아무것도 하지 않는 에이전트" 점검처럼 **자명한 기준 탐지기**를 돌려 본 적이 없습니다(EVD-01).
3. **실제 결함은 수정 전후 쌍으로 옵니다.** Defects4J의 음성은 저자가 새로 쓴 페이지가 아니라 최소화된 실제 수정 버전입니다 [industry]. 이 스킬의 clean control은 저자가 쓴 "결함을 고친 같은 흐름"이라서, 결함 말고 다른 차이가 섞일 수 있습니다 [opinion].
4. **심은 결함의 재현율은 실제 결함의 재현율이 아닙니다.** 손으로 심은 결함은 실제 결함보다 찾기 어렵고(Andrews 2005), 실제 결함의 73 %가 변이체와 결합됩니다(Just 2014) [snippet, STF 브리프 경유]. Papadakis 2018은 테스트 스위트 크기라는 교란 변수를 통제하고 다시 봤습니다 [snippet]. 그 결과 상관이 약했다는 것은 기억이며 확인하지 못했습니다.
5. **중복 탐지를 어떻게 셀지 정해야 합니다.** PASCAL VOC는 한 정답에 탐지 하나만 인정하고 나머지를 오탐으로 셉니다 [snippet]. `bench.py`는 한 결함에 걸린 여러 발견을 모두 "matched"로 넣고, 컨테이너 선택자 규칙이나 페이지 단위 발견 때문에 한 발견이 여러 결함을 채점할 수 있습니다 [derived: `bench.py` L32–33, L99–100].
6. **이 벤치마크는 free-response 위치 탐지 과제입니다.** 한 페이지에 결함이 여럿이고, 위치(선택자)를 맞혀야 하며, 결함 없는 페이지가 있습니다. 의료 영상의 FROC(병변 위치 비율 대 영상당 오탐)와 보행자 탐지의 miss rate 대 FPPI가 같은 구조입니다 [snippet]. 음성 요소를 열거할 수 없으므로 ROC와 특이도는 정의가 불안정하고, "clean 시나리오당 오탐 단위 수"가 맞는 x축입니다 [opinion].
7. **비용 비대칭은 미리 선언합니다.** SV-COMP는 틀린 답에 맞는 답의 16–32배 벌점을 줍니다 [snippet]. 이 스킬의 H4 임계값(clean 시나리오당 P0–P1 ≤ 1, P0–P2 ≤ 5)은 암묵적인 비용 비율인데, 근거가 적혀 있지 않습니다 [derived].
8. **사례-대조 설계는 정확도를 부풀립니다.** 진단 검사 연구에서 사례-대조(case-control) 설계는 진단 오즈비를 약 3배로 과대 추정했습니다(Lijmer 1999) [snippet]. "뚜렷하게 심은 결함 + 깨끗한 대조"는 사례-대조 설계이고, 실제 제품에서 돌리는 것은 코호트 설계입니다. 합성 스위트의 재현율과 정밀도는 실제 제품보다 좋게 나올 것으로 예상해야 합니다 [opinion].
9. **평가법 비교 연구의 교훈.** 작은 설계 결함이 결론을 뒤집습니다(Gray & Salzman 1998) [snippet]. 문제 개수 세기와 매칭은 "dogma"이고, 짧은 문제 기술은 맞추기 어렵습니다(Hornbæk 2010) [snippet]. 통합(consolidation)은 중복 제거와 목록 병합의 두 단계이며, 협업 병합은 중복을 줄였지만 **심각도 평가를 크게 올렸습니다**(Law & Hvannberg 2008) [snippet]. 이 스킬의 문제 단위(`swarm.units`)도 통합 단계이고, 단위 심각도는 구성원 중 가장 나쁜 값입니다 [derived: `swarm.py` L176].

### 2.2 지표: 신뢰구간, 짝 비교, 운영점, 비용, 범주, 단위

**2.2.1 단일 비율의 구간.**

- 수백 개 미만의 데이터에서는 CLT 기반 구간이 목표 신뢰수준을 지키지 못하고, 군집 CLT도 마찬가지입니다. Wilson 구간과 베이즈 신용구간은 작은 n에서도 포함 확률을 지킵니다(Bowyer et al. 2025) [snippet]. `bench.wilson`을 쓰는 현재 방식은 이 권고와 맞습니다(KEEP).
- 문항이 묶여 있으면 군집 표준오차를 써야 하고, 유명한 평가에서 군집 표준오차는 순진한 표준오차의 3배를 넘을 수 있습니다. 두 모형을 같은 문항에서 비교할 때는 짝지은 차이를 씁니다(Miller 2024) [industry].
- 군집 수가 적으면 군집 강건 표준오차가 너무 작아집니다(Cameron & Miller 2015) [snippet]. heldout-2가 제품 4개 안팎이라면 제품 단위 군집 구간은 확증용으로 쓸 수 없습니다 [derived].

[derived] Wilson 95 % 구간(독립 가정):

| n | 재현율 0.6 | 0.7 | 0.8 |
| --- | --- | --- | --- |
| 20 | 0.39–0.78 (±0.20) | 0.48–0.86 (±0.19) | 0.58–0.92 (±0.17) |
| 40 | 0.45–0.74 (±0.15) | 0.55–0.82 (±0.14) | 0.65–0.90 (±0.12) |
| 45 | 0.46–0.73 (±0.14) | 0.54–0.81 (±0.13) | 0.66–0.89 (±0.12) |
| 50 | 0.46–0.72 (±0.13) | 0.56–0.81 (±0.12) | 0.67–0.89 (±0.11) |

[derived] 반폭(half-width)을 맞추는 데 필요한 결함 수:

| 목표 반폭 | 재현율 0.6 | 0.7 | 0.8 |
| --- | --- | --- | --- |
| ±0.15 | 38 | 33 | 26 |
| ±0.10 | 89 | 78 | 60 |
| ±0.075 | 161 | 141 | 107 |
| ±0.05 | 366 | 320 | 245 |

- 40–50개 결함으로는 재현율을 ±0.11–0.15로만 압니다. ±0.05는 245–366개가 필요합니다 [derived]. STF 브리프의 "p = 0.8에서 ±0.05에 약 246개"와 같은 결론입니다.
- **군집 효과.** 결함은 제품과 저자, 페이지로 묶입니다. 설계 효과는 DEFF = 1 + (m − 1)·ICC입니다(m = 군집당 결함 수). 결함 45개, 제품 4개(m ≈ 11)에서 [derived]:

  | ICC | DEFF | 유효 n | p = 0.7의 대략적 반폭 |
  | --- | --- | --- | --- |
  | 0.05 | 1.5 | 30 | ±0.17 |
  | 0.10 | 2.0 | 22 | ±0.19 |
  | 0.20 | 3.1 | 15 | ±0.23 |
  | 0.30 | 4.1 | 11 | ±0.27 |

- **이 저장소의 스위트 간 변동은 큽니다.** 스위트를 처음 채점했을 때(first look) swarm 재현율은 mobile-commerce v1 0.82(17개), game-desktop v1 0.31(16개), heldout-mixed 0.60(20개)이었습니다(`validation-and-limits.md`). 이 셋만으로 거칠게 계산하면 스위트 간 표준편차 τ ≈ 0.23이고, 새 스위트 하나의 95 % 예측구간은 사실상 0.1–1.0입니다 [derived]. 이 사이에 탐지기 버전도 바뀌었으므로 τ에는 스위트 차이와 버전 차이가 섞여 있습니다. 그래도 "한 스위트의 Wilson 구간"은 "다음 제품에서의 재현율"에 대한 불확실성을 크게 과소평가합니다.

**2.2.2 짝 비교.**

- 같은 결함에서 두 구성을 비교할 때는 불일치 쌍만 정보를 줍니다. [derived] 정확 McNemar 양측 p: 9 대 0 → 0.0039, 6 대 0 → 0.031, 5 대 0 → 0.0625, 8 대 1 → 0.039, 6 대 1 → 0.125, 8 대 2 → 0.109.
- `ergo_eval._paired_diff`는 결함을 다시 뽑는 percentile 부트스트랩입니다. 불일치 쌍이 0이면 구간이 [0, 0]으로 폭이 없고, 불일치 쌍이 몇 개뿐이면 포함 확률이 불안정합니다 [derived: 코드와 모의실험]. 정확 조건부 방법(McNemar 기반)이나 짝 비율 차이의 score 구간(Newcombe 1998의 방법. 이번 세션에서 원문 확인 못 함)이 표준적인 대안입니다.

**2.2.3 운영점.**

- `recall_strict_by_operating_point`(P0–P1, P0–P2, 전체)와 `clean_control_units_by_severity`는 이미 있습니다. 둘을 같은 심각도 문턱에서 짝지으면 FROC 점이 됩니다. 문턱 4개(P0, ≤ P1, ≤ P2, ≤ P3)마다 (재현율, clean 시나리오당 오탐 단위)를 한 표로 보고하면, 보고서 기본 운영점을 근거 있게 고를 수 있습니다 [derived, opinion].
- 보행자 탐지처럼 "clean 시나리오당 오탐 1개에서의 miss rate"를 한 숫자 요약으로 쓸 수 있습니다 [snippet: Dollár 방식의 유추].

**2.2.4 비용과 유병률.**

- 정밀도(또는 실효 오탐 비율)는 결함 밀도에 달려 있습니다. 시나리오당 오탐 단위 f, 재현율 r, 시나리오당 실제 결함 d일 때 실효 오탐 비율은 f / (f + r·d)입니다 [derived]. r = 0.7에서:

  | f (시나리오당 오탐 단위) | d = 0.5 | d = 1 | d = 2 | d = 5.3 (개발 스위트 밀도) |
  | --- | --- | --- | --- | --- |
  | 0.17 | 33 % | 20 % | 11 % | 4 % |
  | 0.35 | 50 % | 33 % | 20 % | 9 % |
  | 0.7 (현재 개발 스위트 P0–P2) | 67 % | 50 % | 33 % | 16 % |
  | 2.7 (현재 개발 스위트 전체) | 89 % | 79 % | 66 % | 42 % |
  | 5.0 (H4 P0–P2 상한) | 93 % | 88 % | 78 % | 57 % |

- 개발 스위트는 결함 시나리오 약 10개에 결함 53개, 즉 시나리오당 약 5.3개를 심었습니다 [derived: 실행 목록]. 실제 제품의 흐름당 문제 수는 이보다 훨씬 적을 것이므로, **같은 오탐 밀도라도 실제 제품에서는 실효 오탐 비율이 훨씬 높습니다.** 시나리오당 오탐 밀도 f가 제품 사이에서 옮겨지는 양이고, 벤치마크 정밀도는 옮겨지지 않습니다 [derived].
- OWASP의 Youden J와 SV-COMP의 비대칭 점수는 "비용을 미리 선언한 지표"의 예입니다 [industry]/[snippet].

**2.2.5 범주별 보고.**

- OWASP는 범주별 점수를 평균해 범주마다 같은 가중치를 줍니다. 표본이 작은 범주의 결정이 더 큰 비중을 얻으므로 논쟁적이라는 지적이 있습니다 [snippet].
- [derived] 범주당 결함이 3–8개면 Wilson 반폭이 ±0.25–0.35입니다. 범주별 합격·불합격은 불가능하고 k/n만 보고해야 합니다. 범주·`detectable_by`·`audience_relevance`별 분해는 사전등록대로 기술 통계로 두는 것이 맞습니다.

**2.2.6 심각도.** 양측 심각도 지표와 3인 이상 합의는 UEM-04, UEM-08, STF-05가 다뤘습니다. 여기서는 한 가지만 더합니다. 단위 심각도가 구성원 중 최악값이고 통합이 심각도를 올린다는 보고(Law & Hvannberg 2008) [snippet]가 있으므로, 단위를 더 크게 묶을수록 심각도 분포가 위로 밀립니다 [derived].

**2.2.7 문제 단위와 매칭.**

- 단위 키는 (시나리오, 검사, 차등 조건)입니다 [derived: `swarm.py` L173]. 예를 들어 PT-02 단위 하나에 표적 5개가 들어 있고 그중 하나만 심은 결함이면, 그 단위는 통째로 "matched"가 되고 나머지 4개는 유효한 단위 안에 숨습니다. `validity_lb_units`는 묶음이 굵을수록 올라가고, clean control의 단위 수는 내려갑니다. 단위의 굵기가 지표를 움직이는 **Goodhart 경로**입니다 [derived]. 사례 단위(instance) 지표를 함께 보고하면 막을 수 있습니다(EVD-11).
- 매칭 규칙: id 접두사("#opt-"), 컨테이너(`context_selectors`), 접미사(`endswith`), 공백·">" 분할이 모두 관대한 쪽입니다 [derived: `bench.py` L22–44]. 매칭 관대함은 UEM-10이 다뤘고, 여기서는 "우연 수준"을 재는 방법을 더합니다(EVD-01).

### 2.3 사람·LLM 판정

**2.3.1 일치도 지표.**

- Krippendorff α: 보통 α ≥ .800을 요구하고, 잠정 결론이 허용될 때 α ≥ .667이 생각할 수 있는 최저선입니다(Hayes & Krippendorff 2007) [snippet].
- LLM 판정자 평가에서 퍼센트 일치는 판정자를 잘 구분하지 못했고 Cohen κ가 더 잘 구분했습니다. 퍼센트 일치로는 30점 차이였던 것이 κ로는 53점 차이였고, κ로 "excellent"에 든 것은 GPT-4 Turbo(0.84)와 Llama-3 70B(0.79)뿐이었습니다(Thakur et al.) [snippet].
- [derived] 1차 판정(`adjudication-round1.json` 요약값: 68개, 둘 다 invalid 52, 둘 다 valid 10, 불일치 6): 일치 0.912, κ 0.715, **부트스트랩 95 % 구간 0.45–0.91**. κ 0.72라는 점추정은 "substantial"로 보이지만 구간은 "moderate"부터 "almost perfect"까지 걸칩니다(Landis & Koch의 흔히 쓰는 구간 이름. 이번에 원문 확인 안 함).
- [derived] 같은 자료의 타당 비율: valid만 세면 10/68 = 0.147(Wilson 0.08–0.25), 불일치를 절반으로 세면 13/68 = 0.19(0.12–0.30), 불일치를 모두 valid로 세면 16/68 = 0.235(0.15–0.35).

**2.3.2 판정자와 사람 기준 수.**

- Alt-test는 LLM이 사람 주석자를 대신해도 되는지 통계적으로 판정합니다. 사람을 한 명씩 빼고(leave-one-out) 나머지 사람과의 일치를 LLM과 뺀 사람 사이에서 비교합니다. 사람 최소 2명(3명 이상 권장), 항목 50–100개(최소 30), ε는 전문가 0.2·숙련자 0.15·크라우드 0.1, 여러 데이터셋이면 Benjamini–Yekutieli FDR 통제를 씁니다 [paper, 저자 README].
- 심각도 평가는 3–4명이 실용적이라는 Nielsen 1992 결과는 UEM-08, 서로 다른 계열 3개 모델 패널(PoLL)은 LAT-14에 있습니다.
- 동일 계열 판정자 2명의 κ는 **일관성**을 재고 **타당성**을 재지 않습니다. 두 판정자의 오류가 상관되어 있으면 κ는 높고 정확도는 낮을 수 있습니다 [opinion].

**2.3.3 LLM 판정자의 편향.**

- GPT-4 판정자는 사람 선호와 80 % 넘게 일치해 사람끼리의 일치와 비슷했지만, 위치·장황함·자기 강화(self-enhancement) 편향을 보였습니다(Zheng et al. 2023) [snippet]. 판정자별 위치 일관성 수치는 원문을 열지 못해 쓰지 않습니다.
- 자기 선호의 강도는 자기 인식 능력과 선형으로 상관했고, GPT-4와 Llama 2는 기본 상태에서도 자기 출력을 상당히 구별했습니다(Panickssery et al. 2024) [snippet]. LLM 판정자는 perplexity가 낮은 출력을 선호한다는 설명도 있습니다(Wataoka 등) [snippet].
- 전문 지식 과제에서 전문가(SME)와 LLM 판정자의 일치는 영양학 68 %, 정신건강 64 %였습니다(Szymanski et al., IUI 2025) [snippet]. 접근성·인간공학 판정은 전문 지식 과제에 가깝습니다 [opinion].
- **LLM이 만든 벤치마크의 자기 편향.** 모델이 자기가 만든 벤치마크에서 비현실적으로 잘하는 현상이 있고, 원인은 질문 영역, 언어 스타일, 그리고 가장 큰 요인인 **자기가 반복하는 틀린 정답 라벨**입니다. 여러 모델 앙상블로 사람 벤치마크 순위와의 Pearson 상관이 평균 0.655에서 0.833으로 올랐습니다(Silencer, Yuan et al. 2025). 번역 벤치마크에서는 자기 편향 때문에 모델마다 자기를 1위에 놓았습니다(Xu et al. 2025) [snippet].
- **이 저장소에 주는 뜻** [derived, opinion]: heldout-2의 저자, 탐지기 작성자, Stage-0 조사자, 판정자가 모두 Claude입니다. 자기 편향은 두 경로로 들어옵니다. (1) 답안 키: 같은 모델 계열이 같은 온톨로지로 결함과 검사를 썼으므로, 키의 틀린 라벨이 탐지기와 같은 방향으로 틀릴 수 있습니다. (2) 판정: 규칙 문구와 발견 요약도 Claude가 썼습니다. 사용자의 "Claude만" 규칙 아래에서는 계열 다양성을 얻을 수 없으므로, **사람 기준 집합**(EVD-09)과 **키 감사**(EVD-07)가 유일한 외부 기준입니다.

**2.3.4 눈가림.** 진단 정확도 연구의 원칙대로 참조 표준 판정자는 지표 검사 결과를 모르고, 지표 검사 판독자는 참조 표준을 몰라야 합니다 [opinion; STARD 원문 미확인]. 이 저장소의 현황 [derived]:

| 누가 | 무엇을 몰라야 하나 | 현재 | 빈틈 |
| --- | --- | --- | --- |
| 벤치마크 저자 | 탐지기 코드 | 지킴(spec §12) | 저작 프롬프트가 규칙 집합 예시를 담음(수정 1이 인정) |
| 도구 작성자 | 키, 페이지, 시나리오, 결함별 결과 | 지킴(봉인) | 과거 스위트에서 저자 요약을 통한 누출 기록 있음 |
| Stage-0 조사자 | 키 | 지킴 | **키의 `audience_relevance`와 같은 brief를 읽음**(순환성, EVD-06) |
| 판정자 | 키, 출처 구성, 변형(결함/clean), 심각도 | 키만 가림 | 변형·구성·검사 이름·심각도가 드러날 수 있음(EVD-08) |

**2.3.5 판정 표본 크기** [derived].

- 판정 60개로 전체 타당 비율은 ±0.10–0.12로 추정됩니다. 검사 가족 8개에 나누면 가족당 7–8개라서 ±0.26–0.29입니다. 가족별 결정에는 부족합니다.
- 타당 비율 0.5와 0.17을 단측 α = 0.05, 검정력 0.8로 가르려면 검사당 13개가 필요합니다(3개 이하 타당이면 기각). 0.5와 0.25는 23개, 0.5와 0.30은 37개입니다.
- `decisions.md`의 "판정 타당도 ≤ 1/6"(n = 6) 규칙: Wilson 구간 0.03–0.56입니다. 평평한 사전분포에서 P(타당도 < 0.5) = 0.94이므로 **되돌릴 수 있는 강등**의 방아쇠로는 쓸 만합니다. 그러나 타당도 수준이 낮다는 주장이나 KEEP 결정의 근거는 못 됩니다. 6개가 같은 스위트·같은 페이지에서 나와 독립도 아닙니다.

### 2.4 벤치마크 과적합, 오염, 사전등록, 다중 비교

**2.4.1 홀드아웃 재사용과 새 테스트 세트.**

- 데이터 분석은 본래 적응적입니다. 앞선 분석 결과를 보고 다음 분석을 고르면, 고정된 절차를 가정한 타당성 보장이 깨집니다. Dwork 등은 차등 프라이버시로 홀드아웃을 여러 번 안전하게 쓰는 Thresholdout을 제안했습니다(Science 2015) [snippet]. 이 저장소는 "한 번 채점하면 개발 스위트가 된다"는 더 단순하고 보수적인 규칙을 씁니다(KEEP).
- 원래 절차를 따라 새로 만든 테스트 세트에서 정확도가 CIFAR-10은 3–15 %, ImageNet은 11–14 % 떨어졌습니다. 원인은 적응적 과적합이 아니라 조금 더 "어려운" 이미지에 일반화하지 못한 것이었고, 원래 세트에서의 향상은 새 세트에서 더 큰 향상으로 이어졌습니다(Recht et al. 2019) [snippet].
  - 이 저장소에 적용하면 [opinion]: 개발 0.906 대 첫 채점 held-out 0.60의 차이는 대부분 "새 저자, 새 제품"이라는 분포 이동일 가능성이 있습니다. 그렇다면 held-out의 절대 재현율보다 **구성 사이 순위**(C4 ≥ C3 > C2 > C1)가 재현되는지가 더 믿을 만한 신호입니다.
- 에이전트 평가가 정확도만 보고 비용 같은 다른 지표를 보지 않으면, 에이전트가 불필요하게 복잡하고 비싸지며 정확도 향상의 원인을 잘못 짚게 됩니다(Kapoor et al. 2024) [snippet]. 같은 논문이 "많은 에이전트 벤치마크에 적절한 홀드아웃이 없다"고 지적했다는 것은 기억이며, 이번 발췌에서는 확인하지 못했습니다. ABC는 과제·결과 타당도 결함이 성능을 상대적으로 최대 100 % 틀리게 만든다고 보고했습니다 [snippet].

**2.4.2 오염과 봉인.**

- BIG-bench는 모든 과제 파일에 편집 금지 canary 문자열을 넣어, 웹에서 긁은 학습 데이터에 벤치마크가 섞였는지 검출할 수 있게 했습니다 [industry].
- 이 저장소의 오염 경로 [derived]:
  1. 도구 작성자(같은 세션)가 키를 여는 것. 규율과 봉인으로 막고 있습니다.
  2. 저장소 전체 검색(`rg`, Grep 도구)이 키 내용을 출력하는 사고. 지금은 규율 말고는 막는 장치가 없습니다.
  3. 벤치마크 저자의 완료 보고가 결함을 설명하는 것. 과거 스위트에서 실제로 있었습니다(`validation-and-limits.md`).
  4. 공개 저장소에 올린 held-out이 미래 모델의 학습 데이터에 들어가는 것. 다음 세대 Claude가 에이전트나 판정자로 쓰일 때 문제가 됩니다.

**2.4.3 연구자 자유도와 사전등록.**

- 데이터 수집·분석·보고의 유연성은 명목상 5 %인 위양성률을 크게 올립니다. 해결책으로 저자 요건 6개와 심사자 지침 4개를 제안했습니다(Simmons, Nelson & Simonsohn 2011) [snippet]. 모의실험에서 여러 유연성을 합쳤을 때 약 61 %였다는 수치는 기억이며 확인하지 못했습니다.
- 이 저장소의 사례 [derived]: heldout-mixed는 탐지기 동결(`8c1de02`) 뒤, 채점 전에 id 접두사 매칭 규칙이 채점기에 들어가 0.60이 0.80이 되었습니다. 두 결과를 모두 보고한 것은 맞는 대응입니다(KEEP). heldout-2는 채점기까지 동결합니다(KEEP).
- **Goodhart** [opinion]: 지표가 목표가 되면 좋은 지표가 아니게 됩니다. 이 저장소에서 지표를 움직이는 경로는 셋입니다. (1) 관대한 매칭(2.2.7), (2) 단위 굵기(2.2.7), (3) 개발 스위트 결함을 보고 검사를 추가·재분류한 것(`validation-and-limits.md` Disclosures). 셋 모두 held-out에서 순위가 재현되는지와 자명한 기준선 대비 차이로 점검해야 합니다.

**2.4.4 다중 비교.**

- FDA의 다중 평가변수 지침(2022)은 Bonferroni, Holm, Hochberg, 사전 α 배분, 고정 순서(fixed-sequence), 재표집 기반 절차, gatekeeping, 그래프 방식을 다룹니다. 고정 순서법은 앞 가설이 기각될 때만 다음 가설을 같은 α로 검정합니다 [snippet].
- heldout-2 사전등록에는 판정이 약 10개 있습니다(H2 두 부분, H3, H4 두 부분, H5 두 구성, H6, H7). 판정마다 95 % 구간(단측 0.025)을 쓰고 가족 단위 통제는 없습니다 [derived]. 모든 귀무가설이 참이고 서로 독립이라면 10개 중 하나 이상이 우연히 "pass"할 확률은 1 − 0.975¹⁰ ≈ 22 %입니다 [derived]. 판정 사이에 상관이 있어 실제로는 이보다 낮지만, 유용성 주장이 "어느 하나라도 통과"에 기대면 과장됩니다.

**2.4.5 사전등록 판정 규칙의 작동 특성** [derived: `scripts/ergo_eval.py`의 `_paired_diff`(2,000회 percentile 부트스트랩, 결함 재표집)와 `_verdict`를 그대로 흉내 낸 모의실험].

- **H5**(조건 식별 ≥ 0.5, Wilson 하한이 0.5 이상이어야 pass): 조건부 결함 20개면 15개 이상(0.75), 15개면 12개 이상(0.80), 10개면 9개 이상이 필요합니다.
- **H6**(에이전트 재현율 ≥ 0.30): `agent_judgment` 결함 10개면 6개 이상(0.60), 8개면 5개 이상이 필요합니다.
- **H2 1부**(primary 결함에서 C4@10 − C5@10 평균 ≥ 0.10, 구간 하한이 0.10 이상): 결함 모형은 "모든 시드가 찾음 35 %, 아무도 못 찾음 15 %, 나머지는 부분적"으로 두었습니다.

  | primary 결함 수 | 실제 효과 0 | +0.10 | +0.17 | +0.22 |
  | --- | --- | --- | --- | --- |
  | 10 | pass 0 %, fail 27 % | pass 4 % | pass 12 % | pass 28 % |
  | 15 | pass 0 %, fail 30 % | pass 4 % | pass 20 % | pass 35 % |
  | 20 | pass 0 %, fail 33 % | pass 2 % | pass 23 % | pass 45 % |
  | 25 | pass 0 %, fail 38 % | pass 2 % | pass 26 % | pass 56 % |

  - 효과가 정확히 문턱(+0.10)이면 pass 확률은 2–4 %이고, 효과가 없을 때도 fail은 27–38 %뿐입니다. 결과는 대부분 "inconclusive"가 됩니다.
  - 같은 모형에서 규칙을 "구간 하한 > 0"(우월성)으로 바꾸면 primary 20개에서 pass 확률은 효과 0일 때 3 %, +0.10일 때 38 %, +0.17일 때 81 %입니다.
- **H3**(C4@14 − C3 ≥ −0.05, 결함 45개): 불일치가 없으면 부트스트랩 구간이 [0, 0]이라 항상 pass합니다. 양쪽으로 2 %씩 엇갈리면 pass 47 %, 5 %씩이면 29 %, C3만 5 % 더 찾으면 13 %입니다. 결국 H3는 "C4가 C3가 찾은 것을 사실상 하나도 놓치지 않는다"는 조건이 됩니다. 한계를 −0.10으로 넓히면 같은 경우의 pass 확률은 85 %, 55 %, 31 %입니다.
- **H4**(clean 시나리오당 P0–P1 ≤ 1, P0–P2 ≤ 5): 현재 개발 스위트는 약 10개 clean 시나리오에서 P0–P1 단위 0개, P2 단위 7개입니다(`decisions.md` exp4). 시나리오당 0.7(Poisson 95 % 구간 0.28–1.44)이라서 **지금의 H4는 떨어질 수가 없습니다.** 구간도 쓰지 않습니다.
- **H7**(C3 − C2, 조건 없는 결함에서 ≥ 0): 불일치가 없으면 [0, 0]으로 pass, C3가 하나라도 놓치면 대개 inconclusive입니다. 정상성 점검으로는 괜찮지만 구간 방법은 바꿔야 합니다(EVD-04).

### 2.5 오탐 비용과 경보 피로

- **Google Tricorder**: 새 검사는 실효 오탐(effective false positive, 개발자가 보고도 긍정적 조치를 하지 않은 경우) 10 % 미만을 요구하고, 전체는 5 %에 조금 못 미칩니다. 이미 STF-02에 있습니다 [industry, STF 브리프 경유].
- **Microsoft 개발자 조사(Christakis & Bird 2016)** [paper]:
  - 응답 375건. 받아들일 수 있는 최대 오탐률은 5 %까지가 90 %, 15 %까지가 47 %, 20 %까지가 24 %였습니다.
  - 저자들의 권고는 "no higher than 15–20%"이고, Coverity도 안정 검사기에 20 % 미만을 목표로 합니다.
  - 개발자는 놓침보다 오탐을 훨씬 더 신경 씁니다. 다만 "오탐을 줄이려면 실제 문제를 조금 놓쳐도 된다" 49.3 % 대 "더 찾는 것이 오탐 비용보다 낫다" 50.7 %로 갈렸습니다.
  - 오탐을 쉽게 걸러낼 수 있을 때 받겠다는 응답이 55 %였습니다(다른 선택지는 중요한 코드를 분석할 때).
- **Johnson et al. 2013**: 개발자 20명 인터뷰. 모두 정적 분석이 유익하다고 봤지만, 오탐과 경고 제시 방식이 사용을 막았습니다 [snippet].
- **Facebook Infer (Distefano et al. 2019)**: 일괄(batch) 배포에서는 개발자에게 배정한 20–30건에 거의 아무도 반응하지 않았습니다. 코드 리뷰 시점(diff time)에 보여 주자 수정률이 70 %를 넘었습니다. 오탐률은 20 % 미만으로 봤습니다 [snippet]. **같은 정확도라도 전달 시점과 문맥이 조치율을 바꿉니다.**
- **의료 경보 피로**: CPOE의 약물 안전 경보는 49–96 %가 무시되었고, 낮은 특이도와 불필요한 업무 방해가 오류 유발 조건으로 꼽혔습니다(van der Sijs et al. 2006, 논문 17편 검토) [snippet].
- **이 스킬의 clean control 잡음에 주는 뜻** [derived, opinion]:
  - 2.2.4 표에서 재현율 0.7일 때 실효 오탐 20 % 이하를 지키려면, clean 시나리오당 P0–P2 오탐 단위가 실제 결함 밀도 d = 1이면 0.17 이하, d = 2이면 0.35 이하여야 합니다. 10 % 이하라면 각각 0.08, 0.16입니다.
  - 현재 개발 스위트의 P0–P2는 0.7로, d = 1–2에서 실효 오탐 33–50 %에 해당합니다. H4 상한 5는 78–88 %에 해당합니다.
  - UX 감사 보고서의 독자(디자이너, PM)가 코드 리뷰 봇의 독자보다 오탐을 더 참을 수는 있습니다. 하지만 20–30 %를 넘는 허용치를 뒷받침하는 문헌 수치는 찾지 못했습니다.
  - P0–P1은 "반드시 고쳐야 한다"는 주장이므로 Tricorder 수준(10 % 미만)을 적용하고, 벤치마크 clean 시나리오에서는 0이어야 합니다.
  - Infer 사례에 비추면 보고서 형식(단위 묶음, 수정 제안, 재현 단계)과 전달 시점도 잡음만큼 중요합니다. 이는 STF-02의 `disposition` 장부로 측정합니다.

### 2.6 이 저장소의 검증 계획 감사

`heldout-2-preregistration.md`(수정 1 포함), `decisions.md`, `ergoqa/bench.py`, `scripts/ergo_eval.py`를 2.1–2.5의 기준으로 점검했습니다. "대응"은 3절의 후보 ID입니다.

| # | 항목 | 현재 | 문헌 기준의 문제 | 근거 | 대응 |
| --- | --- | --- | --- | --- | --- |
| A1 | 기준 탐지기 | 없음 | 전부 보고하는 탐지기가 `recall_strict` 최고점을 받음. 매칭 규칙의 우연 수준을 모름 | OWASP 대각선 [industry]; ABC [snippet]; 2.2.7 | EVD-01 |
| A2 | clean 짝과의 대조 | 결함별로는 없음 | 결함이 아니라 요소 자체 때문에 잡혔을 수 있음. 범주별 FPR 없음 | Juliet good/bad [snippet]; OWASP [industry]; LAT-04 | EVD-02 |
| A3 | 가설 가족 | 판정 약 10개, 통제 없음, 최소 검출 효과(MDE) 미기재 | H2는 문턱 효과에서 pass 2–4 %, H3·H7은 부트스트랩 퇴화, H4는 떨어질 수 없음, H5·H6은 요구치가 명목값보다 훨씬 높음 | 2.4.4, 2.4.5 [derived]; FDA [snippet] | EVD-03 |
| A4 | 구간 | 독립 Wilson, 결함 재표집 부트스트랩 | 제품·저자 군집 무시. 스위트 간 τ ≈ 0.23. 불일치 0이면 폭 0 | Miller [industry]; Cameron & Miller, Bowyer [snippet]; 2.2.1 [derived] | EVD-04, EVD-14 |
| A5 | 잡음 관문 H4 | clean 시나리오당 P0–P1 ≤ 1, P0–P2 ≤ 5 | 실효 오탐 78–88 %에 해당. 현재 수준(0.7)에서 떨어질 수 없음. 단위로만 셈 | Christakis & Bird [paper]; Tricorder [industry]; 2.2.4 [derived] | EVD-05, EVD-11 |
| A6 | H2 설계 | 오디언스 파일 하나(한 번의 확률적 추출) 대 무작위 20 시드 평균 | 비교 대상이 약함. 개발 스위트에서 층화가 이미 무작위를 이김(기기당 10개에서 0.906 대 0.827). floor만으로 차이가 날 수 있음. relevance 라벨과 오디언스가 같은 brief에서 나옴 | `ablation-dev-5b6e8fb.json` [derived]; Silencer/Xu [snippet] | EVD-06, EVD-18 |
| A7 | 답안 키 | 제품마다 Claude 저자 1명, 감사 없음 | 틀린 라벨이 자기 편향의 최대 요인. 과제 타당도 점검 없음 | Silencer [snippet]; ABC [snippet]; Defects4J 큐레이션 [industry] | EVD-07 |
| A8 | 2차 판정 | Opus 판정자 2명, 60단위 | 같은 계열 2명의 κ는 일관성만 잼. 불일치(1차 6/68) 해소 규칙 없음. 가족별 n 부족. 사람 기준 없음 | 2.3 [derived]; alt-test [paper]; Szymanski [snippet] | EVD-08, EVD-09 |
| A9 | 외부 기준선 | C1은 "이 도구의 측정 검사"이고 axe·Lighthouse는 안 돌림 | "표준 도구보다 낫다"는 주장을 할 수 없음 | `validation-and-limits.md` [derived]; Vigo, GOV.UK(AUT 브리프) | EVD-10, EVD-18 |
| A10 | 중복·단위 | 한 발견이 여러 결함을 채점할 수 있음. 단위 굵기가 정밀도와 잡음 수를 움직임 | 중복 규칙 없음. Goodhart 경로 | PASCAL VOC [snippet]; 2.2.7 [derived] | EVD-11 |
| A11 | 보관(custody) | 규율과 봉인 | 저장소 전체 검색 사고, 공개 저장소 학습 오염, 열람 횟수 기록 없음 | BIG-bench [industry]; Dwork [snippet] | EVD-12 |
| A12 | `decisions.md` KEEP/CUT 규칙 | n = 6에서 ≤ 1/6, 고유 탐지는 개발 스위트에서만 셈 | 강등에는 쓸 만하나 KEEP이나 수준 주장은 불가. 고유 탐지가 학습 적합(post-hoc) | 2.3.5 [derived] | EVD-13 |
| A13 | 외적 타당도 | 합성 페이지만 | 사례-대조 설계의 스펙트럼 편향. 실제 결함 재현율 미지 | Lijmer [snippet]; Defects4J [industry]; Andrews/Just(STF 경유) | EVD-15 |
| A14 | 보고 | 결과 표와 공개 사항 | 흐름, 기준선, 판정 보정, 열람 횟수, 역할별 모델 계열, 비용이 한 곳에 없음 | Kapoor, ABC, Simmons [snippet] | EVD-16 |
| A15 | 대표 지표 | `precision_labeled`, 한쪽 `severity_agreement`, n이 작은 범주별 값이 요약에 섞임 | 결정에 쓸 수 없는 지표가 헤드라인 옆에 있음 | UEM-04, 2.2.5 [derived] | EVD-17 |

**주의.** 개발 스위트의 clean 시나리오 수(약 10개)는 실행 목록에서 셌습니다. mobile-commerce 4개와 game-desktop 2개는 `-clean` 접미사로 확인했습니다. heldout-mixed는 흐름 4개 × a/b 변형이라 4개로 가정했고, 확인하지 못했습니다.

## 3. Implications for the skill (스킬에 주는 시사점)

### 3.0 요약

- 검출기(checks)보다 **자(ruler)**가 먼저입니다. 지금의 채점기와 판정 규칙으로는 heldout-2가 어떤 결과를 내도 해석이 어렵습니다. 전부 보고하는 탐지기가 최고 재현율을 받고(A1), H2는 효과가 문턱일 때 2–4 %만 통과하며(2.4.5), H4는 떨어질 수 없습니다(A5).
- 가장 값싼 개선 다섯 개는 모두 채점기와 분석 계획의 변경이고, 이미 기록된 실행으로 계산됩니다: 기준 탐지기(EVD-01), clean 짝 판별(EVD-02), 가설 가족 재구성(EVD-03), 군집 구간과 정확 짝 방법(EVD-04), 잡음 관문 교체(EVD-05).
- heldout-2는 아직 동결 전이고 채점 전입니다. 위 다섯 개와 EVD-06(위약 오디언스), EVD-10(axe 기준선)은 **기록 전에** 사전등록 수정 2로 넣어야 합니다. 원래 H1–H7 판정도 그대로 계산해 함께 보고합니다.
- 실효 오탐 기준으로 보면 잡음 목표는 clean 시나리오당 P0–P2 오탐 단위 0.35 이하(실제 결함 밀도 2, 재현율 0.7에서 실효 오탐 20 %)이고, P0–P1은 0입니다. 개발 스위트의 현재 값은 0.7입니다.

### 3.1 후보 표

노력: S ≤ 1일, M ≤ 1주, L > 1주. "수정 2"는 heldout-2 사전등록의 두 번째 수정(동결·기록 전)을 뜻합니다. 행은 기대 가치(이득 × 확신 ÷ 노력) 순서입니다.

| ID | Type | What exactly | Evidence | Expected effect on recall / noise / usefulness | Experiment that decides it (hypothesis, metric, pass rule, data needed) | Effort |
| --- | --- | --- | --- | --- | --- | --- |
| EVD-01 | ADD (수정 2) | **자명한 기준 탐지기와 우연 수준.**<br>• 새 함수 `bench.baselines(key, runs)`. 두 기준선을 같은 `bench.score(exact_viewport=True)`로 채점합니다.<br>• `flag_all`: 기록된 실행의 모든 스냅숏에서 보이는 요소(상호작용 요소 + 텍스트 블록)마다 범주 9개(reach, pointing, gaze, perception, cognition, game, semantics, layout, heuristic)별 발견 하나, `triggered_profiles` = 평가된 전체 프로필, severity P0. 시나리오마다 범주별 `viewport\|` 발견도 하나.<br>• `chance`: 도구 자신의 발견에서 요소 키만 시나리오 안에서 무작위로 바꿔(범주·심각도·프로필·개수 유지) 1,000번 채점.<br>• 출력: `recall_flag_all_{strict,lenient}`, `unreachable_defects`(flag_all로도 안 잡히는 결함 수, 목록은 봉인), `recall_chance_mean`, `recall_chance_p95`, `recall_above_chance`, `kappa_recall` = (recall − chance)/(1 − chance).<br>• 데이터: 스냅숏 JSON의 요소와 선택자(이미 기록됨), 키(채점기만). | 전부 보고하면 TPR·FPR 100 %, 점수 0(OWASP) [industry]. SWE-Lancer는 과제를 풀지 않고 100 %(ABC) [snippet]. 매칭 관대함(UEM-10). 컨테이너·접미사·id 접두사 규칙 [derived: `bench.py` L22–44]. | 탐지기는 그대로입니다. 재현율이 우연 대비로 해석됩니다. 매칭이 너무 관대하면 드러납니다. `unreachable_defects`는 키나 드라이버 문제를 알려 줍니다. | **H:** 우연 재현율 ≤ 0.10, flag_all lenient ≥ 0.95. **Pass:** 둘 다면 heldout-2에 그대로 등록합니다. 우연 재현율 > 0.15인 스위트가 있으면 채점 전에 매칭 규칙을 좁히는 수정을 등록하고 원래 규칙 결과도 보고합니다. flag_all strict < 0.95면 도달 불가 결함을 EVD-07로 넘깁니다. **Data:** 개발 3개 스위트의 기존 기록. | S |
| EVD-02 | ADD (수정 2) | **clean 짝 판별 재현율과 범주별 Youden J.**<br>• 키에 `clean_twin`(결함 시나리오 → clean 시나리오)을 두거나, 없으면 채점기 안에서 `-clean` 접미사, 같은 제품, 같은 흐름으로 유추합니다.<br>• 결함 d는 결함 변형에서 strict로 잡히고, 짝에서는 같은 선택자·같은 범주·조건을 만족하는 프로필로 잡히지 않을 때 `discriminating`입니다. 요소가 짝에 없으면 안 잡힌 것으로 봅니다.<br>• 출력: `recall_discriminating`, `non_discriminating`(수와 검사 ID), 범주별 J = TPR(결함 요소) − FPR(짝 요소)와 범주 평균(OWASP식).<br>• 데이터: 짝 시나리오의 기록(이미 있음), 요소 선택자. | Juliet의 good/bad 짝 [snippet]. OWASP는 범주마다 TP·FP 테스트를 둠 [industry]. LAT-04의 paired anchor Δ를 모든 검사로 넓힘. 모든 프로필에서 발화한 PT-02/PT-04/RH-01 발견(`decisions.md` Round 5) [derived]. | 재현율이 "결함 때문에 잡힌 것"만 셉니다. 문턱이 느슨한 검사가 드러납니다. 범주별 판별력을 한 숫자로 봅니다. | **H:** 개발 스위트 strict 탐지의 ≥ 95 %가 판별적. **Pass:** 보고합니다. 90 % 미만이면 비판별 탐지를 낸 검사를 `decisions.md` 검토 대상으로 올립니다. heldout-2에는 보조 지표로 등록합니다. **Data:** 개발 기록, 짝 대응. | S–M |
| EVD-03 | CHANGE (수정 2) | **확증 가설 가족을 고정 순서로 다시 짜고 MDE를 적습니다.**<br>각 단측 0.025. 앞에서 멈추면 뒤는 기술 통계입니다.<br>1. **N**(잡음 관문, EVD-05): C4@14의 clean P0–P1 단위 0개, P0–P2는 시나리오당 점추정 ≤ 0.35이고 Poisson 95 % 상한 ≤ 1.0.<br>2. **H7′**(정상성): 조건 없는 결함에서 C3 − C2의 정확 짝 구간 하한 ≥ −0.05.<br>3. **HA**(모형 기여): C4@14가 탐지한 조건부 결함 중 차등 조건이 키의 조건을 말한 비율(`condition_identified_given_detected`)의 Wilson 하한 ≥ 0.30. n = 15–20이면 점추정 약 0.53–0.55가 필요합니다.<br>4. **H3′**: C4@14 − C3의 정확 짝 구간 하한 ≥ −0.10.<br>5. **H2′**: primary 결함에서 C4@10 − C4-swap@10(EVD-06)의 하한 > 0이고 점추정 ≥ +0.10. C5와의 비교는 기술 통계. EVD-06이 기록 전에 준비되지 않으면 C4@10 − C5@10에 같은 규칙(하한 > 0, 점추정 ≥ +0.10)을 쓰고, "floor 효과와 구분되지 않음"이라고 적습니다.<br>• 기술 통계로 돌리는 것: H1, 원래 정의의 H5(탐지와 식별이 섞임), H6(`agent_judgment` 결함 < 15개일 때), 범주별 값.<br>• 가설마다 n, 80 % 검정력의 MDE, 모의실험으로 얻은 판정 분포를 적습니다.<br>• 원래 H1–H7 판정도 계산해 함께 보고합니다(사전등록 규칙). | 고정 순서법(FDA 지침) [snippet]. 연구자 자유도(Simmons) [snippet]. 검정력 분석 권고(Miller) [industry]. 2.4.4–2.4.5 [derived]. | 결과가 "inconclusive"로만 끝나는 설계를 피합니다. 유용성 주장이 미리 정한 사슬에 묶입니다. 가족 단위 오류 ≤ 2.5 %. | **H:** 새 규칙이 개발 스위트에서 얻은 그럴듯한 효과(층화 대 무작위 +0.08, A6)에서 pass ≥ 0.5, 효과 0에서 pass ≤ 0.05. **Pass:** 둘 다 만족하는 규칙만 등록합니다. **Data:** 모의실험 스크립트(`prereg_sim*.py`), 개발 스위트 효과 크기. | S |
| EVD-04 | CHANGE (수정 2) | **군집을 아는 구간과 정확 짝 방법.**<br>• 단일 비율: Wilson(지금처럼) + 제품 단위 2단계 군집 부트스트랩(제품을 뽑고 그 안에서 결함을 뽑음, 2,000회) + 제품 하나씩 뺀 범위(leave-one-product-out) + 제품별 표.<br>• 짝 비교: `_paired_diff`의 percentile 부트스트랩을 정확 조건부 방법(McNemar 기반)이나 짝 비율 차이의 score 구간(Newcombe형)으로 바꿉니다. C5처럼 결함별 값이 분수인 비교는 부호 순위 또는 순열 검정.<br>• 제품 수 G < 10이면 군집 구간은 기술용입니다. "다음 제품에서도"라는 주장은 제품별 방향(G개 중 몇 개에서 같은 부호)으로만 합니다.<br>• `ergo_eval.aggregate`에 `n_products`, `per_product`, `recall_cluster_ci95`, `recall_lopo_range`를 더합니다. | 군집 표준오차가 순진한 값의 3배 초과(Miller) [industry]. 군집이 적으면 군집 강건 SE가 너무 작음(Cameron & Miller) [snippet]. 작은 n에서 CLT 구간 실패, Wilson·베이즈는 괜찮음(Bowyer) [snippet]. DEFF 표, first-look τ ≈ 0.23, 불일치 0에서 부트스트랩 폭 0 [derived]. | 구간이 넓어지고 정직해집니다. 잘못된 pass가 줄어듭니다. | **H:** 개발 스위트에서 스위트를 군집으로 두면 군집 구간이 Wilson보다 1.3배 이상 넓다. **Pass:** 두 구간을 모두 보고하도록 구현합니다(판정 규칙은 EVD-03). **Data:** `ablation-dev-*.json`의 결함별 결과. | S |
| EVD-05 | CHANGE (수정 2) | **H4를 실효 오탐 기준과 FROC식 표로 바꿉니다.**<br>• 구성마다 심각도 문턱 4개(P0, ≤ P1, ≤ P2, ≤ P3)에서 `recall_strict`, `recall_discriminating`(EVD-02), clean 시나리오당 오탐 단위(Poisson 95 % 구간), 같은 값의 사례(instance) 단위, 짝 실효 오탐 = 짝 clean의 오탐 단위 / (결함 변형의 TP 단위 + 짝 오탐 단위)를 한 표로.<br>• 관문: P0–P1 clean 단위는 스위트 전체에서 0개. P0–P2는 시나리오당 점추정 ≤ 0.35, Poisson 95 % 상한 ≤ 1.0.<br>• 결함 밀도 d ∈ {0.5, 1, 2}에서 예상 실효 오탐 표(2.2.4)를 보고서에 싣고, "벤치마크 정밀도는 실제 제품으로 옮겨지지 않는다"고 적습니다. | 개발자 90 %가 5 %, 47 %가 15 %, 24 %만 20 %까지 허용하고 권고는 15–20 % 이하(Christakis & Bird) [paper]. Tricorder 10 % 미만(STF-02) [industry]. 경보 49–96 % 무시(van der Sijs) [snippet]. FROC·FPPI [snippet]. 현재 개발 P0–P2 0.7/시나리오, H4 상한은 실효 오탐 78–88 % [derived]. | 잡음이 실제 제약이 됩니다. 걷기·떨림 프로필에서만 44 px 표적을 P2로 올리는 발견(개발 clean P2 7개 중 4개, `decisions.md` Round 5)이 먼저 걸릴 것입니다. SIT-01(프로필 전용 터치 발견 ≤ P3)과 함께면 재현율 손실 없이 통과할 가능성이 큽니다. | **H:** 현재 탐지기는 새 관문을 못 넘고(0.7 > 0.35), SIT-01을 적용하면 넘으며 strict 재현율 손실은 1개 이하. **Pass:** 그렇다면 새 관문을 수정 2에 등록합니다. **Data:** 개발 기록 재분석. | S |
| EVD-06 | ADD (수정 2, 기록 전) | **위약(placebo)·floor 전용 오디언스 팔과 Stage-0 반복.**<br>같은 기록 위에서 오프라인 분석만 더합니다(기록 비용 없음).<br>• `C4-swap@{10,14}`: 각 제품을 다른 제품의 `audience.json`으로 구성(제품 순환 치환).<br>• `C4-floors@{10,14}`: 중립 오디언스(성인 일반 세그먼트 하나, 조건은 floor만)로 구성.<br>• `C4-rep{1..3}`: 제품마다 Stage-0을 독립 세션에서 3번(가능하면 다른 Claude 모델이나 프롬프트) 돌린 파일로 구성하고, C5처럼 평균과 범위를 보고. 파일마다 `audience_run_id`, 모델, 프롬프트 해시를 기록.<br>• 판정: "오디언스 조사가 floor를 넘어 가치를 더한다"는 primary 결함에서 C4-true − C4-floors와 C4-true − C4-swap이 모두 하한 > 0일 때만. 아니면 이득은 floor와 층화의 몫으로 보고합니다. | 개발 스위트에서 층화 0.906 대 무작위 0.827(기기당 10개), 즉 floor만으로 C5를 이길 수 있음 [derived]. `audience_relevance`와 Stage-0이 같은 brief에서 나오고 둘 다 Claude(순환성) [derived]. LLM 자기 편향(Silencer, Xu) [snippet]. C4는 확률적 추출 한 번, C5는 20 시드 평균 [derived: `ergo_eval.configurations`]. | H2가 재는 것을 "오디언스 조사의 가치"로 좁힙니다. 재현율·잡음에는 직접 영향이 없습니다. 유용성 주장의 핵심 반례를 미리 배제합니다. | **H:** C4-true가 C4-swap과 C4-floors보다 primary 재현율이 높다. **Metric:** 짝 차이와 정확 구간, 제품별 부호. **Pass:** 위 판정. **Data:** 제품당 오디언스 파일 2개 추가(Stage-0 토큰 비용), 기존 기록. | M |
| EVD-07 | ADD | **답안 키 감사(과제 타당도).**<br>• 도구 작성자가 아닌 검토자(가능하면 사람 UX·접근성 실무자, 아니면 서로 다른 Claude 모델 2개)가 결함과 decoy마다 두 변형의 스크린숏과 선택자를 보고 판정합니다: (1) 명시된 조건의 사용자에게 실제 문제인가(yes/no/unsure); (2) 선택자가 기록된 DOM에서 유일하고 존재하는가; (3) `severity_min`이 ±1 안에서 타당한가; (4) decoy가 인용 기준에서 정말 허용되는가.<br>• 출력은 봉인된 `key_audit.json`. 공개는 집계만: 키 타당 비율, 선택자 모호 비율, decoy 타당 비율.<br>• 채점을 두 번 합니다: 전체 결함, 감사 통과 결함만. | 과제 타당도(ABC) [snippet]. 틀린 라벨이 자기 편향의 최대 요인(Silencer) [snippet]. Defects4J의 최소화·재현 기준 [industry]. UEM-08의 심각도 합의. | 재현율의 분모가 깨끗해집니다. 키 잡음의 크기를 알게 됩니다. | **H:** 결함의 ≥ 90 %가 타당하고 선택자의 ≥ 95 %가 유일하다(개발 스위트 먼저). **Pass:** 90 % 미만이면 heldout-2 결과를 감사 통과 부분집합과 함께 공동 1차로 보고합니다. **Data:** 키, 두 변형의 스크린숏. | M |
| EVD-08 | CHANGE | **판정 프로토콜 v2(2차 판정).**<br>• 단위마다 판정자 3명, 다수결. Claude 전용 규칙에서는 Opus·Sonnet 두 모델 이상, 또는 LAT-14의 증거 틀 세 가지.<br>• 배치마다 20 %를 숨긴 금(gold) 항목으로 채웁니다: 알려진 타당(EVD-02의 판별 strict 매치)과 알려진 부당(decoy 요소 발견, 짝 clean에서만 나온 발견). 판정자는 금 여부를 모릅니다. 금 항목에서 판정자 민감도·특이도를 구해 LAT-15의 보정에 씁니다.<br>• 표본: 전체 ≥ 60단위(타당도 ±0.10–0.12). KEEP/CUT이 걸린 검사 가족마다 추가로 ≥ 13단위(0.5 대 0.17) 또는 ≥ 23단위(0.5 대 0.25).<br>• 보고: Krippendorff α(명목)와 부트스트랩 95 % 구간, 불일치를 따로 둔 전체 혼동표, 금 정확도.<br>• 눈가림: 변형(결함/clean), 구성, basis, 심각도, 검사 이름. 규칙 문구는 중립화. | α ≥ .800/.667(Hayes & Krippendorff) [snippet]. κ가 퍼센트 일치보다 판정자를 잘 구분(Thakur) [snippet]. 1차 κ 0.715(0.45–0.91) [derived]. 표본 크기 [derived]. LAT-14, LAT-15. 위치·자기 강화 편향(Zheng), 자기 선호(Panickssery) [snippet]. | 정밀도 추정에 알려진 오차가 붙습니다. 가족별 결정이 가능해집니다. 판정 비용은 약 1.5배. | **H:** 1차의 68단위를 v2로 다시 판정하면 α 하한 ≥ 0.667, 금 정확도 ≥ 0.9. **Pass:** 둘 다면 2차 판정에 씁니다. 아니면 판정자는 검토 순서 정렬에만 씁니다. **Data:** 1차 단위와 스크린숏. | S–M |
| EVD-09 | ADD | **사람 기준 집합과 alt-test.**<br>• 층화한 60단위(금 12개 포함)를 사람 3명이 눈가림으로 라벨링합니다(예: 사용자 본인 + UX·접근성 실무자 2명).<br>• Alt-test(ε = 0.2, 전문가 기준, 승률 ≥ 0.5, 가족이 여럿이면 BY-FDR)로 EVD-08 패널이 사람을 대신할 수 있는지 판정합니다.<br>• 실패하면 정밀도 주장은 사람 라벨로만 하고, LLM 판정은 검토 순서 정렬에만 씁니다(LAT-14의 대체안). | Alt-test: 사람 ≥ 2명(3명 권장), 50–100항목, 전문가 ε 0.2 [paper, 저자 README]. 전문 과제에서 SME와 LLM 판정 일치 64–68 %(Szymanski) [snippet]. 일반 과제에서는 80 % 초과(Zheng) [snippet]. 같은 계열 자기 편향 [snippet]. 사용자의 Claude 전용 규칙은 하위 에이전트에 대한 것이고 사람 라벨을 막지 않는다고 봄 [opinion]. | 외부 기준으로 판정자를 보정하는 유일한 수단입니다. 유용성 주장의 신뢰도가 크게 오릅니다. | **H:** 패널이 alt-test를 통과한다. **Metric:** 승률, 평균 우위 확률. **Pass:** 통과하면 2차 판정의 LLM 라벨을 정밀도 추정에 씁니다. **Data:** 사람 3명 × 60단위 × 1–2분 ≈ 3–6인시. | M |
| EVD-10 | ADD (가능하면 수정 2) | **외부 기준선 C0: axe-core(+ Lighthouse 접근성)와 합집합.**<br>• 기록 단계에서 스냅숏마다 axe-core 4.13(WCAG 태그 위반만)을 돌리고(AUT-02 층), 규칙을 스킬 범주로 매핑(AUT §3.3)한 뒤 같은 채점기로 채점. `C0`, `C0∪C1`, `C0∪C4@14`를 보고합니다.<br>• 유용성 헤드라인: C4@14 − C0의 strict 재현율 차이(정확 짝 방법)와 clean 시나리오당 오탐 차이, "C0가 못 찾은 결함" 수(목록은 봉인).<br>• C1(이 도구의 측정 검사)은 내부 절제로만 씁니다.<br>• 데이터: 라이브 페이지(기록 중 axe 호출), DOM, 접근성 트리. | axe·Lighthouse·ATF와 비교하지 않았다고 명시(`validation-and-limits.md`) [derived]. 도구 완전성 14–38 %(Vigo) [snippet]. 최고 도구 40 %(GOV.UK) [industry, AUT 경유]. 같은 테스트 세트에서 도구를 비교(OWASP) [industry]. 정확도만 보면 향상의 원인을 잘못 짚음(Kapoor) [snippet]. | "표준 도구보다 낫다"는 주장을 가능하게 하는 유일한 비교입니다. 인간공학 모형과 프로필이 더하는 증분이 드러납니다. | **H:** C4@14의 strict 재현율이 C0보다 높고(정확 짝 구간 하한 > 0), clean 오탐은 C0보다 시나리오당 0.35 이하로만 많다. **Pass:** 둘 다. **Data:** AUT-02 구현, heldout-2 기록 단계의 axe 호출(동결 전에 들어가야 함). | M |
| EVD-11 | CHANGE | **일대일 매칭, 사례 단위 지표, 단위 순도.**<br>• 결함과 발견 사이 최대 이분 매칭(간선 = strict 매치, 동률이면 심각도, 그다음 선택자 구체성). `recall_strict_1to1`과 `multi_credit_findings`(결함 2개 이상을 채점한 발견·단위)를 보고합니다.<br>• `validity_lb_instances` = 채점 페이지의 matched 사례 / 전체 사례. `unit_purity` = matched 단위 안의 matched 사례 / 그 단위의 사례. clean control을 단위와 사례 두 가지로 셉니다.<br>• 단위 키는 채점기와 함께 동결하고, 바꾸면 이전 키 결과도 보고합니다. | 한 정답에 탐지 하나(PASCAL VOC) [snippet]. 통합의 효과(Law & Hvannberg) [snippet]. 매칭 dogma(Hornbæk) [snippet]. UEM-02, UEM-04. `bench.py` L32–33·L99–100, `swarm.py` L173 [derived]. | 단위 굵기로 정밀도를 올리는 Goodhart 경로를 막습니다. 재현율은 거의 그대로일 것입니다. | **H:** 개발 스위트에서 `recall_strict_1to1`과 `recall_strict`의 차이 ≤ 1개, 단위 순도 ≥ 0.5. **Pass:** 보고합니다. 차이가 1개를 넘으면 키 선택자 겹침을 EVD-07로 넘깁니다. **Data:** 기존 기록. | S |
| EVD-12 | CHANGE | **보관 강화(오염·사고 방지).**<br>• held-out 스위트의 모든 파일과 README에 canary GUID와 "학습 금지" 문구.<br>• 저장소 루트 `.ignore`(ripgrep이 읽음)에 `benchmarks/heldout-*/keys/`, `site/`, `scenarios/`를 넣어 저장소 전체 검색이 내용을 출력하지 않게 합니다. 저자는 `--no-ignore`로 접근합니다.<br>• held-out 키는 채점 전까지 암호화 보관(예: `age`)하고 비밀번호는 사용자가 보관합니다. `ergo_eval.py score`만 복호화합니다.<br>• 채점기가 `LOOKS.md`(커밋, 시각, 출력한 집계)를 덧붙여 held-out 열람 횟수를 감사할 수 있게 합니다. 첫 채점 뒤 개발 스위트 전환은 유지. | BIG-bench canary [industry]. 홀드아웃 재사용의 정보 누출(Dwork) [snippet]. 과거 누출 기록(`validation-and-limits.md`) [derived]. ripgrep의 `.ignore` 처리 [opinion: 문서 재확인 안 함]. | 사고성 누출과 미래 학습 오염을 줄입니다. 비용은 거의 없습니다. | 실험 없음. **점검:** 저장소 루트에서 `rg -l severity_min`이 held-out 키를 출력하지 않고, canary 존재 테스트가 통과. | S |
| EVD-13 | CHANGE | **`decisions.md`의 KEEP/CUT 규칙을 순차 베이즈 규칙으로.**<br>• 판정 타당도에 Beta(1, 1) 사전분포. 강등: P(타당도 < 0.5) ≥ 0.95(예: 13개 중 ≤ 3, 20개 중 ≤ 6). 유지: P(타당도 > 0.5) ≥ 0.95(13개 중 ≥ 10, 20개 중 ≥ 14). 그 사이는 "미정, 더 표집"(검사당 최대 30).<br>• 고유 탐지는 두 스위트 이상에서 세고, 그중 하나는 첫 채점 스위트여야 합니다.<br>• 판정 단위가 한 페이지에 몰리면 페이지당 최대 2개(군집 완화). | 1/6은 Wilson 0.03–0.56, P(< 0.5) = 0.94. 0.5 대 0.17에 13개, 0.5 대 0.25에 23개 [derived]. 순차 표집이 평균 표본을 줄인다는 점 [opinion; SPRT 문헌은 이번에 확인하지 않음]. | 강등과 유지가 대칭이 되고 표본 낭비가 줄어듭니다. 개발 스위트에 과적합한 결정이 줄어듭니다. | **H:** 1차 판정 자료에 소급하면 기존 강등의 대부분이 유지되고, 일부는 "미정"이 된다. **Metric:** 결정이 바뀐 검사 수. **Pass:** 규칙을 채택합니다(도구 변경 없음). **Data:** `adjudication-round1.json`. | S |
| EVD-14 | ADD | **첫 채점 장부와 스위트 간 통합 추정.**<br>• `docs/validation/first-looks.md`: 스위트, 동결 커밋, 결함 수, 제품 수, strict·판별 재현율, clean 시나리오당 오탐.<br>• 로짓 척도의 랜덤효과 모형(DerSimonian–Laird 또는 베이즈)으로 통합 추정과 **새 스위트에 대한 95 % 예측구간**을 보고합니다. 같은 탐지기 버전끼리만 통합하고, 버전이 다르면 층으로 나눕니다. | 새 테스트 세트에서 성능 하락과 순위 보존(Recht) [snippet]. first-look 0.82/0.31/0.60 → τ ≈ 0.23 [derived]. 홀드아웃 재사용 제한(Dwork) [snippet]. | "다음 제품에서 얼마나 찾나"에 정직하게 답합니다. 개발 수치를 held-out처럼 읽는 오류를 막습니다. | **H:** heldout-2 첫 채점이 기존 first-look의 예측구간 안에 든다. **Metric:** 예측구간 폭. **Pass:** 보고만. **Data:** 기존 3개 + heldout-2. | S |
| EVD-15 | ADD | **실제 결함 벤치마크(Defects4J식).**<br>• 오픈소스 웹 앱에서 UI·접근성 버그 ≥ 30개를 채굴합니다: 이슈 라벨(a11y, accessibility, ui), 수정 PR·커밋 연결, 단일 커밋 수정, 무관한 변경 제거, 버그·수정 두 커밋에서 Playwright 시나리오로 재현.<br>• 정답 = 이슈 + 수정 diff. 음성 = 수정 커밋(자연스러운 clean 짝). 범주는 스킬 범주로 매핑.<br>• 버그 커밋에서 재현율, 수정 커밋에서 짝 오탐 단위를 셉니다. 합성 스위트와 절대 합치지 않습니다. | Defects4J 기준(이슈 연결, 단일 커밋, 최소화, 트리거 테스트) [industry]. 손으로 심은 결함은 더 어려움(Andrews), 실제 결함의 73 %가 변이체와 결합(Just)(STF 경유) [snippet]. 사례-대조 설계의 스펙트럼 편향(Lijmer) [snippet]. `validation-and-limits.md`의 "Real products" 보정 계획 [derived]. | 첫 외적 타당도 측정입니다. 재현율은 더 낮고 범주 구성도 다를 것입니다. 인간공학 조건 결함은 이슈로 드물 수 있습니다(한계). | **H:** 실제 결함 재현율이 합성 held-out 재현율의 구간 안에 든다. **Metric:** strict·판별 재현율, 수정 커밋의 오탐 단위. **Pass:** 보고만(외적 타당도 추정). **Data:** 채굴 스크립트, 앱 5–10개. | L |
| EVD-16 | ADD | **유용성 주장 보고 점검표.** `validation-and-limits.md`와 held-out 보고서마다 한 표로:<br>(1) 흐름: 작성된 결함 → 키 감사 통과 → 도달 가능(flag_all) → 채점;<br>(2) 구성별 strict·판별·일대일 재현율, Wilson + 군집 구간, 제품별 값;<br>(3) 기준선: 우연, flag_all, C0;<br>(4) FROC 잡음 표와 결함 밀도별 실효 오탐;<br>(5) 판정: 판정자 모델, α/κ와 구간, 금 정확도, 사람 기준 alt-test 결과;<br>(6) 사전등록과의 차이(수정 시점, 원래 판정과 수정 판정);<br>(7) held-out 열람 횟수(`LOOKS.md`);<br>(8) 역할별 모델 계열(저자, 도구 작성자, Stage-0, 조작자, 판정자);<br>(9) 일치한 결함당 비용(기록 초, 토큰);<br>(10) 주장할 수 없는 것(유병률, 실제 사용자 재현율). | 설계 편향(Lijmer) [snippet]. ABC의 보고 항목 [snippet]. 비용 보고(Kapoor) [snippet]. 공개 요건(Simmons) [snippet]. | 재현율·잡음은 그대로입니다. 제3자가 주장을 점검할 수 있게 됩니다. | 실험 없음. **Pass:** heldout-2 보고서가 10항목을 모두 채운다. | S |
| EVD-17 | CUT | **결정에 쓸 수 없는 지표를 요약에서 뺍니다.**<br>• 빼는 것: 발견 단위 `precision_labeled`(lenient 매치와 중복을 TP로 셈, 미라벨 제외); 한쪽 `severity_agreement`(UEM-04·STF-05의 양측 지표로 대체); n < 10 범주의 pass/fail(k/n만); 분모 없는 `decoys_flagged`(k/n + Wilson으로); `thoroughness_strict`(`recall_strict`와 같은 값); 요약의 `recall_lenient`(진단용으로만).<br>• H1은 통과 규칙이 없으므로 "가설"이 아니라 보고 항목으로 이름을 바꿉니다.<br>• JSON에는 호환을 위해 남기고 보고서와 요약에서만 뺍니다. | 2.2.5 [derived]. UEM-04. `bench.py` 출력 목록 [derived]. | 오해를 부르는 수치가 줄어듭니다. 비용 0. | 실험 없음(표현 변경). **점검:** 요약에 이 지표들이 없다. | S |
| EVD-18 | CUT (조건부) | **C1과 C5를 유용성 주장의 비교 대상에서 내립니다.**<br>• C1은 표준 스캐너가 아니므로(`validation-and-limits.md` 각주) 내부 절제로만 쓰고, 외부 비교는 C0(EVD-10)으로 합니다.<br>• C5(기저율 무작위)는 개발 스위트에서 이미 층화에 지므로, 오디언스 조사의 가치 주장은 EVD-06의 swap·floor 팔로 합니다. C5는 계속 계산하되 기술 통계로 둡니다.<br>• 조건: EVD-06과 EVD-10이 들어간 뒤. | 각주 [derived]. 층화 0.906 대 무작위 0.827 [derived]. | 허수아비 비교가 없어집니다. 계산은 오프라인이라 비용 차이는 거의 없습니다. | 실험 없음. **Pass:** 수정 2에 반영. | S |
| EVD-19 | ADD (낮은 우선순위) | **비용 비율을 선언하고 순가치로 기본 운영점을 고릅니다.**<br>• `net_value(cutoff)` = Σ(탐지된 결함의 w(`severity_min`)) − λ · clean 오탐 단위(≤ cutoff). w = {P0: 8, P1: 4, P2: 2, P3: 1}(UEM 지표 카드). λ는 검토 시간 추정에서 정합니다(예: λ = 1이면 거짓 P2 단위 하나의 비용이 P3 결함 하나를 찾은 가치와 같음).<br>• 개발 스위트에서 보고서 기본 문턱(예: ≤ P2)을 고르고 동결한 뒤 held-out에서 확인합니다. | SV-COMP 비대칭 점수 [snippet]. OWASP Youden [industry]. 오탐 허용치(Christakis & Bird) [paper]. | 기본 보고 범위를 근거 있게 정합니다. λ가 주관적이라는 약점이 있습니다. | **H:** 개발에서 고른 문턱이 held-out에서도 순가치 최대 문턱과 같거나 한 단계 차이. **Data:** FROC 표(EVD-05). | S |
| EVD-21 | CHANGE (다음 held-out) | **heldout-3 설계: 제품을 늘리고 제품당 결함을 줄입니다.**<br>• 같은 결함 약 45개를 제품 4개 × 11개 대신 제품 8–12개 × 4–6개로 나눕니다.<br>• 결함마다 `clean_twin`, `detectable_by`, `audience_relevance`, `taxonomy_ref`를 두고, 키 감사(EVD-07)와 canary(EVD-12)를 처음부터 넣습니다.<br>• 저자는 제품마다 다른 세션으로, 가능하면 다른 Claude 모델로 씁니다. 제품 brief에는 실제 사용 통계처럼 오디언스 조사가 찾아야 하는 사실을 넣고, `audience_relevance` 라벨은 brief 저자가 아닌 사람이나 다른 세션이 붙입니다(순환성 완화, EVD-06).<br>• 조건 둘이 겹쳐야 드러나는 결함(STF-06, STF-07)과 `agent_judgment` 결함을 각각 15개 이상으로 둬서 H6과 조합 가설의 검정력을 확보합니다. | DEFF [derived]: 결함 45개, ICC 0.2에서 제품 4개면 DEFF 3.05(유효 n 15), 8개면 1.93(23), 12개면 1.55(29). ICC 0.1이면 22, 31, 35. H5·H6의 요구 k [derived]. 자기 편향(Silencer, Xu) [snippet]. | 같은 작성 비용으로 "다음 제품" 주장의 유효 표본이 1.5–2배가 됩니다. | **H:** 같은 결함 수에서 제품별 군집 구간이 heldout-2보다 좁다. **Metric:** 군집 부트스트랩 반폭. **Pass:** 보고. **Data:** heldout-3 저작(벤치마크 저자). | M |
| EVD-20 | KEEP | **문헌과 맞는 현재 관행.**<br>• 사전등록, 날짜가 적힌 수정, 원래 분석도 보고하는 규칙;<br>• 결함별 결과 봉인, 집계를 먼저 커밋;<br>• "한 번 채점하면 개발 스위트";<br>• 설계로 넣은 음성(clean control, decoy);<br>• 채점기가 바뀌면 두 결과를 모두 보고(heldout-mixed 0.60/0.80);<br>• C5 20 시드, 단일 비율의 Wilson 구간;<br>• 가설 사이 조정 금지;<br>• 같은 계열, 사후 조정, 누출의 공개(`validation-and-limits.md`). | Dwork, Simmons [snippet]. OWASP [industry], Juliet [snippet]. Bowyer [snippet]. | 없애면 신뢰도가 떨어집니다. | 모든 실험의 회귀 점검으로 유지합니다. | – |

### 3.2 사전등록 수정 2 초안 (heldout-2, 기록 전에 커밋)

아래는 제안입니다. 도구 작성자가 heldout-2 내용을 보지 않은 상태에서, 동결과 첫 기록 전에 날짜를 적어 커밋해야 합니다. 이미 기록이 시작되었다면 "기록 뒤, 채점 전 수정"으로 표시하고, 1차 판정은 원래 규칙으로 두고 아래는 보조 분석으로만 씁니다.

1. **원래 분석 유지.** H1–H7을 원래 규칙으로 계산해 보고합니다.
2. **확증 가족(고정 순서).** N → H7′ → HA → H3′ → H2′ (EVD-03). 앞에서 멈추면 뒤는 기술 통계입니다.
3. **추가 구성.** C0(axe, EVD-10), C4-swap, C4-floors, C4-rep1..3(EVD-06). 모두 같은 기록 위에서 오프라인으로 분석하고, C0만 기록 단계에 axe 호출이 필요합니다.
4. **추가 지표.** `recall_above_chance`, `recall_flag_all`(EVD-01), `recall_discriminating`과 범주별 J(EVD-02), `recall_strict_1to1`, `unit_purity`, 사례 단위 잡음(EVD-11), FROC 표(EVD-05), 제품별 값과 군집 구간(EVD-04).
5. **구간 방법.** 단일 비율은 Wilson + 군집 부트스트랩, 짝 비교는 정확 조건부 방법(EVD-04).
6. **판정.** EVD-08 프로토콜, 가능하면 EVD-09의 사람 기준 집합.
7. **MDE 표.** 가설마다 n과 80 % 검정력의 최소 검출 효과를 적습니다. heldout-2의 결함 수는 도구 작성자에게 집계로만 알려 줄 수 있으므로, 표는 n = 30, 40, 50, 60의 격자로 미리 적어 둡니다.

### 3.3 유용성 주장을 할 수 있는 최소 조건

아래가 모두 성립할 때만 "이 스킬은 표준 도구와 단일 페르소나가 놓치는 결함을, 감당할 수 있는 잡음으로 찾는다"고 씁니다 [opinion, 2.1–2.5에서 도출].

1. **N 관문 통과**: held-out에서 P0–P1 clean 단위 0, P0–P2 시나리오당 ≤ 0.35(EVD-05).
2. **외부 기준선 대비 증분**: C4@14 − C0의 strict 재현율 하한 > 0(EVD-10). C1이나 C2 대비만으로는 부족합니다.
3. **우연 대비**: `recall_above_chance`의 하한 > 0이고, 판별 재현율이 strict 재현율과 크게 다르지 않음(EVD-01, EVD-02).
4. **모형 기여**: HA 통과. 조건부 결함이 "조건을 가진 프로필이 거기 있었기 때문"이 아니라 모형이 조건을 짚었기 때문에 잡혀야 합니다.
5. **사람에 닿은 정밀도**: 판정자가 사람 기준 집합에서 alt-test를 통과했거나, 정밀도를 사람 라벨로 추정(EVD-09).
6. **제품별 일관성**: 위 2와 4의 방향이 제품 대부분에서 같음(EVD-04).
7. **키 감사 통과율 보고**(EVD-07)와 **보고 점검표 10항목**(EVD-16).

오디언스 조사의 가치(H2′)와 에이전트 층의 가치(H6)는 위와 별개의 주장입니다. 각자 통과할 때만 따로 씁니다.

### 3.4 작업 순서

1. **지금(기록 전, 1–2일):** EVD-01, EVD-02, EVD-04, EVD-05, EVD-11을 채점기에 구현하고 개발 스위트에서 계산합니다. EVD-03의 모의실험으로 규칙을 확정하고, 수정 2(3.2)를 커밋합니다. EVD-12의 `.ignore`와 canary도 이때 넣습니다.
2. **기록 전(며칠):** EVD-06의 Stage-0 반복 두 번, EVD-10의 axe 호출(AUT-02가 준비되었다면). 둘 다 기록 전에 끝나야 합니다. 준비가 안 되면 수정 2에서 "다음 held-out으로 연기"라고 적습니다.
3. **채점과 함께:** EVD-07(키 감사, 봉인), EVD-08(판정 v2), EVD-16(보고 점검표).
4. **다음 단계:** EVD-09(사람 기준 집합), EVD-13(규칙 교체), EVD-14(장부), EVD-17·18(표현 정리), EVD-19.
5. **다음 held-out을 만들 때:** EVD-21(제품 수를 늘린 설계).
6. **장기:** EVD-15(실제 결함 벤치마크).

## 4. Risks, open questions and what could not be verified (위험, 열린 질문, 확인하지 못한 것)

### 4.1 확인하지 못했거나 일부만 확인한 것

- **원문 접근.** 1.2의 도메인이 막혀 논문 대부분을 검색 발췌로만 봤습니다. 원문에서 확인한 것은 OWASP Benchmark(점수와 구성), Defects4J(README), Christakis & Bird 2016(전문), Anthropic의 평가 통계 글, alt-test README, BIG-bench README뿐입니다.
- **기억에서 떠올렸고 판단 근거로 쓰지 않은 것.**
  - Zheng et al. 2023의 판정자별 위치 일관성 수치.
  - Simmons et al. 2011의 조합 위양성률(약 61 %).
  - Papadakis et al. 2018에서 스위트 크기를 통제한 뒤 상관이 약했다는 결론의 방향과 크기.
  - Kapoor et al. 2024의 "홀드아웃이 부실하다"는 문장.
- **발췌 수준인데 수치를 쓴 것.** Juliet 규모(64,099개, CWE 118개), SV-COMP 점수(해마다 다를 수 있음), Krippendorff α 기준값, Thakur의 κ 값, Szymanski의 64–68 %, Silencer의 0.655 → 0.833, Recht의 하락 폭, van der Sijs의 49–96 %, Lijmer의 약 3배, Infer의 70 %. 문턱이나 코드에 넣기 전에 원문으로 확인해야 합니다.
- **확인하지 않은 방법론 출처.** Newcombe(1998)의 짝 비율 차이 score 구간, STARD 2015 항목, SPRT, ripgrep의 `.ignore` 처리. 모두 표준적이라고 알고 있지만 이번 세션에서 원문을 보지 않았습니다.
- **저장소 수치의 가정.**
  - 개발 스위트의 clean 시나리오 수(약 10개)와 결함 시나리오당 결함 수(약 5.3개): heldout-mixed의 a/b 변형 중 어느 쪽이 clean인지 확인하지 않았습니다(benchmarks 폴더를 읽지 않음).
  - 1차 판정의 κ 재구성: 불일치 6개를 3 대 3으로 가정했습니다. κ 0.715로 보고값 0.72와 맞습니다.
  - 스위트 간 τ ≈ 0.23: first-look 세 개가 탐지기 버전도 달라서, 스위트 차이와 버전 차이가 섞인 거친 값입니다.
  - 2.4.5의 모의실험: 결함 난이도 분포(모든 시드가 찾음 35 %, 아무도 못 찾음 15 %, 나머지 균등)를 제가 정했습니다. 판정 확률의 크기는 이 가정에 따라 달라집니다. 결론의 방향("문턱 효과에서 pass가 거의 불가능", "불일치 0이면 구간 폭 0")은 가정에 거의 의존하지 않습니다.
- **heldout-2의 제품 수와 결함 수**는 모릅니다(눈가림). 2.2.1과 EVD-21의 "제품 4개" 계산은 가정입니다.

### 4.2 권고안의 위험

- **EVD-01(기준 탐지기).** flag_all은 요소 × 범주 × 프로필로 발견이 아주 많아지지만 오프라인 계산이라 괜찮습니다. 우연 수준은 도구의 발견 밀도에 따라 달라지므로, 밀도가 다른 구성끼리 `kappa_recall`을 비교할 때 조심해야 합니다.
- **EVD-02(clean 짝).** 짝 대응이 모호할 수 있고, clean 짝이 결함 수정 말고도 다를 수 있습니다. 요소가 짝에 없으면 판별적으로 세는 규칙은 판별 재현율을 조금 부풀립니다. 짝에 요소가 없던 경우의 수를 따로 보고해야 합니다.
- **EVD-03, EVD-05(규칙 변경).** 채점 전에 규칙을 바꾸는 것은 누구도 결과를 보지 않았을 때만 정당합니다. "골대를 옮긴다"는 인상을 피하려면 원래 판정을 함께 보고하고, 수정 이유를 이 브리프와 개발 스위트 모의실험으로만 적어야 합니다.
- **EVD-05의 잡음 목표.** 근거는 코드 리뷰 도구에 대한 개발자 조사입니다. UX 보고서의 독자와 비용 구조는 다릅니다. 실제 결함 밀도 d도 모릅니다. 관문이 너무 빡빡하면 실제 P2 문제가 가설 목록으로 밀려납니다. 가설 목록을 한 번에 볼 수 있게 두는 규칙(UEM-03)을 유지해야 합니다.
- **EVD-06(위약 오디언스).** 제품끼리 오디언스가 비슷하면 swap 팔이 C4-true와 같아져 차이가 0이 됩니다. 이것은 오디언스 조사가 쓸모없다는 뜻이 아니라 제품이 비슷하다는 뜻일 수 있습니다. 오디언스 파일 사이 유사도(세그먼트·조건의 Jaccard)를 함께 보고해야 합니다. Stage-0 반복은 토큰 비용이 듭니다.
- **EVD-08, EVD-09(판정).** 사람 판정자에게도 평가자 효과가 있습니다(UEM 브리프의 Hertzum & Jacobsen). 사람끼리 일치가 낮으면 alt-test는 "잡음 많은 사람만큼은 한다"는 쉬운 통과가 될 수 있으므로, 사람끼리 α도 함께 보고해야 합니다.
- **EVD-10(axe 기준선).** axe 규칙을 스킬 범주로 매핑하는 방식이 결과를 좌우합니다. axe가 키에 없는 실제 문제를 찾으면 미라벨로 세고 오탐으로 세지 않아야 합니다.
- **EVD-12(보관).** 암호화는 번거롭고, `.ignore`는 검색만 막고 `cat`은 막지 못합니다. 규율을 대신하지 않고 사고를 줄일 뿐입니다.
- **EVD-13(베이즈 규칙).** Beta(1, 1) 사전분포와 0.95 문턱은 정책 선택입니다. 페이지당 2개 제한은 정보를 버립니다.
- **EVD-15(실제 결함).** 이슈로 올라오는 결함은 누군가 알아챈 결함(예: 스크린 리더 사용자)이라 스펙트럼이 다릅니다. 엄지 도달이나 걷기 중 오터치 같은 인간공학 결함은 이슈로 드물어, 스킬의 고유 범주가 과소 대표될 것입니다.
- **지표가 늘어나는 위험.** 지표를 많이 더하면 그 자체가 갈림길(forking paths)이 됩니다. 판정은 EVD-03의 확증 가족에만 붙이고, 나머지는 기술 통계로 둔다는 규칙이 이를 막습니다.

### 4.3 열린 질문

- 모형 기반 발견(예: 노안 프로필의 작은 글자)에서 "실제 문제"는 무엇인가? 판정자는 규칙 적합성(conformance)만 잴 수 있고, 예측 타당도는 사용자 관찰이 필요합니다(UEM-14, UEM-17).
- 한국 앱의 시나리오당 실제 결함 밀도 d는 얼마인가? EVD-05의 목표가 여기에 달려 있습니다. EVD-15의 실제 결함 벤치마크나 실제 제품 감사의 `disposition` 장부(STF-02)로 추정할 수 있습니다.
- 일반화의 단위는 무엇인가? 오디언스 주장은 제품이 단위이고, 검사 주장은 페이지나 요소가 단위일 수 있습니다. 가설마다 단위를 사전등록에 적어야 합니다.
- heldout-2에 제품이 4개 안팎이라면, "다음 제품에서도"라는 주장은 데이터 4개에 기댑니다. heldout-3을 EVD-21처럼 설계할지 결정해야 합니다.
- 같은 계열 LLM 판정자가 정밀도 추정에 쓰일 수 있는 조건은 무엇인가? 이 브리프의 답은 "사람 기준 집합에서 alt-test를 통과할 때만"입니다. 사용자의 Claude 전용 규칙이 사람 라벨까지 막는지는 사용자에게 확인해야 합니다.
- 에이전트 층(C6)은 LAT 브리프가 다뤘습니다. 이 브리프의 기여는 H6의 요구 k(결함 10개면 6개)와 "결함 15개 미만이면 기술 통계로"라는 규칙뿐입니다.
