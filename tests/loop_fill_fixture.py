"""Owned evidence and product files for the fill command's contract tests."""
import copy
import shutil
import tempfile
import unittest
from pathlib import Path

import _paths
from uxloop.demo_factory import make_packet


class FillFixture:
    def __init__(self, case: unittest.TestCase) -> None:
        temporary = tempfile.TemporaryDirectory()
        case.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.evidence = self.root / "evidence"
        self.site = self.root / "site"
        self.site.mkdir()
        shutil.copy2(_paths.SKILL / "examples/loop/site/index.html", self.site / "index.html")
        self.packet = make_packet(self.evidence)
        self.original = copy.deepcopy(self.packet)
        self.receipts = {
            item["path"]: (self.evidence / item["path"]).read_bytes()
            for item in self.packet["artifacts"]
        }
        self.draft = self.evidence / "draft.json"
        self.out = self.evidence / "filled.json"
