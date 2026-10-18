"""CLI-level invariants for bookkeeping only; fixtures do not prove live UX."""
import copy
import difflib
import json
import subprocess
import sys
import unittest
from functools import cached_property

from _paths import SKILL
from loop_fill_fixture import FillFixture
from uxloop.demo_factory import write_json
from test_loop_product_context import bind_context, acknowledge, attach_changed_review
from uxloop.io import digest, sha

KINDS = {'console', 'network', 'runtime', 'steps', 'accessibility', 'visual_report'}


class FillTests(unittest.TestCase):
    @cached_property
    def fixture(self) -> FillFixture:
        return FillFixture(self)

    def cli(self, *args):
        command = [sys.executable, str(SKILL / 'scripts/ux_loop.py'), *map(str, args)]
        print('COMMAND:', repr(command), flush=True)
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        print('EXIT:', result.returncode, 'STDOUT:', result.stdout, 'STDERR:', result.stderr, flush=True)
        return result.returncode, json.loads(result.stdout) if result.stdout else {}

    def prepare(self):
        for run in self.fixture.packet['browser_runs']:
            run['scenario_digest'] = '@auto'
        for run in self.fixture.packet['bundle']['records']['runs']:
            run.update(scenario_id='@auto', surface_ref='@auto')
        for fix in self.fixture.packet['fixes']:
            fix.update(before_revision='@auto', after_revision='@auto', changed_paths='@auto')
        for artifact in self.fixture.packet['artifacts']:
            artifact['sha256'] = '@auto'
            if artifact['kind'] in KINDS:
                path = self.fixture.evidence / artifact['path']
                payload = json.loads(path.read_text())
                payload.update({k: '@auto' for k in ('run_id', 'scenario_digest', 'code_revision', 'kind')})
                if artifact['kind'] in {'steps', 'accessibility'}:
                    payload['results'] = '@auto'
                if artifact['kind'] == 'visual_report':
                    payload['comparison'] = '@auto'
                write_json(path, payload)

    def fill(self, workspace=True):
        write_json(self.fixture.draft, self.fixture.packet)
        args = ['fill', self.fixture.draft, '--evidence-root', self.fixture.evidence, '--out', self.fixture.out]
        if workspace:
            args += ['--workspace', self.fixture.site]
        return self.cli(*args)

    def snapshot(self):
        return {str(p.relative_to(self.fixture.root)): p.read_bytes()
                for p in self.fixture.root.rglob('*') if p.is_file()}

    def refuse(self, workspace=True):
        write_json(self.fixture.draft, self.fixture.packet)
        before = self.snapshot()
        status, result = self.fill(workspace)
        self.assertEqual(status, 2, result)
        self.assertEqual(self.snapshot(), before)

    def test_fill_validate_and_real_fixture_patch(self):
        # Given host-authored evidence with only mechanical duplicates missing.
        before = (self.fixture.site / 'index.html').read_bytes()
        self.prepare()
        # When the public command fills and the existing engine executes it.
        status, result = self.fill()
        self.assertEqual(status, 0, result)
        filled = json.loads(self.fixture.out.read_text())
        self.assertEqual(filled, self.fixture.original)
        for path, raw in self.fixture.receipts.items():
            self.assertEqual((self.fixture.evidence / path).read_bytes(), raw)
        self.assertEqual((self.fixture.site / 'index.html').read_bytes(), before)
        self.assertTrue(result['filled'])
        self.assertTrue(all(x.startswith('/') for x in result['filled']))
        self.assertEqual(self.cli('validate', self.fixture.out, '--evidence-root', self.fixture.evidence)[0], 0)
        status, outcome = self.cli('run', self.fixture.out, '--workspace', self.fixture.site, '--evidence-root', self.fixture.evidence,
                                   '--checkpoint', self.fixture.root / 'checkpoint.json', '--grant', 'code_write',
                                   '--actor', 'fixture-supervisor', '--reason', 'isolated-fixture')
        # Then a real isolated text patch occurred without a product claim.
        self.assertEqual(status, 0, outcome)
        self.assertFalse(outcome['product_complete'])
        self.assertIn('상품 상세 보기', (self.fixture.site / 'index.html').read_text())

    def test_generic_grant_still_cannot_authorize_context_change(self):
        bind_context(self.fixture.packet, self.fixture.evidence)
        acknowledge(self.fixture.packet, decision='authorized_change', actor='fixture-supervisor')
        attach_changed_review(self.fixture.packet, self.fixture.evidence)
        before = (self.fixture.site / 'index.html').read_bytes()
        self.prepare()
        self.assertEqual(self.fill()[0], 0)
        status, outcome = self.cli('run', self.fixture.out, '--workspace', self.fixture.site, '--evidence-root', self.fixture.evidence,
                                   '--checkpoint', self.fixture.root / 'checkpoint.json', '--grant', 'code_write',
                                   '--actor', 'fixture-supervisor', '--reason', 'isolated-fixture')
        self.assertEqual(status, 3, outcome)
        self.assertFalse(outcome['product_complete'])
        self.assertEqual((self.fixture.site / 'index.html').read_bytes(), before)

    def test_sentinel_free_round_trip_preserves_exact_bytes(self):
        write_json(self.fixture.draft, self.fixture.packet)
        before = self.snapshot()
        status, result = self.fill(workspace=False)
        self.assertEqual(status, 0, result)
        self.assertEqual(result['filled'], [])
        self.assertEqual(self.fixture.out.read_bytes(), self.fixture.draft.read_bytes())
        self.fixture.out.unlink()
        self.assertEqual(self.snapshot(), before)

    def test_second_fill_is_idempotent(self):
        self.prepare()
        self.assertEqual(self.fill()[0], 0)
        first = self.fixture.out.read_bytes()
        self.fixture.packet = json.loads(first)
        self.fixture.out = self.fixture.evidence / 'second.json'
        before = {p: p.read_bytes() for p in (self.fixture.evidence / 'artifacts').iterdir()}
        status, result = self.fill()
        self.assertEqual(status, 0, result)
        self.assertEqual(result['filled'], [])
        self.assertEqual(json.loads(self.fixture.out.read_bytes()), json.loads(first))
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_forbidden_packet_sentinels_refuse_without_writes(self):
        for parent, key in [(self.fixture.packet['goal'], 'objective'), (self.fixture.packet['scenarios'][0], 'origin'),
                            (self.fixture.packet['browser_runs'][0], 'code_revision'),
                            (self.fixture.packet['browser_runs'][0], 'outcome'),
                            (self.fixture.packet['artifacts'][0], 'created_at')]:
            with self.subTest(key=key):
                old = parent[key]
                parent[key] = '@auto'
                self.refuse()
                parent[key] = old

    def test_payload_semantic_sentinel_and_hash_bound_rewrite_refuse(self):
        artifact = next(a for a in self.fixture.packet['artifacts'] if a['kind'] == 'console')
        path = self.fixture.evidence / artifact['path']
        original = path.read_bytes()
        for field in ('unexpected_errors', 'run_id'):
            with self.subTest(field=field):
                payload = json.loads(original)
                payload[field] = '@auto'
                write_json(path, payload)
                artifact['sha256'] = '@auto' if field == 'unexpected_errors' else sha(path.read_bytes())
                self.refuse()

    def test_fill_does_not_manufacture_inspection(self):
        artifact = next(a for a in self.fixture.packet['artifacts'] if a['kind'] == 'visual_report')
        path = self.fixture.evidence / artifact['path']
        original = json.loads(path.read_bytes())
        for key in ('image_tool', 'observations', 'viewed_artifact_ids'):
            with self.subTest(key=key):
                payload = copy.deepcopy(original)
                payload['inspection'][key] = '@auto'
                write_json(path, payload)
                artifact['sha256'] = '@auto'
                self.refuse()

    def test_ambiguous_missing_and_malformed_owners_refuse(self):
        self.prepare()
        original = copy.deepcopy(self.fixture.packet)
        for case in ('shared', 'duplicate', 'missing', 'malformed', 'revision', 'wrong-kind', 'orphan', 'visual'):
            with self.subTest(case=case):
                self.fixture.packet = copy.deepcopy(original)
                run = self.fixture.packet['browser_runs'][0]
                if case == 'shared':
                    self.fixture.packet['browser_runs'][1]['evidence']['console'] = run['evidence']['console']
                elif case == 'duplicate':
                    self.fixture.packet['browser_runs'].append(copy.deepcopy(run))
                elif case == 'missing':
                    run['scenario_id'] = 'missing'
                elif case == 'malformed':
                    run['steps'] = None
                elif case == 'revision':
                    run['code_revision'] = None
                elif case == 'wrong-kind':
                    run['evidence']['console'] = run['evidence']['runtime']
                elif case == 'orphan':
                    del run['evidence']['console']
                else:
                    self.fixture.packet['visual_checks'].append({**self.fixture.packet['visual_checks'][0], 'id': 'other'})
                self.refuse()

    def test_unsafe_and_colliding_paths_refuse(self):
        self.prepare()
        original = self.fixture.out
        for path in (self.fixture.draft, self.fixture.evidence / 'packet.json', self.fixture.site / 'new.json',
                     self.fixture.evidence / 'artifacts/artifact-baseline-console.json', self.fixture.root / 'outside.json',
                     self.fixture.evidence / 'artifacts/artifact-baseline-console.json/child.json',
                     self.fixture.evidence / '.ux-loop/checkpoint.json'):
            with self.subTest(path=path):
                self.fixture.out = path
                self.refuse()
        self.fixture.out = original
        linked = self.fixture.root / 'linked'
        linked.symlink_to(self.fixture.evidence, target_is_directory=True)
        self.fixture.out = linked / 'output.json'
        self.refuse()

    def test_missing_artifact_and_unsafe_artifact_refuse(self):
        artifact = self.fixture.packet['artifacts'][0]
        for path in ('artifacts/absent.json', '../outside.json'):
            artifact['path'] = path
            self.refuse()

    def test_patch_and_concrete_revision_mismatch_refuse(self):
        self.prepare()
        fix = self.fixture.packet['fixes'][0]
        for field, wrong in [('before_revision', '0' * 64), ('after_revision', '0' * 64),
                             ('changed_paths', ['other.html'])]:
            old = fix[field]
            fix[field] = wrong
            self.refuse()
            fix[field] = old
        patch = next(a for a in self.fixture.packet['artifacts'] if a['kind'] == 'code_patch')
        (self.fixture.evidence / patch['path']).write_text('--- a/index.html\n+++ b/index.html\n@@ -1 +1 @@\n-wrong\n+new\n')
        patch['sha256'] = '@auto'
        self.refuse()

    def test_late_forbidden_semantic_receipt_preserves_staged_payloads(self):
        self.prepare()
        artifact = next(a for a in self.fixture.packet['artifacts'] if a['kind'] == 'regression')
        path = self.fixture.evidence / artifact['path']
        payload = json.loads(path.read_text())
        payload['status'] = '@auto'
        write_json(path, payload)
        self.refuse()

    def test_requested_revisions_require_workspace(self):
        self.fixture.packet['fixes'][0]['after_revision'] = '@auto'
        self.refuse(workspace=False)

    def test_native_surface_is_derived_without_browser_identity_invention(self):
        for scenario in self.fixture.packet['scenarios']:
            scenario['origin'] = 'ios-app://com.example.product/'
        for run in self.fixture.packet['browser_runs']:
            run['environment']['origin'] = 'ios-app://com.example.product/'
            run['tool'] = dict(name='XCUITest', version='27', platform='ios', os_version='27',
                               application_id='com.example.product')
        self.prepare()
        status, result = self.fill()
        self.assertEqual(status, 0, result)
        packet = json.loads(self.fixture.out.read_text())
        self.assertEqual(packet['bundle']['records']['runs'][0]['surface_ref'], 'ios-app://com.example.product/product')

    def test_multiple_fixes_follow_declared_round_order(self):
        first = self.fixture.packet['fixes'][0]
        before = (self.fixture.site / 'index.html').read_text()
        middle = before.replace('>다음</a>', '>상품 상세 보기</a>')
        after = middle.replace('>상품 상세 보기</a>', '>자세히 보기</a>')
        patch = ''.join(difflib.unified_diff(middle.splitlines(True), after.splitlines(True),
                                           fromfile='a/index.html', tofile='b/index.html')).encode()
        artifact = {**next(a for a in self.fixture.packet['artifacts'] if a['kind'] == 'code_patch'),
                    'id': 'patch-2', 'path': 'artifacts/second.patch', 'sha256': sha(patch)}
        (self.fixture.evidence / artifact['path']).write_bytes(patch)
        self.fixture.packet['artifacts'].append(artifact)
        self.fixture.packet['fixes'].insert(0, {**first, 'id': 'fix-2', 'patch_artifact_id': 'patch-2',
                                       'before_revision': '@auto', 'after_revision': '@auto', 'changed_paths': '@auto'})
        self.fixture.packet['rounds'][0]['fix_ids'].append('fix-2')
        status, result = self.fill()
        self.assertEqual(status, 0, result)
        second = json.loads(self.fixture.out.read_text())['fixes'][0]
        self.assertEqual(second['before_revision'], digest({'index.html': middle}))
        self.assertEqual(second['after_revision'], digest({'index.html': after}))
        self.assertEqual((self.fixture.site / 'index.html').read_text(), before)

    def test_invalid_written_packet_is_not_acceptance(self):
        self.fixture.packet['policy']['raw_community_storage'] = True
        status, result = self.fill()
        self.assertEqual(status, 1, result)
        self.assertFalse(result['valid'])
        self.assertTrue(result['errors'])
        self.assertTrue(self.fixture.out.is_file())


if __name__ == '__main__':
    unittest.main()
