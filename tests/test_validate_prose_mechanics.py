import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "validate-prose-mechanics.py"
FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures" / "prose-mechanics"


class ValidateProseMechanicsTests(unittest.TestCase):
    maxDiff = 20000

    def run_validator(self, fixture: str):
        root = FIXTURES_ROOT / fixture
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root)],
            capture_output=True,
            text=True,
            check=False,
        )
        return result

    def parse_rule_codes(self, text: str):
        return sorted(set(re.findall(r"PM-[A-Z0-9-]+", text)))

    def test_positive_fixture_passes(self):
        result = self.run_validator("positive")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("passed", (result.stdout + result.stderr).lower())
        self.assertFalse(self.parse_rule_codes(result.stderr + result.stdout))

    def test_negative_fixture_fails_with_expected_codes(self):
        result = self.run_validator("negative")
        self.assertNotEqual(result.returncode, 0)
        text = result.stderr + result.stdout
        rules = self.parse_rule_codes(text)
        self.assertIn("PM-ITEM-WONDROUS-TYPE", rules)
        self.assertIn("PM-ITEM-ATTACHED-SPELLS", rules)
        self.assertIn("PM-ITEM-CHARGE-MECH", rules)
        self.assertIn("PM-ITEM-BONUS", rules)
        self.assertIn("PM-CHAR-OPTIONS-COUNT", rules)
        self.assertIn("PM-CHAR-ADDITIONAL-SPELLS", rules)
        self.assertIn("PM-ITEM-DEFENSE-RESIST", rules)
        self.assertIn("PM-ITEM-DEFENSE-CONDITION", rules)
        self.assertIn("Dead Battery", result.stdout + result.stderr)
        self.assertIn("Mana Crystal Prototype", result.stdout + result.stderr)
        self.assertIn("Burnt Generator", result.stdout + result.stderr)
        self.assertIn("startingEquipment.defaultData", text)

    def test_meta_requirement_sentence_not_flagged(self):
        """Requirement sentences that say an item must name a save DC or spell attack bonus
        must not be treated as static bonus grants."""
        fixture_data = {
            "_meta": {
                "sources": [
                    {
                        "json": "meta-requirement.json",
                        "abbreviation": "MR",
                        "full": "Meta Requirement Fixtures"
                    }
                ]
            },
            "item": [
                {
                    "name": "Matrix Rules",
                    "source": "MR",
                    "wondrous": True,
                    "entries": [
                        "An enchanted Arcavene item must name: bound spell and spell level; activation method and trigger; save DC or spell attack bonus; attunement requirement; use limit and reset condition; concentration handling; discharge, suppression, and end behavior."
                    ]
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            collection_dir = root / "collection"
            collection_dir.mkdir()
            (collection_dir / "meta-requirement.json").write_text(json.dumps(fixture_data))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertNotIn("PM-ITEM-BONUS", result.stderr + result.stdout)

    def test_static_bonus_prose_still_flagged(self):
        """A sentence that grants a static spell attack bonus must still trigger PM-ITEM-BONUS."""
        fixture_data = {
            "_meta": {
                "sources": [
                    {
                        "json": "static-bonus.json",
                        "abbreviation": "SB",
                        "full": "Static Bonus Fixtures"
                    }
                ]
            },
            "item": [
                {
                    "name": "Bonus Ring",
                    "source": "SB",
                    "wondrous": True,
                    "entries": [
                        "Your spell attack bonus is +1."
                    ]
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            collection_dir = root / "collection"
            collection_dir.mkdir()
            (collection_dir / "static-bonus.json").write_text(json.dumps(fixture_data))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PM-ITEM-BONUS", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
