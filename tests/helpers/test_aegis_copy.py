"""Behavioral regressions for copied discovery files and their registry ownership."""

import copy
import importlib.util
import posixpath
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("aegis_update", REPO_ROOT / "scripts" / "aegis-update.py")
update = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update)


class AegisCopyOwnershipTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="aegis-copy-ownership-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.registry = self.root / "installations.json"

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def make_entry(self, prefix="", suffix=""):
        pack = self.root / ("pack" + suffix)
        for name in update.COPY_DISCOVERY_KEY_SKILLS:
            self.write(pack / "skills" / name / "SKILL.md", f"# {name}\n")
        return {
            "id": "test" + suffix,
            "host": "copy-test",
            "methodPackRoot": pack.as_posix(),
            "discoveryRoot": (self.root / ("discovery" + suffix)).as_posix(),
            "discoveryNamePrefix": prefix,
            "syncMode": "copy-skills",
            "discoveryShape": "direct-child",
        }

    def args(self, entry):
        return update.build_parser().parse_args([
            "register", "--registry", str(self.registry),
            "--host", entry["host"], "--id", entry["id"],
            "--method-pack-root", entry["methodPackRoot"],
            "--discovery-root", entry["discoveryRoot"],
            "--discovery-name-prefix", entry["discoveryNamePrefix"],
            "--sync-mode", "copy-skills",
        ])

    def registered(self):
        return update.load_registry(self.registry)["installations"][0]

    def snapshot(self, root):
        if not root.exists():
            return {}
        return {
            path.relative_to(root).as_posix(): path.read_bytes() if path.is_file() else None
            for path in root.rglob("*")
        }

    def register(self, entry):
        with patch.object(update, "run_doctor", return_value={"ok": True}):
            return update.command_register(self.args(entry))

    def run_update(self, selected, *, verify=False):
        with patch.object(update, "update_method_pack_checkout", return_value={
            "status": "updated", "beforeCommit": "old", "afterCommit": "new",
        }):
            return update.update_registered_installations(
                self.registry, selected, config_path=None, dry_run=False,
                stash=False, force=False, verify=verify,
            )

    def test_register_and_reregister_keep_unrelated_skills_and_refresh_owned_files(self):
        for prefix in ("", "aegis-"):
            with self.subTest(prefix=prefix):
                entry = self.make_entry(prefix, suffix=prefix or "plain")
                target = Path(entry["discoveryRoot"])
                for name in ("personal", "aegis-personal"):
                    self.write(target / name / "SKILL.md", name)
                source = Path(entry["methodPackRoot"]) / "skills" / "using-aegis" / "SKILL.md"
                self.register(entry)
                source.write_text("updated source", encoding="utf-8")
                result = self.register(entry)
                self.assertEqual((target / f"{prefix}using-aegis" / "SKILL.md").read_text(), "updated source")
                for name in ("personal", "aegis-personal"):
                    self.assertEqual((target / name / "SKILL.md").read_text(), name)
                self.assertIn("copyInventory", result)
                data = update.load_registry(self.registry)
                self.assertEqual(data["schemaVersion"], 1)
                self.assertEqual(next(item for item in data["installations"] if item["id"] == entry["id"])["copyInventory"], result["copyInventory"])

    def test_collision_stops_registration_before_any_discovery_changes(self):
        entry = self.make_entry()
        target = Path(entry["discoveryRoot"])
        collision = target / "verification-before-completion" / "SKILL.md"
        self.write(collision, "personal collision")
        before = self.snapshot(target)
        with patch.object(update, "run_doctor") as doctor:
            with self.assertRaisesRegex(update.UpdateError, "verification-before-completion.*Reconcile"):
                update.command_register(self.args(entry))
        self.assertEqual(self.snapshot(target), before)
        self.assertNotIn("copyInventory", self.registered())
        doctor.assert_not_called()

    def test_legacy_identical_files_are_adopted_without_claiming_unknown_files(self):
        entry = self.make_entry("aegis-")
        source = Path(entry["methodPackRoot"]) / "skills"
        target = Path(entry["discoveryRoot"])
        for child in source.iterdir():
            shutil.copytree(child, target / ("aegis-" + child.name))
        self.write(target / "aegis-retired" / "SKILL.md", "unidentified legacy copy")
        self.write(target / "aegis-using-aegis" / "personal.txt", "personal addition")
        self.register(entry)
        inventory = self.registered()["copyInventory"]["files"]
        self.assertEqual(len(inventory), len(update.COPY_DISCOVERY_KEY_SKILLS))
        (source / "using-aegis" / "SKILL.md").write_text("upstream update")
        self.run_update([self.registered()])
        self.assertEqual((target / "aegis-using-aegis" / "SKILL.md").read_text(), "upstream update")
        self.assertEqual((target / "aegis-using-aegis" / "personal.txt").read_text(), "personal addition")
        self.assertTrue((target / "aegis-retired" / "SKILL.md").is_file())

    def test_update_retires_only_unchanged_files_and_preserves_modified_stale_files(self):
        entry = self.make_entry()
        source = Path(entry["methodPackRoot"]) / "skills"
        target = Path(entry["discoveryRoot"])
        for name in ("retired", "retired-with-user-file", "retired-modified"):
            self.write(source / name / "SKILL.md", name)
        self.write(source / "using-aegis" / "obsolete.txt", "old helper")
        self.register(entry)
        self.write(target / "retired-with-user-file" / "personal.txt", "keep me")
        self.write(target / "retired-modified" / "SKILL.md", "local changes")
        for name in ("retired", "retired-with-user-file", "retired-modified"):
            shutil.rmtree(source / name)
        (source / "using-aegis" / "obsolete.txt").unlink()
        self.run_update([copy.deepcopy(self.registered())])
        self.assertFalse((target / "retired").exists())
        self.assertFalse((target / "retired-with-user-file" / "SKILL.md").exists())
        self.assertEqual((target / "retired-with-user-file" / "personal.txt").read_text(), "keep me")
        self.assertEqual((target / "retired-modified" / "SKILL.md").read_text(), "local changes")
        self.assertFalse((target / "using-aegis" / "obsolete.txt").exists())
        self.assertNotIn("retired/SKILL.md", self.registered()["copyInventory"]["files"])

    def test_local_edit_blocks_all_writes_and_retirement_then_retries_after_reconciliation(self):
        entry = self.make_entry()
        source = Path(entry["methodPackRoot"]) / "skills"
        target = Path(entry["discoveryRoot"])
        self.write(source / "retired" / "SKILL.md", "retire later")
        self.register(entry)
        old_registry = self.registry.read_bytes()
        self.write(source / "using-aegis" / "SKILL.md", "upstream change")
        self.write(source / "new-skill" / "SKILL.md", "new")
        shutil.rmtree(source / "retired")
        collision = target / "verification-before-completion" / "SKILL.md"
        collision.write_text("local edits")
        before = self.snapshot(target)
        with self.assertRaisesRegex(update.UpdateError, "locally modified"):
            self.run_update([self.registered()])
        self.assertEqual(self.snapshot(target), before)
        self.assertEqual(self.registry.read_bytes(), old_registry)
        shutil.copy2(source / "verification-before-completion" / "SKILL.md", collision)
        self.run_update([self.registered()])
        self.assertFalse((target / "retired").exists())
        self.assertEqual((target / "using-aegis" / "SKILL.md").read_text(), "upstream change")
        self.assertTrue((target / "new-skill" / "SKILL.md").is_file())

    def test_reregistration_does_not_reuse_evidence_after_any_scope_change(self):
        for changed in ("source", "target", "prefix"):
            with self.subTest(changed=changed):
                entry = self.make_entry(suffix=changed)
                source = Path(entry["methodPackRoot"]) / "skills"
                target = Path(entry["discoveryRoot"])
                self.write(source / "notes.txt", "original")
                self.register(entry)
                if changed == "source":
                    other = self.root / "other-pack"
                    shutil.copytree(Path(entry["methodPackRoot"]), other)
                    entry["methodPackRoot"] = str(other)
                    source = other / "skills"
                elif changed == "target":
                    other = self.root / "other-discovery"
                    shutil.copytree(target, other)
                    entry["discoveryRoot"] = str(other)
                    target = other
                else:
                    entry["discoveryNamePrefix"] = "aegis-"
                (source / "notes.txt").write_text("new source")
                before = self.snapshot(target)
                with self.assertRaisesRegex(update.UpdateError, "notes.txt.*untracked"):
                    self.register(entry)
                self.assertEqual(self.snapshot(target), before)
                saved = next(item for item in update.load_registry(self.registry)["installations"] if item["id"] == entry["id"])
                self.assertNotIn("copyInventory", saved)

    def test_register_saves_inventory_before_doctor_failure_and_retry(self):
        entry = self.make_entry()
        def fail_doctor(*args, **kwargs):
            self.assertIn("copyInventory", self.registered())
            raise update.UpdateError("doctor unavailable")
        with patch.object(update, "run_doctor", side_effect=fail_doctor):
            with self.assertRaisesRegex(update.UpdateError, "doctor unavailable"):
                update.command_register(self.args(entry))
        source = Path(entry["methodPackRoot"]) / "skills" / "using-aegis" / "SKILL.md"
        source.write_text("next version")
        self.register(entry)
        self.assertEqual((Path(entry["discoveryRoot"]) / "using-aegis" / "SKILL.md").read_text(), "next version")

    def test_update_saves_new_inventory_before_doctor_failure_and_retry(self):
        entry = self.make_entry()
        self.register(entry)
        old_inventory = self.registered()["copyInventory"]
        source = Path(entry["methodPackRoot"]) / "skills" / "using-aegis" / "SKILL.md"
        source.write_text("second version")
        def fail_doctor(*args, **kwargs):
            self.assertNotEqual(self.registered()["copyInventory"], old_inventory)
            raise update.UpdateError("doctor unavailable")
        with patch.object(update, "run_doctor", side_effect=fail_doctor):
            with self.assertRaisesRegex(update.UpdateError, "doctor unavailable"):
                self.run_update([copy.deepcopy(self.registered())], verify=True)
        self.assertNotIn("lastVerifiedCommit", self.registered())
        source.write_text("third version")
        self.run_update([self.registered()])
        self.assertEqual((Path(entry["discoveryRoot"]) / "using-aegis" / "SKILL.md").read_text(), "third version")

    def test_shared_checkout_update_saves_each_discovery_inventory_before_doctor(self):
        entry = self.make_entry()
        self.register(entry)
        second = dict(entry, id="second", discoveryRoot=str(self.root / "second-discovery"))
        self.register(second)
        source = Path(entry["methodPackRoot"]) / "skills" / "using-aegis" / "SKILL.md"
        source.write_text("shared source update")
        selected = copy.deepcopy(update.load_registry(self.registry)["installations"])
        def doctor(current, **kwargs):
            registered = update.load_registry(self.registry)["installations"]
            saved = next(item for item in registered if item["id"] == current["id"])
            self.assertEqual(saved["copyInventory"], current["copyInventory"])
            if current["id"] == "second":
                raise update.UpdateError("second doctor unavailable")
            return {"ok": True}
        with patch.object(update, "run_doctor", side_effect=doctor):
            with self.assertRaisesRegex(update.UpdateError, "second doctor unavailable"):
                self.run_update(selected, verify=True)
        saved = update.load_registry(self.registry)["installations"]
        for current in saved:
            self.assertEqual((Path(current["discoveryRoot"]) / "using-aegis" / "SKILL.md").read_text(), "shared source update")
        self.assertEqual(saved[0]["lastVerifiedCommit"], "new")
        self.assertNotIn("lastVerifiedCommit", saved[1])

    def test_update_does_not_write_through_a_hardlink_to_an_external_file(self):
        entry = self.make_entry()
        self.register(entry)
        source = Path(entry["methodPackRoot"]) / "skills" / "using-aegis" / "SKILL.md"
        destination = Path(entry["discoveryRoot"]) / "using-aegis" / "SKILL.md"
        outside = self.root / "external-file"
        try:
            outside.hardlink_to(destination)
        except OSError as exc:
            self.skipTest(f"hard links unavailable: {exc}")
        original = outside.read_text()
        source.write_text("upstream update")
        self.run_update([self.registered()])
        self.assertEqual(outside.read_text(), original)
        self.assertEqual(destination.read_text(), "upstream update")

    def test_stale_managed_hardlink_with_distinct_name_is_retired(self):
        entry = self.make_entry()
        source = Path(entry["methodPackRoot"]) / "skills"
        target = Path(entry["discoveryRoot"])
        self.write(source / "current.txt", "original")
        self.write(source / "obsolete.txt", "original")
        update.sync_skills(entry)
        (target / "obsolete.txt").unlink()
        (target / "obsolete.txt").hardlink_to(target / "current.txt")
        (source / "obsolete.txt").unlink()
        update.sync_skills(entry)
        self.assertFalse((target / "obsolete.txt").exists())
        self.assertEqual((target / "current.txt").read_text(), "original")

    def test_interrupted_file_copy_keeps_original_and_retry_succeeds(self):
        entry = self.make_entry()
        self.register(entry)
        source = Path(entry["methodPackRoot"]) / "skills" / "using-aegis" / "SKILL.md"
        destination = Path(entry["discoveryRoot"]) / "using-aegis" / "SKILL.md"
        original = destination.read_text()
        source.write_text("upstream update")
        def partial_copy(path, target):
            Path(target).write_text("partial")
            raise OSError("copy interrupted")
        with patch("aegis_copy.shutil.copy2", side_effect=partial_copy):
            with self.assertRaisesRegex(update.UpdateError, "copy interrupted"):
                self.run_update([self.registered()])
        self.assertEqual(destination.read_text(), original)
        self.assertEqual(list(destination.parent.glob(".aegis-copy-*")), [])
        self.run_update([self.registered()])
        self.assertEqual(destination.read_text(), "upstream update")

    def test_prefix_mapping_collision_stops_before_writes(self):
        entry = self.make_entry("aegis-")
        source = Path(entry["methodPackRoot"]) / "skills"
        self.write(source / "aegis-using-aegis" / "support.txt", "support directory")
        target = Path(entry["discoveryRoot"])
        with self.assertRaisesRegex(update.UpdateError, "same destination"):
            update.sync_skills(entry)
        self.assertFalse(target.exists())

    def test_portable_source_name_collisions_stop_before_any_target_writes(self):
        names = (
            ("example", "AEGIS-EXAMPLE"),
            ("caf\u00e9", "aegis-cafe\u0301"),
            ("stra\u00dfe", "aegis-STRASSE"),
        )
        for index, (skill, support) in enumerate(names):
            with self.subTest(skill=skill, support=support):
                entry = self.make_entry("aegis-", suffix=str(index))
                source = Path(entry["methodPackRoot"]) / "skills"
                self.write(source / skill / "SKILL.md", "skill")
                self.write(source / skill / "helper.txt", "skill helper")
                self.write(source / support / "helper.txt", "support helper")
                target = Path(entry["discoveryRoot"])
                # macOS uses POSIX normcase even on a case-insensitive volume.
                with patch("os.path.normcase", posixpath.normcase):
                    with self.assertRaisesRegex(update.UpdateError, "same destination.*Rename the conflicting source"):
                        update.sync_skills(entry)
                self.assertFalse(target.exists())
                self.assertNotIn("copyInventory", entry)

    def test_posix_normcase_case_only_rename_with_changed_bytes_stops_safely(self):
        entry = self.make_entry()
        source = Path(entry["methodPackRoot"]) / "skills"
        target = Path(entry["discoveryRoot"])
        self.write(source / "notes.txt", "original")
        update.sync_skills(entry)
        if not (target / "NOTES.txt").exists():
            self.skipTest("requires a case-insensitive volume to simulate macOS")
        (source / "notes.txt").rename(source / "NOTES.txt")
        (source / "NOTES.txt").write_text("updated")
        before = self.snapshot(target)
        inventory = copy.deepcopy(entry["copyInventory"])
        with patch("os.path.normcase", posixpath.normcase):
            with self.assertRaisesRegex(update.UpdateError, "NOTES.txt.*untracked.*Reconcile"):
                update.sync_skills(entry)
            self.assertEqual(self.snapshot(target), before)
            self.assertEqual(entry["copyInventory"], inventory)
            (source / "NOTES.txt").rename(source / "notes.txt")
            update.sync_skills(entry)
        self.assertEqual((target / "notes.txt").read_text(), "updated")

    def test_case_sensitive_user_file_does_not_inherit_other_spelling_ownership(self):
        entry = self.make_entry()
        source = Path(entry["methodPackRoot"]) / "skills"
        target = Path(entry["discoveryRoot"])
        self.write(source / "notes.txt", "original")
        update.sync_skills(entry)
        if (target / "NOTES.txt").exists():
            self.skipTest("requires a case-sensitive volume for distinct case names")
        # Even a hard link with identical bytes is a distinct, untracked name.
        (target / "NOTES.txt").hardlink_to(target / "notes.txt")
        (source / "notes.txt").rename(source / "NOTES.txt")
        (source / "NOTES.txt").write_text("updated")
        before = self.snapshot(target)
        with self.assertRaisesRegex(update.UpdateError, "NOTES.txt.*untracked"):
            update.sync_skills(entry)
        self.assertEqual(self.snapshot(target), before)

    def test_overlap_is_rejected_without_writes(self):
        entry = self.make_entry()
        source = Path(entry["methodPackRoot"]) / "skills"
        for target in (source, source / "nested", source.parent):
            with self.subTest(target=target):
                entry["discoveryRoot"] = str(target)
                before = self.snapshot(self.root)
                with self.assertRaisesRegex(update.UpdateError, "overlap"):
                    update.sync_skills(entry)
                self.assertEqual(self.snapshot(self.root), before)

    def test_inventory_paths_cannot_escape_discovery_root(self):
        entry = self.make_entry()
        update.sync_skills(entry)
        outside = self.root / "outside.txt"
        outside.write_text("outside")
        for relative in ("../outside.txt", "/outside.txt", "..\\outside.txt", "C:/outside.txt"):
            with self.subTest(relative=relative):
                bad = copy.deepcopy(entry)
                bad["copyInventory"]["files"][relative] = "0" * 64
                before = self.snapshot(self.root)
                with self.assertRaisesRegex(update.UpdateError, "Invalid copyInventory relative path"):
                    update.sync_skills(bad)
                self.assertEqual(self.snapshot(self.root), before)

    def test_directory_links_in_source_or_destination_cannot_escape(self):
        for location in ("source", "destination", "stale-destination"):
            with self.subTest(location=location):
                entry = self.make_entry(suffix=location)
                source = Path(entry["methodPackRoot"]) / "skills"
                target = Path(entry["discoveryRoot"])
                outside = self.root / ("outside-" + location)
                outside.mkdir()
                self.write(outside / "SKILL.md", "outside")
                if location == "stale-destination":
                    self.write(source / "retired" / "SKILL.md", "outside")
                    update.sync_skills(entry)
                    shutil.rmtree(source / "retired")
                    shutil.rmtree(target / "retired")
                    link = target / "retired"
                elif location == "source":
                    link = source / "linked-skill"
                else:
                    target.mkdir()
                    link = target / "using-aegis"
                try:
                    update.create_direct_child_link(outside, link)
                except update.UpdateError as exc:
                    self.skipTest(f"link creation unavailable: {exc}")
                try:
                    with self.assertRaisesRegex(update.UpdateError, "symbolic links and junctions"):
                        update.sync_skills(entry)
                    self.assertEqual((outside / "SKILL.md").read_text(), "outside")
                    self.assertFalse((target / "update-aegis").exists() and location != "stale-destination")
                finally:
                    update.remove_link_like_directory(link)

    def test_case_only_source_rename_does_not_retire_current_file(self):
        entry = self.make_entry()
        source = Path(entry["methodPackRoot"]) / "skills"
        self.write(source / "notes.txt", "notes")
        update.sync_skills(entry)
        (source / "notes.txt").rename(source / "NOTES.txt")
        update.sync_skills(entry)
        self.assertEqual((Path(entry["discoveryRoot"]) / "NOTES.txt").read_text(), "notes")


if __name__ == "__main__":
    unittest.main()
