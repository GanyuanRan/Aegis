import importlib.util
import json
import os
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
    def make_method_pack_with_skills(self, root: Path, skills: list[str]) -> Path:
        source_skills = root / "skills"
        source_skills.mkdir(parents=True)
        for skill in skills:
            skill_dir = source_skills / skill
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")
        return source_skills

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

    def test_register_installation_records_discovery_name_prefix(self):
        with tempfile.TemporaryDirectory(prefix="aegis-update-prefix-") as tmp:
            registry = Path(tmp) / "installations.json"
            root = Path(tmp) / "aegis"

            entry = update.register_installation(
                registry,
                host="copilot",
                method_pack_root=root,
                discovery_root=Path(tmp) / "skills",
                sync_mode="junction",
                discovery_shape="direct-child",
                discovery_name_prefix="aegis-",
            )

            self.assertEqual(entry["discoveryNamePrefix"], "aegis-")
            data = update.load_registry(registry)
            self.assertEqual(data["installations"][0]["discoveryNamePrefix"], "aegis-")

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

    def test_run_doctor_passes_registered_discovery_name_prefix(self):
        entry = {
            "id": "copilot:default",
            "host": "copilot",
            "methodPackRoot": REPO_ROOT.as_posix(),
            "syncMode": "junction",
            "discoveryRoot": "/tmp/repo/.github/skills",
            "discoveryShape": "direct-child",
            "discoveryNamePrefix": "aegis-",
        }

        with patch.object(update, "run_command") as run_command:
            run_command.return_value.stdout = json.dumps(
                {
                    "ok": True,
                    "workspaceSupport": "available",
                    "configStatus": "configured",
                    "expectedDiscoveryShape": "prefixed-direct-child-skill-directories",
                    "discoveryShapeStatus": "current",
                    "compatibilityExposureStatus": "generated-copy-view-current",
                    "discoveryNamePolicy": "prefix:aegis-",
                    "discoveryNamePrefix": "aegis-",
                }
            )
            update.run_doctor(entry, config_path=None)

        command = run_command.call_args.args[0]
        self.assertIn("--discovery-name-prefix", command)
        self.assertIn("aegis-", command)

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

    def test_sync_skills_copies_prefixed_direct_child_skills(self):
        with tempfile.TemporaryDirectory(prefix="aegis-update-prefixed-copy-") as tmp:
            method_pack_root = Path(tmp) / "method-pack"
            self.make_method_pack_with_skills(
                method_pack_root,
                list(update.COPY_DISCOVERY_KEY_SKILLS),
            )
            discovery_root = Path(tmp) / "discovery"
            discovery_root.mkdir()
            personal_skill = discovery_root / "personal-skill"
            personal_skill.mkdir()
            (personal_skill / "SKILL.md").write_text("# personal\n", encoding="utf-8")

            entry = {
                "id": "prefixed-copy:default",
                "host": "prefixed-copy",
                "methodPackRoot": method_pack_root.as_posix(),
                "syncMode": "copy-skills",
                "discoveryRoot": discovery_root.as_posix(),
                "discoveryShape": "direct-child",
                "discoveryNamePrefix": "aegis-",
            }

            update.sync_skills(entry)

            for skill in update.COPY_DISCOVERY_KEY_SKILLS:
                self.assertTrue((discovery_root / f"aegis-{skill}" / "SKILL.md").is_file())
                self.assertFalse((discovery_root / skill).exists())
            self.assertTrue((personal_skill / "SKILL.md").is_file())

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

    def test_register_installation_defaults_zcode_to_direct_child(self):
        with tempfile.TemporaryDirectory(prefix="aegis-update-zcode-shape-") as tmp:
            registry = Path(tmp) / "installations.json"
            root = Path(tmp) / "aegis"

            entry = update.register_installation(
                registry,
                host="ZCode",
                method_pack_root=root,
                discovery_root=Path(tmp) / "zcode-skills",
                sync_mode="junction",
            )

            self.assertEqual(entry["host"], "zcode")
            self.assertEqual(entry["syncMode"], "junction")
            self.assertEqual(entry["discoveryShape"], "direct-child")

    def test_sync_skills_creates_direct_child_links_for_zcode_junction(self):
        with tempfile.TemporaryDirectory(prefix="aegis-update-zcode-links-") as tmp:
            method_pack_root = Path(tmp) / "method-pack"
            self.make_method_pack_with_skills(method_pack_root, ["using-aegis", "brainstorming"])
            discovery_root = Path(tmp) / "discovery"
            sync_mode = "junction" if os.name == "nt" else "symlink"
            entry = {
                "id": "zcode:default",
                "host": "zcode",
                "methodPackRoot": method_pack_root.as_posix(),
                "syncMode": sync_mode,
                "discoveryRoot": discovery_root.as_posix(),
                "discoveryShape": "direct-child",
            }

            update.sync_skills(entry)

            for skill in ["using-aegis", "brainstorming"]:
                self.assertTrue((discovery_root / skill / "SKILL.md").is_file())
                self.assertEqual(
                    (discovery_root / skill / "SKILL.md").read_text(encoding="utf-8"),
                    f"# {skill}\n",
                )

    def test_sync_skills_creates_prefixed_direct_child_links(self):
        with tempfile.TemporaryDirectory(prefix="aegis-update-prefixed-links-") as tmp:
            method_pack_root = Path(tmp) / "method-pack"
            self.make_method_pack_with_skills(method_pack_root, ["using-aegis", "brainstorming"])
            discovery_root = Path(tmp) / "discovery"
            sync_mode = "junction" if os.name == "nt" else "symlink"
            entry = {
                "id": "copilot:default",
                "host": "copilot",
                "methodPackRoot": method_pack_root.as_posix(),
                "syncMode": sync_mode,
                "discoveryRoot": discovery_root.as_posix(),
                "discoveryShape": "direct-child",
                "discoveryNamePrefix": "aegis-",
            }

            update.sync_skills(entry)

            for skill in ["using-aegis", "brainstorming"]:
                self.assertTrue((discovery_root / f"aegis-{skill}" / "SKILL.md").is_file())
                self.assertFalse((discovery_root / skill).exists())

    def test_sync_skills_prunes_stale_direct_child_links(self):
        with tempfile.TemporaryDirectory(prefix="aegis-update-zcode-prune-") as tmp:
            method_pack_root = Path(tmp) / "method-pack"
            source_skills = self.make_method_pack_with_skills(method_pack_root, ["using-aegis"])
            retired_source = source_skills / "retired-skill"
            retired_source.mkdir()
            discovery_root = Path(tmp) / "discovery"
            discovery_root.mkdir()
            personal_skill = discovery_root / "personal-skill"
            personal_skill.mkdir()
            (personal_skill / "SKILL.md").write_text("# personal\n", encoding="utf-8")
            stale_link = discovery_root / "retired-skill"
            sync_mode = "junction" if os.name == "nt" else "symlink"
            try:
                update.create_direct_child_link(retired_source, stale_link)
            except update.UpdateError as exc:
                self.skipTest(f"direct-child link creation unavailable: {exc}")
            entry = {
                "id": "zcode:default",
                "host": "zcode",
                "methodPackRoot": method_pack_root.as_posix(),
                "syncMode": sync_mode,
                "discoveryRoot": discovery_root.as_posix(),
                "discoveryShape": "direct-child",
            }

            update.sync_skills(entry)

            self.assertFalse(stale_link.exists())
            self.assertTrue((discovery_root / "using-aegis" / "SKILL.md").is_file())
            self.assertTrue((personal_skill / "SKILL.md").is_file())

    def test_command_register_syncs_and_verifies_zcode_installation(self):
        with tempfile.TemporaryDirectory(prefix="aegis-update-zcode-register-") as tmp:
            parser = update.build_parser()
            registry = Path(tmp) / "installations.json"
            root = Path(tmp) / "method-pack"
            discovery_root = Path(tmp) / "discovery"
            args = parser.parse_args(
                [
                    "register",
                    "--registry",
                    registry.as_posix(),
                    "--host",
                    "zcode",
                    "--method-pack-root",
                    root.as_posix(),
                    "--sync-mode",
                    "junction",
                    "--discovery-root",
                    discovery_root.as_posix(),
                ]
            )

            with patch.object(update, "sync_skills") as sync_skills, patch.object(
                update, "run_doctor"
            ) as run_doctor:
                sync_skills.return_value = "junction: direct-child links current"
                run_doctor.return_value = {
                    "ok": True,
                    "workspaceSupport": "available",
                    "configStatus": "configured",
                }
                result = update.command_register(args)

            self.assertEqual(result["status"], "registered")
            self.assertEqual(result["discoveryShape"], "direct-child")
            self.assertTrue(result["verified"])
            sync_skills.assert_called_once()
            run_doctor.assert_called_once()

    def test_command_register_requires_zcode_discovery_root_before_registry_write(self):
        with tempfile.TemporaryDirectory(prefix="aegis-update-zcode-register-root-") as tmp:
            parser = update.build_parser()
            registry = Path(tmp) / "installations.json"
            args = parser.parse_args(
                [
                    "register",
                    "--registry",
                    registry.as_posix(),
                    "--host",
                    "zcode",
                    "--method-pack-root",
                    (Path(tmp) / "method-pack").as_posix(),
                    "--sync-mode",
                    "junction",
                ]
            )

            with self.assertRaisesRegex(update.UpdateError, "--discovery-root"):
                update.command_register(args)

            self.assertFalse(registry.exists())

    def test_register_installation_defaults_antigravity_cli_to_host_managed(self):
        with tempfile.TemporaryDirectory(prefix="aegis-update-antigravity-shape-") as tmp:
            registry = Path(tmp) / "installations.json"
            root = Path(tmp) / "aegis"

            entry = update.register_installation(
                registry,
                host="antigravity-cli",
                method_pack_root=root,
                sync_mode="repo-only",
            )

            self.assertEqual(entry["syncMode"], "repo-only")
            self.assertEqual(entry["discoveryShape"], "host-managed")

    def test_doctor_discovery_root_skips_host_managed_antigravity_shape(self):
        entry = {
            "id": "antigravity-cli:default",
            "host": "antigravity-cli",
            "syncMode": "repo-only",
            "discoveryRoot": "/tmp/antigravity-plugin-cache",
            "discoveryShape": "host-managed",
        }

        self.assertIsNone(update.doctor_discovery_root(entry))

    def test_default_method_pack_root_prefers_user_local_config(self):
        with tempfile.TemporaryDirectory(prefix="aegis-update-config-root-") as tmp:
            configured_root = Path(tmp) / "configured-aegis"
            configured_root.mkdir()
            config_path = Path(tmp) / "config.toml"
            config_path.write_text(
                f'method_pack_root = "{configured_root.as_posix()}"\n',
                encoding="utf-8",
            )

            self.assertEqual(
                update.configured_method_pack_root(config_path),
                configured_root.resolve(),
            )

    def test_update_registered_installations_reuses_shared_method_pack_root_once(self):
        shared_root = (Path(tempfile.gettempdir()) / "shared-aegis-root").resolve()
        selected = [
            {
                "id": "codex:default",
                "host": "codex",
                "methodPackRoot": shared_root.as_posix(),
                "trackedRef": "main",
                "syncMode": "junction",
                "reloadHint": "restart Codex",
            },
            {
                "id": "kimi:default",
                "host": "kimi",
                "methodPackRoot": shared_root.as_posix(),
                "trackedRef": "main",
                "syncMode": "junction",
                "reloadHint": "restart Kimi",
            },
        ]
        registry = {
            "schemaVersion": 1,
            "installations": [dict(selected[0]), dict(selected[1])],
        }

        with tempfile.TemporaryDirectory(prefix="aegis-update-shared-root-") as tmp:
            registry_path = Path(tmp) / "installations.json"
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            with patch.object(update, "update_method_pack_checkout") as update_root, patch.object(
                update, "sync_skills"
            ) as sync_skills, patch.object(update, "run_doctor") as run_doctor:
                update_root.return_value = {
                    "status": "updated",
                    "beforeCommit": "abc",
                    "afterCommit": "def",
                    "methodPackRoot": shared_root.as_posix(),
                }
                sync_skills.side_effect = lambda entry: f"synced {entry['host']}"
                run_doctor.return_value = {
                    "ok": True,
                    "workspaceSupport": "available",
                    "configStatus": "configured",
                }

                results = update.update_registered_installations(
                    registry_path,
                    selected,
                    config_path=None,
                    dry_run=False,
                    stash=False,
                    force=False,
                    verify=True,
                )

            self.assertEqual(update_root.call_count, 1)
            self.assertEqual(sync_skills.call_count, 2)
            self.assertEqual(run_doctor.call_count, 2)
            self.assertFalse(results[0].get("sharedMethodPackRootReused", False))
            self.assertTrue(results[1]["sharedMethodPackRootReused"])


if __name__ == "__main__":
    unittest.main()
