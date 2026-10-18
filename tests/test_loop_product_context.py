"""Product-context intent protection: the opt-in goal binding gates writes and completion.

One focused module for the additive contract: preserved constraints must be acknowledged
before any code write with a concrete prewrite decision, unresolved material conflicts
block only the fixes they overlap, explicitly authorized changes need a recorded current
human decision (a separate operator record, never a generic grant or provider claim), and completion requires a
fresh, same-round replay-linked intent review covering every applicable constraint with
actual declared scenario evidence. Packets without the binding keep the exact v1 behavior.
"""
import copy
import difflib
import json
import shutil
import tempfile
import unittest
import subprocess
import sys
from pathlib import Path

from loop_factory import ROOT, SKILL, append_recovery_round, make_packet
from uxloop.contracts import validate_packet
from uxloop.engine import report, run
from uxloop.io import ContractError, sha, now, digest
from uxloop.demo_factory import replace_artifact
from uxloop.storage import load

ACTOR = 'test-supervisor'
REASON = 'Approve only the isolated fixture site patch'
CONTEXT_AT = '2026-09-14T00:00:00+00:00'
REVIEW_AT = '2026-09-14T00:07:00+00:00'
REVIEW2_AT = '2026-09-14T00:17:00+00:00'

CONFLICT = {
    'id': 'conflict-label',
    'description': '프로젝트 문서는 지금의 "다음" 라벨을 유지할 것을 권고하지만, 요청은 목적지를 분명히 하라고 한다.',
    'source_id': 'ctx-doc',
    'scope': {'paths': ['index.html'], 'scenario_ids': []},
}
UNRELATED_CONFLICT = {
    'id': 'conflict-checkout',
    'description': '결제 흐름의 안내 문구를 바꿀지는 별도로 정해야 한다.',
    'source_id': 'ctx-doc',
    'scope': {'paths': ['checkout.html'], 'scenario_ids': []},
}
PRESERVED_ENTRY = {'fix_id': 'fix-1', 'constraint_id': 'constraint-action-flow', 'outcome': 'preserved',
                   'evidence': '재실행에서 버튼 위치와 진행 흐름은 그대로이고 라벨만 목적지를 분명히 나타냈다.',
                   'run_id': 'replay-1'}
CHANGED_ENTRY = {'fix_id': 'fix-1', 'constraint_id': 'constraint-action-flow', 'outcome': 'intentionally_changed',
                 'evidence': '요청한 결정대로 라벨이 바뀌었고 확인 흐름은 유지되었다.', 'run_id': 'replay-1'}
CONFLICT_ENTRY = {'fix_id': 'fix-1', 'conflict_id': 'conflict-label', 'outcome': 'resolved',
                  'evidence': '요청한 결정대로 라벨만 바뀌었고 확인 흐름은 유지되었다.', 'run_id': 'replay-1'}


def go_kwargs(kwargs):
    options = {'grants': ['code_write'], 'actor': ACTOR, 'reason': REASON}
    options.update(kwargs)
    return options


def context_payload(conflicts=(), memory_status='searched_not_available', include_memory_source=False,
                    drop_memory_search=False):
    sources = [
        {'id': 'ctx-doc', 'kind': 'project_doc', 'ref': 'docs/product-notes.md', 'version': 'git ad5b461',
         'checked_at': '2026-09-13'},
        {'id': 'ctx-decision', 'kind': 'current_user_decision', 'ref': '요청 대화 2026-10-01', 'version': 'session-1',
         'checked_at': '2026-09-13'},
    ]
    if include_memory_source:
        sources.append({'id': 'ctx-memory', 'kind': 'memory', 'ref': 'memory://sessions/ergo', 'version': 'auto',
                        'checked_at': '2026-09-12'})
    payload = {
        'kind': 'product_context', 'goal_id': 'goal-action-label',
        'product': {'name': '예제 상점', 'version': '1', 'surface': 'https://example.test/product'},
        'path_scenarios': {'index.html': ['scenario-1']},
        'memory_search': {'status': memory_status,
                          'detail': 'AGENTS.md, README, PRD와 세션 기록 위치를 확인했다. 이 제품에 대해 남아 있는 메모리는 없다.'},
        'sources': sources,
        'constraints': [{
            'id': 'constraint-action-flow',
            'title': '다음 행동 버튼의 위치와 진행 흐름 유지',
            'reason': '기획 문서에 근거해 사용자가 다음 행동을 한 단계씩 확인하며 진행하도록 의도적으로 설계되었다.',
            'source_id': 'ctx-doc', 'decision_date': '2026-09-13',
            'scope': {'paths': ['index.html'], 'scenario_ids': ['scenario-1']},
        }],
        'conflicts': list(conflicts),
    }
    if drop_memory_search:
        payload.pop('memory_search')
    return payload


def _add_artifact(packet, root, artifact_id, kind, payload, at):
    path = 'artifacts/' + artifact_id + '.json'
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + '\n').encode()
    (root / path).write_bytes(raw)
    packet['artifacts'].append({'id': artifact_id, 'path': path, 'sha256': sha(raw), 'kind': kind,
                                'provenance': 'fixture', 'created_at': at})
    return artifact_id


def bind_context(packet, root, payload=None, at=CONTEXT_AT):
    packet['goal']['product_context_artifact_id'] = _add_artifact(
        packet, root, 'artifact-context', 'product_context', payload or context_payload(), at)


def review_payload(packet, results=None, conflict_results=(), fix_ids=('fix-1',), revision=None, run_ids=None):
    replay = packet['replays'][0]
    return {'kind': 'intent_review', 'replay_id': replay['id'],
            'product_context_artifact_id': packet['goal'].get('product_context_artifact_id'),
            'product_context_sha256': next((a['sha256'] for a in packet['artifacts'] if a['id'] == packet['goal'].get('product_context_artifact_id')), None),
            'code_revision': revision or replay['regression']['code_revision'],
            'run_ids': list(run_ids if run_ids is not None else replay['run_ids']), 'fix_ids': list(fix_ids),
            'constraint_results': [dict(PRESERVED_ENTRY)] if results is None else list(results),
            'conflict_results': list(conflict_results)}


def attach_review(packet, root, payload=None, at=REVIEW_AT):
    replay = packet['replays'][0]
    if payload is None:
        payload = review_payload(packet)
        payload['constraint_results'] = [dict(PRESERVED_ENTRY)]
    replay['intent_review_artifact_id'] = _add_artifact(packet, root, 'artifact-intent-review', 'intent_review',
                                                         payload, at)


def attach_changed_review(packet, root):
    payload = review_payload(packet)
    payload['constraint_results'] = [dict(CHANGED_ENTRY)]
    attach_review(packet, root, payload)


def acknowledge(packet, decision='preserved', evidence='버튼의 위치와 진행 흐름은 그대로 두고 라벨만 목적지를 분명히 바꾼다.',
                actor=None):
    ack = {'constraint_id': 'constraint-action-flow', 'decision': decision, 'evidence': evidence}
    if actor is not None:
        ack['actor'] = actor
    packet['fixes'][0]['constraint_acknowledgements'] = [ack]


def resolve_conflicts(packet, actor=ACTOR):
    packet['fixes'][0]['conflict_resolutions'] = [
        {'conflict_id': 'conflict-label', 'actor': actor,
         'note': '요청자가 2026-10-01 대화에서 이 화면의 라벨을 먼저 다듬기로 결정했다.'}]


def operator_decision(packet, conflict_id=None):
    binding = packet['goal']['product_context_artifact_id']
    artifact = next(x for x in packet['artifacts'] if x['id'] == binding)
    return {'context_artifact_id': binding, 'context_sha256': artifact['sha256'],
            'fix_id': 'fix-1', 'decision': 'resolve' if conflict_id else 'authorized_change',
            'decided_at': now(), 'reference': 'Explicit operator message for this context and target',
            **({'conflict_id': conflict_id} if conflict_id else {'constraint_id': 'constraint-action-flow'})}


def make_no_change(packet, root):
    packet['bundle']['records']['findings'] = []
    packet['bundle']['records']['proposals'] = []
    packet['fixes'] = []
    packet['rounds'][0]['fix_ids'] = []
    before = packet['browser_runs'][0]['code_revision']
    packet['browser_runs'][1]['code_revision'] = before
    packet['replays'][0]['regression']['code_revision'] = before
    for artifact in packet['artifacts']:
        if artifact['kind'] in {'code_patch', 'screenshot', 'figma_readback'}:
            continue
        payload = json.loads((root / artifact['path']).read_text())
        if 'code_revision' in payload:
            replace_artifact(packet, root, artifact['id'], lambda value: value.update(code_revision=before))


def add_second_scenario(p,e):
    records=p['bundle']['records']
    s=copy.deepcopy(p['scenarios'][0]);s['id']='scenario-2';s['route']='/checkout'; s['steps'][0]['action']='Open /checkout in an isolated browser';p['scenarios'].append(s)
    p['goal']['scenario_ids'].append('scenario-2')
    records['scenarios'].append({'id':'scenario-2','persona_id':'persona-1','task':'Checkout task without action-label check'})
    for phase in ['baseline','replay']:
        src=next(r for r in p['browser_runs'] if r['phase']==phase)
        new=copy.deepcopy(src);new['id']=phase+'-2';new['scenario_id']='scenario-2';new['scenario_digest']=digest(s)
        new['environment']['route']='/checkout';new['environment']['session_id']='isolated-'+phase+'-2'
        visual=copy.deepcopy(next(v for v in p['visual_checks'] if v['run_id']==src['id']))
        visual['id']+='-2';visual['run_id']=new['id'];visual['route']='/checkout'
        ids=set(new['evidence'].values()) | {x for row in new['steps'] for x in row['artifact_ids']} | {r['artifact_id'] for r in new['accessibility']} | {visual['actual_artifact_id'], visual['comparison_artifact_id']}
        mapping={i:i+'-2' for i in ids}
        for k,a in list(new['evidence'].items()):new['evidence'][k]=mapping[a]
        for st in new['steps']:st['artifact_ids']=[mapping[x] for x in st['artifact_ids']]
        for a in new['accessibility']:a['artifact_id']=mapping[a['artifact_id']]
        visual['actual_artifact_id']=mapping[visual['actual_artifact_id']];visual['comparison_artifact_id']=mapping[visual['comparison_artifact_id']]
        for old_id,new_id in mapping.items():
            a=copy.deepcopy(next(x for x in p['artifacts'] if x['id']==old_id))
            path=Path(a['path']);a['id']=new_id;a['path']=str(path.with_name(path.stem+'-2'+path.suffix));raw=(e/path).read_bytes()
            if a['kind']!='screenshot':
                value=json.loads(raw)
                if 'run_id' in value:value['run_id']=new['id']
                if 'scenario_digest' in value:value['scenario_digest']=digest(s)
                if a['kind']=='steps':value['results']=new['steps']
                elif a['kind']=='accessibility':value['results']=new['accessibility']
                elif a['kind']=='visual_report':
                    value['comparison']=visual
                    value['inspection']['viewed_artifact_ids']=[visual['actual_artifact_id'],visual['reference_artifact_id']]
                raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
            a['sha256']=sha(raw);(e/a['path']).write_bytes(raw);p['artifacts'].append(a)
        p['browser_runs'].append(new);p['visual_checks'].append(visual)
        records['runs'].append({'id':new['id'],'scenario_id':s['id'],'status':'completed','surface_ref':s['origin']+s['route']})
        p['rounds'][0]['baseline_run_ids'].append(new['id']) if phase=='baseline' else p['replays'][0]['run_ids'].append(new['id'])
    p['replays'][0]['regression']['scenario_ids'].append('scenario-2')
    replace_artifact(p,e,'artifact-regression', lambda v:v.update(run_ids=p['replays'][0]['run_ids'],scenario_ids=p['goal']['scenario_ids']))


class ProductContextIntentTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.ux-loop').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.ux-loop')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.evidence_root = self.root / 'evidence'
        self.workspace = self.root / 'site'
        self.workspace.mkdir()
        shutil.copy2(SKILL / 'examples/loop/site/index.html', self.workspace / 'index.html')
        self.checkpoint = self.root / 'checkpoint.json'
        self.packet = make_packet(self.evidence_root)
        self.original = (self.workspace / 'index.html').read_text()

    def fresh(self, case='happy'):
        """An isolated disposable run directory for cases that must not share a checkpoint."""
        directory = tempfile.TemporaryDirectory(dir=ROOT / '.ux-loop')
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        evidence_root = root / 'evidence'
        workspace = root / 'site'
        workspace.mkdir()
        shutil.copy2(SKILL / 'examples/loop/site/index.html', workspace / 'index.html')
        packet = make_packet(evidence_root, case)
        options = go_kwargs({'workspace': workspace, 'evidence_root': evidence_root,
                             'checkpoint': root / 'checkpoint.json'})
        return packet, options

    def go(self, packet=None, **kwargs):
        return run(self.packet if packet is None else packet, self.checkpoint, self.workspace,
                   self.evidence_root, **go_kwargs(kwargs))

    def assert_not_complete(self, state, status=None):
        if status:
            self.assertEqual(state['status'], status, state['reason'])
        self.assertNotEqual(state['status'], 'complete')
        self.assertEqual(state['accepted_fix_ids'], [])
        self.assertFalse(report(state)['product_complete'])

    def assert_untouched(self, options):
        self.assertEqual((options['workspace'] / 'index.html').read_text(),
                         (SKILL / 'examples/loop/site/index.html').read_text())

    def test_binding_accepts_patch_only_after_fresh_covering_intent_replay(self):
        bind_context(self.packet, self.evidence_root)
        acknowledge(self.packet)
        attach_review(self.packet, self.evidence_root)
        self.assertEqual(validate_packet(self.packet), [])
        state = self.go()
        self.assertEqual(state['status'], 'complete', state['reason'])
        self.assertEqual(state['accepted_fix_ids'], ['fix-1'])
        self.assertIn('상품 상세 보기', (self.workspace / 'index.html').read_text())
        summary = report(state)['product_context']
        self.assertEqual(summary['artifact_id'], 'artifact-context')
        self.assertEqual(summary['memory_search'], 'searched_not_available')
        self.assertEqual(summary['constraints'][0]['id'], 'constraint-action-flow')
        self.assertEqual(summary['applied_fix_decisions']['fix-1']['acknowledgements'],
                         {'constraint-action-flow': 'preserved'})
        self.assertIn('imported authored records', ' '.join(report(state)['limitations']))
        # Completion is revalidated against the artifact hash: a tampered review cannot keep success.
        (self.evidence_root / 'artifacts/artifact-intent-review.json').write_text('{}')
        self.assert_not_complete(run(None, self.checkpoint), 'unknown')

    def test_conflict_blocks_write_until_a_current_request_settles_exactly_that_conflict(self):
        bind_context(self.packet, self.evidence_root, context_payload(conflicts=[CONFLICT]))
        acknowledge(self.packet)
        state = self.go()
        self.assert_not_complete(state, 'blocked')
        self.assertEqual(state['phase'], 'fix')
        self.assertIn('Unresolved material intent conflict conflict-label', state['reason'])
        self.assertEqual((self.workspace / 'index.html').read_text(), self.original)

        packet, options = self.fresh()
        bind_context(packet, options['evidence_root'], context_payload(conflicts=[CONFLICT]))
        acknowledge(packet)
        resolve_conflicts(packet)
        payload = review_payload(packet, conflict_results=[dict(CONFLICT_ENTRY)])
        attach_review(packet, options['evidence_root'], payload)
        self.assertEqual(validate_packet(packet), [])
        done = run(packet, **options, intent_decisions=[operator_decision(packet, 'conflict-label')])
        self.assertEqual(done['status'], 'complete', done['reason'])
        self.assertIn('상품 상세 보기', (options['workspace'] / 'index.html').read_text())

    def test_unrelated_conflict_or_gap_does_not_stop_safe_fixes(self):
        bind_context(self.packet, self.evidence_root, context_payload(conflicts=[UNRELATED_CONFLICT]))
        acknowledge(self.packet)
        attach_review(self.packet, self.evidence_root)
        state = self.go()
        self.assertEqual(state['status'], 'complete', state['reason'])
        self.assertEqual(report(state)['product_context']['unresolved_conflicts'][0]['id'], 'conflict-checkout')
        self.assertIn('상품 상세 보기', (self.workspace / 'index.html').read_text())

    def test_missing_or_fabricated_context_blocks_code_write_not_earlier_phases(self):
        cases = (
            ('missing artifact file',
             lambda p, r: (bind_context(p, r), (r / 'artifacts/artifact-context.json').unlink())),
            ('fabricated memory source',
             lambda p, r: bind_context(p, r, context_payload(include_memory_source=True))),
            ('unrecorded memory search',
             lambda p, r: bind_context(p, r, context_payload(drop_memory_search=True))),
        )
        for label, mutate in cases:
            with self.subTest(label=label):
                packet, options = self.fresh()
                acknowledge(packet)
                attach_review(packet, options['evidence_root'])
                mutate(packet, options['evidence_root'])
                self.assertEqual(validate_packet(packet), [])
                state = run(packet, **options)
                self.assert_not_complete(state, 'blocked')
                self.assertEqual(state['phase'], 'fix', label)  # research, planning and QA were never stopped
                self.assertTrue('product context' in state['reason'] or 'Missing artifact' in state['reason'])
                self.assert_untouched(options)

    def test_prewrite_acknowledgement_needs_concrete_evidence_and_current_decision(self):
        cases = (
            ('no acknowledgement', lambda p: None, 'does not acknowledge'),
            ('blank evidence', lambda p: acknowledge(p, evidence='   '), 'concrete'),
            ('provider actor', lambda p: acknowledge(p, decision='authorized_change', actor='provider-agent'), 'operator intent decision'),
            ('matching grant actor', lambda p: acknowledge(p, decision='authorized_change', actor=ACTOR), 'operator intent decision'),
        )
        for label, setup, reason in cases:
            with self.subTest(label=label):
                packet, options = self.fresh()
                bind_context(packet, options['evidence_root'])
                setup(packet)
                attach_changed_review(packet, options['evidence_root'])
                state = run(packet, **options)
                self.assert_not_complete(state, 'blocked')
                self.assertIn(reason, state['reason'])
                self.assert_untouched(options)
        packet, options = self.fresh()
        bind_context(packet, options['evidence_root'])
        acknowledge(packet, decision='authorized_change', actor=ACTOR)
        attach_changed_review(packet, options['evidence_root'])
        state = run(packet, **options, intent_decisions=[operator_decision(packet)])
        self.assertEqual(state['status'], 'complete', state['reason'])
        self.assertEqual(len(state['intent_decisions']), 1)
        self.assertEqual(state['applied_fixes'][0]['intent_decision_ids'], [state['intent_decisions'][0]['id']])

    def test_completion_refuses_missing_stale_failing_duplicate_or_uncovered_review(self):
        duplicate = [dict(PRESERVED_ENTRY),
                     {**PRESERVED_ENTRY, 'evidence': '동일한 근거를 반복해도 증거가 되지 않는다.'}]
        cases = (
            ('no review', lambda p, r: None, 'blocked', 'no linked intent review'),
            ('wrong revision', lambda p, r: attach_review(p, r, review_payload(p, revision='f' * 64)),
             'unknown', 'stale, cross-round'),
            ('reordered run evidence', lambda p, r: attach_review(p, r, review_payload(p, run_ids=[])),
             'unknown', 'stale, cross-round'),
            ('predates replay', lambda p, r: attach_review(p, r, at='2026-09-14T00:04:30+00:00'),
             'unknown', 'predates its replay runs'),
            ('uncovered constraint', lambda p, r: attach_review(p, r, review_payload(p, results=[])),
             'unknown', 'does not cover applicable'),
            ('duplicate coverage', lambda p, r: attach_review(p, r, review_payload(p, results=duplicate)),
             'unknown', 'duplicates'),
            ('contradicting outcome',
             lambda p, r: attach_review(p, r, review_payload(p, results=[dict(CHANGED_ENTRY)])),
             'unknown', 'contradicts'),
            ('empty evidence',
             lambda p, r: attach_review(p, r, review_payload(p, results=[{**PRESERVED_ENTRY, 'evidence': '  '}])),
             'unknown', 'lacks concrete replay evidence'),
            ('run outside this replay',
             lambda p, r: attach_review(p, r, review_payload(
                 p, results=[{**PRESERVED_ENTRY, 'run_id': 'baseline-1',
                              'evidence': '수정 전 실행으로는 보존을 확인할 수 없다.'}])),
             'unknown', 'outside this round'),
        )
        for label, attach, status, reason in cases:
            with self.subTest(label=label):
                packet, options = self.fresh()
                bind_context(packet, options['evidence_root'])
                acknowledge(packet)
                attach(packet, options['evidence_root'])
                state = run(packet, **options)
                self.assert_not_complete(state, status)
                self.assertEqual(state['phase'], 'replay')
                self.assertIn(reason, state['reason'])
                self.assertEqual(state['accepted_fix_ids'], [])  # patch may exist, acceptance never happens

    def test_goal_binding_cannot_be_downgraded_or_replaced_on_resume(self):
        bind_context(self.packet, self.evidence_root)
        acknowledge(self.packet)
        attach_review(self.packet, self.evidence_root)
        self.assert_not_complete(self.go(pause_after='browser'), 'interrupted')
        for mutate in (lambda p: p['goal'].pop('product_context_artifact_id'),
                       lambda p: p['goal'].update(product_context_artifact_id='artifact-context-2')):
            downgrade = copy.deepcopy(self.packet)
            mutate(downgrade)
            with self.assertRaises(ContractError):
                run(downgrade, self.checkpoint)
        self.assertEqual(load(self.checkpoint)['packet']['goal']['product_context_artifact_id'],
                         'artifact-context')
        resumed = run(None, self.checkpoint)
        self.assertEqual(resumed['status'], 'complete', resumed['reason'])
        self.assertEqual(resumed['accepted_fix_ids'], ['fix-1'])

    def test_no_change_round_and_retry_still_require_intent_evidence(self):
        for label, review, expected in (('empty review', [], 'unknown'),
                                        ('full review', [{**PRESERVED_ENTRY, 'fix_id': None}], 'complete'),
                                        ('no review', None, 'blocked')):
            with self.subTest(label=label):
                packet, options = self.fresh()
                make_no_change(packet, options['evidence_root'])
                bind_context(packet, options['evidence_root'])
                if review is not None:
                    attach_review(packet, options['evidence_root'], review_payload(packet, results=review, fix_ids=()))
                state = run(packet, **options)
                self.assertEqual(state['status'], expected, state['reason'])
                self.assertEqual(state['applied_fixes'], [])
                self.assertEqual(state['accepted_fix_ids'], [])
                self.assert_untouched(options)

        for label, with_review, expected in (('fresh round-2 review', True, 'complete'),
                                             ('no round-2 review', False, 'blocked')):
            with self.subTest(label=label):
                packet, options = self.fresh('failed_visual')
                bind_context(packet, options['evidence_root'])
                acknowledge(packet)
                attach_review(packet, options['evidence_root'])
                self.assert_not_complete(run(packet, **options), 'failed')  # round 1 keeps its own review
                newer = append_recovery_round(packet, options['evidence_root'])
                newer['replays'][1].pop('intent_review_artifact_id', None)
                if with_review:
                    newer['replays'][1]['intent_review_artifact_id'] = _add_artifact(
                        newer, options['evidence_root'], 'artifact-intent-review-2', 'intent_review',
                        {'kind': 'intent_review', 'replay_id': 'replay-set-2',
                         'product_context_artifact_id': 'artifact-context',
                         'product_context_sha256': next(a['sha256'] for a in newer['artifacts'] if a['id'] == 'artifact-context'),
                         'code_revision': newer['replays'][1]['regression']['code_revision'],
                         'run_ids': ['replay-2'], 'fix_ids': ['fix-1'],
                         'constraint_results': [{**PRESERVED_ENTRY, 'run_id': 'replay-2'}],
                         'conflict_results': []}, REVIEW2_AT)
                state = run(newer, **dict(options, retry=True))
                if expected == 'complete':
                    self.assertEqual(state['status'], 'complete', state['reason'])
                    self.assertEqual(state['iteration'], 2)
                    self.assertEqual(state['accepted_fix_ids'], ['fix-1'])
                else:
                    self.assert_not_complete(state, 'blocked')
                    self.assertIn('no linked intent review', state['reason'])

    def test_packets_without_binding_keep_v1_behavior(self):
        self.assertEqual(validate_packet(self.packet), [])
        state = self.go()
        self.assertEqual(state['status'], 'complete', state['reason'])
        self.assertIsNone(report(state)['product_context'])
        self.assertFalse(report(state)['intent_verified'])
        self.assertIn('Legacy packet', report(state)['limitations'][-1])
        self.assertIn('상품 상세 보기', (self.workspace / 'index.html').read_text())

        acks_only = copy.deepcopy(self.packet)
        acknowledge(acks_only)
        self.assertTrue(any('the goal product_context_artifact_id binding' in x
                            for x in validate_packet(acks_only)))
        review_only = copy.deepcopy(self.packet)
        attach_review(review_only, self.evidence_root)
        self.assertTrue(any('the goal product_context_artifact_id binding' in x
                            for x in validate_packet(review_only)))
        wrong_kind = copy.deepcopy(self.packet)
        wrong_kind['goal']['product_context_artifact_id'] = 'artifact-figma'
        self.assertTrue(any('wrong artifact kind' in x for x in validate_packet(wrong_kind)))
        unknown = copy.deepcopy(self.packet)
        unknown['goal']['product_context_artifact_id'] = 'artifact-missing'
        self.assertTrue(any('unknown record' in x for x in validate_packet(unknown)))


    def test_provider_conflict_claim_is_not_operator_authority(self):
        bind_context(self.packet, self.evidence_root, context_payload(conflicts=[CONFLICT]))
        acknowledge(self.packet)
        resolve_conflicts(self.packet, actor='provider-agent')
        attach_review(self.packet, self.evidence_root, review_payload(self.packet, conflict_results=[CONFLICT_ENTRY]))
        state = self.go()
        self.assert_not_complete(state, 'blocked')
        self.assertIn('specific operator intent decision', state['reason'])
        self.assertEqual((self.workspace / 'index.html').read_text(), self.original)
        resumed = run(None, self.checkpoint, intent_decisions=[operator_decision(self.packet, 'conflict-label')],
                      actor=ACTOR, reason='Explicitly settle this conflict in this context')
        self.assertEqual(resumed['status'], 'complete', resumed['reason'])
        self.assertEqual(load(self.checkpoint)['intent_decisions'], resumed['intent_decisions'])
        self.assertEqual(report(resumed)['product_context']['unresolved_conflicts'], [])
        self.assertEqual(report(resumed)['product_context']['resolved_conflict_ids'], ['conflict-label'])

    def test_operator_decisions_are_bound_and_not_retroactive(self):
        mutations = [lambda d: d.update(context_artifact_id='foreign'),
                     lambda d: d.update(context_sha256='f' * 64),
                     lambda d: d.update(fix_id='foreign'),
                     lambda d: d.update(constraint_id='foreign'),
                     lambda d: d.update(decision='preserve'),
                     lambda d: d.update(decided_at='2026-09-01T00:00:00Z'),
                     lambda d: d.update(decided_at='2030-01-01T00:00:00Z'),
                     lambda d: d.update(decided_at='not-a-date'),
                     lambda d: d.update(reference=[])]
        for mutate in mutations:
            packet, options = self.fresh()
            bind_context(packet, options['evidence_root'])
            acknowledge(packet, decision='authorized_change')
            decision = operator_decision(packet)
            mutate(decision)
            with self.assertRaises(ContractError):
                run(packet, **options, intent_decisions=[decision])
            self.assert_untouched(options)
        bind_context(self.packet, self.evidence_root)
        acknowledge(self.packet)
        attach_review(self.packet, self.evidence_root)
        self.assertEqual(self.go()['status'], 'complete')
        with self.assertRaisesRegex(ContractError, 'retroactively'):
            run(None, self.checkpoint, intent_decisions=[operator_decision(self.packet)], actor=ACTOR, reason=REASON)

    def test_malformed_context_types_and_dates_stop_before_write(self):
        for field in ('status', 'kind', 'source_id', 'checked_at', 'decision_date', 'path_scenarios', 'constraints'):
            for bad in ([], {}, False, 2, None, 'not-a-date'):
                with self.subTest(field=field, bad=bad):
                    packet, options = self.fresh()
                    ctx = context_payload()
                    if field == 'status': ctx['memory_search']['status'] = bad
                    elif field == 'kind': ctx['sources'][0]['kind'] = bad
                    elif field == 'source_id': ctx['constraints'][0]['source_id'] = bad
                    elif field == 'checked_at': ctx['sources'][0]['checked_at'] = bad
                    elif field == 'decision_date': ctx['constraints'][0]['decision_date'] = bad
                    else: ctx[field] = bad
                    bind_context(packet, options['evidence_root'], ctx)
                    acknowledge(packet)
                    state = run(packet, **options)
                    # Empty constraints list is valid intake, but cannot approve a foreign acknowledgement.
                    self.assert_not_complete(state, 'blocked')
                    self.assert_untouched(options)
                    self.assertEqual(load(options['checkpoint'])['status'], 'blocked')

    def test_context_dates_must_follow_declared_order(self):
        for field in ('source-after-context', 'decision-after-source', 'future-context'):
            packet, options = self.fresh()
            ctx = context_payload()
            if field == 'source-after-context': ctx['sources'][0]['checked_at'] = '2026-09-15'
            if field == 'decision-after-source': ctx['constraints'][0]['decision_date'] = '2026-09-14'
            bind_context(packet, options['evidence_root'], ctx,
                         at='2030-01-01T00:00:00Z' if field == 'future-context' else CONTEXT_AT)
            acknowledge(packet)
            state = run(packet, **options)
            self.assert_not_complete(state, 'blocked')
            self.assert_untouched(options)

    def test_malformed_review_types_have_durable_unknown_state(self):
        for field in ('fix_id', 'constraint_id', 'run_id', 'constraint_results', 'conflict_results'):
            for bad in ([], {}, False, 3, None):
                if field == 'fix_id' and bad is None:
                    continue  # null is valid for unchanged goal-scope constraints, but foreign here.
                with self.subTest(field=field, bad=bad):
                    packet, options = self.fresh()
                    bind_context(packet, options['evidence_root'])
                    acknowledge(packet)
                    payload = review_payload(packet)
                    if field.endswith('_results'): payload[field] = bad
                    else: payload['constraint_results'][0][field] = bad
                    attach_review(packet, options['evidence_root'], payload)
                    state = run(packet, **options)
                    # An empty conflict list is the correct shape for this context.
                    expected = 'complete' if field == 'conflict_results' and bad == [] else 'unknown'
                    self.assertEqual(state['status'], expected, state['reason'])
                    self.assertEqual(load(options['checkpoint'])['status'], expected)
                    if expected == 'unknown': self.assertEqual(state['accepted_fix_ids'], [])

    def test_two_scenarios_require_two_reviews_and_path_scope_rejects_other_screen(self):
        for case in ('missing-second', 'both-covered', 'foreign-screen', 'path-covered'):
            with self.subTest(case=case):
                packet, options = self.fresh()
                add_second_scenario(packet, options['evidence_root'])
                ctx = context_payload()
                ctx['constraints'][0]['scope']['scenario_ids'] = (
                    ['scenario-1', 'scenario-2'] if case in ('missing-second', 'both-covered') else [])
                bind_context(packet, options['evidence_root'], ctx)
                acknowledge(packet)
                rows = [dict(PRESERVED_ENTRY)]
                if case == 'both-covered': rows.append({**PRESERVED_ENTRY, 'run_id': 'replay-2'})
                if case == 'foreign-screen': rows[0]['run_id'] = 'replay-2'
                attach_review(packet, options['evidence_root'], review_payload(packet, results=rows))
                state = run(packet, **options)
                self.assertEqual(state['status'], 'complete' if case in ('both-covered', 'path-covered') else 'unknown', state['reason'])

    def test_unchanged_constraints_remain_required_after_another_fix(self):
        for include in (False, True):
            packet, options = self.fresh()
            add_second_scenario(packet, options['evidence_root'])
            ctx = context_payload()
            ctx['constraints'].append({**ctx['constraints'][0], 'id': 'checkout-rule',
                                       'scope': {'scenario_ids': ['scenario-2']}})
            bind_context(packet, options['evidence_root'], ctx)
            acknowledge(packet)
            rows = [dict(PRESERVED_ENTRY)]
            if include: rows.append({**PRESERVED_ENTRY, 'fix_id': None, 'constraint_id': 'checkout-rule', 'run_id': 'replay-2'})
            attach_review(packet, options['evidence_root'], review_payload(packet, results=rows))
            state = run(packet, **options)
            self.assertEqual(state['status'], 'complete' if include else 'unknown', state['reason'])

    def test_no_edit_empty_context_cannot_complete(self):
        make_no_change(self.packet, self.evidence_root)
        ctx = context_payload()
        ctx['constraints'] = []
        bind_context(self.packet, self.evidence_root, ctx)
        attach_review(self.packet, self.evidence_root, review_payload(self.packet, results=[], fix_ids=()))
        state = self.go()
        self.assert_not_complete(state, 'blocked')
        self.assertIn('empty review cannot complete', state['reason'])

    def test_default_improvement_cli_requires_binding_and_records_operator_decision(self):
        packet_path = self.root / 'packet.json'
        cli = [sys.executable, str(SKILL / 'scripts/ux_loop.py'), 'improve', str(packet_path),
               '--workspace', str(self.workspace), '--evidence-root', str(self.evidence_root),
               '--checkpoint', str(self.checkpoint), '--grant', 'code_write', '--actor', ACTOR, '--reason', REASON]
        packet_path.write_text(json.dumps(self.packet))
        result = subprocess.run(cli, capture_output=True, text=True)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn('requires goal.product_context_artifact_id', result.stdout)
        self.assertFalse(self.checkpoint.exists())
        bind_context(self.packet, self.evidence_root)
        acknowledge(self.packet, decision='authorized_change')
        attach_changed_review(self.packet, self.evidence_root)
        packet_path.write_text(json.dumps(self.packet))
        decision_path = self.root / 'operator.json'
        decision_path.write_text(json.dumps([operator_decision(self.packet)]))
        result = subprocess.run(cli + ['--intent-decisions', str(decision_path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report_ = json.loads(result.stdout)
        self.assertTrue(report_['intent_verified'])
        self.assertFalse(report_['product_complete'])
        self.assertEqual(len(report_['intent_decisions']), 1)

    def test_old_checkpoint_loads_without_new_decision_ledger(self):
        from uxloop.storage import save
        state = self.go(pause_after='browser')
        state.pop('intent_decisions')
        save(self.checkpoint, state)
        resumed = run(None, self.checkpoint)
        self.assertEqual(resumed['status'], 'complete', resumed['reason'])
        self.assertFalse(report(resumed)['intent_verified'])


    def test_shared_path_changes_require_other_scenarios_intent_before_write(self):
        for kind in ('constraint', 'conflict'):
            packet, options = self.fresh()
            add_second_scenario(packet, options['evidence_root'])
            ctx = context_payload()
            ctx['path_scenarios']['index.html'] = ['scenario-1', 'scenario-2']
            ctx['constraints'][0]['scope'] = {'scenario_ids': ['scenario-2']}
            if kind == 'conflict':
                ctx['constraints'] = []
                ctx['conflicts'] = [{**CONFLICT, 'scope': {'scenario_ids': ['scenario-2']}}]
            bind_context(packet, options['evidence_root'], ctx)
            # Finding is scenario-1, but its changed file also serves scenario-2.
            state = run(packet, **options)
            self.assert_not_complete(state, 'blocked')
            self.assertEqual(state['phase'], 'fix')
            self.assert_untouched(options)

    def test_malformed_persisted_operator_decisions_never_traceback_or_write(self):
        from uxloop.storage import save
        for malformed in ({}, {'id': []}, {'recorded_at': 'not-a-date'}):
            packet, options = self.fresh()
            bind_context(packet, options['evidence_root'])
            acknowledge(packet)
            state = run(packet, **options, pause_after='browser')
            state['intent_decisions'] = [malformed]
            save(options['checkpoint'], state)
            with self.assertRaisesRegex(ContractError, 'Malformed operator intent decision'):
                run(None, options['checkpoint'])
            self.assert_untouched(options)


    def test_conflicted_queue_preserves_revision_order_and_allows_independent_patch(self):
        for independent in (False, True):
            packet, options = self.fresh()
            root, workspace = options['evidence_root'], options['workspace']
            original = (workspace / 'index.html').read_text()
            fixed = original.replace('>다음</a>', '>상품 상세 보기</a>')
            (workspace / 'checkout.html').write_text(original)
            packet['goal']['code_paths'] = ['index.html', 'checkout.html']
            before = digest({'index.html': original, 'checkout.html': original})
            first_after = digest({'index.html': fixed, 'checkout.html': original})
            second_after = digest({'index.html': fixed, 'checkout.html': fixed})
            for run_ in packet['browser_runs']:
                run_['code_revision'] = before if run_['phase'] == 'baseline' else second_after
            packet['replays'][0]['regression']['code_revision'] = second_after
            for artifact in packet['artifacts']:
                if artifact['kind'] in {'code_patch', 'screenshot', 'figma_readback'}: continue
                value = json.loads((root / artifact['path']).read_text())
                if 'code_revision' in value:
                    revision = before if value.get('run_id') == 'baseline-1' else second_after
                    replace_artifact(packet, root, artifact['id'], lambda v, r=revision: v.update(code_revision=r))
            first = packet['fixes'][0]
            first.update(before_revision=before, after_revision=first_after)
            records = packet['bundle']['records']
            records['findings'].append({**copy.deepcopy(records['findings'][0]), 'id': 'finding-2', 'severity': 'P2'})
            records['proposals'].append({**copy.deepcopy(records['proposals'][0]), 'id': 'proposal-2', 'finding_ids': ['finding-2']})
            second = {**copy.deepcopy(first), 'id': 'fix-2', 'proposal_id': 'proposal-2', 'finding_ids': ['finding-2'],
                      'changed_paths': ['checkout.html'], 'patch_artifact_id': 'artifact-patch-2',
                      'before_revision': before if independent else first_after,
                      'after_revision': digest({'index.html': original, 'checkout.html': fixed}) if independent else second_after}
            raw = ''.join(difflib.unified_diff(original.splitlines(True), fixed.splitlines(True),
                                              fromfile='a/checkout.html', tofile='b/checkout.html')).encode()
            (root / 'artifacts/patch-2.patch').write_bytes(raw)
            packet['artifacts'].append({'id': 'artifact-patch-2', 'path': 'artifacts/patch-2.patch', 'sha256': sha(raw),
                                        'kind': 'code_patch', 'provenance': 'fixture', 'created_at': CONTEXT_AT})
            packet['fixes'].append(second)
            packet['rounds'][0]['fix_ids'].append('fix-2')
            ctx = context_payload(conflicts=[CONFLICT])
            ctx['constraints'] = []
            bind_context(packet, root, ctx)
            state = run(packet, **options)
            self.assert_not_complete(state, 'blocked')
            self.assertEqual((workspace / 'index.html').read_text(), original)
            self.assertEqual((workspace / 'checkout.html').read_text(), fixed if independent else original)
            self.assertEqual([x['fix_id'] for x in state['applied_fixes']], ['fix-2'] if independent else [])
            if not independent: self.assertIn('preserve its reviewed patch order', state['reason'])


    def test_unmapped_changed_path_conservatively_protects_all_goal_scenarios(self):
        for kind in ('constraint', 'conflict'):
            for mapping in ({}, None):
                packet, options = self.fresh()
                add_second_scenario(packet, options['evidence_root'])
                ctx = context_payload()
                if mapping is None: ctx.pop('path_scenarios')
                else: ctx['path_scenarios'] = mapping
                ctx['constraints'][0]['scope'] = {'scenario_ids': ['scenario-2']}
                if kind == 'conflict':
                    ctx['constraints'] = []
                    ctx['conflicts'] = [{**CONFLICT, 'scope': {'scenario_ids': ['scenario-2']}}]
                bind_context(packet, options['evidence_root'], ctx)
                state = run(packet, **options)
                self.assert_not_complete(state, 'blocked')
                self.assertEqual(state['phase'], 'fix')
                self.assert_untouched(options)


if __name__ == '__main__':
    unittest.main()
