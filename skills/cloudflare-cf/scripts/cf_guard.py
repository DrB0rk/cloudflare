#!/usr/bin/env python3
"""Static cf command preflight; does NOT execute anything.

This is an advisory guardrail, not a security boundary: never interpret a pass as
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

BUILDBACKED = (
    ("init",), ("dev",), ("build",), ("deploy",), ("previews", "deploy"),
    ("workers", "versions", "create"), ("workers", "triggers", "deploy"),
    ("workers", "check"),
)
READ_VERBS = {"list", "get", "show", "query", "raw", "search", "whoami", "check", "types", "schema", "info", "inspect"}
WRITE_VERBS = {
    "create", "update", "edit", "patch", "delete", "remove", "put", "purge", "deploy",
    "apply", "bulk-delete", "bulk-edit", "bulk-put", "upload", "revoke", "disable", "enable",
    "migrate", "login", "logout", "activate", "deactivate", "init", "respond", "send",
}


def assess(argv: list[str], cwd: Path) -> dict:
    if not argv or argv[0] not in ("cf", "cloudflare"):
        return {"status": "invalid", "error": "Expected command starting cf or cloudflare",
                "executed": False}
    # Best-effort shape parsing; do not reveal argument values (IDs, JSON, secrets).
    # Global flags can precede the command, but this static analysis isn't a parser.
    global_flags_with_values = {"--profile", "--zone", "-z", "--mode", "-m"}
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
        # Terminal operations are where generated command paths end.
        if item in WRITE_VERBS or item in READ_VERBS or item in {"dev", "build", "init"}:
            break
    # Without a known command terminator, the remaining values might be
    # positional IDs or secrets. Never echo unclassified raw arguments.
    has_terminator = any(token in WRITE_VERBS or token in READ_VERBS or
                         token in {"dev", "build", "init"} for token in command_tokens)
    segments = command_tokens if has_terminator else []
    state = project_state(cwd)
    dry_run = "--dry-run" in argv
    force = "--force" in argv
    buildbacked = any(tuple(segments[:len(prefix)]) == prefix for prefix in BUILDBACKED)
    wrangler_blocked = state["kind"] == "wrangler-only" and buildbacked
    known_write = any(s in WRITE_VERBS for s in segments) and not (segments and segments[0] in {"schema", "cli", "docs"})
    notes = []
    if wrangler_blocked:
        notes.append("BLOCKED: build-backed cf command in a Wrangler-only project; migrate deliberately or use Wrangler.")
    if state["kind"] == "unconfigured" and buildbacked:
        notes.append("Automatic project configuration may install packages or change files even during some previews.")
    if force:
        notes.append("--force can bypass confirmations or change API semantics; require explicit review.")
    if known_write and not dry_run:
        notes.append("Potential remote mutation or local filesystem/auth change: explicit authorization and independent verification required.")
    if dry_run:
        notes.append("Dry-run suppresses API mutation for supported commands but may still build/read/change local state; confirm --help.")
    if not segments:
        notes.append("Cannot classify; inspect help/schema before execution.")
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
        "project_kind": state["kind"],
        "command_path_only": segments,  # No flags or positional values after first flag.
        "recognized_build_backed": buildbacked,
        "possible_write": known_write,
        "has_dry_run_flag": dry_run,
        "has_force_flag": force,
        "notes": notes,
        "executed": False,
        "authorization_granted_by_tool": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", default=".", help="Directory containing project configuration")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="cf command tokens after --")
    args = parser.parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    print(json.dumps(assess(command, Path(args.cwd)), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
