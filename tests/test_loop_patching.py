import difflib
import shutil
import tempfile
import unittest
from pathlib import Path

from loop_factory import ROOT
from uxloop.io import ContractError, GateStop, code_snapshot, digest
from uxloop.patching import apply_text_patch, finish_intent, plan_intent


class PatchTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.ux-loop').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.ux-loop')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_text_patch_matches_reviewed_content(self):
        patch = '--- a/page.html\n+++ b/page.html\n@@ -1 +1 @@\n-old\n+new\n'
        self.assertEqual(apply_text_patch({'page.html': 'old\n'}, patch), {'page.html': 'new\n'})

    def test_new_file_and_deletion_are_explicitly_supported(self):
        creation = '--- /dev/null\n+++ b/new.txt\n@@ -0,0 +1 @@\n+created\n'
        self.assertEqual(apply_text_patch({'new.txt': None}, creation), {'new.txt': 'created\n'})
        deletion = '--- a/old.txt\n+++ /dev/null\n@@ -1 +0,0 @@\n-deleted\n'
        self.assertEqual(apply_text_patch({'old.txt': 'deleted\n'}, deletion), {'old.txt': None})

    def test_no_final_newline_is_preserved(self):
        patch = '--- a/a.txt\n+++ b/a.txt\n@@ -1 +1 @@\n-old\n\\ No newline at end of file\n+new\n\\ No newline at end of file\n'
        self.assertEqual(apply_text_patch({'a.txt': 'old'}, patch), {'a.txt': 'new'})

    def test_multi_hunk_changes(self):
        old = ''.join(f'{x}\n' for x in range(30))
        new = old.replace('1\n', 'one\n', 1).replace('28\n', 'twenty-eight\n')
        patch = ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='a/a.txt', tofile='b/a.txt'))
        self.assertEqual(apply_text_patch({'a.txt': old}, patch), {'a.txt': new})

    def test_out_of_scope_context_and_mode_patches_rejected(self):
        candidates = [
            '--- a/outside\n+++ b/outside\n@@ -1 +1 @@\n-old\n+new\n',
            '--- a/a.txt\n+++ b/a.txt\n@@ -1 +1 @@\n-wrong\n+new\n',
            'diff --git a/a.txt b/a.txt\nold mode 100644\nnew mode 120000\n',
            'GIT binary patch\nliteral 3\nabc\n',
        ]
        for value in candidates:
            with self.assertRaises(ContractError):
                apply_text_patch({'a.txt': 'old\n'}, value)

    def test_partial_multifile_write_resumes_without_duplicate_application(self):
        before = {'a.txt': 'old-a\n', 'b.txt': 'old-b\n'}
        after = {'a.txt': 'new-a\n', 'b.txt': 'new-b\n'}
        for name, value in before.items():
            (self.root / name).write_text(value)
        patch = ''.join(''.join(difflib.unified_diff(before[n].splitlines(True), after[n].splitlines(True), fromfile='a/'+n, tofile='b/'+n)) for n in before)
        fix = {'id': 'fix-two', 'before_revision': digest(before), 'after_revision': digest(after), 'changed_paths': list(before)}
        intent = plan_intent(self.root, list(before), fix, patch.encode())
        (self.root / 'a.txt').write_text(after['a.txt'])  # Simulate a crash after the first atomic file write.
        finish_intent(self.root, intent)
        self.assertEqual(code_snapshot(self.root, list(before)), after)
        finish_intent(self.root, intent)
        self.assertEqual(code_snapshot(self.root, list(before)), after)

    def test_resume_never_overwrites_concurrent_unknown_content(self):
        (self.root / 'a.txt').write_text('concurrent user change\n')
        intent = {'after_files': {'a.txt': 'new\n'}, 'before_hashes': {'a.txt': digest('old\n')},
                  'changed_paths': ['a.txt'], 'after_revision': digest({'a.txt': 'new\n'})}
        with self.assertRaises(GateStop):
            finish_intent(self.root, intent)
        self.assertEqual((self.root / 'a.txt').read_text(), 'concurrent user change\n')

    def test_symlink_code_path_is_never_written(self):
        outside = self.root / 'original.txt'
        outside.write_text('old\n')
        (self.root / 'a.txt').symlink_to(outside)
        with self.assertRaises(ContractError):
            code_snapshot(self.root, ['a.txt'])
        self.assertEqual(outside.read_text(), 'old\n')


if __name__ == '__main__':
    unittest.main()
