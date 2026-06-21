#!/usr/bin/env python3
"""Generate and optionally validate Plutonium index files for this repository."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, DefaultDict, Dict, Iterable, Mapping, MutableMapping

ROOT_DIR = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT_DIR / "_generated"
INDEX_FILES = (
    "index-sources.json",
    "index-props.json",
    "index-meta.json",
    "index-timestamps.json",
)

SKIP_DIRS = {".git", ".mypy_cache", ".venv", "node_modules", ".github"}
TOP_LEVEL_DIRS = {
    "race",
    "subrace",
    "subraces",
    "class",
    "classes",
    "classFeature",
    "subclass",
    "subclasses",
    "feat",
    "optionalfeature",
    "reward",
    "action",
    "monster",
    "vehicle",
    "vehicleUpgrade",
    "deck",
    "card",
    "table",
    "variantrule",
    "adventure",
    "book",
    "background",
    "condition",
    "disease",
    "status",
    "deity",
    "language",
    "recipe",
    "trap",
    "hazard",
    "psionic",
    "cult",
    "supernaturalGift",
    "object",
    "bastion",
    "item",
}


class IndexGenerationError(RuntimeError):
    pass


def is_skippable(path: Path) -> bool:
    rel_parts = path.relative_to(ROOT_DIR).parts
    return path.name in INDEX_FILES or any(part in SKIP_DIRS for part in rel_parts)


def iter_content_files() -> Iterable[Path]:
    for path in ROOT_DIR.rglob("*.json"):
        if is_skippable(path):
            continue

        rel = path.relative_to(ROOT_DIR)
        if not rel.parts:
            continue

        top = rel.parts[0]
        if top in {"schemas", "tools", "_generated", "img"}:
            continue

        if top not in TOP_LEVEL_DIRS:
            # Keep generation focused on content directories.
            continue

        yield path


def load_json(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, Mapping):
        raise IndexGenerationError(f"{path}: top-level JSON is not an object")
    return data


def get_int(value: Any, default: int) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return default


def build_indexes() -> Dict[str, Any]:
    source_to_file: Dict[str, str] = {}
    prop_to_files: DefaultDict[str, Dict[str, str]] = defaultdict(dict)
    file_meta: Dict[str, Dict[str, Any]] = {}
    file_timestamps: Dict[str, Dict[str, int]] = {}
    has_content_files = False

    for path in iter_content_files():
        has_content_files = True
        rel = path.relative_to(ROOT_DIR).as_posix()
        data = load_json(path)

        meta = data.get("_meta")
        if not isinstance(meta, Mapping):
            raise IndexGenerationError(f"{rel}: missing or invalid _meta object")

        sources = meta.get("sources")
        if not isinstance(sources, list) or not sources:
            raise IndexGenerationError(f"{rel}: missing or empty _meta.sources")

        top_level_props = [
            key
            for key, value in data.items()
            if key != "_meta" and isinstance(value, list)
        ]
        if not top_level_props:
            raise IndexGenerationError(f"{rel}: no top-level content arrays found")

        top_dir = rel.split("/", 1)[0]
        for prop in top_level_props:
            prop_to_files[prop][rel] = top_dir

        meta_status = meta.get("status")
        meta_status_value = "ready"
        if isinstance(meta_status, str) and meta_status.strip():
            meta_status_value = meta_status.strip()

        meta_edition = meta.get("edition")
        meta_edition_value = 1
        if meta_edition == "classic":
            meta_edition_value = 0

        date_added = get_int(meta.get("dateAdded"), 1700000000)
        date_modified = get_int(meta.get("dateLastModified"), date_added)
        date_published = get_int(meta.get("datePublished"), date_modified)
        file_timestamps[rel] = {
            "a": date_added,
            "m": date_modified,
            "p": date_published,
        }
        filename = path.name
        if filename in file_meta:
            raise IndexGenerationError(f"{rel}: filename '{filename}' duplicates another content filename")

        source_ids: set[str] = set()
        for source in sources:
            if not isinstance(source, Mapping):
                raise IndexGenerationError(f"{rel}: _meta.sources entry is not an object")

            source_id = source.get("json")
            if not isinstance(source_id, str) or not source_id.strip():
                raise IndexGenerationError(f"{rel}: _meta.sources entry missing json id")
            source_id = source_id.strip()

            existing_path = source_to_file.get(source_id)
            if existing_path is None:
                source_to_file[source_id] = rel
            elif existing_path != rel:
                raise IndexGenerationError(
                    f"{rel}: source '{source_id}' already mapped to '{existing_path}' "
                    f"and cannot be remapped to '{rel}'"
                )
            source_ids.add(source_id)

        file_meta[filename] = {
            "n": sorted(source_ids),
            "s": meta_status_value,
            "e": meta_edition_value,
        }

    if not has_content_files:
        raise IndexGenerationError("No content files were discovered under content directories")

    normalized_props = {k: v for k, v in sorted(prop_to_files.items())}
    for path_map in normalized_props.values():
        if not path_map:
            continue
        # Sort keys for deterministic output while preserving object-values.
        normalized_paths = {k: path_map[k] for k in sorted(path_map)}
        path_map.clear()
        path_map.update(normalized_paths)

    return {
        "index-sources.json": source_to_file,
        "index-props.json": normalized_props,
        "index-meta.json": file_meta,
        "index-timestamps.json": file_timestamps,
    }


def write_if_needed(path: Path, expected: MutableMapping[str, Any], check_mode: bool) -> bool:
    existing: Optional[Mapping[str, Any]] = None
    if path.exists():
        with path.open("r", encoding="utf-8") as file:
            existing = json.load(file)

    if isinstance(existing, Mapping) and isinstance(expected, Mapping):
        existing_cmp = dict(existing)
        expected_cmp = dict(expected)
        existing_cmp.pop("generatedAt", None)
        expected_cmp.pop("generatedAt", None)
        if existing_cmp == expected_cmp:
            return False

    if existing == expected:
        return False

    if check_mode:
        return True

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(expected, file, indent=2, ensure_ascii=True, sort_keys=True)
        file.write("\n")
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate that generated index files are already up to date",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        indexes = build_indexes()
    except IndexGenerationError as err:
        print(f"Generator failed: {err}", file=sys.stderr)
        return 1

    changed = False
    for filename in INDEX_FILES:
        path = GENERATED_DIR / filename
        expected = indexes[filename]
        if write_if_needed(path, expected, args.check):
            changed = True
            if args.check:
                print(f"[check] mismatch: {path.relative_to(ROOT_DIR)}")

    if args.check:
        if changed:
            print("Plutonium index check failed: regeneration required.", file=sys.stderr)
            return 1
        print("Plutonium index check passed.")
        return 0

    if changed:
        print("Plutonium indexes generated.")
    else:
        print("Plutonium indexes already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
