from __future__ import annotations
import contextlib,copy,fcntl,importlib.util,io,json,os,subprocess,sys,tempfile,time,unittest
from datetime import datetime,timezone
from pathlib import Path
from unittest.mock import patch
import engine_release_factory as f
from uxresearch import audiences,engine,grading,merge,minimize,reports,schema
from uxresearch.canonical import EngineError,Ids,byte_digest,canonical,claim_identity,digest,loads,resource_url,timestamp
from uxresearch.cli import main
from uxresearch.flags import captured,empty
from uxresearch.ledger import Run
from uxresearch.storage import Store,atomic,read_json
from scripts.validate_bundle import validate_bundle,validate_receipts,bundle_warnings


class GradingBoundaries(unittest.TestCase):
    def test_status_table(self):
        cases=[('empty',[],'lead_only',0),('A',[('measured','product_analytics',True)],'supported_high',1),('B',[('voice','community',True)],'single_voice',1),('two B same',[('voice','community',True),('voice','community',True)],'supported_medium',2),('two B distinct',[('voice','community',True),('voice','app_store_reviews',True)],'supported_high',2),('all E',[('none','synthetic',True)],'unfit',0),('E D',[('none','synthetic',True),('expert_judgment','expert_judgment',True)],'lead_only',0),('unknown',[('voice','community',False)],'lead_only',0)]
        for name,items,status,units in cases:
            with self.subTest(name=name):
                ss=[f.source(i+1,fam,ch,author=author) for i,(fam,ch,author) in enumerate(items)];ev=[f.evidence(i+1,s) for i,s in enumerate(ss)];b=f.bundle(ss,ev,f.claim(support=[e['id'] for e in ev]));rows,issues,_=f.grade(b)
                self.assertEqual((rows[0]['status'],len(rows[0]['units'])),(status,units));self.assertEqual(issues,[])
                self.assertEqual(set(rows[0]['counting_evidence_ids'])|set(rows[0]['context_evidence_ids']),{e['id'] for e in ev})
    def test_statistical_organizations_copies_and_undated(self):
        for count,same_org,same_quote,status,units in [(1,False,False,'supported_medium',1),(2,True,False,'supported_medium',1),(2,False,False,'supported_high',2),(2,False,True,'supported_medium',1)]:
            with self.subTest(count=count,same_org=same_org,same_quote=same_quote):
                ss=[f.source(i+1,'statistical',org='same' if same_org else 'org-'+str(i)) for i in range(count)];es=[f.evidence(i+1,s,text='Exact copy.' if same_quote else 'Different item '+str(i)) for i,s in enumerate(ss)]
                for s,e in zip(ss,es):f.statistical(s,e)
                rows,issues,_=f.grade(f.bundle(ss,es,f.claim(support=[e['id'] for e in es])));self.assertEqual((rows[0]['status'],len(rows[0]['units'])),(status,units));self.assertEqual(issues,[])
        ss=[f.source(i+1,published=None) for i in range(2)];es=[f.evidence(i+1,s) for i,s in enumerate(ss)];rows,_,_=f.grade(f.bundle(ss,es,f.claim(support=[e['id'] for e in es])));self.assertEqual(rows[0]['status'],'lead_only');self.assertEqual({g['final_grade'] for g in rows[0]['grades']},{'C'})
    def test_b_plus_c_channel_rule_and_lone_institution(self):
        for channel,status in [('community','single_voice'),('news','supported_medium')]:
            a=f.source(1);b=f.source(2, 'voice' if channel=='community' else 'secondary',channel,published=None if channel=='community' else '2026-09-01');es=[f.evidence(1,a),f.evidence(2,b)];rows,_,_=f.grade(f.bundle([a,b],es,f.claim(support=[e['id'] for e in es])));self.assertEqual(rows[0]['status'],status)
        s=f.source(1,'measured',published=None);e=f.evidence(1,s);rows,_,_=f.grade(f.bundle([s],[e],f.claim(support=[e['id']])));self.assertEqual(rows[0]['status'],'lead_only')
    def test_conflict_currency_precedence(self):
        for contrary,current,matching,status in [(False,False,False,'supported_high'),(True,False,False,'conflicting'),(False,True,False,'stale'),(True,True,False,'conflicting'),(False,True,True,'supported_high')]:
            s=f.source(1,'measured',version='v1' if matching else 'v0');e=f.evidence(1,s);c=f.evidence(2,s);rows,_,_=f.grade(f.bundle([s],[e,c],f.claim(support=[e['id']],counter=[c['id']] if contrary else [],about_current_version=current)));self.assertEqual(rows[0]['status'],status)
    def test_observations_and_missing_release(self):
        for completed,observed,status in [(False,True,'needs_product_check'),(True,False,'needs_product_check'),(True,True,'supported_high')]:
            b=f.bundle([],[],f.claim('product_behavior'));f.observation(b,completed=completed,observed=observed);rows,_,_=f.grade(b);self.assertEqual(rows[0]['status'],status);self.assertIsNone(rows[0]['best_grade'])
        b=f.bundle([],[],f.claim('product_behavior',about_current_version=True));f.observation(b);rows,issues,_=f.grade(b,{'product':{'url':'https://product.example','current_version':'v1'}});self.assertEqual(rows[0]['status'],'stale');self.assertIn('release_date_required',{x['code'] for x in issues})
    def test_counter_triggers_and_completed_none_found(self):
        for trigger in ('primary','high','P0','P1'):
            s=f.source(1,'measured');e=f.evidence(1,s);c=f.claim(support=[e['id']]);b=f.bundle([s],[e],c)
            if trigger=='primary':b['research']['manifest']['segments'][0]['priority']='primary'
            elif trigger=='high':c['stakes']='high'
            else:c['scenario_priorities']=[trigger]
            rows,issues,_=f.grade(b);self.assertTrue(rows[0]['counter_search_required']);self.assertIn('counter_required',{x['code'] for x in issues})
            c['counter_search']=dict(call_ids=['Q-1'],read_source_ids=[],counter_evidence_ids=[],outcome='none_found',summary='No contrary diagnostic result.',resolution_id=None)
            query={'receipts':[dict(call_id='Q-1',outcome='completed',phase='counter_search')]};rows,issues,_=f.grade(b,query=query);self.assertEqual(issues,[])
    def test_numeric_printed_values_and_bounds(self):
        s=f.source(1,'measured');d=f.denominator();e=f.evidence(1,s,text='The measured share is 20%.',denominator=d,scope=f.scope(**{k:d[k] for k in ('population','period_start','period_end','product_relation')}));c=f.claim('segment_share',support=[e['id']]);c['audience_values']=[dict(join=dict(segment_id='seg',entity_kind='segment',entity_id='seg',field='share'),value=0.2,denominator_evidence_ids=[e['id']],value_checks=[dict(pointer='',evidence_id=e['id'],value_as_printed='20%',conversion='percent_to_fraction',numerator_as_printed=None,denominator_as_printed=None)])]
        b=f.bundle([s],[e],c);rows,issues,_=f.grade(b);self.assertEqual(rows[0]['export_values'][0]['value'],0.2);self.assertIn('counter_required',{i['code'] for i in issues})
        for mutate in (lambda b:b['records']['claims'][0]['audience_values'][0].update(value=.8),lambda b:b['records']['evidence'][0]['denominator'].update(sampling_frame='review count'),lambda b:b['records']['evidence'][0]['denominator'].update(period_end='2027-01-01'),lambda b:b['records']['claims'][0]['audience_values'][0].update(value_checks=[])):
            bad=copy.deepcopy(b);mutate(bad)
            with self.assertRaises(EngineError):f.grade(bad)
        bound=copy.deepcopy(b);bound['records']['evidence'][0]['denominator'].update(product_relation='general_population',interpretation='population_bound');bound['records']['evidence'][0]['scope']['product_relation']='general_population';rows,_,_=f.grade(bound);self.assertIn('population_bound',rows[0]['export_values'][0]['reason_codes'])
    def test_search_eighty_percent_exact_budget_and_over(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=f.fixture.build(Path(tmp)/"run",clock=lambda:f.CLOCK);run=Run(root,clock=lambda:f.CLOCK);ret=read_json(root/"returns/editors.json");manifest=read_json(root/"axes.json");_,assignments=merge.manifest_plan(manifest,run);run.policy["search_queries"]=5
            for n in (4,5,6):
                calls=[]
                for i in range(n):
                    call=copy.deepcopy(ret["queries_run"][0]);call["call_id"]="Q-"+format(i+1,"016x");call["outcome"]="failed" if i==0 else "completed";calls.append(call)
                returned=copy.deepcopy(ret);returned.update(queries_run=calls,search_count=n);returned["budget_used"]["searches"]=n;issues=[]
                query=merge.reconcile([returned],calls,assignments,{"entries":[]},run,[],{"hosts":{},"run":{"docs":0,"policy_requests":0}},issues)
                self.assertEqual(query["total_invocations"],n);self.assertEqual(bool(issues),n>5);self.assertTrue(query["warnings"]);self.assertEqual(len(query["duplicate_queries"]),1)

    def test_person_and_resource_excerpt_caps(self):
        for n,over in ((5,False),(6,True)):
            source=f.source(1);evs=[f.evidence(i+1,source) for i in range(n)];issues=[];grading.validate_caps(f.bundle([source],evs,f.claim()),issues);self.assertEqual(bool(issues),over)
        for n,over in ((3,False),(4,True)):
            sources=[f.source(i+1) for i in range(n)]
            for source in sources:source["author_key"]="a"*16;source["captures"][0]["metadata"]["author_key"]="a"*16
            evs=[f.evidence(i+1,source) for i,source in enumerate(sources)];issues=[];grading.validate_caps(f.bundle(sources,evs,f.claim()),issues);self.assertEqual(bool(issues),over)

    def test_voice_numeric_never_counting(self):
        a=f.source(1);b=f.source(2,'measured');es=[f.evidence(1,a),f.evidence(2,b)];c=f.claim('segment_share',support=[e['id'] for e in es])
        with self.assertRaises(EngineError) as caught:f.grade(f.bundle([a,b],es,c))
        self.assertEqual(caught.exception.issue['code'],'voice_numeric')
    def test_incentive_pain_caps_and_exact_clearance(self):
        for publication,secondhand,wanted in [('2026-09-01',False,'C'),(None,False,'C'),(None,True,'D')]:
            s=f.source(1,published=publication,flags={'secondhand':secondhand});e=f.evidence(1,s,flags={'incentive_hits':[dict(id='inc',code='seller_event',position='body')]});c=f.claim('pain_point',support=[e['id']]);b=f.bundle([s],[e],c)
            decision=dict(id='D-1',kind='incentive',target_kind='evidence',target_id=e['id'],capture_ref=e['capture_ref'],target_sha256='',flag_ids=['inc'],reviewer_ref='reviewer',checked_at='2026-09-20T00:00:00Z',outcome='confirmed',basis_evidence_ids=[e['id']],reason='Event trace reviewed.')
            decision['target_sha256']=grading.target_hash(decision,b,f.receipt(b));b['research']['verifier_decisions']=[decision]
            rows,issues,_=f.grade(b);self.assertEqual(rows[0]['grades'][0]['final_grade'],wanted);self.assertEqual(issues,[])
        s=f.source(1,flags={'injection_flags':[dict(id='inj',code='instruction_override',position='body')]});e=f.evidence(1,s);b=f.bundle([s],[e],f.claim(support=[e['id']]));rows,_,_=f.grade(b);self.assertEqual(rows[0]['grades'][0]['final_grade'],'E')
        d=dict(id='D-clear',kind='injection',target_kind='source',target_id=s['id'],capture_ref=e['capture_ref'],target_sha256='',flag_ids=['inj'],reviewer_ref='reviewer',checked_at='2026-09-20T00:00:00Z',outcome='cleared',basis_evidence_ids=[],reason='Reviewed.');d['target_sha256']=grading.target_hash(d,b,f.receipt(b));b['research']['verifier_decisions']=[d];rows,_,_=f.grade(b);self.assertEqual(rows[0]['status'],'single_voice')
        s['captures'][0]['metadata']['title']='New capture data'
        with self.assertRaises(EngineError):f.grade(b)
    def test_page_identity_and_scope_cycles(self):
        s=f.source(1,author=False);s['identity_status']='unknown';e=f.evidence(1,s);rows,_,_=f.grade(f.bundle([s],[e],f.claim(support=[e['id']])));self.assertEqual(rows[0]['status'],'single_voice')
        b=f.bundle([],[],f.claim('product_behavior'));f.observation(b);b['records']['scenarios'][0]['motivation_claim_ids']=['CLM-11111111'];self.assertEqual(f.grade(b)[0][0]['status'],'supported_high')
        b['research']['scope_resolutions']=[dict(kind='scope_change',claim_id='a',prior_claim_id='b'),dict(kind='scope_change',claim_id='b',prior_claim_id='a')]
        with self.assertRaises(EngineError):grading.scope_cycles(b)
    def test_task_amount_exact_observation_proof(self):
        b=f.bundle([],[],f.claim('product_behavior'));f.observation(b);c=b['records']['claims'][0];c['subject']['task_id']='lookup';b['records']['scenarios'][0]['task_id']='lookup';join=dict(segment_id='seg',entity_kind='task',entity_id='lookup',field='concrete_data');value=dict(amount=25000,duration=42)
        c['audience_values']=[dict(join=join,value=value,denominator_evidence_ids=[],value_checks=[])];b['records']['observations'][0]['product_values']=[dict(join=join,value=value)];rows,_,_=f.grade(b);self.assertTrue(rows[0]['export_values'][0]['eligible'])
        b['records']['observations'][0]['product_values'][0]['value']={'amount':20000}
        with self.assertRaises(EngineError):f.grade(b)


class CommandAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='research-release-');self.root=Path(self.temp.name).resolve();self.run=f.fixture.build(self.root/'run',clock=lambda:f.CLOCK)
    def tearDown(self):self.temp.cleanup()
    def load(self,name):return read_json(self.run/name)
    def write(self,name,value):atomic(self.run/name,value if isinstance(value,bytes) else json.dumps(value,ensure_ascii=False).encode() if name=="run.json" else canonical(value))
    def command(self,name,*extra):
        args=[name,'--run',str(self.run)]
        if name=='merge':args+=['--manifest',str(self.run/'axes.json'),'--search-ledger',str(self.run/'search-ledger.jsonl'),'--imports',str(self.run/'sanitized-imports.json'),'--returns',str(self.run/'returns/editors.json')]
        else:args+=['--bundle',str(self.run/'bundle.json')]
        if name in {'report-check','export-audience','minimize'}:args+=['--gate',str(self.run/'gate.json')]
        if name=='export-audience':args+=['--audience-id','AU-diagnostic']
        with contextlib.redirect_stdout(io.StringIO()) as output,contextlib.redirect_stderr(io.StringIO()):code=main(args+list(extra),clock=lambda:getattr(self,'clock',f.CLOCK))
        return code,json.loads(output.getvalue())
    def merged(self):self.assertEqual(self.command('merge')[0],0)
    def attest(self):
        bundle=self.load('bundle.json');bundle['records']['sources'][0]['summary']='An independently authored safe diagnostic source summary.'
        for group in bundle['records'].values():
            for record in group:
                for key in ('summary','statement'):
                    if key in record:bundle['research']['summary_attestations'].append(dict(record_id=record['id'],field=key,content_sha256=digest(record[key]),reviewed_by='self',reviewed_at='2026-10-01T00:00:00Z'))
        self.write('bundle.json',bundle)
    def gated(self):self.merged();self.attest();self.assertEqual(self.command('gate','--write-bundle')[0],0)
    def test_end_to_end_and_idempotence(self):
        self.gated();gate=(self.run/'gate.json').read_bytes();bundle=(self.run/'bundle.json').read_bytes()
        for extra in ((),('--write-bundle',)):
            self.assertEqual(self.command('gate',*extra)[0],0);self.assertEqual((self.run/'gate.json').read_bytes(),gate);self.assertEqual((self.run/'bundle.json').read_bytes(),bundle)
        self.assertEqual(self.command('export-audience')[0],0)
        with Store(self.run) as store:
            b,g=engine.fresh(Run(self.run,clock=lambda:f.CLOCK),store,self.run/'bundle.json',self.run/'gate.json');d=self.load('audience.draft.json');self.assertEqual(audiences.check_audience(d,b,g,self.load('brief.json'),draft=True)['exit_code'],0);d['segments'][0]['values']['name_ko']='Fabricated';self.assertEqual(audiences.check_audience(d,b,g,self.load('brief.json'),draft=True)['exit_code'],1)
        self.assertEqual(self.command('minimize')[0],0);raw=(self.run/'bundle.min.json').read_bytes();self.assertEqual(self.command('minimize')[0],0);self.assertEqual((self.run/'bundle.min.json').read_bytes(),raw);self.assertEqual(validate_bundle(self.load('bundle.min.json')),[])
    def test_failing_fixtures(self):
        rows=json.loads((f.SKILL/'examples/research/failures.json').read_text())
        for row in rows:
            with self.subTest(name=row['name']),tempfile.TemporaryDirectory(dir=self.root) as temp:
                self.run=f.fixture.build(Path(temp)/'run',clock=lambda:f.CLOCK);ret=self.load('returns/editors.json');imp=self.load('sanitized-imports.json');kind=row['mutation']
                if kind=='invented_quote':ret['excerpts'][0]['excerpt']='Never captured.'
                elif kind=='wrong_family':ret['sources'][0]['source_family']='voice'
                elif kind=='extra_status':ret['candidate_claims'][0]['status']='supported_high'
                elif kind=='unreviewed':imp['imports'][0]['sanitization']['review_attestation']=False
                elif kind=='identifier':ret['excerpts'][0]['summary']='Contact person@example.com'
                elif kind=='partial':ret['axis']['completion']='partial'
                elif kind=='search_count':ret['search_count']=2
                elif kind=='hash':ret['sources'][0]['provenance']['content_sha256']='0'*64
                elif kind=='length':
                    text='x'*301;self.write('sample.txt',text.encode());imp['imports'][0]['content_sha256']=byte_digest(text.encode());imp['imports'][0]['import_id']=merge.import_identity(imp['imports'][0]);ret['sources'][0]['provenance'].update(import_id=imp['imports'][0]['import_id'],content_sha256=imp['imports'][0]['content_sha256']);ret['excerpts'][0].update(capture_ref=imp['imports'][0]['import_id'],excerpt=text)
                elif kind=='fixture':
                    metadata=json.loads((self.run/'run.json').read_text());metadata['test_hooks']=True;self.write('run.json',metadata)
                self.write('returns/editors.json',ret);self.write('sanitized-imports.json',imp)
                extra=[]
                if kind=='duplicate':
                    other=copy.deepcopy(ret);other['candidate_claims'][0]['statement']='Changed duplicate';self.write('returns/duplicate.json',other);extra=['--returns',str(self.run/'returns/editors.json'),str(self.run/'returns/duplicate.json')]
                if row['command']!='merge':
                    self.merged()
                    if kind=='counter':
                        b=self.load('bundle.json');b['records']['claims'][0]['stakes']='high';self.write('bundle.json',b)
                    elif kind=='claim_identity':
                        b=self.load('bundle.json');b['records']['claims'][0]['statement']='Different identity';self.write('bundle.json',b)
                    elif kind=='lock':
                        with Store(self.run,0):code,result=self.command('gate','--lock-timeout','0')
                        self.assertEqual(code,row['exit_code']);continue
                    else:
                        self.assertEqual(self.command('gate')[0],0)
                        if kind=='stale':
                            b=self.load('bundle.json');b['records']['claims'][0]['stakes']='high';self.write('bundle.json',b)
                code,result=self.command(row['command'],*extra);self.assertEqual(code,row['exit_code'],result)
    def test_partial_ack_and_search_targets(self):
        ret=self.load('returns/editors.json');ret['axis']['completion']='partial';self.write('returns/editors.json',ret)
        self.write('acks.json',dict(schema_version='ux-axis-acknowledgements.v1',run_id=ret['run_id'],entries=[dict(kind='partial',axis_id='product',assignment_id='discovery-1',reason='Known gap',acknowledged_by='agent',acknowledged_at='2026-10-01T00:00:00Z')]))
        self.assertEqual(self.command('merge','--acknowledgements',str(self.run/'acks.json'))[0],0);self.assertEqual(self.command('gate')[0],0)
    def test_failed_gate_keeps_prior_snapshot_and_blocks_consumers(self):
        self.gated()
        with Store(self.run) as store:before=store.state()['generation_id']
        b=self.load('bundle.json');b['records']['claims'][0]['stakes']='high';self.write('bundle.json',b);self.assertEqual(self.command('gate')[0],1)
        with Store(self.run) as store:self.assertEqual(store.state()['generation_id'],before)
        self.assertEqual(self.command('export-audience')[0],2);self.assertTrue((self.run/'gate_failed.json').exists())
    def test_retention_purge_and_sticky_counter(self):
        self.gated();b=self.load('bundle.json');r=self.load('merge_receipt.json');src=b['records']['sources'][0];src['retention_until']='2026-10-01T00:00:00Z';src['captures'][0]['metadata']['retention_until']=src['retention_until'];e=b['records']['evidence'][0]['id'];b['records']['claims'][0]['counter_evidence_ids']=[e]
        out,receipt=engine.purge(b,r,[src['id']],datetime.fromtimestamp(f.CLOCK,timezone.utc));self.assertTrue(out['research']['gaps'][-1]['counter_gap']);self.assertNotIn('title',out['records']['sources'][0]);self.assertEqual(out['records']['claims'][0]['counter_evidence_ids'],[])
        self.assertTrue(engine.expired_sources(b,datetime.fromtimestamp(f.CLOCK,timezone.utc)));self.assertFalse(engine.expired_sources(b,datetime.fromtimestamp(f.CLOCK-.001,timezone.utc)))
        self.assertEqual(timestamp('2026-09-30',bare_date=True).timestamp(),f.CLOCK)
    def test_authoritative_reader_capture_and_identity_hints(self):
        ret=json.loads((f.SKILL/'examples/research/reader-return.example.json').read_text());ret['run_id']=self.load('run.json')['run_id'];src=ret['sources'][0];fetch=src['provenance']['fetch_id'];text='business operators completed order lookup. This invented page illustrates a successful source capture.'
        run=Run(self.run,clock=lambda:f.CLOCK);run.save_page(fetch,text)
        outcome=dict(kind='outcome',source='read',fetch_id=fetch,url=src['url'],bucket='read',verdict='ok_strong',stop_class=None,content_sha256=byte_digest(text.encode()),fetched_at=src['observed_at'],presentation='honest_ua',rung='R1',access_basis='public_anonymous',robots={'decision':'allowed','status':'ok'},context='anonymous',terms=None)
        request=dict(kind='request',fetch_id=fetch,url=src['url'],final_url=src['url'],purpose='page',host='measurement.example')
        src.update(item_key='guessed-comment',author_key='a'*16)
        _,_,_,_=merge.source_capture(src,run,[request,outcome],{},[],[]);self.assertIsNone(src['author_key']);self.assertIsNone(src['item_key']);self.assertEqual(src['identity_status'],'unknown')
        src['url']='https://measurement.example/another'
        with self.assertRaises(EngineError):merge.source_capture(src,run,[request,outcome],{},[],[])
        src['url']=outcome['url'];outcome['bucket']='stopped'
        with self.assertRaises(EngineError):merge.source_capture(src,run,[request,outcome],{},[],[])
    def test_whole_input_hash_and_post_close_gate(self):
        self.gated();before=self.load('gate.json')['bundle_input_sha256'];b=self.load('bundle.json');b['research']['gaps'].append(dict(code='coverage_note',note='A new uncertainty'));self.write('bundle.json',b)
        self.assertEqual(self.command('gate')[0],0);self.assertNotEqual(self.load('gate.json')['bundle_input_sha256'],before)
        run=Run(self.run,clock=lambda:f.CLOCK);run.close();self.assertEqual(self.command('gate')[0],0);self.assertEqual(self.command('export-audience')[0],0)
    def test_counter_history_survives_failed_gate_and_cannot_be_removed(self):
        self.gated();bundle=self.load("bundle.json");claim=bundle["records"]["claims"][0];eid=bundle["records"]["evidence"][0]["id"]
        claim["counter_evidence_ids"]=[eid];claim["stakes"]="high";self.write("bundle.json",bundle)
        code,result=self.command("gate");self.assertEqual(code,1,result)
        with Store(self.run) as store:self.assertEqual(store.committed("gate_receipt.json")["counter_history"][0]["counter_evidence_ids"],[eid])
        bundle=self.load("bundle.json");bundle["records"]["claims"][0]["counter_evidence_ids"]=[];self.write("bundle.json",bundle)
        self.assertEqual(self.command("gate")[0],2)

    def test_crash_reservation_acknowledgement_does_not_reduce_budget(self):
        hosts=self.load("hosts.json");hosts["run"]["docs"]=1;hosts["hosts"]["public.example"]={"docs":1,"policy_requests":0};self.write("hosts.json",hosts)
        self.assertEqual(self.command("merge")[0],1)
        rid=self.load("axes.json")["run_id"]
        self.write("acks.json",dict(schema_version="ux-axis-acknowledgements.v1",run_id=rid,entries=[dict(kind="unattributed_request",axis_id=None,assignment_id=None,reason="A booked request was interrupted",acknowledged_by="agent",acknowledged_at="2026-10-01T00:00:00Z",request_gap=dict(host="public.example",charged_documents=1,logged_documents=0,unmatched_count=1))]))
        self.assertEqual(self.command("merge","--acknowledgements",str(self.run/"acks.json"))[0],0)
        self.assertEqual(self.load("query_log.json")["document_requests"],1)

    def test_write_gate_repairs_expiry_and_purges_cached_input(self):
        returned=self.load("returns/editors.json");imports=self.load("sanitized-imports.json")
        deadline="2026-10-01T00:00:01Z";returned["sources"][0]["retention_until"]=deadline;imports["imports"][0]["retention_until"]=deadline
        self.write("returns/editors.json",returned);self.write("sanitized-imports.json",imports);self.merged();self.assertEqual(self.command("gate")[0],0)
        self.clock=f.CLOCK+1
        self.assertEqual(self.command("gate")[0],2)
        code,result=self.command("gate","--write-bundle");self.assertEqual(code,0,result)
        bundle=self.load("bundle.json");self.assertEqual(bundle["records"]["sources"][0]["access_method"],"retention_purge");self.assertNotIn("excerpt",bundle["records"]["evidence"][0]);self.assertFalse((self.run/"sample.txt").exists());self.assertFalse((self.run/"returns/editors.json").exists())
        self.assertEqual(self.command("export-audience")[0],0);self.assertEqual(self.load("audience.draft.json")["segments"],[])

    def test_expiry_keeps_fresh_capture_and_blocks_expired_counter(self):
        self.gated();bundle=self.load("bundle.json");receipt=self.load("merge_receipt.json");source=bundle["records"]["sources"][0]
        old=copy.deepcopy(source["captures"][0]);old["capture_ref"]="IMP-"+"f"*64;old["metadata"]["retention_until"]="2026-10-01T00:00:00Z";source["captures"].append(old)
        ev=copy.deepcopy(bundle["records"]["evidence"][0]);ev.update(id="EV-deadbeef",capture_ref=old["capture_ref"]);bundle["records"]["evidence"].append(ev);bundle["records"]["claims"][0]["counter_evidence_ids"]=[ev["id"]]
        out,proof=engine.purge(bundle,receipt,[source["id"]],datetime.fromtimestamp(f.CLOCK,timezone.utc))
        self.assertNotIn("research_tombstone",out["records"]["sources"][0]);self.assertEqual(len(out["records"]["sources"][0]["captures"]),1);self.assertNotIn("excerpt",out["records"]["evidence"][1]);self.assertTrue(out["research"]["gaps"][-1]["counter_gap"])

    def test_schema_pin_and_examples(self):
        resolver=schema.Resolver();self.assertEqual(resolver.validate(json.loads((f.SKILL/'examples/research/reader-return.example.json').read_text()),'ux-reader-return.v1.schema.json'),[])
        ret=self.load('returns/editors.json');ret['sources'][0].update(source_type='survey',producer_stake='vendor',source_family='estimate');self.assertEqual(resolver.validate(ret,'ux-reader-return.v1.schema.json'),[]);ret['sources'][0]['source_family']='measured';self.assertTrue(resolver.validate(ret,'ux-reader-return.v1.schema.json'))


class StorageReportsAndValidator(unittest.TestCase):
    def test_canonical_urls_and_short_collision(self):
        for value,expected in [(1.,b'1'),(-0.,b'0'),({'z':True,'e\u0301':'e\u0301'},'{"z":true,"é":"é"}'.encode()),(.125,b'0.125')]:self.assertEqual(canonical(value),expected)
        for value in (b'{"a":1,"a":2}',b'{"x":NaN}',b'"\\ud800"',b'{"e\\u0301":1,"\\u00e9":2}'):
            with self.assertRaises(EngineError):loads(value)
        ids=Ids(lambda _: 'a'*64);ids.make('SRC',['one'])
        with self.assertRaises(EngineError):ids.make('SRC',['two'])
        self.assertEqual(resource_url('HTTPS://Example.COM.:443/Case/%7e?id=1&id=2&UTM_Source=x#frag'),'https://example.com/Case/~?id=1&id=2')
        for url in ('https://u:p@example.com','https://example.com/?token=***','https://example.com/%xz'):
            with self.assertRaises(EngineError):resource_url(url)
        self.assertNotEqual(resource_url('https://example.com/a?ref=1'),resource_url('https://example.com/a?ref=2'))
    def test_minimized_origin_mode_cannot_cross_into_live_loop(self):
        from loop_factory import make_packet
        from uxloop.contracts import validate_packet
        temporary=tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        packet=make_packet(Path(temporary.name))
        packet["bundle"]["minimized_from"]=dict(bundle_id=packet["bundle"]["bundle_id"],bundle_input_sha256="0"*64,gate_input_sha256="0"*64,rules_version="source-grading-2026-10-01.1",sanitizer_version="minimize-2026-10-01.1",mode="live" if packet["mode"]=="fixture" else "fixture")
        self.assertTrue(any("consuming loop mode" in x for x in validate_packet(packet)))

    def test_minimizer_preserves_an_unlinked_hypothesis(self):
        bundle=f.bundle([],[],f.claim());c=bundle["records"]["claims"][0]
        bundle["research"]["summary_attestations"]=[dict(record_id=c["id"],field="statement",content_sha256=digest(c["statement"]),reviewed_by="self",reviewed_at="2026-10-01T00:00:00Z")]
        gate=dict(bundle_input_sha256="0"*64,rules_version="source-grading-2026-10-01.1",mode="fixture")
        out,result=minimize.minimize(bundle,gate);self.assertEqual(result["exit_code"],0,result);self.assertEqual(out["records"]["claims"][0]["evidence_ids"],[]);self.assertEqual(validate_bundle(out),[])

    def test_claim_proofs_outside_identity(self):
        a=f.claim();a['audience_values']=[dict(join=dict(segment_id='seg',entity_kind='segment',entity_id='seg',field='share'),value=.2,denominator_evidence_ids=['e1'],value_checks=[])]
        b=copy.deepcopy(a);b['audience_values'][0]['denominator_evidence_ids']=['e2'];self.assertEqual(claim_identity('run',a),claim_identity('run',b))
    def test_atomic_manifest_failure_and_competing_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve()
            with Store(root) as store:store.publish('test',{'value.json':{'value':1}})
            for step in ('staged','snapshot','before_manifest','after_manifest'):
                with self.subTest(step=step):
                    def fault(at):
                        if at==step:raise RuntimeError('injected crash')
                    with Store(root,fault=fault) as store:
                        with self.assertRaises(RuntimeError):store.publish('test',{'value.json':{'value':2}})
                    with Store(root) as store:
                        self.assertEqual(store.committed('value.json')['value'],2 if step=='after_manifest' else 1);self.assertEqual(len(list((root/".engine").iterdir())),1);store.publish('reset',{'value.json':{'value':1}})
            with Store(root):
                with self.assertRaises(EngineError) as caught:
                    with Store(root,0):pass
                self.assertEqual(caught.exception.exit_code,3)
    def test_symlinks_and_schema_network_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp).resolve();(p/'outside').write_text('{}');(p/'link').symlink_to(p/'outside')
            with self.assertRaises(EngineError):read_json(p/'link')
        r=schema.Resolver()
        with self.assertRaises(EngineError):r.ref('https://untrusted.example/schema','ux-reader-return.v1.schema.json')
        with self.assertRaises(EngineError):r.check_schema({'invented_keyword':True})
    def test_report_parser_order_annex_and_encoded_ids(self):
        b=f.bundle([],[],f.claim());g={'claims':[dict(claim_id='CLM-11111111',status='supported_high',counter_search_required=False)],'bundle_id':'BND-test'};text='# Report\n\n## Decision\nCLM-11111111 supported_high: A result with source SRC-11111111.\nNext step: Test it.\nCoverage: no pages; none stopped; fixture only.\n\n## Annex\n'
        def mapping(t):return dict(schema_version='ux-report-claims.v1',report_sha256=byte_digest(t.encode()),statements=[])
        self.assertEqual(reports.check(text,mapping(text),b,g,{})['exit_code'],0)
        for changed,code in [(text.replace('## Decision','## Method'),1),(text.replace('CLM-11111111','clm-11111111'),2),(text+'\n```\nunclosed',1),(text+'\nCLM-deadbeef',2)]:
            with self.subTest(code=code),self.assertRaises(EngineError) as caught:reports.check(changed,mapping(changed),b,g,{})
            self.assertEqual(caught.exception.exit_code,code)
        g['claims'][0]['status']='lead_only';self.assertEqual(reports.check(text,mapping(text),b,g,{})['exit_code'],1)
        lines,heads,fences,paths,annex=reports.markdown('Title\n===\n\n결론\n---\n\n## Annex\n### Child\nCLM-11111111\n## Other\nCLM-11111111');self.assertTrue(annex[9]);self.assertFalse(annex[11])
        g['claims'][0]['status']='supported_high';changed=text+'\n[community](https://reddit.com/r/example)';routes={'platforms':[{'platform_family':'community','hosts':['reddit.com']}]};self.assertEqual(reports.check(changed,mapping(changed),b,g,routes)['exit_code'],1)
    def test_persona_qa_receipt_second_pass_and_report(self):
        legacy=json.loads((Path(__file__).parent/'fixtures/valid-bundle.json').read_text());self.assertEqual(validate_bundle(legacy),[]);self.assertTrue(bundle_warnings(legacy))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();raw=b'invented capture';(root/'capture.png').write_bytes(raw);run=legacy['records']['runs'][0];run['started_at']='2026-09-01T00:00:00Z';obs=legacy['records']['observations'][0];obs['receipt']=dict(artifact_path='capture.png',sha256=byte_digest(raw),captured_at='2026-09-01T00:00:01Z',surface_url=run['surface_ref'],build_id='diagnostic',device='phone',quoted_ui_text='Find order')
            finding=legacy['records']['findings'][0];finding['second_pass']=dict(reviewer='self',task_completed=True,control_name='Find order',omitted=[],severity='agree',inconclusive=False)
            self.assertEqual(validate_bundle(legacy,artifacts_root=root),[])
            for key,val in [('sha256','0'*64),('captured_at','2026-08-31T23:59:59Z'),('artifact_path','../missing')]:
                b=copy.deepcopy(legacy);b['records']['observations'][0]['receipt'][key]=val;self.assertTrue(validate_bundle(b,artifacts_root=root))
            finding['second_pass']['severity']='disagree';self.assertTrue(validate_bundle(legacy,artifacts_root=root));finding['second_pass']['resolution']='Reviewed and retained.';self.assertEqual(validate_bundle(legacy,artifacts_root=root),[])
            report=root/'report.md';report.write_text('# QA\n\n## Decision\nVerdict: ship after fixes — diagnostic build.\n');self.assertEqual(validate_bundle(legacy,report=report),[]);report.write_text('# QA\n\n## Method\nVerdict: ship\n');self.assertTrue(validate_bundle(legacy,report=report))
    def test_malformed_optional_fields_never_throw(self):
        legacy=json.loads((Path(__file__).parent/'fixtures/valid-bundle.json').read_text())
        for value in (None,[],{},True):self.assertTrue(validate_bundle(value))
        for field in ('observation_ids','counter_evidence_ids','context_evidence_ids','research_support_evidence_ids'):
            for value in ({},True,[{}]):
                b=copy.deepcopy(legacy);b['records']['claims'][0][field]=value;self.assertTrue(validate_bundle(b))
    def test_start_runtime_versions_and_old_python(self):
        with tempfile.TemporaryDirectory() as tmp,contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(['start','--run',str(Path(tmp)/'run')]),0);value=json.loads(output.getvalue());self.assertIn('python',value['runtime_versions']);self.assertIn('nodejs',value['runtime_versions'])
        with patch('uxresearch.cli.sys.version_info',(3,9,0)),contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(['start','--run','unused']),2);self.assertIn('Python 3.10',output.getvalue())
    def test_preflight_only_close_totals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=f.fixture.build(Path(tmp)/'run',clock=lambda:f.CLOCK);run=Run(root,clock=lambda:f.CLOCK)
            denied={'allowed':False,'robots_status':'ok','decision':'disallowed'}
            with patch('uxresearch.ladder.net.check_host'),patch('uxresearch.ladder.robots_decision',return_value=denied):
                from uxresearch.ladder import check_robots
                self.assertEqual(check_robots(run,'https://public.example/page')['exit_code'],3)
            summary=run.close();self.assertEqual((summary['totals']['urls'],summary['totals']['stopped']),(1,1))


if __name__=='__main__':unittest.main()
