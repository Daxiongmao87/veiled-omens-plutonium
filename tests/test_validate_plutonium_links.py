import importlib.util
from pathlib import Path
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "validate-plutonium-links.py"
ROOT_DIR = SCRIPT.parent.parent
for path in (SCRIPT.parent, ROOT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def _load_validator():
    spec = importlib.util.spec_from_file_location("plutonium_validate_plutonium_links", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = _load_validator()


class ValidatePlutoniumLinksTests(unittest.TestCase):
    def test_class_spells_non_string_entry(self):
        errors = validator.validate({
            "collection/test.json": {
                "class": [
                    {
                        "name": "Occultist",
                        "classSpells": [
                            42
                        ],
                    }
                ]
            }
        })
        self.assertTrue(any("non-string classSpells entry" in e for e in errors))

    def test_veiledomens_class_spells_must_be_local(self):
        errors = validator.validate({
            "collection/test.json": {
                "spell": [
                    {
                        "name": "Known Local Spell",
                        "source": "VeiledOmens"
                    }
                ],
                "class": [
                    {
                        "name": "Occultist",
                        "classSpells": [
                            "Known Local Spell|VeiledOmens",
                            "Missing Local Spell|VeiledOmens",
                        ]
                    }
                ]
            }
        })
        self.assertIn(
            "Missing Local Spell|VeiledOmens",
            "".join(errors)
        )
        self.assertIn("missing local spell entity", "".join(errors))

    def test_non_veiledomens_class_spells_not_checked_locally(self):
        errors = validator.validate({
            "collection/test.json": {
                "class": [
                    {
                        "name": "Occultist",
                        "classSpells": [
                            "Mage Hand",
                            "Cause Fear|XGE",
                            "Spectral Weapon|VeiledOmens"
                        ]
                    }
                ],
                "spell": [
                    {
                        "name": "Spectral Weapon",
                        "source": "VeiledOmens"
                    }
                ]
            }
        })
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
