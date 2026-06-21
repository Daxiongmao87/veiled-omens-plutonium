# 5etools Homebrew Conventions (Plutonium)

This document records the upstream 5etools homebrew conventions this repository follows and the local adaptations needed for Plutonium imports.

## Reference sources

- TheGiddyLimit/homebrew repository: `https://github.com/TheGiddyLimit/homebrew`
- TheGiddyLimit/homebrew README and conventions: `https://raw.githubusercontent.com/TheGiddyLimit/homebrew/master/README.md`
- TheGiddyLimit/homebrew root tree: `https://github.com/TheGiddyLimit/homebrew/tree/master`
- TheGiddyLimit/homebrew `_img` directory: `https://github.com/TheGiddyLimit/homebrew/tree/master/_img`
- TheGiddyLimit/homebrew image repository: `https://github.com/TheGiddyLimit/homebrew-img`
- Upstream schemas: `https://github.com/TheGiddyLimit/5etools-utils/tree/master/schema/brew`
- Main 5etools data reference: `https://github.com/5etools-mirror-3/5etools-src/tree/main/data`
- 5etools homebrew helpers: `https://wiki.tercept.net/en/5eTools/HelpPages/makebrew`

## Conventions adopted from upstream

Upstream homebrew conventions used here:

- Homebrew JSON files are compatible with 5etools and are loaded through the 5etools Brew Manager or by using raw JSON.
- The recommended creation path is to copy existing brews as templates and compare against main 5etools data.
- Repository content is organized by top-level content-type directories such as `race`, `class`, `subclass`, `feat`, `optionalfeature`, `spell`, `item`, and `background`.
- Files use tabs, LF line endings, and UTF-8 without BOM.
- Upstream contribution filenames use package/homebrew identity rather than a broad mechanical class bucket for single packages.
- `_meta.sources[].json` values are unique source IDs across homebrew.
- When a source URL is missing, use `https://github.com/TheGiddyLimit/homebrew` as the upstream source URL.
- Content authors belong in source `author` / `authors` fields; conversion credit belongs in `convertedBy`.
- File metadata includes `dateAdded` as a Unix timestamp in seconds.
- Images and similar assets belong in the upstream homebrew image repository, `https://github.com/TheGiddyLimit/homebrew-img`.

## Local adaptations for this repository

Patrick-directed local adaptations retained for this repo:

- Canonical species file remains:
  - `race/Veiled Omens; Species.json`
- Canonical single package subclass file:
  - `subclass/Veiled Omens; Occult Knight.json`
- Canonical file placement is content-class based. Do not use Foundry world export filenames as canonical repository filenames.
- Canonical images are stored in this repository under `img/icons/` and referenced via raw GitHub URLs.
- Content remains repository-owned where practical; image transplants are performed in-repo instead of re-pointing to foundry-only assets by default.
- Plutonium URL Source fields need raw JSON files. Do not use GitHub HTML pages or raw GitHub directory roots as URL Sources.
- Plutonium Base Homebrew Repository URL uses a branch root in the form `https://raw.githubusercontent.com/<user>/<repo>/<branch>`.
- For a single-package file, source identity in `_meta.sources[].json` should match package content identity (for example, `VeiledOmensOccultKnight` for `subclass/Veiled Omens; Occult Knight.json`).
- Broad package names like `Veiled Omens; Fighter Subclasses.json` are invalid for single-entry files.

## Content-type directory to top-level property mapping

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

## `_generated` index workflow

`_generated/` files are expected to be present for a valid Plutonium datasource:

- `_generated/index-sources.json`
- `_generated/index-props.json`
- `_generated/index-meta.json`
- `_generated/index-timestamps.json`

`python3 tools/generate-plutonium-indexes.py` regenerates these files.

- `python3 tools/generate-plutonium-indexes.py --check` verifies index consistency.

Naming and source-id conventions are validated against local behavior by checking matching examples in TheGiddyLimit/homebrew first, then re-running the local index checks and parser validation.

## Asset transplant workflow

Use the workflow below for any foundry-path image references that originate from a local world directory:

1. Locate the Foundry-relative path in source objects (for example, `worlds/the-star-of-wintercrest/assets/images/Vaetyr_3.png`).
2. Download from the Foundry base URL: `https://foundry.instance3.astralkeep.com/worlds/the-star-of-wintercrest/assets/images/<image>.png`.
3. Save each image into `img/icons/` using a repo-owned asset name.
4. Reference the image from repo JSON via raw GitHub URL (for example, `https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/img/icons/vaetyr.png`).
5. For Foundry paths that are global module/system references (for example, `modules/plutonium/...` or `icons/...` paths), do not automatically transplant; keep external references only if the dependency is intentionally external and valid at runtime.
6. Do not create packed-name aliases unless the source JSON contains that path and the server serves it. For the Vaetyr dossier, the source path is `Vaetyr_3.png`.

## Distinction: world paths vs external paths

- **Custom world paths**:
  - Must be fetched and transplanted into the repo when used in this datasource.
  - Example: `worlds/the-star-of-wintercrest/assets/images/...`

- **Core/module paths**:
  - Keep as-is only when the dependency is stable external runtime content.
  - Example: `modules/plutonium/...`, shared `icons/...` references intended for Foundry/system-provided assets.
