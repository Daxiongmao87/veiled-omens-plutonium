# Veiled Omens Plutonium

Repository of Plutonium/5etools-ready Veiled Omens JSON for Foundry VTT import.

## Plutonium configuration

Use this as the **Base Homebrew Repository URL**:

`https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/`

`URL Sources` and `Additional Homebrew Files` must be direct file URLs, for example:

`https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/collection/Patrick%20Richardson%3B%20Veiled%20Omens%20Campaign%20Setting.json`

## Repository Layout And Naming

- Current canonical source package: `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`
- Current canonical source ID: `VeiledOmens`
- Source IDs model source material/package identity, not individual classes, subclasses, species, spells, items, or features.
- Use `collection/` when one source material package spans multiple content types.
- Use a type-specific directory when the source material package is a single-type package or a true type-specific collection.
- Author metadata belongs in `_meta.sources[].authors` and adventure/book `author` fields.
- Image assets for this source package live under `img/VeiledOmens/icons/`.

## Required Contributor Update Flow

After content path, source metadata, source-file, or asset-path changes:

```bash
python3 tools/generate-plutonium-indexes.py
python3 tools/generate-plutonium-indexes.py --check
python3 tools/validate-plutonium-datasource.py
```

Then confirm every repository JSON file parses.

Conventions validation is part of the same flow:

- Compare the new or changed file naming and source-id pattern against corresponding TheGiddyLimit/homebrew examples before finishing.
- Confirm `_generated/index-sources.json` maps each source ID to the correct package file.
- Confirm `_generated/index-props.json` maps every top-level content array to the correct top-level directory.
- Confirm there are no split source IDs for individual mechanical options inside the same Veiled Omens source package.

## Useful Docs

- [DEVELOPMENT.md](./DEVELOPMENT.md)
- [schemas/README.md](./schemas/README.md)
- [5etools homebrew conventions](./docs/5etools-homebrew-conventions.md)
- [schemas/plutonium-content-types.md](./schemas/plutonium-content-types.md)
