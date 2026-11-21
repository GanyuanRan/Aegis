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

# Test-only re-exports: tests/helpers/test_workspace_*.py load this file by
# path. Remove once those tests import the owning modules.
from aegis_workspace_helper.checks import command_check
from aegis_workspace_helper.errors import WorkspaceError
from aegis_workspace_helper.evidence import (
    command_add_attempt,
    command_add_evidence,
    command_bundle,
)
from aegis_workspace_helper.inputs import read_json_dict
from aegis_workspace_helper.layout import initialize_workspace
from aegis_workspace_helper.work import (
    command_add_checkpoint,
    command_add_drift_check,
    command_new_work,
)


if __name__ == "__main__":
    raise SystemExit(main())
