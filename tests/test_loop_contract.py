import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from loop_factory import ROOT, SKILL, make_packet, replace_artifact, write_json
from scripts.validate_bundle import validate_bundle
from uxloop.contracts import merge_packet, validate_packet
from uxloop.io import ContractError, parse_json, safe_relative
from uxloop.schema import validate


class ContractTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.ux-loop').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.ux-loop')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.packet = make_packet(self.root)

    def test_happy_contract_is_valid(self):
        self.assertEqual(validate_packet(self.packet), [])

    def test_all_stop_conditions_are_mandatory_true(self):
        for condition in self.packet['goal']['stop_conditions']:
            packet = copy.deepcopy(self.packet)
            packet['goal']['stop_conditions'][condition] = False
            self.assertTrue(validate_packet(packet), condition)

    def test_budgets_are_bounded_integers_not_booleans(self):
        for value in (True, False, 0, -1, 11, '10', [], {}):
            packet = copy.deepcopy(self.packet)
            packet['goal']['max_iterations'] = value
            self.assertTrue(validate_packet(packet), repr(value))

    def test_unsafe_paths_are_rejected(self):
        for value in ('../outside', '/absolute', 'a/../../b', 'a//b', '.git/config', '.ux-loop/state', 'a\\b', 'a b'):
            with self.assertRaises(ContractError, msg=value):
                safe_relative(value)

    def test_unknown_root_field_cannot_inject_a_command(self):
        self.packet['command'] = 'touch NEVER_EXECUTE'
        self.assertTrue(validate_packet(self.packet))
        self.assertFalse((self.root / 'NEVER_EXECUTE').exists())

    def test_extra_record_groups_rejected_without_traceback(self):
        self.packet['bundle']['records']['unknown'] = [None, {}]
        self.assertTrue(validate_packet(self.packet))

    def test_duplicate_new_ids_rejected(self):
        for name in ('artifacts', 'browser_runs', 'visual_checks', 'fixes', 'rounds', 'replays'):
            packet = copy.deepcopy(self.packet)
            packet[name].append(copy.deepcopy(packet[name][0]))
            self.assertTrue(validate_packet(packet), name)

    def test_stale_or_changed_scenario_is_rejected(self):
        self.packet['scenarios'][0]['steps'][0]['action'] = 'Do a different task'
        self.assertTrue(any('digest' in x for x in validate_packet(self.packet)))

    def test_route_device_fixture_changes_are_rejected(self):
        for field in ('route', 'device', 'fixture_revision', 'account_ref'):
            packet = copy.deepcopy(self.packet)
            packet['browser_runs'][1]['environment'][field] = 'wrong'
            self.assertTrue(validate_packet(packet), field)

    def test_malformed_origin_has_no_traceback(self):
        self.packet['scenarios'][0]['origin'] = 'https://['
        self.assertTrue(validate_packet(self.packet))

    def test_figma_version_conflict_rejected(self):
        self.packet['visual_checks'][1]['readback_version'] = 'different'
        self.assertTrue(any('Figma' in x for x in validate_packet(self.packet)))

    def test_figma_url_alone_is_not_readback(self):
        self.packet['bundle']['records']['figma'][0]['readback_artifact_ref'] = 'https://figma.com/file/example'
        self.assertTrue(validate_packet(self.packet))

    def test_visual_pass_cannot_hide_side_accent_failure(self):
        self.packet['visual_checks'][1]['checks']['side_accents'] = 'failed'
        self.assertTrue(validate_packet(self.packet))

    def test_figma_baseline_is_required_only_by_a_figma_first_policy(self):
        self.packet['fixes'][0]['figma_id'] = None
        self.assertTrue(any('Figma-first policy' in x for x in validate_packet(self.packet)))
        self.packet['policy']['figma_first'] = False
        self.assertEqual(validate_packet(self.packet), [])

    def test_visual_pass_requires_all_six_semantic_checks(self):
        for field in ('alignment', 'spacing', 'typography', 'text_clipping', 'component_occlusion', 'figma_fidelity'):
            packet = copy.deepcopy(self.packet)
            packet['visual_checks'][1]['checks'].pop(field)
            self.assertTrue(validate_packet(packet), field)

    def test_optional_pixel_tolerance_is_schema_validated(self):
        check = self.packet['visual_checks'][1]
        check['method'] = 'pixel_diff'
        for tolerance in ({'channel_delta': 0, 'max_changed_fraction': 0},
                          {'channel_delta': 64, 'max_changed_fraction': 0.1}):
            check['tolerance'] = tolerance
            self.assertEqual(validate_packet(self.packet), [])
        for tolerance in (None, [], {}, {'channel_delta': 0}, {'channel_delta': True, 'max_changed_fraction': 0},
                          {'channel_delta': 65, 'max_changed_fraction': 0},
                          {'channel_delta': 0, 'max_changed_fraction': 0.11},
                          {'channel_delta': 0, 'max_changed_fraction': float('inf')},
                          {'channel_delta': 0, 'max_changed_fraction': 0, 'extra': True}):
            check['tolerance'] = tolerance
            self.assertTrue(validate_packet(self.packet), repr(tolerance))

    def test_cli_validate_admits_optional_pixel_tolerance(self):
        check = self.packet['visual_checks'][1]
        check.update(method='pixel_diff', tolerance={'channel_delta': 12, 'max_changed_fraction': 0.01})
        replace_artifact(self.packet, self.root, check['comparison_artifact_id'], lambda value: value.update(comparison=check))
        write_json(self.root / 'packet.json', self.packet)
        command = [sys.executable, str(SKILL / 'scripts/ux_loop.py'), 'validate', str(self.root / 'packet.json'),
                   '--evidence-root', str(self.root)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)['valid'])
        check['tolerance']['channel_delta'] = 65
        write_json(self.root / 'packet.json', self.packet)
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse(json.loads(result.stdout)['valid'])

    def test_run_pass_cannot_hide_step_failure(self):
        self.packet['browser_runs'][1]['steps'][0]['outcome'] = 'failed'
        self.assertTrue(validate_packet(self.packet))

    def test_steps_and_accessibility_must_cover_matrix(self):
        for field in ('steps', 'accessibility'):
            packet = copy.deepcopy(self.packet)
            packet['browser_runs'][1][field].pop()
            self.assertTrue(validate_packet(packet), field)

    def test_duplicate_sessions_rejected(self):
        self.packet['browser_runs'][1]['environment']['session_id'] = self.packet['browser_runs'][0]['environment']['session_id']
        self.assertTrue(validate_packet(self.packet))

    def test_fixture_evidence_cannot_enter_live_packet(self):
        self.packet['mode'] = 'live'
        self.assertTrue(validate_packet(self.packet))

    def test_cross_references_are_checked(self):
        self.packet['fixes'][0]['finding_ids'] = ['not-a-finding']
        self.assertTrue(validate_packet(self.packet))

    def test_changed_paths_are_scoped(self):
        self.packet['fixes'][0]['changed_paths'] = ['outside.html']
        self.assertTrue(validate_packet(self.packet))

    def test_regression_cannot_skip_scenarios(self):
        self.packet['replays'][0]['regression']['scenario_ids'] = ['other-scenario']
        self.assertTrue(validate_packet(self.packet))

    def test_raw_community_content_must_be_minimized(self):
        self.packet['bundle']['records']['evidence'][0]['excerpt'] = 'Raw source content should stay external.'
        self.assertTrue(validate_packet(self.packet))

    def test_community_cannot_verify_prevalence(self):
        claim = self.packet['bundle']['records']['claims'][0]
        claim.update({'claim_kind': 'prevalence', 'epistemic_status': 'observed', 'verification_status': 'verified'})
        self.assertTrue(any('preference or prevalence' in x for x in validate_packet(self.packet)))

    def test_goal_and_permission_metadata_cannot_change_on_resume(self):
        for mutate in (lambda x: x['goal'].update(objective='Changed goal'),
                       lambda x: x['bundle']['permissions']['requested'].append('code_write')):
            updated = copy.deepcopy(self.packet)
            mutate(updated)
            with self.assertRaises(ContractError):
                merge_packet(self.packet, updated)

    def test_existing_evidence_cannot_be_overwritten_deleted_or_reordered(self):
        for mutate in (lambda x: x['browser_runs'][1].update(operator='new operator'),
                       lambda x: x['visual_checks'].pop(), lambda x: x['artifacts'].reverse()):
            updated = copy.deepcopy(self.packet)
            mutate(updated)
            with self.assertRaises(ContractError):
                merge_packet(self.packet, updated)

    def test_malformed_legacy_fields_are_rejected_without_traceback(self):
        for group, name in [('findings', 'severity'), ('figma', 'readback_artifact_ref'),
                             ('figma', 'read_at'), ('figma', 'file_key'), ('runs', 'status')]:
            for value in ([], {}, None):
                packet = copy.deepcopy(self.packet)
                packet['bundle']['records'][group][0][name] = value
                self.assertTrue(validate_packet(packet), (group, name, value))

    def test_enormous_budget_is_rejected_without_float_overflow(self):
        self.packet['goal']['max_iterations'] = 10 ** 400
        self.assertTrue(validate_packet(self.packet))

    def test_all_sample_fields_handle_wrong_json_types_without_crashing(self):
        paths = []
        def collect(value, prefix=()):
            if isinstance(value, dict):
                for key, child in value.items():
                    paths.append(prefix + (key,))
                    collect(child, prefix + (key,))
            elif isinstance(value, list):
                for key, child in enumerate(value):
                    collect(child, prefix + (key,))
        collect(self.packet)
        for path in paths:
            for replacement in (None, [], {}):
                packet = copy.deepcopy(self.packet)
                parent = packet
                for key in path[:-1]:
                    parent = parent[key]
                parent[path[-1]] = replacement
                # Optional original-v1 metadata can be unconstrained. This test
                # asserts stable validation behavior, not that all variants fail.
                self.assertIsInstance(validate_packet(packet), list)

    def test_identical_packet_is_idempotent(self):
        self.assertEqual(merge_packet(self.packet, copy.deepcopy(self.packet)), self.packet)

    def test_duplicate_json_keys_and_nonfinite_values_rejected(self):
        for raw in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
            with self.assertRaises(ContractError):
                parse_json(raw)

    def test_schema_unsupported_keyword_is_not_silently_ignored(self):
        self.assertTrue(validate({}, {'type': 'object', 'madeUpValidator': True}))

    def test_v1_unhashable_values_are_rejected_without_traceback(self):
        original = json.loads((ROOT / 'tests/fixtures/valid-bundle.json').read_text())
        targets = [('evidence', 'source_id'), ('claims', 'persona_ids'), ('findings', 'observation_ids'),
                   ('figma', 'defect_class'), ('personas', 'basis'), ('sources', 'retention_status')]
        for group, field in targets:
            for bad in ([], {}, [None, {}], False):
                bundle = copy.deepcopy(original)
                bundle['records'][group][0][field] = bad
                self.assertTrue(validate_bundle(bundle), (group, field, bad))
        for key in ('requested', 'granted'):
            bundle = copy.deepcopy(original)
            bundle['permissions'][key] = [{}]
            self.assertTrue(validate_bundle(bundle))

    def test_v1_verified_finding_requires_observed_same_scenario_run(self):
        bundle = copy.deepcopy(self.packet['bundle'])
        bundle['records']['runs'][0]['status'] = 'blocked'
        self.assertTrue(any('completed same-scenario' in x for x in validate_bundle(bundle)))
        bundle = copy.deepcopy(self.packet['bundle'])
        bundle['records']['findings'][0]['epistemic_status'] = 'inferred'
        self.assertTrue(validate_bundle(bundle))


if __name__ == '__main__':
    unittest.main()
