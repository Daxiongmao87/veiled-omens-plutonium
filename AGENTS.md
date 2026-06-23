# Veiled Omens Plutonium Instructions

## Source-Package Convention

- Follow TheGiddyLimit/homebrew package/source conventions.
- Source IDs model source material/package identity, not individual classes, subclasses, species, spells, items, or features.
- Current canonical package file: `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`
- Current canonical source ID: `VeiledOmens`
- Current canonical source author: `Patrick Richardson`
- Current Veiled Omens player-facing material is one mixed collection package/source unless a future source material is a separate publication/package.
- Do not split the current Veiled Omens package into source IDs for individual mechanical options.
- Use `collection/` when one source material package spans multiple content types.
- Use type-specific directories when the source package is a single-type package or a true type-specific collection.

## Required Validation

Before reporting source organization work complete:

1. Regenerate indexes with `python3 tools/generate-plutonium-indexes.py`.
2. Run `python3 tools/generate-plutonium-indexes.py --check`.
3. Run `python3 tools/validate-plutonium-datasource.py`.
4. Parse every repository JSON file.
5. Audit `_generated/index-sources.json` for one source ID per source package.
6. Audit `_generated/index-props.json` for correct content-directory mappings.
7. Run stale-reference scans for removed source IDs and removed package paths.

## Assets

- Current package assets live under `img/VeiledOmens/icons/`.
- Active JSON must reference package assets through raw GitHub URLs that include `/img/VeiledOmens/icons/`.
