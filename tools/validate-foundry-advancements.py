#!/usr/bin/env python3
"""Validate Foundry dnd5e advancement coverage for player options."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping

from plutonium_content import iter_content_json_files


ROOT_DIR = Path(__file__).resolve().parents[1]
FOUNDRY_ID_RE = re.compile(r"^[A-Za-z0-9]{16}$")
LEVEL_IN_NAME_RE = re.compile(r"\(Level (?P<level>\d+)\)")
REACH_LEVEL_RE = re.compile(r"\breach (?P<level>\d+)(?:st|nd|rd|th) level\b", re.IGNORECASE)
RACE_FEATURE_SKIP_NAMES = {
    "Ability Score Increase",
    "Ability Score Changes",
    "Age",
    "Alignment",
    "Languages",
    "Size",
    "Speed",
    "Subrace",
}


def rel_path(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, Mapping):
        raise ValueError(f"{rel_path(path)}: top-level JSON must be an object")
    return data


def parse_subclass_feature_level(ref: str, label: str, errors: list[str]) -> int | None:
    parts = ref.split("|")
    if len(parts) != 7:
        errors.append(f"{label}: subclass feature ref must have 7 pipe-delimited parts")
        return None
    level_raw = parts[5]
    if not level_raw.isdigit():
        errors.append(f"{label}: subclass feature level must be an integer, got {level_raw!r}")
        return None
    return int(level_raw)


def walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            out.extend(walk_strings(item))
        return out
    if isinstance(value, Mapping):
        out: list[str] = []
        for item in value.values():
            out.extend(walk_strings(item))
        return out
    return []


def get_required_race_feature_levels(
    race: Mapping[str, Any],
    label: str,
    errors: list[str],
) -> set[int]:
    entries = race.get("entries", [])
    if not isinstance(entries, list):
        errors.append(f"{label}.entries: expected array")
        return set()

    levels: set[int] = set()
    has_level_zero_feature = False

    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        if name in RACE_FEATURE_SKIP_NAMES:
            continue

        match = LEVEL_IN_NAME_RE.search(name)
        if match:
            levels.add(int(match.group("level")))
            continue

        has_level_zero_feature = True
        entry_text = " ".join(walk_strings(entry.get("entries", [])))
        for text_match in REACH_LEVEL_RE.finditer(entry_text):
            levels.add(int(text_match.group("level")))

    if has_level_zero_feature:
        levels.add(0)

    return levels


def get_required_subclass_feature_levels(
    subclass: Mapping[str, Any],
    label: str,
    errors: list[str],
) -> dict[int, int]:
    levels: dict[int, int] = defaultdict(int)
    subclass_features = subclass.get("subclassFeatures", [])
    if not isinstance(subclass_features, list):
        errors.append(f"{label}.subclassFeatures: expected array")
        return levels

    for index, ref in enumerate(subclass_features):
        ref_label = f"{label}.subclassFeatures[{index}]"
        if not isinstance(ref, str):
            errors.append(f"{ref_label}: expected string")
            continue
        level = parse_subclass_feature_level(ref, ref_label, errors)
        if level is not None:
            levels[level] += 1
    return levels


def validate_item_grant_advancement(
    advancement: Mapping[str, Any],
    label: str,
    errors: list[str],
) -> int | None:
    advancement_id = advancement.get("_id")
    if not isinstance(advancement_id, str) or not FOUNDRY_ID_RE.fullmatch(advancement_id):
        errors.append(f"{label}._id: expected 16-character Foundry id")

    if advancement.get("type") != "ItemGrant":
        errors.append(f"{label}.type: expected 'ItemGrant'")

    level = advancement.get("level")
    if isinstance(level, bool) or not isinstance(level, int):
        errors.append(f"{label}.level: expected integer")
        level_out = None
    else:
        level_out = level

    if advancement.get("title") != "Features":
        errors.append(f"{label}.title: expected 'Features'")

    value = advancement.get("value")
    if not isinstance(value, Mapping):
        errors.append(f"{label}.value: expected object")

    configuration = advancement.get("configuration")
    if not isinstance(configuration, Mapping):
        errors.append(f"{label}.configuration: expected object")
        return level_out

    items = configuration.get("items")
    if not isinstance(items, list):
        errors.append(f"{label}.configuration.items: expected array")

    if configuration.get("optional") is not False:
        errors.append(f"{label}.configuration.optional: expected false")

    if "spell" not in configuration:
        errors.append(f"{label}.configuration.spell: key is required; use null when unused")

    return level_out


def validate_subclass_advancements(
    rel: str,
    index: int,
    subclass: Mapping[str, Any],
    errors: list[str],
) -> None:
    name = subclass.get("name", f"subclass[{index}]")
    label = f"{rel}.subclass[{index}:{name!r}]"
    required_levels = get_required_subclass_feature_levels(subclass, label, errors)
    if not required_levels:
        return

    advancements = subclass.get("foundryAdvancement")
    if not isinstance(advancements, list):
        errors.append(f"{label}.foundryAdvancement: required for subclasses with subclassFeatures")
        return

    item_grant_levels: dict[int, int] = defaultdict(int)
    for advancement_index, advancement in enumerate(advancements):
        adv_label = f"{label}.foundryAdvancement[{advancement_index}]"
        if not isinstance(advancement, Mapping):
            errors.append(f"{adv_label}: expected object")
            continue
        if advancement.get("type") != "ItemGrant":
            continue
        level = validate_item_grant_advancement(advancement, adv_label, errors)
        if level is not None:
            item_grant_levels[level] += 1

    for level, feature_count in sorted(required_levels.items()):
        if item_grant_levels[level] != 1:
            errors.append(
                f"{label}: expected one ItemGrant advancement at level {level} "
                f"for {feature_count} subclass feature ref(s), found {item_grant_levels[level]}"
            )

    extra_levels = sorted(set(item_grant_levels) - set(required_levels))
    if extra_levels:
        errors.append(f"{label}: ItemGrant advancement levels have no subclass feature refs: {extra_levels}")


def validate_race_advancements(
    rel: str,
    index: int,
    race: Mapping[str, Any],
    errors: list[str],
) -> None:
    name = race.get("name", f"race[{index}]")
    label = f"{rel}.race[{index}:{name!r}]"

    if not any(race.get(prop) for prop in ("ability", "size", "skillProficiencies", "languageProficiencies", "toolProficiencies")):
        errors.append(f"{label}: race lacks advancement-producing 5etools fields")

    required_levels = get_required_race_feature_levels(race, label, errors)
    if not required_levels:
        return

    advancements = race.get("foundryAdvancement")
    if not isinstance(advancements, list):
        errors.append(f"{label}.foundryAdvancement: required for races with feature entries")
        return

    item_grant_levels: dict[int, int] = defaultdict(int)
    for advancement_index, advancement in enumerate(advancements):
        adv_label = f"{label}.foundryAdvancement[{advancement_index}]"
        if not isinstance(advancement, Mapping):
            errors.append(f"{adv_label}: expected object")
            continue
        if advancement.get("type") != "ItemGrant":
            continue
        level = validate_item_grant_advancement(advancement, adv_label, errors)
        if level is not None:
            item_grant_levels[level] += 1

    for level in sorted(required_levels):
        if item_grant_levels[level] != 1:
            errors.append(
                f"{label}: expected one ItemGrant advancement at level {level} "
                f"for race feature entries, found {item_grant_levels[level]}"
            )

    extra_levels = sorted(set(item_grant_levels) - required_levels)
    if extra_levels:
        errors.append(f"{label}: ItemGrant advancement levels have no race feature evidence: {extra_levels}")


def validate_character_option_surfaces(rel: str, data: Mapping[str, Any], errors: list[str]) -> None:
    for index, race in enumerate(data.get("race", [])):
        if not isinstance(race, Mapping):
            errors.append(f"{rel}.race[{index}]: expected object")
            continue
        validate_race_advancements(rel, index, race, errors)

    for index, cls in enumerate(data.get("class", [])):
        if not isinstance(cls, Mapping):
            errors.append(f"{rel}.class[{index}]: expected object")
            continue
        name = cls.get("name", f"class[{index}]")
        label = f"{rel}.class[{index}:{name!r}]"
        if not cls.get("hd"):
            errors.append(f"{label}.hd: required for Foundry HitPoints advancement generation")
        if not cls.get("proficiency"):
            errors.append(f"{label}.proficiency: required for Foundry save advancement generation")
        if not cls.get("startingProficiencies"):
            errors.append(f"{label}.startingProficiencies: required for Foundry skill/proficiency advancement generation")

    for index, subclass in enumerate(data.get("subclass", [])):
        if not isinstance(subclass, Mapping):
            errors.append(f"{rel}.subclass[{index}]: expected object")
            continue
        validate_subclass_advancements(rel, index, subclass, errors)


def validate(data_by_path: Mapping[str, Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    for rel, data in data_by_path.items():
        validate_character_option_surfaces(rel, data, errors)
    return errors


def main() -> int:
    try:
        data_by_path = {
            rel_path(path): load_json(path)
            for path in iter_content_json_files(ROOT_DIR)
        }
    except (json.JSONDecodeError, OSError, ValueError) as err:
        print(f"Foundry advancement validation failed while loading content: {err}", file=sys.stderr)
        return 1

    errors = validate(data_by_path)
    if errors:
        print("Foundry advancement validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Foundry advancement validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
