#!/usr/bin/env python3
"""Run the repository-local public-page reader CLI without installing a package."""
from pathlib import Path
import shlex
import sys

if sys.version_info < (3, 10):
    print("Python 3.10 or newer is required; found " + sys.version.split()[0], file=sys.stderr)
    print("Discover installed runtimes:", file=sys.stderr)
    print(shlex.quote(sys.executable) + " "
          + shlex.quote(str(Path(__file__).resolve().with_name("find_runtime.py"))), file=sys.stderr)
    raise SystemExit(2)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from uxresearch.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
