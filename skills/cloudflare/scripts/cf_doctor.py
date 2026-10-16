#!/usr/bin/env python3
"""Read-only, secret-redacting local diagnostic for Cloudflare platform tools.

Covers cf CLI, Wrangler CLI, cloudflared, and project configurations.
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
    nearest_parent_wrangler = next(
        (str(parent / f) for parent in directory.parents for f in WRANGLER_FILES if (parent / f).is_file()),
        None,
    )
    return {
        "working_directory": str(directory),
        "kind": kind,
        "configuration_files": files,
        "nearest_parent_cf_config": nearest_parent_cf,
        "nearest_parent_wrangler_config": nearest_parent_wrangler,
        "note": (
            "Wrangler-only: use Wrangler for dev/build/deploy. Migrate to cf only when cloudflare.config.ts is present."
            if kind == "wrangler-only"
            else "The presence of cloudflare.config.ts permits cf Worker commands, subject to review."
            if kind == "cf-configured"
            else "Unconfigured: commands may create new configurations or prompt for project creation."
        ),
    }


def safe_run(argv: list[str], *, cwd: Path, timeout: int = 8) -> str | None:
    try:
        result = subprocess.run(
            argv, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, check=False,
            env={**os.environ, "CF_SEND_TELEMETRY": "false", "WRANGLER_SEND_METRICS": "false"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    output = (result.stdout or result.stderr).strip()
    return output.splitlines()[0][:160] if output else None


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


def cf_cli_info(directory: Path) -> dict:
    result = []
    for name in ("cf", "cloudflare"):
        path = shutil.which(name)
        if path:
            result.append({
                "name": name,
                "executable": path,
                "version_output": safe_run([path, "--version"], cwd=directory)
            })
    return {"found": bool(result), "candidates": result, "preferred": result[0]["name"] if result else None}


def wrangler_info(directory: Path) -> dict:
    local_wrangler = directory / "node_modules" / ".bin" / "wrangler"
    global_wrangler = shutil.which("wrangler")
    executable = str(local_wrangler) if local_wrangler.is_file() else global_wrangler
    version = safe_run([executable, "--version"], cwd=directory) if executable else None
    return {
        "found": bool(executable),
        "is_local": local_wrangler.is_file(),
        "executable": executable,
        "version_output": version,
    }


def tunnel_info(directory: Path) -> dict:
    path = shutil.which("cloudflared")
    version = safe_run([path, "--version"], cwd=directory) if path else None
    return {
        "found": bool(path),
        "executable": path,
        "version_output": version,
    }


def env_file_keys(directory: Path) -> list[str]:
    path = directory / ".env"
    if not path.is_file():
        return []
    keys = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = re.match(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=", line)
            if match and (match.group(1).startswith("CLOUDFLARE_") or match.group(1).startswith("CF_") or match.group(1).startswith("WRANGLER_")):
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
    cf_cli = cf_cli_info(cwd)
    wrangler = wrangler_info(cwd)
    tunnel = tunnel_info(cwd)
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
    if not cf_cli["found"] and not wrangler["found"]:
        alerts.append("Neither cf nor wrangler found on PATH; install cf (npm install -g cf) or wrangler (npm install -D wrangler).")
    if project["kind"] == "wrangler-only":
        alerts.append("Use Wrangler for dev/build/deploy until intentional cf migrate; cf resource commands remain available.")
    if flags["CLOUDFLARE_API_TOKEN_set_in_process"]:
        alerts.append("CLOUDFLARE_API_TOKEN overrides OAuth profiles; inspect intended account before mutations.")
    return {
        "project": project,
        "node": node,
        "cf_cli": cf_cli,
        "wrangler": wrangler,
        "tunnel": tunnel,
        "credential_presence_only": flags,
        "alerts": alerts,
        "makes_api_calls": False
    }


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
