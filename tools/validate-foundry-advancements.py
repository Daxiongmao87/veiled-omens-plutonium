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
SPELL_TAG_RE = re.compile(r"\{@spell\s+(?P<spell>[^}|#]+)(?:[|#][^}]*)?\}", re.IGNORECASE)
RACE_SPELLCASTING_TEXT_RE = re.compile(r"\{@spell|\bcan cast\b|\bcantrip\b", re.IGNORECASE)
RACE_FEATURE_SKIP_NAMES = {
    "Ability Score Increase",
    "Ability Score Changes",
    "Age",
    "Alignment",
    "Language",
    "Languages",
    "Hardy and Wise",
    "Mystical Crafters",
    "Secluded Mariners",
    "Size",
    "Speed",
    "Subrace",
    "Vaetyr Names",
    "Whispers on the Wind",
}
CLASS_FEATURE_ITEM_SKIP_NAMES = {
    "Ability Score Improvement",
}


def rel_path(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, Mapping):
        raise ValueError(f"{rel_path(path)}: top-level JSON must be an object")
    return data


def parse_int(value: Any, label: str, errors: list[str]) -> int | None:
    if isinstance(value, bool):
        errors.append(f"{label}: expected integer, got boolean")
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    errors.append(f"{label}: expected integer, got {value!r}")
    return None


def validate_foundry_id(value: Any, label: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not FOUNDRY_ID_RE.fullmatch(value):
        errors.append(f"{label}: expected 16-character Foundry id")
        return None
    return value


def parse_class_feature_ref(
    ref: Any,
    label: str,
    errors: list[str],
) -> tuple[str, str, str, int, str] | None:
    if isinstance(ref, Mapping):
        ref = ref.get("classFeature")
    if not isinstance(ref, str):
        errors.append(f"{label}: class feature ref must be a string or object with classFeature")
        return None

    parts = ref.split("|")
    if len(parts) not in {4, 5}:
        errors.append(f"{label}: class feature ref must have 4 or 5 pipe-delimited parts")
        return None
    name, class_name, class_source, level_raw = parts[:4]
    source = parts[4] if len(parts) == 5 else class_source
    level = parse_int(level_raw, f"{label}.level", errors)
    required = [name, class_name, class_source, source]
    if level is None or any(not item.strip() for item in required):
        errors.append(f"{label}: class feature ref contains an empty required field")
        return None
    return name, class_name, class_source, level, source


def parse_subclass_feature_ref(
    ref: Any,
    label: str,
    errors: list[str],
) -> tuple[str, str, str, str, str, int, str] | None:
    if not isinstance(ref, str):
        errors.append(f"{label}: subclass feature ref must be a string")
        return None

    parts = ref.split("|")
    if len(parts) != 7:
        errors.append(f"{label}: subclass feature ref must have 7 pipe-delimited parts")
        return None
    name, class_name, class_source, subclass_short_name, subclass_source, level_raw, source = parts
    level = parse_int(level_raw, f"{label}.level", errors)
    required = [name, class_name, class_source, subclass_short_name, subclass_source, source]
    if level is None or any(not item.strip() for item in required):
        errors.append(f"{label}: subclass feature ref contains an empty required field")
        return None
    return name, class_name, class_source, subclass_short_name, subclass_source, level, source


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


def normalize_spell_name(value: str) -> str:
    value = value.split("#", 1)[0].split("|", 1)[0]
    return re.sub(r"\s+", " ", value.strip().lower())


def collect_additional_spell_names(value: Any) -> set[str]:
    if isinstance(value, str):
        if "=" in value:
            return set()
        normalized = normalize_spell_name(value)
        return {normalized} if normalized else set()
    if isinstance(value, list):
        out: set[str] = set()
        for item in value:
            out.update(collect_additional_spell_names(item))
        return out
    if isinstance(value, Mapping):
        out: set[str] = set()
        for item in value.values():
            out.update(collect_additional_spell_names(item))
        return out
    return set()


def extract_spell_tag_names(text: str) -> set[str]:
    return {
        normalize_spell_name(match.group("spell"))
        for match in SPELL_TAG_RE.finditer(text)
    }


def is_race_spellcasting_entry(entry_text: str) -> bool:
    return bool(RACE_SPELLCASTING_TEXT_RE.search(entry_text))


def collect_class_feature_ids(
    rel: str,
    data: Mapping[str, Any],
    errors: list[str],
) -> dict[tuple[str, str, str, int, str], str]:
    out: dict[tuple[str, str, str, int, str], str] = {}
    for index, feature in enumerate(data.get("classFeature", [])):
        label = f"{rel}.classFeature[{index}]"
        if not isinstance(feature, Mapping):
            errors.append(f"{label}: expected object")
            continue
        name = feature.get("name")
        class_name = feature.get("className")
        class_source = feature.get("classSource")
        source = feature.get("source")
        level = parse_int(feature.get("level"), f"{label}.level", errors)
        foundry_id = validate_foundry_id(feature.get("_foundryId"), f"{label}._foundryId", errors)
        required = [name, class_name, class_source, source]
        if level is None or foundry_id is None or any(not isinstance(item, str) or not item.strip() for item in required):
            continue
        out[(name, class_name, class_source, level, source)] = foundry_id
    return out


def collect_subclass_feature_ids(
    rel: str,
    data: Mapping[str, Any],
    errors: list[str],
) -> dict[tuple[str, str, str, str, str, int, str], str]:
    out: dict[tuple[str, str, str, str, str, int, str], str] = {}
    for index, feature in enumerate(data.get("subclassFeature", [])):
        label = f"{rel}.subclassFeature[{index}]"
        if not isinstance(feature, Mapping):
            errors.append(f"{label}: expected object")
            continue
        name = feature.get("name")
        class_name = feature.get("className")
        class_source = feature.get("classSource")
        subclass_short_name = feature.get("subclassShortName")
        subclass_source = feature.get("subclassSource")
        source = feature.get("source")
        level = parse_int(feature.get("level"), f"{label}.level", errors)
        foundry_id = validate_foundry_id(feature.get("_foundryId"), f"{label}._foundryId", errors)
        required = [name, class_name, class_source, subclass_short_name, subclass_source, source]
        if level is None or foundry_id is None or any(not isinstance(item, str) or not item.strip() for item in required):
            continue
        out[(name, class_name, class_source, subclass_short_name, subclass_source, level, source)] = foundry_id
    return out


def get_required_class_feature_targets(
    cls: Mapping[str, Any],
    label: str,
    class_feature_ids: Mapping[tuple[str, str, str, int, str], str],
    errors: list[str],
) -> dict[int, set[str]]:
    class_features = cls.get("classFeatures", [])
    if not isinstance(class_features, list):
        errors.append(f"{label}.classFeatures: expected array")
        return {}

    targets_by_level: dict[int, set[str]] = defaultdict(set)
    for index, raw_ref in enumerate(class_features):
        ref_label = f"{label}.classFeatures[{index}]"
        parsed = parse_class_feature_ref(raw_ref, ref_label, errors)
        if parsed is None:
            continue
        name, class_name, class_source, level, source = parsed
        if name in CLASS_FEATURE_ITEM_SKIP_NAMES:
            continue
        target_id = class_feature_ids.get((name, class_name, class_source, level, source))
        if target_id is None:
            errors.append(f"{ref_label}: missing classFeature _foundryId target for {parsed!r}")
            continue
        targets_by_level[level].add(target_id)
    return targets_by_level


def get_required_subclass_feature_targets(
    subclass: Mapping[str, Any],
    label: str,
    subclass_feature_ids: Mapping[tuple[str, str, str, str, str, int, str], str],
    errors: list[str],
) -> dict[int, set[str]]:
    subclass_features = subclass.get("subclassFeatures", [])
    if not isinstance(subclass_features, list):
        errors.append(f"{label}.subclassFeatures: expected array")
        return {}

    targets_by_level: dict[int, set[str]] = defaultdict(set)
    for index, raw_ref in enumerate(subclass_features):
        ref_label = f"{label}.subclassFeatures[{index}]"
        parsed = parse_subclass_feature_ref(raw_ref, ref_label, errors)
        if parsed is None:
            continue
        target_id = subclass_feature_ids.get(parsed)
        if target_id is None:
            errors.append(f"{ref_label}: missing subclassFeature _foundryId target for {parsed!r}")
            continue
        targets_by_level[parsed[5]].add(target_id)
    return targets_by_level


def get_required_race_feature_targets(
    race: Mapping[str, Any],
    label: str,
    errors: list[str],
) -> dict[int, set[str]]:
    entries = race.get("entries", [])
    if not isinstance(entries, list):
        errors.append(f"{label}.entries: expected array")
        return {}

    targets_by_level: dict[int, set[str]] = defaultdict(set)
    has_additional_spells = bool(race.get("additionalSpells"))

    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        if name in RACE_FEATURE_SKIP_NAMES:
            continue

        entry_text = " ".join(walk_strings(entry.get("entries", [])))
        match = LEVEL_IN_NAME_RE.search(name)
        if match:
            level = int(match.group("level"))
        elif has_additional_spells and is_race_spellcasting_entry(entry_text):
            level = 0
        else:
            text_levels = [int(match.group("level")) for match in REACH_LEVEL_RE.finditer(entry_text)]
            level = min(text_levels) if text_levels and not is_race_spellcasting_entry(entry_text) else 0

        foundry_id = validate_foundry_id(entry.get("_foundryId"), f"{label}.entries[{index}:{name!r}]._foundryId", errors)
        if foundry_id is None:
            continue
        targets_by_level[level].add(foundry_id)

    return targets_by_level


def validate_race_additional_spells(
    rel: str,
    index: int,
    race: Mapping[str, Any],
    errors: list[str],
) -> None:
    name = race.get("name", f"race[{index}]")
    label = f"{rel}.race[{index}:{name!r}]"
    entries = race.get("entries", [])
    if not isinstance(entries, list):
        return

    required_spell_names: set[str] = set()
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        entry_text = " ".join(walk_strings(entry.get("entries", [])))
        if not is_race_spellcasting_entry(entry_text):
            continue
        required_spell_names.update(extract_spell_tag_names(entry_text))

    if not required_spell_names:
        return

    additional_spells = race.get("additionalSpells")
    if not isinstance(additional_spells, list) or not additional_spells:
        errors.append(
            f"{label}.additionalSpells: required for Drow-style racial spellcasting traits "
            f"granting {sorted(required_spell_names)}"
        )
        return

    for additional_spell_index, additional_spell_block in enumerate(additional_spells):
        if not isinstance(additional_spell_block, Mapping):
            errors.append(f"{label}.additionalSpells[{additional_spell_index}]: expected object")

    actual_spell_names = collect_additional_spell_names(additional_spells)
    missing_spell_names = sorted(required_spell_names - actual_spell_names)
    if missing_spell_names:
        errors.append(
            f"{label}.additionalSpells: missing racial spell grant(s) from feature text: "
            f"{missing_spell_names}"
        )


def validate_item_grant_advancement(
    advancement: Mapping[str, Any],
    label: str,
    errors: list[str],
) -> tuple[int | None, set[str]]:
    validate_foundry_id(advancement.get("_id"), f"{label}._id", errors)

    if advancement.get("type") != "ItemGrant":
        errors.append(f"{label}.type: expected 'ItemGrant'")

    level = parse_int(advancement.get("level"), f"{label}.level", errors)

    if advancement.get("title") != "Features":
        errors.append(f"{label}.title: expected 'Features'")

    value = advancement.get("value")
    added: Mapping[str, Any] = {}
    if not isinstance(value, Mapping):
        errors.append(f"{label}.value: expected object")
    elif not isinstance(value.get("added"), Mapping) or not value.get("added"):
        errors.append(f"{label}.value.added: expected non-empty object")
    else:
        added = value["added"]

    configuration = advancement.get("configuration")
    if not isinstance(configuration, Mapping):
        errors.append(f"{label}.configuration: expected object")
        return level, set()

    items = configuration.get("items")
    target_ids: set[str] = set()
    uuid_by_target_id: dict[str, str] = {}
    if not isinstance(items, list):
        errors.append(f"{label}.configuration.items: expected array")
    elif not items:
        errors.append(f"{label}.configuration.items: source-authored ItemGrant rows must not be empty")
    else:
        for item_index, item in enumerate(items):
            item_label = f"{label}.configuration.items[{item_index}]"
            if not isinstance(item, Mapping):
                errors.append(f"{item_label}: expected object")
                continue
            uuid = item.get("uuid")
            if not isinstance(uuid, str) or not uuid.strip():
                errors.append(f"{item_label}.uuid: expected non-empty string")
                continue
            if not uuid.startswith("."):
                errors.append(f"{item_label}.uuid: expected relative child item UUID")
                continue
            target_id = uuid[1:]
            validate_foundry_id(target_id, f"{item_label}.uuid target", errors)
            if item.get("optional") is not False:
                errors.append(f"{item_label}.optional: expected false")
            target_ids.add(target_id)
            uuid_by_target_id[target_id] = uuid

    if configuration.get("optional") is not False:
        errors.append(f"{label}.configuration.optional: expected false")

    spell = configuration.get("spell")
    if not isinstance(spell, Mapping):
        errors.append(f"{label}.configuration.spell: expected Plutonium ItemGrant spell object")
    else:
        if spell.get("ability") != [""]:
            errors.append(f"{label}.configuration.spell.ability: expected ['']")
        if spell.get("preparation") != "":
            errors.append(f"{label}.configuration.spell.preparation: expected empty string")
        uses = spell.get("uses")
        if not isinstance(uses, Mapping) or uses.get("max") != "" or uses.get("per") != "":
            errors.append(f"{label}.configuration.spell.uses: expected empty max/per strings")

    if added:
        added_keys = set(added)
        if added_keys != set(uuid_by_target_id):
            errors.append(
                f"{label}.value.added: keys must match configuration item ids; "
                f"missing={sorted(set(uuid_by_target_id) - added_keys)} extra={sorted(added_keys - set(uuid_by_target_id))}"
            )
        for target_id, uuid in uuid_by_target_id.items():
            if added.get(target_id) != uuid:
                errors.append(f"{label}.value.added[{target_id!r}]: expected {uuid!r}")

    return level, target_ids


def validate_source_item_grants(
    entity: Mapping[str, Any],
    label: str,
    errors: list[str],
    required_targets_by_level: Mapping[int, set[str]] | None = None,
) -> dict[int, set[str]]:
    advancements = entity.get("foundryAdvancement")
    if advancements is None:
        if required_targets_by_level:
            errors.append(f"{label}.foundryAdvancement: required for feature ItemGrant coverage")
        return {}
    if not isinstance(advancements, list):
        errors.append(f"{label}.foundryAdvancement: expected array")
        return {}
    if required_targets_by_level and not advancements:
        errors.append(f"{label}.foundryAdvancement: required rows must not be empty")

    item_grants_by_level: dict[int, set[str]] = defaultdict(set)
    for advancement_index, advancement in enumerate(advancements):
        adv_label = f"{label}.foundryAdvancement[{advancement_index}]"
        if not isinstance(advancement, Mapping):
            errors.append(f"{adv_label}: expected object")
            continue
        if advancement.get("type") != "ItemGrant":
            continue
        level, target_ids = validate_item_grant_advancement(advancement, adv_label, errors)
        if level is not None:
            item_grants_by_level[level].update(target_ids)

    if required_targets_by_level is not None:
        expected_levels = set(required_targets_by_level)
        actual_levels = set(item_grants_by_level)
        missing_levels = sorted(expected_levels - actual_levels)
        if missing_levels:
            errors.append(f"{label}: missing ItemGrant advancement level(s): {missing_levels}")
        extra_levels = sorted(actual_levels - expected_levels)
        if extra_levels:
            errors.append(f"{label}: ItemGrant advancement levels have no feature evidence: {extra_levels}")
        for level in sorted(expected_levels & actual_levels):
            expected_targets = required_targets_by_level[level]
            actual_targets = item_grants_by_level[level]
            missing_targets = sorted(expected_targets - actual_targets)
            extra_targets = sorted(actual_targets - expected_targets)
            if missing_targets:
                errors.append(f"{label}: level {level} ItemGrant missing feature target(s): {missing_targets}")
            if extra_targets:
                errors.append(f"{label}: level {level} ItemGrant has unexpected feature target(s): {extra_targets}")

    return item_grants_by_level


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

    validate_race_additional_spells(rel, index, race, errors)

    required_targets_by_level = get_required_race_feature_targets(race, label, errors)
    validate_source_item_grants(race, label, errors, required_targets_by_level)


def validate_character_option_surfaces(rel: str, data: Mapping[str, Any], errors: list[str]) -> None:
    class_feature_ids = collect_class_feature_ids(rel, data, errors)
    subclass_feature_ids = collect_subclass_feature_ids(rel, data, errors)

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
        required_targets_by_level = get_required_class_feature_targets(cls, label, class_feature_ids, errors)
        validate_source_item_grants(cls, label, errors, required_targets_by_level)

    for index, subclass in enumerate(data.get("subclass", [])):
        if not isinstance(subclass, Mapping):
            errors.append(f"{rel}.subclass[{index}]: expected object")
            continue
        name = subclass.get("name", f"subclass[{index}]")
        label = f"{rel}.subclass[{index}:{name!r}]"
        required_targets_by_level = get_required_subclass_feature_targets(subclass, label, subclass_feature_ids, errors)
        validate_source_item_grants(subclass, label, errors, required_targets_by_level)


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
