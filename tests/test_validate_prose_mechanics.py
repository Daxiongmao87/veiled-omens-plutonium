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

    def test_magicvariant_resistance_prose_requires_inherits_resist(self):
        """A magicvariant with resistance prose in inherits.entries must have inherits.resist."""
        fixture_data = {
            "_meta": {
                "sources": [
                    {
                        "json": "mv-resist-test.json",
                        "abbreviation": "MVT",
                        "full": "Magicvariant Resist Test"
                    }
                ]
            },
            "magicvariant": [
                {
                    "name": "Ghostplate",
                    "type": "GV|DMG",
                    "requires": [{"armor": True}],
                    "inherits": {
                        "namePrefix": "Ghostplate ",
                        "source": "MVT",
                        "entries": [
                            "While wearing this armor, the wearer has resistance to necrotic damage."
                        ]
                    },
                    "source": "MVT"
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            collection_dir = root / "collection"
            collection_dir.mkdir()
            (collection_dir / "mv-resist-test.json").write_text(json.dumps(fixture_data))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PM-ITEM-DEFENSE-RESIST", result.stderr + result.stdout)
            self.assertIn("resist", result.stderr + result.stdout)

    def test_magicvariant_with_inherits_resist_passes(self):
        """A magicvariant with resistance prose and inherits.resist should pass."""
        fixture_data = {
            "_meta": {
                "sources": [
                    {
                        "json": "mv-resist-ok.json",
                        "abbreviation": "MVT",
                        "full": "Magicvariant Resist OK"
                    }
                ]
            },
            "magicvariant": [
                {
                    "name": "Shadesilver Armor",
                    "type": "GV|DMG",
                    "requires": [{"armor": True}],
                    "inherits": {
                        "namePrefix": "Shadesilver ",
                        "source": "MVT",
                        "resist": ["necrotic"],
                        "entries": [
                            "While wearing Shadesilver armor, the wearer has resistance to necrotic damage."
                        ]
                    },
                    "source": "MVT"
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            collection_dir = root / "collection"
            collection_dir.mkdir()
            (collection_dir / "mv-resist-ok.json").write_text(json.dumps(fixture_data))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertNotIn("PM-ITEM-DEFENSE", result.stderr + result.stdout)

    def test_magicvariant_negated_prose_no_false_positive(self):
        """Arcavene-style negated bonus/resistance prose must not trigger PM-ITEM-BONUS or PM-ITEM-DEFENSE."""
        fixture_data = {
            "_meta": {
                "sources": [
                    {
                        "json": "mv-negated-test.json",
                        "abbreviation": "MVT",
                        "full": "Magicvariant Negated Test"
                    }
                ]
            },
            "magicvariant": [
                {
                    "name": "Arcavene Armor",
                    "type": "GV|DMG",
                    "requires": [{"armor": True}],
                    "inherits": {
                        "namePrefix": "Arcavene ",
                        "source": "MVT",
                        "entries": [
                            "No default enchantment benefits: no AC bonus, no resistance, no damage-type change, no weight reduction, no stealth benefit."
                        ]
                    },
                    "source": "MVT"
                },
                {
                    "name": "Arcavene Weapon",
                    "type": "GV|DMG",
                    "requires": [{"weapon": True}],
                    "inherits": {
                        "namePrefix": "Arcavene ",
                        "source": "MVT",
                        "entries": [
                            "No default attack bonus, damage bonus, extra damage, damage-type change, or additional passive benefit."
                        ]
                    },
                    "source": "MVT"
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            collection_dir = root / "collection"
            collection_dir.mkdir()
            (collection_dir / "mv-negated-test.json").write_text(json.dumps(fixture_data))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertNotIn("PM-ITEM-BONUS", result.stderr + result.stdout)
            self.assertNotIn("PM-ITEM-DEFENSE", result.stderr + result.stdout)

    def test_magicvariant_inherits_missing_spell_charge_bonus_fails(self):
        """A magicvariant with spell-casting, charge, and AC-bonus prose in inherits.entries
        must fail without inherits.attachedSpells, inherits.charges/recharge, and inherits.bonusAc."""
        fixture_data = {
            "_meta": {
                "sources": [
                    {
                        "json": "mv-missing-all.json",
                        "abbreviation": "MVM",
                        "full": "Magicvariant Missing All"
                    }
                ]
            },
            "magicvariant": [
                {
                    "name": "Incomplete Enchantment",
                    "type": "GV|DMG",
                    "requires": [{"armor": True}],
                    "inherits": {
                        "namePrefix": "Incomplete ",
                        "source": "MVM",
                        "entries": [
                            "While attuned, you can use an action to cast {@spell firebolt|XGtE} from this item.",
                            "This item has 3 charges. It regains all expended charges at dawn.",
                            "While wearing this armor, you gain a +1 bonus to AC."
                        ]
                    },
                    "source": "MVM"
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            collection_dir = root / "collection"
            collection_dir.mkdir()
            (collection_dir / "mv-missing-all.json").write_text(json.dumps(fixture_data))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            text = result.stderr + result.stdout
            self.assertNotEqual(result.returncode, 0, msg=text)
            self.assertIn("PM-ITEM-ATTACHED-SPELLS", text)
            self.assertIn("PM-ITEM-CHARGE-MECH", text)
            self.assertIn("PM-ITEM-BONUS", text)

    def test_magicvariant_fully_structured_inherits_passes(self):
        """A magicvariant with spell-casting, charge, and AC-bonus prose fully structured
        in inherits must pass all five item-validator surfaces."""
        fixture_data = {
            "_meta": {
                "sources": [
                    {
                        "json": "mv-full-ok.json",
                        "abbreviation": "MVF",
                        "full": "Magicvariant Full OK"
                    }
                ]
            },
            "magicvariant": [
                {
                    "name": "Complete Enchantment",
                    "type": "GV|DMG",
                    "requires": [{"armor": True}],
                    "inherits": {
                        "namePrefix": "Complete ",
                        "source": "MVF",
                        "wondrous": True,
                        "bonusAc": 1,
                        "charges": 3,
                        "recharge": "Dawn",
                        "rechargeAmount": 3,
                        "attachedSpells": [
                            {
                                "spell": "firebolt|MVF",
                                "type": "activation",
                                "uses": 1
                            }
                        ],
                        "entries": [
                            "While attuned, you can use an action to cast {@spell firebolt|MVF} from this item.",
                            "This item has 3 charges. It regains all expended charges at dawn.",
                            "While wearing this armor, you gain a +1 bonus to AC."
                        ]
                    },
                    "source": "MVF"
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            collection_dir = root / "collection"
            collection_dir.mkdir()
            (collection_dir / "mv-full-ok.json").write_text(json.dumps(fixture_data))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertNotIn("PM-ITEM-ATTACHED-SPELLS", result.stderr + result.stdout)
            self.assertNotIn("PM-ITEM-CHARGE-MECH", result.stderr + result.stdout)
            self.assertNotIn("PM-ITEM-BONUS", result.stderr + result.stdout)
            self.assertNotIn("PM-ITEM-WONDROUS", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
