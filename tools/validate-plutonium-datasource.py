#!/usr/bin/env python3
"""Validate generated Plutonium datasource indexes against repository content."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Mapping, Set

from plutonium_content import iter_content_json_files

ROOT_DIR = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT_DIR / "_generated"
REQUIRED_INDEX_FILES = {
    "index-sources.json",
    "index-props.json",
    "index-meta.json",
    "index-timestamps.json",
}


def parse_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def collect_repo_content() -> tuple[
    dict[str, Mapping[str, Any]],
    Set[str],
    dict[str, Set[str]],
    dict[str, list[str]],
    dict[str, dict[str, int]],
    dict[str, str],
]:
    """Return content by path, sources present, per-file props, per-file meta, and timestamps."""
    by_path: dict[str, Mapping[str, Any]] = {}
    source_ids: Set[str] = set()
    file_to_props: dict[str, Set[str]] = {}
    file_to_meta: dict[str, list[str]] = {}
    file_timestamps: dict[str, dict[str, int]] = {}
    file_to_dir: dict[str, str] = {}
    seen_filenames: Set[str] = set()

    for path in iter_content_json_files(ROOT_DIR):
        rel = path.relative_to(ROOT_DIR).as_posix()
        data = parse_json(path)
        if not isinstance(data, Mapping):
            raise ValueError(f"{rel}: top-level JSON is not an object")

        meta = data.get("_meta")
        if not isinstance(meta, Mapping):
            raise ValueError(f"{rel}: missing _meta")

        sources = meta.get("sources")
        if not isinstance(sources, list):
            raise ValueError(f"{rel}: _meta.sources must be an array")

        props = {
            key
            for key, value in data.items()
            if key != "_meta" and isinstance(value, list)
        }
        if not props:
            raise ValueError(f"{rel}: no top-level content arrays found")

        by_path[rel] = data
        file_to_props[rel] = props

        for source in sources:
            if not isinstance(source, Mapping):
                raise ValueError(f"{rel}: _meta.sources entry is not an object")
            source_id = source.get("json")
            if not isinstance(source_id, str) or not source_id.strip():
                raise ValueError(f"{rel}: source missing json id")
            source_ids.add(source_id.strip())

        status = meta.get("status")
        status_value = status if isinstance(status, str) and status.strip() else "ready"

        edition = meta.get("edition")
        edition_value = 0 if edition == "classic" else 1

        date_added = meta.get("dateAdded")
        date_modified = meta.get("dateLastModified")
        date_published = meta.get("datePublished")
        for value_name, value in (("dateAdded", date_added), ("dateLastModified", date_modified), ("datePublished", date_published)):
            if isinstance(value, bool) or (isinstance(value, float) and not value.is_integer()):
                raise ValueError(f"{rel}: _meta[{value_name}] must be an integer")

        def get_int(value: Any, default: int) -> int:
            if isinstance(value, int):
                return value
            if value is None:
                return default
            if isinstance(value, float):
                return int(value)
            return default

        file_timestamps[rel] = {
            "a": get_int(date_added, 1700000000),
            "m": get_int(date_modified, get_int(date_added, 1700000000)),
            "p": get_int(date_published, get_int(date_modified, get_int(date_added, 1700000000))),
        }

        filename = path.name
        if filename in seen_filenames:
            raise ValueError(f"{rel}: duplicate filename '{filename}' across content files")
        seen_filenames.add(filename)

        source_ids_for_file = []
        for source in sources:
            if not isinstance(source, Mapping):
                raise ValueError(f"{rel}: _meta.sources entry is not an object")
            source_id = source.get("json")
            if not isinstance(source_id, str) or not source_id.strip():
                raise ValueError(f"{rel}: source missing json id")
            source_ids_for_file.append(source_id.strip())

        file_to_meta[filename] = {
            "n": sorted(set(source_ids_for_file)),
            "s": status_value.strip(),
            "e": edition_value,
        }
        file_to_dir[rel] = rel.split("/", 1)[0]

    return (
        by_path,
        source_ids,
        {k: set(v) for k, v in file_to_props.items()},
        file_to_meta,
        file_timestamps,
        file_to_dir,
    )


def ensure(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate() -> int:
    errors: list[str] = []

    for name in REQUIRED_INDEX_FILES:
        path = GENERATED_DIR / name
        if not path.exists():
            errors.append(f"Missing required index file: {path.relative_to(ROOT_DIR)}")

    if errors:
        for message in errors:
            print(message, file=sys.stderr)
        return 1

    try:
        index_sources = parse_json(GENERATED_DIR / "index-sources.json")
        index_props = parse_json(GENERATED_DIR / "index-props.json")
        index_meta = parse_json(GENERATED_DIR / "index-meta.json")
        index_timestamps = parse_json(GENERATED_DIR / "index-timestamps.json")
        (
            content_files,
            source_ids,
            file_to_props,
            expected_file_meta,
            expected_timestamps,
            file_to_dir,
        ) = collect_repo_content()
    except (json.JSONDecodeError, ValueError, OSError) as err:
        print(f"Validation failed while parsing JSON: {err}", file=sys.stderr)
        return 1

    if not isinstance(index_sources, Mapping):
        errors.append("index-sources.json must be an object")
    if isinstance(index_sources, Mapping):
        if "generatedAt" in index_sources:
            errors.append("index-sources.json must not use top-level generatedAt")
        if "sources" in index_sources:
            errors.append("index-sources.json must be a direct source-id map, not wrapped in 'sources'")

    if not isinstance(index_props, Mapping):
        errors.append("index-props.json must be an object")
    if isinstance(index_props, Mapping):
        if "generatedAt" in index_props:
            errors.append("index-props.json must not use top-level generatedAt")
        if "props" in index_props:
            errors.append("index-props.json must be a direct prop->path map, not wrapped in 'props'")

    if not isinstance(index_meta, Mapping):
        errors.append("index-meta.json must be an object")
    if isinstance(index_meta, Mapping):
        if "generatedAt" in index_meta:
            errors.append("index-meta.json must not use top-level generatedAt")
        if "sources" in index_meta:
            errors.append("index-meta.json must be a direct filename-keyed object, not wrapped in 'sources'")

    if not isinstance(index_timestamps, Mapping):
        errors.append("index-timestamps.json must be an object")
    if isinstance(index_timestamps, Mapping) and "generatedAt" in index_timestamps:
        errors.append("index-timestamps.json should not contain generatedAt wrapper key")

    if errors:
        for message in errors:
            print(message, file=sys.stderr)
        return 1

    src_map = index_sources
    prop_map = index_props
    meta_map = index_meta
    ts_map = index_timestamps

    def is_invalid_path(path: str) -> bool:
        return path == "index.json" or path.startswith("index.json/")

    def ensure_keyed_mapping(value: Any, name: str) -> bool:
        if not isinstance(value, Mapping):
            ensure(False, f"{name} must map keys to values", errors)
            return False
        return True

    if ensure_keyed_mapping(src_map, "index-sources.json"):
        for source_id, mapped_path in src_map.items():
            ensure(isinstance(mapped_path, str), f"index-sources entry '{source_id}' must be a string", errors)
            if isinstance(mapped_path, str):
                ensure(mapped_path in content_files, f"index-sources entry '{source_id}' maps to missing content file '{mapped_path}'", errors)
                ensure(not is_invalid_path(mapped_path), f"index-sources entry '{source_id}' must not map to '{mapped_path}'", errors)

    # all JSON files parse check already done by JSON parse stage.

    for source_id in sorted(source_ids):
        ensure(source_id in src_map, f"source '{source_id}' is missing from index-sources.json", errors)
    for source_id in src_map:
        if source_id not in source_ids:
            ensure(
                False,
                f"index-sources contains unknown source '{source_id}'",
                errors,
            )

    expected_props: Set[str] = set()
    for props in file_to_props.values():
        expected_props.update(props)
    ensure(set(prop_map.keys()) == expected_props, "index-props.json is missing or has extra top-level props", errors)

    if ensure_keyed_mapping(prop_map, "index-props.json"):
        for prop, path_to_dir in prop_map.items():
            ensure_keyed_mapping(path_to_dir, f"index-props[{prop}]")
            if not isinstance(path_to_dir, Mapping):
                continue
            for mapped_path, mapped_dir in path_to_dir.items():
                ensure(
                    isinstance(mapped_path, str),
                    f"index-props[{prop}] contains non-string path key",
                    errors,
                )
                if not isinstance(mapped_path, str):
                    continue
                ensure(mapped_path in content_files, f"index-props[{prop}] points to missing file '{mapped_path}'", errors)
                ensure(mapped_path not in file_to_dir or mapped_dir == file_to_dir[mapped_path], f"index-props[{prop}][{mapped_path}] must map to directory '{file_to_dir.get(mapped_path)}'", errors)
                ensure(not is_invalid_path(mapped_path), f"index-props[{prop}] contains invalid path '{mapped_path}'", errors)
                ensure(isinstance(mapped_dir, str), f"index-props[{prop}][{mapped_path}] must be a directory string", errors)
                if isinstance(mapped_dir, str):
                    ensure(mapped_dir == mapped_path.split("/", 1)[0], f"index-props[{prop}][{mapped_path}] must map to its top-level directory", errors)

    for rel_path, props in file_to_props.items():
        for prop in sorted(props):
            mapped = prop_map.get(prop)
            ensure(isinstance(mapped, Mapping), f"index-props missing prop '{prop}' as map", errors)
            if not isinstance(mapped, Mapping):
                continue
            ensure(
                rel_path in mapped,
                f"index-props missing '{rel_path}' for prop '{prop}'",
                errors,
            )

    ensure(set(ts_map.keys()) == set(expected_timestamps.keys()), "index-timestamps.json contains missing or extra content files", errors)
    if ensure_keyed_mapping(ts_map, "index-timestamps.json"):
        for rel_path, expected_ts in expected_timestamps.items():
            ensure(
                rel_path in ts_map,
                f"index-timestamps.json missing entry for '{rel_path}'",
                errors,
            )
            if rel_path not in ts_map:
                continue
            actual_ts = ts_map[rel_path]
            ensure(isinstance(actual_ts, Mapping), f"index-timestamps entry '{rel_path}' is not an object", errors)
            if not isinstance(actual_ts, Mapping):
                continue
            ensure(not is_invalid_path(rel_path), f"index-timestamps entry '{rel_path}' is invalid", errors)
            for field_name, value in (("a", expected_ts.get("a")), ("m", expected_ts.get("m")), ("p", expected_ts.get("p"))):
                ensure(field_name in actual_ts, f"index-timestamps[{rel_path}] missing '{field_name}'", errors)
                if field_name in actual_ts:
                    ensure(isinstance(actual_ts[field_name], int) and not isinstance(actual_ts[field_name], bool), f"index-timestamps[{rel_path}].{field_name} must be integer", errors)
                if isinstance(actual_ts.get(field_name), int):
                    ensure(actual_ts[field_name] == value, f"index-timestamps[{rel_path}].{field_name} must match _meta", errors)

    if ensure_keyed_mapping(meta_map, "index-meta.json"):
        ensure(
            set(meta_map.keys()) == set(expected_file_meta.keys()),
            "index-meta.json contains missing or extra filenames",
            errors,
        )
        for filename, expected_meta in expected_file_meta.items():
            actual_meta = meta_map.get(filename)
            ensure(
                isinstance(actual_meta, Mapping),
                f"index-meta entry '{filename}' is not an object",
                errors,
            )
            if not isinstance(actual_meta, Mapping):
                continue
            ensure(
                sorted(actual_meta.get("n", [])) == sorted(expected_meta["n"]),
                f"index-meta[{filename}].n must match _meta.sources",
                errors,
            )
            ensure(
                actual_meta.get("s") == expected_meta["s"],
                f"index-meta[{filename}].s must be {expected_meta['s']}",
                errors,
            )
            ensure(
                actual_meta.get("e") == expected_meta["e"],
                f"index-meta[{filename}].e must be {expected_meta['e']}",
                errors,
            )
            ensure(isinstance(actual_meta.get("e"), int) and not isinstance(actual_meta.get("e"), bool), f"index-meta[{filename}].e must be integer", errors)

    # Documentation guidance check: remove remote root index.json contract language.
    dev_path = ROOT_DIR / "DEVELOPMENT.md"
    if dev_path.exists():
        dev = dev_path.read_text(encoding="utf-8")
        ensure(
            "Use index.json at the repository root" not in dev,
            "DEVELOPMENT.md still describes index.json as a root datasource contract",
            errors,
        )

    if errors:
        for message in errors:
            print(message, file=sys.stderr)
        return 1

    print("Plutonium datasource validation passed.")
    return 0


def main() -> int:
    return validate()


if __name__ == "__main__":
    sys.exit(main())
