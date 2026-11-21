#!/usr/bin/env python3
"""Manage a target project's docs/aegis workspace.

This helper belongs to the Aegis Method Pack, but it writes only to the project
root explicitly passed by the caller. It validates workspace structure and
index coverage; it does not make authoritative governance decisions.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Load the implementation package that sits next to this file. Resolve it
# from __file__, not sys.path[0] or the cwd, so `python -I`, PYTHONSAFEPATH,
# and load-by-path imports all work. Write no bytecode: the helper writes only
# under the --root it is given.
sys.dont_write_bytecode = True
_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from aegis_workspace_helper.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
