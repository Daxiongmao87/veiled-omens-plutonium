# Veiled Omens Plutonium Development Guide

This repository is the public raw-content source for Veiled Omens player-facing homebrew used by Plutonium/5etools in Foundry VTT.

Use this repository for JSON homebrew data, source images, and repeatable validation notes. Keep canonical lore and campaign-development prose in the main `venoure` repository; keep only Plutonium-ready data here.

## Plutonium configuration

Set Plutonium's Base Homebrew Repository URL to:

```text
https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/
```

This repository is an indexed Plutonium datasource and must publish these generated files at the root `_generated/` directory:

```text
_generated/index-sources.json
_generated/index-props.json
_generated/index-meta.json
_generated/index-timestamps.json
```

In Plutonium config/data sources, the **Base Homebrew Repository URL** must be the raw repository root shown above.

`URL Sources` and `Additional Homebrew Files` fields are direct JSON file inputs.
Do not point these fields at the repository root URL. A raw repo root fetch returns HTTP 400.

Direct-file examples:

```text
https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/collection/Patrick%20Richardson%3B%20Veiled%20Omens%20Campaign%20Setting.json
```

## Contributor workflow for changes

Configure the tracked pre-commit hook in each clone:

```bash
git config core.hooksPath .githooks
```

After changing file paths, content type paths, source metadata, or file names:

```bash
python3 tools/generate-plutonium-indexes.py
python3 tools/validate-content-json.py
python3 tools/generate-plutonium-indexes.py --check
python3 tools/validate-plutonium-datasource.py
python3 tools/validate-plutonium-links.py
python3 tools/validate-foundry-advancements.py
```

The pre-commit hook runs the validation commands that do not mutate files. `validate-content-json.py` parses every repository JSON file and checks every JSON file under recognized content directories.

Conventions validation step before merge:

- Compare package filenames and source IDs against corresponding TheGiddyLimit/homebrew example files in the same directory. Use `collection/` examples when a source material package spans multiple content types.
- Before changing or troubleshooting a content behavior, inspect corresponding TheGiddyLimit/homebrew examples for that behavior and record the reference paths or search result in the work notes.
- Before changing schema notes or validators for a player-option category, audit matching TheGiddyLimit/homebrew JSONs and Plutonium bundled source/side-data; record the controlling evidence in `docs/5etools-homebrew-conventions.md`.
- Confirm every content JSON file is discovered and validated by `tools/validate-content-json.py`.
- Do not treat index/json checks as sufficient if naming and source identity do not match package-level conventions.
- Do not treat Plutonium linked-entity resolution as sufficient for player options. Run `tools/validate-foundry-advancements.py` and confirm character-option advancement coverage.

## Foundry character-option advancements

Foundry dnd5e advancement coverage is required for player character options.

- Races/species rely on 5etools fields such as `ability`, `size`, `skillProficiencies`, `languageProficiencies`, and `toolProficiencies` to generate generic Foundry advancements. Plutonium imports named race entries as race-feature items on the actor path.
- Classes rely on 5etools fields such as `hd`, `proficiency`, and `startingProficiencies` to generate Foundry advancements.
- Class `startingProficiencies.tools` and `multiclassing.proficienciesGained.tools` arrays use strings. Free-choice tool grants use official-style strings, such as `one type of {@item artisan's tools|PHB} of your choice`, not object `choose` blocks.
- Classes and subclasses rely on `classFeatures` and `subclassFeatures` references that resolve to real feature records. Plutonium's actor import path imports those feature records and creates feature `ItemGrant` links with populated item UUIDs.
- Normal `classFeatures` and `subclassFeatures` entries use the official string-reference form. `classFeatures` objects are used for reference metadata such as `gainSubclassFeature`, `gainSubclassFeatureHasContent`, or `tableDisplayName`.
- Every subclass must list a subclass-named header `subclassFeature` first. Plutonium imports that first feature into the subclass item and ignores it as a child feature item. Real same-level mechanical subclass features must be `refSubclassFeature` entries inside the header; later-level mechanical subclass features follow the header as sibling `subclassFeatures`.
- TheGiddyLimit/homebrew examples and Plutonium's bundled 5etools side-data use concrete non-item advancement data such as `ScaleValue`; they do not source-author `ItemGrant` rows for feature grants.
- Do not add source-authored `ItemGrant` rows. Feature grants are proven by concrete feature/item records, resolving references, and generated importer output from the real actor import path.
- For named class, subclass, race, species, subrace, feat, optional feature, or item-grant behavior, create or identify the concrete feature/item records first, then verify Plutonium generated the actor-owned grants through real import output.
- Plutonium item conversion fields are part of this completion gate. Follow TheGiddyLimit/homebrew source fields for item `type`, `wondrous`, attunement, rarity, charges, and related converter inputs. Wondrous magic items use `wondrous: true` and omit fake item type values such as `type: "WONDROUS"`.
- Drow-style racial spellcasting traits use `additionalSpells` for cantrips, innate spells, and later-level spell availability; do not turn those spell levels into race feature `ItemGrant` rows unless the source has separate named feature entries at those levels.
- `tools/validate-foundry-advancements.py` enforces this rule for every repository content JSON file.

## Source identity

Use this source block for Veiled Omens content unless a file has a specific reason to do otherwise:

```json
{
  "_meta": {
    "sources": [
      {
        "json": "VeiledOmens",
        "abbreviation": "VO",
        "full": "Veiled Omens Campaign Setting",
        "authors": ["Patrick Richardson"],
        "version": "1.0.0-foundry-mechanics"
      }
    ]
  }
}
```

Rules:

- `json` is the stable machine source ID. Do not rename it casually.
- `abbreviation` is the compact label shown in lists.
- `full` is the human-readable campaign setting/source name.
- All entries in the file use `"source": "VeiledOmens"` unless importing third-party material.

### File naming and metadata class rule

Content file names describe source material/package identity inside the directory that matches the package shape.

- Current canonical source package: `collection/Patrick Richardson; Veiled Omens Campaign Setting.json`
- Use `collection/` when one source material package spans multiple content types.
- Use a type-specific directory when the source package is a single-type package or a true type-specific collection.
- Author and account attribution belongs in `_meta.sources[].authors` and adventure/book `author` fields.
- Follow the upstream author-name filename segment for package files when the package convention requires it.

Source IDs follow the package/homebrew identity, not the content bucket or individual mechanical option.

- Current canonical source ID: `VeiledOmens`
- Current Veiled Omens player-facing content remains one collection source unless a future source material is a separate publication/package.
- Do not create split source IDs for individual classes, subclasses, species, spells, items, or features inside the same source material.

## Recommended repository layout

```text
/
  +--- DEVELOPMENT.md
  +--- README.md
  +--- tools/
  |    +--- generate-plutonium-indexes.py
  |    +--- plutonium_content.py
  |    +--- validate-content-json.py
  |    +--- validate-plutonium-datasource.py
  |    +--- validate-plutonium-links.py
  +--- .githooks/
  |    +--- pre-commit
  +--- _generated/
  |    +--- index-meta.json
  |    +--- index-props.json
  |    +--- index-sources.json
  |    +--- index-timestamps.json
  +--- collection/
  |    +--- Patrick Richardson; Veiled Omens Campaign Setting.json
  +--- img/
       +--- VeiledOmens/
            +--- icons/
```

Git does not preserve empty directories, so add `.gitkeep` files when needed.

## Core references

Primary public references:

- Plutonium landing page: `https://5e.tools/plutonium.html`
- 5etools homebrew help: `https://wiki.tercept.net/en/5eTools/HelpPages/makebrew`
- 5etools homebrew table of reference: `https://wiki.tercept.net/en/Homebrew/TableOfReference`
- Race reference: `https://wiki.tercept.net/en/Homebrew/TableOfReference/Race`
- Class reference: `https://wiki.tercept.net/en/Homebrew/TableOfReference/Class`
- Subclass reference: `https://wiki.tercept.net/en/Homebrew/TableOfReference/Subclass`
- Lexicon / Foundry fields: `https://wiki.tercept.net/en/Homebrew/Lexicon`

## Homebrew conventions reference

Use this repository's conventions document for a full crosswalk to TheGiddyLimit/homebrew and Plutonium ingest behavior:

- [5etools homebrew conventions](./docs/5etools-homebrew-conventions.md)

That document covers:

- The adopted and adapted 5etools/homebrew conventions for this repository.
- content-type directory to top-level `__prop` / array mapping.
- `_generated` index file semantics.
- foundry asset transplant workflow (world-relative paths to repo-hosted `img/` files).

Schema repositories and examples may move. When in doubt, inspect the live 5etools/Plutonium data cache and compare against an official race, class, feat, spell, or item that behaves the way the new content is expected to behave.

## Race/species format

Races/species define traits directly in the race object's `entries` array. Do not use class-style feature references for species.

Minimal pattern:

```json
{
  "_meta": {
    "sources": [
      {
        "json": "VeiledOmens",
        "abbreviation": "VO",
        "full": "Veiled Omens Campaign Setting",
        "authors": ["Patrick Richardson"],
        "version": "1.0.0-foundry-mechanics"
      }
    ]
  },
  "race": [
    {
      "name": "Example Species",
      "source": "VeiledOmens",
      "size": ["M"],
      "speed": 30,
      "ability": [{"dex": 2, "wis": 1}],
      "darkvision": 60,
      "languageProficiencies": [{"common": true}],
      "skillProficiencies": [{"perception": true}],
      "creatureTypes": ["humanoid"],
      "foundryImg": "https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/img/VeiledOmens/icons/example.png",
      "entries": [
        {
          "name": "Darkvision",
          "type": "entries",
          "entries": [
            "You can see in dim light within 60 feet of you as if it were bright light, and in darkness as if it were dim light. You can't discern color in darkness, only shades of gray."
          ]
        },
        {
          "name": "Example Trait",
          "type": "entries",
          "entries": [
            "Trait text goes here."
          ]
        }
      ],
      "__prop": "race"
    }
  ]
}
```

Notes:

- Plutonium may not convert every `entries` trait into a separate Foundry dnd5e Advancement row. Exact Foundry item preservation may require direct Foundry item JSON rather than 5etools race JSON.
- Use `foundryImg` for the imported item image.
- Prefer full raw GitHub image URLs while testing; relative paths can be tested after the base repository URL is confirmed.

## Subrace/subspecies format

Subspecies generally follow the race format but include parent identifiers:

```json
{
  "name": "Example Species (Subspecies)",
  "source": "VeiledOmens",
  "raceName": "Example Species",
  "raceSource": "VeiledOmens",
  "_baseName": "Example Species",
  "_baseSource": "VeiledOmens",
  "_subraceName": "Subspecies",
  "_isSubRace": true,
  "size": ["M"],
  "speed": 30,
  "ability": [{"dex": 2, "cha": 1}],
  "entries": []
}
```

## Class format

Classes use explicit feature references. The class object has a `classFeatures` array. Each referenced feature must exist in the top-level `classFeature` array.

Feature string format:

```text
Feature Name|Class Name|Class Source|Level
```

Example:

```json
{
  "class": [
    {
      "name": "Example Class",
      "source": "VeiledOmens",
      "hd": {"number": 1, "faces": 8},
      "proficiency": ["wis", "cha"],
      "startingProficiencies": {
        "armor": ["light"],
        "weapons": ["simple"],
        "tools": ["one type of {@item artisan's tools|PHB} of your choice"],
        "skills": [
          {
            "choose": {
              "from": ["arcana", "history", "insight", "religion"],
              "count": 2
            }
          }
        ]
      },
      "classFeatures": [
        "First Feature|Example Class|VeiledOmens|1"
      ],
      "subclassTitle": "Example Path",
      "__prop": "class"
    }
  ],
  "classFeature": [
    {
      "name": "First Feature",
      "source": "VeiledOmens",
      "className": "Example Class",
      "classSource": "VeiledOmens",
      "level": 1,
      "entries": ["Feature text goes here."]
    }
  ]
}
```

Normal class feature references use strings. Subclass choice features use an object in `classFeatures`:

```json
{
  "classFeature": "Example Path|Example Class|VeiledOmens|3",
  "gainSubclassFeature": true
}
```

## Subclass format

Subclass feature reference format:

```text
Feature Name|Class Name|Class Source|Subclass Short Name|Subclass Source|Level|Feature Source
```

Example:

```json
{
  "subclass": [
    {
      "name": "Path of Omens",
      "shortName": "Omens",
      "source": "VeiledOmens",
      "className": "Example Class",
      "classSource": "VeiledOmens",
      "subclassFeatures": [
        "Omen Reading|Example Class|VeiledOmens|Omens|VeiledOmens|3|VeiledOmens"
      ]
    }
  ],
  "subclassFeature": [
    {
      "name": "Omen Reading",
      "source": "VeiledOmens",
      "className": "Example Class",
      "classSource": "VeiledOmens",
      "subclassShortName": "Omens",
      "subclassSource": "VeiledOmens",
      "level": 3,
      "entries": ["Subclass feature text goes here."]
    }
  ]
}
```

## Images

Recommended image policy:

- Put icons under the package asset directory, currently `img/VeiledOmens/icons/`.
- Use lowercase hyphenated or snake_case names.
- Reference images with full raw URLs until Plutonium import is confirmed.
- Keep image dimensions reasonable for Foundry item icons, typically square PNG or WebP.

Example:

```text
"foundryImg": "https://raw.githubusercontent.com/Daxiongmao87/veiled-omens-plutonium/main/img/VeiledOmens/icons/ghost_elf.png"
```

## Validation checklist

Before committing content:

1. Confirm the JSON parses with `jq` or an equivalent validator.
2. Confirm `_meta.sources[].json` matches every entry's `source` field.
3. Confirm feature reference strings exactly match the names and source IDs of their target records.
4. Confirm `_generated/index-sources.json` includes the content file path for each source.
5. Confirm `_generated/index-props.json` includes top-level arrays for every content property in each file.
6. Confirm each generated path resolves to a file in the repository.
7. Import into a disposable Foundry world before relying on it in campaign play.
8. Confirm Plutonium shows the content under the expected importer.
9. Confirm item image resolution works.
10. Confirm rules text appears in the Description tab.
11. Confirm mechanical choices apply correctly to a test actor.
12. Confirm `python3 tools/validate-plutonium-datasource.py` passes before release.
13. Confirm generated indexes were produced with `python3 tools/generate-plutonium-indexes.py --check`.
14. Confirm `python3 tools/validate-plutonium-links.py` passes before release.

## Plutonium troubleshooting

If content does not appear:

- Confirm `_generated/index-sources.json` exists.
- Confirm `_generated/index-props.json` exists.
- Confirm `_generated/index-meta.json` exists.
- Confirm `_generated/index-timestamps.json` exists.
- Confirm the target files are present and paths are relative to the repository root.
- Check that the Base Homebrew Repository URL ends with `/main/`.
- For local testing, check that `index.json` import mode works if you are explicitly using local `index.json` file import.
- Try loading the exact raw JSON URL in a browser.
- Clear/reload Plutonium homebrew data.
- Restart Foundry after changing source metadata.
- Search by source abbreviation and by item name.

If icons do not appear:

- Open the raw image URL in a browser.
- Confirm `foundryImg` points to the image, not to a GitHub HTML page.
- Prefer `raw.githubusercontent.com`, not `github.com/.../blob/...`.

If race/species traits appear in Description but not Advancement:

- Do not accept description rendering as completion for a player option.
- Confirm the behavior against Plutonium's bundled 5etools source data and side-data before changing source JSON.
- Do not add source-authored `ItemGrant` rows. Create or repair the concrete race entries, class feature records, subclass feature records, and references, then prove Plutonium generated the actor-owned `ItemGrant` rows through real actor import output.
- If the missing trait is racial spellcasting, add or repair `additionalSpells` instead of adding fake spell-level `ItemGrant` rows.
- Use direct Foundry item JSON or portable compendium UUIDs only when exact child-item linking is required outside the 5etools/Plutonium feature-reference import path.

## Foundry / Plutonium import validation

The Python validators check JSON structure, source indexes, and link resolution. The Foundry import validation tests real actor import behavior through a running FoundryVTT instance with dnd5e and Plutonium. They are separate evidence paths.

### Prerequisites

1. A FoundryVTT application directory (containing `package.json` and `main.js`)
2. A Foundry data directory with `Data/systems/dnd5e`, `Data/modules/plutonium`, `Data/modules/lib-wrapper`, and the target world
3. A system Chromium browser (e.g. `/snap/bin/chromium`)
4. `npm install` in this repository to install `playwright-core` (does not download browsers)

### Preflight

```bash
FOUNDRY_APP_DIR=/path/to/foundry \
FOUNDRY_DATA_DIR=/path/to/foundry-data \
CHROMIUM_EXECUTABLE_PATH=/snap/bin/chromium \
node tools/validate-foundry-plutonium-import.mjs --preflight
```

The preflight checks:
- Foundry app directory exists with `package.json` and `main.js`
- Foundry data template contains dnd5e, Plutonium, and lib-wrapper modules
- Foundry data template contains the target world directory
- `playwright-core` is installed
- `CHROMIUM_EXECUTABLE_PATH` points to an existing browser binary
- Package JSON file is valid and contains player-facing arrays

### Full import

```bash
FOUNDRY_APP_DIR=/path/to/foundry \
FOUNDRY_DATA_DIR=/path/to/foundry-data \
CHROMIUM_EXECUTABLE_PATH=/snap/bin/chromium \
node tools/validate-foundry-plutonium-import.mjs
```

The full run:
1. Runs preflight checks
2. Copies the Foundry data template to `tmp/` to avoid mutating the source
3. Starts a local static HTTP server for the package JSON
4. Launches Foundry via `node main.js` with the temp data path
5. Opens Foundry in a headless Chromium browser
6. Verifies `game.ready`, dnd5e, Plutonium, and lib-wrapper are active
7. Loads the Veiled Omens package through `BrewUtil2.pAddBrewFromUrl`
8. Imports every race into a test character actor via the Plutonium importer
9. Imports every class and subclass through the Plutonium importer with configured levels
10. Records actor items, advancement rows, malformed advancement rows, Plutonium flags, boot versions, package URL, and failures
11. Writes the report to `tmp/foundry-plutonium-import-result.json`
12. Closes the browser, stops the static server, and terminates the Foundry child process

If Plutonium prompts or blocks on choices during import, the exact failure is recorded as a blocker in the result JSON rather than being reported as a pass.
Use shorter values of `FOUNDRY_IMPORT_STEP_TIMEOUT_MS` to quickly reproduce interactive blockers; a timeout is blocker evidence with diagnostics, not Foundry verification.

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
