import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("gen_gestalt", ROOT / "tools" / "generate-gestalt-variants.py")
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)
TEMPLATE = json.loads((ROOT / "templates" / "gestalt-class.json").read_text(encoding="utf-8"))


class GestaltVariantTests(unittest.TestCase):
    def setUp(self):
        self.v = gen.build_variants(TEMPLATE)

    def test_one_class_per_die_with_matching_hd(self):
        self.assertEqual([(c["name"], c["hd"]["faces"]) for c in self.v["class"]],
                         [(f"Gestalt (d{n})", n) for n in gen.DICE])

    def test_every_reference_points_at_its_own_variant(self):
        for c in self.v["class"]:
            refs = [x if isinstance(x, str) else x["classFeature"] for x in c["classFeatures"]]
            self.assertTrue(refs and all(r.split("|")[1] == c["name"] for r in refs), c["name"])
        for s in self.v["subclass"]:
            self.assertTrue(all(r.split("|")[1] == s["className"] for r in s["subclassFeatures"]), s["name"])
        for prop in ("classFeature", "subclass", "subclassFeature", "class"):
            for r in self.v[prop]:
                self.assertNotIn("|Gestalt|VeiledOmens|", json.dumps(r))

    def test_foundry_ids_unique_across_variants(self):
        ids = [r["_foundryId"] for p in ("classFeature", "subclassFeature") for r in self.v[p]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_hit_die_sentence_names_the_variant(self):
        for n in gen.DICE:
            f = next(r for r in self.v["classFeature"] if r["className"] == f"Gestalt (d{n})" and r["name"] == "Foundations")
            self.assertIn(f"This is Gestalt (d{n})", json.dumps(f))
            self.assertNotIn("adjust it on your character sheet", json.dumps(f))

    def test_regenerate_replaces_old_gestalt_records_and_keeps_others(self):
        coll = {"class": [{"name": "Occultist", "source": "VeiledOmens"}, {"name": "Gestalt", "source": "VeiledOmens"}],
                "classFeature": [{"name": "X", "className": "Gestalt (d6)", "source": "VeiledOmens"}],
                "subclass": [], "subclassFeature": []}
        out = gen.regenerate(copy.deepcopy(coll), TEMPLATE)
        self.assertEqual(out["class"][0]["name"], "Occultist")
        self.assertEqual(sum(1 for c in out["class"] if c["name"].startswith("Gestalt")), len(gen.DICE))
        self.assertFalse(any(r.get("name") == "X" for r in out["classFeature"]))

    def test_collection_is_current(self):
        expected = gen.dump_text(gen.regenerate(gen.load(gen.COLLECTION), TEMPLATE))
        self.assertEqual(expected, gen.COLLECTION.read_text(encoding="utf-8"), "run tools/generate-gestalt-variants.py")


if __name__ == "__main__":
    unittest.main()
