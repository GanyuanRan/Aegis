#!/usr/bin/env python3
"""Offline proxy and fake-Codex tests for the benchmark preflight."""

from __future__ import annotations

import copy
import json
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import agentic_benchmark_isolation
import agentic_benchmark_provider_preflight
from agentic_benchmark_isolation import (
    PERMISSION_PROFILE_NAME,
    PROXY_KEYS,
    build_bwrap_command,
    build_codex_live_command,
    build_provider_preflight_command,
    direct_codex_environment,
    mount_audit_command,
    network_policy_metadata,
    prepare_arm_layout,
    prepare_provider_preflight_layout,
    prompt_input_summary,
    redact_proxy_output,
    reset_directory,
    resolve_proxy_policy,
    resolve_codex_direct_executable,
    run_provider_preflight,
    tool_sandbox_audit_command,
    validate_bwrap_command,
)
from agentic_benchmark_provider_preflight import (
    CredentialPolicy,
    freeze_auth_file,
    run_sanitized_provider_preflight,
    scrub_confidential_artifact_tree,
)


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
        shutil.copy2(shutil.which("true") or "/usr/bin/true", self.codex)
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

    def test_repeated_commands_read_the_same_sealed_auth_from_offset_zero(self):
        self.auth.write_text('{"OPENAI_API_KEY":"abc"}', encoding="utf-8")
        payload = self.auth.read_bytes()
        frozen = freeze_auth_file(self.auth)
        script = "import os,sys; sys.stdout.buffer.write(os.read(int(sys.argv[2]), 1048576))"
        command = [
            sys.executable,
            "-c",
            script,
            "--ro-bind-data",
            str(frozen.descriptor),
            "/auth.json",
            "--",
        ]
        try:
            first = agentic_benchmark_provider_preflight._default_command_runner(command, 1.0)
            second = agentic_benchmark_provider_preflight._default_command_runner(command, 1.0)
        finally:
            frozen.close()
        self.assertEqual(first.stdout.encode(), payload)
        self.assertEqual(second.stdout.encode(), payload)

    def test_concurrent_commands_do_not_share_the_sealed_auth_offset(self):
        self.auth.write_text('{"OPENAI_API_KEY":"abc"}', encoding="utf-8")
        payload = self.auth.read_bytes()
        frozen = freeze_auth_file(self.auth)
        gate = self.scratch / "read-gate"
        ready = [self.scratch / f"reader-{number}.ready" for number in range(2)]
        script = (
            "import os,pathlib,sys,time; "
            "fd=int(sys.argv[2]); ready=pathlib.Path(sys.argv[5]); gate=pathlib.Path(sys.argv[6]); "
            "ready.touch(); "
            "deadline=time.monotonic()+1; "
            "\nwhile not gate.exists() and time.monotonic()<deadline: time.sleep(0.001); "
            "sys.stdout.buffer.write(os.read(fd, 1048576))"
        )

        def run(number: int) -> subprocess.CompletedProcess[str]:
            command = [
                sys.executable,
                "-c",
                script,
                "--ro-bind-data",
                str(frozen.descriptor),
                "/auth.json",
                "--",
                str(ready[number]),
                str(gate),
            ]
            return agentic_benchmark_provider_preflight._default_command_runner(command, 2.0)

        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(run, number) for number in range(2)]
                deadline = time.monotonic() + 1
                while not all(path.exists() for path in ready) and time.monotonic() < deadline:
                    time.sleep(0.001)
                self.assertTrue(all(path.exists() for path in ready))
                gate.touch()
                results = [future.result() for future in futures]
        finally:
            frozen.close()
        self.assertEqual([result.stdout.encode() for result in results], [payload, payload])

    def test_popen_failure_closes_each_fresh_memfd_descriptor(self):
        self.auth.write_text('{"OPENAI_API_KEY":"abc"}', encoding="utf-8")
        frozen = freeze_auth_file(self.auth)
        command = [
            sys.executable,
            "-c",
            "pass",
            "--ro-bind-data",
            str(frozen.descriptor),
            "/auth.json",
            "--",
        ]
        opened: list[int] = []
        real_open = os.open

        def track_open(path: str, flags: int) -> int:
            descriptor = real_open(path, flags)
            opened.append(descriptor)
            return descriptor

        try:
            with mock.patch.object(agentic_benchmark_provider_preflight.os, "open", side_effect=track_open), mock.patch.object(
                agentic_benchmark_provider_preflight.subprocess,
                "Popen",
                side_effect=OSError("spawn failed"),
            ):
                with self.assertRaises(OSError):
                    agentic_benchmark_provider_preflight._default_command_runner(command, 1.0)
            self.assertEqual(len(opened), 1)
            with self.assertRaises(OSError):
                os.fstat(opened[0])
        finally:
            for descriptor in opened:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
            frozen.close()

    def test_one_command_rewrites_every_reference_to_the_same_fresh_descriptor(self):
        self.auth.write_text('{"OPENAI_API_KEY":"abc"}', encoding="utf-8")
        frozen = freeze_auth_file(self.auth)
        command = [
            "fake-bwrap",
            "--ro-bind-data",
            str(frozen.descriptor),
            "/first-auth.json",
            "--ro-bind-data",
            str(frozen.descriptor),
            "/second-auth.json",
            "--",
            "fake-codex",
        ]
        try:
            with mock.patch.object(agentic_benchmark_provider_preflight.subprocess, "Popen") as popen:
                agentic_benchmark_provider_preflight.popen_with_independent_memfd_offsets(command)
            launched = popen.call_args.args[0]
            fresh_descriptor = int(launched[2])
            self.assertEqual(launched[5], str(fresh_descriptor))
            self.assertEqual(popen.call_args.kwargs["pass_fds"], (fresh_descriptor,))
            with self.assertRaises(OSError):
                os.fstat(fresh_descriptor)
        finally:
            frozen.close()

    def test_payload_prompt_proc_fd_zero_stays_literal_and_is_not_inherited(self):
        self.auth.write_text('{"OPENAI_API_KEY":"abc"}', encoding="utf-8")
        frozen = freeze_auth_file(self.auth)
        command = [
            "fake-bwrap",
            "--ro-bind-data",
            str(frozen.descriptor),
            "/auth.json",
            "--",
            "fake-codex",
            "prompt",
            "/proc/self/fd/0",
        ]
        try:
            with mock.patch.object(agentic_benchmark_provider_preflight.subprocess, "Popen") as popen:
                agentic_benchmark_provider_preflight.popen_with_independent_memfd_offsets(command)
            launched = popen.call_args.args[0]
            inherited = popen.call_args.kwargs["pass_fds"]
            self.assertEqual(launched[command.index("--") + 1 :], command[command.index("--") + 1 :])
            self.assertNotIn(0, inherited)
            self.assertEqual(len(inherited), 1)
        finally:
            frozen.close()

    def test_direct_client_auth_link_gets_a_private_offset_zero_descriptor(self):
        self.auth.write_text('{"OPENAI_API_KEY":"abc"}', encoding="utf-8")
        frozen = freeze_auth_file(self.auth)
        auth_link = self.scratch / "direct-home/.codex/auth.json"
        auth_link.parent.mkdir(parents=True)
        auth_link.touch(mode=0o600)
        try:
            with mock.patch.object(agentic_benchmark_provider_preflight.subprocess, "Popen") as popen:
                agentic_benchmark_provider_preflight.popen_with_independent_auth_link(
                    ["fake-codex"], auth_file=frozen.mount_path, auth_link=auth_link,
                )
            inherited = popen.call_args.kwargs["pass_fds"]
            self.assertEqual(len(inherited), 1)
            self.assertEqual(auth_link.readlink(), Path(f"/proc/self/fd/{inherited[0]}"))
            with self.assertRaises(OSError):
                os.fstat(inherited[0])
            self.assertEqual(os.lseek(frozen.descriptor, 0, os.SEEK_CUR), 0)
        finally:
            frozen.close()

    def test_unrelated_payload_proc_fd_is_neither_rewritten_nor_inherited(self):
        self.auth.write_text('{"OPENAI_API_KEY":"abc"}', encoding="utf-8")
        frozen = freeze_auth_file(self.auth)
        unrelated = os.memfd_create("unrelated-payload")
        payload = f"/proc/self/fd/{unrelated}"
        command = [
            "fake-bwrap",
            "--ro-bind-data",
            str(frozen.descriptor),
            "/auth.json",
            "--",
            "fake-codex",
            payload,
        ]
        try:
            with mock.patch.object(agentic_benchmark_provider_preflight.subprocess, "Popen") as popen:
                agentic_benchmark_provider_preflight.popen_with_independent_memfd_offsets(command)
            launched = popen.call_args.args[0]
            inherited = popen.call_args.kwargs["pass_fds"]
            self.assertEqual(launched[-1], payload)
            self.assertNotIn(unrelated, inherited)
            self.assertEqual(len(inherited), 1)
        finally:
            os.close(unrelated)
            frozen.close()

    def test_payload_literal_separator_stays_opaque_and_can_launch(self):
        self.auth.write_text('{"OPENAI_API_KEY":"abc"}', encoding="utf-8")
        frozen = freeze_auth_file(self.auth)
        command = [
            "fake-bwrap",
            "--ro-bind-data",
            str(frozen.descriptor),
            "/auth.json",
            "--",
            "fake-codex",
            "prompt-before",
            "--",
            "prompt-after",
        ]
        try:
            with mock.patch.object(agentic_benchmark_provider_preflight.subprocess, "Popen") as popen:
                agentic_benchmark_provider_preflight.popen_with_independent_memfd_offsets(command)
            launched = popen.call_args.args[0]
            separator = command.index("--")
            self.assertEqual(launched[separator + 1 :], command[separator + 1 :])
            self.assertEqual(popen.call_count, 1)
        finally:
            frozen.close()

    def test_ro_bind_data_rejects_empty_or_option_shaped_targets_before_popen(self):
        self.auth.write_text('{"OPENAI_API_KEY":"abc"}', encoding="utf-8")
        frozen = freeze_auth_file(self.auth)
        try:
            for target in ("", "-relative-option", "--bind"):
                command = [
                    "fake-bwrap",
                    "--ro-bind-data",
                    str(frozen.descriptor),
                    target,
                    "--",
                    "fake-codex",
                ]
                with self.subTest(target=target), mock.patch.object(
                    agentic_benchmark_provider_preflight.subprocess,
                    "Popen",
                ) as popen:
                    with self.assertRaises(SystemExit):
                        agentic_benchmark_provider_preflight.popen_with_independent_memfd_offsets(command)
                    popen.assert_not_called()
        finally:
            frozen.close()

    def test_memfd_spawn_rejects_ambiguous_or_malformed_bwrap_prefixes(self):
        malformed = [
            ["fake-bwrap", "fake-codex"],
            ["fake-bwrap", "--ro-bind-data", "--", "fake-codex"],
            ["fake-bwrap", "--ro-bind-data", "not-a-descriptor", "/auth.json", "--", "fake-codex"],
        ]
        for command in malformed:
            with self.subTest(command=command), mock.patch.object(
                agentic_benchmark_provider_preflight.subprocess,
                "Popen",
            ):
                with self.assertRaises(SystemExit):
                    agentic_benchmark_provider_preflight.popen_with_independent_memfd_offsets(command)

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

    def test_prompt_audit_uses_only_the_validated_proxy_policy(self):
        layout = prepare_provider_preflight_layout(self.scratch / "prompt-layout", self.auth)
        command = build_bwrap_command(
            bwrap=self.bwrap,
            codex=self.codex,
            layout=layout,  # type: ignore[arg-type]
            prompt="audit prompt",
            debug_prompt=True,
            isolate_network=False,
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
        self.assertEqual(sorted(set(setenv_keys(command)) & set(PROXY_KEYS)), ["HTTP_PROXY"])
        self.assertNotIn("--unshare-net", command)

    def test_mount_audit_remains_network_disabled_and_receives_no_proxy(self):
        layout = prepare_provider_preflight_layout(self.scratch / "mount-layout", self.auth)
        command = mount_audit_command(
            bwrap=self.bwrap,
            codex=self.codex,
            layout=layout,  # type: ignore[arg-type]
        )
        validate_bwrap_command(
            command,
            root=self.root,
            output_root=self.scratch,
            layout=layout,  # type: ignore[arg-type]
        )
        self.assertTrue(set(setenv_keys(command)).isdisjoint(PROXY_KEYS))
        self.assertIn("--unshare-net", command)

    def test_live_command_and_no_model_probe_use_permission_profile_bwrap(self):
        seed = self.root / "tests/e2e/fixtures/replay-projects/change-necessity-before-edit"
        layout = prepare_arm_layout(
            self.scratch / "sandbox-layout", seed, self.auth, None, virtualized_paths=False,
        )
        forbidden = [self.root / "tests/helpers/score_agentic_benchmark_outcome.py"]
        probe = tool_sandbox_audit_command(
            codex=self.codex,
            layout=layout,
            forbidden_files=forbidden,
            skill_file=None,
        )
        self.assertEqual(probe[:6], [
            str(self.codex), "sandbox", "--permission-profile",
            PERMISSION_PROFILE_NAME, "--cd", str(layout["workspace"]),
        ])
        self.assertNotIn("use_legacy_landlock", probe)

        live = build_codex_live_command(
            codex=self.codex,
            layout=layout,
            prompt="prompt",
            model="model",
        )
        self.assertEqual(live[0], str(self.codex))
        self.assertNotIn("--sandbox", live)
        self.assertNotIn("use_legacy_landlock", live)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", live)
        environment = direct_codex_environment(layout, self.policy)
        self.assertEqual(environment["HOME"], str(layout["home"]))
        self.assertEqual(environment["CODEX_HOME"], str(layout["home"] / ".codex"))
        self.assertEqual(environment["TMPDIR"], str(layout["tmp"]))
        self.assertEqual(environment["HTTP_PROXY"], "http://proxy.invalid:8080")

    def test_live_command_resolves_the_packaged_native_codex_runtime(self):
        package = self.scratch / "codex-package"
        launcher = package / "bin/codex.js"
        target = {
            "x86_64": "x86_64-unknown-linux-musl",
            "aarch64": "aarch64-unknown-linux-musl",
        }[os.uname().machine]
        native = package / f"node_modules/@openai/codex-test/vendor/{target}/bin/codex"
        launcher.parent.mkdir(parents=True)
        launcher.touch()
        native.parent.mkdir(parents=True)
        shutil.copy2(shutil.which("true") or "/usr/bin/true", native)
        self.assertEqual(resolve_codex_direct_executable(launcher), native)

    def test_direct_codex_runtime_rejects_unknown_wrappers(self):
        wrapper = self.scratch / "codex-wrapper"
        wrapper.write_text("#!/bin/sh\nexec codex \"$@\"\n", encoding="utf-8")
        wrapper.chmod(0o755)
        with self.assertRaises(SystemExit):
            resolve_codex_direct_executable(wrapper)

    def test_direct_skill_projection_is_read_only_and_cleanup_safe(self):
        snapshot = self.scratch / "snapshot"
        skill = snapshot / "skills/example/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("---\nname: example\n---\n", encoding="utf-8")
        seed = self.root / "tests/e2e/fixtures/replay-projects/change-necessity-before-edit"
        layout = prepare_arm_layout(
            self.scratch / "projection-layout", seed, self.auth, snapshot,
            virtualized_paths=False,
        )
        projected = layout["home"] / ".agents/skills/aegis/example/SKILL.md"
        self.assertEqual(projected.stat().st_nlink, 1)
        self.assertEqual(projected.stat().st_mode & 0o222, 0)
        self.assertIsNone(scrub_confidential_artifact_tree(
            layout["root"], resolve_proxy_policy({}), CredentialPolicy(()),
        ))

    def test_direct_skill_projection_rejects_source_symlinks(self):
        snapshot = self.scratch / "symlink-snapshot"
        skill_directory = snapshot / "skills/example"
        skill_directory.mkdir(parents=True)
        private = self.scratch / "private-source.txt"
        private.write_text("must not be projected", encoding="utf-8")
        (skill_directory / "SKILL.md").symlink_to(private)
        seed = self.root / "tests/e2e/fixtures/replay-projects/change-necessity-before-edit"
        with self.assertRaises(SystemExit):
            prepare_arm_layout(
                self.scratch / "symlink-layout", seed, self.auth, snapshot,
                virtualized_paths=False,
            )
        projected = self.scratch / "symlink-layout/home/.agents/skills/aegis/example/SKILL.md"
        self.assertTrue(projected.is_symlink())
        self.assertEqual(projected.readlink(), private)

    def test_prompt_audit_failure_redacts_proxy_values(self):
        proxy = "http://proxy.invalid:8080"
        policy = resolve_proxy_policy({"HTTP_PROXY": proxy})
        with self.assertRaises(SystemExit) as caught:
            agentic_benchmark_isolation.run_command(
                [sys.executable, "-c", f"import sys; sys.stderr.write({proxy!r}); raise SystemExit(9)", "--"],
                "prompt audit",
                proxy_policy=policy,
            )
        self.assertIn("[REDACTED_PROXY]", str(caught.exception))
        self.assertNotIn(proxy, str(caught.exception))

    def test_prompt_summary_ignores_only_volatile_top_level_item_ids(self):
        first = [
            {
                "id": "msg_first",
                "type": "message",
                "role": "developer",
                "content": [{"type": "input_text", "text": "same", "id": "nested-first"}],
            }
        ]
        second = copy.deepcopy(first)
        second[0]["id"] = "msg_second"
        first_summary = prompt_input_summary(first, "absent", [])
        second_summary = prompt_input_summary(second, "absent", [])
        self.assertNotEqual(first_summary["inputHash"], second_summary["inputHash"])
        self.assertEqual(first_summary["nonSkillInputHash"], second_summary["nonSkillInputHash"])

        first[0]["content"][0]["text"] = (
            '<permission_profile><entry access="read"><path>'
            '/home/benchmark/.codex/tmp/arg0/codex-arg0First123</path></entry></permission_profile>'
        )
        second[0]["content"][0]["text"] = first[0]["content"][0]["text"].replace("First123", "Second456")
        self.assertEqual(
            prompt_input_summary(first, "absent", [])["nonSkillInputHash"],
            prompt_input_summary(second, "absent", [])["nonSkillInputHash"],
        )

        for label, mutate in (
            ("role", lambda value: value[0].update(role="user")),
            ("type", lambda value: value[0].update(type="different")),
            ("content", lambda value: value[0]["content"][0].update(text="changed")),
            ("nested-id", lambda value: value[0]["content"][0].update(id="nested-second")),
        ):
            with self.subTest(label=label):
                drifted = copy.deepcopy(first)
                mutate(drifted)
                self.assertNotEqual(
                    first_summary["nonSkillInputHash"],
                    prompt_input_summary(drifted, "absent", [])["nonSkillInputHash"],
                )

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
            "--",
        ]
        started = time.monotonic()
        result = run_sanitized_provider_preflight(command, "requested-model", 0.2)
        self.assertEqual(result["status"], "timeout")
        self.assertLess(time.monotonic() - started, 1.0)

    def test_outer_supervised_isolation_and_preflight_children_do_not_create_sessions(self):
        command = [sys.executable, "-c", "import os; print(os.getpgrp())", "--"]
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
