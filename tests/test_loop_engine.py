import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from loop_factory import REPLAY_START, ROOT, SKILL, append_recovery_round, make_packet, replace_artifact
from uxloop.contracts import validate_packet
from uxloop.engine import create_state, report, run
from uxloop.io import ContractError, digest, load_json
from uxloop.patching import finish_intent
from uxloop.storage import event, load, lock


class LoopTests(unittest.TestCase):
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

    def go(self, **kwargs):
        options = {'grants': ['code_write'], 'actor': 'test-supervisor', 'reason': 'Approve only the isolated fixture site patch'}
        options.update(kwargs)
        return run(self.packet, self.checkpoint, self.workspace, self.evidence_root, **options)

    def assert_not_complete(self, state, status=None):
        if status:
            self.assertEqual(state['status'], status, state['reason'])
        self.assertNotEqual(state['status'], 'complete')
        self.assertEqual(state['accepted_fix_ids'], [])
        self.assertFalse(report(state)['product_complete'])
        self.assertEqual(report(state)['decision'], 'stop_without_completion')

    def test_happy_path_applies_real_text_patch_and_accepts_only_after_replay(self):
        state = self.go()
        self.assertEqual(state['status'], 'complete', state['reason'])
        self.assertEqual(state['accepted_fix_ids'], ['fix-1'])
        self.assertIn('상품 상세 보기', (self.workspace / 'index.html').read_text())
        self.assertEqual(report(state)['decision'], 'fixture_only_pass_not_product_verification')
        self.assertFalse(report(state)['product_complete'])
        self.assertFalse(report(state)['live_execution_performed_by_cli'])
        self.assertEqual(load(self.checkpoint)['run_id'], state['run_id'])

    def test_code_first_project_completes_without_figma(self):
        self.packet = make_packet(self.evidence_root, 'code_first')
        self.assertEqual(validate_packet(self.packet), [])
        state = self.go()
        self.assertEqual(state['status'], 'complete', state['reason'])
        self.assertEqual(state['accepted_fix_ids'], ['fix-1'])
        figma_first = copy.deepcopy(self.packet)
        figma_first['policy']['figma_first'] = True
        self.assertTrue(any('Figma-first policy' in x for x in validate_packet(figma_first)))

    def test_blocked_permission_never_modifies_code(self):
        self.packet = make_packet(self.evidence_root, 'blocked_permission')
        state = self.go(grants=[])
        self.assert_not_complete(state, 'blocked')
        self.assertIn('requires explicit code_write', state['reason'])
        self.assertNotIn('code_write', state['permissions'])
        self.assertEqual((self.workspace / 'index.html').read_text(), self.original)

    def test_interruption_resume_preserves_ids_permissions_and_run_id(self):
        state = self.go(pause_after='browser')
        self.assert_not_complete(state, 'interrupted')
        original_permissions = copy.deepcopy(state['permissions'])
        ids = report(state)['evidence_ids']
        resumed = run(None, self.checkpoint)
        self.assertEqual(resumed['status'], 'complete', resumed['reason'])
        self.assertEqual(resumed['run_id'], state['run_id'])
        self.assertEqual(resumed['permissions'], original_permissions)
        self.assertEqual(report(resumed)['evidence_ids'], ids)
        self.assertEqual(len(resumed['applied_fixes']), 1)

    def test_fix_is_not_accepted_at_patch_checkpoint(self):
        state = self.go(pause_after='fix')
        self.assert_not_complete(state, 'interrupted')
        self.assertEqual([x['fix_id'] for x in state['applied_fixes']], ['fix-1'])
        self.assertIn('상품 상세 보기', (self.workspace / 'index.html').read_text())

    def test_crash_between_code_write_and_receipt_is_resumable_and_idempotent(self):
        def finish_then_interrupt(workspace, intent):
            finish_intent(workspace, intent)
            raise KeyboardInterrupt()
        with patch('uxloop.engine.finish_intent', side_effect=finish_then_interrupt):
            state = self.go()
        self.assert_not_complete(state, 'interrupted')
        self.assertIsNotNone(state['pending_intent'])
        self.assertEqual(state['applied_fixes'], [])
        self.assertIn('상품 상세 보기', (self.workspace / 'index.html').read_text())
        resumed = run(None, self.checkpoint)
        self.assertEqual(resumed['status'], 'complete', resumed['reason'])
        self.assertIsNone(resumed['pending_intent'])
        self.assertEqual(len(resumed['applied_fixes']), 1)
        resumed_again = run(None, self.checkpoint)
        self.assertEqual(len(resumed_again['applied_fixes']), 1)

    def test_failed_visual_comparison_cannot_complete(self):
        self.packet = make_packet(self.evidence_root, 'failed_visual')
        state = self.go()
        self.assert_not_complete(state, 'failed')
        self.assertIn('Visual comparison failed', state['reason'])
        self.assertEqual(len(state['applied_fixes']), 1)

    def test_unknown_required_research_cannot_complete_or_fix(self):
        self.packet = make_packet(self.evidence_root, 'unknown_evidence')
        state = self.go()
        self.assert_not_complete(state, 'unknown')
        self.assertEqual(state['phase'], 'research')
        self.assertEqual((self.workspace / 'index.html').read_text(), self.original)

    def test_regression_failure_cannot_complete(self):
        self.packet = make_packet(self.evidence_root, 'regression_failure')
        state = self.go()
        self.assert_not_complete(state, 'failed')
        self.assertIn('Regression is failed', state['reason'])

    def test_missing_live_browser_is_explicitly_blocked(self):
        self.packet = make_packet(self.evidence_root, 'missing_browser')
        state = self.go()
        self.assert_not_complete(state, 'blocked')
        self.assertEqual(state['phase'], 'browser')
        self.assertIn('no live browser launcher is configured', state['reason'])

    def test_missing_replay_receipt_is_blocked_after_fix(self):
        self.packet['replays'] = []
        state = self.go()
        self.assert_not_complete(state, 'blocked')
        self.assertEqual(state['phase'], 'replay')
        self.assertIn('No replay receipt', state['reason'])
        self.assertEqual(len(state['applied_fixes']), 1)

    def test_append_missing_replay_after_patch_then_resume(self):
        complete_packet = copy.deepcopy(self.packet)
        self.packet['replays'] = []
        state = self.go()
        self.assert_not_complete(state, 'blocked')
        resumed = run(complete_packet, self.checkpoint)
        self.assertEqual(resumed['status'], 'complete', resumed['reason'])
        self.assertEqual(len(resumed['applied_fixes']), 1)
        self.assertEqual(resumed['permissions'], state['permissions'])

    def test_unknown_browser_run_cannot_be_completed(self):
        run_ = self.packet['browser_runs'][0]
        run_.update(outcome='unknown', epistemic_status='unknown', reason='Browser did not execute')
        records = self.packet['bundle']['records']
        records['runs'][0]['status'] = 'unknown'
        records['findings'][0]['verification_status'] = 'unverified'
        records['findings'][0]['epistemic_status'] = 'unknown'
        records['observations'][0]['epistemic_status'] = 'unknown'
        self.assertEqual(validate_packet(self.packet), [])
        self.assert_not_complete(self.go(), 'unknown')

    def test_unknown_visual_check_cannot_complete(self):
        self.packet['visual_checks'][1].update(status='unknown', reason='No usable comparison')
        self.assert_not_complete(self.go(), 'unknown')

    def test_keyboard_failure_cannot_complete(self):
        run_ = self.packet['browser_runs'][1]
        run_['accessibility'][0].update(status='failed', detail='Keyboard trap')
        replace_artifact(self.packet, self.evidence_root, 'artifact-replay-a11y', lambda x: x.update(results=run_['accessibility']))
        self.assert_not_complete(self.go(), 'failed')

    def test_unexpected_network_errors_cannot_complete(self):
        replace_artifact(self.packet, self.evidence_root, 'artifact-replay-network', lambda x: x.update(unexpected_errors=['Unexpected 500']))
        self.assert_not_complete(self.go(), 'failed')

    def test_lying_regression_receipt_is_unknown_not_success(self):
        replace_artifact(self.packet, self.evidence_root, 'artifact-regression', lambda x: x.update(failed_checks=['Unreported failure']))
        self.assert_not_complete(self.go(), 'unknown')

    def test_cross_run_console_artifact_is_unknown(self):
        replace_artifact(self.packet, self.evidence_root, 'artifact-replay-console', lambda x: x.update(run_id='baseline-1'))
        self.assert_not_complete(self.go(), 'unknown')

    def test_stale_replay_revision_cannot_complete(self):
        self.packet['browser_runs'][1]['code_revision'] = 'f' * 64
        self.assert_not_complete(self.go(), 'unknown')

    def test_missing_or_corrupt_figma_blocks_before_write(self):
        path = self.evidence_root / 'artifacts/artifact-figma.json'
        path.unlink()
        self.assert_not_complete(self.go(), 'blocked')
        self.assertEqual((self.workspace / 'index.html').read_text(), self.original)

    def test_screenshot_without_comparison_cannot_complete(self):
        self.packet['visual_checks'] = [self.packet['visual_checks'][0]]
        self.assert_not_complete(self.go(), 'blocked')

    def test_comparison_may_follow_its_run(self):
        # Figma-first QA draws the target after the baseline run, so that comparison is written later.
        artifacts = {x['id']: x for x in self.packet['artifacts']}
        artifacts['artifact-baseline-visual']['created_at'] = '2026-09-14T00:02:30+00:00'
        state = self.go()
        self.assertEqual(state['status'], 'complete', state['reason'])

    def test_comparison_cannot_predate_its_capture(self):
        artifacts = {x['id']: x for x in self.packet['artifacts']}
        artifacts['artifact-replay-visual']['created_at'] = REPLAY_START
        state = self.go()
        self.assert_not_complete(state, 'unknown')
        self.assertIn('predates its capture or reference export', state['reason'])

    def test_false_editable_figma_cannot_become_success(self):
        replace_artifact(self.packet, self.evidence_root, 'artifact-figma', lambda x: x.update(editable=False))
        self.assert_not_complete(self.go(), 'unknown')
        self.assertEqual((self.workspace / 'index.html').read_text(), self.original)

    def test_design_and_test_data_actions_block_even_when_granted_without_adapter(self):
        for kind in ('design_write', 'test_data_write'):
            with self.subTest(kind=kind):
                if self.checkpoint.exists():
                    self.checkpoint.unlink()
                self.packet['fixes'][0]['kind'] = kind
                state = self.go(grants=[kind])
                self.assert_not_complete(state, 'blocked')
                self.assertIn('integration is not implemented', state['reason'])
                self.assertEqual((self.workspace / 'index.html').read_text(), self.original)

    def test_grant_requires_named_operator_and_reason(self):
        with self.assertRaises(ContractError):
            self.go(actor='')
        self.assertFalse(self.checkpoint.exists())
        self.assertEqual((self.workspace / 'index.html').read_text(), self.original)

    def test_revocation_after_interruption_prevents_write_then_explicit_grant_resumes(self):
        self.go(pause_after='browser')
        blocked = run(None, self.checkpoint, revokes=['code_write'], actor='operator', reason='Pause authorization')
        self.assert_not_complete(blocked, 'blocked')
        self.assertEqual((self.workspace / 'index.html').read_text(), self.original)
        resumed = run(None, self.checkpoint, grants=['code_write'], actor='operator', reason='Approve scoped change again')
        self.assertEqual(resumed['status'], 'complete', resumed['reason'])
        self.assertTrue(any(x['decision'] == 'revoke' for x in resumed['permission_events']))

    def test_workspace_drift_blocks_patch(self):
        state = self.go(pause_after='browser')
        (self.workspace / 'index.html').write_text(self.original + '<!-- concurrent edit -->\n')
        resumed = run(None, self.checkpoint)
        self.assert_not_complete(resumed, 'blocked')
        self.assertIn('Workspace drift', resumed['reason'])
        self.assertIn('concurrent edit', (self.workspace / 'index.html').read_text())

    def test_predicted_hash_mismatch_does_not_write(self):
        self.packet['fixes'][0]['after_revision'] = 'f' * 64
        self.assert_not_complete(self.go(), 'blocked')
        self.assertEqual((self.workspace / 'index.html').read_text(), self.original)

    def test_completion_is_revalidated_when_artifact_changes(self):
        self.go()
        (self.evidence_root / 'artifacts/artifact-replay-visual.json').write_text('{}')
        self.assert_not_complete(run(None, self.checkpoint), 'unknown')

    def test_completion_is_revalidated_when_source_changes(self):
        self.go()
        target = self.workspace / 'index.html'
        target.write_text(target.read_text() + '<!-- drift -->\n')
        self.assert_not_complete(run(None, self.checkpoint), 'unknown')

    def test_baseline_artifact_changed_during_pause_blocks_write(self):
        self.go(pause_after='browser')
        (self.evidence_root / 'artifacts/artifact-baseline-steps.json').write_text('{}')
        self.assert_not_complete(run(None, self.checkpoint), 'unknown')
        self.assertEqual((self.workspace / 'index.html').read_text(), self.original)

    def test_immutable_input_tamper_on_resume_is_rejected(self):
        self.go(pause_after='browser')
        modified = copy.deepcopy(self.packet)
        modified['goal']['objective'] = 'Different goal'
        with self.assertRaises(ContractError):
            run(modified, self.checkpoint)
        self.assertEqual(load(self.checkpoint)['packet'], self.packet)

    def test_checkpoint_corruption_cannot_be_reset_into_success(self):
        self.go(pause_after='browser')
        value = json.loads(self.checkpoint.read_text())
        value['status'] = 'complete'
        self.checkpoint.write_text(json.dumps(value))
        with self.assertRaises(ContractError):
            run(None, self.checkpoint)

    def test_failed_replay_does_not_auto_retry(self):
        self.packet = make_packet(self.evidence_root, 'failed_visual')
        state = self.go()
        resumed = run(None, self.checkpoint)
        self.assert_not_complete(resumed, 'failed')
        self.assertEqual(resumed['iteration'], 1)
        self.assertEqual(resumed['applied_fixes'], state['applied_fixes'])

    def test_iteration_limit_is_terminal_without_success(self):
        self.packet = make_packet(self.evidence_root, 'failed_visual')
        self.packet['goal']['max_iterations'] = 1
        self.go()
        state = run(None, self.checkpoint, retry=True)
        self.assert_not_complete(state, 'iteration_limit')
        self.assertEqual(run(None, self.checkpoint)['status'], 'iteration_limit')

    def test_bounded_step_budget_creates_resumable_interruption(self):
        state = self.go(max_steps=1)
        self.assert_not_complete(state, 'interrupted')
        self.assertEqual(state['phase'], 'plan')
        self.assertEqual(run(None, self.checkpoint)['status'], 'complete')

    def test_illegal_state_transitions_cannot_mark_complete(self):
        state = create_state(self.packet, self.workspace, self.evidence_root)
        with self.assertRaises(ContractError):
            event(state, 'decision', 'complete', 'Pretend done')
        with self.assertRaises(ContractError):
            event(state, 'replay', 'running', 'Skip all gates')

    def test_workspace_lock_blocks_concurrent_writer(self):
        from uxloop.io import GateStop
        with lock(self.workspace / '.ux-loop/workspace.lock'):
            with self.assertRaises(GateStop):
                self.go()
        self.assertEqual((self.workspace / 'index.html').read_text(), self.original)

    def test_symlink_artifacts_cannot_escape_evidence_root(self):
        path = self.evidence_root / 'artifacts/artifact-figma.json'
        original = path.read_bytes()
        outside = self.root / 'outside.json'
        outside.write_bytes(original)
        path.unlink()
        path.symlink_to(outside)
        self.assert_not_complete(self.go(), 'blocked')

    def test_cli_reports_nonzero_blocked_not_success(self):
        command = [sys.executable, str(SKILL / 'scripts/ux_loop.py'), 'run', str(self.evidence_root / 'packet.json'),
                   '--workspace', str(self.workspace), '--evidence-root', str(self.evidence_root), '--checkpoint', str(self.checkpoint)]
        process = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=10)
        self.assertEqual(process.returncode, 3, process.stdout + process.stderr)
        self.assertEqual(json.loads(process.stdout)['status'], 'blocked')

    def test_successful_second_round_preserves_failed_evidence_and_permissions(self):
        self.packet = make_packet(self.evidence_root, 'failed_visual')
        failed = self.go()
        newer = append_recovery_round(self.packet, self.evidence_root)
        self.assertEqual(validate_packet(newer), [])
        completed = run(newer, self.checkpoint, retry=True)
        self.assertEqual(completed['status'], 'complete', completed['reason'])
        self.assertEqual(completed['iteration'], 2)
        self.assertEqual(completed['permissions'], failed['permissions'])
        self.assertEqual(completed['packet']['visual_checks'][1]['status'], 'failed')
        self.assertEqual(completed['packet']['bundle']['records']['evidence'], failed['packet']['bundle']['records']['evidence'])
        self.assertEqual(completed['accepted_fix_ids'], ['fix-1'])

    def test_missing_scenario_matrix_cannot_complete(self):
        self.packet['rounds'][0]['baseline_run_ids'] = []
        self.assert_not_complete(self.go(), 'blocked')
        self.assertEqual((self.workspace / 'index.html').read_text(), self.original)

    def test_resume_report_cannot_overwrite_evidence_or_locks(self):
        self.go(pause_after='browser')
        artifact = self.evidence_root / 'artifacts/artifact-figma.json'
        original = artifact.read_bytes()
        for target in [artifact, self.checkpoint.with_suffix('.lock'), self.workspace / '.ux-loop/workspace.lock', self.workspace / 'index.html']:
            process = subprocess.run([sys.executable, str(SKILL / 'scripts/ux_loop.py'), 'resume',
                '--checkpoint', str(self.checkpoint), '--report', str(target)], cwd=ROOT,
                text=True, capture_output=True, timeout=10)
            self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
            self.assertNotIn('Traceback', process.stderr)
        self.assertEqual(artifact.read_bytes(), original)
        self.assertEqual((self.workspace / 'index.html').read_text(), self.original)

    def test_new_intake_invalidates_complete_before_save(self):
        self.go()
        newer = append_recovery_round(self.packet, self.evidence_root)
        from uxloop.storage import save as real_save
        snapshots = []
        def capture(path, state):
            snapshots.append(copy.deepcopy(state))
            real_save(path, state)
        with patch('uxloop.engine.save', side_effect=capture):
            state = run(newer, self.checkpoint)
        self.assertNotEqual(snapshots[0]['status'], 'complete')
        self.assertEqual(state['status'], 'complete')

    def test_cli_rejects_duplicate_json_keys(self):
        file = self.root / 'invalid.json'
        file.write_text('{"schema_version":"ux-loop.v1","schema_version":"unsafe"}')
        process = subprocess.run([sys.executable, str(SKILL / 'scripts/ux_loop.py'), 'validate', str(file)],
                                 cwd=ROOT, text=True, capture_output=True, timeout=10)
        self.assertEqual(process.returncode, 2)
        self.assertFalse(json.loads(process.stdout)['product_complete'])


if __name__ == '__main__':
    unittest.main()
