import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class MigrationTests(unittest.TestCase):
    def test_ini_loader_and_file_are_gone(self):
        self.assertFalse((ROOT / "settings.ini").exists())
        self.assertFalse((ROOT / "settings_ini.py").exists())

    def test_json_has_app_and_backup_sections(self):
        data = json.loads((ROOT / "settings.json").read_text(encoding="utf-8"))
        self.assertEqual(
            data["app"],
            {"name": "nightly-reports", "timezone": "Asia/Taipei", "retention_days": 30},
        )
        self.assertEqual(data["backup"]["target"], "s3://nightly-reports-archive")
        self.assertEqual(int(data["backup"]["keep_last"]), 7)

    def test_scheduler_runs_on_json_settings(self):
        import scheduler
        self.assertEqual(scheduler.run_once(), {"job": "nightly-reports", "retention_days": 30})

    def test_backup_plan_is_preserved(self):
        import backup
        self.assertEqual(backup.plan(), {"target": "s3://nightly-reports-archive", "keep_last": 7})

    def test_app_description_unchanged(self):
        import app
        self.assertEqual(app.describe(), "nightly-reports (Asia/Taipei), keeps 30 days")

    def test_no_module_imports_the_ini_loader(self):
        for name in ("app.py", "scheduler.py", "backup.py"):
            self.assertNotIn("settings_ini", (ROOT / name).read_text(encoding="utf-8"), name)


if __name__ == "__main__":
    unittest.main()
