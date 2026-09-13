"""Regression coverage for spell metadata consumed by Plutonium's importer."""

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location(
    "validate_content_json", ROOT / "tools" / "validate-content-json.py"
)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class SpellAttackValidationTests(unittest.TestCase):
    """Catch the boolean attack metadata which crashed Spirit Lantern imports."""

    def validate_spell(self, fields):
        data = {
            "_meta": {"sources": [{"json": "VeiledOmens"}]},
            "spell": [{"name": "Spirit Lantern", "source": "VeiledOmens", **fields}],
        }
        return VALIDATOR.validate_content_file(ROOT / "collection" / "fixture.json", data)

    def test_rejects_malformed_attack_metadata(self):
        for value in (True, False, None, "R", [], ["r"], ["ranged"], [True], [{}]):
            with self.subTest(value=value):
                errors = self.validate_spell({"spellAttack": value})
                self.assertEqual(len(errors), 1, errors)
                self.assertIn("Spirit Lantern", errors[0])
                self.assertIn("spellAttack", errors[0])

    def test_accepts_reference_attack_arrays_and_absent_field(self):
        for fields in ({}, {"spellAttack": ["M"]}, {"spellAttack": ["R"]},
                       {"spellAttack": ["O"]}, {"spellAttack": ["M", "R"]}):
            with self.subTest(fields=fields):
                self.assertEqual(self.validate_spell(fields), [])


if __name__ == "__main__":
    unittest.main()
