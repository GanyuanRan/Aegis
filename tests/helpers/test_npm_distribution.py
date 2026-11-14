"""Exercise the packed registry artifact, not just its source manifest."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("npm_builder", ROOT / "scripts/build-npm-package.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class NpmDistributionTests(unittest.TestCase):
    def test_scoped_artifact_is_complete_and_loadable(self):
        before = (ROOT / "package.json").read_bytes()
        with tempfile.TemporaryDirectory(prefix="aegis-artifact-test-") as directory:
            work = Path(directory).resolve()
            result = builder.build("@aegis-artifact-test/aegis", work / "output")
            self.assertFalse(result["published"])
            installed = work / "node_modules/@aegis-artifact-test/aegis"
            installed.mkdir(parents=True)
            with tarfile.open(result["tarball"], "r:gz") as archive:
                for member in archive.getmembers():
                    relative = Path(member.name).relative_to("package")
                    target = installed / relative
                    self.assertTrue(target.resolve().is_relative_to(installed))
                    self.assertTrue(member.isfile())
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.extractfile(member).read())
            manifest = json.loads((installed / "package.json").read_text())
            self.assertEqual(manifest["name"], "@aegis-artifact-test/aegis")
            self.assertNotIn("private", manifest)
            self.assertEqual(manifest["publishConfig"]["access"], "public")
            self.assertEqual(manifest["peerDependencies"], json.loads(before)["peerDependencies"])
            patch = (installed / "extensions/dsh/cordis.patch.yml").read_text()
            self.assertIn("id: aegis-method-pack", patch)
            self.assertIn("@aegis-artifact-test/aegis/extensions/dsh/index.js", patch)
            subprocess.run([
                "node", "-e",
                "const {createRequire}=require('node:module');"
                "const r=createRequire(process.argv[1]);"
                "r.resolve('@aegis-artifact-test/aegis/extensions/dsh/index.js');",
                str(work / "probe.cjs"),
            ], check=True)
            skills = subprocess.check_output(["git", "ls-files", "skills"], cwd=ROOT, text=True).splitlines()
            self.assertGreater(len(skills), 20)
            for relative in skills:
                self.assertEqual((installed / relative).read_bytes(), (ROOT / relative).read_bytes(), relative)
            for forbidden in (".git", "tests", "docs/archive", ".github", "node_modules"):
                self.assertFalse((installed / forbidden).exists(), forbidden)
            doctor = subprocess.run([
                sys.executable, str(installed / "scripts/aegis-doctor.py"),
                "--config", str(work / "config.toml"), "--write-config", "--json",
            ], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(doctor.returncode, 0, doctor.stdout + doctor.stderr)
            health = json.loads(doctor.stdout)
            self.assertTrue(health["ok"])
            self.assertEqual(health["workspaceSupport"], "available")
            self.assertEqual(health["configStatus"], "configured")
            with self.assertRaises(FileExistsError):
                builder.build("@aegis-artifact-test/aegis", work / "output")
        self.assertEqual((ROOT / "package.json").read_bytes(), before)

    def test_unscoped_or_unsafe_names_are_rejected(self):
        for name in ("aegis", "aegis-method-pack", "@../aegis", "@owner/other", "@owner/aegis;echo"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                builder.build(name, Path("unused"))

    def test_untracked_files_are_excluded_and_tracked_private_paths_fail(self):
        with tempfile.TemporaryDirectory(prefix="aegis-payload-test-") as directory:
            work = Path(directory).resolve()
            root = work / "source"
            root.mkdir()
            required = (
                "package.json", "LICENSE", "skills/using-aegis/SKILL.md",
                "scripts/aegis-doctor.py", "scripts/aegis-workspace.py",
                "extensions/dsh/index.js", "extensions/dsh/bootstrap.js",
                "extensions/dsh/cordis.patch.yml",
            )
            for relative in required:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
            (root / "docs/archive").mkdir(parents=True)
            (root / "docs/archive/private.md").write_text("must never ship")
            result = builder.build("@aegis-artifact-test/aegis", work / "output", root)
            with tarfile.open(result["tarball"], "r:gz") as archive:
                self.assertNotIn("package/docs/archive/private.md", archive.getnames())
            subprocess.run(["git", "add", "docs"], cwd=root, check=True, capture_output=True)
            with self.assertRaisesRegex(ValueError, "Non-distribution path"):
                builder.build("@aegis-artifact-test/aegis", work / "other", root)


if __name__ == "__main__":
    unittest.main()
