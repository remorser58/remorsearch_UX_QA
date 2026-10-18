from __future__ import annotations
import contextlib,copy,io,json,tempfile,unittest
from unittest.mock import patch
from datetime import datetime,timezone
from pathlib import Path
import _paths
import engine_release_factory as f
from uxresearch import audiences,merge,personas
from uxresearch.canonical import EngineError,byte_digest,canonical,digest
from uxresearch.cli import main
from uxresearch.ledger import Run
from uxresearch.storage import Store,atomic,read_bytes,read_json
from scripts.validate_bundle import validate_bundle

FIXTURES=Path(__file__).parent/"fixtures/research"
TASK_DATA=json.loads((FIXTURES/"persona-task-data.json").read_text())
NOW=datetime.fromtimestamp(f.CLOCK,timezone.utc)
STOPPED_ACCESS=dict(rung="R1",presentation="honest_ua",verdict="suspect",stop_class="auth_gate",
                    fetched_at="2026-09-15T00:00:00Z",robots=dict(decision=None,status=None),
                    context="anonymous",terms=None)


def in_memory_gate(bundle,*,query=None,mode="live"):
    rows,issues,warnings=f.grade(bundle,query=query)
    return dict(mode=mode,bundle_input_sha256=digest(bundle),process_input_sha256="0"*64,
                claims=rows,result="pass" if not issues else "fail")


def authored(starter_or_bundle,claim_ids,**overrides):
    if isinstance(starter_or_bundle,dict) and "claim_cards" in starter_or_bundle:
        bundle_id,gate_hash=starter_or_bundle["bundle_id"],starter_or_bundle["gate_bundle_input_sha256"]
    else:
        bundle_id,gate_hash=starter_or_bundle["bundle_id"],starter_or_bundle["gate_bundle_input_sha256"]
    entry=dict(persona_id="PER-first-cost",label_ko="첫 주문 최종 금액 확인 가설",
               situation_ko="할인 안내를 보고 주문을 시작해 배달팁 포함 최종 금액을 확인하려는 상황",
               assumptions_ko=["첫 사용·한 손 사용은 검사를 위해 정한 조건이며 사용자 비율과 선호는 알 수 없다."],
               motivation_claim_ids=list(claim_ids),authored=True,
               scenario=dict(scenario_id="SC-first-cost",task_goal_ko=TASK_DATA["task_goal_ko"],
                             context_ko=TASK_DATA["context_ko"],concrete_data=TASK_DATA["concrete_data"],
                             surface_url=TASK_DATA["surface_url"],device_ids=TASK_DATA["device_ids"],
                             a11y_conditions=["one_hand"],
                             expected_behavior_ko=TASK_DATA["expected_behavior_ko"],
                             expected_decision_ko=TASK_DATA["expected_decision_ko"],
                             likely_failure_ko=TASK_DATA["likely_failure_ko"],
                             falsifying_product_test_ko=TASK_DATA["falsifying_product_test_ko"],
                             falsifying_interview_question_ko=TASK_DATA["falsifying_interview_question_ko"],
                             priority=TASK_DATA["priority"]))
    entry.update(overrides)
    return dict(schema_version="ux-research-persona-hypotheses.v1",bundle_id=bundle_id,
                gate_bundle_input_sha256=gate_hash,authored=True,personas=[entry])


def prepare_sparse_fixture(run, *, published="2026-10-01"):
    """An owned invented voice import exercises native provenance; no real user is claimed."""
    excerpt="쿠폰 적용 조건을 다시 읽느라 첫 주문의 최종 금액을 확인하기 어려웠다."
    text="검사용 합성 문의. " + excerpt + " 이 문장은 실제 고객 경험을 담지 않는다."
    atomic(run/"sample.txt",text.encode())
    imports=read_json(run/"sanitized-imports.json");imp=imports["imports"][0]
    imp.update(source_type="community",content_sha256=byte_digest(text.encode()))
    imp["acquisition"]["kind"]="document";imp["import_id"]=merge.import_identity(imp)
    atomic(run/"sanitized-imports.json",canonical(imports))
    returned=read_json(run/"returns/editors.json");source=returned["sources"][0]
    source.update(title="검사용 합성 글",source_type="community",source_family="voice",
                  platform_family="community",published_at=published,privacy_class="ordinary",public_scope="deidentified_excerpt",
                  provenance=dict(kind="import",import_id=imp["import_id"],content_sha256=imp["content_sha256"]))
    returned["excerpts"][0].update(capture_ref=imp["import_id"],excerpt=excerpt,summary="합성 문의에 최종 금액 확인의 어려움이 기록되어 있다.",evidence_type="firsthand")
    returned["candidate_claims"][0].update(claim_kind="pain_point",statement="단일 합성 문의는 첫 주문에서 쿠폰 조건과 최종 금액을 확인하는 상황을 제시한다.",audience_values=[])
    returned["candidate_claims"][0]["subject"]["pain_point_id"]="final-cost"
    atomic(run/"returns/editors.json",canonical(returned))


class CounterSearchRounds(unittest.TestCase):
    """merge.py and the axes schema agree: discovery 0, expansion 1-2, counter_search 0-2."""

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="counter-rounds-")
        self.run=f.fixture.build(Path(self.temp.name)/"run",clock=lambda:f.CLOCK)

    def tearDown(self):self.temp.cleanup()

    def manifest(self,purpose,round_):
        doc=read_json(self.run/"axes.json")
        doc["axes"][0]["assignments"]=[dict(assignment_id="discovery-1",reader_id="reader-1",round=0,purpose="discovery"),
                                       dict(assignment_id=f"{purpose}-{round_}",reader_id="reader-1",round=round_,purpose=purpose)]
        return doc

    def test_contract(self):
        run=Run(self.run,clock=lambda:f.CLOCK)
        for purpose,round_,ok in [("counter_search",0,True),("counter_search",1,True),("counter_search",2,True),
                                  ("expansion",1,True),("expansion",2,True),
                                  ("discovery",1,False),("discovery",2,False),("expansion",0,False)]:
            with self.subTest(purpose=purpose,round=round_):
                manifest=self.manifest(purpose,round_)
                if ok:
                    merge.manifest_plan(manifest,run)  # must not raise
                else:
                    with self.assertRaises(EngineError) as caught:merge.manifest_plan(manifest,run)
                    self.assertEqual(caught.exception.issue["code"],"manifest")
        bad=self.manifest("counter_search",3)  # outside the schema's 0-2 range
        from uxresearch.schema import Resolver
        self.assertTrue(Resolver().validate(bad,"ux-research-axes.v1.schema.json"))


class PersonaExportInMemory(unittest.TestCase):
    def voice_bundle(self):
        source=f.source(1);ev=f.evidence(1,source)
        return f.bundle([source],[ev],f.claim(support=[ev["id"]],statement="A single reported checkout difficulty."))

    def export(self,bundle,doc,gate=None):
        return personas.export(bundle,gate or in_memory_gate(bundle),{"product":{"name":"diagnostic","url":"https://product.example"}},doc,"AU-diagnostic",now=NOW)

    def test_single_voice_is_exportable_when_audience_stays_empty(self):
        bundle=self.voice_bundle();gate=in_memory_gate(bundle)
        self.assertEqual(gate["claims"][0]["status"],"single_voice")
        draft=audiences.make_draft(bundle,gate,{"product":{"name":"diagnostic"}}, "AU-diagnostic",diagnostic=True)
        self.assertEqual(draft["segments"],[])  # the baseline: no composable audience
        out,issues,warnings=self.export(bundle,authored(dict(bundle_id=bundle["bundle_id"],gate_bundle_input_sha256=gate["bundle_input_sha256"]),[bundle["records"]["claims"][0]["id"]]))
        self.assertEqual(issues,[]);self.assertEqual(warnings,[])
        packet,stubs=out["packet"],out["stubs"]
        self.assertEqual(validate_bundle(packet,now=NOW),[])
        scenario=packet["records"]["scenarios"][0]
        self.assertEqual(scenario["motivation"][0]["gate_status"],"single_voice")
        self.assertEqual(scenario["epistemic_status"],"inferred");self.assertEqual(scenario["verification_status"],"unverified")
        self.assertIn("population_share",scenario["unknowns"])
        persona=packet["records"]["personas"][0]
        self.assertEqual(persona["basis"],"synthetic");self.assertEqual(persona["stop_reason"],"authored_synthetic_no_dataset")
        self.assertIn("population_share",persona["unfilled_strata"])
        self.assertEqual(len(stubs),1);self.assertEqual(stubs[0]["schema_version"],"ergo-scenario.v1")
        self.assertEqual(packet["records"]["claims"][0]["verification_status"],bundle["records"]["claims"][0]["verification_status"])

    def test_lead_only_and_supported_export_and_counter_card(self):
        s=f.source(1,published=None);e=f.evidence(1,s)
        lead=f.bundle([s],[e],f.claim(support=[e["id"]]))
        out,issues,_=self.export(lead,authored(dict(bundle_id=lead["bundle_id"],gate_bundle_input_sha256=digest(lead)),[lead["records"]["claims"][0]["id"]]))
        self.assertEqual(issues,[]);self.assertEqual(out["packet"]["records"]["scenarios"][0]["motivation"][0]["gate_status"],"lead_only")
        s2=f.source(2,"measured");e2=f.evidence(2,s2)
        supported=f.bundle([s2],[e2],f.claim(support=[e2["id"]],stakes="high"))
        claim=supported["records"]["claims"][0]
        claim["counter_search"]=dict(call_ids=["Q-0000000000000001"],read_source_ids=[],counter_evidence_ids=[],outcome="none_found",summary="No contrary diagnostic result.",resolution_id=None)
        gate=in_memory_gate(supported,query={"receipts":[dict(call_id="Q-0000000000000001",outcome="completed",phase="counter_search")]})
        out,issues,_=self.export(supported,authored(dict(bundle_id=supported["bundle_id"],gate_bundle_input_sha256=gate["bundle_input_sha256"]),[claim["id"]]),gate)
        self.assertEqual(issues,[])
        card=out["packet"]["records"]["scenarios"][0]["motivation"][0]
        self.assertEqual(card["counter_outcome"],"none_found");self.assertEqual(card["counter_summary"],"No contrary diagnostic result.")

    def test_unsafe_sources_are_refused_even_as_a_prompt(self):
        for name,mutate in [
            ("withdrawn",lambda b:b["records"]["sources"][0].update(retention_status="withdrawn")),
            ("stopped",lambda b:b["records"]["sources"][0].update(access=copy.deepcopy(STOPPED_ACCESS))),
            ("injection",lambda b:b["records"]["sources"][0].update(flags={"injection_flags":[dict(id="inj",code="instruction_override",position="body")]})),
        ]:
            with self.subTest(name=name):
                bundle=self.voice_bundle();mutate(bundle)
                source=bundle["records"]["sources"][0]
                for key in ("retention_status","access","flags"):
                    source["captures"][0]["metadata"][key]=copy.deepcopy(source[key])
                bundle["records"]["claims"][0]["statement"]="Unsafe prompt content must not reach persona authoring."
                gate=in_memory_gate(bundle)
                if name=="injection":self.assertEqual(gate["claims"][0]["status"],"unfit")
                doc=authored(dict(bundle_id=bundle["bundle_id"],gate_bundle_input_sha256=gate["bundle_input_sha256"]),[bundle["records"]["claims"][0]["id"]])
                out,issues,warnings=self.export(bundle,doc,gate)
                self.assertIsNone(out)
                self.assertTrue(any(i["code"]=="unsafe_motivation" for i in issues),issues)
                cards=personas.claim_cards(bundle,gate)
                self.assertFalse(cards[0]["exportable"]);self.assertTrue(cards[0]["blocked_reason"])
                self.assertEqual(set(cards[0]),{"claim_id","gate_status","exportable","blocked_reason"})
                self.assertNotIn("Unsafe prompt content",canonical(personas.starter(bundle,gate,{})).decode())

    def test_fabricated_refs_stale_gates_and_unauthored_starters_fail(self):
        bundle=self.voice_bundle();gate=in_memory_gate(bundle);cid=bundle["records"]["claims"][0]["id"]
        out,issues,_=self.export(bundle,authored(dict(bundle_id=bundle["bundle_id"],gate_bundle_input_sha256=gate["bundle_input_sha256"]),["CLM-deadbeef"]))
        self.assertIsNone(out);self.assertTrue(any(i["code"]=="unknown_claim" and i["location"]=="personas[0].motivation_claim_ids[0]" for i in issues))
        out,issues,_=self.export(bundle,authored(dict(bundle_id=bundle["bundle_id"],gate_bundle_input_sha256="f"*64),[cid]))
        self.assertIsNone(out);self.assertTrue(any(i["code"]=="stale_gate" for i in issues))
        starter=personas.starter(bundle,gate,{})
        self.assertEqual(starter["personas"],[]);self.assertFalse(starter["authored"])
        out,issues,_=self.export(bundle,starter)
        self.assertIsNone(out)
        self.assertTrue({i["code"] for i in issues}>={"not_authored","no_personas"})
        with self.assertRaises(EngineError) as caught:self.export(bundle,starter,in_memory_gate(bundle,mode="fixture"))
        self.assertEqual(caught.exception.issue["code"],"fixture_export")

    def test_schema_has_no_demographic_or_share_fields(self):
        bundle=self.voice_bundle();gate=in_memory_gate(bundle);cid=bundle["records"]["claims"][0]["id"]
        doc=authored(dict(bundle_id=bundle["bundle_id"],gate_bundle_input_sha256=gate["bundle_input_sha256"]),[cid])
        doc["personas"][0]["age_band"]="60대";doc["personas"][0]["region"]="서울"
        out,issues,_=self.export(bundle,doc)
        self.assertIsNone(out);self.assertTrue(any(i["code"]=="hypotheses_schema" and i["location"]=="personas[0].<key>" for i in issues),issues)

    def test_missing_task_inputs_report_specific_fields_without_inventing(self):
        bundle=self.voice_bundle();gate=in_memory_gate(bundle);cid=bundle["records"]["claims"][0]["id"]
        doc=authored(dict(bundle_id=bundle["bundle_id"],gate_bundle_input_sha256=gate["bundle_input_sha256"]),[cid])
        doc["personas"][0]["scenario"]["concrete_data"]=None;doc["personas"][0]["scenario"]["device_ids"]=[]
        out,issues,warnings=self.export(bundle,doc)
        self.assertEqual(issues,[])
        self.assertEqual(out["stubs"],[])
        self.assertEqual({w["field"] for w in warnings},{"scenarios.SC-first-cost"})
        self.assertIn("concrete_data",warnings[0]["reason"]);self.assertIn("device_ids",warnings[0]["reason"])

    def test_starter_handles_sparse_status_and_suppresses_unsafe_counter_text(self):
        for published,status in [("2026-09-01","single_voice"),(None,"lead_only")]:
            with self.subTest(status=status):
                src=f.source(1,published=published);ev=f.evidence(1,src)
                bundle=f.bundle([src],[ev],f.claim(support=[ev["id"]]))
                starter=personas.starter(bundle,in_memory_gate(bundle),{})
                self.assertEqual(starter["claim_cards"][0]["gate_status"],status)
                self.assertIsNone(starter["claim_cards"][0]["confidence"])
                self.assertTrue(starter["claim_cards"][0]["exportable"])
        bundle=self.voice_bundle();src=f.source(2,retention_status="withdrawn");ev=f.evidence(2,src)
        bundle["records"]["sources"].append(src);bundle["records"]["evidence"].append(ev)
        claim=bundle["records"]["claims"][0];claim["counter_evidence_ids"]=[ev["id"]]
        claim["counter_search"]=dict(call_ids=["Q-0000000000000002"],read_source_ids=[src["id"]],
                                    counter_evidence_ids=[ev["id"]],outcome="contradicts",summary="Withdrawn counter content.",resolution_id=None)
        gate=in_memory_gate(bundle,query={"receipts":[dict(call_id="Q-0000000000000002",outcome="completed",phase="counter_search")]})
        starter=personas.starter(bundle,gate,{})
        self.assertFalse(starter["claim_cards"][0]["exportable"])
        self.assertNotIn("Withdrawn counter content",canonical(starter).decode())
        out,issues,_=self.export(bundle,authored(starter,[claim["id"]]),gate)
        self.assertIsNone(out);self.assertTrue(any(i["code"]=="unsafe_motivation" for i in issues))

    def test_old_capture_and_evidence_injections_do_not_become_prompts(self):
        for target in ("capture","evidence"):
            with self.subTest(target=target):
                bundle=self.voice_bundle()
                value=bundle["records"]["sources"][0]["captures"][0]["metadata"] if target=="capture" else bundle["records"]["evidence"][0]
                value["flags"]["injection_flags"]=[dict(id="F-aaaaaaaaaaaaaaaa",code="instruction_override",position="body")]
                gate=in_memory_gate(bundle);self.assertEqual(gate["claims"][0]["status"],"unfit")
                cards=personas.starter(bundle,gate,{})["claim_cards"]
                self.assertEqual(set(cards[0]),{"claim_id","gate_status","exportable","blocked_reason"})
                self.assertFalse(cards[0]["exportable"])

    def test_duplicate_ids_and_missing_assumptions_fail(self):
        bundle=self.voice_bundle();gate=in_memory_gate(bundle)
        doc=authored(personas.starter(bundle,gate,{}),[bundle["records"]["claims"][0]["id"]])
        doc["personas"].append(copy.deepcopy(doc["personas"][0]))
        out,issues,_=self.export(bundle,doc)
        self.assertIsNone(out);self.assertEqual(sum(i["code"]=="duplicate_id" for i in issues),2)
        doc["personas"].pop();del doc["personas"][0]["assumptions_ko"]
        out,issues,_=self.export(bundle,doc)
        self.assertIsNone(out);self.assertTrue(any("assumptions_ko" in i["reason"] for i in issues))

    def test_high_priority_requires_declared_supported_counter_search(self):
        bundle=self.voice_bundle();gate=in_memory_gate(bundle);cid=bundle["records"]["claims"][0]["id"]
        doc=authored(personas.starter(bundle,gate,{}),[cid]);doc["personas"][0]["scenario"]["priority"]="P1"
        out,issues,_=self.export(bundle,doc)
        self.assertIsNone(out);self.assertTrue(any(i["code"]=="priority_prerequisites" for i in issues))
        src=f.source(2,"measured");ev=f.evidence(2,src)
        bundle=f.bundle([src],[ev],f.claim(support=[ev["id"]],scenario_priorities=["P1"]))
        claim=bundle["records"]["claims"][0]
        claim["counter_search"]=dict(call_ids=["Q-0000000000000001"],read_source_ids=[],counter_evidence_ids=[],
                                    outcome="none_found",summary="No contrary fixture result.",resolution_id=None)
        gate=in_memory_gate(bundle,query={"receipts":[dict(call_id="Q-0000000000000001",outcome="completed",phase="counter_search")]})
        out,issues,_=self.export(bundle,authored(personas.starter(bundle,gate,{}),[cid],scenario=dict(doc["personas"][0]["scenario"])),gate)
        self.assertEqual(issues,[]);self.assertEqual(out["packet"]["records"]["scenarios"][0]["priority"],"P1")
        gate=in_memory_gate(bundle,query={"receipts":[dict(call_id="Q-0000000000000001",outcome="failed",phase="counter_search")]})
        out,issues,_=self.export(bundle,authored(dict(bundle_id=bundle["bundle_id"],gate_bundle_input_sha256=gate["bundle_input_sha256"]),[cid]),gate)
        self.assertIsNone(out);self.assertTrue(any(i["code"]=="failed_gate" for i in issues))

    def test_sensitive_surface_urls_fail_with_safe_field_diagnostics(self):
        bundle=self.voice_bundle();gate=in_memory_gate(bundle);starter=personas.starter(bundle,gate,{})
        cid=bundle["records"]["claims"][0]["id"]
        for url in ("https://product.example/checkout?token=PRIVATE", "https://user:PRIVATE@product.example/",
                    "https://product.example/#access_token=PRIVATE", "javascript:PRIVATE"):
            with self.subTest(url_type=url.split(":",1)[0]):
                doc=authored(starter,[cid]);doc["personas"][0]["scenario"]["surface_url"]=url
                out,issues,_=self.export(bundle,doc)
                self.assertIsNone(out);self.assertTrue(any(i["code"]=="unsafe_url" and i["location"]=="personas[0].scenario.surface_url" for i in issues),issues)
                self.assertNotIn("PRIVATE",canonical(issues).decode())
        brief={"product":{"url":"https://product.example/?token=PRIVATE"}}
        with self.assertRaises(EngineError) as caught:personas.starter(bundle,gate,brief)
        self.assertEqual(caught.exception.issue["location"],"product.url")
        out,issues,_=personas.export(bundle,gate,brief,authored(starter,[cid]),"AU-test",now=NOW)
        self.assertIsNone(out);self.assertTrue(any(i["location"]=="product.url" for i in issues))

    def test_unknown_device_and_identifying_export_id_fail(self):
        bundle=self.voice_bundle();gate=in_memory_gate(bundle);cid=bundle["records"]["claims"][0]["id"]
        doc=authored(personas.starter(bundle,gate,{}),[cid])
        doc["personas"][0]["scenario"]["device_ids"]=["invented-device"]
        out,issues,_=self.export(bundle,doc)
        self.assertIsNone(out);self.assertTrue(any(i["code"]=="unknown_device" and i["location"]=="personas[0].scenario.device_ids[0]" for i in issues))
        doc["personas"][0]["scenario"]["device_ids"]=TASK_DATA["device_ids"]
        out,issues,_=personas.export(bundle,gate,{},doc,"person@example.com",now=NOW)
        self.assertIsNone(out);self.assertTrue(any(i["location"]=="audience_id" for i in issues))
        self.assertNotIn("person@example.com",canonical(issues).decode())


class PersonaExportCommand(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="persona-export-");self.root=Path(self.temp.name).resolve()
        self.clock=f.CLOCK
        self.run=f.fixture.build(self.root/"run",clock=lambda:self.clock)

    def tearDown(self):self.temp.cleanup()

    def command(self,name,*extra):
        args=[name,"--run",str(self.run)]
        if name=="merge":args+=["--manifest",str(self.run/"axes.json"),"--search-ledger",str(self.run/"search-ledger.jsonl"),"--imports",str(self.run/"sanitized-imports.json"),"--returns",str(self.run/"returns/editors.json")]
        else:args+=["--bundle",str(self.run/"bundle.json")]
        if name in {"persona-starter","export-personas","persona-intake"}:args+=["--gate",str(self.run/"gate.json")]
        if name=="export-personas":args+=["--hypotheses",str(self.run/"persona.hypotheses.json"),"--audience-id","AU-diagnostic"]
        with contextlib.redirect_stdout(io.StringIO()) as output,contextlib.redirect_stderr(io.StringIO()):
            code=main(args+list(extra),clock=lambda:self.clock)
        return code,json.loads(output.getvalue())

    def gated(self):
        code,result=self.command("merge");self.assertEqual(code,0,result)
        bundle=read_json(self.run/"bundle.json")
        bundle["records"]["sources"][0]["summary"]="An independently authored safe diagnostic source summary."
        for group in bundle["records"].values():
            for record in group:
                for key in ("summary","statement"):
                    if key in record:bundle["research"]["summary_attestations"].append(dict(record_id=record["id"],field=key,content_sha256=digest(record[key]),reviewed_by="self",reviewed_at="2026-10-01T00:00:00Z"))
        atomic(self.run/"bundle.json",canonical(bundle))
        self.assertEqual(self.command("gate","--write-bundle")[0],0)

    def test_starter_author_export_and_ergoqa_consumption(self):
        self.gated()
        code,result=self.command("persona-starter")
        self.assertEqual(code,0,result);self.assertEqual(result["files"],["persona.hypotheses.starter.json"])
        starter=read_json(self.run/"persona.hypotheses.starter.json")
        card=starter["claim_cards"][0]
        self.assertEqual(card["gate_status"],"supported_high");self.assertTrue(card["exportable"])
        self.assertTrue(any(d["field"]=="personas" for d in starter["diagnostics"]))
        doc=authored(starter,[card["claim_id"]])
        atomic(self.run/"persona.hypotheses.json",canonical(doc))
        code,result=self.command("export-personas")
        self.assertEqual(code,0,result)
        self.assertEqual([Path(p).name for p in result["files"]],["qa-personas.json","qa-personas.md","persona-export.json","SC-first-cost.json"])
        packet=read_json(result["qa_intake"]["packet"])
        self.assertEqual(validate_bundle(packet,now=NOW),[])
        self.assertEqual(packet["persona_export"]["basis"],"synthetic_exploratory")
        self.assertEqual(packet["persona_export"]["source_bundle_id"],read_json(self.run/"bundle.json")["bundle_id"])
        scenario=packet["records"]["scenarios"][-1]
        self.assertEqual(scenario["motivation_claim_ids"],[card["claim_id"]])
        self.assertEqual(scenario["motivation"][0]["gate_status"],"supported_high")
        self.assertEqual(scenario["verification_status"],"unverified")
        from ergoqa.snapshot import validate_scenario
        from ergoqa.cli import _load_scenarios
        stub=read_json(result["qa_intake"]["scenario_files"][0])
        self.assertEqual(validate_scenario(stub),[])
        self.assertIn("DIAG5000",stub["task_goal_ko"])  # provided fixture task data reaches the QA scenario
        loaded=_load_scenarios(result["qa_intake"]["scenario_files"])
        self.assertEqual(list(loaded),["SC-first-cost"])
        self.assertEqual(loaded["SC-first-cost"]["audience_ref"]["basis"],"synthetic_exploratory")
        self.assertTrue((self.run/"qa-personas.md").read_text().startswith("# 합성 페르소나 QA 시나리오"))

    def test_sparse_native_input_exports_usable_qa_without_population_segment(self):
        prepare_sparse_fixture(self.run);self.gated()
        self.assertEqual(self.command("persona-starter")[0],0)
        starter=read_json(self.run/"persona.hypotheses.starter.json")
        self.assertEqual(starter["claim_cards"][0]["gate_status"],"single_voice")
        self.assertIsNone(starter["claim_cards"][0]["confidence"])
        args=["export-audience","--run",str(self.run),"--bundle",str(self.run/"bundle.json"),"--gate",str(self.run/"gate.json"),"--audience-id","AU-diagnostic"]
        with contextlib.redirect_stdout(io.StringIO()):code=main(args,clock=lambda:self.clock)
        self.assertEqual(code,0);self.assertEqual(read_json(self.run/"audience.draft.json")["segments"],[])
        self.author_from_current_gate();code,result=self.command("export-personas");self.assertEqual(code,0,result)
        packet=read_json(self.run/"qa-personas.json");self.assertEqual(validate_bundle(packet,now=NOW),[])
        self.assertEqual(packet["records"]["scenarios"][0]["motivation"][0]["gate_status"],"single_voice")
        self.assertEqual(packet["records"]["sources"],read_json(self.run/"bundle.json")["records"]["sources"])
        from ergoqa.snapshot import validate_scenario
        from ergoqa.cli import _load_scenarios
        scenario=_load_scenarios(result["qa_intake"]["scenario_files"])["SC-first-cost"]
        self.assertEqual(validate_scenario(scenario),[]);self.assertEqual(scenario["steps"],[])
        self.assertIn("DIAG5000",scenario["task_goal_ko"])

    def test_stale_bundle_fails_and_writes_actionable_failure(self):
        self.gated()
        self.assertEqual(self.command("persona-starter")[0],0)
        starter=read_json(self.run/"persona.hypotheses.starter.json")
        doc=authored(starter,[starter["claim_cards"][0]["claim_id"]])
        atomic(self.run/"persona.hypotheses.json",canonical(doc))
        bundle=read_json(self.run/"bundle.json");bundle["research"]["gaps"].append(dict(code="coverage_note",note="changed"))
        atomic(self.run/"bundle.json",canonical(bundle))
        code,result=self.command("export-personas")
        self.assertEqual(code,2,result)
        self.assertFalse((self.run/"qa-personas.json").exists())

    def author_from_current_gate(self):
        self.assertEqual(self.command("persona-starter")[0],0)
        starter=read_json(self.run/"persona.hypotheses.starter.json")
        atomic(self.run/"persona.hypotheses.json",canonical(authored(starter,[starter["claim_cards"][0]["claim_id"]])))

    def test_authored_and_unrelated_scenario_files_are_preserved(self):
        self.gated();self.author_from_current_gate()
        folder=self.run/"qa-scenarios";folder.mkdir(mode=0o700)
        authored_path=folder/"SC-first-cost.json";atomic(authored_path,b'{"steps":["authored"]}')
        unrelated=folder/"SC-unrelated.json";atomic(unrelated,b'{"owned":"another task"}')
        code,result=self.command("export-personas")
        self.assertEqual(code,2,result);self.assertEqual(result["issues"][0]["code"],"output_conflict")
        self.assertEqual(read_bytes(authored_path),b'{"steps":["authored"]}')
        marker=read_json(self.run/"persona-export.json")
        self.assertEqual(marker["result"],"fail")  # a failed latest export blocks intake; recovery keeps the authored file
        authored_path.unlink();self.assertEqual(self.command("export-personas")[0],0)
        stub=read_json(authored_path);stub["steps"]=[dict(action="click",selector="#approved-fixture")]
        atomic(authored_path,canonical(stub));before=read_bytes(authored_path)
        self.assertEqual(self.command("persona-starter")[0],0)  # a later publish must not remirror a generated original
        self.assertEqual(read_bytes(authored_path),before)
        code,result=self.command("export-personas");self.assertEqual(code,2,result)
        self.assertEqual(read_bytes(authored_path),before)
        self.assertEqual(read_bytes(unrelated),b'{"owned":"another task"}')
        self.assertEqual(self.command("merge")[0],0)
        self.assertEqual(read_bytes(authored_path),before);self.assertTrue(unrelated.exists())
        with Store(self.run) as store:self.assertFalse(store.has("qa-scenarios/SC-first-cost.json"))

    def test_generated_scenarios_are_committed_and_obsolete_ones_removed(self):
        self.gated();self.author_from_current_gate();self.assertEqual(self.command("export-personas")[0],0)
        with Store(self.run) as store:
            self.assertEqual(store.committed("qa-scenarios/SC-first-cost.json"),read_json(self.run/"qa-scenarios/SC-first-cost.json"))
        doc=read_json(self.run/"persona.hypotheses.json");doc["personas"][0]["scenario"]["scenario_id"]="SC-new-condition"
        atomic(self.run/"persona.hypotheses.json",canonical(doc));self.assertEqual(self.command("export-personas")[0],0)
        self.assertFalse((self.run/"qa-scenarios/SC-first-cost.json").exists())
        self.assertTrue((self.run/"qa-scenarios/SC-new-condition.json").exists())
        self.assertEqual(self.command("merge")[0],0)
        self.assertFalse((self.run/"qa-scenarios/SC-new-condition.json").exists())
        for name in ("qa-personas.json","qa-personas.md","persona-export.json","persona.hypotheses.starter.json"):
            self.assertFalse((self.run/name).exists(),name)

    def test_failed_export_marks_latest_and_blocks_intake_until_corrected_export(self):
        self.gated();self.author_from_current_gate();self.assertEqual(self.command("export-personas")[0],0)
        with Store(self.run) as store:
            generation=store.state()["generation_id"];packet=store.committed("qa-personas.json")
        hypotheses=self.run/"persona.hypotheses.json";authored_bytes=read_bytes(hypotheses)
        atomic(hypotheses,b'{"persona file": not valid json')  # malformed authored input
        code,result=self.command("export-personas");self.assertEqual(code,2,result)
        self.assertEqual(result["issues"][0]["code"],"invalid_json")
        marker=read_json(self.run/"persona-export.json")
        self.assertEqual((marker["result"],marker["exit_code"]),("fail",2))
        self.assertNotIn("not valid json",canonical(marker).decode())  # no raw input in the marker
        code,result=self.command("persona-intake");self.assertEqual(code,2,result)
        self.assertEqual(result["issues"][0]["code"],"failed_export")
        hypotheses.unlink()  # a missing authored input is a marked failed export too
        code,result=self.command("export-personas");self.assertEqual(code,2,result)
        self.assertEqual(result["issues"][0]["code"],"io")
        code,result=self.command("persona-intake");self.assertEqual(code,2,result)
        self.assertEqual(result["issues"][0]["code"],"failed_export")
        with Store(self.run) as store:  # the last committed snapshot and generation wait intact for recovery
            self.assertEqual(store.state()["generation_id"],generation)
            self.assertEqual(store.committed("qa-personas.json"),packet)
        atomic(hypotheses,authored_bytes)  # the corrected export unblocks intake
        code,result=self.command("export-personas");self.assertEqual(code,0,result)
        code,result=self.command("persona-intake");self.assertEqual(code,0,result)
        self.assertEqual(validate_bundle(read_json(result["qa_intake"]["packet"]),now=NOW),[])

    def test_staging_crash_never_publishes_a_partial_export(self):
        self.gated();self.author_from_current_gate()
        def fault(stage):
            if stage=="before_manifest":raise RuntimeError("fixture crash")
        def factory(root,timeout):return Store(root,timeout,fault=fault)
        with Store(self.run) as store:before=store.state()["generation_id"]
        with patch("uxresearch.commands.Store",side_effect=factory):
            with self.assertRaises(RuntimeError):self.command("export-personas")
        with Store(self.run) as store:
            self.assertEqual(store.state()["generation_id"],before)
            self.assertFalse(store.has("persona-export.json"))
        self.assertFalse((self.run/"persona-export.json").exists())
        self.assertFalse((self.run/"qa-scenarios/SC-first-cost.json").exists())

    def test_public_intake_after_manifest_crash_uses_current_coherent_generation(self):
        self.gated();self.author_from_current_gate();self.assertEqual(self.command("export-personas")[0],0)
        old=read_json(self.run/"qa-scenarios/SC-first-cost.json")
        old_marker=read_json(self.run/"persona-export.json")
        doc=read_json(self.run/"persona.hypotheses.json")
        goal="중단 후 쿠폰 조건과 최종 금액을 다시 확인한다"
        doc["personas"][0]["scenario"]["task_goal_ko"]=goal
        atomic(self.run/"persona.hypotheses.json",canonical(doc))
        def fault(stage):
            if stage=="after_manifest":raise RuntimeError("fixture crash after commit")
        def factory(root,timeout):return Store(root,timeout,fault=fault)
        with patch("uxresearch.commands.Store",side_effect=factory):
            with self.assertRaises(RuntimeError):self.command("export-personas")
        self.assertEqual(read_json(self.run/"qa-scenarios/SC-first-cost.json"),old)
        self.assertEqual(read_json(self.run/"persona-export.json"),old_marker)
        code,result=self.command("persona-intake");self.assertEqual(code,0,result)
        from ergoqa.cli import _load_scenarios
        from ergoqa.snapshot import validate_scenario
        packet=read_json(result["qa_intake"]["packet"])
        loaded=_load_scenarios(result["qa_intake"]["scenario_files"])["SC-first-cost"]
        self.assertEqual(validate_scenario(loaded),[])
        self.assertTrue(loaded["task_goal_ko"].startswith(goal));self.assertNotEqual(loaded["task_goal_ko"],old["task_goal_ko"])
        self.assertEqual(packet["records"]["scenarios"][0]["task"],goal)
        self.assertEqual(Path(result["qa_intake"]["scenario_files"][0]).parents[1],Path(result["qa_intake"]["packet"]).parent)
        with Store(self.run) as store:self.assertEqual(store.committed("qa-personas.json"),packet)

    def test_closed_run_keeps_valid_intake_and_changed_inputs_refuse_it(self):
        self.gated();self.author_from_current_gate();self.assertEqual(self.command("export-personas")[0],0)
        with contextlib.redirect_stdout(io.StringIO()):code=main(["close","--run",str(self.run)],clock=lambda:self.clock)
        self.assertEqual(code,0)
        code,result=self.command("persona-intake");self.assertEqual(code,0,result)
        self.assertEqual(validate_bundle(read_json(result["qa_intake"]["packet"]),now=NOW),[])
        bundle=read_json(self.run/"bundle.json");bundle["research"]["gaps"].append(dict(code="coverage_note",note="changed after closing"))
        atomic(self.run/"bundle.json",canonical(bundle))
        code,result=self.command("persona-intake");self.assertEqual(code,2,result)
        self.assertEqual(result["issues"][0]["code"],"stale_gate")

    def test_retention_purge_removes_generated_persona_content_and_snapshots(self):
        deadline="2026-10-01T00:00:01Z"
        for name,key in (("returns/editors.json","sources"),("sanitized-imports.json","imports")):
            doc=read_json(self.run/name);doc[key][0]["retention_until"]=deadline;atomic(self.run/name,canonical(doc))
        self.gated();self.author_from_current_gate();self.assertEqual(self.command("export-personas")[0],0)
        self.clock=f.CLOCK+1
        self.assertEqual(self.command("gate","--write-bundle")[0],0)
        for name in ("qa-personas.json","qa-personas.md","persona-export.json","persona.hypotheses.starter.json","qa-scenarios/SC-first-cost.json"):
            self.assertFalse((self.run/name).exists(),name)
            with Store(self.run) as store:self.assertFalse(store.has(name),name)
        for path in (self.run/".engine").rglob("*"):
            if path.is_file():self.assertNotIn(b"DIAG5000",read_bytes(path))

    def test_regating_changed_inputs_invalidates_export(self):
        self.gated();self.author_from_current_gate();self.assertEqual(self.command("export-personas")[0],0)
        bundle=read_json(self.run/"bundle.json");bundle["research"]["gaps"].append(dict(code="coverage_note",note="A changed uncertainty"))
        atomic(self.run/"bundle.json",canonical(bundle));self.assertEqual(self.command("gate")[0],0)
        self.assertFalse((self.run/"qa-personas.json").exists())
        self.assertFalse((self.run/"qa-scenarios/SC-first-cost.json").exists())


if __name__=="__main__":unittest.main()
