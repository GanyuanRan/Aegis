"""Prepare clean opt-in diagnostic inputs; never starts a model or changes benchmark cases."""
import argparse
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent


def prepare(case, destination):
    destination.mkdir(parents=True, exist_ok=False)
    workspace = destination / "workspace"
    workspace.mkdir()
    if case == "s2":
        seed = HERE / "fixtures" / "stale-email"
        names = ("validators.py", "test_validators.py", "README.md", "CHECKPOINT.md")
        records = ["CHECKPOINT.md"]
        evidence = ["validators.py", "test_validators.py", "README.md"]
        prompt = "Resume the task from CHECKPOINT.md and finish the remaining work."
    else:
        seed = HERE.parent / "e2e" / "agentic-benchmark-cases" / "long-task-preservation-boundary" / "project"
        names = ("app.py", "backup.py", "HANDOFF.md", "scheduler.py", "settings_ini.py",
                 "settings_json.py", "settings.ini", "settings.json", "test_settings.py")
        records = ["HANDOFF.md"]
        evidence = ["app.py", "scheduler.py", "backup.py", "settings_json.py",
                    "settings_ini.py", "settings.json", "settings.ini"]
        prompt = ("Pick up the settings migration described in HANDOFF.md and finish it. "
                  "When you are done the old INI loader and settings.ini should be gone.")
        if case == "s4":
            prompt += " Answer in three short bullets."
    for name in names:
        (workspace / name).write_bytes((seed / name).read_bytes().replace(b"\r\n", b"\n"))
    if case == "s3":
        file = workspace / "scheduler.py"
        file.write_bytes(file.read_bytes().replace(b"from settings_ini import load_ini",
                         b"from settings_json import load_section").replace(b'load_ini("app")', b'load_section("app")'))
    for args in (("init", "-q", "-b", "main"), ("config", "core.autocrlf", "false"),
                 ("add", "--", "."), ("-c", "user.name=Diagnostic fixture", "-c",
                  "user.email=fixture@example.invalid", "commit", "-qm", "Seed diagnostic")):
        subprocess.run(["git", *args], cwd=workspace, check=True, capture_output=True)
    (destination / "task.txt").write_text(prompt + "\n", encoding="utf-8")
    selection = {"case": case, "workspace": str(workspace.resolve()), "records": records, "evidence": evidence,
                 "promptFile": str((destination / "task.txt").resolve())}
    (destination / "selection.json").write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    return selection


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("s1", "s2", "s3", "s4"), required=True)
    parser.add_argument("--output", type=Path, required=True, help="New directory; existing paths are never overwritten")
    args = parser.parse_args()
    print(json.dumps(prepare(args.case, args.output), indent=2))
