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
SPELL_TAG_UID_RE = re.compile(r"\{@spell\s+(?P<spell>[^}]+)\}", re.IGNORECASE)
RACE_SPELLCASTING_TEXT_RE = re.compile(r"\{@spell|\bcan cast\b|\bcantrip\b", re.IGNORECASE)
SPELLCASTING_FIXED_GRANT_TEXT_RE = re.compile(r"\bat\s+\d+(?:st|nd|rd|th)\s+level,\s*you\s+(?:know|learn)\b", re.IGNORECASE)
SPELLCASTING_PROGRESSION_FIELDS = (
    "cantripProgression",
    "spellsKnownProgression",
    "preparedSpellsProgression",
    "spellsKnownProgressionFixed",
    "spellsKnownProgressionFixedByLevel",
    "spellsKnownProgressionFixedAllowLowerLevel",
    "spellsKnownProgressionFixedAllowHigherLevel",
)
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


def iter_ref_subclass_feature_refs(value: Any) -> list[str]:
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            out.extend(iter_ref_subclass_feature_refs(item))
        return out
    if isinstance(value, Mapping):
        out: list[str] = []
        if value.get("type") == "refSubclassFeature":
            ref = value.get("subclassFeature")
            if isinstance(ref, str):
                out.append(ref)
        for item in value.values():
            out.extend(iter_ref_subclass_feature_refs(item))
        return out
    return []


def normalize_spell_name(value: str) -> str:
    value = value.split("#", 1)[0].split("|", 1)[0]
    return re.sub(r"\s+", " ", value.strip().lower())


def normalize_spell_uid(value: str) -> str:
    value = value.split("#", 1)[0]
    parts = [part.strip() for part in value.split("|")]
    name = re.sub(r"\s+", " ", parts[0].strip().lower())
    source = parts[1].strip().lower() if len(parts) > 1 else ""
    return f"{name}|{source}" if name and source else name


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


def collect_additional_spell_uids(value: Any) -> set[str]:
    if isinstance(value, str):
        if "=" in value:
            return set()
        normalized = normalize_spell_uid(value)
        return {normalized} if normalized else set()
    if isinstance(value, list):
        out: set[str] = set()
        for item in value:
            out.update(collect_additional_spell_uids(item))
        return out
    if isinstance(value, Mapping):
        out: set[str] = set()
        for item in value.values():
            out.update(collect_additional_spell_uids(item))
        return out
    return set()


def extract_spell_tag_names(text: str) -> set[str]:
    return {
        normalize_spell_name(match.group("spell"))
        for match in SPELL_TAG_RE.finditer(text)
    }


def extract_spell_tag_uids(text: str) -> set[str]:
    return {
        normalize_spell_uid(match.group("spell"))
        for match in SPELL_TAG_UID_RE.finditer(text)
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


def collect_class_feature_records(
    rel: str,
    data: Mapping[str, Any],
    errors: list[str],
) -> dict[tuple[str, str, str, int, str], Mapping[str, Any]]:
    out: dict[tuple[str, str, str, int, str], Mapping[str, Any]] = {}
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
        required = [name, class_name, class_source, source]
        if level is None or any(not isinstance(item, str) or not item.strip() for item in required):
            continue
        out[(name, class_name, class_source, level, source)] = feature
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


def collect_subclass_feature_records(
    rel: str,
    data: Mapping[str, Any],
    errors: list[str],
) -> dict[tuple[str, str, str, str, str, int, str], Mapping[str, Any]]:
    out: dict[tuple[str, str, str, str, str, int, str], Mapping[str, Any]] = {}
    for index, feature in enumerate(data.get("subclassFeature", [])):
        label = f"{rel}.subclassFeature[{index}]"
        if not isinstance(feature, Mapping):
            continue
        name = feature.get("name")
        class_name = feature.get("className")
        class_source = feature.get("classSource")
        subclass_short_name = feature.get("subclassShortName")
        subclass_source = feature.get("subclassSource")
        source = feature.get("source")
        level = parse_int(feature.get("level"), f"{label}.level", errors)
        required = [name, class_name, class_source, subclass_short_name, subclass_source, source]
        if level is None or any(not isinstance(item, str) or not item.strip() for item in required):
            continue
        out[(name, class_name, class_source, subclass_short_name, subclass_source, level, source)] = feature
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


def validate_subclass_header_feature(
    subclass: Mapping[str, Any],
    label: str,
    subclass_feature_records: Mapping[tuple[str, str, str, str, str, int, str], Mapping[str, Any]],
    errors: list[str],
) -> None:
    subclass_name = subclass.get("name")
    if not isinstance(subclass_name, str) or not subclass_name.strip():
        return

    subclass_features = subclass.get("subclassFeatures", [])
    if not isinstance(subclass_features, list) or not subclass_features:
        errors.append(f"{label}.subclassFeatures: expected non-empty array")
        return

    parsed = parse_subclass_feature_ref(subclass_features[0], f"{label}.subclassFeatures[0]", errors)
    if parsed is None:
        return

    first_feature = subclass_feature_records.get(parsed)
    if first_feature is None:
        return

    first_feature_name = first_feature.get("name")
    if first_feature_name == subclass_name:
        header_child_refs = {
            ref
            for ref in iter_ref_subclass_feature_refs(first_feature.get("entries", []))
        }
        duplicate_refs = sorted(header_child_refs.intersection(subclass_features[1:]))
        if duplicate_refs:
            errors.append(
                f"{label}.subclassFeatures: same-level mechanical features referenced by the "
                f"subclass header must not also be listed as sibling subclassFeatures: {duplicate_refs}"
            )
        return

    errors.append(
        f"{label}.subclassFeatures[0]: first subclass feature must be a header named {subclass_name!r}; "
        "Plutonium ignores the first subclass feature at the subclass-pick level as the subclass header, "
        "so same-level mechanical subclass features must be referenced inside that header"
    )


def get_required_subclass_feature_targets(
    subclass: Mapping[str, Any],
    label: str,
    subclass_feature_ids: Mapping[tuple[str, str, str, str, str, int, str], str],
    subclass_feature_records: Mapping[tuple[str, str, str, str, str, int, str], Mapping[str, Any]],
    errors: list[str],
) -> dict[int, set[str]]:
    subclass_features = subclass.get("subclassFeatures", [])
    if not isinstance(subclass_features, list):
        errors.append(f"{label}.subclassFeatures: expected array")
        return {}

    targets_by_level: dict[int, set[str]] = defaultdict(set)
    header_feature: Mapping[str, Any] | None = None
    for index, raw_ref in enumerate(subclass_features):
        ref_label = f"{label}.subclassFeatures[{index}]"
        parsed = parse_subclass_feature_ref(raw_ref, ref_label, errors)
        if parsed is None:
            continue
        if index == 0:
            header_feature = subclass_feature_records.get(parsed)
        target_id = subclass_feature_ids.get(parsed)
        if target_id is None:
            errors.append(f"{ref_label}: missing subclassFeature _foundryId target for {parsed!r}")
            continue
        targets_by_level[parsed[5]].add(target_id)

    if header_feature is not None:
        for index, raw_ref in enumerate(iter_ref_subclass_feature_refs(header_feature.get("entries", []))):
            ref_label = f"{label}.subclassFeatures[0].entries.refSubclassFeature[{index}]"
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


def validate_no_source_item_grants(
    entity: Mapping[str, Any],
    label: str,
    errors: list[str],
) -> None:
    advancements = entity.get("foundryAdvancement")
    if advancements is None:
        return
    if not isinstance(advancements, list):
        errors.append(f"{label}.foundryAdvancement: expected array")
        return

    for advancement_index, advancement in enumerate(advancements):
        adv_label = f"{label}.foundryAdvancement[{advancement_index}]"
        if not isinstance(advancement, Mapping):
            errors.append(f"{adv_label}: expected object")
            continue
        if advancement.get("type") == "ItemGrant":
            errors.append(
                f"{adv_label}: source-authored ItemGrant rows are forbidden; "
                "Plutonium generates feature ItemGrant links during actor import"
            )


def validate_class_tool_proficiency_shape(
    proficiencies: Any,
    label: str,
    errors: list[str],
) -> None:
    if not isinstance(proficiencies, Mapping):
        return

    tools = proficiencies.get("tools")
    if tools is None:
        return
    if not isinstance(tools, list):
        errors.append(f"{label}.tools: expected array")
        return

    for index, tool in enumerate(tools):
        if not isinstance(tool, str):
            errors.append(
                f"{label}.tools[{index}]: expected string; "
                "Plutonium class advancement conversion calls string tool entries directly"
            )


def get_character_option_spellcasting_feature_records(
    entity: Mapping[str, Any],
    label: str,
    is_subclass: bool,
    class_feature_records: Mapping[tuple[str, str, str, int, str], Mapping[str, Any]],
    subclass_feature_records: Mapping[
        tuple[str, str, str, str, str, int, str],
        Mapping[str, Any],
    ],
    errors: list[str],
) -> list[Mapping[str, Any]]:
    refs = entity.get("subclassFeatures" if is_subclass else "classFeatures", [])
    if not isinstance(refs, list):
        errors.append(f"{label}.{ 'subclassFeatures' if is_subclass else 'classFeatures'}: expected array")
        return []

    feature_records: list[Mapping[str, Any]] = []
    for index, raw_ref in enumerate(refs):
        if is_subclass:
            parsed = parse_subclass_feature_ref(
                raw_ref,
                f"{label}.subclassFeatures[{index}]",
                errors,
            )
            if parsed is None:
                continue
            feature = subclass_feature_records.get(parsed)
        else:
            parsed = parse_class_feature_ref(
                raw_ref,
                f"{label}.classFeatures[{index}]",
                errors,
            )
            if parsed is None:
                continue
            feature = class_feature_records.get(parsed)

        if feature is None:
            continue

        feature_name = feature.get("name")
        if isinstance(feature_name, str) and feature_name.strip().lower() == "spellcasting":
            feature_records.append(feature)
    return feature_records


def validate_character_spellcasting_additional_spells(
    entity: Mapping[str, Any],
    label: str,
    is_subclass: bool,
    class_feature_records: Mapping[tuple[str, str, str, int, str], Mapping[str, Any]],
    subclass_feature_records: Mapping[
        tuple[str, str, str, str, str, int, str],
        Mapping[str, Any],
    ],
    errors: list[str],
) -> None:
    spellcasting_ability = entity.get("spellcastingAbility")
    if not isinstance(spellcasting_ability, str) or not spellcasting_ability.strip():
        return

    progression_fields = [field for field in SPELLCASTING_PROGRESSION_FIELDS if field in entity]
    if progression_fields and not entity.get("casterProgression"):
        errors.append(
            f"{label}.casterProgression: required when spellcasting progression arrays exist: "
            f"{progression_fields}"
        )

    spellcast_feature_records = get_character_option_spellcasting_feature_records(
        entity,
        label,
        is_subclass,
        class_feature_records,
        subclass_feature_records,
        errors,
    )

    required_spell_uids: set[str] = set()
    for feature in spellcast_feature_records:
        for text in walk_strings(feature.get("entries", [])):
            if SPELLCASTING_FIXED_GRANT_TEXT_RE.search(text):
                required_spell_uids.update(extract_spell_tag_uids(text))

    if not required_spell_uids:
        return

    additional_spells = entity.get("additionalSpells")
    if not isinstance(additional_spells, list) or not additional_spells:
        errors.append(
            f"{label}.additionalSpells: required for fixed spell grants in spellcasting prose: "
            f"{sorted(required_spell_uids)}"
        )
        return

    for additional_spell_index, additional_spell_block in enumerate(additional_spells):
        if not isinstance(additional_spell_block, Mapping):
            errors.append(f"{label}.additionalSpells[{additional_spell_index}]: expected object")

    actual_spell_uids = collect_additional_spell_uids(additional_spells)
    missing_spell_uids = sorted(required_spell_uids - actual_spell_uids)
    if missing_spell_uids:
        errors.append(
            f"{label}.additionalSpells: missing fixed spell grant UID(s) from spellcasting prose: "
            f"{missing_spell_uids}"
        )


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

    get_required_race_feature_targets(race, label, errors)
    validate_no_source_item_grants(race, label, errors)


def validate_character_option_surfaces(rel: str, data: Mapping[str, Any], errors: list[str]) -> None:
    class_feature_ids = collect_class_feature_ids(rel, data, errors)
    class_feature_records = collect_class_feature_records(rel, data, errors)
    subclass_feature_ids = collect_subclass_feature_ids(rel, data, errors)
    subclass_feature_records = collect_subclass_feature_records(rel, data, errors)

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
        validate_class_tool_proficiency_shape(
            cls.get("startingProficiencies"),
            f"{label}.startingProficiencies",
            errors,
        )
        multiclassing = cls.get("multiclassing")
        if isinstance(multiclassing, Mapping):
            validate_class_tool_proficiency_shape(
                multiclassing.get("proficienciesGained"),
                f"{label}.multiclassing.proficienciesGained",
                errors,
            )
        get_required_class_feature_targets(cls, label, class_feature_ids, errors)
        validate_character_spellcasting_additional_spells(
            cls,
            label,
            False,
            class_feature_records,
            subclass_feature_records,
            errors,
        )
        validate_no_source_item_grants(cls, label, errors)

    for index, subclass in enumerate(data.get("subclass", [])):
        if not isinstance(subclass, Mapping):
            errors.append(f"{rel}.subclass[{index}]: expected object")
            continue
        name = subclass.get("name", f"subclass[{index}]")
        label = f"{rel}.subclass[{index}:{name!r}]"
        validate_subclass_header_feature(subclass, label, subclass_feature_records, errors)
        get_required_subclass_feature_targets(
            subclass,
            label,
            subclass_feature_ids,
            subclass_feature_records,
            errors,
        )
        validate_character_spellcasting_additional_spells(
            subclass,
            label,
            True,
            class_feature_records,
            subclass_feature_records,
            errors,
        )
        validate_no_source_item_grants(subclass, label, errors)


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
