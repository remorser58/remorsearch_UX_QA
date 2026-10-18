"""Put the skill folder on sys.path for tests run from the repository checkout.

The runtime code (uxloop, ergoqa, scripts, schemas, drivers, examples) ships inside
the installable skill folder; tests, fixtures and benchmarks stay at the repository
root. Import this module before importing uxloop, ergoqa or scripts.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "remorsearch-ux-qa"

for entry in (SKILL / "scripts", SKILL):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))
