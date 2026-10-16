#!/usr/bin/env python3
"""Read-only, secret-redacting local diagnostic for Cloudflare cf CLI agents.

No Cloudflare API requests, no logins, no file writes. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

WRANGLER_FILES = ("wrangler.json", "wrangler.jsonc", "wrangler.toml")
CONFIG_FILE = "cloudflare.config.ts"
MIN_NODE_VERSION = (22, 18, 0)


def project_state(directory: Path) -> dict:
    directory = directory.resolve()
    files = sorted([name for name in (*WRANGLER_FILES, CONFIG_FILE) if (directory / name).is_file()])
    has_cf = CONFIG_FILE in files
    has_wrangler = any(name in files for name in WRANGLER_FILES)
    if has_cf:
        kind = "cf-configured"
    elif has_wrangler:
        kind = "wrangler-only"
    else:
        kind = "unconfigured"
    nearest_parent_cf = next(
        (str(parent / CONFIG_FILE) for parent in directory.parents if (parent / CONFIG_FILE).is_file()),
        None,
    )
    return {
        "working_directory": str(directory),
        "kind": kind,
        "configuration_files": files,
        "nearest_parent_cf_config": nearest_parent_cf,
        "note": (
            "Wrangler-only: NEVER run cf init/dev/build/deploy or build-backed Worker commands before migration."
            if kind == "wrangler-only"
            else "The presence of cloudflare.config.ts permits cf Worker commands, subject to review."
            if kind == "cf-configured"
            else "Unconfigured: cf project commands may automatically create/modify files and install packages."
        ),
    }


def safe_run(argv: list[str], *, cwd: Path, timeout: int = 8) -> str | None:
    try:
        result = subprocess.run(
            argv, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, check=False,
            env={**os.environ, "CF_SEND_TELEMETRY": "false"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return (result.stdout or result.stderr).strip().splitlines()[0][:160] if (result.stdout or result.stderr).strip() else None


def node_info(directory: Path) -> dict:
    path = shutil.which("node")
    if not path:
        return {"found": False, "compatible": False, "required": ">=22.18.0"}
    version = safe_run([path, "--version"], cwd=directory)
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?", version or "")
    parsed = tuple(int(x) for x in match.groups()) if match else None
    return {
        "found": True,
        "executable": path,
        "version": version,
        "compatible": (parsed >= MIN_NODE_VERSION) if parsed else False,
        "required": ">=22.18.0",
    }


def cli_info(directory: Path) -> dict:
    result = []
    for name in ("cf", "cloudflare"):
        path = shutil.which(name)
        if path:
            result.append({"name": name, "executable": path,
                           "version_output": safe_run([path, "--version"], cwd=directory)})
    return {"found": bool(result), "candidates": result, "preferred": result[0]["name"] if result else None}


def env_file_keys(directory: Path) -> list[str]:
    path = directory / ".env"
    if not path.is_file():
        return []
    keys = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = re.match(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=", line)
            if match and (match.group(1).startswith("CLOUDFLARE_") or match.group(1).startswith("CF_")):
                keys.append(match.group(1))
    except OSError:
        return []
    return sorted(set(keys))  # Never return values.


def collect(cwd: Path) -> dict:
    cwd = cwd.resolve()
    if not cwd.is_dir():
        raise ValueError("--cwd must be an existing directory")
    project = project_state(cwd)
    node = node_info(cwd)
    cli = cli_info(cwd)
    keys = env_file_keys(cwd)
    flags = {
        "CLOUDFLARE_API_TOKEN_set_in_process": bool(os.environ.get("CLOUDFLARE_API_TOKEN")),
        "CLOUDFLARE_ACCOUNT_ID_set_in_process": bool(os.environ.get("CLOUDFLARE_ACCOUNT_ID")),
        "CLOUDFLARE_ZONE_ID_set_in_process": bool(os.environ.get("CLOUDFLARE_ZONE_ID")),
        "CI_set": bool(os.environ.get("CI")),
        "dot_env_exists": (cwd / ".env").is_file(),
        "dot_env_matching_key_names_only": keys,
    }
    alerts = []
    if not node["compatible"]:
        alerts.append("Node.js >=22.18 is required; CLI project config loading is unsupported on Bun.")
    if not cli["found"]:
        alerts.append("cf/cloudflare executable not on PATH; install with npm install --global cf.")
    if project["kind"] == "wrangler-only":
        alerts.append("Use Wrangler for dev/build/deploy until intentional cf migrate; cf resource commands remain available.")
    if flags["CLOUDFLARE_API_TOKEN_set_in_process"]:
        alerts.append("CLOUDFLARE_API_TOKEN overrides OAuth profiles; inspect intended account before mutations.")
    return {"project": project, "node": node, "cf_cli": cli,
            "credential_presence_only": flags, "alerts": alerts, "makes_api_calls": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", default=".", help="Directory to inspect without modification")
    args = parser.parse_args()
    try:
        report = collect(Path(args.cwd))
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
