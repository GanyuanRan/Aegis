#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "aegis-doctor.py"
SPEC = importlib.util.spec_from_file_location("aegis_doctor", MODULE_PATH)
doctor = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(doctor)


class KimiDoctorTests(unittest.TestCase):
    def make_root(self, base: Path, *, version: str = "2.5.0") -> Path:
        root = base / "aegis"
        skill = root / "skills" / "using-aegis"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            '---\nname: using-aegis\ndescription: "Route Aegis work"\n---\n',
            encoding="utf-8",
        )
        (root / "package.json").write_text(
            json.dumps({"name": "aegis", "version": version}),
            encoding="utf-8",
        )
        (root / "kimi.plugin.json").write_text(
            json.dumps(
                {
                    "name": "aegis",
                    "version": version,
                    "skills": "./skills/",
                    "sessionStart": {"skill": "using-aegis"},
                }
            ),
            encoding="utf-8",
        )
        return root

    def write_installed(
        self,
        kimi_home: Path,
        root: Path,
        *,
        enabled: bool = True,
        plugin_id: str = "aegis",
    ) -> Path:
        path = kimi_home / "plugins" / "installed.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "plugins": [
                        {
                            "id": plugin_id,
                            "root": root.as_posix(),
                            "source": "github",
                            "enabled": enabled,
                            "installedAt": "2026-07-23T00:00:00Z",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return path

    def expose_skill(self, discovery_root: Path, name: str = "using-aegis") -> Path:
        target = discovery_root / name
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text(
            f'---\nname: {name}\ndescription: "fixture"\n---\n',
            encoding="utf-8",
        )
        return target

    def test_missing_installed_file_is_an_empty_registry(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aegis-kimi-doctor-") as tmp:
            result = doctor.load_kimi_installed_file(Path(tmp))
        self.assertEqual(result, {"version": 1, "plugins": []})

    def test_corrupt_installed_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aegis-kimi-doctor-") as tmp:
            kimi_home = Path(tmp)
            path = kimi_home / "plugins" / "installed.json"
            path.parent.mkdir(parents=True)
            path.write_text("{ not json", encoding="utf-8")
            with self.assertRaisesRegex(doctor.DoctorError, "cannot parse Kimi plugin registry"):
                doctor.load_kimi_installed_file(kimi_home)

    def test_valid_plugin_record_reports_bounded_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aegis-kimi-doctor-") as tmp:
            base = Path(tmp)
            root = self.make_root(base)
            kimi_home = base / "kimi-home"
            self.write_installed(kimi_home, root)
            result = doctor.validate_kimi_plugin_record(root, kimi_home)
        self.assertEqual(result["id"], "aegis")
        self.assertTrue(result["enabled"])
        self.assertEqual(result["version"], "2.5.0")
        self.assertEqual(result["sessionStartSkill"], "using-aegis")

    def test_missing_or_disabled_plugin_fails_auto_mode(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aegis-kimi-doctor-") as tmp:
            base = Path(tmp)
            root = self.make_root(base)
            kimi_home = base / "kimi-home"
            with self.assertRaisesRegex(doctor.DoctorError, "exactly one installed"):
                doctor.validate_kimi_plugin_record(root, kimi_home)
            self.write_installed(kimi_home, root, enabled=False)
            with self.assertRaisesRegex(doctor.DoctorError, "disabled"):
                doctor.validate_kimi_plugin_record(root, kimi_home)

    def test_wrong_managed_root_and_version_mismatch_fail(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aegis-kimi-doctor-") as tmp:
            base = Path(tmp)
            root = self.make_root(base)
            alternate = self.make_root(base / "other")
            kimi_home = base / "kimi-home"
            self.write_installed(kimi_home, alternate)
            with self.assertRaisesRegex(doctor.DoctorError, "managed Aegis plugin root"):
                doctor.validate_kimi_plugin_record(root, kimi_home)

            self.write_installed(kimi_home, root)
            manifest = json.loads((root / "kimi.plugin.json").read_text(encoding="utf-8"))
            manifest["version"] = "2.4.0"
            (root / "kimi.plugin.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(doctor.DoctorError, "differs"):
                doctor.validate_kimi_plugin_record(root, kimi_home)

    def test_finds_kimi_and_shared_direct_child_collisions(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aegis-kimi-doctor-") as tmp:
            base = Path(tmp)
            root = self.make_root(base)
            kimi_home = base / "kimi-home"
            fake_home = base / "os-home"
            kimi_collision = self.expose_skill(kimi_home / "skills")
            shared_collision = self.expose_skill(fake_home / ".agents" / "skills")
            with patch.object(doctor.Path, "home", return_value=fake_home):
                result = doctor.find_kimi_skill_collisions(root, kimi_home)
        self.assertEqual(result, [kimi_collision, shared_collision])

    def test_explicit_mode_accepts_one_route_and_rejects_plugin_conflict(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aegis-kimi-doctor-") as tmp:
            base = Path(tmp)
            root = self.make_root(base)
            kimi_home = base / "kimi-home"
            discovery_root = kimi_home / "skills"
            self.expose_skill(discovery_root)
            fake_home = base / "os-home"
            with patch.object(doctor.Path, "home", return_value=fake_home):
                result = doctor.validate_kimi_explicit_mode(root, kimi_home, discovery_root)
            self.assertEqual(result["mode"], "explicit")
            self.assertFalse(result["pluginEnabled"])

            self.write_installed(kimi_home, root)
            with self.assertRaisesRegex(doctor.DoctorError, "conflicts"):
                doctor.validate_kimi_explicit_mode(root, kimi_home, discovery_root)

    def test_explicit_mode_rejects_an_alternate_direct_child_route(self) -> None:
        with tempfile.TemporaryDirectory(prefix="aegis-kimi-doctor-") as tmp:
            base = Path(tmp)
            root = self.make_root(base)
            kimi_home = base / "kimi-home"
            selected = kimi_home / "skills"
            self.expose_skill(selected)
            fake_home = base / "os-home"
            self.expose_skill(fake_home / ".agents" / "skills")
            with patch.object(doctor.Path, "home", return_value=fake_home):
                with self.assertRaisesRegex(doctor.DoctorError, "multiple direct-child"):
                    doctor.validate_kimi_explicit_mode(root, kimi_home, selected)


if __name__ == "__main__":
    unittest.main()
