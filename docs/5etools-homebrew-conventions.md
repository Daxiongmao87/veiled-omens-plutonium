# 5etools Homebrew Conventions (Plutonium)

This document records the upstream 5etools homebrew conventions this repository follows and the local rules needed for Plutonium imports.

## Reference Sources

- TheGiddyLimit/homebrew repository: `https://github.com/TheGiddyLimit/homebrew`
- TheGiddyLimit/homebrew README and conventions: `https://raw.githubusercontent.com/TheGiddyLimit/homebrew/master/README.md`
- TheGiddyLimit/homebrew root tree: `https://github.com/TheGiddyLimit/homebrew/tree/master`
- TheGiddyLimit/homebrew `_generated/index-props.json`: `https://raw.githubusercontent.com/TheGiddyLimit/homebrew/master/_generated/index-props.json`
- Upstream mixed collection example: `collection/Matthew Mercer; TalDorei Campaign Guide.json`
- TheGiddyLimit/homebrew image repository: `https://github.com/TheGiddyLimit/homebrew-img`
- Upstream schemas: `https://github.com/TheGiddyLimit/5etools-utils/tree/master/schema/brew`
- 5etools homebrew helpers: `https://wiki.tercept.net/en/5eTools/HelpPages/makebrew`

## Adopted Upstream Rules

- Homebrew JSON files are compatible with 5etools and are loaded through the 5etools Brew Manager or by direct raw JSON.
- Repository content is organized by top-level package/content directories such as `collection`, `race`, `class`, `subclass`, `feat`, `optionalfeature`, `spell`, `item`, and `background`.
- `collection/` is used when one source material package spans multiple content types.
- Type-specific directories are used when the source package is a single-type package or a true type-specific collection.
- Filenames identify the source material/package. Upstream contribution filenames use `Author Name; Homebrew Name.json`.
- `_meta.sources[].json` values are unique source IDs across homebrew.
- Source IDs model source material/package identity, not individual mechanical options.
- Content authors belong in source `author` / `authors` fields; conversion credit belongs in `convertedBy`.
- File metadata includes `dateAdded` as a Unix timestamp in seconds.

## Local Rules For This Repository

- Current canonical source package: `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`
- Current canonical source ID: `VeiledOmens`
- Current canonical source author: `Patrick Richardson`
- Current package images live under `img/VeiledOmens/icons/` and are referenced through raw GitHub URLs.
- Current Veiled Omens player-facing content remains one collection package/source unless a future source material is a separate publication/package.
- Individual classes, subclasses, species, spells, items, and features inside the current package must not receive separate source IDs.
- Plutonium URL Source fields need raw JSON files. Do not use GitHub HTML pages or raw GitHub directory roots as URL Sources.
- Plutonium Base Homebrew Repository URL uses a branch root in the form `https://raw.githubusercontent.com/<user>/<repo>/<branch>/`.

## Foundry Advancement Source Data

- Plutonium's bundled 5etools source data uses race entries, class feature records, subclass feature records, and references as the source-data shape for feature grants.
- Normal class and subclass feature references use 5etools string refs. Class feature objects are reserved for reference metadata such as `gainSubclassFeature`, `gainSubclassFeatureHasContent`, or `tableDisplayName`.
- Class tool-proficiency grants use strings, including free-choice strings like `one type of {@item artisan's tools|PHB} of your choice`; class tool arrays do not use object `choose` blocks.
- Bundled Plutonium side-data uses `advancement` rows for non-item values such as `ScaleValue`; it does not source-author `ItemGrant` rows for class, subclass, or race feature grants.
- Do not add source-authored `ItemGrant` rows for feature grants. Verify those grants through the real Plutonium actor import path, where the importer creates actor-owned `ItemGrant` rows from the concrete feature records.

Reference audit evidence from the 2026-06-24 TheGiddyLimit/homebrew clone:

- 1,294 JSON files parsed with zero JSON errors.
- `classFeatures`: 6,526 string refs and 1,527 object refs; object refs carried metadata such as `gainSubclassFeature` or `tableDisplayName`.
- `subclassFeatures`: 20,585 string refs, zero object refs.
- Class `startingProficiencies.tools` and `multiclassing.proficienciesGained.tools`: 278 string entries, zero object entries.
- `foundryAdvancement`: 194 rows, all `ScaleValue`; zero source-authored `ItemGrant` rows.
- Items: 6,884 `wondrous: true` entries and zero `type: "WONDROUS"` entries.

## Directory To Top-Level Property Mapping

- `collection/` -> mixed top-level arrays from one source package
- `race/` -> `race`
- `subrace/` -> `subrace`
- `class/` -> `class`
- `subclass/` -> `subclass`
- `feat/` -> `feat`
- `optionalfeature/` -> `optionalfeature`
- `spell/` -> `spell`
- `item/` -> `item`
- `baseitem/` -> `baseitem`
- `magicvariant/` -> `magicvariant`
- `background/` -> `background`
- `adventure/` -> `adventure`
- `book/` -> `book`
- `monster/` -> `monster`
- Other object-specific directories map to matching top-level array keys in the same pattern, including `action`, `reward`, `vehicle`, `object`, `deity`, `language`, `trap`, `hazard`, `cult`, `boon`, `condition`, `disease`, `variantrule`, `table`, and `psionic`.

## Source Inventory Gate

Before accepting any source organization change:

1. Inspect the source material scope.
2. Classify whether the content is one mixed package, one single-type package, a true type-specific collection, or a separate publication/package.
3. Map each `_meta.sources[].json` value to exactly one package file.
4. Confirm source IDs are not split by individual mechanical options inside the same source material.
5. Regenerate indexes.
6. Run `python3 tools/validate-content-json.py` to parse every repository JSON file and check every content JSON file.
7. Run the datasource validator.
8. Run the Plutonium link validator.
9. Run stale-reference scans for removed source IDs and removed file paths.

## Commit-Time Validation

The tracked hook at `.githooks/pre-commit` enforces the non-mutating validation suite before every commit:

```bash
git config core.hooksPath .githooks
```

The hook runs:

```bash
python3 tools/validate-content-json.py
python3 tools/generate-plutonium-indexes.py --check
python3 tools/validate-plutonium-datasource.py
python3 tools/validate-plutonium-links.py
```

`tools/validate-content-json.py` uses the shared content discovery helper in `tools/plutonium_content.py`, so generator and validator tooling use the same definition of content JSON files.

## `_generated` Index Workflow

`_generated/` files are expected to be present for a valid Plutonium datasource:

- `_generated/index-sources.json`
- `_generated/index-props.json`
- `_generated/index-meta.json`
- `_generated/index-timestamps.json`

`python3 tools/generate-plutonium-indexes.py` regenerates these files.

`python3 tools/generate-plutonium-indexes.py --check` verifies index consistency.

`python3 tools/validate-content-json.py` parses every repository JSON file and checks every repository content JSON file.

`python3 tools/validate-plutonium-datasource.py` validates the generated datasource maps against repository content.

`python3 tools/validate-plutonium-links.py` validates Plutonium linked-entity references such as class feature, subclass feature, spell, and item references.

## Asset Transplant Workflow

Use the workflow below for any Foundry-path image references that originate from a local world directory:

1. Locate the Foundry-relative path in source objects, such as `worlds/the-star-of-wintercrest/assets/images/Vaetyr_3.png`.
2. Download from the Foundry base URL: `https://foundry.instance3.astralkeep.com/worlds/the-star-of-wintercrest/assets/images/<image>.png`.
3. Save each image into the package asset directory, currently `img/VeiledOmens/icons/`.
4. Reference the image from repo JSON via raw GitHub URL, for example `https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/img/VeiledOmens/icons/vaetyr.png`.
5. For Foundry paths that are global module/system references, such as `modules/plutonium/...` or `icons/...`, keep external references when the dependency is intentionally external and valid at runtime.
6. Do not create packed-name aliases unless the source JSON contains that path and the server serves it.

## Distinction: World Paths Vs External Paths

- Custom world paths must be fetched and transplanted into the repo when used in this datasource.
- Core/module paths remain external when the dependency is stable runtime content.
