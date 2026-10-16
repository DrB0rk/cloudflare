#!/usr/bin/env python3
"""Validate Cloudflare skill structure and core reference links (read-only)."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
REQUIRED_REFERENCES = (
    "decision-framework.md",
    "security-baseline.md",
    "worker-security.md",
    "zero-trust-security.md",
    "dns-tls-waf.md",
    "data-integrity.md",
    "production-delivery.md",
    "observability-incidents.md",
    "performance-cost.md",
    "agent-safety.md",
    "compliance-governance.md",
    "architecture-recipes.md",
    "quality-gates.md",
    "source-policy.md",
    "service-index.md",
)

def validate(root: Path) -> list[str]:
    root = root.resolve()
    issues: list[str] = []
    entry = root / "SKILL.md"
    metadata = root / "agents" / "openai.yaml"
    if not entry.is_file():
        return ["Missing SKILL.md"]
    body = entry.read_text(encoding="utf-8")
    if not body.startswith("---\n") or "\n---\n" not in body[4:]:
        issues.append("SKILL.md must contain YAML frontmatter boundaries")
    else:
        frontmatter = body.split("\n---\n", 1)[0]
        if not re.search(r"(?m)^name:\s+cloudflare\s*$", frontmatter):
            issues.append("SKILL.md frontmatter name must be cloudflare")
        if not re.search(r"(?m)^description:\s*(\S|[>|])", frontmatter):
            issues.append("SKILL.md frontmatter must have a description")
    if not metadata.is_file():
        issues.append("Missing agents/openai.yaml")
    for ref in REQUIRED_REFERENCES:
        if not (root / "references" / ref).is_file():
            issues.append(f"Missing required reference: {ref}")
    pages = [entry] + [root / "references" / x for x in REQUIRED_REFERENCES]
    for page in pages:
        if not page.is_file():
            continue
        page_body = page.read_text(encoding="utf-8")
        for raw in LINK.findall(page_body):
            path = raw.split("#", 1)[0].strip()
            if not path or "://" in path or path.startswith(("mailto:", "#", "/")):
                continue
            target = (page.parent / path).resolve()
            if not target.is_relative_to(root):
                issues.append(f"{page.relative_to(root)}: link escapes skill root: {raw}")
            elif not target.exists():
                issues.append(f"{page.relative_to(root)}: broken link: {raw}")
    return issues

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    issues = validate(args.root)
    if issues:
        for issue in issues:
            print("ERROR:", issue)
        return 1
    print("OK: Cloudflare skill entrypoint, core references and links")
    return 0

if __name__ == "__main__":
    sys.exit(main())
