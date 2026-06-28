#!/usr/bin/env python3
"""Validate prose-to-mechanics conventions for Plutonium content JSON."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

from plutonium_content import iter_content_json_files


def _load_foundry_helpers():
    module_path = Path(__file__).with_name("validate-foundry-advancements.py")
    spec = importlib.util.spec_from_file_location("validate_foundry_advancements", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load validator helpers from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_foundry_helpers = _load_foundry_helpers()
collect_additional_spell_uids = _foundry_helpers.collect_additional_spell_uids
collect_class_feature_records = _foundry_helpers.collect_class_feature_records
collect_subclass_feature_records = _foundry_helpers.collect_subclass_feature_records
collect_named_items = _foundry_helpers.collect_named_items
extract_spell_tag_uids = _foundry_helpers.extract_spell_tag_uids
validate_character_spellcasting_additional_spells_foundry = (
    _foundry_helpers.validate_character_spellcasting_additional_spells
)
validate_class_feature_item_grants = _foundry_helpers.validate_class_feature_item_grants

ROOT_DIR = Path(__file__).resolve().parents[1]

SPELL_TRIGGER_RE = re.compile(
    r"\b(?:cast|casts|casting|learn|learns|learned|grant|grants|granted|contained|contain|contains|use|uses|expend|expend\w*)\b",
    re.IGNORECASE,
)
CHARGE_TRIGGER_RE = re.compile(r"\bcharge\b|\bcharges\b|\bcharge\w*\b", re.IGNORECASE)
CHARGE_CONTEXT_RE = re.compile(
    r"\b(?:has\s+(?:the\s+)?charges?|maximum\s+number\s+of\s+charges?|maximum\s+charges?|regain(?:s|ed|ing)?|long\s+rest|short\s+rest|dawn|at\s+dawn|regains?)\b",
    re.IGNORECASE,
)
CHARGE_FULL_REGEN_RE = re.compile(
    r"\b(?:"
    r"regain(?:s|ed|ing)?\s+all(?:\s+(?:its|their))?(?:\s+(?:expended|spent))?\s+(?:charges?|uses?)\b"
    r"|all\s+(?:its\s+)?(?:expended|spent)?\s*(?:charges?|uses?)\s+(?:are|have\s+been|be)?\s+(?:restored|returned|recovered|regained)\b"
    r")\b",
    re.IGNORECASE,
)
BONUS_WEAPON_RE = re.compile(
    r"\b(?:"
    r"(?:to\s+hit|attack\s+bonus|attack\s+rolls?|attack\s+and\s+damage\s+rolls?|attack\s+damage)\b.*\bbonus\b"
    r"|"
    r"bonus\b.{0,80}\b(?:to\s+hit|attack\s+(?:and\s+damage\s+)?rolls?|damage)\b"
    r")",
    re.IGNORECASE,
)
BONUS_AC_RE = re.compile(r"\bbonus\b[^.!?]{0,60}\bac\b|\bac\b[^.!?]{0,60}\bbonus\b", re.IGNORECASE)
BONUS_SPELL_ATTACK_RE = re.compile(r"\bspell\s+attack\b", re.IGNORECASE)
BONUS_SPELL_SAVE_RE = re.compile(r"\bspell\s+save\b\s+dc\b", re.IGNORECASE)
CHOICE_RE = re.compile(
    r"\bchoose\s+(?:(?P<number_word>one|two|three|four|five|six|seven|eight|nine|ten)|(?P<number>\d+))\b",
    re.IGNORECASE,
)
WORD_TO_INT = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}
WORN_STATE_RE = re.compile(r"\b(attuned|worn|wearing|wielding|holding|carried)\b", re.IGNORECASE)
DEFENSE_IMMUNITY_RE = re.compile(
    r"\bresist(?:ance|ant)?\b|\bcondition\s+immune\b|\bcondition\s+immunit(?:y|ies)\b|\bimmunit(?:y|ies)\b|\bimmune\b",
    re.IGNORECASE,
)
TEMPORARY_ACTIVE_RE = re.compile(
    r"\b(?:once|until|for\s+\d+\s+(?:minute|hour|day|round|turn|week)|as\s+an\s+action|bonus\s+action|reaction|activation|activated)\b",
    re.IGNORECASE,
)
OPTION_ENTRY_TYPES = {"refOptionalfeature", "refSubclassFeature"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT_DIR,
        help="Repository root to scan content files from (default: current repository root).",
    )
    return parser.parse_args()


def load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, Mapping):
        raise TypeError(f"{path}: top-level JSON must be an object")
    return data


def rel_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def walk_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from walk_strings(item)
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from walk_strings(item)


def collect_strings(value: Any) -> list[str]:
    return list(walk_strings(value))


def normalize_spell_uid(value: str) -> str:
    value = value.split("#", 1)[0]
    name, source = (value.split("|", 1) + [""])[:2]
    name = re.sub(r"\s+", " ", name.strip().lower())
    source = source.strip().lower()
    return f"{name}|{source}" if source else name


def extract_choice_count(text: str) -> int | None:
    match = CHOICE_RE.search(text)
    if not match:
        return None
    if match.group("number"):
        return int(match.group("number"))
    if match.group("number_word"):
        return WORD_TO_INT[match.group("number_word").lower()]
    return None


def add_error(
    errors: list[str],
    file_path: str,
    label: str,
    rule: str,
    trigger: str,
    expected: str,
    convention_class: str,
) -> None:
    errors.append(
        f"{file_path}:{label} [{rule}] trigger={trigger!r} expected={expected} convention={convention_class}"
    )


def collect_option_refs(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, list):
        for item in value:
            found.extend(collect_option_refs(item))
        return found
    if not isinstance(value, Mapping):
        return found

    node_type = value.get("type")
    if node_type in OPTION_ENTRY_TYPES:
        key = "optionalfeature" if node_type == "refOptionalfeature" else "subclassFeature"
        ref_value = value.get(key)
        if isinstance(ref_value, str):
            found.append(ref_value)

    for item in value.values():
        found.extend(collect_option_refs(item))

    return found


def iter_option_blocks(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, list):
        for item in value:
            yield from iter_option_blocks(item)
        return
    if not isinstance(value, Mapping):
        return

    if value.get("type") == "options":
        yield value

    options_payload = value.get("options")
    if isinstance(options_payload, Mapping):
        yield options_payload

    for item in value.values():
        if item is not options_payload:
            yield from iter_option_blocks(item)


def validate_item_attached_spells(
    file_path: str,
    bucket: str,
    index: int,
    item: Mapping[str, Any],
    errors: list[str],
) -> None:
    label = f"{bucket}[{index}:{item.get('name', 'unnamed')!r}]"
    attached_spells = item.get("attachedSpells")

    if attached_spells is not None and not isinstance(attached_spells, (list, Mapping)):
        add_error(
            errors,
            file_path,
            label,
            "PM-ITEM-ATTACHED-SPELLS",
            "attachedSpells type",
            "attachedSpells as list or bucket object",
            "item.prose-spell-mechanics",
        )
        return

    attached_spell_uids = set()
    if isinstance(attached_spells, (list, Mapping)):
        attached_spell_uids = collect_additional_spell_uids(attached_spells)

    attached_spell_names = {normalize_spell_uid(uid).split("|")[0] for uid in attached_spell_uids}

    for sentence in collect_strings(item.get("entries", [])):
        if not sentence_has_spell_trigger(sentence):
            continue

        required_uids = {normalize_spell_uid(tag) for tag in extract_spell_tag_uids(sentence)}
        if not required_uids:
            continue

        if not attached_spell_uids:
            add_error(
                errors,
                file_path,
                label,
                "PM-ITEM-ATTACHED-SPELLS",
                sentence,
                "attachedSpells",
                "item.prose-spell-mechanics",
            )
            return

        missing = sorted(required_uids - attached_spell_uids)
        if missing:
            required_names = {normalize_spell_uid(uid).split("|")[0] for uid in required_uids}
            missing_names = sorted(name for name in required_names if name not in attached_spell_names)
            add_error(
                errors,
                file_path,
                label,
                "PM-ITEM-ATTACHED-SPELLS",
                sentence,
                f"attachedSpells containing {missing_names or missing}",
                "item.prose-spell-mechanics",
            )


def sentence_has_spell_trigger(sentence: str) -> bool:
    return "{@spell" in sentence.lower() and bool(SPELL_TRIGGER_RE.search(sentence))


def validate_item_charge_mechanics(
    file_path: str,
    bucket: str,
    index: int,
    item: Mapping[str, Any],
    errors: list[str],
) -> None:
    label = f"{bucket}[{index}:{item.get('name', 'unnamed')!r}]"

    has_charge_prose = False
    for sentence in collect_strings(item.get("entries", [])):
        if CHARGE_TRIGGER_RE.search(sentence) and CHARGE_CONTEXT_RE.search(sentence):
            has_charge_prose = True
            break

    if not has_charge_prose:
        return

    if not has_sanctioned_charge_mechanics(item):
        add_error(
            errors,
            file_path,
            label,
            "PM-ITEM-CHARGE-MECH",
            "charge prose present",
            "charges plus recharge/rechargeAmount (or sanctioned dynamic charge pattern)",
            "item.charge-mechanics",
        )


def has_sanctioned_charge_mechanics(item: Mapping[str, Any]) -> bool:
    charges = item.get("charges")
    if charges is None:
        return False

    if not isinstance(charges, (int, str, Mapping)):
        return False

    recharge = item.get("recharge")
    if recharge is not None:
        if not isinstance(recharge, str):
            return False
        normalized_recharge = re.sub(r"[-_\\s]+", "", recharge.strip().lower())
        if normalized_recharge == "longrest":
            return False

    if any(CHARGE_FULL_REGEN_RE.search(sentence) for sentence in collect_strings(item.get("entries", []))):
        charges = item.get("charges")
        recharge_amount = item.get("rechargeAmount")

        if isinstance(charges, bool) or isinstance(recharge_amount, bool):
            return False

        numeric_charges = None
        numeric_recharge_amount = None

        if isinstance(charges, int):
            numeric_charges = charges
        elif isinstance(charges, str) and re.fullmatch(r"\d+", charges.strip()):
            numeric_charges = int(charges.strip())

        if isinstance(recharge_amount, int):
            numeric_recharge_amount = recharge_amount
        elif isinstance(recharge_amount, str) and re.fullmatch(r"\d+", recharge_amount.strip()):
            numeric_recharge_amount = int(recharge_amount.strip())

        if numeric_charges is not None and numeric_recharge_amount is not None:
            if numeric_charges == numeric_recharge_amount:
                return bool(item.get("recharge") or item.get("rechargeAmount"))
            return False

        if recharge_amount is None:
            return bool(item.get("recharge") or item.get("rechargeAmount"))
        return False

    return bool(item.get("recharge") or item.get("rechargeAmount"))


def validate_item_bonus_fields(
    file_path: str,
    bucket: str,
    index: int,
    item: Mapping[str, Any],
    errors: list[str],
) -> None:
    label = f"{bucket}[{index}:{item.get('name', 'unnamed')!r}]"

    required_fields: dict[str, str] = {}
    for sentence in collect_strings(item.get("entries", [])):
        lower = sentence.lower()
        if "bonus" in lower and ("attack" in lower or "to hit" in lower or "damage" in lower):
            if BONUS_WEAPON_RE.search(sentence):
                required_fields.setdefault("bonusWeapon", sentence)
        if BONUS_AC_RE.search(sentence):
            required_fields.setdefault("bonusAc", sentence)
        if BONUS_SPELL_ATTACK_RE.search(sentence):
            required_fields.setdefault("bonusSpellAttack", sentence)
        if BONUS_SPELL_SAVE_RE.search(sentence):
            required_fields.setdefault("bonusSpellSaveDc", sentence)

    for field, trigger in required_fields.items():
        if field not in item or item[field] in ("", None):
            add_error(
                errors,
                file_path,
                label,
                "PM-ITEM-BONUS",
                trigger,
                field,
                "item.bonus-mechanics",
            )


def validate_item_defenses(
    file_path: str,
    bucket: str,
    index: int,
    item: Mapping[str, Any],
    errors: list[str],
) -> None:
    label = f"{bucket}[{index}:{item.get('name', 'unnamed')!r}]"
    has_resist = isinstance(item.get("resist"), list) and bool(item["resist"])
    has_immune = isinstance(item.get("immune"), list) and bool(item["immune"])
    has_condition_immune = isinstance(item.get("conditionImmune"), list) and bool(item["conditionImmune"])

    for sentence in collect_strings(item.get("entries", [])):
        if not WORN_STATE_RE.search(sentence):
            continue
        if not DEFENSE_IMMUNITY_RE.search(sentence):
            continue
        if TEMPORARY_ACTIVE_RE.search(sentence):
            continue

        lower = sentence.lower()
        if "resist" in lower and not has_resist:
            add_error(
                errors,
                file_path,
                label,
                "PM-ITEM-DEFENSE-RESIST",
                sentence,
                "resist",
                "item.defense-mechanics",
            )

        if (
            "condition" in lower
            and ("immune" in lower or "immunit" in lower)
            and not has_condition_immune
        ):
            add_error(
                errors,
                file_path,
                label,
                "PM-ITEM-DEFENSE-CONDITION",
                sentence,
                "conditionImmune",
                "item.defense-mechanics",
            )
        elif ("immune" in lower or "immunit" in lower) and not has_immune:
            add_error(
                errors,
                file_path,
                label,
                "PM-ITEM-DEFENSE-IMMUNE",
                sentence,
                "immune",
                "item.defense-mechanics",
            )


def validate_item_wondrous_type(
    file_path: str,
    bucket: str,
    index: int,
    item: Mapping[str, Any],
    errors: list[str],
) -> None:
    label = f"{bucket}[{index}:{item.get('name', 'unnamed')!r}]"
    item_type = item.get("type")
    if isinstance(item_type, str) and item_type.strip().lower() in {"wondrous", "wondrous item"}:
        add_error(
            errors,
            file_path,
            label,
            "PM-ITEM-WONDROUS-TYPE",
            item_type,
            "omit type and set wondrous=true",
            "item.wondrous-convention",
        )


def validate_option_blocks(
    file_path: str,
    entity_label: str,
    entity: Mapping[str, Any],
    errors: list[str],
) -> None:
    entity_context = " ".join(collect_strings(entity.get("entries", []))).strip()

    for options_block in iter_option_blocks(entity):
        count = options_block.get("count")
        if not isinstance(count, int):
            continue

        texts: list[str] = []
        if isinstance(options_block.get("name"), str):
            texts.append(options_block["name"])  # type: ignore[index]
        texts.extend(
            text for text in collect_strings(options_block.get("entries", [])) if isinstance(text, str)
        )

        combined = " ".join(texts).strip()
        if entity_context and combined:
            combined = f"{entity_context} {combined}"
        elif entity_context:
            combined = entity_context
        if not combined:
            continue

        choose_count = extract_choice_count(combined)
        if choose_count is None:
            continue

        if choose_count != count:
            add_error(
                errors,
                file_path,
                entity_label,
                "PM-CHAR-OPTIONS-COUNT",
                combined,
                f"options.count == {choose_count}",
                "character-option.choice-count",
            )

        refs = collect_option_refs(options_block)
        if len(refs) < count:
            add_error(
                errors,
                file_path,
                entity_label,
                "PM-CHAR-OPTIONS-REFS",
                combined,
                f"at least {count} option refs (refOptionalfeature/refSubclassFeature)",
                "character-option.choice-count",
            )


def validate_file(rel: str, data: Mapping[str, Any], errors: list[str]) -> None:
    class_feature_records = collect_class_feature_records(rel, data, errors)
    subclass_feature_records = collect_subclass_feature_records(rel, data, errors)
    item_records = collect_named_items(data)

    for index, item in enumerate(data.get("item", [])):
        if not isinstance(item, Mapping):
            add_error(
                errors,
                rel,
                f"item[{index}]",
                "PM-ITEM-TYPE",
                str(item),
                "object",
                "item.structure",
            )
            continue

        validate_item_wondrous_type(rel, "item", index, item, errors)
        validate_item_attached_spells(rel, "item", index, item, errors)
        validate_item_charge_mechanics(rel, "item", index, item, errors)
        validate_item_bonus_fields(rel, "item", index, item, errors)
        validate_item_defenses(rel, "item", index, item, errors)

    for index, cls in enumerate(data.get("class", [])):
        if not isinstance(cls, Mapping):
            add_error(
                errors,
                rel,
                f"class[{index}]",
                "PM-CHAR-ENTITY-TYPE",
                str(cls),
                "object",
                "character-option.structure",
            )
            continue

        label = f"class[{index}:{cls.get('name', 'unnamed')!r}]"
        validate_class_feature_item_grants(
            cls,
            label,
            class_feature_records,
            item_records,
            errors,
        )
        validate_option_blocks(rel, label, cls, errors)
        validate_character_spellcasting_additional_spells(
            rel,
            label,
            cls,
            False,
            class_feature_records,
            subclass_feature_records,
            errors,
        )

    for index, subclass in enumerate(data.get("subclass", [])):
        if not isinstance(subclass, Mapping):
            add_error(
                errors,
                rel,
                f"subclass[{index}]",
                "PM-CHAR-ENTITY-TYPE",
                str(subclass),
                "object",
                "character-option.structure",
            )
            continue

        label = f"subclass[{index}:{subclass.get('name', 'unnamed')!r}]"
        validate_option_blocks(rel, label, subclass, errors)
        validate_character_spellcasting_additional_spells(
            rel,
            label,
            subclass,
            True,
            class_feature_records,
            subclass_feature_records,
            errors,
        )

    for bucket in ("race", "classFeature", "subclassFeature", "feat", "optionalfeature", "background"):
        for index, entity in enumerate(data.get(bucket, [])):
            if not isinstance(entity, Mapping):
                continue
            validate_option_blocks(
                rel,
                f"{bucket}[{index}:{entity.get('name', 'unnamed')!r}]",
                entity,
                errors,
            )


def validate_character_spellcasting_additional_spells(
    file_path: str,
    entity_label: str,
    entity: Mapping[str, Any],
    is_subclass: bool,
    class_feature_records: Mapping[tuple[str, str, str, int, str], Mapping[str, Any]],
    subclass_feature_records: Mapping[
        tuple[str, str, str, str, str, int, str],
        Mapping[str, Any],
    ],
    errors: list[str],
) -> None:
    local_errors: list[str] = []
    validate_character_spellcasting_additional_spells_foundry(
        entity,
        entity_label,
        is_subclass,
        class_feature_records,
        subclass_feature_records,
        local_errors,
    )

    for message in local_errors:
        normalized = message.lower()
        if ".additionalspells" in normalized:
            add_error(
                errors,
                file_path,
                entity_label,
                "PM-CHAR-ADDITIONAL-SPELLS",
                message,
                "additionalSpells matching fixed spell grants in spellcasting prose",
                "character-option.spellcasting-additional-spells",
            )
            continue

        if ".casterprogression" in normalized:
            add_error(
                errors,
                file_path,
                entity_label,
                "PM-CHAR-SPELLCASTING-PROGRESSION",
                message,
                "casterProgression when spellcasting progression fields exist",
                "character-option.spellcasting-progression",
            )
            continue

        # Preserve unmatched messages as generic prose-mechanics failures for review.
        errors.append(f"{file_path}:{entity_label}: {message}")


def run_validation(root: Path) -> tuple[int, list[str]]:
    if not root.exists() or not root.is_dir():
        return 1, [f"Prose-to-mechanics validation failed: root '{root}' is not a directory"]

    paths = list(iter_content_json_files(root))
    if not paths:
        return 1, [f"Prose-to-mechanics validation failed: no content files discovered under {root}"]

    errors: list[str] = []
    data_by_path: dict[str, Mapping[str, Any]] = {}

    for path in paths:
        rel = rel_path(path, root)
        try:
            data_by_path[rel] = load_json(path)
        except (OSError, json.JSONDecodeError, TypeError) as err:
            errors.append(f"{rel}: failed to load JSON: {err}")

    for rel, data in sorted(data_by_path.items(), key=lambda item: item[0]):
        validate_file(rel, data, errors)

    if errors:
        return 1, errors

    return 0, []


def main() -> int:
    args = parse_args()
    code, errors = run_validation(args.root)
    if code:
        print("Prose-to-mechanics validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return code

    print(f"Prose-to-mechanics validation passed: {len(list(iter_content_json_files(args.root)))} content file(s) scanned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
