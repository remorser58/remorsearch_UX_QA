"""The loop's synthetic fixture builder, for the tests (it lives in uxloop/demo_factory.py).

ROOT is the repository checkout and SKILL the skill folder. Nothing here runs a browser.
"""
from __future__ import annotations

from _paths import REPO as ROOT, SKILL  # noqa: F401  (puts the skill folder on sys.path)
from uxloop.demo_factory import (  # noqa: F401  (re-exported for the tests)
    CAPTURE, END, REGRESSION_AT, REPLAY_CAPTURE, REPLAY_END, REPLAY_START, START, append_recovery_round, make_packet,
    replace_artifact, write_json)
