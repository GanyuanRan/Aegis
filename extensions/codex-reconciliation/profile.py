"""Install an explicitly selected Codex profile without changing base config."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

from review import capture, require
from transport import RunError

FORMAT = "aegis-codex-reconciliation-v1"
SOURCES = ("hook.py", "profile.py", "review.py", "transport.py")


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def private_path(path):
    for part in (path, *path.parents):
        require(not part.is_symlink(), "Private profile paths must not contain symlinks")
        require(not getattr(part, "is_junction", lambda: False)(), "Private profile paths must not contain junctions")
    return path


def read_json(path, limit=262_144):
    private_path(path)
    require(path.is_file() and path.stat().st_size <= limit, "Missing or oversized private state")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise RunError("Invalid private JSON state") from exc


def write_json(path, data):
    private_path(path)
    temporary = path.with_suffix(".new")
    private_path(temporary)
    with temporary.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    os.replace(temporary, path)


def load_config(path, expected=None):
    config = read_json(path)
    if expected is not None:
        require(json_hash(config) == expected, "Profile configuration changed; install and trust a new profile")
    fields = {"format", "workspace", "records", "evidence", "model", "effort", "timeout", "codex", "codeHashes"}
    require(isinstance(config, dict) and set(config) == fields and config["format"] == FORMAT,
            "Unrecognized profile configuration")
    require(isinstance(config["workspace"], str) and Path(config["workspace"]).is_absolute(), "Invalid workspace")
    for name in ("records", "evidence"):
        require(isinstance(config[name], list) and all(isinstance(x, str) and x for x in config[name]), "Invalid input selectors")
    require(config["records"] and len(config["records"]) + len(config["evidence"]) <= 32, "Invalid input count")
    require(isinstance(config["model"], str) and 0 < len(config["model"]) <= 128, "Select a model")
    require(config["effort"] in ("low", "medium", "high", "xhigh"), "Invalid reasoning effort")
    require(type(config["timeout"]) is int and 30 <= config["timeout"] <= 600, "Invalid assessment timeout")
    require(isinstance(config["codex"], str) and Path(config["codex"]).is_absolute(), "Use an absolute Codex executable")
    require(config["codeHashes"] == {name: file_hash(Path(__file__).with_name(name)) for name in SOURCES},
            "Installed code changed; install and trust a new profile")
    root = Path(config["workspace"]).resolve(strict=True)
    require(not path.resolve().is_relative_to(root), "Private profile configuration must be outside the workspace")
    return config


def install(workspace, records, evidence, codex_home, model, effort, timeout, codex):
    root = Path(workspace).resolve(strict=True)
    require(root.is_dir(), "Workspace must be a directory")
    capture(root, records, evidence)  # Validate bounds locally; no model call.
    home = private_path(Path(codex_home).absolute())
    require(not home.resolve().is_relative_to(root), "Codex home must be outside the workspace")
    executable = Path(codex).resolve(strict=True)
    require(executable.is_file() and executable.suffix.lower() not in (".ps1", ".cmd", ".bat"),
            "Use the native Codex executable, not a Windows shell shim")
    code_hashes = {name: file_hash(Path(__file__).with_name(name)) for name in SOURCES}
    config = {"format": FORMAT, "workspace": str(root), "records": records, "evidence": evidence,
              "model": model, "effort": effort, "timeout": timeout, "codex": str(executable), "codeHashes": code_hashes}
    config_hash = json_hash(config)
    name = "aegis-reconcile-" + hashlib.sha256(str(root).encode()).hexdigest()[:12] + "-" + config_hash[:12]
    data = home / "aegis-reconciliation" / name
    config_path, profile = data / "config.json", home / f"{name}.config.toml"
    command_parts = [sys.executable, str(data / "code" / "hook.py"), "--config", str(config_path),
                     "--expected-config", config_hash]
    lines = ["# Generated optional Aegis profile. Review and trust its hooks before use."]
    for event in ("UserPromptSubmit", "Stop"):
        parts = command_parts + ["--event", event]
        command = subprocess.list2cmdline(parts) if os.name == "nt" else shlex.join(parts)
        lines += [f"[[hooks.{event}]]", f"[[hooks.{event}.hooks]]", 'type = "command"',
                  "command = " + json.dumps(command), f"timeout = {timeout + 30}",
                  'statusMessage = "Checking selected inherited records"']
    text = "\n".join(lines) + "\n"
    private_path(profile)
    private_path(data)
    if profile.exists() or data.exists():
        require(profile.is_file() and config_path.is_file() and read_json(config_path) == config
                and profile.read_text(encoding="utf-8") == text
                and all((data / "code" / source).is_file()
                        and file_hash(data / "code" / source) == digest for source, digest in code_hashes.items()),
                "Existing profile differs; preserve it and review its configuration before reinstalling")
    else:
        data.mkdir(parents=True, mode=0o700)
        created = []
        try:
            write_json(config_path, config)
            created.append(config_path)
            load_config(config_path)
            (data / "code").mkdir(mode=0o700)
            for source in SOURCES:
                destination = data / "code" / source
                with destination.open("xb") as stream:
                    stream.write(Path(__file__).with_name(source).read_bytes())
                created.append(destination)
            with profile.open("x", encoding="utf-8", newline="\n") as stream:
                created.append(profile)
                stream.write(text)
        except Exception:
            for item in reversed(created):
                item.unlink()  # Only files created by this installation.
            if (data / "code").is_dir():
                (data / "code").rmdir()  # Empty-only cleanup, never recursive.
            data.rmdir()
            raise
    return {"profile": name, "config": str(config_path), "profileFile": str(profile),
            "next": "Review and trust the hooks, then select this profile with codex -p <profile> -C <workspace>."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--record", action="append", required=True)
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", choices=("low", "medium", "high", "xhigh"), required=True)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--codex", default=shutil.which("codex"))
    args = parser.parse_args()
    try:
        require(args.codex is not None, "Codex executable not found; supply --codex")
        print(json.dumps(install(args.workspace, args.record, args.evidence, args.codex_home,
                                 args.model, args.effort, args.timeout, args.codex), indent=2))
    except (RunError, OSError, ValueError) as exc:
        parser.exit(2, f"Profile not installed: {exc}\n")


if __name__ == "__main__":
    main()
