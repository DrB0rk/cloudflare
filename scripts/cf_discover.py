#!/usr/bin/env python3
"""Read-only cf cli search/docs search/schema/help orchestration for agents.

Never executes API resource operations and never shells out through a shell.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from typing import Any

COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def resolve_cli(override: str | None = None) -> str:
    if override:
        path = shutil.which(override)
        if not path:
            raise FileNotFoundError(f"CLI executable not found: {override}")
        return path
    for name in ("cf", "cloudflare"):
        path = shutil.which(name)
        if path:
            return path
    raise FileNotFoundError("Cloudflare cf not found on PATH. Install npm install --global cf.")


def invoke(cli: str, args: list[str], timeout: int = 25) -> tuple[int, str, str]:
    env = os.environ.copy()
    # Don't transmit natural-language search prompts in telemetry unless explicitly enabled.
    env.setdefault("CF_SEND_TELEMETRY", "false")
    try:
        result = subprocess.run([cli, *args], capture_output=True, text=True,
                                check=False, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return 124, "", "Timed out while introspecting cf"
    return result.returncode, result.stdout, result.stderr


def command_components(candidate: Any) -> list[str] | None:
    if not isinstance(candidate, str):
        return None
    try:
        tokens = shlex.split(candidate)
    except ValueError:
        return None
    if len(tokens) < 2 or tokens[0] not in ("cf", "cloudflare"):
        return None
    if any(not COMPONENT.fullmatch(token) for token in tokens[1:]):
        return None
    return tokens[1:]


def parse_matches(raw: str, *, docs: bool = False) -> list[dict]:
    data = json.loads(raw)
    if isinstance(data, dict):
        # The beta CLI may wrap results; don't conflate a wrapper with an entry.
        data = data.get("results", data.get("matches"))
    if not isinstance(data, list):
        raise ValueError("Expected JSON results array from cf discovery")
    if docs:
        # Preserve ranked documentation metadata such as title/description/url.
        return [item for item in data if isinstance(item, dict)]
    return [{"command": item.get("command"),
             "summary": item.get("summary", item.get("description"))}
            for item in data if isinstance(item, dict)]


def discover(query: str, *, cli: str, inspect: bool = False, docs: bool = False,
             max_chars: int = 12000) -> dict:
    cmd = ["docs", "search", query] if docs else ["cli", "search", query]
    code, stdout, stderr = invoke(cli, cmd)
    result: dict[str, Any] = {"query": query, "mode": "docs" if docs else "commands",
                              "only_discovery_invoked": True, "search_returncode": code}
    if code != 0:
        result["error"] = (stderr or "Search failed")[:max_chars]
        return result
    try:
        matches = parse_matches(stdout, docs=docs)
    except (ValueError, json.JSONDecodeError) as exc:
        result["error"] = f"Cannot parse result: {exc}"
        result["raw_result_excerpt"] = stdout[:max_chars]
        return result
    result["results"] = matches
    if docs or not inspect or not matches:
        return result
    top = command_components(matches[0].get("command"))
    if top is None:
        result["inspect_error"] = "Top command not a safe cf group/operation path; no command executed"
        return result
    if len(top) >= 2:
        rc, data, err = invoke(cli, ["schema", *top])
        if rc == 0:
            try:
                result["schema"] = json.loads(data)
            except json.JSONDecodeError:
                result["schema_excerpt"] = data[:max_chars]
        else:
            result["schema_unavailable"] = (err or "cf schema not applicable to hand-written commands")[:max_chars]
    else:
        result["schema_unavailable"] = "Top-level command; inspect its --help instead"
    rc, data, err = invoke(cli, [*top, "--help"])
    if rc == 0:
        result["help_excerpt"] = data[:max_chars]
    else:
        result["help_unavailable"] = (err or "--help failed")[:max_chars]
    result["inspected_command"] = matches[0].get("command")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Natural-language task, quoted as one shell argument")
    parser.add_argument("--inspect", action="store_true", help="Read only top match schema and help")
    parser.add_argument("--docs", action="store_true", help="Use beta.15+ cf docs search instead")
    parser.add_argument("--cli", default=None, help="Override executable name/path")
    parser.add_argument("--max-chars", type=int, default=12000, help="Limit text excerpts")
    args = parser.parse_args()
    if not args.query.strip():
        parser.error("query must not be empty")
    try:
        cli = resolve_cli(args.cli)
    except FileNotFoundError as exc:
        print(json.dumps({"error": str(exc), "only_discovery_invoked": True}), file=sys.stdout)
        return 2
    report = discover(args.query, cli=cli, inspect=args.inspect, docs=args.docs,
                      max_chars=max(100, min(args.max_chars, 100000)))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not report.get("error") else 1


if __name__ == "__main__":
    sys.exit(main())
