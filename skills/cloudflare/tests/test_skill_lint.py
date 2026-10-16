"""Test the Cloudflare skill structure checker without network or credentials."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from skill_lint import validate, REQUIRED_REFERENCES


class TestSkillLint(unittest.TestCase):
    @staticmethod
    def populate(root: Path):
        (root / "agents").mkdir()
        (root / "agents" / "openai.yaml").write_text("interface: {}\n")
        (root / "references").mkdir()
        for reference in REQUIRED_REFERENCES:
            (root / "references" / reference).write_text("# Reference\n")
        (root / "SKILL.md").write_text(
            "---\nname: cloudflare\ndescription: Cloudflare engineering instructions\n---\n"
            "\n[Security](references/security-baseline.md)\n"
        )

    def test_valid_skill(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.populate(root)
            self.assertEqual(validate(root), [])

    def test_missing_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.populate(root)
            (root / "references" / "security-baseline.md").unlink()
            self.assertTrue(any("security-baseline.md" in issue for issue in validate(root)))

    def test_rejects_parent_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.populate(root)
            (root / "SKILL.md").write_text(
                (root / "SKILL.md").read_text() + "\n[Escape](../../outside.md)\n"
            )
            self.assertTrue(any("escapes skill root" in issue for issue in validate(root)))


if __name__ == "__main__":
    unittest.main()
