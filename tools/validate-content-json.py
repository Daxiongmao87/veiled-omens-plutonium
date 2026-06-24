#!/usr/bin/env python3
"""Validate every repository content JSON file."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping

from plutonium_content import is_content_json_path, iter_repository_json_files


ROOT_DIR = Path(__file__).resolve().parents[1]
WONDROUS_ITEM_TYPE_VALUES = {"wondrous", "wondrous item"}


def rel_path(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_content_file(path: Path, data: Any) -> list[str]:
    rel = rel_path(path)
    errors: list[str] = []

    if not isinstance(data, Mapping):
        return [f"{rel}: top-level JSON must be an object"]

    meta = data.get("_meta")
    if not isinstance(meta, Mapping):
        errors.append(f"{rel}: missing _meta object")
        source_ids: set[str] = set()
    else:
        sources = meta.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{rel}: _meta.sources must be a non-empty array")
            source_ids = set()
        else:
            source_ids = set()
            for index, source in enumerate(sources):
                if not isinstance(source, Mapping):
                    errors.append(f"{rel}: _meta.sources[{index}] must be an object")
                    continue
                source_id = source.get("json")
                if not isinstance(source_id, str) or not source_id.strip():
                    errors.append(f"{rel}: _meta.sources[{index}].json must be a non-empty string")
                    continue
                source_ids.add(source_id.strip())

    content_arrays = {
        key: value
        for key, value in data.items()
        if key != "_meta" and isinstance(value, list)
    }
    if not content_arrays:
        errors.append(f"{rel}: no top-level content arrays found")

    for prop, entries in content_arrays.items():
        for index, entry in enumerate(entries):
            label = f"{rel}.{prop}[{index}]"
            if not isinstance(entry, Mapping):
                errors.append(f"{label}: content entries must be objects")
                continue

            entry_source = entry.get("source")
            if not isinstance(entry_source, str) or not entry_source.strip():
                errors.append(f"{label}.source must be a non-empty string")
            elif source_ids and entry_source.strip() not in source_ids:
                errors.append(f"{label}.source '{entry_source}' is not declared in _meta.sources")

            entry_prop = entry.get("__prop")
            if entry_prop is not None and entry_prop != prop:
                errors.append(f"{label}.__prop must match top-level array '{prop}'")

            if prop == "item":
                errors.extend(validate_item_entry(label, entry))

    return errors


def validate_item_entry(label: str, entry: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []

    item_type = entry.get("type")
    if isinstance(item_type, str) and item_type.strip().lower() in WONDROUS_ITEM_TYPE_VALUES:
        errors.append(
            f"{label}.type must not be '{item_type}'; "
            "wondrous items follow reference convention by omitting type and setting wondrous=true"
        )

    wondrous = entry.get("wondrous")
    if wondrous is not None and not isinstance(wondrous, bool):
        errors.append(f"{label}.wondrous must be boolean when present")

    return errors


def main() -> int:
    paths = list(iter_repository_json_files(ROOT_DIR))
    errors: list[str] = []
    checked_content_count = 0

    if not paths:
        errors.append("No repository JSON files were discovered")

    for path in paths:
        try:
            data = load_json(path)
        except json.JSONDecodeError as err:
            errors.append(f"{rel_path(path)}: invalid JSON: {err}")
            continue
        except OSError as err:
            errors.append(f"{rel_path(path)}: could not read file: {err}")
            continue

        if is_content_json_path(path, ROOT_DIR):
            checked_content_count += 1
            errors.extend(validate_content_file(path, data))

    if checked_content_count == 0:
        errors.append("No content JSON files were discovered under content directories")

    if errors:
        print("Content JSON validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Content JSON validation passed: "
        f"{checked_content_count} content file(s) checked; {len(paths)} repository JSON file(s) parsed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
