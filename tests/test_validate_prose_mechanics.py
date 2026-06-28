import re
import subprocess
import sys
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


if __name__ == "__main__":
    unittest.main()
