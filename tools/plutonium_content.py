"""Shared content-file discovery for Plutonium repository tooling."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


CONTENT_DIRS = {
    "collection",
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

SKIP_DIRS = {".git", ".github", ".mypy_cache", ".venv", "__pycache__", "node_modules"}


def is_content_json_path(path: Path, root_dir: Path) -> bool:
    """Return true when a path is a repository content JSON file."""
    if path.suffix != ".json":
        return False

    rel = path.relative_to(root_dir)
    if not rel.parts:
        return False
    if any(part.startswith(".") or part in SKIP_DIRS for part in rel.parts):
        return False

    return rel.parts[0] in CONTENT_DIRS


def is_repository_json_path(path: Path, root_dir: Path) -> bool:
    """Return true when a path is a tracked-repository JSON candidate."""
    if path.suffix != ".json":
        return False

    rel = path.relative_to(root_dir)
    if not rel.parts:
        return False
    return not any(part.startswith(".") or part in SKIP_DIRS for part in rel.parts)


def iter_repository_json_files(root_dir: Path) -> Iterable[Path]:
    """Yield every non-hidden repository JSON file in deterministic order."""
    paths = (
        path
        for path in root_dir.rglob("*.json")
        if is_repository_json_path(path, root_dir)
    )
    yield from sorted(paths, key=lambda path: path.relative_to(root_dir).as_posix())


def iter_content_json_files(root_dir: Path) -> Iterable[Path]:
    """Yield every Plutonium content JSON file in deterministic order."""
    paths = (
        path
        for path in root_dir.rglob("*.json")
        if is_content_json_path(path, root_dir)
    )
    yield from sorted(paths, key=lambda path: path.relative_to(root_dir).as_posix())
