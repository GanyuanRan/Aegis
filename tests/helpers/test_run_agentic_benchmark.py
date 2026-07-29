#!/usr/bin/env python3
"""Offline fake-host contract tests for the repeated agentic benchmark runner."""

from __future__ import annotations

import copy
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_agentic_benchmark as benchmark_runner
import agentic_benchmark_provider_preflight
from run_agentic_benchmark import (
    ARMS,
    AUTHORITY_BOUNDARY,
    aggregate,
    communicate_with_timeout,
    execute_target,
    initial_ledger,
    require_execution_opt_in,
    resolve_auth_file,
    schedule_targets,
    validate_live_isolation_report,
)
from agentic_benchmark_isolation import resolve_proxy_policy
from agentic_benchmark_provider_preflight import CredentialPolicy, freeze_auth_file, freeze_credential_policy, redact_credential_output


EMPTY_CREDENTIAL_POLICY = CredentialPolicy(())


def ready_tool_sandbox() -> dict:
    return {
        "backend": "permission-profile-bwrap", "status": "ready",
        "workspaceRead": True, "workspaceWrite": True, "forbiddenReadDenied": True,
        "networkDenied": True, "proxyEnvironmentAbsent": True, "skillProjectionReady": True,
        "skillProjectionPresent": False, "authDescriptorHidden": True,
    }

def fake_batch(*, max_attempts: int | None = None) -> dict:
    cases = [
        {"id": "case-one", "scenarioClass": "scenario-one", "partition": "development"},
        {"id": "case-two", "scenarioClass": "scenario-two", "partition": "development"},
    ]
    schedule = schedule_targets(cases, 1, "fake-seed")
    batch = {
        "version": 1,
        "authorityBoundary": AUTHORITY_BOUNDARY,
        "batchId": "fake-batch",
        "batchDigest": "a" * 64,
        "batchSeed": "fake-seed",
        "partition": "development",
        "datasetPartitions": ["development"],
        "caseIds": [case["id"] for case in cases],
        "portfolioCaseCount": 30,
        "caseCount": len(cases),
        "arms": list(ARMS),
        "repetitions": 1,
        "targetRunCount": len(schedule),
        "maxAttempts": max_attempts if max_attempts is not None else len(schedule),
        "profileId": "fake-profile",
        "workers": 2,
        "wallClockBudgetSeconds": 100,
        "perAttemptTimeoutSeconds": 10,
        "infrastructureFailureLimit": 2,
        "modelPolicy": {"requestedModel": "fake-model"},
        "networkPolicy": {"mode": "direct", "keys": [], "schemes": [], "fingerprint": "c" * 64},
        "distributionSnapshot": {"version": "test", "treeHash": "b" * 64, "skillCount": 2},
        "hostVersions": {"codex": "fake-codex", "bwrap": "fake-bwrap"},
        "schedule": schedule,
    }
    return batch


def valid_result(target: dict, *, reverse: bool = False) -> dict:
    passed = target["arm"] == ("baseline-no-aegis" if reverse else "aegis-auto")
    return {
        "status": "valid",
        "contractPass": passed,
        "elapsedSeconds": 1.0,
        "tokens": {"input_tokens": 10, "output_tokens": 2},
        "observedModels": ["fake-model"],
        "costUsd": None,
    }


class RunnerContractTest(unittest.TestCase):
    def ledger(self, batch: dict, result_for_target):
        ledger = initial_ledger(batch)
        for attempt_number, target in enumerate(batch["schedule"], start=1):
            attempt = {
                "attemptNumber": attempt_number,
                "waveNumber": (attempt_number - 1) // batch["workers"] + 1,
                "targetId": target["targetId"],
                "caseId": target["caseId"],
                "scenarioClass": target["scenarioClass"],
                "partition": target["partition"],
                "repetition": target["repetition"],
                "arm": target["arm"],
            }
            attempt.update(result_for_target(target))
            ledger["attempts"].append(attempt)
        return ledger

    def run_unscrubbed_attempt(
        self,
        output_root: Path,
        *,
        returncode: int = 0,
        parsed: dict | None = None,
        scorer_error: BaseException | None = None,
        output_exceeded: bool = False,
    ) -> tuple[dict, mock.Mock]:
        root = Path(__file__).resolve().parents[2]
        workspace = output_root / "workspace"
        workspace.mkdir()
        (output_root / "prompt.txt").write_text("prompt", encoding="utf-8")
        frozen_case = {"caseId": "case", "frozenSeedProjectPath": "seed", "frozenPromptPath": "prompt.txt", "frozenOutcomeContractPath": "contract.json"}
        batch = {"frozenCases": [frozen_case], "modelPolicy": {"requestedModel": "model"}}
        target = {"targetId": "target", "caseId": "case", "arm": "baseline-no-aegis"}
        fake_process = mock.Mock(returncode=returncode)
        layout = {"workspace": workspace, "home": output_root / "home", "tmp": output_root / "tmp"}
        (layout["home"] / ".codex").mkdir(parents=True)
        (layout["home"] / ".codex/auth.json").touch(mode=0o600)
        layout["tmp"].mkdir()
        with mock.patch.object(benchmark_runner, "prepare_arm_layout", return_value=layout), mock.patch.object(
            benchmark_runner, "snapshot_workspace", return_value={}
        ), mock.patch.object(
            benchmark_runner, "build_codex_live_command", return_value=["fake-codex"]
        ), mock.patch.object(benchmark_runner, "validate_codex_live_command"), mock.patch.object(
            benchmark_runner, "direct_codex_environment", return_value={}
        ), mock.patch.object(benchmark_runner, "validate_direct_codex_environment"), mock.patch.object(
            benchmark_runner, "popen_with_independent_auth_link", return_value=fake_process
        ) as popen, mock.patch.object(
            benchmark_runner,
            "communicate_with_timeout",
            return_value=("{}", "", False, output_exceeded, False),
        ), mock.patch.object(benchmark_runner, "parse_codex_jsonl", return_value=parsed), mock.patch.object(
            benchmark_runner, "score_outcome", side_effect=scorer_error
        ):
            result = benchmark_runner._execute_target_unscrubbed(
                root=root, output_root=output_root, batch=batch, target=target, attempt_number=1,
                auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                timeout_seconds=1.0, proxy_policy=resolve_proxy_policy({}),
                credential_policy=EMPTY_CREDENTIAL_POLICY, process_group_supervised=True,
            )
        return result, popen

    def test_full_success(self):
        batch = fake_batch()
        ledger = self.ledger(batch, valid_result)
        report = aggregate(batch, ledger)
        self.assertEqual(report["completeness"], "complete")
        self.assertEqual(report["profileId"], "fake-profile")
        self.assertEqual(report["attempts"]["valid"], 4)
        self.assertEqual(report["overall"]["deltaPercentagePoints"], 100.0)
        self.assertEqual(report["overall"]["arms"]["aegis-auto"]["unsafeOutcomeRate"], 0.0)

    def test_aggregate_rejects_forged_terminal_identity(self):
        batch = fake_batch()
        ledger = self.ledger(batch, valid_result)
        ledger["attempts"][0]["targetId"] = batch["schedule"][1]["targetId"]
        ledger["attempts"][0]["caseId"] = "forged-case"
        with self.assertRaises(SystemExit):
            aggregate(batch, ledger)

    def test_aggregate_rejects_terminal_attempts_after_circuit_stop(self):
        batch = fake_batch(max_attempts=6)
        ledger = self.ledger(
            batch,
            lambda target: valid_result(target)
            if target["caseId"] == "case-one"
            else {"status": "invalid", "invalidReason": "infrastructure", "errorType": "executor-exception"},
        )
        for attempt_number, target in enumerate(batch["schedule"][2:4], start=5):
            ledger["attempts"].append(
                {
                    "attemptNumber": attempt_number,
                    "waveNumber": 3,
                    "targetId": target["targetId"],
                    "caseId": target["caseId"],
                    "scenarioClass": target["scenarioClass"],
                    "partition": target["partition"],
                    "repetition": target["repetition"],
                    "arm": target["arm"],
                    **valid_result(target),
                }
            )
        with self.assertRaises(SystemExit):
            aggregate(batch, ledger)

    def test_schedule_promotes_a_deterministic_paired_canary(self):
        first = schedule_targets(
            [
                {"id": "case-one", "scenarioClass": "scenario-one", "partition": "development"},
                {"id": "case-two", "scenarioClass": "scenario-two", "partition": "development"},
            ],
            2,
            "pair-seed",
        )
        second = schedule_targets(
            [
                {"id": "case-one", "scenarioClass": "scenario-one", "partition": "development"},
                {"id": "case-two", "scenarioClass": "scenario-two", "partition": "development"},
            ],
            2,
            "pair-seed",
        )
        self.assertEqual(first, second)
        self.assertEqual(first[0]["caseId"], first[1]["caseId"])
        self.assertEqual(first[0]["repetition"], first[1]["repetition"])
        self.assertEqual([target["arm"] for target in first[:2]], list(ARMS))
        self.assertEqual(len({target["targetId"] for target in first}), 8)

    def test_execution_opt_ins_are_profile_specific_and_full_is_retired(self):
        require_execution_opt_in("development-pilot", {"AEGIS_AGENTIC_BENCHMARK_LIVE": "1"})
        with self.assertRaises(SystemExit):
            require_execution_opt_in(
                "standard-held-out",
                {"AEGIS_AGENTIC_BENCHMARK_LIVE": "1", "AEGIS_AGENTIC_BENCHMARK_FULL": "1"},
            )
        require_execution_opt_in(
            "standard-held-out",
            {"AEGIS_AGENTIC_BENCHMARK_LIVE": "1", "AEGIS_AGENTIC_BENCHMARK_HELD_OUT": "1"},
        )
        with self.assertRaises(SystemExit):
            require_execution_opt_in(
                "extended-held-out",
                {"AEGIS_AGENTIC_BENCHMARK_LIVE": "1", "AEGIS_AGENTIC_BENCHMARK_HELD_OUT": "1"},
            )
        require_execution_opt_in(
            "extended-held-out",
            {
                "AEGIS_AGENTIC_BENCHMARK_LIVE": "1",
                "AEGIS_AGENTIC_BENCHMARK_HELD_OUT": "1",
                "AEGIS_AGENTIC_BENCHMARK_EXTENDED": "1",
            },
        )

    def test_arm_contamination_is_refused(self):
        batch = fake_batch()
        arm = {
            "evaluatedSkillMatchCount": 0,
            "methodPackMarkerCount": 0,
            "nonSkillInputHash": "same",
            "authReadOnly": True,
            "benchmarkRepoVisible": False,
            "peerWorkspaceVisible": False,
            "scorerVisible": False,
            "visibleProcessCount": 2,
            "snapshotVisible": False,
            "toolSandbox": ready_tool_sandbox(),
        }
        report = {
            "modelCalls": 0,
            "authorityBoundary": AUTHORITY_BOUNDARY,
            "distributionSnapshot": {"treeHash": batch["distributionSnapshot"]["treeHash"]},
            "auditNetworkPolicy": {
                "promptInput": copy.deepcopy(batch["networkPolicy"]),
                "mountAudit": {"mode": "network-disabled"},
            },
            "arms": {
                "baseline-no-aegis": copy.deepcopy(arm),
                "aegis-auto": {
                    **copy.deepcopy(arm), "evaluatedSkillMatchCount": 2, "methodPackMarkerCount": 2,
                    "snapshotVisible": True,
                    "toolSandbox": {**ready_tool_sandbox(), "skillProjectionPresent": True},
                },
            },
        }
        validate_live_isolation_report(report, batch)
        report["arms"]["baseline-no-aegis"]["evaluatedSkillMatchCount"] = 1
        with self.assertRaises(SystemExit):
            validate_live_isolation_report(report, batch)

    def test_isolation_report_keeps_prompt_and_mount_network_policies_distinct(self):
        batch = fake_batch()
        report = {
            "modelCalls": 0,
            "authorityBoundary": AUTHORITY_BOUNDARY,
            "distributionSnapshot": {"treeHash": batch["distributionSnapshot"]["treeHash"]},
            "auditNetworkPolicy": {
                "promptInput": copy.deepcopy(batch["networkPolicy"]),
                "mountAudit": {"mode": "network-disabled"},
            },
            "arms": {
                arm: {
                    "evaluatedSkillMatchCount": 0 if arm == "baseline-no-aegis" else 2,
                    "methodPackMarkerCount": 0 if arm == "baseline-no-aegis" else 2,
                    "nonSkillInputHash": "same",
                    "authReadOnly": True,
                    "benchmarkRepoVisible": False,
                    "peerWorkspaceVisible": False,
                    "scorerVisible": False,
                    "visibleProcessCount": 2,
                    "snapshotVisible": arm == "aegis-auto",
                    "toolSandbox": {**ready_tool_sandbox(), "skillProjectionPresent": arm == "aegis-auto"},
                }
                for arm in ARMS
            },
        }
        validate_live_isolation_report(report, batch)
        for field, value in (
            ("promptInput", {"mode": "network-disabled"}),
            ("mountAudit", copy.deepcopy(batch["networkPolicy"])),
        ):
            with self.subTest(field=field):
                drifted = copy.deepcopy(report)
                drifted["auditNetworkPolicy"][field] = value
                with self.assertRaises(SystemExit):
                    validate_live_isolation_report(drifted, batch)

    def test_partial_batch_flag(self):
        batch = fake_batch(max_attempts=4)
        ledger = self.ledger(
            batch,
            lambda target: valid_result(target)
            if target["caseId"] == "case-one"
            else {"status": "invalid", "invalidReason": "infrastructure", "errorType": "executor-exception"},
        )
        report = aggregate(batch, ledger)
        flags = {flag["id"] for flag in report["review"]["flags"]}
        self.assertIn("partial-batch", flags)
        self.assertEqual(report["review"]["status"], "unknown")

    def test_negative_delta_is_preserved(self):
        batch = fake_batch()
        ledger = self.ledger(batch, lambda target: valid_result(target, reverse=True))
        report = aggregate(batch, ledger)
        self.assertEqual(report["overall"]["deltaPercentagePoints"], -100.0)

    def test_scorer_unknown_requires_review(self):
        batch = fake_batch(max_attempts=4)
        ledger = self.ledger(
            batch,
            lambda target: valid_result(target) if target["caseId"] == "case-one" else {"status": "invalid", "invalidReason": "scorer-unknown"},
        )
        report = aggregate(batch, ledger)
        flags = {flag["id"] for flag in report["review"]["flags"]}
        self.assertIn("scorer-unknown", flags)
        self.assertEqual(report["review"]["status"], "unknown")

    def test_credential_output_is_redacted_and_invalidatable(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(prefix="agentic-credential-test-", dir=root / ".tmp") as value:
            auth = Path(value) / "auth.json"
            secret = "private-refresh-token-value"
            auth.write_text(json.dumps({"tokens": {"refresh_token": secret}}), encoding="utf-8")
            auth.chmod(0o600)
            redacted, exposed = redact_credential_output(f"debug: {secret}", freeze_credential_policy(auth))
        self.assertTrue(exposed)
        self.assertNotIn(secret, redacted)
        self.assertIn("[REDACTED_CREDENTIAL]", redacted)

    def test_credential_policy_is_frozen_in_memory_without_secret_representation(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(prefix="agentic-credential-freeze-test-", dir=root / ".tmp") as value:
            auth = Path(value) / "auth.json"
            original = "private-original-token-value"
            replacement = "private-replacement-token-value"
            auth.write_text(json.dumps({"tokens": {"refresh_token": original}}), encoding="utf-8")
            auth.chmod(0o600)
            policy = freeze_credential_policy(auth)
            auth.write_text(json.dumps({"tokens": {"refresh_token": replacement}}), encoding="utf-8")
            redacted, exposed = redact_credential_output(original, policy)
        self.assertTrue(exposed)
        self.assertEqual(redacted, "[REDACTED_CREDENTIAL]")
        self.assertNotIn(original, repr(policy))
        self.assertNotIn(replacement, repr(policy))
        with self.assertRaises(TypeError):
            json.dumps(policy)

    def test_auth_schema_protects_short_secrets_without_treating_metadata_as_credentials(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(prefix="agentic-auth-schema-test-", dir=root / ".tmp") as value:
            auth = Path(value) / "auth.json"
            auth.write_text(
                json.dumps(
                    {
                        "auth_mode": "chatgpt-account-login",
                        "last_refresh": "2026-07-27T00:00:00Z",
                        "tokens": {"account_id": "account-metadata-value", "access_token": "abc"},
                    }
                ),
                encoding="utf-8",
            )
            auth.chmod(0o600)
            policy = freeze_credential_policy(auth)
        redacted, exposed = redact_credential_output("token=abc", policy)
        self.assertTrue(exposed)
        self.assertNotIn("abc", redacted)
        metadata, metadata_exposed = redact_credential_output("account-metadata-value chatgpt-account-login", policy)
        self.assertFalse(metadata_exposed)
        self.assertEqual(metadata, "account-metadata-value chatgpt-account-login")

    def test_every_unknown_auth_path_fails_before_a_frozen_mount_exists(self):
        root = Path(__file__).resolve().parents[2]
        cases = (
            ({"session": "private-value"}, "Codex auth contains an unknown root field"),
            ({"bearer": "private-value"}, "Codex auth contains an unknown root field"),
            ({"profile_name": "ordinary-metadata"}, "Codex auth contains an unknown root field"),
            ({"tokens": {"session": "private-value"}}, "Codex auth contains an unknown tokens field"),
        )
        for payload, message in cases:
            with self.subTest(field=next(iter(payload))), tempfile.TemporaryDirectory(
                prefix="agentic-auth-unknown-key-test-", dir=root / ".tmp"
            ) as value:
                auth = Path(value) / "auth.json"
                auth.write_text(json.dumps(payload), encoding="utf-8")
                auth.chmod(0o600)
                with self.assertRaises(SystemExit) as caught:
                    freeze_auth_file(auth)
            self.assertEqual(str(caught.exception), message)
            self.assertNotIn("private-value", str(caught.exception))

    def test_unpaired_surrogate_auth_fails_safely_without_creating_an_artifact(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(prefix="agentic-auth-surrogate-test-", dir=root / ".tmp") as value:
            directory = Path(value)
            auth = directory / "auth.json"
            auth.write_bytes(b'{"OPENAI_API_KEY":"\\ud800"}')
            auth.chmod(0o600)
            before = set(Path("/proc/self/fd").iterdir())
            with self.assertRaises(SystemExit) as caught:
                freeze_auth_file(auth)
            after = set(Path("/proc/self/fd").iterdir())
            self.assertEqual(before, after)
            self.assertEqual(list(directory.iterdir()), [auth])
        self.assertEqual(str(caught.exception), "credential markers contain invalid Unicode")

    def test_frozen_auth_memfd_crosses_a_worker_boundary_and_detects_source_rotation(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(prefix="agentic-auth-memfd-test-", dir=root / ".tmp") as value:
            auth = Path(value) / "auth.json"
            original = b'{"OPENAI_API_KEY":"abc"}'
            auth.write_bytes(original)
            auth.chmod(0o600)
            frozen = freeze_auth_file(auth)
            mount_path = frozen.mount_path
            try:
                completed = subprocess.run(
                    [sys.executable, "-c", "import pathlib,sys; raise SystemExit(pathlib.Path(sys.argv[1]).read_bytes()!=sys.stdin.buffer.read())", str(mount_path)],
                    input=original,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    pass_fds=(frozen.descriptor,),
                    check=False,
                )
                self.assertEqual(completed.returncode, 0)
                auth.write_bytes(b'{"OPENAI_API_KEY":"rotated"}')
                self.assertEqual(mount_path.read_bytes(), original)
                with self.assertRaises(SystemExit):
                    frozen.assert_source_unchanged()
            finally:
                frozen.close()
            self.assertFalse(mount_path.exists())

    def test_auth_cli_path_rejects_a_symlink_before_resolve(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(prefix="agentic-auth-link-test-", dir=root / ".tmp") as value:
            directory = Path(value)
            auth = directory / "auth.json"
            auth.write_text("{}\n", encoding="utf-8")
            link = directory / "auth-link.json"
            link.symlink_to(auth)
            with self.assertRaises(SystemExit) as caught:
                resolve_auth_file(link)
        self.assertEqual(str(caught.exception), "Codex auth file must not be a symlink")

    def test_attempt_artifacts_are_scrubbed_before_any_result_returns(self):
        root = Path(__file__).resolve().parents[2]
        proxy = "http://proxy.invalid:8080"
        policy = resolve_proxy_policy({"HTTP_PROXY": proxy})
        target = {"targetId": "fake-target"}
        with tempfile.TemporaryDirectory(prefix="agentic-artifact-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-fake-target"

            def fake_inner(**_kwargs):
                for relative in ("isolated/home/.codex/cache", "isolated/cache.bin", "workspace/result.txt", "codex-stderr.log"):
                    path = attempt_root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(f"before {proxy} after".encode())
                return {"status": "valid", "contractPass": True, "elapsedSeconds": 2.5}

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner):
                result = execute_target(
                    root=root,
                    output_root=output_root,
                    batch={},
                    target=target,
                    attempt_number=1,
                    auth_file=output_root / "auth",
                    bwrap=output_root / "bwrap",
                    codex=output_root / "codex",
                    timeout_seconds=1,
                    proxy_policy=policy,
                    credential_policy=EMPTY_CREDENTIAL_POLICY,
                )
            self.assertEqual(result, {"status": "invalid", "invalidReason": "proxy-exposure", "elapsedSeconds": 2.5})
            self.assertFalse((attempt_root / "isolated/home").exists())
            for path in attempt_root.rglob("*"):
                if path.is_file():
                    self.assertNotIn(proxy.encode(), path.read_bytes())

            def exposed_error(**_kwargs):
                exposed_path = attempt_root / "workspace/error.txt"
                exposed_path.parent.mkdir(parents=True, exist_ok=True)
                exposed_path.write_text(proxy, encoding="utf-8")
                raise RuntimeError("original error")

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=exposed_error):
                result = execute_target(
                    root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                    auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                    timeout_seconds=1, proxy_policy=policy, credential_policy=EMPTY_CREDENTIAL_POLICY,
                )
            self.assertEqual(result, {"status": "invalid", "invalidReason": "proxy-exposure", "elapsedSeconds": 0.0})

    def test_credential_exposure_deletes_attempt_for_every_retained_artifact_surface(self):
        root = Path(__file__).resolve().parents[2]
        proxy_policy = resolve_proxy_policy({})
        secret = "private-refresh-token-value"
        credential_policy = CredentialPolicy((secret,))
        target = {"targetId": "credential-target"}
        for surface in ("workspace", "filename", "symlink", "event-log", "outcome", "exception"):
            with self.subTest(surface=surface), tempfile.TemporaryDirectory(
                prefix="agentic-credential-artifact-test-", dir=root / ".tmp"
            ) as value:
                output_root = Path(value)
                attempt_root = output_root / "attempts/001-credential-target"

                def fake_inner(**_kwargs):
                    workspace = attempt_root / "workspace"
                    workspace.mkdir(parents=True)
                    if surface == "workspace":
                        (workspace / "result.bin").write_bytes(b"prefix\xff" + secret.encode())
                    elif surface == "filename":
                        (workspace / f"result-{secret}").write_text("safe", encoding="utf-8")
                    elif surface == "symlink":
                        os.symlink(b"prefix-" + secret.encode() + b"-\xff", os.fsencode(workspace / "result-link"))
                    elif surface == "event-log":
                        (attempt_root / "codex-events.jsonl").write_text(secret, encoding="utf-8")
                    elif surface == "outcome":
                        (attempt_root / "outcome.json").write_text(secret, encoding="utf-8")
                    else:
                        raise RuntimeError(f"private child detail {secret}")
                    return {"status": "valid", "contractPass": True, "elapsedSeconds": 1.5}

                with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner):
                    result = execute_target(
                        root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                        auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                        timeout_seconds=1, proxy_policy=proxy_policy, credential_policy=credential_policy,
                    )
                self.assertEqual(result["invalidReason"], "credential-exposure")
                self.assertNotIn(secret, json.dumps(result, sort_keys=True))
                self.assertFalse(attempt_root.exists())

    def test_generic_credential_shapes_and_non_utf8_artifacts_are_deleted(self):
        root = Path(__file__).resolve().parents[2]
        proxy_policy = resolve_proxy_policy({})
        target = {"targetId": "generic-target"}
        payloads = (
            b"\xffsk-abcdefghijklmnopQRSTUV",
            b"\xffeyJabcdefgh.ijklmnop.qrstuvwx",
            b"\xffapi_key=generic-secret-value",
        )
        for payload in payloads:
            with self.subTest(payload=payload[:8]), tempfile.TemporaryDirectory(
                prefix="agentic-generic-credential-test-", dir=root / ".tmp"
            ) as value:
                output_root = Path(value)
                attempt_root = output_root / "attempts/001-generic-target"

                def fake_inner(**_kwargs):
                    artifact = attempt_root / "workspace/result.bin"
                    artifact.parent.mkdir(parents=True)
                    artifact.write_bytes(payload)
                    return {"status": "valid", "contractPass": True, "elapsedSeconds": 0.5}

                with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner):
                    result = execute_target(
                        root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                        auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                        timeout_seconds=1, proxy_policy=proxy_policy, credential_policy=EMPTY_CREDENTIAL_POLICY,
                    )
                self.assertEqual(result["invalidReason"], "credential-exposure")
                self.assertFalse(attempt_root.exists())

    def test_safe_retained_artifacts_are_not_removed(self):
        root = Path(__file__).resolve().parents[2]
        target = {"targetId": "safe-target"}
        with tempfile.TemporaryDirectory(prefix="agentic-safe-artifact-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-safe-target"
            expected = {"status": "valid", "contractPass": True, "elapsedSeconds": 0.25}

            def fake_inner(**_kwargs):
                artifact = attempt_root / "workspace/result.bin"
                artifact.parent.mkdir(parents=True)
                artifact.write_bytes(b"safe\xffartifact")
                return expected

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner):
                result = execute_target(
                    root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                    auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                    timeout_seconds=1, proxy_policy=resolve_proxy_policy({}), credential_policy=EMPTY_CREDENTIAL_POLICY,
                )
            self.assertIs(result, expected)
            self.assertEqual((attempt_root / "workspace/result.bin").read_bytes(), b"safe\xffartifact")

    def test_retained_artifact_xattrs_are_scanned_and_removed(self):
        root = Path(__file__).resolve().parents[2]
        target = {"targetId": "xattr-target"}
        secret = "short"
        for carrier in ("root-name", "directory-value", "file-value"):
            with self.subTest(carrier=carrier), tempfile.TemporaryDirectory(
                prefix="agentic-xattr-secret-test-", dir=root / ".tmp"
            ) as value:
                output_root = Path(value)
                attempt_root = output_root / "attempts/001-xattr-target"

                def fake_inner(**_kwargs):
                    directory = attempt_root / "workspace"
                    artifact = directory / "result.txt"
                    directory.mkdir(parents=True)
                    artifact.write_text("safe", encoding="utf-8")
                    if carrier == "root-name":
                        os.setxattr(attempt_root, f"user.{secret}", b"safe")
                    elif carrier == "directory-value":
                        os.setxattr(directory, "user.note", secret.encode())
                    else:
                        os.setxattr(artifact, "user.note", b"prefix-" + secret.encode())
                    return {"status": "valid", "contractPass": True, "elapsedSeconds": 0.1}

                with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner):
                    result = execute_target(
                        root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                        auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                        timeout_seconds=1, proxy_policy=resolve_proxy_policy({}),
                        credential_policy=CredentialPolicy((secret,)),
                    )
                self.assertEqual(result["invalidReason"], "credential-exposure")
                self.assertFalse(attempt_root.exists())

        with tempfile.TemporaryDirectory(prefix="agentic-xattr-safe-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-xattr-target"

            def safe_inner(**_kwargs):
                directory = attempt_root / "workspace"
                artifact = directory / "result.txt"
                directory.mkdir(parents=True)
                artifact.write_text("safe", encoding="utf-8")
                for path in (attempt_root, directory, artifact):
                    os.setxattr(path, "user.benchmark-note", b"safe-metadata")
                return {"status": "valid", "contractPass": True, "elapsedSeconds": 0.1}

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=safe_inner):
                result = execute_target(
                    root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                    auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                    timeout_seconds=1, proxy_policy=resolve_proxy_policy({}),
                    credential_policy=EMPTY_CREDENTIAL_POLICY,
                )
            self.assertEqual(result["status"], "valid")
            self.assertTrue(all(not os.listxattr(path, follow_symlinks=False) for path in (
                attempt_root, attempt_root / "workspace", attempt_root / "workspace/result.txt"
            )))

    def test_proxy_xattr_is_removed_and_symlink_xattrs_are_never_followed(self):
        root = Path(__file__).resolve().parents[2]
        proxy = "http://proxy.invalid:8080"
        target = {"targetId": "xattr-link-target"}
        with tempfile.TemporaryDirectory(prefix="agentic-xattr-link-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-xattr-link-target"
            outside = output_root / "outside.txt"
            outside.write_text("safe", encoding="utf-8")
            os.setxattr(outside, "user.external", b"external-metadata")
            link = attempt_root / "workspace/link"

            def fake_inner(**_kwargs):
                artifact = attempt_root / "workspace/result.txt"
                artifact.parent.mkdir(parents=True)
                artifact.write_text("safe", encoding="utf-8")
                os.setxattr(artifact, "user.proxy", proxy.encode())
                link.symlink_to(outside)
                return {"status": "valid", "contractPass": True, "elapsedSeconds": 0.1}

            real_listxattr = os.listxattr
            symlink_checks: list[bool] = []

            def tracking_listxattr(path, *, follow_symlinks=True):
                if os.fsdecode(path) == str(link):
                    symlink_checks.append(follow_symlinks)
                return real_listxattr(path, follow_symlinks=follow_symlinks)

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner), mock.patch.object(
                agentic_benchmark_provider_preflight.os, "listxattr", side_effect=tracking_listxattr
            ):
                result = execute_target(
                    root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                    auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                    timeout_seconds=1, proxy_policy=resolve_proxy_policy({"HTTP_PROXY": proxy}),
                    credential_policy=EMPTY_CREDENTIAL_POLICY,
                )
            self.assertEqual(result["invalidReason"], "proxy-exposure")
            self.assertEqual(symlink_checks, [False])
            self.assertEqual(os.getxattr(outside, "user.external"), b"external-metadata")
            self.assertFalse(os.listxattr(attempt_root / "workspace/result.txt"))

    def test_xattr_read_failure_deletes_attempt_and_exposes_no_error_detail(self):
        root = Path(__file__).resolve().parents[2]
        target = {"targetId": "xattr-failure-target"}
        with tempfile.TemporaryDirectory(prefix="agentic-xattr-failure-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-xattr-failure-target"

            def fake_inner(**_kwargs):
                artifact = attempt_root / "workspace/result.txt"
                artifact.parent.mkdir(parents=True)
                artifact.write_text("safe", encoding="utf-8")
                return {"status": "valid", "contractPass": True, "elapsedSeconds": 0.1}

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner), mock.patch.object(
                agentic_benchmark_provider_preflight.os,
                "listxattr",
                side_effect=OSError("private xattr detail"),
            ):
                with self.assertRaises(SystemExit) as caught:
                    execute_target(
                        root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                        auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                        timeout_seconds=1, proxy_policy=resolve_proxy_policy({}),
                        credential_policy=EMPTY_CREDENTIAL_POLICY,
                    )
            self.assertEqual(str(caught.exception), "benchmark attempt artifact cleanup failed")
            self.assertNotIn("private xattr detail", str(caught.exception))
            self.assertFalse(attempt_root.exists())

    def test_hardlinks_fifos_and_sockets_fail_closed_and_delete_attempt_root(self):
        root = Path(__file__).resolve().parents[2]
        target = {"targetId": "special-entry-target"}
        for kind in ("hardlink", "fifo", "socket"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory(
                prefix="agentic-special-entry-test-", dir=root / ".tmp"
            ) as value:
                output_root = Path(value)
                attempt_root = output_root / "attempts/001-special-entry-target"
                outside = output_root / "outside.txt"
                outside.write_text("outside-safe", encoding="utf-8")

                def fake_inner(**_kwargs):
                    carrier = attempt_root / "workspace/carrier"
                    carrier.parent.mkdir(parents=True)
                    if kind == "hardlink":
                        os.link(outside, carrier)
                    elif kind == "fifo":
                        os.mkfifo(carrier)
                    else:
                        endpoint = socket.socket(socket.AF_UNIX)
                        previous = Path.cwd()
                        try:
                            os.chdir(carrier.parent)
                            endpoint.bind(carrier.name)
                        finally:
                            os.chdir(previous)
                            endpoint.close()
                    return {"status": "valid", "contractPass": True, "elapsedSeconds": 0.1}

                with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner):
                    with self.assertRaises(SystemExit) as caught:
                        execute_target(
                            root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                            auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                            timeout_seconds=1, proxy_policy=resolve_proxy_policy({}),
                            credential_policy=EMPTY_CREDENTIAL_POLICY,
                        )
                self.assertEqual(str(caught.exception), "benchmark attempt artifact cleanup failed")
                self.assertFalse(attempt_root.exists())
                self.assertEqual(outside.read_text(encoding="utf-8"), "outside-safe")

    def test_safe_artifact_remover_unlinks_a_root_symlink_without_following_it(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(prefix="agentic-remove-link-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            outside = output_root / "outside"
            secret = outside / "secret.txt"
            outside.mkdir()
            secret.write_text("external-secret", encoding="utf-8")
            link = output_root / "attempts"
            link.symlink_to(outside, target_is_directory=True)
            benchmark_runner.remove_tmp_artifact_entry(link, root)
            self.assertFalse(link.is_symlink())
            self.assertEqual(secret.read_text(encoding="utf-8"), "external-secret")

    def test_safe_artifact_remover_rejects_mountinfo_and_cross_device_trees_before_deletion(self):
        root = Path(__file__).resolve().parents[2]
        for boundary in ("root-mount", "descendant-mount", "cross-device"):
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory(
                prefix=f"agentic-remove-{boundary}-", dir=root / ".tmp"
            ) as value:
                output_root = Path(value)
                attempt_root = output_root / "attempts"
                mounted = attempt_root / "mounted space"
                artifact = mounted / "result.txt"
                artifact.parent.mkdir(parents=True)
                artifact.write_text("must-remain", encoding="utf-8")
                outside = output_root / "outside.txt"
                outside.write_text("external-remains", encoding="utf-8")
                link = attempt_root / "outside-link"
                link.symlink_to(outside)
                mount_target = attempt_root if boundary == "root-mount" else mounted
                encoded_mount = os.fsencode(mount_target).replace(b" ", b"\\040")
                fake_mountinfo = b"1 0 0:1 / / rw - ext4 root rw\n2 1 0:1 / " + encoded_mount + b" rw - ext4 bind rw\n"
                real_read_bytes = Path.read_bytes
                real_lstat = Path.lstat

                def read_bytes(path: Path) -> bytes:
                    return fake_mountinfo if path == Path("/proc/self/mountinfo") else real_read_bytes(path)

                def lstat(path: Path):
                    metadata = real_lstat(path)
                    if boundary == "cross-device" and path == attempt_root:
                        metadata = mock.Mock(st_mode=metadata.st_mode, st_dev=metadata.st_dev + 1)
                    return metadata

                mountinfo = read_bytes if boundary != "cross-device" else real_read_bytes
                with mock.patch.object(Path, "read_bytes", new=mountinfo), mock.patch.object(Path, "lstat", new=lstat):
                    with self.assertRaises(SystemExit):
                        benchmark_runner.remove_tmp_artifact_entry(attempt_root, root)
                self.assertEqual(artifact.read_text(encoding="utf-8"), "must-remain")
                self.assertTrue(link.is_symlink())
                self.assertEqual(outside.read_text(encoding="utf-8"), "external-remains")

    def test_credential_cleanup_failure_retries_deletion_and_fails_without_secret(self):
        root = Path(__file__).resolve().parents[2]
        secret = "private-refresh-token-value"
        target = {"targetId": "cleanup-target"}
        with tempfile.TemporaryDirectory(prefix="agentic-credential-cleanup-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-cleanup-target"

            def fake_inner(**_kwargs):
                artifact = attempt_root / "workspace/result.txt"
                artifact.parent.mkdir(parents=True)
                artifact.write_text(secret, encoding="utf-8")
                return {"status": "valid", "contractPass": True, "elapsedSeconds": 0.1}

            real_remove = benchmark_runner.remove_tmp_artifact_entry
            attempt_removals = 0

            def fail_attempt_once(path: Path, repo: Path):
                nonlocal attempt_removals
                if path == attempt_root:
                    attempt_removals += 1
                    if attempt_removals == 1:
                        raise OSError(f"private cleanup detail {secret}")
                return real_remove(path, repo)

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner), mock.patch.object(
                benchmark_runner, "remove_tmp_artifact_entry", side_effect=fail_attempt_once
            ):
                with self.assertRaises(SystemExit) as caught:
                    execute_target(
                        root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                        auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                        timeout_seconds=1, proxy_policy=resolve_proxy_policy({}),
                        credential_policy=CredentialPolicy((secret,)),
                    )
            self.assertEqual(str(caught.exception), "benchmark attempt artifact cleanup failed")
            self.assertNotIn(secret, str(caught.exception))
            self.assertEqual(attempt_removals, 2)
            self.assertFalse(attempt_root.exists())

    def test_confidentiality_scan_preserves_entry_and_file_size_caps(self):
        root = Path(__file__).resolve().parents[2]
        target = {"targetId": "limit-target"}
        for limit_name in ("MAX_ARTIFACT_ENTRIES", "MAX_ARTIFACT_FILE_BYTES"):
            with self.subTest(limit=limit_name), tempfile.TemporaryDirectory(
                prefix="agentic-artifact-limit-test-", dir=root / ".tmp"
            ) as value:
                output_root = Path(value)
                attempt_root = output_root / "attempts/001-limit-target"

                def fake_inner(**_kwargs):
                    artifact = attempt_root / "workspace/result.bin"
                    artifact.parent.mkdir(parents=True)
                    artifact.write_bytes(b"safe-artifact")
                    return {"status": "valid", "contractPass": True, "elapsedSeconds": 0.1}

                with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner), mock.patch.object(
                    agentic_benchmark_provider_preflight, limit_name, 0
                ):
                    with self.assertRaises(SystemExit) as caught:
                        execute_target(
                            root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                            auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                            timeout_seconds=1, proxy_policy=resolve_proxy_policy({}),
                            credential_policy=EMPTY_CREDENTIAL_POLICY,
                        )
                self.assertEqual(str(caught.exception), "benchmark attempt artifact cleanup failed")
                self.assertFalse(attempt_root.exists())

    def test_attempt_cleanup_preserves_normal_result_and_reraises_original_errors(self):
        root = Path(__file__).resolve().parents[2]
        policy = resolve_proxy_policy({"HTTP_PROXY": "http://proxy.invalid:8080"})
        target = {"targetId": "fake-target"}
        with tempfile.TemporaryDirectory(prefix="agentic-artifact-flow-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-fake-target"
            expected = {"status": "invalid", "invalidReason": "infrastructure",
                        "errorType": "executor-exception", "elapsedSeconds": 1.0}

            def normal(**_kwargs):
                (attempt_root / "isolated/home").mkdir(parents=True)
                (attempt_root / "workspace").mkdir()
                (attempt_root / "workspace/result.txt").write_text("safe", encoding="utf-8")
                return expected

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=normal):
                result = execute_target(
                    root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                    auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                    timeout_seconds=1, proxy_policy=policy, credential_policy=EMPTY_CREDENTIAL_POLICY,
                )
            self.assertIs(result, expected)
            self.assertFalse((attempt_root / "isolated/home").exists())

        for label, error in (("parse", ValueError("parse detail")), ("scorer", RuntimeError("scorer detail")), ("popen", OSError("popen detail"))):
            with self.subTest(label=label), tempfile.TemporaryDirectory(prefix="agentic-artifact-error-test-", dir=root / ".tmp") as value:
                output_root = Path(value)
                attempt_root = output_root / "attempts/001-fake-target"

                def failing(**_kwargs):
                    (attempt_root / "isolated/home").mkdir(parents=True)
                    (attempt_root / "workspace").mkdir()
                    (attempt_root / "workspace/result.txt").write_text("safe", encoding="utf-8")
                    raise error

                with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=failing):
                    with self.assertRaises(type(error)) as caught:
                        execute_target(
                            root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                            auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                            timeout_seconds=1, proxy_policy=policy, credential_policy=EMPTY_CREDENTIAL_POLICY,
                        )
                self.assertIs(caught.exception, error)
                self.assertFalse((attempt_root / "isolated/home").exists())

    def test_attempt_proxy_symlink_is_materialized_and_invalidates_result(self):
        root = Path(__file__).resolve().parents[2]
        proxy = "http://proxy.invalid:8080"
        policy = resolve_proxy_policy({"HTTP_PROXY": proxy})
        target = {"targetId": "symlink-target"}
        with tempfile.TemporaryDirectory(prefix="agentic-artifact-link-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-symlink-target"
            proxy_link = attempt_root / "workspace/proxy-link"
            safe_link = attempt_root / "workspace/safe-link"

            def fake_inner(**_kwargs):
                proxy_link.parent.mkdir(parents=True)
                os.symlink(proxy.encode() + b"\xff-tail", os.fsencode(proxy_link))
                safe_link.symlink_to("unrelated-target")
                return {"status": "valid", "contractPass": True, "elapsedSeconds": 1.25}

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner):
                result = execute_target(
                    root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                    auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                    timeout_seconds=1, proxy_policy=policy, credential_policy=EMPTY_CREDENTIAL_POLICY,
                )
            self.assertEqual(result, {"status": "invalid", "invalidReason": "proxy-exposure", "elapsedSeconds": 1.25})
            self.assertFalse(proxy_link.is_symlink())
            self.assertEqual(proxy_link.read_bytes(), b"[REDACTED_PROXY]\xff-tail")
            self.assertTrue(safe_link.is_symlink())
            self.assertEqual(os.readlink(os.fsencode(safe_link)), b"unrelated-target")

    def test_scrub_failure_deletes_attempt_root_and_fails_closed(self):
        root = Path(__file__).resolve().parents[2]
        policy = resolve_proxy_policy({"HTTP_PROXY": "http://proxy.invalid:8080"})
        target = {"targetId": "fake-target"}
        with tempfile.TemporaryDirectory(prefix="agentic-artifact-failure-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-fake-target"

            def fake_inner(**_kwargs):
                (attempt_root / "isolated/home").mkdir(parents=True)
                (attempt_root / "workspace").mkdir()
                return {"status": "valid", "contractPass": True}

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner), mock.patch.object(
                agentic_benchmark_provider_preflight, "scrub_confidential_artifact_tree", side_effect=OSError("private proxy detail")
            ):
                with self.assertRaises(SystemExit) as caught:
                    execute_target(
                        root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                        auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                        timeout_seconds=1, proxy_policy=policy, credential_policy=EMPTY_CREDENTIAL_POLICY,
                    )
            self.assertEqual(str(caught.exception), "benchmark attempt artifact cleanup failed")
            self.assertFalse(attempt_root.exists())

        with tempfile.TemporaryDirectory(prefix="agentic-home-cleanup-failure-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-fake-target"

            def fake_inner(**_kwargs):
                (attempt_root / "isolated/home").mkdir(parents=True)
                return {"status": "valid", "contractPass": True}

            real_remove = benchmark_runner.remove_tmp_artifact_entry
            calls = 0

            def fail_home_once(path: Path, repo: Path):
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise OSError("private home cleanup detail")
                return real_remove(path, repo)

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner), mock.patch.object(
                benchmark_runner, "remove_tmp_artifact_entry", side_effect=fail_home_once
            ):
                with self.assertRaises(SystemExit) as caught:
                    execute_target(
                        root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                        auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                        timeout_seconds=1, proxy_policy=policy, credential_policy=EMPTY_CREDENTIAL_POLICY,
                    )
            self.assertEqual(str(caught.exception), "benchmark attempt artifact cleanup failed")
            self.assertFalse(attempt_root.exists())

    def test_stale_attempts_are_scrubbed_before_scheduler_recovery(self):
        root = Path(__file__).resolve().parents[2]
        proxy = "http://proxy.invalid:8080"
        policy = resolve_proxy_policy({"HTTP_PROXY": proxy})
        with tempfile.TemporaryDirectory(prefix="agentic-stale-artifact-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-stale"
            home_cache = attempt_root / "isolated/home/.codex/cache"
            workspace = attempt_root / "workspace/result.txt"
            proxy_link = attempt_root / "workspace/proxy-link"
            safe_link = attempt_root / "workspace/safe-link"
            home_cache.parent.mkdir(parents=True)
            workspace.parent.mkdir(parents=True)
            home_cache.write_text(proxy, encoding="utf-8")
            workspace.write_text(proxy, encoding="utf-8")
            os.symlink(b"prefix-" + proxy.encode() + b"-\xff", os.fsencode(proxy_link))
            safe_link.symlink_to("unrelated-target")
            agentic_benchmark_provider_preflight.scrub_stale_confidential_artifacts(
                output_root / "attempts",
                {"001-stale"},
                policy,
                EMPTY_CREDENTIAL_POLICY,
                lambda path: benchmark_runner.remove_tmp_artifact_entry(path, root),
            )
            self.assertFalse((attempt_root / "isolated/home").exists())
            self.assertEqual(workspace.read_text(encoding="utf-8"), "[REDACTED_PROXY]")
            self.assertFalse(proxy_link.is_symlink())
            self.assertEqual(proxy_link.read_bytes(), b"prefix-[REDACTED_PROXY]-\xff")
            self.assertTrue(safe_link.is_symlink())
            self.assertEqual(os.readlink(os.fsencode(safe_link)), b"unrelated-target")

    def test_stale_credential_attempt_is_deleted_and_cannot_resume_as_valid(self):
        root = Path(__file__).resolve().parents[2]
        secret = "private-refresh-token-value"
        with tempfile.TemporaryDirectory(prefix="agentic-stale-credential-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            leaking_roots = [output_root / f"attempts/{number:03d}-stale" for number in (1, 2)]
            for attempt_root in leaking_roots:
                artifact = attempt_root / "workspace/result.txt"
                artifact.parent.mkdir(parents=True)
                artifact.write_text(secret, encoding="utf-8")
            safe_root = output_root / "attempts/003-safe"
            safe_artifact = safe_root / "workspace/result.txt"
            safe_artifact.parent.mkdir(parents=True)
            safe_artifact.write_text("safe", encoding="utf-8")
            with self.assertRaises(SystemExit) as caught:
                agentic_benchmark_provider_preflight.scrub_stale_confidential_artifacts(
                    output_root / "attempts",
                    {root.name for root in [*leaking_roots, safe_root]},
                    resolve_proxy_policy({}),
                    CredentialPolicy((secret,)),
                    lambda path: benchmark_runner.remove_tmp_artifact_entry(path, root),
                )
            self.assertEqual(str(caught.exception), "stale benchmark attempt artifacts were unsafe")
            self.assertNotIn(secret, str(caught.exception))
            self.assertTrue(all(not attempt_root.exists() for attempt_root in leaking_roots))
            self.assertEqual(safe_artifact.read_text(encoding="utf-8"), "safe")

    def test_interrupted_recovered_and_orphan_attempt_trees_are_deleted_without_current_markers(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(prefix="agentic-stale-ledger-state-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            completed = output_root / "attempts/001-completed"
            uncertain = [
                output_root / "attempts/002-launched",
                output_root / "attempts/003-recovered",
                output_root / "attempts/999-orphan",
            ]
            for attempt_root in [completed, *uncertain]:
                artifact = attempt_root / "workspace/result.txt"
                artifact.parent.mkdir(parents=True)
                artifact.write_text("old-secret-not-in-current-auth", encoding="utf-8")
            orphan_link = output_root / "attempts/orphan-link"
            outside = output_root / "outside"
            outside.mkdir()
            orphan_link.symlink_to(outside, target_is_directory=True)
            agentic_benchmark_provider_preflight.scrub_stale_confidential_artifacts(
                output_root / "attempts",
                {"001-completed"},
                resolve_proxy_policy({}),
                EMPTY_CREDENTIAL_POLICY,
                lambda path: benchmark_runner.remove_tmp_artifact_entry(path, root),
            )
            self.assertTrue(completed.is_dir())
            self.assertTrue(all(not attempt_root.exists() for attempt_root in uncertain))
            self.assertFalse(orphan_link.exists())
            self.assertTrue(outside.is_dir())

    def test_production_child_timeout_escalates_to_bounded_sigkill(self):
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); print('ready', flush=True); time.sleep(60)",
            ],
            text=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            self.assertEqual(process.stdout.readline().strip(), "ready")  # type: ignore[union-attr]
            started = time.monotonic()
            _stdout, _stderr, timed_out, output_exceeded, artifact_limit_observed = communicate_with_timeout(
                process,
                0.05,
                cleanup_timeout_seconds=0.1,
            )
            elapsed = time.monotonic() - started
            self.assertTrue(timed_out)
            self.assertFalse(output_exceeded)
            self.assertFalse(artifact_limit_observed)
            self.assertEqual(process.returncode, -signal.SIGKILL)
            self.assertLess(elapsed, 1.0)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=1)

    def test_outer_supervised_attempt_child_does_not_create_a_nested_session(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(prefix="agentic-attempt-group-", dir=root / ".tmp") as value:
            output_root = Path(value)
            result, popen = self.run_unscrubbed_attempt(output_root, output_exceeded=True)
            self.assertFalse(popen.call_args.kwargs["start_new_session"])
            self.assertEqual(result["invalidReason"], "infrastructure")
            self.assertEqual(result["errorType"], "attempt-output-limit")
            stderr = (output_root / "attempts/001-target/codex-stderr.log").read_text(encoding="utf-8")
            self.assertNotIn("timed out", stderr)

    def test_attempt_pipeline_maps_host_events_and_scorer_failures_to_stable_error_types(self):
        root = Path(__file__).resolve().parents[2]
        parsed_valid = {
            "malformedLineCount": 0, "recordCount": 1, "finalResponse": "safe response",
            "events": [], "toolExecutionCount": 1,
        }
        cases = (
            ("host-exit", 9, parsed_valid, None, "attempt-host-exit"),
            ("events-invalid", 0, {**parsed_valid, "recordCount": 0}, None, "attempt-host-events-invalid"),
            ("tool-sandbox", 0, {**parsed_valid, "toolSandboxFailureCount": 1}, None, "attempt-tool-sandbox-unavailable"),
            ("tool-unobserved", 0, {**parsed_valid, "toolExecutionCount": 0}, None, "attempt-tool-execution-unobserved"),
            ("scorer-failure", 0, parsed_valid, SystemExit("private scorer detail"), "attempt-scorer-failure"),
        )
        for label, returncode, parsed, scorer_error, expected in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory(
                prefix=f"agentic-attempt-diagnostic-{label}-", dir=root / ".tmp"
            ) as value:
                result, _popen = self.run_unscrubbed_attempt(
                    Path(value), returncode=returncode, parsed=parsed, scorer_error=scorer_error
                )
                self.assertEqual(result["invalidReason"], "infrastructure")
                self.assertEqual(result["errorType"], expected)
                self.assertNotIn("private scorer detail", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
