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

Configure the tracked pre-commit hook in each clone:

```bash
git config core.hooksPath .githooks
```

After content path, source metadata, source-file, or asset-path changes:

```bash
python3 tools/generate-plutonium-indexes.py
python3 tools/validate-content-json.py
python3 tools/generate-plutonium-indexes.py --check
python3 tools/validate-plutonium-datasource.py
python3 tools/validate-plutonium-links.py
python3 tools/validate-foundry-advancements.py
```

The pre-commit hook runs the validation commands above that do not modify files. `validate-content-json.py` parses every repository JSON file and checks every JSON file under recognized content directories.

Conventions validation is part of the same flow:

- Compare the new or changed file naming and source-id pattern against corresponding TheGiddyLimit/homebrew examples before finishing.
- Before troubleshooting or changing a content behavior, inspect corresponding TheGiddyLimit/homebrew examples and record the reference paths or search result.
- Confirm every content JSON file is discovered by `tools/validate-content-json.py`.
- Confirm `_generated/index-sources.json` maps each source ID to the correct package file.
- Confirm `_generated/index-props.json` maps every top-level content array to the correct top-level directory.
- Confirm class and subclass feature references resolve to real Plutonium entities.
- Confirm Foundry dnd5e advancement coverage with `tools/validate-foundry-advancements.py`; character options are not complete when they only pass JSON, source-index, or link-resolution checks.
- Confirm subclass feature arrays start with a subclass-named header feature, with same-level mechanical features linked inside that header and later-level features listed after it.
- Confirm there are no source-authored `ItemGrant` rows for feature grants; Plutonium must generate actor-owned feature grants during real actor import.
- Confirm there are no split source IDs for individual mechanical options inside the same Veiled Omens source package.

## Useful Docs

- [DEVELOPMENT.md](./DEVELOPMENT.md)
- [schemas/README.md](./schemas/README.md)
- [5etools homebrew conventions](./docs/5etools-homebrew-conventions.md)
- [schemas/plutonium-content-types.md](./schemas/plutonium-content-types.md)

## Foundry / Plutonium Import Validation

The Python validators check JSON structure, source indexes, and link resolution. The Foundry import validation tests real actor import behavior through a running FoundryVTT instance with dnd5e and Plutonium. They are separate evidence paths.

```bash
npm install
FOUNDRY_APP_DIR=/path/to/foundry \
FOUNDRY_DATA_DIR=/path/to/foundry-data \
CHROMIUM_EXECUTABLE_PATH=/snap/bin/chromium \
node tools/validate-foundry-plutonium-import.mjs --preflight
```

Then run the full import:

```bash
FOUNDRY_APP_DIR=/path/to/foundry \
FOUNDRY_DATA_DIR=/path/to/foundry-data \
CHROMIUM_EXECUTABLE_PATH=/snap/bin/chromium \
node tools/validate-foundry-plutonium-import.mjs
```

The script starts a local FoundryVTT server, drives a headless Chromium browser, loads the Veiled Omens package through BrewUtil2, imports every race, class, and subclass through the real Plutonium importer, and writes actor items, advancement rows, and any failures to `tmp/foundry-plutonium-import-result.json`.

Use shorter timeout values to force quicker reproduction of interactive blockers; timeout results are blocker evidence with diagnostics, not Foundry verification.

### Environment variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `FOUNDRY_APP_DIR` | none | yes | Foundry application directory containing `package.json` and `main.js` |
| `FOUNDRY_DATA_DIR` | none | yes | Foundry data template directory containing `Data/systems/dnd5e`, `Data/modules/plutonium`, `Data/modules/lib-wrapper`, and the target world |
| `FOUNDRY_WORLD` | `veiled-omens-import` | no | World name to load |
| `FOUNDRY_NODE` | `process.execPath` | no | Node.js executable for Foundry |
| `FOUNDRY_PORT` | `30000` | no | Foundry HTTP port |
| `FOUNDRY_STATIC_PORT` | none | no | Static file server port for serving the package JSON |
| `FOUNDRY_IMPORT_REPORT_PATH` | `tmp/foundry-plutonium-import-result.json` | no | Output report path |
| `CHROMIUM_EXECUTABLE_PATH` | none | yes | Path to a system Chromium binary (e.g. `/snap/bin/chromium`) |
| `FOUNDRY_IMPORT_STEP_TIMEOUT_MS` | `300000` | no | Per real Plutonium import/finalize step timeout in milliseconds; timeout reports a blocker with diagnostics |
| `PACKAGE_JSON` | `collection/Patrick Richardson; Veiled Omens Campaign Setting.json` | no | Package JSON file path |
| `VO_SOURCE_ID` | `VeiledOmens` | no | Source ID to verify after BrewUtil2 load |
| `FOUNDRY_IMPORT_LEVELS` | `1,2,3` | no | Character levels for class import |
| `FOUNDRY_HEADLESS` | `true` | no | Run Chromium headless |
