import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


workspace = load_module("aegis_workspace", "scripts/aegis-workspace.py")
doctor = load_module("aegis_doctor", "scripts/aegis-doctor.py")


class WorkspaceTextWriteCompatibilityTests(unittest.TestCase):
    def test_workspace_helper_does_not_depend_on_path_write_text_newline(self):
        original_write_text = Path.write_text

        def old_write_text(self, data, encoding=None, errors=None):
            return original_write_text(self, data, encoding=encoding, errors=errors)

        with tempfile.TemporaryDirectory(prefix="aegis-compat-") as tmp:
            root = Path(tmp)
            with patch.object(Path, "write_text", old_write_text):
                workspace.initialize_workspace(root)
                args = type(
                    "Args",
                    (),
                    {
                        "root": str(root),
                        "date": "2026-05-09",
                        "slug": "compat-check",
                        "title": "Compatibility Check",
                        "requested_outcome": "Verify old Path.write_text compatibility.",
                        "scope": "temporary target project",
                        "change_kind": ["test"],
                        "risk_hint": [],
                        "baseline_ref": [],
                        "affected_layer": [],
                        "owner": [],
                        "invariant": [],
                        "non_goal": [],
                        "compat_boundary": "",
                        "why_relevant": "",
                        "missing_authority": [],
                        "task_id": None,
                        "current_todo": None,
                        "active_slice": None,
                        "blocked_on": None,
                        "next_step": None,
                    },
                )()
                self.assertEqual(workspace.command_new_work(args), 0)

            work_dir = root / "docs" / "aegis" / "work" / "2026-05-09-compat-check"
            self.assertTrue((work_dir / "10-intent.md").is_file())
            self.assertTrue((work_dir / "task-intent-draft.json").is_file())

    def test_doctor_config_write_does_not_depend_on_path_write_text_newline(self):
        original_write_text = Path.write_text

        def old_write_text(self, data, encoding=None, errors=None):
            return original_write_text(self, data, encoding=encoding, errors=errors)

        with tempfile.TemporaryDirectory(prefix="aegis-doctor-compat-") as tmp:
            config = Path(tmp) / "config.toml"
            with patch.object(Path, "write_text", old_write_text):
                doctor.write_config(config, REPO_ROOT, REPO_ROOT / "scripts" / "aegis-workspace.py")

            text = config.read_text(encoding="utf-8")
            self.assertIn('activation_mode = "auto"', text)
            self.assertIn("method_pack_root =", text)
            self.assertIn("workspace_helper =", text)


if __name__ == "__main__":
    unittest.main()
