"""Invented in-memory boundaries and real offline command input builders."""
from __future__ import annotations
import copy,importlib.util,sys
from pathlib import Path
import _paths
from uxresearch.canonical import byte_digest,digest
from uxresearch.flags import empty
from uxresearch.merge import ARRAYS
from uxresearch.grading import assess
SKILL=_paths.SKILL
spec=importlib.util.spec_from_file_location('offline_research_fixture',SKILL/'examples/research/fixture.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)

CLOCK=1790812800


def scope(**kw):
    result=dict(product_relation='product_users',population='diagnostic population',period_start=None,period_end=None,version=None,segment_id='seg',context_id=None);result.update(kw);return result


def source(i,family='voice',channel=None,*,author=True,org=None,published='2026-09-01',**kw):
    types=dict(voice='community',measured='product_analytics',statistical='official_statistics',estimate='market_report',intent='official_docs',secondary='news',expert_judgment='expert_judgment',none='synthetic')
    channel=channel or types[family];flags=empty();flags.update(kw.pop('flags',{}))
    metadata=dict(title='Invented source',source_type=types[family],source_family=family,producer_stake='independent',platform_family=channel,org=org or ('institution-'+str(i) if family!='voice' else None),author_key=format(i,'016x') if family=='voice' and author else None,thread_key=None,published_at=published,observed_at='2026-09-15T00:00:00Z',valid_at=None,version=None,access_method='team_export',access_basis='team_provided',public_scope='deidentified_aggregate',retention_status='retained',retention_until=None,privacy_class='ordinary',promo_check='text_only',flags=flags,provenance=dict(kind='import',import_id='IMP-'+format(i,'064x'),content_sha256=byte_digest(('capture '+str(i)).encode())),access=None)
    metadata.update(kw)
    return dict(**metadata,id='SRC-'+format(i,'08x'),channel=channel,source_ref='team-import://run/'+metadata['provenance']['import_id'],item_key=None,identity_status='attested' if author else None,aliases=[],captures=[dict(capture_ref=metadata['provenance']['import_id'],content_sha256=metadata['provenance']['content_sha256'],metadata=copy.deepcopy(metadata))])


def evidence(i,src,**kw):
    text=kw.pop('text','Invented firsthand excerpt '+str(i)+'.');flags=empty();flags.update(kw.pop('flags',{}))
    ev=dict(id='EV-'+format(i,'08x'),source_id=src['id'],capture_ref=src['captures'][0]['capture_ref'],excerpt=text,summary='An authored diagnostic summary.',evidence_type='firsthand' if src['source_family']=='voice' else 'statistic' if src['source_family']=='statistical' else 'quantitative',epistemic_status='observed',flags=flags,scope=scope(),cues={k:None for k in ('segment','context','task','condition','device')},denominator=None,copypaste_group=byte_digest(text.encode()))
    ev.update(kw);return ev


def claim(kind='segment_exists',support=(),counter=(),**kw):
    c=dict(id='CLM-11111111',claim_kind=kind,statement='An invented assertion for grading.',epistemic_status='inferred',research_epistemic_status='inferred',verification_status='unverified',evidence_ids=list(support),research_support_evidence_ids=list(support),research_context_evidence_ids=[],context_evidence_ids=[],counter_evidence_ids=list(counter),observation_ids=[],subject=dict(segment_id='seg',task_id=None,condition_id=None,context_id=None,pain_point_id=None),scope=scope(),about_current_version=False,stakes='normal',scenario_priorities=[],audience_values=[],counter_search=None)
    c.update(kw);return c


def bundle(sources,evs,c):
    out=dict(schema_version='ux-evidence-bundle.v1',bundle_id='BND-test',permissions=dict(requested=['read_only'],granted=['read_only'],blocked=[]),records={k:[] for k in ARRAYS},research=dict(contract_version='research-engine-2026-10-01.1',run_id='run',manifest=dict(segments=[dict(segment_id='seg',priority='secondary',decision_ref='owner',summary='Diagnostic scope')]),query_log_sha256='0'*64,expansion_log_sha256='0'*64,merge_receipt_sha256='0'*64,rules_version='source-grading-2026-10-01.1',verifier_decisions=[],scope_resolutions=[],gaps=[],summary_attestations=[]))
    out['records'].update(sources=sources,evidence=evs,claims=[c]);return out


def receipt(b):
    return dict(source_proofs=[dict(source_id=s['id'],full_id_sha256=digest(s['id'])) for s in b['records']['sources']],evidence_proofs=[],claim_proofs=[],counter_history=[])


def grade(b,brief=None,query=None):
    from datetime import datetime,timezone
    return assess(b,brief or dict(product=dict(name='diagnostic',url='https://product.example',release_date='2026-09-01',current_version='v1')),query or dict(receipts=[]),receipt(b),digest(b),datetime.fromtimestamp(CLOCK,timezone.utc))


def denominator(bound=False,printed='20%',n=100):
    return dict(population='diagnostic population',period_start='2026-09-01',period_end='2026-09-14',product_relation='general_population' if bound else 'product_users',sampling_frame='neutral census',n=n,method='census',unit='percent',value_as_printed=printed,interpretation='population_bound' if bound else 'product_measure')


def statistical(src,ev):
    d=denominator(True);ev['denominator']=d;ev['scope']=scope(**{k:d[k] for k in ('population','period_start','period_end','product_relation')})
    card=dict(publisher=src['org'],title='Invented census',approval_no=None,table_id=None,reference_period=d['period_start']+'/'+d['period_end'],frame=d['sampling_frame'],n=d['n'],method=d['method'],sampling_error=None,unit=d['unit'],value_as_printed=d['value_as_printed'],url=None,retrieved_at='2026-09-15T00:00:00Z',licence=None)
    src['stat_card']=card;src['captures'][0]['metadata']['stat_card']=copy.deepcopy(card)


def observation(b,*,completed=True,observed=True):
    sc=scope(product_relation='product_surface')
    b['records']['claims'][0]['scope']=copy.deepcopy(sc)
    b['records']['personas']=[dict(id='PER-observer',basis='human')]
    b['records']['scenarios']=[dict(id='SC-test',persona_id='PER-observer',task='Lookup order',scope=copy.deepcopy(sc),task_id=None,segment_id='seg')]
    b['records']['runs']=[dict(id='RUN-test',scenario_id='SC-test',status='completed' if completed else 'interrupted',surface_ref='https://product.example/editor',started_at='2026-09-20T00:00:00Z',version='v1',scope=copy.deepcopy(sc))]
    b['records']['observations']=[dict(id='OBS-test',run_id='RUN-test',epistemic_status='observed' if observed else 'inferred',result='The lookup control completed the task.',scope=copy.deepcopy(sc),version='v1')]
    b['records']['claims'][0]['observation_ids']=['OBS-test']
