import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


workspace = load_module("aegis_workspace", "scripts/aegis-workspace.py")


def args(**values):
    return type("Args", (), values)()


def new_work_record(root: Path) -> Path:
    workspace.initialize_workspace(root)
    result = workspace.command_new_work(
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
                    workspace.command_add_attempt(
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
            data = workspace.read_json_dict(drafts[0])
            self.assertEqual(data["evidenceStatus"], "attempted")
            self.assertEqual(len(data["attempts"]), 3)
            self.assertEqual(data["attemptSummary"]["total"], 3)
            self.assertNotIn("EvidenceBundleDraft: slice-1", (work / "90-evidence.md").read_text(encoding="utf-8"))

            self.assertEqual(workspace.command_bundle(args(root=str(root), work=work.name)), 0)
            pack = workspace.read_json_dict(work / "gate-input-pack.json")
            self.assertNotIn(
                "docs/aegis/work/2026-09-01-evidence-convergence/evidence-bundle-draft-slice-1.json",
                pack["evidenceBundle"],
            )

    def test_terminal_evidence_is_idempotent_and_closes_slice(self):
        with tempfile.TemporaryDirectory(prefix="aegis-terminal-") as tmp:
            root = Path(tmp)
            work = new_work_record(root)
            for attempt_id in ("attempt-1", "attempt-2"):
                workspace.command_add_attempt(
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
            self.assertEqual(workspace.command_add_evidence(terminal), 0)
            self.assertEqual(workspace.command_add_evidence(terminal), 0)

            drafts = sorted(work.glob("evidence-bundle-draft-slice-1*.json"))
            self.assertEqual(len(drafts), 1)
            evidence_markdown = (work / "90-evidence.md").read_text(encoding="utf-8")
            self.assertEqual(evidence_markdown.count("## EvidenceBundleDraft: slice-1"), 1)
            self.assertNotIn("No evidence has been recorded yet.", evidence_markdown)

            self.assertEqual(workspace.command_bundle(args(root=str(root), work=work.name)), 0)
            pack = workspace.read_json_dict(work / "gate-input-pack.json")
            self.assertIn(
                "docs/aegis/work/2026-09-01-evidence-convergence/evidence-bundle-draft-slice-1.json",
                pack["evidenceBundle"],
            )

            with self.assertRaises(workspace.WorkspaceError):
                workspace.command_add_attempt(
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
                workspace.command_add_attempt(
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
                    workspace.command_check(
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
            workspace.command_add_drift_check(
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
            workspace.command_add_checkpoint(
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
                workspace.command_add_checkpoint(
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


if __name__ == "__main__":
    unittest.main()
