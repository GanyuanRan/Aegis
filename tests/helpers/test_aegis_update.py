import importlib.util
import json
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


update = load_module("aegis_update", "scripts/aegis-update.py")


class AegisUpdateRegistryTests(unittest.TestCase):
    def test_register_installation_keeps_hosts_separate(self):
        with tempfile.TemporaryDirectory(prefix="aegis-update-") as tmp:
            registry = Path(tmp) / "installations.json"
            codex_root = Path(tmp) / "codex-aegis"
            opencode_root = Path(tmp) / "opencode-aegis"

            update.register_installation(
                registry,
                host="codex",
                method_pack_root=codex_root,
                discovery_root=Path(tmp) / "codex-skills",
                sync_mode="junction",
                tracked_ref="main",
                update_mode="manual",
                reload_hint="restart Codex",
            )
            update.register_installation(
                registry,
                host="opencode",
                method_pack_root=opencode_root,
                discovery_root=Path(tmp) / "opencode-skills",
                sync_mode="plugin-managed",
                tracked_ref="main",
                update_mode="manual",
                reload_hint="restart OpenCode",
            )

            data = update.load_registry(registry)

            self.assertEqual(data["schemaVersion"], 1)
            self.assertEqual(
                [item["id"] for item in data["installations"]],
                ["codex:default", "opencode:default"],
            )
            self.assertEqual(
                update.select_installations(data, host="codex", all_hosts=False)[0][
                    "methodPackRoot"
                ],
                codex_root.as_posix(),
            )

    def test_register_installation_records_discovery_shape(self):
        with tempfile.TemporaryDirectory(prefix="aegis-update-shape-") as tmp:
            registry = Path(tmp) / "installations.json"
            root = Path(tmp) / "aegis"

            entry = update.register_installation(
                registry,
                host="cc-gui",
                method_pack_root=root,
                discovery_root=Path(tmp) / "skills",
                sync_mode="junction",
                discovery_shape="direct-child",
            )

            self.assertEqual(entry["discoveryShape"], "direct-child")
            data = update.load_registry(registry)
            self.assertEqual(data["installations"][0]["discoveryShape"], "direct-child")

    def test_update_without_host_refuses_ambiguous_multi_host_registry(self):
        data = {
            "schemaVersion": 1,
            "installations": [
                {"id": "codex:default", "host": "codex"},
                {"id": "opencode:default", "host": "opencode"},
            ],
        }

        with self.assertRaisesRegex(update.UpdateError, "Multiple Aegis installations"):
            update.select_installations(data, host=None, all_hosts=False)

    def test_update_all_requires_explicit_all_flag(self):
        data = {
            "schemaVersion": 1,
            "installations": [
                {"id": "codex:default", "host": "codex"},
                {"id": "opencode:default", "host": "opencode"},
            ],
        }

        selected = update.select_installations(data, host=None, all_hosts=True)

        self.assertEqual([item["id"] for item in selected], ["codex:default", "opencode:default"])

    def test_json_flag_is_accepted_after_subcommand(self):
        parser = update.build_parser()

        status_args = parser.parse_args(["status", "--registry", "registry.json", "--json"])
        update_args = parser.parse_args(
            ["update", "--host", "codex", "--registry", "registry.json", "--json"]
        )

        self.assertTrue(status_args.json)
        self.assertEqual(status_args.registry, "registry.json")
        self.assertTrue(update_args.json)
        self.assertEqual(update_args.registry, "registry.json")

    def test_doctor_discovery_root_uses_registered_discovery_shape(self):
        copy_entry = {
            "id": "codebuddy:default",
            "host": "codebuddy",
            "syncMode": "copy-skills",
            "discoveryRoot": "/tmp/codebuddy-skills",
            "discoveryShape": "direct-child",
        }
        junction_entry = {
            "id": "codex:default",
            "host": "codex",
            "syncMode": "junction",
            "discoveryRoot": "/tmp/codex-skills",
            "discoveryShape": "umbrella-root",
        }

        self.assertEqual(update.doctor_discovery_root(copy_entry), "/tmp/codebuddy-skills")
        self.assertEqual(update.doctor_discovery_root(junction_entry), "/tmp/codex-skills")

    def test_run_doctor_verifies_copy_skills_discovery_root(self):
        entry = {
            "id": "codebuddy:default",
            "host": "codebuddy",
            "methodPackRoot": REPO_ROOT.as_posix(),
            "syncMode": "copy-skills",
            "discoveryRoot": "/tmp/codebuddy-skills",
            "discoveryShape": "direct-child",
        }

        with patch.object(update, "run_command") as run_command:
            run_command.return_value.stdout = json.dumps(
                {
                    "ok": True,
                    "workspaceSupport": "available",
                    "configStatus": "configured",
                    "expectedDiscoveryShape": "direct-child-skill-directories",
                    "discoveryShapeStatus": "current",
                    "compatibilityExposureStatus": "generated-copy-view-current",
                }
            )
            update.run_doctor(entry, config_path=None)

        command = run_command.call_args.args[0]
        self.assertIn("--discovery-root", command)
        self.assertIn("/tmp/codebuddy-skills", command)

    def test_sync_skills_prunes_stale_aegis_skill_directories_for_copy_mode(self):
        with tempfile.TemporaryDirectory(prefix="aegis-update-copy-") as tmp:
            method_pack_root = Path(tmp) / "method-pack"
            source_skills = method_pack_root / "skills"
            source_skills.mkdir(parents=True)
            for skill in update.COPY_DISCOVERY_KEY_SKILLS:
                skill_dir = source_skills / skill
                skill_dir.mkdir()
                (skill_dir / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")

            discovery_root = Path(tmp) / "discovery"
            discovery_root.mkdir()
            stale_skill = discovery_root / "retired-skill"
            stale_skill.mkdir()
            (stale_skill / "SKILL.md").write_text("# stale\n", encoding="utf-8")

            entry = {
                "id": "codebuddy:default",
                "host": "codebuddy",
                "methodPackRoot": method_pack_root.as_posix(),
                "syncMode": "copy-skills",
                "discoveryRoot": discovery_root.as_posix(),
                "discoveryShape": "direct-child",
            }

            update.sync_skills(entry)

            self.assertFalse(stale_skill.exists())
            for skill in update.COPY_DISCOVERY_KEY_SKILLS:
                self.assertTrue((discovery_root / skill / "SKILL.md").is_file())

    def test_register_installation_defaults_discovery_shape_from_sync_mode(self):
        with tempfile.TemporaryDirectory(prefix="aegis-update-default-shape-") as tmp:
            registry = Path(tmp) / "installations.json"
            root = Path(tmp) / "aegis"

            copy_entry = update.register_installation(
                registry,
                host="deepseek-tui",
                method_pack_root=root,
                discovery_root=Path(tmp) / "deepseek-skills",
                sync_mode="copy-skills",
            )
            junction_entry = update.register_installation(
                registry,
                host="codex",
                install_id="codex:alt",
                method_pack_root=root,
                discovery_root=Path(tmp) / "codex-skills",
                sync_mode="junction",
            )

            self.assertEqual(copy_entry["discoveryShape"], "direct-child")
            self.assertEqual(junction_entry["discoveryShape"], "umbrella-root")


if __name__ == "__main__":
    unittest.main()
