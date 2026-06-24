#!/usr/bin/env python3
"""Validate Plutonium linked-entity references inside repository content."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

from plutonium_content import iter_content_json_files

ROOT_DIR = Path(__file__).resolve().parents[1]
INLINE_REF_RE = re.compile(r"\{@(?P<tag>spell|item) (?P<body>[^}]+)\}")


class LinkValidationError(RuntimeError):
    pass


def load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, Mapping):
        raise LinkValidationError(f"{path.relative_to(ROOT_DIR)}: top-level JSON is not an object")
    return data


def walk_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from walk_strings(item)
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from walk_strings(item)


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


def class_feature_key(entry: Mapping[str, Any], label: str, errors: list[str]) -> tuple[str, str, str, int, str] | None:
    name = entry.get("name")
    class_name = entry.get("className")
    class_source = entry.get("classSource")
    source = entry.get("source")
    level = parse_int(entry.get("level"), f"{label}.level", errors)
    required = {
        "name": name,
        "className": class_name,
        "classSource": class_source,
        "source": source,
    }
    for key, value in required.items():
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}.{key}: expected non-empty string, got {value!r}")
    if level is None or any(not isinstance(value, str) or not value.strip() for value in required.values()):
        return None
    return (name, class_name, class_source, level, source)


def subclass_feature_key(entry: Mapping[str, Any], label: str, errors: list[str]) -> tuple[str, str, str, str, str, int, str] | None:
    name = entry.get("name")
    class_name = entry.get("className")
    class_source = entry.get("classSource")
    subclass_short_name = entry.get("subclassShortName")
    subclass_source = entry.get("subclassSource")
    source = entry.get("source")
    level = parse_int(entry.get("level"), f"{label}.level", errors)
    required = {
        "name": name,
        "className": class_name,
        "classSource": class_source,
        "subclassShortName": subclass_short_name,
        "subclassSource": subclass_source,
        "source": source,
    }
    for key, value in required.items():
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}.{key}: expected non-empty string, got {value!r}")
    if level is None or any(not isinstance(value, str) or not value.strip() for value in required.values()):
        return None
    return (name, class_name, class_source, subclass_short_name, subclass_source, level, source)


def parse_class_feature_ref(value: str, label: str, errors: list[str]) -> tuple[str, str, str, int, str] | None:
    parts = value.split("|")
    if len(parts) not in {4, 5}:
        errors.append(f"{label}: class feature ref must have 4 or 5 pipe-delimited parts, got {len(parts)}: {value!r}")
        return None
    name, class_name, class_source, level_raw = parts[:4]
    source = parts[4] if len(parts) == 5 else class_source
    level = parse_int(level_raw, f"{label}.level", errors)
    required = [name, class_name, class_source, source]
    if level is None or any(not item.strip() for item in required):
        errors.append(f"{label}: class feature ref contains an empty required field: {value!r}")
        return None
    return (name, class_name, class_source, level, source)


def parse_subclass_feature_ref(value: str, label: str, errors: list[str]) -> tuple[str, str, str, str, str, int, str] | None:
    parts = value.split("|")
    if len(parts) != 7:
        errors.append(f"{label}: subclass feature ref must have 7 pipe-delimited parts, got {len(parts)}: {value!r}")
        return None
    name, class_name, class_source, subclass_short_name, subclass_source, level_raw, source = parts
    level = parse_int(level_raw, f"{label}.level", errors)
    required = [name, class_name, class_source, subclass_short_name, subclass_source, source]
    if level is None or any(not item.strip() for item in required):
        errors.append(f"{label}: subclass feature ref contains an empty required field: {value!r}")
        return None
    return (name, class_name, class_source, subclass_short_name, subclass_source, level, source)


def get_class_feature_ref(value: Any, label: str, errors: list[str]) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        ref = value.get("classFeature")
        if isinstance(ref, str):
            return ref
        errors.append(f"{label}: class feature object missing string 'classFeature' value")
        return None
    errors.append(f"{label}: class feature ref must be a string or object, got {type(value).__name__}")
    return None


def validate_inline_refs(
    data_by_path: Mapping[str, Mapping[str, Any]],
    local_entities: Mapping[tuple[str, str, str], str],
    errors: list[str],
) -> None:
    for rel, data in data_by_path.items():
        for text in walk_strings(data):
            for match in INLINE_REF_RE.finditer(text):
                tag = match.group("tag")
                body = match.group("body")
                parts = body.split("|")
                name = parts[0].strip()
                source = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
                if source != "VeiledOmens":
                    continue
                key = (tag, name, source)
                if key not in local_entities:
                    errors.append(f"{rel}: inline {{@{tag} {body}}} references missing local {tag} entity")


def validate(data_by_path: Mapping[str, Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    class_features: set[tuple[str, str, str, int, str]] = set()
    subclass_features: set[tuple[str, str, str, str, str, int, str]] = set()
    local_entities: dict[tuple[str, str, str], str] = {}

    for rel, data in data_by_path.items():
        for prop in ("spell", "item"):
            for index, entry in enumerate(data.get(prop, [])):
                if not isinstance(entry, Mapping):
                    errors.append(f"{rel}.{prop}[{index}]: expected object")
                    continue
                name = entry.get("name")
                source = entry.get("source")
                if isinstance(name, str) and isinstance(source, str):
                    local_entities[(prop, name, source)] = rel

        for index, entry in enumerate(data.get("classFeature", [])):
            if not isinstance(entry, Mapping):
                errors.append(f"{rel}.classFeature[{index}]: expected object")
                continue
            key = class_feature_key(entry, f"{rel}.classFeature[{index}]", errors)
            if key is not None:
                if key in class_features:
                    errors.append(f"{rel}.classFeature[{index}]: duplicate class feature entity key {key!r}")
                class_features.add(key)

        for index, entry in enumerate(data.get("subclassFeature", [])):
            if not isinstance(entry, Mapping):
                errors.append(f"{rel}.subclassFeature[{index}]: expected object")
                continue
            key = subclass_feature_key(entry, f"{rel}.subclassFeature[{index}]", errors)
            if key is not None:
                if key in subclass_features:
                    errors.append(f"{rel}.subclassFeature[{index}]: duplicate subclass feature entity key {key!r}")
                subclass_features.add(key)

    for rel, data in data_by_path.items():
        for class_index, cls in enumerate(data.get("class", [])):
            if not isinstance(cls, Mapping):
                errors.append(f"{rel}.class[{class_index}]: expected object")
                continue
            class_name = cls.get("name", f"class[{class_index}]")
            for ref_index, raw_ref in enumerate(cls.get("classFeatures", [])):
                label = f"{rel}.class[{class_index}:{class_name!r}].classFeatures[{ref_index}]"
                ref = get_class_feature_ref(raw_ref, label, errors)
                if ref is None:
                    continue
                key = parse_class_feature_ref(ref, label, errors)
                if key is not None and key not in class_features:
                    errors.append(f"{label}: missing classFeature entity for {key!r}")

        for subclass_index, subclass in enumerate(data.get("subclass", [])):
            if not isinstance(subclass, Mapping):
                errors.append(f"{rel}.subclass[{subclass_index}]: expected object")
                continue
            subclass_name = subclass.get("name", f"subclass[{subclass_index}]")
            for ref_index, ref in enumerate(subclass.get("subclassFeatures", [])):
                label = f"{rel}.subclass[{subclass_index}:{subclass_name!r}].subclassFeatures[{ref_index}]"
                if not isinstance(ref, str):
                    errors.append(f"{label}: subclass feature ref must be a string")
                    continue
                key = parse_subclass_feature_ref(ref, label, errors)
                if key is not None and key not in subclass_features:
                    errors.append(f"{label}: missing subclassFeature entity for {key!r}")

    validate_inline_refs(data_by_path, local_entities, errors)
    return errors


def main() -> int:
    try:
        data_by_path = {
            path.relative_to(ROOT_DIR).as_posix(): load_json(path)
            for path in iter_content_json_files(ROOT_DIR)
        }
    except (json.JSONDecodeError, OSError, LinkValidationError) as err:
        print(f"Plutonium link validation failed while loading content: {err}", file=sys.stderr)
        return 1

    errors = validate(data_by_path)
    if errors:
        print("Plutonium link validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Plutonium link validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
