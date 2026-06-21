# Veiled Omens Plutonium

Repository of Plutonium/5etools-ready Veiled Omens JSON for Foundry VTT import.

## Plutonium configuration

Use this as the **Base Homebrew Repository URL**:

`https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/`

`URL Sources` and `Additional Homebrew Files` must be direct file URLs, for example:

`https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/race/Veiled%20Omens%3B%20Species.json`

## Repository layout and naming

- Canonical species file path: `race/Veiled Omens; Species.json`
- File names use package/homebrew identity, not author/account or mechanical bucket name.
- Canonical subclass file example: `subclass/Veiled Omens; Occult Knight.json`
- Do not use broad content-bucket filenames for single packages (for example, `subclass/Veiled Omens; Fighter Subclasses.json`) unless the file is a real collection containing multiple entries in that collection.
- Author metadata belongs in `_meta.sources[].authors` and adventure/book `author` fields.

## Required contributor update flow

After content path, source metadata, or source-file changes:

```bash
python3 tools/generate-plutonium-indexes.py
python3 tools/generate-plutonium-indexes.py --check
python3 tools/validate-plutonium-datasource.py
```

Then confirm every repository JSON file parses.

Conventions validation is part of the same flow:

- Compare the new/changed file naming and source-id pattern against corresponding TheGiddyLimit/homebrew examples in `homebrew/*` before finishing.
- Ensure the source-id inside `_meta.sources[].json` matches the package name identity for the file content (for example `VeiledOmensOccultKnight` for `subclass/Veiled Omens; Occult Knight.json`).

## Useful docs

- [DEVELOPMENT.md](./DEVELOPMENT.md)
- [schemas/README.md](./schemas/README.md)
- [5etools homebrew conventions](./docs/5etools-homebrew-conventions.md)
- [schemas/plutonium-content-types.md](./schemas/plutonium-content-types.md)
