#!/usr/bin/env python3
"""Offline proxy and fake-Codex tests for the benchmark preflight."""

from __future__ import annotations

import json
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import agentic_benchmark_isolation
import agentic_benchmark_provider_preflight
from agentic_benchmark_isolation import (
    PROXY_KEYS,
    build_bwrap_command,
    build_provider_preflight_command,
    network_policy_metadata,
    prepare_provider_preflight_layout,
    redact_proxy_output,
    reset_directory,
    resolve_proxy_policy,
    run_provider_preflight,
    validate_bwrap_command,
)
from agentic_benchmark_provider_preflight import freeze_auth_file, run_sanitized_provider_preflight


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
            "malformed-percent": {"HTTP_PROXY": "http://proxy.invalid/%ZZ"},
            "backslash": {"HTTP_PROXY": "http://proxy.invalid\\route"},
            "leading-hyphen": {"HTTP_PROXY": "http://-proxy.invalid"},
            "empty-label": {"HTTP_PROXY": "http://proxy..invalid"},
            "unicode-host": {"HTTP_PROXY": "http://prøxy.invalid"},
        }
        for label, environment in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(SystemExit) as caught:
                    resolve_proxy_policy(environment)
                message = str(caught.exception)
                self.assertIn(next(iter(environment)).upper(), message)
                for value in environment.values():
                    self.assertNotIn(value, message)

    def test_valid_dns_ipv4_and_bracketed_ipv6_are_accepted(self):
        policy = resolve_proxy_policy(
            {
                "HTTP_PROXY": "http://proxy.example:8080",
                "HTTPS_PROXY": "https://127.0.0.1:443",
                "ALL_PROXY": "socks5h://[2001:db8::1]:1080",
            }
        )
        self.assertEqual(network_policy_metadata(policy)["keys"], list(PROXY_KEYS))


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
        isolated_root = self.scratch / "provider-preflight-isolated"

        def fake_runner(command: list[str], _timeout: float) -> subprocess.CompletedProcess[str]:
            captured.append(command)
            codex_home = isolated_root / "home/.codex"
            (codex_home / "models_cache.json").write_text("private raw catalog", encoding="utf-8")
            (codex_home / "log").mkdir()
            (codex_home / "log/debug.log").write_text(
                "provider used http://proxy.invalid:8080",
                encoding="utf-8",
            )
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
            batch_root=self.scratch,
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
        self.assertFalse(isolated_root.exists())
        self.assertEqual(set(result), {"status", "elapsedSeconds", "requestedModelAvailable", "catalogCount"})
        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["requestedModelAvailable"])
        self.assertEqual(result["catalogCount"], 2)
        serialized = json.dumps(result, sort_keys=True)
        for forbidden in ("requested-model", "other-model", "raw catalog", "proxy.invalid"):
            self.assertNotIn(forbidden, serialized)

    def test_sealed_auth_memfd_is_readable_through_a_real_bwrap_mount(self):
        self.auth.write_text('{"OPENAI_API_KEY":"abc"}', encoding="utf-8")
        payload = self.auth.read_bytes()
        frozen = freeze_auth_file(self.auth)
        try:
            layout = prepare_provider_preflight_layout(self.scratch / "memfd-layout", frozen.mount_path)
            command = build_provider_preflight_command(
                bwrap=Path(shutil.which("bwrap") or "/missing/bwrap"),
                codex=self.codex,
                layout=layout,
                proxy_policy=self.policy,
            )
            validate_bwrap_command(
                command,
                root=self.root,
                output_root=self.scratch,
                layout=layout,  # type: ignore[arg-type]
                client_network=True,
                proxy_policy=self.policy,
            )
            prefix = command[: command.index("--")]
            self.assertIn("--ro-bind-data", prefix)
            self.assertIn(str(frozen.descriptor), prefix)
            bwrap = Path(shutil.which("bwrap") or "/missing/bwrap")
            mount = subprocess.run(
                [
                    str(bwrap), "--die-with-parent", "--unshare-net", "--ro-bind", "/usr", "/usr",
                    "--ro-bind", "/bin", "/bin", "--ro-bind", "/lib", "/lib", "--ro-bind", "/lib64", "/lib64",
                    "--proc", "/proc", "--dev", "/dev", "--ro-bind-data", str(frozen.descriptor), "/auth.json",
                    "--", "/usr/bin/sha256sum", "/auth.json",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                pass_fds=(frozen.descriptor,),
                check=False,
            )
            self.assertEqual(mount.returncode, 0, mount.stderr)
            self.assertEqual(mount.stdout.split()[0], hashlib.sha256(payload).hexdigest())
        finally:
            frozen.close()

    def test_failure_timeout_and_exception_remove_the_entire_isolated_root(self):
        for status in ("failure", "timeout", "exception"):
            with self.subTest(status=status):
                isolated_root = self.scratch / "provider-preflight-isolated"

                def fake_runner(command: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
                    codex_home = isolated_root / "home/.codex"
                    (codex_home / "models_cache.json").write_text("private raw catalog", encoding="utf-8")
                    (codex_home / "debug.log").write_text("http://proxy.invalid:8080", encoding="utf-8")
                    if status == "timeout":
                        raise subprocess.TimeoutExpired(command[0], timeout, output="raw", stderr="private")
                    if status == "exception":
                        raise RuntimeError("private provider exception")
                    return subprocess.CompletedProcess(command, 9, "raw catalog", "private stderr")

                arguments = {
                    "root": self.root,
                    "batch_root": self.scratch,
                    "auth_file": self.auth,
                    "bwrap": self.bwrap,
                    "codex": self.codex,
                    "requested_model": "requested-model",
                    "timeout_seconds": 30,
                    "proxy_policy": self.policy,
                    "command_runner": fake_runner,
                }
                if status == "exception":
                    with self.assertRaises(RuntimeError):
                        run_provider_preflight(**arguments)
                    result = {}
                else:
                    result = run_provider_preflight(**arguments)
                    self.assertEqual(result["status"], "timeout" if status == "timeout" else "command-failed")
                self.assertFalse(isolated_root.exists())
                serialized = json.dumps(result, sort_keys=True)
                for forbidden in ("raw catalog", "private stderr", "proxy.invalid"):
                    self.assertNotIn(forbidden, serialized)

    def test_cleanup_failure_fails_closed_without_disclosure(self):
        isolated_root = self.scratch / "provider-preflight-isolated"
        patcher = mock.patch(
            "agentic_benchmark_isolation.shutil.rmtree",
            side_effect=OSError("private cleanup detail http://proxy.invalid:8080"),
        )

        def fake_runner(command: list[str], _timeout: float) -> subprocess.CompletedProcess[str]:
            (isolated_root / "home/.codex/models_cache.json").write_text("raw catalog", encoding="utf-8")
            patcher.start()
            return subprocess.CompletedProcess(command, 0, '{"models":[{"slug":"requested-model"}]}', "")

        try:
            with self.assertRaises(SystemExit) as caught:
                run_provider_preflight(
                    root=self.root,
                    batch_root=self.scratch,
                    auth_file=self.auth,
                    bwrap=self.bwrap,
                    codex=self.codex,
                    requested_model="requested-model",
                    timeout_seconds=30,
                    proxy_policy=self.policy,
                    command_runner=fake_runner,
                )
        finally:
            patcher.stop()
            if isolated_root.exists():
                shutil.rmtree(isolated_root)
        self.assertEqual(str(caught.exception), "provider preflight isolated root cleanup failed")
        self.assertNotIn("proxy.invalid", str(caught.exception))

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

    def test_command_environment_is_an_exact_prefix_only_contract(self):
        layout = prepare_provider_preflight_layout(self.scratch / "exact-env-layout", self.auth)
        base = build_provider_preflight_command(
            bwrap=self.bwrap,
            codex=self.codex,
            layout=layout,
            proxy_policy=self.policy,
        )
        separator = base.index("--")
        child_argument = base.copy()
        child_argument.extend(["--setenv", "NO_PROXY", "child-only-secret"])
        validate_bwrap_command(
            child_argument,
            root=self.root,
            output_root=self.scratch,
            layout=layout,  # type: ignore[arg-type]
            client_network=True,
            proxy_policy=self.policy,
        )

        mutations: list[tuple[str, list[str], str]] = []
        arbitrary = base.copy()
        arbitrary[separator:separator] = ["--setenv", "EXTRA", "private-value"]
        mutations.append(("arbitrary", arbitrary, "EXTRA"))
        duplicate = base.copy()
        duplicate[separator:separator] = ["--setenv", "HOME", "private-value"]
        mutations.append(("duplicate", duplicate, "HOME"))
        drift = base.copy()
        home_value = drift.index("HOME") + 1
        drift[home_value] = "/private/home"
        mutations.append(("base-drift", drift, "HOME"))
        missing = base.copy()
        tmpdir_flag = missing.index("TMPDIR") - 1
        del missing[tmpdir_flag : tmpdir_flag + 3]
        mutations.append(("missing", missing, "TMPDIR"))
        proxy_drift = base.copy()
        proxy_value = proxy_drift.index("HTTP_PROXY") + 1
        proxy_drift[proxy_value] = "http://private.invalid"
        mutations.append(("proxy-drift", proxy_drift, "HTTP_PROXY"))
        for label, command, key in mutations:
            with self.subTest(label=label):
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
                for secret in ("private-value", "/private/home", "private.invalid"):
                    self.assertNotIn(secret, str(caught.exception))

    def test_reset_directory_rejects_leaf_symlinks_without_touching_targets(self):
        sibling = self.scratch / "sibling"
        sibling.mkdir()
        sibling_marker = sibling / "marker"
        sibling_marker.write_text("keep", encoding="utf-8")
        dot_marker = self.scratch / "dot-marker"
        dot_marker.write_text("keep", encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="agentic-preflight-outside-") as outside_value:
            outside = Path(outside_value)
            outside_marker = outside / "marker"
            outside_marker.write_text("keep", encoding="utf-8")
            links = {
                "dot-link": Path("."),
                "sibling-link": Path("sibling"),
                "outside-link": outside,
            }
            for name, target in links.items():
                link = self.scratch / name
                link.symlink_to(target, target_is_directory=True)
                with self.subTest(name=name), self.assertRaises(SystemExit):
                    reset_directory(link, self.root)
            self.assertEqual(outside_marker.read_text(encoding="utf-8"), "keep")
        self.assertEqual(sibling_marker.read_text(encoding="utf-8"), "keep")
        self.assertEqual(dot_marker.read_text(encoding="utf-8"), "keep")


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
        result = run_sanitized_provider_preflight(command, "requested-model", 0.2)
        self.assertEqual(result["status"], "timeout")
        self.assertLess(time.monotonic() - started, 1.0)

    def test_outer_supervised_isolation_and_preflight_children_do_not_create_sessions(self):
        command = [sys.executable, "-c", "import os; print(os.getpgrp())"]
        isolation_group = agentic_benchmark_isolation.run_command(
            command,
            "isolation child",
            timeout=1.0,
            process_group_supervised=True,
        )
        preflight = agentic_benchmark_provider_preflight._default_command_runner(
            command,
            1.0,
            process_group_supervised=True,
        )
        self.assertEqual(int(isolation_group.strip()), os.getpgrp())
        self.assertEqual(int(preflight.stdout.strip()), os.getpgrp())


if __name__ == "__main__":
    unittest.main()
