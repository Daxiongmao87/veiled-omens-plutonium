#!/usr/bin/env python3
"""Generate the per-Hit-Die Gestalt class variants in the collection from one template.

Plutonium's Charactermancer computes level-up hit points from the class record's single
`hd`, so Gestalt (whose Hit Die depends on the two classes chosen) ships as one class per
die: Gestalt (d6), (d8), (d10) and (d12). The hand-edited source of truth is
templates/gestalt-class.json; never edit the generated records in the collection directly.

Usage:
  python3 tools/generate-gestalt-variants.py            # rewrite the collection
  python3 tools/generate-gestalt-variants.py --check    # exit 1 if the collection is stale
  python3 tools/generate-gestalt-variants.py --extract  # (one-off) create the template
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "collection" / "Patrick Richardson; Veiled Omens Campaign Setting.json"
TEMPLATE = ROOT / "templates" / "gestalt-class.json"
SRC = "VeiledOmens"
BASE = "Gestalt"
DICE = (6, 8, 10, 12)
TEMPLATE_HD_SENTENCE = (
    "This class record lists a d8 Hit Die; if your Gestalt Hit Die differs, adjust it on your character sheet."
)
VARIANT_HD_SENTENCE = (
    "Import the Gestalt variant whose Hit Die matches yours. This is Gestalt (d{n}), for a d{n} Hit Die; "
    "if your Gestalt Hit Die is different, use the matching variant instead."
)
PROPS = ("class", "classFeature", "subclass", "subclassFeature")


def md5_14(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:14]


def is_gestalt_family(prop: str, rec: dict) -> bool:
    if rec.get("source") != SRC:
        return False
    if prop == "class":
        return rec.get("name", "").startswith(BASE)
    return rec.get("className", "").startswith(BASE)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_text(data: dict) -> str:
    return json.dumps(data, indent="\t", ensure_ascii=False) + "\n"


def rename_refs(value, old: str, new: str):
    """Rewrite every '|<old>|VeiledOmens|' class reference inside strings, recursively."""
    if isinstance(value, str):
        return value.replace(f"|{old}|{SRC}|", f"|{new}|{SRC}|")
    if isinstance(value, list):
        return [rename_refs(v, old, new) for v in value]
    if isinstance(value, dict):
        return {k: rename_refs(v, old, new) for k, v in value.items()}
    return value


def replace_sentence(value, old: str, new: str, hits: list):
    if isinstance(value, str):
        if old in value:
            hits.append(1)
            return value.replace(old, new)
        return value
    if isinstance(value, list):
        return [replace_sentence(v, old, new, hits) for v in value]
    if isinstance(value, dict):
        return {k: replace_sentence(v, old, new, hits) for k, v in value.items()}
    return value


def build_variants(template: dict) -> dict:
    out = {prop: [] for prop in PROPS}
    for n in DICE:
        name = f"{BASE} (d{n})"
        for prop in PROPS:
            for rec in template[prop]:
                r = rename_refs(copy.deepcopy(rec), BASE, name)
                if prop == "class":
                    r["name"] = name
                    r["hd"] = {"number": 1, "faces": n}
                else:
                    r["className"] = name
                if prop == "classFeature":
                    hits: list = []
                    r = replace_sentence(r, TEMPLATE_HD_SENTENCE, VARIANT_HD_SENTENCE.format(n=n), hits)
                    if r["name"] == "Foundations" and not hits:
                        raise SystemExit("template Foundations no longer contains the Hit Die sentence")
                    r["_foundryId"] = "CF" + md5_14(f"{r['name']}|{name}|{SRC}|{r['level']}|{SRC}")
                elif prop == "subclassFeature":
                    ref = f"{r['name']}|{name}|{SRC}|{r['subclassShortName']}|{SRC}|{r['level']}|{SRC}"
                    r["_foundryId"] = "SF" + md5_14(ref)
                out[prop].append(r)
    return out


def regenerate(collection: dict, template: dict) -> dict:
    data = copy.deepcopy(collection)
    variants = build_variants(template)
    for prop in PROPS:
        kept = [r for r in data.get(prop, []) if not is_gestalt_family(prop, r)]
        data[prop] = kept + variants[prop]
    return data


def extract(collection: dict) -> dict:
    tpl = {"_comment": "Hand-edited source for the Gestalt class. tools/generate-gestalt-variants.py stamps out "
                       "Gestalt (d6/d8/d10/d12) into the collection from this file."}
    for prop in PROPS:
        tpl[prop] = [r for r in collection.get(prop, [])
                     if is_gestalt_family(prop, r) and (r.get("name") == BASE if prop == "class" else r.get("className") == BASE)]
    if len(tpl["class"]) != 1:
        raise SystemExit(f"expected exactly one base {BASE} class record, found {len(tpl['class'])}")
    return tpl


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--extract", action="store_true")
    args = ap.parse_args()
    collection = load(COLLECTION)
    if args.extract:
        TEMPLATE.parent.mkdir(exist_ok=True)
        TEMPLATE.write_text(dump_text(extract(collection)), encoding="utf-8")
        print(f"Wrote {TEMPLATE.relative_to(ROOT)}")
        return 0
    expected = dump_text(regenerate(collection, load(TEMPLATE)))
    current = COLLECTION.read_text(encoding="utf-8")
    if args.check:
        if expected != current:
            print("Gestalt variants are stale: run python3 tools/generate-gestalt-variants.py", file=sys.stderr)
            return 1
        print("Gestalt variant check passed.")
        return 0
    if expected != current:
        COLLECTION.write_text(expected, encoding="utf-8")
        print(f"Regenerated Gestalt variants ({len(DICE)} classes) in {COLLECTION.relative_to(ROOT)}")
    else:
        print("Gestalt variants already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
