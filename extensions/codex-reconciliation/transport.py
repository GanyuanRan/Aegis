"""Bounded, read-only Codex assessor transport for the optional profile."""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


class RunError(Exception):
    pass


def owner_alive(pid):
    if os.name != "nt":
        return os.getppid() == pid
    # Windows retains the original parent PID after parent exit.
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    handle = kernel.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE only
    if not handle:
        return False
    try:
        return kernel.WaitForSingleObject(handle, 0) == 0x00000102  # WAIT_TIMEOUT
    finally:
        kernel.CloseHandle(handle)


def terminate_tree(process):
    if os.name == "nt":
        if process.poll() is not None:
            return
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait(timeout=5)


def supervise(timeout, owner, command_path):
    """Keep the deadline alive if a host cancels/kills its hook parent."""
    def interrupted(_signum, _frame):
        raise InterruptedError("Assessor supervisor interrupted")
    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, interrupted)
    process = None
    deadline = time.monotonic() + timeout
    try:
        prompt = sys.stdin.buffer.read(262_145)
        if len(prompt) > 262_144 or not owner_alive(owner):
            return 125
        command = json.loads(Path(command_path).read_text(encoding="utf-8"))
        process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                   start_new_session=os.name != "nt",
                                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)
        first = True
        while owner_alive(owner) and time.monotonic() < deadline:
            try:
                process.communicate(prompt if first else None, timeout=0.25)
                return process.returncode
            except subprocess.TimeoutExpired:
                first = False
        print("Assessor deadline expired or hook owner exited", file=sys.stderr)
        return 124
    except InterruptedError:
        return 125
    finally:
        if process is not None:
            terminate_tree(process)


def validate_events(path, answer):
    if path.stat().st_size > 8_388_608:
        raise RunError("Assessor event stream exceeds the bounded limit")
    started = completed = False
    last = None
    with path.open(encoding="utf-8") as stream:
        for count, line in enumerate(stream):
            if count >= 10_000 or len(line.encode("utf-8")) > 262_144:
                raise RunError("Assessor event stream exceeds the bounded limit")
            try:
                event = json.loads(line)
            except (ValueError, UnicodeError) as exc:
                raise RunError("Invalid assessor event stream") from exc
            if not isinstance(event, dict):
                raise RunError("Invalid assessor event")
            kind = event.get("type")
            if kind in ("turn.failed", "error"):
                raise RunError("Assessor turn failed")
            if kind == "turn.started":
                if started and not completed:
                    raise RunError("Overlapping assessor turns")
                started, completed, last = True, False, None
            if kind == "turn.completed":
                if not started or completed:
                    raise RunError("Completion without an active assessor turn")
                completed = True
            if kind in ("item.started", "item.updated", "item.completed"):
                item = event.get("item")
                if not started or completed or not isinstance(item, dict):
                    raise RunError("Assessor item outside an active turn")
                if item.get("type") not in ("agent_message", "reasoning"):
                    raise RunError("Read-only assessor attempted a tool or reported an error")
                if kind == "item.completed" and item.get("type") == "agent_message":
                    last = item.get("text")
    if not completed or not answer.strip() or not isinstance(last, str) or last.strip() != answer.strip():
        raise RunError("Final file does not match the completed assessor turn")


class Reviewer:
    def __init__(self, config, output):
        self.config, self.output = config, Path(output)
        self.cwd = self.output / "assessor"
        self.cwd.mkdir(exist_ok=True)

    def run(self, prompt, *, label, reviewer=True, schema=None):
        if reviewer is not True or schema is None:
            raise RunError("Only structured read-only assessment is supported")
        final = self.output / f"{label}.txt"
        events = self.output / f"{label}.events.jsonl"
        schema_path = self.output / f"{label}.schema.json"
        schema_path.write_text(json.dumps(schema), encoding="utf-8")
        command = [self.config["codex"], "exec", "--json", "--ephemeral",
                   "--strict-config", "--ignore-user-config", "--ignore-rules",
                   "--skip-git-repo-check", "-s", "read-only", "-C", str(self.cwd),
                   "-m", self.config["model"], "-c", 'approval_policy="never"',
                   "-c", f'model_reasoning_effort="{self.config["effort"]}"',
                   "-c", 'web_search="disabled"', "--output-schema", str(schema_path),
                   "-o", str(final)]
        for feature in ("shell_tool", "unified_exec", "apps", "plugins", "multi_agent",
                        "browser_use", "computer_use", "image_generation"):
            command += ["--disable", feature]
        command.append("-")
        command_path = self.output / f"{label}.command.json"
        command_path.write_text(json.dumps(command), encoding="utf-8")
        supervisor = [sys.executable, str(Path(__file__).resolve()), "--supervise",
                      str(self.config["timeout"]), str(os.getpid()), str(command_path)]
        environment = dict(os.environ, AEGIS_RECONCILIATION_ASSESSOR="1")
        with events.open("wb") as stdout, (self.output / f"{label}.stderr.txt").open("wb") as stderr:
            process = subprocess.Popen(supervisor, cwd=self.cwd, env=environment,
                                       stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                       start_new_session=os.name != "nt",
                                       creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)
            try:
                process.communicate(prompt.encode("utf-8"), timeout=self.config["timeout"] + 5)
            except subprocess.TimeoutExpired as exc:
                process.terminate()  # Supervisor finally block cleans its assessor group.
                try:
                    process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    terminate_tree(process)
                raise RunError("Assessor timed out; inspect private logs") from exc
        if process.returncode != 0 or not final.is_file() or final.stat().st_size > 65_536:
            raise RunError("Assessor did not produce a bounded successful response")
        try:
            answer = final.read_text(encoding="utf-8")
            validate_events(events, answer)
        except UnicodeError as exc:
            raise RunError("Assessor output is not UTF-8") from exc
        return answer


if __name__ == "__main__":
    if len(sys.argv) != 5 or sys.argv[1] != "--supervise":
        raise SystemExit("Internal assessor supervisor only")
    raise SystemExit(supervise(float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]))
