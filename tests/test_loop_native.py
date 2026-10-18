"""Native identity contract regressions. Fixtures do not prove app execution."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from loop_factory import make_packet, replace_artifact, SKILL
from uxloop.engine import run, report
from test_loop_product_context import bind_context, attach_review, acknowledge
from uxloop.contracts import validate_packet
from uxloop.io import ContractError, digest, safe_relative, within

class NativeContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.packet = make_packet(self.root)

    def native(self, platform='ios', app_id='com.example.preview'):
        packet = copy.deepcopy(self.packet)
        origin = platform + '-app://' + app_id
        for scenario in packet['scenarios']:
            scenario['origin'] = origin
        for run in packet['browser_runs']:
            scenario = next(s for s in packet['scenarios'] if s['id'] == run['scenario_id'])
            run['environment']['origin'] = origin
            run['scenario_digest'] = digest(scenario)
            run['tool'] = dict(name='XCUITest' if platform == 'ios' else 'UIAutomator',
                               version='27.0', platform=platform, os_version='27.0', application_id=app_id)
        for run in packet['bundle']['records']['runs']:
            run['surface_ref'] = origin + packet['scenarios'][0]['route']
        return packet

    def test_web_contract_remains_valid(self):
        self.assertEqual(validate_packet(self.packet), [])
        del self.packet['browser_runs'][0]['tool']['browser']
        self.assertTrue(validate_packet(self.packet))

    def test_ios_and_android_identity(self):
        for platform in ('ios', 'android'):
            self.assertEqual(validate_packet(self.native(platform)), [])

    def test_native_identity_cannot_be_omitted_or_mixed(self):
        for key in ('platform', 'os_version', 'application_id'):
            packet = self.native()
            del packet['browser_runs'][0]['tool'][key]
            self.assertTrue(validate_packet(packet), key)
        for key, value in [('application_id', 'com.other.app'), ('platform', 'android'),
                           ('browser', 'Safari'), ('browser_version', '27')]:
            packet = self.native()
            packet['browser_runs'][0]['tool'][key] = value
            self.assertTrue(validate_packet(packet), key)

    def test_native_origin_rejects_credential_port_path_and_malformed_ids(self):
        for app_id in ('user@com.example.app', 'com.example.app:80', 'com.example.app/x',
                       'com.example.app?q=x', 'com.example.app#x', 'com', '[', 'com.%65xample.app'):
            self.assertTrue(validate_packet(self.native(app_id=app_id)), app_id)

    def test_native_does_not_waive_unexecuted_accessibility(self):
        packet = self.native()
        packet['scenarios'][0]['a11y_checks'].remove('keyboard')
        self.assertTrue(validate_packet(packet))
        packet = self.native()
        packet['browser_runs'][0]['accessibility'].pop()
        self.assertTrue(validate_packet(packet))

    def test_raw_native_origin_is_not_normalized_into_an_identity(self):
        for app_id in ('com.exam\tple.preview', 'com.example.preview\n',
                       'com.example.preview?', 'com.example.preview#'):
            packet = self.native(app_id=app_id)
            for item in packet['browser_runs']:
                item['tool']['application_id'] = 'com.example.preview'
            self.assertTrue(validate_packet(packet), repr(app_id))

    def engine_packet(self):
        packet = self.native()
        scenario_digest = digest(packet['scenarios'][0])
        for artifact in packet['artifacts']:
            if artifact['path'].endswith('.json'):
                payload = json.loads((self.root / artifact['path']).read_text())
                if 'scenario_digest' in payload:
                    replace_artifact(packet, self.root, artifact['id'],
                                     lambda value: value.update(scenario_digest=scenario_digest))
        bind_context(packet, self.root)
        acknowledge(packet)
        attach_review(packet, self.root)
        workspace = self.root / 'workspace'
        workspace.mkdir()
        shutil.copy2(SKILL / 'examples/loop/site/index.html', workspace / 'index.html')
        return packet, workspace

    def execute(self, packet, workspace):
        return run(packet, self.root / 'checkpoint.json', workspace, self.root,
                   grants=['code_write'], actor='test-supervisor', reason='Synthetic native contract test only')

    def test_native_receipts_replay_and_intent_review_reach_fixture_completion(self):
        packet, workspace = self.engine_packet()
        state = self.execute(packet, workspace)
        self.assertEqual(state['status'], 'complete', state['reason'])
        self.assertTrue(report(state)['intent_verified'])
        self.assertFalse(report(state)['product_complete'])

    def test_unknown_keyboard_receipt_prevents_engine_completion(self):
        packet, workspace = self.engine_packet()
        replay = packet['browser_runs'][1]
        replay['accessibility'][0].update(status='unknown', detail='Keyboard was not executed')
        replace_artifact(packet, self.root, replay['accessibility'][0]['artifact_id'],
                         lambda value: value.update(results=replay['accessibility']))
        state = self.execute(packet, workspace)
        self.assertNotEqual(state['status'], 'complete')
        self.assertFalse(report(state)['product_complete'])
        self.assertIn('Accessibility', state['reason'])

    def test_blocked_keyboard_without_receipt_prevents_engine_completion(self):
        packet, workspace = self.engine_packet()
        packet['browser_runs'][0]['accessibility'][0].update(
            status='blocked', detail='Keyboard access unavailable', artifact_id=None)
        state = self.execute(packet, workspace)
        self.assertEqual(state['status'], 'blocked', state['reason'])
        self.assertFalse(report(state)['product_complete'])

    def test_native_replay_without_intent_review_is_blocked(self):
        packet, workspace = self.engine_packet()
        packet['replays'][0].pop('intent_review_artifact_id')
        state = self.execute(packet, workspace)
        self.assertNotEqual(state['status'], 'complete')
        self.assertFalse(report(state)['intent_verified'])

    def test_real_swift_paths_and_existing_path_guards(self):
        for name in ('AppModel+Demo.swift', 'ClubSession+Actions.swift'):
            self.assertEqual(safe_relative('apps/ios/' + name), 'apps/ios/' + name)
        for name in ('../App+X.swift', '/App+X.swift', 'a//App+X.swift', '.git/App+X.swift',
                     'a/../App+X.swift', 'a/./App+X.swift', 'a\\App+X.swift', 'a;App+X.swift', 'a b.swift'):
            with self.assertRaises(ContractError, msg=name):
                safe_relative(name)
        outside = self.root / 'outside'
        outside.mkdir()
        workspace = self.root / 'workspace'
        workspace.mkdir()
        (workspace / 'Linked+Source').symlink_to(outside)
        with self.assertRaises(ContractError):
            within(workspace, 'Linked+Source/File.swift')

if __name__ == '__main__':
    unittest.main()
