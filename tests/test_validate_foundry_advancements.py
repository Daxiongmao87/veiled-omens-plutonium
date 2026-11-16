import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "validate-foundry-advancements.py"
_spec = importlib.util.spec_from_file_location("validate_foundry_advancements", SCRIPT)
vfa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vfa)


def class_record(**overrides):
    record = {
        "name": "Testclass",
        "source": "TestSrc",
        "hd": {"number": 1, "faces": 8},
        "startingProficiencies": {"skills": [{"any": 2}]},
        "classFeatures": [],
    }
    record.update(overrides)
    return {"test.json": {"class": [record]}}


def save_errors(data):
    return [e for e in vfa.validate(data) if "proficiency" in e or "savingThrowProficiencies" in e]


class ClassSaveProficiencyTests(unittest.TestCase):
    def test_fixed_saves_pass(self):
        self.assertEqual(save_errors(class_record(proficiency=["str", "con"])), [])

    def test_missing_saves_fail(self):
        errors = save_errors(class_record())
        self.assertEqual(len(errors), 1)
        self.assertIn("proficiency: required", errors[0])

    def test_chosen_saves_pass(self):
        data = class_record(startingProficiencies={
            "skills": [{"any": 2}],
            "savingThrowProficiencies": [{"choose": {"from": ["str", "dex", "con", "int", "wis", "cha"], "count": 2}}],
        })
        self.assertEqual(save_errors(data), [])

    def test_malformed_chosen_saves_fail(self):
        for bad in (
            [{"choose": {"from": ["strength"], "count": 1}}],
            [{"choose": {"from": ["str", "dex"], "count": 3}}],
            [{"str": "yes"}],
            {"choose": {"from": ["str"]}},
        ):
            with self.subTest(bad=bad):
                data = class_record(startingProficiencies={"skills": [{"any": 2}], "savingThrowProficiencies": bad})
                self.assertTrue(save_errors(data), msg=f"expected an error for {bad!r}")


if __name__ == "__main__":
    unittest.main()
