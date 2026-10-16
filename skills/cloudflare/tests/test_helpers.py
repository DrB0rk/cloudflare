"""Tests for deterministic skill helpers. No network or Cloudflare API access."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import textwrap
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import cf_discover  # noqa: E402
import cf_doctor  # noqa: E402
import cf_guard  # noqa: E402


class TestDoctor(unittest.TestCase):
    def test_detects_wrangler_and_cf_configs(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "wrangler.jsonc").write_text("{}")
            self.assertEqual(cf_doctor.project_state(folder)["kind"], "wrangler-only")
            (folder / "cloudflare.config.ts").write_text("export default {}")
            self.assertEqual(cf_doctor.project_state(folder)["kind"], "cf-configured")

    def test_env_never_leaks_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / ".env").write_text("CLOUDFLARE_API_TOKEN=SUPER_SECRET_VALUE\nFOO=123\n")
            report = cf_doctor.collect(folder)
            out = json.dumps(report)
            self.assertNotIn("SUPER_SECRET_VALUE", out)
            self.assertIn("CLOUDFLARE_API_TOKEN", out)
            self.assertNotIn('"FOO"', out)


class TestGuard(unittest.TestCase):
    def test_blocks_deploy_in_wrangler_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "wrangler.toml").write_text("name = 'example'\n")
            report = cf_guard.assess(["cf", "deploy", "--dry-run"], folder)
            self.assertEqual(report["status"], "blocked-project-tool-mismatch")
            report = cf_guard.assess(["cf", "dns", "records", "list", "--zone", "example.com"], folder)
            self.assertFalse(report["recognized_build_backed"])

    def test_no_positional_values_exposed(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = cf_guard.assess(["cf", "dns", "records", "delete", "SENSITIVE_RECORD_ID", "--zone", "EXAMPLE.COM"], Path(tmp))
            text = json.dumps(report)
            self.assertEqual(report["status"], "review-required")
            self.assertNotIn("SENSITIVE_RECORD_ID", text)
            self.assertNotIn("EXAMPLE.COM", text)

    def test_unknown_command_never_prints_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = cf_guard.assess(["cf", "unrecognized", "PRIVATE_TOKEN_VALUE"], Path(tmp))
            self.assertEqual(report["command_path_only"], [])
            self.assertNotIn("PRIVATE_TOKEN_VALUE", json.dumps(report))

    def test_introspection_not_classified_as_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = cf_guard.assess(["cf", "schema", "dns", "records", "delete"], Path(tmp))
            self.assertFalse(result["possible_write"])
    def test_wrangler_deploy_review_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = cf_guard.assess(["wrangler", "deploy"], Path(tmp))
            self.assertEqual(report["status"], "review-required")
            self.assertTrue(report["possible_write"])
            self.assertEqual(report["tool"], "wrangler")

    def test_wrangler_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = cf_guard.assess(["wrangler", "deploy", "--dry-run"], Path(tmp))
            self.assertEqual(report["status"], "preview-review-required")
            self.assertTrue(report["has_dry_run_flag"])

    def test_cloudflared_destructive_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = cf_guard.assess(["cloudflared", "tunnel", "delete", "my-tunnel"], Path(tmp))
            self.assertEqual(report["status"], "review-required")
            self.assertTrue(report["is_destructive"])
            self.assertEqual(report["tool"], "cloudflared")


class TestDiscover(unittest.TestCase):
    def test_rejects_injected_commands(self):
        self.assertIsNone(cf_discover.command_components('cf dns records create; rm -rf /'))
        self.assertIsNone(cf_discover.command_components('cf dns records create --body "a"'))
        self.assertEqual(cf_discover.command_components('cf d1 create'), ["d1", "create"])
        self.assertEqual(cf_discover.command_components('cf deploy'), ["deploy"])
        self.assertEqual(cf_discover.parse_matches('{"results":[{"command":"cf zones list"}]}'),
                         [{"command":"cf zones list", "summary":None}])

    def test_fake_cli_search_schema_help_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "cf"
            fake.write_text(textwrap.dedent('''\
                #!/usr/bin/env python3
                import json, sys
                args = sys.argv[1:]
                if args[:2] == ['cli', 'search']:
                    print(json.dumps([{'command':'cf d1 create','summary':'Create D1 Database'}]))
                elif args[:2] == ['docs', 'search']:
                    print(json.dumps([{'title':'D1','url':'https://developers.cloudflare.com/d1/','description':'DB'}]))
                elif args[:2] == ['schema', 'd1']:
                    print(json.dumps({'httpMethod':'POST','path':'/accounts/{account_id}/d1/database'}))
                elif args[-1] == '--help':
                    print('Usage: cf d1 create [options]')
                else:
                    print('unexpected', file=sys.stderr)
                    sys.exit(1)
            '''))
            fake.chmod(0o755)
            result = cf_discover.discover("create D1 database", cli=str(fake), inspect=True)
            self.assertEqual(result["search_returncode"], 0)
            self.assertEqual(result["schema"]["httpMethod"], "POST")
            self.assertIn("Usage:", result["help_excerpt"])
            docs = cf_discover.discover("learn D1", cli=str(fake), docs=True)
            self.assertEqual(docs["results"][0]["title"], "D1")


if __name__ == "__main__":
    unittest.main()
