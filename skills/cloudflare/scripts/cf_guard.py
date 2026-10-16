#!/usr/bin/env python3
"""Static Cloudflare command preflight; does NOT execute anything.

Supports cf CLI, Wrangler CLI, and cloudflared.
Advisory guardrail, not a security boundary: never interpret a pass as
permission to mutate production Cloudflare resources.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

try:
    from cf_doctor import project_state
except ImportError:
    from .cf_doctor import project_state

BUILDBACKED_CF = (
    ("init",), ("dev",), ("build",), ("deploy",), ("previews", "deploy"),
    ("workers", "versions", "create"), ("workers", "triggers", "deploy"),
    ("workers", "check"),
)

READ_VERBS = {
    "list", "get", "show", "query", "raw", "search", "whoami", "check", "types",
    "schema", "info", "inspect", "tail", "docs", "ping", "status"
}

WRITE_VERBS = {
    "create", "update", "edit", "patch", "delete", "remove", "put", "purge", "deploy",
    "apply", "bulk-delete", "bulk-edit", "bulk-put", "upload", "revoke", "disable", "enable",
    "migrate", "login", "logout", "activate", "deactivate", "init", "respond", "send",
    "rollback", "publish", "route"
}


def assess(argv: list[str], cwd: Path) -> dict:
    if not argv:
        return {"status": "invalid", "error": "Empty command provided", "executed": False}

    tool = argv[0]
    if tool not in ("cf", "cloudflare", "wrangler", "cloudflared"):
        return {
            "status": "invalid",
            "error": f"Expected command starting with cf, cloudflare, wrangler, or cloudflared (got {tool})",
            "executed": False
        }

    global_flags_with_values = {"--profile", "--zone", "-z", "--mode", "-m", "--env", "-e", "--config", "-c"}
    command_tokens = []
    skip_next = False
    for item in argv[1:]:
        if skip_next:
            skip_next = False
            continue
        if item in global_flags_with_values:
            skip_next = True
            continue
        if item.startswith("-"):
            continue
        command_tokens.append(item)
        if item in WRITE_VERBS or item in READ_VERBS or item in {"dev", "build", "init", "run"}:
            break

    has_terminator = any(
        token in WRITE_VERBS or token in READ_VERBS or token in {"dev", "build", "init", "run"}
        for token in command_tokens
    )
    segments = command_tokens if has_terminator else []
    state = project_state(cwd)
    dry_run = "--dry-run" in argv
    force = "--force" in argv or "-y" in argv or "--yes" in argv

    is_cf = tool in ("cf", "cloudflare")
    is_wrangler = tool == "wrangler"
    is_tunnel = tool == "cloudflared"

    buildbacked = is_cf and any(tuple(segments[:len(prefix)]) == prefix for prefix in BUILDBACKED_CF)
    wrangler_blocked = is_cf and state["kind"] == "wrangler-only" and buildbacked

    known_write = any(s in WRITE_VERBS for s in segments) and not (segments and segments[0] in {"schema", "cli", "docs"})
    is_delete = any(s in ("delete", "remove", "purge", "bulk-delete", "revoke") for s in segments)

    notes = []
    if wrangler_blocked:
        notes.append("BLOCKED: build-backed cf command in a Wrangler-only project; migrate deliberately or use Wrangler.")
    if is_wrangler:
        notes.append("Tool selection: use Wrangler when it is the established project workflow; use cf for supported typed projects and public API operations. Preserve IaC ownership.")
        if state["kind"] == "cf-configured" and segments and segments[0] in ("deploy", "build"):
            notes.append("Note: cloudflare.config.ts present. Check whether project standard is cf CLI instead of Wrangler.")
    if state["kind"] == "unconfigured" and (buildbacked or (is_wrangler and segments and segments[0] in ("dev", "deploy"))):
        notes.append("Automatic project configuration may install packages or change files even during some previews.")
    if is_delete:
        notes.append("DESTRUCTIVE ACTION: Deletion of Cloudflare resources requires explicit human authorization and verified target ID.")
    if force:
        notes.append("--force or --yes bypasses confirmation prompts; ensure operation and target are verified.")
    if known_write and not dry_run:
        notes.append("Potential remote mutation: explicit authorization and postcondition verification required.")
    if dry_run:
        notes.append("Dry-run suppresses remote mutation for supported commands; local build or packaging may still occur.")
    if not segments:
        notes.append("Cannot classify command path; inspect help/docs before execution.")

    if wrangler_blocked:
        status = "blocked-project-tool-mismatch"
    elif known_write and not dry_run:
        status = "review-required"
    elif dry_run:
        status = "preview-review-required"
    else:
        status = "read-or-unknown-review"

    return {
        "status": status,
        "tool": tool,
        "project_kind": state["kind"],
        "command_path_only": segments,
        "recognized_build_backed": buildbacked,
        "possible_write": known_write,
        "is_destructive": is_delete,
        "has_dry_run_flag": dry_run,
        "has_force_flag": force,
        "notes": notes,
        "executed": False,
        "authorization_granted_by_tool": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", default=".", help="Directory containing project configuration")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="command tokens after --")
    args = parser.parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    print(json.dumps(assess(command, Path(args.cwd)), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
