import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
# Import the helper package from this checkout; write no bytecode under scripts/.
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from aegis_workspace_helper.checks import command_check
from aegis_workspace_helper.errors import WorkspaceError
from aegis_workspace_helper.evidence import command_add_attempt, command_add_evidence, command_bundle
from aegis_workspace_helper.inputs import read_json_dict
from aegis_workspace_helper.layout import initialize_workspace
from aegis_workspace_helper.work import (
    command_add_checkpoint,
    command_add_drift_check,
    command_new_work,
)


def args(**values):
    return type("Args", (), values)()


def new_work_record(root: Path) -> Path:
    initialize_workspace(root)
    result = command_new_work(
        args(
            root=str(root),
            date="2026-09-01",
            slug="evidence-convergence",
            title="Evidence Convergence",
            task_id=None,
            requested_outcome="Verify retry evidence convergence.",
            goal=None,
            success_evidence=[],
            stop_condition=None,
            scope="temporary target project",
            change_kind=["test"],
            risk_hint=[],
            baseline_ref=[],
            why_relevant="",
            missing_authority=[],
            affected_layer=[],
            owner=[],
            invariant=[],
            compat_boundary="",
            non_goal=[],
            current_todo=None,
            active_slice=None,
            blocked_on=None,
            next_step=None,
        )
    )
    assert result == 0
    return root / "docs" / "aegis" / "work" / "2026-09-01-evidence-convergence"


class EvidenceConvergenceTests(unittest.TestCase):
    def test_failed_attempts_share_one_draft_and_stay_out_of_bundle(self):
        with tempfile.TemporaryDirectory(prefix="aegis-evidence-") as tmp:
            root = Path(tmp)
            work = new_work_record(root)
            for attempt_id in ("attempt-1", "attempt-2", "attempt-3"):
                self.assertEqual(
                    command_add_attempt(
                        args(
                            root=str(root),
                            work=work.name,
                            slice_id="slice-1",
                            attempt_id=attempt_id,
                            attempt_status="failed",
                            summary=f"{attempt_id} failed",
                            type="test",
                            source="unit test",
                            verifier="test_workspace_evidence_convergence",
                            evidence_ref=[],
                            date="2026-09-01",
                        )
                    ),
                    0,
                )

            drafts = sorted(work.glob("evidence-bundle-draft-slice-1*.json"))
            self.assertEqual(len(drafts), 1)
            data = read_json_dict(drafts[0])
            self.assertEqual(data["evidenceStatus"], "attempted")
            self.assertEqual(len(data["attempts"]), 3)
            self.assertEqual(data["attemptSummary"]["total"], 3)
            self.assertNotIn("EvidenceBundleDraft: slice-1", (work / "90-evidence.md").read_text(encoding="utf-8"))

            self.assertEqual(command_bundle(args(root=str(root), work=work.name)), 0)
            pack = read_json_dict(work / "gate-input-pack.json")
            self.assertNotIn(
                "docs/aegis/work/2026-09-01-evidence-convergence/evidence-bundle-draft-slice-1.json",
                pack["evidenceBundle"],
            )

    def test_evidence_update_keeps_backslashes_in_summary(self):
        # Updating an existing evidence section used the summary as an re
        # replacement template, so a Windows path such as C:\logs raised
        # "bad escape" after the JSON sidecar had already been written.
        with tempfile.TemporaryDirectory(prefix="aegis-backslash-") as tmp:
            root = Path(tmp)
            work = new_work_record(root)
            summary = "Logs saved under C:\\logs\\run.txt"
            terminal = args(
                root=str(root),
                work=work.name,
                artifact_key="slice-1",
                slice_id="slice-1",
                evidence_status="evidence-finalized",
                type="test",
                source="unit test",
                summary=summary,
                verifier="test_workspace_evidence_convergence",
                date="2026-09-01",
            )
            self.assertEqual(command_add_evidence(terminal), 0)
            self.assertEqual(command_add_evidence(terminal), 0)
            evidence_markdown = (work / "90-evidence.md").read_text(encoding="utf-8")
            self.assertEqual(evidence_markdown.count(summary), 1)

    def test_bundle_lists_status_less_sidecar_as_legacy(self):
        # A sidecar without evidenceStatus is valid legacy evidence; it used to
        # be classified invalid, leaving the proof bundle's legacy list empty.
        with tempfile.TemporaryDirectory(prefix="aegis-legacy-") as tmp:
            root = Path(tmp)
            work = new_work_record(root)
            (work / "evidence-bundle-draft-legacy.json").write_text(
                '{"summary": "recorded before evidenceStatus existed"}\n', encoding="utf-8"
            )
            (work / "evidence-bundle-draft-unknown.json").write_text(
                '{"evidenceStatus": "unknown-status"}\n', encoding="utf-8"
            )
            self.assertEqual(command_bundle(args(root=str(root), work=work.name)), 0)
            proof = (work / "proof-bundle.md").read_text(encoding="utf-8")
            legacy_section = proof.split("## Legacy Unclassified Evidence\n\n", 1)[1].split("\n## ", 1)[0]
            self.assertIn("evidence-bundle-draft-legacy.json", legacy_section)
            self.assertNotIn("evidence-bundle-draft-unknown.json", legacy_section)
            pack = read_json_dict(work / "gate-input-pack.json")
            self.assertEqual(pack["evidenceBundle"], [])

    def test_terminal_evidence_is_idempotent_and_closes_slice(self):
        with tempfile.TemporaryDirectory(prefix="aegis-terminal-") as tmp:
            root = Path(tmp)
            work = new_work_record(root)
            for attempt_id in ("attempt-1", "attempt-2"):
                command_add_attempt(
                    args(
                        root=str(root),
                        work=work.name,
                        slice_id="slice-1",
                        attempt_id=attempt_id,
                        attempt_status="failed",
                        summary=f"{attempt_id} failed",
                        type="test",
                        source="unit test",
                        verifier="test_workspace_evidence_convergence",
                        evidence_ref=[],
                        date="2026-09-01",
                    )
                )

            terminal = args(
                root=str(root),
                work=work.name,
                artifact_key="slice-1",
                slice_id="slice-1",
                evidence_status="evidence-finalized",
                type="test",
                source="unit test",
                summary="terminal evidence",
                verifier="test_workspace_evidence_convergence",
                date="2026-09-01",
            )
            self.assertEqual(command_add_evidence(terminal), 0)
            self.assertEqual(command_add_evidence(terminal), 0)

            drafts = sorted(work.glob("evidence-bundle-draft-slice-1*.json"))
            self.assertEqual(len(drafts), 1)
            evidence_markdown = (work / "90-evidence.md").read_text(encoding="utf-8")
            self.assertEqual(evidence_markdown.count("## EvidenceBundleDraft: slice-1"), 1)
            self.assertNotIn("No evidence has been recorded yet.", evidence_markdown)

            self.assertEqual(command_bundle(args(root=str(root), work=work.name)), 0)
            pack = read_json_dict(work / "gate-input-pack.json")
            self.assertIn(
                "docs/aegis/work/2026-09-01-evidence-convergence/evidence-bundle-draft-slice-1.json",
                pack["evidenceBundle"],
            )

            with self.assertRaises(WorkspaceError):
                command_add_attempt(
                    args(
                        root=str(root),
                        work=work.name,
                        slice_id="slice-1",
                        attempt_id="attempt-3",
                        attempt_status="failed",
                        summary="closed slice attempt",
                        type="test",
                        source="unit test",
                        verifier="test_workspace_evidence_convergence",
                        evidence_ref=[],
                        date="2026-09-01",
                    )
                )

    def test_check_reports_attempt_pressure_without_becoming_a_gate(self):
        with tempfile.TemporaryDirectory(prefix="aegis-pressure-") as tmp:
            root = Path(tmp)
            work = new_work_record(root)
            for attempt_id in ("attempt-1", "attempt-2", "attempt-3"):
                command_add_attempt(
                    args(
                        root=str(root),
                        work=work.name,
                        slice_id="slice-1",
                        attempt_id=attempt_id,
                        attempt_status="failed",
                        summary=f"{attempt_id} failed",
                        type="test",
                        source="unit test",
                        verifier="test_workspace_evidence_convergence",
                        evidence_ref=[],
                        date="2026-09-01",
                    )
                )

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(
                    command_check(
                        args(root=str(root), process_pressure=True)
                    ),
                    0,
                )
            output = stdout.getvalue()
            self.assertIn("max_attempts_per_slice: 3", output)
            self.assertIn("convergence-stop", output)

    def test_checkpoint_rewrite_preserves_drift_section(self):
        with tempfile.TemporaryDirectory(prefix="aegis-checkpoint-drift-") as tmp:
            root = Path(tmp)
            work = new_work_record(root)
            command_add_drift_check(
                args(
                    root=str(root),
                    work=work.name,
                    decision="needs-verification",
                    scope_status="aligned",
                    compat_status="unchanged",
                    retirement_status="none",
                    baseline_ref=[],
                    new_risk_signal=[],
                )
            )
            command_add_checkpoint(
                args(
                    root=str(root),
                    work=work.name,
                    date="2026-09-01",
                    current_todo="preserve drift",
                    completed_todo=["drift written"],
                    active_slice="slice-1",
                    evidence_ref=[],
                    blocked_on=None,
                    next_step="verify markdown",
                    resume_instruction="read checkpoint and drift",
                    unsafe_to_assume=[],
                )
            )
            text = (work / "20-checkpoint.md").read_text(encoding="utf-8")
            self.assertIn("## DriftCheckDraft", text)
            self.assertIn("Advisory decision: needs-verification", text)

    def test_bounded_checkpoint_rewrite_keeps_recent_history(self):
        with tempfile.TemporaryDirectory(prefix="aegis-checkpoint-") as tmp:
            root = Path(tmp)
            work = new_work_record(root)
            for index in range(8):
                command_add_checkpoint(
                    args(
                        root=str(root),
                        work=work.name,
                        date="2026-09-01",
                        current_todo=f"todo-{index}",
                        completed_todo=[f"done-{index}"],
                        active_slice="slice-1",
                        evidence_ref=[],
                        blocked_on=None,
                        next_step=f"step-{index}",
                        resume_instruction=f"resume-{index}",
                        unsafe_to_assume=[],
                    )
                )
            text = (work / "20-checkpoint.md").read_text(encoding="utf-8")
            self.assertEqual(text.count("## Checkpoint Update"), 5)
            self.assertIn("## Current Checkpoint", text)
            self.assertIn("todo-7", text)

    def test_bounded_checkpoint_history_keeps_newest_entries_first(self):
        with tempfile.TemporaryDirectory(prefix="aegis-checkpoint-") as tmp:
            root = Path(tmp)
            work = new_work_record(root)
            for index in range(8):
                command_add_checkpoint(
                    args(
                        root=str(root),
                        work=work.name,
                        date="2026-09-01",
                        current_todo=f"todo-{index}",
                        completed_todo=[f"done-{index}"],
                        active_slice="slice-1",
                        evidence_ref=[],
                        blocked_on=None,
                        next_step=f"step-{index}",
                        resume_instruction=f"resume-{index}",
                        unsafe_to_assume=[],
                    )
                )
            text = (work / "20-checkpoint.md").read_text(encoding="utf-8")
            history = text.split("## Recent Checkpoint History", 1)[1]
            # Current is todo-7; history keeps the five newest predecessors.
            for index in range(2, 7):
                self.assertIn(f"todo-{index}", history)
            for index in range(0, 2):
                self.assertNotIn(f"todo-{index}", history)
            self.assertLess(history.index("todo-6"), history.index("todo-2"))


if __name__ == "__main__":
    unittest.main()
