import importlib.util
import tempfile
import unittest
from pathlib import Path


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

    def test_copy_skill_discovery_is_not_passed_to_doctor_symlink_check(self):
        copy_entry = {
            "id": "codebuddy:default",
            "host": "codebuddy",
            "syncMode": "copy-skills",
            "discoveryRoot": "/tmp/codebuddy-skills",
        }
        junction_entry = {
            "id": "codex:default",
            "host": "codex",
            "syncMode": "junction",
            "discoveryRoot": "/tmp/codex-skills",
        }

        self.assertIsNone(update.doctor_discovery_root(copy_entry))
        self.assertEqual(update.doctor_discovery_root(junction_entry), "/tmp/codex-skills")


if __name__ == "__main__":
    unittest.main()
