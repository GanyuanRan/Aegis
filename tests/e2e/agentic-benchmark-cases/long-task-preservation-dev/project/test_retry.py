import contextlib
import io
import unittest

import config
import report_cli
import retry
from services import SERVICES


class RetryProfileTests(unittest.TestCase):
    def test_services_without_explicit_profile_inherit_balanced(self):
        self.assertEqual(retry.attempts_for("search"), 3)
        self.assertEqual(retry.attempts_for("reports"), 3)
        self.assertEqual(config.resolved_profile_name(None), "balanced")

    def test_billing_keeps_its_explicit_conservative_choice(self):
        self.assertEqual(SERVICES["billing"]["profile"], "conservative")
        self.assertEqual(retry.attempts_for("billing"), 5)

    def test_conservative_profile_still_exists(self):
        self.assertIn("conservative", config.PROFILES)
        self.assertEqual(config.PROFILES["conservative"]["attempts"], 5)

    def test_legacy_alias_is_retired(self):
        self.assertFalse(hasattr(config, "LEGACY_DEFAULT"))

    def test_report_cli_service_filter(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = report_cli.main(["--service", "billing"])
        self.assertEqual(code, 0)
        lines = [line for line in out.getvalue().splitlines() if line.strip()]
        self.assertEqual(len(lines), 1)
        self.assertIn("billing", lines[0])
        self.assertIn("conservative", lines[0])

    def test_report_cli_service_filter_selects_one_non_billing_service(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = report_cli.main(["--service", "search"])
        self.assertEqual(code, 0)
        lines = [line for line in out.getvalue().splitlines() if line.strip()]
        self.assertEqual(len(lines), 1)
        self.assertIn("search", lines[0])

    def test_report_cli_without_filter_lists_every_service(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = report_cli.main([])
        self.assertEqual(code, 0)
        text = out.getvalue()
        for name in ("billing", "reports", "search"):
            self.assertIn(name, text)


if __name__ == "__main__":
    unittest.main()
