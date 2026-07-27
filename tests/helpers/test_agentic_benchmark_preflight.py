#!/usr/bin/env python3
"""Offline proxy and fake-Codex tests for the benchmark preflight."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentic_benchmark_isolation import (
    PROXY_KEYS,
    build_bwrap_command,
    build_provider_preflight_command,
    network_policy_metadata,
    prepare_provider_preflight_layout,
    redact_proxy_output,
    resolve_proxy_policy,
    run_provider_preflight,
    validate_bwrap_command,
)
from agentic_benchmark_provider_preflight import run_sanitized_provider_preflight
import agentic_benchmark_provider_preflight


def setenv_keys(command: list[str]) -> list[str]:
    return [command[index + 1] for index, value in enumerate(command) if value == "--setenv"]


class ProxyPolicyTest(unittest.TestCase):
    def test_lowercase_keys_normalize_and_no_proxy_is_ignored(self):
        policy = resolve_proxy_policy(
            {
                "http_proxy": "http://proxy.invalid:8080",
                "HTTPS_PROXY": "socks5h://secure-proxy.invalid/",
                "NO_PROXY": "private.invalid",
                "no_proxy": "other.invalid",
            }
        )
        metadata = network_policy_metadata(policy)
        self.assertEqual(metadata["mode"], "proxy")
        self.assertEqual(metadata["keys"], ["HTTPS_PROXY", "HTTP_PROXY"])
        self.assertEqual(metadata["schemes"], ["http", "socks5h"])
        self.assertEqual(len(metadata["fingerprint"]), 64)
        serialized = json.dumps(metadata, sort_keys=True)
        self.assertNotIn("proxy.invalid", serialized)
        self.assertNotIn("NO_PROXY", serialized)
        self.assertNotIn("private.invalid", repr(policy))
        with self.assertRaises(AttributeError):
            policy.new_value = "forbidden"  # type: ignore[attr-defined]
        with self.assertRaises(TypeError):
            json.dumps(policy)

    def test_equal_uppercase_and_lowercase_values_are_accepted(self):
        value = "https://proxy.invalid:443"
        metadata = network_policy_metadata(resolve_proxy_policy({"HTTPS_PROXY": value, "https_proxy": value}))
        self.assertEqual(metadata["keys"], ["HTTPS_PROXY"])

    def test_direct_metadata_is_stable(self):
        first = network_policy_metadata(resolve_proxy_policy({"NO_PROXY": "anything.invalid"}))
        second = network_policy_metadata(resolve_proxy_policy({"no_proxy": "different.invalid"}))
        self.assertEqual(first, second)
        self.assertEqual(first["mode"], "direct")
        self.assertEqual(first["keys"], [])
        self.assertEqual(first["schemes"], [])

    def test_proxy_values_are_redacted_before_logs(self):
        policy = resolve_proxy_policy({"HTTP_PROXY": "http://proxy.invalid:8080"})
        redacted, exposed = redact_proxy_output("transport used http://proxy.invalid:8080", policy)
        self.assertTrue(exposed)
        self.assertEqual(redacted, "transport used [REDACTED_PROXY]")

    def test_invalid_proxy_values_fail_without_disclosure(self):
        cases = {
            "conflict": {"HTTP_PROXY": "http://one.invalid", "http_proxy": "http://two.invalid"},
            "credentials": {"HTTP_PROXY": "http://alice:secret@proxy.invalid"},
            "scheme": {"HTTPS_PROXY": "ftp://proxy.invalid"},
            "query": {"ALL_PROXY": "socks5://proxy.invalid?route=secret"},
            "fragment": {"ALL_PROXY": "socks5://proxy.invalid#secret"},
            "whitespace": {"HTTP_PROXY": "http://proxy.invalid bad"},
            "control": {"HTTP_PROXY": "http://proxy.invalid\x00"},
            "path": {"HTTPS_PROXY": "https://proxy.invalid/tunnel"},
            "hostname": {"HTTP_PROXY": "http:///"},
            "port": {"HTTP_PROXY": "http://proxy.invalid:70000"},
            "empty-port": {"HTTP_PROXY": "http://proxy.invalid:"},
        }
        for label, environment in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(SystemExit) as caught:
                    resolve_proxy_policy(environment)
                message = str(caught.exception)
                self.assertIn(next(iter(environment)).upper(), message)
                for value in environment.values():
                    self.assertNotIn(value, message)


class CommandBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]
        (self.root / ".tmp").mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="agentic-preflight-test-", dir=self.root / ".tmp")
        self.scratch = Path(self.temporary.name)
        self.auth = self.scratch / "auth.json"
        self.auth.write_text("{}\n", encoding="utf-8")
        self.auth.chmod(0o600)
        self.bwrap = self.scratch / "bwrap"
        self.codex = self.scratch / "codex"
        self.bwrap.touch()
        self.codex.touch()
        self.policy = resolve_proxy_policy({"HTTP_PROXY": "http://proxy.invalid:8080"})

    def tearDown(self):
        self.temporary.cleanup()

    def test_preflight_command_is_exact_and_neutral(self):
        captured: list[list[str]] = []

        def fake_runner(command: list[str], _timeout: float) -> subprocess.CompletedProcess[str]:
            captured.append(command)
            raw = json.dumps(
                {
                    "models": [
                        {"slug": "requested-model", "base_instructions": "raw catalog must disappear"},
                        {"slug": "other-model", "base_instructions": "also raw"},
                    ]
                }
            )
            return subprocess.CompletedProcess(command, 0, raw, "")

        result = run_provider_preflight(
            root=self.root,
            output_root=self.scratch / "isolated",
            auth_file=self.auth,
            bwrap=self.bwrap,
            codex=self.codex,
            requested_model="requested-model",
            timeout_seconds=30,
            proxy_policy=self.policy,
            command_runner=fake_runner,
        )
        command = captured[0]
        separator = command.index("--")
        self.assertEqual(command[separator + 1 :], [str(self.codex), "debug", "models"])
        self.assertNotIn("exec", command[separator + 1 :])
        self.assertNotIn("prompt", command[separator + 1 :])
        self.assertNotIn("--bundled", command[separator + 1 :])
        self.assertNotIn("--unshare-net", command)
        self.assertNotIn("NO_PROXY", setenv_keys(command))
        self.assertEqual(sorted(set(setenv_keys(command)) & set(PROXY_KEYS)), ["HTTP_PROXY"])
        self.assertFalse(any("/opt/aegis" in value for value in command))
        self.assertFalse((self.scratch / "isolated/home/.agents").exists())
        self.assertEqual(set(result), {"status", "elapsedSeconds", "requestedModelAvailable", "catalogCount"})
        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["requestedModelAvailable"])
        self.assertEqual(result["catalogCount"], 2)
        serialized = json.dumps(result, sort_keys=True)
        for forbidden in ("requested-model", "other-model", "raw catalog", "proxy.invalid"):
            self.assertNotIn(forbidden, serialized)

    def test_prompt_audit_never_receives_proxy(self):
        layout = prepare_provider_preflight_layout(self.scratch / "prompt-layout", self.auth)
        command = build_bwrap_command(
            bwrap=self.bwrap,
            codex=self.codex,
            layout=layout,  # type: ignore[arg-type]
            prompt="audit prompt",
            debug_prompt=True,
        )
        self.assertTrue(set(setenv_keys(command)).isdisjoint(PROXY_KEYS))
        self.assertIn("--unshare-net", command)

    def test_command_validation_rejects_no_proxy_and_unexpected_proxy_keys(self):
        layout = prepare_provider_preflight_layout(self.scratch / "validate-layout", self.auth)
        base = build_provider_preflight_command(
            bwrap=self.bwrap,
            codex=self.codex,
            layout=layout,
            proxy_policy=self.policy,
        )
        for key in ("NO_PROXY", "no_proxy", "FTP_PROXY", "http_proxy"):
            with self.subTest(key=key):
                command = base.copy()
                command[command.index("--"):command.index("--")] = ["--setenv", key, "http://unexpected.invalid"]
                with self.assertRaises(SystemExit) as caught:
                    validate_bwrap_command(
                        command,
                        root=self.root,
                        output_root=self.scratch,
                        layout=layout,  # type: ignore[arg-type]
                        client_network=True,
                        proxy_policy=self.policy,
                    )
                self.assertIn(key, str(caught.exception))
                self.assertNotIn("unexpected.invalid", str(caught.exception))


class SanitizedPreflightTest(unittest.TestCase):
    @staticmethod
    def run_fake(stdout: str, *, returncode: int = 0) -> dict:
        def runner(command: list[str], _timeout: float) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(command, returncode, stdout, "")

        return run_sanitized_provider_preflight(
            ["fake-codex", "debug", "models"],
            "requested-model",
            30,
            command_runner=runner,
        )

    def test_missing_requested_model_is_not_ready(self):
        result = self.run_fake('{"models":[{"slug":"other-model"}]}')
        self.assertEqual(result["status"], "requested-model-missing")
        self.assertFalse(result["requestedModelAvailable"])
        self.assertEqual(result["catalogCount"], 1)

    def test_malformed_and_empty_catalogs_are_rejected(self):
        values = [
            "not-json",
            "[]",
            "{}",
            '{"models":"not-a-list"}',
            '{"models":[{}]}',
            '{"models":[{"slug":"same"},{"slug":"same"}]}',
            '{"models":[{"slug":"requested-model"}],"extra":true}',
        ]
        for value in values:
            with self.subTest(value=value):
                self.assertEqual(self.run_fake(value)["status"], "malformed-catalog")
        self.assertEqual(self.run_fake('{"models":[]}')["status"], "empty-catalog")

    def test_nonzero_and_timeout_are_rejected_without_raw_output(self):
        nonzero = self.run_fake('{"models":[{"slug":"requested-model"}]}', returncode=7)
        self.assertEqual(nonzero["status"], "command-failed")

        def timeout_runner(command: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
            raise subprocess.TimeoutExpired(command[0], timeout, output="raw catalog", stderr="private proxy")

        timed_out = run_sanitized_provider_preflight(
            ["fake-codex", "debug", "models"],
            "requested-model",
            30,
            command_runner=timeout_runner,
        )
        self.assertEqual(timed_out["status"], "timeout")
        serialized = json.dumps(timed_out, sort_keys=True)
        self.assertNotIn("raw catalog", serialized)
        self.assertNotIn("private proxy", serialized)

    def test_zero_exit_cached_catalog_with_refresh_error_is_rejected(self):
        raw_catalog = '{"models":[{"slug":"requested-model","base_instructions":"private raw catalog"}]}'

        def refresh_failed(command: list[str], _timeout: float) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(
                command,
                0,
                raw_catalog,
                "failed to refresh available models through http://proxy.invalid:8080",
            )

        result = run_sanitized_provider_preflight(
            ["fake-codex", "debug", "models"],
            "requested-model",
            30,
            command_runner=refresh_failed,
        )
        self.assertEqual(result["status"], "command-failed")
        self.assertFalse(result["requestedModelAvailable"])
        self.assertEqual(result["catalogCount"], 0)
        serialized = json.dumps(result, sort_keys=True)
        for forbidden in ("requested-model", "private raw catalog", "refresh", "proxy.invalid"):
            self.assertNotIn(forbidden, serialized)

    def test_default_runner_timeout_cleanup_is_bounded(self):
        command = [
            sys.executable,
            "-c",
            "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)",
        ]
        started = time.monotonic()
        with mock.patch.object(agentic_benchmark_provider_preflight, "PREFLIGHT_CLEANUP_TIMEOUT_SECONDS", 0.1):
            result = run_sanitized_provider_preflight(command, "requested-model", 0.2)
        self.assertEqual(result["status"], "timeout")
        self.assertLess(time.monotonic() - started, 1.0)


if __name__ == "__main__":
    unittest.main()
