from __future__ import annotations
import contextlib,io,json,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
import _paths
import engine_release_factory as f
from uxresearch import ledger,merge
from uxresearch.canonical import canonical,loads
from uxresearch.cli import main
from uxresearch.ledger import Run
from uxresearch.storage import atomic,read_bytes,read_json

FIXTURES=Path(__file__).parent/"fixtures/research"


def virgin_run(root):
    brief=dict(schema_version="ux-research-brief.v1",product=dict(name="Example checkout",surface="web",url="https://product.example",locale="en",category="commerce",release_date="2026-09-01",current_version="1"),audience_questions=["segments"],budgets=dict(per_run=200,per_host=30,search_queries=12))
    routes=json.loads((f.SKILL/"uxresearch/data/routes.json").read_text())
    path=ledger.create(Path(root)/"run",ledger.build_policy(brief,{}),brief=brief,routes=routes,routes_source="packaged",clock=lambda:f.CLOCK)
    return path


def draft_manifest(run_id,*,rounds=None,axis_id="product",questions=("segments",),excluded=False):
    assignments=[dict(assignment_id="discovery-1",reader_id="reader-1",round=0,purpose="discovery")]
    for r in rounds or []:
        assignments.append(dict(assignment_id=f"counter-{r}",reader_id="reader-1",round=r,purpose="counter_search"))
    return dict(schema_version="ux-research-axes.v1",run_id=run_id,
                axes=[dict(axis_id=axis_id,audience_questions=list(questions),excluded=excluded,reason="excluded by plan" if excluded else None,assignments=[] if excluded else assignments)],
                segments=[dict(segment_id="operators",priority="secondary",decision_ref="owner-diagnostic",summary="An illustrative segment.")],
                question_gaps=[])


class PlanCommand(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="research-plan-");self.root=Path(self.temp.name).resolve()
        self.run=virgin_run(self.root);self.rid=Run(self.run,clock=lambda:f.CLOCK).meta["run_id"]

    def tearDown(self):self.temp.cleanup()

    def command(self,*extra):
        args=["plan","--run",str(self.run),"--manifest",str(self.run/"plan.draft.json")]+list(extra)
        with contextlib.redirect_stdout(io.StringIO()) as output,contextlib.redirect_stderr(io.StringIO()):
            code=main(args,clock=lambda:f.CLOCK)
        return code,json.loads(output.getvalue())

    def write_draft(self,manifest):atomic(self.run/"plan.draft.json",canonical(manifest))

    def test_creates_companions_together_and_is_idempotent(self):
        self.write_draft(draft_manifest(self.rid))
        code,result=self.command()
        self.assertEqual(code,0,result)
        self.assertEqual(result["files"],["axes.json","axis-acknowledgements.json","search-ledger.jsonl"])
        manifest=read_json(self.run/"axes.json");self.assertEqual(manifest["run_id"],self.rid)
        ack=read_json(self.run/"axis-acknowledgements.json");self.assertEqual(ack["entries"],[])
        self.assertEqual(read_bytes(self.run/"search-ledger.jsonl"),b"")
        before=(read_bytes(self.run/"axes.json"),read_bytes(self.run/"axis-acknowledgements.json"))
        code,result=self.command()
        self.assertEqual(code,0,result);self.assertTrue(any("unchanged" in w for w in result["warnings"]))
        self.assertEqual((read_bytes(self.run/"axes.json"),read_bytes(self.run/"axis-acknowledgements.json")),before)

    def test_malformed_fields_get_actionable_paths(self):
        bad=draft_manifest(self.rid);bad["axes"][0]["assignments"][0]["round"]=5;bad["axes"][0]["assignments"][0]["purpose"]="expansion"
        self.write_draft(bad)
        code,result=self.command()
        self.assertEqual(code,2,result)
        self.assertTrue(any(i["location"]=="axes[0].assignments[0].round" for i in result["issues"]),result["issues"])
        self.assertFalse((self.run/"axes.json").exists())
        missing=draft_manifest(self.rid);del missing["axes"][0]["assignments"][0]["purpose"]
        self.write_draft(missing)
        code,result=self.command()
        self.assertEqual(code,2,result)
        self.assertTrue(any(i["location"]=="axes[0].assignments[0]" and "purpose" in i["reason"] for i in result["issues"]),result["issues"])
        atomic(self.run/"plan.draft.json",b"{not json")
        code,result=self.command()
        self.assertEqual(code,2,result);self.assertEqual(result["issues"][0]["location"],"manifest")

    def test_semantic_failures_name_the_field(self):
        for mutate,path in [
            (lambda m:m.update(run_id="run-other"),"run_id"),
            (lambda m:m["axes"][0]["assignments"].clear(),"axes[0].assignments"),
            (lambda m:m["axes"].append(dict(axis_id=m["axes"][0]["axis_id"],audience_questions=["segments"],excluded=False,reason=None,assignments=[dict(assignment_id="d2",reader_id="r",round=0,purpose="discovery")])),"axes[1].axis_id"),
            (lambda m:m["axes"][0]["assignments"].append(dict(assignment_id="e1",reader_id="r",round=0,purpose="expansion")),"axes[0].assignments[1].round"),
            (lambda m:m["question_gaps"].append(dict(question="weight",reason="no data",acknowledged_by="agent",acknowledged_at="2026-10-01T00:00:00Z")),"question_gaps"),
        ]:
            with self.subTest(path=path):
                for name in ("axes.json","axis-acknowledgements.json","search-ledger.jsonl"):
                    target=self.run/name
                    if target.exists():target.unlink()
                bad=draft_manifest(self.rid);mutate(bad);self.write_draft(bad)
                code,result=self.command()
                self.assertEqual(code,2,result)
                self.assertTrue(any(i["location"]==path for i in result["issues"]),result["issues"])
                self.assertFalse((self.run/"axes.json").exists())

    def test_conflicting_plan_is_preserved(self):
        self.write_draft(draft_manifest(self.rid));self.assertEqual(self.command()[0],0)
        good=read_bytes(self.run/"axes.json")
        other=draft_manifest(self.rid);other["segments"][0]["segment_id"]="operators-b"
        self.write_draft(other)
        code,result=self.command()
        self.assertEqual(code,2,result);self.assertEqual(result["issues"][0]["code"],"plan_conflict")
        self.assertEqual(read_bytes(self.run/"axes.json"),good)

    def test_nonempty_search_ledger_is_preserved(self):
        self.write_draft(draft_manifest(self.rid));self.assertEqual(self.command()[0],0)
        receipt=canonical(dict(call_id="Q-0000000000000001",tool="t",called_at="2026-10-01T00:00:00Z",phase="discovery",queries=[dict(q="q",lang="en")],results_n=1,outcome="completed",assignment_id="discovery-1"))+b"\n"
        atomic(self.run/"search-ledger.jsonl",receipt)
        code,result=self.command()  # same plan rerun: idempotent, ledger untouched
        self.assertEqual(code,0,result);self.assertEqual(read_bytes(self.run/"search-ledger.jsonl"),receipt)
        other=draft_manifest(self.rid);other["axes"][0]["assignments"].append(dict(assignment_id="counter-1",reader_id="r",round=1,purpose="counter_search"))
        self.write_draft(other)
        code,result=self.command()
        self.assertEqual(code,2,result)
        self.assertEqual(read_bytes(self.run/"search-ledger.jsonl"),receipt);self.assertNotEqual(read_bytes(self.run/"axes.json"),canonical(other))

    def test_searches_before_plan_are_refused(self):
        atomic(self.run/"search-ledger.jsonl",canonical(dict(call_id="Q-0000000000000001",tool="t",called_at="2026-10-01T00:00:00Z",phase="discovery",queries=[dict(q="q",lang="en")],results_n=1,outcome="completed",assignment_id="discovery-1"))+b"\n")
        self.write_draft(draft_manifest(self.rid))
        code,result=self.command()
        self.assertEqual(code,2,result);self.assertEqual(result["issues"][0]["code"],"search_ledger_not_empty")
        self.assertFalse((self.run/"axes.json").exists())

    def test_acknowledgements_are_validated_and_created(self):
        bad=dict(schema_version="ux-axis-acknowledgements.v1",run_id=self.rid,entries=[dict(kind="partial",axis_id="product",assignment_id="missing-1",reason="gap",acknowledged_by="agent",acknowledged_at="2026-10-01T00:00:00Z")])
        atomic(self.run/"acks.json",canonical(bad));self.write_draft(draft_manifest(self.rid))
        code,result=self.command("--acknowledgements",str(self.run/"acks.json"))
        self.assertEqual(code,2,result);self.assertTrue(any(i["location"]=="entries[0].assignment_id" for i in result["issues"]),result["issues"])
        good=dict(bad,entries=[dict(kind="partial",axis_id="product",assignment_id="discovery-1",reason="known gap",acknowledged_by="agent",acknowledged_at="2026-10-01T00:00:00Z")])
        atomic(self.run/"acks.json",canonical(good))
        code,result=self.command("--acknowledgements",str(self.run/"acks.json"))
        self.assertEqual(code,0,result)
        self.assertEqual(read_json(self.run/"axis-acknowledgements.json")["entries"],good["entries"])

    def test_plan_output_is_a_valid_merge_manifest(self):
        self.write_draft(draft_manifest(self.rid,rounds=(1,2)))
        code,result=self.command();self.assertEqual(code,0,result)
        run=Run(self.run,clock=lambda:f.CLOCK)
        axes,assignments=merge.manifest_plan(read_json(self.run/"axes.json"),run)
        self.assertEqual({a["purpose"] for _,a in assignments.values()},{"discovery","counter_search"})
        self.assertEqual(sorted(a["round"] for _,a in assignments.values() if a["purpose"]=="counter_search"),[1,2])

    def test_omitted_acknowledgements_still_validate_existing_records(self):
        self.write_draft(draft_manifest(self.rid))
        bad=dict(schema_version="ux-axis-acknowledgements.v1",run_id="another-run",entries=[])
        for bad_doc,path in [(bad,"run_id"),
                             (dict(bad,run_id=self.rid,entries=[dict(kind="partial",axis_id="product",assignment_id="missing",reason="gap",acknowledged_by="agent",acknowledged_at="2026-10-01T00:00:00Z")]),"entries[0].assignment_id"),
                             ({"schema_version":"bad","run_id":self.rid,"entries":[]},"acknowledgements.schema_version")]:
            with self.subTest(path=path):
                atomic(self.run/"axis-acknowledgements.json",canonical(bad_doc))
                before=read_bytes(self.run/"axis-acknowledgements.json")
                code,result=self.command()
                self.assertEqual(code,2,result);self.assertTrue(any(i["location"]==path for i in result["issues"]),result["issues"])
                self.assertEqual(read_bytes(self.run/"axis-acknowledgements.json"),before)
                self.assertFalse((self.run/"axes.json").exists());self.assertFalse((self.run/"search-ledger.jsonl").exists())

    def test_existing_ack_conflict_is_preserved_before_any_search(self):
        self.write_draft(draft_manifest(self.rid));self.assertEqual(self.command()[0],0)
        before=read_bytes(self.run/"axis-acknowledgements.json")
        different=dict(schema_version="ux-axis-acknowledgements.v1",run_id=self.rid,entries=[dict(kind="partial",axis_id="product",assignment_id="discovery-1",reason="a new gap",acknowledged_by="agent",acknowledged_at="2026-10-01T00:00:00Z")])
        atomic(self.run/"acks.json",canonical(different))
        code,result=self.command("--acknowledgements",str(self.run/"acks.json"))
        self.assertEqual(code,2,result);self.assertEqual(result["issues"][0]["code"],"plan_conflict")
        self.assertEqual(read_bytes(self.run/"axis-acknowledgements.json"),before)
        self.assertEqual(read_json(self.run/"acks.json"),different)
        # JSON formatting does not turn an identical plan into a conflict.
        atomic(self.run/"axes.json",json.dumps(read_json(self.run/"axes.json"),indent=2).encode())
        self.assertEqual(self.command()[0],0)

    def test_write_failure_rolls_back_only_new_companions(self):
        self.write_draft(draft_manifest(self.rid))
        def failing_write(path,raw):
            if path.name=="axis-acknowledgements.json":raise OSError("fixture disk failure")
            atomic(path,raw)
        with patch("uxresearch.planning.atomic",side_effect=failing_write):code,result=self.command()
        self.assertEqual(code,2,result);self.assertEqual(result["issues"][0]["code"],"plan_write")
        for name in ("axes.json","axis-acknowledgements.json","search-ledger.jsonl"):
            self.assertFalse((self.run/name).exists(),name)
        self.assertTrue((self.run/"plan.draft.json").exists())


if __name__=="__main__":unittest.main()
