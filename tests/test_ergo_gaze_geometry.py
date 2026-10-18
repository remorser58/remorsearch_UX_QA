"""Region identity, display-ray geometry and evidence limits for gaze v3."""

from __future__ import annotations

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import _paths  # noqa: F401
from ergoqa import analyze, bundle, checks, params, swarm
from ergoqa.devices import mm_per_css_px
from ergoqa.hf import gaze
from ergoqa.snapshot import validate_snapshot
from ergoqa.profiles import sample_profiles
from test_ergo_fixes import ctx, el
from test_ergo_pipeline import make_run


class RayGeometry(unittest.TestCase):
    def test_symmetric_rays_and_legacy_call(self) -> None:
        a, b, eye = (-100, 0), (100, 0), (0, 0)
        expected = math.degrees(2 * math.atan2(100, 300))
        self.assertAlmostEqual(gaze.angular_separation_mm(a, b, 300, eye), expected)
        self.assertAlmostEqual(gaze.angular_separation_mm(b, a, 300, eye), expected)
        self.assertAlmostEqual(gaze.eccentricity_deg(a, b, 300), math.degrees(math.atan2(200, 300)))
        self.assertEqual(gaze.angular_separation_mm(a, a, 300, eye), 0)

    def test_independent_axes_and_resolution_invariance(self) -> None:
        horizontal = gaze.angular_separation_css((0, 0), (100, 0), 0.2, 0.4, 300, (0, 0))
        vertical = gaze.angular_separation_css((0, 0), (0, 100), 0.2, 0.4, 300, (0, 0))
        self.assertGreater(vertical, horizontal)
        a, b, eye = (20, 740), (330, 30), (180, 390)
        angle = gaze.angular_separation_css(a, b, 0.18, 0.19, 300, eye)
        self.assertAlmostEqual(angle, gaze.angular_separation_css(
            tuple(v * 2 for v in a), tuple(v * 2 for v in b), 0.09, 0.095, 300, tuple(v * 2 for v in eye)))
        self.assertAlmostEqual(angle, gaze.angular_separation_css(a, b, 0.36, 0.38, 600, eye))
        # Swap wide/tall axes and the physical scales: the same display rays.
        self.assertAlmostEqual(angle, gaze.angular_separation_css(a[::-1], b[::-1], 0.19, 0.18, 300, eye[::-1]))

    def test_invalid_geometry_abstains_and_large_finite_rays_work(self) -> None:
        for value in (0, -1, float('nan'), float('inf'), True, '300'):
            with self.subTest(value=value):
                self.assertIsNone(gaze.angular_separation_mm((0, 0), (1, 1), value))
                self.assertIsNone(gaze.angular_separation_css((0, 0), (1, 1), value, 0.2, 300, (0, 0)))
        self.assertIsNone(gaze.angular_separation_mm((float('nan'), 0), (1, 1), 300))
        self.assertIsNone(gaze.angular_separation_mm((0, 0), (1, 1), 300, (float('inf'), 0)))
        self.assertAlmostEqual(gaze.angular_separation_mm((-1e200, 0), (1e200, 0), 1e200, (0, 0)), 90)


class VisualRegions(unittest.TestCase):
    def setUp(self) -> None:
        self.primary = el('primary', 'button', (20, 500, 150, 48), text='계속', interactive=True, roles=('primary',), dom_id='continue')
        self.other = el('other', 'button', (20, 100, 150, 48), text='이전', interactive=True, dom_id='back')
        self.viewport = (360, 780)

    def sample(self, elements, priorities):
        return gaze.sample_equivalent_fixations(elements, priorities, self.viewport, (90, 230), 0.18, 300,
                                                mm_per_css_px_y=0.19, eye_css=(180, 390), n_runs=120, n_fix=4)

    def test_dom_aliases_share_hits_without_diluting_other_regions(self) -> None:
        original, hits = self.sample([self.primary, self.other], {'primary': 0.6, 'other': 1})
        aliases = [dict(self.primary, id=f'alias-{i}', selector=f'#api-{i}') for i in range(4)]
        regions, aliased_hits = self.sample([self.other, *aliases], {**{e['id']: 0.6 for e in aliases}, 'other': 1})
        self.assertEqual(len(regions), len(original))
        self.assertEqual(aliased_hits['other'], hits['other'])
        for alias in aliases:
            self.assertEqual(aliased_hits[alias['id']], hits['primary'])
        self.assertEqual(len(gaze.predicted_scanpath([*aliases, self.other], {**{e['id']: 0.6 for e in aliases}, 'other': 1}, self.viewport)), 2)

    def test_order_and_unrelated_ids_do_not_change_hits(self) -> None:
        _, a = self.sample([self.primary, self.other], {'primary': 0.6, 'other': 1})
        renamed = [dict(self.other, id='zz'), dict(self.primary, id='aa')]
        _, b = self.sample(renamed, {'zz': 1, 'aa': 0.6})
        self.assertEqual(a['primary'], b['aa'])
        self.assertEqual(a['other'], b['zz'])
        _, reverse = self.sample(list(reversed(renamed)), {'aa': 0.6, 'zz': 1})
        self.assertEqual(b, reverse)

    def test_distinct_overlapping_or_nested_controls_remain_distinct(self) -> None:
        peer = dict(self.primary, id='peer', selector='#peer', dom_id='peer')
        nested = dict(peer, ancestor_ids=['continue'])
        for other in (peer, nested, dict(peer, box={'x': 25, 'y': 500, 'w': 150, 'h': 48})):
            self.assertEqual(len(gaze.equivalent_regions([self.primary, other], self.viewport)), 2)
        label = dict(self.primary, id='label', selector='#label', dom_id='label', role='paragraph',
                     interactive=False, ancestor_ids=['continue'])
        self.assertEqual(len(gaze.equivalent_regions([label, self.primary], self.viewport)), 1)

    def test_invalid_hidden_zero_and_offscreen_boxes_never_become_regions(self) -> None:
        invalid = [dict(self.other, id='hidden', visible=False), dict(self.other, id='offscreen', in_viewport=False),
                   dict(self.other, id='zero', box={'x': 0, 'y': 0, 'w': 0, 'h': 20}),
                   dict(self.other, id='nan', box={'x': float('nan'), 'y': 0, 'w': 100, 'h': 20}),
                   dict(self.other, id='outside', box={'x': 400, 'y': 0, 'w': 100, 'h': 20})]
        self.assertEqual(gaze.equivalent_regions(invalid, self.viewport), [])
        self.assertEqual(gaze.element_priorities(invalid, self.viewport, 'mobile'), {})
        self.assertEqual(gaze.fixation_probabilities({'a': (0, 0)}, {'a': 1}, (0, 0), 0, 300), {})
        self.assertEqual(gaze.fixation_probabilities({'a': (0, 0)}, {'a': 1}, (0, 0), 0.2, 300, n_runs=0), {})

    def test_viewport_intersection_controls_size_cue(self) -> None:
        cropped = dict(self.other, id='crop', box={'x': 20, 'y': -24, 'w': 150, 'h': 48})
        visible = dict(cropped, box={'x': 20, 'y': 0, 'w': 150, 'h': 24})
        self.assertEqual(gaze.clipped_visible_box(cropped, self.viewport), (20, 0, 150, 24))
        a = gaze.element_priorities([cropped, self.primary], self.viewport, 'mobile')
        b = gaze.element_priorities([visible, self.primary], self.viewport, 'mobile')
        self.assertEqual(a, b)

    def test_competitors_count_distinct_regions_and_thresholds_stay(self) -> None:
        aliases = [dict(self.other, id=f'alias-{i}', selector=f'#api-{i}') for i in range(4)]
        with patch.object(checks, '_priorities', return_value={'primary': 0.2, **{e['id']: 1 for e in aliases}}):
            observations = checks.check_gaze(ctx([self.primary, *aliases]))
        competitor = next(o for o in observations if o.check_id == 'GZ-04')
        self.assertEqual(competitor.measurement['value'], 1)
        self.assertEqual(competitor.measurement['threshold'], params.GAZE_COMPETITORS_MAX)
        self.assertTrue(competitor.passed)


class EvidenceLimits(unittest.TestCase):
    def test_gz01_records_simulation_and_unmeasured_anchor(self) -> None:
        primary = el('p', 'button', (10, 500, 200, 48), text='계속', interactive=True, roles=('primary',))
        for focus, basis in ((None, gaze.START_PRIOR_PEAK), ({'x': 100, 'y': 500}, gaze.START_LAST_ACTION)):
            record = next(o for o in checks.check_gaze(ctx([primary], focus=focus)) if o.check_id == 'GZ-01')
            m = record.measurement
            self.assertEqual(m['unit'], 'simulation_hit_fraction')
            self.assertEqual(m['model_version'], gaze.MODEL_ID)
            self.assertEqual(m['n_runs'], params.GAZE_MC_RUNS)
            self.assertEqual(m['n_fix'], params.GAZE_MC_FIXATIONS)
            self.assertEqual(m['start_basis'], basis)
            self.assertFalse(m['measured_gaze'])
            self.assertFalse(m['calibrated'])
            self.assertEqual(m['threshold'], params.GAZE_PRIMARY_P2)
            self.assertEqual(m['reference_target'], params.GAZE_PRIMARY_PASS)

    def test_gz02_uses_last_action_to_nearest_feedback_ray(self) -> None:
        stable = el('stable', 'paragraph', (10, 10, 100, 30), text='유지')
        message = el('msg', 'status', (100, 400, 250, 60), text='저장됨', roles=('status',))
        focus = {'x': 80, 'y': 420}
        c = ctx([stable, message], previous={'surface': {'url': 'http://x/a'}, 'elements': [stable]}, focus=focus)
        record = next(o for o in checks.check_gaze(c) if o.check_id == 'GZ-02')
        expected = gaze.angular_separation_css((80, 420), (100, 420), mm_per_css_px(c.device, 'x'),
                                               mm_per_css_px(c.device, 'y'), checks._viewing_distance(c), (180, 390))
        self.assertEqual(record.measurement['value'], round(expected, 1))
        self.assertEqual(record.measurement['nearest_feedback_css'], [100, 420])
        self.assertEqual(record.measurement['anchor_basis'], gaze.START_LAST_ACTION)
        self.assertEqual(record.measurement['eye_projection'], gaze.EYE_PROJECTION)

    def test_clipped_primary_abstains_and_preserves_non_gaze_geometry(self) -> None:
        primary = el('p', 'button', (10, 100, 180, 48), text='계속', interactive=True, roles=('primary',))
        clipped = dict(primary, visible_box={'x': 10, 'y': 100, 'w': 180, 'h': 2}, visible_geometry='ancestor_clipped')
        record = next(o for o in checks.check_gaze(ctx([clipped])) if o.check_id == 'GZ-01')
        self.assertIsNone(record.measurement['value'])
        self.assertFalse(record.passed)
        self.assertIsNone(record.severity)
        self.assertEqual(record.extra['verdict'], 'inconclusive')
        for check in (checks.check_target_size, checks.check_reach):
            self.assertEqual([o.to_dict(0) for o in check(ctx([primary]))], [o.to_dict(0) for o in check(ctx([clipped]))])
        legacy = dict(primary, paint={'gaps': ['clipped_paint']})
        self.assertEqual(gaze.element_priorities([legacy], (360, 780), 'mobile'), {})

    def test_optional_visible_geometry_is_finite_and_legacy_is_valid(self) -> None:
        doc = json.loads((Path(__file__).parent / 'fixtures/ergo/sample_snapshot.json').read_text())
        self.assertEqual(validate_snapshot(doc), [])
        for box, status in (({'x': 0, 'y': 0, 'w': float('nan'), 'h': 2}, 'ancestor_clipped'),
                            (None, 'measured'), ({'x': 0, 'y': 0, 'w': 10, 'h': 2}, 'empty')):
            malformed = copy.deepcopy(doc)
            malformed['elements'][0].update(visible_box=box, visible_geometry=status)
            self.assertTrue(validate_snapshot(malformed))

    def test_clipped_feedback_survives_as_a_limit_with_no_aggregate_finding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = make_run(Path(temporary))
            file = run / 'S-R-1-001.json'
            doc = json.loads(file.read_text())
            message = next(e for e in doc['elements'] if e['id'] == 'error')
            message.update(visible_geometry='ancestor_clipped', visible_box={**message['box'], 'h': 2})
            file.write_text(json.dumps(doc))
            profiles = sample_profiles(14, 3, ['galaxy-s24'])
            result = analyze.analyze_run(run, profiles)
            gap = next(o for o in result['observations'] if o['check_id'] == 'GZ-02')
            self.assertEqual(gap['extra']['verdict'], 'inconclusive')
            self.assertIsNone(gap['measurement']['value'])
            self.assertFalse(gap['passed'])
            self.assertTrue(any('GZ-02' in line and '보류' in line for line in result['limitations']))
            findings = swarm.aggregate([result], profiles)
            self.assertFalse(any(f['check_id'] == 'GZ-02' for f in findings))
            output = bundle.to_evidence_bundle('gaze-clipping', [result], findings, profiles)
            self.assertFalse(any(o['check_id'] == 'GZ-02' for o in output['records']['observations']))
            self.assertTrue(any('GZ-02' in line for line in output['notes']['limitations']))

    def test_attachment_preserves_clipped_limit_and_capture_receipts(self) -> None:
        from ergoqa.qa_attach import attach_run
        from validate_bundle import validate_bundle
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run = make_run(root)
            # Keep a bounded run with one unclipped primary, then new clipped status.
            for file in run.glob('S-*.json'):
                doc = json.loads(file.read_text())
                doc['elements'] = [e for e in doc['elements'] if e['id'] == 'pay' or e['id'] == 'error']
                for message in doc['elements']:
                    if message['id'] == 'error':
                        message.update(visible_geometry='ancestor_clipped', visible_box={**message['box'], 'h': 2})
                file.write_text(json.dumps(doc))
            profiles = sample_profiles(3, 7, ['galaxy-s24'])
            qa = json.loads((Path(__file__).parent / 'fixtures/valid-bundle.json').read_text())
            qa['records']['findings'][0]['severity'] = 'P2'
            output = attach_run(qa, run, profiles, {'scenario-1': 'EP-01'}, receipts_root=root / 'receipts', gaze_enabled=False)
            self.assertEqual(validate_bundle(output, artifacts_root=root / 'receipts'), [])
            self.assertEqual(output['notes']['ergo_attach']['capture_count'], 2)
            self.assertTrue(any('GZ-02' in line for line in output['notes']['ergo_attach']['limitations']))
            self.assertFalse(any(o.get('check_id') == 'GZ-02' for o in output['records']['observations']))


class FeedbackFocusRelocation(unittest.TestCase):
    def context(self):
        phone = el('phone', 'textbox', (16, 430, 352, 48), interactive=True, dom_id='phone', tag='input')
        field = el('name', 'textbox', (16, 136, 352, 48), interactive=True, dom_id='name', tag='input',
                   a11y={'invalid': True, 'described_by': ['name-error'], 'focusable': True})
        button = el('next', 'button', (16, 760, 352, 52), text='다음', interactive=True,
                    dom_id='next', tag='button', roles=('primary',))
        error = el('name-error', 'alert', (16, 190, 352, 22.5), text='성명을 입력해 주세요.',
                   dom_id='name-error', roles=('error_message',), fg='#d32f2f', weight=600)
        previous = {'snapshot_id': 'B', 'surface': {'url': 'http://x/a'}, 'focus': {'on_body': False, 'dom_id': 'phone'},
                    'elements': [phone, field, button]}
        step = {'action': {'action': 'tap', 'target': '#next'}, 'result': 'ok', 'target_element_id': 'next',
                'before': 'B', 'after': 'S-1', 'point': {'x': 192, 'y': 786}}
        c = ctx([phone, field, button, error], device_id='galaxy-s24-ultra', previous=previous, step=step,
                focus={'x': 192, 'y': 786})
        c.snapshot['focus'] = {'on_body': False, 'dom_id': 'name'}
        return c

    def feedback(self, c, selector='#name-error'):
        return next(o for o in checks.check_gaze(c) if o.check_id == 'GZ-02' and o.element_key.startswith(selector + '|'))

    def test_observed_field_transfer_reanchors_only_feedback_and_preserves_input(self) -> None:
        c = self.context()
        original = copy.deepcopy(c.step)
        record = self.feedback(c)
        self.assertEqual(record.measurement['value'], 1.1)
        self.assertIsNone(record.severity)
        self.assertEqual(record.measurement['anchor_basis'], 'observed_programmatic_focus_relocation')
        self.assertEqual(record.measurement['anchor_css'], [192, 160])
        self.assertEqual(record.measurement['input_anchor_css'], [192, 786])
        self.assertEqual(record.measurement['feedback_focus_relation'], 'aria-describedby')
        self.assertFalse(record.measurement['measured_gaze'])
        primary = next(o for o in checks.check_gaze(c) if o.check_id == 'GZ-01')
        self.assertEqual(primary.measurement['anchor_css'], [192, 786])
        self.assertEqual(primary.measurement['start_basis'], gaze.START_LAST_ACTION)
        self.assertEqual(c.step, original)

    def test_observed_body_to_field_is_supported_but_missing_focus_is_not(self) -> None:
        c = self.context()
        c.previous['focus'] = {'on_body': True, 'dom_id': None}
        self.assertEqual(self.feedback(c).measurement['anchor_basis'], 'observed_programmatic_focus_relocation')
        c.previous.pop('focus')
        self.assertEqual(self.feedback(c).measurement['anchor_basis'], gaze.START_LAST_ACTION)

    def test_unchanged_unrelated_ambiguous_hidden_and_wrong_frame_focus_keep_input(self) -> None:
        for variant in ('unchanged', 'unrelated', 'duplicate', 'hidden', 'clipped', 'missing_after', 'wrong_frame', 'failed_action'):
            with self.subTest(variant=variant):
                c = self.context()
                field = next(e for e in c.elements if e['id'] == 'name')
                if variant == 'unchanged': c.previous['focus']['dom_id'] = 'name'
                if variant == 'unrelated': field['a11y']['described_by'] = ['other-error']
                if variant == 'duplicate': c.snapshot['elements'].append(dict(field, id='duplicate'))
                if variant == 'hidden': field['visible'] = False
                if variant == 'clipped': field.update(visible_geometry='ancestor_clipped', visible_box={**field['box'], 'h': 2})
                if variant == 'missing_after': c.snapshot.pop('focus')
                if variant == 'wrong_frame': c.step['after'] = 'another-frame'
                if variant == 'failed_action': c.step['result'] = 'error'
                record = self.feedback(c)
                self.assertEqual(record.measurement['anchor_basis'], gaze.START_LAST_ACTION)
                self.assertEqual(record.measurement['value'], 20.4)
                self.assertEqual(record.severity, 'P2')

    def test_native_error_message_association_must_be_applicable(self) -> None:
        c = self.context()
        field = next(e for e in c.elements if e['id'] == 'name')
        field['a11y'] = {'invalid': True, 'error_message': 'name-error'}
        self.assertEqual(self.feedback(c).measurement['feedback_focus_relation'], 'aria-errormessage')
        field['a11y']['invalid'] = False
        self.assertEqual(self.feedback(c).measurement['anchor_basis'], gaze.START_LAST_ACTION)

    def test_unrelated_feedback_does_not_inherit_or_get_suppressed_by_field_anchor(self) -> None:
        c = self.context()
        c.snapshot['elements'].append(el('independent', 'alert', (16, 20, 352, 22), text='별도 오류입니다.',
                             dom_id='independent', roles=('error_message',), fg='#d32f2f', weight=600))
        record = self.feedback(c, '#independent')
        self.assertEqual(record.measurement['anchor_basis'], gaze.START_LAST_ACTION)
        self.assertEqual(record.severity, 'P2')
        self.assertFalse(record.measurement['redundant_with_noticed_feedback'])

    def test_offscreen_error_remains_directly_flagged(self) -> None:
        c = self.context()
        error = next(e for e in c.elements if e['id'] == 'name-error')
        error.update(box={**error['box'], 'y': 950}, in_viewport=False)
        record = self.feedback(c)
        self.assertEqual(record.severity, 'P1')
        self.assertEqual(record.measurement['band'], 'offscreen')

    def test_redundancy_requires_same_anchor_basis_and_point_in_both_directions(self) -> None:
        # The linked error is far from its field; a status beside the old input
        # cannot substitute for it. A status beside that same field can.
        for mode, y, linked, redundant in (('input', 760, False, False), ('field', 190, True, True)):
            with self.subTest(mode=mode):
                c = self.context()
                error = next(e for e in c.elements if e['id'] == 'name-error')
                error['box']['y'] = 650
                status = el('notice', 'status', (16, y, 352, 22), text='완료 상태', dom_id='notice',
                            roles=('status',), fg='#d32f2f', weight=600)
                c.snapshot['elements'].append(status)
                if linked:
                    next(e for e in c.elements if e['id'] == 'name')['a11y']['described_by'].append('notice')
                record = self.feedback(c)
                self.assertEqual(record.measurement['redundant_with_noticed_feedback'], redundant)
                self.assertEqual(record.severity, None if redundant else 'P3')
                self.assertEqual(record.measurement['anchor_css'], [192, 160])
        # Preserve redundancy when both messages use the original input anchor.
        c = self.context()
        c.previous['focus']['dom_id'] = 'name'
        c.snapshot['elements'].append(el('notice', 'status', (16, 760, 352, 22), text='완료 상태',
                                       dom_id='notice', roles=('status',), fg='#d32f2f', weight=600))
        self.assertTrue(self.feedback(c).measurement['redundant_with_noticed_feedback'])

    def test_same_anchor_basis_with_different_points_is_not_redundant(self) -> None:
        c = self.context()
        next(e for e in c.elements if e['id'] == 'name-error')['box']['y'] = 650
        c.snapshot['elements'].append(el('notice', 'status', (16, 190, 352, 22), text='완료 상태',
                                       dom_id='notice', roles=('status',), fg='#d32f2f', weight=600))
        field_anchor = checks._feedback_focus_anchor
        def distinct_point(context, feedback):
            if feedback['id'] == 'notice':
                return (192, 180), {'anchor_basis': 'observed_programmatic_focus_relocation'}
            return field_anchor(context, feedback)
        with patch.object(checks, '_feedback_focus_anchor', side_effect=distinct_point):
            record = self.feedback(c)
        self.assertFalse(record.measurement['redundant_with_noticed_feedback'])
        self.assertEqual(record.severity, 'P3')

    def test_keyboard_and_direct_field_pointer_keep_original_semantics(self) -> None:
        for kind in ('keyboard', 'field', 'label'):
            with self.subTest(kind=kind):
                c = self.context()
                if kind == 'keyboard': c.step['action']['action'] = 'press'
                if kind == 'field':
                    c.step['target_element_id'] = 'name'
                    c.step['action']['target'] = '#name'
                if kind == 'label':
                    label = el('label', 'label', (16, 110, 352, 22), interactive=True, dom_id='label', tag='label')
                    c.previous['elements'].append(label)
                    c.step['target_element_id'] = 'label'
                self.assertEqual(self.feedback(c).measurement['anchor_basis'], gaze.START_LAST_ACTION)

    def test_thumb_occlusion_retains_physical_input_anchor(self) -> None:
        c = self.context()
        with patch.object(checks.reach, 'occluded_by_thumb', return_value=False) as occlusion:
            self.feedback(c)
        self.assertEqual(occlusion.call_args.args[0], checks._point_mm(c, 192, 786))


if __name__ == '__main__':
    unittest.main()
