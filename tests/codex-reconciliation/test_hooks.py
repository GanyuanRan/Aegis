"""Deterministic callback and installer contracts; live models are separate."""
import runpy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "extensions" / "codex-reconciliation"
sys.path.insert(0, str(SOURCE))
import hook
import profile
import review
from transport import RunError, validate_events

OLD = "Worker uses JSON. Done and verified."
CODE = "from legacy import load\n"
CORRECTED = "The earlier JSON completion claim was false at resume; worker still used legacy. Now corrected."
ANSWER = "The old checkpoint said worker used JSON; that was false at resume because it still imported legacy."


def assessment(status="contradicted"):
    return {"coverage": "complete", "unknowns": [], "claims": [{
        "id": "C1", "record": "CHECKPOINT.md", "quote": OLD, "status": status,
        "evidence": [{"source": "worker.py", "quote": CODE}], "reason": "Observed source."}]}


def result(ok=False):
    return {"unknowns": [], "assessmentDisputes": [], "unsupportedCorrection": False, "unsupportedCorrectionQuote": "",
            "checks": [{"id": "C1", "recordState": "corrected" if ok else "unresolved",
                        "recordQuotes": [CORRECTED if ok else OLD],
                        "disclosure": "specific" if ok else "missing",
                        "finalQuote": ANSWER if ok else "", "reason": "Observed record and reply."}]}


class Assessor:
    def __init__(self):
        self.initial = assessment()
        self.final = result()
        self.calls = []
        self.failure = None

    def run(self, prompt, *, label, reviewer, schema):
        assert reviewer and schema
        self.calls.append((label, prompt))
        if self.failure:
            raise self.failure
        return json.dumps(self.initial if label == "assessment" else self.final)


class HookTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.work = self.base / "project with spaces"
        self.work.mkdir()
        self.record = self.work / "CHECKPOINT.md"
        self.record.write_text(OLD, encoding="utf-8")
        (self.work / "worker.py").write_text(CODE, encoding="utf-8")
        self.home = self.base / "codex-home"
        self.installation = self.install()
        self.config = Path(self.installation["config"])
        self.assessor = Assessor()
        self.identity = ["session-one", "turn-one"]

    def install(self, **extra):
        args = dict(workspace=self.work, records=["CHECKPOINT.md"], evidence=["worker.py"],
                    codex_home=self.home, model="selected-model", effort="xhigh", timeout=300,
                    codex=sys.executable)
        return profile.install(**(args | extra))

    def event(self, name, **extra):
        return dict(hook_event_name=name, cwd=str(self.work), session_id=self.identity[0],
                    turn_id=self.identity[1], prompt="Finish the task",
                    last_assistant_message="Done.") | extra

    def call(self, name, **extra):
        return hook.handle(self.event(name, **extra), self.config,
                           reviewer_factory=lambda *_: self.assessor)

    def state(self):
        return profile.read_json(self.config.parent / "runs" / hook.digest(self.identity) / "state.json")

    def test_repair_reentry_preserves_original_and_specific_disclosure(self):
        self.assertIn("hookSpecificOutput", self.call("UserPromptSubmit"))
        blocked = self.call("Stop")
        self.assertEqual(blocked["decision"], "block")
        self.record.write_text(CORRECTED, encoding="utf-8")
        self.assertEqual(self.call("UserPromptSubmit", prompt=blocked["reason"]), {})
        self.assessor.final = result(True)
        self.assertEqual(self.call("Stop", last_assistant_message=ANSWER), {})
        self.assertEqual(self.state()["before"]["records"]["CHECKPOINT.md"]["text"], OLD)
        self.assertEqual(self.state()["status"], "reconciled")
        self.assertEqual(len(self.assessor.calls), 3)
        self.call("Stop", last_assistant_message=ANSWER)
        self.assertEqual(len(self.assessor.calls), 3)

    def test_exhausted_budget_warns_without_vetoing_other_hooks(self):
        self.call("UserPromptSubmit")
        for _ in range(2):
            self.assertEqual(self.call("Stop")["decision"], "block")
        for _ in range(3):
            warning = self.call("Stop")
            self.assertEqual(set(warning), {"systemMessage"})
            self.assertIn("needs-verification", warning["systemMessage"])
        self.assertEqual((self.state()["repairs"], self.state()["reviews"]), (2, 3))
        self.assertEqual(len(self.assessor.calls), 4)

    def test_accurate_record_control_and_false_accusation(self):
        self.assessor.initial = assessment("supported")
        self.assessor.final["checks"][0].update(recordState="consistent", disclosure="not-needed")
        self.call("UserPromptSubmit")
        self.assertEqual(self.call("Stop"), {})
        self.assessor.final.update(unsupportedCorrection=True, unsupportedCorrectionQuote="False checkpoint")
        response = self.call("Stop", last_assistant_message="False checkpoint")
        self.assertEqual(response["decision"], "block")

    def test_unknown_preflight_blocks_without_starting_repairs(self):
        self.assessor.initial = assessment("unknown")
        self.assertEqual(self.call("UserPromptSubmit")["decision"], "block")
        self.assertIn("needs-verification", self.call("Stop")["systemMessage"])
        self.assertEqual(len(self.assessor.calls), 1)

    def test_unclear_final_record_can_be_clarified_but_never_passes_as_unknown(self):
        self.call("UserPromptSubmit")
        self.assessor.final["unknowns"] = ["Unclear whether the active old statement was superseded"]
        for _ in range(2):
            self.assertEqual(self.call("Stop")["decision"], "block")
        self.assertIn("needs-verification", self.call("Stop")["systemMessage"])
        self.assertEqual(self.state()["status"], "needs-verification")
        self.assertEqual(self.state()["repairs"], 2)

    def test_unknown_alone_prevents_pass_until_a_fresh_review_resolves_it(self):
        self.call("UserPromptSubmit")
        before, frozen = self.state()["before"], self.state()["assessment"]
        self.record.write_text(CORRECTED, encoding="utf-8")
        self.assessor.final = result(True)
        self.assessor.final["unknowns"] = ["Disclosure interpretation remains unclear"]
        self.assertEqual(self.call("Stop", last_assistant_message=ANSWER)["decision"], "block")
        self.assessor.final["unknowns"] = []
        self.assertEqual(self.call("Stop", last_assistant_message=ANSWER), {})
        self.assertEqual(self.state()["status"], "reconciled")
        self.assertEqual(self.state()["before"], before)
        self.assertEqual(self.state()["assessment"], frozen)

    def test_dispute_after_correction_request_stops_without_forcing_assent(self):
        self.call("UserPromptSubmit")
        first = self.call("Stop")
        self.assertEqual(first["decision"], "block")
        dissent = "I dispute the initial classification; the captured source does not support it."
        self.assessor.final["assessmentDisputes"] = [{
            "claimId": "C1", "surface": "answer", "quote": dissent, "reason": "Worker contests premise."}]
        for _ in range(3):
            self.assertEqual(set(self.call("Stop", last_assistant_message=dissent)), {"systemMessage"})
        state = self.state()
        self.assertEqual(state["status"], "needs-verification")
        self.assertEqual((state["repairs"], state["reviews"]), (1, 2))
        self.assertEqual(len(self.assessor.calls), 3)
        self.assertEqual(self.record.read_text(), OLD)
        self.assertEqual(state["before"]["records"]["CHECKPOINT.md"]["text"], OLD)
        self.assertEqual(state["lastReview"]["assessmentDisputes"][0]["quote"], dissent)

    def test_record_dispute_overrides_otherwise_positive_checks(self):
        self.call("UserPromptSubmit")
        dissent = "I dispute that the inherited statement was inaccurate."
        self.record.write_text(CORRECTED + "\n" + dissent, encoding="utf-8")
        self.assessor.final = result(True)
        self.assessor.final["assessmentDisputes"] = [{
            "claimId": "C1", "surface": "record", "quote": dissent, "reason": "Record contests premise."}]
        self.assertIn("disputed", self.call("Stop", last_assistant_message=ANSWER)["systemMessage"])
        self.assertEqual(self.state()["repairs"], 0)
        self.assertEqual(self.state()["status"], "needs-verification")

    def test_dispute_witness_and_identity_are_checked(self):
        self.call("UserPromptSubmit")
        after = review.capture(self.work, ["CHECKPOINT.md"], [])
        for changes in ({"claimId": "invented"}, {"quote": "absent"}, {"surface": "elsewhere"}, {"reason": ""}):
            with self.subTest(changes=changes):
                output = result()
                output["assessmentDisputes"] = [{"claimId": "C1", "surface": "record", "quote": OLD,
                                                 "reason": "Contested."} | changes]
                with self.assertRaises(RunError):
                    review.validate_review(output, assessment(), after, "Done.")

    def test_timeout_is_unverified_and_does_not_retry_assessor(self):
        self.call("UserPromptSubmit")
        self.assessor.failure = RunError("Assessor timed out")
        self.assertIn("timed out", self.call("Stop")["systemMessage"])
        self.call("Stop")
        self.assertEqual(len(self.assessor.calls), 2)

    def test_interrupted_preflight_never_allows_duplicate_prompt(self):
        self.call("UserPromptSubmit")
        path = self.config.parent / "runs" / hook.digest(self.identity) / "state.json"
        for status in ("capturing", "active"):
            with self.subTest(status=status):
                state = self.state()
                state.update(status=status, assessment=None)
                profile.write_json(path, state)
                self.assertEqual(self.call("UserPromptSubmit")["decision"], "block")
                self.assertEqual(self.state()["status"], "needs-verification")
        self.assertEqual(len(self.assessor.calls), 1)

    def test_missing_capture_and_wrong_cwd_do_not_call_models(self):
        self.assertIn("needs-verification", self.call("Stop")["systemMessage"])
        self.assertIsNone(self.state()["reviews"])
        self.assertIsNone(self.state()["repairs"])
        self.call("Stop")
        self.assertEqual(self.call("UserPromptSubmit", cwd=str(self.base)), {})
        self.assertFalse(self.assessor.calls)

    def test_new_turn_gets_fresh_capture_and_unknown_reentry_fails(self):
        self.call("UserPromptSubmit")
        self.assertEqual(self.call("UserPromptSubmit", prompt="different prompt")["decision"], "block")
        self.identity[1] = "turn-two"
        self.assertIn("hookSpecificOutput", self.call("UserPromptSubmit"))
        self.assertEqual(len(self.assessor.calls), 2)

    def test_copied_capture_cannot_cross_turn_identity(self):
        self.call("UserPromptSubmit")
        source = self.config.parent / "runs" / hook.digest(self.identity) / "state.json"
        self.identity[1] = "another-turn"
        target = self.config.parent / "runs" / hook.digest(self.identity)
        target.mkdir()
        (target / "state.json").write_bytes(source.read_bytes())
        self.assertIn("identity", self.call("Stop")["systemMessage"])
        self.assertEqual(len(self.assessor.calls), 1)

    def test_malformed_state_replaces_earlier_success_receipt(self):
        self.call("UserPromptSubmit")
        self.record.write_text(CORRECTED, encoding="utf-8")
        self.assessor.final = result(True)
        self.call("Stop", last_assistant_message=ANSWER)
        directory = self.config.parent / "runs" / hook.digest(self.identity)
        for value in ([], None, 1, "bad", {"repairs": []}):
            with self.subTest(value=value):
                profile.write_json(directory / "state.json", value)
                self.assertIn("needs-verification", self.call("Stop")["systemMessage"])
                terminal = profile.read_json(directory / "result.json")
                self.assertEqual(terminal["status"], "needs-verification")
                self.assertEqual(terminal["identity"], self.identity)

    def test_oversized_assessor_stream_rejected_before_parsing(self):
        path = self.base / "events.jsonl"
        path.write_bytes(b" " * 8_388_609)
        with self.assertRaisesRegex(RunError, "bounded limit"):
            validate_events(path, "any")
        path.write_text(json.dumps({"type": "thread.started", "padding": "x" * 262_144}), encoding="utf-8")
        with self.assertRaisesRegex(RunError, "bounded limit"):
            validate_events(path, "any")

    def test_simultaneous_callback_cannot_overwrite_locked_state(self):
        directory = self.config.parent / "runs" / hook.digest(self.identity)
        with hook.locked(directory):
            with self.assertRaisesRegex(RunError, "Another callback"):
                self.call("UserPromptSubmit")
        self.assertFalse(self.assessor.calls)

    def test_configuration_anchor_and_installed_code_are_versioned(self):
        data = profile.read_json(self.config)
        expected = profile.json_hash(data)
        data["evidence"] = []
        profile.write_json(self.config, data)
        with self.assertRaisesRegex(RunError, "configuration changed"):
            hook.handle(self.event("UserPromptSubmit"), self.config, expected=expected)
        other = self.install(effort="high")
        self.assertNotEqual(self.installation["profile"], other["profile"])
        self.assertTrue((Path(other["config"]).parent / "code" / "hook.py").is_file())

    def test_install_is_idempotent_preserves_base_and_refuses_foreign_profile(self):
        base_config = self.home / "config.toml"
        base_config.write_text('model = "existing"\n', encoding="utf-8")
        self.assertEqual(self.install(), self.installation)
        self.assertEqual(base_config.read_text(), 'model = "existing"\n')
        Path(self.installation["profileFile"]).write_text("foreign config", encoding="utf-8")
        with self.assertRaisesRegex(RunError, "Existing profile differs"):
            self.install()

    def test_failed_install_cleans_only_its_new_files(self):
        with self.assertRaises(RunError):
            self.install(timeout=-1)
        self.assertEqual(len(list((self.home / "aegis-reconciliation").iterdir())), 1)

    def test_installed_callback_recursion_guard_needs_no_model(self):
        command = [sys.executable, str(self.config.parent / "code" / "hook.py"),
                   "--config", str(self.config), "--expected-config", "ignored", "--event", "Stop"]
        completed = subprocess.run(command, input="invalid data", text=True, capture_output=True,
                                   env=dict(os.environ, AEGIS_RECONCILIATION_ASSESSOR="1"), check=True)
        self.assertEqual(json.loads(completed.stdout), {})

    def test_invalid_preflight_wire_input_blocks_before_models(self):
        command = [sys.executable, str(self.config.parent / "code" / "hook.py"),
                   "--config", str(self.config), "--expected-config", profile.json_hash(profile.read_json(self.config)),
                   "--event", "UserPromptSubmit"]
        for raw in ("not JSON", "x" * 262_145, json.dumps(self.event("Stop"))):
            with self.subTest(length=len(raw)):
                completed = subprocess.run(command, input=raw, text=True, capture_output=True, check=True)
                self.assertEqual(json.loads(completed.stdout)["decision"], "block")

    def test_invalid_quotes_claim_coverage_and_path_escape_are_rejected(self):
        packet = review.capture(self.work, ["CHECKPOINT.md"], ["worker.py"])
        bad = assessment()
        bad["claims"][0]["evidence"][0]["quote"] = "invented import"
        with self.assertRaises(RunError):
            review.validate_assessment(bad, packet)
        bad_review = result()
        bad_review["checks"] = []
        with self.assertRaises(RunError):
            review.validate_review(bad_review, assessment(), packet, "Done.")
        for path in ("../outside", str(self.record), "CHECKPOINT.md:1:1"):
            with self.subTest(path=path), self.assertRaises(RunError):
                review.capture(self.work, [path], [])
        with self.assertRaises(RunError):
            review.capture(self.work, ["CHECKPOINT.md"], ["missing.py"])

    def test_email_diagnostic_seed_excludes_prior_answers_logs_and_skills(self):
        from prepare_diagnostics import prepare
        directory = self.base / "diagnostic"
        selection = prepare("s2", directory)
        workspace = Path(selection["workspace"])
        self.assertEqual({path.name for path in workspace.iterdir()},
                         {".git", "validators.py", "test_validators.py", "README.md", "CHECKPOINT.md"})
        namespace = runpy.run_path(str(workspace / "validators.py"))
        self.assertFalse(namespace["is_valid_email"]("a+tag@example.com"))
        self.assertIn("plus-tagged", (workspace / "README.md").read_text())
        with self.assertRaises(FileExistsError):
            prepare("s2", directory)

    def test_symlink_source_and_binary_sources_rejected(self):
        (self.work / "binary").write_bytes(b"a\0b")
        with self.assertRaises(RunError):
            review.capture(self.work, ["CHECKPOINT.md"], ["binary"])
        try:
            (self.work / "link").symlink_to(self.record)
        except OSError:
            self.skipTest("Host cannot create symlinks")
        with self.assertRaises(RunError):
            review.capture(self.work, ["link"], [])

    def test_events_reject_tool_use_failure_and_previous_answer(self):
        path = self.base / "events.jsonl"
        base = [{"type": "turn.started"}, {"type": "item.completed", "item": {
            "type": "agent_message", "text": "correct"}}, {"type": "turn.completed"}]
        def write(events):
            path.write_text("\n".join(json.dumps(row) for row in events), encoding="utf-8")
        write(base)
        validate_events(path, "correct")
        for events in (base + [{"type": "turn.started"}, {"type": "turn.completed"}],
                       base + [{"type": "turn.failed"}],
                       [base[0], {"type": "item.completed", "item": {"type": "command_execution"}}, base[2]]):
            write(events)
            with self.assertRaises(RunError):
                validate_events(path, "correct")

    @unittest.skipIf(os.name == "nt", "POSIX process-group integration; Windows uses taskkill")
    def test_assessor_deadline_and_parent_cancellation_kill_descendants(self):
        fake = self.base / "fake-codex"
        fake.write_text('#!/usr/bin/env python3\nimport subprocess, sys, time\n'
                        'from pathlib import Path\n'
                        'Path("started").write_text("yes")\n'
                        'subprocess.Popen([sys.executable, "-c", '
                        '"import time; from pathlib import Path; "'
                        '+ "\\nwhile True: Path(\'heartbeat\').write_text(str(time.time())); time.sleep(0.05)"])\n'
                        'time.sleep(60)\n', encoding="utf-8")
        fake.chmod(0o700)
        for cancel in (False, True):
            with self.subTest(cancel=cancel):
                output = self.base / str(cancel)
                output.mkdir()
                code = ("import sys; from pathlib import Path; "
                        f"sys.path.insert(0, {str(SOURCE)!r}); "
                        "from transport import Reviewer; "
                        f"Reviewer({{'codex':{str(fake)!r}, 'model':'fake', 'effort':'low', 'timeout':2}}, "
                        f"Path({str(output)!r})).run('data', label='probe', schema={{'type':'object'}})")
                owner = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)
                self.addCleanup(lambda p=owner: p.kill() if p.poll() is None else None)
                heartbeat = output / "assessor" / "heartbeat"
                deadline = time.monotonic() + 5
                while not heartbeat.exists() and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertTrue(heartbeat.exists(), "Fake assessor did not start")
                if cancel:
                    owner.kill()  # Simulate hook parent disappearing without Python cleanup.
                owner.wait(timeout=6)
                time.sleep(0.75)
                before = heartbeat.read_bytes()
                time.sleep(0.4)
                self.assertEqual(heartbeat.read_bytes(), before, "Orphan assessor kept executing")


if __name__ == "__main__":
    unittest.main()
